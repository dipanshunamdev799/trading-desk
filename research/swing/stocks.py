"""Corporate-action-aware stock panels and causal stock-characteristic features."""
from __future__ import annotations
import json,re
from pathlib import Path
import numpy as np
import pandas as pd
from .signals import aggregate,make_signals
TZ='Asia/Kolkata'
START='2024-11-10';END='2026-11-10'
SECTORS={
 'banks':'AXISBANK HDFCBANK ICICIBANK INDUSINDBK KOTAKBANK SBIN',
 'financial_services':'BAJAJFINSV BAJFINANCE HDFCLIFE SBILIFE SHRIRAMFIN',
 'IT':'HCLTECH INFY TCS TECHM WIPRO',
 'autos':'BAJAJ-AUTO EICHERMOT HEROMOTOCO M&M MARUTI TATAMOTORS',
 'consumer_staples':'BRITANNIA HINDUNILVR ITC NESTLEIND TATACONSUM',
 'consumer_discretionary':'ASIANPAINT TITAN TRENT',
 'healthcare':'APOLLOHOSP CIPLA DRREDDY SUNPHARMA',
 'metals_materials':'GRASIM HINDALCO JSWSTEEL TATASTEEL ULTRATECH ULTRACEMCO',
 'energy_utilities':'BPCL COALINDIA NTPC ONGC POWERGRID RELIANCE',
 'industrials_infrastructure':'ADANIENT ADANIPORTS BEL LT',
 'telecom':'BHARTIARTL'}
def sector(symbol):
 return next((k for k,v in SECTORS.items() if symbol in v.split()),'other')
def load_bars(path):
 d=pd.read_csv(path);d.index=pd.to_datetime(d.pop('ts'),utc=True).dt.tz_convert(TZ)
 return d.sort_index()
def corporate_events(spec,records):
 events=[];seen=set()
 for r in records:
  if r.get('symbol') not in [spec['symbol'],spec['current_symbol']] or r.get('series')!='EQ':continue
  subject=r.get('subject','');key=(r['exDate'],subject)
  if key in seen:continue
  seen.add(key)
  try:day=pd.to_datetime(r['exDate'],format='%d-%b-%Y').strftime('%Y-%m-%d')
  except ValueError:continue
  if not '2023-01-01'<=day<END:continue
  lower=subject.lower();factor=1.;dividend=0.;kind='other'
  if 'bonus' in lower:
   m=re.search(r'(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)',subject)
   if m:factor=1+float(m[1])/float(m[2]);kind='split_bonus'
   else:kind='unresolved_capital_action'
  elif 'split' in lower:
   nums=re.findall(r'(?:Rs\.?|Re\.?)\s*(\d+(?:\.\d+)?)',subject,re.I)
   if len(nums)>=2:factor=float(nums[0])/float(nums[1]);kind='split_bonus'
   else:kind='unresolved_capital_action'
  elif any(w in lower for w in ['demerg','rights','scheme','amalgam','merger']):kind='unresolved_capital_action'
  elif 'dividend' in lower:
   m=re.search(r'(?:Rs\.?|Re\.?)\s*(\d+(?:\.\d+)?)',subject,re.I)
   if m:dividend=float(m[1]);kind='dividend'
   else:kind='unresolved_dividend'
  if kind!='other':events.append({'date':day,'kind':kind,'factor':factor,'dividend':dividend,'subject':subject,'source':'NSE corporate actions historical API'})
 return events
