"""Matched market-window evidence, revision calibration and survival summaries."""
from collections import defaultdict
from functools import lru_cache

from .common import *
from .data import Daily

LOSSES=('brier','log_loss','remaining_brier','remaining_log_loss','endpoint_crps','remaining_return_crps',
        'endpoint_pinball','endpoint_is80','remaining_return_is80','vol_mae','vol_qlike','vol_crps',
        'remaining_vol_mae','remaining_vol_qlike','range_crps','range_is80',
        'remaining_range_crps','high_crps','low_crps','drawdown_crps','rebound_crps','joint_energy')
METRICS=LOSSES+('endpoint_cov50','endpoint_cov80','endpoint_width80','vol_cov80','vol_width80',
        'range_cov80','range_width80','remaining_return_cov80','remaining_return_width80','remaining_range_cov80',
        'p_up','p_remaining_up','remaining_vol_mean','vol_mean','endpoint_mean','endpoint_q10','endpoint_q50',
        'endpoint_q90','remaining_range_mean','endpoint','remaining_return','range','vol')
IDENT=['horizon','origin','asof','target','cohort','checkpoint','remaining','model','literal_calendar']
CONTRASTS=[
    ('frozen','price_only','price and elapsed time',False),
    ('price_only','iv_restart','revised raw risk',True),('iv_restart','gjr_restart','state risk',True),
    ('iv_restart','domestic','domestic addition',True),('domestic_stale','domestic','fresh domestic',True),
    ('domestic','full','all eligible inputs',True),('iv_restart','derivatives_first','surface first',True),
    ('derivatives_first','full','other blocks after surface',True),
    ('full_stale_surface','full','fresh surface',True),('full_stale_global','full','fresh foreign',True),
    ('iv_restart','full','fully revised baseline',True),('full_delayed','full','delayed control',True),
    ('full_permuted','full','block-permuted fit control',True),('full_noise','full','delayed plus noise control',True),
    *[(a,b,'restart comparison',True) for a in ('iv_restart','gjr_restart') for b in
      ('historical','refit','incremental','particle','hybrid','vol_state','analogue','sign_magnitude','heavy_tail','episode_tail')],
    ('iv_restart','vol_only_shock','shock scale only',True),('vol_only_shock','shock_persistence','shock drift',True),
]
MAIN_MATCH=('brier','endpoint_crps','remaining_brier','remaining_return_crps','vol_mae','vol_qlike',
            'range_crps','remaining_range_crps','remaining_vol_mae','joint_energy')


@lru_cache(maxsize=50)
def boot_weight(n,b):
    rng=np.random.default_rng(SEED+1009*n+19*b)
    start=rng.integers(0,n,size=(DRAW,int(np.ceil(n/b))))
    ix=((start[:,:,None]+np.arange(b))%n).reshape(DRAW,-1)[:,:n]
    w=np.zeros((DRAW,n))
    rr=np.broadcast_to(np.arange(DRAW)[:,None],ix.shape)
    np.add.at(w,(rr,ix),1)
    return w


def paired_intervals(gains,h,mask_family=None):
    # Gains indexed by chronologically sorted original windows. Missing pairs contribute to neither mean nor denominator.
    observed=np.isfinite(gains).astype(float)
    values=np.nan_to_num(gains,nan=0.)
    mean=values.sum(axis=0)/observed.sum(axis=0).clip(1)
    result={}
    for b in BLOCKS:
        w=boot_weight(len(gains),b)
        m=(w@values)/np.maximum(1,w@observed)
        lo,hi=np.quantile(m,[.025,.975],axis=0)
        if b in {10,21}:
            sd=m.std(axis=0).clip(1.e-12)
            zz=(m-mean)/sd
            if mask_family is None:
                mult=np.max(np.abs(zz),axis=1)
                bounds=np.quantile(mult,.95)
            else:
                bounds=np.zeros(len(mean))
                for j in np.unique(mask_family):
                    use=mask_family==j
                    mult=np.max(np.abs(zz[:,use]),axis=1)
                    bounds[use]=np.quantile(mult,.95)
            result['family_low'+str(b)]=mean-bounds*sd
            result['family_high'+str(b)]=mean+bounds*sd
        result['low'+str(b)]=lo; result['high'+str(b)]=hi
    return result


