"""Run the frozen family-by-age matrix on cumulative, incremental and risk targets."""
from collections import defaultdict
from .common import *
from .panel import GROUPS,cash
from .modeling import fit_slope,timed,variant_matrix,center_book,curves,MEASURES,rank,block_intervals,disjoint

def timestamped(a):
    return a.to_numpy(dtype='U10')

def columns(intervals):
    return pd.DataFrame(intervals,columns=['mode','start_offset','end_offset'])

def summarize_window(axis,answers,names,loss,parent,case,seed):
    # The same dates are used for a candidate, its parent, and its aged control.
    main=np.where(case['active'],parent[:,None]-loss,np.nan)
    good=np.flatnonzero(np.isfinite(main).sum(axis=0)>=25)
    test={}
    if len(good):
        for j,g in zip(good,block_intervals(main[:,good],max(5,case['duration']),600,seed).to_dict('records')) if len(good) else []:
            test[j]=g
    out=[]
    forecast=answers[:,:,MEASURES.index('mean')]
    observation=case['actual']
    idx={k:j for j,k in enumerate(names)}
    for j,(family,age) in enumerate(names):
        active=case['active'][:,j]
        stable=case['active'][:,idx[family,'lag5']]&active
        matched=int(active.sum())
        n=disjoint(axis.loc[active].rename(columns={'start':'forecast_day'}).rename(columns={'first_target':'day'})[['day','target_end']])
        m=loss[:,j]
        z=main[:,j]
        pscore=parent[active].mean() if matched else np.nan
        es=m[active].mean() if matched else np.nan
        baseline=case['parent_forecast']
        def mean_on(x,ok):
            return float(np.mean(x[ok])) if ok.any() else np.nan
        early=axis.cohort.eq('early').to_numpy()
        later=axis.cohort.eq('later').to_numpy()
        common=active&axis.common21.notna().to_numpy()
        w=(observation-baseline)
        denom=np.square(w[active]).sum()
        effect=np.square(observation[active]-forecast[active,j]).sum()
        slope=forecast[:,j]-baseline
        v={'matched':matched,'disjoint':n,'n_total':len(m),'coverage':matched/len(m),'parent':pscore,'enhanced':es,
           'gain':pscore-es,'relative_gain':(pscore-es)/pscore if pscore>0 else np.nan,
           'full_error':float(m.mean()),'full_parent_error':float(parent.mean()),
           'full_gain':float((parent-m).mean()),'earlier_n':int((active&early).sum()),'earlier_gain':mean_on(z,active&early),
           'later_n':int((active&later).sum()),'later_gain':mean_on(z,active&later),
           'common_n':int(common.sum()),'common_21_gain':mean_on(z,common),
           'lag5_same_n':int(stable.sum()),'gain_vs_lag5':mean_on(loss[:,idx[family,'lag5']]-m,stable),
           'linear_residual_corr':float(np.corrcoef(slope[active],w[active])[0,1]) if matched>7 and np.std(slope[active])>1e-10 and np.std(w[active])>1e-10 else np.nan,
           'rank_forecast':rank(forecast[active,j],observation[active]),
           'rank_increment':rank(slope[active],w[active]),
           'incremental_oos_r2':1-effect/denom if denom>1e-12 else np.nan}
        if j in test:
            v|={k:test[j][k] for k in ('low','high','adjusted_low','adjusted_high','sd')}
        out.append(dict(family=family,age=age,**v))
    return pd.DataFrame(out)

