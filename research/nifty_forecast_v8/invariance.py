"""Intervene on representation while keeping market observations fixed."""
from sklearn.linear_model import Ridge
import warnings
from .common import *
from .models import fit, location, predict
from .experiments import frames, queries, cutoff_dates, row


def transformed(x,names,variant):
    if variant=='as_is':return x
    if variant=='reordered':return x[x.columns[::-1]]
    if variant=='equivalent_units':return x.assign(**{n:x[n]*100+3 for n in names})
    if variant=='equivalent_formula':return x.assign(**{n:(x[n]+3)/4 for n in names})
    count=3 if variant in ['three_copies','balanced_three'] else 1
    copies={f'zz_alias{j}_{n}': x[n]*(100 if variant=='affine_copy' else 1)+(3 if variant=='affine_copy' else 0)
            for j in range(count) for n in names}
    return pd.concat([x,pd.DataFrame(copies,index=x.index)],axis=1)


def fitted(spec,x,y,names,variant):
    obj=fit(spec,x,y)
    if variant=='balanced_three':
        # Divide standardized original and three copies by sqrt(4).
        focus=[j for j,n in enumerate(obj['scale'].cols) if n in names or n.startswith('zz_alias')]
        obj['transform'][focus,focus]/=2
        design=obj['scale'].transform(x)@obj['transform']
        obj['estimator']=Ridge(alpha=100).fit(design,y)
    return obj


def run(sector_alias=False):
    x,_=frames();native=x['native'];names=[c for c in native if any(s in c for s in ['nifty_fmcg','nifty_pharma','NIFTY_HEALTHCARE'])]
    variants=['as_is','one_copy','three_copies','reordered','equivalent_units','affine_copy','equivalent_formula']
    methods={'ridge':{},'elastic':{'kind':'elastic'},'cluster':{'rep':'cluster'},
             'canonical_ridge':{'dedup':True},'canonical_cluster':{'dedup':True,'rep':'cluster'},
             'canonical_elastic':{'dedup':True,'rep':'cluster','kind':'elastic'}}
    if sector_alias:
        methods={m:methods[m] for m in ['cluster','canonical_cluster']}
        variants=['as_is','one_copy','three_copies']
    batch='sector-alias' if sector_alias else 'invariance'
    prefix='IS' if sector_alias else 'I'
    cfg={f'{prefix}_{m}_{v}':{'method':m,'variant':v,'diagnostic':True,'parent':'B_FULL','frame':'native'} for m in methods for v in variants}
    if not sector_alias:cfg['I_ridge_balanced_three']={'method':'ridge','variant':'balanced_three','diagnostic':True,'parent':'B_FULL','frame':'native'}
    save(batch+'-registry.json',{'registered_at':now(),'configurations':cfg,'seed':SEED,'cohort':'primary','defensive_inputs':names,
          'specs':methods,'equivalence_tolerance':1e-11,'prediction_tolerance':1e-10})
    rows=[];effects=[];ledger=[];price=matrix('price.csv').close;y=matrix('labels-5.csv')
    for fold,g in queries(5,'primary').groupby('fold'):
        cutoff=g.origin.min();tr,ii,vv,tc,ic=cutoff_dates(y,native.index,cutoff,{},None)
        ref={}
        for name,c in cfg.items():
            method=c['method'];variant=c['variant'];spec=methods[method];a=transformed(native,names,variant)
            if sector_alias:a=a.rename(columns=lambda c:'i_zz_'+c if c.startswith('zz_alias') else c)
            yt=y.loc[tr,'return'].to_numpy();yi=y.loc[ii,'return'].to_numpy();yv=y.loc[vv,'return'].to_numpy()
            try:
                with warnings.catch_warnings(record=True) as cautions:
                    warnings.simplefilter('always')
                    outer=fitted(spec,a.loc[tr],yt,names,variant);inner=fitted(spec,a.loc[ii],yi,names,variant)
                err=yv-location(inner,a.loc[vv]);risk=a.loc[vv,'p_rv21'].to_numpy();laws=predict(outer,a.loc[g.origin],err,risk,np.zeros(len(vv)))
                if variant=='as_is':ref[method]=laws
                d0=ref[method]
                def dist_error(left,right):
                    differences=[abs(left.stats()['p_up']-right.stats()['p_up']),abs(left.stats()['mean_return']-right.stats()['mean_return'])]
                    if len(left.a)==len(right.a):differences.extend([np.max(abs(left.a-right.a)),np.max(abs(left.w-right.w))])
                    return max(differences)
                maxerr=max(dist_error(d,b) for d,b in zip(laws,d0));dp=np.array([d.stats()['p_up']-b.stats()['p_up'] for d,b in zip(laws,d0)])
                require=method.startswith('canonical') or name=='I_ridge_balanced_three'
                effects.append({'model':name,'method':method,'variant':variant,'fold':fold,'n':len(g),'max_law_error':maxerr,
                                'mean_abs_probability_change':abs(dp).mean(),'max_probability_change':abs(dp).max(),
                                'required_invariance':require,'passes_tolerance':bool(maxerr<1e-10),
                                'aliases':len(outer['metadata']['aliases'])})
                for r,d in zip(g.itertuples(),laws):rows.append(row(5,fold,name,r,d,float(price.loc[r.origin]),'primary'))
                ledger.append({'model':name,'fold':fold,'horizon':5,'status':'ok','cutoff':cutoff,'train_cutoff':tc,'inner_cutoff':ic,
                               'last_endpoint':y.loc[tr,'endpoint'].max(),'inner_last_endpoint':y.loc[ii,'endpoint'].max(),
                               'aliases':outer['metadata']['aliases'],'warnings':[str(w.message)[:250] for w in cautions]})
            except Exception as exc:ledger.append({'model':name,'fold':fold,'horizon':5,'status':'failed','error':str(exc)})
    write(batch+'-effects.csv',pd.DataFrame(effects));write(batch+'-predictions.csv',pd.DataFrame(rows));save(batch+'-ledger.json',ledger)
    required=[r for r in effects if r['required_invariance']]
    assert len(required)==(15 if sector_alias else 110) and all(r['passes_tolerance'] for r in required)
    print('Invariant complete-law vectors',len(required),'of',len(effects),'diagnostic vectors; max error',max(r['max_law_error'] for r in required),flush=True)


if __name__=='__main__':
    import sys
    run('--sector-alias' in sys.argv)
