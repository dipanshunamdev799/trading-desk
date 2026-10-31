"""Unit tests for premium-adjusted P&L engine (no market data required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from nifty_max_pain import compute_max_pain, compute_premium_pnl, premium_pnl_scenarios  # noqa: E402

def approx(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(b))


def main() -> int:
    fails = 0

    # Test 1: Call expires worthless (short call keeps premium)
    r = compute_premium_pnl([24000], [1000], [0], [100.0], [0.0], lot_size=1, candidates=[23900])
    exp = 100.0 - max(23900 - 24000, 0)
    got = r.call_pnl[0] / (1000 * 1)
    if not approx(got, exp):
        print("FAIL T1", got, exp); fails += 1
    else:
        print("PASS T1 call worthless", got)

    # Test 2: Call ITM
    r = compute_premium_pnl([24000], [1000], [0], [100.0], [0.0], lot_size=1, candidates=[24200])
    exp = 100.0 - max(24200 - 24000, 0)
    got = r.call_pnl[0] / 1000
    if not approx(got, exp):
        print("FAIL T2", got, exp); fails += 1
    else:
        print("PASS T2 call ITM", got)

    # Test 3: Put worthless
    r = compute_premium_pnl([24000], [0], [800], [0.0], [120.0], lot_size=1, candidates=[24100])
    exp = 120.0 - max(24000 - 24100, 0)
    got = r.put_pnl[0] / 800
    if not approx(got, exp):
        print("FAIL T3", got, exp); fails += 1
    else:
        print("PASS T3 put worthless", got)

    # Test 4: Put ITM
    r = compute_premium_pnl([24000], [0], [800], [0.0], [120.0], lot_size=1, candidates=[23800])
    exp = 120.0 - max(24000 - 23800, 0)
    got = r.put_pnl[0] / 800
    if not approx(got, exp):
        print("FAIL T4", got, exp); fails += 1
    else:
        print("PASS T4 put ITM", got)

    # Test 5: Identity PnL = PremiumValue - P_total, and min PnL == max payout
    strikes = [23000, 23500, 24000, 24500, 25000]
    c_oi = [100, 200, 500, 300, 80]
    p_oi = [90, 250, 480, 220, 70]
    c_pr = [310.0, 180.0, 95.0, 48.0, 22.0]
    p_pr = [25.0, 55.0, 110.0, 210.0, 380.0]
    lot = 65
    pain = compute_max_pain(strikes, c_oi, p_oi, lot_size=lot)
    pnl = compute_premium_pnl(
        strikes, c_oi, p_oi, c_pr, p_pr, lot_size=lot,
        max_pain=pain.strike, candidates=strikes,
    )
    # identity
    for i, s in enumerate(strikes):
        left = pnl.combined_pnl[i]
        right = pnl.premium_value - pain.total_payout[i]
        if not approx(left, right, 1e-6):
            print("FAIL T5 identity", s, left, right); fails += 1
            break
    else:
        print("PASS T5 identity", pnl.premium_value)

    # min PnL price should maximize total payout (opposite of max pain)
    max_payout_s = strikes[int(max(range(len(strikes)), key=lambda i: pain.total_payout[i]))]
    if not approx(pnl.min_pnl_price, max_payout_s):
        print("FAIL T5b min_pnl_price", pnl.min_pnl_price, max_payout_s); fails += 1
    else:
        print("PASS T5b min_pnl_price at max payout", pnl.min_pnl_price, "vs max_pain", pain.strike)

    # Test 6: premium scale shifts vertically, not argmin
    sc = premium_pnl_scenarios(strikes, c_oi, p_oi, c_pr, p_pr, lot_size=lot, candidates=strikes)
    prices = {k: v.min_pnl_price for k, v in sc.items()}
    if len(set(prices.values())) != 1:
        print("FAIL T6 argmin moved", prices); fails += 1
    else:
        print("PASS T6 argmin stable across scenarios", prices["snapshot"])
    # low < snapshot < high combined at same S
    s0 = 0
    if not (sc["low_10pct"].combined_pnl[s0] < sc["snapshot"].combined_pnl[s0] < sc["high_10pct"].combined_pnl[s0]):
        print("FAIL T6b vertical order"); fails += 1
    else:
        print("PASS T6b vertical shift")

    # Test 7: coverage warning for zero premium with OI
    r = compute_premium_pnl([24000], [1000], [0], [0.0], [0.0], lot_size=1, candidates=[24000])
    if not r.warnings:
        print("FAIL T7 expected warning"); fails += 1
    else:
        print("PASS T7 warnings", r.warnings)

    # Test 8: edge minimum warning
    r = compute_premium_pnl(
        [23000, 24000, 25000], [10, 10, 5000], [5000, 10, 10],
        [50, 50, 50], [50, 50, 50], lot_size=1, candidates=[23000, 24000, 25000],
    )
    if not any("edge" in w for w in r.warnings):
        print("FAIL T8 edge warning", r.warnings, r.min_pnl_price); fails += 1
    else:
        print("PASS T8 edge warning")

    # Test 9: buyer PnL is exact negation of seller
    r = compute_premium_pnl(
        [24000], [1000], [800], [100.0], [120.0], lot_size=65, candidates=[23800, 24000, 24200]
    )
    for i in range(3):
        if not approx(float(r.buyer_combined_pnl[i]), float(-r.combined_pnl[i])):
            print("FAIL T9 buyer = -seller", r.buyer_combined_pnl[i], r.combined_pnl[i]); fails += 1
            break
    else:
        print("PASS T9 buyer = -seller")
    # long call keeps intrinsic-prem when ITM
    # S=24200, K=24000, prem=100 => long call unit = 200-100 = +100
    exp_lc = (max(24200 - 24000, 0) - 100.0) * 1000 * 65
    if not approx(float(r.buyer_call_pnl[2]), exp_lc):
        print("FAIL T9b buy call", r.buyer_call_pnl[2], exp_lc); fails += 1
    else:
        print("PASS T9b buy call ITM", r.buyer_call_pnl[2])
    exp_lp = (max(24000 - 23800, 0) - 120.0) * 800 * 65
    if not approx(float(r.buyer_put_pnl[0]), exp_lp):
        print("FAIL T9c buy put", r.buyer_put_pnl[0], exp_lp); fails += 1
    else:
        print("PASS T9c buy put ITM", r.buyer_put_pnl[0])

    print("fails", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
