"""Causal contextual-feature panel and fixed ablations; no orders or strategy tuning."""
from pathlib import Path
import hashlib
import json
import sqlite3
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts'/'directional_research_phase2'
BASE = ROOT/'artifacts'/'directional_research'
sys.path[:0] = [str(ROOT/'backend'), str(ROOT/'scripts')]
import research_directional_lab as lab

SHORTLIST = [
    'ema_trend|12_26_gap0.5|trend|afternoon|h60',
    'donchian|lookback20_buffer0|trend|afternoon|h60',
    'pullback|ema21_tolerance0.75|trend|afternoon|h60',
]


def dump(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2, default=str, allow_nan=False), encoding='utf-8')


def read_candles(path):
    d = pd.DataFrame(json.loads(path.read_text(encoding='utf-8')))
    d['ts'] = pd.to_datetime(d.ts, utc=True).dt.tz_convert('Asia/Kolkata')
    return d.sort_values('ts', kind='stable').drop_duplicates('ts').reset_index(drop=True)


def freeze_observations():
    path = OUT/'feature-observations.json'
    if path.exists():
        return json.loads(path.read_text())
    from app.config import get_settings
    from sqlalchemy import create_engine, text
    engine = create_engine(get_settings().database_url_sync)
    with engine.connect() as conn:
        data = conn.execute(text('SELECT observation_key,factor_id,source,reported_at,observed_at,payload FROM nifty_observations ORDER BY observed_at,observation_key')).mappings()
        rows = [dict(row) for row in data]
    # Capture every revision; store source values, never connection settings.
    path.write_text(json.dumps(rows, default=str), encoding='utf-8')
    return json.loads(path.read_text())


def prepare_observations(rows):
    d = pd.DataFrame(rows)
    if d.empty:
        return d
    d['observed_at'] = pd.to_datetime(d.observed_at, utc=True,format='mixed')
    d['reported_at'] = pd.to_datetime(d.reported_at, utc=True,format='mixed')
    d['available_at'] = pd.concat([d.observed_at, d.reported_at], axis=1).max(axis=1)
    d['effective_report'] = d.reported_at.fillna(d.observed_at)
    d['value'] = [r.get('value') if isinstance(r, dict) else None for r in d.payload]
    return d.sort_values(['available_at','observation_key'], kind='stable')


def asof_observation(d, decision):
    """Filter information time first, then resolve latest reporting-period revision."""
    valid = d[(d.observed_at<=decision) & (d.reported_at.isna() | (d.reported_at<=decision))]
    return valid.sort_values(['factor_id','effective_report','observed_at','observation_key'], kind='stable').drop_duplicates('factor_id', keep='last')


def observation_panel(times, obs):
    factors = ['pcr','iv','max_pain','fii_cash','dii_cash']
    rows = []
    records=obs[['factor_id','available_at','effective_report','observed_at','reported_at','observation_key','value']].to_dict('records')
    cursor=0;latest={}
    for decision in times:
        result = {'known_at':decision,'captured_factor_count':0}
        while cursor<len(records) and records[cursor]['available_at']<=decision:
            row=records[cursor];factor=row['factor_id'];old=latest.get(factor)
            key=lambda r:(r['effective_report'],r['observed_at'],r['observation_key'])
            if old is None or key(row)>key(old):latest[factor]=row
            cursor+=1
        result['captured_factor_count']=len(latest)
        for factor in factors:
            row=latest.get(factor)
            if row is not None:
                value=pd.to_numeric(pd.Series([row['value']]), errors='coerce').iloc[0]
                result['captured_'+factor] = value
                result['captured_'+factor+'_age_minutes'] = (decision-row['available_at']).total_seconds()/60
                result['captured_'+factor+'_reported_age_minutes'] = (decision-row['reported_at']).total_seconds()/60 if pd.notna(row['reported_at']) else np.nan
                result['captured_'+factor+'_observation_key'] = row['observation_key']
        rows.append(result)
    return pd.DataFrame(rows)


