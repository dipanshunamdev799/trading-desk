"""Independent randomized-direction controls with full maturity/purging rules."""
import json
import numpy as np
import pandas as pd
from .audit import OUT,save
from .models import SPECS,train,predict,SEED
from .experiment import available,score_prediction,summarize,paired_ci

def main():
    x=pd.read_csv(OUT/'features.csv',index_col=0);results=[];records=[]
    for h in [5,21]:
        original=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0)
        for seed in [SEED,SEED+1,SEED+2]:
            labels=original.copy();rng=np.random.default_rng(seed)
            signs=rng.choice([-1,1],len(labels))
            labels['return']=labels['return'].abs()*signs
            labels['direction']=(labels['return']>0).astype(float)
            months={}
            for day in x.index:
                if day>='2026-07-01' and len(available(labels,day))>=126:months.setdefault(day[:7],[]).append(day)
            for month,query in months.items():
                tr=available(labels,query[0]);model=train(SPECS['M01_ridge_full'],x.loc[tr],labels.loc[tr])
                predictions=predict(model,x.loc[query])
                for day,p in zip(query,predictions):
                    if not np.isfinite(labels.loc[day,'return']):continue
                    records.append({'horizon':h,'seed':seed,'origin':day,'endpoint':labels.loc[day,'endpoint'],
                        'target':'independent randomized direction; volatility targets intentionally not randomized',**score_prediction(p,labels.loc[day])})
    frame=pd.DataFrame(records);frame.to_csv(OUT/'randomized-control-predictions.csv',index=False)
    for (h,seed),g in frame.groupby(['horizon','seed']):
        results.append({'horizon':int(h),'seed':int(seed),'metrics':summarize(g),
            'direction_improvement_ci95':paired_ci(.25-g.brier.to_numpy(),int(h)),
            'interpretation':'Negative control for direction only; no model selection from these results'})
    save('negative-controls.json',results)
    print('Randomized-target controls complete',len(results),flush=True)
if __name__=='__main__':main()
