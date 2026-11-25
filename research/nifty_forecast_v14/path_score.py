"""Score coherent OHLC forecasts, passage time and joint multivariate outcomes."""
from .common import *
from .data import observed_metrics
from .generation import TICK
from research.nifty_forecast_v13.data import path_metrics

Q_NAMES=['q025','q05','q10','q25','q50','q75','q90','q95','q975']
SCORE_TARGETS=('endpoint_return','abs_return','volatility','range','high','low','drawdown','rebound',
               'max_gap','speed','vol_change','vol_acceleration','overnight_sd','regular_sd')
INNER={'50':(3,5),'80':(2,6),'90':(1,7),'95':(0,8)}
ENERGY=('endpoint_return','range','high','low','volatility','drawdown')
LOG_FLOOR=.0005


def log_brier(probability,hit):
    p=np.clip(probability,LOG_FLOOR,1-LOG_FLOOR)
    return (probability-hit)**2,-hit*np.log(p)-(1-hit)*np.log1p(-p)


def summaries(a,y,w):
    """Score independent marginal projections of one specified weighted law."""
    a=np.asarray(a,float)
    if a.ndim==1:
        a=a[:,None]
    y=np.asarray(y,float)
    weight=np.asarray(w,float)
    assert np.isclose(weight.sum(),1.0)
    ix=np.argsort(a,axis=0,kind='stable')
    atoms=np.take_along_axis(a,ix,axis=0)
    sw=weight[ix]
    cdf=sw.cumsum(axis=0)
    q_index=np.sum(cdf[None,:,:]<QUANTILES[:,None,None]-1e-13,axis=1).clip(max=len(a)-1)
    q=np.take_along_axis(atoms,q_index,axis=0)
    mean=weight@a
    crps=weight@np.abs(a-y)-np.sum(sw*atoms*(2*cdf-sw-1),axis=0)
    pin=np.maximum(QUANTILES[:,None]*(y-q),(QUANTILES[:,None]-1)*(y-q)).mean(axis=0)
    out=[]
    for k in range(a.shape[1]):
        s=dict(predicted_mean=mean[k],predicted_median=q[4,k],mae=abs(mean[k]-y[k]),
               se=(mean[k]-y[k])**2,crps=crps[k],pinball=pin[k],
               pit=float(weight@(a[:,k]<=y[k])))
        s.update({n:q[j,k] for j,n in enumerate(Q_NAMES)})
        for c,(lo,hi) in INNER.items():
            v,z=q[lo,k],q[hi,k]
            s.update({f'coverage{c}':int(v<=y[k]<=z),f'width{c}':z-v,f'lower_miss{c}':int(y[k]<v),f'upper_miss{c}':int(y[k]>z),
                    f'interval_score{c}':z-v+2/(1-int(c)/100)*(max(0.,v-y[k])+max(0.,y[k]-z))})
        out.append(s)
    return out


def path_quantities(paths,target,origin_trailing_lag):
    one=path_metrics(paths)
    extra=observed_metrics(paths)
    # Expansion and acceleration reference the historical realized state.
    one.update({k:extra[k] for k in ('max_gap','first_gap','speed','variance','aligned_fraction','peak_shock_share',
                                     'vol_first','vol_last','acceleration')})
    one['vol_change']=one['volatility']-target.trailing_at_origin
    one['vol_acceleration']=one['speed']-(target.trailing_at_origin-origin_trailing_lag)
    return one


def events(h,m,t,th):
    vol0=t.trailing_at_origin
    sigma=t.horizon_sd_at_origin
    rv=m['volatility']
    ret=m['endpoint_return']
    return {
      'upper_fixed':ret>=(.03 if h==5 else .05),'lower_fixed':ret<=(-.03 if h==5 else -.05),
      'range_fixed':m['range']>=(.055 if h==5 else .10),
      'upper_excursion_fixed':m['high']>=.05,'lower_excursion_fixed':m['low']<=-.05,
      'upper_relative':ret>=th.up90,'lower_relative':ret<=th.down10,'range_relative':m['range']>=th.range90,
      'high_relative':m['high']>=th.high90,'low_relative':m['low']<=th.low10,
      'upper_iv_scaled':ret>=1.5*sigma,'lower_iv_scaled':ret<=-1.5*sigma,'range_iv_scaled':m['range']>=2*sigma,
      'expand':rv>=1.25*vol0,'contract':rv<=.8*vol0,'high_state':rv>=th.high_risk,
      'enter_high':rv>=th.high_risk,'exit_high':rv<th.high_risk,
      'persist_high':(m['vol_first']>=th.high_risk)&(m['vol_last']>=th.high_risk),
      'rapid_risk':m['speed']>th.speed90,'variance_extreme':m['variance']>=th.var90,
      'persist_up':(ret>=th.up90)&(m['aligned_fraction']>=.65)&(m['peak_shock_share']<=.5),
      'persist_down':(ret<=th.down10)&(m['aligned_fraction']>=.65)&(m['peak_shock_share']<=.5),
      'gap_fixed':m['max_gap']>=.012,'gap_relative':m['max_gap']>=th.gap90,'acceleration':m['acceleration']>=th.accel90}


