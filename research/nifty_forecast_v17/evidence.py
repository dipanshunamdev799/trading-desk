"""Compare exact matched cases and cluster all intraday evidence by trading date."""
from .common import *
from .residual import BIN_TARGETS,RISK_TARGETS
from research.nifty_forecast_v16.evidence import bands

METRICS=('brier','crps','log_loss','abs_error','sq_error','qlike','quantile_loss','interval_score')
EP_METRICS=('brier','endpoint_crps','range_crps','vol_mae','variance_qlike','energy','touch_brier','integrated_brier')
PASS=('brier_by_1','touch_brier','conditional_brier','integrated_brier','event_time_log','brier_by_3','brier_by_5','brier_by_10','brier_by_21')


def load(name,root=OUT):
    return pd.read_csv(root/name,low_memory=False)


def mmean(v):
    return float(v.mean()) if len(v) else np.nan


def nonoverlap(g):
    if 'target_end' not in g:
        return g.day.nunique()
    last='';count=0
    for day,end in g[['day','target_end']].dropna().drop_duplicates().sort_values(['day','target_end']).itertuples(index=False,name=None):
        if day>last:
            count+=1;last=end
    return count


def match(z,groups,metrics,ref,check_disjoint=False):
    out=[]
    for key,g in z.groupby(groups,sort=True):
        if not isinstance(key,tuple):key=(key,)
        label=dict(zip(groups,key))
        days=pd.Index(sorted(g.day.unique()))
        rows=[];series=[]
        models={k:v.set_index('day').sort_index() for k,v in g.groupby('model')}
        for a,b in ref(label,g):
            if a==b or a not in models or b not in models:continue
            v,u=models[a].align(models[b],axis=0,join='inner')
            assert not v.index.has_duplicates
            if len(v)<20:continue
            for metric in metrics:
                if metric not in v or metric not in u:continue
                d=(u[metric]-v[metric]).dropna()
                if len(d)<20:continue
                ia=v.loc[d.index]
                ib=u.loc[d.index]
                r=dict(**label,candidate=a,control=b,metric=metric,n=len(d),candidate_loss=v.loc[d.index,metric].mean(),
                       control_loss=u.loc[d.index,metric].mean(),gain=d.mean(),early_n=int(ia.cohort.eq('early').sum()),
                       later_n=int(ia.cohort.eq('later').sum()),early_gain=mmean(d.loc[ia.cohort.eq('early')]),later_gain=mmean(d.loc[ia.cohort.eq('later')]),
                       candidate_coverage80=mmean(ia.covered) if 'covered' in ia else np.nan,
                       control_coverage80=mmean(ib.covered) if 'covered' in ib else np.nan,
                       disjoint=nonoverlap(ia.reset_index()) if check_disjoint else np.nan)
                rows.append(r);series.append(d.reindex(days).to_numpy())
        if rows:
            ci=bands(np.stack(series,axis=1),[r['metric'] for r in rows])
            out.extend([r|{k:v[i] for k,v in ci.items()} for i,r in enumerate(rows)])
    return pd.DataFrame(out)


def summarize(z,groups,event=None):
    out=[];calibration=[]
    full=pd.concat([z,z.assign(cohort='combined')],ignore_index=True)
    for key,g in full.groupby([*groups,'cohort','model']):
        r=dict(zip([*groups,'cohort','model'],key))
        d=r|dict(n=g.day.nunique(), disjoint=nonoverlap(g),observations=len(g))
        for k in (*METRICS,'mae','mean','median','width','covered','p'):
            if k in g:d[k]=mmean(g[k])
        if 'sq_error' in g:d['rmse']=np.sqrt(d['sq_error'])
        if 'abs_error' in g:d['median_abs_error']=g.abs_error.median()
        is_event=event and event in g
        event_truth=g[event].gt(.5) if is_event else g.actual.gt(0) if 'actual' in g else None
        if 'p' in g and event_truth is not None and g.p.notna().any():
            flag=g.p.notna();hit=(g.p.ge(.5)==event_truth).where(flag)
            d['accuracy']=hit.mean();d['realized_rate']=event_truth.loc[flag].mean()
            d['balanced_accuracy']=(mmean(hit[event_truth])+mmean(hit[~event_truth]))/2
            tmp=pd.DataFrame(dict(p=g.p,hit=event_truth))
            tmp['bin']=np.minimum(np.floor(tmp.p*10),9)
            for k,a in tmp.groupby('bin'):
                calibration.append(r|dict(bin=int(k),n=len(a),mean_probability=a.p.mean(),observed_rate=a.hit.mean()))
        if {'actual','mean'}.issubset(g) and g.actual.nunique()>1 and g['mean'].nunique()>1:
            d['rank_correlation']=g[['actual','mean']].rank().corr().iloc[0,1]
        out.append(d)
    return pd.DataFrame(out),pd.DataFrame(calibration)


def with_event(z):
    d=z.copy()
    d['event']=np.where(d.target.isin(BIN_TARGETS),d.actual.gt(.5),d.actual.gt(0))
    d['event']=d.event.astype(float)
    return d


def passage_compare(file,refs,screen='original'):
    z=load(file)
    if screen=='prefix_survivor':z=z[z.known_touch.eq(0)]
    rows=[]
    for (h,cut),g in z.groupby(['horizon','cutoff']):
        models={m:s.set_index(['day','barrier','side']) for m,s in g.groupby('model')}
        for a,b in refs:
            if a not in models or b not in models:continue
            v,u=models[a].align(models[b],axis=0,join='inner')
            for metric in PASS:
                if metric not in v or metric not in u:continue
                k=v[metric].notna()&u[metric].notna()
                if not k.any():continue
                x=v.loc[k,metric].groupby(level='day').mean();y=u.loc[k,metric].groupby(level='day').mean()
                days=pd.Index(sorted(g.day.unique()))
                d=y-x
                ii=bands(d.reindex(days).to_numpy()[:,None],['passage'])
                rows.append(dict(horizon=h,cutoff=cut,candidate=a,control=b,screen=screen,metric=metric,
                   n=len(x),side_barrier_cases=int(k.sum()),candidate_loss=x.mean(),control_loss=y.mean(),gain=d.mean(),
                   **{k:u[0] for k,u in ii.items()}))
    return pd.DataFrame(rows)


