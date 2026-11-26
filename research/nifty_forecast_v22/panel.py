"""Build comparable local-session tasks with exact UTC label maturity."""
from itertools import combinations

from .common import *
from .sources import BY_CODE,FX

FIELDS=('shock','mom3','mom5','mom10','mom21','vol_level','vol_ratio','drawdown','trend_efficiency','down_share',
        'global1','global5','regional1','regional5','relative5','cross_dispersion','synchronization','fx5','global_vix',
        'tech_lead','global_finance','oil5','rates5','local_breadth','local_sector','pc_global','local_innovation5')
STATE=('mom3','mom5','mom21','vol_level','vol_ratio','drawdown','trend_efficiency','relative5','cross_dispersion',
       'synchronization','global_vix','global5','local_innovation5')
LOCAL=('shock','mom3','mom5','mom10','mom21','vol_level','vol_ratio','drawdown','trend_efficiency','down_share',
       'fx5','local_breadth','local_sector','local_innovation5')
GLOBAL=('global1','global5','regional1','regional5','cross_dispersion','synchronization','global_vix','tech_lead','global_finance',
        'oil5','rates5','pc_global')
MECHANISMS={
 'momentum_reversal':('shock','mom3','mom5','mom10','mom21','trend_efficiency'),
 'drawdown_recovery':('drawdown','mom3','mom21','trend_efficiency'),
 'volatility_clustering':('vol_level','vol_ratio','down_share','global_vix'),
 'synchronization_relative':('relative5','local_innovation5','global5','regional5','cross_dispersion','synchronization'),
 'breadth_leadership':('local_breadth','local_sector','tech_lead','global_finance'),
}


def logs(row):
    return np.log(row.groupby('code').close.transform(lambda x:x/x.shift(1)))


def earlier_book(z,field):
    d=z.loc[z[field].notna()&z.available.notna(),['available',field]].sort_values('available')
    t=utc_int(d.available) if len(d) else np.empty(0,np.int64)
    return t,d[field].to_numpy(float)


def asof(book,key,tim,age=7):
    if key not in book:
        return np.full(len(tim),np.nan)
    when,value=book[key]
    if len(when)==0:
        return np.full(len(tim),np.nan)
    loc=np.searchsorted(when,tim,side='right')-1
    j=loc.clip(0)
    ok=(loc>=0)&(tim-when[j]<=age*86400_000_000_000)
    return np.where(ok,value[j],np.nan)


def average(vals,axis=1):
    obs=np.isfinite(vals)
    return np.divide(np.nansum(vals,axis=axis),obs.sum(axis=axis),out=np.full(np.nansum(vals,axis=axis).shape,np.nan),where=obs.sum(axis=axis)>0)


def pca_book(tape,primary):
    x=tape[tape.code.isin(primary)&tape.code.ne('india')].pivot(index='day',columns='code',values='r1')
    x=x.reindex(columns=[k for k in primary if k!='india'])
    days=pd.date_range(FIRST,FREEZE,freq='D').strftime('%Y-%m-%d')
    x=x.reindex(days)
    beta=np.full(x.shape,np.nan)
    rows=[]
    for i in range(98,len(days)):
        # Leave two UTC dates for completion of all exchanges and the publication guard.
        d=x.iloc[max(0,i-160):i-2].to_numpy(float)
        take=np.isfinite(d).sum(axis=1)>=max(5,int(.70*len(x.columns)))
        a=d[take]
        if len(a)<53:
            continue
        med=np.nanmedian(a,axis=0);sd=np.nanstd(a,axis=0).clip(.002)
        b=np.where(np.isfinite(a),(a-med)/sd,0.)
        _,s,v=np.linalg.svd(b,full_matrices=False)
        w=v[0]*np.sign(v[0].sum())
        beta[i]=w/np.sum(np.abs(w))
        rows.append(dict(utc_day=days[i],last_included_utc_day=days[i-3],paired_days=len(a),first_pc_variance_share=float(s[0]**2/np.sum(s*s)),countries=len(w)))
    write('global-pca-receipts.csv',pd.DataFrame(rows))
    w=pd.DataFrame(beta,index=days,columns=x.columns)
    coeff=w.dropna().rename_axis('utc_day').reset_index()
    write('global-pca-loadings.csv',coeff)
    return w


