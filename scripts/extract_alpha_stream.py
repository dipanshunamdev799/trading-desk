"""Freeze targeted historical depth observations from the inherited local database."""
import hashlib,json,sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine,text
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'backend')]
from app.config import get_settings
OUT=ROOT/'artifacts'/'project_alpha';OLD=ROOT/'artifacts'/'directional_research';P2=ROOT/'artifacts'/'directional_research_phase2'


def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,default=str,allow_nan=False),encoding='utf-8')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    engine=create_engine(get_settings().database_url_sync)
    signals=pd.read_csv(OLD/'lab-selected-trades.csv')
    signals=signals[(signals.session>='2026-10-26')&(signals.session<='2026-10-29')&signals.strategy.str.startswith(('ema_trend|','donchian|','pullback|'))]
    universe={r['date']:r for r in json.loads((P2/'option-nse-retained-eod.json').read_text())}
    # Signal-time spot from completed historical bar; availability checked against received stream ticks separately.
    index=pd.DataFrame(json.loads((OLD/'nifty-upstox-5minute.json').read_text()));index['stamp']=pd.to_datetime(index.ts,utc=True);marks=dict(zip(index.stamp,index.close))
    selection=[]
    dump('stream-protocol.json',{'signal_count':len(signals),'policies':['ATM','one_step_ITM','one_step_OTM','abs_delta_0.4_0.6','abs_delta_0.6_0.8'],
        'expiry':'nearest captured expiry strictly after signal session; historical metadata must match prior completed NSE archive',
        'selection':'Latest received chain snapshot no later than decision, <=60 seconds old; choose by source spot close, compare available index tick. Delta from snapshot only.',
        'quote_time':'source_at is broadcast FRAME currentTs; received_at is actual local receipt. No exchange level-specific book event timestamp exists.',
        'selection_not_execution':'Source chain Greeks may be stale even when snapshot fresh; each provenance time is retained. Quote replays must validate LTT and individual source/receipt.',
        'source_signal_sha256':hashlib.sha256((OLD/'lab-selected-trades.csv').read_bytes()).hexdigest()})
    with engine.connect() as conn:
        for t in signals.to_dict('records'):
            at=pd.Timestamp(t['entry_at']).tz_convert('UTC');spot=float(marks[at-pd.Timedelta(minutes=5)])
            prior=max(day for day in universe if day<t['session']);u=universe[prior]
            chains=conn.execute(text('''SELECT DISTINCT ON (expiry) expiry,observed_at,payload,provenance FROM market_stream_chains
              WHERE underlying_key=:key AND observed_at<=:at AND observed_at>=:lower
              AND expiry>CAST(:day AS date) ORDER BY expiry,observed_at DESC'''),
              {'key':'NSE_INDEX|Nifty 50','at':at.to_pydatetime(),'lower':(at-pd.Timedelta(seconds=60)).to_pydatetime(),'day':t['session']}).mappings().all()
            if not chains:
                selection.append({**t,'status':'no_fresh_prior_chain'});continue
            c=min(chains,key=lambda r:r['expiry']);exp=str(c['expiry']);legname='call_options' if t['direction']==1 else 'put_options'
            priorcontracts={str(r[0]):r for ch in u['chains'] if ch['expiry']==exp for r in ch['contracts']}
            candidates=[]
            for row in c['payload']:
                leg=row.get(legname,{})
                key=leg.get('instrument_key','');token=key.split('|')[-1];metadata=priorcontracts.get(token)
                if metadata is None:continue
                strike=float(row.get('strike_price',metadata[1]));side='CE' if t['direction']==1 else 'PE'
                if float(metadata[1])!=strike or metadata[2]!=side:continue
                g=leg.get('option_greeks',{});delta=g.get('delta');iv=g.get('iv');p=leg.get('_provenance',{})
                candidates.append({'instrument_key':key,'token':token,'strike':strike,'expiry':exp,'option_type':side,'lot':int(metadata[4]),
                    'delta':float(delta) if delta is not None else None,'iv':float(iv) if iv is not None else None,
                    'greeks_at':p.get('greeks_at'),'iv_at':p.get('iv_at'),'greeks_source':p.get('greeks_source'),
                    'prior_volume':metadata[6],'prior_metadata_day':prior,'chain_observed_at':c['observed_at'].isoformat()})
            if not candidates:
                selection.append({**t,'status':'no_dated_contract_match'});continue
            atm=min(candidates,key=lambda r:(abs(r['strike']-spot),r['strike']))
            for policy in ['ATM','one_step_ITM','one_step_OTM','abs_delta_0.4_0.6','abs_delta_0.6_0.8']:
                eligible=candidates
                if policy=='ATM':chosen=atm
                elif policy in ['one_step_ITM','one_step_OTM']:
                    itm=policy=='one_step_ITM'
                    eligible=[r for r in candidates if ((r['strike']<atm['strike']) if t['direction']==1 else (r['strike']>atm['strike']))==itm and r['strike']!=atm['strike']]
                    chosen=min(eligible,key=lambda r:abs(r['strike']-atm['strike'])) if eligible else None
                else:
                    low,high=(.4,.6) if policy=='abs_delta_0.4_0.6' else (.6,.8)
                    eligible=[r for r in candidates if r['delta'] is not None and low<=abs(r['delta'])<=high and r['greeks_source']=='websocket' and r['greeks_at'] and pd.Timestamp(r['greeks_at'])<=at and (at-pd.Timestamp(r['greeks_at'])).total_seconds()<=30]
                    chosen=min(eligible,key=lambda r:(abs(abs(r['delta'])-(low+high)/2),r['strike'])) if eligible else None
                selection.append({**t,'policy':policy,'selection_spot':spot,**(chosen or {}),'status':'selected' if chosen else 'no_eligible_contract'})
    dump('stream-selection.json',selection)
    # Freeze each selected key/session once, bounding extraction to its required entry/exit window.
    chosen=pd.DataFrame([r for r in selection if r['status']=='selected']);counts=[]
    with engine.connect() as conn:
        for (key,day),g in chosen.groupby(['instrument_key','session']):
            start=pd.to_datetime(g.entry_at,utc=True).min()-pd.Timedelta(seconds=2)
            end=pd.to_datetime(g.exit_at,utc=True).max()+pd.Timedelta(seconds=10)
            path=OUT/f"stream-quotes-{key.split('|')[-1]}-{day}.json"
            if path.exists():quotes=json.loads(path.read_text())
            else:
                result=conn.execute(text('''SELECT source_at,received_at,feed_type,
                  payload->'fullFeed'->'marketFF'->'marketLevel'->'bidAskQuote' AS depth,
                  payload->'fullFeed'->'marketFF'->'ltpc' AS ltpc,
                  payload->'fullFeed'->'marketFF'->'optionGreeks' AS greeks,
                  payload->'fullFeed'->'marketFF'->>'iv' AS iv
                  FROM market_stream_ticks WHERE instrument_key=:key AND source_at BETWEEN :lo AND :hi
                  ORDER BY source_at,received_at'''),{'key':key,'lo':start.to_pydatetime(),'hi':end.to_pydatetime()}).mappings()
                quotes=[]
                for q in result:
                    depth=q['depth'] or [];best=depth[0] if depth else {};ltpc=q['ltpc'] or {}
                    quotes.append({'source_at':q['source_at'].isoformat(),'received_at':q['received_at'].isoformat(),'feed_type':q['feed_type'],
                        'bid':float(best.get('bidP',0)),'ask':float(best.get('askP',0)),'bid_qty':float(best.get('bidQ',0)),'ask_qty':float(best.get('askQ',0)),
                        'ltt':ltpc.get('ltt'),'ltp':ltpc.get('ltp'),'greeks':q['greeks'],'iv':q['iv'],'depth':depth,
                        'book_timestamp_verified':False,'timestamp_basis':'broadcast_frame_and_local_receipt'})
                path.write_text(json.dumps(quotes),encoding='utf-8')
            counts.append({'instrument_key':key,'session':day,'quotes':len(quotes),'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            print(key,day,len(quotes),flush=True)
    dump('stream-extraction-summary.json',{'signals':len(signals),'policies':len(selection),'selected':int(chosen.shape[0]),'source_windows':counts,
        'total_extracted_quote_rows':sum(r['quotes'] for r in counts),'rejections':pd.Series([r['status'] for r in selection]).value_counts().to_dict()})


if __name__=='__main__':main()
