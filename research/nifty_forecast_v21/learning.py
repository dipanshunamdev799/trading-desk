"""Chronological, date-balanced learning across the authenticated equity panel."""
from dataclasses import dataclass
from scipy.special import ndtr
from scipy.stats import rankdata

from .common import *
from .panel import TECH,STRUCT,COUNTS,CONTENT,REACTION,ACTIVITY
from .universe import SECTOR_NAMES

TARGETS=('absolute','market_relative','sector_relative','vol_normalized','outperform_market','magnitude','realized_volatility','factor_residual')
TECHNICAL=TECH+STRUCT
FULL=TECHNICAL+COUNTS+CONTENT+REACTION+ACTIVITY
DESIGNS={
    'technical':TECHNICAL,'counts':TECHNICAL+COUNTS,'semantic_and_surprise':TECHNICAL+CONTENT,
    'observed_reaction':TECHNICAL+REACTION,'delivery_and_deals':TECHNICAL+ACTIVITY,'pooled':FULL,
}
MODELS=('history','independent','technical','counts','semantic_and_surprise','observed_reaction','delivery_and_deals','pooled',
        'sector_pool','partial_sector','partial_company','common_relative','factor_residual','random_aux_labels',
        'shifted_company','random_sector','short_pool')


@dataclass
class Ridge:
    center: np.ndarray
    scale: np.ndarray
    base: np.ndarray
    beta: np.ndarray

    def predict(self,x):
        a=np.where(np.isfinite(x),x,self.center)
        return self.base+np.clip((a-self.center)/self.scale,-5,5)@self.beta


def solve(x,y,w,penalty):
    w=w/w.sum()
    finite=np.isfinite(x)
    centers=(w@np.where(finite,x,0.))/np.maximum(1.e-8,w@finite)
    v=np.where(finite,x-centers,0.)
    scale=np.maximum(1.e-6,np.sqrt(w@(v*v)))
    z=np.clip(v/scale,-5,5)
    xb=w@z
    ym=w@y
    z=z-xb
    beta=np.linalg.solve((z*w[:,None]).T@z+penalty*np.eye(x.shape[1]),(z*w[:,None]).T@(y-ym))
    return Ridge(centers,scale,ym-xb@beta,beta)


def date_fit(x,y,good,penalty):
    date,names=np.where(good)
    if len(date)<30:
        return None
    counts=np.bincount(date,minlength=len(good))
    return solve(x[date,names],y[date,names],1/counts[date],penalty)


def independent(x,y,good,core_ix):
    out=[]
    for j in range(x.shape[1]):
        ok=good[:,j]
        t=x[ok,j][:,core_ix]
        out.append(solve(t,y[ok,j],np.ones(len(t)),3.) if len(t)>=35 else None)
    return out


def score(mu,sigma,actual):
    sigma=np.maximum(sigma,1.e-5)
    z=(actual-mu)/sigma
    # CRPS for a normal forecast law in return or volatility units.
    crps=sigma*(z*(2*ndtr(z)-1)+np.sqrt(2/np.pi)*np.exp(-.5*z*z)-1/np.sqrt(np.pi))
    pr=ndtr(mu/sigma)
    event=actual>0
    log=-np.log(np.clip(np.where(event,pr,1-pr),.0005,1.))
    return dict(mae=np.abs(actual-mu), mse=(actual-mu)**2, crps=crps, p=pr, brier=(pr-event)**2,
                log_loss=log, coverage=np.abs(z)<=1.2815515655, width=2.56310313*sigma,
                score_correct=(pr>=.5)==event, actual_up=event)


def aggregate_rows(rows,day,horizon,model,pred,actual,sc,valid,cohort,groups,sector_evidence,event_available):
    for k,name in enumerate(TARGETS):
        y=actual[:,k];mu=pred[:,k]
        ok=valid&np.isfinite(y)&np.isfinite(mu)
        if ok.sum()<8:
            continue
        logs=score(mu[ok],sc[ok,k],y[ok])
        if name=='outperform_market':
            probability=np.clip(mu[ok],.005,.995)
            logs.update(p=probability,brier=(probability-y[ok])**2,
                log_loss=-np.log(np.where(y[ok]>.5,probability,1-probability)),crps=(probability-y[ok])**2,
                score_correct=(probability>=.5)==(y[ok]>.5))
        detail={v:float(np.mean(q)) for v,q in logs.items()}
        rank=np.corrcoef(rankdata(mu[ok]),rankdata(y[ok]))[0,1] if np.std(mu[ok])>1.e-10 and np.std(y[ok])>1.e-10 else np.nan
        row=dict(day=day,horizon=horizon,cohort=cohort,model=model,target=name,n=int(ok.sum()),rank_corr=rank,**detail)
        rows.append(row)
        if name not in ('absolute','market_relative','sector_relative','realized_volatility') or model not in (
             'history','technical','pooled','sector_pool','partial_sector','common_relative','factor_residual','observed_reaction','counts','semantic_and_surprise'):
            continue
        for c in (*SECTOR_NAMES,'event_present','event_absent'):
            inside=(event_available if c=='event_present' else ~event_available) if c.startswith('event_') else groups==SECTOR_NAMES.index(c)
            use=inside[ok]
            if use.sum()<3:
                continue
            sector_evidence.append(dict(day=day,horizon=horizon,cohort=cohort,model=model,target=name,group=c,n=int(use.sum()),
                **{key:float(q[use].mean()) for key,q in logs.items()}))


