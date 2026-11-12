"""Fixed-variant transfer test on starting-period NIFTY50 constituents.

Run after scripts/fetch_stock_swing.py. No strategy optimization or broker orders.
"""
from __future__ import annotations
import sys,json,hashlib,time
from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.swing.signals import catalog,clear_cache
from research.swing.stocks import prepare_stock,stock_signals,characteristics,sector,load_bars
from research.swing.stock_engine import simulate
from research.swing.validation import trade_uncertainty,daily_returns,search_max_t
OUT=ROOT/'artifacts'/'stock_swing_research'
IDS=['structure_only_base','E_tf120_30','E_buffer0.0','E_zone0.25','E_no_slope',
     'B_macd8_21_5','B_macd5_35_5','E_ema90','E_macd8_21_5','E_tf240_60',
     'E_macd5_35_5','E_r3','F_r4']
PARTS={'development':('2024-11-10','2025-11-10'),'validation':('2025-11-10','2026-05-10'),
       'final':('2026-05-10','2026-11-10'),'two_year':('2024-11-10','2026-11-10')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):
 (OUT/name).write_text(json.dumps(x,indent=2,default=str,allow_nan=False))
def features_for_trades(t,features,symbol,c,part):
 if t.empty:return t
 t=t.copy();t['signal_time']=pd.to_datetime(t.signal_time,utc=True).dt.tz_convert('Asia/Kolkata')
 t=t.sort_values('signal_time');f=features.reset_index().rename(columns={'available_at':'feature_time'})
 t=pd.merge_asof(t,f,left_on='signal_time',right_on='feature_time',direction='backward')
 t.insert(0,'part',part);t.insert(0,'sector',sector(symbol));t.insert(0,'id',c['id']);t.insert(0,'symbol',symbol)
 return t
def stock_benchmark(execution,start,end):
 d=execution.loc[(execution.index>=pd.Timestamp(start,tz='Asia/Kolkata'))&(execution.index<pd.Timestamp(end,tz='Asia/Kolkata'))]
 if d.empty:return None
 s=pd.DataFrame({'side':[1],'stop':[.00001],'atr':[np.nan]},index=d.index[:1])
 return simulate(execution,s,{'cost_model':'equity_delivery','risk_fraction':1.,'stop_constraints':False,'exit':'time',
                             'max_hold_sessions':10000},start,end,allow_short=False)
