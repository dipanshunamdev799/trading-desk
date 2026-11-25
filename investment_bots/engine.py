"""Independent implementation of the supplied specifications.

The accounting book is deliberately fractional, exactly as specified. Whole-share
intents are reported separately; they never masquerade as broker fills. No broker
or order-submission module is imported here.
"""
from collections import Counter
from copy import deepcopy
import math
import numpy as np
import pandas as pd

from .catalog import CAPITAL, COST


class DataBlocked(ValueError):
    pass


def is_fund(row):
    symbol, name = str(row.get('symbol', '')).upper(), str(row.get('name', '')).upper()
    return (any(x in symbol for x in ('ETF', 'BEES', 'IETF', 'GOLD', 'LIQUID', 'NIFTY', 'SENSEX'))
            or any(x in name for x in (' ETF', 'FUND', 'EXCHANGE TRADED')))


def features(closes, volumes, instruments, *, start='2025-01-01', end='2026-12-31'):
    """Rows are completed NIFTY sessions; paper defaults retain the frozen window.

    Explicit alternate bounds are used only by separately versioned research.
    """
    closes = closes.loc[start:end]
    volumes = volumes.reindex_like(closes)
    history = closes.notna().cumsum()
    adv = (closes * volumes).rolling(63, min_periods=50).median()
    returns = np.log(closes / closes.shift(1))
    sigma = returns.rolling(42, min_periods=36).std(ddof=1)
    # Causal event-session through event+5 mask. Never inspect future prices.
    large = (closes / closes.shift(1) - 1).abs() > .40
    masked = large.rolling(6, min_periods=1).max().astype(bool)
    allowed = pd.Series({k: not is_fund(instruments[k]) and not instruments[k]['isin'].startswith('INF')
                         for k in closes.columns})
    eligible = (history >= 63) & closes.notna() & (volumes > 0) & adv.notna() & ~masked & allowed
    universe = pd.DataFrame(False, index=closes.index, columns=closes.columns)
    for day in closes.index:
        candidates = adv.loc[day, eligible.loc[day]].sort_values(ascending=False, kind='stable')
        if len(candidates) > 300 and candidates.iloc[299] == candidates.iloc[300]:
            raise DataBlocked(f'universe_ties: {day}')
        keys = candidates.index[:300]
        for key in keys:
            isin = instruments[key]['isin']
            if len(isin) != 12 or not isin.startswith('INE'):
                raise DataBlocked(f'classification: {key}')
        universe.loc[day, keys] = True
    raw = (closes / closes.shift(63) - 1) / (sigma * math.sqrt(63))
    if ((sigma == 0) & universe & (history >= 64)).any().any():
        raise DataBlocked('non_finite_score: zero daily volatility')
    scores = raw.where(universe & (history >= 64))
    if np.isinf(scores.to_numpy()).any():
        raise DataBlocked('non_finite_score')
    return universe, scores


def select(scores, holdings, instruments):
    ranked = sorted((k for k, v in scores.items() if pd.notna(v)), key=lambda k: (-scores[k], k))
    if any(not math.isfinite(scores[k]) for k in ranked):
        raise DataBlocked('non_finite_score')
    if len(ranked) < 20:
        return None
    ranks = {k: i for i, k in enumerate(ranked)}
    sells = [k for k in holdings if ranks.get(k, math.inf) >= 40]
    kept = [k for k in holdings if k not in sells]
    count = Counter(instruments[k].get('industry', 'Other') for k in kept)
    new = []
    for key in ranked:
        if len(kept) + len(new) >= 20:
            break
        industry = instruments[key].get('industry', 'Other')
        if key in holdings or count[industry] >= 6:
            continue
        new.append(key)
        count[industry] += 1
    return sells, kept, new


def fresh_book(capital=CAPITAL):
    return dict(cash=capital, holdings={}, pending_sells=[], pending_buys=[], pending_resize={},
                realized_pnl=0., fees=0.)


def equity(book):
    return book['cash'] + sum(p['value'] for p in book['holdings'].values())


def mark(book, prices):
    for key, p in book['holdings'].items():
        price = prices.get(key)
        if price is not None and math.isfinite(float(price)) and price > 0:
            p['value'] *= price / p['mark']
            p['mark'] = float(price)


def whole_quantity(value, price):
    if not math.isfinite(float(price)) or price <= 0 or not math.isfinite(float(value)):
        return 0
    return max(0, math.floor(value / price))


def auction_gate(q, dec, final=None, stale=False):
    if not math.isfinite(q) or q <= 0 or int(q) != q:
        return 'rejected_order'
    if dec is None:
        return 'unobserved'
    if stale:
        return 'stale_quote'
    iep, ieq = dec.get('iep') or 0, dec.get('ieq') or 0
    if not math.isfinite(iep) or not math.isfinite(ieq) or iep <= 0 or ieq <= 0:
        return 'no_auction_indicated'
    if dec.get('imbalance_market') is None or dec['imbalance_market'] != 0:
        return 'uncertain_market_imbalance'
    if q > .10 * ieq:
        return 'uncertain_size'
    if final is not None:
        volume = final.get('volume') or 0
        if not math.isfinite(volume) or volume <= 0:
            return 'no_auction_final'
        if q > .10 * volume:
            return 'uncertain_size'
    return 'likely'


def target_exposure(shadow_equities):
    if len(shadow_equities) < 21:
        return 1.
    a = np.asarray(shadow_equities[-21:], dtype=float)
    r = a[1:] / a[:-1] - 1
    vol = float(np.std(r, ddof=1)) * math.sqrt(252)
    return min(1., .15 / vol) if math.isfinite(vol) and vol > 0 else 1.


