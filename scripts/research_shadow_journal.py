"""Idempotent observation/abstention journal for bounded quote captures. No broker orders.

This stores research decisions; it does not invent fills or reconstruct old quotes.
Optional signal JSON: {known_at, direction: 1|-1, rule, horizon_minutes:60}.
"""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'directional_research_phase2'
POLICY_VERSION='shadow-observation-v2'
FROZEN_RULES={
    'ema_trend|12_26_gap0.5|trend|afternoon|h60',
    'donchian|lookback20_buffer0|trend|afternoon|h60',
    'pullback|ema21_tolerance0.75|trend|afternoon|h60',
}


def timestamp(value):
    try:
        result=datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return result if result.tzinfo else None
    except (ValueError,TypeError):return None


def initialize(conn):
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS captures(capture_id TEXT PRIMARY KEY,captured_at TEXT NOT NULL,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS decisions(decision_id TEXT PRIMARY KEY,capture_id TEXT NOT NULL,instrument_key TEXT NOT NULL,
      decision TEXT NOT NULL,reasons TEXT NOT NULL,signal TEXT,quote TEXT NOT NULL,
      FOREIGN KEY(capture_id) REFERENCES captures(capture_id));
    ''')
    if 'policy_version' not in {r[1] for r in conn.execute('PRAGMA table_info(decisions)')}:
        conn.execute("ALTER TABLE decisions ADD COLUMN policy_version TEXT NOT NULL DEFAULT 'shadow-observation-v1'")
    conn.execute('PRAGMA foreign_keys=ON')


def record(conn,snapshot,signal=None):
    captured=timestamp(snapshot.get('captured_at'))
    if captured is None:raise ValueError('Timezone-aware capture time required')
    blob=json.dumps(snapshot,sort_keys=True,allow_nan=False);cid=hashlib.sha256(blob.encode()).hexdigest()
    inserted=conn.execute('INSERT OR IGNORE INTO captures VALUES(?,?,?)',(cid,captured.isoformat(),blob)).rowcount
    counts={};new=0
    for row in snapshot['rows']:
        contract=row['contract'];key=contract['instrument_key'];reasons=list(row.get('rejection_reasons',[]))
        if snapshot.get('market_status',{}).get('status')!='NORMAL_OPEN':reasons.append('market_not_normal_open')
        if not row.get('eligible_quote_proxy'):reasons.append('quote_proxy_not_eligible')
        for field in ['quote_age_seconds','last_trade_age_seconds']:
            age=row.get(field)
            if type(age) not in (int,float) or not -2<=age<=30:reasons.append(field+'_not_fresh')
        if not 0<float(row.get('bid',0))<=float(row.get('ask',0)):reasons.append('invalid_book')
        elif (float(row['ask'])-float(row['bid']))/((float(row['ask'])+float(row['bid']))/2)>.02:reasons.append('spread_above_two_percent')
        lot=int(contract.get('lot_size',0))
        if lot<=0 or min(float(row.get('bid_qty',0)),float(row.get('ask_qty',0)))<lot:reasons.append('insufficient_depth')
        # Exchange-depth event time is not established by HTTP response time/LTT.
        # Observation can be eligible for further review, never assumed executable.
        if signal is None:reasons.append('no_contemporaneous_signal')
        else:
            known=timestamp(signal.get('known_at'))
            if known is None or not 0<=(captured-known).total_seconds()<=60:reasons.append('signal_stale_or_future')
            direction=signal.get('direction')
            side=('CE' if direction==1 else 'PE' if direction==-1 else None) if type(direction) is int else None
            if contract.get('instrument_type')!=side:reasons.append('wrong_signal_side')
            if signal.get('rule') not in FROZEN_RULES or signal.get('horizon_minutes')!=60:reasons.append('unknown_signal_specification')
            if known and (known.second or known.microsecond or known.astimezone(timezone(timedelta(hours=5,minutes=30))).strftime('%H:%M') not in [f'{h:02d}:{m:02d}' for h in [13,14] for m in range(0,60,5) if (h==13 and m>=5) or (h==14 and m<=10)]):reasons.append('outside_frozen_entry_window')
            due=captured+timedelta(minutes=60)
            local_due=due.astimezone(timezone(timedelta(hours=5,minutes=30)))
            if local_due>local_due.replace(hour=15,minute=10,second=0,microsecond=0):reasons.append('actual_exit_after_research_cutoff')
            try:
                if date.fromisoformat(contract.get('expiry',''))<local_due.date():reasons.append('contract_expires_before_exit')
            except (TypeError,ValueError):reasons.append('invalid_contract_expiry')
        decision='abstain' if reasons else 'eligible_for_shadow_review'
        reasons=sorted(set(reasons));did=hashlib.sha256((POLICY_VERSION+'|'+cid+'|'+key+'|'+json.dumps(signal,sort_keys=True)).encode()).hexdigest()
        new+=conn.execute('INSERT OR IGNORE INTO decisions VALUES(?,?,?,?,?,?,?,?)',
            (did,cid,key,decision,json.dumps(reasons),json.dumps(signal) if signal else None,json.dumps(row,allow_nan=False),POLICY_VERSION)).rowcount
        counts[decision]=counts.get(decision,0)+1
    conn.commit()
    return {'capture_id':cid,'policy_version':POLICY_VERSION,'new_capture':bool(inserted),'new_decisions':new,'observed_decisions':counts,
            'fill_count':0,'limitation':'HTTP/LTT freshness does not establish exchange-depth event time; this is an observation journal without assumed fills.'}


def self_test():
    conn=sqlite3.connect(':memory:');initialize(conn)
    snap={'captured_at':'2026-11-09T08:00:00+00:00','market_status':{'status':'CLOSED'},'rows':[
        {'contract':{'instrument_key':'SYNTHETIC|1','instrument_type':'CE','lot_size':65,'expiry':'2026-11-17'},
         'bid':10,'ask':11,'bid_qty':65,'ask_qty':65,'eligible_quote_proxy':False,'rejection_reasons':['market_not_normal_open']}]}
    first=record(conn,snap);second=record(conn,snap)
    assert first['new_decisions']==1 and second['new_decisions']==0
    assert conn.execute('SELECT COUNT(*) FROM decisions').fetchone()[0]==1
    assert first['observed_decisions']=={'abstain':1} and first['fill_count']==0
    snap['market_status']['status']='NORMAL_OPEN';snap['rows'][0]['eligible_quote_proxy']=True;snap['rows'][0]['rejection_reasons']=[]
    record(conn,snap,{'known_at':'2026-11-09T09:00:00+00:00','direction':1,'rule':'fixture','horizon_minutes':60})
    reasons=json.loads(conn.execute('SELECT reasons FROM decisions ORDER BY rowid DESC LIMIT 1').fetchone()[0]);assert 'signal_stale_or_future' in reasons
    snap['captured_at']='2026-11-09T08:00:05+00:00';snap['rows'][0].update(ask=10.1,quote_age_seconds=5,last_trade_age_seconds=5)
    valid={'known_at':'2026-11-09T08:00:00+00:00','direction':1,'rule':sorted(FROZEN_RULES)[0],'horizon_minutes':60}
    result=record(conn,snap,valid);assert result['observed_decisions']=={'eligible_for_shadow_review':1} and result['fill_count']==0
    for change,reason in [({'direction':True},'wrong_signal_side'),({'rule':'invented'},'unknown_signal_specification'),({'known_at':'2026-11-09T08:00:01+00:00'},'outside_frozen_entry_window')]:
        record(conn,snap,{**valid,**change})
        reasons=json.loads(conn.execute('SELECT reasons FROM decisions ORDER BY rowid DESC LIMIT 1').fetchone()[0]);assert reason in reasons
    snap['captured_at']='2026-11-09T08:40:30+00:00';valid['known_at']='2026-11-09T08:40:00+00:00'
    record(conn,snap,valid)
    reasons=json.loads(conn.execute('SELECT reasons FROM decisions ORDER BY rowid DESC LIMIT 1').fetchone()[0]);assert 'actual_exit_after_research_cutoff' in reasons
    snap['rows'][0]['contract']['expiry']='nonsense';record(conn,snap,valid)
    reasons=json.loads(conn.execute('SELECT reasons FROM decisions ORDER BY rowid DESC LIMIT 1').fetchone()[0]);assert 'invalid_contract_expiry' in reasons
    conn.close();return {'idempotency_closed_future_rule_direction_bar_time_expiry_deadline_checks':'passed','synthetic_fixture_only':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--snapshot',type=Path);parser.add_argument('--signal',type=Path);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if args.self_test:print(json.dumps(self_test()));return
    path=args.snapshot or max(OUT.glob('option-forward-*.json'),key=lambda p:p.name)
    signal=json.loads(args.signal.read_text()) if args.signal else None
    snapshot=json.loads(path.read_text());conn=sqlite3.connect(OUT/'shadow-journal.sqlite3');initialize(conn)
    result=record(conn,snapshot,signal);conn.close();(OUT/'shadow-journal-summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