def run():
    res=with_event(pd.concat([load('residual-'+c.replace(':','')+'-scores.csv.gz') for c in SESSION_CLOCKS],ignore_index=True))
    columns=['cutoff','target']
    summary,cal=summarize(res,columns,'event')
    write('postopen-model-leaderboard.csv',summary)
    write('postopen-probability-calibration.csv',cal)
    def all_parents(key,g):
        if key['target'] in BIN_TARGETS or key['target'] in RISK_TARGETS:
            core='native_control'
        else:
            core='price_vol'
        baseline=list(g[['model','baseline']].drop_duplicates().itertuples(index=False,name=None))
        return list(dict.fromkeys(baseline+[(k,core) for k in g.model.unique() if k!=core]))
    tab=match(res,columns,METRICS,all_parents,True)
    write('postopen-matched-evidence.csv',tab)
    sources=res[['cutoff','target','model','category']].drop_duplicates().rename(columns={'model':'candidate'})
    maps=tab.merge(sources,on=['cutoff','target','candidate'],validate='m:1')
    maps=maps[maps.category.ne('parent')].copy()
    maps['simultaneous_benefit']=(maps.adjusted_low21>0)&(maps.early_gain>0)&(maps.later_gain>0)
    write('multiscale-information-matrix.csv',maps)
    net=load('network-scores.csv.gz')
    k,_=summarize(net,columns)
    write('network-leaderboard.csv',k)
    net_ev=match(net,columns,('crps','brier','abs_error'),lambda _,g:[(m,'own_state') for m in g.model.unique()],True)
    write('network-matched.csv',net_ev)
    orig=load('original-clock-forecasts.csv.gz').rename(columns={'target_date':'target_end'})
    cols=['horizon','cutoff']
    ks,rr=summarize(orig,cols)
    write('original-timed-leaderboard.csv',ks)
    write('original-timed-calibration.csv',rr)
    pairs=match(orig,cols,METRICS,lambda _,g:[(m,'clock_structural') for m in g.model.unique()]+[('stock_residual','stock_direct')],True)
    write('original-timed-matched.csv',pairs)
    z=load('protected-law-residual-overlays.csv.gz').rename(columns={'target_date':'target_end'})
    z0=load('protected-original-scores.csv.gz').rename(columns={'target_date':'target_end'})
    zz=pd.concat([z,z0.assign(cutoff='after_prior_guard')],ignore_index=True)
    refs=lambda k,g:[('V14_stock_overlay','V14_sign_shrinkage' if k['horizon']==5 else 'V14_domestic_GJR')]
    ov=match(zz,cols,('brier','crps','log_loss'),refs,True).assign(subset='full')
    only=zz.merge(z.loc[z.adapted.eq(1),['day','horizon']].drop_duplicates(),on=['day','horizon'])
    write('original-protected-overlay-matched.csv',pd.concat([ov,match(only,cols,('brier','crps','log_loss'),refs,True).assign(subset='adapted')]))
    # A distinct native pre-auction and same-clock previous-close comparison stays separate from post-open laws.
    p=load('retimed-path-scores.csv.gz').rename(columns={'target':'target_end'})
    k,_=summarize(p,cols)
    write('retimed-path-leaderboard.csv',k)
    p_refs=[('decomposed_gift','decomposed'),('session_state','decomposed'),('decomposed_gift','same_clock_IV'),('decomposed_gift','same_clock_GJR'),
            ('session_state','same_clock_IV'),('session_state','same_clock_GJR')]
    write('retimed-path-matched.csv',match(p,cols,EP_METRICS,lambda *_:p_refs,True))
    write('retimed-barrier-matched.csv',passage_compare('retimed-passage-scores.csv.gz',p_refs))
    q=load('postopen-path-scores.csv.gz').rename(columns={'target':'target_end'})
    q_refs=[('cash_IV_stock','cash_IV')]
    write('postopen-path-matched.csv',match(q,cols,EP_METRICS,lambda *_:q_refs,True))
    write('postopen-barrier-matched.csv',pd.concat([passage_compare('postopen-passage-scores.csv.gz',q_refs,'all'),
         passage_compare('postopen-passage-scores.csv.gz',q_refs,'prefix_survivor')]))
    r=load('postopen-volatility-scores.csv.gz').rename(columns={'target':'target_end','mae':'abs_error'})
    risk_ref=load('volatility-scores.csv.gz',V16).rename(columns={'target':'target_end','mae':'abs_error','actual_expand':'expansion','actual_vol':'actual','pred_vol':'mean'})
    risk0,_=summarize(r,cols,'expansion')
    write('postopen-volatility-leaderboard.csv',risk0)
    u=pd.concat([r,risk_ref],ignore_index=True)
    risk_options=('opening_surprise','participation','liquidity_disagreement','option_surface','raw_IV','cash_risk')
    risk_ev=match(u,cols,METRICS,lambda _,g:[(a,b) for a in risk_options for b in ('cash_risk','raw_iv','offshore_plus_domestic','fixed_iv_rv','GJR')],True)
    write('postopen-volatility-matched.csv',risk_ev)
    print('Matched evidence',len(tab),'post-open tested metric/contrast cells and',len(maps),'mapped source cells',flush=True)


if __name__=='__main__':
    run()
