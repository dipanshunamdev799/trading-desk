"""Independent checks of the persisted direction-lab selection and trade ledger."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from research_directional_lab import OUT,load_data

summary=json.loads((OUT/'lab-summary.json').read_text())
frozen=json.loads((OUT/'lab-frozen-selection.json').read_text())
table=pd.read_csv(OUT/'lab-all-configurations.csv')
ledger=pd.read_csv(OUT/'lab-selected-trades.csv')
checks=[]
def check(label,value):
 assert value,label
 checks.append(label)
selected=[]
for family,g in table.groupby('family'):
 pool=g[(g.development_n>=100)&(g.validation_n>=30)&(g.development_net2_mean>0)&(g.validation_net2_mean>0)].copy()
 if len(pool):
  pool['score']=pool[['development_net2_mean','validation_net2_mean']].min(axis=1)
  selected.append(pool.sort_values(['score','validation_n'],ascending=False).iloc[0]['name'])
check('selection exactly reproduced without holdout columns',selected==frozen['selected'])
check('all fixed configurations disclosed',len(table)==summary['configuration_count']==3600)
raw,_=load_data();raw=raw.set_index('ts')
for col in ['entry_at','exit_at','signal_at']: ledger[col]=pd.to_datetime(ledger[col],utc=True).dt.tz_convert('Asia/Kolkata')
check('signal closes at exact next-bar entry',bool((ledger.entry_at==ledger.signal_at).all()))
check('all exits no later than15:10 IST',bool((ledger.exit_at.dt.hour*60+ledger.exit_at.dt.minute<=910).all()))
check('all positions close within entry session',bool((ledger.entry_at.dt.date==ledger.exit_at.dt.date).all()))
for name,t in ledger.groupby('strategy'):
 spec=table[table.name==name].iloc[0]
 check(name+' duration',bool(((t.exit_at-t.entry_at).dt.total_seconds()==spec.horizon*60).all()))
 ordered=t.sort_values('entry_at')
 check(name+' no overlapping positions',bool((ordered.entry_at.iloc[1:].to_numpy()>=ordered.exit_at.iloc[:-1].to_numpy()).all()))
 expected_entry=raw.loc[t.entry_at,'open'].to_numpy()
 expected_exit=raw.loc[t.exit_at-pd.Timedelta(minutes=5),'close'].to_numpy()
 check(name+' exact source prices',bool(np.allclose(t.entry,expected_entry)&np.allclose(t.exit,expected_exit)))
 check(name+' signed pnl',bool(np.allclose(t.gross_index_points,(expected_exit-expected_entry)*t.direction)))
 for split,g in t.groupby('split'):
  check(name+' '+split+' trade count',len(g)==spec[split+'_n'])
  check(name+' '+split+' mean',bool(np.isclose(g.gross_index_points.mean(),spec[split+'_gross_mean'])))
check('all feature prefix checks passed',all(x['passed'] for x in summary['audit']['prefix_tests']))
(OUT/'lab-verification.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2))
print(len(checks),'verification checks passed')