def advance(book, *, day, offset, opens, closes, scores, instruments, exposure=1., overlay=False, gate=None):
    """One completed session: prior intents at open, marking, then close decision."""
    book = deepcopy(book)
    executions, decisions = [], []

    def execution(key, side, amount, price, reason, gate_status='reference'):
        executions.append(dict(instrument_key=key, side=side, reference_amount=amount,
                               reference_quantity=amount / price, price=price, reason=reason,
                               session=day, gate=gate_status, simulated=True,
                               accounting='fractional reference convention', real_orders_submitted=0))

    # Full rank exits before resizes and new buys.
    pending = []
    for intent in book['pending_sells']:
        key = intent['instrument_key']
        if key not in book['holdings']:
            continue
        price = opens.get(key)
        evidence = gate(key, 'SELL', intent['quantity']) if gate else 'reference'
        if not price or not math.isfinite(price) or price <= 0 or evidence not in ('reference', 'likely'):
            pending.append(intent)
            executions.append(dict(instrument_key=key, side='SELL', status='PENDING', gate=evidence, session=day))
            continue
        p = book['holdings'].pop(key)
        value = p['value'] * price / p['mark']
        proceeds = value * (1 - COST)
        book['cash'] += proceeds
        book['realized_pnl'] += proceeds - p['basis']
        book['fees'] += value * COST
        execution(key, 'SELL', value, price, 'rank_exit', evidence)
    book['pending_sells'] = pending
    mark(book, opens)
    eq = equity(book)
    ordered = sorted(book['pending_resize'].items(),
                     key=lambda x: x[1] - book['holdings'].get(x[0], {}).get('value', 0.) / eq)
    for key, weight in ordered:
        p, price = book['holdings'].get(key), opens.get(key)
        if p is None or not price or not math.isfinite(price) or price <= 0:
            continue
        trade = weight * eq - p['value']
        if trade < 0:
            amount = min(-trade, p['value'])
            basis = p['basis'] * amount / p['value']
            p['value'] -= amount
            p['basis'] -= basis
            book['cash'] += amount * (1 - COST)
            book['realized_pnl'] += amount * (1 - COST) - basis
            side = 'SELL'
        else:
            amount = min(trade, book['cash'])
            book['cash'] -= amount
            p['value'] += amount * (1 - COST)
            p['basis'] += amount
            side = 'BUY'
        if amount > 0:
            book['fees'] += amount * COST
            execution(key, side, amount, price, 'exposure_resize')
        if p['value'] <= 1e-10:
            del book['holdings'][key]
    book['pending_resize'] = {}
    eq_open = eq  # frozen sim5: opening equity is fixed before resize costs
    for intent in book['pending_buys']:
        key, weight = intent['instrument_key'], intent['weight']
        price = opens.get(key)
        amount = min(weight * eq_open, book['cash'])
        evidence = gate(key, 'BUY', intent['quantity']) if gate else 'reference'
        reason = ('position_limit' if len(book['holdings']) >= 20 else
                  'already_held' if key in book['holdings'] else
                  'missing_open' if not price or not math.isfinite(price) or price <= 0 else
                  'minimum_buy' if amount < .2 * eq_open / 20 else
                  'fill_not_assumed' if evidence not in ('reference', 'likely') else '')
        if reason:
            executions.append(dict(instrument_key=key, side='BUY', status='DROPPED',
                                   reason=reason, gate=evidence, session=day))
            continue
        book['cash'] -= amount
        book['holdings'][key] = dict(value=amount * (1 - COST), mark=price, basis=amount,
                                     entry_session=day)
        book['fees'] += amount * COST
        execution(key, 'BUY', amount, price, 'new_position', evidence)
    book['pending_buys'] = []
    mark(book, closes)
    eq = equity(book)
    x = sum(p['value'] for p in book['holdings'].values()) / eq
    rebalance = offset >= 0 and offset % 5 == 0
    selection = select(scores, book['holdings'], instruments) if rebalance else None
    if rebalance and selection is not None:
        sells, kept, new = selection
        book['pending_sells'] = [dict(instrument_key=k,
                                      quantity=whole_quantity(book['holdings'][k]['value'], book['holdings'][k]['mark']))
                                  for k in sells]
        book['pending_buys'] = [dict(instrument_key=k, weight=exposure / 20,
                                     quantity=whole_quantity(exposure * eq / 20, closes[k])) for k in new]
        for side, intents in [('SELL', book['pending_sells']), ('BUY', book['pending_buys'])]:
            for order in intents:
                decisions.append(dict(**order, side=side, decision_session=day,
                                      status='INTENDED' if order['quantity'] > 0 else 'REJECTED',
                                      reason='' if order['quantity'] > 0 else 'zero_or_negative_qty'))
    else:
        kept = list(book['holdings'])
    # On a scheduled session with <20 scores the WHOLE decision is skipped.
    if overlay and (not rebalance or selection is not None) and x > 0 and abs(x - exposure) > .10:
        book['pending_resize'] = {k: book['holdings'][k]['value'] / eq * exposure / x for k in kept}
        for key, weight in book['pending_resize'].items():
            delta = weight * eq - book['holdings'][key]['value']
            quantity = whole_quantity(abs(delta), book['holdings'][key]['mark'])
            decisions.append(dict(instrument_key=key, side='BUY' if delta > 0 else 'SELL',
                                  quantity=quantity, target_weight=weight, decision_session=day,
                                  status='INTENDED' if quantity else 'REJECTED', reason='exposure_resize'))
    if book['cash'] < -1e-6 or not math.isfinite(equity(book)):
        raise DataBlocked('invalid_portfolio_state')
    return book, executions, decisions
