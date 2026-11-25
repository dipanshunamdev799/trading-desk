"""OHLC path candidates, barrier families, and directional attribution."""
import hashlib

from scipy.special import logit
from sklearn.linear_model import LogisticRegression, Ridge

from .common import *
from .data import path_metrics, DOMESTIC, POSITION, GLOBAL
from .volatility import rescale_features, maturity, LEVEL
from research.nifty_forecast_v10.estimators import Distribution

PATH_MODELS = ['empirical','rv_scaled','iv_scaled','hybrid_scaled','domestic_drift','state_iv','global_iv',
               'position_iv','surface_iv','random_state_iv','shift_state_iv','diffusion_iv','asymmetry_iv','event_iv']
TARGETS = ('endpoint_return','abs_return','volatility','high','low','range','close_high','close_low','drawdown',
           'rebound','positive_days','max_daily','overnight_sd','regular_sd')
JOINT_EXAMPLES = ('empirical','rv_scaled','iv_scaled','state_iv','diffusion_iv')
STATE = ['iv_nearest','iv_relative','cash5','finance','breadth5','sector_dispersion','intraday_rv']
EVENT = ['near_weekly_expiry','near_monthly_expiry','roll_observed','fomc_during_window','rbi_during_window','index_review_during_window']
SHOCKS = ['prior_move','sector_shock','breadth_decay','iv_jump','global_jump']


def div_close(p):
    """Per-session log OHLC relative to the preceding close."""
    ref = np.column_stack([np.ones(len(p)),p[:,:-1,3]])
    return np.log(p/ref[:,:,None])


def from_steps(steps):
    close = np.cumsum(steps[:,:,3],axis=1)
    prior = np.column_stack([np.zeros(len(steps)),close[:,:-1]])
    return np.exp(steps+prior[:,:,None])


def robust_probs(r,x,variants):
    """Filter known-on-origin source availability per feature set, preserve chronology."""
    a,b,_,_=rescale_features(r,x,variants)
    d=np.mean(np.minimum((a-b)**2,16),axis=1)
    w=np.exp(-.5*d)
    return .35/len(d)+.65*w/w.sum()


def scale_steps(steps, scale, drift=0., skew=0.):
    z=steps*scale[:,None,None]
    if skew:
        multiplier=1+skew*np.sign(z[:,:,3])
        z*=multiplier[:,:,None]
    if drift:
        # Open retains the scaled gap; close and both extrema remain consistent with the altered drift.
        z[:,:,3]+=drift
        z[:,:,1]=np.maximum(z[:,:,1],z[:,:,3])
        z[:,:,2]=np.minimum(z[:,:,2],z[:,:,3])
    return z


def diffusion(h, annual, rng):
    gaps=rng.normal(0,annual/np.sqrt(252)*.28,(N_PATHS,h))
    draws=rng.normal(0,annual/np.sqrt(252)*np.sqrt((1-.28**2)/24),(N_PATHS,h,24))
    r=np.concatenate([np.zeros((N_PATHS,h,1)),draws.cumsum(axis=2)],axis=2)+gaps[:,:,None]
    return from_steps(np.stack([gaps,r.max(axis=2),r.min(axis=2),r[:,:,-1]],axis=2))


def order_masks(paths,k):
    u=paths[:,:,1] >= 1+k
    d=paths[:,:,2] <= 1-k
    up,dn=u.any(axis=1),d.any(axis=1)
    i=np.where(up,u.argmax(axis=1),paths.shape[1])
    j=np.where(dn,d.argmax(axis=1),paths.shape[1])
    op=paths[np.arange(len(paths)),np.minimum(i,paths.shape[1]-1),0]
    first_up=(i<j)|(up&dn&(i==j)&(op>=1+k))
    first_down=(j<i)|(up&dn&(i==j)&(op<=1-k))
    return {'upper_touch':up,'lower_touch':dn,'both':up&dn,'neither':~(up|dn),
            'first_upper_definite':first_up,'first_lower_definite':first_down,
            'first_ambiguous':up&dn&~first_up&~first_down}


