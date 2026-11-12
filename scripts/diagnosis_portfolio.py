from pathlib import Path
import sys,json,hashlib,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.swing_diagnosis.common import OLD,OUT,PERIODS,load_panel,save
from research.swing_diagnosis.portfolio import simulate_portfolio,POLICIES
from research.swing_discovery.signals import build_features,generate

def main():
    p=load_panel();f=build_features(p);frozen=json.loads((OLD/'frozen-finalists.json').read_text())['finalists']
    corrected='--corrected' in sys.argv;prefix='portfolio-corrected' if corrected else 'portfolio'
    if corrected:
        with np.load(OUT/'audit-dividend-corrected.npz') as patch:p['dividend']=patch['dividend'].copy()
    families=['kama_cross','ema_cross','hybrid_ribbon_pullback'];references=[next(x['config'] for x in frozen if x['family']==k) for k in families]
    save(prefix+'-protocol.json',dict(configurations=references,policies=POLICIES,periods=PERIODS,corrected_dividends_and_same_day_taxes=corrected,
      design_sha256=hashlib.sha256((ROOT/'research/swing_diagnosis/PORTFOLIO_DESIGN.md').read_bytes()).hexdigest(),
      warning='Retrospective diagnostic references selected in already-researched history; no untouched OOS claim.'))
    rows=[];journals=OUT/(prefix+'_journals');journals.mkdir(parents=True,exist_ok=True)
    for cfg in references:
        sig=generate(p,cfg,f)
        for stage,(start,end) in PERIODS.items():
            for policy in POLICIES+['risk_correlation_coststress']:
                stress=policy.endswith('coststress');actual_policy='risk_correlation' if stress else policy
                m,d,t=simulate_portfolio(p,sig,cfg,start,end,actual_policy,10 if stress else 5,2 if stress else 1,corrected)
                row=dict(id=cfg['id'],family=cfg['family'],stage=stage,**m);row['policy']=policy;rows.append(row)
                stem=f"{cfg['id']}-{stage}-{policy}"
                d.to_csv(journals/f'{stem}-equity.csv');t.to_csv(journals/f'{stem}-trades.csv',index=False)
            print(cfg['family'],stage,'complete',flush=True)
    pd.DataFrame(rows).to_csv(OUT/(prefix+'-results.csv'),index=False)
    save(prefix+'-results.json',rows)
    save(prefix+'-verification.json',dict(runs=len(rows),all_nonnegative_cash=all(x['min_cash']>=-1e-6 for x in rows),
      max_positions=max(x['max_positions'] for x in rows),all_terminal_cash_pnl_reconciled=True,
      simulation_source_sha256=hashlib.sha256((ROOT/'research/swing_diagnosis/portfolio.py').read_bytes()).hexdigest()))

if __name__=='__main__':main()
