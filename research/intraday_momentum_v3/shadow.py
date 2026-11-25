"""Exactly three forward hypotheses; gated hypothetical ledger, no broker calls."""
from dataclasses import asdict
from datetime import timedelta
import hashlib
from .features import FeatureBuffer,Quote,timestamp
from .execution import proposed_size,depth_walk,markout
from research.intraday_momentum.costs import fees

HORIZONS=(30,60,180,300,900,1800)


def hypotheses(f):
    r=f.get('return60_bps');r5=f.get('return300_bps');daily=f.get('daily_return');imb=f.get('imbalance_mean10')
    if r is None or r5 is None or daily is None:return []
    events=[];side=1 if r>=0 else -1;volume=f.get('volume_acceleration')
    if abs(r)>=20 and abs(r5)>=50 and r*r5>0 and abs(daily)>=.01:
        supported=(f.get('support_up_fraction') if side==1 else f.get('support_down_fraction')) or 0
        events.append(dict(family='H3-A',side=side,volume_confirmation=volume is not None and volume>=2,
            depth_confirmation=supported>=.8 and f.get('support_seconds10',0)>=8 and f['spread_bps']<=10))
    high=f.get('prior_high300');low=f.get('prior_low300');minimum=f.get('mid_min3');maximum=f.get('mid_max3')
    bside=1 if high and minimum and minimum>high*1.0005 else -1 if low and maximum and maximum<low*.9995 else 0
    if bside and abs(r)>=10 and f.get('observed_seconds3',0)>=3:
        med=f.get('median_spread60')
        events.append(dict(family='H3-B',side=bside,volume_confirmation=volume is not None and volume>=1.5,
            depth_confirmation=imb is not None and bside*imb>=.1 and f['spread_bps']<=10 and med is not None and f['spread_bps']<=2*max(med,.1)))
    if abs(r5)>=100 and abs(daily)>=.02 and r*r5<0 and abs(r)>=10:
        impulse=1 if r5>0 else -1;med=f.get('median_spread60')
        events.append(dict(family='H3-C',side=-impulse,original_continuation_side=impulse,volume_confirmation=volume is not None and volume>=1,
            depth_confirmation=imb is not None and impulse*imb<0 and med is not None and f['spread_bps']>=2*max(med,.1),
            avoidance_test=True))
    return events


