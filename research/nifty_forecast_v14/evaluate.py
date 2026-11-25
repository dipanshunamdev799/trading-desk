"""Matched multi-objective scoring and overlap-aware simultaneous uncertainty."""
from functools import lru_cache
from scipy.stats import spearmanr

from .common import *
from .diagnostics import disjoint
from .path_score import ENERGY, summaries, multivariate

EXPECTED={5:265,21:217}
V13_RISK={'iv_nearest':'V13_raw_ATM','iv_bracket':'V13_bracketed_IV','iv_calibrated':'V13_calibrated_IV',
          'egarch':'V13_EGARCH','gjr':'V13_GJR','prior_trailing':'V13_trailing',
          'fixed_iv_rv_0.75':'V13_75IV25RV','prior_intraday':'V13_IV_intraday','prior_fitted_iv':'V13_fitted_IV'}
V13_END={'PH_NATIVE_PHASE_MIXTURE__scale_only':'V13_week_Brier','J12_GROUP_BALANCED__scale_only':'V13_week_CRPS',
         'B_CHANGE':'V11_later_Brier','V8_W_STRUCT_EMBARGO_EQ':'V11_later_CRPS',
         'NEUTRAL':'symmetric','NEUTRAL__scale_only':'V13_IV_scaled_symmetric',
         'V12_NATIVE_RV':'V12_week_Brier','J12_Q_GROUP':'V12_week_CRPS'}
TRANSITIONS={'expand','contract','high_state','enter_high','exit_high','persist_high','rapid_risk','variance_extreme'}
PATH_RANGE=['range','high','low','drawdown','abs_return','max_gap','rebound','regular_sd','overnight_sd']


def keep_scope(data,scope):
    return data if scope=='combined' else data[data.cohort.eq(scope)]


def add_cohort(a,y):
    if 'cohort' not in a:
        a=pd.concat([f.assign(cohort=f.origin.map(y[h].cohort)) for h,f in a.groupby('horizon')],ignore_index=True)
    assert a.cohort.notna().all()
    return a


