"""Synthetic execution/portfolio invariants, independent of historical outcomes."""
from dataclasses import replace
import unittest

import numpy as np
import pandas as pd

from research.intraday_momentum.costs import adverse_price, fees
from research.intraday_momentum.engine import Config, fill_trade, planned_size, run, summarize


TZ = 'Asia/Kolkata'
DAY = '2025-01-02'


def at(clock, day=DAY):
    return pd.Timestamp(day+' '+clock, tz=TZ)


def record(key='A', day=DAY):
    index = pd.date_range(at('09:15', day), at('15:10', day), freq='5min')
    frame = pd.DataFrame(dict(open=100., high=100.2, low=99.8, close=100., volume=1_000_000.), index=index)
    return dict(key=key, symbol=key, day=day, bars=frame)


def signal(key='A', clock='09:30', day=DAY, side=1, score=1.):
    return dict(key=key, mechanism='cross8', known_at=at(clock, day).isoformat(),
                side=side, raw_price=100., move=.08*side, rvol=2., score=score)


def config(**kwargs):
    return replace(Config('cross8', capital=100_000., risk_fraction=.01,
                          daily_loss_fraction=.1, slippage_bps=0., hold_minutes=15), **kwargs)


class FillTests(unittest.TestCase):
    def test_entry_is_next_open_and_time_exit_is_due_open(self):
        r = record()
        # The completed decision candle's extremes must never execute this order.
        r['bars'].loc[at('09:25'), ['high', 'low']] = [110., 90.]
        # Later intrabar extremes at the time-exit bar are unavailable at its open.
        r['bars'].loc[at('09:45'), ['open', 'high', 'low', 'close']] = [100.3, 110., 90., 105.]
        t, tag = fill_trade(r, signal(), 10, config())
        self.assertEqual(tag, 'filled')
        self.assertEqual(pd.Timestamp(t['entry_at']), at('09:30'))
        self.assertEqual(t['entry_price'], 100.)
        self.assertEqual(t['reason'], 'TIME_EXIT')
        self.assertEqual(pd.Timestamp(t['exit_bar_at']), at('09:45'))
        self.assertEqual(pd.Timestamp(t['capital_released_at']), at('09:45'))
        self.assertEqual(t['exit_price'], 100.3)

    def test_same_bar_stop_and_target_use_stop_first(self):
        r = record()
        r['bars'].loc[at('09:30'), ['high', 'low']] = [102., 99.]
        cfg = config(slippage_bps=10.)
        t, _ = fill_trade(r, signal(), 10, cfg)
        self.assertTrue(t['ambiguous'])
        self.assertEqual(t['reason'], 'STOP_FIRST_AMBIGUOUS')
        self.assertAlmostEqual(t['entry_price'], 100.1)
        self.assertAlmostEqual(t['stop_price'], 100.1*.995)
        self.assertAlmostEqual(t['exit_price'], 100.1*.995*.999)
        self.assertEqual(pd.Timestamp(t['capital_released_at']), at('09:35'))

    def test_future_flat_entry_candle_does_not_cancel_the_order(self):
        r = record()
        r['bars'].loc[at('09:30'), ['open', 'high', 'low', 'close']] = 100.
        trade, tag = fill_trade(r, signal(), 10, config())
        self.assertEqual(tag, 'filled')
        self.assertEqual(trade['entry_price'], 100.)
        self.assertEqual(trade['reason'], 'TIME_EXIT')

    def test_gap_through_stop_uses_adverse_open(self):
        r = record()
        r['bars'].loc[at('09:35'), ['open', 'high', 'low', 'close']] = [98.2, 98.4, 98., 98.3]
        t, _ = fill_trade(r, signal(), 10, config(slippage_bps=10.))
        self.assertEqual(t['reason'], 'STOP')
        self.assertFalse(t['ambiguous'])
        self.assertAlmostEqual(t['exit_price'], 98.2*.999)
        self.assertLess(t['exit_price'], t['stop_price'])

    def test_unavailable_entry_is_skipped_and_unavailable_exit_is_explicit(self):
        r = record()
        r['bars'] = r['bars'].drop(at('09:30'))
        self.assertEqual(fill_trade(r, signal(), 10, config()), (None, 'missing_entry_bar'))
        r = record()
        r['bars'] = r['bars'].drop(at('09:45'))
        with self.assertRaisesRegex(ValueError, 'Missing scheduled exit'):
            fill_trade(r, signal(), 10, config())
        r = record()
        r['bars'].loc[at('09:45'), 'volume'] = 0.
        with self.assertRaisesRegex(ValueError, 'zero traded volume'):
            fill_trade(r, signal(), 10, config())

    def test_adverse_entry_gap_is_rejected_instead_of_resized(self):
        r = record()
        r['bars'].loc[at('09:30'), ['open', 'high', 'low', 'close']] = [102., 102.2, 101.8, 102.]
        self.assertEqual(fill_trade(r, signal(), 10, config()), (None, 'beyond_chase_limit'))


