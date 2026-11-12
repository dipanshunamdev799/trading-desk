from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.ema_validation.engine import OUT,save,prepare

def holm(p):
    p=np.asarray(p);order=np.argsort(p);z=np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]);out=np.empty(len(p));out[order]=np.minimum(z,1);return out

def main():
    det=pd.read_csv(OUT/'deterministic-results.csv');ran=pd.read_csv(OUT/'random-results.csv');observed=np.load(OUT/'deterministic_paths.npz');q=prepare();rows=[];mc=[];contrasts=[];averages={}
    for stage in ['two_year','final_reset']:
        for rs in [0,1]:
            for cell in ['B','D']:
                label=f'{cell}_rs{rs}_{stage}';arr=[]
                for path in sorted((OUT/'random_paths').glob('*.npz')):
                    with np.load(path) as a:arr.append(a[label+'_equity'])
                averages[label]=np.asarray(arr).mean(axis=0)
                group=ran[(ran.stage==stage)&ran.rs_filter.eq(rs)&ran.cell.eq(cell)]
                counterpart='A' if cell=='B' else 'C';actual=det[(det.stage==stage)&det.rs_filter.eq(rs)&det.cell.eq(counterpart)].iloc[0]
                vals=group.total_return_pct.to_numpy();p=(1+np.sum(vals>=actual.total_return_pct))/(1+len(vals))
                rows.append(dict(stage=stage,rs_filter=rs,random_cell=cell,observed_cell=counterpart,seeds=len(vals),observed_return_pct=actual.total_return_pct,
                  random_mean_return_pct=vals.mean(),random_q05=np.quantile(vals,.05),random_median=np.median(vals),random_q95=np.quantile(vals,.95),
                  random_min=vals.min(),random_max=vals.max(),conditional_upper_p=p,percentile=100*np.mean(vals<actual.total_return_pct),
                  actual_trades=actual.n_trades,random_mean_trades=group.n_trades.mean(),actual_exposure_pct=actual.exposure_pct,random_mean_exposure_pct=group.exposure_pct.mean(),
                  actual_turnover=actual.turnover_multiple,random_mean_turnover=group.turnover_multiple.mean()))
        def value(cell,rs=1):return float(det[(det.stage==stage)&det.rs_filter.eq(rs)&det.cell.eq(cell)].total_return_pct.iloc[0])
        b=ran[(ran.stage==stage)&ran.rs_filter.eq(1)].pivot(index='seed',columns='cell',values='total_return_pct')
        for test,actual,null in [('EMA_given_expansion',value('A'),b.B),('EMA_without_expansion',value('C'),b.D),('EMA_gate_interaction',value('A')-value('C'),b.B-b.D)]:
            mc.append(dict(stage=stage,test=test,observed_pct=actual,null_mean_pct=null.mean(),conditional_upper_p=(1+int((null>=actual).sum()))/(1+len(null))))
        # One shared market-date draw for every cell; random paths stay dependent.
        labels=[f'{c}_rs{rs}_{stage}' for rs in [1,0] for c in ['A','B','C','D']]
        equity=np.column_stack([observed[x+'_equity'] if x[0] in ['A','C'] else averages[x] for x in labels]);n=len(equity)
        daily=equity/np.vstack([np.full((1,8),1e6),equity[:-1]])-1;rng=np.random.default_rng(673020)
        draws=[]
        for offset in range(0,3000,100):
            starts=rng.integers(0,n,(100,int(np.ceil(n/10))));ix=((starts[:,:,None]+np.arange(10))%n).reshape(100,-1)[:,:n]
            draws.append(100*(np.prod(1+daily[ix],axis=1)-1))
        d=np.vstack(draws);base=100*(equity[-1]/1e6-1)
        funcs={'EMA_expansion':lambda a:a[:,0]-a[:,1],'EMA_no_gate':lambda a:a[:,2]-a[:,3],
          'gate_given_EMA':lambda a:a[:,0]-a[:,2],'gate_given_random':lambda a:a[:,1]-a[:,3],
          'EMA_gate_interaction':lambda a:a[:,0]-a[:,1]-a[:,2]+a[:,3],
          'RS_filter_given_EMA_gate':lambda a:a[:,0]-a[:,4],
          'RS_filter_given_random_gate':lambda a:a[:,1]-a[:,5]}
        z=np.column_stack([fn(d) for fn in funcs.values()]);point=np.asarray([fn(base[None,:])[0] for fn in funcs.values()]);sd=z.std(axis=0,ddof=1)
        maxstat=np.max(np.abs((z-point)/np.where(sd>0,sd,1)),axis=1);critical=np.quantile(maxstat,.95)
        for i,name in enumerate(funcs):contrasts.append(dict(stage=stage,test=name,contrast_pct=point[i],ci95_low_pct=np.quantile(z[:,i],.025),ci95_high_pct=np.quantile(z[:,i],.975),simultaneous95_low_pct=point[i]-critical*sd[i],simultaneous95_high_pct=point[i]+critical*sd[i]))
        for cell in ['A','C']:
            i=labels.index(f'{cell}_rs1_{stage}');contrasts.append(dict(stage=stage,test=cell+'_absolute',contrast_pct=base[i],ci95_low_pct=np.quantile(d[:,i],.025),ci95_high_pct=np.quantile(d[:,i],.975)))
    pd.DataFrame(rows).to_csv(OUT/'randomization-ranking.csv',index=False);m=pd.DataFrame(mc);m['holm_p']=np.nan
    for stage,g in m.groupby('stage'):m.loc[g.index,'holm_p']=holm(g.conditional_upper_p)
    m.to_csv(OUT/'factorial-randomization.csv',index=False);pd.DataFrame(contrasts).to_csv(OUT/'factorial-confidence.csv',index=False)
    np.savez_compressed(OUT/'mean_random_equity.npz',**averages)
    save('inference-scope.json',dict(randomization='Conditional placebo ranks over1000 fixed seeds, not a correction for discovery, an exchangeability proof or independent market history.',
      bootstrap='3000 shared circular10session market-date blocks. Random controls use equal-initial-capital mean NAV acrossseedaccounts, not mean dailyreturn. Fixed-path returns resampled; no re-execution/cash constraints within each draw. Seven contrast intervals adjusted simultaneously by bootstrap max absolute standardized error; three primary randomization tests Holm-adjusted per horizon.',
      event_limit='Only four pooled volatility events; day blocks may understate uncertainty across genuinely independent episodes. No positive temporalOOS claim.'))
    print(pd.DataFrame(rows).to_string(index=False));print(m.to_string(index=False));print('INFERENCE_COMPLETE')

if __name__=='__main__':main()
