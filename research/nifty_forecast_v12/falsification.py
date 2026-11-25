"""Bounded refit-and-select nulls, future sentinels and exact feature aliases."""
from .common import *
from .market import MAIN,registered,transform_market,separate_masks,common_history
from .phase import make_plan,fit_family,combinations as phase_laws
from .ensemble import CORE,distribution_keys,features as expert_features,solve_weights
from research.nifty_forecast_v11.engine import inputs
from research.nifty_forecast_v9.run_models import cohort_queries


def permute(values,h,seed):
    a=np.asarray(values)
    blocks=np.array_split(a,max(2,len(a)//h))
    rng=np.random.default_rng(seed)
    return np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])


def first_days(query):
    months=[g.iloc[0] for _,g in query.groupby(['split','fold'],sort=False)]
    result=[]
    for c in ['early','later']:
        selected=[r for r in months if r.split==c]
        result.extend(selected[i] for i in np.linspace(0,len(selected)-1,3,dtype=int))
    return result


def run():
    cfg,q_cfg=registered();cfg.update(q_cfg)
    names=['V12_RV_SCALE','V12_STRADDLE_SCALE','V12_IV_SCALE','V12_JOINT_IV','V12_EVENT_IV','P12_Q_PHYSICAL_MIX']
    save('null-registry.json',{'registered_at':now(),'code':sha(SRC/'falsification.py'),'draws':12,
          'market_family':names,'phases':'All eligible deterministic training phases, no phase preselected for null ranking',
          'ensemble_objectives':['brier','crps'],'test_origins':'First origin in three evenly spaced earlier and three later monthly refits per horizon.',
          'interpretation':'Fixed archived evaluation and statistical anchor. Representative matured-block label perturbations and re-selection, conditional on prior V1–V12 exposure.'})
    frames,_,state,price,broad,pos,loss=inputs()
    old=original_laws({MAIN})
    priced={(int(h),d):law for (h,k,d,e),law in bundle_entries(OUT/'laws/aligned-Q.npz') if k=='TRADE'}
    all_laws=distribution_keys()
    stress=[];checks=[];results=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv')
        a=matrix(f'features/{h}-TRADE.csv',OUT)
        qs={d:law for (k,d),law in priced.items() if k==h}
        q=cohort_queries(h)
        shared=[d for d in q.origin if all((h,n,d) in all_laws for n in CORE)]
        e=expert_features(all_laws,h,CORE,shared,y)
        for r in first_days(q):
            d=r.origin
            if not a.at[d,'surface_available']:continue
            stat=old[h,MAIN,d]
            t,pool=common_history(y,d,a,separate_masks(cfg['V12_IV_SCALE'],a,qs))
            p=pool[-252:];history=y.loc[p,'return'].to_numpy()
            actual=y.at[d,'return']
            base=stat.score(actual)
            p0=Distribution(history).score(actual)
            phase_spec={'frame':'native'}
            tr,inner,valid,all_mature,ic=make_plan(y,phase_spec,state,d,pos,h,loss)
            x=frames['native']
            available_ensemble=[k for k in shared if y.at[k,'endpoint']<d]
            for draw in range(-1,12):
                seed=SEED+ max(0,draw)*101+int(d.replace('-',''))
                for n in names:
                    s=cfg[n]
                    if s.get('density') and d not in qs:continue
                    mask=separate_masks(s,a,qs)
                    tt,_=common_history(y,d,a,mask)
                    if len(tt)<42:continue
                    yy=y.copy()
                    if draw>=0:yy.loc[tt,['return','volatility']]=permute(y.loc[tt,['return','volatility']].to_numpy(),h,seed)
                    law,_,_=transform_market(s,a,tt,[d],yy,h,[stat],qs,pd.DataFrame(),history,d)
                    sc=law[0].score(actual)
                    results.append({'family':'market recalibration','horizon':h,'cohort':r.split,'origin':d,'draw':draw,'model':n,
                                    'brier_gain':base['brier']-sc['brier'],'crps_gain':base['crps']-sc['crps']})
                a0=fit_family(x.loc[tr],y,x.loc[[d]],pos,h,d,state,seed if draw>=0 else None,phase_only=True)
                b0=fit_family(x.loc[inner],y,x.loc[valid],pos,h,ic,state,seed+13 if draw>=0 else None,phase_only=True)
                for i in sorted(set(a0['phases'])&set(b0['phases'])):
                    dist=phase_laws('phase',i,a0,b0,y,valid,history)[0]
                    sc=dist.score(actual)
                    results.append({'family':'deterministic phases','horizon':h,'cohort':r.split,'origin':d,'draw':draw,'model':f'phase {i}',
                                    'brier_gain':p0['brier']-sc['brier'],'crps_gain':p0['crps']-sc['crps']})
                if d not in e or len(available_ensemble)<20:continue
                yy=y.loc[available_ensemble,'return'].to_numpy()
                yy=permute(yy,h,seed) if draw>=0 else yy
                values=[]
                for day,target in zip(available_ensemble,yy):
                    v=dict(e[day])
                    if draw>=0:
                        v['direction']=int(target>0)
                        v['abs']=np.array([all_laws[h,n,day].w@abs(all_laws[h,n,day].a-target) for n in CORE])
                    values.append(v)
                equally=mixture([all_laws[h,n,d] for n in CORE]).score(actual)
                for mode in ['brier','crps']:
                    w,status=solve_weights(values,len(CORE),mode)
                    sc=mixture([all_laws[h,n,d] for n in CORE],w).score(actual)
                    results.append({'family':'ensemble weighting','horizon':h,'cohort':r.split,'origin':d,'draw':draw,'model':mode,
                                    'brier_gain':equally['brier']-sc['brier'],'crps_gain':equally['crps']-sc['crps']})
            spec=cfg['V12_IV_SCALE'];original=transform_market(spec,a,t,[d],y,h,[stat],qs,pd.DataFrame(),history,d)
            combined={**spec,'columns':spec['columns']+['zz_IV_AFFINE_COPY','zz_EARLY_RISK_COPY']}
            duplicated=a.assign(zz_IV_AFFINE_COPY=3+11*a.iv_nearest,zz_EARLY_RISK_COPY=1+9*a.rv21)
            future=a.copy()
            numeric=spec['columns']
            future.loc[future.index>d,numeric]*=-11
            altered=y.copy()
            forbidden=y.endpoint.isna()|y.endpoint.ge(d)
            altered.loc[forbidden,'return']=.40;altered.loc[forbidden,'volatility']=1.
            for label,s,features,labels in [('affine duplicate',combined,duplicated,y),('future information sentinel',spec,future,altered)]:
                laws,risk,_=transform_market(s,features,t,[d],labels,h,[stat],qs,pd.DataFrame(),history,d)
                np.testing.assert_allclose(original[0][0].a,laws[0].a,rtol=1e-10,atol=1e-10)
                np.testing.assert_allclose(original[0][0].w,laws[0].w,rtol=1e-10,atol=1e-10)
                np.testing.assert_allclose(original[1],risk,rtol=1e-10,atol=1e-10)
                checks.append({'horizon':h,'origin':d,'check':label,'maximum_atom_delta':np.max(abs(original[0][0].a-laws[0].a))})
            from research.nifty_forecast_v10.estimators import choose
            for j in range(10):
                sample=choose(t,min(85,len(t)),'random_blocks',state,d,SEED+j)
                ds,risk,_=transform_market(spec,a,sample,[d],y,h,[stat],qs,pd.DataFrame(),history,d)
                s0=ds[0].score(actual)
                stress.append({'horizon':h,'origin':d,'draw':j,'training_rows':len(sample),'sample':'|'.join(sample),
                               'p':s0['p'],'mean':s0['predicted_mean'],'brier':s0['brier'],'crps':s0['crps'],'width80':s0['width80'],'annualized_risk':risk[0]})
        print('Null falsification',h,len(results),flush=True)
    a=pd.DataFrame(results);report=[]
    for (family,h,c,draw),q in a.groupby(['family','horizon','cohort','draw']):
        for metric in ['brier_gain','crps_gain']:
            stat=q.groupby('model')[metric].mean().sort_values(ascending=False)
            report.append({'family':family,'horizon':h,'cohort':c,'draw':draw,'metric':metric,'winner':stat.index[0],
                           'best_gain':stat.iloc[0],'origins':q.origin.nunique(),'candidates':len(stat)})
    write('refit-null-origins.csv',a);write('refit-null-selected.csv',pd.DataFrame(report))
    write('market-timing-and-copy-sentinels.csv',pd.DataFrame(checks));write('market-training-perturbations.csv',pd.DataFrame(stress))


if __name__=='__main__':run()
