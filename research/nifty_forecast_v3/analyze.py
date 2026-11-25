"""Matched comparisons, simultaneous block intervals and conditional diagnostics."""
import json
import numpy as np
import pandas as pd
from .audit import OUT,save
from .models import SEED,SPECS
from .experiment import summarize,nonoverlap,effective_n,paired_ci

TARGETS={'direction':'brier','return':'mae','distribution':'crps','volatility':'qlike','tail':'tail02_brier'}

def main():
    frame=pd.read_csv(OUT/'predictions.csv');comparisons=[];groups=[];selective=[];simult=[]
    for h in [5,21]:
        outer=frame[(frame.horizon==h)&(frame.split=='outer_exposed')]
        contrasts=[];names=[]
        for target,metric in TARGETS.items():
            pivot=outer.pivot(index='origin',columns='model',values=metric).sort_index()
            baseline_names=[c for c in pivot if c.startswith(('B','Z'))]
            best_fixed=min(baseline_names,key=lambda c:pivot[c].mean())
            for model in pivot:
                delta=pivot[best_fixed].to_numpy()-pivot[model].to_numpy()
                comparisons.append({'horizon':h,'target':target,'metric':metric,'model':model,
                    'strongest_fixed_baseline':best_fixed,'baseline_selected_on_outer':True,
                    'mean_improvement':float(delta.mean()),'paired_ci95':paired_ci(delta,h),
                    'research_only':bool(model in SPECS and SPECS[model]['research_only']),
                    'n':len(delta),'qualification':'EXPLORATORY_RESEARCH_EXPOSED'})
                contrasts.append(delta);names.append((target,model))
            model='S_'+target;base='C_'+target
            delta=pivot[base].to_numpy()-pivot[model].to_numpy()
            comparisons.append({'horizon':h,'target':target,'metric':metric,'model':model,
                'strongest_fixed_baseline':base,'baseline_selected_on_outer':False,
                'mean_improvement':float(delta.mean()),'paired_ci95':paired_ci(delta,h),
                'n':len(delta),'qualification':'NESTED_SELECTOR_RESEARCH_EXPOSED'})
        n=len(contrasts[0]);n_contrasts=len(contrasts)
        if n>=8*h:
            rng=np.random.default_rng(SEED);block=2*h
            starts=rng.integers(0,n-block+1,(2000,int(np.ceil(n/block))))
            ix=(starts[:,:,None]+np.arange(block)).reshape(2000,-1)[:,:n]
            means=np.array([d.mean() for d in contrasts]);boot=np.column_stack([d[ix].mean(axis=1) for d in contrasts])
            scale=np.std(boot,axis=0);scale[scale<1e-12]=1e-12
            maximum=np.max(np.abs((boot-means)/scale),axis=1);critical=float(np.quantile(maximum,.95))
            for j,(target,model) in enumerate(names):
                simult.append({'horizon':h,'target':target,'model':model,'contrasts_in_family':n_contrasts,
                    'mean_improvement':float(means[j]),'simultaneous_ci95':[float(means[j]-critical*scale[j]),float(means[j]+critical*scale[j])],
                    'interpretation':'Conditional familywise block interval across models AND target types; exposed history, not independent validation'})
        else:simult.append({'horizon':h,'status':'NOT_ESTIMATED','n':n,'minimum_origin_rows':8*h,'reason':'Too few monthly dependent observations'})
        for model in ['S_direction','S_return','S_distribution','S_volatility','S_tail','M05_lgbm','M01_ridge_full','A00_sector']:
            data=outer[outer.model==model].sort_values('origin')
            groups.append({'horizon':h,'model':model,'slice':'nonoverlap','metrics':summarize(nonoverlap(data)),
                'effective_size_note':'Disjoint return days do not guarantee statistical independence'})
            for variable in ['fold','regime','trend_regime','breadth_regime','expiry_regime','global_riskoff','large_prior_move']:
                for value,g in data.groupby(variable):groups.append({'horizon':h,'model':model,'slice':variable,'value':str(value),'metrics':summarize(g)})
            selected=data[data.selected_confident]
            base=outer[outer.model=='C_direction'].set_index('origin').reindex(selected.origin)
            selective.append({'horizon':h,'model':model,'coverage':float(len(selected)/len(data)),
                'selected_metrics':summarize(selected),'matched_baseline_metrics':summarize(base.reset_index()),
                'threshold':'Purged inner80th percentile abs(p-.5), floor .05; never selected from test outcomes'})
    save('paired-comparisons.json',comparisons);save('simultaneous-uncertainty.json',simult)
    save('conditional-diagnostics.json',groups);save('selective-forecasting.json',selective)
    # Matched ablations: full versus removals and current-basket inclusion.
    ablations=[]
    for h in [5,21]:
        data=frame[(frame.horizon==h)&(frame.split=='outer_exposed')]
        for metric in TARGETS.values():
            pivot=data.pivot(index='origin',columns='model',values=metric)
            for name in ['M00_ridge_price','A00_sector','A01_nofo','A02_proxy','A03_interact','M04_corr_ridge','M07_sequence']:
                delta=pivot[name]-pivot.M01_ridge_full
                ablations.append({'horizon':h,'metric':metric,'comparison':name,'full_context_improvement':float(delta.mean()),
                    'paired_ci95':paired_ci(delta,h),'proxy_cannot_validate_true_historical_breadth':name=='A02_proxy'})
    save('feature-family-ablations.json',ablations)
    print('Conditional and simultaneous uncertainty finished',len(comparisons),'paired comparisons',flush=True)
if __name__=='__main__':main()