def prepare_stock(spec,out,actions):
 symbol=spec['symbol'];regular=load_bars(out/f'{symbol}-regular.csv');special=load_bars(out/f'{symbol}-special.csv')
 execution=pd.concat([regular,special]).sort_index();assert not execution.index.has_duplicates
 events=corporate_events(spec,actions)
 exclusions=[e for e in events if e['date']>=START and (e['kind'].startswith('unresolved') or abs(e['factor']-round(e['factor']))>1e-9)]
 audit={'symbol':symbol,'events':events,'ranking_excluded':bool(exclusions),'exclusion_reasons':exclusions,'split_detections':[]}
 if execution.empty:return regular,execution,audit
 # Reset pre-research warmup at unmodeled changes in the company's capital/business.
 warmup_events=[e['date'] for e in events if e['date']<START and e['kind'].startswith('unresolved')]
 if warmup_events:
  reset=pd.Timestamp(max(warmup_events),tz=TZ)
  regular=regular.loc[regular.index>=reset];execution=execution.loc[execution.index>=reset]
  audit['warmup_reset']=str(reset)
 actual_multiplier=pd.Series(1.,index=execution.index);unit_factor=pd.Series(1.,index=execution.index)
 execution['split_factor']=1.;execution['dividend']=0.
 for e in events:
  date=pd.Timestamp(e['date'],tz=TZ);before=execution.index<date;on=execution.index.normalize()==date
  if e['kind']=='split_bonus':
   factor=e['factor'];old=execution.loc[before,'close'];new=execution.loc[~before,'open']
   if old.empty or new.empty:continue
   ratio=float(new.iloc[0]/old.iloc[-1]);adjusted=abs(np.log(ratio))<abs(np.log(ratio*factor))
   residual=min(abs(np.log(ratio)),abs(np.log(ratio*factor)))
   if residual>.20:
    audit['ranking_excluded']=True;audit['exclusion_reasons'].append({'date':e['date'],'reason':'ambiguous_split_price_basis','ratio':ratio})
   if adjusted:actual_multiplier.loc[before]*=factor
   unit_factor.loc[before]*=factor
   if on.any():execution.loc[execution.index[on][0],'split_factor']*=factor
   elif e['date']>=START:
    audit['ranking_excluded']=True;audit['exclusion_reasons'].append({'date':e['date'],'reason':'split_ex_date_candles_missing'})
   audit['split_detections'].append({**e,'observed_open_previous_close_ratio':ratio,'provider_pre_event_adjusted':bool(adjusted),'continuity_log_error':residual})
  elif e['kind']=='dividend' and on.any():execution.loc[execution.index[on][0],'dividend']+=e['dividend']
 # Restore contemporaneous historical trade prices, then remove only share-count
 # discontinuities for indicator calculation. Future unit scale is homogeneous:
 # it cannot predict direction; stop/ATR values are converted back at each date.
 for col in ['open','high','low','close']:execution[col]*=actual_multiplier
 execution['unit_factor']=unit_factor
 neutral=execution.loc[regular.index].copy()
 for col in ['open','high','low','close']:neutral[col]/=unit_factor.reindex(neutral.index)
 neutral['actual_close']=execution.close.reindex(neutral.index)
 audit['price_basis']='Reconstruct actual pre-event units when provider prices are already split-adjusted; indicator-only split-neutral unit series; integer executable quantities change on modeled ex-date.'
 # Unknown enormous overnight jumps are not silently accepted as stock alpha.
 daily=execution.groupby(execution.index.normalize()).agg(open=('open','first'),close=('close','last'),factor=('split_factor','prod'))
 economic_gap=daily.open*daily.factor/daily.close.shift()-1
 unexplained=economic_gap.abs()>.30
 if unexplained.any():
  audit['ranking_excluded']=True;audit['unexplained_large_gaps']={str(k):float(v) for k,v in economic_gap[unexplained].items()}
 return neutral,execution,audit
def stock_signals(neutral,execution,config):
 s=make_signals(neutral,config).copy()
 # A candle finishing at15:30 belongs to that day's share basis, not the next day.
 mapping=execution.index.searchsorted(s.index,side='left')-1
 factor=execution.unit_factor.to_numpy()[np.clip(mapping,0,len(execution)-1)]
 for col in ['close','stop','atr','target','target_long','target_short','trail_stop','trail_stop_long','trail_stop_short']:
  if col in s:s[col]*=factor
 return s
def characteristics(neutral,execution,nifty_daily):
 daily=aggregate(neutral,375).copy()
 ret=daily.close.pct_change();nr=nifty_daily.reindex(daily.index.normalize()).set_axis(daily.index).pct_change()
 change=daily.close.diff().abs()
 daily['volatility_60']=ret.rolling(60).std()*np.sqrt(252)
 daily['efficiency_60']=daily.close.diff(60).abs()/change.rolling(60).sum()
 daily['momentum_126']=daily.close.pct_change(126)
 daily['beta_60']=ret.rolling(60).cov(nr)/nr.rolling(60).var()
 daily['gap_60']=(daily.open/daily.close.shift()-1).abs().rolling(60).mean()
 daily['liquidity_60']=(daily.close*daily.volume).rolling(60).median()
 # Entire feature row is available only after that complete daily candle.
 return daily[['volatility_60','efficiency_60','momentum_126','beta_60','gap_60','liquidity_60']]
