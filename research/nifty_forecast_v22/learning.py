"""Date-balanced transfer on comparable market tasks and strictly held-out domains."""
from itertools import chain

from .common import *
from .panel import FIELDS,GLOBAL,MECHANISMS

OWN=FIELDS[:10]+('fx5',)
TARGETS=('directional_location','global_component','regional_component','country_innovation','magnitude','volatility_log_ratio',
         'range_log_ratio','expansion','contraction','reversal','recovery','divergence','breadth_deterioration')
MODELS=('local_history','local_persistence','local_ridge','local_own_only','global_factor_only','loco_transfer','loro_transfer',
        'pooled_with_context','partial_country','factor_and_innovation','factor_only','dominant_excluded','country_shuffle',
        'shifted_country_features','date_block_null','delayed_transfer','low_rank_shared',
        *('mechanism_'+s for s in MECHANISMS))
Q=(np.arange(64)+.5)/64
START='2025-06-01'
LATER='2026-07-01'
DAY=86_400_000_000_000


@dataclass
class Model:
    fields: tuple
    center: np.ndarray
    scale: np.ndarray
    intercept: np.ndarray
    coefficient: np.ndarray

    def predict(self,raw):
        x=raw[:,self.fields]
        z=np.clip((np.where(np.isfinite(x),x,self.center)-self.center)/self.scale,-5,5)
        return self.intercept+z@self.coefficient

    def raw_prior(self,center,scale):
        b=self.coefficient/self.scale[:,None]
        return b*scale[:,None], self.intercept+(center-self.center)@b


def selected(fields):
    return tuple(FIELDS.index(k) for k in dict.fromkeys(fields))


def train(x,y,day,indices,penalty=1.65,prior=None):
    """Train-only preprocessing. Each available UTC origin date contributes one unit of mass."""
    x=x[:,indices]
    observer=np.isfinite(y).any(axis=1)
    if not observer.any():
        raise ValueError('Empty training targets')
    x=x[observer];y=y[observer];day=day[observer]
    _,ix,n=np.unique(day,return_inverse=True,return_counts=True)
    w=1./n[ix];w=w/w.sum()
    seen=np.isfinite(x)
    xx=np.where(seen,x,0.)
    c=(w@xx)/np.maximum(1.e-8,w@seen)
    raw=np.where(seen,x-c,0.)
    s=np.maximum(1.e-6,np.sqrt(w@(raw*raw)))
    z=np.clip(raw/s,-5.,5.)
    # A mechanical copy of a column must leave the posterior unchanged.
    dup=[];flag=set()
    for j in range(z.shape[1]):
        key=np.ascontiguousarray(z[:,j]).tobytes()
        if key in flag: dup.append(j)
        flag.add(key)
    z[:,dup]=0.
    k=z.shape[1];m=y.shape[1]
    intercept=np.zeros(m);coef=np.zeros((k,m))
    prior_b,prior_c=(prior.raw_prior(c,s) if prior is not None else (np.zeros((k,m)),np.zeros(m)))
    prior_b[dup]=0.
    target_masks={}
    for j in range(m):
        q=np.isfinite(y[:,j])
        target_masks.setdefault(q.tobytes(),(q,[]))[1].append(j)
    for q,cols in target_masks.values():
        if q.sum()<22:
            intercept[cols]=prior_c[cols]
            continue
        a=z[q];v=y[q][:,cols];u=w[q]/w[q].sum()
        ex=u@a;base=u@v
        a=a-ex
        mat=(a*u[:,None]).T@a+penalty*np.eye(k)
        vec=(a*u[:,None]).T@(v-base)+penalty*prior_b[:,cols]
        coef[:,cols]=np.linalg.solve(mat,vec)
        intercept[cols]=base-ex@coef[:,cols]
    return Model(indices,c,s,intercept,coef)


