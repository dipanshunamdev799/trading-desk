from pathlib import Path
import sys,json,itertools
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.ema_validation.engine import *

def main():
    q=prepare();gate=q['gate'].copy();gate[:q['cols'][0]-1]=False;gate[q['cols'][-1]:]=False;on=np.flatnonzero(gate)
    groups=np.split(on,np.flatnonzero(np.diff(on)>10)+1);ids=np.full(len(gate),-1,int)
    for i,g in enumerate(groups):ids[g]=i
    rows=[]
    for path in sorted((OUT/'random_paths').glob('*.npz')):
        with np.load(path) as a:tr=a['B_rs1_two_year_trades']
        for e in range(len(groups)):
            selected=ids[tr[:,1].astype(int)]==e;g=tr[selected];rows.append(dict(seed=int(path.stem),event=e,trades=len(g),net_pnl=g[:,8].sum()))
    random=pd.DataFrame(rows);random.to_csv(OUT/'episode-random-results.csv',index=False);actual=pd.read_csv(OUT/'market-episodes.csv');summary=[]
    for e,g in random.groupby('event'):
        own=actual[actual.event==e].iloc[0];summary.append(dict(event=e,start=own.start,end=own.end,EMA_pnl=own.net_pnl,random_mean_pnl=g.net_pnl.mean(),EMA_increment_pnl=own.net_pnl-g.net_pnl.mean(),conditional_upper_p=(1+int(g.net_pnl.ge(own.net_pnl).sum()))/(1+len(g))))
    out=pd.DataFrame(summary);out.to_csv(OUT/'episode-incremental-EMA.csv',index=False)
    d=out.EMA_increment_pnl.to_numpy();null=np.array([np.mean(d*np.array(s)) for s in itertools.product([-1,1],repeat=len(d))])
    save('episode-inference.json',dict(events=len(d),EMA_increment_events_positive=int((d>0).sum()),EMA_increment_mean_pnl_per_event=float(d.mean()),
      descriptive_sign_flip_one_sided_p=float((null>=d.mean()-1e-9).mean()),assignments=len(null),minimum_one_sided_p=1/len(null),
      scope='Four pooled event clusters; sign symmetry/exchangeability not established. Descriptive complete sign enumeration, not robust validation. Only16assignments so strongest possible one-sided p is.0625. Episode endpoints used only in retrospective attribution.'))
    print(out.to_string(index=False))

if __name__=='__main__':main()
