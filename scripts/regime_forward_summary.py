from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.regime_opportunities.framework import OUT,save

def main():
    a=pd.read_csv(OUT/'forward-contrasts-combined.csv');b=a[(a.horizon==10)&a.method.eq('nonoverlap20grid')];rows=[]
    for (regime,domain),g in b.groupby(['regime','domain']):
        index=domain not in ['stock_mean','stock_excess_N50','stock_positive_fraction'];stages=['index_development','index_validation','index_transfer'] if index else ['development','validation','final'];r=dict(regime=regime,domain=domain,history='multi_cycle_index' if index else 'recent_stock_cohort')
        for stage in stages:
            h=g[g.stage==stage]
            if len(h):r[stage+'_contrast_pct']=h.iloc[0].contrast_pct;r[stage+'_BH_q']=h.iloc[0].bh_q;r[stage+'_n_on']=h.iloc[0].n_on
        effects=[r.get(s+'_contrast_pct',np.nan) for s in stages];r['all_three_positive']=all(np.isfinite(x) and x>0 for x in effects);r['all_three_adjusted_positive']=r['all_three_positive'] and all(r.get(s+'_BH_q',1)<=.05 for s in stages)
        rows.append(r)
    pd.DataFrame(rows).to_csv(OUT/'regime-transfer-stability.csv',index=False)
    report=[]
    for (stage,method,h),g in a.groupby(['stage','method','horizon']):report.append(dict(stage=stage,method=method,horizon=h,tests=len(g),eligible=int(g.inference_eligible.sum()),BH_significant=int(g.bh_q.le(.05).sum()),BY_significant=int(g.BY_q.le(.05).sum())))
    pd.DataFrame(report).to_csv(OUT/'forward-testing-summary.csv',index=False)
    save('forward-summary.json',dict(contrasts=len(a),primary_horizon10_nonoverlap_tests=len(b),positive_primary_regime_domain_pairs_across_three_index_periods=sum(x['all_three_positive'] for x in rows if x['history']=='multi_cycle_index'),
      adjusted_positive_regime_domain_pairs_across_three_index_periods=sum(x['all_three_adjusted_positive'] for x in rows if x['history']=='multi_cycle_index'),
      primary_stock_limit='Fixed20sessiongrid onlyabout6datespervalidation/finalsegment, insufficient5on+5off forformaltests; descriptivecountsretainedinseparatefile.',
      domains='Nifty50/500/sectorTRI marketprediction; stockmean/positivefraction/excessN50 separatecohortquestions; noneprovesentrystrategyeffect.'))
    print('FORWARD_SUMMARY_COMPLETE')

if __name__=='__main__':main()
