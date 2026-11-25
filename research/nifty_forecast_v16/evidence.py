"""Matched-origin scores, reliability and dependence-aware comparisons."""
from functools import lru_cache

from .common import *

METRICS=('brier','crps','log_loss','mae','sq_error','mean','median','actual','correct','covered','width','interval_score','p_up',
         'p_down05','p_up05','p_down10','p_up10','down05_brier','up05_brier','pit')

@lru_cache(maxsize=90)
def weights(n,length):
    g=np.random.default_rng(SEED+29*n+107*length)
    js=g.integers(0,n,size=(BOOT,int(np.ceil(n/length))))
    ids=((js[:,:,None]+np.arange(length))%n).reshape((BOOT,-1))[:,:n]
    w=np.zeros((BOOT,n))
    np.add.at(w,(np.broadcast_to(np.arange(BOOT)[:,None],ids.shape),ids),1)
    return w


def bands(gains,cats):
    a=np.where(np.isfinite(gains),gains,0.)
    b=np.isfinite(gains).astype(float)
    center=a.sum(axis=0)/b.sum(axis=0)
    output={}
    for l in BLOCKS:
        w=weights(len(a),l)
        dist=(w@a)/(w@b).clip(1.)
        lo,hi=np.quantile(dist,[.025,.975],axis=0)
        output[f'lo{l}']=lo
        output[f'hi{l}']=hi
        if l in (10,21):
            delta=dist-center
            sd=delta.std(axis=0).clip(1.e-12)
            ff=np.array(cats)
            for tag in np.unique(ff):
                idx=ff==tag
                crit=np.quantile(np.max(abs(delta[:,idx])/sd[idx],axis=1),.95)
                lo[idx]=center[idx]-sd[idx]*crit
                hi[idx]=center[idx]+sd[idx]*crit
            output[f'adjusted_low{l}']=lo
            output[f'adjusted_high{l}']=hi
            output[f'lo{l}']=np.quantile(dist,.025,axis=0)
            output[f'hi{l}']=np.quantile(dist,.975,axis=0)
    return output


def pairs(frame,groups,metrics,pair_map=None,index='day',default='baseline'):
    out=[]
    for name,z in frame.groupby(groups,sort=False):
        ident=dict(zip(groups,name if isinstance(name,tuple) else (name,)))
        days=sorted(z[index].unique())
        models=sorted(z.model.unique())
        comps=pair_map(ident,z) if pair_map is not None else z[['model',default]].drop_duplicates().itertuples(index=False,name=None)
        deltas=[]; rows=[]
        for candidate,base in comps:
            if candidate==base or candidate not in models or base not in models:
                continue
            s=z[z.model.eq(candidate)].set_index(index)
            t=z[z.model.eq(base)].set_index(index)
            s,t=s.align(t,axis=0,join='inner')
            if len(s)<20:
                continue
            for mm in metrics:
                d=t[mm]-s[mm]
                ok=d.notna()
                if ok.sum()<20:
                    continue
                if 'cohort' in s:
                    later=d.loc[s.cohort.eq('later')].mean()
                    early=d.loc[s.cohort.eq('early')].mean()
                else:
                    later=np.nan;early=np.nan
                rows.append(dict(**ident,candidate=candidate,control=base,metric=mm,n=int(ok.sum()),candidate_loss=s.loc[ok,mm].mean(),
                    control_loss=t.loc[ok,mm].mean(),gain=d.mean(),early_gain=early,later_gain=later))
                deltas.append(d.reindex(days).to_numpy())
        if not rows:continue
        ci=bands(np.column_stack(deltas),[x['metric'] for x in rows])
        for j,row in enumerate(rows):
            row.update({k:s[j] for k,s in ci.items()})
        out.extend(rows)
    return pd.DataFrame(out)