class SizingTests(unittest.TestCase):
    def test_integer_quantity_satisfies_cash_risk_fees_and_prior_volume(self):
        cfg = config()
        r = record()
        bar = r['bars'].loc[at('09:25')]
        q = planned_size(signal(), bar, 100_000., 0., 100_000., cfg)
        self.assertIsInstance(q, int)
        self.assertGreater(q, 0)
        worst = 100.*1.005
        stop_fill = worst*.995
        entry_fee = fees('BUY', worst, q)['total']
        exit_fee = fees('SELL', stop_fill, q)['total']
        risk_room = 1000.
        self.assertLessEqual(worst*q+entry_fee, 100_000.+1e-8)
        self.assertLessEqual((worst-stop_fill)*q+entry_fee+exit_fee, risk_room+1e-8)
        self.assertLessEqual(q, int(bar['volume']*.01))
        bigger = q+1
        self.assertTrue(
            bigger > int(bar['volume']*.01)
            or worst*bigger+fees('BUY', worst, bigger)['total'] > 100_000.
            or (worst-stop_fill)*bigger+fees('BUY', worst, bigger)['total']
               + fees('SELL', stop_fill, bigger)['total'] > risk_room)

    def test_future_entry_volume_does_not_resize_the_order(self):
        a = record()
        a['bars'].loc[at('09:25'), 'volume'] = 1000.
        b = dict(a, bars=a['bars'].copy())
        b['bars'].loc[at('09:30'), 'volume'] = 100.
        left = run([a], [signal()], [DAY], config())['trades'][0]
        right = run([b], [signal()], [DAY], config())['trades'][0]
        self.assertEqual(left['quantity'], 10)
        self.assertEqual(right['quantity'], 10)
        self.assertAlmostEqual(left['decision_bar_participation'], .01)
        self.assertAlmostEqual(right['entry_bar_participation'], .1)

    def test_exhausted_daily_risk_and_missing_volume_produce_zero_size(self):
        cfg = config(daily_loss_fraction=.01)
        bar = record()['bars'].loc[at('09:25')].copy()
        self.assertEqual(planned_size(signal(), bar, 100_000., -1000., 100_000., cfg), 0)
        bar['volume'] = 0.
        self.assertEqual(planned_size(signal(), bar, 100_000., 0., 100_000., cfg), 0)

    def test_actual_short_gap_cannot_exceed_stop_risk_just_because_favorable(self):
        r = record()
        r['bars'].loc[at('09:30'), ['open', 'high', 'low', 'close']] = [102., 102.2, 101.8, 102.]
        cfg = config(allow_short=True, risk_fraction=.001)
        result = run([r], [signal(side=-1)], [DAY], cfg)
        # The two-percent higher short entry is favorable directionally, but
        # raises notional stop risk above the precommitted ₹100 budget.
        self.assertFalse(result['trades'])
        self.assertEqual(sum(result['rejections'].values()), 1)

    def test_unaffordable_entry_is_rejected_before_reading_future_exit(self):
        r=record()
        r['bars'].loc[at('09:30'), ['open','high','low','close']]=[102.,102.2,101.8,102.]
        r['bars']=r['bars'].drop(at('09:45'))
        result=run([r],[signal(side=-1)],[DAY],config(allow_short=True,risk_fraction=.001))
        self.assertFalse(result['trades'])
        self.assertEqual(result['rejections'],{'gap_exceeds_planned_risk':1})