def context_panel(nifty, daily, vix, etf):
    n = nifty[['ts','open','close','day']].copy()
    n['known_at'] = n.ts+pd.Timedelta(minutes=5)
    daily = daily.copy(); daily['day'] = daily.ts.dt.strftime('%Y-%m-%d')
    # Strict earlier date: no current/future daily OHLC is needed to derive the prior close.
    positions=np.searchsorted(daily.day.to_numpy(),n.day.to_numpy(),side='left')-1
    n['prior_official_close']=[float(daily.close.iloc[i]) if i>=0 else np.nan for i in positions]
    n['prior_official_day']=[daily.day.iloc[i] if i>=0 else None for i in positions]
    n['official_gap_points'] = n.groupby('day').open.transform('first')-n.prior_official_close
    # Source timestamps denote candle starts; values first become available at close.
    v = vix.copy(); v['known_at']=v.ts+pd.Timedelta(minutes=5); v['day']=v.ts.dt.strftime('%Y-%m-%d')
    v['vix_level']=v.close
    previous=v.groupby('day').close.last().shift()
    v['vix_prior_close']=v.day.map(previous)
    v['vix_change_pct']=100*(v.close/v.vix_prior_close-1)
    v['vix_day_open']=v.groupby('day').open.transform('first')
    v['vix_intraday_change_pct']=100*(v.close/v.vix_day_open-1)
    n = pd.merge_asof(n.sort_values('known_at'),v[['known_at','vix_level','vix_prior_close','vix_change_pct','vix_intraday_change_pct']],on='known_at',direction='backward',tolerance=pd.Timedelta(minutes=0))
    e=etf.copy();e['known_at']=e.ts+pd.Timedelta(minutes=5);e['day']=e.ts.dt.strftime('%Y-%m-%d');e['clock']=e.ts.dt.strftime('%H:%M')
    e['volume']=pd.to_numeric(e.volume,errors='coerce')
    e['typical_notional']=(e.high+e.low+e.close)/3*e.volume
    e['etf_candle_vwap_proxy']=e.groupby('day').typical_notional.cumsum()/e.groupby('day').volume.cumsum().replace(0,np.nan)
    e['etf_close']=e.close
    # Reindex each clock to the same observed-session calendar before rolling; missing bars stay missing.
    volumes=e.pivot(index='day',columns='clock',values='volume').sort_index()
    med=volumes.shift().rolling(20,min_periods=5).median()
    counts=volumes.shift().rolling(20,min_periods=1).count()
    e['etf_prior_sameclock_median']=pd.MultiIndex.from_frame(e[['day','clock']]).map(med.stack())
    e['etf_prior_sameclock_sessions']=pd.MultiIndex.from_frame(e[['day','clock']]).map(counts.stack())
    e['etf_rvol']=e.volume/e.etf_prior_sameclock_median.replace(0,np.nan)
    n = pd.merge_asof(n.sort_values('known_at'),e[['known_at','etf_close','etf_candle_vwap_proxy','etf_rvol','etf_prior_sameclock_sessions']],on='known_at',direction='backward',tolerance=pd.Timedelta(minutes=0))
    for name in ['prior_official_close','vix_level','vix_change_pct','etf_candle_vwap_proxy','etf_rvol']:
        n[name+'_missing']=n[name].isna()
    return n


