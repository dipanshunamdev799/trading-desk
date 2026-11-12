"""Persisted-output and provenance checks for the completed Phase 2 research."""
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'directional_research_phase2'


def read(name):return json.loads((OUT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks=[];hash_checks=0
    for mapping in [read('option-manifest.json')['files'],read('feature-audit.json')['input_sha256'],read('long-preregister.json')['input_hashes']]:
        for name,expected in mapping.items():
            assert sha(ROOT/name)==expected,name
            hash_checks+=1
    assert sha(ROOT/'scripts'/'research_long_horizons.py')==read('long-preregister.json')['script_sha256']
    checks.append('All option/feature/long-horizon recorded source hashes match')
    controls=read('control-expanded-summary.json')
    assert controls['coverage']['sessions']==1196
    assert all(not r['passes_conditional6_gate'] for r in controls['primary'] if r['strategy']!='fixed_router')
    checks.append('Expanded controls coverage and conditional-gate claims reconcile')
    features=pd.read_csv(OUT/'feature-ablations.csv')
    assert len(features)==54 and (features.loc[features.split=='holdout','net2_ci_low']<=0).all()
    with sqlite3.connect(OUT/'feature-panel.sqlite') as conn:
        tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert any(conn.execute('SELECT COUNT(*) FROM "'+name+'"').fetchone()[0]==32518 for name in tables)
    checks.append('Context counts, SQLite panel and no-positive-lower-bound claim reconcile')
    premiums=pd.read_csv(OUT/'option-premium-trades.csv');s=read('option-premium-summary.json')
    good=premiums[premiums.status=='premium_proxy_observed']
    assert len(good)==424 and len(s['groups'])==16
    distinct=good.drop_duplicates(['strategy','signal_date','token','expiry','strike','option_type'])
    assert len(distinct)==374
    for r in s['groups']:
        g=good[(good.strategy==r['strategy'])&(good.expiry_bucket==r['expiry_bucket'])&(good.strike_rule==r['strike_rule'])]
        assert len(g)==r['n'] and np.isclose(g.illustrative_net_rupees_per_lot.mean(),r['illustrative_net_mean_rupees_per_lot'])
        assert r['net_ci95_rupees_per_lot'][0]<=0
    checks.append('Daily premium 424 policies/374 distinct outcomes/16 groups reconcile; none positive-lower-bound')
    intra=pd.read_csv(OUT/'option-intraday-trades.csv');accepted=intra[intra.status=='observed_candle_proxy']
    assert len(intra)==68 and len(accepted)==62
    assert ((pd.to_datetime(accepted.universe_date)<pd.to_datetime(accepted.session))).all()
    assert ((accepted.premium_exit-accepted.premium_entry)*accepted.lot-accepted.gross_rupees_per_lot).abs().max()<1e-7
    # Verify exposure counts and public report's small-sample warning.
    group=accepted.groupby(['strategy','expiry_bucket','strike_rule']).size()
    assert len(group)==12 and group.between(4,7).all()
    checks.append('Recent premium 68attempts/62outcomes, prior universes, exact gross PnL and small group counts reconcile')
    with sqlite3.connect(OUT/'shadow-journal.sqlite3') as conn:
        count=conn.execute("SELECT COUNT(*) FROM decisions WHERE policy_version='shadow-observation-v2'").fetchone()[0]
        abstain=conn.execute("SELECT COUNT(*) FROM decisions WHERE policy_version='shadow-observation-v2' AND decision='abstain'").fetchone()[0]
        assert count==abstain==8
        assert {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}=={'captures','decisions'}
    checks.append('Eight actual current-policy decisions are abstentions; no fill table exists')
    for name in ['NIFTY_RESEARCH_PHASE2.md','README.md']:
        for path in re.findall(r'\]\((C:/[^)]+)\)',(ROOT/name).read_text(encoding='utf-8')):assert Path(path).exists(),path
    checks.append('Report and README local links resolve')
    # Frozen source/output inventory. Exclude this mutable verification output/manifest themselves.
    paths=[ROOT/'NIFTY_RESEARCH_PHASE2.md',ROOT/'README.md',Path(__file__)]
    paths+=list((ROOT/'scripts').glob('*research*.py'))+list((ROOT/'scripts').glob('research_*.py'))
    paths+=list(OUT.rglob('*'))
    paths=sorted({p for p in paths if p.is_file() and p.name not in ['phase2-verification.json','phase2-manifest.json'] and p.suffix not in ['.pyc','-wal','-shm']})
    manifest={'research_date':'2026-11-09','files':{str(p.relative_to(ROOT)):sha(p) for p in paths}}
    (OUT/'phase2-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    result={'passed_groups':len(checks),'recorded_hashes_verified':hash_checks,'manifest_files':len(paths),'checks':checks}
    (OUT/'phase2-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
