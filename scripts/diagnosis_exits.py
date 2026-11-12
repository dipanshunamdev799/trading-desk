"""Controlled exit/filter experiments after audit findings; never selects a winner."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.swing_diagnosis.common import OLD,OUT,PERIODS,load_panel,save
from research.swing_diagnosis.audit_engine import simulate
from research.swing_discovery.signals import build_features,generate
from research.swing_discovery.diagnostics import summarize_run

def main():
    changes={'base':{},'stop_1atr':{'stop_atr':1.},'stop_3atr':{'stop_atr':3.},'target_3r':{'reward':3.},
      'time_only_10':{'exit':'time'},'hold_20':{'max_hold_sessions':20},'without_filter':{'filter':'none'},'zero_friction':{}}
    families=['kama_cross','ema_cross','hybrid_ribbon_pullback']
    save('exit-design.json',dict(questions=['Do wider stops improve same signal policy?','Does removing fixed profit target help?','Does a longer hold help?','Are reference filters suppressing returns?','Does positive gross edge survive costs?'],
      families=families,one_coordinate_changes=changes,periods={k:v for k,v in PERIODS.items() if k!='two_year'},
      assumptions='Corrected dividends and actual same-day taxes. zero_friction removes fees and slippage. Same frozen reference signals; execution changes can change subsequent available entries. No result used to choose or tune rules; dates reused and not independent OOS.'))
    p=load_panel()
    with np.load(OUT/'audit-dividend-corrected.npz') as a:p['dividend']=a['dividend'].copy()
    f=build_features(p);eligible=np.flatnonzero(p['eligible']);frozen=json.loads((OLD/'frozen-finalists.json').read_text())['finalists'];rows=[]
    daily=[]
    for family in families:
        base=next(x['config'] for x in frozen if x['family']==family)
        for label,change in changes.items():
            cfg={**base,**change};cfg['params']={**base['params'],**change};s=generate(p,cfg,f)
            for stage,(start,end) in PERIODS.items():
                if stage=='two_year':continue
                r=simulate(p,s,cfg,start,end,stocks=eligible,slippage_bps=0 if label=='zero_friction' else 5,
                  cost_multiplier=0 if label=='zero_friction' else 1,keep_trades=False)
                rows.append(dict(family=family,variant=label,stage=stage,**summarize_run(r)))
                daily.extend(dict(family=family,variant=label,stage=stage,day=str(d.date()),net_return=float(v)) for d,v in r['returns'].items())
        print('exit controls complete',family,flush=True)
    a=pd.DataFrame(rows);baseline=a[a.variant=='base'].set_index(['family','stage'])
    a['return_delta_pct']=[r.total_return_pct-baseline.loc[(r.family,r.stage),'total_return_pct'] for r in a.itertuples()]
    a.to_csv(OUT/'exit-controls.csv',index=False);pd.DataFrame(daily).to_csv(OUT/'exit-control-daily.csv',index=False)
    save('exit-summary.json',dict(runs=len(a),scope='One-factor diagnosis; not a search or validated selection. Paired outcomes share dates and stocks; no inference from best observed setting.'))

if __name__=='__main__':main()
