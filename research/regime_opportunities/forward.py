import numpy as np
import pandas as pd
from .framework import OUT,PERIODS,save

INDEX_PERIODS={'index_development':('2017-01-01','2021-01-01'),'index_validation':('2021-01-01','2023-01-01'),'index_transfer':('2023-01-01','2024-11-10'),'index_recent_diagnostic':('2024-11-10','2026-11-10'),'index_all':('2017-01-01','2026-11-10')}

def bh(p):
    p=np.asarray(p,float);order=np.argsort(p);result=np.empty(len(p));result[order]=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1];return np.minimum(result,1)

def events(mask,spacing=20):
    on=np.flatnonzero(mask)
    return [] if not len(on) else np.split(on,np.flatnonzero(np.diff(on)>spacing)+1)

def weights(n,block=20,draws=3000):
    rng=np.random.default_rng(74260112);result=np.zeros((draws,n),np.float32)
    starts=rng.integers(0,n,(draws,int(np.ceil(n/block))));ix=((starts[:,:,None]+np.arange(block))%n).reshape(draws,-1)[:,:n]
    for i,row in enumerate(ix):result[i]=np.bincount(row,minlength=n)
    return result

def analyze(y,maskmatrix,available,names,stage,domain,horizon,method,calendar):
    n=len(y)
    if n<10:return []
    w=weights(n,3 if method=='nonoverlap20grid' else 20);good=np.isfinite(y);on=maskmatrix&available&good[:,None];off=~maskmatrix&available&good[:,None]
    def calc(m):
        den=w@m.astype(float);num=w@(m*np.where(good,y,0)[:,None]);return np.divide(num,den,out=np.full_like(num,np.nan),where=den>0)
    dif=calc(on)-calc(off);rows=[]
    for j,name in enumerate(names):
        a=y[on[:,j]];b=y[off[:,j]];v=dif[:,j];v=v[np.isfinite(v)]
        point=a.mean()-b.mean() if len(a) and len(b) else np.nan
        # Count pooled episodes on original session spacing, not compressed grid.
        indices=calendar[on[:,j]];ne=0 if not len(indices) else 1+int(np.sum(np.diff(indices)>20))
        eligible=len(a)>=5 and len(b)>=5 and ne>=3
        p=(1+int((abs(v-point)>=abs(point)).sum()))/(1+len(v)) if eligible and len(v) else 1.
        rows.append(dict(domain=domain,stage=stage,horizon=horizon,method=method,regime=name,n_on=len(a),n_off=len(b),on_mean_pct=a.mean() if len(a) else None,off_mean_pct=b.mean() if len(b) else None,
          contrast_pct=point,ci95_low_pct=np.quantile(v,.025) if len(v) else None,ci95_high_pct=np.quantile(v,.975) if len(v) else None,p=p,pooled_on_events=ne,inference_eligible=eligible))
    return rows

