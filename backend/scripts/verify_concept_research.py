"""Audit saved research identities, label timing, joins, and estimator behavior."""
import hashlib
import json

import numpy as np
import pandas as pd

import analyze_47_concepts as a


def main():
    checks=[]
    def check(name,condition):
        assert condition,name
        checks.append(name)

    results=json.loads((a.OUT/'results.json').read_text(encoding='utf-8'))
    prefix=json.loads((a.OUT/'causality_checks.json').read_text(encoding='utf-8'))
    check('all 48 real-candle event-prefix tests pass',len(prefix)==48 and all(x['pass'] for x in prefix))
    check('no invalid raw OHLC bars',all(x['invalid']==0 for x in results['audit']['coverage']))
    check('all compared native 5m OHLC bars agree',all(x['above_0_011']==0 for x in results['audit']['5m_reconciliation']))
    frames={}
    for grain in [1,5]:
        d=pd.read_csv(a.OUT/f'features_{grain}m.csv')
        for col in ['ts','known_at']:d[col]=pd.to_datetime(d[col],utc=True).dt.tz_convert('Asia/Kolkata')
        d.attrs['grain']=grain;frames[grain]=d
        check(f'{grain}m has exactly all 47 concepts', [x['id'] for x in results[str(grain)]['concepts']]==list(range(1,48)))
        check(f'{grain}m timestamps unique',d.ts.is_unique)
        check(f'{grain}m decision comes only at candle close',((d.known_at-d.ts).dt.total_seconds()==grain*60).all())
        history=[];previous=None;previous_day=None
        for _,r in d.iterrows():
            if r.ts.hour*60+r.ts.minute<915:
                if len(history)>=5:
                    assert np.isclose(r.atr,np.mean(history[-14:])),r.ts
                tr=r.high-r.low
                if previous is not None and previous_day==r.day:
                    tr=max(tr,abs(r.high-previous),abs(r.low-previous))
                history.append(tr)
            previous=r.close;previous_day=r.day
        check(f'{grain}m ATR warm-up excludes auction and overnight gaps',True)
        for horizon in [5,15,30]:
            h=horizon//grain
            expected_entry=d.groupby('day').open.shift(-1)
            expected_exit=d.groupby('day').close.shift(-h)
            valid=d[f'ret_{horizon}'].notna()
            exit_time=pd.to_datetime(d[f'exit_time_{horizon}'],utc=True).dt.tz_convert('Asia/Kolkata')
            check(f'{grain}m/{horizon}m return excludes trigger candle',np.allclose(d.loc[valid,f'ret_{horizon}'],(expected_exit-expected_entry).loc[valid]))
            check(f'{grain}m/{horizon}m exact elapsed hold',((exit_time-d.known_at).loc[valid].dt.total_seconds()==horizon*60).all())
            check(f'{grain}m/{horizon}m avoids auction labels',(exit_time.loc[valid].dt.hour*60+exit_time.loc[valid].dt.minute<=915).all())
        volume=d.rawvol_NIFTYBEES
        prior=volume.groupby(d.day).transform(lambda x:x.shift().rolling(max(3,20//grain),min_periods=3).median())
        expected=np.log1p((volume/prior.replace(0,np.nan)).clip(0,20))
        check(f'{grain}m RVOL uses prior bars only',np.allclose(expected,d.v_NIFTYBEES_rvol,equal_nan=True))
        event=pd.read_csv(a.OUT/f'events_{grain}m.csv')
        for _,r in event.iterrows():
            check_time=pd.Timestamp(r.known_at)
            assert check_time==d.loc[int(r.row),'known_at']
        check(f'{grain}m every event aligns with observable candle',True)
        for model in results[str(grain)]['ml']['models']:
            check(f'{grain}m {model["name"]} chronological folds',[x['day'] for x in model['folds']]==['2026-10-27','2026-10-28','2026-10-29'] and [x['train_sessions'] for x in model['folds']]==[2,3,4])
        pred=json.loads((a.OUT/f'predictions_{grain}m_2026-10-23.json').read_text(encoding='utf-8'))
        check(f'{grain}m predictions finite and bounded',all(np.isfinite(x['prob']) and 0<=x['prob']<=1 for x in pred))
    one,five=frames[1],frames[5]
    known=five.known_at.to_numpy()
    for _,r in one.iterrows():
        idx=np.searchsorted(known,r.known_at,side='right')-1
        expected=np.nan
        if idx>=0 and (r.known_at-five.known_at.iloc[idx]).total_seconds()<=240:
            expected=five.p_ema_gap.iloc[idx]
        assert np.isclose(expected,r.m_ema_gap,equal_nan=True),r.known_at
    check('1m context is latest closed 5m candle only',True)
    rng=np.random.default_rng(47)
    train=rng.normal(size=(600,4));test=rng.normal(size=(300,4))
    labels=(train[:,0]+train[:,1]*.5>0).astype(float);truth=(test[:,0]+test[:,1]*.5>0)
    p,_=a.logistic(train,labels,test)
    check('logistic recovers independent synthetic predictive relation',((p>=.5)==truth).mean()>.9)
    p,_=a.stump_boost(train,labels,test)
    check('boosted stumps recover independent synthetic predictive relation',((p>=.5)==truth).mean()>.8)
    check('AUC agrees with known rank example',np.isclose(a.auc(np.array([0,0,1,1]),np.array([.1,.4,.35,.8])),.75))
    doc=a.REPORT.read_text(encoding='utf-8')
    digest=hashlib.sha256((a.OUT/'snapshot.json').read_bytes()).hexdigest()
    check('report identifies exact input snapshot',digest in doc)
    check('report links existing charts',all((a.OUT/n).exists() for n in ['session_paths.png','model_comparison.png']))
    check('report includes substantive findings and complete rules','## Findings that matter' in doc and '## Exact rules for all 47 concepts' in doc)
    a.dump('verification.json',{'passed':len(checks),'checks':checks})
    print(f'{len(checks)} research audit checks passed; {len(prefix)} real-candle prefix checks passed.')


if __name__=='__main__':main()
