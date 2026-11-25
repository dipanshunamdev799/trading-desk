"""Compare shared and horizon-specific heads and construct dependent monthly components."""
from itertools import combinations
from math import factorial
from .common import *
from .modeling import fit,matrix,timed,center_book,blend_laws,sample_law,weighted_store,rank
from .panel import CORE,WEEKLY,MONTHLY,COMPLEMENT,cash,dedup
from research.nifty_forecast_v17.weekly import evaluate
from research.nifty_forecast_v15.sequential import TICK

NAMES=tuple(COMPLEMENT)
SUBSETS=[tuple(g) for k in range(len(NAMES)+1) for g in combinations(NAMES,k)]
SPECS=(
 'archived_same_clock','archived_joint_GJR','A_one_shared_head','B_separate_heads','B_equal_fields_control',
 'C_shared_state_two_heads','D_core_with_horizon_residual','E_sparse_horizon_inputs','F_regularized_multihorizon',
 'G_fixed_specialized_mixture','auxiliary_sector_shared_heads',
)

def archived(clock):
    score=csv('original-clock-forecasts.csv.gz',V17)
    key=score[score.cutoff.eq(clock)&score.model.isin(['component_plus_residual','neutral'])]
    raw=np.load(V17/'original-clock-laws.npz',allow_pickle=False)['atoms']
    p={}
    for r in key.itertuples(index=False):
        if not (r.horizon==5 and r.model=='component_plus_residual') and not (r.horizon==21 and r.model=='neutral'):continue
        a=np.expm1(raw[r.law].astype(float))
        p[r.horizon,r.day]=(a,np.full(len(a),1/len(a)))
    return p

def scale_design(x,t,i):
    active=np.isfinite(x[t]).sum(axis=0)>=14
    a=x[t][:,active]
    m=np.nanmedian(a,axis=0)
    a=np.where(np.isfinite(a),a,m)
    c=a.mean(axis=0);s=a.std(axis=0).clip(1.e-6)
    v=np.where(np.isfinite(x[i,active]),x[i,active],m)
    z=np.clip((a-c)/s,-5,5)
    q=np.clip((v-c)/s,-5,5)
    return z,q

def reduced_prediction(z,q,yy,penalty,rank_):
    m=fit(z,yy,penalty)
    u,s,v=np.linalg.svd(m.coefficient[1:],full_matrices=False)
    cur=q[m.active]
    standardized=np.clip((cur-m.center)/m.sd,-5,5)
    return m.coefficient[0]+standardized@((u[:,:rank_]*s[:rank_])@v[:rank_])

def centered(raw,estimate):
    a,w=raw
    x=np.log1p(a)
    z=x-float(w@x)+estimate
    return np.expm1(z),w

def historical_state(x,t,i):
    b,c=scale_design(x,t,i)
    _,_,v=np.linalg.svd(b,full_matrices=False)
    load=v[:3].T
    return b@load,c@load

def joint_inputs():
    p=csv('asof-features.csv.gz')
    y0=csv('multi-horizon-targets.csv').set_index('day')
    f=p[p.cutoff.eq('preauction_0855')].set_index('day')
    y=y0.reindex(f.index)
    cut=f.decision.str[:10].to_numpy(dtype='U10')
    return f,y,cut

def paths_index():
    return {(r['horizon'],r['origin']):r for r in read('retimed-path-archive.json',V17)['files']}

def outcome_series(y,key):
    return y['return_'+key].to_numpy(float),y['end_'+key].fillna('9999-12-31').to_numpy(dtype='U10')

