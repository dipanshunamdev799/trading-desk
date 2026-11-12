"""Persistent order lifecycle and central risk gate shared by every strategy worker."""
import hashlib,math,time,uuid
from datetime import datetime,timedelta,timezone
from .store import encoded,now
from .market import stamp,validate_quote
from .strategy import features
from .broker import broker_for,UnknownSubmission

ACTIVE=('ENTRY_PENDING','OPEN','EXIT_PENDING','UNKNOWN')
TERMINAL=('COMPLETE','CANCELLED','REJECTED')
IST=timezone(timedelta(hours=5,minutes=30))


def day_of(value):return stamp(value).astimezone(IST).date().isoformat()


def fees(side,value,at,brokerage):
    exchange=value*.0003553;sebi=value*.000001;stamp_duty=value*.00003 if side=='BUY' else 0
    stt=value*(.0015 if day_of(at)>='2026-04-01' else .001) if side=='SELL' else 0
    gst=(brokerage+exchange)*.18
    return {'brokerage':brokerage,'exchange_and_ipft':exchange,'sebi':sebi,'stamp':stamp_duty,'stt':stt,'gst':gst,'total':brokerage+exchange+sebi+stamp_duty+stt+gst,'basis':'estimated rate schedule, reconcile live contract note'}


class Engine:
    def __init__(self,store,strategy,market,broker=None,token=None):
        self.store,self.strategy,self.market,self.broker,self.token=store,strategy,market,broker,token
    def _broker(self,config):return self.broker or broker_for(config)
    def _active(self,c):return [r['payload'] for r in self.store.rows('trades',c) if r['status'] in ACTIVE]
    def error(self,message):
        with self.store.tx() as c:
            self.store.fenced(c,self.token);c.execute("UPDATE state SET status='ERROR',error=?",(message,));self.store.event(c,'ERROR',message=message)
    def _attempt(self,c,order,kind):
        settings=self.store.global_settings(c);c.execute('DELETE FROM control.attempts WHERE at<?',(time.time()-60,))
        count=c.execute('SELECT COUNT(*) FROM control.attempts').fetchone()[0]
        limit=settings['max_orders_per_minute']-(settings['max_positions'] if kind=='ENTRY' else 0)
        if count>=limit:raise ValueError('Order submission rate limit; exit capacity reserved')
        c.execute('INSERT INTO control.attempts VALUES(?,?)',(order['id'],time.time()))
    def signal(self,f,side,at):
        r=f.iloc[-1];known=r.known_at.to_pydatetime();sid=hashlib.sha256((self.store.bot_id+'|'+known.isoformat()).encode()).hexdigest()
        indicators={k:float(r[k]) if math.isfinite(float(r[k])) else None for k in ['atr','trend','efficiency','rsi','ema9','ema12','ema21','ema26','vol_ratio','gap']}
        return {'id':sid,'at':known.isoformat(),'side':int(side),'underlying':'NSE_INDEX|Nifty 50','spot':float(r.close),'indicators':indicators,
            'reason':self.strategy.DEFINITION.description,'strategy':self.strategy.DEFINITION.json()}
    def tick(self,at=None):
        supplied_at=at
        self._clock=(lambda:supplied_at) if supplied_at is not None else (lambda:datetime.now(timezone.utc))
        at=at or datetime.now(timezone.utc)
        state=self.store.state();config=state['config'];broker=self._broker(config)
        # Reconcile durable orders before considering another signal. Never blindly resubmit live intents.
        for row in self.store.rows('orders'):
            o=row['payload']
            if o['status'] in TERMINAL:continue
            result=broker.poll(o) if o.get('broker_order_id') else broker.lookup(o)
            if result is None:
                self.error('Uncertain order '+o['id']+' has no broker match; entries frozen, manual reconciliation required');return
            self._apply(o,result,at)
            if result['status']=='PENDING' and not o.get('cancel_requested_at') and (result['filled_qty']>0 or (at-stamp(o['created_at'])).total_seconds()>=config['order_timeout_seconds']):
                with self.store.tx() as c:
                    current=next(r['payload'] for r in self.store.rows('orders',c) if r['id']==o['id'])
                    self._attempt(c,{'id':'cancel-'+o['id']},'EXIT');current['cancel_requested_at']=at.isoformat();self.store.save(c,'orders',current)
                    self.store.event(c,'CANCEL_REQUESTED',order_id=o['id'],reason='order_timeout_or_partial')
                broker.cancel({**o,'broker_order_id':result['order_id']})
        state=self.store.state()
        with self.store.connection() as c:active=self._active(c);global_settings=self.store.global_settings(c)
        for trade in active:
            if trade['status']!='OPEN':continue
            q=self.market.quote(trade['instrument_key'],at);at=self._clock();validate_quote(q,trade['execution_config'],at)
            bid=q['bid'];cfg=trade['execution_config'];remaining=trade['quantity']-trade['sold_quantity']
            reason=None;peak=max(trade.get('high_water_bid',bid),bid)
            stop=trade.get('stop_price');target=trade.get('target_price')
            trailing=peak*(1-cfg['trailing_percent']/100) if cfg.get('trailing_percent') else None
            if global_settings['kill_switch']:reason='GLOBAL_KILL'
            elif state['desired']=='STOPPED':reason='BOT_STOP'
            elif at.astimezone(IST).time()>=datetime.strptime('15:10','%H:%M').time():reason='SESSION_SQUARE_OFF'
            elif at>=stamp(trade['due_at']):reason='TIME_EXIT'
            elif stop and bid<=stop:reason='STOP_LOSS'
            elif target and bid>=target:reason='TARGET'
            elif trailing and bid<=trailing:reason='TRAILING_STOP'
            with self.store.tx() as c:
                gross_mark=(bid-trade['entry_price'])*remaining
                net_mark=gross_mark-trade['entry_fees']*remaining/trade['quantity']-fees('SELL',bid*remaining,at.isoformat(),cfg['brokerage_per_order'])['total']
                self.store.fenced(c,self.token);trade.update(high_water_bid=peak,last_bid=bid,mark_at=q['captured_at'],gross_unrealized_pnl=gross_mark,unrealized_pnl=net_mark)
                self.store.save(c,'trades',trade)
            if reason:self._exit(trade,q,reason,at,broker)
        with self.store.tx() as c:
            self.store.fenced(c,self.token);state=self.store.state(c);active=self._active(c);g=self.store.global_settings(c)
            status='STOPPING' if state['desired']=='STOPPED' and active else state['desired']
            if state['status']=='ERROR' and active:status='ERROR'
            c.execute('UPDATE state SET status=?',(status,))
        # Pausing/stop/kill prevents entries but never abandons existing positions.
        if state['desired']!='RUNNING' or state['status']=='ERROR' or active or g['kill_switch']:return
        local=at.astimezone(IST);minute=local.hour*60+local.minute
        window=self.strategy.DEFINITION.window
        if minute<575 or minute>850 or (window=='afternoon' and minute<785) or (window=='morning' and minute>660):return
        candles=self.market.candles(at);at=self._clock();f=features(candles,at);side=int(self.strategy.signals(f)[-1]);r=f.iloc[-1]
        if state['last_signal']==r.known_at.isoformat():return
        s=self.signal(f,side,at)
        with self.store.tx() as c:
            self.store.fenced(c,self.token);c.execute('UPDATE state SET last_signal=?',(r.known_at.isoformat(),))
            if c.execute('SELECT 1 FROM signals WHERE id=?',(s['id'],)).fetchone():return
            c.execute('INSERT INTO signals VALUES(?,?,?,?)',(s['id'],s['at'],'DETECTED' if side else 'NO_SETUP',encoded(s)))
        if not side:return
        try:
            if day_of(s['at'])!=local.date().isoformat() or not 0<=(at-stamp(s['at'])).total_seconds()<=config['signal_max_age_seconds']:raise ValueError('Stale or future signal')
            due=stamp(s['at'])+timedelta(minutes=self.strategy.DEFINITION.hold_minutes)
            if due.astimezone(IST).strftime('%H:%M')>'15:10':raise ValueError('Holding period exceeds session cutoff')
            contract=self.market.select(side,s['spot'],at);q=self.market.quote(contract['key'],at);at=self._clock();validate_quote(q,config,at)
            self._enter(s,contract,q,at,broker)
        except Exception as e:
            with self.store.tx() as c:
                self.store.fenced(c,self.token)
                reason=str(e) if isinstance(e,ValueError) else type(e).__name__+': market/execution input unavailable'
                c.execute("UPDATE signals SET status='SKIPPED',payload=? WHERE id=? AND status='DETECTED'",(encoded({**s,'rejection_reason':reason}),s['id']));self.store.event(c,'SIGNAL_SKIPPED',signal_id=s['id'],reason=reason)
            if not isinstance(e,ValueError):raise
    def _enter(self,s,contract,q,at,broker):
        with self.store.tx() as c:
            self.store.fenced(c,self.token);state=self.store.state(c);cfg=state['config'];global_cfg=self.store.global_settings(c)
            if not 0<=(at-stamp(s['at'])).total_seconds()<=cfg['signal_max_age_seconds']:raise ValueError('Signal expired during data retrieval')
            if bool(broker.live)!=(cfg['mode']=='live'):raise ValueError('Execution mode changed; reevaluate with the matching broker')
            if state['desired']!='RUNNING' or state['status']=='ERROR' or global_cfg['kill_switch']:raise ValueError('Entries disabled')
            if self._active(c):raise ValueError('Existing position/order prevents entry')
            if c.execute('SELECT 1 FROM trades WHERE signal_id=?',(s['id'],)).fetchone():raise ValueError('Duplicate signal already executed')
            validate_quote(q,cfg,at)
            lot=contract['lot']
            if type(lot) is not int or lot<=0:raise ValueError('Invalid dated lot size')
            price=math.ceil((q['ask']+max(cfg['slippage_points'],q['ask']*.005))*20)/20
            unit_risk=price*(cfg['stop_percent']/100 if cfg['stop_percent'] else 1)
            per_lot_fees=fees('BUY',price*lot,s['at'],cfg['brokerage_per_order'])['total']+fees('SELL',price*lot,s['at'],cfg['brokerage_per_order'])['total']
            trades=[r['payload'] for r in self.store.rows('trades',c) if r['payload']['mode']==cfg['mode']]
            today=[r for r in trades if day_of(r['created_at'])==day_of(s['at'])]
            pnl=sum(r.get('net_pnl',0) for r in trades if r.get('exit_at') and day_of(r['exit_at'])==day_of(s['at']))
            if len(today)>=cfg['max_trades_per_day']:raise ValueError('Maximum daily trade attempts reached')
            budget=min(cfg['max_loss_per_trade'],cfg['max_daily_loss']+pnl)
            cash=max(0,min(cfg['capital'],cfg['capital']+sum(r.get('net_pnl',0) for r in trades)))
            lots=min(int(budget//(unit_risk*lot+per_lot_fees)),cfg['max_quantity']//lot,int(cash//(price*lot+per_lot_fees)))
            if lots<1:raise ValueError('Minimum lot exceeds remaining risk, quantity or capital budget')
            qty=lots*lot
            fee_reserve=fees('BUY',price*qty,s['at'],cfg['brokerage_per_order'])['total']+fees('SELL',price*qty,s['at'],cfg['brokerage_per_order'])['total']
            capital=price*qty+fee_reserve;reserved_risk=unit_risk*qty+fee_reserve
            if capital>cash or reserved_risk>budget:raise ValueError('Quantity exceeds cash or risk after fees')
            exposure=c.execute('SELECT COUNT(*),COALESCE(SUM(capital),0) FROM control.exposure').fetchone()
            if exposure[0]>=global_cfg['max_positions'] or exposure[1]+capital>global_cfg['max_capital']:raise ValueError('Global position or capital limit')
            if int(q['ask_qty'])<lot or int(q['bid_qty'])<lot:raise ValueError('Insufficient one-lot depth')
            tid=uuid.uuid4().hex;oid=hashlib.sha256((s['id']+'ENTRY').encode()).hexdigest()[:32]
            trade={'id':tid,'signal_id':s['id'],'bot_id':self.store.bot_id,'mode':cfg['mode'],'status':'ENTRY_PENDING','created_at':at.isoformat(),
                'instrument_key':contract['key'],'symbol':contract['symbol'],'exchange':contract['exchange'],'contract':contract,'direction':'LONG','signal_direction':s['side'],
                'quantity':0,'sold_quantity':0,'entry_value':0,'exit_value':0,'entry_price':0,'entry_fees':0,'exit_fees':0,'gross_pnl':0,'net_pnl':0,
                'entry_reason':s['reason'],'signal':s,'execution_config':cfg,'due_at':(stamp(s['at'])+timedelta(minutes=self.strategy.DEFINITION.hold_minutes)).isoformat()}
            order={'id':oid,'trade_id':tid,'kind':'ENTRY','side':'BUY','instrument_key':contract['key'],'quantity':qty,'lot':lot,'limit_price':price,
                'quote':q,'slippage_points':cfg['slippage_points'],'created_at':at.isoformat(),'status':'SUBMITTING','applied_qty':0,'applied_value':0,'applied_fees':0,'config':cfg}
            self._attempt(c,order,'ENTRY');self.store.save(c,'trades',trade);self.store.save(c,'orders',order)
            c.execute('INSERT INTO control.exposure VALUES(?,?,?,?,?,?)',(self.store.bot_id,tid,cfg['mode'],capital,reserved_risk,qty))
            c.execute("UPDATE signals SET status='ORDER_INTENT' WHERE id=?",(s['id'],));self.store.event(c,'ORDER_INTENT',order=order)
        self._submit(order,broker,at)
    def _exit(self,trade,q,reason,at,broker):
        with self.store.tx() as c:
            self.store.fenced(c,self.token)
            current=next(r['payload'] for r in self.store.rows('trades',c) if r['id']==trade['id'])
            if current['status']!='OPEN':return
            cfg=current['execution_config'];qty=current['quantity']-current['sold_quantity']
            price=max(.05,math.floor((q['bid']-max(cfg['slippage_points'],q['bid']*.005))*20)/20)
            order={'id':uuid.uuid4().hex,'trade_id':current['id'],'kind':'EXIT','side':'SELL','instrument_key':current['instrument_key'],'quantity':qty,
                'lot':current['contract']['lot'],'limit_price':price,'quote':q,'slippage_points':cfg['slippage_points'],'created_at':at.isoformat(),
                'status':'SUBMITTING','applied_qty':0,'applied_value':0,'applied_fees':0,'config':cfg,'exit_reason':reason}
            self._attempt(c,order,'EXIT');current['status']='EXIT_PENDING';self.store.save(c,'trades',current);self.store.save(c,'orders',order);self.store.event(c,'EXIT_INTENT',order=order)
        self._submit(order,broker,at)
    def _submit(self,order,broker,at):
        at=getattr(self,'_clock',lambda:at)()
        try:validate_quote(order['quote'],order['config'],at)
        except ValueError as e:
            self._apply(order,{'order_id':'not-submitted-'+order['id'],'status':'REJECTED','filled_qty':0,'average_price':0,'error':str(e)},at);return
        try:self._apply(order,broker.submit(order),at)
        except Exception as e:
            # Keep reservation and durable intent. A placement error is never permission to retry it.
            with self.store.tx() as c:
                self.store.fenced(c,self.token)
                current=next(r['payload'] for r in self.store.rows('orders',c) if r['id']==order['id'])
                current['status']='UNKNOWN';current['execution_error']=type(e).__name__;self.store.save(c,'orders',current)
                trade=next(r['payload'] for r in self.store.rows('trades',c) if r['id']==order['trade_id']);trade['status']='UNKNOWN';self.store.save(c,'trades',trade)
                self.store.event(c,'SUBMISSION_UNCERTAIN',order_id=order['id'],error_type=type(e).__name__)
            self.error(type(e).__name__+': order outcome requires reconciliation')
    def _apply(self,order,result,at):
        with self.store.tx() as c:
            self.store.fenced(c,self.token)
            o=next(r['payload'] for r in self.store.rows('orders',c) if r['id']==order['id'])
            t=next(r['payload'] for r in self.store.rows('trades',c) if r['id']==o['trade_id'])
            filled=int(result['filled_qty']);value=filled*float(result.get('average_price') or 0)
            if not o['applied_qty']<=filled<=o['quantity'] or (filled and value<=0):raise ValueError('Broker fill regression or invalid quantity')
            delta=filled-o['applied_qty'];delta_value=value-o['applied_value']
            cumulative_fees=fees(o['side'],value,at.isoformat(),o['config']['brokerage_per_order']) if filled else {'total':0}
            delta_fees=cumulative_fees['total']-o['applied_fees']
            if o['kind']=='ENTRY':
                t['quantity']+=delta;t['entry_value']+=delta_value;t['entry_fees']+=delta_fees
                if t['quantity']:
                    t['entry_price']=t['entry_value']/t['quantity'];t.setdefault('entry_at',at.isoformat())
                    cfg=t['execution_config'];t['stop_price']=t['entry_price']*(1-cfg['stop_percent']/100) if cfg['stop_percent'] else None
                    t['target_price']=t['entry_price']*(1+cfg['target_percent']/100) if cfg['target_percent'] else None
            else:
                t['sold_quantity']+=delta;t['exit_value']+=delta_value;t['exit_fees']+=delta_fees
                if t['sold_quantity']>t['quantity']:raise ValueError('Exit overfill; reconciliation required')
            o.update(broker_order_id=result.get('order_id'),status=result['status'],applied_qty=filled,applied_value=value,applied_fees=cumulative_fees['total'],last_result=result,updated_at=at.isoformat())
            o['fee_breakdown']=cumulative_fees
            if result['status'] in TERMINAL:
                if o['kind']=='ENTRY':
                    t['status']='OPEN' if t['quantity'] else 'REJECTED'
                    c.execute('UPDATE signals SET status=? WHERE id=?',('EXECUTED' if t['quantity'] else 'REJECTED',t['signal_id']))
                else:t['status']='CLOSED' if t['sold_quantity']==t['quantity'] else 'OPEN'
            else:t['status']='ENTRY_PENDING' if o['kind']=='ENTRY' else 'EXIT_PENDING'
            if t['status']=='CLOSED':
                t.update(exit_at=at.isoformat(),exit_reason=o['exit_reason'],exit_price=t['exit_value']/t['sold_quantity'],
                    gross_pnl=t['exit_value']-t['entry_value'],net_pnl=t['exit_value']-t['entry_value']-t['entry_fees']-t['exit_fees'],
                    holding_seconds=(at-stamp(t['entry_at'])).total_seconds(),unrealized_pnl=0)
            if t['quantity']:
                t['realized_pnl_so_far']=t['exit_value']-t['entry_price']*t['sold_quantity']-t['entry_fees']*t['sold_quantity']/t['quantity']-t['exit_fees']
            if t['status'] in ('CLOSED','REJECTED'):c.execute('DELETE FROM control.exposure WHERE trade_id=?',(t['id'],))
            elif t['status']=='OPEN':
                remaining=t['quantity']-t['sold_quantity'];value=t['entry_price']*remaining;cfg=t['execution_config']
                exit_fee=fees('SELL',value,at.isoformat(),cfg['brokerage_per_order'])['total']
                risk=value*(cfg['stop_percent']/100 if cfg['stop_percent'] else 1)+t['entry_fees']+exit_fee
                c.execute('UPDATE control.exposure SET capital=?,risk=?,qty=? WHERE trade_id=?',(value+t['entry_fees']+exit_fee,risk,remaining,t['id']))
            self.store.save(c,'orders',o);self.store.save(c,'trades',t);self.store.event(c,'ORDER_UPDATE',order_id=o['id'],result=result,fill_delta=delta,trade_status=t['status'])
