"""Audit-corrected replay of the exact previously frozen benchmark controls."""
import json
import numpy as np
import pandas as pd
from .benchmarks import OLD,OUT,PARTS,clean
from .audit_engine import simulate
from research.swing_discovery.data import prepare_data
from research.swing_discovery.signals import build_features,smooth,lag
from research.swing_discovery.diagnostics import summarize_run

def main():
 panel=prepare_data(OLD);panel['nifty']=panel['niftyclose'];panel['dividend']=np.load(OUT/'audit-dividend-corrected.npz')['dividend'];features=build_features(panel);ids=np.flatnonzero(panel['eligible']);c=panel['neutral']['close']
 frequency=pd.read_csv(OUT/'benchmark-random-probabilities.csv').set_index('symbol').loc[panel['symbols'],'development_entry_probability'].to_numpy();controls=[('simple_trend_ema200',c>smooth(c,200)),('simple_momentum60',c/lag(c,60)>1)]
 for seed in range(20261111,20261131):controls.append(('random_'+str(seed),np.random.default_rng(seed).random(c.shape)<frequency[:,None]))
 base={'initial_capital':1_000_000,'risk_fraction':.005,'stop_atr':2.,'reward':2.,'max_hold_sessions':10,'exit':'fixed','stop_mode':'atr','min_turnover':50_000_000,'participation':.01};rows=[];days=[]
 for name,entry in controls:
  for stage in ['final','two_year']:
   start,end=PARTS[stage];r=simulate(panel,{'entry':entry,'atr':features['atr']},base,start,end,stocks=ids,slippage_bps=5,cost_multiplier=1,keep_trades=True);t=r['trades'];turnover=float((t.entry_fill*t.entry_quantity+t['exit']*t.quantity).sum())/(len(ids)*1_000_000) if len(t) else 0.
   rows.append({'control':name,'stage':stage,'cost_scenario':'audited_dividends_and_actual_same_day_statutory_taxes',**summarize_run(r),'gross_return_pct':float(r['stock_metrics'].gross_profit.mean()/10000),'two_sided_turnover_capital_multiple':turnover});days.append(pd.DataFrame({'control':name,'stage':stage,'day':r['dates'].strftime('%Y-%m-%d'),'equity':r['equity'].to_numpy(),'return':r['returns'].to_numpy()}))
  print('corrected complete',name,flush=True)
 pd.DataFrame(rows).to_csv(OUT/'benchmark-controls-corrected.csv',index=False);pd.concat(days).to_csv(OUT/'benchmark-control-days-corrected.csv',index=False)
 pd.DataFrame(rows).groupby('stage').total_return_pct.agg(['count','mean','min','max']).to_csv(OUT/'benchmark-controls-corrected-summary.csv')
 print(json.dumps({'runs':len(rows),'control_count':len(controls),'selection':'Identical controls/seeds/probabilities; actualsame-daytax and multicomponentdividend corrections only.'}),flush=True)
if __name__=='__main__':main()