def barrier_actual(y, paths, idx, k, label_id):
    flags={name:bool(mask[0]) for name,mask in order_masks(paths[idx:idx+1],k).items()}
    if label_id is not None:
        flags['ordered_upper_resolved']=y[f'ordering_{label_id}']=='upper'
        flags['ordered_lower_resolved']=y[f'ordering_{label_id}']=='lower'
        flags['order_is_observed']=y[f'ordering_{label_id}']!='ambiguous'
    else:
        flags['ordered_upper_resolved']=flags['first_upper_definite']
        flags['ordered_lower_resolved']=flags['first_lower_definite']
        flags['order_is_observed']=not flags['first_ambiguous']
    flags.update(upper_close=y.close_high>=k,lower_close=y.close_low<=-k,
                 upper_endpoint=y.endpoint_return>=k,lower_endpoint=y.endpoint_return<=-k)
    return flags


def path_barriers(paths,metrics,k):
    flags=order_masks(paths,k)
    flags.update(upper_close=metrics['close_high']>=k,lower_close=metrics['close_low']<=-k,
                 upper_endpoint=metrics['endpoint_return']>=k,lower_endpoint=metrics['endpoint_return']<=-k)
    return {key:float(value.mean()) for key,value in flags.items()}


def fitted_range(train,test,y,fields):
    z,k,_,_=rescale_features(train,test,fields)
    response=y[['range','high','low']].to_numpy()
    model=Ridge(alpha=140).fit(z,response)
    center=model.predict(k)[0]
    errors=response-model.predict(z)
    return center+errors


def score_distribution(values,y):
    law=Distribution(values)
    sc=law.score(y)
    metrics = {k:sc[k] for k in ('p','predicted_mean','predicted_median','brier','log_loss','mae','squared_error',
               'median_mae','crps','pinball','coverage50','coverage80','width50','width80')}
    metrics.update({f'q{int(100*p):02}':float(law.quantile(p)) for p in [.05,.10,.25,.5,.75,.9,.95]})
    return metrics


