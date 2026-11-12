from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.swing_diagnosis.common import OUT,save
from research.swing_diagnosis.features import bootstrap,bh

def main():
    a=pd.read_csv(OUT/'exit-control-daily.csv');rows=[]
    for stage,g in a.groupby('stage'):
        for family,h in g.groupby('family'):
            x=h.pivot(index='day',columns='variant',values='net_return')
            for variant in x.columns.drop('base'):
                rows.append(dict(stage=stage,family=family,variant=variant,**bootstrap(100*(x[variant]-x['base']).to_numpy())))
    d=pd.DataFrame(rows);d['bh_q']=np.nan
    for stage,g in d.groupby('stage'):d.loc[g.index,'bh_q']=bh(g.p)
    d.to_csv(OUT/'exit-control-uncertainty.csv',index=False)
    rng=np.random.default_rng(52341);rows=[]
    for path in sorted((OUT/'portfolio-corrected_journals').glob('*risk_correlation-equity.csv')):
        x=pd.read_csv(path);r=x.equity.to_numpy()/np.r_[1e6,x.equity.to_numpy()[:-1]]-1;n=len(r)
        starts=rng.integers(0,n,size=(3000,int(np.ceil(n/10))));ix=((starts[:,:,None]+np.arange(10))%n).reshape(3000,-1)[:,:n]
        draws=(np.prod(1+r[ix],axis=1)-1)*100
        rows.append(dict(journal=path.name,return_pct=(x.equity.iloc[-1]/1e6-1)*100,ci95_low_pct=np.quantile(draws,.025),ci95_high_pct=np.quantile(draws,.975)))
    pd.DataFrame(rows).to_csv(OUT/'portfolio-uncertainty.csv',index=False)
    save('uncertainty-scope.json',dict(exit='3000 paired circular10session blocks of daily-return differences. BH across21 alternative-vs-reference tests per stage. Delta/interval describes sum of daily differences in percentage points, not an independently re-executed alternative strategy.',
      portfolio='3000 circular10session blocks of corrected risk+correlation account returns, compounded per draw. Conditional on realized selected rules/trade path; not a cash-simulation bootstrap, alpha test, or correction for all prior research.'))

if __name__=='__main__':main()
