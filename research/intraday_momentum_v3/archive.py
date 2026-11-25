"""Complete per-chunk archive coverage; read-only, bounded and resumable."""
import json,time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
import pandas as pd
from psycopg2 import sql
from .common import OUT,dump,base,now


def chunk_inventory(chunk):
    started=time.monotonic();name=chunk['chunk_name'];path=OUT/'archive-chunks'/(name+'.json')
    if path.exists():
        old=json.loads(path.read_text())
        if old.get('status')=='ok' and old.get('version')=='coverage-index-v3':return old
    try:
        with base.connection() as c:
            c.execute("SET LOCAL statement_timeout='600s'");c.execute("SET LOCAL work_mem='64MB'");c.execute('SET LOCAL max_parallel_workers_per_gather=0')
            c.execute('SET LOCAL enable_seqscan=off');c.execute('SET LOCAL enable_bitmapscan=off')
            query=sql.SQL("""WITH q AS (
              SELECT instrument_key,(source_at AT TIME ZONE 'Asia/Kolkata')::date AS session,source_at,received_at
              FROM {}.{}
            ) SELECT instrument_key,session,'ALL_RETAINED_STREAM_TYPES' AS feed_type,count(*) rows,min(source_at) first_source,max(source_at) last_source,
              min(received_at) first_received,max(received_at) last_received,
              count(DISTINCT source_at) source_times,
              count(*) FILTER(WHERE received_at-source_at>interval '5seconds') receipt_delay_over5s,
              count(*) FILTER(WHERE source_at-received_at>interval '5seconds') future_source_over5s,
              count(DISTINCT date_trunc('minute',source_at)) source_minutes,
              min(extract(epoch FROM received_at-source_at)) min_delay_s,
              max(extract(epoch FROM received_at-source_at)) max_delay_s,
              avg(extract(epoch FROM received_at-source_at)) mean_delay_s
              FROM q GROUP BY instrument_key,session ORDER BY session,instrument_key""").format(sql.Identifier(chunk['chunk_schema']),sql.Identifier(name))
            c.execute(query);rows=[dict(r) for r in c.fetchall()]
            # Materialized narrow PK sampling avoids reading ~50GB of JSON for
            # a coverage inventory. Every payload lookup uses its exact PK.
            sample_query=sql.SQL("""WITH s AS MATERIALIZED (
              SELECT source_at,instrument_key,received_at FROM {}.{}
              WHERE extract(milliseconds FROM source_at)::int % 1000 < 10)
              SELECT s.instrument_key,(s.source_at AT TIME ZONE 'Asia/Kolkata')::date AS session,
              x.feed_type,COALESCE(x.payload->>'requestMode','unknown') AS mode,
              jsonb_array_length(COALESCE(x.payload#>'{{fullFeed,marketFF,marketLevel,bidAskQuote}}','[]'::jsonb)) AS levels,
              count(*) sampled_rows FROM s CROSS JOIN LATERAL (
                SELECT feed_type,payload FROM {}.{} t WHERE t.source_at=s.source_at AND
                t.instrument_key=s.instrument_key AND t.received_at=s.received_at LIMIT 1) x
              GROUP BY s.instrument_key,session,x.feed_type,mode,levels""").format(sql.Identifier(chunk['chunk_schema']),sql.Identifier(name),sql.Identifier(chunk['chunk_schema']),sql.Identifier(name))
            c.execute(sample_query);sample=[dict(r) for r in c.fetchall()]
        result={'version':'coverage-index-v3','status':'ok','chunk':chunk,'checked_at':now().isoformat(),'rows':rows,'depth_sample':sample,'elapsed':time.monotonic()-started}
    except Exception as exc:result={'status':'failed','chunk':chunk,'error_type':type(exc).__name__,'elapsed':time.monotonic()-started}
    dump(path,result);print(name,result['status'],round(result['elapsed'],1),flush=True);return result


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with base.connection() as c:
        c.execute("SELECT chunk_schema,chunk_name,range_start,range_end,is_compressed FROM timescaledb_information.chunks WHERE hypertable_name='market_stream_ticks' ORDER BY range_start")
        chunks=[dict(r) for r in c.fetchall()]
    # Freeze membership to current chunks; no retrospective P&L or model search.
    all_results=[]
    with ThreadPoolExecutor(max_workers=1) as pool:
        for f in as_completed([pool.submit(chunk_inventory,c) for c in chunks]):all_results.append(f.result())
    rows=[r for result in all_results if result['status']=='ok' for r in result['rows']]
    if rows:
        frame=pd.DataFrame(rows);frame['session']=frame['session'].astype(str)
        # Chunk boundaries are UTC midnights; sum per instrument/session/type.
        sums=['rows','source_times','receipt_delay_over5s','future_source_over5s','source_minutes']
        matrix=frame.groupby(['instrument_key','session','feed_type'],as_index=False).agg({**{k:'sum' for k in sums},'first_source':'min','last_source':'max','first_received':'min','last_received':'max','min_delay_s':'min','max_delay_s':'max'})
        matrix['repeated_source_timestamps']=matrix.rows-matrix.source_times
        matrix['segment']=matrix.instrument_key.str.split('|',regex=False).str[0]
        matrix.to_csv(OUT/'archive-coverage.csv',index=False)
        sample=pd.DataFrame([r for result in all_results if result['status']=='ok' for r in result.get('depth_sample',[])])
        sample.to_csv(OUT/'archive-depth-type-sample.csv',index=False)
        summary=dict(archive_rows=int(matrix.rows.sum()),instruments=int(matrix.instrument_key.nunique()),sessions=sorted(matrix.session.unique()),
            segments=matrix.groupby('segment').rows.sum().astype(int).to_dict(),sampled_depth5_rows=int(sample.loc[sample.levels>=5,'sampled_rows'].sum()) if len(sample) else 0,sampled_depth30_rows=int(sample.loc[sample.levels>=30,'sampled_rows'].sum()) if len(sample) else 0,depth_sample_rows=int(sample.sampled_rows.sum()) if len(sample) else 0,
            equity_instruments=int(matrix.loc[matrix.segment.eq('NSE_EQ'),'instrument_key'].nunique()),source_receipt_delay_over5s=int(matrix.receipt_delay_over5s.sum()),
            repeated_source_timestamps=int(matrix.repeated_source_timestamps.sum()))
    else:summary={}
    dump(OUT/'archive-inventory.json',dict(checked_at=now().isoformat(),chunks=len(chunks),successful_chunks=sum(r['status']=='ok' for r in all_results),
        complete=all(r['status']=='ok' for r in all_results),summary=summary,failures=[r for r in all_results if r['status']!='ok'],
        limitation='Complete row/time coverage; depth fields sampled deterministically at timestamps with millisecond remainder<10, not inferred for all rows. Repeated timestamps are not necessarily duplicate payloads. A source-minute with any update is occupancy, not continuous quote completeness. Chunk boundaries can overlap a local minute; detailed ordered replay audits gaps and duplicates separately.'))
    print(json.dumps(summary,default=str,indent=2))

if __name__=='__main__':main()