def direction_forecasts(x,y,q,h):
    file=OUT/'prior-endpoint-quantiles.npz'
    with np.load(file,allow_pickle=False) as z:
        keys=z['keys'];vals=z['values'];means=z['means'];sd=z['sd']
    lookup={(n,d):(a,m,s) for (k,n,d),a,m,s in zip(keys,vals,means,sd) if int(k)==h}
    returns=[]; ledger=[]
    for d,row in q.iterrows():
        t=maturity(y,d)[-180:]
        if len(t)<40:
            continue
        a=x.loc[d]
        vol=a.iv_nearest if h==5 else a.iv_bracket
        iv=x.iv_nearest if h==5 else x.iv_bracket
        volscale=float(vol*np.sqrt(h/252))
        for n in REFERENCE:
            if n in ['Q12_RAW','P12_Q_PHYSICAL_MIX'] or (n,d) not in lookup:
                continue
            atoms,m,s=lookup[n,d]
            if s<=0 or not np.isfinite(volscale):
                continue
            k=np.clip(volscale/s,.60,1.55)
            for name,v in [(n+'__scale_only',m+(atoms-m)*k),
                           (n+'__half_scale',m+(atoms-m)*np.sqrt(k))]:
                returns.append(dict(horizon=h,origin=d,model=name,target='endpoint_return',actual=row.endpoint_return,
                                    **score_distribution(v,row.endpoint_return)))
        fields=DOMESTIC+['finance_iv','breadth_iv','iv_skew','iv_relative']
        z,k,names,median=rescale_features(x.loc[t],x.loc[[d]],fields)
        endpoint=y.loc[t,'endpoint_return'].to_numpy()
        norm_scale=iv.fillna(x.har21).loc[t].clip(.03).to_numpy()*np.sqrt(h/252)
        for normalized in [False,True]:
            fit=Ridge(alpha=200).fit(z,endpoint/norm_scale if normalized else endpoint)
            center=float(fit.predict(k)[0]*(volscale if normalized else 1.))
            training=fit.predict(z)*(norm_scale if normalized else 1.)
            error=(endpoint-training)/norm_scale if normalized else endpoint-training
            values=center+(error*volscale if normalized else error)
            name='rotation_iv_normalized' if normalized else 'rotation_iv_level'
            returns.append(dict(horizon=h,origin=d,model=name,target='endpoint_return',actual=row.endpoint_return,
                                **score_distribution(values,row.endpoint_return)))
            ledger.append(dict(horizon=h,origin=d,model=name,max_endpoint=y.loc[t,'endpoint'].max(),
                               columns=names,medians=median,coef=fit.coef_.tolist(),intercept=float(fit.intercept_)))
        mature=[k for k in t if ('Q12_RAW',k) in lookup and ('V12_STAT',k) in lookup]
        if len(mature)<24 or ('Q12_RAW',d) not in lookup or ('V12_STAT',d) not in lookup:
            continue
        priced,_,priced_sd=lookup['Q12_RAW',d]
        baseline,mu,_=lookup['V12_STAT',d]
        past=np.array([lookup['Q12_RAW',k][2] for k in mature])
        ratio=np.clip(np.median(np.abs(y.loc[mature,'endpoint_return'])/past)/.6745,.65,1.45)
        shape=mu+(priced-priced.mean())*ratio
        raw_prob=np.array([(lookup['Q12_RAW',k][0]>0).mean() for k in mature])
        target=y.loc[mature,'endpoint_return'].gt(0)
        if target.nunique()<2:
            continue
        reg=LogisticRegression(C=.15).fit(logit(np.clip(raw_prob,.02,.98))[:,None],target)
        p=reg.predict_proba([[logit(np.clip((priced>0).mean(),.02,.98))]])[0,1]
        if (shape>0).any() and (shape<=0).any():
            w=np.where(shape>0,p/max(1,(shape>0).sum()),(1-p)/max(1,(shape<=0).sum()))
            shape=shape[np.searchsorted(np.cumsum(w),(np.arange(512)+.5)/512)]
        for name,v in [('q_physical_adjusted',shape),('q_physical_mix25',np.r_[np.tile(baseline,3),shape])]:
            returns.append(dict(horizon=h,origin=d,model=name,target='endpoint_return',actual=row.endpoint_return,
                                **score_distribution(v,row.endpoint_return)))
        ledger.append(dict(horizon=h,origin=d,model='q_physical_adjusted',max_endpoint=y.loc[mature,'endpoint'].max(),
                           training=len(mature),dispersion_ratio=float(ratio),tilt=float(reg.coef_[0,0]),
                           intercept=float(reg.intercept_[0])))
    return returns,ledger