def region_peers(key,allowed):
    r=BY_CODE[key].region
    r='Asia Pacific' if r=='South Asia' else r
    return [c for c in allowed if BY_CODE[c].region==r]


def signals(tape,primary,cut,time,key,pc):
    group=tape['books']
    peers=[x for x in primary if x not in {key,'india'}]
    reg=region_peers(key,peers)
    a=np.column_stack([asof(group['r1'],c,time) for c in peers]);b=np.column_stack([asof(group['r5'],c,time) for c in peers])
    spreads=np.column_stack([asof(group['z1'],c,time) for c in peers])
    if not reg:
        reg=peers
    rr=[peers.index(c) for c in reg]
    # The denominator is one market per country or jurisdiction. Sector ETFs enter only as context.
    equity=average(b)
    fxkey='fx_'+BY_CODE[key].currency.lower()
    tech=asof(group['r5'],'ndx',time)-asof(group['r5'],'us',time)
    fin=asof(group['r5'],'us_finance',time)-asof(group['r5'],'us',time)
    weights=pc.reindex(pd.to_datetime(cut,utc=True).dt.strftime('%Y-%m-%d'))[peers].to_numpy(float)
    m=np.isfinite(spreads)&np.isfinite(weights)
    val=np.where(m,spreads*weights,0.).sum(axis=1)
    v=np.where(m,np.abs(weights),0.).sum(axis=1)
    val=np.divide(val,v,out=np.full(len(v),np.nan),where=v>0)
    return dict(global1=average(a),global5=equity,regional1=average(a[:,rr]),regional5=average(b[:,rr]),
                cross_dispersion=np.nanstd(spreads,axis=1),synchronization=np.abs(average(np.sign(a))),
                fx5=asof(group['r5'],fxkey,time),global_vix=asof(group['log_close'],'vix',time),
                tech_lead=tech,global_finance=fin,oil5=asof(group['r5'],'brent',time),rates5=asof(group['rate5'],'us10y',time),
                pc_global=val,foreign_available=np.isfinite(a).sum(axis=1))


def caps(a,n):
    return pd.Series(a).rolling(n,min_periods=n).sum().to_numpy()


def reported_factors(books,primary,key,reference,settled):
    peers=[p for p in primary if p not in (key,'india')]
    rg=region_peers(key,peers) or peers
    book=books['log_close']
    y=np.column_stack([asof(book,k,settled)-asof(book,k,reference) for k in peers])
    return average(y),average(y[:,[peers.index(k) for k in rg]])


def factor_fit(y,glob,regional,end,decision):
    p=np.zeros((len(y),2))+[1.,0.];p[:35]=np.nan
    sizes=np.zeros(len(y),int)
    for i in range(35,len(y)):
        mask=(np.arange(len(y))<i)&(end<decision[i])&np.isfinite(y)&np.isfinite(glob)&np.isfinite(regional)
        t=np.flatnonzero(mask)[-116:]
        if len(t)<34:
            continue
        x=np.column_stack([glob[t],regional[t]-glob[t]])
        a=x-x.mean(axis=0)
        y0=y[t]-y[t].mean()
        ridge=.12*np.mean(np.sum(a*a,axis=0))+1.e-6
        b=np.linalg.solve(a.T@a+ridge*np.eye(2),a.T@y0+ridge*np.array([1.,0.]))
        p[i]=np.clip(b,[-.55,-1.5],[2.6,1.5]);sizes[i]=len(t)
    return p,sizes


def windows(z,hh):
    n=len(z);r=pd.to_numeric(z.close).to_numpy(float)
    obs=np.column_stack([z[k].to_numpy(float) for k in ('open','high','low','close')]);obs[~z.ohlc_valid,:]=np.nan
    empty=np.full((n,hh,4),np.nan)
    h=np.arange(hh)
    ok=np.arange(1,n-hh+1)
    empty[ok]=np.log(obs[ok[:,None]+h]/r[ok-1,None,None])
    return empty