def run():
 universe=json.loads((OUT/'universe.json').read_text())['stocks'];actions=json.loads((OUT/'nse-actions-all.json').read_text())
 original=json.loads((ROOT/'artifacts/swing_research/protocol.json').read_text())
 configs=[next(c for c in original['configs'] if c['id']==i) for i in IDS]
 controls=[c for c in catalog() if c['id'] in ['ema_only_base','macd_only_base']]
 configlist=configs+controls
 protocol={'window':['2024-11-10','2026-11-10 exclusive'],'parts':PARTS,'universe':universe,'configs':configs,'controls':controls,
  'selection':'Fixed13distinct variants listed in preceding response; no stock-specific parameter changes. Stock shortlist per rule uses development only:>=8trades, positive netR; highest meanR5stocks. Choices frozen before examining validation/final tables.',
  'characteristics':'Only completed daily candles at signal time. Volatility60, efficiency60, momentum126, beta60 vsNIFTY, absolute overnight gap60, median turnover proxy60; sector fixed coarse business label. Low/mid/high thresholds fit on unique development stock/signal events only.',
  'costs':'Stock equity delivery fees (including0.1%STT bothsides), adverse2bps/side fills; final severe stress doubled fees and5bps/side. No leverage or delivery shorts.',
  'corporate_actions':'Historical NSE event archive2023-2026. Detect provider split adjustment at each ex-date, restore actual contemporary prices, use split-neutral indicators with actual-unit stop/ATR conversion; adjust carried share counts and protective prices. Dividend economic entitlement at ex-date included; payment timing/withholding outside scope. Unresolved demergers/rights/fractional bonus and unexplained>30%gaps quarantine stocks from comparable ranking before any performance computation.',
  'data_quality':'At least98%of493regular sessions required. Any omitted ordinary research session quarantines stock from comparable whole-period ranking; data unavailable cases retained explicitly.',
  'multiple_testing':'650stock/variant hypotheses registered, pluscontrols; historical winners descriptive. Approximate one-sided search max-t across eligible validation daily returns and clustered final expectancy intervals, no true independent holdout claim.',
  'capital':'Each stock-rule sleeve starts₹1m, risk0.5%includingfees, maxoneposition, cash-notional cap. These are independent sleeves, not simultaneous₹1mportfolio positions.',
  'seed':20261110,'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'research/swing/stocks.py',ROOT/'research/swing/stock_engine.py',Path(__file__)]}}
 save('protocol.json',protocol)
 nifty=load_bars(ROOT/'artifacts/swing_research/nifty-5minute.csv').groupby(lambda t:t.normalize()).close.last()
 metrics=[];trades=[];daily=[];audits=[];benchmarks=[];t0=time.monotonic()
 expected=load_bars(ROOT/'artifacts/swing_research/nifty-5minute.csv');expected=set(expected.loc[expected.index>=pd.Timestamp('2024-11-10',tz='Asia/Kolkata')].index.strftime('%Y-%m-%d'))
 for number,spec in enumerate(universe,1):
  symbol=spec['symbol'];path=OUT/f'{symbol}-regular.csv'
  if '--wait-data' in sys.argv and not (OUT/f'{symbol}-audit.json').exists():
   print(symbol,'WAITING_FOR_DATA',flush=True)
   deadline=time.monotonic()+1800
   while not (OUT/f'{symbol}-audit.json').exists() and time.monotonic()<deadline:time.sleep(1)
  if not path.exists():
   audits.append({'symbol':symbol,'ranking_excluded':True,'reason':'acquisition_incomplete'});continue
  neutral,execution,audit=prepare_stock(spec,OUT,actions)
  actual_days=set(neutral.loc[neutral.index>=pd.Timestamp('2024-11-10',tz='Asia/Kolkata')].index.strftime('%Y-%m-%d'))
  missing=sorted(expected-actual_days)
  if missing:
   audit['ranking_excluded']=True;audit['ordinary_research_sessions_missing']=missing
  audits.append(audit)
  if audit['ranking_excluded']:
   print(symbol,'QUARANTINED',len(audit['exclusion_reasons']),len(missing),flush=True);clear_cache();continue
  features=characteristics(neutral,execution,nifty)
  for part,(start,end) in PARTS.items():
   b=stock_benchmark(execution,start,end)
   if b:benchmarks.append({'symbol':symbol,'sector':sector(symbol),'part':part,**b['metrics']})
  for c in configlist:
   s=stock_signals(neutral,execution,c);exe={**c,'cost_model':'equity_delivery'}
   for part,(start,end) in PARTS.items():
    r=simulate(execution,s,exe,start,end,allow_short=False)
    metrics.append({'symbol':symbol,'sector':sector(symbol),'id':c['id'],'control':c['id'] not in IDS,'part':part,**r['metrics']})
    tagged=features_for_trades(r['trades'],features,symbol,c,part)
    if len(tagged):trades.append(tagged)
    dr=daily_returns(r['equity'])
    for ts,value in dr.items():daily.append({'symbol':symbol,'id':c['id'],'part':part,'day':ts.strftime('%Y-%m-%d'),'return':value})
    if part=='final':
     sr=simulate(execution,s,exe,start,end,allow_short=False,cost_multiplier=2,slippage_bps=5)
     metrics.append({'symbol':symbol,'sector':sector(symbol),'id':c['id'],'control':c['id'] not in IDS,'part':'final_severe',**sr['metrics']})
   # Journals for every continuous stock/variant combination.
   journal=OUT/'journals';journal.mkdir(exist_ok=True)
   if len(r['trades']):r['trades'].to_csv(journal/f'{symbol}-{c["id"]}-trades.csv',index=False)
   r['equity'].groupby(r['equity'].index.normalize()).last().to_csv(journal/f'{symbol}-{c["id"]}-daily-equity.csv')
  clear_cache()
  pd.DataFrame(metrics).to_csv(OUT/'metrics.csv',index=False)
  save('stock-data-audit.json',audits)
  print(symbol,'TESTED',number,'/',len(universe),'elapsed',round(time.monotonic()-t0),flush=True)
 pd.DataFrame(metrics).to_csv(OUT/'metrics.csv',index=False)
 (pd.concat(trades,ignore_index=True) if trades else pd.DataFrame()).to_csv(OUT/'trades-with-characteristics.csv',index=False)
 pd.DataFrame(daily).to_csv(OUT/'daily-returns.csv',index=False)
 pd.DataFrame(benchmarks).to_csv(OUT/'buy-hold.csv',index=False)
 save('stock-data-audit.json',audits)
 save('run-summary.json',{'registered_stocks':len(universe),'tested_stocks':len({m['symbol'] for m in metrics}),'variants':len(configs),'controls':len(controls),'metric_rows':len(metrics),'elapsed_seconds':time.monotonic()-t0})
 from research.swing.stock_reporting import build_report
 build_report(OUT,ROOT)
if __name__=='__main__':run()
