"""Exact matched expert bank and descriptive forecast geometry."""
from itertools import combinations

from .common import *
from .laws import Law,loaded,piece,store,metrics,logshape,GRID
from .reference import PARENTS

NATIVE = {
    5: {
        'exact_v14':'market_risk','v18_corporate_native':'corporate','omit_latest_21_training_origins':'corporate',
        'price_reaction':'corporate','anchor_asymmetry':'corporate','secondary_location_beyond_gift':'offshore',
        'secondary_location_domestic_only':'domestic','parent_location_domestic_only':'domestic',
        'parent_location_offshore_only':'offshore','parent_scale_only':'market_risk','parent_sign_only':'domestic',
    },
    21: {
        'exact_v14':'market_risk','v19_position_native':'positioning','eight_calendar_day_embargo':'positioning',
        'smooth5':'positioning','anchor_aggregate_position':'positioning','parent_mixture_foreign_tail':'pools',
        'parent_location_domestic_only':'domestic','parent_location_offshore_only':'offshore',
        'parent_scale_only':'market_risk','parent_sign_only':'domestic',
    },
}
COMMON = {'analogue_domestic_history':'historical','analogue_india_nearest':'historical',
          'analogue_mixed_metric':'foreign','direct_loco_transfer':'foreign','direct_factor_only':'offshore'}
PRE = {'archived_same_clock':'historical','archived_joint_GJR':'market_risk','stock_gaussian_shrink':'breadth'}
OLD = {'neutral':'historical','historical':'historical','clock_structural':'domestic','stock_direct':'breadth',
       'component_plus_residual':'domestic','low_rank_tasks':'domestic','low_rank_sector_risk':'breadth',
       'stock_residual':'breadth','fixed_structural_mixture':'pools'}
V19 = {'V18_corporate_same_clock':'corporate','V18_nonprice_same_clock':'corporate',
       'V18_repricing_same_clock':'corporate','price_plus_position_changes':'positioning',
       'price_plus_innovation':'positioning','positions_beyond_oi':'positioning'}
V21 = {'anchor_asymmetry':'corporate','anchor_aggregate_position':'positioning',
       'anchor_fixed_joint_mixture':'pools','stock_conditional_joint':'breadth','date_only_ridge':'domestic'}


def origins():
    f=csv('international-feature-panel.csv.gz',V22,usecols=['row','code','day','issue_ns','last_local_available_ns','reference'])
    g=csv('international-target-panel.csv.gz',V22,usecols=['row','horizon','cohort','ret','mature_ns','target_day'])
    x=g[g.cohort.notna()].merge(f[f.code.eq('india')],on='row',validate='m:1')
    x=x.set_index(['horizon','day']).sort_index()
    return x


def signed_law(arr,i,kind):
    if kind=='weighted':
        return piece(arr,int(i))
    if kind=='log':
        return Law.build(np.expm1(arr[int(i)]))
    raise ValueError(kind)


def load_bank():
    book=csv('matched-expert-cases.csv.gz')
    raw=loaded(OUT,'matched-expert-laws.npz')
    return book,raw


