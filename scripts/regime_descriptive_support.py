from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.regime_opportunities.framework import OUT,PERIODS,save
from research.regime_opportunities.forward import INDEX_PERIODS,events
from research.ema_validation.engine import prepare,cache_correlations,orders
from research.regime_opportunities.engine import simulate

def main():
    labels=pd.read_csv(OUT/'regime-labels.csv',index_col=0);features=pd.read_csv(OUT/'regime-features.csv',index_col=0);dates=pd.DatetimeIndex(pd.to_datetime(labels.index,utc=True)).tz_convert('Asia/Kolkata');rows=[]
    for stage,(start,end) in {**INDEX_PERIODS,**PERIODS}.items():
        ix=np.flatnonzero((dates>=pd.Timestamp(start,tz=dates.tz))&(dates<pd.Timestamp(end,tz=dates.tz)))
        for name in labels:
            mask=labels[name].to_numpy()[ix]&np.isfinite(features[name].to_numpy()[ix])
            for i,g in enumerate(events(mask)):
                rows.append(dict(stage=stage,regime=name,event=i,start=str(dates[ix[g[0]]].date()),end=str(dates[ix[g[-1]]].date()),on_sessions=len(g),calendar_sessions=int(g[-1]-g[0]+1)))
    pd.DataFrame(rows).to_csv(OUT/'regime-pooled-events.csv',index=False)
    q=prepare();cache_correlations(q)
    with np.load(OUT/'portfolio-inputs.npz') as a:q['ranks']=list(a['ranks']);pool=a['entry_buyhold10'].copy()
    rows=[]
    for stage,(start,end) in PERIODS.items():
        mask=np.zeros_like(pool);i=np.flatnonzero(q['p']['dates']>=pd.Timestamp(start,tz=q['p']['dates'].tz))[0];mask[:,i]=pool[:,i]
        a=simulate(q,orders(q,mask),start,end,hold_only=True,hold_sessions=10**9)
        rows.append(dict(stage=stage,style='full_segment_buyhold',**a['metrics']));np.savez_compressed(OUT/f'full-buyhold-{stage}.npz',**{k:a[k] for k in ['equity','cash','utilization','positions','trades','cols']})
    pd.DataFrame(rows).to_csv(OUT/'funded-buyhold.csv',index=False)
    # Retain primary grids that lack enoughnonoverlappingdates for inference.
    sd=q['p']['dates'];ix=dates.get_indexer(sd);anchor=np.flatnonzero(dates>=pd.Timestamp('2017-01-01',tz=dates.tz))[0];grid=(ix-anchor)%20==0
    with np.load(OUT/'stock-forward-arrays.npz') as a:mean=np.nanmean(a['forward10'],axis=0)
    tri=pd.read_csv(OUT/'official-TRI.csv',index_col=0);nifty=tri['Nifty 50'].to_numpy();fwd=np.full(len(nifty),np.nan);fwd[:-10]=100*(nifty[10:]/nifty[:-10]-1);missing=[]
    for stage,(start,end) in PERIODS.items():
        use=(sd>=pd.Timestamp(start,tz=sd.tz))&(sd<pd.Timestamp(end,tz=sd.tz))&grid;endvalid=np.arange(len(sd))+10<len(sd);endvalid&=sd[np.minimum(np.arange(len(sd))+10,len(sd)-1)]<pd.Timestamp(end,tz=sd.tz);use&=endvalid
        if use.sum()>=10:continue
        for name in labels:
            valid=use&np.isfinite(features[name].to_numpy()[ix]);on=valid&labels[name].to_numpy()[ix];off=valid&~labels[name].to_numpy()[ix]
            for domain,y in [('stock_mean',mean),('stock_excess_N50',mean-fwd[ix])]:missing.append(dict(stage=stage,domain=domain,horizon=10,regime=name,total_grid_dates=int(use.sum()),n_on=int(on.sum()),n_off=int(off.sum()),on_mean_pct=float(np.nanmean(y[on])) if on.any() else None,off_mean_pct=float(np.nanmean(y[off])) if off.any() else None,status='insufficientnonoverlappingdates; no significanceclaim'))
    pd.DataFrame(missing).to_csv(OUT/'insufficient-primary-stock-grids.csv',index=False)
    save('support-scope.json',dict(buyhold='Oneentrybatchafterfirstcompletedsegmentclose; hashprioritymax10positions, referenceATRquantitywithsamecash/sectorcaps, noSL/target, holdtosegmentend. Differentrealizedriskfromprotectivestrategies; holdingbenchmarkonly.',
      grid='Fixedglobal20sessiongrid gives fewerthan10validation/finaldates. Preservecounts/descriptivemeans; min5on+5offcannotbesatisfied, soformaltestsnotcomputed. No syntheticadditionalobservations.'))
    print('DESCRIPTIVE_SUPPORT_COMPLETE')

if __name__=='__main__':main()
