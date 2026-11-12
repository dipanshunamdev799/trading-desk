"""Frozen simple-signal/random controls; no changes to original research."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from research.swing_discovery.data import prepare_data
from research.swing_discovery.signals import build_features,generate,smooth,lag
from research.swing_discovery.engine import simulate
from research.swing_discovery.diagnostics import summarize_run,portfolio_metrics

PARTS={'development':('2024-11-10','2025-11-10'),'validation':('2025-11-10','2026-05-10'),'final':('2026-05-10','2026-11-10'),'two_year':('2024-11-10','2026-11-10')}
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'artifacts/swing_discovery';OUT=ROOT/'artifacts/swing_diagnosis'
def clean(v):
 if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [clean(x) for x in v]
 if isinstance(v,(np.floating,float)):return float(v) if np.isfinite(v) else None
 if isinstance(v,np.integer):return int(v)
 if isinstance(v,np.bool_):return bool(v)
 return v

def main():
 OUT.mkdir(exist_ok=True);panel=prepare_data(OLD);panel['nifty']=panel['niftyclose'];features=build_features(panel)
 dates=panel['dates'];ids=np.flatnonzero(panel['eligible']);dev=(dates>=pd.Timestamp(PARTS['development'][0],tz=dates.tz))&(dates<pd.Timestamp(PARTS['development'][1],tz=dates.tz))
 frozen=json.loads((OLD/'frozen-finalists.json').read_text())['finalists']
 frequency=np.zeros(len(panel['symbols']))
 for record in frozen:frequency+=generate(panel,record['config'],features)['entry'][:,dev].mean(axis=1)/len(frozen)
 pd.DataFrame({'symbol':panel['symbols'],'development_entry_probability':frequency,'eligible':panel['eligible']}).to_csv(OUT/'benchmark-random-probabilities.csv',index=False)
 c=panel['neutral']['close'];atr=features['atr'];ema200=smooth(c,200)
 base={'initial_capital':1_000_000,'risk_fraction':.005,'stop_atr':2.,'reward':2.,'max_hold_sessions':10,'exit':'fixed','stop_mode':'atr','min_turnover':50_000_000,'participation':.01}
 summary=[];daily=[]
 controls=[('simple_trend_ema200',c>ema200),('simple_momentum60',c/lag(c,60)>1)]
 for seed in range(20261111,20261131):controls.append(('random_'+str(seed),np.random.default_rng(seed).random(c.shape)<frequency[:,None]))
 for name,entry in controls:
  signal={'entry':entry,'atr':atr}
  for stage,(start,end) in PARTS.items():
   for cost,slip,label in [(1.,5.,'baseline'),(0.,0.,'zero_cost_counterfactual')]:
    r=simulate(panel,signal,base,start,end,stocks=ids,slippage_bps=slip,cost_multiplier=cost,keep_trades=True)
    t=r['trades'];s=summarize_run(r);turnover=float((t.entry_fill*t.entry_quantity+t['exit']*t.quantity).sum())/(len(ids)*1_000_000) if len(t) else 0.
    summary.append({'control':name,'stage':stage,'cost_scenario':label,**s,'gross_return_pct':float(r['stock_metrics'].gross_profit.mean()/10000),'two_sided_turnover_capital_multiple':turnover,'entry_probability_mean':float(entry[ids][:,dev].mean())})
    daily.append(pd.DataFrame({'control':name,'stage':stage,'cost_scenario':label,'day':dates[(dates>=pd.Timestamp(start,tz=dates.tz))&(dates<pd.Timestamp(end,tz=dates.tz))].strftime('%Y-%m-%d'),'equity':r['equity'].to_numpy(),'return':r['returns'].to_numpy()}))
  print('complete',name,flush=True)
 pd.DataFrame(summary).to_csv(OUT/'benchmark-controls.csv',index=False);pd.concat(daily).to_csv(OUT/'benchmark-control-days.csv',index=False)
 frame=pd.DataFrame(summary);random=frame[frame.control.str.startswith('random_')];rows=[]
 original=pd.read_csv(OLD/'all-runs.csv')
 for (stage,cost),g in random.groupby(['stage','cost_scenario']):
  for metric in ['total_return_pct','sharpe','max_drawdown_pct','expectancy_r','exposure_pct','n_trades','two_sided_turnover_capital_multiple']:
   rows.append({'stage':stage,'cost_scenario':cost,'metric':metric,'seeds':len(g),'mean':g[metric].mean(),'q05':g[metric].quantile(.05),'median':g[metric].median(),'q95':g[metric].quantile(.95)})
  if cost=='baseline':
   obs=original[(original.stage==stage)&(original.pool=='all_eligible_stocks')]
   if len(obs):
    record=obs[['id','total_return_pct']].copy();record['random_seed_percentile']=record.total_return_pct.map(lambda x:100*(g.total_return_pct<x).mean());record['stage']=stage;record.to_csv(OUT/f'benchmark-finalist-random-{stage}.csv',index=False)
 pd.DataFrame(rows).to_csv(OUT/'benchmark-random-distribution.csv',index=False)
 (OUT/'benchmark-execution.json').write_text(json.dumps(clean({'control_count':len(controls),'execution_runs':len(summary),'seed_range':[20261111,20261130],'stocks':len(ids),'configuration':base,'assumptions':'Independent sleeves, not funded portfolio; no seed selected; random seed distribution is conditional on one reused market history; simple trend/momentum entries use same fixed stop/target/hold as original, not canonical fully-invested indices.','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}),indent=2))
 print(frame[~frame.control.str.startswith('random_')][['control','stage','cost_scenario','total_return_pct','exposure_pct','n_trades']].to_string(index=False),flush=True)

if __name__=='__main__':main()