def generate():
    orig=origins()
    z=csv('india-forecast-cases.csv.gz',V22)
    cases=[];laws=[]
    data=[
      (22,V22,z,loaded(V22,'india-forecast-laws.npz'),'weighted','india-forecast-cases.csv.gz'),
      (21,root_for(21),csv('index-forecast-cases.csv.gz',root_for(21)),loaded(root_for(21),'index-forecast-laws.npz'),'weighted','index-forecast-cases.csv.gz'),
      (19,root_for(19),csv('endpoint-cases.csv.gz',root_for(19)),np.load(root_for(19)/'endpoint-laws.npz')['log_return_atoms'],'log','endpoint-cases.csv.gz'),
      (17,root_for(17),csv('original-clock-forecasts.csv.gz',root_for(17)),np.load(root_for(17)/'original-clock-laws.npz')['atoms'],'log','original-clock-forecasts.csv.gz'),
    ]
    skipped=[]
    for ver,root,z,store0,kind,file in data:
        col='target_end' if 'target_end' in z else 'target_date'
        for (h,clock,m),frame in z.groupby(['horizon','cutoff','model']):
            if h not in HORIZONS or clock not in CLOCKS:
                continue
            allowed = ((NATIVE[h]|COMMON) if clock=='native_0910' else (PRE|COMMON)) if ver==22 else (
                V21 if ver==21 and clock=='preauction_0855' else V19 if ver==19 else OLD if ver==17 else {})
            if m not in allowed:
                continue
            ctx=orig.loc[h]
            cn=frame[frame.day.isin(ctx.index)].copy().set_index('day').sort_index()
            if not len(cn) or cn.index.duplicated().any():
                skipped.append(dict(version=ver,model=m,horizon=h,clock=clock,reason='empty or duplicate keys'))
                continue
            assert cn[col].eq(ctx.target_day.reindex(cn.index)).all()
            np.testing.assert_allclose(cn.actual,ctx.ret.reindex(cn.index),rtol=0,atol=2.e-10)
            if len(cn)!=sum(COHORTS[h][:2]):
                skipped.append(dict(version=ver,model=m,horizon=h,clock=clock,reason='incomplete common expert panel',n=len(cn)))
                continue
            if clock=='previous_1700':
                decision=utc_int(pd.DatetimeIndex([stamp(day,'17:00') for day in cn.origin]))
            elif clock=='native_0910':
                decision=utc_int(pd.DatetimeIndex([stamp(day,'09:10') for day in cn.index]))
            else:
                decision=ctx.issue_ns.reindex(cn.index).to_numpy()
            for cp,row in zip(decision,cn.reset_index().itertuples(index=False),strict=True):
                r=ctx.loc[row.day]
                if r.last_local_available_ns>=cp:
                    skipped.append(dict(version=ver,model=m,horizon=h,clock=clock,day=row.day,reason='prior cash mark absent at archived clock under declared guard'))
                    continue
                law=signed_law(store0,row.law,kind)
                sc=metrics(law,row.actual,h)
                if ver==22 and abs(sc['crps']-row.crps)>2e-9:
                    raise ValueError((m,row.day,sc['crps'],row.crps))
                rec=logshape(law)
                cases.append(dict(horizon=h,clock=clock,expert=f'V{ver}/{m}',family=allowed[m],day=row.day,origin=row.origin,target=r.target_day,
                          reference=float(r.reference),cohort=r.cohort,issue_ns=cp,mature_ns=int(r.mature_ns),active=bool(getattr(row,'active',True)),
                          source=(root/file).relative_to(ROOT).as_posix(),source_law=int(row.law),law=len(laws),law_hash=law.eq_id(),
                          log_location=rec[0],log_scale=rec[1],asymmetry=rec[2],**sc))
                laws.append(law)
    frame=pd.DataFrame(cases)
    assert not frame.duplicated(['horizon','clock','day','expert']).any()
    for (h,clock),refs in PARENTS.items():
        assert set(refs).issubset(frame.loc[frame.horizon.eq(h)&frame.clock.eq(clock),'expert'].unique()),(h,clock,refs)
    write('matched-expert-cases.csv.gz',frame)
    store('matched-expert-laws.npz',laws)
    write('matched-expert-exclusions.csv',pd.DataFrame(skipped))
    write('matched-expert-family-map.csv',frame.groupby(['horizon','clock','expert','family','source'],as_index=False).agg(
          n=('day','size'),active=('active','sum'),first_origin=('day','min'),last_origin=('day','max')))
    return frame,laws


def corr(a,b):
    return float(np.corrcoef(a,b)[0,1]) if np.std(a)>1.e-12 and np.std(b)>1.e-12 else np.nan


