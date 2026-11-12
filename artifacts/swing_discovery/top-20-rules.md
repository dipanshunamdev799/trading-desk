# Exact rules for the 20 descriptive leaders

These rules were frozen before final evaluation. The order below is a post-evaluation description, not another parameter selection step. All prices/indicators use neutral split units; order prices use actual contemporaneous share units.

A rejection means abs(low-level)<=zone*ATR, close>level, close>open, and lower wick>=25% of the daily range. EMA/Wilder averages are SMA-seeded; ATR/ADX/RSI use 14 sessions. KAMA efficiency ratio uses trailing displacement/absolute travel with squared fast 2/slow 30 smoothing bounds. Completed weeks release only in the following observed week. Strict pivots require all left/right neighbors and release after the right bars.

## 1. kama_cross

`kama_cross_098a05a5d438` — diagnostic; evidence screen failed.

**Entry:** KAMA 10 crosses above KAMA 30.

**Filter:** stock 60-session return>NIFTY 60-session return

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return 0.006677%; pooled expectancy 0.018206 R; 347 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "efficiency-ratio KAMA cross; rs filter",
  "exit": "fixed",
  "family": "kama_cross",
  "fast": 10,
  "filter": "rs",
  "id": "kama_cross_098a05a5d438",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 10,
    "filter": "rs",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "slow": 30,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "slow": 30,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_rs"
}
```

## 2. ema_cross

`ema_cross_8d2ff7f02140` — diagnostic; evidence screen failed.

**Entry:** EMA 20 crosses above EMA 50.

**Filter:** stock 60-session return>NIFTY 60-session return

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return 0.004651%; pooled expectancy 0.013925 R; 303 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "EMA cross; rs filter",
  "exit": "fixed",
  "family": "ema_cross",
  "fast": 20,
  "filter": "rs",
  "id": "ema_cross_8d2ff7f02140",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 20,
    "filter": "rs",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "slow": 50,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "slow": 50,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_rs"
}
```

## 3. macd_zero_cross

`macd_zero_cross_7cb993665d76` — diagnostic; evidence screen failed.

**Entry:** MACD(12,26,9) crosses above zero.

**Filter:** stock 60-session return>NIFTY 60-session return

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.020555%; pooled expectancy -0.040064 R; 507 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "MACD oscillator zero-line recovery; rs filter",
  "exit": "fixed",
  "family": "macd_zero_cross",
  "fast": 12,
  "filter": "rs",
  "id": "macd_zero_cross_7cb993665d76",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "rs",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_rs"
}
```

## 4. ppo_zero_cross

`ppo_zero_cross_dffda8cb8df2` — diagnostic; evidence screen failed.

**Entry:** PPO(12,26,9) crosses above zero.

**Filter:** stock 60-session return>NIFTY 60-session return

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.020555%; pooled expectancy -0.040064 R; 507 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "PPO oscillator zero-line recovery; rs filter",
  "exit": "fixed",
  "family": "ppo_zero_cross",
  "fast": 12,
  "filter": "rs",
  "id": "ppo_zero_cross_dffda8cb8df2",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "rs",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_rs"
}
```

## 5. ema_pullback

`ema_pullback_5c8277569304` — diagnostic; evidence screen failed.

**Entry:** rejection of EMA 20; EMA 20>EMA 50 and EMA 50>its value 3 sessions earlier.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.002524%; pooled expectancy -0.003023 R; 716 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "EMA pullback; breadth filter",
  "exit": "fixed",
  "family": "ema_pullback",
  "fast": 20,
  "filter": "breadth",
  "id": "ema_pullback_5c8277569304",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 20,
    "filter": "breadth",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "slow": 50,
    "stop_atr": 2.0,
    "stop_mode": "atr",
    "zone": 0.5
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "slow": 50,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth",
  "zone": 0.5
}
```

## 6. hybrid_ribbon_pullback

`hybrid_ribbon_pullback_345d115be690` — diagnostic; evidence screen failed.

**Entry:** rejection of EMA 20; EMA 9>EMA 20>EMA 50 and slow EMA rising over 3 sessions. Zone=0.5 ATR; pivot confirmation=2 bars; MACD parameters=9/50/9 when used.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** A confirmed support, retest, round level or rejection does not prevent the level from breaking. Confirmation and touch rules can reduce sample size; overnight gaps can exceed the intended stop risk. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.003030%; pooled expectancy -0.004429 R; 660 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "ribbon pullback; breadth filter",
  "exit": "fixed",
  "family": "hybrid_ribbon_pullback",
  "fast": 9,
  "filter": "breadth",
  "id": "hybrid_ribbon_pullback_345d115be690",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "middle": 20,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 9,
    "filter": "breadth",
    "max_hold_sessions": 10,
    "middle": 20,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "slow": 50,
    "stop_atr": 2.0,
    "stop_mode": "atr",
    "zone": 0.5
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "slow": 50,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth",
  "zone": 0.5
}
```

