# NIFTY directional strategy laboratory

Frozen research: 458 complete sessions, 2025-01-01 through 2026-11-06; 32518 five-minute bars.
Tested 3600 fixed configurations across 11 families; 185 passed development/validation eligibility.

## Design
Signals are observed at five-minute candle close, entered at the following open, held 15/30/60 minutes and closed by15:10 IST. Exactly one position at a time per configuration; no stop/target or position sizing optimization. Session regimes use only observations available at signal time. EMA/RSI/ATR can retain earlier-session context; breakouts and opening range reset by session. Index volume is never used as traded volume.

{
  "development": {
    "first": "2025-01-01",
    "last": "2026-02-06",
    "sessions": 274
  },
  "validation": {
    "first": "2026-02-09",
    "last": "2026-06-25",
    "sessions": 92
  },
  "holdout": {
    "first": "2026-06-29",
    "last": "2026-11-06",
    "sessions": 92
  }
}

The selection file was written before holdout evaluation: one eligible winner per family, ranked by the minimum of development and validation mean after two illustrative index points. Eligibility requires at least100/30 development/validation trades and positive net2 mean in both. Full holdout grid is disclosed for transparency and MUST NOT become a new selection set.

## Frozen finalists
|Family|Rule|Dev N|Val N|Holdout N|Holdout gross mean pts|Net2|Net5|Net2 block-bootstrap95% CI|
|---|---|---:|---:|---:|---:|---:|---:|---|
|compression_breakout|range3_body0.5 / normal_vol / afternoon / 60m|245|82|85|2.54|0.54|-2.46|-8.88, 11.42|
|donchian|lookback20_buffer0 / trend / afternoon / 60m|130|54|42|8.83|6.83|3.83|-10.19, 25.22|
|ema_reversion|distance3 / normal_vol / midday / 15m|115|39|40|-1.94|-3.94|-6.94|-12.59, 5.10|
|ema_trend|12_26_gap0.5 / trend / afternoon / 60m|194|70|69|9.07|7.07|4.07|-6.34, 21.05|
|failed_breakout|lookback20 / range / all / 60m|148|57|44|-2.33|-4.33|-7.33|-17.19, 7.36|
|gap_fade|gap_atr1 / range / all / 60m|178|74|60|4.10|2.10|-0.90|-8.31, 12.79|
|gap_follow|gap_atr3 / high_vol / all / 60m|112|67|54|-1.28|-3.28|-6.28|-15.45, 8.97|
|momentum|lookback6_atr0.5 / trend / afternoon / 60m|199|80|69|5.18|3.18|0.18|-6.71, 15.31|
|orb|minutes60_buffer0.25 / trend / afternoon / 60m|138|53|55|7.58|5.58|2.58|-8.48, 20.70|
|pullback|ema21_tolerance0.75 / trend / afternoon / 60m|183|69|61|7.42|5.42|2.42|-6.95, 19.55|
|rsi_reversion|rsi40_distance0 / ema_aligned / all / 60m|104|38|41|-9.50|-11.50|-14.50|-27.76, 3.98|

## Interpretation
A positive index-points result does not establish a profitable long-call/long-put strategy. Premium sensitivity to implied volatility, theta, strike, expiry, bid/ask and execution must be tested separately. The five-session moving-block intervals measure uncertainty conditional on these fixed finalists; they do not fully correct the earlier parameter search or a changing market.

No live bot is deployed. A descriptive holdout gate (>=30 trades, net5 positive, and net2 lower CI>0) is a further research filter, never an automatic trading approval.

The holdout is historical, not fully untouched: October2026 was inspected by prior project research. New November sessions are separately disclosed without further selection. Initial DB-only run is preserved in lab-initial-db-run/; this broader run changes data coverage, not the rule grid or selection rule.

## Newly observed November diagnostic
|Family|N|Gross mean index pts|Net2|
|---|---:|---:|---:|
|compression_breakout|5|21.58|19.58|
|donchian|5|34.85|32.85|
|ema_reversion|1|-1.80|-3.80|
|ema_trend|7|39.99|37.99|
|failed_breakout|1|-37.65|-39.65|
|gap_fade|3|-12.98|-14.98|
|gap_follow|4|18.19|16.19|
|momentum|7|14.30|12.30|
|orb|4|34.69|32.69|
|pullback|5|39.18|37.18|
|rsi_reversion|1|-13.10|-15.10|

Only the fixed family finalists are shown; five sessions cannot establish stability. The previous-session15:10 mark used by gap rules is not the official daily close and can span multiple days if a session was excluded.

## Baselines
|Baseline|Hold minutes|Holdout N|Holdout gross pts|Holdout net2 pts|
|---|---:|---:|---:|---:|
|always_up|15|2024|-1.02|-3.02|
|always_up|30|1012|-1.38|-3.38|
|always_up|60|460|-1.10|-3.10|
|always_down|15|2024|1.02|-0.98|
|always_down|30|1012|1.38|-0.62|
|always_down|60|460|1.10|-0.90|
|momentum_30m|15|1932|1.07|-0.93|
|momentum_30m|30|920|2.11|0.11|
|momentum_30m|60|460|5.96|3.96|

## Data and reproducibility
Input SHA256 and exclusions: lab-data-audit.json. 5 feature prefix-invariance tests passed. Every exported entry and exit was asserted against its exact timestamp and holding horizon.

Full ledger: lab-all-configurations.csv; fixed finalist trades: lab-selected-trades.csv; frozen selector: lab-frozen-selection.json; forward-known regime diagnostics: lab-holdout-regimes.csv.
