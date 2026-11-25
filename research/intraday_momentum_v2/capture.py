"""Read-only primary feed recorder. Raw Upstox only in existing PG tables.

No order methods, DDL, bot configuration or shared application imports.
Derived features and recorder health events stay local. Errors never expose
authenticated redirect URLs, tokens or response headers.
"""
import asyncio
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import time
import uuid

from research.intraday_momentum import data as base
from .data import OUT


def now():return datetime.now(timezone.utc)
def feed_client():
    from upstox_analytics import UpstoxAnalyticsClient
    token=base._settings().upstox_trading_token.get_secret_value()
    # Even when available, this client exposes only market-data reads here.
    return UpstoxAnalyticsClient(analytics_token=token,timeout=15,max_retries=0) if token else base._client()
def epoch(value):
    try:
        v=float(value);return datetime.fromtimestamp(v/1000 if v>1e11 else v,timezone.utc)
    except (TypeError,ValueError,OverflowError,OSError):return None


def stale_instruments(watch,last_seen,at,threshold=15):
    return [{'key':key,'seconds_since_received':at-last_seen[key] if key in last_seen else None}
            for key in sorted(watch) if key not in last_seen or at-last_seen[key]>threshold]


def book_features(feed,received,current_ts):
    full=(feed.get('fullFeed') or {}).get('marketFF') or feed
    lt=full.get('ltpc') or feed.get('ltpc') or {}
    levels=(full.get('marketLevel') or {}).get('bidAskQuote') or []
    bids=[(float(x.get('bidP',0)),int(x.get('bidQ',0))) for x in levels if float(x.get('bidP',0))>0 and int(x.get('bidQ',0))>0]
    asks=[(float(x.get('askP',0)),int(x.get('askQ',0))) for x in levels if float(x.get('askP',0))>0 and int(x.get('askQ',0))>0]
    bid=max((x[0] for x in bids),default=None);ask=min((x[0] for x in asks),default=None)
    bq=sum(x[1] for x in bids);aq=sum(x[1] for x in asks);ts=epoch(current_ts);trade=epoch(lt.get('ltt'))
    return dict(levels=len(levels),best_bid=bid,best_ask=ask,
        spread_bps=(ask-bid)/((ask+bid)/2)*1e4 if bid and ask and ask>=bid else None,
        depth_imbalance=(bq-aq)/(bq+aq) if bq+aq else None,bid_quantity=bq,ask_quantity=aq,
        total_buy_quantity=full.get('tbq'),total_sell_quantity=full.get('tsq'),
        last_price=lt.get('ltp'),previous_close=lt.get('cp'),last_quantity=lt.get('ltq'),last_trade_at=trade.isoformat() if trade else None,
        traded_volume=full.get('vtt'),source_at=ts.isoformat() if ts else None,
        feed_stale=ts is None or not -5<=(received-ts).total_seconds()<=5,
        trade_stale=trade is None or not -5<=(received-trade).total_seconds()<=30,
        interpretation='Displayed-depth snapshots; no aggressor flags, cancellations or guaranteed executable liquidity')


def archive_rest(payload,keys,received):
    params=json.dumps({'instrument_keys':keys},sort_keys=True)
    key=hashlib.sha256(('intraday_v2.quotes'+params).encode()).hexdigest()
    with base.connection(write=True) as c:
        c.execute('INSERT INTO market_responses(recorded_at,request_key,method,parameters,payload) VALUES(%s,%s,%s,%s::jsonb,%s::jsonb) ON CONFLICT DO NOTHING',
            (received,key,'intraday_v2.get_full_market_quotes_v3',params,json.dumps(payload,allow_nan=False)))


def archive_frame(frame,received):
    ts=epoch(frame.get('currentTs'))
    if ts is None:return False
    with base.connection(write=True) as c:
        for key,feed in frame.get('feeds',{}).items():
            c.execute('INSERT INTO market_stream_ticks(source_at,instrument_key,received_at,feed_type,payload) VALUES(%s,%s,%s,%s,%s::jsonb) ON CONFLICT DO NOTHING',
                (ts,key,received,frame.get('type','unknown'),json.dumps(feed,allow_nan=False)))
    return True