def summarize_sessions(a):
    y=a.copy()
    y['up']=y.actual.gt(0).astype(int)
    y['correct_up']=y.correct.where(y.up.eq(1))
    y['correct_down']=y.correct.where(y.up.eq(0))
    y=pd.concat([y,y.assign(cohort='combined')])
    bands=['exercise','cutoff','target','cohort','model','family']
    out=y.groupby(bands,as_index=False).agg(n=('day','size'),unique_targets=('target_date','nunique'),pos_rate=('up','mean'),
                         tpr=('correct_up','mean'),tnr=('correct_down','mean'),**{m:(m,'mean') for m in METRICS})
    out['balanced_accuracy']=(out.tpr+out.tnr)/2
    out['rmse']=np.sqrt(out.sq_error)
    keep_group=['exercise','cutoff','target','model','cohort']
    dis=[]
    for group,v in y.groupby(keep_group,sort=False):
        prev='';n=0
        for q in v.sort_values(['target_date','origin']).itertuples(index=False):
            if q.origin>=prev:
                n+=1
                prev=q.target_date
        dis.append(dict(zip(keep_group,group),disjoint=n))
    out=out.merge(pd.DataFrame(dis),on=keep_group,validate='one_to_one')
    write('session-leaderboard.csv',out)
    # Reliability is scored for sign and for signed gaps above 0.5% and 1%.
    g=a[a.exercise.eq('opening_gap')].copy()
    rows=[]
    for col in ('p_up','p_up05','p_down05','p_up10','p_down10'):
        g['bin']=pd.cut(g[col],np.linspace(0,1,11),labels=False,include_lowest=True)
        g['hit']={'p_up':g.actual>0,'p_up05':g.actual>=.005,'p_down05':g.actual<=-.005,
                  'p_up10':g.actual>=.01,'p_down10':g.actual<=-.01}[col].astype(int)
        rows.append(g.groupby(['cutoff','model','bin'],as_index=False).agg(n=('model','size'),mean_forecast=(col,'mean'),
                      hit_rate=('hit','mean')).assign(event=col))
    write('gap-reliability.csv',pd.concat(rows,ignore_index=True))


def endpoints(s):
    expect=s.model.isin(['historical_iv'])
    base=s[expect]
    columns=['horizon','origin','target','cohort','actual_endpoint']
    d=base[columns].copy()
    d['day']=d.origin
    signal=[]; f=pd.read_csv(OUT/'session-targets.csv').set_index('origin')
    for r in d.itertuples(index=False):
        target='five' if r.horizon==5 else 'twentyone'
        hist=f.loc[(f['label_'+target]<r.origin)&f[target].notna(),target].tail(160).to_numpy()
        n=len(hist)
        assert n>=54
        # Preserve a symmetric empirical distribution as the distributional control for neutral.
        xn=np.r_[abs(hist),-abs(hist)]
        for name,p,x in [('neutral',.50,xn),('matured_historical',(np.sum(hist>0)+.5)/(n+1),hist)]:
            law=np.expm1(np.sort(x))
            y=r.actual_endpoint
            lo,hi=np.quantile(law,[.1,.9])
            crps=np.abs(law-y).mean()-law@(2*np.arange(len(law))-len(law)+1)/len(law)**2
            signal.append(dict(horizon=r.horizon,origin=r.origin,target=r.target,cohort=r.cohort,actual_endpoint=y,model=name,p_up=p,
                   brier=(p-(y>0))**2,log_loss=-np.log(p if y>0 else 1-p),endpoint_crps=crps,endpoint_mae=abs(law.mean()-y),
                   endpoint_coverage80=int(lo<=y<=hi),endpoint_width80=hi-lo))
    bb=pd.DataFrame(signal)
    legacy=pd.read_csv(V15/'earlier-endpoint-references.csv.gz')
    legacy=legacy.rename(columns={'actual':'actual_endpoint','p':'p_up','crps':'endpoint_crps','mae':'endpoint_mae',
                    'coverage80':'endpoint_coverage80','width80':'endpoint_width80'})
    legacy=legacy.drop_duplicates(['horizon','origin','model'])
    legacy=legacy.merge(d[['horizon','origin','target','cohort']],on=['horizon','origin'],validate='many_to_one')
    legacy['model']=legacy.model.str.replace('NEUTRAL','V13_NEUTRAL')
    metrics=['brier','log_loss','endpoint_crps','endpoint_mae','endpoint_coverage80','endpoint_width80']
    columns=['horizon','origin','model','target','cohort','actual_endpoint','p_up',*metrics]
    z=pd.concat([s[columns],bb[columns],legacy[columns]],ignore_index=True)
    z['correct']=(z.p_up.ge(.5)==z.actual_endpoint.gt(0)).astype(int)
    z['tpr']=z.correct.where(z.actual_endpoint.gt(0))
    z['tnr']=z.correct.where(z.actual_endpoint.le(0))
    x=pd.concat([z,z.assign(cohort='combined')])
    out=x.groupby(['horizon','cohort','model'],as_index=False).agg(n=('origin','nunique'),
         accuracy=('correct','mean'),hit_up=('tpr','mean'),hit_down=('tnr','mean'),**{m:(m,'mean') for m in metrics})
    out['balanced_accuracy']=(out.hit_up+out.hit_down)/2
    write('original-endpoint-leaderboard.csv',out)
    write('original-endpoint-scores.csv.gz',z)
    def references(key,g):
        preferred='V14_sign_shrinkage' if key['horizon']==5 else 'V14_domestic_GJR'
        return [(m,base) for m in g.model.unique() if m in set(s.model)|set(bb.model) for base in
                [preferred,'V15_gjr_restart','historical_iv','neutral']]
    pp=pairs(z,['horizon'],['brier','endpoint_crps','log_loss'],references,'origin')
    write('multiscale-matched.csv',pp)
    joint=s.groupby(['horizon','model'],as_index=False).agg(n=('origin','size'),
        **{k:(k,'mean') for k in ['brier','endpoint_crps','log_loss','range_crps','range_coverage80','range_width80','vol_mae','vol_crps','variance_qlike',
           'drawdown_crps','high_crps','low_crps','touch_brier','integrated_brier','energy']})
    write('joint-path-leaderboard.csv',joint)
    def sp(key,g):
        return [(m,b) for m in g.model.unique() if not m.startswith('V') for b in ['V14_gjr_student','V14_iv_scaled_blocks','V15_iv_restart','V15_gjr_restart','decomposed']]
    pp=pairs(s,['horizon'],['range_crps','vol_mae','touch_brier','integrated_brier','energy'],sp,'origin')
    write('joint-path-matched.csv',pp)


