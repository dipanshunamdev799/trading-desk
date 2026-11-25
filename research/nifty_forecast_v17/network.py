"""Separate a quoted basis and same-bar co-movement from a later cash/sector move."""
from .common import *
from .panel import PX,RV,NATIVE
from .stocks import bar_inventory,read_bars
from .gift import score
from research.nifty_forecast_v15.sessions import candles
from research.nifty_forecast_v16.model import fit

CLOCKS=('09:25','09:55','10:20','12:30')
DRIVERS={
    'bank_relative':('bank_own_last5','finance_own_last5','bank_above','bank_cross_dispersion'),
    'finance_relative':('bank_own_last5','finance_own_last5','financial_lead','finance_own_relvol'),
    'it_relative':('it_own_last5','it_own_last15','it_cross_dispersion','it_above'),
    'nifty_later':('bank_own_last5','finance_own_last5','it_own_last5','heavy_vs_broad','native_sync','own_sector_last5'),
    'nifty_range':('bank_own_last5','stock_sync','native_sync','own_sector_dispersion','liquidity_acceleration'),
    'nifty_volatility':('bank_own_last5','stock_sync','native_sync','own_sector_dispersion','liquidity_acceleration'),
    'nifty_cash_leg':('nifty_etf_tracking','etf_tracking_vs_past','etf_volume','etf_vwap'),
    'nifty_etf_leg':('nifty_etf_tracking','etf_tracking_vs_past','etf_volume','etf_vwap'),
    'nifty_basis_leg':('nifty_etf_tracking','etf_tracking_vs_past','etf_volume','etf_vwap'),
    'bank_index_leg':('bank_etf_tracking','bank_tracking_vs_past','bank_etf_volume','bank_etf_vwap'),
    'bank_etf_leg':('bank_etf_tracking','bank_tracking_vs_past','bank_etf_volume','bank_etf_vwap'),
    'bank_basis_leg':('bank_etf_tracking','bank_tracking_vs_past','bank_etf_volume','bank_etf_vwap'),
}


def interval(b,start,end):
    part=b[(b.index>=start)&(b.end<=end)]
    if part.empty or part.index[0]!=start or part.end.iloc[-1]!=end:
        return np.nan
    if len(part)>1 and not np.array_equal(part.end.iloc[:-1].to_numpy(),part.index[1:].to_numpy()):
        return np.nan
    return float(np.log(part.close.iloc[-1]/part.open.iloc[0]))


def combined(inventory,tag):
    x=read_bars(inventory[tag])
    if x.empty:
        return {}
    x['end']=x.ts+pd.to_timedelta(x.resolution,unit='m')
    return {d:f.set_index('ts').sort_index() for d,f in x.groupby('day')}


def segments(f,y):
    book=bar_inventory()
    native={k:combined(book,k) for k in ('bank','finance','it','NIFTYBEES','BANKBEES')}
    cash,_,_=candles((V13/'sources/upstox').glob('nifty-5m-*'),5)
    keys=list(DRIVERS)
    observations=[]
    for z in f.itertuples(index=False):
        d=z.day;dt=pd.Timestamp(z.decision);here=cash.get(d)
        if here is None:
            continue
        r={k:np.nan for k in keys}
        intervals={}
        for key in ('bank','finance','it'):
            a=native[key].get(d)
            if a is None:
                continue
            g=a[(a.index>=dt)&(a.end<=dt+pd.Timedelta(minutes=60))]
            if g.empty:
                continue
            start=g.index[0];end=start+pd.Timedelta(minutes=25)
            own=interval(a,start,end)
            there=interval(here,start,end)
            r[key+'_relative']=own-there
            intervals[key]=(start,end,own)
            r[key+'_return_start']=start.isoformat();r[key+'_return_end']=end.isoformat()
        for nm,tag,base in [('nifty','NIFTYBEES','cash'),('bank','BANKBEES','index')]:
            e=native[tag].get(d)
            if e is None or (nm=='bank' and 'bank' not in intervals):
                continue
            if nm=='bank':
                start,end,original=intervals['bank']
            else:
                start,end=dt,dt+pd.Timedelta(minutes=30)
                original=interval(here,start,end)
            other=interval(e,start,end)
            if np.isfinite([original,other]).all():
                r[nm+'_'+base+'_leg']=original
                r[nm+'_etf_leg']=other
                r[nm+'_basis_leg']=other-original
                r[nm+'_basis_return_end']=end.isoformat()
        k=y.loc[(d,z.cutoff)]
        r.update(day=d,cutoff=z.cutoff,feature_last_bar=z.feature_last_bar,
                 nifty_later=k.r30,nifty_range=k.remaining_range,nifty_volatility=k.remaining_vol)
        observations.append(r)
    return pd.DataFrame(observations)