class HypotheticalLedger:
    def __init__(self,gate=None):
        self.gate=gate or {};self.equity=1_000_000.;self.opening=self.equity;self.day=None;self.count=0;self.used=set();self.position=None;self.pending=None;self.halted=False
        self.peak=self.equity;self.max_intraday_dd=0.
    def state(self):
        def position(value):
            if value is None:return None
            return {k:asdict(v) if isinstance(v,Quote) else v for k,v in value.items()}
        return dict(equity=self.equity,opening=self.opening,day=self.day,count=self.count,used=sorted(self.used),
            halted=self.halted,peak=self.peak,max_intraday_dd=self.max_intraday_dd,pending=position(self.pending),position=position(self.position))
    def restore(self,value):
        def quote(record):
            r=dict(record)
            for key in ('source_at','received_at','available_at','last_trade_at'):r[key]=timestamp(r.get(key))
            r['bids']=tuple(tuple(x) for x in r['bids']);r['asks']=tuple(tuple(x) for x in r['asks']);return Quote(**r)
        def position(record):
            if record is None:return None
            r=dict(record)
            for key in ('decision','entry_quote'):
                if key in r:r[key]=quote(r[key])
            for key in ('not_before','due','failure_since','failure_exit_requested'):
                if key in r:r[key]=timestamp(r[key])
            return r
        for key in ('equity','opening','day','count','halted','peak','max_intraday_dd'):setattr(self,key,value[key])
        self.used=set(value['used']);self.position=position(value.get('position'));self.pending=position(value.get('pending'))
    def candidate(self,candidate,q,metadata,decision_at=None):
        decision_at=decision_at or q.available_at
        if not q.fresh(decision_at):return dict(status='REJECTED_STALE_DECISION_QUOTE')
        day=decision_at.astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date().isoformat()
        if self.day!=day:
            if self.position or self.pending:return dict(status='REJECTED_UNRESOLVED_PRIOR_SESSION')
            self.day=day;self.opening=self.equity;self.count=0;self.used=set();self.halted=False;self.peak=self.equity
        if not self.gate.get('quality_pass'):return dict(status='REJECTED_QUALITY_GATE',proposed_quantity=None)
        if q.transport!='ws':return dict(status='REJECTED_TRANSPORT_NOT_QUALIFIED',proposed_quantity=None)
        if not self.gate.get('predictor_frozen'):return dict(status='REJECTED_PREDICTOR_NOT_FROZEN',proposed_quantity=None)
        if not candidate.get('volume_confirmation') or not candidate.get('depth_confirmation'):return dict(status='REJECTED_CONFIRMATION_NOT_MET')
        if self.position or self.pending:return dict(status='REJECTED_CAPITAL_BUSY')
        if self.halted or self.equity-self.opening<=-.01*self.opening:return dict(status='REJECTED_DAILY_LOSS_BUDGET')
        if self.count>=3:return dict(status='REJECTED_THREE_ENTRY_CAP')
        if q.key in self.used:return dict(status='REJECTED_SAME_SYMBOL_REENTRY')
        side=candidate['side'];f=candidate['features'];lo=f.get('low60');hi=f.get('high60')
        anchor=(lo-q.spread_bps*q.mid/1e4) if side==1 and lo else (hi+q.spread_bps*q.mid/1e4) if hi else None
        stop_fraction=side*(q.mid-anchor)/q.mid if anchor else 0
        risk=min(self.equity*.005,self.opening*.01+self.equity-self.opening)
        meta_ok=metadata.get('in_mis') and not metadata.get('in_suspended') and metadata.get('security_type')=='NORMAL' and not metadata.get('stale_history',True)
        account=self.gate.get('account_segments_verified',False) and (side==1 or self.gate.get('short_execution_verified',False))
        proposal=proposed_size(q,side,self.equity,risk,stop_fraction,f.get('volume60'),meta_ok,account)
        if not proposal['accepted']:return dict(status='REJECTED_'+proposal['reason'].upper(),proposal=proposal)
        # Model prediction must be supplied by the frozen forward model, never a
        # target distance mislabelled expected return. Missing means reject.
        gross=candidate.get('predicted_gross_bps');cost=markout(q,q,side,proposal['quantity'])
        predicted=gross+cost['net_bps'] if gross is not None and cost.get('status')=='QUOTED_BOUND_ONLY' else None
        uncertainty=self.gate.get('execution_uncertainty_bps',float('inf'))
        if predicted is None or predicted<=max(5,2*uncertainty):return dict(status='REJECTED_ECONOMIC_EDGE_UNPROVEN',proposal=proposal)
        self.pending=dict(candidate=candidate,proposal=proposal,decision=q,not_before=decision_at+timedelta(seconds=1))
        return dict(status='HYPOTHETICAL_PENDING_NEXT_QUOTE',proposal=proposal)
    def observe(self,q):
        events=[]
        if self.pending and q.key==self.pending['decision'].key and q.transport==self.pending['decision'].transport and q.available_at>=self.pending['not_before']:
            p=self.pending;self.pending=None;quantity=p['proposal']['quantity'];side=p['candidate']['side']
            if (q.available_at-p['not_before']).total_seconds()>1:return [dict(status='HYPOTHETICAL_UNFILLED_LATENCY_GAP')]
            if not q.valid_book or not q.fresh(q.available_at):return [dict(status='HYPOTHETICAL_UNFILLED_STALE_QUOTE')]
            bound=depth_walk(q.asks if side==1 else q.bids,quantity)
            if bound['unfilled']:return [dict(status='HYPOTHETICAL_UNFILLED_PARTIAL_DEPTH',bound=bound)]
            change=side*(bound['price_bound']/p['proposal']['entry_bound']-1)
            if change>.003:return [dict(status='HYPOTHETICAL_UNFILLED_CHASE_LIMIT')]
            ep=bound['price_bound']*(1+side*.0001);stop=p['proposal']['stop'];exit_bound=stop*(1-side*.0001)
            charges=fees('BUY' if side==1 else 'SELL',ep,quantity)['total']+fees('SELL' if side==1 else 'BUY',exit_bound,quantity)['total']
            room=min(self.equity*.005,self.opening*.01+self.equity-self.opening)
            if ep*quantity+fees('BUY' if side==1 else 'SELL',ep,quantity)['total']>self.equity or max(0,side*(ep-stop))*quantity+charges>room:
                return [dict(status='HYPOTHETICAL_UNFILLED_ENTRY_CASH_RISK')]
            self.position={**p,'entry_quote':q,'side':side,'quantity':quantity,'due':q.available_at+timedelta(minutes=30),'status':'OPEN_QUOTE_BOUND'}
            self.count+=1;self.used.add(q.key);events.append(dict(status='HYPOTHETICAL_OPENED',episode_id=p['candidate'].get('episode_id'),quantity=quantity,entries_today=self.count))
        pos=self.position
        if pos and pos['entry_quote'].key==q.key and pos['entry_quote'].transport==q.transport:
            if not q.valid_book or not q.fresh(q.available_at):return events+[dict(status='UNPRICED_EXPOSURE_CAPITAL_RESERVED')]
            bid=q.bids[0][0] if pos['side']==1 else q.asks[0][0];p=pos['proposal'];side=pos['side']
            stop=side*(bid-p['stop'])<=0;target=side*(bid-p['target'])>=0
            close=q.available_at.astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).strftime('%H:%M')>='15:10'
            mark=markout(pos['entry_quote'],q,side,pos['quantity'])
            if mark['status']=='QUOTED_BOUND_ONLY':
                marked=self.equity+mark['net_pnl'];self.peak=max(self.peak,marked);self.max_intraday_dd=min(self.max_intraday_dd,marked/self.peak-1)
                events.append(dict(status='HYPOTHETICAL_MARK',episode_id=pos['candidate'].get('episode_id'),marked_equity=marked,max_intraday_drawdown=self.max_intraday_dd))
            failure=pos.get('failure_exit_requested') is not None and q.available_at>pos['failure_exit_requested']
            if stop or target or close or failure or q.available_at>=pos['due']:
                if mark['status']!='QUOTED_BOUND_ONLY':self.halted=True;return events+[dict(status='UNRESOLVED_EXIT_CAPITAL_RESERVED',mark=mark)]
                self.equity+=mark['net_pnl'];self.position=None;self.halted=self.equity-self.opening<=-.01*self.opening
                events.append({**mark,'quote_bound_status':mark['status'],'status':'HYPOTHETICAL_CLOSED',
                    'reason':'STOP' if stop else 'TARGET' if target else 'THESIS_FAILURE' if failure else 'TIME_CUTOFF','equity':self.equity,
                    'episode_id':pos['candidate'].get('episode_id'),'quantity':pos['quantity'],'side':side,'entry_at':pos['entry_quote'].available_at})
        return events
    def thesis(self,f,at):
        p=self.position
        if not p or p['entry_quote'].key!=f['key']:return
        failed=f.get('imbalance_mean10') is not None and p['side']*f['imbalance_mean10']<=0 and p['side']*(f['mid']-p['entry_quote'].mid)<0
        if failed:
            p.setdefault('failure_since',at)
            if (at-p['failure_since']).total_seconds()>=3:p['failure_exit_requested']=at
        else:p.pop('failure_since',None)