def opening_influence(a):
    a=a[a.exercise.eq('opening_gap')].copy()
    selected=['gift_calibrated','gift_raw','gift_plus_global','asia_partial','single_US','six_cash','equal_six','domestic']
    u=a[a.model.isin(selected)]
    tracked=pd.read_csv(OUT/'session-targets.csv',usecols=['day','origin','regular_weekday'])
    tracked['outside_normal']=tracked.regular_weekday.ne(1)
    prev=pd.to_datetime(tracked.origin)
    day=pd.to_datetime(tracked.day)
    tracked['holiday_gap']=np.busday_count(prev.to_numpy(dtype='datetime64[D]'),day.to_numpy(dtype='datetime64[D]'))>1
    tracked['weekend']=day.dt.day_of_week>=5
    z=u.merge(tracked[['day','outside_normal','holiday_gap','weekend']],on='day',validate='many_to_one')
    comps=[('gift_raw','equal_six'),('gift_raw','single_US'),('gift_raw','six_cash'),('gift_raw','asia_partial'),
           ('gift_plus_global','gift_calibrated'),('asia_partial','domestic')]
    rows=[]; episode=[]
    for k,v in z.groupby('cutoff'):
        for model,parent in comps:
            p=v[v.model.eq(model)].set_index('day')
            q=v[v.model.eq(parent)].set_index('day')
            p,q=p.align(q,axis=0,join='inner')
            if not len(p):continue
            for label,keep in [('all',p.actual.notna()),('ordinary',~p.outside_normal),('no_large_gaps',p.actual.abs()<.01),
                ('non_roll',p.roll_guard.eq(0)),('holiday_or_special',p.holiday_gap|p.outside_normal|p.weekend),
                ('strict_ordinary_non_roll',~(p.outside_normal|p.holiday_gap|p.weekend)&p.roll_guard.eq(0))]:
                if not keep.any():
                    continue
                for mm in ['brier','crps','mae','log_loss']:
                    gain=(q.loc[keep,mm]-p.loc[keep,mm])
                    rows.append(dict(cutoff=k,model=model,control=parent,case_filter=label,metric=mm,n=int(keep.sum()),
                                      loss=p.loc[keep,mm].mean(),base=q.loc[keep,mm].mean(),gain=gain.mean()))
            for period in sorted(set(p.index.str[:7])):
                keep=p.index.str[:7]!=period
                episode.append(dict(cutoff=k,model=model,control=parent,deletion='calendar_month',omitted=period,n=int(keep.sum()),
                        brier_gain=(q.loc[keep,'brier']-p.loc[keep,'brier']).mean(),crps_gain=(q.loc[keep,'crps']-p.loc[keep,'crps']).mean()))
            gp=np.flatnonzero(p.actual.abs().ge(.01).to_numpy())
            batch=np.split(gp,np.flatnonzero(np.diff(gp)>2)+1)
            for zz in batch:
                if not len(zz):continue
                keep=np.ones(len(p),bool)
                keep[zz[0]:zz[-1]+1]=False
                episode.append(dict(cutoff=k,model=model,control=parent,deletion='large_gap_episode',
                        omitted=f'{p.index[zz[0]]} to {p.index[zz[-1]]}',n=int(keep.sum()),
                        brier_gain=(q.loc[keep,'brier']-p.loc[keep,'brier']).mean(),crps_gain=(q.loc[keep,'crps']-p.loc[keep,'crps']).mean()))
    for n,data in [('opening-gap-sensitivity',rows),('opening-gap-deletion',episode)]:
        write(n+'.csv',pd.DataFrame(data))
    aa=a[a.model.isin(['gift_raw','gift_calibrated','domestic','asia_partial'])].copy()
    aa['cutoff_family']=aa.model
    aa['model']=aa.cutoff
    def time_pairs(*args):
        return [(c,'09:10') for c in CLOCKS[:3]]+[(c,'08:30') for c in ('08:45','08:55')]
    write('opening-clock-matched.csv',pairs(aa,['cutoff_family'],['brier','crps','mae','log_loss'],time_pairs))


