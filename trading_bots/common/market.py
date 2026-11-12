from datetime import datetime,timedelta,timezone
import math,time
from .store import now


def stamp(value):
    if isinstance(value,(int,float)) or str(value).isdigit():return datetime.fromtimestamp(float(value)/(1000 if float(value)>1e11 else 1),timezone.utc)
    t=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError('Timestamp has no timezone')
    return t


def validate_quote(q,config,at):
    if not q.get('market_open'):raise ValueError('Market is not open; no fills')
    for field in ['captured_at','source_at','last_trade_at']:
        if not q.get(field) or not -1<=(at-stamp(q[field])).total_seconds()<=config['quote_max_age_seconds']:raise ValueError('Stale or undated '+field)
    if not all(math.isfinite(float(q.get(k,0))) for k in ['bid','ask','bid_qty','ask_qty']):raise ValueError('Invalid book numbers')
    if not 0<q['bid']<=q['ask']:raise ValueError('Missing or crossed bid/ask')
    if 100*(q['ask']-q['bid'])/((q['ask']+q['bid'])/2)>config['max_spread_percent']:raise ValueError('Spread exceeds limit')


class MarketData:
    def __init__(self):
        from app.services.upstox_service import get_upstox
        self.gateway=get_upstox();self.history=None;self.last_bucket=None;self.contract_cache=None
    def candles(self,at):
        local=at.astimezone(timezone(timedelta(hours=5,minutes=30)));bucket=int(at.timestamp())//300
        if self.history is None:
            p=self.gateway.get_historical_candles_v3('NSE_INDEX|Nifty 50','minutes',5,(local.date()-timedelta(days=1)).isoformat(),(local.date()-timedelta(days=27)).isoformat())
            self.history={r[0]:dict(zip(('ts','open','high','low','close','volume','oi'),r)) for r in p['candles']}
        if bucket!=self.last_bucket:
            p=self.gateway._remote_call('get_intraday_candles_v3','NSE_INDEX|Nifty 50','minutes',5)
            for r in p['candles']:self.history[r[0]]=dict(zip(('ts','open','high','low','close','volume','oi'),r))
            completed=[stamp(r[0]).timestamp()+300 for r in p['candles'] if stamp(r[0]).timestamp()+300<=at.timestamp()]
            if (completed and max(completed)>=bucket*300) or at.timestamp()-bucket*300>10:self.last_bucket=bucket
        return list(self.history.values())
    def select(self,side,spot,at):
        day=at.astimezone(timezone(timedelta(hours=5,minutes=30))).date().isoformat()
        if self.contract_cache is None or self.contract_cache[0]!=day:self.contract_cache=(day,self.gateway.get_option_contracts('NSE_INDEX|Nifty 50'))
        rows=[r for r in self.contract_cache[1] if r['expiry']>day and r['instrument_type']==('CE' if side==1 else 'PE')]
        if not rows:raise ValueError('No eligible dated option contracts')
        exp=min(r['expiry'] for r in rows);r=min((r for r in rows if r['expiry']==exp),key=lambda r:(abs(r['strike_price']-spot),r['strike_price']))
        return {'key':r['instrument_key'],'symbol':r.get('trading_symbol') or r.get('tradingsymbol') or r['instrument_key'],
            'exchange':'NSE_FO','expiry':r['expiry'],'strike':r['strike_price'],'option_type':r['instrument_type'],'lot':int(r['lot_size'])}
    def quote(self,key,at):
        session=self.gateway.get_market_session(key)
        # Direct quote request avoids treating retained cache receipt as a fresh observation.
        payload=self.gateway._remote_call('get_full_market_quotes_v2',[key]);captured=now()
        q=next((r for r in payload.values() if r.get('instrument_token')==key),{})
        depth=q.get('depth') or {};buys=depth.get('buy') or [];sells=depth.get('sell') or []
        b=buys[0] if buys else {};a=sells[0] if sells else {}
        return {'bid':float(b.get('price',0)),'ask':float(a.get('price',0)),'bid_qty':int(b.get('quantity',0)),
            'ask_qty':int(a.get('quantity',0)),'source_at':stamp(q['timestamp']).isoformat() if q.get('timestamp') else None,
            'last_trade_at':stamp(q['last_trade_time']).isoformat() if q.get('last_trade_time') else None,
            'captured_at':captured,'market_open':bool(session.get('active')),'timestamp_basis':'REST feed update and last trade; not verified book event time'}