def scales(p,h):
    base=np.nan_to_num(p[f'scale{h}'],nan=.02 if h==5 else .045).clip(.005,.35)
    vol=np.nan_to_num(p['stock_features'][:,:,list(p['fields']).index('vol21')],nan=.24).clip(.035,1.8)
    return np.stack([base,.78*base,.72*base,np.ones_like(base),np.full_like(base,.5),.74*base,vol*.40,.69*base],axis=-1)


def fit_window(x,y,eligible,t,groups,columns,i,h):
    xx=x[t];yy=y[t]
    ok=eligible[t]&np.isfinite(yy).all(axis=2)
    out={}
    for name,col in columns.items():
        out[name]=date_fit(xx[:,:,col],yy,ok,1.8)
    base=out['pooled']
    z=columns['pooled']
    cn=columns['technical'][:7]
    individual=independent(xx,yy,ok,cn)
    sector=[];null_sectors=[]
    rng=np.random.default_rng(SEED+17*h+i)
    perm=rng.permutation(xx.shape[1])
    for j in range(len(SECTOR_NAMES)):
        sector.append(date_fit(xx[:,:,z],yy,ok&(groups[t]==j),2.2))
        null_sectors.append(date_fit(xx[:,:,z],yy,ok&(groups[t][:,perm]==j),2.2))
    # Reordering labels within a date retains its market shock and removes issuer alignment.
    permute=np.argsort(rng.uniform(size=yy.shape[:2]),axis=1)
    randomized=np.take_along_axis(yy,permute[:,:,None],axis=1)
    rnd=date_fit(xx[:,:,z],randomized,ok&np.isfinite(randomized).all(axis=2),1.8)
    shifted=x[np.maximum(0,t-5)][:,:,z].copy()
    shifted[t<5]=np.nan
    shift=date_fit(shifted,yy,ok,1.8)
    short=date_fit(xx[-70:,:,z],yy[-70:],ok[-70:],1.8)
    safe=np.where(ok[:,:,None],yy,0.)
    day=safe.sum(axis=1)/ok.sum(axis=1)[:,None].clip(1)
    mu=day[ok.any(axis=1)].mean(axis=0)
    n=ok.sum(axis=0)
    hist=.7*mu+.3*np.divide(safe.sum(axis=0),n[:,None],out=np.tile(mu,(len(n),1)),where=n[:,None]>=20)
    info=dict(train_equity_rows=int(ok.sum()),train_dates=int(ok.any(axis=1).sum()),training_assets=int((n>0).sum()),
              coefficient_l2=float(np.linalg.norm(base.beta)),short_coefficient_l2=float(np.linalg.norm(short.beta)))
    return (out,individual,sector,null_sectors,perm,rnd,shift,short,hist,info)


def infer(x,c,groups,market_history,market_ret,sector_hist,bt,gm):
    out,ind,sector,rs,perm,rnd,shift,short,hist,_=c
    z=COLUMNS['pooled']
    f={k:m.predict(x[:,COLUMNS[k]]) for k,m in out.items()}
    pool=f['pooled'];f['history']=hist
    ind_base=COLUMNS['technical'][:7]
    f['independent']=np.array([m.predict(x[j,ind_base]) if m is not None else hist[j] for j,m in enumerate(ind)])
    f['sector_pool']=pool.copy()
    f['random_sector']=pool.copy()
    for j,m in enumerate(sector):
        choose=groups==j
        if m is not None:
            f['sector_pool'][choose]=m.predict(x[choose][:,z])
        choose=groups[perm]==j
        if rs[j] is not None:
            f['random_sector'][choose]=rs[j].predict(x[choose][:,z])
    f['partial_sector']=.25*f['sector_pool']+.75*pool
    f['partial_company']=.18*f['independent']+.82*pool
    f['random_aux_labels']=rnd.predict(x[:,z])
    f['shifted_company']=shift.predict(x[:,z])
    f['short_pool']=short.predict(x[:,z])
    anchor=float(np.nanmedian(market_ret[market_history]))
    rel=np.nanmedian(sector_hist[market_history]-market_ret[market_history,None],axis=0)
    f['common_relative']=pool.copy()
    f['common_relative'][:,0]=anchor+pool[:,1]
    f['factor_residual']=pool.copy()
    f['factor_residual'][:,0]=np.nan_to_num(bt,nan=1.)*anchor+np.nan_to_num(gm)*rel[groups]+pool[:,7]
    return np.stack([f[k] for k in MODELS])


COLUMNS={}