def tests(nifty,daily,vix,etf,obs):
    checks=[]
    # Delayed release and revision: reporting date alone may never make a later capture available.
    examples=[{'observation_key':'a','factor_id':'f','source':'x','reported_at':'2026-01-01T15:00Z','observed_at':'2026-01-02T10:00Z','payload':{'value':1}},
              {'observation_key':'b','factor_id':'f','source':'x','reported_at':'2026-01-01T15:00Z','observed_at':'2026-01-03T10:00Z','payload':{'value':2}},
              {'observation_key':'c','factor_id':'g','source':'x','reported_at':'2026-01-04T10:00Z','observed_at':'2026-01-03T10:00Z','payload':{'value':3}}]
    example=prepare_observations(examples)
    assert asof_observation(example,pd.Timestamp('2026-01-01T16:00Z')).empty
    assert asof_observation(example,pd.Timestamp('2026-01-02T11:00Z')).iloc[0]['value']==1
    assert asof_observation(example,pd.Timestamp('2026-01-03T11:00Z')).iloc[0]['value']==2
    assert len(asof_observation(example,pd.Timestamp('2026-01-03T11:00Z')))==1
    checks+=['delayed observation excluded','old revision retained before new capture','revision enters only after capture','future reported timestamp excluded']
    full=context_panel(nifty,daily,vix,etf)
    for stop in [555,5001,16001,len(nifty)-5]:
        if stop>=len(nifty):continue
        cutoff=nifty.ts.iloc[stop-1]+pd.Timedelta(minutes=5)
        prefix=context_panel(nifty.iloc[:stop],daily[daily.ts<cutoff.normalize()],vix[vix.ts+pd.Timedelta(minutes=5)<=cutoff],etf[etf.ts+pd.Timedelta(minutes=5)<=cutoff])
        relevant=full.iloc[:stop]
        pd.testing.assert_frame_equal(prefix.reset_index(drop=True),relevant.reset_index(drop=True),check_dtype=False)
        checks.append('context prefix invariant at '+str(cutoff))
    assert obs.observed_at.notna().all()
    checks.append('all captured observations have explicit observed_at')
    # Verify the incremental production join against the independently filtered/sorted oracle.
    decisions=pd.Series(pd.to_datetime(['2026-10-24T17:10Z','2026-10-27T08:00Z','2026-11-06T08:00Z']))
    joined=observation_panel(decisions,obs)
    for decision,r in zip(decisions,joined.to_dict('records')):
        selected=asof_observation(obs,decision)
        assert r['captured_factor_count']==len(selected)
        for factor in ['pcr','iv','max_pain','fii_cash','dii_cash']:
            chosen=selected[selected.factor_id==factor]
            if len(chosen):assert r['captured_'+factor+'_observation_key']==chosen.iloc[0].observation_key
    checks.append('incremental as-of join matches independent revision oracle at three decision times')
    return full,checks


def paired_intervals(base, kept, days):
    """Conditional interval for means and filtered-minus-baseline mean using paired day blocks."""
    def arrays(rows):
        count=rows.groupby('session').size().reindex(days,fill_value=0).to_numpy()
        total=rows.groupby('session').net2_index_points.sum().reindex(days,fill_value=0).to_numpy()
        return count,total
    bc,bp=arrays(base);kc,kp=arrays(kept)
    length=len(days);block=min(5,length);rng=np.random.default_rng(20261109)
    starts=rng.integers(0,length,size=(3000,int(np.ceil(length/block)),1))
    idx=((starts+np.arange(block))%length).reshape(3000,-1)[:,:length]
    bn=bc[idx].sum(axis=1);kn=kc[idx].sum(axis=1);valid=(bn>0)&(kn>0)
    if not valid.any():return {'net2_ci_low':None,'net2_ci_high':None,'delta_ci_low':None,'delta_ci_high':None}
    bm=bp[idx].sum(axis=1)[valid]/bn[valid];km=kp[idx].sum(axis=1)[valid]/kn[valid]
    ci=np.quantile(km,[.025,.975]);delta=np.quantile(km-bm,[.025,.975])
    return {'net2_ci_low':float(ci[0]),'net2_ci_high':float(ci[1]),'delta_ci_low':float(delta[0]),'delta_ci_high':float(delta[1])}


