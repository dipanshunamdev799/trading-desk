"""Test whether native-law positioning gains come from bias correction or inputs."""
from .common import *
from .forecast import matrix,matured,shift,book_panel,POSITION,INNOV,coverage,shuffled_blocks
from .evidence import boot,disjoint
from research.nifty_forecast_v17.weekly import evaluate

def run():
    source=csv('native-residual-cases.csv.gz')
    panel=csv('asof-positioning-features.csv.gz')
    prev=csv('v18-native-exact-replay.csv')
    archive=np.load(OUT/'v18-native-replayed-laws.npz',allow_pickle=False)
    a,w,o=archive['atoms'],archive['weights'],archive['offsets']
    rows=[];gain=[];placebos=[];pred=[];weights=[];fitrows=[]
    for h in HORIZONS:
        f,y=book_panel('preauction_0855',h,panel)
        day=f.index.to_numpy(); decision=f.decision.str[:10].to_numpy()
        ends=y[f'end_original{h}'].fillna('9999-12-31').to_numpy()
        targets=y[f'original{h}'].to_numpy(float)
        design=POSITION+INNOV
        x=matrix(f,design)
        lags={k:matrix(f,tuple(f'{q}_delay{k}' for q in design)) for k in (1,5)}
        live=coverage(f)['innovation']
        cohort=y[f'cohort_{h}']
        ids=np.flatnonzero(cohort.notna())
        parent=prev[prev.horizon.eq(h)&prev.model.eq('V14_exact')].set_index('day')
        registered=source[source.horizon.eq(h)&source.model.eq('V14_plus_positions')].set_index('day')
        e=np.full(len(day),np.nan)
        for i in ids:
            e[i]=targets[i]-np.log1p(parent.loc[day[i],'mean'])
        for i in ids:
            meta=parent.loc[day[i]]; k=int(meta.law_index)
            base,wgt=a[o[k]:o[k+1]],w[o[k]:o[k+1]]
            train=matured(day,ends,targets,i,decision)
            tr=train[np.isfinite(e[train])&live[train]] if live[i] else train[:0]
            cap=.009 if h==5 else .012
            bias,_,_=shift(x,e,i,tr,cap,'intercept')
            original,mdl,selected=shift(x,e,i,tr,cap)
            assert abs(original-registered.loc[day[i],'shift'])<1.e-10
            args=dict(day=day[i],origin=meta.origin,target_end=ends[i],cohort=cohort.iloc[i],horizon=h,cutoff='native_v14_guard',
                      active=int(mdl is not None),last_mature=max(ends[selected]) if len(selected) else None,n_train=len(selected),
                      source_day=f.source_day.iloc[i],source_release=f.source_release.iloc[i])
            estimates={'V14_exact':0.,'V14_plus_positions':original,'V14_bias_only':bias,
                       'V14_position_increment_without_bias':float(np.clip(original-bias,-cap,cap))}
            ux={}
            for lag,z in lags.items():
                active=tr[np.isfinite(z[tr]).any(axis=1)] if np.isfinite(z[i]).any() else tr[:0]
                dv,_,_=shift(z,e,i,active,cap)
                ux[f'positions_delay{lag}']=int(len(active)>=38)
                estimates[f'positions_delay{lag}']=dv
            base_score=evaluate(base,wgt,np.expm1(targets[i]))
            bias_score={}
            for name,delta in estimates.items():
                law=(1+base)*np.exp(delta)-1
                val=evaluate(law,wgt,np.expm1(targets[i]))
                pred.append(law);weights.append(wgt)
                rows.append(args|dict(model=name,law=len(pred)-1,shift=delta,active=ux.get(name,args['active']),**val))
                if name=='V14_bias_only':bias_score=val
                gain.append(args|dict(model=name,pair='full_vs_V14',
                       brier_gain=base_score['brier']-val['brier'],crps_gain=base_score['crps']-val['crps']))
            group={'index_and_stock_levels':np.arange(3),'position_changes':np.arange(3,10),'crowding':np.arange(10,len(POSITION)),
                   'innovation':np.arange(len(POSITION),len(design))}
            if mdl is not None:
                fitrows.append(args|mdl.receipt(design))
            else:
                continue
            observed={}
            for label,cols in group.items():
                effect,_,_=shift(x[:,cols],e,i,tr,cap)
                observed[label]=evaluate((1+base)*np.exp(effect)-1,wgt,np.expm1(targets[i]))
            for seed in range(23):
                for label,cols in group.items():
                    xx=x[:,cols]
                    shuffled=np.roll(np.arange(len(tr)),(seed+3)*7) if seed%2==0 else shuffled_blocks(len(tr),SEED+seed)
                    delta,_,_=shift(xx,e,i,tr,cap,random_order=shuffled)
                    null=evaluate((1+base)*np.exp(delta)-1,wgt,np.expm1(targets[i]))
                    obs=observed[label]
                    placebos.append(args|dict(seed=seed,block=label,real_brier=bias_score['brier']-obs['brier'],
                        real_crps=bias_score['crps']-obs['crps'],brier_gain=bias_score['brier']-null['brier'],
                        crps_gain=bias_score['crps']-null['crps']))
    cases=pd.DataFrame(rows)
    write('native-mechanism-cases.csv.gz',cases)
    write('native-mechanism-gains.csv.gz',pd.DataFrame(gain))
    placebo=pd.DataFrame(placebos)
    write('native-refit-null-cases.csv.gz',placebo)
    summary=[]
    for (h,arm),g in cases.groupby(['horizon','model']):
        for tag,q in [('all',g),('matched active',g[g.active.eq(1)]),('earlier',g[g.cohort.eq('early')]),('later',g[g.cohort.eq('later')])]:
            summary.append(dict(horizon=h,model=arm,cohort=tag,n=len(q),brier=q.brier.mean(),crps=q.crps.mean(),log_loss=q.log_loss.mean()))
    write('native-mechanism-summary.csv',pd.DataFrame(summary))
    bands=[]
    for h,g in cases.groupby('horizon'):
        t=g[g.active.eq(1)]
        c=t[t.model.eq('V14_bias_only')].set_index('day')
        for metric in ('brier','crps'):
            stack=[]
            for name,q in t.groupby('model'):
                if name=='V14_bias_only':
                    continue
                q=q.set_index('day')
                idx=q.index.intersection(c.index)
                diff=c.loc[idx,metric]-q.loc[idx,metric]
                span=q.loc[idx].reset_index()[['day','target_end']]
                stack.append((dict(horizon=h,model=name,parent='V14_bias_only',metric=metric,
                                  n=len(diff),disjoint=disjoint(span),gain=diff.mean()),diff))
            bands.extend(boot(stack,32+h))
    write('native-bias-control-bands.csv',pd.DataFrame(bands))
    active=placebo[placebo.active.eq(1)]
    result=[]
    for (h,),q in active.groupby(['horizon']):
        for k in ('brier','crps'):
            grouped=q.groupby(['seed','block'])[[k+'_gain','real_'+k]].mean()
            dist=grouped[k+'_gain'].groupby('seed').max()
            real=grouped['real_'+k].max()
            result.append(dict(horizon=h,metric=k,best_observed_increment=real,rotation_median=dist.median(),
                rotation_95=dist.quantile(.95),exceedances=int(dist.ge(real).sum()),runs=len(dist)))
    write('native-refit-null-summary.csv',pd.DataFrame(result))
    coeff=pd.DataFrame([dict(horizon=r['horizon'],day=r['day'],feature=c,beta=b)
                        for r in fitrows for c,b in zip(r['columns'],r['parameters'][1:])])
    out=coeff.groupby(['horizon','feature'],as_index=False).agg(fits=('beta','size'),mean_standardized_coefficient=('beta','mean'),
          median_standardized_coefficient=('beta','median'),positive_share=('beta',lambda v:v.gt(0).mean()),abs_median=('beta',lambda v:abs(v).median()))
    write('native-positioning-weight-summary.csv',out)
    with gzip.open(OUT/'native-positioning-fits.ndjson.gz','wt',encoding='utf8') as g:
        for row in fitrows:g.write(json.dumps(row,allow_nan=False,default=str)+'\n')
    np.savez_compressed(OUT/'native-mechanism-laws.npz',atoms=np.concatenate(pred),weights=np.concatenate(weights),
                       offsets=np.r_[0,np.cumsum([len(r) for r in pred])])
    print('Archived bias-only, timing and residual-component controls on the original native law',flush=True)

if __name__=='__main__':
    run()

