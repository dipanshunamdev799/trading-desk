"""One diagnosis-driven expansion-gate replay, not a new grid/holdout claim."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.swing_diagnosis.common import OLD,OUT,PERIODS,load_panel,save
from research.swing_diagnosis.audit_engine import simulate
from research.swing_diagnosis.portfolio import simulate_portfolio
from research.swing_discovery.signals import build_features,generate
from research.swing_discovery.diagnostics import summarize_run

def main():
    save('regime-replay-design.json',dict(trigger='Preliminary development-selected broad-family regime trade-subset findings from this diagnosis. Validation/final subset outcomes were already inspected before this replay. This is an execution falsification of a retrospective hypothesis, not independent confirmation.',
      families=['kama_cross','ema_cross','macd_zero_cross'],gate='Completed signal-day NIFTY50 price-index20session sample return std /60session sample return std >1.2. No future values; gate entry only, exits unchanged.',
      controls='Universal same frozen rule vs expansion gate. Corrected dividends and actual same-day taxes; baseline5bps and originaldeliveryovernightcosts. Independent375/95pools and one actual1m risk+correlation account. Allfourperiods; no threshold tuning or rule reselection.',
      next='Any favorable replay still requires new stock/time evidence, regime coverage and cost stress before an edge claim.'))
    p=load_panel()
    with np.load(OUT/'audit-dividend-corrected.npz') as a:p['dividend']=a['dividend'].copy()
    r=pd.Series(p['niftyclose']).pct_change();gate=(r.rolling(20).std()/r.rolling(60).std()>1.2).to_numpy()
    protocol=json.loads((OLD/'protocol.json').read_text());pools={k:np.array([i for i,s in enumerate(p['symbols']) if s in set(protocol[key])]) for k,key in [('development375','development_stocks'),('reserved95','reserved_stocks')]}
    f=build_features(p);frozen=json.loads((OLD/'frozen-finalists.json').read_text())['finalists'];rows=[]
    path=OUT/'regime_replay_journals';path.mkdir(exist_ok=True)
    for family in ['kama_cross','ema_cross','macd_zero_cross']:
        cfg=next(x['config'] for x in frozen if x['family']==family);base=generate(p,cfg,f)
        for stage,(start,end) in PERIODS.items():
            for gated in [False,True]:
                sig={**base,'entry':base['entry']&gate[None,:]} if gated else base
                for pool,stocks in pools.items():
                    a=simulate(p,sig,cfg,start,end,stocks=stocks,slippage_bps=5,cost_multiplier=1)
                    rows.append(dict(family=family,stage=stage,pool=pool,gated=gated,**summarize_run(a)))
                m,d,t=simulate_portfolio(p,sig,cfg,start,end,'risk_correlation',5,1,True)
                rows.append(dict(family=family,stage=stage,pool='funded_1m',gated=gated,**m))
                stem=f'{family}-{stage}-{gated}';d.to_csv(path/(stem+'-equity.csv'));t.to_csv(path/(stem+'-trades.csv'),index=False)
        print('regime replay complete',family,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'regime-replay-results.csv',index=False);save('regime-replay-results.json',rows)
    save('regime-calendar-coverage.json', {stage:dict(sessions=int(((p['dates']>=pd.Timestamp(start,tz=p['dates'].tz))&(p['dates']<pd.Timestamp(end,tz=p['dates'].tz))).sum()),
      expansion_sessions=int(gate[(p['dates']>=pd.Timestamp(start,tz=p['dates'].tz))&(p['dates']<pd.Timestamp(end,tz=p['dates'].tz))].sum())) for stage,(start,end) in PERIODS.items()})

if __name__=='__main__':main()