def gap_correction(nifty,panel,summary):
    # This is a separately registered feature-definition correction, with the original frozen parameters.
    dump('feature-gap-preregister.json',{'comparison':'Original previous15:10 research close versus strictly preceding official daily close',
        'frozen_rules':['gap_fade|gap_atr1|range|all|h60','gap_follow|gap_atr3|high_vol|all|h60'],
        'parameters_changed':False,'timing':'Registered after context ablations, before reading corrected gap outcomes; exploratory historical comparison'})
    original=lab.features(nifty);corrected=original.copy()
    corrected['gap']=(corrected.session_open-panel.prior_official_close.to_numpy())/corrected.atr
    metrics=[]
    for definition,f in [('research_close',original),('official_close',corrected)]:
        for mode,threshold,filter_name in [('fade',1,'range'),('follow',3,'high_vol')]:
            side=np.sign(f.gap)*(-1 if mode=='fade' else 1)
            condition=(f.efficiency<.25) if filter_name=='range' else (f.vol_ratio>=1.2)
            active=(f.gap.abs()>threshold)&(f.minute<660)&(f.minute>=570)&condition&f.atr.gt(0)
            signal=np.where(active,side,0)
            trades=lab.trade_rows(f,signal,60)
            rows=[]
            for i,j,direction,pnl in trades:
                rows.append({'session':f.day.iloc[int(i)],'net2_index_points':pnl-2,'gross_index_points':pnl})
            ledger=pd.DataFrame(rows,columns=['session','net2_index_points','gross_index_points'])
            for split,info in summary['splits'].items():
                held=ledger[(ledger.session>=info['first'])&(ledger.session<=info['last'])]
                result={'mode':mode,'definition':definition,'split':split,'n':len(held),
                        'gross_mean':float(held.gross_index_points.mean()) if len(held) else None,
                        'net2_mean':float(held.net2_index_points.mean()) if len(held) else None,
                        'net5_mean':float(held.gross_index_points.mean()-5) if len(held) else None}
                if split=='holdout':
                    days=panel.loc[(panel.day>=info['first'])&(panel.day<=info['last']),'day'].unique()
                    result.update(paired_intervals(held,held,days))
                metrics.append(result)
    pd.DataFrame(metrics).to_csv(OUT/'feature-gap-correction.csv',index=False)
    return metrics


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    paths={'vix':OUT/'context-vix-5minute.json','etf':OUT/'context-niftybees-5minute.json','daily':BASE/'nifty-upstox-1day.json'}
    missing=[str(p) for p in paths.values() if not p.exists()]
    if missing:raise FileNotFoundError('Context fetch pending: '+', '.join(missing))
    # Write all addition rules before reading any outcome ledger.
    dump('feature-preregister.json',{'shortlist':SHORTLIST,'filters':['baseline','vix_below_dev_median','vix_not_rising','etf_vwap_agreement','etf_rvol_ge1','official_gap_agreement'],
        'thresholds':'Only VIX median estimated on development feature rows. All others fixed a priori.',
        'comparison':'Same fixed trade opportunities; unavailable features reject additions but never silently filter baseline',
        'execution':'Retain phase1 fixed entries/exits; index points only','selection':'No feature or strategy selection from results; all ablations disclosed'})
    nifty,nifty_audit=lab.load_data()
    daily=read_candles(paths['daily']);vix=read_candles(paths['vix']);etf=read_candles(paths['etf'])
    source_checks=[]
    for name,source in [('daily',daily),('vix',vix),('etf',etf)]:
        assert np.isfinite(source[['open','high','low','close']]).all().all(),name
        assert (source.low>0).all() and (source.high>=source[['open','low','close']].max(axis=1)).all() and (source.low<=source[['open','high','close']].min(axis=1)).all(),name
        source_checks.append(name+' source OHLC finite and internally consistent')
    obs=prepare_observations(freeze_observations())
    panel,checks=tests(nifty,daily,vix,etf,obs)
    checks+=source_checks
    capture=observation_panel(panel.known_at,obs)
    panel=panel.merge(capture,on='known_at',how='left',validate='one_to_one')
    summary=json.loads((BASE/'lab-summary.json').read_text())
    gap_metrics=gap_correction(nifty,panel,summary)
    dev_end=summary['splits']['development']['last']
    vix_median=float(panel.loc[panel.day<=dev_end,'vix_level'].median())
    ledger=pd.read_csv(BASE/'lab-selected-trades.csv')
    ledger=ledger[ledger.strategy.isin(SHORTLIST)].copy()
    ledger['known_at']=pd.to_datetime(ledger.signal_at,utc=True).dt.tz_convert('Asia/Kolkata')
    joined=ledger.merge(panel.drop(columns=['open','close','day','ts']),on='known_at',how='left',validate='many_to_one')
    masks={'baseline':np.ones(len(joined),bool),
           'vix_below_dev_median':joined.vix_level<vix_median,
           'vix_not_rising':joined.vix_change_pct<=0,
           'etf_vwap_agreement':joined.direction*(joined.etf_close-joined.etf_candle_vwap_proxy)>0,
           'etf_rvol_ge1':joined.etf_rvol>=1,
           'official_gap_agreement':joined.direction*joined.official_gap_points>0}
    metrics=[]
    for strategy in SHORTLIST:
        for split in ['development','validation','holdout']:
            group=(joined.strategy==strategy)&(joined.split==split)
            for label,mask in masks.items():
                rows=joined[group&mask];base=joined[group];p=rows.gross_index_points
                result={'strategy':strategy,'split':split,'filter':label,'n':len(rows),'baseline_n':len(base),'gross_mean':float(p.mean()) if len(p) else None,'net2_mean':float(p.mean()-2) if len(p) else None,'net5_mean':float(p.mean()-5) if len(p) else None,
                        'same_opportunity_baseline_gross_mean':float(base.gross_index_points.mean()) if len(base) else None,'coverage_pct':100*len(rows)/len(base) if len(base) else None}
                if split=='holdout':
                    info=summary['splits'][split]
                    days=panel.loc[(panel.day>=info['first'])&(panel.day<=info['last']),'day'].unique()
                    result.update(paired_intervals(base,rows,days))
                metrics.append(result)
    # Fields are useful only with source-age bounds. No capture factor is used as a strategy condition here.
    panel.to_csv(OUT/'feature-panel.csv',index=False)
    joined.to_csv(OUT/'feature-trade-panel.csv',index=False)
    pd.DataFrame(metrics).to_csv(OUT/'feature-ablations.csv',index=False)
    sql=panel.copy()
    for c in sql:
        if pd.api.types.is_datetime64_any_dtype(sql[c]):sql[c]=sql[c].astype(str)
    with sqlite3.connect(OUT/'feature-panel.sqlite') as conn:
        sql.to_sql('features',conn,if_exists='replace',index=False)
    obs_audit={'records':len(obs),'factors':int(obs.factor_id.nunique()),'first_capture':str(obs.observed_at.min()),'last_capture':str(obs.observed_at.max()),'first_reported':str(obs.reported_at.min()),'snapshots_available_before_first_capture':0,
               'reported_after_observed_rows':int((obs.reported_at>obs.observed_at).sum()),'latest_dashboard_is_not_point_in_time':True}
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*paths.values(),BASE/'lab-selected-trades.csv',OUT/'feature-observations.json',Path(__file__),*[BASE/name for name in nifty_audit['input_hashes']]]}
    audit={'checks':checks,'checks_passed':len(checks),'input_sha256':hashes,'observations':obs_audit,'panel_rows':len(panel),'development_vix_median':vix_median,
           'missing_pct':{c:float(panel[c].isna().mean()*100) for c in ['vix_level','etf_candle_vwap_proxy','etf_rvol','prior_official_close']},
           'sessions_with_any_captured_factor':int(panel.loc[panel.captured_factor_count>0,'day'].nunique())}
    dump('feature-audit.json',audit)
    lines=['# Point-in-time contextual research','',f"{len(panel):,} five-minute decisions; {len(checks)} availability/prefix checks passed. Development-only VIX median: {vix_median:.2f}.",
           '', 'All additions were fixed before outcomes were read. Every baseline trade remains in the ledger; each added filter evaluates a subset of those same opportunities. Differences in subset averages are exploratory and do not establish causal or incremental predictive value. No filter was selected for deployment.',
           '', '|Frozen rule|Filter|Final trades|Baseline trades|Gross pts|Net2 pts|Net5 pts|Net2 95% block interval|Change vs baseline 95% interval|','|---|---|---:|---:|---:|---:|---:|---|---|']
    for r in metrics:
        if r['split']=='holdout':
            vals=[f"{r[k]:.2f}" if r[k] is not None else 'NA' for k in ['gross_mean','net2_mean','net5_mean']]
            ci=f"{r['net2_ci_low']:.2f} to {r['net2_ci_high']:.2f}" if r['net2_ci_low'] is not None else 'NA'
            delta=f"{r['delta_ci_low']:.2f} to {r['delta_ci_high']:.2f}" if r['delta_ci_low'] is not None else 'NA'
            lines.append('|'+ '|'.join([r['strategy'].split('|')[0],r['filter'],str(r['n']),str(r['baseline_n']),*vals,ci,delta])+'|')
    lines+=['','## Feature definitions and boundaries',
            '- Official gap uses the preceding published daily close, strictly prior to the current date. It replaces the 15:10 research-window close only for this feature; underlying entry rules remain frozen.',
            '- VIX values join only exact completed five-minute timestamps, with no stale carry. Prior VIX close uses the preceding observed VIX session. No current-session final close is exposed earlier.',
            '- ETF relative volume uses the same clock bucket over the prior 20 observed ETF sessions, minimum five valid bars. Missing observations stay missing. Volume is actual ETF reported volume, not spot-index volume.',
            '- ETF VWAP is explicitly a candle typical-price-times-volume proxy accumulated from completed bars. It is not a true tick-by-tick traded-price VWAP.',
            '- Missing context rejects a filtered trade; it does not disappear from baseline coverage. This is a coverage/execution requirement, not evidence that unobserved trades would fail.',
            '', '## Fixed gap-rule correction',
            'The original gap-fade and gap-follow finalists are also replayed with their frozen threshold/filter/60-minute exit, replacing the research-window prior close with the official prior daily close. This feature-definition comparison was separately registered after context ablations, before corrected gap outcomes were computed. It remains exploratory historical evidence.',
            '', '|Gap rule|Prior-close definition|Final trades|Gross pts|Net2 pts|Net5 pts|Net2 95% interval|',
            '|---|---|---:|---:|---:|---:|---|']
    for r in gap_metrics:
        if r['split']=='holdout':
            vals=[f"{r[k]:.2f}" if r[k] is not None else 'NA' for k in ['gross_mean','net2_mean','net5_mean']]
            ci=f"{r['net2_ci_low']:.2f} to {r['net2_ci_high']:.2f}" if r['net2_ci_low'] is not None else 'NA'
            lines.append('|'+ '|'.join([r['mode'],r['definition'],str(r['n']),*vals,ci])+'|')
    lines += [
            '', '## Captured dashboard observations',
            f"The frozen database contains {len(obs):,} records across {obs.factor_id.nunique()} factors, captured {obs_audit['first_capture']} through {obs_audit['last_capture']}. Only {audit['sessions_with_any_captured_factor']} replay sessions fall after initial capture and have any previously captured factor; freshness varies, including stale values after collection stopped.",
            'Historical joins first require observed_at <= decision and reported_at <= decision when present, then select the latest reporting period/revision. A June reporting label collected in October remains unavailable to June decisions. Future source timestamps are delayed until that timestamp. All revisions are retained in feature-observations.json.',
            'Captured PCR, IV, max-pain and cash-flow values are exported with both availability age and reported-data age, plus observation keys. They were not used as broad-history trading filters: the capture window is too short, and each series still needs semantic freshness/publication review. A newly captured old reporting period is still old data. These columns can be arbitrarily stale; both ages must be checked before execution.',
            '', 'The application latest()/history() dashboard helpers do not themselves enforce historical information availability. This research uses its own explicit selection before revision resolution. Synthetic delayed-publication/revision cases and source-candle prefix tests verify that behavior.',
            '', 'Intervals use 3,000 paired five-session circular moving-block resamples. Filtered-minus-baseline intervals compare per-trade means on the same resampled sessions, retaining the coverage effect. They are conditional on frozen rules and filters, not corrected for the broader strategy/feature search.',
            '', 'Outputs: feature-panel.csv/.sqlite, feature-trade-panel.csv, feature-ablations.csv, feature-audit.json, feature-preregister.json and frozen observation revisions. All results are index points, not option returns.']
    (OUT/'feature-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'panel_rows':len(panel),'checks':len(checks),'captured_sessions':audit['sessions_with_any_captured_factor'],'vix_median':vix_median}))


if __name__=='__main__':main()