def indices(p,k,side):
    b=(p[:,:,1]>=1+k) if side=='upper' else (p[:,:,2]<=1-k)
    return np.where(b.any(axis=1),b.argmax(axis=1)+1,p.shape[1]+1)


def order(p,tup,tdn,k):
    h=p.shape[1]
    equal=(tup==tdn)&(tup<=h)
    loc=p[np.arange(len(p)),np.minimum(tup-1,h-1),0]
    p_up=(tup<tdn)|(equal&(loc>=1+k))
    p_down=(tdn<tup)|(equal&(loc<=1-k))
    return np.where(p_up,0,np.where(p_down,1,np.where(equal,2,3)))


def score_barriers(p,w,observed,h,ts,meta):
    sides=[];ordering=[]
    last_upper,last_lower=1.,1.
    for label,k,real_tu,real_td,real_order,resolved in ts:
        # Observed and simulated order use the same daily-candle information.
        u=indices(p,k,'upper')
        d=indices(p,k,'lower')
        both=float(w@((u<=h)&(d<=h)))
        neither=float(w@((u>h)&(d>h)))
        rank=order(p,u,d,k)
        counts=np.bincount(rank,weights=w,minlength=4)
        assert abs(counts.sum()-1.)<1.e-9 and abs(counts[3]-neither)<1.e-9
        jointly=dict(**meta,barrier=label,threshold=k,p_both=both,p_neither=neither,
                     p_upper_first=counts[0],p_lower_first=counts[1],p_same_candle=counts[2],
                     actual_daily_order=real_order,intraday_resolved_order=resolved,
                     order_brier=float(np.square(counts-np.eye(4)[real_order]).sum()),
                     order_log_loss=float(-np.log(np.clip(counts[real_order],LOG_FLOOR,1))),
                     actual_both=int(real_tu<=h and real_td<=h),actual_neither=int(real_tu>h and real_td>h))
        ordering.append(jointly)
        probability=[]
        for side,ti,actual,endpoint,ac in [('upper',u,real_tu,p[:,-1,3]>=1+k,np.any(p[:,:,3]>=1+k,axis=1)),
                                          ('lower',d,real_td,p[:,-1,3]<=1-k,np.any(p[:,:,3]<=1-k,axis=1))]:
            pmf=np.bincount(ti,weights=w,minlength=h+2)
            fp=pmf.cumsum()[1:h+1]
            label_time=(np.arange(1,h+1)>=actual)
            hit=int(actual<=h)
            pr=min(1.,float(fp[-1]))
            end_p=float(w@endpoint)
            any_close_p=float(w@ac)
            assert pr+2.e-12>=any_close_p and any_close_p+2.e-12>=end_p
            loss,_=log_brier(pr,hit)
            match=observed[0,:,3]
            end_obs=int(match[-1]>=1+k if side=='upper' else match[-1]<=1-k)
            close_obs=int(np.any(match>=1+k if side=='upper' else match<=1-k))
            # Passage-day categories include H+1 for no hit, giving a censored terminal category.
            expected=float(np.dot(np.arange(1,h+1),pmf[1:h+1])/pr) if pr>1.e-12 else np.nan
            sides.append(dict(**meta,barrier=label,threshold=k,side=side,p_touch=pr,actual=hit,actual_time=actual,
                p_endpoint=end_p,actual_endpoint=end_obs,p_close=any_close_p,actual_close=close_obs,brier=loss,
                log_loss=-np.log(np.clip(pr if hit else 1-pr,LOG_FLOOR,1)),
                integrated_brier=float(np.mean((fp-label_time)**2)),
                passage_log_loss=float(-np.log(np.clip(pmf[actual],LOG_FLOOR,1))),
                expected_time_given_touch=expected,survival=1-pr,p_by_session=json.dumps(fp.round(10).tolist())))
            probability.append(pr)
        assert abs(both+neither-(1-probability[0]-probability[1]+2*both))<1.e-9
        assert both<=min(probability)+1.e-9
        if label.isdigit():
            assert probability[0]<=last_upper+1.e-9 and probability[1]<=last_lower+1.e-9
            last_upper,last_lower=probability
    return sides,ordering


def multivariate(values,actual,scale,w):
    v=values/scale
    a=actual/scale
    # Energy's pair term uses independently permuted ranks with common random numbers.
    g=np.random.default_rng(SEED+177)
    pos=g.random((2,1024))
    c=w.cumsum()
    ix=np.searchsorted(c,pos).clip(max=len(w)-1)
    energy=float(w@np.linalg.norm(v-a,axis=1)-.5*np.linalg.norm(v[ix[0]]-v[ix[1]],axis=1).mean())
    vi,vj=np.triu_indices(v.shape[1],1)
    dependence=(w@np.sqrt(abs(v[:,vi]-v[:,vj]))-np.sqrt(abs(a[vi]-a[vj])))**2
    return dict(energy_score=energy,variogram_score=float(dependence.mean()))