def piece_cases():
    f,y,cut=joint_inputs()
    x=matrix(f,dedup(WEEKLY+MONTHLY))
    data=[outcome_series(y,f'{a}_{b}') for a,b in COMPONENTS]
    response=np.column_stack([a for a,b in data])
    end=data[-1][1]
    rows=[];store=[];fit_rows=[]
    arcs=archived('preauction_0855')
    direct,_e=outcome_series(y,'0_21')
    comps=[center_book(f,a,b,cut) for a,b in data]
    errors=response-np.column_stack([r[0] for r in comps])
    sizes=(.008,.010,.011,.013)
    sy=matrix(f,('iv_prev','trailing_vol','prior_ret21','cash_breadth_change'))
    dx=[matrix(f,tuple(g)) for g in [
        CORE+('count2','count9','fund_surprise','reaction_mean'),
        CORE+('FII_index_futures_level','FII_index_futures_d5','FII_index_futures_d21'),
        CORE+('FII_index_futures_slow','index_futures_detail_hhi_z','Pro_index_futures_level'),
        CORE+('FII_index_futures_d21','Pro_index_futures_level','financial21','index_futures_detail_hhi_z')]]
    uniform=np.full(len(Q),1./len(Q))
    sh5=csv('architecture-cases.csv.gz').query("model == 'B_separate_heads' and horizon == 21").set_index('day')
    shlog=np.load(OUT/'architecture-laws.npz')
    keep=np.flatnonzero(y.cohort_21.notna())
    for i in keep:
        t=timed(end,cut,i,direct)
        t=t[np.isfinite(errors[t]).all(axis=1)]
        assert len(t)>=45 and max(end[t])<cut[i]
        ea=errors[t]
        center=np.array([r[0][i] for r in comps])
        z,q=scale_design(x,t,i)
        sd=ea.std(axis=0).clip(.003)
        joint=fit(x[t],ea/sd,170)
        full=np.clip(.58*joint.values(x[i])*sd,-np.asarray(sizes),np.asarray(sizes))
        low=np.clip(.65*reduced_prediction(z,q,ea/sd,180,2)*sd,-np.asarray(sizes),np.asarray(sizes))
        vec=np.array([.58*fit(a[t],ea[:,j],165).values(a[i]) for j,a in enumerate(dx)]).clip(-np.asarray(sizes),np.asarray(sizes))
        cmp=np.sort(np.random.default_rng(SEED+i).choice(len(t),len(Q),replace=True))
        residual=ea[cmp]-np.median(ea,axis=0)
        # Compare an equally sized conditional historical law in whole-row residual vectors.
        z0,q0=scale_design(sy,t,i)
        within=np.argsort(np.square(z0-q0).mean(axis=1),kind='stable')[:max(35,len(t)//2)]
        conditional=ea[np.sort(np.random.default_rng(SEED+31*i).choice(within,len(Q),replace=True))]
        conditional=conditional-np.median(ea,axis=0)
        independent=np.column_stack([residual[np.random.default_rng(SEED+i*7+j).permutation(len(residual)),j] for j in range(4)])
        alternatives={'unconditioned_joint':center+residual,'joint_multioutput':center+full+residual,
                      'low_rank_joint':center+low+residual,'horizon_specific_components':center+vec+residual,
                      'conditional_history_components':center+vec+conditional,'independent_components_control':center+vec+independent}
        qrow=sh5.loc[f.index[i]]
        a,b=shlog['offsets'][int(qrow.law):int(qrow.law)+2]
        controls={'direct_specialized':(shlog['atoms'][a:b],shlog['weights'][a:b]),'same_clock_neutral':arcs[21,f.index[i]]}
        cov=np.corrcoef(residual,rowvar=False)
        info=dict(track='temporal',cutoff='preauction_0855',horizon=21,day=f.index[i],origin=y.origin.iloc[i],
                  target_end=end[i],cohort=y.cohort_21.iloc[i],last_mature=max(end[t]),train_n=len(t))
        for name,a0 in alternatives.items():
            np.testing.assert_allclose(np.prod(np.exp(a0),axis=1)-1,np.expm1(a0.sum(axis=1)),atol=1.e-12)
            rows.append(info|dict(model=name,parent='direct_specialized',law=len(store),active=1,piece_correlation=cov[0,3],
                                  **evaluate(np.expm1(a0.sum(axis=1)),uniform,np.expm1(direct[i]))))
            store.append(a0.astype(np.float32))
            for j,(a,b) in enumerate(COMPONENTS):
                q=evaluate(np.expm1(a0[:,j]),uniform,np.expm1(response[i,j]))
                fit_rows.append(info|dict(model=name,start_offset=a,end_offset=b,law=len(store)-1,component=j,**q))
        for name,(v,w) in controls.items():
            rows.append(info|dict(model=name,parent=name,law=-1,active=1,piece_correlation=np.nan,**evaluate(v,w,np.expm1(direct[i]))))
    write('temporal-cases.csv.gz',pd.DataFrame(rows))
    write('component-case-scores.csv.gz',pd.DataFrame(fit_rows))
    np.savez_compressed(OUT/'component-law-archive.npz',log_return_components=np.stack(store),weights=uniform)
    print('Joint component laws cover',len(keep),'monthly origins',flush=True)

def architectures():
    f,y,cut=joint_inputs()
    ids=np.flatnonzero(y.cohort_5.notna()|y.cohort_21.notna())
    ar=archived('preauction_0855')
    archive=paths_index()
    data=[outcome_series(y,f'0_{h}') for h in HORIZONS]
    end=data[1][1]
    base=[center_book(f,r,e,cut) for r,e in data]
    raw=np.column_stack([d[0] for d in data])
    error=raw-np.column_stack([a[0] for a in base])
    x=matrix(f,CORE+('count9','fund_surprise','FII_index_futures_d21','index_futures_detail_hhi_z','financial21'))
    v=[matrix(f,WEEKLY),matrix(f,MONTHLY)]
    s=[matrix(f,('count9','fund_surprise','official_finance1','iv_prev','reaction_mean')),
       matrix(f,('FII_index_futures_d21','FII_index_futures_level','Pro_index_futures_level','index_futures_detail_hhi_z','financial21'))]
    daily=cash()
    rels=[np.log(daily[x]/daily.nifty50) for x in ('niftybank','niftyit')]
    aux=np.column_stack([(r.shift(-h)-r).reindex(y.origin).to_numpy() for r,h in zip(rels,HORIZONS)])
    out=[];weight=[];used=[]
    for i in ids:
        # Both heads train on the very same original decision rows with fully mature monthly outcomes.
        t=timed(end,cut,i,raw[:,1])
        t=t[np.isfinite(error[t]).all(axis=1)]
        assert len(t)>=45 and max(end[t])<cut[i]
        r=error[t];sd=r.std(axis=0).clip(.004);standard=r/sd
        z,q=scale_design(x,t,i)
        shared=fit(x[t],standard.mean(axis=1),155)
        common=shared.values(x[i])
        equal=fit(x[t],standard,155).values(x[i])*sd
        fz,fq=historical_state(x,t,i)
        pca=fit(fz,standard,145).values(fq)*sd
        constrained=reduced_prediction(z,q,standard,240,1)*sd
        sparse=np.array([fit(m[t],r[:,j],175).values(m[i]) for j,m in enumerate(s)])
        sep=np.array([fit(m[t],r[:,j],155).values(m[i]) for j,m in enumerate(v)])
        mix_resp=standard-standard.mean(axis=1)[:,None]
        core=np.array([fit(m[t],mix_resp[:,j],255).values(m[i]) for j,m in enumerate(s)])*sd+common*sd
        subset=np.isfinite(aux[t]).all(axis=1)
        aux_pred=constrained
        if subset.sum()>=45:
            scale=aux[t[subset]].std(axis=0).clip(.004)
            goal=np.column_stack([standard[subset],.55*aux[t[subset]]/scale])
            aux_pred=reduced_prediction(z[subset],q,goal,220,2)[:2]*sd
        estimates=[common*sd,sep,equal,pca,core,sparse,constrained]
        for j,h in enumerate(HORIZONS):
            if pd.isna(y[f'cohort_{h}'].iloc[i]):continue
            actual=np.expm1(raw[i,j])
            a,w=ar[h,f.index[i]]
            r0=archive[h,y.origin.iloc[i]]
            with np.load(V17/r0['file'],allow_pickle=False) as b:
                paths=b['preauction_0855_same_clock_GJR']
                mark=np.expm1(paths[:,-1,3]*TICK)
            outlaws=[(a,w),(mark,np.ones(len(mark))/len(mark))]
            for est in estimates:
                dv=np.clip(.66*est[j],-.013,.013)
                # Use the same protected horizon shape for every architecture; only the head changes.
                outlaws.append(centered((a,w),base[j][0][i]+dv))
            outlaws.append(blend_laws(a,w,*outlaws[-2],.50))
            outlaws.append(centered((a,w),base[j][0][i]+np.clip(.66*aux_pred[j],-.013,.013)))
            assert len(SPECS)==len(outlaws)
            info=dict(track='architecture',cutoff='preauction_0855',horizon=h,day=f.index[i],origin=y.origin.iloc[i],
                     target_end=data[j][1][i],cohort=y[f'cohort_{h}'].iloc[i],last_mature=max(end[t]),active=1,
                     train_n=len(t),reference_close=y.reference_close.iloc[i])
            for name,(a0,w0) in zip(SPECS,outlaws):
                weight.append((a0,w0))
                out.append(info|dict(model=name,parent='archived_same_clock' if name!='archived_joint_GJR' else name,
                                     law=len(weight)-1,**evaluate(a0,w0,actual)))
            used.append(dict(horizon=h,day=f.index[i],train_last=max(end[t]),n=len(t),aux_n=int(subset.sum()),
                             matched_calendar=True,n_shared_fields=x.shape[1],n_head_fields=v[j].shape[1]))
    write('architecture-cases.csv.gz',pd.DataFrame(out))
    write('architecture-training-receipts.csv',pd.DataFrame(used))
    weighted_store('architecture-laws.npz',weight)
    save('architecture-config.json',dict(systems=SPECS,sparse=dict(weekly=5,monthly=5),
      parent='V17 exact session-decomposition atoms for five sessions and symmetric neutral atoms for the monthly forecast. V15-style same-clock GJR path endpoint is a separate control.',
      location='Every fitted head uses the same empirical parent shape. Individual heads change only location; mixture preserves both laws. Head training uses the same mature monthly windows across horizons.',
      auxiliary='Native bank and IT relative index returns are auxiliary targets on the same dates in a reduced-rank model. No extra NIFTY outcomes are counted.',
      temporal='Four unseen future log components. Joint residual rows are preserved or deliberately permuted for an independence control. Monthly endpoints compound the same atoms.'))
    print('Horizon architecture laws',len(out),flush=True)

def complementarity():
    f,y,cut=joint_inputs()
    arcs=archived('preauction_0855')
    cases=[];attribution=[];correlations=[];receipts=[]
    for h in HORIZONS:
        actual,en=outcome_series(y,f'0_{h}')
        keep=np.flatnonzero(y[f'cohort_{h}'].notna())
        err=np.full(len(y),np.nan)
        x={s:matrix(f,dedup(k for g in s for k in COMPLEMENT[g])) for s in SUBSETS if s}
        for i in keep:
            a,w=arcs[h,f.index[i]]
            err[i]=actual[i]-np.log1p(w@a)
        for i in keep:
            p=timed(en,cut,i,err)
            f0=f.index[i]
            a,w=arcs[h,f0]
            truth=np.expm1(actual[i])
            vals={};shifts={}
            for s in SUBSETS:
                dv=0.
                if s and len(p)>=38:
                    m=fit(x[s][p],err[p],185)
                    dv=float(np.clip(.58*(m.values(x[s][i])-m.coefficient[0]),-.013,.013))
                shifted=np.expm1(np.log1p(a)+dv)
                v=evaluate(shifted,w,truth)
                vals[s]=v
                shifts[s]=dv
                cases.append(dict(track='complementarity',horizon=h,cutoff='preauction_0855',day=f0,origin=y.origin.iloc[i],
                    target_end=en[i],cohort=y[f'cohort_{h}'].iloc[i],model='+'.join(s) if s else 'same_clock_parent',parent='same_clock_parent',
                    active=int(bool(len(p)>=38) or not s),last_mature=max(en[p]) if len(p) else None,shift=dv,**v))
            for name in NAMES:
                remaining=[s for s in SUBSETS if name not in s]
                joined=lambda s: tuple(k for k in NAMES if k in s or k==name)
                gain={k:sum(factorial(len(s))*factorial(len(NAMES)-1-len(s))/factorial(len(NAMES))*
                             (vals[s][k]-vals[joined(s)][k]) for s in remaining) for k in ('brier','crps')}
                attribution.append(dict(horizon=h,day=f0,cohort=y[f'cohort_{h}'].iloc[i],block=name,
                    active=int(len(p)>=38),first_brier=vals[()]['brier']-vals[(name,)]['brier'],
                    last_brier=vals[tuple(k for k in NAMES if k!=name)]['brier']-vals[NAMES]['brier'],**gain))
            if len(p)>=38 and i in keep[::12]:
                for a0,b0 in combinations(NAMES,2):
                    j=matrix(f,COMPLEMENT[a0]+COMPLEMENT[b0])[p]
                    cross=[abs(rank(j[:,a],j[:,b])) for a in range(len(COMPLEMENT[a0])) for b in range(len(COMPLEMENT[a0]),j.shape[1])]
                    receipts.append(dict(horizon=h,day=f0,pair=a0+' / '+b0,last_mature=max(en[p]),
                                         median_absolute_pairwise_feature_rank=np.nanmedian(cross),max_absolute_pairwise_feature_rank=np.nanmax(cross)))
    d=pd.DataFrame(cases)
    for (h,c),v in d[d.active.eq(1)].groupby(['horizon','cohort']):
        ok=v.pivot(index='day',columns='model',values=['mean','actual','shift'])
        for a,b in combinations(NAMES,2):
            g=ok['mean'];u=ok['actual'];p=ok['shift']
            correlations.append(dict(horizon=h,cohort=c,group_a=a,group_b=b,n=len(g),forecast_rank=rank(g[a],g[b]),
              error_rank=rank(u[a]-g[a],u[b]-g[b]),correction_rank=rank(p[a],p[b])))
    write('complementarity-cases.csv.gz',d)
    write('complementarity-shapley.csv.gz',pd.DataFrame(attribution))
    write('complementarity-prediction-correlation.csv',pd.DataFrame(correlations))
    write('complementarity-feature-redundancy.csv',pd.DataFrame(receipts))
    print('Complementarity contrasts',len(d),flush=True)

if __name__=='__main__':
    architectures()
    piece_cases()
    complementarity()