def market_tasks(z,books,primary,pc,india_refs):
    k=z.code.iloc[0];dt=z.day.to_numpy(dtype='U10');c=np.log(z.close.to_numpy(float));n=len(z)
    issue=utc_int(z.issue);avail=utc_int(z.available);ref=np.r_[np.iinfo('int64').min,avail[:-1]]
    rl=np.r_[np.nan,np.diff(c)];yesterday=np.r_[np.nan,rl[:-1]]
    vol=np.sqrt(pd.Series(yesterday*yesterday).rolling(21,min_periods=16).mean().to_numpy(float)).clip(.002,.13)
    v5=np.sqrt(pd.Series(yesterday*yesterday).rolling(5,min_periods=4).mean().to_numpy(float));down=pd.Series(np.square(np.minimum(yesterday,0.))).rolling(21,min_periods=16).mean().to_numpy()
    c0=np.r_[np.nan,c[:-1]]
    high=pd.Series(c0).rolling(21,min_periods=16).max().to_numpy(float)
    glob,reg=reported_factors(books,primary,k,ref,avail)
    b,counts=factor_fit(rl,glob,reg,avail,issue)
    error=rl-b[:,0]*glob-b[:,1]*(reg-glob)
    sequential=np.r_[np.nan,error[:-1]]
    f=dict(shock=yesterday/vol,vol_level=np.log(vol*np.sqrt(252)),vol_ratio=np.log(np.maximum(.002,v5)/vol),
           drawdown=(c0-high)/np.maximum(.009,vol*np.sqrt(21)),down_share=down/(vol*vol),
           trend_efficiency=caps(yesterday,10)/np.maximum(.001,caps(np.abs(yesterday),10)),
           local_innovation5=caps(sequential,5)/(vol*np.sqrt(5)))
    for h in (3,5,10,21):
        f[f'mom{h}']=caps(yesterday,h)/(vol*np.sqrt(h))
    f.update(signals(dict(books=books),primary,z.issue,issue,k,pc))
    f['relative5']=f['mom5']-f['global5']/(vol*np.sqrt(5))
    f['local_breadth']=np.full(n,np.nan);f['local_sector']=np.full(n,np.nan)
    realized_breadth=np.full(n,np.nan)
    following_vol=np.r_[vol[1:],vol[-1]]
    if k=='india':
        d=cash().reindex(dt)
        def index_ret(name):
            return np.log(d[name]/d[name].shift(5)).shift().to_numpy(float)
        f['local_breadth']=(index_ret('nifty500equalweight')-index_ret('nifty500'))/(vol*np.sqrt(5))
        f['local_sector']=(index_ret('niftybank')-index_ret('nifty50'))/(vol*np.sqrt(5))
        xp=np.log(d.nifty500equalweight).diff(5)-np.log(d.nifty500).diff(5)
        realized_breadth=xp.to_numpy(float)/(following_vol*np.sqrt(5))
    else:
        buddy={'us':('us_equal','us_finance'),'uk':('uk_mid',None),'china':('china300',None),'japan':('topix_etf',None),'australia':(None,'aus_finance')}.get(k,(None,None))
        for key,side in zip(('local_breadth','local_sector'),buddy):
            if side:
                f[key]=(asof(books['r5'],side,issue)-caps(yesterday,5))/(vol*np.sqrt(5))
        if buddy[0]:
            realized_breadth=(asof(books['r5'],buddy[0],avail)-caps(rl,5))/(following_vol*np.sqrt(5))
    x=pd.DataFrame(f).assign(code=k,region=BY_CODE[k].region,day=dt,issue=z.issue.to_numpy(),issue_ns=issue,
             last_local_available_ns=ref,raw_daily_sigma=vol,reference=np.exp(c0),market_beta=b[:,0],regional_beta=b[:,1],
             paired_exposure_days=counts,observed_daily_return=rl,global_realized_daily=glob,regional_realized_daily=reg,
             realized_local_innovation=error)
    hi=windows(z,max(HORIZONS))
    # Ending windows shorter than 21 remain valid near the frozen boundary.
    panels=[];path_arrays={}
    for h in HORIZONS:
        q=hi[:,:h].copy() if h==21 else windows(z,h)
        s=np.full(n,np.nan);te=np.full(n,'',dtype='U10');mature=np.full(n,np.iinfo('int64').max,np.int64)
        i=np.arange(1,n-h+1);j=i+h-1
        s[i]=(c[j]-c0[i]);te[i]=dt[j];mature[i]=avail[j]
        cumq=reported_factors(books,primary,k,ref[i],mature[i]);g=np.full(n,np.nan);rr=g.copy()
        g[i],rr[i]=cumq
        residual=s-b[:,0]*g-b[:,1]*(rr-g)
        diff=np.diff(np.concatenate([np.zeros((n,1)),q[:,:,3]],axis=1),axis=1)
        rv=np.sqrt(np.mean(diff*diff,axis=1)*252)
        spread=np.max(np.exp(q[:,:,1]),axis=1)-np.min(np.exp(q[:,:,2]),axis=1)
        path=np.concatenate([np.zeros((n,1)),q[:,:,3]],axis=1)
        dd=np.max(1-np.exp(path-np.maximum.accumulate(path,axis=1)),axis=1)
        scale=vol*np.sqrt(h)
        cr=BY_CODE[k].currency
        fx='fx_'+cr.lower()
        usd=s.copy()
        if cr!='USD':
            usd=np.full_like(s,np.nan)
            usd[i]=s[i]+asof(books['log_close'],fx,mature[i])-asof(books['log_close'],fx,issue[i])
        breadth=f['local_breadth'];after_breadth=np.full(n,np.nan);after_breadth[i]=realized_breadth[j]
        phase=dict(horizon=h,target_day=te,mature_ns=mature,ret_log=s,ret=np.expm1(s),normalized=s/scale,
             absolute=np.abs(s)/scale,realized_vol=rv,expansion=np.where(np.isfinite(rv)&np.isfinite(vol),(rv>1.25*vol*np.sqrt(252)),np.nan),
             contraction=np.where(np.isfinite(rv)&np.isfinite(vol),(rv<.80*vol*np.sqrt(252)),np.nan),
             future_range=spread,modeled_dd=dd,global_log=g,regional_log=rr,innovation_log=residual,usd_log=usd,
             reversal=np.where(np.isfinite(s)&(np.abs(f['mom5'])>=.35),np.sign(s)!=np.sign(f['mom5']),np.nan),
             recovery=np.where(np.isfinite(s)&(f['drawdown']<-.55),(s>=.50*scale),np.nan),
             divergence=np.where(np.isfinite(residual)&(f['synchronization']>.55),np.abs(residual)>.8*scale,np.nan),
             breadth_deterioration=np.where(np.isfinite(breadth)&np.isfinite(after_breadth),after_breadth<breadth-.60,np.nan))
        co=np.full(n,'',dtype='U7')
        if k=='india' and h in ORIGINAL:
            orig=india_refs.reindex(dt)
            co=orig[f'cohort_{h}'].fillna('').to_numpy(dtype='U7');ok=co!=''
            assert (te[ok]==orig[f'end_0_{h}'].to_numpy()[ok]).all()
            np.testing.assert_allclose(s[ok],orig[f'return_0_{h}'].to_numpy(float)[ok],rtol=0,atol=2.e-10)
        panels.append(pd.DataFrame(phase).assign(code=k,day=dt,cohort=co))
        path_arrays[h]=q.astype(np.float32)
    return x,pd.concat(panels,ignore_index=True),path_arrays


