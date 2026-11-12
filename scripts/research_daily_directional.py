"""Frozen exploratory multi-session NIFTY direction study; not option P&L."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'directional_research'
SEED = 20261109


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def features(raw):
    d = raw.copy()
    prev = d.close.shift()
    tr = pd.concat([d.high-d.low, (d.high-prev).abs(), (d.low-prev).abs()], axis=1).max(axis=1)
    d['atr'] = tr.rolling(14, min_periods=14).mean()
    for span in [5, 10, 20, 30, 50, 200]:
        d[f'ema{span}'] = d.close.ewm(span=span, adjust=False).mean()
    delta = d.close.diff()
    up = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    d['rsi'] = 100*up/(up+down)
    for n in [10, 20, 50]:
        d[f'high{n}'] = d.high.shift().rolling(n, min_periods=n).max()
        d[f'low{n}'] = d.low.shift().rolling(n, min_periods=n).min()
    for n in [5, 10, 20]:
        d[f'mom{n}'] = d.close.diff(n)/d.atr
    return d


def configurations(d):
    rules = []
    def add(family, params, buy, sell):
        rules.append((family, params, np.where(buy, 1, np.where(sell, -1, 0))))
    for fast, slow in [(5,20), (10,30), (20,50), (50,200)]:
        gap = (d[f'ema{fast}']-d[f'ema{slow}'])/d.atr
        for threshold in [0, .5]:
            add('ema_trend', f'{fast}_{slow}_gap{threshold}', gap>threshold, gap<-threshold)
    for n in [10,20,50]:
        for buffer in [0,.25]:
            add('donchian', f'lookback{n}_buffer{buffer}', d.close>d[f'high{n}']+buffer*d.atr, d.close<d[f'low{n}']-buffer*d.atr)
    for n in [5,10,20]:
        for threshold in [0,1]:
            add('momentum', f'lookback{n}_atr{threshold}', d[f'mom{n}']>threshold, d[f'mom{n}']<-threshold)
    for threshold in [20,30,40]:
        add('rsi_reversion', f'rsi{threshold}', d.rsi<threshold, d.rsi>100-threshold)
    configs = []
    for family, params, side in rules:
        filters = {'none': np.ones(len(d), bool), 'ema_aligned': side*(d.ema20-d.ema50)>0, 'long_only': side>0}
        for filter_name, mask in filters.items():
            signal = np.where(mask & d.atr.gt(0), side, 0)
            for hold in [1,3,5]:
                name = f'{family}|{params}|{filter_name}|h{hold}'
                configs.append((name, family, params, filter_name, hold, signal))
    return configs


def trades(d, signal, hold, start, stop):
    rows = []
    last_exit = -1
    for i in range(start, stop):
        j = i+hold
        if not signal[i] or i<last_exit or j>=stop:
            continue
        entry = float(d.open.iloc[i+1]); price = float(d.close.iloc[j]); side = int(signal[i])
        underlying = (price/entry-1)*10000
        rows.append({'signal_i': i, 'entry_i': i+1, 'exit_i': j,
                     'signal_date': d.day.iloc[i], 'entry_date': d.day.iloc[i+1], 'exit_date': d.day.iloc[j],
                     'side': side, 'entry': entry, 'exit': price,
                     'gross_bps': side*underlying, 'net5_bps': side*underlying-5,
                     'net10_bps': side*underlying-10, 'matched_long_gross_bps': underlying,
                     'excess_vs_matched_long_bps': (side-1)*underlying})
        last_exit = j
    return rows


def stats(rows):
    if not rows:
        return {'n': 0, 'gross_bps': None, 'net5_bps': None, 'net10_bps': None, 'win_pct': None, 'excess_vs_matched_long_bps': None}
    p = np.array([r['gross_bps'] for r in rows])
    return {'n': len(rows), 'gross_bps': float(p.mean()), 'net5_bps': float(p.mean()-5),
            'net10_bps': float(p.mean()-10), 'win_pct': float((p>0).mean()*100),
            'excess_vs_matched_long_bps': float(np.mean([r['excess_vs_matched_long_bps'] for r in rows]))}


def intervals(rows, start, stop):
    # Preserve clusters of entry dates; resample 10 consecutive research sessions.
    count = np.zeros(stop-start)
    pnl = np.zeros(stop-start)
    excess = np.zeros(stop-start)
    for r in rows:
        i = r['entry_i']-start
        count[i] += 1; pnl[i] += r['net5_bps']; excess[i] += r['excess_vs_matched_long_bps']
    rng = np.random.default_rng(SEED)
    length = len(count); block = 10
    indices = (rng.integers(0, length-block+1, (3000, int(np.ceil(length/block)), 1)) + np.arange(block)).reshape(3000, -1)[:, :length]
    denominators = count[indices].sum(axis=1)
    good = denominators>0
    def ci(values):
        return np.quantile(values[indices].sum(axis=1)[good]/denominators[good], [.025,.975]).tolist() if good.any() else [None,None]
    return {'net5_ci95_bps': ci(pnl), 'excess_ci95_bps': ci(excess)}


def main():
    path = OUT/'nifty-upstox-1day.json'
    raw = pd.DataFrame(json.loads(path.read_text()))
    raw['day'] = raw.ts.str[:10]
    raw = raw.sort_values('day', kind='stable').reset_index(drop=True)
    assert not raw.day.duplicated().any(), 'Duplicate sessions'
    assert np.isfinite(raw[['open','high','low','close']]).all().all()
    assert (raw.low>0).all() and (raw.high>=raw[['open','close','low']].max(axis=1)).all() and (raw.low<=raw[['open','close','high']].min(axis=1)).all()
    full = features(raw)
    prefix_checks = []
    for n in [210,501,1001,1701,len(raw)-1]:
        pd.testing.assert_frame_equal(full.iloc[:n], features(raw.iloc[:n]), check_exact=True)
        prefix_checks.append(n)
    d = full.iloc[200:].reset_index(drop=True)
    n = len(d); a = int(n*.6); b = int(n*.8)
    parts = {'development': (0,a), 'validation': (a,b), 'holdout': (b,n)}
    coverage = {k:{'first': d.day.iloc[lo], 'last': d.day.iloc[hi-1], 'sessions': hi-lo} for k,(lo,hi) in parts.items()}
    configs = configurations(d)
    save('daily-preregister.json', {'data_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'configuration_count':len(configs),
        'splits':coverage, 'warmup_sessions':200, 'holds_sessions':[1,3,5], 'friction_round_trip_index_bps':[0,5,10],
        'entry':'Next observed session open after closing signal', 'exit':'Close of holding session; trades crossing partition boundaries are excluded',
        'selection':'One per family; dev>=50,val>=20,dev and val net5>0; rank min(dev net5,val net5). Holdout not used.',
        'bootstrap':'3000 moving ten-session blocks, indexed by entry session; conditional, no multiplicity adjustment',
        'seed':SEED, 'special_sessions':'Included as published daily observations; a session need not have regular duration'})
    table = []
    for name,family,params,filter_name,hold,signal in configs:
        record = {'name':name,'family':family,'params':params,'filter':filter_name,'hold_sessions':hold}
        for part in ['development','validation']:
            lo,hi = parts[part]
            record.update({f'{part}_{k}':v for k,v in stats(trades(d,signal,hold,lo,hi)).items()})
        record['eligible'] = record['development_n']>=50 and record['validation_n']>=20 and record['development_net5_bps']>0 and record['validation_net5_bps']>0
        record['selection_score'] = min(record['development_net5_bps'],record['validation_net5_bps']) if record['eligible'] else None
        table.append(record)
    eligible = sorted((r for r in table if r['eligible']),key=lambda r:(-r['selection_score'],r['name']))
    chosen = []
    for row in eligible:
        if row['family'] not in [r['family'] for r in chosen]:
            chosen.append(dict(row))
    save('daily-frozen-selection.json', chosen)
    names = {r['name'] for r in chosen}
    exported = []; finalists = []; verification = 0
    for record,config in zip(table,configs):
        name,family,params,filter_name,hold,signal = config
        lo,hi = parts['holdout']
        held = trades(d,signal,hold,lo,hi)
        record.update({f'holdout_{k}':v for k,v in stats(held).items()})
        if name not in names:
            continue
        result = {**record,**intervals(held,lo,hi)}
        result['descriptive_gate'] = result['holdout_n']>=30 and result['holdout_net10_bps']>0 and result['net5_ci95_bps'][0]>0
        finalists.append(result)
        for part,(lo,hi) in parts.items():
            rows = trades(d,signal,hold,lo,hi)
            previous_exit = -1
            for r in rows:
                assert r['entry_i']==r['signal_i']+1 and r['exit_i']-r['entry_i']+1==hold
                assert lo<=r['signal_i']<r['entry_i']<=r['exit_i']<hi
                assert r['entry_i']>previous_exit
                assert r['entry']==float(d.open.iloc[r['entry_i']]) and r['exit']==float(d.close.iloc[r['exit_i']])
                assert abs(r['gross_bps']-r['side']*(r['exit']/r['entry']-1)*10000)<1e-8
                exported.append({'strategy':name,'split':part,**r}); previous_exit = r['exit_i']; verification+=5
    baselines = []
    for direction in [1,-1]:
        for hold in [1,3,5]:
            lo,hi=parts['holdout']; rows=trades(d,np.full(n,direction),hold,lo,hi)
            baselines.append({'name':'always_long' if direction==1 else 'always_short','hold_sessions':hold,**stats(rows),**intervals(rows,lo,hi)})
    summary = {'splits':coverage,'configuration_count':len(configs),'eligible':len(eligible),'finalists':finalists,'baselines':baselines,
               'prefix_tests':len(prefix_checks),'trade_assertions_passed':verification,
               'descriptive_pass_count':sum(r['descriptive_gate'] for r in finalists)}
    save('daily-summary.json',summary)
    pd.DataFrame(table).to_csv(OUT/'daily-all-configurations.csv',index=False)
    pd.DataFrame(exported).to_csv(OUT/'daily-selected-trades.csv',index=False)
    lines=['# Multi-session NIFTY directional study','',
           f"{len(raw)} daily observations (2017-01-02 to 2026-11-08); 200 sessions reserved for warmup. {len(configs)} configurations across four families; {len(eligible)} development/validation eligible; {len(finalists)} frozen finalists.",
           '', 'Signals use completed daily bars; entry is next observed session open and exit is the close after 1, 3 or 5 sessions. Special sessions are included as published. No compounding, position sizing, stops or premium simulation. Index basis points (bps), not option returns; 5/10 bps friction is illustrative, not actual trading fees. Trades spanning chronological partitions are excluded.',
           '', '|Partition|First|Last|Sessions|','|---|---|---|---:|']
    for part,v in coverage.items(): lines.append(f"|{part}|{v['first']}|{v['last']}|{v['sessions']}|")
    lines+=['','One winner per family selected solely by development/validation net5 means, requiring at least 50/20 trades and positive means in both. Historical holdout was not used to choose rules; it is not a prospective test and overlaps other inspected project history. Full grid publication is not permission to reselect using holdout.',
            '', '|Family|Frozen rule|Hold sessions|Final N|Gross bps|Net5 bps|Net10 bps|Net5 95% block interval|Matched-long excess bps|',
            '|---|---|---:|---:|---:|---:|---:|---|---:|']
    for r in finalists:
        ci=r['net5_ci95_bps']
        lines.append(f"|{r['family']}|{r['params']} / {r['filter']}|{r['hold_sessions']}|{r['holdout_n']}|{r['holdout_gross_bps']:.2f}|{r['holdout_net5_bps']:.2f}|{r['holdout_net10_bps']:.2f}|{ci[0]:.2f}, {ci[1]:.2f}|{r['holdout_excess_vs_matched_long_bps']:.2f}|")
    lines+=['','Matched-long excess compares every selected entry/exit with buying the index at those identical times. Long-only rules necessarily have zero matched-long excess; this is a control for direction choice, not a complete test of entry timing skill.',
            '', '|Baseline|Hold sessions|Final N|Gross bps|Net5 bps|Net5 95% interval|','|---|---:|---:|---:|---:|---|']
    for r in baselines:
        ci=r['net5_ci95_bps']; lines.append(f"|{r['name']}|{r['hold_sessions']}|{r['n']}|{r['gross_bps']:.2f}|{r['net5_bps']:.2f}|{ci[0]:.2f}, {ci[1]:.2f}|")
    lines+=['',f"Descriptive gate passes: {summary['descriptive_pass_count']} (final N>=30, net10>0, lower net5 interval>0). This is not a multiple-testing-adjusted result or a trading approval. {len(prefix_checks)} feature-prefix tests and {verification} exact timestamp/price/duration/nonoverlap/PnL assertions passed.",
            '', 'Interval estimates use 3,000 ten-session moving-block resamples by entry date. Weekly/monthly option expiries still require exact premiums, contemporaneous contract choice, IV, spreads and dated fees. No return or edge is established for options by this file.']
    (OUT/'daily-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'configs':len(configs),'eligible':len(eligible),'finalists':len(finalists),'gate_passes':summary['descriptive_pass_count'],'prefix_tests':len(prefix_checks),'trade_assertions':verification}))


if __name__=='__main__':
    main()