## 7. macd_below_zero

`macd_below_zero_9975e2d7b57f` — diagnostic; evidence screen failed.

**Entry:** MACD(12,26,9) crosses above its signal; cross requires today > and previous <= the corresponding reference and line <0.

**Filter:** stock 60-session return>NIFTY 60-session return

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.029015%; pooled expectancy -0.062381 R; 452 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "MACD below-zero crossover reversal; rs filter",
  "exit": "fixed",
  "family": "macd_below_zero",
  "fast": 12,
  "filter": "rs",
  "id": "macd_below_zero_9975e2d7b57f",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "rs",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_rs"
}
```

## 8. ema_ribbon

`ema_ribbon_f4b21f854b81` — diagnostic; evidence screen failed.

**Entry:** new EMA 9>EMA 20>EMA 50 stack with slow EMA rising over 3 sessions.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.010518%; pooled expectancy -0.020183 R; 519 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "new aligned EMA ribbon; breadth filter",
  "exit": "fixed",
  "family": "ema_ribbon",
  "fast": 9,
  "filter": "breadth",
  "id": "ema_ribbon_f4b21f854b81",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "middle": 20,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 9,
    "filter": "breadth",
    "max_hold_sessions": 10,
    "middle": 20,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "slow": 50,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "slow": 50,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth"
}
```

## 9. round_bounce

`round_bounce_315f7e58bebf` — diagnostic; evidence screen failed.

**Entry:** rejection of actual-rupee round support; steps 10 below 100,50 below 500,100 below 1000,500 below 5000,otherwise 1000; convert level into neutral units only afterward. Zone=0.25 ATR; pivot confirmation=2 bars; MACD parameters=12/26/9 when used.

**Filter:** none

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** A confirmed support, retest, round level or rejection does not prevent the level from breaking. Confirmation and touch rules can reduce sample size; overnight gaps can exceed the intended stop risk. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.036415%; pooled expectancy -0.045489 R; 753 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "round bounce",
  "exit": "fixed",
  "family": "round_bounce",
  "filter": "none",
  "id": "round_bounce_315f7e58bebf",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "filter": "none",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "stop_atr": 2.0,
    "stop_mode": "atr",
    "zone": 0.25
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "control",
  "zone": 0.25
}
```

## 10. ppo_below_zero

`ppo_below_zero_135f863def60` — diagnostic; evidence screen failed.

**Entry:** PPO(12,26,9) crosses above its signal; cross requires today > and previous <= the corresponding reference and line <0.

**Filter:** stock 60-session return>NIFTY 60-session return

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.032451%; pooled expectancy -0.069125 R; 455 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "PPO below-zero crossover reversal; rs filter",
  "exit": "fixed",
  "family": "ppo_below_zero",
  "fast": 12,
  "filter": "rs",
  "id": "ppo_below_zero_135f863def60",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "rs",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_rs"
}
```

## 11. hybrid_sweep_reversal

`hybrid_sweep_reversal_b3f456d6c407` — diagnostic; evidence screen failed.

**Entry:** low below released pivot support, close>support and close>open, plus first histogram rise after a non-rising bar. Zone=0.5 ATR; pivot confirmation=2 bars; MACD parameters=12/26/9 when used.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** A confirmed support, retest, round level or rejection does not prevent the level from breaking. Confirmation and touch rules can reduce sample size; overnight gaps can exceed the intended stop risk. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.015845%; pooled expectancy -0.034805 R; 440 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "sweep reversal; breadth filter",
  "exit": "fixed",
  "family": "hybrid_sweep_reversal",
  "fast": 12,
  "filter": "breadth",
  "id": "hybrid_sweep_reversal_b3f456d6c407",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "breadth",
    "max_hold_sessions": 10,
    "pivot": 2,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr",
    "zone": 0.5
  },
  "participation": 0.01,
  "pivot": 2,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth",
  "zone": 0.5
}
```

## 12. kama_reclaim

`kama_reclaim_917b9cb2ef86` — diagnostic; evidence screen failed.

**Entry:** close crosses above KAMA 10; KAMA 10>KAMA 30 and slow KAMA rising over 3 sessions.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.027926%; pooled expectancy -0.034637 R; 753 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "efficiency-ratio KAMA reclaim; breadth filter",
  "exit": "fixed",
  "family": "kama_reclaim",
  "fast": 10,
  "filter": "breadth",
  "id": "kama_reclaim_917b9cb2ef86",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 10,
    "filter": "breadth",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "slow": 30,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "slow": 30,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth"
}
```