def run():
    all_scores=[]; all_barriers=[]; all_events=[]; receipts=[]; direction_ledger=[]; sim_checks=[]
    for h in HORIZONS:
        x=pd.read_csv(OUT/f'features-{h}.csv',index_col=0).copy()
        y=pd.read_csv(OUT/f'targets-{h}.csv',index_col=0)
        q=y[y.cohort.notna()]
        data=np.load(OUT/f'observed-paths-{h}.npz',allow_pickle=False)
        paths=data['paths']
        assert np.array_equal(data['origins'],y.index)
        step=div_close(paths)
        ix={d:i for i,d in enumerate(y.index)}
        x['finance_iv']=x.finance*x.iv_relative
        x['breadth_iv']=x.breadth5*x.iv_relative
        iv=x.iv_nearest if h==5 else x.iv_bracket
        x['selected_iv']=iv
        x['shifted_state']=x.iv_relative.shift(21)
        arrays=[]; array_keys=[]
        for d,row in q.iterrows():
            t=maturity(y,d)[-210:]
            if len(t)<40:
                continue
            i=ix[d]
            indexes=np.array([ix[k] for k in t])
            a=x.loc[d]
            today_rv=float(a.har21)
            today_iv=float(a.selected_iv)
            if not np.isfinite(today_iv):
                continue
            past=x.loc[t]
            target_days=np.sqrt(h/252)
            iv_ref=past.selected_iv.fillna(past.har21).to_numpy().clip(.035)
            rv_ref=past.har21.to_numpy().clip(.035)
            # Same sampled paths across primary candidates lowers Monte Carlo comparison variance.
            rng=np.random.default_rng(SEED+h*10000+i)
            common=rng.choice(len(t),N_PATHS)
            base_scale=np.clip(today_iv/iv_ref,.44,2.3)
            state=robust_probs(past,x.loc[[d]],STATE)
            global_w=robust_probs(past,x.loc[[d]],GLOBAL+['global_iv_gap','global_breadth'])
            position=robust_probs(past,x.loc[[d]],POSITION)
            surf=robust_probs(past,x.loc[[d]],LEVEL)
            shifted=past[['shifted_state']].copy()
            shuffled=np.array(state)[rng.permutation(len(state))]
            selected=robust_probs(shifted,x.loc[[d]],['shifted_state'])
            event_flags=x[EVENT].fillna(0).astype(bool)
            for key in SHOCKS:
                event_flags[key]=x[key].gt(past[key].quantile(.80))
            active=event_flags.loc[d]
            match=event_flags.loc[t,active].any(axis=1).to_numpy()
            historical_event=np.flatnonzero(match)
            weights=np.full(len(t),1/len(t))
            if len(historical_event)>=12:
                weights*=.65
                weights[historical_event]+=.35/len(historical_event)
            for key, flag in active.items():
                all_events.append(dict(horizon=h,origin=d,event=key,active=bool(flag),
                                       training_events=int(event_flags.loc[t,key].sum())))
            drift=0.
            z,k,_,_=rescale_features(past,x.loc[[d]],DOMESTIC)
            ny=y.loc[t,'endpoint_return'].to_numpy()/(iv_ref*target_days)
            drift=float(np.clip(Ridge(alpha=250).fit(z,ny).predict(k)[0],-.5,.5)*today_iv*target_days/h)
            kappa=float(np.clip(-a.iv_skew,-.10,.10)) if np.isfinite(a.iv_skew) else 0.
            variables=dict(empirical=(common,np.ones(len(t)),0.,0.),rv_scaled=(common,np.clip(today_rv/rv_ref,.44,2.3),0.,0.),
              iv_scaled=(common,base_scale,0.,0.),hybrid_scaled=(common,np.clip(np.sqrt((today_rv**2+today_iv**2)/(rv_ref**2+iv_ref**2)),.44,2.3),0.,0.),
              domestic_drift=(common,base_scale,drift,0.),state_iv=(rng.choice(len(t),N_PATHS,p=state),base_scale,0.,0.),
              global_iv=(rng.choice(len(t),N_PATHS,p=global_w),base_scale,0.,0.),
              position_iv=(rng.choice(len(t),N_PATHS,p=position),base_scale,0.,0.),
              surface_iv=(rng.choice(len(t),N_PATHS,p=surf),base_scale,0.,0.),
              random_state_iv=(rng.choice(len(t),N_PATHS,p=shuffled),base_scale,0.,0.),
              shift_state_iv=(rng.choice(len(t),N_PATHS,p=selected),base_scale,0.,0.),
              event_iv=(rng.choice(len(t),N_PATHS,p=weights),base_scale,0.,0.),
              asymmetry_iv=(common,base_scale,0.,kappa))
            fixed=[(str(j),k,barrier_actual(row,paths,i,k,j)) for j,k in enumerate(THRESHOLDS)]
            scaled=[(f'iv{mult}',mult*today_iv*target_days,barrier_actual(row,paths,i,mult*today_iv*target_days,None)) for mult in [.5,1.,1.5,2.]]
            for name in PATH_MODELS:
                if name=='diffusion_iv':
                    simulated=diffusion(h,today_iv,rng)
                else:
                    draws,scale,location,skew=variables[name]
                    simulated=from_steps(scale_steps(step[indexes[draws]],scale[draws],location,skew))
                assert np.isfinite(simulated).all() and (simulated>0).all()
                assert (simulated[:,:,1]+1e-12>=simulated.max(axis=2)).all()
                assert (simulated[:,:,2]-1e-12<=simulated.min(axis=2)).all()
                m=path_metrics(simulated)
                np.testing.assert_allclose(m['range'],m['high']-m['low'],atol=2e-12)
                assert (m['high']>=m['endpoint_return']-1e-12).all() and (m['low']<=m['endpoint_return']+1e-12).all()
                if name in JOINT_EXAMPLES:
                    arrays.append(np.column_stack([m[k] for k in TARGETS]).astype('float32'))
                    array_keys.append((d,name))
                for target in TARGETS:
                    all_scores.append(dict(horizon=h,origin=d,model=name,target=target,actual=row[target],
                                           **score_distribution(m[target],row[target])))
                for label,threshold,actuals in fixed+scaled:
                    probs=path_barriers(simulated,m,threshold)
                    assert abs(sum(probs[k] for k in ['first_upper_definite','first_lower_definite','first_ambiguous','neither'])-1)<1.e-9
                    for kind,prob in probs.items():
                        all_barriers.append(dict(horizon=h,origin=d,model=name,barrier=label,threshold=threshold,event=kind,
                                                 p=prob,actual=int(actuals[kind]),mc_se=float(np.sqrt(prob*(1-prob)/N_PATHS))))
                    if label in ['2','iv1.0'] and name in ['iv_scaled','diffusion_iv']:
                        n=N_PATHS//2
                        a1=simulated[:n,:,1].max(axis=1)>=1+threshold
                        a2=simulated[n:,:,1].max(axis=1)>=1+threshold
                        sim_checks.append(dict(horizon=h,origin=d,model=name,barrier=label,split_delta=float(a1.mean()-a2.mean())))
                receipts.append(dict(horizon=h,origin=d,model=name,train_start=t.min(),train_end=t.max(),
                                     max_endpoint=y.loc[t,'endpoint'].max(),train_count=len(t),
                                     sample_size=N_PATHS,seed=SEED+h*10000+i,hash=hashlib.sha256(simulated.tobytes()).hexdigest()))
            sampled=fitted_range(past,x.loc[[d]],y.loc[t],['selected_iv','har21','parkinson_gap','sector_dispersion','finance','breadth5','iv_skew'])
            for j,target in enumerate(['range','high','low']):
                a=sampled[:,j].clip(0) if target=='range' else sampled[:,j]
                all_scores.append(dict(horizon=h,origin=d,model='separate_range_ridge',target=target,actual=row[target],
                                       **score_distribution(a,row[target])))
            # Standalone barrier fits do not describe joint passage order.
            z,k,_,_=rescale_features(past,x.loc[[d]],['selected_iv','har21','iv_skew','sector_dispersion','cash5','finance'])
            for side in ['upper_touch','lower_touch']:
                last=1.
                for j,threshold in enumerate(THRESHOLDS):
                    truth=y.loc[t,f'{side}_{j}']
                    if truth.nunique()>1:
                        reg=LogisticRegression(C=.15).fit(z,truth)
                        value=float(reg.predict_proba(k)[0,1])
                    else:
                        value=float((truth.sum()+.5)/(len(truth)+1))
                    last=min(last,value)
                    all_barriers.append(dict(horizon=h,origin=d,model='separate_barrier_logit',barrier=str(j),threshold=threshold,
                                             event=side,p=last,actual=int(row[f'{side}_{j}'])))
        np.savez_compressed(OUT/f'joint-path-target-atoms-{h}.npz',keys=np.asarray(array_keys),targets=np.asarray(TARGETS),values=np.stack(arrays))
        direction,led=direction_forecasts(x,y,q,h)
        all_scores.extend(direction)
        direction_ledger.extend(led)
        print(h,'sessions:',len(q),'historical joint-path and barrier queries',flush=True)
    write('distribution-predictions.csv',pd.DataFrame(all_scores),index=False)
    write('barrier-predictions.csv.gz',pd.DataFrame(all_barriers),index=False)
    write('events.csv',pd.DataFrame(all_events),index=False)
    write('monte-carlo-checks.csv',pd.DataFrame(sim_checks),index=False)
    save('path-ledger.json',{'fits':receipts,'direction_fits':direction_ledger,'models':PATH_MODELS,
         'joint_atoms':JOINT_EXAMPLES,'representation':'Log OHLC relative to prior close, recomposed from one joint path. Diffusion uses 24 intraday steps and an overnight jump. Drawdown/rebound measured on ordered closes.'})


if __name__ == '__main__':
    run()
