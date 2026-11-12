"""Independent checks of the batch wrapper and corporate-action cash identity."""
import unittest

import numpy as np
import pandas as pd

from research.swing_discovery.engine import fee_coeff, simulate, simulate_many


def market(stocks=3, periods=45):
    rng = np.random.default_rng(121)
    close = 100 + 20*np.arange(stocks)[:, None] + np.cumsum(rng.normal(0, .7, (stocks, periods)), axis=1)
    opening = close + rng.normal(0, .2, close.shape)
    actual = dict(open=opening, high=np.maximum(opening, close)+1.4,
                  low=np.minimum(opening, close)-1.4, close=close,
                  volume=np.full(close.shape, 1e6))
    shape = close.shape
    return dict(symbols=[f'S{i}' for i in range(stocks)],
                dates=pd.bdate_range('2026-02-02', periods=periods, tz='Asia/Kolkata'),
                actual=actual, neutral=actual, unit_factor=np.ones(shape),
                split_factor=np.ones(shape), dividend=np.zeros(shape),
                liquidity_value=np.full(shape, 1e8), median_volume20=np.full(shape, 1e5))


def signals(panel, variant=0):
    rng = np.random.default_rng(55+variant)
    close = panel['neutral']['close']
    return dict(entry=rng.random(close.shape) < .4,
                exit=rng.random(close.shape) < .12,
                atr=np.full(close.shape, 1.5), level=close-4,
                trail=close-2.5)


def rules(mode='fixed', count=3):
    return [dict(id=f'rule_{i}', initial_capital=100000., risk_fraction=.01,
                 reward=2., stop_atr=2., max_hold_sessions=6, exit=mode,
                 stop_mode='level', buffer=.2, trail_atr=2.,
                 min_turnover=5e7, participation=.01) for i in range(count)]


def action_panel(prices, split=None, dividend=None, unit=None):
    prices = np.asarray(prices, float)[None, :]
    result = market(1, prices.shape[1])
    result['actual'] = dict(open=prices.copy(), high=prices+.5,
                            low=prices-.5, close=prices.copy(), volume=np.full_like(prices, 1e6))
    if split is not None: result['split_factor'][0] = split
    if dividend is not None: result['dividend'][0] = dividend
    if unit is not None: result['unit_factor'][0] = unit
    result['neutral'] = {key: value/result['unit_factor'] if key != 'volume' else value
                         for key, value in result['actual'].items()}
    return result


def action_signal(panel, entry_day=0, level=45., atr=1.):
    shape = panel['actual']['close'].shape
    entry = np.zeros(shape, bool)
    entry[0, entry_day] = True
    return dict(entry=entry, atr=np.full(shape, atr), level=np.full(shape, level))


