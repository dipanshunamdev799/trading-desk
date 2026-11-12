# Phase1 discovery freeze before backtest implementation

This records the hypothesis space before simulating new strategies. The companion
research notes add source detail; no source is treated as proof of an Indian stock
edge. Every proposed family can fail. Numeric thresholds below define a coherent
coarse screen; development-only neighborhoods investigate useful nearby values.

## Primary sources and what they establish

- Fidelity MACD documentation defines the oscillator/trend signal and its uses:
  https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd
- StockCharts PPO documentation explains price normalization and signal overlap:
  https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo
- StockCharts' own overlay/parameter reference documents KAMA's adaptive role:
  https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays
  https://help.stockcharts.com/charts-and-tools/sharpcharts/sharpcharts-workbench/editing-sharpcharts/sharpcharts-parameter-reference
- Schwab's documented CAM study is a concrete MACD/ADX hybrid precedent:
  https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/C-D/CAM-Indicator
- Osler's New York Fed research motivates separate reversal/breakout and round-
  number hypotheses through order placement in currency markets. Its evidence is
  not direct evidence for Indian equity profitability:
  https://www.newyorkfed.org/research/staff_reports/sr125.html
  https://www.newyorkfed.org/medialibrary/media/research/epr/00v06n2/0007osle.pdf

## MACD/PPO families

Test signal-line crosses, zero crosses, first histogram recovery after declining
momentum, two-bar histogram acceleration, and crossover strength normalized by
ATR. Contrast above-zero continuation with below-zero early reversal. Use both
standard MACD and PPO to distinguish level normalization from trigger timing.

Regular bullish divergence: second confirmed price pivot low is lower, oscillator
value at that pivot is higher. Hidden bullish divergence reverses the price and
oscillator comparisons. Compare oscillator values at the same price-pivot dates,
release only after the second pivot's right-confirmation candles, require distinct
pivots, and avoid searching for a favorable future oscillator extremum. Treat
divergence near confirmed support separately from divergence anywhere.

Explore fast/slow/signal tuples such as5/13/4,8/21/5,12/26/9,16/32/9,24/52/18;
do not assume settings are optimal. PPO signal behavior may be redundant with
MACD in some configurations; identical trading outcomes must not inflate the
count of independent evidence.

## EMA/adaptive-average families

Test fast/slow crosses, price reclaims in a persistent higher trend, pullback/wick
rejection, continuation after contraction, ribbon stacks and slope/ATR magnitude.
Pairs include9/21,20/50,20/100,50/200plus less conventional neighbors. Test aligned
weekly trend with daily entries and a separate EMA-based invalidation exit.

KAMA uses efficiency ratio from trailing absolute displacement divided by sum of
trailing absolute changes; its adaptive smoothing constant is squared between
fast/slow bounds. Compare KAMA reclaim/crossover/pullback with EMA counterparts
instead of claiming adaptivity automatically improves performance. A gap or range
can cause whipsaws; smoothers that avoid them may enter reversals later.

## Structural support/resistance families

1. Confirmed pivot support bounce: strict1/2/3/5right-bar confirmation, not future
   pivots drawn retrospectively. Require price rejection with an explicit wick or
   close condition; zone tolerance0.25/0.5/0.75ATR.
2. Clustered horizontal support: combine previously released pivots only, require
   two or three past touches separated by bars; freeze level when testing entry.
   Contrast multiple-touch criteria against nearest-pivot-only levels.
3. Donchian/price-channel close breakouts:20/55/100lookbacks and0/0.25/0.5ATR
   confirmation buffer. Prior channel excludes the current candle.
4. Breakout/retest/role reversal: close beyond a frozen prior level, subsequent
   retest within a bounded1-5bar window, then rejection or recovery; do not use the
   eventual successful retest to label the initial breakout.
5. False breakout/liquidity-sweep proxies: low trades below a prior support but
   closes back above, optionally with histogram recovery. OHLC does not certify
   actual order-book liquidity, so call the rule a price-sweep proxy.
6. Previous complete day/week/month extrema, floor pivots from prior HLC, and
   higher-timeframe confluence; incomplete current calendar extrema are forbidden.
7. Fibonacci pullbacks from confirmed ordered swing anchors:0.382/0.5/0.618and
   adjacent non-Fibonacci control ratios. A positive generic pullback result does
   not establish a special predictive property of Fibonacci ratios.
8. Psychological round levels computed in actual contemporary rupee share units,
   not globally back-adjusted future split units. Convert levels only after they
   are defined; otherwise a later split changes the historical psychological rule.
9. Causal anchored VWAP from a released pivot is an OHLCV volume-weighted price
   proxy. True volume-profile nodes require trustworthy volume-at-price data and
   remain untested when that data are unavailable.

## Hybrids, regimes and ablations

Separate EMA trend/MACD timing/S&R entry, support bounce plus histogram recovery,
EMA reclaim plus zero regime, breakout plus trend/momentum, divergence plus
support, ribbon plus pullback, and sweep plus reversal. Keep simple family controls
and add one filter at a time: relative volume, ADX14, RSI14, ATR/price regime,
relative strength against NIFTY, market trend, sector-peer momentum or breadth.

Test MACD/EMA as exits independently of their entry role. Initial common execution
uses an ATR stop and fixed netR target; structural stops, ATR trails, EMA/trend
invalidation and time-only exits test specific hypotheses. Typical coarse stop
scales1.5/2/3ATR, rewards1.5/2/3R, and holds5/10/20sessions cover several-day swing
behavior without an unbounded Cartesian search. A confirmed stop can be too far
away, and a price gap can exceed any planned risk.

## Search discipline

Family breadth is justified by different mechanisms, not raw experiment count.
Each family gets common execution plus interpretable component changes. The
coarse grid is frozen before outcomes; promising training neighborhoods receive
predeclared nearby integer/threshold values. Every attempted parameter tuple,
failed configuration and data exclusion is persisted. Validation/final returns
cannot determine a new neighborhood. Repeatedly tuning reused final dates cannot
create an untouched holdout. The research design specifies independent safeguards.
