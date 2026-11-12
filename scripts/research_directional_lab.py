"""Chronological NIFTY direction lab. Research only; no broker/order access.

Run: .venv/Scripts/python.exe scripts/research_directional_lab.py
Inputs are frozen JSON candle files in artifacts/directional_research.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'directional_research'
SEED=20261109

def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,default=str,allow_nan=False),encoding='utf-8')

def frame(path):
    obj=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(obj,dict): obj=obj.get('candles',obj.get('data',[]))
    if obj and isinstance(obj[0],list):
        obj=[dict(zip(['ts','open','high','low','close','volume','oi'],r)) for r in obj]
    d=pd.DataFrame(obj)
    d['ts']=pd.to_datetime(d.ts,utc=True).dt.tz_convert('Asia/Kolkata')
    for col in ['open','high','low','close']:
        d[col]=pd.to_numeric(d[col],errors='coerce')
    return d.sort_values('ts',kind='stable').drop_duplicates('ts',keep='last')

def load_data():
    paths=[OUT/'nifty-db-1minute.json',OUT/'nifty-db-5minute.json']
    one=frame(paths[0]);minute=one.ts.dt.hour*60+one.ts.dt.minute
    one=one[(minute>=555)&(minute<910)].copy()
    one['bucket']=one.ts.dt.floor('5min')
    agg=one.groupby('bucket').agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),n=('open','size')).reset_index().rename(columns={'bucket':'ts'})
    agg=agg[agg.n==5].drop(columns='n');agg['source']='db_1m_aggregate'
    native=frame(paths[1]);native['source']='db_native_5m'
    extra=OUT/'nifty-upstox-5minute.json'
    if extra.exists():
        paths.append(extra);extra_frame=frame(extra);extra_frame['source']='upstox_download_5m'
        native=pd.concat([native,extra_frame]).sort_values('ts',kind='stable').drop_duplicates('ts',keep='last')
    overlap=agg.merge(native,on='ts',suffixes=('_a','_b'))
    deviations={col:float((overlap[col+'_a']-overlap[col+'_b']).abs().max()) if len(overlap) else None for col in ['open','high','low','close']}
    conflicts=overlap.loc[np.any(np.column_stack([(overlap[c+'_a']-overlap[c+'_b']).abs()>.011 for c in ['open','high','low','close']]),axis=1),'ts']
    conflict_days=set(conflicts.dt.strftime('%Y-%m-%d'))
    d=pd.concat([agg,native]).sort_values('ts',kind='stable').drop_duplicates('ts',keep='last').reset_index(drop=True)
    minute=d.ts.dt.hour*60+d.ts.dt.minute;d=d[(minute>=555)&(minute<910)].copy();d['day']=d.ts.dt.strftime('%Y-%m-%d')
    valid=np.isfinite(d[['open','high','low','close']]).all(axis=1)&(d.low>0)&(d.high>=d[['open','close','low']].max(axis=1))&(d.low<=d[['open','close','high']].min(axis=1))
    invalid_days=set(d.loc[~valid,'day'])
    complete=[];excluded=[]
    for day,g in d.groupby('day'):
        expected=list(range(555,910,5));actual=list(g.ts.dt.hour*60+g.ts.dt.minute)
        if actual!=expected or day in invalid_days or day in conflict_days:
            excluded.append({'day':day,'bars':len(g),'invalid':day in invalid_days,'conflict':day in conflict_days})
        else: complete.append(day)
    d=d[d.day.isin(complete)].reset_index(drop=True)
    audit={'input_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'overlap_bars':len(overlap),'overlap_max_abs_difference':deviations,'conflicting_days':sorted(conflict_days),'excluded_sessions':excluded,'sessions':len(complete),'first':complete[0],'last':complete[-1],'bars':len(d)}
    return d,audit

def features(d):
    d=d.copy();g=d.groupby('day');d['minute']=d.ts.dt.hour*60+d.ts.dt.minute;d['bar']=g.cumcount();d['known_at']=d.ts+pd.Timedelta(minutes=5)
    prior=g.close.shift();tr=pd.concat([d.high-d.low,(d.high-prior).abs(),(d.low-prior).abs()],axis=1).max(axis=1)
    d['atr']=tr.shift().rolling(14,min_periods=14).mean();d['vol_ratio']=d.atr/d.atr.shift().rolling(200,min_periods=100).median()
    delta=g.close.diff();gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean();loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean();d['rsi']=100*gain/(gain+loss)
    for length in [5,9,12,21,26,50]: d[f'ema{length}']=d.close.ewm(span=length,adjust=False).mean()
    for length in [3,6,12,20]:
        d[f'ret{length}']=g.close.diff(length)/d.atr
        d[f'high{length}']=g.high.transform(lambda s:s.shift().rolling(length,min_periods=length).max())
        d[f'low{length}']=g.low.transform(lambda s:s.shift().rolling(length,min_periods=length).min())
    d['efficiency']=g.close.diff(12).abs()/delta.abs().groupby(d.day).transform(lambda s:s.rolling(12,min_periods=12).sum())
    d['trend']=(d.ema9-d.ema21)/d.atr;d['distance']=(d.close-d.ema21)/d.atr
    d['body']=(d.close-d.open)/d.atr;d['range_atr']=(d.high-d.low)/d.atr
    for minutes in [15,30,60]:
        # Running levels freeze exactly when the last opening-range bar closes.
        h=d.high.where(d.minute<555+minutes).groupby(d.day).cummax().groupby(d.day).ffill()
        l=d.low.where(d.minute<555+minutes).groupby(d.day).cummin().groupby(d.day).ffill()
        d[f'orb_high{minutes}']=h.where(d.minute+5>=555+minutes)
        d[f'orb_low{minutes}']=l.where(d.minute+5>=555+minutes)
    d['session_open']=g.open.transform('first')
    # Shifted previous complete research session's 15:10 mark; not official EOD.
    session_close=g.close.last();previous=session_close.shift()
    d['prev_research_close']=d.day.map(previous);d['gap']=(d.session_open-d.prev_research_close)/d.atr
    return d

def rules(d):
    zero=np.zeros(len(d),dtype=np.int8);out=[]
    def add(family,param,long,short):
        side=np.where(long,1,np.where(short,-1,0)).astype(np.int8)
        side[np.asarray(long)&np.asarray(short)]=0
        out.append((family,param,side))
    for fast,slow in [(5,21),(9,21),(12,26),(21,50)]:
        diff=(d[f'ema{fast}']-d[f'ema{slow}'])/d.atr
        for threshold in [0,.5]:add('ema_trend',f'{fast}_{slow}_gap{threshold}',diff>threshold,diff<-threshold)
    for length in [6,12,20]:
        for buffer in [0,.25]:add('donchian',f'lookback{length}_buffer{buffer}',d.close>d[f'high{length}']+buffer*d.atr,d.close<d[f'low{length}']-buffer*d.atr)
    for length in [3,6,12]:
        for threshold in [.5,1.5]:add('momentum',f'lookback{length}_atr{threshold}',d[f'ret{length}']>threshold,d[f'ret{length}']<-threshold)
    for minutes in [15,30,60]:
        for buffer in [0,.25]:add('orb',f'minutes{minutes}_buffer{buffer}',d.close>d[f'orb_high{minutes}']+buffer*d.atr,d.close<d[f'orb_low{minutes}']-buffer*d.atr)
    for tolerance in [.25,.75]:
        for slow in [21,50]:add('pullback',f'ema{slow}_tolerance{tolerance}',(d.ema9>d[f'ema{slow}'])&(d.low<=d.ema9+tolerance*d.atr)&(d.close>d.ema9)&(d.close>d.open),(d.ema9<d[f'ema{slow}'])&(d.high>=d.ema9-tolerance*d.atr)&(d.close<d.ema9)&(d.close<d.open))
    for threshold in [20,30,40]:
        for dist in [0,1]:add('rsi_reversion',f'rsi{threshold}_distance{dist}',(d.rsi<threshold)&(d.distance<-dist),(d.rsi>100-threshold)&(d.distance>dist))
    for threshold in [1,2,3]:
        add('ema_reversion',f'distance{threshold}',d.distance<-threshold,d.distance>threshold)
    prior_range=(d.high6-d.low6)/d.atr
    for compression in [2,3]:
        for body in [.5,1]:add('compression_breakout',f'range{compression}_body{body}',(prior_range<compression)&(d.close>d.high6)&(d.body>body),(prior_range<compression)&(d.close<d.low6)&(d.body<-body))
    for threshold in [1,3]:
        for mode in ['fade','follow']:
            side=np.sign(d.gap)*(-1 if mode=='fade' else 1)
            active=(d.gap.abs()>threshold)&(d.minute<660)
            add('gap_'+mode,f'gap_atr{threshold}',active&(side>0),active&(side<0))
    for length in [6,12,20]:
        add('failed_breakout',f'lookback{length}',(d.low<d[f'low{length}'])&(d.close>d[f'low{length}'])&(d.close>d.open),(d.high>d[f'high{length}'])&(d.close<d[f'high{length}'])&(d.close<d.open))
    return out

def configurations(d):
    configs=[]
    windows={'all':(d.minute>=570),'morning':(d.minute>=570)&(d.minute<660),'midday':(d.minute>=660)&(d.minute<780),'afternoon':d.minute>=780}
    # Six fixed conditions; no end-of-session regime labels.
    for family,param,side in rules(d):
        filters={'none':np.ones(len(d),bool),'trend':(d.efficiency>=.35)&(d.trend.abs()>=.5),'range':d.efficiency<.25,'ema_aligned':side*d.trend>0,'high_vol':d.vol_ratio>=1.2,'normal_vol':d.vol_ratio<1.2}
        for filter_name,mask in filters.items():
            for window,wmask in windows.items():
                signal=np.where(np.asarray(mask)&np.asarray(wmask)&d.atr.gt(0),side,0)
                for horizon in [15,30,60]:
                    name=f'{family}|{param}|{filter_name}|{window}|h{horizon}'
                    configs.append((name,family,param,filter_name,window,horizon,signal))
    return configs

def trade_rows(d,signal,horizon):
    h=horizon//5;n=len(d);inds=np.flatnonzero(signal);day=d.day.to_numpy();minute=d.minute.to_numpy();op=d.open.to_numpy();cl=d.close.to_numpy();rows=[];last_exit=-1
    for i in inds:
        if i<last_exit or i+h>=n or day[i+h]!=day[i] or minute[i+h]+5>910:continue
        # Complete sessions guarantee exact contiguous elapsed horizons.
        j=i+h;rows.append((i,j,float(signal[i]),float((cl[j]-op[i+1])*signal[i])));last_exit=j
    return np.array(rows,dtype=float).reshape(-1,4)

def stats(trades,day_codes,partition_days):
    if len(trades):
        tc=day_codes[trades[:,0].astype(int)];t=trades[np.isin(tc,partition_days)]
    else:t=trades
    if not len(t):return {'n':0,'gross_mean':0.,'net2_mean':0.,'net5_mean':0.,'win_pct':0.,'gross_total':0.,'net2_total':0.,'trading_days':0,'positive_session_pct':0.,'net2_session_mean':0.,'worst_session':0.}
    p=t[:,3];codes=day_codes[t[:,0].astype(int)];daily=np.array([np.sum(p[codes==day]-2) for day in partition_days]);active=np.unique(codes)
    return {'n':len(t),'gross_mean':float(p.mean()),'net2_mean':float((p-2).mean()),'net5_mean':float((p-5).mean()),'win_pct':float((p>0).mean()*100),'gross_total':float(p.sum()),'net2_total':float((p-2).sum()),'trading_days':len(active),'positive_session_pct':float((daily>0).mean()*100),'net2_session_mean':float(daily.mean()),'worst_session':float(daily.min())}

def bootstrap(trades,day_codes,days):
    t=trades[np.isin(day_codes[trades[:,0].astype(int)],days)];codes=day_codes[t[:,0].astype(int)]
    totals=np.array([np.sum(t[codes==day,3]-2) for day in days]);counts=np.array([np.sum(codes==day) for day in days]);rng=np.random.default_rng(SEED)
    # Moving 5-session blocks preserve short-run serial dependence better than IID trades.
    block=min(5,len(days));samples=[]
    for _ in range(3000):
        starts=rng.integers(0,len(days),math.ceil(len(days)/block));idx=np.concatenate([(np.arange(block)+s)%len(days) for s in starts])[:len(days)]
        if counts[idx].sum():samples.append(totals[idx].sum()/counts[idx].sum())
    return {'net2_mean_ci95':np.percentile(samples,[2.5,97.5]).tolist() if samples else [None,None],'block_sessions':block,'resamples':3000}

def audit_features(d,f):
    checks=[]
    for cut in [45,81,len(d)//3+17,len(d)//2+31,len(d)-25]:
        p=features(d.iloc[:cut]);cols=[c for c in p if c not in ['source','volume','oi']]
        pd.testing.assert_frame_equal(p[cols],f.iloc[:cut][cols],check_dtype=False)
        checks.append({'prefix_bars':cut,'passed':True})
    return checks

def main():
    d,audit=load_data();f=features(d);audit['prefix_tests']=audit_features(d,f)
    days=np.array(sorted(d.day.unique()));n=len(days);a=int(n*.6);b=int(n*.8)
    if n<40:raise ValueError('Need at least 40 complete sessions')
    parts={'development':days[:a],'validation':days[a:b],'holdout':days[b:]};codes=d.day.to_numpy();configs=configurations(f)
    dump('lab-preregister.json',{'seed':SEED,'configuration_count':len(configs),'families':sorted(set(c[1] for c in configs)),'splits':{k:{'first':v[0],'last':v[-1],'sessions':len(v)} for k,v in parts.items()},'entry':'Next bar open after signal close','exit':'Close after 15/30/60 minutes, <=15:10 IST','costs':'0,2,5 INDEX points round trip; not option costs','selection':'Best per family by min(development net2_mean, validation net2_mean). Eligibility: dev>=100 trades, val>=30, positive dev/val net2 means. No holdout use.'})
    devrows=[];stored={}
    for idx,c in enumerate(configs):
        name,family,param,filter_name,window,horizon,signal=c;t=trade_rows(f,signal,horizon);stored[name]=t
        row={'name':name,'family':family,'params':param,'filter':filter_name,'window':window,'horizon':horizon}
        for part in ['development','validation']:
            row.update({part+'_'+key:val for key,val in stats(t,codes,parts[part]).items()})
        row['selection_score']=min(row['development_net2_mean'],row['validation_net2_mean'])
        row['eligible']=row['development_n']>=100 and row['validation_n']>=30 and row['selection_score']>0
        devrows.append(row)
    table=pd.DataFrame(devrows);selected=[]
    for family,g in table.groupby('family'):
        pool=g[g.eligible]
        if len(pool):selected.append(pool.sort_values(['selection_score','validation_n'],ascending=False).iloc[0]['name'])
    # This artifact is written BEFORE any holdout return is scored.
    frozen={'selected':selected,'selector_hash':hashlib.sha256(table.to_csv(index=False).encode()).hexdigest(),'uses_holdout':False}
    dump('lab-frozen-selection.json',frozen)
    for row in devrows:
        row.update({'holdout_'+k:v for k,v in stats(stored[row['name']],codes,parts['holdout']).items()})
    table=pd.DataFrame(devrows);table.to_csv(OUT/'lab-all-configurations.csv',index=False)
    selected_results=[];trade_export=[]
    for name in selected:
        row=table.set_index('name').loc[name].to_dict();t=stored[name];row.update(bootstrap(t,codes,parts['holdout']));row['name']=name
        row['new_november_diagnostic']=stats(t,codes,days[days>='2026-11-02'])
        row['passes_descriptive_holdout_gate']=bool(row['holdout_n']>=30 and row['holdout_net5_mean']>0 and row['net2_mean_ci95'][0]>0)
        # Selection-adjusted p-values are NOT implied by this descriptive gate.
        selected_results.append(row)
        for i,j,side,pnl in t:
            i,j=int(i),int(j);part=next(k for k,v in parts.items() if codes[i] in v)
            assert f.ts.iloc[i+1]==f.known_at.iloc[i]
            assert f.known_at.iloc[j]-f.ts.iloc[i+1]==pd.Timedelta(minutes=row['horizon'])
            trade_export.append({'strategy':name,'split':part,'session':codes[i],'signal_at':str(f.known_at.iloc[i]),'entry_at':str(f.ts.iloc[i+1]),'exit_at':str(f.known_at.iloc[j]),'direction':int(side),'entry':float(f.open.iloc[i+1]),'exit':float(f.close.iloc[j]),'gross_index_points':pnl,'net2_index_points':pnl-2,'net5_index_points':pnl-5,'signal_efficiency':float(f.efficiency.iloc[i]) if np.isfinite(f.efficiency.iloc[i]) else None,'signal_trend':float(f.trend.iloc[i]),'signal_vol_ratio':float(f.vol_ratio.iloc[i]) if np.isfinite(f.vol_ratio.iloc[i]) else None})
    pd.DataFrame(trade_export).to_csv(OUT/'lab-selected-trades.csv',index=False)
    baselines=[]
    for label,signal in [('always_up',np.ones(len(f))),('always_down',-np.ones(len(f))),('momentum_30m',np.sign(f.ret6.fillna(0).to_numpy()))]:
        for horizon in [15,30,60]:
            s=np.where(f.minute>=570,signal,0);t=trade_rows(f,s,horizon)
            baselines.append({'name':label,'horizon':horizon,**{part:stats(t,codes,partdays) for part,partdays in parts.items()}})
    regimes=[]
    for row in trade_export:
        if row['split']!='holdout':continue
        eff=row['signal_efficiency'];regime='trend' if eff is not None and eff>=.35 and abs(row['signal_trend'])>=.5 else 'range' if eff is not None and eff<.25 else 'transition'
        regimes.append({**row,'regime':regime})
    if regimes:
        pd.DataFrame(regimes).groupby(['strategy','regime']).agg(trades=('gross_index_points','size'),gross_mean=('gross_index_points','mean'),net2_mean=('net2_index_points','mean')).to_csv(OUT/'lab-holdout-regimes.csv')
    summary={'audit':audit,'configuration_count':len(configs),'eligible_development_validation':int(table.eligible.sum()),'splits':{k:{'first':v[0],'last':v[-1],'sessions':len(v)} for k,v in parts.items()},'selected':selected_results,'baselines':baselines,'limitations':['Index direction study, not option-premium P&L.','Many related variants: selecting among final results invalidates untouched holdout status.','Historical holdout: October2026 was inspected in prior project research. It is not a fully untouched prospective period. November2–6 is separately disclosed new-data diagnostic, too short to validate.','No position sizing, stop losses, targets, executable bid/ask, taxes or funding model.','Full-session completeness filtering is a data-quality screen and may induce sample selection.','Gap reference is prior complete research session 15:10 mark, not official closing price; missing sessions can make this a multi-day gap.']}
    dump('lab-summary.json',summary);dump('lab-data-audit.json',audit)
    lines=['# NIFTY directional strategy laboratory','',f"Frozen research: {n} complete sessions, {audit['first']} through {audit['last']}; {len(d)} five-minute bars.",f"Tested {len(configs)} fixed configurations across {len(set(c[1] for c in configs))} families; {int(table.eligible.sum())} passed development/validation eligibility.",'','## Design','Signals are observed at five-minute candle close, entered at the following open, held 15/30/60 minutes and closed by15:10 IST. Exactly one position at a time per configuration; no stop/target or position sizing optimization. Session regimes use only observations available at signal time. EMA/RSI/ATR can retain earlier-session context; breakouts and opening range reset by session. Index volume is never used as traded volume.','',json.dumps(summary['splits'],indent=2),'','The selection file was written before holdout evaluation: one eligible winner per family, ranked by the minimum of development and validation mean after two illustrative index points. Eligibility requires at least100/30 development/validation trades and positive net2 mean in both. Full holdout grid is disclosed for transparency and MUST NOT become a new selection set.','', '## Frozen finalists','|Family|Rule|Dev N|Val N|Holdout N|Holdout gross mean pts|Net2|Net5|Net2 block-bootstrap95% CI|','|---|---|---:|---:|---:|---:|---:|---:|---|']
    for r in selected_results:
        ci=r['net2_mean_ci95'];lines.append(f"|{r['family']}|{r['params']} / {r['filter']} / {r['window']} / {r['horizon']}m|{r['development_n']}|{r['validation_n']}|{r['holdout_n']}|{r['holdout_gross_mean']:.2f}|{r['holdout_net2_mean']:.2f}|{r['holdout_net5_mean']:.2f}|{ci[0]:.2f}, {ci[1]:.2f}|")
    if not selected_results:lines.append('No configuration passed the predeclared eligibility criteria.')
    lines+=['','## Interpretation','A positive index-points result does not establish a profitable long-call/long-put strategy. Premium sensitivity to implied volatility, theta, strike, expiry, bid/ask and execution must be tested separately. The five-session moving-block intervals measure uncertainty conditional on these fixed finalists; they do not fully correct the earlier parameter search or a changing market.','', 'No live bot is deployed. A descriptive holdout gate (>=30 trades, net5 positive, and net2 lower CI>0) is a further research filter, never an automatic trading approval.','', 'The holdout is historical, not fully untouched: October2026 was inspected by prior project research. New November sessions are separately disclosed without further selection. Initial DB-only run is preserved in lab-initial-db-run/; this broader run changes data coverage, not the rule grid or selection rule.', '', '## Newly observed November diagnostic', '|Family|N|Gross mean index pts|Net2|', '|---|---:|---:|---:|']
    for r in selected_results:
        new=r['new_november_diagnostic'];lines.append(f"|{r['family']}|{new['n']}|{new['gross_mean']:.2f}|{new['net2_mean']:.2f}|")
    lines+=['', 'Only the fixed family finalists are shown; five sessions cannot establish stability. The previous-session15:10 mark used by gap rules is not the official daily close and can span multiple days if a session was excluded.', '', '## Baselines','|Baseline|Hold minutes|Holdout N|Holdout gross pts|Holdout net2 pts|','|---|---:|---:|---:|---:|']
    for r in baselines:lines.append(f"|{r['name']}|{r['horizon']}|{r['holdout']['n']}|{r['holdout']['gross_mean']:.2f}|{r['holdout']['net2_mean']:.2f}|")
    lines+=['','## Data and reproducibility',f"Input SHA256 and exclusions: lab-data-audit.json. {len(audit['prefix_tests'])} feature prefix-invariance tests passed. Every exported entry and exit was asserted against its exact timestamp and holding horizon.",'','Full ledger: lab-all-configurations.csv; fixed finalist trades: lab-selected-trades.csv; frozen selector: lab-frozen-selection.json; forward-known regime diagnostics: lab-holdout-regimes.csv.','']
    (OUT/'lab-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'sessions':n,'configurations':len(configs),'eligible':int(table.eligible.sum()),'selected':len(selected),'holdout_passes':[r['name'] for r in selected_results if r['passes_descriptive_holdout_gate']]},indent=2))

if __name__=='__main__':main()
