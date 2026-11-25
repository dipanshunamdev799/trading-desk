"""Matched scoring, calibration, disjoint coverage and simultaneous block comparisons."""
from scipy.stats import spearmanr

from .common import *
from .paths import TARGETS
from .volatility import LEVEL, CHANGE, MODELS, maturity, ridge_risk, rescale_features


def chronology():
    return {h:pd.read_csv(OUT/f'targets-{h}.csv',index_col=0) for h in HORIZONS}


def disjoint(index, y):
    count=0
    last=''
    for d in sorted(set(index)):
        if d >= last:
            count+=1
            last=y.at[d,'endpoint']
    return count


def effective(values):
    v=np.asarray(values,dtype=float)
    z=v-v.mean()
    denom=z@z
    if denom<1e-14:
        return np.nan
    lags=[z[i:]@z[:-i]/denom for i in range(1,min(25,len(v)//3))]
    decay=[]
    for x in lags:
        if x<=0:
            break
        decay.append(x)
    return len(v)/(1+2*sum(decay))


def by_cohort(frame):
    yield 'combined',frame
    for key in ['early','later']:
        yield key,frame[frame.cohort.eq(key)]


def enrich(frame,y):
    z=frame.copy()
    z['cohort']=z.origin.map(y.cohort)
    assert z.cohort.notna().all()
    return z


def event_losses(p,y):
    p=np.asarray(p)
    v=np.asarray(y)
    brier=(p-v)**2
    clipped=p.clip(.002,.998)
    return brier,-v*np.log(clipped)-(1-v)*np.log1p(-clipped)


def terminal(p):
    return p.assign(actual=p.realized_return,target='endpoint_return')


def calibration(frame, columns, key):
    p=frame[key].clip(0,1)
    ids=pd.cut(p,np.linspace(0,1,11),include_lowest=True)
    return (frame.assign(bin=ids).groupby(columns+['bin'],observed=True)
            .agg(n=('actual','size'),observed=('actual','mean'),predicted=(key,'mean')).reset_index())


def volatility_frames(y):
    new=pd.read_csv(OUT/'volatility-predictions.csv')
    prior=pd.read_csv(OUT/'prior-volatility.csv')
    sources=[new,prior]
    if (OUT/'supplemental-volatility.csv').exists():
        sources.append(pd.read_csv(OUT/'supplemental-volatility.csv'))
    risk=pd.concat(sources,ignore_index=True)
    clock=pd.read_csv(V12/'horizon-alignment.csv')
    exact=clock.loc[clock.version.eq('NATURAL')&clock.natural_realized.eq(True),['horizon','origin']]
    accepted=pd.MultiIndex.from_frame(exact)
    risk=risk.loc[~risk.model.eq('iv_exact')|pd.MultiIndex.from_frame(risk[['horizon','origin']]).isin(accepted)]
    risk= pd.concat([enrich(risk[risk.horizon.eq(h)],y[h]) for h in HORIZONS])
    risk['actual']=[y[h].at[d,'volatility'] for h,d in zip(risk.horizon,risk.origin)]
    risk['mae']=(risk.prediction-risk.actual).abs()
    risk['square']=(risk.prediction-risk.actual)**2
    ratio=(risk.actual/risk.prediction)**2
    risk['qlike']=ratio-np.log(ratio)-1
    write('scored-volatility.csv',risk,index=False)
    return risk


def score_risk(risk,y):
    result=[]; risk_buckets=[]
    for (h,n),g in risk.groupby(['horizon','model']):
        for cohort,s in by_cohort(g):
            if s.empty:
                continue
            a,b=s.actual,s.prediction
            result.append(dict(horizon=h,cohort=cohort,model=n,n=len(s),disjoint=disjoint(s.origin,y[h]),
                       ess=effective(a),mae=s.mae.mean(),rmse=np.sqrt(s.square.mean()),qlike=s.qlike.mean(),
                       bias=(b-a).mean(),spearman=spearmanr(a,b).statistic))
        # Quantile bins summarize retrospective calibration and are excluded from model selection.
        bucket=pd.cut(g.prediction,[0,.09,.12,.15,.19,1],include_lowest=True)
        for label,s in g.groupby(bucket,observed=True):
            risk_buckets.append(dict(horizon=h,model=n,annualized_prediction_bin=str(label),n=len(s),
                    disjoint=disjoint(s.origin,y[h]),predicted=s.prediction.mean(),realized=s.actual.mean(),mae=s.mae.mean()))
    write('volatility-calibration.csv',pd.DataFrame(risk_buckets),index=False)
    return pd.DataFrame(result)


def score_distributions(pred,y):
    result=[]
    for (h,m,target),data in pred.groupby(['horizon','model','target']):
        for c,g in by_cohort(data):
            if g.empty:
                continue
            p=g.p.ge(.5); up=g.actual.gt(0)
            tpr=p[up].mean()
            tnr=(~p[~up]).mean()
            z=dict(horizon=h,model=m,target=target,cohort=c,n=len(g),disjoint=disjoint(g.origin,y[h]),ess=effective(g.actual),
                   accuracy=(p==up).mean(),balanced_accuracy=.5*(tpr+tnr),rmse=np.sqrt(g.squared_error.mean()),
                   down_tail_pred=g.q05.gt(g.actual).mean(),up_tail_pred=g.q95.lt(g.actual).mean())
            z.update({k:g[k].mean() for k in ['mae','median_mae','brier','crps','log_loss','pinball','coverage50','coverage80','width50','width80']})
            result.append(z)
    return pd.DataFrame(result)


def score_barriers(data,y):
    result=[]
    for (h,m,b,event),g in data.groupby(['horizon','model','barrier','event']):
        for c,s in by_cohort(g):
            if s.empty:
                continue
            result.append(dict(horizon=h,model=m,barrier=b,event=event,cohort=c,n=len(s),disjoint=disjoint(s.origin,y[h]),
                ess=effective(s.actual),brier=s.brier.mean(),log_loss=s.log_loss.mean(),observed=s.actual.mean(),predicted=s.p.mean(),mc_se=s.mc_se.mean()))
    return pd.DataFrame(result)


def pair_series(data, losses, model_baselines):
    results=[]
    groups={key:frame.set_index('origin') for key,frame in data.groupby(['target','model'])}
    for (target, name),q in groups.items():
        for baseline in model_baselines(target,name):
            b=groups.get((target,baseline))
            if b is None or baseline==name:
                continue
            common=q.index.intersection(b.index).sort_values()
            if len(common)<8:
                continue
            for m in losses(target):
                a=q.loc[common,m]
                control=b.loc[common,m]
                keep=a.notna()&control.notna()
                if keep.sum()<8:
                    continue
                results.append(((target,name,baseline,m),a[keep],control[keep]))
    return results


def paired(data, y, metrics, baselines, family):
    estimates=[]
    for h in HORIZONS:
        for c,g in by_cohort(data[data.horizon.eq(h)]):
            pairs=pair_series(g,metrics,lambda t,n:baselines(h,t,n))
            if not pairs:
                continue
            idx=y[h].index[y[h].cohort.notna() & (y[h].cohort.eq(c) if c!='combined' else True)]
            delta=pd.concat([(b-a).reindex(idx) for _,a,b in pairs],axis=1).to_numpy()
            keep=np.isfinite(delta)
            center=np.nanmean(delta,axis=0)
            rooted=np.nan_to_num(delta-center)
            n=len(idx)
            rng=np.random.default_rng(SEED+h)
            bands={}
            for k in [5,10,21,42]:
                starts=rng.integers(0,n,size=(N_BOOT,int(np.ceil(n/k))))
                draws=((starts[:,:,None]+np.arange(k))%n).reshape(N_BOOT,-1)[:,:n]
                counts=np.array([np.bincount(row,minlength=n) for row in draws],float)
                denominator=counts@keep.astype(float)
                # Ratios respect each candidate's available dates on every block draw.
                errors=np.divide(counts@rooted,denominator,out=np.zeros_like(denominator),where=denominator>0)
                sigma=errors.std(axis=0)
                standard=np.divide(errors,sigma,out=np.zeros_like(errors),where=sigma>1e-14)
                critical=float(np.quantile(abs(standard).max(axis=1),.95))
                bands[k]=(center-critical*sigma,center+critical*sigma)
            for i,((t,m,b,metric),a,z) in enumerate(pairs):
                independent=disjoint(a.index,y[h])
                link=dict(family=family,horizon=h,cohort=c,target=t,model=m,baseline=b,metric=metric,n=len(a),
                          disjoint=independent,ess=effective(z-a),candidate=a.mean(),control=z.mean(),gain=center[i])
                for k,(lo,hi) in bands.items():
                    link[f'low{k}']=lo[i] if independent>=5 else np.nan
                    link[f'high{k}']=hi[i] if independent>=5 else np.nan
                link['classification']='sparse' if independent<8 else 'positive adjusted historical' if link[f'low{10 if h==5 else 21}']>0 else 'historically inconclusive'
                estimates.append(link)
    return estimates


def event_profiles(risk,paths,barriers,y):
    flags=pd.read_csv(OUT/'events.csv')
    outputs=[]; conditioning=[]; premiums=[]
    for h in HORIZONS:
        data=y[h]
        x=pd.read_csv(OUT/f'features-{h}.csv',index_col=0)
        base='iv_nearest' if h==5 else 'iv_bracket'
        r=risk[(risk.horizon.eq(h))&risk.model.isin([base,'har_iv','premium_ridge','prior_fitted_rv','global_plus_iv','position_ridge'])]
        path=paths[paths.horizon.eq(h)&paths.model.isin(['iv_scaled','event_iv','empirical','position_iv','global_iv'])&paths.target.isin(['range','high','low','abs_return'])]
        hit=barriers[barriers.horizon.eq(h)&barriers.model.isin(['iv_scaled','event_iv','position_iv'])&barriers.barrier.eq('2')&barriers.event.isin(['upper_touch','lower_touch'])]
        for event,g in flags[flags.horizon.eq(h)].groupby('event'):
            for active,kk in g.groupby('active'):
                ids=kk.origin
                for (model,target),v in path[path.origin.isin(ids)].groupby(['model','target']):
                    outputs.append(dict(horizon=h,event=event,active=active,model=model,target=target,n=len(v),
                        disjoint=disjoint(v.origin,data),predicted=v.predicted_mean.mean(),observed=v.actual.mean(),loss=v.crps.mean(),loss_type='CRPS'))
                for model,v in r[r.origin.isin(ids)].groupby('model'):
                    outputs.append(dict(horizon=h,event=event,active=active,model=model,target='volatility',n=len(v),
                        disjoint=disjoint(v.origin,data),predicted=v.prediction.mean(),observed=v.actual.mean(),loss=v.mae.mean(),loss_type='MAE'))
                for (model,target),v in hit[hit.origin.isin(ids)].groupby(['model','event']):
                    outputs.append(dict(horizon=h,event=event,active=active,model=model,target=target,n=len(v),
                        disjoint=disjoint(v.origin,data),predicted=v.p.mean(),observed=v.actual.mean(),loss=v.brier.mean(),loss_type='Brier'))
        for d,row in data[data.cohort.notna()].iterrows():
            t=maturity(data,d)
            cuts=x.loc[t,'variance_gap'].quantile([.25,.75]).to_numpy()
            gap=x.at[d,'variance_gap']
            tier='missing' if not np.isfinite(gap) else 'cheap' if gap<cuts[0] else 'expensive' if gap>cuts[1] else 'middle'
            premiums.append(dict(horizon=h,origin=d,cohort=row.cohort,regime=tier,
                implied_vol=x.at[d,base],trailing_vol=x.at[d,'har21'],realized_vol=row.volatility,
                var_premium_proxy=gap,var_error=x.at[d,base]**2-row.volatility**2,
                expanded=int(row.volatility>x.at[d,'har21']),absolute_move=row.abs_return,endpoint_return=row.endpoint_return))
        for (m,c),g in risk[risk.horizon.eq(h)].groupby(['model','cohort']):
            expansion=g.actual.gt(g.origin.map(x.har21))
            for expanded,a in g.groupby(expansion):
                conditioning.append(dict(horizon=h,model=m,cohort=c,expansion=expanded,n=len(a),disjoint=disjoint(a.origin,data),
                    mae=a.mae.mean(),qlike=a.qlike.mean(),bias=(a.prediction-a.actual).mean()))
    write('events-risk-and-path.csv',pd.DataFrame(outputs),index=False)
    write('volatility-expansion-contraction.csv',pd.DataFrame(conditioning),index=False)
    p=pd.DataFrame(premiums)
    write('variance-premium-origins.csv',p,index=False)
    sums=p.groupby(['horizon','regime']).agg(n=('origin','size'),mean_implied=('implied_vol','mean'),
        mean_realized=('realized_vol','mean'),var_gap=('var_premium_proxy','mean'),expanded=('expanded','mean'),
        magnitude=('absolute_move','mean'),mean_return=('endpoint_return','mean')).reset_index()
    write('variance-premium-regimes.csv',sums,index=False)


def refit_null(y, risk):
    out=[]
    models=['shape_level','shape_change','shape_combined','position_ridge','global_plus_iv']
    for h in HORIZONS:
        data=y[h]
        x=pd.read_csv(OUT/f'features-{h}.csv',index_col=0).copy()
        x['iv_primary']=x.iv_nearest if h==5 else x.iv_bracket
        dates=data.index[data.cohort.notna()][::10]
        rng=np.random.default_rng(SEED+h+110)
        for draw in range(12):
            for name in models:
                for day in dates:
                    t=maturity(data,day)[-180:]
                    train=x.loc[t].copy()
                    fields=MODELS[name]
                    block=np.array_split(np.arange(len(train)),max(2,len(train)//12))
                    arr=np.concatenate([block[j] for j in rng.permutation(len(block))])
                    payload=[k for k in fields if k!='iv_primary']
                    train[payload]=train[payload].iloc[arr].to_numpy()
                    pred,_=ridge_risk(train,x.loc[[day]],data.loc[t,'volatility'],fields,name,rng)
                    observed=data.at[day,'volatility']
                    raw=abs(x.at[day,'iv_primary']-observed)
                    out.append(dict(horizon=h,model=name,origin=day,draw=draw,abs_error=abs(pred[0]-observed),raw_iv_error=raw,gain=raw-abs(pred[0]-observed)))
    a=pd.DataFrame(out)
    write('refit-null-origins.csv',a,index=False)
    selected=a.groupby(['horizon','draw','model']).gain.mean().reset_index().sort_values('gain').groupby(['horizon','draw']).tail(1)
    observed=risk[risk.model.isin(models)].merge(a[['horizon','origin','raw_iv_error']].drop_duplicates(),on=['horizon','origin'])
    observed=observed.assign(gain=observed.raw_iv_error-observed.mae).groupby(['horizon','model']).gain.mean().reset_index().sort_values('gain').groupby('horizon').tail(1)
    observed['draw']='unpermuted'
    write('refit-null-winners.csv',pd.concat([selected,observed]),index=False)


def run():
    y=chronology()
    risk=volatility_frames(y)
    pp=pd.read_csv(OUT/'distribution-predictions.csv',low_memory=False)
    extra=pd.read_csv(OUT/'protected-rescaled-endpoint.csv',low_memory=False)
    frozen=terminal(pd.read_csv(OUT/'reproduced-endpoint.csv',low_memory=False))
    protected=terminal(pd.read_csv(OUT/'protected-endpoint.csv',low_memory=False))
    controls=pd.read_csv(OUT/'exact-and-analytic-path-controls.csv')
    paths=pd.concat([pp,frozen,protected,extra,controls],ignore_index=True)
    paths=pd.concat([enrich(paths[paths.horizon.eq(h)],y[h]) for h in HORIZONS],ignore_index=True)
    assert not paths.duplicated(['horizon','origin','model','target']).any()
    events=pd.read_csv(OUT/'barrier-predictions.csv.gz',low_memory=False)
    events=pd.concat([events,pd.read_csv(OUT/'exact-and-analytic-barrier-controls.csv')],ignore_index=True)
    events=pd.concat([enrich(events[events.horizon.eq(h)],y[h]) for h in HORIZONS],ignore_index=True)
    events['brier'],events['log_loss']=event_losses(events.p,events.actual)
    a=score_risk(risk,y)
    b=score_distributions(paths,y)
    c=score_barriers(events,y)
    write('volatility-leaderboard.csv',a,index=False)
    write('distribution-and-path-leaderboard.csv',b,index=False)
    write('barrier-leaderboard.csv',c,index=False)
    write('endpoint-calibration.csv',calibration(paths[paths.target.eq('endpoint_return')].assign(actual=lambda f:f.actual.gt(0)),
                                               ['horizon','cohort','model'],'p'),index=False)
    write('barrier-calibration.csv',calibration(events,['horizon','model','barrier','event'],'p'),index=False)
    touch=events[events.event.isin(['upper_touch','lower_touch'])&events.barrier.isin(list('01234'))]
    joint=touch.groupby(['horizon','origin','cohort','model'])[['brier','log_loss']].mean().reset_index()
    joint['target']='touch_family'
    write('touch-family-loss.csv',joint,index=False)
    write('observed-order-resolution.csv',pd.concat([
        f[f.cohort.notna()].melt(id_vars=['cohort'],value_vars=[f'ordering_source_{i}' for i in range(len(THRESHOLDS))],
                                var_name='barrier',value_name='resolution').assign(horizon=h).groupby(['horizon','cohort','barrier','resolution']).size().rename('n').reset_index()
        for h,f in y.items()]),index=False)
    print('Built point, distribution and barrier leaderboards',flush=True)
    refs={'position_ridge':'shape_level','shape_change':'shape_level','shape_combined':'shape_level','shape_pca':'shape_level',
          'global_divergence':'global_plus_iv','global_plus_iv':'har_iv','regime_iv':'har_iv'}
    evalrisk=risk.assign(target='volatility')
    paired_rows=paired(evalrisk,y,lambda t:['mae','qlike'],
        lambda h,t,n:list(dict.fromkeys(['iv_nearest' if h==5 else 'iv_bracket','prior_fitted_rv',refs.get(n,'har_iv')])), 'volatility')
    def endrefs(h,t,n):
        if t!='endpoint_return':
            return ['empirical_exact','rv_scaled','iv_scaled']
        parent=n.split('__')[0] if '__' in n else 'V12_STAT'
        return list(dict.fromkeys(['NEUTRAL','V12_NATIVE_RV' if h==5 else 'PH_NATIVE_PHASE_MIXTURE',
                    'J12_Q_GROUP' if h==5 else 'V12_STAT',parent]))
    paired_rows+=paired(paths,y,lambda t:['brier','crps'] if t=='endpoint_return' else ['mae','crps','pinball'],endrefs,'return-and-path')
    paired_rows+=paired(joint,y,lambda t:['brier','log_loss'],
                        lambda h,t,n:['empirical_exact','rv_scaled','iv_scaled','analytic_iv_diffusion'],'touch')
    write('paired-search-adjusted.csv',pd.DataFrame(paired_rows),index=False)
    print('Paired block intervals',len(paired_rows),flush=True)
    event_profiles(risk,paths,events,y)
    if not (OUT/'refit-null-winners.csv').exists():
        refit_null(y,risk)
    print('Scored',len(risk),'risk',len(paths),'distribution and',len(events),'barrier rows with',len(paired_rows),'adjusted comparisons',flush=True)


if __name__=='__main__':
    run()