def run():
    f=pd.read_csv(OUT/'intraday-feature-panel.csv.gz',low_memory=False)
    f=f[f.cutoff.isin(CLOCKS)].copy()
    y=pd.read_csv(OUT/'intraday-target-panel.csv.gz').set_index(['day','cutoff'])
    s=segments(f,y)
    write('network-observed-segments.csv.gz',s)
    f=f.merge(s.drop(columns=['feature_last_bar']),on=['day','cutoff'],validate='1:1')
    scores=[];associations=[];fits=[];laws=[]
    for clock,g in f.groupby('cutoff'):
        g=g.sort_values('day').reset_index(drop=True)
        base=g.reindex(columns=PX+RV+NATIVE).to_numpy(float)
        for k,fields in DRIVERS.items():
            response=g[k].to_numpy(float)
            driver=g.reindex(columns=fields).to_numpy(float)
            past=g.reindex(columns=fields).shift(1).to_numpy(float)
            # Dynamic factor residuals are generated before each respective day's outcome.
            innov=np.full_like(driver,np.nan)
            residual=np.full(len(g),np.nan)
            scale=np.full(len(g),np.nan)
            for i in range(32,len(g)):
                t=np.arange(max(0,i-100),i)
                enough=np.isfinite(driver[t]).sum(0)>=18
                if enough.any():
                    x=driver[t][:,enough]
                    med=np.nanmedian(x,axis=0)
                    nfit=fit(base[t],np.where(np.isfinite(x),x,med),100.)
                    innov[i,enough]=driver[i,enough]-nfit.values(base[i])
                m=t[np.isfinite(response[t])]
                if len(m)>=32:
                    baseline=fit(base[m],response[m],135.)
                    lm=float(.65*baseline.values(base[i])+.35*np.median(response[m]))
                    scale[i]=lm
                    residual[i]=response[i]-lm
            for j,field in enumerate(fields):
                a=pd.DataFrame({'x':driver[:,j],'prev':past[:,j],'lag':innov[:,j],'y':response,'e':residual})
                corr=lambda x,y: float(a[x].corr(a[y])) if a[[x,y]].dropna()[x].nunique()>1 else np.nan
                associations.append(dict(cutoff=clock,target=k,source=field,aligned=int(a[['x','y']].dropna().shape[0]),
                     lead_r=corr('x','y'),one_day_old_r=corr('prev','y'),partial_r=corr('lag','e'),partial_n=int(a[['lag','e']].dropna().shape[0])))
            both=np.column_stack((driver,past))
            design=np.column_stack((base,both))
            v=np.column_stack((innov,pd.DataFrame(innov).shift(1)))
            for i in range(80,len(g)):
                if not np.isfinite(response[i]) or not np.isfinite(driver[i,0]) or not np.isfinite(scale[i]):
                    continue
                t=np.flatnonzero(np.isfinite(residual[:i])&np.isfinite(driver[:i,0]))[-110:]
                if len(t)<38:
                    continue
                y0=response[t];e0=residual[t]
                parent=scale[i]+np.quantile(e0-np.median(e0),Q)
                direct=fit(design[t],y0,180.)
                res=fit(v[t],e0,150.)
                old=fit(past[t],e0,150.)
                signal=[]
                for j in range(v.shape[1]):
                    match=np.isfinite(v[t,j]);x=v[t,j][match]
                    signal.append(abs(np.corrcoef(x,e0[match])[0,1]) if match.sum()>=25 and x.std()>1e-10 and e0[match].std()>1e-10 else -1.)
                active=np.argsort(signal,kind='stable')[-2:]
                sparse=fit(v[t][:,active],e0,120.)
                center=.65*direct.values(np.r_[base[i],both[i]])+.35*np.median(y0)
                for tag,law in {'own_state':parent,'distributed_ridge':parent+(center-scale[i]),
                      'factor_residual':parent+.55*res.values(v[i]),'sparse_residual':parent+.55*sparse.values(v[i,active]),
                      'old_input':parent+.55*old.values(past[i])}.items():
                    is_risk=k in ('nifty_range','nifty_volatility')
                    a=np.maximum(law,1e-7) if is_risk else law
                    out=score(a,response[i],arithmetic=not is_risk)
                    if is_risk:
                        out.update(p=np.nan,brier=np.nan,log_loss=np.nan,correct=np.nan)
                    ix=len(laws);laws.append(np.asarray(a,'float32'))
                    scores.append(dict(law=ix,day=g.day.iloc[i],origin=g.day.iloc[i],target_end=g.day.iloc[i],cohort=y.loc[(g.day.iloc[i],clock),'cohort'],
                        cutoff=clock,target=k,model=tag,last_mature=g.day.iloc[t[-1]],baseline='own_state',**out))
                fits.append(dict(day=g.day.iloc[i],cutoff=clock,target=k,trained=len(t),last_mature=g.day.iloc[t[-1]],
                                 sparse_columns=active.tolist(),direct=direct.receipt(tuple(PX+RV+NATIVE+fields+tuple('prev_'+x for x in fields))),
                                 factor=res.receipt(tuple(fields+tuple('prev_'+x for x in fields)))))
    d=pd.DataFrame(scores)
    assert d.last_mature.lt(d.day).all()
    write('network-scores.csv.gz',d)
    write('network-correlations.csv',pd.DataFrame(associations))
    save('network-fits.json',fits)
    np.savez_compressed(OUT/'network-laws.npz',atoms=np.stack(laws))
    print('Matched later network forecasts',len(d),flush=True)


if __name__=='__main__':
    run()
