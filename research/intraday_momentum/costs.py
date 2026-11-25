"""Pure cash-equity intraday cost and adverse-fill assumptions.

Rates use the current Upstox basic plan and combined NSE exchange/IPFT rate
documented in SOURCES.md. This is an estimate before contract-note rounding,
not an observed historical account plan. No delivery/DP or financing fee applies.
"""
from math import isfinite
from numbers import Integral, Real


def _side(side: str) -> str:
    if not isinstance(side, str) or side.upper() not in ('BUY', 'SELL'):
        raise ValueError('side must be BUY or SELL')
    return side.upper()


def _positive_price(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError('price must be a positive finite number')
    price = float(value)
    if not isfinite(price) or price <= 0:
        raise ValueError('price must be a positive finite number')
    return price


def fees(side: str, price: float, quantity: int) -> dict[str, float]:
    """Estimate one executed order's fees in rupees, without intermediate rounding.

    STT applies to a sell, including a short entry; stamp duty applies to a buy,
    including a short cover. ``exchange_ipft`` is already the combined charge.
    Quantity is a positive integer number of cash-equity shares.
    """
    side = _side(side)
    price = _positive_price(price)
    if isinstance(quantity, bool) or not isinstance(quantity, Integral) or quantity <= 0:
        raise ValueError('quantity must be a positive integer')
    try:
        turnover = price * int(quantity)
    except OverflowError as exc:
        raise ValueError('turnover must be finite') from exc
    if not isfinite(turnover):
        raise ValueError('turnover must be finite')
    brokerage = min(20.0, 0.001 * turnover)
    exchange_ipft = 0.0000307 * turnover
    sebi = 0.000001 * turnover
    gst = 0.18 * (brokerage + exchange_ipft + sebi)
    stt = 0.00025 * turnover if side == 'SELL' else 0.0
    stamp = 0.00003 * turnover if side == 'BUY' else 0.0
    result = dict(brokerage=brokerage, exchange_ipft=exchange_ipft, sebi=sebi,
                  gst=gst, stt=stt, stamp=stamp, dp=0.0)
    result['total'] = sum(result.values())
    result['turnover'] = turnover
    return result


def adverse_price(raw: float, side: str, bps: float) -> float:
    """Raise BUY fills or lower SELL fills by ``bps / 10_000``.

    Zero slippage is valid; 0 <= bps < 10,000 keeps both sides positive.
    Tick rounding and market-depth availability are outside this helper.
    """
    raw = _positive_price(raw)
    side = _side(side)
    if isinstance(bps, bool) or not isinstance(bps, Real):
        raise ValueError('bps must be finite and between 0 inclusive and 10000 exclusive')
    bps = float(bps)
    if not isfinite(bps) or not 0 <= bps < 10000:
        raise ValueError('bps must be finite and between 0 inclusive and 10000 exclusive')
    fill = raw * (1 + (bps / 10000 if side == 'BUY' else -bps / 10000))
    if not isfinite(fill) or fill <= 0:
        raise ValueError('adverse fill must be positive and finite')
    return fill