def horizon(p,h):
    days=p['days'];x=p['stock_features'];y=p[f'target{h}'];end=p[f'end{h}'];cohort=p[f'cohort{h}']
    fields=list(p['fields']);sc=scales(p,h);beta=p['beta'];gamma=p['sector_beta'];groups=p['sector'];eligible=p['eligible']
    COLUMNS.update({k:np.array([fields.index(v) for v in dict.fromkeys(f)]) for k,f in DESIGNS.items()})
    s0=p[f'sector_target{h}'];sector_view=np.zeros((len(days),len(SECTOR_NAMES)))
    sector_view[:]=s0
    st=0
    index=p[f'index{h}'];n,d,o=x.shape
    fitted=np.full((len(MODELS),n,d,len(TARGETS)),np.nan,dtype=np.float32)
    receipts=[];metric=[]; by_sector=[]
    cache=None;t=None;last=None;params=[]
    for i,day in enumerate(days):
        if i<65:
            continue
        if cache is None or i-last>=8:
            t=np.flatnonzero((end<day)&(np.arange(n)<i)&np.isfinite(index))[-135:]
            if len(t)<48 or np.isfinite(y[t,:,7]).any(axis=1).sum()<45:
                continue
            cache=fit_window(x,y,eligible,t,groups, COLUMNS,i,h)
            last=i
            m=cache[0]['pooled']
            params.append(dict(day=day,center=m.center.tolist(),scale=m.scale.tolist(),intercept=m.base.tolist(),coefficients=m.beta.tolist()))
        block=infer(x[i],cache,groups[i],t,index,sector_view,beta[i],gamma[i])
        fitted[:,i]=block
        assert end[t[-1]]<day
        receipts.append(dict(horizon=h,day=day,fit_day=days[last],last_mature=end[t[-1]],cohort=cohort[i],**cache[-1]))
        if cohort[i]:
            act=x[i,:,fields.index('announcement_count')]>0
            for j,name in enumerate(MODELS):
                aggregate_rows(metric,day,h,name,block[j],y[i],sc[i],eligible[i],cohort[i],groups[i],by_sector,act)
        st+=1
    save(f'pooled-coefficients-{h}.json',dict(features=list(DESIGNS['pooled']),targets=TARGETS,fits=params))
    print('Pooled/independent evaluation',h,'sessions,',st,'chronological forecasts',flush=True)
    return fitted,sc,pd.DataFrame(metric),pd.DataFrame(by_sector),pd.DataFrame(receipts)


def run():
    p={k:v for k,v in np.load(OUT/'component-panel.npz',allow_pickle=False).items()}
    result={h:horizon(p,h) for h in HORIZONS}
    np.savez_compressed(OUT/'equity-forecast-laws.npz',models=np.array(MODELS),targets=np.array(TARGETS),dates=p['days'],symbols=p['symbols'],
                        **{f'mean{h}':result[h][0] for h in HORIZONS},**{f'sigma{h}':result[h][1] for h in HORIZONS})
    hourly=pd.concat([result[h][2] for h in HORIZONS],ignore_index=True)
    sect=pd.concat([result[h][3] for h in HORIZONS],ignore_index=True)
    fit=pd.concat([result[h][4] for h in HORIZONS],ignore_index=True)
    write('stock-date-scores.csv.gz',hourly)
    write('stock-sector-date-scores.csv.gz',sect)
    write('equity-fit-receipts.csv',fit)
    metrics=['mae','mse','rank_corr','crps','brier','log_loss','coverage','width','score_correct','p','actual_up']
    main=pd.concat([hourly.assign(scope='combined'),hourly.assign(scope=hourly.cohort)])
    z=main.groupby(['horizon','model','target','scope'],as_index=False).agg(dates=('day','size'),stock_cases=('n','sum'),
                        **{k:(k,'mean') for k in metrics}).assign(rmse=lambda x:x.mse**.5)
    write('stock-leaderboard.csv',z)
    more=sect.groupby(['horizon','model','target','group','cohort'],as_index=False).agg(dates=('day','size'),stock_cases=('n','sum'),
                    **{k:(k,'mean') for k in metrics if k!='rank_corr'})
    write('stock-sector-leaderboard.csv',more)
    save('equity-model-config.json',dict(architectures=MODELS,designs=DESIGNS,targets=TARGETS,refit_every=8,
        objective='Ridge with one unit of mass per source date distributed across eligible securities. Robust train-only centering, imputation and scaling.',
        pooled_penalty=1.8,per_stock_penalty=3.,sector_penalty=2.2,sector_deviation_weight=.25,company_deviation_weight=.18,
        no_transfer='Per-issuer fit with the same date cut and past technical information',
        distribution='Gaussian marginal location and recorded historical scale. Outperformance uses one explicitly calibrated Bernoulli head.',
        nulls='Within-date randomized auxiliary targets, features shifted five cash sessions earlier, random sector labels, 70-date estimation.',
        dates='At most 135 recently matured dates. Training labels end strictly before the forecast session. Stocks receive fixed date mass.',
        risk='Daily realized volatility target is distinct from terminal absolute return and from Gaussian predictive dispersion.'))


if __name__=='__main__':
    run()