class PortfolioTests(unittest.TestCase):
    def test_three_trades_shared_across_symbols_one_position_and_no_reentry(self):
        records = [record(k) for k in 'ABCDE']
        signals = [signal('A', score=1.), signal('B', score=2.),
                   signal('B', '09:45', score=3.), signal('C', '09:45'),
                   signal('D', '10:00'), signal('E', '10:15')]
        result = run(records, signals, [DAY], config())
        self.assertEqual([t['instrument_key'] for t in result['trades']], ['B', 'C', 'D'])
        self.assertEqual(result['daily'][0]['trades'], 3)
        self.assertEqual(result['rejections']['position_already_open'], 1)
        self.assertEqual(result['rejections']['same_symbol_reentry'], 1)
        self.assertEqual(result['rejections']['daily_trade_cap'], 1)
        for left, right in zip(result['trades'], result['trades'][1:]):
            self.assertGreaterEqual(pd.Timestamp(right['entry_at']), pd.Timestamp(left['capital_released_at']))

    def test_short_uses_collateral_and_correct_tax_sides(self):
        result = run([record()], [signal(side=-1)], [DAY], config(allow_short=True, slippage_bps=10.))
        t = result['trades'][0]
        self.assertEqual(t['side'], 'SHORT')
        self.assertLessEqual(t['entry_price']*t['quantity']+t['entry_fee_components']['total'], t['equity_before'])
        self.assertAlmostEqual(t['gross_pnl'], (t['entry_price']-t['exit_price'])*t['quantity'])
        self.assertAlmostEqual(t['entry_fee_components']['stt'], .00025*t['entry_price']*t['quantity'])
        self.assertEqual(t['entry_fee_components']['stamp'], 0.)
        self.assertEqual(t['exit_fee_components']['stt'], 0.)
        self.assertAlmostEqual(t['exit_fee_components']['stamp'], .00003*t['exit_price']*t['quantity'])
        self.assertAlmostEqual(t['equity_after'], 100_000.+t['net_pnl'])
        self.assertLess(t['equity_after'], 100_000.)

    def test_future_stop_does_not_label_an_earlier_signal_as_daily_halt(self):
        first = record('A')
        first['bars'].loc[at('09:40'), ['open', 'high', 'low', 'close']] = [97., 97.3, 96.8, 97.1]
        result = run([first, record('B'), record('C')],
                     [signal('A'), signal('B', '09:35'), signal('C', '09:45')], [DAY],
                     config(hold_minutes=60, risk_fraction=.1, daily_loss_fraction=.001))
        self.assertEqual(len(result['trades']), 1)
        self.assertLess(result['trades'][0]['net_pnl'], -100.)
        self.assertEqual(result['rejections'].get('position_already_open', 0), 1)
        self.assertEqual(result['rejections'].get('daily_loss_budget', 0), 1)

    def test_future_candidates_cannot_change_earlier_trades(self):
        records = [record(k) for k in 'ABC']
        initial = [signal('A'), signal('B', '10:00')]
        before = run(records, initial, [DAY], config())
        extended = run(records, [*initial, signal('C', '10:30', score=1e12)], [DAY], config())
        self.assertEqual(before['trades'], extended['trades'][:2])
        changed = [dict(r, bars=r['bars'].copy()) for r in records]
        for r in changed:
            later = r['bars'].index >= at('11:00')
            r['bars'].loc[later, ['open', 'high', 'low', 'close']] *= 2.
        mutated = run(changed, initial, [DAY], config())
        self.assertEqual(before['trades'], mutated['trades'])

    def test_closed_cashflows_reconcile_across_sessions(self):
        next_day = '2025-01-03'
        records = [record('A'), record('B'), record('A', next_day)]
        first = records[0]
        first['bars'].loc[at('09:35'), 'high'] = 101.5
        result = run(records, [signal('A'), signal('B', '10:00'), signal('A', day=next_day)],
                     [DAY, next_day], config(slippage_bps=10.))
        trades = result['trades']
        net = sum(t['net_pnl'] for t in trades)
        gross = sum(t['gross_pnl'] for t in trades)
        costs = sum(t['fees'] for t in trades)
        self.assertAlmostEqual(net, gross-costs)
        self.assertAlmostEqual(result['daily'][-1]['equity'], 100_000.+net)
        self.assertAlmostEqual(sum(d['pnl'] for d in result['daily']), net)
        self.assertEqual(len(trades), 3)  # Re-entry next session is permitted.
        summary = summarize(result)
        self.assertAlmostEqual(summary['net_pnl'], net)
        self.assertAlmostEqual(summary['fees'], costs)
        self.assertAlmostEqual(summary['total_return'], net/100_000.)
        self.assertTrue(all(np.isfinite(d['equity']) for d in result['daily']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