async def probe_ws(client,key):
    import websockets
    from upstox_ws_v3 import UpstoxMarketDataWSV3
    result={'connection':'UNVERIFIED','full':'UNVERIFIED','full_d30':'UNVERIFIED','market_closed_update_cadence':'NOT_MEASURABLE'}
    try:
        uri=await asyncio.to_thread(client.get_market_data_feed_ws_url_v3)
        async with websockets.connect(uri,ping_interval=20,ping_timeout=10,open_timeout=15,max_size=None) as ws:
            result['connection']='VERIFIED'
            for mode in ('full','full_d30'):
                await ws.send(json.dumps({'guid':uuid.uuid4().hex,'method':'sub' if mode=='full' else 'change_mode','data':{'mode':mode,'instrumentKeys':[key]}}).encode())
                deadline=time.monotonic()+7;maxlevels=0;errors=0;frames=0
                while time.monotonic()<deadline:
                    try:raw=await asyncio.wait_for(ws.recv(),max(.01,deadline-time.monotonic()))
                    except asyncio.TimeoutError:break
                    frame=UpstoxMarketDataWSV3.decode_protobuf(raw) if isinstance(raw,bytes) else json.loads(raw)
                    if frame.get('feeds'):
                        await asyncio.to_thread(archive_frame,frame,now());frames+=1
                    for f in frame.get('feeds',{}).values():
                        maxlevels=max(maxlevels,book_features(f,now(),frame.get('currentTs'))['levels'])
                    if frame.get('status')=='error' or frame.get('error'):errors+=1
                result[mode]=dict(status='OBSERVED' if maxlevels>=(30 if mode=='full_d30' else 5) else 'UNVERIFIED',
                    max_observed_levels=maxlevels,frames=frames,error_messages=errors)
    except Exception as exc:result['error_type']=type(exc).__name__;result['status_code']=getattr(exc,'status_code',None)
    return result


def audit():
    plan=json.loads((OUT/'jobs-plan.json').read_text());keys=[s['instrument_key'] for s in plan['cohort']['stocks']]
    result={'checked_at':now().isoformat(),'read_only_market_endpoints':True,'real_orders_submitted':0}
    try:
        with base.connection() as c:
            c.execute("SET LOCAL statement_timeout='10s'")
            c.execute("SELECT interval,source,count(*) AS rows,count(DISTINCT instrument_key) AS keys,min(ts),max(ts) FROM public.candles WHERE instrument_key=ANY(%s) AND ts>='2024-07-01' GROUP BY interval,source",(keys+[base.NIFTY],))
            result['candle_inventory']=[dict(r) for r in c.fetchall()]
    except Exception as exc:result['candle_inventory']={'status':'AGGREGATE_UNAVAILABLE','error_type':type(exc).__name__,'alternative':'Daily frozen plan and per-request acquisition manifest retain coverage'}
    client=base._client()
    try:
        status=client.get_market_status('NSE');result['market_status']=status
    except Exception as exc:result['market_status']={'error_type':type(exc).__name__,'status_code':getattr(exc,'status_code',None)}
    try:
        quotes=client.get_full_market_quotes_v3(keys);archive_rest(quotes,keys,now())
        result['quotes']=dict(status='VERIFIED',instruments=len(quotes),fields=sorted({k for q in quotes.values() for k in q}),
            bid_levels=sorted({len(q.get('depth',{}).get('buy',[])) for q in quotes.values()}),
            ask_levels=sorted({len(q.get('depth',{}).get('sell',[])) for q in quotes.values()}),
            last_trade_times=sorted({str(q.get('last_trade_time')) for q in quotes.values()})[:3])
    except Exception as exc:result['quotes']={'error_type':type(exc).__name__,'status_code':getattr(exc,'status_code',None)}
    result['websocket']=asyncio.run(probe_ws(client,keys[0]))
    if result['websocket'].get('status_code')==401 and base._settings().upstox_trading_token.get_secret_value():
        result['websocket_with_access_credential']=asyncio.run(probe_ws(feed_client(),keys[0]))
    base.dump(OUT/'api-audit.json',result);print(json.dumps(result,default=str,indent=2))


