"""One bounded read-only quote capture for forward shadow research. No orders."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient

OUT=ROOT/'artifacts'/'directional_research_phase2'


def age_seconds(value, captured):
    try:
        if str(value).isdigit():
            t=pd.to_datetime(int(value),unit='ms',utc=True).to_pydatetime()
        else:t=pd.Timestamp(value).to_pydatetime()
        if t.tzinfo is None:return None
        return (captured-t).total_seconds()
    except (ValueError,TypeError,OverflowError):return None


def main():
    OUT.mkdir(exist_ok=True)
    client=UpstoxAnalyticsClient(get_settings().upstox_analytics_token,timeout=15,max_retries=0)
    contracts=client.get_option_contracts('NSE_INDEX|Nifty 50')
    index=client.get_full_market_quotes_v2('NSE_INDEX|Nifty 50')
    status=client.get_market_status('NSE')
    spot=float(next(iter(index.values()))['last_price'])
    today=pd.Timestamp.now(tz='Asia/Kolkata').date().isoformat()
    expiries=sorted({r['expiry'] for r in contracts if r['expiry']>=today})
    monthly=sorted({r['expiry'] for r in contracts if not r.get('weekly',False) and r['expiry']>=today})
    choices=[]
    for expiry in sorted(set(expiries[:1]+monthly[:1])):
        for side in ['CE','PE']:
            subset=[r for r in contracts if r['expiry']==expiry and r['instrument_type']==side]
            atm=min(subset,key=lambda r:(abs(r['strike_price']-spot),r['strike_price']))
            itm=[r for r in subset if (r['strike_price']<atm['strike_price'] if side=='CE' else r['strike_price']>atm['strike_price'])]
            near=min(itm,key=lambda r:abs(r['strike_price']-atm['strike_price'])) if itm else None
            choices.extend([atm]+([near] if near else []))
    quotes=client.get_full_market_quotes_v2([r['instrument_key'] for r in choices])
    try:greeks=client.get_option_greeks_v3([r['instrument_key'] for r in choices])
    except Exception as exc:greeks={'error_type':type(exc).__name__,'status':getattr(exc,'status_code',None)}
    captured=datetime.now(timezone.utc)
    rows=[]
    for contract in choices:
        quote=next((q for q in quotes.values() if q.get('instrument_token')==contract['instrument_key']),{})
        buys=(quote.get('depth') or {}).get('buy') or [];sells=(quote.get('depth') or {}).get('sell') or []
        bid=buys[0].get('price',0) if buys else 0;ask=sells[0].get('price',0) if sells else 0
        bid_qty=buys[0].get('quantity',0) if buys else 0;ask_qty=sells[0].get('quantity',0) if sells else 0
        quote_age=age_seconds(quote.get('timestamp'),captured);last_trade_age=age_seconds(quote.get('last_trade_time'),captured)
        reasons=[]
        if status.get('status')!='NORMAL_OPEN':reasons.append('market_not_normal_open')
        if quote_age is None or not -2<=quote_age<=30:reasons.append('quote_timestamp_not_fresh')
        if last_trade_age is None or not -2<=last_trade_age<=30:reasons.append('last_trade_not_fresh')
        if not 0<bid<=ask:reasons.append('missing_or_crossed_book')
        if min(bid_qty,ask_qty)<contract['lot_size']:reasons.append('insufficient_one_lot_depth')
        if bid>0 and (ask-bid)/((ask+bid)/2)>.02:reasons.append('spread_above_two_percent')
        rows.append({'contract':contract,'bid':bid,'ask':ask,'bid_qty':bid_qty,'ask_qty':ask_qty,
                     'quote_timestamp':quote.get('timestamp'),'last_trade_time':quote.get('last_trade_time'),
                     'quote_age_seconds':quote_age,'last_trade_age_seconds':last_trade_age,
                     'eligible_quote_proxy':not reasons,'rejection_reasons':reasons,'raw_quote':quote})
    snapshot={'captured_at':captured.isoformat(),'schema_version':1,'market_status':status,'underlying_quote':index,
              'contract_selection_spot':spot,'rows':rows,'greeks_response':greeks,
              'limitations':'HTTP quote timestamp may be response time; last trade age is a conservative freshness proxy, not a verified book event timestamp. No signal/order/fill is implied.'}
    path=OUT/('option-forward-'+captured.strftime('%Y%m%dT%H%M%SZ')+'.json')
    path.write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
    print(json.dumps({'snapshot':str(path.relative_to(ROOT)),'contracts':len(rows),'eligible_quote_proxies':sum(r['eligible_quote_proxy'] for r in rows),'market_status':status.get('status')}))


if __name__=='__main__':main()
