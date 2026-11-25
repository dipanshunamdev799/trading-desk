"""Read-only audit of C0-R-X's saved paper decisions and auction evidence."""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime,timedelta
import csv,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from investment_bots.data import Inputs,IST,digest
from investment_bots.db import Session
from investment_bots.engine import advance
from investment_bots.catalog import DAY0
from research.intraday_momentum import data as base


class AuditDatabase:
    market_table='public.candles'
    @contextmanager
    def connection(self):
        with base.connection() as cursor:
            cursor.execute('SET LOCAL search_path TO investment_bots,public')
            yield Session(cursor.connection)


def main():
    source=Inputs(AuditDatabase());now=datetime.now(IST);directory=ROOT/'artifacts/investment_bots'/('c0rx-audit-'+now.date().isoformat())
    directory.mkdir(parents=True,exist_ok=True)
    with source.connection() as c:
        control=dict(c.execute("SELECT * FROM controls WHERE id='C0_R_X'").fetchone())
        kill=bool(c.execute('SELECT kill_switch FROM settings WHERE id=1').fetchone()[0])
        records=[dict(r) for r in c.execute("SELECT session,payload,sha256 FROM records WHERE bot_id='C0_R_X' ORDER BY session")]
        names={r['key']:json.loads(r['payload'])['symbol'] for r in c.execute('SELECT key,payload FROM instruments')}
        meta={r['key']:json.loads(r['payload']) for r in c.execute("SELECT key,payload FROM metadata WHERE key IN ('last_refresh','latest_integrity')")}
    assert all(digest(json.loads(r['payload']))==r['sha256'] for r in records),'Saved reference checksum mismatch'
    report=dict(checked_at=now.isoformat(),control=control,kill_switch=kill,record_checksums_match=True,
                last_refresh=meta.get('last_refresh'),last_integrity=meta.get('latest_integrity'),
                real_orders_submitted=0,production_writes=0,strategy_rules_changed=False)
    latest=json.loads(records[-1]['payload']) if records else None
    report.update(last_processed_session=latest['session'] if latest else None,metrics=latest['metrics'] if latest else None)
    if len(records)>=2:
        previous=json.loads(records[-2]['payload']);day=latest['session'];keys=list(dict.fromkeys(k for b in previous['books'] for k in
            [*b['holdings'],*(x['instrument_key'] for x in b['pending_buys']),*(x['instrument_key'] for x in b['pending_sells'])]))
        with source.connection() as c:
            rows=[dict(r) for r in c.execute('SELECT * FROM snapshots WHERE session=%s ORDER BY label',(day,))]
            bars=[dict(r) for r in c.execute("SELECT DISTINCT ON(instrument_key) instrument_key,open,close FROM public.candles WHERE interval='1day' AND source='upstox' AND instrument_key=ANY(%s) AND ts>=%s AND ts<%s ORDER BY instrument_key,ts DESC",
                    (keys,day+' 00:00+05:30',(datetime.fromisoformat(day)+timedelta(days=1)).date().isoformat()+' 00:00+05:30'))]
            sessions=[str(r[0]) for r in c.execute("SELECT DISTINCT (ts AT TIME ZONE 'Asia/Kolkata')::date FROM public.candles WHERE instrument_key='NSE_INDEX|Nifty 50' AND interval='1day' AND source='upstox' AND ts>=%s AND ts<%s ORDER BY 1",
                    (DAY0+' 00:00+05:30',(datetime.fromisoformat(day)+timedelta(days=1)).date().isoformat()+' 00:00+05:30'))]
        assert all(digest(json.loads(r['payload']))==r['sha256'] for r in rows),'Saved auction checksum mismatch'
        dec=next((r for r in reversed(rows) if r['label']<='09:05:00' and datetime.fromisoformat(r['received_at']).astimezone(IST).date().isoformat()==day
                  and datetime.fromisoformat(r['received_at']).astimezone(IST).strftime('%H:%M:%S.%f')<='09:05:00.000000'),None)
        final=next((r for r in rows if '09:12:00'<=r['label']<'09:15:00'),None)
        quotes=json.loads(dec['payload']).get('quotes',{}) if dec else {};details=[]
        for j,b in enumerate(previous['books']):
            for intent in b['pending_buys']:
                key=intent['instrument_key'];q=quotes.get(key,{})
                observed=next((x for x in latest['executions'] if x['instrument_key']==key and x['side']=='BUY' and x['book']==j),{})
                gate=source.evidence(day,key,intent['quantity'])
                details.append(dict(symbol=names.get(key,key),instrument_key=key,quantity=intent['quantity'],
                    decision_iep=q.get('indicative_equilibrium_price'),decision_ieq=q.get('indicative_equilibrium_quantity'),
                    decision_market_imbalance=q.get('indicative_imbalance_quantity_market'),source_timestamp=q.get('timestamp'),
                    gate=gate,saved_gate=observed.get('gate'),saved_status=observed.get('status'),matches=gate==observed.get('gate')))
        assert all(r['matches'] for r in details),'Stored classification differs from genuine archived evidence'
        offset=sessions.index(day)-sessions.index(DAY0)
        # A non-rebalance session can be replayed without refitting historical
        # signals: only the already-pinned intents and stored open/close matter.
        replay=None
        if offset%5 and len(previous['books'])==1:
            book,fills,intents=advance(previous['books'][0],day=day,offset=offset,opens={b['instrument_key']:b['open'] for b in bars},
                closes={b['instrument_key']:b['close'] for b in bars},scores={},instruments={},
                gate=lambda key,side,quantity:source.evidence(day,key,quantity))
            replay=book==latest['books'][0] and [dict(**x,book=0) for x in fills]==latest['executions'] and not intents
            assert replay,'Pure replay differs from the saved paper ledger'
        report.update(execution_session=day,previous_decision_session=previous['session'],initial_candidates=len(details),
            gate_counts=dict(Counter(x['gate'] for x in details)),all_classifications_match=True,pure_nonrebalance_replay_matches=replay,
            snapshot_count=len(rows),snapshot_checksums_match=True,
            decision_snapshot=dict(label=dec['label'],received_at=dec['received_at']) if dec else None,
            postmatch_snapshot=dict(label=final['label'],received_at=final['received_at']) if final else None,
            pending_buys=sum(len(b['pending_buys']) for b in latest['books']),pending_sells=sum(len(b['pending_sells']) for b in latest['books']),
            holdings=sum(len(b['holdings']) for b in latest['books']),offset_from_anchor=offset)
        with (directory/'candidate-gates.csv').open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(details[0]) if details else ['symbol']);writer.writeheader();writer.writerows(details)
    base.dump(directory/'audit.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='last_integrity'},indent=2,default=str))
    return report


if __name__=='__main__':main()