async def record(seconds=60):
    import websockets
    from upstox_ws_v3 import UpstoxMarketDataWSV3
    plan=json.loads((OUT/'jobs-plan.json').read_text());keys=[s['instrument_key'] for s in plan['cohort']['stocks']]
    directory=OUT/'forward'/now().strftime('%Y%m%d-%H%M%S');directory.mkdir(parents=True)
    # No persistent service/scheduler; explicit bounded process, one owned connection.
    base.dump(directory/'manifest.json',dict(started_at=now().isoformat(),plan_sha256=base.sha(OUT/'jobs-plan.json'),
        seconds=seconds,scanner_keys=keys,rich_watchlist_max=20,mode='full',real_orders_submitted=0,
        source='PrimaryUpstox rawframes in existing PG market_stream_ticks; derived book/health local'))
    deadline=time.monotonic()+seconds;watch=set();latest={};generation=0;delay=1
    with gzip.open(directory/'derived-and-health.jsonl.gz','at',encoding='utf-8') as log:
        def emit(v):log.write(json.dumps({'observed_at':now().isoformat(),**v},allow_nan=False)+'\n');log.flush()
        while time.monotonic()<deadline:
            try:
                uri=await asyncio.to_thread(feed_client().get_market_data_feed_ws_url_v3)
                async with websockets.connect(uri,ping_interval=20,ping_timeout=10,open_timeout=15,max_size=None) as ws:
                    generation+=1;watch=set();latest={};last_seen={};last_health=0;emit({'event':'connected','generation':generation})
                    async def control(method,mode,ks):
                        await ws.send(json.dumps({'guid':uuid.uuid4().hex,'method':method,'data':{'mode':mode,'instrumentKeys':list(ks)}}).encode())
                    await control('sub','ltpc',keys);last_rotate=0
                    while time.monotonic()<deadline:
                        try:raw=await asyncio.wait_for(ws.recv(),min(5,max(.01,deadline-time.monotonic())))
                        except asyncio.TimeoutError:
                            emit({'event':'no_frame_5s','generation':generation,'silent_instruments':stale_instruments(watch,last_seen,time.monotonic())});continue
                        frame=UpstoxMarketDataWSV3.decode_protobuf(raw) if isinstance(raw,bytes) else json.loads(raw)
                        received=now();committed=await asyncio.to_thread(archive_frame,frame,received)
                        for key,feed in frame.get('feeds',{}).items():
                            f=book_features(feed,received,frame.get('currentTs'));latest[key]=f;last_seen[key]=time.monotonic()
                            emit({'event':'snapshot','key':key,'generation':generation,'raw_pg_committed':committed,**f})
                        if time.monotonic()-last_health>=5:
                            emit({'event':'instrument_health','silent_instruments':stale_instruments(watch,last_seen,time.monotonic()),'meaning':'Missing or quiet feed; not a proven exchange outage'})
                            last_health=time.monotonic()
                        if time.monotonic()-last_rotate>=30:
                            def score(k):
                                value=latest.get(k,{});lt=value.get('last_price')
                                cp=value.get('previous_close')
                                return abs(float(lt)/float(cp)-1) if lt and cp else 0
                            chosen=set(sorted(keys,key=lambda k:(-score(k),k))[:20])
                            if watch-chosen:await control('change_mode','ltpc',watch-chosen)
                            if chosen-watch:await control('change_mode','full',chosen-watch)
                            emit({'event':'watchlist','keys':sorted(chosen),'reason':'Largest observed absolute move; stable tie key;20controls when no move data'})
                            watch=chosen;last_rotate=time.monotonic()
            except Exception as exc:
                emit({'event':'disconnect_or_failure','error_type':type(exc).__name__,'generation':generation})
                if getattr(exc,'status_code',None)==401:
                    emit({'event':'ws_auth_unavailable_rest_snapshot_fallback','cadence_seconds':5})
                    while time.monotonic()<deadline:
                        try:
                            quotes=await asyncio.to_thread(base._client().get_full_market_quotes_v3,keys)
                            received=now();await asyncio.to_thread(archive_rest,quotes,keys,received)
                            for quote in quotes.values():
                                buy=quote.get('depth',{}).get('buy',[]);sell=quote.get('depth',{}).get('sell',[])
                                levels=[dict(bidP=buy[i].get('price',0) if i<len(buy) else 0,bidQ=buy[i].get('quantity',0) if i<len(buy) else 0,
                                    askP=sell[i].get('price',0) if i<len(sell) else 0,askQ=sell[i].get('quantity',0) if i<len(sell) else 0) for i in range(max(len(buy),len(sell)))]
                                proxy={'ltpc':{'ltp':quote.get('last_price'),'ltt':quote.get('last_trade_time'),'cp':quote.get('prev_close_price')},
                                    'marketLevel':{'bidAskQuote':levels},'tbq':quote.get('total_buy_quantity'),'tsq':quote.get('total_sell_quantity'),'vtt':quote.get('volume')}
                                # Conversion is derived/local only. Raw REST payload was archived verbatim.
                                source=quote.get('timestamp');ts=int(datetime.fromisoformat(source.replace('Z','+00:00')).timestamp()*1000) if isinstance(source,str) else None
                                emit({'event':'rest_snapshot','key':quote.get('instrument_token'),'transport':'rest_5second',**book_features(proxy,received,ts)})
                        except Exception as fallback:emit({'event':'rest_failure','error_type':type(fallback).__name__})
                        await asyncio.sleep(min(5,max(0,deadline-time.monotonic())))
                    break
                await asyncio.sleep(min(delay,max(0,deadline-time.monotonic())));delay=min(delay*2,30)
        emit({'event':'bounded_capture_finished','real_orders_submitted':0})
    print('Capture complete:',directory)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['audit','record']);p.add_argument('--seconds',type=int,default=60);args=p.parse_args()
    if args.mode=='audit':audit()
    else:asyncio.run(record(args.seconds))
