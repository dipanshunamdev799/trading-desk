"""Earlier-regime replication and fixed 10/20-session extensions of daily rules."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import research_daily_directional as base
OUT=ROOT/'artifacts'/'directional_research_phase2'


def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')


def bootstrap(rows,start,stop):
    n=stop-start;count=np.zeros(n);net=np.zeros(n);excess=np.zeros(n)
    for r in rows:
        j=r['entry_i']-start;count[j]+=1;net[j]+=r['net10_bps'];excess[j]+=r['excess_vs_matched_long_bps']
    rng=np.random.default_rng(20261109);block=min(60,n);net_samples=[];excess_samples=[]
    for _ in range(3000):
        starts=rng.integers(0,n,int(np.ceil(n/block)))
        idx=((starts[:,None]+np.arange(block))%n).ravel()[:n];den=count[idx].sum()
        if den:net_samples.append(net[idx].sum()/den);excess_samples.append(excess[idx].sum()/den)
    return {'net10_ci95_bps':np.quantile(net_samples,[.025,.975]).tolist() if net_samples else [None,None],
            'excess_ci95_bps':np.quantile(excess_samples,[.025,.975]).tolist() if excess_samples else [None,None]}


def main():
    paths=[OUT/'expanded-nifty-1day.json',ROOT/'artifacts'/'directional_research'/'nifty-upstox-1day.json']
    raw=pd.concat([pd.DataFrame(json.loads(p.read_text())) for p in paths],ignore_index=True)
    raw['day']=raw.ts.str[:10];raw=raw.sort_values('day',kind='stable').reset_index(drop=True)
    assert not raw.day.duplicated().any()
    good=np.isfinite(raw[['open','high','low','close']]).all(axis=1)&raw.low.gt(0)&raw.high.ge(raw[['open','close','low']].max(axis=1))&raw.low.le(raw[['open','close','high']].min(axis=1))
    bad=raw.loc[~good,'day'].tolist();raw=raw[good].reset_index(drop=True)
    f=base.features(raw)
    for n in [201,1001,3001,len(raw)-3]:pd.testing.assert_frame_equal(f.iloc[:n],base.features(raw.iloc[:n]),check_exact=True)
    d=f.iloc[252:].reset_index(drop=True)
    selections=json.loads((ROOT/'artifacts'/'directional_research'/'daily-frozen-selection.json').read_text())
    configs=base.configurations(d);byname={c[0]:c for c in configs}
    experiments=[]
    for selected in selections:
        config=byname[selected['name']]
        for h in [1,3,5,10,20]:experiments.append((selected['family']+'|'+selected['params']+'|'+selected['filter']+f'|h{h}',selected['family'],h,config[-1]))
    baselines={'always_long':np.ones(len(d),dtype=int),'always_short':-np.ones(len(d),dtype=int),
               'momentum252':np.sign(f.close-f.close.shift(252)).iloc[252:].fillna(0).to_numpy(dtype=int)}
    for name,signal in baselines.items():
        for h in [1,3,5,10,20]:experiments.append((name+f'|h{h}','baseline',h,signal))
    masks={'backward_2000_2016':d.day<'2017-01-01','previously_used_2017_2024':(d.day>='2017-01-01')&(d.day<'2025-01-16'),'historical_final_2025_2026':d.day>='2025-01-16'}
    parts={name:(int(np.flatnonzero(mask)[0]),int(np.flatnonzero(mask)[-1])+1) for name,mask in masks.items()}
    save('long-preregister.json',{'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'rules':[e[0] for e in experiments], 'original_frozen_selector':'artifacts/directional_research/daily-frozen-selection.json',
        'selection':'No additional selection. All four previously selected parameter sets evaluated at all five horizons; 3 fixed baselines.',
        'caveat':'Earlier dates are backward replication, not prospective evidence; 10/20-session extensions are exploratory on already inspected historical periods.',
        'bootstrap':'3000 circular moving60-session blocks; conditional intervals, no search adjustment',
        'excluded_invalid_daily_dates':bad,'data_first':raw.day.iloc[0],'data_last':raw.day.iloc[-1],'daily_bars':len(raw)})
    summaries=[];ledger=[];checks=0
    for name,family,h,signal in experiments:
        for period,(lo,hi) in parts.items():
            rows=base.trades(d,signal,h,lo,hi)
            result={'rule':name,'family':family,'hold_sessions':h,'period':period,'first':d.day.iloc[lo],'last':d.day.iloc[hi-1],**base.stats(rows),**bootstrap(rows,lo,hi)}
            # Bonferroni across35 fixed rules would need wider intervals; no significance gate here.
            summaries.append(result);previous=-1
            for row in rows:
                assert row['entry_i']>previous and row['exit_i']<hi
                assert row['exit_i']-row['entry_i']+1==h
                assert np.isclose(row['gross_bps'],row['side']*(row['exit']/row['entry']-1)*10000)
                ledger.append({'rule':name,'period':period,**row});previous=row['exit_i'];checks+=3
    pd.DataFrame(summaries).to_csv(OUT/'long-results.csv',index=False)
    pd.DataFrame(ledger).to_csv(OUT/'long-trades.csv',index=False)
    save('long-summary.json',{'daily_bars':len(raw),'first':raw.day.iloc[0],'last':raw.day.iloc[-1],
        'rules':len(experiments),'prefix_checks':4,'trade_assertions':checks,'results':summaries})
    lines=['# Fixed longer-horizon and earlier-regime research','',
        f"{len(raw)} daily observations from {raw.day.iloc[0]} to {raw.day.iloc[-1]}. Four previously selected daily parameter sets, five fixed horizons (1/3/5/10/20 sessions), three baselines:35 rules, no new selection.",
        '', 'Signals at completed daily close; entry next observed session open; fixed exit close; no overlapping positions within a rule. Trades spanning a period boundary are excluded. Returns are underlying index basis points per trade after10 illustrative bps round-trip friction, not option premium or account returns.',
        '', 'Older2000–2016 observations provide backward replication. They are not a forward holdout for rules selected from2017–2025. The10/20-session extensions are exploratory and do not make weekly/monthly options profitable by inference. A20-session position can require a different expiry and includes overnight exposure. Some earliest index history predates the relevant options market.',
        '', '|Rule|Period|Hold|N|Net10bps|95% conditional interval|Excess versus matched long|', '|---|---|---:|---:|---:|---|---:|']
    for r in summaries:
        if r['hold_sessions'] not in [10,20] or r['period']=='previously_used_2017_2024':continue
        ci=r['net10_ci95_bps'];label=r['rule'].replace('|',' / ');lines.append(f"|{label}|{r['period']}|{r['hold_sessions']}|{r['n']}|{r['net10_bps']:.2f}|{ci[0]:.2f} to {ci[1]:.2f}|{r['excess_vs_matched_long_bps']:.2f}|")
    lines+=['',f"Four feature-prefix checks and {checks} price/holding/nonoverlap assertions passed. All105 rule-period results are in long-results.csv; the full ledger is in long-trades.csv. Intervals use3000 moving60-session blocks and are not adjusted for prior or present searches. Compare baselines and dependence on market drift before interpreting positive averages."]
    (OUT/'long-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'daily_bars':len(raw),'rules':len(experiments),'results':len(summaries),'trade_assertions':checks,'excluded_invalid_dates':bad}))


if __name__=='__main__':main()