class DiscoveryBatchTests(unittest.TestCase):
    def assert_result_equal(self, actual, expected):
        np.testing.assert_allclose(actual['stock_equity'], expected['stock_equity'], atol=1e-9, rtol=1e-12)
        pd.testing.assert_series_equal(actual['equity'], expected['equity'])
        pd.testing.assert_series_equal(actual['returns'], expected['returns'])
        pd.testing.assert_frame_equal(actual['stock_metrics'].reset_index(drop=True),
                                      expected['stock_metrics'].reset_index(drop=True))
        if len(actual['trades']) or len(expected['trades']):
            order = ['entry_day', 'exit_day', 'symbol']
            a = actual['trades'].sort_values(order).reset_index(drop=True)
            b = expected['trades'].sort_values(order).reset_index(drop=True)
            # pandas infers StringDtype for scalar journals but object after
            # removing batch prefixes; compare the journal's economic content.
            pd.testing.assert_frame_equal(a, b, check_dtype=False)
        else:
            self.assertTrue(actual['trades'].empty)

    def test_batch_matches_scalar_all_exit_modes_and_stock_subset(self):
        panel = market()
        sig = [signals(panel, i) for i in range(3)]
        for mode in ['fixed', 'time', 'atr_trail', 'ema', 'macd', 'trend']:
            with self.subTest(mode=mode):
                cfgs = rules(mode)
                start, end = '2026-02-09', '2026-04-03'
                batch = simulate_many(panel, sig, cfgs, start, end, stocks=[2, 0],
                                      slippage_bps=7., cost_multiplier=2., keep_trades=True)
                for cfg, signal in zip(cfgs, sig):
                    scalar = simulate(panel, signal, cfg, start, end, stocks=[2, 0],
                                      slippage_bps=7., cost_multiplier=2., keep_trades=True)
                    self.assert_result_equal(batch[cfg['id']], scalar)

    def test_batch_matches_scalar_with_split_and_dividend(self):
        panel = action_panel([100, 100, 48, 49, 50, 51], split=[1, 1, 2, 1, 1, 1],
                             dividend=[0, 0, 2, 0, 0, 0], unit=[2, 2, 1, 1, 1, 1])
        sig = [action_signal(panel), action_signal(panel, entry_day=2, level=45.)]
        cfgs = rules('time', 2)
        for cost, slip in [(0., 0.), (1., 5.), (3., 20.)]:
            with self.subTest(cost=cost, slip=slip):
                batch = simulate_many(panel, sig, cfgs, '2026-02-02', '2026-02-10',
                                      cost_multiplier=cost, slippage_bps=slip, keep_trades=True)
                for cfg, signal in zip(cfgs, sig):
                    scalar = simulate(panel, signal, cfg, '2026-02-02', '2026-02-10',
                                      cost_multiplier=cost, slippage_bps=slip, keep_trades=True)
                    self.assert_result_equal(batch[cfg['id']], scalar)

    def test_split_and_dividend_preserve_economic_value_and_journal_cash(self):
        panel = action_panel([100, 100, 48, 48], split=[1, 1, 2, 1],
                             dividend=[0, 0, 2, 0], unit=[2, 2, 1, 1])
        cfg = {**rules('time', 1)[0], 'initial_capital':10000., 'risk_fraction':.01, 'buffer':0.}
        run = simulate(panel, action_signal(panel), cfg, '2026-02-02', '2026-02-07',
                       slippage_bps=0., cost_multiplier=0., keep_trades=True)
        trade = run['trades'].iloc[0]
        self.assertEqual(trade.entry_quantity, 10)
        self.assertEqual(trade.quantity, 20)
        self.assertEqual(trade.dividends, 40)
        self.assertEqual(trade.entry_adjusted, 50)
        self.assertEqual(trade.gross_pnl, 0)
        self.assertEqual(trade.net_pnl, 0)
        np.testing.assert_equal(run['stock_equity'], np.full((1, 4), 10000.))

    def test_ex_dividend_day_new_buy_gets_no_entitlement(self):
        panel = action_panel([100, 100, 95, 95], dividend=[0, 0, 5, 0])
        cfg = {**rules('time', 1)[0], 'initial_capital':10000., 'buffer':0.}
        run = simulate(panel, action_signal(panel, entry_day=1, level=90.), cfg,
                       '2026-02-02', '2026-02-07', slippage_bps=0., cost_multiplier=0., keep_trades=True)
        self.assertEqual(run['trades'].iloc[0].dividends, 0)
        self.assertEqual(run['trades'].iloc[0].net_pnl, 0)

    def test_same_day_and_overnight_exit_fees_have_exact_dp_difference(self):
        same_day = action_panel([100, 100, 100])
        overnight = action_panel([100, 100, 100])
        # Fill the same95 stop, once on entry day and once next session.
        same_day['actual']['low'][0, 1] = 95
        same_day['neutral']['low'][0, 1] = 95
        overnight['actual']['low'][0, 2] = 95
        overnight['neutral']['low'][0, 2] = 95
        cfg = {**rules('time', 1)[0], 'initial_capital':100000., 'buffer':0.}
        a = simulate(same_day, action_signal(same_day, level=95.), cfg,
                     '2026-02-02', '2026-02-06', slippage_bps=0., keep_trades=True)['trades'].iloc[0]
        b = simulate(overnight, action_signal(overnight, level=95.), cfg,
                     '2026-02-02', '2026-02-06', slippage_bps=0., keep_trades=True)['trades'].iloc[0]
        self.assertEqual(a.entry_quantity, b.entry_quantity)
        self.assertAlmostEqual(b.fees-a.fees, 23.6)

    def test_realized_journal_pnl_reconciles_after_repeated_trades(self):
        panel = market()
        cfg = rules('fixed', 1)[0]
        result = simulate(panel, signals(panel), cfg, '2026-02-02', '2026-04-08',
                          slippage_bps=5., cost_multiplier=1.5, keep_trades=True)
        pnl = result['trades'].groupby('symbol').net_pnl.sum()
        for _, row in result['stock_metrics'].iterrows():
            self.assertAlmostEqual(row.net_profit, pnl.get(row.symbol, 0.), places=8)
        self.assertAlmostEqual(result['equity'].iloc[-1], cfg['initial_capital']+pnl.sum()/3, places=8)

    def test_fee_schedule_transition_is_by_fill_day(self):
        panel = action_panel([100, 100, 100])
        panel['dates'] = pd.DatetimeIndex(['2026-02-27', '2026-03-02', '2026-03-03'], tz='Asia/Kolkata')
        cfg = {**rules('time', 1)[0], 'initial_capital':100000., 'buffer':0.}
        result = simulate(panel, action_signal(panel, level=95.), cfg,
                          '2026-02-27', '2026-03-04', slippage_bps=0., keep_trades=True)
        trade = result['trades'].iloc[0]
        br, bf = fee_coeff('2026-03-02', True, False)
        sr, sf = fee_coeff('2026-03-03', False, True)
        self.assertAlmostEqual(trade.fees, 100*trade.quantity*(br+sr)+bf+sf)

    def test_current_column_of_already_lagged_liquidity_controls_entry(self):
        panel = action_panel([100, 100, 100])
        # A median at execution t is already based on sessions before t. Do
        # not lag this prepared array again by looking at its t-1 column.
        panel['median_volume20'][0, 1] = 100
        cfg = {**rules('time', 1)[0], 'initial_capital':100000., 'buffer':0.}
        result = simulate(panel, action_signal(panel, level=95.), cfg,
                          '2026-02-02', '2026-02-06', slippage_bps=0., cost_multiplier=0., keep_trades=True)
        self.assertEqual(result['trades'].iloc[0].entry_quantity, 1)
        panel['liquidity_value'][0, 1] = 1e6
        blocked = simulate(panel, action_signal(panel, level=95.), cfg,
                           '2026-02-02', '2026-02-06', slippage_bps=0., cost_multiplier=0., keep_trades=True)
        self.assertTrue(blocked['trades'].empty)

    def test_current_unit_volume_cap_not_split_adjusted_twice(self):
        panel = action_panel([100, 100, 50, 50], split=[1, 1, 2, 1], unit=[2, 2, 1, 1])
        panel['median_volume20'][0, 2] = 100
        cfg = {**rules('time', 1)[0], 'initial_capital':100000., 'buffer':0.}
        result = simulate(panel, action_signal(panel, entry_day=1, level=45.), cfg,
                          '2026-02-02', '2026-02-07', slippage_bps=0., cost_multiplier=0., keep_trades=True)
        # Prepared schema3 median is already100 current shares, not100 old
        # shares. A2:1split must not increase1%of this capacity from1share to2.
        self.assertEqual(result['trades'].iloc[0].entry_quantity, 1)

    def test_batch_rejects_heterogeneous_execution(self):
        panel = market(1, 5)
        cfgs = rules(count=2)
        cfgs[1]['reward'] = 3
        with self.assertRaises(ValueError):
            simulate_many(panel, [signals(panel), signals(panel, 1)], cfgs,
                          '2026-02-02', '2026-02-10')

    def test_batch_empty_date_segment_matches_scalar_error(self):
        panel = market(1, 5)
        with self.assertRaises(ValueError):
            simulate_many(panel, [signals(panel)], rules(count=1),
                          '2027-01-01', '2027-02-01')

    def test_batch_accepts_already_aware_boundaries(self):
        panel = market(1, 5)
        cfg = rules(count=1)[0]
        sig = signals(panel)
        start = pd.Timestamp('2026-02-02', tz='Asia/Kolkata')
        end = pd.Timestamp('2026-02-10', tz='Asia/Kolkata')
        batch = simulate_many(panel, [sig], [cfg], start, end, slippage_bps=2.)
        self.assert_result_equal(batch[cfg['id']], simulate(panel, sig, cfg, start, end))

    def test_batch_rejects_mismatched_signal_and_config_counts(self):
        panel = market(1, 5)
        with self.assertRaises(ValueError):
            simulate_many(panel, [signals(panel), signals(panel, 1)], rules(count=1),
                          '2026-02-02', '2026-02-10')


if __name__ == '__main__':
    unittest.main()
