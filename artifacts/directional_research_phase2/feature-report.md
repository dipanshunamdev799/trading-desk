# Point-in-time contextual research

32,518 five-minute decisions; 13 availability/prefix checks passed. Development-only VIX median: 12.62.

All additions were fixed before outcomes were read. Every baseline trade remains in the ledger; each added filter evaluates a subset of those same opportunities. Differences in subset averages are exploratory and do not establish causal or incremental predictive value. No filter was selected for deployment.

|Frozen rule|Filter|Final trades|Baseline trades|Gross pts|Net2 pts|Net5 pts|Net2 95% block interval|Change vs baseline 95% interval|
|---|---|---:|---:|---:|---:|---:|---|---|
|ema_trend|baseline|69|69|9.07|7.07|4.07|-6.34 to 21.05|0.00 to 0.00|
|ema_trend|vix_below_dev_median|28|69|1.38|-0.62|-3.62|-13.22 to 14.42|-25.99 to 10.90|
|ema_trend|vix_not_rising|27|69|0.75|-1.25|-4.25|-13.79 to 13.40|-22.58 to 5.53|
|ema_trend|etf_vwap_agreement|69|69|9.07|7.07|4.07|-6.34 to 21.05|0.00 to 0.00|
|ema_trend|etf_rvol_ge1|49|69|14.16|12.16|9.16|-6.21 to 29.13|-2.27 to 12.19|
|ema_trend|official_gap_agreement|38|69|17.87|15.87|12.87|-4.22 to 37.29|-1.72 to 21.44|
|donchian|baseline|42|42|8.83|6.83|3.83|-10.19 to 25.22|0.00 to 0.00|
|donchian|vix_below_dev_median|16|42|3.92|1.92|-1.08|-13.40 to 15.62|-26.74 to 14.97|
|donchian|vix_not_rising|16|42|2.36|0.36|-2.64|-18.32 to 19.95|-27.88 to 13.86|
|donchian|etf_vwap_agreement|41|42|9.64|7.64|4.64|-9.79 to 26.38|0.00 to 2.64|
|donchian|etf_rvol_ge1|33|42|10.99|8.99|5.99|-10.08 to 30.48|-3.53 to 9.34|
|donchian|official_gap_agreement|22|42|13.41|11.41|8.41|-23.89 to 50.31|-15.06 to 27.26|
|pullback|baseline|61|61|7.42|5.42|2.42|-6.95 to 19.55|0.00 to 0.00|
|pullback|vix_below_dev_median|27|61|-0.44|-2.44|-5.44|-13.88 to 11.34|-23.26 to 7.74|
|pullback|vix_not_rising|27|61|1.16|-0.84|-3.84|-12.46 to 11.18|-20.59 to 7.24|
|pullback|etf_vwap_agreement|59|61|8.81|6.81|3.81|-5.80 to 21.15|0.00 to 3.59|
|pullback|etf_rvol_ge1|38|61|11.61|9.61|6.61|-8.81 to 30.43|-5.27 to 15.20|
|pullback|official_gap_agreement|31|61|15.36|13.36|10.36|-7.06 to 38.39|-4.36 to 23.10|

## Feature definitions and boundaries
- Official gap uses the preceding published daily close, strictly prior to the current date. It replaces the 15:10 research-window close only for this feature; underlying entry rules remain frozen.
- VIX values join only exact completed five-minute timestamps, with no stale carry. Prior VIX close uses the preceding observed VIX session. No current-session final close is exposed earlier.
- ETF relative volume uses the same clock bucket over the prior 20 observed ETF sessions, minimum five valid bars. Missing observations stay missing. Volume is actual ETF reported volume, not spot-index volume.
- ETF VWAP is explicitly a candle typical-price-times-volume proxy accumulated from completed bars. It is not a true tick-by-tick traded-price VWAP.
- Missing context rejects a filtered trade; it does not disappear from baseline coverage. This is a coverage/execution requirement, not evidence that unobserved trades would fail.

## Fixed gap-rule correction
The original gap-fade and gap-follow finalists are also replayed with their frozen threshold/filter/60-minute exit, replacing the research-window prior close with the official prior daily close. This feature-definition comparison was separately registered after context ablations, before corrected gap outcomes were computed. It remains exploratory historical evidence.

|Gap rule|Prior-close definition|Final trades|Gross pts|Net2 pts|Net5 pts|Net2 95% interval|
|---|---|---:|---:|---:|---:|---|
|fade|research_close|60|4.10|2.10|-0.90|-8.31 to 12.79|
|follow|research_close|54|-1.28|-3.28|-6.28|-15.45 to 8.97|
|fade|official_close|64|5.29|3.29|0.29|-7.49 to 13.35|
|follow|official_close|47|-10.98|-12.98|-15.98|-36.98 to 4.90|

## Captured dashboard observations
The frozen database contains 35,348 records across 64 factors, captured 2026-10-24 17:09:32.913132+00:00 through 2026-11-01 18:31:19.137512+00:00. Only 10 replay sessions fall after initial capture and have any previously captured factor; freshness varies, including stale values after collection stopped.
Historical joins first require observed_at <= decision and reported_at <= decision when present, then select the latest reporting period/revision. A June reporting label collected in October remains unavailable to June decisions. Future source timestamps are delayed until that timestamp. All revisions are retained in feature-observations.json.
Captured PCR, IV, max-pain and cash-flow values are exported with both availability age and reported-data age, plus observation keys. They were not used as broad-history trading filters: the capture window is too short, and each series still needs semantic freshness/publication review. A newly captured old reporting period is still old data. These columns can be arbitrarily stale; both ages must be checked before execution.

The application latest()/history() dashboard helpers do not themselves enforce historical information availability. This research uses its own explicit selection before revision resolution. Synthetic delayed-publication/revision cases and source-candle prefix tests verify that behavior.

Intervals use 3,000 paired five-session circular moving-block resamples. Filtered-minus-baseline intervals compare per-trade means on the same resampled sessions, retaining the coverage effect. They are conditional on frozen rules and filters, not corrected for the broader strategy/feature search.

Outputs: feature-panel.csv/.sqlite, feature-trade-panel.csv, feature-ablations.csv, feature-audit.json, feature-preregister.json and frozen observation revisions. All results are index points, not option returns.