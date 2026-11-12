"""Replay frozen finalists with only demonstrated audit corrections; no selection."""
from pathlib import Path
import json,hashlib
from collections import defaultdict
import numpy as np
import pandas as pd
from scripts.diagnosis_audit import load_panel,journal_impact,dividend_corrections
from research.swing_discovery.signals import build_features,generate
from research.swing_discovery.diagnostics import summarize_run
from research.swing_diagnosis.audit_engine import simulate_many,execution_signature
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'artifacts/swing_discovery';OUT=ROOT/'artifacts/swing_diagnosis'

def main():
    p=load_panel()
    journal_impact(p,dividend_corrections())
    with np.load(OUT/'audit-dividend-corrected.npz') as a:p['dividend']=a['dividend'].copy()
    f=build_features(p);configs=[x['config'] for x in json.loads((OLD/'frozen-finalists.json').read_text())['finalists']]
    groups=defaultdict(list)
    for c in configs:groups[execution_signature(c)].append(c)
    stocks=np.flatnonzero(p['eligible']);rows=[];journals=OUT/'audit_corrected_journals';journals.mkdir(exist_ok=True)
    for stage,start,end in [('final','2026-05-10','2026-11-10'),('two_year','2024-11-10','2026-11-10')]:
        for group in groups.values():
            for offset in range(0,len(group),8):
                batch=group[offset:offset+8]
                result=simulate_many(p,[generate(p,c,f) for c in batch],batch,start,end,stocks=stocks,slippage_bps=5,cost_multiplier=1,keep_trades=True)
                for c in batch:
                    r=result[c['id']];s=summarize_run(r)
                    assert np.isclose(r['trades'].net_pnl.sum()/470+1e6,r['equity'].iloc[-1],atol=1e-6)
                    rows.append(dict(id=c['id'],family=c['family'],stage=stage,**s))
                    r['trades'].to_csv(journals/f'{c["id"]}-{stage}-trades.csv.gz',index=False)
                    pd.DataFrame({'equity':r['equity'],'return':r['returns']}).to_csv(journals/f'{c["id"]}-{stage}-equity.csv')
                    print(stage,c['family'],s['total_return_pct'],flush=True)
    df=pd.DataFrame(rows);df.to_csv(OUT/'audit-corrected-replay.csv',index=False)
    summary={stage:dict(rules=len(g),positive_rules=int(g.total_return_pct.gt(0).sum()),median_return_pct=g.total_return_pct.median(),max_return_pct=g.total_return_pct.max()) for stage,g in df.groupby('stage')}
    summary['scope']='48 frozen finalists only; same entries/params, no new selection. Correct multi-component dividends and actual same-day STT/stamp; retain planned overnight-risk/targets, economic ex-date accrual, flat brokerage and all original execution limitations. This reuses contaminated dates and does not newly validate robustness.'
    summary['original_panel_sha256']=hashlib.sha256((OLD/'daily-panel.npz').read_bytes()).hexdigest()
    (OUT/'audit-corrected-replay-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
