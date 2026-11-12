"""New availability experiment: use provider Greeks actually received before entry.

Preserves the original chain-snapshot-only study and its zero eligible delta rows.
"""
import hashlib,json,sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine,text
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'backend')]
from app.config import get_settings
OUT=ROOT/'artifacts'/'project_alpha';P2=ROOT/'artifacts'/'directional_research_phase2'


def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,default=str,allow_nan=False),encoding='utf-8')


def main():
    protocol={'experiment':'DELTA-RECEIVED-V2','date':'2026-11-10',
        'why':'Original chain snapshot is collected about every60seconds; fresh streamGreeks may exist between chain captures.',
        'availability':'Latest instrument frame received<=decision, sourceclockoffsetwithin±1second, providerLTTage0–30sec, frameage<=30sec withsameclockqualification.',
        'universe':'Original datedchain/expiry; priorNSEmetadata; strikeswithin500points ofsignalspot. No futureGreek, premium or latercontractmaster.',
        'selection':'Fixedabsdelta.4–.6target.5 and.6–.8target.7; ATMcontrol unchanged. No outcome-based choice.',
        'limitation':'Provider modelGreeks as received, no independentlyverifiedGreekcalculationtimestamp; exploratory extension on inspectedhistory, not newholdout.',
        'quotes':'No exchange-book event clock; original frame-snapshot assumptions remain.',
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    dump('stream-delta-v2-protocol.json',protocol)
    original=json.loads((OUT/'stream-selection.json').read_text());archive={r['date']:r for r in json.loads((P2/'option-nse-retained-eod.json').read_text())}
    signatures={}
    for r in original:signatures.setdefault((r['strategy'],r['entry_at']),[]).append(r)
    engine=create_engine(get_settings().database_url_sync);result=[];sources=[]
    with engine.connect() as conn:
        for (strategy,entry),rows in signatures.items():
            atm=next((r for r in rows if r.get('policy')=='ATM'),None)
            if atm is None or atm['status']!='selected':
                for policy in ['ATM','abs_delta_0.4_0.6','abs_delta_0.6_0.8']:result.append({**rows[0],'policy':policy,'status':'no_fresh_prior_chain'})
                continue
            result.append(atm);at=pd.Timestamp(entry).tz_convert('UTC');exp=atm['expiry'];side=atm['option_type'];spot=atm['selection_spot']
            prior=archive[atm['prior_metadata_day']]
            contracts=[r for c in prior['chains'] if c['expiry']==exp for r in c['contracts'] if r[2]==side and abs(float(r[1])-spot)<=500 and r[6] and r[6]>0]
            eligible=[]
            for c in contracts:
                key='NSE_FO|'+str(c[0]);q=conn.execute(text('''SELECT source_at,received_at,payload->'fullFeed'->'marketFF'->'optionGreeks' AS greeks,
                  payload->'fullFeed'->'marketFF'->'ltpc' AS ltpc,payload->'fullFeed'->'marketFF'->>'iv' AS iv
                  FROM market_stream_ticks WHERE instrument_key=:key AND source_at BETWEEN :lo AND :hi AND received_at<=:at
                  ORDER BY source_at DESC,received_at DESC LIMIT1'''.replace('LIMIT1','LIMIT 1')),
                  {'key':key,'lo':(at-pd.Timedelta(seconds=30)).to_pydatetime(),'hi':(at+pd.Timedelta(seconds=1)).to_pydatetime(),'at':at.to_pydatetime()}).mappings().first()
                if q is None:continue
                delta=(q['greeks'] or {}).get('delta');ltt=(q['ltpc'] or {}).get('ltt')
                offset=(q['source_at']-q['received_at']).total_seconds()
                try:trade_age=(pd.Timestamp(q['source_at'])-pd.to_datetime(int(ltt),unit='ms',utc=True)).total_seconds()
                except (TypeError,ValueError):continue
                evidence={'strategy':strategy,'entry_at':entry,'instrument_key':key,'source_at':q['source_at'],'received_at':q['received_at'],'greeks':q['greeks'],'iv':q['iv'],'ltt':ltt,'offset_seconds':offset,'provider_trade_age_seconds':trade_age}
                sources.append(evidence)
                if not (-1<=offset<=1 and 0<=trade_age<=30 and delta is not None and 0<abs(float(delta))<=1 and ((float(delta)>0)==(side=='CE'))):continue
                eligible.append({**atm,'instrument_key':key,'token':str(c[0]),'strike':float(c[1]),'lot':int(c[4]),'delta':float(delta),'iv':float(q['iv']) if q['iv'] is not None else None,
                    'greeks_at':q['source_at'].isoformat(),'greeks_received_at':q['received_at'].isoformat(),'greeks_source':'received_provider_stream','prior_volume':c[6]})
            for policy,low,high in [('abs_delta_0.4_0.6',.4,.6),('abs_delta_0.6_0.8',.6,.8)]:
                pool=[r for r in eligible if low<=abs(r['delta'])<=high]
                choice=min(pool,key=lambda r:(abs(abs(r['delta'])-(low+high)/2),r['strike'])) if pool else None
                result.append({**(choice or atm),'policy':policy,'status':'selected' if choice else 'no_eligible_received_delta'})
    dump('stream-delta-v2-sources.json',sources);dump('stream-selection-delta-v2.json',result)
    chosen=pd.DataFrame([r for r in result if r['status']=='selected']);counts=[]
    with engine.connect() as conn:
        for (key,day),g in chosen.groupby(['instrument_key','session']):
            path=OUT/f"stream-quotes-{key.split('|')[-1]}-{day}.json"
            if path.exists():quotes=json.loads(path.read_text())
            else:
                lo=pd.to_datetime(g.entry_at,utc=True).min()-pd.Timedelta(seconds=2);hi=pd.to_datetime(g.exit_at,utc=True).max()+pd.Timedelta(seconds=10)
                rows=conn.execute(text('''SELECT source_at,received_at,feed_type,
                  payload->'fullFeed'->'marketFF'->'marketLevel'->'bidAskQuote' AS depth,
                  payload->'fullFeed'->'marketFF'->'ltpc' AS ltpc,payload->'fullFeed'->'marketFF'->'optionGreeks' AS greeks,
                  payload->'fullFeed'->'marketFF'->>'iv' AS iv FROM market_stream_ticks
                  WHERE instrument_key=:key AND source_at BETWEEN :lo AND :hi ORDER BY source_at,received_at'''),{'key':key,'lo':lo.to_pydatetime(),'hi':hi.to_pydatetime()}).mappings()
                quotes=[]
                for q in rows:
                    depth=q['depth'] or [];b=depth[0] if depth else {};ltpc=q['ltpc'] or {}
                    quotes.append({'source_at':q['source_at'].isoformat(),'received_at':q['received_at'].isoformat(),'feed_type':q['feed_type'],'bid':float(b.get('bidP',0)),'ask':float(b.get('askP',0)),
                        'bid_qty':float(b.get('bidQ',0)),'ask_qty':float(b.get('askQ',0)),'ltt':ltpc.get('ltt'),'ltp':ltpc.get('ltp'),'greeks':q['greeks'],'iv':q['iv'],'depth':depth,'book_timestamp_verified':False})
                path.write_text(json.dumps(quotes),encoding='utf-8')
            counts.append({'instrument_key':key,'day':day,'rows':len(quotes),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    dump('stream-delta-v2-extraction.json',{'opportunities':len(result),'selected':len(chosen),'status_counts':pd.Series([r['status'] for r in result]).value_counts().to_dict(),'sources':counts})
    print(json.dumps({'opportunities':len(result),'selected':len(chosen),'status_counts':pd.Series([r['status'] for r in result]).value_counts().to_dict()}))


if __name__=='__main__':main()