def run():
    panel=csv('asof-features.csv.gz')
    y0=csv('multi-horizon-targets.csv').set_index('day')
    calendar=cash().index
    names=[(family,age) for family in GROUPS for age in AGES]
    shapes=[('cumulative',0,h) for h in LIFETIMES]+[('incremental',a,b) for a,b in (*INCREMENTS[1:],(5,21))]
    shapes += [('risk',0,h) for h in LIFETIMES]
    tables=[];law_rows=[];law_specs=[];trace=[];bench=[]
    stream=gzip.open(OUT/'lifetime-cases.csv.gz','wt',encoding='utf-8',newline='')
    empty=True
    try:
        for ic,clock in enumerate(CLOCKS):
            f=panel[panel.cutoff.eq(clock)].set_index('day')
            y=y0.reindex(f.index)
            designs={k:v for family,fields in GROUPS.items()
                     for age,v in variant_matrix(f,fields,calendar).items() for k in [(family,age)]}
            available={k:np.isfinite(v).any(axis=1) for k,v in designs.items()}
            cut=timestamped(f.decision.str[:10])
            for j,(mode,a,b) in enumerate(shapes):
                lab=f'{a}_{b}'
                risk=mode=='risk'
                t=y[('risk_' if risk else 'return_')+lab].to_numpy(float)
                value=np.log(np.maximum(t,.005)) if risk else t
                end=timestamped(y['end_'+lab].fillna('9999-12-31'))
                ch=5 if b<=5 else 21
                keep=np.flatnonzero(y[f'cohort_{ch}'].notna().to_numpy())
                assert len(keep)==EXPECTED[ch] and np.isfinite(value[keep]).all()
                center,atoms,used,last=center_book(f,value,end,cut)
                resid=value-center
                shifts=np.zeros((len(keep),len(names)))
                active=np.zeros_like(shifts,dtype=bool)
                n_train=np.zeros_like(shifts,dtype=np.int16)
                fit_end=np.full(shifts.shape,'',dtype='U10')
                all_scores=np.full((*shifts.shape,len(MEASURES)),np.nan)
                parent_scores=np.full((len(keep),len(MEASURES)),np.nan)
                law_id=[]
                for r,i in enumerate(keep):
                    hist=timed(end,cut,i,resid)
                    assert used[i]>=45 and len(hist)>=45 and np.isfinite(atoms[i]).all()
                    law_rows.append(atoms[i])
                    law_id.append(len(law_rows)-1)
                    law_specs.append(dict(law=law_id[-1],cutoff=clock,mode=mode,start_offset=a,end_offset=b,day=f.index[i],
                      target_end=end[i],reference=y.reference_close.iloc[i],n_train_parent=used[i],last_parent_label=last[i]))
                    cap=.20 if risk else .009*np.sqrt((b-a)/5)
                    for k,name in enumerate(names):
                        ok=available[name]
                        if not ok[i]:continue
                        tr=hist[ok[hist]]
                        if len(tr)<45:continue
                        x=designs[name]
                        delta,mdl=fit_slope(x[tr],resid[tr],x[i])
                        if len(mdl.active)==0:continue
                        active[r,k]=True
                        shifts[r,k]=np.clip(.65*delta,-cap,cap)
                        n_train[r,k]=len(tr)
                        fit_end[r,k]=max(end[tr])
                        if name[1]=='fresh' and not risk and (a,b) in ((0,5),(0,21),(5,21)) and i in keep[::9]:
                            trace.append(dict(law=law_id[-1],family=name[0],last_mature=fit_end[r,k],n=len(tr),coefficient_scale=.65,cap=cap,
                                                **mdl.receipt(GROUPS[name[0]])))
                    ars=curves(atoms[i],np.r_[0.,shifts[r]],value[i],risk)
                    parent_scores[r]=ars[0]
                    all_scores[r]=ars[1:]
                axis=pd.DataFrame(dict(start=f.index[keep],first_target=y['start_'+lab].iloc[keep].to_numpy(),
                    cohort=y[f'cohort_{ch}'].iloc[keep].to_numpy(),common21=y.cohort_21.iloc[keep].to_numpy(),target_end=end[keep]))
                case=dict(active=active,actual=np.exp(value[keep]) if risk else np.expm1(value[keep]),
                          duration=b-a,parent_forecast=parent_scores[:,MEASURES.index('mean')])
                extra=dict(mode=mode,start_offset=a,end_offset=b,comparison_cohort=ch,cutoff=clock)
                for k,metric in [(0,'qlike' if risk else 'brier'),(1,'crps')]:
                    tab=summarize_window(axis,all_scores,names,all_scores[:,:,k],parent_scores[:,k],case,SEED+ic*625+j*13+k)
                    tables.append(tab.assign(metric=metric,**extra))
                d=pd.DataFrame({k:all_scores[:,:,i].flatten() for i,k in enumerate(MEASURES)})
                n=len(names)
                d=d.assign(**extra,day=np.repeat(f.index[keep].to_numpy(),n),target_end=np.repeat(end[keep],n),cohort=np.repeat(axis.cohort.to_numpy(),n),
                    active=active.flatten(),law=np.repeat(law_id,n),shift=shifts.flatten(),family=np.tile([s[0] for s in names],len(keep)),
                    age=np.tile([s[1] for s in names],len(keep)),n_train=n_train.flatten(),last_mature=fit_end.flatten(),
                    actual=np.repeat(case['actual'],n),parent_primary=np.repeat(parent_scores[:,0],n),parent_crps=np.repeat(parent_scores[:,1],n))
                d.to_csv(stream,index=False,header=empty,float_format='%.12g')
                empty=False
                for q,idx in enumerate(keep):
                    bench.append(extra|dict(day=f.index[idx],target_end=end[idx],law=law_id[q],cohort=axis.cohort.iloc[q],
                        actual=case['actual'][q],**dict(zip(MEASURES,parent_scores[q]))))
                if j%5==0 or j==len(shapes)-1:
                    print(clock,mode,lab,'costed',len(keep),'origins,',len(names),'age designs',flush=True)
    finally:
        stream.close()
    final=pd.concat(tables,ignore_index=True)
    write('information-lifetime-matrix.csv',final)
    write('lifetime-parent-cases.csv.gz',pd.DataFrame(bench))
    write('lifetime-law-index.csv',pd.DataFrame(law_specs))
    np.savez_compressed(OUT/'lifetime-parent-laws.npz',atoms=np.stack(law_rows))
    receipt('lifetime-fresh-fit-examples.ndjson.gz',trace)
    save('lifetime-receipt.json',dict(target_clock_cells=len(law_specs),case_rows=len(law_specs)*len(names),
          clinical_scope='Cumulative one session also represents the first incremental segment. Additional 6–21 row explicitly removes the first five-session move.',
          reconstruction='Add per-case shift to the indexed log atoms. Exponentiate and subtract one for returns or exponentiate for annualized volatility. All atoms are equal weight. Fallback has zero shift.',
          strong_parents='The general age matrix uses its preregistered chronological price/risk parent. Native and rebuilt five- and 21-session stronger baseline experiments are stored separately.',
          dependence='Circular paired date-block bootstrap with 600 draws and max-standardized adjustment per clock, target, metric and age/family search. Earliest active sample is common to candidate/parent.',
          raw_opening='The native opening-gap benchmark is separate. A one-session close return includes overnight and regular-session components.',
          failed_sources=final[final.matched.eq(0)].groupby(['family']).size().to_dict()))
    print('Lifetime matrix contains',len(final),'matched summary rows',flush=True)

if __name__=='__main__':
    run()