def dependence(tape,primary):
    d=tape[tape.code.isin(primary)].pivot(index='day',columns='code',values='r1').reindex(columns=primary)
    for h in (1,*ORIGINAL):
        if h==1:
            s=d
        else:
            # Market-session cumulative returns are joined by ending local day for descriptive dependence only.
            temp=tape[tape.code.isin(primary)].copy()
            temp['rh']=temp.groupby('code').r1.transform(lambda x:x.rolling(h,min_periods=h).sum())
            s=temp.pivot(index='day',columns='code',values='rh').reindex(columns=primary)
        r=s.corr(min_periods=45)
        vals=r.to_numpy(float);e=np.linalg.eigvalsh(np.nan_to_num(vals,nan=0.))
        row=dict(horizon=h,markets=len(primary),distinct_dates=int(s.notna().any(axis=1).sum()),global_week_episodes=int(pd.to_datetime(s.index[s.notna().any(axis=1)]).to_period('W-SUN').nunique()),
                 observed_returns=int(s.notna().sum().sum()),effective_rank=float(e.sum()**2/np.sum(e*e)),first_eigen_share=float(e[-1]/e.sum()),
                 mean_pair_corr=float(np.nanmean(vals[np.triu_indices(len(vals),1)])))
        write(f'international-return-correlations-{h}.csv',r.rename_axis('code').reset_index())
        yield row


