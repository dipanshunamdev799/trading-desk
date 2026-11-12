from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.swing_diagnosis.common import OLD,OUT,PERIODS,load_panel,save
from research.swing_diagnosis.portfolio import simulate_portfolio
from research.swing_discovery.signals import build_features,generate

def main():
    save('regime-stress-design.json',dict(scope='Stress the same one expansion gate and three rules, no threshold changes or new selection.',stress='Double modeled fees and10bps adverse fills; all four old periods, funded risk+correlation account. Triggered after baseline replay, conditional retrospective stress only.'))
    p=load_panel()
    with np.load(OUT/'audit-dividend-corrected.npz') as a:p['dividend']=a['dividend'].copy()
    r=pd.Series(p['niftyclose']).pct_change();gate=(r.rolling(20).std()/r.rolling(60).std()>1.2).to_numpy();f=build_features(p)
    frozen=json.loads((OLD/'frozen-finalists.json').read_text())['finalists'];rows=[]
    for family in ['kama_cross','ema_cross','macd_zero_cross']:
        cfg=next(x['config'] for x in frozen if x['family']==family);sig=generate(p,cfg,f);sig={**sig,'entry':sig['entry']&gate[None,:]}
        for stage,(start,end) in PERIODS.items():
            m,d,t=simulate_portfolio(p,sig,cfg,start,end,'risk_correlation',10,2,True)
            rows.append(dict(family=family,stage=stage,**m));d.to_csv(OUT/'regime_replay_journals'/f'{family}-{stage}-stress-equity.csv')
        print('regime stress complete',family,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'regime-stress-results.csv',index=False)
    ci=[];rng=np.random.default_rng(9732)
    for path in sorted((OUT/'regime_replay_journals').glob('*-True-equity.csv')):
        a=pd.read_csv(path);returns=a.equity.to_numpy()/np.r_[1e6,a.equity.to_numpy()[:-1]]-1;n=len(a)
        starts=rng.integers(0,n,(3000,int(np.ceil(n/10))));ix=((starts[:,:,None]+np.arange(10))%n).reshape(3000,-1)[:,:n]
        vals=100*(np.prod(1+returns[ix],axis=1)-1)
        ci.append(dict(journal=path.name,return_pct=100*(a.equity.iloc[-1]/1e6-1),ci95_low_pct=np.quantile(vals,.025),ci95_high_pct=np.quantile(vals,.975)))
    pd.DataFrame(ci).to_csv(OUT/'regime-portfolio-uncertainty.csv',index=False)

if __name__=='__main__':main()
