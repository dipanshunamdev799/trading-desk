"""Matured-label transition, tail, opening-gap and direct barrier models."""
from scipy.optimize import minimize
from scipy.special import expit, logit, ndtr
from scipy.stats import chi2

from .common import *
from .data import BASE, DOM, GLOBAL, INTRA, MECHANICS, SURFACE
from .volatility import robust_design, ridge, design_apply

RISK_BASE = ('atm','trailing','rv5','rv21','vix_level','ewma_fast','ewma_slow','atm1')
ALT=('iv_nearest','iv_term','iv_skew','iv_curvature','density_forward_skew','density_priced_down5','q_up3','q_down3')


def specifications():
    return {
      'persist':('trailing','rv5','rv21','rv42','ewma_fast','ewma_slow'),
      'raw_iv_logistic':('atm',),
      'domestic':RISK_BASE+DOM+MECHANICS[:4],
      'surface':RISK_BASE+SURFACE+tuple('trade_'+k for k in ('q_up3','q_down3')),
      'surface_lag5':RISK_BASE+tuple('lag5_'+k for k in ALT),
      'surface_shift21':RISK_BASE+tuple(k+'_shifted' for k in SURFACE),
      'surface_permuted':RISK_BASE+SURFACE,
      'surface_liquid':RISK_BASE+tuple('liquid_'+k for k in ALT),
      'surface_truncated':RISK_BASE+tuple('truncated_'+k for k in ALT),
      'intraday':RISK_BASE+INTRA+('intra_gap21','rth_rv21','overnight_rv21'),
      'jump_1m':RISK_BASE+('jump_share_1','positive_excess_1','max_abs_intraday_1','past_largest_gap'),
      'jump_5m':RISK_BASE+('jump_share_5','positive_excess_5','max_abs_intraday_5','past_largest_gap'),
      'jump_shift21':RISK_BASE+('jump_share_1_shift21','jump_share_5_shift21','past_largest_gap'),
      'offshore_opening':RISK_BASE+('global_gap_risk','fx_shock','oil_shock','night_asia','night_us','overnight_rv21'),
      'domestic_global_interaction':RISK_BASE+DOM+GLOBAL+MECHANICS+('global_gap_risk','night_asia','night_us'),
      'markov_state':('trailing','rv5','rv21','atm','market_state','state_age','state_prior','atm1','vrp')}


def fit_logistic(z, y, penalty=22.):
    a=np.column_stack([np.ones(len(z)),z])
    keep=np.isfinite(y)
    k=int(keep.sum())
    values=y[keep]
    nup=int(values.sum())
    init=np.zeros(a.shape[1])
    init[0]=logit((nup+.75)/(k+1.50))
    if min(nup,k-nup)<4 or not z.shape[1]:
        return init,dict(n=k,events=nup,converged=True,fallback='smoothed frequencies')
    xx=a[keep]
    def loss(b):
        t=xx@b
        grad=xx.T@(expit(t)-values)
        grad[1:]+=penalty*b[1:]
        return np.logaddexp(0,t).sum()-values@t+.5*penalty*(b[1:]@b[1:]),grad
    ret=minimize(loss,init,jac=True,method='L-BFGS-B',options={'maxiter':50,'gtol':1.e-6})
    return ret.x,dict(n=k,events=nup,converged=bool(ret.success),fallback=None)


def process_probabilities(h,t,threshold,sd):
    a=float(t.trailing_at_origin)
    hvar=threshold.high_risk
    scale=sd*np.sqrt(h/252.)
    jump_level=.03 if h==5 else .05
    return {
      'upper_fixed':ndtr(-np.log1p(jump_level)/scale),'lower_fixed':ndtr(np.log1p(-jump_level)/scale),
      'upper_relative':ndtr(-np.log1p(threshold.up90)/scale),'lower_relative':ndtr(np.log1p(threshold.down10)/scale),
      'upper_iv_scaled':ndtr(-np.log1p(1.5*t.horizon_sd_at_origin)/scale),
      'lower_iv_scaled':ndtr(np.log1p(-1.5*t.horizon_sd_at_origin)/scale),
      'expand':chi2.sf(h*(1.25*a/sd)**2,h),'contract':chi2.cdf(h*(.80*a/sd)**2,h),
      'high_state':chi2.sf(h*(hvar/sd)**2,h),'enter_high':chi2.sf(h*(hvar/sd)**2,h),
      'exit_high':chi2.cdf(h*(hvar/sd)**2,h),'variance_extreme':chi2.sf(h*threshold.var90/sd**2,h)
      }


