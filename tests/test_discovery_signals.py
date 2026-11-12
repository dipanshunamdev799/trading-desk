import unittest
import numpy as np
import pandas as pd

from research.swing_discovery.signals import (
    build_features, generate, catalog, catalog_manifest, neighbors, _weekly_averages, _divergence,
)


def synthetic_panel(sessions=340, stocks=3):
    rng = np.random.default_rng(731)
    dates = pd.bdate_range('2024-01-01', periods=sessions, tz='Asia/Kolkata')
    t = np.arange(sessions)[None, :]
    base = 100+np.arange(stocks)[:, None]*40+.06*t+5*np.sin(t/8)
    close = base+np.cumsum(rng.normal(0, .6, (stocks, sessions)), axis=1)
    opening = close+rng.normal(0, .4, close.shape)
    high = np.maximum(opening, close)+rng.uniform(.2, 2, close.shape)
    low = np.minimum(opening, close)-rng.uniform(.2, 2, close.shape)
    bars = dict(open=opening, high=high, low=low, close=close,
                volume=rng.uniform(1e6, 3e6, close.shape))
    return dict(symbols=['S'+str(i) for i in range(stocks)], dates=dates,
                neutral=bars, actual={k: v.copy() for k, v in bars.items()},
                unit_factor=np.ones(close.shape), split_factor=np.ones(close.shape),
                dividend=np.zeros(close.shape), nifty=20000.+np.arange(sessions)*3,
                sector=['industrial']*stocks)


def prefix(panel, end):
    return {k: ({a: b[:, :end].copy() for a, b in v.items()} if k in ('neutral', 'actual')
                else v[:end] if k in ('dates', 'nifty')
                else v[:, :end].copy() if isinstance(v, np.ndarray) and v.ndim == 2
                else v.copy() if hasattr(v, 'copy') else v)
            for k, v in panel.items()}


class DiscoverySignalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = synthetic_panel()
        cls.configs = catalog()

    def test_catalog_frozen_mechanisms_and_single_factor_ablations(self):
        self.assertEqual(len(self.configs), 1174)
        self.assertEqual(len({c['id'] for c in self.configs}), len(self.configs))
        families = {c['family'] for c in self.configs}
        self.assertEqual(len(families), 48)
        for family in families:
            members = [c for c in self.configs if c['family'] == family]
            self.assertTrue(any(c['filter'] == 'none' and c['variant'] == 'control' for c in members))
            self.assertEqual({c['filter'] for c in members if c['variant'].startswith('filter_')},
                             {'volume', 'adx', 'rsi', 'volatility', 'market', 'rs', 'breadth', 'sector'})
        for config in self.configs:
            self.assertTrue(all(config[k] == value for k, value in config['params'].items()))
        manifest = catalog_manifest()
        self.assertEqual(manifest['configurations'], len(self.configs))
        self.assertEqual(manifest['counts'], dict(entry_controls=193, filter_ablations=384, execution_ablations=597))

    def test_entire_catalog_generates_valid_panel_arrays(self):
        f = build_features(self.panel)
        shape = self.panel['neutral']['close'].shape
        for config in self.configs:
            with self.subTest(config=config['id']):
                out = generate(self.panel, config, f)
                self.assertEqual(set(out), {'entry', 'exit', 'level', 'atr', 'regime', 'trail'})
                self.assertTrue(all(a.shape == shape for a in out.values()))
                self.assertEqual(out['entry'].dtype, np.dtype(bool))
                self.assertEqual(out['exit'].dtype, np.dtype(bool))
                self.assertFalse(out['entry'][:, :13].any())

    def test_all_family_signals_are_prefix_invariant(self):
        cut = 233  # Wednesday: deliberately ends in an unfinished week.
        short = prefix(self.panel, cut)
        fullf, shortf = build_features(self.panel), build_features(short)
        representatives = {}
        for c in self.configs:
            if c['variant'] == 'control': representatives.setdefault(c['family'], c)
        for c in representatives.values():
            for mode in ('fixed', 'ema', 'macd', 'trend'):
                config = {**c, 'exit': mode}
                a, b = generate(self.panel, config, fullf), generate(short, config, shortf)
                for key in a:
                    with self.subTest(family=c['family'], mode=mode, key=key):
                        np.testing.assert_allclose(a[key][:, :cut], b[key], equal_nan=True)

    def test_weekly_features_use_only_prior_completed_week(self):
        dates = pd.bdate_range('2025-01-06', periods=15)
        close = np.arange(1., 16.)[None, :]
        fast, slow = _weekly_averages(close, dates, 1, 1)
        self.assertTrue(np.isnan(fast[:, :5]).all())
        np.testing.assert_array_equal(fast[:, 5:10], np.full((1, 5), 5.))
        np.testing.assert_array_equal(slow[:, 10:], np.full((1, 5), 10.))
        altered = close.copy(); altered[:, 5:10] = 1e6
        other, _ = _weekly_averages(altered, dates, 1, 1)
        np.testing.assert_array_equal(other[:, 5:10], fast[:, 5:10])
        prefix_fast, _ = _weekly_averages(close[:, :8], dates[:8], 1, 1)
        np.testing.assert_allclose(prefix_fast, fast[:, :8], equal_nan=True)

    def test_future_mutation_cannot_change_any_released_feature(self):
        cut = 217
        changed = prefix(self.panel, len(self.panel['dates']))
        for bars in ('actual', 'neutral'):
            for name in changed[bars]: changed[bars][name][:, cut:] *= 4
        changed['nifty'][cut:] *= .2
        f, g = build_features(self.panel), build_features(changed)
        for key in ('atr', 'rsi', 'adx', 'volume20', 'return20', 'return60', 'breadth', 'sector_momentum',
                    'market50', 'market200', 'market_return60'):
            np.testing.assert_allclose(f[key][..., :cut], g[key][..., :cut], equal_nan=True)

    def test_initial_partial_week_is_withheld_and_special_saturday_is_in_week(self):
        dates = pd.DatetimeIndex(['2025-01-08', '2025-01-09', '2025-01-10', '2025-01-13', '2025-01-14'])
        fast, _ = _weekly_averages(np.arange(1., 6.)[None, :], dates, 1, 1)
        self.assertTrue(np.isnan(fast).all())
        dates = pd.DatetimeIndex(['2025-01-06', '2025-01-10', '2025-01-11', '2025-01-13'])
        fast, _ = _weekly_averages(np.asarray([[1., 5., 6., 7.]]), dates, 1, 1)
        self.assertTrue(np.isnan(fast[:, :3]).all())
        self.assertEqual(fast[0, 3], 6.)

    def test_divergence_uses_same_price_pivot_dates_and_release_event(self):
        # The favorable oscillator reading at the release candle is irrelevant:
        # only oscillator observations at the two confirmed price-pivot dates count.
        oscillator = np.asarray([[0., -5., 0., -3., 100., 100.]])
        s = dict(pivot_low=np.asarray([[np.nan, np.nan, 10., 10., 9., 9.]]),
                 prev_pivot_low=np.asarray([[np.nan, np.nan, np.nan, np.nan, 10., 10.]]),
                 pivot_low_idx=np.asarray([[-1, -1, 1, 1, 3, 3]]),
                 prev_pivot_low_idx=np.asarray([[-1, -1, -1, -1, 1, 1]]),
                 pivot_low_event=np.asarray([[False, False, True, False, True, False]]))
        out = _divergence({}, s, oscillator)
        np.testing.assert_array_equal(out, [[False, False, False, False, True, False]])
        oscillator[0, 3] = -6.
        self.assertFalse(_divergence({}, s, oscillator).any())

    def test_neighbors_are_one_axis_development_only_and_deterministic(self):
        c = next(x for x in self.configs if x['family'] == 'macd_cross' and x['variant'] == 'control')
        result = neighbors(c)
        self.assertTrue(result)
        self.assertEqual(result, neighbors(c))
        self.assertEqual(len({x['id'] for x in result}), len(result))
        for child in result:
            changed = [k for k in child['params'] if child['params'][k] != c['params'].get(k)]
            self.assertEqual(changed, [child['neighbor_axis']])
            self.assertEqual(child['parent_id'], c['id'])
            self.assertEqual(child['selection_scope'], 'development_only')
        for stage in ('validation', 'final'):
            with self.assertRaises(ValueError): neighbors({**c, 'stage': stage})
            with self.assertRaises(ValueError): neighbors({**result[0], 'stage': stage})


if __name__ == '__main__':
    unittest.main()