## 13. hybrid_reclaim_zero

`hybrid_reclaim_zero_6b5cb38089f8` — diagnostic; evidence screen failed.

**Entry:** close crosses above EMA 20; EMA 20>EMA 50 and EMA 50 rising over 3 sessions; MACD line>0. Zone=0.5 ATR; pivot confirmation=2 bars; MACD parameters=12/26/9 when used.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** A confirmed support, retest, round level or rejection does not prevent the level from breaking. Confirmation and touch rules can reduce sample size; overnight gaps can exceed the intended stop risk. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.010057%; pooled expectancy -0.015314 R; 614 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "reclaim zero; breadth filter",
  "exit": "fixed",
  "family": "hybrid_reclaim_zero",
  "fast": 12,
  "filter": "breadth",
  "id": "hybrid_reclaim_zero_6b5cb38089f8",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "breadth",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth"
}
```

## 14. ema_reclaim

`ema_reclaim_3e0587af88d8` — diagnostic; evidence screen failed.

**Entry:** close crosses above EMA 20; EMA 20>EMA 50 and EMA 50>its value 3 sessions earlier.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.011429%; pooled expectancy -0.015039 R; 695 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "EMA reclaim; breadth filter",
  "exit": "fixed",
  "family": "ema_reclaim",
  "fast": 20,
  "filter": "breadth",
  "id": "ema_reclaim_3e0587af88d8",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 20,
    "filter": "breadth",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "slow": 50,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "slow": 50,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth"
}
```

## 15. anchored_vwap

`anchored_vwap_dcf04a5bf71f` — diagnostic; evidence screen failed.

**Entry:** close crosses above typical-price volume-weighted average anchored at the latest released pivot low; EMA 20>EMA 50 and EMA 50 rising over 3 sessions. Zone=0.5 ATR; pivot confirmation=2 bars; MACD parameters=12/26/9 when used.

**Filter:** at least 50% of finite panel names above EMA 50

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** A confirmed support, retest, round level or rejection does not prevent the level from breaking. Confirmation and touch rules can reduce sample size; overnight gaps can exceed the intended stop risk. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.032135%; pooled expectancy -0.029096 R; 1043 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "anchored vwap; breadth filter",
  "exit": "fixed",
  "family": "anchored_vwap",
  "filter": "breadth",
  "id": "anchored_vwap_dcf04a5bf71f",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "filter": "breadth",
    "max_hold_sessions": 10,
    "pivot": 2,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "pivot": 2,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_breadth"
}
```

## 16. macd_strength_cross

`macd_strength_cross_25d860e37c1e` — diagnostic; evidence screen failed.

**Entry:** MACD(24,52,18) crosses above its signal; cross requires today > and previous <= the corresponding reference, with absolute line-signal separation >= 0.05 ATR-equivalent units.

**Filter:** none

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.017897%; pooled expectancy -0.084469 R; 205 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "MACD ATR-normalized crossover strength",
  "exit": "fixed",
  "family": "macd_strength_cross",
  "fast": 24,
  "filter": "none",
  "id": "macd_strength_cross_25d860e37c1e",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 24,
    "filter": "none",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 18,
    "slow": 52,
    "stop_atr": 2.0,
    "stop_mode": "atr",
    "strength": 0.05
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 18,
  "slow": 52,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "strength": 0.05,
  "variant": "control"
}
```

## 17. previous_week

`previous_week_faa21f7bd4c5` — diagnostic; evidence screen failed.

**Entry:** rejection of previous completed calendar-week low. Zone=0.5 ATR; pivot confirmation=2 bars; MACD parameters=12/26/9 when used.