def add_observable_mechanisms(x):
    x=x.copy()
    # Build ex-ante synchronization and transmitted gap-risk channels using earlier market timestamps.
    x['night_asia']=x[['asia_shock','hk_shock']].mean(axis=1)
    x['night_us']=x[['nasdaq_shock','us_shock']].mean(axis=1)
    x['global_gap_risk']=x[['night_asia','night_us','fx_shock','oil_shock']].divide(
        x[['night_asia','night_us','fx_shock','oil_shock']].shift().rolling(63,min_periods=25).median().clip(.0001)).mean(axis=1)
    cutoff=x.rv5.shift().rolling(126,min_periods=35).quantile(.75)
    state=x.rv5.gt(cutoff).astype(float).where(cutoff.notna())
    x['market_state']=state
    x['state_prior']=state.shift().rolling(21,min_periods=12).mean()
    x['state_age']=state.groupby((state!=state.shift()).cumsum()).cumcount().clip(15).to_numpy()
    x=pd.concat([x,x.reindex(columns=SURFACE).shift(21).add_suffix('_shifted')],axis=1)
    return x


def regimes():
    estimates,orders,gaps,fit_records,warning,led_skip=[],[],[],[],[],[]
    f=pd.read_csv(OUT/'process-risk-predictions.csv')
    stat={(h,m):g.set_index('origin').prediction for (h,m),g in f.groupby(['horizon','model'])}
    previous=pd.read_csv(V13/'distribution-predictions.csv',low_memory=False)
    specs=specifications()
    risk_continuous=['vol_change','vol_acceleration','speed']
    continuous_rows=[]
    for h in HORIZONS:
        x=add_observable_mechanisms(matrix(f'features-{h}.csv'))
        y=matrix(f'targets-{h}.csv')
        thresholds=matrix(f'thresholds-{h}.csv')
        query=y[y.cohort.notna()]
        event_cols=[k for k in y if k.startswith('event_')]
        support_cols=[k for k in y if k.startswith(('upper_touch_','lower_touch_'))]
        y_train=y[event_cols].to_numpy()
        prior=previous[previous.horizon.eq(h)&previous.model.eq('diffusion_iv')&previous.target.eq('range')].set_index('origin')
        warnings=prior.actual.gt(prior.q90).astype(float).reindex(y.index)
        # Refit at each first forecast in a month. The oldest archived outcome used by any fit is visible in its receipt.
        for month,group in query.groupby(query.index.str[:7],sort=True):
            start=group.index.min()
            t=mature(y,start,185)
            if len(t)<50:
                led_skip.append(dict(horizon=h,month=month,reason='fewer than 50 completed train windows'))
                continue
            tr=x.reindex(y.index).iloc[t]
            test=x.loc[group.index]
            outcomes=y_train[t]
            actual=group[event_cols].to_numpy()
            valid=np.isfinite(actual)
            stats=y.iloc[t]
            last_mature=stats.endpoint.max()
            assert last_mature<start
            for name,fields in specs.items():
                a,b,note=robust_design(tr,test,fields)
                if name=='surface_permuted':
                    ids=np.array_split(np.arange(len(a)),max(2,len(a)//13))
                    rng=np.random.default_rng(SEED+h+pd.Timestamp(start).toordinal())
                    rows=np.concatenate([ids[j] for j in rng.permutation(len(ids))])
                    flag=np.array([k not in RISK_BASE for k in note['fields']])
                    a[:,flag]=a[rows][:,flag]
                params=[]; descriptions=[]
                for j,event in enumerate(event_cols):
                    pars,meta=fit_logistic(a,outcomes[:,j])
                    params.append(pars)
                    descriptions.append({'event':event[6:],**meta})
                probs=expit(np.column_stack([np.ones(len(b)),b])@np.stack(params).T)
                for i,day in enumerate(group.index):
                    for j in np.flatnonzero(valid[i]):
                        estimates.append(dict(horizon=h,origin=day,model=name,event=event_cols[j][6:],
                                              actual=int(actual[i,j]),p=float(probs[i,j])))
                fit_records.append(dict(horizon=h,cutoff=start,last_mature=last_mature,model=name,
                                        training_dates=tr.index.tolist(),query_dates=group.index.tolist(),
                                        transform=note,columns=descriptions,parameters=np.stack(params).tolist()))
                if name in {'persist','intraday','surface','domestic_global_interaction'}:
                    usable=stats[risk_continuous].notna().all(axis=1).to_numpy()
                    coefs=ridge(a[usable],stats.loc[usable,risk_continuous].to_numpy(),145.)
                    y_hat=design_apply(b,coefs)
                    for i,d in enumerate(group.index):
                        for j,k in enumerate(risk_continuous):
                            continuous_rows.append(dict(horizon=h,origin=d,model=name,target=k,prediction=float(y_hat[i,j]),
                                                  actual=float(group.at[d,k])))
                    fit_records[-1]['transition_continuous_parameters']=coefs.tolist()
            base_exp=np.divide(np.nansum(outcomes,axis=0)+.75,np.sum(np.isfinite(outcomes),axis=0)+1.5)
            for day,tgt in group.iterrows():
                threshold=thresholds.loc[day]
                for j,k in enumerate(event_cols):
                    if np.isfinite(tgt[k]):
                        estimates.append(dict(horizon=h,origin=day,model='historical',event=k[6:],actual=int(tgt[k]),p=float(base_exp[j])))
                        if k[6:] in {'expand','contract','high_state','enter_high','exit_high','variance_extreme'}:
                            estimates.append(dict(horizon=h,origin=day,model='no_change',event=k[6:],actual=int(tgt[k]),
                                p=float(tgt.trailing_at_origin>=threshold.high_risk) if k[6:]=='high_state' else 0.))
                for name,risk in [('iv_raw',x.at[day,'atm']),('gjr_control',stat[h,'gjr_student'].at[day]),
                                  ('gjr_iv_control',stat[h,'gjr_ivx'].at[day]),('state_variance_control',stat[h,'two_state'].at[day])]:
                    for k,p in process_probabilities(h,tgt,threshold,risk).items():
                        if np.isfinite(tgt['event_'+k]):
                            estimates.append(dict(horizon=h,origin=day,model=name,event=k,
                                                  actual=int(tgt['event_'+k]),p=float(p)))
            # A standalone barrier classifier has one calibrated regression per side and strike.
            a,b,note=robust_design(tr,test,RISK_BASE+DOM[:5]+('iv_skew','overnight_share'))
            column=[]; tokens=[]
            for k in support_cols:
                v,notes=fit_logistic(a,stats[k].to_numpy(float),25.)
                column.append(v)
                tokens.append((k,notes))
            probabilities=expit(np.column_stack([np.ones(len(b)),b])@np.stack(column).T)
            for i,d in enumerate(group.index):
                for side in ['upper','lower']:
                    upper=1.
                    for j,k in enumerate(BARRIERS):
                        key=f'{side}_touch_{j}'
                        p=min(upper,probabilities[i,support_cols.index(key)])
                        upper=p
                        orders.append(dict(horizon=h,origin=d,model='logistic_barrier',barrier=str(j),threshold=k,
                                           side=side,p_touch=float(p),actual=int(group.at[d,key])))
            fit_records.append(dict(horizon=h,cutoff=start,last_mature=last_mature,model='logistic_barrier',transform=note,
                                  columns=tokens,parameters=np.stack(column).tolist(),training_dates=tr.index.tolist()))
            # Target the first subsequent open rather than adding generic offshore predictors to the daily endpoint.
            for name,cols in [('opening_gap_domestic',('overnight_rv21','vix_level','atm','past_largest_gap','rv5')),
                              ('opening_gap_offshore',('overnight_rv21','vix_level','atm','past_largest_gap','rv5','night_us',
                               'night_asia','global_gap_risk','vix_move','vxn_move','fx_shock','oil_shock','gold_etf_risk','weak_global'))]:
                a,b,note=robust_design(tr,test,cols)
                g=stats.first_gap.to_numpy()
                coef=ridge(a,np.log(np.maximum(abs(g),.00055)),145.)
                est=np.exp(design_apply(b,coef))
                direction,meta=fit_logistic(a,np.asarray(g>0,float),26.)
                pr=expit(design_apply(b,direction))
                for i,d in enumerate(group.index):
                    gaps.append(dict(horizon=h,origin=d,model=name,actual_abs=abs(group.at[d,'first_gap']),
                                     actual_sign=int(group.at[d,'first_gap']>0),forecast_abs=est[i],p_gap_up=pr[i]))
                fit_records.append(dict(horizon=h,cutoff=start,last_mature=last_mature,model=name,
                                  transform=note,parameters=coef.tolist(),direction=direction.tolist(),sign_fit=meta,
                                  training_dates=tr.index.tolist()))
            # Warn of an underestimated range using exclusively matured historical V13 errors.
            a,b,note=robust_design(tr,test,BASE+DOM+('global_gap_risk','jump_share_5','iv_skew','vrp'))
            hist=warnings.iloc[t].to_numpy()
            if np.isfinite(hist).sum()>=20:
                equation,meta=fit_logistic(a,hist,36.)
                pred=expit(design_apply(b,equation))
                for i,d in enumerate(group.index):
                    warning.append(dict(horizon=h,origin=d,p_warning=pred[i],actual=warnings.at[d],sample=meta['n']))
                fit_records.append(dict(horizon=h,cutoff=start,last_mature=last_mature,model='range_miss_warning',transform=note,
                                  parameters=equation.tolist(),status=meta,training_dates=tr.index.tolist()))
    write('transition-and-tail-probabilities.csv.gz',pd.DataFrame(estimates))
    write('transition-continuous.csv',pd.DataFrame(continuous_rows))
    write('direct-barriers.csv',pd.DataFrame(orders))
    write('opening-gap-forecasts.csv',pd.DataFrame(gaps))
    write('failure-warning-forecasts.csv',pd.DataFrame(warning))
    save('signal-fit-ledger.json',{'fits':fit_records,'unestimated':led_skip})
    print('Transition/tail probability rows',len(estimates),'and standalone barriers',len(orders),flush=True)


if __name__=='__main__':
    regimes()