def effective(v):
    z=np.asarray(v,float)
    z=z-np.mean(z)
    frac=z@z
    if frac<1.e-15:
        return np.nan
    total=0.
    for j in range(1,min(25,len(z)//3)):
        rho=z[j:]@z[:-j]/frac
        if rho<=0:
            break
        total+=rho
    return len(z)/(1+2*total)


def volatility_rows(y):
    old=pd.read_csv(V13/'scored-volatility.csv',low_memory=False)
    old=old[old.model.isin(V13_RISK)].loc[:,['horizon','model','origin','prediction']]
    # The two predeclared horizons use different raw option maturity choices.
    old=old.loc[~((old.model.eq('iv_bracket')&old.horizon.eq(5))|(old.model.eq('iv_nearest')&old.horizon.eq(21)))]
    old['model']=old.model.map(V13_RISK)
    dfs=[old,pd.read_csv(OUT/'process-risk-predictions.csv'),pd.read_csv(OUT/'point-risk-models.csv')]
    p=pd.concat(dfs,ignore_index=True)
    p['actual']=[y[h].at[d,'volatility'] for h,d in zip(p.horizon,p.origin)]
    p['mae']=abs(p.actual-p.prediction)
    p['se']=(p.actual-p.prediction)**2
    z=(p.actual/p.prediction)**2
    assert (z>0).all()
    p['qlike']=z-np.log(z)-1
    p['bias']=p.prediction-p.actual
    p['target']='volatility'
    return add_cohort(p,y)


def prior_path_marginals(y):
    rows=[]; joint=[]
    for h in HORIZONS:
        old=y[h]
        with np.load(V13/f'joint-path-target-atoms-{h}.npz',allow_pickle=False) as a:
            values=a['values']
            names=a['targets'].tolist()
            keys=a['keys']
        for j,(d,name) in enumerate(keys):
            if name not in ['iv_scaled','rv_scaled','diffusion_iv']:
                continue
            t=old.loc[d]
            a=values[j].astype(float)
            weight=np.full(len(a),1/len(a))
            used=[k for k in PATH_RANGE+['volatility','endpoint_return'] if k in names]
            idx=[names.index(k) for k in used]
            base=dict(horizon=h,origin=d,cohort=t.cohort,model='V13_'+name)
            s=summaries(a[:,idx],t[used].to_numpy(float),weight)
            for k,val in zip(used,s):
                rows.append(dict(**base,**val,target=k,actual=t[k],p_up=float((a[:,names.index(k)]>0).mean()) if k=='endpoint_return' else np.nan))
            selected=[names.index(k) for k in ENERGY]
            std=old.iloc[mature(old,d,180)][list(ENERGY)].std().clip(.003).to_numpy()
            joint.append(dict(**base,**multivariate(a[:,selected],t[list(ENERGY)].to_numpy(float),std,weight)))
        with np.load(OUT/f'observed-{h}.npz',allow_pickle=False) as a:
            p=a['paths']
        for row in old[old.cohort.notna()].itertuples():
            hist=p[mature(old,row.Index,210)]
            r=hist[:,:,1].max(axis=1)-hist[:,:,2].min(axis=1)
            s=summaries(r,np.array([row.range]),np.full(len(r),1/len(r)))[0]
            rows.append(dict(horizon=h,origin=row.Index,cohort=row.cohort,model='V13_empirical_range',target='range',
                             actual=row.range,**s))
    p=pd.DataFrame(rows)
    q=p.target.eq('endpoint_return')
    p.loc[q,'brier']=(p.loc[q,'p_up']-p.loc[q,'actual'].gt(0))**2
    pr=p.loc[q,'p_up'].clip(.0005,.9995)
    p.loc[q,'log_loss']=-np.log(np.where(p.loc[q,'actual'].gt(0),pr,1-pr))
    return p,pd.DataFrame(joint)


def marginal_rows(y):
    p=pd.read_csv(OUT/'path-marginals.csv.gz',low_memory=False)
    standalone=pd.read_csv(OUT/'endpoint-attribution.csv',low_memory=False)
    archive=pd.read_csv(OUT/'benchmark-endpoint-origins.csv',low_memory=False)
    archive=archive.rename(columns={'squared_error':'se','p':'p_up'})
    archive['model']=archive.model.map(V13_END)
    cols=[c for c in p if c in archive and c!='cohort']
    archive=add_cohort(archive[cols],y)
    replay,joint=prior_path_marginals(y)
    data=pd.concat([p,standalone,archive,replay],ignore_index=True)
    assert not data.duplicated(['horizon','origin','model','target']).any()
    return dict(frame=data,joint=joint)


def binary_rows(y):
    old=pd.read_csv(OUT/'transition-and-tail-probabilities.csv.gz',low_memory=False)
    old['model']=old.model.replace({'jump_1m':'jump_1m_logistic'})
    new=pd.read_csv(OUT/'path-tail-and-transition-probabilities.csv.gz',low_memory=False)
    b=add_cohort(pd.concat([new.drop(columns='cohort'),old],ignore_index=True),y)
    assert not b.duplicated(['horizon','origin','model','event']).any()
    probability=b.p.clip(.0005,.9995)
    b['brier']=(b.p-b.actual)**2
    b['log_loss']=-np.log(np.where(b.actual.eq(1),probability,1-probability))
    b['target']=b.event
    return b


def passage_rows(y):
    p=pd.read_csv(OUT/'path-passage.csv.gz',low_memory=False,dtype={'barrier':str})
    p['diagnostic_time_error']=abs(p.expected_time_given_touch-p.actual_time).where(p.actual.eq(1))
    model=pd.read_csv(OUT/'direct-barriers.csv',low_memory=False,dtype={'barrier':str})
    model=add_cohort(model,y)
    model['brier']=(model.p_touch-model.actual)**2
    model['log_loss']=-np.log(np.where(model.actual.eq(1),model.p_touch,1-model.p_touch).clip(.0005,1))
    old=pd.read_csv(OUT/'benchmark-touch-origins.csv')
    old['model']='V13_'+old.model
    old=add_cohort(old,y)
    fixed=p[p.barrier.isin(list('01234'))]
    agg_base=pd.concat([fixed[['horizon','origin','cohort','model','brier','log_loss','integrated_brier','passage_log_loss']],
                         model[['horizon','origin','cohort','model','brier','log_loss']]],ignore_index=True)
    agg=agg_base.groupby(['horizon','origin','cohort','model'])[['brier','log_loss','integrated_brier','passage_log_loss']].mean().reset_index()
    fixed_mean=pd.concat([agg,old],ignore_index=True).assign(target='fixed_touch_family')
    return p, model, fixed_mean


def score_table(data,y,group,metrics,risk=False,endpoint=False,actual='actual'):
    rows=[]
    scope=('combined','early','later')
    for c in scope:
        a=keep_scope(data,c)
        for ids,b in a.groupby(group,sort=False,observed=True):
            r=dict(zip(group,ids))
            h=r['horizon']
            days=tuple(sorted(b.origin.unique()))
            r.update(cohort=c,n=len(days),disjoint=cached_disjoint(h,days),
              prediction_rows=len(b))
            if actual in b:
                r['ess']=effective(b.sort_values('origin')[actual].to_numpy())
            r.update({k:float(b[k].mean()) if k in b else np.nan for k in metrics})
            if 'se' in r:
                r['rmse']=np.sqrt(r.pop('se'))
            if risk and b.prediction.nunique()>1:
                r['rank_correlation']=spearmanr(b.actual,b.prediction).statistic
            if endpoint:
                true=b.actual.gt(0)
                sign=b.p_up.ge(.5)
                r.update(accuracy=(true==sign).mean(),balanced_accuracy=.5*(sign[true].mean()+(~sign[~true]).mean()))
            rows.append(r)
    return pd.DataFrame(rows)


Y={}


@lru_cache(maxsize=20000)
def cached_disjoint(h,dates):
    return disjoint(dates,Y[h])


def pair_frame(a,scope,targets,choices,losses):
    tables=[]
    scoped=keep_scope(a,scope)
    for (h,target),g in scoped.groupby(['horizon','target'],observed=True,sort=False):
        if targets is not None and target not in targets:
            continue
        for metric in losses:
            if metric not in g:
                continue
            w=g.pivot(index='origin',columns='model',values=metric).sort_index()
            if w.empty:
                continue
            refs=choices(h,target,metric)
            for base in refs:
                if base not in w:
                    continue
                for n in w:
                    if n==base:
                        continue
                    ok=w[n].notna()&w[base].notna()
                    if ok.sum()<8:
                        continue
                    d=w.index[ok]
                    other=w.loc[ok,n].to_numpy()
                    comparator=w.loc[ok,base].to_numpy()
                    if np.isfinite(other).all() and np.isfinite(comparator).all():
                        tables.append((dict(horizon=h,scope=scope,target=target,metric=metric,model=n,baseline=base,
                            n=len(d),disjoint=cached_disjoint(h,tuple(d)),candidate=other.mean(),control=comparator.mean(),
                            gain=float(np.mean(comparator-other)),difference_ess=effective(comparator-other)),
                            pd.Series(comparator-other,index=d)))
    return tables


def adjusted_families(families,y):
    rng=np.random.default_rng(SEED+33)
    output=[]
    for topic,frame,targets,choice,metrics in families:
        if frame.empty:
            continue
        for scope in ('combined','early','later'):
            pairs=pair_frame(frame,scope,targets,choice,metrics)
            for h in HORIZONS:
                select=[(r,a) for r,a in pairs if r['horizon']==h]
                if not select:
                    continue
                index=y[h].index[y[h].cohort.notna() & (y[h].cohort.eq(scope) if scope!='combined' else True)]
                n=len(index)
                delta=np.column_stack([a.reindex(index).to_numpy() for _,a in select])
                keep=np.isfinite(delta)
                point=np.nanmean(delta,axis=0)
                rooted=np.nan_to_num(delta-point)
                supports=np.array([r['disjoint']>=4 for r,a in select])
                bands={}
                for k in BLOCKS:
                    start=rng.integers(0,n,(BOOT,int(np.ceil(n/k))))
                    indices=((start[:,:,None]+np.arange(k))%n).reshape(BOOT,-1)[:,:n]
                    counts=np.array([np.bincount(v,minlength=n) for v in indices],float)
                    denominator=counts@keep.astype(float)
                    errors=np.divide(counts@rooted,denominator,out=np.zeros_like(denominator),where=denominator>0)
                    sd=errors.std(axis=0)
                    z=np.divide(errors,sd,out=np.zeros_like(errors),where=sd>1.e-13)
                    quantile=float(np.quantile(abs(z[:,supports]).max(axis=1),.95)) if supports.any() else np.nan
                    bands[k]=(point-quantile*sd,point+quantile*sd)
                for i,(r,_) in enumerate(select):
                    for k in BLOCKS:
                        r.update({f'low{k}':bands[k][0][i] if supports[i] else np.nan,
                                  f'high{k}':bands[k][1][i] if supports[i] else np.nan})
                    key=10 if h==5 else 21
                    r['evidence']='sparse' if r['disjoint']<8 else 'positive adjusted historical' if r[f'low{key}']>1.e-12 else 'uncertain'
                    output.append(dict(family=topic,**r))
        print('Paired family',topic,'finished',flush=True)
    return pd.DataFrame(output)


def calibration_summary(p,intervals,y):
    rows=[]
    short=p[p.target.isin(['range','endpoint_return','high','low','volatility'])]
    for level in ('50','80','90','95'):
        v=short.reindex(columns=['horizon','origin','cohort','model','target','actual',
                        'coverage'+level,'width'+level,'interval_score'+level,'upper_miss'+level,'lower_miss'+level])
        v=v.rename(columns={k+level:k for k in ['coverage','width','interval_score','upper_miss','lower_miss']})
        v=v.dropna(subset=['coverage','interval_score'])
        v['method']='whole_law'
        v['central']=int(level)
        v['fitted']=True
        rows.append(v)
    book=pd.concat([*rows,intervals],ignore_index=True)
    agg=score_table(book,y,['horizon','target','model','method','central'],
                    ['coverage','width','interval_score','lower_miss','upper_miss','fitted'],actual='unused')
    by_state=[]
    for h in HORIZONS:
        risk=y[h].trailing_at_origin
        source=risk.shift().rolling(126,min_periods=40).quantile(.75)
        regime=pd.Series(np.where(risk>=source,'high trailing risk','ordinary trailing risk'),index=risk.index)
        regime=regime.where(source.notna())
        a=book[book.horizon.eq(h)&book.target.eq('range')&book.central.eq(80)].copy()
        a['origin_state']=a.origin.map(regime)
        a['realized_expansion']=a.origin.map(y[h].event_expand)
        for k,f in a.groupby(['model','method','origin_state','realized_expansion'],dropna=False):
            by_state.append(dict(horizon=h,model=k[0],method=k[1],origin_state=k[2],realized_expansion=k[3],
                         n=len(f),disjoint=cached_disjoint(h,tuple(sorted(f.origin))),coverage80=f.coverage.mean(),
                         width80=f.width.mean(),score80=f.interval_score.mean()))
    write('conditional-interval-calibration.csv',pd.DataFrame(by_state))
    return agg


def complexity(name):
    if name in {'constant_iv','raw_iv','V13_raw_ATM','V13_bracketed_IV','symmetric','historical','V13_empirical_range',
                'V13_empirical_exact','V13_analytic_iv_diffusion'}:
        return 1
    if any(k in name.lower() for k in ('surface','offshore','joint','mixture','intraday','regime','sign_magnitude','blocks')):
        return 3
    return 2


def pareto(views):
    output=[]
    for objective,a,metric,coverage_score in views:
        for h in HORIZONS:
            b=a[a.horizon.eq(h)].copy()
            full=set(b.loc[b.cohort.eq('combined')&b.n.eq(EXPECTED[h]),'model'])
            b=b[b.model.isin(full)]
            if b.empty:
                continue
            for model,g in b.groupby('model'):
                q=g[g.cohort.eq('combined')]
                both=g[g.cohort.isin(['early','later'])]
                if len(q)!=1 or len(both)!=2:
                    continue
                base=q.iloc[0]
                gap=abs(float(both[metric].iloc[0]-both[metric].iloc[1]))
                row=dict(horizon=h,objective=objective,model=model,loss=base[metric],absolute_cohort_gap=gap,
                          complexity_tier=complexity(model))
                if coverage_score and pd.notna(base.get('coverage80',np.nan)):
                    row['coverage80_error']=abs(base.coverage80-.8)
                output.append(row)
    a=pd.DataFrame(output)
    selections=[]
    for _,group in a.groupby(['horizon','objective']):
        axes=['loss','absolute_cohort_gap','complexity_tier']
        if group.coverage80_error.notna().all():
            axes.append('coverage80_error')
        v=group[axes].to_numpy()
        dominated=np.all(v[:,None,:]<=v[None,:,:],axis=2)&np.any(v[:,None,:]<v[None,:,:],axis=2)
        selections.extend(group.assign(pareto=np.logical_not(dominated.any(axis=0))).to_dict('records'))
    return pd.DataFrame(selections)


def run():
    global Y
    Y={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    y=Y
    risk=volatility_rows(y)
    write('risk-scores-per-origin.csv',risk)
    projections=marginal_rows(y)
    paths=projections['frame']
    endpoints=paths[paths.target.eq('endpoint_return')]
    risk_summary=score_table(risk,y,['horizon','model'],['mae','se','qlike','bias'],risk=True)
    write('volatility-leaderboard.csv',risk_summary)
    path_metrics=['mae','se','crps','pinball']+[k+c for c in ['50','80','90','95'] for k in ['coverage','width','interval_score']]
    end_result=score_table(endpoints,y,['horizon','model'],path_metrics+['brier','log_loss'],endpoint=True)
    write('endpoint-leaderboard.csv',end_result)
    path_summary=score_table(paths[~paths.target.eq('endpoint_return')],y,['horizon','target','model'],path_metrics)
    write('path-marginal-leaderboard.csv',path_summary)
    joint=add_cohort(pd.concat([pd.read_csv(OUT/'multivariate-path-scores.csv'),projections['joint']],ignore_index=True).assign(target='joint'),y)
    joint_summary=score_table(joint,y,['horizon','model'],['energy_score','variogram_score'])
    write('joint-leaderboard.csv',joint_summary)
    ev=binary_rows(y)
    events_summary=score_table(ev,y,['horizon','event','model'],['brier','log_loss','p','actual'])
    write('transition-and-tail-leaderboard.csv',events_summary)
    risk_target=pd.read_csv(OUT/'transition-continuous.csv')
    risk_target['mae']=abs(risk_target.actual-risk_target.prediction)
    risk_target['se']=(risk_target.actual-risk_target.prediction)**2
    write('continuous-transition-leaderboard.csv',score_table(add_cohort(risk_target,y),y,
                                                          ['horizon','target','model'],['mae','se']))
    path_p,direct,bar=passage_rows(y)
    passage_all=pd.concat([path_p,direct],ignore_index=True)
    write('barrier-leaderboard.csv',score_table(passage_all,y,['horizon','model','side','barrier'],
              ['p_touch','actual','p_endpoint','actual_endpoint','p_close','brier','log_loss',
               'integrated_brier','passage_log_loss','diagnostic_time_error','expected_time_given_touch']))
    bar_result=score_table(bar,y,['horizon','model'],['brier','log_loss','integrated_brier','passage_log_loss'])
    write('touch-and-passage-family.csv',bar_result)
    ordered=pd.read_csv(OUT/'path-ordering.csv.gz',low_memory=False,dtype={'barrier':str})
    ordered['target']='order_family'
    ord_summary=score_table(ordered,y,['horizon','model','barrier'],['p_both','actual_both','p_neither','actual_neither',
                                'p_upper_first','p_lower_first','p_same_candle','order_brier','order_log_loss'])
    write('ordering-leaderboard.csv',ord_summary)
    order_agg=ordered[ordered.barrier.isin(list('01234'))].groupby(['horizon','origin','cohort','model','target'])[['order_brier','order_log_loss']].mean().reset_index()
    intervals=pd.read_csv(OUT/'standalone-calibrated-intervals.csv.gz',low_memory=False)
    interval_summary=calibration_summary(paths,intervals,y)
    write('interval-calibration-leaderboard.csv',interval_summary)
    # Paired interval-score contrasts use the raw parent law on exactly the same origins.
    it=intervals[intervals.central.isin([80,90,95])&intervals.target.eq('range')].copy()
    it['base_model']=it.model
    it['target']=it.model+'_'+it.central.astype(str)
    it['model']=it.method
    controls=it.groupby(['horizon','origin','cohort','target']).baseline_interval_score.first().reset_index()
    iv=pd.concat([it[['horizon','origin','cohort','model','target','interval_score']],
        controls.rename(columns={'baseline_interval_score':'interval_score'}).assign(model='unadjusted_parent')],ignore_index=True)
    gaps=add_cohort(pd.read_csv(OUT/'opening-gap-forecasts.csv'),y)
    gaps['mae']=abs(gaps.forecast_abs-gaps.actual_abs)
    gaps['brier']=(gaps.p_gap_up-gaps.actual_sign)**2
    gaps['target']='next_gap'
    write('global-gap-leaderboard.csv',score_table(gaps,y,['horizon','model'],['mae','brier'],actual='actual_abs'))
    wide=path_summary[path_summary.target.eq('range')]
    front=pareto([('weekly_and_monthly_direction',end_result,'brier',False),
        ('endpoint_distribution',end_result,'crps',True),('volatility',risk_summary,'mae',False),
        ('range',wide,'crps',True),('touch',bar_result,'brier',False),('joint',joint_summary,'energy_score',False)])
    write('pareto-frontiers.csv',front)
    print('Finished separate point, interval, passage and joint leaderboards',flush=True)

    families=[
      ('volatility',risk,None,lambda h,t,m:['V13_raw_ATM' if h==5 else 'V13_bracketed_IV','V13_GJR','V13_trailing'],['mae','qlike']),
      ('direction',endpoints,None,lambda h,t,m:['V13_week_Brier','symmetric'] if h==5 else ['symmetric','V13_IV_scaled_symmetric'],['brier']),
      ('endpoint_return',endpoints,None,lambda h,t,m:['V13_week_CRPS','symmetric'] if h==5 else ['V13_IV_scaled_symmetric','symmetric'],['crps']),
      ('range_path',paths,PATH_RANGE,lambda h,t,m:['V13_diffusion_iv','V13_iv_scaled','constant_iv','path_mixture'],['mae','crps','interval_score80','interval_score95']),
      ('volatility_transition',ev,TRANSITIONS,lambda h,t,m:['historical','iv_raw','gjr_control','constant_iv'],['brier']),
      ('extremes',ev,set(ev.event)-TRANSITIONS,lambda h,t,m:['historical','iv_raw','iv_scaled_blocks','constant_iv'],['brier']),
      ('touch',bar,None,lambda h,t,m:['V13_diffusion_iv' if h==5 else 'V13_analytic_iv_diffusion','V13_iv_scaled','V13_empirical_exact','constant_iv'],['brier']),
      ('passage_time',bar,None,lambda h,t,m:['constant_iv','iv_scaled_blocks','path_mixture'],['integrated_brier','passage_log_loss']),
      ('order',order_agg,None,lambda h,t,m:['constant_iv','iv_scaled_blocks'],['order_brier','order_log_loss']),
      ('joint',joint,None,lambda h,t,m:['constant_iv','V13_diffusion_iv','V13_iv_scaled','path_mixture'],['energy_score','variogram_score']),
      ('interval',iv,None,lambda h,t,m:['unadjusted_parent'],['interval_score']),
      ('offshore_gap',gaps,None,lambda h,t,m:['opening_gap_domestic'],['mae','brier'])]
    contrast=adjusted_families(families,y)
    write('matched-search-adjusted.csv',contrast)
    save('evaluation-counts.json',dict(risk_rows=len(risk),distribution_rows=len(paths),joint_rows=len(joint),event_rows=len(ev),
         passage_rows=len(path_p),direct_touch_rows=len(direct),interval_rows=len(intervals),matched=len(contrast),
         used_families=[f[0] for f in families],bootstrap=BOOT,blocks=BLOCKS))
    print('Scored all objectives and saved',len(contrast),'matched comparisons',flush=True)


if __name__=='__main__':
    run()
