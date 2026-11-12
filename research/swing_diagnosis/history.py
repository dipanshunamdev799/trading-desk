"""Rebuild index benchmarks/history feasibility from retained primary-source files."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from research.swing_discovery.diagnostics import portfolio_metrics
from research.swing_discovery.data import prepare_data
from research.swing_discovery.benchmarks import buy_hold
from .benchmarks import PARTS,ROOT,OLD,OUT

def buyhold_extra(panel,stocks,start,end):
 from research.swing_discovery.engine import fee_coeff
 dates=panel['dates'];cols=np.flatnonzero((dates>=pd.Timestamp(start,tz=dates.tz))&(dates<pd.Timestamp(end,tz=dates.tz)));sel=np.asarray(stocks);n=len(sel)
 a=panel['actual'];cash=np.full(n,1_000_000.);q=np.zeros(n,int);ever=np.zeros(n,bool);entry_t=np.zeros(n,int);nav=[];notional=[];exposure=[];turnover=0.;fees=0.;slip=.0005
 for t in cols:
  q=np.round(q*panel['split_factor'][sel,t]).astype(int);cash+=q*panel['dividend'][sel,t]
  o=a['open'][sel,t];c=a['close'][sel,t];vol=panel['liquidity_volume'][sel,t];liquidity=panel['liquidity_turnover'][sel,t]
  ready=~ever&np.isfinite(o)&(liquidity>=50_000_000)&np.isfinite(vol);br,bf=fee_coeff(dates[t],True,False);fill=o*(1+slip)
  quantity=np.minimum(np.floor((cash-bf)/(fill*(1+br))),np.floor(vol*.01));ready&=np.isfinite(quantity)&(quantity>=1);ids=np.flatnonzero(ready)
  q[ids]=quantity[ids].astype(int);cost=q[ids]*fill[ids]*br+bf;cash[ids]-=q[ids]*fill[ids]+cost;ever[ids]=True;entry_t[ids]=t;turnover+=float((q[ids]*fill[ids]).sum());fees+=float(cost.sum())
  exposure.append((q>0).mean());notional.append(float((q*c).sum())/float((cash+q*c).sum()))
  if t==cols[-1]:
   sr,sf=fee_coeff(dates[t],False,False);exitfill=c*(1-slip);cost=exitfill*q*sr+sf+(entry_t!=t)*23.6;fees+=float(np.where(q>0,cost,0).sum());turnover+=float((exitfill*q).sum());cash+=np.where(q>0,exitfill*q-cost,0);q[:]=0
  nav.append(float((cash+q*c).mean()))
 return {'held_stockday_pct':float(np.mean(exposure)*100),'average_invested_nav_pct':float(np.mean(notional)*100),'two_sided_turnover_capital_multiple':turnover/(n*1_000_000),'fees_all_sleeves':fees,'fees_mean_sleeve':fees/n},np.asarray(nav)

def main():
 rows=[];hist=[];allvalues=[]
 for path in sorted((OUT/'benchmark_raw').glob('*-tri.json')):
  data=pd.DataFrame(json.loads(path.read_text()));data['day']=pd.to_datetime(data.Date,format='%d %b %Y');data['value']=pd.to_numeric(data.TotalReturnsIndex.str.replace(',',''));data=data.sort_values('day');assert not data.day.duplicated().any();name=data['Index Name'].iloc[0];allvalues.append(data[['day','value']].assign(index=name))
  for stage,(start,end) in PARTS.items():
   before=data[data.day<pd.Timestamp(start)];g=data[(data.day>=pd.Timestamp(start))&(data.day<pd.Timestamp(end))];base=float(before.value.iloc[-1]);equity=pd.Series(g.value.to_numpy()/base*1_000_000,index=pd.DatetimeIndex(g.day));m=portfolio_metrics(equity,0);rows.append({'index':name,'stage':stage,'base_day':str(before.day.iloc[-1].date()),'first_day':str(g.day.iloc[0].date()),'last_day':str(g.day.iloc[-1].date()),'observations':len(g),'exposure_pct':100,'turnover':None,**m})
 pd.DataFrame(rows).to_csv(OUT/'benchmark-tri-comparison.csv',index=False);pd.concat(allvalues).to_csv(OUT/'benchmark-tri-history.csv',index=False)
 x=pd.ExcelFile(OUT/'benchmark_raw/IndexInclExcl.xls')
 for sheet in x.sheet_names:
  d=pd.read_excel(x,sheet);date=pd.to_datetime(d['Event Date'],errors='coerce',format='mixed');hist.append({'index':sheet,'rows':len(d),'first_event':str(date.min()),'last_event':str(date.max()),'undated_rows':int(date.isna().sum()),'events_2016_2026':int(date.between('2016-01-01','2026-11-09').sum())})
 pd.DataFrame(hist).to_csv(OUT/'history-membership-events-coverage.csv',index=False)
 probes=[]
 for path in sorted((OUT/'benchmark_raw').glob('history-probe-*.json')):
  d=json.loads(path.read_text());a=d.get('candles',d.get('data',{}).get('candles',[]));probes.append({'symbol':path.stem.removeprefix('history-probe-'),'requested_from':'2016-01-01','requested_to':'2019-12-31','rows':len(a),'first':min([x[0] for x in a],default=None),'last':max([x[0] for x in a],default=None),'limitation':'Availability probe only; corporate-action adjustment, survivorship and delisted identity coverage not certified.'})
 (OUT/'history-price-probes.json').write_text(json.dumps(probes,indent=2))
 panel=prepare_data(OLD);corrected={**panel,'dividend':panel['dividend'].copy()};patch=pd.read_csv(OUT/'audit-dividend-corrections.csv');di={str(d.date()):i for i,d in enumerate(panel['dates'])};si={s:i for i,s in enumerate(panel['symbols'])}
 for r in patch.itertuples():
  if r.symbol in si and r.date in di:corrected['dividend'][si[r.symbol],di[r.date]]=r.corrected
 eligible=np.flatnonzero(panel['eligible']);out=[]
 for label,p in [('original_dividends',panel),('corrected_multicomponent_dividends',corrected)]:
  for stage,(start,end) in PARTS.items():
   r=buy_hold(p,eligible,start,end);extra,nav=buyhold_extra(p,eligible,start,end);assert np.allclose(nav,r['equity'].to_numpy(),rtol=0,atol=1e-8);out.append({'stage':stage,'dividend_model':label,**r['summary'],**extra});r['stock_metrics'].to_csv(OUT/f'benchmark-buyhold-{stage}-{label}-stocks.csv',index=False);r['equity'].to_csv(OUT/f'benchmark-buyhold-{stage}-{label}-equity.csv')
 pd.DataFrame(out).to_csv(OUT/'benchmark-buyhold-correction.csv',index=False)
 print(pd.DataFrame(out)[['stage','dividend_model','total_return_pct','max_drawdown_pct','sharpe']].to_string(index=False));print(json.dumps(probes,indent=2))
if __name__=='__main__':main()