def time_labels(observed,t,h):
    o=[]
    levels=[(str(j),k,j) for j,k in enumerate(BARRIERS)]
    levels+=[(f'iv{z}',float(z*t.horizon_sd_at_origin),None) for z in SCALED]
    for name,k,j in levels:
        a=indices(observed,k,'upper')[0]
        b=indices(observed,k,'lower')[0]
        c=order(observed,np.array([a]),np.array([b]),k)[0]
        resolved=t[f'ordering_{j}'] if j is not None and f'ordering_{j}' in t else None
        o.append((name,k,int(a),int(b),int(c),resolved))
    return o


def path_score():
    y={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    threshold={h:matrix(f'thresholds-{h}.csv') for h in HORIZONS}
    book={h:dict() for h in HORIZONS}
    for h in HORIZONS:
        with np.load(OUT/f'observed-{h}.npz') as z:
            paths=z['paths']
            origins=z['origins']
        book[h]={d:paths[i:i+1] for i,d in enumerate(origins)}
    catalog=read('joint-path-ledger.json')
    names=catalog['models']
    ev_rows=[];bar_rows=[];or_rows=[];dist_rows=[];joint=[]
    for i,r in enumerate(catalog['rows']):
        day=r['origin']
        eligible=[h for h in HORIZONS if day in y[h].index and pd.notna(y[h].at[day,'cohort'])]
        cases={}
        for h in eligible:
            row=y[h].loc[day]
            observed=book[h][day]
            hist=y[h].iloc[mature(y[h],day,180)][list(ENERGY)]
            cases[h]=(row,threshold[h].loc[day],y[h].trailing_at_origin.shift(max(1,h//2)).at[day],observed,
                      time_labels(observed,row,h),hist.std().clip(.003).to_numpy())
        with np.load(OUT/r['file'],allow_pickle=False) as file:
            same_paths=None
            w_pit=file['joint_pit_weights']
            n=r['samples']
            weights=np.full(n,1/n)
            for model in names:
                key='path_mixture' if model=='joint_pit' else model
                if key=='path_mixture' and same_paths is not None:
                    prices=same_paths
                else:
                    prices=np.exp(TICK*file[key])
                    if key=='path_mixture':
                        same_paths=prices
                w=w_pit if model=='joint_pit' else weights
                # Same paths and weights ensure common-origin fixed-barrier monotonicity across both horizons.
                if len(eligible)==2:
                    for k in BARRIERS:
                        assert np.all((prices[:,:5,1].max(axis=1)>=1+k)<=(prices[:,:,1].max(axis=1)>=1+k))
                        assert np.all((prices[:,:5,2].min(axis=1)<=1-k)<=(prices[:,:,2].min(axis=1)<=1-k))
                for h in eligible:
                    row,cut,pre,observed,time,unit=cases[h]
                    p=prices[:,:h]
                    metrics=path_quantities(p,row,pre)
                    assert (abs(metrics['range']-(metrics['high']-metrics['low']))<2.e-12).all()
                    targets=[k for k in SCORE_TARGETS if np.isfinite(row[k])]
                    forecast=np.column_stack([metrics[k] for k in targets])
                    actual=row[targets].to_numpy(dtype=float)
                    base=dict(horizon=h,origin=day,cohort=row.cohort,model=model)
                    for k,j in zip(targets,summaries(forecast,actual,w)):
                        j.update(base,target=k,actual=row[k])
                        if k=='endpoint_return':
                            p1=float(w@(metrics[k]>0))
                            b,l=log_brier(p1,int(row[k]>0))
                            j.update(p_up=p1,brier=b,log_loss=l)
                        dist_rows.append(j)
                    current=events(h,metrics,row,cut)
                    ek=[name for name in current if np.isfinite(row['event_'+name])]
                    ev=np.column_stack([current[k] for k in ek])
                    rates=w@ev
                    ev_rows.extend(dict(**base,event=k,actual=int(row['event_'+k]),p=float(prob))
                                   for k,prob in zip(ek,rates))
                    bs,os=score_barriers(p,w,observed,h,time,base)
                    bar_rows.extend(bs);or_rows.extend(os)
                    dims=np.column_stack([metrics[k] for k in ENERGY])
                    joint.append(dict(**base,**multivariate(dims,row[list(ENERGY)].to_numpy(float),unit,w)))
        if (i+1)%45==0:
            print('Scored joint path origins',i+1,'/',len(catalog['rows']),flush=True)
    write('path-marginals.csv.gz',pd.DataFrame(dist_rows))
    write('path-tail-and-transition-probabilities.csv.gz',pd.DataFrame(ev_rows))
    write('path-passage.csv.gz',pd.DataFrame(bar_rows))
    write('path-ordering.csv.gz',pd.DataFrame(or_rows))
    write('multivariate-path-scores.csv',pd.DataFrame(joint))
    print('Path scores:',len(dist_rows),'marginals,',len(bar_rows),'passage forecasts,',len(ev_rows),'extreme/transition probabilities',flush=True)


if __name__=='__main__':
    path_score()
