"""Fixed causal fifteen-minute confirmation and descriptive regime diagnostics."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import research_stronger_controls as controls
import research_directional_lab as lab
OUT=ROOT/'artifacts'/'project_alpha'


def confirmation(raw):
    d=raw.copy();d['bucket']=d.ts.dt.floor('15min')
    agg=d.groupby(['day','bucket']).agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),count=('close','size')).reset_index()
    # Clock09:15 aligns with exchange opening; three exactly contiguous5m bars required.
    agg=agg[agg['count']==3].rename(columns={'bucket':'ts'}).sort_values('ts').reset_index(drop=True)
    agg['known_at']=agg.ts+pd.Timedelta(minutes=15)
    agg['ema4']=agg.close.ewm(span=4,adjust=False).mean();agg['ema9']=agg.close.ewm(span=9,adjust=False).mean()
    agg['direction15']=np.sign(agg.ema4-agg.ema9)
    return agg


def main():
    raw,audit=controls.load('artifacts/directional_research_phase2/expanded-nifty-5minute.json')
    f=lab.features(raw);higher=confirmation(raw)
    protocol={'families':['ema_trend','donchian','pullback'],'comparison':'Unmodified5m entries versus same entries filtered by latest completed15mEMA4/9direction',
        'parameters':'EMA4/9 approximates60/135minutes of context; fixed once, no optimization. Same-day completed15m bars only; EMA retains preceding session context.',
        'scope':'Causal15mconfirmation ablation, not a complete independent15mstrategy family search. Already inspected historical data, no prospective holdout.',
        'data_sha256':hashlib.sha256((ROOT/'artifacts/directional_research_phase2/expanded-nifty-5minute.json').read_bytes()).hexdigest()}
    (OUT/'timeframe-preregister.json').write_text(json.dumps(protocol,indent=2))
    checks=[]
    for cut in [51,1001,len(raw)-4]:
        p=confirmation(raw.iloc[:cut]);expected=higher[higher.known_at<=raw.ts.iloc[cut-1]+pd.Timedelta(minutes=5)]
        pd.testing.assert_frame_equal(p.reset_index(drop=True),expected.reset_index(drop=True),check_dtype=False);checks.append(cut)
    names=['ema_trend|12_26_gap0.5|trend|afternoon|h60','donchian|lookback20_buffer0|trend|afternoon|h60','pullback|ema21_tolerance0.75|trend|afternoon|h60']
    configs={c[0]:c for c in lab.configurations(f)}
    allrows=[];summaries=[]
    for name in names:
        t=lab.trade_rows(f,configs[name][-1],60);rows=[]
        for i,j,side,pnl in t:
            i=int(i);j=int(j);at=f.known_at.iloc[i]
            rows.append({'strategy':name,'known_at':at,'session':f.day.iloc[i],'side':int(side),'gross':pnl,'net2_index_points':pnl-2,
                'entry_at':str(f.ts.iloc[i+1]),'exit_at':str(f.known_at.iloc[j]),'efficiency':f.efficiency.iloc[i],'trend':f.trend.iloc[i]})
        d=pd.DataFrame(rows).sort_values('known_at')
        d=pd.merge_asof(d,higher[['known_at','direction15','day']].sort_values('known_at'),on='known_at',direction='backward',tolerance=pd.Timedelta(minutes=15))
        d['agrees15']=(d.side==d.direction15)&(d.session==d.day)
        for period,mask in [('backward2022_2024',d.session<'2025-01-01'),('historical_final',d.session>='2026-06-29')]:
            b=d[mask]
            for policy,g in [('baseline',b),('confirm15m',b[b.agrees15])]:
                days=sorted(raw.loc[(raw.day<'2025-01-01') if period=='backward2022_2024' else (raw.day>='2026-06-29'),'day'].unique())
                totals=g.groupby('session').net2_index_points.sum().reindex(days,fill_value=0).to_numpy();counts=g.groupby('session').size().reindex(days,fill_value=0).to_numpy()
                rng=np.random.default_rng(20261110);sample=[]
                for _ in range(3000):
                    starts=rng.integers(0,len(days),int(np.ceil(len(days)/5)));idx=((starts[:,None]+np.arange(5))%len(days)).ravel()[:len(days)]
                    if counts[idx].sum():sample.append(totals[idx].sum()/counts[idx].sum())
                ci=np.quantile(sample,[.025,.975]).tolist() if sample else [None,None]
                summaries.append({'strategy':name.split('|')[0],'period':period,'policy':policy,'trades':len(g),'net2_mean':float(g.net2_index_points.mean()),'ci95':ci})
        allrows.extend(d.to_dict('records'))
    pd.DataFrame(allrows).to_csv(OUT/'timeframe-trades.csv',index=False)
    # Forward60m realized-state labels are evaluation outcomes, never classifier inputs.
    labels=[]
    for day,g in f.groupby('day'):
        g=g.reset_index(drop=True)
        for i in range(12,len(g)-12):
            efficiency=float(g.efficiency.iloc[i]);trend=float(g.trend.iloc[i]);pred='trend' if efficiency>=.35 and abs(trend)>=.5 else 'range' if efficiency<.25 else 'transition'
            future=g.close.iloc[i+1:i+13].to_numpy();path=np.r_[g.close.iloc[i],future];den=np.abs(np.diff(path)).sum()
            realized=abs(path[-1]-path[0])/den if den else 0;actual='trend' if realized>=.35 else 'range'
            labels.append({'day':day,'predicted':pred,'future_label':actual,'future_efficiency':realized,'known_at':str(g.known_at.iloc[i])})
    reg=pd.DataFrame(labels);conf=reg.groupby(['predicted','future_label']).size().reset_index(name='count');conf.to_csv(OUT/'regime-confusion.csv',index=False)
    # Descriptive volatility profile; regularresearchwindowonly, no predictive selection.
    f['clock']=f.ts.dt.strftime('%H:%M');f['bar_range']=f.high-f.low;f['absolute_change']=(f.close-f.open).abs()
    season=f.groupby('clock').agg(bars=('close','size'),mean_range=('bar_range','mean'),median_range=('bar_range','median'),mean_absolute_change=('absolute_change','mean'))
    season.to_csv(OUT/'time-of-day-volatility.csv')
    result={'coverage':audit,'prefix_checks':checks,'summaries':summaries,'regime_labels':len(reg),'confusion':conf.to_dict('records'),
        'warning':'Realizedfuture-efficiency labels are diagnostic outcomes, not truth known atdecision; the binarylabel omits direction/events/expiries.'}
    (OUT/'timeframe-summary.json').write_text(json.dumps(result,default=str,indent=2,allow_nan=False))
    lines=['# Fifteen-minute confirmation and regime diagnostics','', 'This is a fixed confirmation ablation of three frozen5mstrategies, not a newly optimized15mstrategy. All history has already been inspected; no new final holdout is claimed.',
        '', '|Rule|Period|Policy|Trades|Net2points|95% conditional interval|','|---|---|---|---:|---:|---|']
    for r in summaries:lines.append(f"|{r['strategy']}|{r['period']}|{r['policy']}|{r['trades']}|{r['net2_mean']:.2f}|{r['ci95'][0]:.2f} to {r['ci95'][1]:.2f}|")
    lines+=['', 'Aggregation requires three complete contiguous5mbars per15mbar; only already closed15mbars enter the confirmation. Signals, price entry/exit and costs remain unchanged. Intervals use3000five-sessionblock samples and are not selection-adjusted.',
        '', 'Regime confusion compares a causal current efficiency/EMA classifier with subsequently realized60mprice-path efficiency. Future labels appear only in evaluation. Imperfect agreement demonstrates the uncertainty of state identification; it is not a causal proof of market-state truth. Confusion counts are exported without training a new classifier.',
        '', 'Time-of-day volatility is a descriptive profile of candle ranges/absolutechanges across regular research windows. It does not establish that options were cheap at those times.',
        '', f'{len(checks)} completed-bar prefix checks passed. All exact trade joins, state confusion and clock profiles are retained.']
    (OUT/'timeframe-report.md').write_text('\n'.join(lines),encoding='utf-8');print(json.dumps({'summaries':len(summaries),'regime_outcomes':len(reg),'prefix_checks':len(checks)}))


if __name__=='__main__':main()
