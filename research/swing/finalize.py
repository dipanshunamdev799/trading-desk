"""Reconcile uncertainty, gate diagnostics, source hashes, and the final report."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .validation import trade_uncertainty


def finalize(out: Path, root: Path):
    frozen=json.loads((out/'frozen-selection.json').read_text())
    summary=json.loads((out/'summary.json').read_text())
    final=pd.read_csv(out/'final-all-variants-descriptive.csv')
    selections=set(c['id'] for c in frozen['family_finalists'])|{frozen['fixed_baseline']}
    uncertainty={}
    for instrument in summary['instruments']:
        regular=pd.read_csv(out/f'{instrument.lower()}-5minute.csv',usecols=['ts'])
        special=pd.read_csv(out/f'{instrument.lower()}-special-execution.csv',usecols=['ts'])
        idx=pd.to_datetime(pd.concat([regular,special]).ts,utc=True).dt.tz_convert('Asia/Kolkata')
        idx=idx[(idx>=pd.Timestamp('2026-05-10',tz='Asia/Kolkata'))&(idx<pd.Timestamp('2026-11-10',tz='Asia/Kolkata'))]
        days=pd.DatetimeIndex(idx).normalize().unique().sort_values()
        for i in selections:
            path=out/f'finalists/{instrument}-{i}-final-trades.csv'
            trades=pd.read_csv(path) if path.exists() else pd.DataFrame()
            result=trade_uncertainty(trades,days)
            uncertainty[f'{instrument}/{i}']=result
            mask=(final.instrument==instrument)&(final.id==i)
            final.loc[mask,'r_ci95']=json.dumps(result['r_ci95'])
            final.loc[mask,'positive_probability']=result['positive_probability']
    final.to_csv(out/'final-all-variants-descriptive.csv',index=False)
    other=pd.read_csv(out/'development-validation.csv')
    pd.concat([other,final],ignore_index=True).to_csv(out/'all-period-metrics.csv',index=False)
    (out/'finalist-uncertainty.json').write_text(json.dumps(uncertainty,indent=2,allow_nan=False),encoding='utf-8')
    stress=pd.read_csv(out/'cost-stress.csv')
    adjusted=json.loads((out/'validation-search-control.json').read_text())
    wf=json.loads((out/'walkforward.json').read_text())
    wf_return=float(np.prod([1+x.get('total_return_pct',0)/100 for x in wf])-1) if wf else 0.
    gates=[]
    for c in frozen['family_finalists']:
        i=c['id'];primary=summary['primary']
        f=final[(final.instrument==primary)&(final.id==i)].iloc[0]
        s=stress[(stress.instrument==primary)&(stress.id==i)&(stress.stress=='severe')].iloc[0]
        bank=final[(final.instrument=='BANKBEES')&(final.id==i)]
        ci=uncertainty[f'{primary}/{i}']['r_ci95']
        row={'id':i,'development_validation_eligible':bool(c['eligible']),
             'final_min_20_trades':bool(f.n_trades>=20),
             'final_positive_expectancy':bool(pd.notna(f.expectancy_r) and f.expectancy_r>0),
             'ci_lower_above_zero':bool(ci[0] is not None and ci[0]>0),
             'validation_search_adjusted_p_le_005':bool(adjusted[i]['max_t_adjusted_p']<=.05),
             'severe_cost_positive_return':bool(s.total_return_pct>0),
             'bankbees_positive_min_10_trades':bool(len(bank) and bank.iloc[0].n_trades>=10 and bank.iloc[0].expectancy_r>0),
             'walkforward_policy_positive':bool(wf_return>0),
             'genuinely_fresh_holdout':False}
        row['all_historical_diagnostics_pass']=all(v for k,v in row.items() if k not in ['id','genuinely_fresh_holdout'])
        row['deployment_supported']=False
        gates.append(row)
    pd.DataFrame(gates).to_csv(out/'validation-gates.csv',index=False)
    environment=json.loads((out/'environment.json').read_text())
    sources=list((root/'research'/'swing').glob('*.py'))+[
        root/'scripts'/'run_swing_research.py',root/'scripts'/'extend_swing_evidence.py']
    environment['source_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.exists()}
    environment['statistical_calendar']='Regular and special execution sessions plus every observed trade-exit date; local IST dates'
    (out/'environment.json').write_text(json.dumps(environment,indent=2),encoding='utf-8')
    from .reporting import build_report
    build_report(out,root)
    return gates


if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]
    finalize(root/'artifacts'/'swing_research',root)
