"""Prespecified archive quality/execution bounds; no alpha or P&L search."""
from collections import Counter
from datetime import datetime,timedelta
import bisect,json
import numpy as np
import pandas as pd
from .common import OUT,base,dump
from .features import normalize
from .execution import depth_walk
from research.intraday_momentum.costs import fees


def quantiles(values):
    x=np.asarray([v for v in values if v is not None and np.isfinite(v)],float)
    return dict(zip(('min','p50','p95','p99','max'),map(float,np.quantile(x,[0,.5,.95,.99,1])))) if len(x) else None


def assess(quotes,day):
    quotes=sorted(quotes,key=lambda q:q.available_at);availability=[q.available_at.timestamp() for q in quotes]
    lo=pd.Timestamp(day+' 09:15',tz='Asia/Kolkata');hi=pd.Timestamp(day+' 15:10',tz='Asia/Kolkata')
    grid=pd.date_range(lo,hi,freq='s',inclusive='left');covered=0;spreads=[];costs=[];latencies=[]
    duplicate=len(quotes)-len({(q.source_at,q.fingerprint) for q in quotes})
    for at in grid:
        j=bisect.bisect_right(availability,at.timestamp())-1
        if j>=0 and quotes[j].valid_book and quotes[j].fresh(at.to_pydatetime()):covered+=1
    for at in pd.date_range(lo,hi-pd.Timedelta(seconds=10),freq='30s'):
        j=bisect.bisect_right(availability,at.timestamp())-1
        if j<0:continue
        q=quotes[j]
        if not q.valid_book or not q.fresh(at.to_pydatetime()):continue
        spreads.append(q.spread_bps)
        for capital in (100000,500000,1000000):
            qty=int(capital/q.asks[0][0]);a=depth_walk(q.asks,qty);b=depth_walk(q.bids,qty)
            full=not a['unfilled'] and not b['unfilled'];cost=None
            if full:
                charges=fees('BUY',a['price_bound'],qty)['total']+fees('SELL',b['price_bound'],qty)['total']
                cost=((a['price_bound']-b['price_bound'])*qty+charges)/(a['price_bound']*qty)*1e4
            costs.append(dict(capital=capital,full_quote_depth=full,quoted_roundtrip_bps=cost,unfilled_entry=a['unfilled'],unfilled_exit=b['unfilled']))
        for delay in (.1,.5,1,5):
            target=at.timestamp()+delay;k=bisect.bisect_left(availability,target)
            if k>=len(quotes):continue
            later=quotes[k];wait=availability[k]-target;identified=wait<=(.2 if delay<=1 else 1) and later.valid_book and later.fresh(later.available_at)
            latencies.append(dict(delay_seconds=delay,identified=identified,wait_seconds=wait,
                buy_adverse_bps=(later.asks[0][0]/q.asks[0][0]-1)*1e4 if identified else None,
                sell_adverse_bps=(q.bids[0][0]/later.bids[0][0]-1)*1e4 if identified else None))
    capacity=[]
    for capital in (100000,500000,1000000):
        cs=[r for r in costs if r['capital']==capital]
        capacity.append(dict(capital=capital,observations=len(cs),full_depth_fraction=np.mean([r['full_quote_depth'] for r in cs]) if cs else None,
            quoted_roundtrip_bps=quantiles([r['quoted_roundtrip_bps'] for r in cs]),depth_fraction_assumption=.1))
    cadence=[]
    for delay in (.1,.5,1,5):
        ls=[r for r in latencies if r['delay_seconds']==delay]
        cadence.append(dict(delay_seconds=delay,observations=len(ls),identified_fraction=np.mean([r['identified'] for r in ls]) if ls else None,
            buy_adverse_bps=quantiles([r['buy_adverse_bps'] for r in ls]),sell_adverse_bps=quantiles([r['sell_adverse_bps'] for r in ls])))
    return dict(updates=len(quotes),exact_source_payload_duplicates=duplicate,valid_books=sum(q.valid_book for q in quotes),
        grid_seconds=len(grid),fresh_valid_grid_fraction=covered/len(grid),
        receipt_minus_source_seconds=quantiles([(q.received_at-q.source_at).total_seconds() for q in quotes]),
        interarrival_seconds=quantiles(np.diff(availability)),gaps_over2s=int((np.diff(availability)>2).sum()),
        spread_bps=quantiles(spreads),capacity=capacity,latency_observation_bounds=cadence,
        interpretation='Retained, research-exposed archive quality and quoted capacity bounds only; no realized order fills or strategy profitability')


def main():
    matrix=pd.read_csv(OUT/'archive-coverage.csv');eq=matrix[matrix.segment.eq('NSE_EQ')]
    v2=json.loads((base.ROOT/'artifacts/intraday_momentum_v2/jobs-plan.json').read_text());ranking=v2['ranking'];liquidity={r['instrument_key']:r['freeze_adv'] for r in ranking}
    core={r['instrument_key'] for r in v2['cohort']['stocks']};keys=set(eq.instrument_key)
    chosen=sorted(keys&core,key=lambda k:(-liquidity.get(k,0),k))[:5]+sorted(keys-core,key=lambda k:(-liquidity.get(k,0),k))[:5]
    selected=[]
    for key in chosen:
        rows=eq[eq.instrument_key.eq(key)&(eq.source_minutes>=300)].sort_values('session').tail(2)
        for r in rows.to_dict('records'):selected.append({'key':key,'day':r['session'],'group':'v2_core' if key in core else 'outside_v2_core'})
    freeze=OUT/'quality-selection.json'
    if freeze.exists():assert json.loads(freeze.read_text())['selected']==selected
    else:dump(freeze,dict(rule='First5 highest pre2025liquidity archived core +5outsidecore; latest2sessions with>=300source minutes; no performance selection',selected=selected))
    results=[]
    for item in selected:
        path=OUT/'quality-days'/(item['key'].replace('|','_')+'-'+item['day']+'.json')
        if path.exists():results.append(json.loads(path.read_text()));continue
        with base.connection() as c:
            c.execute("SET LOCAL statement_timeout='60s'")
            c.execute("SELECT source_at,received_at,payload FROM market_stream_ticks WHERE instrument_key=%s AND source_at>=%s AND source_at<%s ORDER BY received_at,source_at",(item['key'],item['day']+' 09:15+05:30',item['day']+' 15:10+05:30'))
            rows=c.fetchall()
        quotes=[normalize(item['key'],r['payload'],r['source_at'],r['received_at']) for r in rows];quotes=[q for q in quotes if q]
        result={**item,**assess(quotes,item['day'])};dump(path,result);results.append(result)
        print('Quality',item['key'],item['day'],len(quotes),flush=True)
    dump(OUT/'detailed-quality.json',dict(stock_days=len(results),keys=len(chosen),results=results,fresh_forward_sessions=0))
    pd.DataFrame([{k:v for k,v in r.items() if k not in ('capacity','latency_observation_bounds')} for r in results]).to_csv(OUT/'detailed-quality.csv',index=False)
    coverage=dict(total_archive_equity_keys=len(keys),inside_v2=len(keys&core),outside_v2=len(keys-core),selected_quality_stock_days=len(selected),
        limitation='Detailed payload quality is a prespecified subset; complete time/row coverage matrix includes every retained instrument/session.')
    dump(OUT/'universe-archive-comparison.json',coverage);print(json.dumps(coverage))

if __name__=='__main__':main()