def run():
    a=pd.concat([pd.read_csv(f,low_memory=False) for k in ['opening','decay','network'] for f in sorted(OUT.glob(k+'-*-scores.csv.gz'))],ignore_index=True)
    a.loc[a.target.eq('session_risk'),['brier','log_loss','correct','down05_brier','up05_brier']]=np.nan
    summarize_sessions(a)
    opening_influence(a)
    def compare(key,g):
        parent=list(g[['model','baseline']].drop_duplicates().itertuples(index=False,name=None))
        if key['exercise']=='opening_gap':
            parent.extend([(m,z) for m in ['gift_raw','gift_plus_global','asia_partial','rich_global_ridge'] for z in
                           ['domestic','single_US','equal_six','six_cash','gift_calibrated']])
        return sorted(set(parent))
    write('session-matched-evidence.csv',pairs(a,['exercise','cutoff','target'],['brier','crps','log_loss','mae'],compare))
    print('Session evidence and calibration:',len(a),'forecasts',flush=True)
    endpoints(pd.read_csv(OUT/'path-scores.csv.gz',low_memory=False))
    v=pd.read_csv(OUT/'volatility-scores.csv.gz')
    def vp(key,g):
        return [(m,b) for m in g.model.unique() for b in ['raw_iv','fixed_iv_rv','student_EGARCH','price_seen_risk_only']]
    write('volatility-matched.csv',pairs(v,['horizon','cutoff'],['brier','log_loss','mae','qlike'],vp))
    direct=pd.read_csv(OUT/'session-continuation-scores.csv.gz')
    f=pd.read_csv(OUT/'first-touch-fill-scores.csv.gz')
    write('absorption-matched.csv',pairs(direct,['cutoff','target'],['brier','log_loss'],
        lambda key,g:[(m,'gap_sign_size') for m in g.model.unique()]))
    write('fill-matched.csv',pairs(f,['cutoff','threshold'],['brier','integrated_brier','time_log_loss'],
        lambda key,g:[(m,'survivor_history') for m in g.model.unique()]))
    print('Paired model and null-independent score tables complete',flush=True)

if __name__=='__main__':
    run()
