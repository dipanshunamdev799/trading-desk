"""Current Upstox metadata reconciliation, with fail-closed execution status."""
from collections import Counter
import gzip,hashlib,json
import requests
from .common import OUT,base,dump,now,archive_response

URL='https://assets.upstox.com/market-quote/instruments/exchange/'


def reconcile(master,mis,suspended):
    master_eq={r['instrument_key']:r for r in master if r.get('segment')=='NSE_EQ' and r.get('instrument_type')=='EQ'}
    def identity(r):return (r.get('exchange'),r.get('segment'),r.get('instrument_type'),str(r.get('exchange_token')),r.get('instrument_key'))
    mids={identity(r) for r in mis};sids={identity(r) for r in suspended}
    skeys={r.get('instrument_key') for r in suspended}
    rows=[]
    for key,r in sorted(master_eq.items()):
        inmis=identity(r) in mids;insuspended=identity(r) in sids
        conflict=inmis and insuspended
        state='CONFLICT_QUARANTINE' if conflict else 'SUSPENDED_REPORTED' if insuspended else 'MIS_LISTED_CURRENT_ACCOUNT_UNVERIFIED' if inmis else 'NOT_MIS_LISTED'
        rows.append(dict(key=key,symbol=r.get('trading_symbol'),name=r.get('name'),security_type=r.get('security_type'),
            exchange_token=str(r.get('exchange_token')),instrument_type=r.get('instrument_type'),
            tick_size=r.get('tick_size'),lot_size=r.get('lot_size'),in_master=True,in_mis=inmis,in_suspended=insuspended,
            other_series_suspended=key in skeys and not insuspended,
            execution_state=state,observation_allowed=True,short_execution_verified=False))
    return rows


def main():
    directory=OUT/'metadata'/now().strftime('%Y%m%d-%H%M%S');directory.mkdir(parents=True,exist_ok=True)
    values={};audit=[]
    for name,file in [('master','NSE.json.gz'),('mis','NSE_MIS.json.gz'),('suspended','suspended-instrument.json.gz')]:
        url=URL+file
        try:
            r=requests.get(url,headers={'Cache-Control':'no-cache'},timeout=30);r.raise_for_status();raw=r.content
            payload=json.loads(gzip.decompress(raw));assert isinstance(payload,list)
            (directory/file).write_bytes(raw);values[name]=payload
            archive_response('intraday_v3.metadata.'+name,{'url':url},payload)
            audit.append(dict(kind=name,rows=len(payload),raw_sha256=hashlib.sha256(raw).hexdigest(),
                canonical_sha256=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(),
                source_url=url,last_modified=r.headers.get('Last-Modified'),etag=r.headers.get('ETag'),
                segments=dict(Counter(x.get('segment') for x in payload))))
        except Exception as exc:audit.append(dict(kind=name,error_type=type(exc).__name__))
    if set(values)!={'master','mis','suspended'}:
        dump(OUT/'metadata-audit.json',{'status':'INCOMPLETE','sources':audit});return
    rows=reconcile(values['master'],values['mis'],values['suspended'])
    dump(OUT/'metadata-reconciliation.json',rows)
    import pandas as pd
    pd.DataFrame(rows).to_csv(OUT/'metadata-reconciliation.csv',index=False)
    masterkeys={r.get('instrument_key') for r in values['master']};suspendedkeys={r.get('instrument_key') for r in values['suspended']}
    result=dict(checked_at=now().isoformat(),sources=audit,equity_keys=len(rows),states=dict(Counter(r['execution_state'] for r in rows)),
        master_suspended_identical_canonical=next(a['canonical_sha256'] for a in audit if a['kind']=='master')==next(a['canonical_sha256'] for a in audit if a['kind']=='suspended'),
        suspended_keys_in_current_master=len(masterkeys&suspendedkeys),suspended_key_count=len(suspendedkeys),
        interpretation='Instrument keys share ISINs across trading series. Compare current exchange/segment/type/token/key tuple, not key-only joins. Current MIS listing is not account activation, historical eligibility or guaranteed short execution.')
    dump(OUT/'metadata-audit.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