class Evaluator:
    def __init__(self,plan,emit,gate=None):
        self.plan=plan;self.metadata={r['key']:r for r in plan['stocks']};self.features=FeatureBuffer();self.emit=emit;self.pending={};self.last_episode={};self.last_independent={};self.last_feature={};self.ledger=HypotheticalLedger(gate);self.context=lambda at:{}
        self.model=None
        self.selection_queue=[]
    def observe(self,q,observed_at=None):
        at=observed_at or q.available_at;status=self.features.add(q)
        if status!='accepted':self.emit(dict(kind='quote_quality',key=q.key,at=at,status=status));return
        if q.available_at>at:self.emit(dict(kind='quote_quality',key=q.key,at=at,status='NOT_YET_AVAILABLE_CLOCK_AHEAD'));return
        self.flush_selection(at)
        for event in self.ledger.observe(q):self.emit(dict(kind='shadow_ledger',key=q.key,at=at,**event))
        ident=(q.key,q.transport);remaining=[]
        for item in self.pending.get(ident,[]):
            if q.available_at<item['due']:remaining.append(item);continue
            lateness=(q.available_at-item['due']).total_seconds();eligible=q.valid_book and q.fresh(q.available_at) and lateness<=(2 if q.transport=='ws' else 10)
            self.emit(dict(kind='observed_outcome',episode_id=item['id'],horizon_seconds=item['horizon'],at=at,
                status='OBSERVED' if eligible else 'CENSORED_ENDPOINT',mid_return_bps=(q.mid/item['entry_mid']-1)*1e4 if eligible else None,
                net_quote_markout=markout(item['entry_quote'],q,item['side'],item['quantity']) if eligible and item['quantity']>0 else None))
        self.pending[ident]=remaining
        last=self.last_feature.get(ident)
        if last and (at-last).total_seconds()<1:return
        self.last_feature[ident]=at
        f=self.features.at(q.key,q.transport,at)
        if not f or q.key not in self.metadata:return
        self.ledger.thesis(f,at)
        clock=at.astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).strftime('%H:%M')
        if not '09:30'<=clock<='14:30':return
        for h in hypotheses(f):
            ident=(q.key,q.transport,h['family']);last=self.last_episode.get(ident)
            if last and (at-last).total_seconds()<30:continue
            self.last_episode[ident]=at
            independent=self.last_independent.get(q.key)
            eligible=independent is None or (at-independent).total_seconds()>=1800
            if eligible:self.last_independent[q.key]=at
            episode=hashlib.sha256((q.key+q.transport+h['family']+at.isoformat()).encode()).hexdigest()
            candidate=dict(episode_id=episode,key=q.key,at=at.isoformat(),features=f,nonoverlapping_within_stock=eligible,
                market_context=self.context(at),
                transport=q.transport,proposed_entry=q.asks[0][0] if h['side']==1 else q.bids[0][0],
                predictor_status='NOT_YET_TRAINED',predicted_net_bps=None,shared_capital=1_000_000,max_daily_entries=3,**h)
            anchor=(f['low60']-q.spread_bps*q.mid/1e4) if h['side']==1 else (f['high60']+q.spread_bps*q.mid/1e4)
            setup=proposed_size(q,h['side'],1_000_000,5_000,h['side']*(q.mid-anchor)/q.mid,f.get('volume60'),True,True)
            candidate.update(pre_entry_quote=asdict(q),illustrative_setup=setup,setup_is_nonactionable=True,
                proposed_stop=setup.get('stop'),proposed_target=setup.get('target'),risk_budget_rupees=5_000,
                metadata_execution_state=self.metadata[q.key].get('execution_state'),
                account_segments_verified=self.ledger.gate.get('account_segments_verified',False),short_execution_verified=self.ledger.gate.get('short_execution_verified',False))
            from .model import predict
            forecasts=predict(self.model,h['family'],f,at,h['side'])
            candidate['paired_model_predictions']=forecasts
            candidate['predicted_gross_bps']=forecasts.get('PVD')
            if setup.get('accepted'):
                cost=markout(q,q,h['side'],setup['quantity']);candidate['expected_quote_cost']=cost
                if forecasts.get('PVD') is not None and cost.get('status')=='QUOTED_BOUND_ONLY':candidate['predicted_net_bps']=forecasts['PVD']+cost['net_bps']
            if forecasts:candidate['predictor_status']='FROZEN_POSTTRAINING_PREDICTION'
            if self.ledger.gate.get('quality_pass') and self.ledger.gate.get('predictor_frozen'):
                self.selection_queue.append(candidate);candidate['shadow_decision']={'status':'QUEUED_ONE_SECOND_SELECTION'}
            else:candidate['shadow_decision']=self.ledger.candidate(candidate,q,self.metadata[q.key],at)
            self.emit(dict(kind='candidate',**candidate))
            qty=min(int(100000/q.asks[0][0]),int((f.get('volume60') or 0)*.01))
            self.emit(dict(kind='diagnostic_entry_cost',episode_id=episode,key=q.key,at=at,transport=q.transport,
                quantity=qty,cost=markout(q,q,h['side'],qty) if qty>0 else None,is_control=False))
            for horizon in HORIZONS:self.pending.setdefault((q.key,q.transport),[]).append(dict(id=episode,key=q.key,transport=q.transport,due=at+timedelta(seconds=horizon),horizon=horizon,entry_mid=q.mid,entry_quote=q,side=h['side'],quantity=qty))
            self.controls(candidate,q,at)
    def flush_selection(self,at):
        from .model import predict
        ready=[c for c in self.selection_queue if int(timestamp_for(c['at']))<int(at.timestamp())]
        self.selection_queue=[c for c in self.selection_queue if c not in ready]
        scored=[]
        for c in ready:
            q=next((q for q in reversed(self.features.data.get((c['key'],c['transport']),[])) if q.available_at<=at),None)
            f=self.features.at(c['key'],c['transport'],at)
            if not q or not f or not any(h['family']==c['family'] and h['side']==c['side'] for h in hypotheses(f)):
                self.emit(dict(kind='selection',episode_id=c['episode_id'],at=at,status='REJECTED_CONFIRMATION_EXPIRED'));continue
            forecasts=predict(self.model,c['family'],f,at,c['side']);updated={**c,'features':f,'predicted_gross_bps':forecasts.get('PVD')}
            volume=f.get('volume60') or 0;qty=min(int(100000/q.asks[0][0]),int(volume*.01),int(min(sum(v for _,v in q.asks),sum(v for _,v in q.bids))*.1))
            bound=markout(q,q,c['side'],qty) if qty>0 else {}
            score=updated['predicted_gross_bps']+bound['net_bps'] if updated['predicted_gross_bps'] is not None and bound.get('status')=='QUOTED_BOUND_ONLY' else float('-inf')
            scored.append((score,updated,q))
        for score,c,q in sorted(scored,key=lambda x:(-x[0],x[1]['key'],x[1]['family'])):
            if score==float('-inf'):
                self.emit(dict(kind='selection',episode_id=c['episode_id'],at=at,status='REJECTED_RANKING_COST_OR_FORECAST_UNAVAILABLE'));continue
            result=self.ledger.candidate(c,q,self.metadata[q.key],at)
            self.emit(dict(kind='selection',episode_id=c['episode_id'],at=at,ranking_net_bps=score if score!=float('-inf') else None,**result))
    def controls(self,candidate,q,at):
        from .model import predict
        target=self.metadata[q.key];matched=0
        for key in self.plan.get('controls',[]):
            if key==q.key:continue
            meta=self.metadata[key]
            if bool((meta.get('adv') or 0)>=1e9)!=bool((target.get('adv') or 0)>=1e9):continue
            f=self.features.at(key,q.transport,at)
            if not f or bool(f['mid']>=500)!=bool(q.mid>=500):continue
            observed=next((x for x in reversed(self.features.data.get((key,q.transport),[])) if x.available_at<=at),None)
            if observed is None:continue
            ident=hashlib.sha256((candidate['episode_id']+'|control|'+key).encode()).hexdigest()
            self.emit(dict(kind='matched_control',episode_id=ident,paired_to=candidate['episode_id'],key=key,at=at.isoformat(),
                transport=q.transport,side=candidate['side'],features=f,nonoverlapping_within_stock=False,not_a_trade=True,
                paired_model_predictions=predict(self.model,candidate['family'],f,at,candidate['side'])))
            quantity=min(int(100000/observed.asks[0][0]),int((f.get('volume60') or 0)*.01))
            self.emit(dict(kind='diagnostic_entry_cost',episode_id=ident,key=key,at=at,transport=q.transport,
                quantity=quantity,cost=markout(observed,observed,candidate['side'],quantity) if quantity>0 else None,is_control=True))
            for horizon in HORIZONS:self.pending.setdefault((key,q.transport),[]).append(dict(id=ident,key=key,transport=q.transport,due=at+timedelta(seconds=horizon),horizon=horizon,entry_mid=observed.mid,entry_quote=observed,side=candidate['side'],quantity=quantity))
            matched+=1
            if matched==2:break
        self.emit(dict(kind='control_coverage',episode_id=candidate['episode_id'],matched=matched,required=2,at=at))
    def close(self):
        from .common import now
        for items in self.pending.values():
            for item in items:self.emit(dict(kind='observed_outcome',episode_id=item['id'],horizon_seconds=item['horizon'],status='PENDING_UNCOLLECTED_FUTURE' if item['due']>now() else 'CENSORED_UNOBSERVED_ENDPOINT'))
        if self.ledger.position or self.ledger.pending:self.emit(dict(kind='shadow_ledger',at=now(),status='UNRESOLVED_AT_RECORDER_SHUTDOWN',capital_released=False))


def timestamp_for(value):
    from .features import timestamp
    return timestamp(value).timestamp()
