r"""Run the frozen two-year MACD/EMA/structure study without placing orders.

PowerShell: .\.venv\Scripts\python.exe scripts\run_swing_research.py
Use --offline to reuse audited local data after the initial fetch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.swing.signals import catalog, make_signals
from research.swing.engine import simulate, transaction_cost, summarize
from research.swing.validation import daily_returns, search_max_t, trade_uncertainty

OUT = ROOT / 'artifacts' / 'swing_research'
EXECUTION_PANELS = {}
PARTS = {'development': ('2024-11-10', '2025-11-10'),
         'validation': ('2025-11-10', '2026-05-10'),
         'final': ('2026-05-10', '2026-11-10')}


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (pd.Timestamp, Path)):
        return str(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def save(name, value):
    path = OUT/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, allow_nan=False), encoding='utf-8')


def write_result(stem, result):
    for key in ['trades', 'equity']:
        frame = result[key]
        if not frame.empty:
            path = OUT/f'{stem}-{key}.csv'
            path.parent.mkdir(parents=True, exist_ok=True)
            frame.to_csv(path, index=key == 'equity')


def metric(result, name, fallback=0):
    value = result['metrics'].get(name, fallback)
    return fallback if value is None or not np.isfinite(value) else value


def executable_config(config, instrument):
    c = dict(config)
    c.update(initial_capital=1_000_000, risk_fraction=.005,
             cost_model='index_proxy' if instrument == 'NIFTY' else 'etf_delivery')
    return c


def evaluate(bars, signals, config, instrument, part, **kwargs):
    start, end = PARTS[part] if isinstance(part, str) else part
    bars = EXECUTION_PANELS.get(instrument, bars)
    return simulate(bars, signals, executable_config(config, instrument), start, end,
                    allow_short=instrument == 'NIFTY', **kwargs)


def random_control(signals, seed, allow_short=True):
    """Randomize side/entry timing within causal eligible-bar universe.

    Keep the realized signal count only as a descriptive exposure control. This
    is not a forward strategy: reference frequency is estimated over the segment.
    Stops use each eligible row's known ATR; the engine enforces capital limits.
    """
    rng = np.random.default_rng(seed)
    s = signals.copy()
    valid = s['atr'].gt(0) & s['close'].notna()
    count = int((s['side'].ne(0) if allow_short else s['side'].gt(0)).sum())
    possible = np.flatnonzero(valid.to_numpy())
    s['side'] = 0
    if count and len(possible):
        take = rng.choice(possible, min(count, len(possible)), replace=False)
        s.iloc[take, s.columns.get_loc('side')] = rng.choice([-1, 1], len(take)) if allow_short else 1
        # No price information can be inferred from an arbitrary stored pivot.
        # make_signals includes close at the decision event for ATR controls.
        if 'close' in s:
            s['stop'] = s['close'] - s['side']*1.5*s['atr']
    return s


def buy_hold(bars, instrument, start, end):
    d = bars.loc[(bars.index >= pd.Timestamp(start, tz='Asia/Kolkata')) &
                 (bars.index < pd.Timestamp(end, tz='Asia/Kolkata'))]
    capital = 1_000_000.
    model = 'index_proxy' if instrument == 'NIFTY' else 'etf_delivery'
    entry = float(d.open.iloc[0])*1.0002
    quantity = int(capital//entry)
    while quantity*entry+transaction_cost(entry, quantity, 'buy', d.index[0], model) > capital:
        quantity -= 1
    opening = transaction_cost(entry, quantity, 'buy', d.index[0], model)
    closing = transaction_cost(float(d.close.iloc[-1])*.9998, quantity, 'sell', d.index[-1], model, True)
    eq = capital-opening+(d.close-entry)*quantity
    eq.iloc[-1] = capital-opening-closing+(float(d.close.iloc[-1])*.9998-entry)*quantity
    return pd.DataFrame({'equity': eq.to_numpy(), 'exposed': True}, index=d.index+pd.Timedelta(minutes=5))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--skip-walkforward', action='store_true')
    parser.add_argument('--limit', type=int, default=0, help='Smoke test only; not final research')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    from research.swing.data import prepare_data
    panels = prepare_data(OUT, as_of='2026-11-10', offline=args.offline)
    for instrument, bars in panels.items():
        special_path = OUT/f'{instrument.lower()}-special-execution.csv'
        if special_path.exists():
            special = pd.read_csv(special_path)
            special['ts'] = pd.to_datetime(special.ts, utc=True).dt.tz_convert('Asia/Kolkata')
            special = special.set_index('ts')
            EXECUTION_PANELS[instrument] = pd.concat([bars, special]).sort_index()
            assert not EXECUTION_PANELS[instrument].index.has_duplicates
        else:
            EXECUTION_PANELS[instrument] = bars
    configs = catalog()
    if args.limit:
        configs = configs[:args.limit]
    config_by_id = {c['id']: c for c in configs}
    assert len(config_by_id) == len(configs), 'Duplicate experiment identifiers'
    primary = 'NIFTYBEES' if 'NIFTYBEES' in panels else 'NIFTY'
    protocol = {
        'created_for': '2026-11-10', 'seed': 20261110,
        'window': ['2024-11-10', '2026-11-10 exclusive'], 'parts': PARTS,
        'primary_instrument': primary, 'configs': configs,
        'instruments': list(panels), 'selection': 'Per family: require >=12 development and >=6 validation trades, positive net expectancy in both; maximize validation expectancy_R with development expectancy_R tie-break. If none eligible, keep most traded validation candidate as rejected diagnostic.',
        'top_three': 'Eligible family finalists ordered by validation expectancy_R, then diagnostic family finalists. Frozen before the final batch.',
        'deployment_gate': '>=20 final trades, positive net expectancy, 95% 10-session block-bootstrap lower expectancy bound >0, validation search max-t adjusted p<=0.05, positive final return under double fees and 5bps/side slippage, positive BANKBEES final expectancy with >=10 trades, positive walk-forward selected policy, and genuinely fresh independent forward validation. Historical final already examined by earlier project; fresh condition cannot pass here.',
        'costs': 'ETF date-aware statutory/broker fees, conservative ETF delivery schedule, 2bps/side slippage; index proxy 5bps/side friction plus2bps slippage, no claim of executable index P&L.',
        'scope': 'A-J and one-component variants; all data and all losing variants retained. No futures roll or option premium reconstruction.',
        'holdout_status': 'Reserved for this run, previously researched in this workspace. Not genuinely untouched. All variant final rows evaluated once after selection freeze for transparent descriptive two-year ledger; no reselection.',
        'warmup': 'Pre-window prices initialize indicators; warmup trades excluded. Special sessions omitted from indicator training but their complete raw bars replay protective orders/next-tradable fills; ordinary stray out-of-session bars excluded.',
        'walkforward': 'Three 9-month training/3-month forward folds ending2026-05-10; choose eligible rule by training expectancy only, never forward performance.',
    }
    save('protocol.json', protocol)
    save('environment.json', {'python': sys.version, 'pandas': pd.__version__,
                             'numpy': np.__version__, 'source_sha256': {
                                 str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (ROOT/'research'/'swing').glob('*.py')}})
    benchmarks = []
    for instrument, bars in panels.items():
        for part, (start, end) in {**PARTS, 'two_year_continuous': ('2024-11-10', '2026-11-10')}.items():
            eq = buy_hold(EXECUTION_PANELS[instrument], instrument, start, end)
            benchmarks.append({'instrument': instrument, 'part': part,
                               **summarize(pd.DataFrame(), eq)})
            if part == 'two_year_continuous':
                eq.to_csv(OUT/f'{instrument}-buy-hold-equity.csv')
    pd.DataFrame(benchmarks).to_csv(OUT/'buy-hold-benchmarks.csv', index=False)
    rows, cache, validation_returns = [], {}, {}
    t0 = time.monotonic()
    for instrument, bars in panels.items():
        for j, c in enumerate(configs):
            s = make_signals(bars, c)
            cache[(instrument, c['id'])] = s
            for part in ['development', 'validation']:
                result = evaluate(bars, s, c, instrument, part)
                rows.append({'instrument': instrument, 'id': c['id'],
                             'family': c['family'], 'part': part, **result['metrics']})
                if instrument == primary and part == 'validation':
                    validation_returns[c['id']] = daily_returns(result['equity'])
            if (j+1) % 20 == 0 or j == len(configs)-1:
                print(f'{instrument} screening {j+1}/{len(configs)} elapsed={time.monotonic()-t0:.1f}s', flush=True)
        pd.DataFrame(rows).to_csv(OUT/'development-validation.csv', index=False)
    ledger = pd.DataFrame(rows)
    primary_rows = ledger[ledger.instrument == primary]
    d = primary_rows[primary_rows.part == 'development'].set_index('id')
    v = primary_rows[primary_rows.part == 'validation'].set_index('id')
    choices = []
    for family in sorted(set(c['family'] for c in configs)):
        ids = [c['id'] for c in configs if c['family'] == family]
        eligible = [i for i in ids if d.loc[i, 'n_trades'] >= 12 and v.loc[i, 'n_trades'] >= 6
                    and d.loc[i, 'expectancy_r'] > 0 and v.loc[i, 'expectancy_r'] > 0]
        pool = eligible or ids
        chosen = max(pool, key=lambda i: ((v.loc[i, 'expectancy_r'] if eligible else v.loc[i, 'n_trades']),
                                         d.loc[i, 'expectancy_r'] if pd.notna(d.loc[i, 'expectancy_r']) else -99))
        choices.append({'id': chosen, 'family': family, 'eligible': bool(eligible),
                        'validation_expectancy_r': v.loc[chosen, 'expectancy_r'],
                        'config': config_by_id[chosen]})
    choices.sort(key=lambda x: (x['eligible'], x['validation_expectancy_r'] if pd.notna(x['validation_expectancy_r']) else -99), reverse=True)
    top3 = choices[:3]
    frozen = {'family_finalists': choices, 'top_three': [x['id'] for x in top3],
              'fixed_baseline': configs[0]['id'], 'frozen_before_final': True}
    save('frozen-selection.json', frozen)
    adjusted = search_max_t(validation_returns)
    save('validation-search-control.json', adjusted)
    # Final batch follows the saved choice. Every grid row remains descriptive;
    # subsequent reporting cannot change candidate selection.
    final_rows, finalist_results = [], {}
    selected_ids = set(x['id'] for x in choices) | {configs[0]['id']}
    for instrument, bars in panels.items():
        for j, c in enumerate(configs):
            result = evaluate(bars, cache[(instrument, c['id'])], c, instrument, 'final')
            row = {'instrument': instrument, 'id': c['id'], 'family': c['family'],
                   'part': 'final', **result['metrics']}
            if c['id'] in selected_ids:
                execution = EXECUTION_PANELS[instrument]
                sessions = execution.loc[(execution.index >= pd.Timestamp(PARTS['final'][0], tz='Asia/Kolkata'))
                                         & (execution.index < pd.Timestamp(PARTS['final'][1], tz='Asia/Kolkata'))].index.normalize().unique()
                row.update(trade_uncertainty(result['trades'], sessions))
                finalist_results[(instrument, c['id'])] = result
                write_result(f'finalists/{instrument}-{c["id"]}-final', result)
            final_rows.append(row)
            if (j+1) % 30 == 0 or j == len(configs)-1:
                print(f'{instrument} final batch {j+1}/{len(configs)}', flush=True)
    final = pd.DataFrame(final_rows)
    final.to_csv(OUT/'final-all-variants-descriptive.csv', index=False)
    pd.concat([ledger, final], ignore_index=True).to_csv(OUT/'all-period-metrics.csv', index=False)
    stress = []
    diagnostics = []
    for instrument, bars in panels.items():
        for choice in choices:
            c = choice['config']
            s = cache[(instrument, c['id'])]
            for label, cm, slip in [('double_fees', 2., 2.), ('severe', 2., 5.)]:
                result = evaluate(bars, s, c, instrument, 'final', cost_multiplier=cm, slippage_bps=slip)
                stress.append({'instrument': instrument, 'id': c['id'], 'stress': label, **result['metrics']})
            # Descriptive full-window run for exact trade/year/regime diagnostics.
            result = evaluate(bars, s, c, instrument, ('2024-11-10', '2026-11-10'))
            write_result(f'finalists/{instrument}-{c["id"]}-two-year', result)
            diagnostics.append({'instrument': instrument, 'id': c['id'], 'part': 'two_year_continuous', **result['metrics']})
        print(f'{instrument} stress/diagnostics complete', flush=True)
    pd.DataFrame(stress).to_csv(OUT/'cost-stress.csv', index=False)
    pd.DataFrame(diagnostics).to_csv(OUT/'finalist-two-year-metrics.csv', index=False)
    # Descriptive randomized timing control on baseline with observable ATR stops.
    controls = []
    for instrument, bars in panels.items():
        for base_id in [configs[0]['id'], 'A_base']:
            if base_id not in config_by_id:
                continue
            base = config_by_id[base_id]
            s = cache[(instrument, base_id)]
            s = s.loc[(s.index >= pd.Timestamp(PARTS['final'][0], tz='Asia/Kolkata')) &
                      (s.index < pd.Timestamp(PARTS['final'][1], tz='Asia/Kolkata'))]
            if 'close' in s:
                for seed in range(20261110, 20261130):
                    r = evaluate(bars, random_control(s, seed, instrument == 'NIFTY'),
                                 {**base, 'stop_mode': 'atr'}, instrument, 'final')
                    controls.append({'instrument': instrument, 'reference_id': base_id, 'seed': seed, **r['metrics']})
    pd.DataFrame(controls).to_csv(OUT/'randomized-controls.csv', index=False)
    folds = [('2024-11-10', '2025-08-10', '2025-11-10'),
             ('2025-02-10', '2025-11-10', '2026-02-10'),
             ('2025-05-10', '2026-02-10', '2026-05-10')]
    wf = []
    if not args.skip_walkforward:
        bars = panels[primary]
        for train_start, test_start, test_end in folds:
            scores = []
            for c in configs:
                r = evaluate(bars, cache[(primary, c['id'])], c, primary, (train_start, test_start))
                if metric(r, 'n_trades') >= 12 and metric(r, 'expectancy_r') > 0:
                    scores.append((metric(r, 'expectancy_r'), c['id']))
            if scores:
                selected = max(scores)[1]
                c = config_by_id[selected]
                r = evaluate(bars, cache[(primary, selected)], c, primary, (test_start, test_end))
                wf.append({'train_start': train_start, 'test_start': test_start, 'test_end': test_end,
                           'id': selected, 'training_expectancy_r': max(scores)[0], **r['metrics']})
                write_result(f'walkforward/{test_start}-{selected}', r)
            else:
                wf.append({'train_start': train_start, 'test_start': test_start, 'test_end': test_end,
                           'id': 'cash_no_eligible_training_strategy', 'n_trades': 0, 'total_return_pct': 0})
            print(f'Walk-forward {test_start} complete', flush=True)
    save('walkforward.json', wf)
    summary = {'configurations': len(configs), 'instruments': list(panels), 'primary': primary,
               'periods': PARTS, 'finalists': choices, 'top_three': [x['id'] for x in top3],
               'elapsed_seconds': time.monotonic()-t0, 'fresh_holdout': False,
               'research_verdict': 'No strategy tested has sufficient evidence of a durable positive edge.'}
    save('summary.json', summary)
    print(json.dumps(clean({k: v for k, v in summary.items() if k != 'finalists'})), flush=True)
    from scripts.extend_swing_evidence import run
    run(OUT)
    from research.swing.finalize import finalize
    finalize(OUT, ROOT)


if __name__ == '__main__':
    main()