def run(q,market,tri,states,definitions):
    names=list(states);labels=np.column_stack([states[x] for x in names]);values=pd.read_csv(OUT/'regime-features.csv',index_col=0)
    available=np.isfinite(values[names].to_numpy());dates=market.index;rows=[];freq=[]
    for stage,(start,end) in {**INDEX_PERIODS,**PERIODS}.items():
        use=(dates>=pd.Timestamp(start,tz=dates.tz))&(dates<pd.Timestamp(end,tz=dates.tz));idx=np.flatnonzero(use)
        for j,name in enumerate(names):
            m=labels[idx,j]&available[idx,j];starts=np.flatnonzero(m&~np.r_[False,m[:-1]]);ends=np.flatnonzero(m&~np.r_[m[1:],False]);lengths=ends-starts+1
            freq.append(dict(stage=stage,regime=name,available_sessions=int(available[idx,j].sum()),on_sessions=int(m.sum()),frequency_pct=100*m.sum()/available[idx,j].sum() if available[idx,j].sum() else None,
              contiguous_runs=len(starts),pooled_events=len(events(m)),median_run=np.median(lengths) if len(lengths) else None,max_run=int(max(lengths)) if len(lengths) else 0))
    pd.DataFrame(freq).to_csv(OUT/'regime-frequency-duration.csv',index=False)
    stock=q['p'];eligible=np.flatnonzero(stock['eligible']);sd=stock['dates'];sclose=stock['neutral']['close'][eligible];div=stock['dividend'][eligible]/stock['unit_factor'][eligible];cum=np.cumsum(div,axis=1)
    sidx=dates.get_indexer(sd);stockarrays={};sectorrows=[];stockrows=[]
    anchor=int(np.flatnonzero(dates>=pd.Timestamp('2017-01-01',tz=dates.tz))[0]);grid=(np.arange(len(dates))-anchor)%20==0
    source={x:tri[x].to_numpy() for x in ['Nifty 50','Nifty 500','Nifty Bank','Nifty IT','Nifty Pharma']}
    for h in [5,10,20]:
        target={}
        for name,x in source.items():
            z=np.full(len(x),np.nan);z[:-h]=100*(x[h:]/x[:-h]-1);target[name+'_TRI']=z
        sr=np.full_like(sclose,np.nan);sr[:,:-h]=100*((sclose[:,h:]+cum[:,h:]-cum[:,:-h])/sclose[:,:-h]-1);stockarrays[f'forward{h}']=sr
        mean=np.nanmean(sr,axis=0);fraction=np.nanmean(np.where(np.isfinite(sr),(sr>0).astype(float),np.nan),axis=0)*100
        for name,x in [('stock_mean',mean),('stock_positive_fraction',fraction),('stock_excess_N50',mean-target['Nifty 50_TRI'][sidx])]:
            z=np.full(len(dates),np.nan);z[sidx]=x;target[name]=z
        for domain,y in target.items():
            periods=PERIODS if domain.startswith('stock') else INDEX_PERIODS
            for stage,(start,end) in periods.items():
                use=(dates>=pd.Timestamp(start,tz=dates.tz))&(dates<pd.Timestamp(end,tz=dates.tz));future=np.r_[dates[h:].asi8,np.full(h,np.iinfo(np.int64).max)]
                use&=future<pd.Timestamp(end,tz=dates.tz).value
                for method,choose in [('all_dates_block20',use),('nonoverlap20grid',use&grid)]:
                    ix=np.flatnonzero(choose)
                    rows+=analyze(y[ix],labels[ix],available[ix],names,stage,domain,h,method,ix)
        # All cohort sectors: descriptive proxy groups, not certified sectorindices.
        if h==10:
            for stage,(start,end) in PERIODS.items():
                use=(sd>=pd.Timestamp(start,tz=sd.tz))&(sd<pd.Timestamp(end,tz=sd.tz));validend=np.arange(len(sd))+h<len(sd)
                validend&=sd[np.minimum(np.arange(len(sd))+h,len(sd)-1)]<pd.Timestamp(end,tz=sd.tz)
                for j,name in enumerate(names):
                    on=use&validend&labels[sidx,j]&available[sidx,j]
                    if not on.any():continue
                    for sector in sorted(set(stock['sector'])):
                        which=np.asarray([stock['sector'][s]==sector for s in eligible]);sectorrows.append(dict(stage=stage,regime=name,sector=sector,stocks=int(which.sum()),signal_dates=int(on.sum()),mean_forward10_pct=float(np.nanmean(sr[which][:,on])),basis='frozen_cohort_sector_proxy'))
                    for i,s in enumerate(eligible):stockrows.append(dict(stage=stage,regime=name,symbol=stock['symbols'][s],sector=stock['sector'][s],signal_dates=int(on.sum()),mean_forward10_pct=float(np.nanmean(sr[i,on]))))
        print('FORWARD_HORIZON',h,'complete',flush=True)
    a=pd.DataFrame(rows);a['bh_q']=np.nan
    for _,g in a.groupby(['stage','horizon','method']):a.loc[g.index,'bh_q']=bh(g.p)
    a.to_csv(OUT/'forward-regime-contrasts.csv',index=False);pd.DataFrame(sectorrows).to_csv(OUT/'cohort-sector-forward.csv',index=False);pd.DataFrame(stockrows).to_csv(OUT/'individual-stock-forward.csv',index=False)
    np.savez_compressed(OUT/'stock-forward-arrays.npz',**stockarrays,stock_indices=eligible)
    # Regime selection reads development stockopportunity outcomes only, not portfolioresults.
    train=a[(a.stage=='development')&(a.domain=='stock_excess_N50')&(a.horizon==10)&a.method.eq('all_dates_block20')]
    candidates=train[(train.n_on>=20)&(train.pooled_on_events>=3)&(train.contrast_pct>0)].sort_values('contrast_pct',ascending=False).head(3)
    save('training-regime-shortlist.json',dict(regimes=candidates.regime.tolist(),rows=candidates.to_dict('records'),selection='Development stock10session excessreturn contrast, >=20on-dates and>=3pooledevents. Noentrystyleorvalidation/finalresultsused. Existingcalendarcontaminationremains.'))
    print('FORWARD_COMPLETE',len(a),flush=True)