def target_array(h,x):
    scale=x.raw_daily_sigma.to_numpy(float)*np.sqrt(h)
    rv=x.raw_daily_sigma.to_numpy(float)*np.sqrt(252)
    y=np.column_stack([x.normalized,x.global_log/scale,x.regional_log/scale,x.innovation_log/scale,x.absolute,
           np.log(x.realized_vol/rv),np.log(x.future_range/scale),x.expansion,x.contraction,x.reversal,x.recovery,x.divergence,x.breadth_deterioration])
    y[:,:4]=np.clip(y[:,:4],-7,7)
    y[:,4]=np.clip(y[:,4],0,6)
    y[:,5:7]=np.clip(y[:,5:7],-3,3)
    y[~np.isfinite(y)]=np.nan
    return y


def eligible(x,cut,days=255):
    eligible=x.mature_ns.lt(cut)&x.issue_ns.lt(cut)&x.ret.notna()&x.raw_daily_sigma.notna()
    eligible&=x.issue_ns.ge(cut-days*DAY)
    return eligible.to_numpy()


def date_null(y,day,rng):
    stamps=np.unique(day)
    chunks=np.array_split(stamps,max(3,len(stamps)//8))
    shuffled=np.concatenate([chunks[j] for j in rng.permutation(len(chunks))])
    centers=pd.DataFrame(y).groupby(day).mean().reindex(stamps).to_numpy(float)
    base=np.searchsorted(stamps,day)
    perm=np.searchsorted(stamps,shuffled[base])
    return y+centers[perm]-centers[base]


def date_country_permute(y,day,rng):
    copy=y.copy()
    for d in np.split(np.argsort(day,kind='stable'),np.unique(np.sort(day),return_index=True)[1][1:]):
        copy[d]=y[rng.permutation(d)]
    return copy


def law(history):
    v=np.asarray(history,float);v=v[np.isfinite(v)]
    if len(v)<30:
        return np.linspace(-2.12,2.12,len(Q))
    return np.quantile(v-np.median(v),Q)


def scores(normal,center,scale,y):
    a=np.expm1(np.clip(scale[:,None]*(normal+center[:,None]),-1.9,1.5))
    pp=(a>0).mean(axis=1)
    med=np.quantile(a,.5,axis=1)
    lo=np.quantile(a,.10,axis=1);hi=np.quantile(a,.90,axis=1)
    mu=a.mean(axis=1)
    dy=y>0
    co=(2*np.arange(a.shape[1])-a.shape[1]+1)/a.shape[1]**2
    return dict(p=pp,mean=mu,median=med,brier=(pp-dy)**2,crps=np.abs(a-y[:,None]).mean(axis=1)-a@co,
           log_loss=-np.log(np.clip(np.where(dy,pp,1-pp),.0005,1.)),correct=(pp>=.5)==dy,mae=np.abs(y-mu),
           se=(mu-y)**2,lo=lo,hi=hi,cover=(lo<=y)&(hi>=y),width=hi-lo)


def measured(x,b,mean,dist,shape_idx,fit_cut,last,active):
    scale=x['raw_daily_sigma']*np.sqrt(x['horizon'])
    center=np.clip(mean[:,0],-2.7,2.7)
    y=x['ret']
    p=scores(dist,center,scale,y)
    rv=np.exp(np.clip(mean[:,5],-1.5,1.5))*x['raw_daily_sigma']*np.sqrt(252)
    realized=x['realized_vol']
    rr=np.maximum(.0001,(realized/np.maximum(rv,.001))**2)
    range_=np.exp(np.clip(mean[:,6],-2,2))*scale
    valid=np.isfinite(y)
    p={k:np.where(valid,v,np.nan) for k,v in p.items()}
    res=dict(clock_ns=fit_cut,last_train_ns=last,active=active,law=shape_idx,center_normalized=center,horizon_scale=scale,
         realized=realized,rv_forecast=rv,rv_mae=np.abs(realized-rv),qlike=rr-np.log(rr)-1,range_forecast=range_,
         range_mae=np.abs(range_-x['future_range']),magnitude_forecast=np.maximum(0,mean[:,4])*scale,
         magnitude_mae=np.abs(np.maximum(0.,mean[:,4])*scale-np.abs(x['ret_log'])),
         global_forecast=scale*mean[:,1],regional_forecast=scale*mean[:,2],innovation_forecast=scale*mean[:,3],
         global_mae=np.abs(scale*mean[:,1]-x['global_log']),innovation_mae=np.abs(scale*mean[:,3]-x['innovation_log']),**p)
    for j,key in enumerate(TARGETS[7:],start=7):
        pr=np.clip(mean[:,j],.01,.99)
        res[key+'_p']=pr;res[key+'_brier']=(pr-x[key])**2
    return {k:x[k] for k in ('row','code','region','day','horizon','target_day','mature_ns','issue_ns','cohort','ret','normalized')}|dict(model=b,**res)


def counts_for_history(t,cut):
    if len(t)==0:
        return dict(n_rows=0,n_dates=0,n_markets=0,n_global_weeks=0,n_later_than_cut=0,last_mature=0)
    return dict(n_rows=len(t),n_dates=t.day.nunique(),n_markets=t.code.nunique(),
                n_global_weeks=pd.to_datetime(t.day).dt.to_period('W-SUN').nunique(),last_mature=int(t.mature_ns.max()),
                n_later_than_cut=int(t.mature_ns.ge(cut).sum()))


def foreign_fit(f,x,y,mask,fields,alt=None):
    local_y=y[mask] if alt is None else alt
    return train(x[mask],local_y,f['day'][mask],selected(fields))


def source_masks(f,q):
    code=f['code']
    return q&(code!='india'), code


def shared_models(f,x,y,away,k,h):
    rng=np.random.default_rng(SEED+100*h+k)
    day=f['day'][away]
    pooled=foreign_fit(f,x,y,away,FIELDS)
    fit={'pooled_with_context':(pooled,away),
         'country_shuffle':(foreign_fit(f,x,y,away,FIELDS,date_country_permute(y[away],day,rng)),away),
         'date_block_null':(foreign_fit(f,x,y,away,FIELDS,date_null(y[away],day,rng)),away)}
    keep=away&~np.isin(f['code'],('us','japan','germany'))
    fit['dominant_excluded']=(foreign_fit(f,x,y,keep,FIELDS),keep)
    coef=pooled.coefficient.copy()
    u,s,v=np.linalg.svd(coef[:,:4],full_matrices=False)
    coef[:,:4]=(u[:,:2]*s[:2])@v[:2]
    fit['low_rank_shared']=(Model(pooled.fields,pooled.center,pooled.scale,pooled.intercept,coef),away)
    if h in ORIGINAL:
        for name,group in MECHANISMS.items():
            fit['mechanism_'+name]=(foreign_fit(f,x,y,away,group),away)
    return fit


def target_block(features,h):
    z=csv('international-target-panel.csv.gz')
    z=z[z.horizon.eq(h)].merge(features,on=['row','code','day'],validate='one_to_one').sort_values('row')
    assert np.array_equal(z.row,np.arange(len(z)))
    return z


def run_horizon(features,h):
    z=target_block(features,h)
    f={c:z[c].to_numpy() for c in z}
    x=z[list(FIELDS)].to_numpy(float)
    y=target_array(h,z)
    recent=x.copy()
    for loc in z.groupby('code',sort=False).indices.values():
        recent[loc[:5]]=np.nan
        recent[loc[5:]]=x[loc[:-5]]
    block=(f['issue_ns']//DAY-20089)//10
    test=z.day.ge(START)&z.ret.notna()&z.raw_daily_sigma.notna()
    buffers={};fit_rows=[];coef_rows=[];shapes=[]
    regions=np.unique(f['region'])

    def predict(i,name,mean,dist,cut,mask,active=True):
        d=len(shapes)
        shapes.append(dist)
        o=measured({c:a[i] for c,a in f.items()},name,mean,dist,d,cut,int(f['mature_ns'][mask].max()),active)
        for key,b in o.items():
            buffers.setdefault(key,[]).append(np.broadcast_to(b,(len(i),)))

    def cert(k,cut,name,mask,s,country):
        q=z.loc[mask,['day','mature_ns','code']]
        fit_rows.append(dict(horizon=h,block=k,fit_cut_ns=cut,model=name,holdout=country,**counts_for_history(q,cut)))
        if s is not None and name in {'loco_transfer','local_own_only','loro_transfer',*('mechanism_'+n for n in MECHANISMS)}:
            for j,idx in enumerate(s.fields):
                coef_rows.append(dict(horizon=h,block=k,code=country,model=name,feature=FIELDS[idx],location=s.coefficient[j,0],
                        innovation=s.coefficient[j,3],magnitude=s.coefficient[j,4],volatility=s.coefficient[j,5],
                        expansion=s.coefficient[j,7],contraction=s.coefficient[j,8]))

    for k in np.unique(block[test]):
        cut=int((k*10+20089)*DAY)
        candidates=test&(block==k)&(f['issue_ns']>=cut)
        q=eligible(z,cut);away,code=source_masks(f,q)
        if away.sum()<160:
            continue
        pool=shared_models(f,x,y,away,k,h)
        for name,(m,s) in pool.items():
            cert(k,cut,name,s,m,'all foreign')
        regional={}
        for r in regions:
            r0='Asia Pacific' if r=='South Asia' else r
            mask=away&(f['region']!=r0)
            regional[r]=(foreign_fit(f,x,y,mask,OWN),mask,law(y[mask,0]))
        pool_shapes={name:law(y[s,0]) for name,(_,s) in pool.items()}
        for key in np.unique(code[candidates]):
            ii=np.where(candidates&(code==key))[0]
            loc=q&(code==key)&(f['issue_ns']>=cut-190*DAY)
            if loc.sum()<45:
                continue
            own=selected(OWN);own_x=x[ii];day=f['day'][loc]
            loco=away&(code!=key)
            lv=law(y[loc,0]);foreign_shape=law(y[loco,0])
            local=train(x[loc],y[loc],day,own)
            wide=train(x[loc],y[loc],day,selected(FIELDS))
            shared=foreign_fit(f,x,y,loco,OWN)
            region,rm,regional_shape=regional[f['region'][ii[0]]]
            partial=train(x[loc],y[loc],day,own,prior=shared)
            gl=train(x[loc],y[loc],day,selected(GLOBAL))
            innovations=pool['pooled_with_context'][0].predict(own_x)
            g=innovations.copy()
            gb=np.nan_to_num(f['market_beta'][ii],nan=1)
            rb=np.nan_to_num(f['regional_beta'][ii],nan=0)
            g[:,0]=gb*g[:,1]+rb*(g[:,2]-g[:,1])
            g2=g.copy();g2[:,0]+=.75*g[:,3]
            c=np.nanmean(y[loc],axis=0)
            c=np.nan_to_num(c,nan=.5)
            history=np.repeat(c[None,:],len(ii),axis=0)
            history[:,0]=np.nanmedian(y[loc,0])
            stay=history.copy();stay[:,0]=0.;stay[:,5:7]=0
            models={'local_history':(history,lv,loc,None),'local_persistence':(stay,lv,loc,None),
                    'local_own_only':(local.predict(own_x),lv,loc,local),'local_ridge':(wide.predict(own_x),lv,loc,wide),
                    'global_factor_only':(gl.predict(own_x),lv,loc,gl),
                    'loco_transfer':(shared.predict(own_x),foreign_shape,loco,shared),
                    'loro_transfer':(region.predict(own_x),regional_shape,rm,region),
                    'partial_country':(partial.predict(own_x),lv,loco|loc,partial),
                    'delayed_transfer':(shared.predict(recent[ii]),foreign_shape,loco,shared),
                    'factor_only':(g,foreign_shape,away,None),'factor_and_innovation':(g2,foreign_shape,away,None)}
            for name,(prediction,dist,eligible_rows,model) in models.items():
                predict(ii,name,prediction,dist,cut,eligible_rows)
                cert(k,cut,name,eligible_rows,model,key)
            for name,(mod,s) in pool.items():
                # Full-panel contextual results are distinct from strict country/region exclusion.
                predict(ii,name,mod.predict(own_x),pool_shapes[name],cut,s)
        if k%12==0:
            print('Horizon',h,'UTC cutoff',pd.to_datetime(cut,utc=True).date(),flush=True)

    table=pd.DataFrame({k:np.concatenate(v) for k,v in buffers.items()})
    assert (table.last_train_ns<table.clock_ns).all() and (table.clock_ns<=table.issue_ns).all()
    write(f'international-fit-receipts-{h}.csv',pd.DataFrame(fit_rows))
    table.to_csv(OUT/f'market-forecast-cases-{h}.csv.gz',index=False,
          compression={'method':'gzip','compresslevel':4},float_format='%.11g')
    np.savez_compressed(OUT/f'market-forecast-atoms-{h}.npz',s=np.array(shapes))
    print('Completed',h,'sessions',len(table),'forecast cases',flush=True)
    return table,pd.DataFrame(coef_rows)


def summarize(z):
    metrics=['brier','crps','log_loss','correct','mae','se','cover','width','rv_mae','qlike','range_mae','global_mae','innovation_mae',
             'magnitude_mae',*(k+'_brier' for k in TARGETS[7:])]
    a=z.copy()
    a['scope']=np.where(a.day.ge(LATER),'later','earlier')
    a['actual_up']=a.ret.gt(0).astype(int)
    a['pos_acc']=a.correct.where(a.actual_up==1)
    a['neg_acc']=a.correct.where(a.actual_up==0)
    m=metrics+['pos_acc','neg_acc','p','actual_up']
    rows=[]
    for scope,s in chain(a.groupby('scope'),[('all',a)]):
        t=s.groupby(['horizon','code','model'])[m].mean()
        t['n']=s.groupby(['horizon','code','model']).day.size()
        t['rank_corr']=s.groupby(['horizon','code','model'])[['p','ret']].apply(lambda q:q.p.corr(q.ret,method='spearman') if q.p.nunique()>1 else np.nan)
        t['rmse']=np.sqrt(t.pop('se'))
        t['balanced_accuracy']=.5*(t.pop('pos_acc')+t.pop('neg_acc'))
        t['scope']=scope
        rows.append(t.reset_index())
    return pd.concat(rows,ignore_index=True)


def run():
    feats=csv('international-feature-panel.csv.gz')
    summaries=[];coef=[];india=[]
    import sys
    hs=tuple(map(int,sys.argv[1:])) or HORIZONS
    for h in hs:
        if (OUT/f'market-forecast-cases-{h}.csv.gz').exists() and (OUT/f'international-coefficients-{h}.csv.gz').exists():
            z=csv(f'market-forecast-cases-{h}.csv.gz')
            co=csv(f'international-coefficients-{h}.csv.gz')
        else:
            z,co=run_horizon(feats,h)
            write(f'international-coefficients-{h}.csv.gz',co)
        summaries.append(summarize(z))
        coef.append(co)
        if h in ORIGINAL:
            india.append(z.loc[z.code.eq('india')&z.cohort.notna()])
    write('international-model-leaderboard.csv',pd.concat(summaries,ignore_index=True))
    write('international-coefficient-history.csv.gz',pd.concat(coef,ignore_index=True))
    if india:
        write('india-transfer-input-cases.csv.gz',pd.concat(india,ignore_index=True))


if __name__=='__main__':
    run()