**Filter:** none

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 20 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** A confirmed support, retest, round level or rejection does not prevent the level from breaking. Confirmation and touch rules can reduce sample size; overnight gaps can exceed the intended stop risk. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.188569%; pooled expectancy -0.089554 R; 1997 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "previous week; max_hold_sessions 20",
  "exit": "fixed",
  "family": "previous_week",
  "filter": "none",
  "id": "previous_week_faa21f7bd4c5",
  "initial_capital": 1000000,
  "max_hold_sessions": 20,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "filter": "none",
    "max_hold_sessions": 20,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "stop_atr": 2.0,
    "stop_mode": "atr",
    "zone": 0.5
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "max_hold_sessions_20",
  "zone": 0.5
}
```

## 18. macd_hist_recovery

`macd_hist_recovery_e758e11f9a78` — diagnostic; evidence screen failed.

**Entry:** MACD(12,26,9) histogram rises after a non-rising bar while still below zero.

**Filter:** signal-day volume >=1.25*mean previous 20 volumes

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.064996%; pooled expectancy -0.064705 R; 972 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "MACD first histogram recovery below zero; volume filter",
  "exit": "fixed",
  "family": "macd_hist_recovery",
  "fast": 12,
  "filter": "volume",
  "id": "macd_hist_recovery_e758e11f9a78",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "volume",
    "max_hold_sessions": 10,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_volume"
}
```

## 19. macd_divergence

`macd_divergence_15d39ae71f5a` — diagnostic; evidence screen failed.

**Entry:** MACD(12,26,9) second released price-pivot low is lower and oscillator at that pivot is higher; strict 2-bar left/right pivots.

**Filter:** stock 60-session return>NIFTY 60-session return

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Pivot confirmation delays the decision; a divergence can persist while price continues against the proposed reversal. Low-frequency divergence events give weak independent sample support. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.016857%; pooled expectancy -0.093677 R; 168 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "MACD released regular bullish divergence; rs filter",
  "exit": "fixed",
  "family": "macd_divergence",
  "fast": 12,
  "filter": "rs",
  "id": "macd_divergence_15d39ae71f5a",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 12,
    "filter": "rs",
    "max_hold_sessions": 10,
    "pivot": 2,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 9,
    "slow": 26,
    "stop_atr": 2.0,
    "stop_mode": "atr"
  },
  "participation": 0.01,
  "pivot": 2,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 9,
  "slow": 26,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "filter_rs"
}
```

## 20. hybrid_divergence_support

`hybrid_divergence_support_79e4331438ba` — diagnostic; evidence screen failed.

**Entry:** released regular bullish price/MACD divergence with pivot support within zone*ATR of clustered support. Zone=0.5 ATR; pivot confirmation=2 bars; MACD parameters=5/13/4 when used.

**Filter:** none

**Initial stop:** entry fill-2.0*decision-day ATR converted to entry-day actual units

**Exit:** fee/slippage-aware fixed 2.0 net R target; next-open time exit after 10 sessions; forced liquidation at segment end

**Sizing:** floor shares to risk at most 0.5% of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1% prepared prior 20 median volume cap; minimum prior 20 median turnover ₹50 m; candidate stop distance 0.5..8 ATR

**Execution:** Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.

**Weaknesses and failure scenarios:** Pivot confirmation delays the decision; a divergence can persist while price continues against the proposed reversal. Low-frequency divergence events give weak independent sample support. Volume, spread and fill assumptions remain model inputs.

**Observed evidence failures:** failed frozen development/validation eligibility; final total_return_pct not positive; final expectancy_r not positive; reserved total_return_pct not positive; reserved expectancy_r not positive; final positive-stock breadth below 50%; double-cost total_return_pct not positive; double-cost expectancy_r not positive; final_return_ci 95_lower_pct not positive; final_net_r_ci 95_lower not positive; validation search-adjusted p above .05 or unavailable

**Final evidence:** Net return -0.038681%; pooled expectancy -0.094164 R; 386 stock trades. Status: diagnostic; evidence screen failed.

**Complete frozen configuration:**

```json
{
  "buffer": 0.2,
  "description": "divergence support",
  "exit": "fixed",
  "family": "hybrid_divergence_support",
  "fast": 5,
  "filter": "none",
  "id": "hybrid_divergence_support_79e4331438ba",
  "initial_capital": 1000000,
  "max_hold_sessions": 10,
  "min_turnover": 50000000,
  "params": {
    "buffer": 0.2,
    "exit": "fixed",
    "fast": 5,
    "filter": "none",
    "max_hold_sessions": 10,
    "pivot": 2,
    "reward": 2.0,
    "risk_fraction": 0.005,
    "signal": 4,
    "slow": 13,
    "stop_atr": 2.0,
    "stop_mode": "atr",
    "zone": 0.5
  },
  "participation": 0.01,
  "pivot": 2,
  "reward": 2.0,
  "risk_fraction": 0.005,
  "signal": 4,
  "slow": 13,
  "stop_atr": 2.0,
  "stop_mode": "atr",
  "variant": "control",
  "zone": 0.5
}
```
