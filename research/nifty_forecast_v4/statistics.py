"""Matched uncertainty and realistic independent-window power planning."""
import numpy as np
import pandas as pd
from scipy.stats import norm
from .common import *
from research.nifty_forecast_v3.experiment import nonoverlap,paired_ci

def intervals(matrix,h):
    n,k=matrix.shape
    if n<8*h:return [None]*k
    rng=np.random.default_rng(SEED);block=2*h;starts=rng.integers(0,n-block+1,(2000,int(np.ceil(n/block))))
    idx=(starts[:,:,None]+np.arange(block)).reshape(2000,-1)[:,:n]
    center=matrix.mean(axis=0);boot=matrix[idx].mean(axis=1);sd=boot.std(axis=0);sd[sd<1e-12]=1e-12
    critical=np.quantile(np.max(abs((boot-center)/sd),axis=1),.95)
    return [[float(m-critical*s),float(m+critical*s)] for m,s in zip(center,sd)]

def run():
    from .ledger import events
    if any(e['kind']=='PROTOCOL_FREEZE' for e in events(OUT/'prospective-ledger.jsonl')):raise ValueError('PROTOCOL_ALREADY_FROZEN: no retrospective threshold changes')
    dist=pd.read_csv(OUT/'distribution-predictions.csv');stress=pd.read_csv(OUT/'weekly-stress-predictions.csv');cal=pd.read_csv(OUT/'calibration-predictions.csv');_,_,v3=load()
    comparisons=[];power=[]
    for h in [5,21]:
        descriptors=[];deltas=[]
        g=dist[(dist.horizon==h)&(dist.split=='outer_exposed')]
        for metric in ['crps','brier','pinball','mae','bucket_brier']:
            pivot=g.pivot(index='origin',columns='model',values=metric).sort_index()
            for name in ['D01_regime_shrunk','D02_student_shrunk','D03_residual_shrunk']:
                delta=(pivot.D00_empirical-pivot[name]).to_numpy();deltas.append(delta);descriptors.append({'horizon':h,'type':'distribution','model':name,'metric':metric,'baseline':'D00_empirical'})
        if h==5:
            outer=v3[(v3.horizon==5)&(v3.split=='outer_exposed')];base=outer.pivot(index='origin',columns='model',values='brier').sort_index()
            for a,b in [('M05_lgbm','Z_reversion'),('M05_lgbm','A00_sector'),('A00_sector','Z_reversion')]:
                deltas.append((base[b]-base[a]).to_numpy());descriptors.append({'horizon':5,'type':'frozen_binary','model':a,'metric':'brier','baseline':b})
            for name,f in stress.groupby('model'):
                f=f.set_index('origin').reindex(base.index);delta=base.M05_lgbm-(f.p-f.outcome)**2;deltas.append(delta.to_numpy());descriptors.append({'horizon':5,'type':'stress','model':name,'metric':'brier','baseline':'M05_lgbm'})
            for (name,method),f in cal[cal.method!='RAW'].groupby(['model','method']):
                f=f.set_index('origin').reindex(base.index);delta=base[name]-(f.p-f.outcome)**2;deltas.append(delta.to_numpy());descriptors.append({'horizon':5,'type':'calibration','model':name+'|'+method,'metric':'brier','baseline':name})
        matrix=np.column_stack(deltas);sim=intervals(matrix,h)
        for row,delta,ci in zip(descriptors,deltas,sim):comparisons.append({**row,'n':len(delta),'mean_improvement':float(delta.mean()),'paired95':paired_ci(delta,h),'familywise95':ci,'family_contrasts':len(descriptors),'status':'EXPLORATORY_RESEARCH_EXPOSED'})
    # Planning uses disjoint paired losses. This is noisy pilot variance, not a power guarantee.
    for h,metric,model,base,effects in [(5,'brier','M05_lgbm','Z_reversion',[.01,.02,.02319]),(5,'brier','M05_lgbm','A00_sector',[.01,.02,.02319]),(5,'brier','A00_sector','Z_reversion',[.01,.02,.02319]),(21,'crps','D03_residual_shrunk','D00_empirical',[.001,.002,.005])]:
        data=(v3[(v3.horizon==h)&(v3.split=='outer_exposed')] if h==5 else dist[(dist.horizon==h)&(dist.split=='outer_exposed')])
        pivot=data.pivot(index='origin',columns='model',values=metric).sort_index();ends=data[data.model==model].set_index('origin').endpoint
        pilot=pd.DataFrame({'origin':pivot.index,'endpoint':ends.reindex(pivot.index).to_numpy(),'loss_delta':(pivot[base]-pivot[model]).to_numpy()});pilot=nonoverlap(pilot)
        sd=float(pilot.loss_delta.std(ddof=1));z=float(norm.ppf(1-.05/(2*4))+norm.ppf(.8))
        for effect in effects:
            for inflation in [1.,1.5]:power.append({'horizon':h,'metric':metric,'model':model,'baseline':base,'pilot_disjoint_n':len(pilot),'pilot_paired_sd':sd,'effect_target':effect,'sd_inflation':inflation,
                'required_disjoint_n':int(np.ceil((z*sd*inflation/effect)**2)),'power':.8,'family_alpha':.05,'primary_contrasts':4,
                'assumptions':'Normal approximation, stationary paired loss variance, disjoint outcomes approximately independent; tiny exposed pilot makes estimates uncertain'})
    save('v4-uncertainty.json',comparisons);save('power-assessment.json',power)
    final={str(h):max(r['required_disjoint_n'] for r in power if r['horizon']==h and r['effect_target']==(.01 if h==5 else .001) and r['sd_inflation']==1.5) for h in [5,21]}
    save('prospective-stop-rules.json',{'frozen_at':now(),'fixed_final_disjoint_n':final,'primary_family_size':4,'alpha':.05,
        'weekly_primary_metric':'Brier; three frozen matched comparisons','monthly_primary_metric':'CRPS D03 vs D00',
        'interims':'Descriptive only; no significance claims or activation from interim p-values',
        'qualification':'At fixed final N: simultaneous positive proper-score improvement; adequate calibration; stable subperiod signs; no leakage; noninferior log loss and no material coverage failure. No automatic deployment.',
        'coverage_gate':'Both 50% and80% coverage within10 percentage points of nominal on adequately sampled disjoint prospective outcomes; report Wilson intervals',
        'failure':'Missed clock/missing required source => skip; tamper/calendar/revision => halt for versioned review; never overwrite; source/model change => new registry and cohort',
        'scope_stop':'No input, target, or resolution outside2025–2026; freeze collection when any endpoint would enter2027',
        'feasibility':'Required samples exceed remaining2026 opportunities; NO DEPLOYMENT; future scope extension requires user instruction'})
    print('Uncertainty complete',len(comparisons),'contrasts; final planning Ns',final,flush=True)
if __name__=='__main__':run()