def leader(res):
    res=res.copy()
    res['up']=(res.endpoint>0).astype(int)
    res['right']=((res.p_up>=.5)==res.up).astype(int)
    res['correct_up']=res.right.where(res.up.eq(1))
    res['correct_down']=res.right.where(res.up.eq(0))
    for label,columns in [('checkpoint',['horizon','checkpoint','model']),('checkpoint-cohort',['horizon','cohort','checkpoint','model']),
                          ('update-only',['horizon','model']),('literal-calendar',['horizon','checkpoint','model'])]:
        data=res if label not in {'update-only','literal-calendar'} else res[res.checkpoint.gt(0)] if label=='update-only' else res[res.literal_calendar.eq(1)]
        out=data.groupby(columns,as_index=False).agg(n=('origin','size'),origins=('origin','nunique'),targets=('target','nunique'),
                **{f:(f,'mean') for f in METRICS},up_rate=('up','mean'),accuracy=('right','mean'),
                tpr=('correct_up','mean'),tnr=('correct_down','mean'))
        out['balanced_accuracy']=(out.tpr+out.tnr)/2
        write(label+'-leaderboard.csv',out)


def matched(res,d):
    results=[]; phase_rows=[]; grouped_rows=[]; influence=[]
    extreme=matrix('distinct-extreme-episodes.csv',V14).reset_index()
    for h in HORIZONS:
        ref=res[res.horizon.eq(h)]
        days=pd.Index(ref.origin.unique()).sort_values()
        gain_series=[]; ids=[]
        for k in ('issue','updated',*[str(s) for s in CHECKPOINTS[h] if s]):
            chosen=ref[ref.checkpoint.eq(0)] if k=='issue' else ref[ref.checkpoint.gt(0)] if k=='updated' else ref[ref.checkpoint.eq(int(k))]
            gs=chosen.groupby('model')
            labels=chosen.drop_duplicates('origin').set_index('origin')
            for a,b,purpose,family in CONTRASTS:
                c=gs.get_group(a).set_index(['origin','checkpoint'])
                f=gs.get_group(b).set_index(['origin','checkpoint'])
                c,f=c.align(f,join='inner',axis=0)
                delta=c[list(MAIN_MATCH)]-f[list(MAIN_MATCH)]
                c0=c[list(MAIN_MATCH)].where(delta.notna()).groupby(level=0).mean()
                f0=f[list(MAIN_MATCH)].where(delta.notna()).groupby(level=0).mean()
                agg=delta.groupby(level=0).mean().reindex(days)
                for m in MAIN_MATCH:
                    if agg[m].count()<40:
                        continue
                    g=agg[m]
                    row=dict(horizon=h,checkpoint=k,reference=a,candidate=b,attribution=purpose,metric=m,
                             n=int(g.count()),rows=int(delta[m].count()),distinct_targets=int(labels.loc[g.dropna().index,'target'].nunique()),
                             control=float(c0[m].mean()),model=float(f0[m].mean()),gain=float(g.mean()))
                    gain_series.append(g.to_numpy())
                    ids.append(f'{k}-{m}-{family}')
                    for ct in ('early','later'):
                        field=g.reindex(labels[labels.cohort.eq(ct)].index)
                        row[ct+'_gain']=field.mean()
                        row[ct+'_n']=field.count()
                    results.append(row)
                    if k in ('issue','updated') and m in ('brier','endpoint_crps','range_crps','vol_mae') and a in ('iv_restart','gjr_restart'):
                        v=g.dropna().rename('gain').to_frame()
                        v['phase']=[d.positions[i]%h for i in v.index]
                        v['target']=labels.loc[v.index,'target']
                        v['target_month']=v.target.str[:7]
                        v['endpoint_cluster']=(v.target.map(d.positions)//h).astype(int)
                        ids0=dict(horizon=h,checkpoint=k,reference=a,candidate=b,metric=m)
                        for n,z in v.groupby('phase'):
                            phase_rows.append(dict(**ids0,phase=n,n=len(z),gain=z.gain.mean()))
                        for n,z in v.groupby('target'):
                            grouped_rows.append(dict(**ids0,group='fixed_endpoint',level=n,n=len(z),gain=z.gain.mean()))
                        for n,z in v.groupby('endpoint_cluster'):
                            grouped_rows.append(dict(**ids0,group='disjoint_calendar_bucket',level=str(n),n=len(z),gain=z.gain.mean()))
                        for n,z in v.groupby('target_month'):
                            influence.append(dict(**ids0,deletion_type='target_month',omitted=n,n_removed=len(z),n_remaining=len(v)-len(z),
                                                  gain=v.loc[v.target_month.ne(n),'gain'].mean()))
                        for zz in extreme[extreme.horizon.eq(h)&extreme.event.isin(['upper_fixed','lower_fixed','range_fixed'])].itertuples(index=False):
                            keep=~(v.index.to_series().le(zz.last_endpoint)&v.target.ge(zz.first_origin))
                            if keep.all():
                                continue
                            influence.append(dict(**ids0,deletion_type='overlapping_extreme_episode',omitted=f'{zz.event} {zz.episode}',
                                            n_removed=int((~keep).sum()),n_remaining=int(keep.sum()),gain=v.loc[keep,'gain'].mean()))
        adjust=paired_intervals(np.column_stack(gain_series),h,np.array(ids))
        start=len(results)-len(gain_series)
        for i,row in enumerate(results[start:]):
            row.update({col:vals[i] for col,vals in adjust.items()})
    for name,rows in [('matched-window-evidence',results),('disjoint-phase-evidence',phase_rows),
                      ('endpoint-cluster-evidence',grouped_rows),('leave-group-out-evidence',influence)]:
        write(name+'.csv.gz' if name=='endpoint-cluster-evidence' else name+'.csv',pd.DataFrame(rows))


def revisions(res):
    x=res.sort_values(['horizon','origin','model','checkpoint']).copy()
    groups=x.groupby(['horizon','origin','model'],sort=False)
    values=['p_up','endpoint_mean','endpoint_q50','remaining_vol_mean','endpoint_width80','endpoint_q10','endpoint_q90','remaining_range_mean',
            'expand25'] if 'expand25' in x.columns else ['p_up','endpoint_mean','endpoint_q50','remaining_vol_mean','endpoint_width80',
                                                       'endpoint_q10','endpoint_q90','remaining_range_mean']
    for field in values:
        x['old_'+field]=groups[field].shift()
        x['rev_'+field]=x[field]-x['old_'+field]
    x=x[x.checkpoint.gt(0)].copy()
    x['direction_error']=(x.endpoint>0).astype(float)-x.old_p_up
    x['endpoint_error']=x.endpoint-x.old_endpoint_mean
    x['half_update_p']=.50*x.p_up+.50*x.old_p_up
    x['half_brier']=(x.half_update_p-(x.endpoint>0))**2
    x['old_brier']=x.direction_error**2
    fields=IDENT+values+['old_'+f for f in values]+['rev_'+f for f in values]+[
           'endpoint','brier','old_brier','half_brier','direction_error','endpoint_error']
    write('revision-attribution.csv.gz',x[fields])
    result=[]
    for (h,model),g in x.groupby(['horizon','model']):
        for k,f in [('all',g),*[(str(u),v) for u,v in g.groupby('checkpoint')]]:
            if k!='all' and int(k) not in CHECKPOINTS[h]:
                continue
            base=dict(horizon=h,model=model,checkpoint=k,n=len(f),n_origins=f.origin.nunique(),
                      old_brier=f.old_brier.mean(),new_brier=f.brier.mean(),half_update_brier=f.half_brier.mean())
            for field in values:
                v=f['rev_'+field]
                z=f['old_'+field]
                y=f.direction_error if field=='p_up' else f.endpoint_error if field=='endpoint_mean' else None
                vv=np.mean((v-v.mean())**2)
                cu=np.mean((z-z.mean())*(v-v.mean()))
                result.append(dict(**base,quantity=field,mean_revision=v.mean(),mean_abs_revision=v.abs().mean(),
                         earlier_level_corr=cu/(v.std(ddof=0)*z.std(ddof=0)) if vv>0 and z.std(ddof=0)>0 else 0.,
                         revision_response_slope=float(np.mean((y-y.mean())*(v-v.mean()))/vv) if y is not None and vv>0 else np.nan))
    write('revision-evidence.csv',pd.DataFrame(result))


def aggregate_chunks(file,use,ix,fields):
    tables=[]
    for df in pd.read_csv(OUT/file,usecols=use,chunksize=130000,dtype={'barrier':str},low_memory=False):
        tables.append(df.groupby(ix,as_index=True,observed=True)[fields].agg(['sum','count']))
    return pd.concat(tables).groupby(level=list(range(len(ix)))).sum()


def survival():
    keys=['horizon','origin','checkpoint','model','barrier','side','opposite_after_hit']
    fields=['actual','p','brier','log_loss','integrated_brier','passage_log_loss','observed_rel_time','expected_time_given_hit']
    types={c:'float32' for c in fields}
    types.update(model='category',barrier='category',side='category',horizon='int16',checkpoint='int16',opposite_after_hit='int8',origin='category')
    reset=pd.read_csv(OUT/'sequential-passage.csv.gz',usecols=keys+fields,dtype=types,low_memory=False)
    assert not reset.duplicated(keys).any()
    w=pd.read_csv(OUT/'original-windows.csv',usecols=['horizon','origin','cohort','target'])
    q=reset.merge(w,on=['horizon','origin'],validate='many_to_one')
    q['window_active']=q.checkpoint.gt(0)
    cols=['horizon','model','barrier','side']
    lead=q.groupby(cols+['checkpoint','opposite_after_hit'],as_index=False,observed=True).agg(n=('actual','size'),origin_n=('origin','nunique'),
                              **{m:(m,'mean') for m in fields if m!='expected_time_given_hit'})
    write('passage-side-leaderboard.csv',lead)
    groups=[]
    for group,df in [('all surviving',q),('opposite after hit',q[q.opposite_after_hit.eq(1)]),('fixed thresholds',q[q.barrier.isin(list('01234'))]),
                     ('relative thresholds',q[q.barrier.astype(str).str.startswith('iv')])]:
        for stage,data in [('issue',df[df.checkpoint.eq(0)]),('updated',df[df.window_active])]:
            a=data.groupby(['horizon','model'],as_index=False,observed=True).agg(n=('actual','size'),origins=('origin','nunique'),targets=('target','nunique'),
                    **{m:(m,'mean') for m in fields if m!='expected_time_given_hit'})
            a['stage']=stage;a['group']=group;groups.append(a)
    write('passage-leaderboard.csv',pd.concat(groups,ignore_index=True))
    matchup=[]
    for h in HORIZONS:
        hh=q[q.horizon.eq(h)&q.window_active]
        comparisons=[]; diffs=[]; flags=[]
        keys=['origin','checkpoint','barrier','side']
        for label,g0 in [('all surviving',hh),('opposite after hit',hh[hh.opposite_after_hit.eq(1)])]:
            for a in ('frozen','iv_restart','gjr_restart','historical'):
                for b in ('refit','vol_state','analogue','particle','hybrid','shock_persistence','iv_restart'):
                    if a==b: continue
                    c=g0[g0.model.eq(a)].set_index(keys)
                    f=g0[g0.model.eq(b)].set_index(keys)
                    c,f=c.align(f,axis=0,join='inner')
                    for m in ('brier','integrated_brier','passage_log_loss'):
                        z=(c[m]-f[m]).groupby(level=0).mean()
                        diffs.append(z.reindex(w[w.horizon.eq(h)].origin).to_numpy())
                        flags.append(f'{label}-{m}')
                        comparisons.append(dict(horizon=h,group=label,reference=a,candidate=b,metric=m,n=len(c),origins=len(z),
                                                reference_loss=c[m].mean(),candidate_loss=f[m].mean(),average_episode_gain=z.mean()))
        u=paired_intervals(np.column_stack(diffs),h,np.array(flags))
        for i,r in enumerate(comparisons):
            r.update({k:v[i] for k,v in u.items()})
        matchup.extend(comparisons)
    write('passage-matched-risk-sets.csv',pd.DataFrame(matchup))
    cols=['horizon','checkpoint','model','barrier','score_order','score_additional']
    fields=['order_brier','no_additional_brier','known_upper','known_lower','no_additional_p','no_additional_actual','p_same_candle']
    z=aggregate_chunks('sequential-order.csv.gz',cols+fields,cols,fields)
    y=pd.DataFrame(index=z.index)
    y['count']=z['known_upper']['count']
    for col in fields:
        y[col]=z[col]['sum']/z[col]['count'].replace(0,np.nan)
    write('first-passage-ordering-evidence.csv',y.reset_index())
    # Conditional timing is distinct from the Brier aggregate. Use only cases with an event and nonzero forecast mass.
    f=q[q.actual.eq(1)&q.expected_time_given_hit.notna()].copy()
    f['abs_time_error']=abs(f.expected_time_given_hit-f.observed_rel_time)
    f['timing_bias']=f.expected_time_given_hit-f.observed_rel_time
    timing=f.groupby(['horizon','checkpoint','model','barrier','opposite_after_hit'],observed=True).agg(
            n=('actual','size'),abs_error=('abs_time_error','mean'),bias=('timing_bias','mean'))
    write('conditional-time-given-touch.csv',timing.reset_index())


def shock(scores,d):
    records=[]
    for r in read('joint-update-receipts.json'):
        s=r['posterior']
        records.append(dict(horizon=r['horizon'],origin=r['origin'],checkpoint=r['checkpoint'],trigger=s['trigger'],
                            z=s['last_z'],cusum=s['cusum'],risk_multiplier=s['risk_multiplier'],
                            analogue_ess=r['analogue_ess'],particle_ess=r['particle_ess']))
    a=pd.DataFrame(records)
    y=scores[scores.model.isin(['iv_restart','vol_only_shock','shock_persistence','incremental'])].merge(
                          a,on=['horizon','origin','checkpoint'],validate='many_to_one')
    y=y[y.checkpoint.gt(0)].copy()
    prev=y['asof'].map(d.features.daily_log_return)
    y['continuation']=((prev*y.remaining_return)>0).astype(int)
    y['reversal']=((prev*y.remaining_return)<0).astype(int)
    y['same_sign_p']=np.where(prev>0,y.p_remaining_up,1-y.p_remaining_up)
    y['continuation_brier']=(y.same_sign_p-y.continuation)**2
    y['signed_remaining']=np.sign(prev)*y.remaining_return
    c=y.groupby(['horizon','trigger','model'],as_index=False).agg(n=('origin','size'),origins=('origin','nunique'),
             mean_abs_z=('z',lambda x:np.mean(abs(x))),mean_signed_remaining=('signed_remaining','mean'),
             continuation=('continuation','mean'),reversal=('reversal','mean'),predicted_continuation=('same_sign_p','mean'),
             signed_brier=('continuation_brier','mean'),vol=('vol','mean'),range=('range','mean'),remaining_brier=('remaining_brier','mean'),
             endpoint_crps=('endpoint_crps','mean'),vol_mae=('vol_mae','mean'),range_crps=('range_crps','mean'))
    write('shock-response-evidence.csv',c)
    f=pd.read_csv(OUT/'sequential-passage.csv.gz',usecols=['horizon','origin','checkpoint','model','brier','integrated_brier'],chunksize=140000)
    rows=[]
    for z in f:
        z=z[z.checkpoint.gt(0)&z.model.isin(['iv_restart','vol_only_shock','shock_persistence'])]
        rows.append(z.merge(a,on=['horizon','origin','checkpoint'],validate='many_to_one').groupby(['horizon','trigger','model']).agg(
            cases=('brier','size'),touch_sum=('brier','sum'),passage_sum=('integrated_brier','sum')))
    k=pd.concat(rows).groupby(level=list(range(3))).sum()
    k['touch_brier']=k.touch_sum/k.cases
    k['integrated_brier']=k.passage_sum/k.cases
    write('shock-touch-evidence.csv',k.reset_index())


def run():
    d=Daily.load()
    res=pd.read_csv(OUT/'sequential-scores.csv.gz',usecols=list(dict.fromkeys(IDENT+list(METRICS))),low_memory=False)
    leader(res)
    matched(res,d)
    print('Scored paired fixed-window controls at all registered checkpoints',flush=True)
    revisions(res)
    shock(res,d)
    survival()
    print('Aggregated remaining first-touch risk sets and revision diagnostics',flush=True)


if __name__=='__main__':
    run()
