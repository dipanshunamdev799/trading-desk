# NIFTY directional strategy laboratory

Frozen research: 205 complete sessions, 2026-01-01 through 2026-10-30; 14555 five-minute bars.
Tested 3600 fixed configurations across 11 families; 204 passed development/validation eligibility.

## Design
Signals are observed at five-minute candle close, entered at the following open, held 15/30/60 minutes and closed by15:10 IST. Exactly one position at a time per configuration; no stop/target or position sizing optimization. Session regimes use only observations available at signal time. EMA/RSI/ATR can retain earlier-session context; breakouts and opening range reset by session. Index volume is never used as traded volume.

{
  "development": {
    "first": "2026-01-01",
    "last": "2026-07-03",
    "sessions": 123
  },
  "validation": {
    "first": "2026-07-06",
    "last": "2026-08-31",
    "sessions": 41
  },
  "holdout": {
    "first": "2026-09-01",
    "last": "2026-10-30",
    "sessions": 41
  }
}

The selection file was written before holdout evaluation: one eligible winner per family, ranked by the minimum of development and validation mean after two illustrative index points. Eligibility requires at least100/30 development/validation trades and positive net2 mean in both. Full holdout grid is disclosed for transparency and MUST NOT become a new selection set.

## Frozen finalists
|Family|Rule|Dev N|Val N|Holdout N|Holdout gross mean pts|Net2|Net5|Net2 block-bootstrap95% CI|
|---|---|---:|---:|---:|---:|---:|---:|---|
|compression_breakout|range2_body0.5 / ema_aligned / afternoon / 15m|101|35|26|1.87|-0.13|-3.13|-10.78, 12.70|
|donchian|lookback20_buffer0.25 / ema_aligned / midday / 60m|108|34|34|3.02|1.02|-1.98|-18.98, 23.47|
|ema_reversion|distance1 / range / morning / 15m|150|42|32|1.83|-0.17|-3.17|-8.21, 6.58|
|ema_trend|9_21_gap0.5 / high_vol / all / 60m|178|58|70|-6.57|-8.57|-11.57|-24.44, 10.10|
|failed_breakout|lookback6 / range / all / 60m|218|66|64|-11.40|-13.40|-16.40|-28.05, -1.84|
|gap_follow|gap_atr1 / high_vol / all / 60m|144|51|45|-5.64|-7.64|-10.64|-25.98, 10.50|
|momentum|lookback6_atr1.5 / trend / midday / 60m|105|35|35|1.58|-0.42|-3.42|-21.55, 21.16|
|orb|minutes60_buffer0 / range / afternoon / 30m|176|64|64|0.25|-1.75|-4.75|-10.47, 5.19|
|pullback|ema50_tolerance0.75 / trend / all / 60m|215|70|83|1.19|-0.81|-3.81|-12.77, 10.36|

## Interpretation
A positive index-points result does not establish a profitable long-call/long-put strategy. Premium sensitivity to implied volatility, theta, strike, expiry, bid/ask and execution must be tested separately. The five-session moving-block intervals measure uncertainty conditional on these fixed finalists; they do not fully correct the earlier parameter search or a changing market.

No live bot is deployed. A descriptive holdout gate (>=30 trades, net5 positive, and net2 lower CI>0) is a further research filter, never an automatic trading approval.

## Baselines
|Baseline|Hold minutes|Holdout N|Holdout gross pts|Holdout net2 pts|
|---|---:|---:|---:|---:|
|always_up|15|902|-1.58|-3.58|
|always_up|30|451|-2.49|-4.49|
|always_up|60|205|-2.55|-4.55|
|always_down|15|902|1.58|-0.42|
|always_down|30|451|2.49|0.49|
|always_down|60|205|2.55|0.55|
|momentum_30m|15|861|2.12|0.12|
|momentum_30m|30|410|3.58|1.58|
|momentum_30m|60|205|7.16|5.16|

## Data and reproducibility
Input SHA256 and exclusions: lab-data-audit.json. 3 feature prefix-invariance tests passed. Every exported entry and exit was asserted against its exact timestamp and holding horizon.

Full ledger: lab-all-configurations.csv; fixed finalist trades: lab-selected-trades.csv; frozen selector: lab-frozen-selection.json; forward-known regime diagnostics: lab-holdout-regimes.csv.