def run():
    z=csv('international-daily-book.csv.gz')
    ids=csv('market-universe-audit.csv')
    p=ids.loc[ids.primary_eligible,'code'].tolist()
    assert p[0]=='india' and len(p)>=8
    z=z.sort_values(['code','day']).reset_index(drop=True)
    for code,(ticker,m) in FX.items():
        if m==-1:
            z.loc[z.code.eq('fx_'+code.lower()),'close']=1./z.loc[z.code.eq('fx_'+code.lower()),'close']
    z['log_close']=np.log(z.close)
    z['r1']=z.groupby('code').log_close.diff()
    z['r5']=z.groupby('code').log_close.diff(5)
    z['rate5']=z.groupby('code').close.diff(5)
    sd=z.groupby('code').r1.transform(lambda x:x.shift().rolling(21,min_periods=16).std())
    z['z1']=(z.r1/sd.clip(.002)).clip(-7,7)
    books={f:{k:earlier_book(a,f) for k,a in z.groupby('code',sort=False)} for f in ('r1','r5','rate5','z1','log_close')}
    pc=pca_book(z,p)
    prior=csv('multi-horizon-targets.csv',V20).set_index('day')
    rows=[];targets=[];paths={h:[] for h in HORIZONS};offset=0
    for k in p:
        d=z[z.code.eq(k)].reset_index(drop=True)
        a,b,c=market_tasks(d,books,p,pc,prior)
        a['row']=offset+np.arange(len(a));b['row']=np.tile(a.row,len(HORIZONS))
        offset+=len(a)
        rows.append(a);targets.append(b)
        for h in HORIZONS:
            paths[h].append(c[h])
    a=pd.concat(rows,ignore_index=True);b=pd.concat(targets,ignore_index=True)
    write('international-feature-panel.csv.gz',a)
    write('international-target-panel.csv.gz',b)
    np.savez_compressed(OUT/'local-observed-paths.npz',**{f'path_{h}':np.concatenate(paths[h]) for h in HORIZONS})
    write('international-dependence.csv',pd.DataFrame(dependence(z,p)))
    coverage=b.groupby(['code','horizon'],as_index=False).agg(rows=('row','size'),return_rows=('ret','count'),
          volatility_rows=('realized_vol','count'),ohlc_range_rows=('future_range','count'),global_rows=('global_log','count'),
          residual_rows=('innovation_log','count'),usd_rows=('usd_log','count'),reversal_rows=('reversal','count'),
          expansion_rows=('expansion','count'),breadth_rows=('breadth_deterioration','count'))
    write('local-task-coverage.csv',coverage)
    cols=['code','day','issue','last_local_available_ns','issue_ns','foreign_available','paired_exposure_days']
    write('market-issue-clock-receipts.csv.gz',a[cols])
    save('feature-definitions.json',dict(fields=FIELDS,local=LOCAL,global_fields=GLOBAL,mechanisms=MECHANISMS,state=STATE,
         scale='Earlier 21 local close-return root mean square × square root of horizon. Up to 21 matured bars with minimum 16 to construct the state.',
         horizons=HORIZONS,paths='Anchor prior official close. All future local O/H/L/C log-relative marks retained with missingness. Risk/range/tail are not direction.',
         global_components='One broad price index per market. Leave India and the current market out. Compare available log-price movement over local UTC label interval, used as subsequent targets only.',
         country_exposure='Last 116 paired daily local and foreign observations admitted strictly before local decision. Shrunk global and regional-relative coefficients.',
         usdfx='Separately mapped USD-per-local conversion using last eligible FX levels. Conservative UTC end-of-day plus 12 hours. Never replaces primary local price labels.',
         gaps='Expected local exchange days remain in the series. An unknown open-session price prevents OHLC-path targets from jumping that gap.',
         models='The statistical state excludes India mechanically and uses only earlier globally settled dates. Date-cluster rank is a descriptive dependence diagnostic.'))
    print('Built',len(a),'timestamped market origins;',len(b),'horizon tasks across',len(p),'markets',flush=True)


if __name__=='__main__':
    run()