def geometry(frame,laws):
    pair=[];ranks=[];copies=[]
    centers=('p','mean','log_scale','asymmetry','p_tail_down','p_tail_up','brier','crps')
    for (h,clock),data in frame.groupby(['horizon','clock']):
        g={name:x.set_index('day').sort_index() for name,x in data.groupby('expert')}
        date=pd.Index(sorted(set.intersection(*(set(a.index) for a in g.values()))))
        quant={k:np.array([laws[i].quantiles(GRID) for i in t.reindex(date).law]) for k,t in g.items()}
        for a,b in combinations(g,2):
            x,y=(g[k].reindex(date) for k in (a,b))
            exact=x.law_hash.eq(y.law_hash)
            q=np.abs(quant[a]-quant[b])
            extreme=x.actual.abs().ge(x.actual.abs().quantile(.90))
            dist=q.mean(axis=1)
            ax=x.p.to_numpy();ay=y.p.to_numpy()
            finite_sig=corr(ax,ay)
            shared_parent=bool(a.split('/',1)[1].split('_')[0]==b.split('/',1)[1].split('_')[0])
            pair.append(dict(horizon=h,clock=clock,left=a,right=b,left_family=x.family.iloc[0],right_family=y.family.iloc[0],n=len(date),
              direction_corr=finite_sig,mean_corr=corr(x['mean'],y['mean']),error_corr=corr(x['mean']-x.actual,y['mean']-y.actual),
              brier_loss_corr=corr(x.brier,y.brier),crps_loss_corr=corr(x.crps,y.crps),
              dispersion_corr=corr(x.log_scale,y.log_scale),asymmetry_corr=corr(x.asymmetry,y.asymmetry),
              downside_corr=corr(x.p_tail_down,y.p_tail_down),upside_corr=corr(x.p_tail_up,y.p_tail_up),
              mean_wasserstein_grid_approx=dist.mean(),q90_absolute_distance=q[:,116].mean(),
              extreme_wasserstein=dist[extreme].mean(),nonextreme_wasserstein=dist[~extreme].mean(),
              exact_case_copies=int(exact.sum()),approx_affine_p=bool(abs(finite_sig)>1-1e-11),
              near_equal_laws=bool(dist.mean()<.00030),same_named_source_prefix=shared_parent))
            if exact.any():
                copies.append(dict(horizon=h,clock=clock,a=a,b=b,equal_days=int(exact.sum()),compared_days=len(date),all_equal=exact.all()))
        for col in (*centers,'prediction_error'):
            mat=np.array([(t['mean']-t.actual if col=='prediction_error' else t[col]).reindex(date).to_numpy() for t in g.values()])
            sd=mat.std(axis=1)
            ok=sd>1e-11
            a=(mat[ok]-mat[ok].mean(axis=1,keepdims=True))/sd[ok,None]
            eig=np.linalg.svd(a,compute_uv=False)**2
            ranks.append(dict(horizon=h,clock=clock,coordinate=col,dates=len(date),experts=len(g),nonconstant=ok.sum(),
                              first_share=eig[0]/eig.sum(),effective_rank=eig.sum()**2/(eig@eig)))
    write('forecast-geometry-pairwise.csv.gz',pd.DataFrame(pair))
    write('forecast-geometry-effective-rank.csv',pd.DataFrame(ranks))
    write('forecast-exact-case-duplicates.csv',pd.DataFrame(copies))
    rr=csv('india-risk-path-comparison-cases.csv.gz',V22)
    path=csv('india-protected-same-clock-path-cases.csv.gz',V22)
    u=pd.concat([path[['horizon','day','model','range_mean','range_crps']],rr[~rr.is_stress][['horizon','day','model','range_mean','range_crps']]])
    lines=[]
    for h,z in u.groupby('horizon'):
        for a,b in combinations(z.model.unique(),2):
            x=z[z.model.eq(a)].set_index('day').join(z[z.model.eq(b)].set_index('day'),lsuffix='_a',rsuffix='_b',how='inner')
            lines.append(dict(horizon=h,clock='preauction_0855',left=a,right=b,n=len(x),mean_range_corr=corr(x.range_mean_a,x.range_mean_b),
                   range_loss_corr=corr(x.range_crps_a,x.range_crps_b),mean_range_difference=x.range_mean_a.sub(x.range_mean_b).abs().mean()))
    write('range-geometry-pairwise.csv',pd.DataFrame(lines))


def legacy_alias_controls():
    cases=[]
    received=[]
    for name in ('invariance-effects.csv','sector-alias-effects.csv'):
        p=root_for(10)/'duplicate-replay'/name
        q=csv(p.name,p.parent)
        required=q[q.required_invariance]
        assert required.passes_tolerance.all()
        v=q.groupby(['method','variant','required_invariance'],as_index=False).agg(
            tests=('fold','size'),case_uses=('n','sum'),max_law_delta=('max_law_error','max'),
            max_probability_change=('max_probability_change','max'),recognized_aliases=('aliases','max'))
        cases.append(v.assign(version=10,source=name))
        received.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),required_tests=len(required)))
    p=root_for(11)/'invariance-and-sentinel.csv'
    q=csv(p.name,p.parent)
    assert q.max_atom_delta.le(1.e-11).all()
    b=q.groupby(['test','horizon'],as_index=False).agg(tests=('origin','size'),max_law_delta=('max_atom_delta','max'))
    write('v11-archived-affine-and-sentinel-audit.csv',b)
    write('v10-archived-feature-alias-audit.csv',pd.concat(cases,ignore_index=True))
    save('legacy-affine-inputs.json',received+[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),required_tests=len(q))])


if __name__=='__main__':
    z,laws=generate()
    geometry(z,laws)
    legacy_alias_controls()
    print('Exact matched expert bank:',len(z),'laws across',z.expert.nunique(),'experts.',flush=True)
