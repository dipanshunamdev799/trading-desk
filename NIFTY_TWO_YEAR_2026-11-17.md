# NIFTY: strictly the last two years

Only **17 November 2024–16 November 2026** contributes to this run. The first
available session is 18 November 2024. There are **495 NIFTY sessions**, including
Monday's previously disclosed provisional quote-derived bar, and **475 eligible
feature rows** after indicator warmup.

Every Indian/global series was clipped **before** calculating returns, EMAs,
RSI, volatility or other features. No older indicator initialization, fitted
coefficient, historical prediction or analogue statistic was imported. Source
archives retain older records, but those records do not enter this model.
The dated source freeze is reused so this isolates the history-window change.

## Updated 17 November call

**Neutral:** 50.31% estimated probability of a close above
Monday's 25,291.10 reference; 49.55% probability of closing
above today's open. Before calibration, those estimates are
50.66% and 50.10%. These are model estimates,
not established success probabilities. Issued 2026-11-17T01:11:37.762650+05:30.

## Current learned allocations

|Group|Close vs previous close|Open to close|
|---|---:|---:|
|neutral|62.22%|61.45%|
|trend|0.00%|4.89%|
|candles gaps|0.00%|8.04%|
|volatility|13.27%|25.61%|
|banks financials|1.61%|0.00%|
|gift nifty|22.90%|0.00%|

All other groups have zero allocation in this fit. Cash/FII groups retain their
73 historical out-of-sample predictions and remain below the existing evidence
gate. GIFT uses conservatively lagged completed sessions; volatility combines
India VIX and realized measures. These allocations are conditional model weights,
not permanent economic importance.

## What fits into two years

The same feature groups, penalties, recency half-lives and evidence gates are
retained. The overall startup holdoff changes from 504 rows to the existing
252-row expert training minimum, because 504 initial rows cannot fit inside this
window. Monthly expert refits and daily prior-error weight learning remain.

There are **222 chronological predictions after initial expert training**,
23 December 2025–16 November 2026. The first 126 supply error-learning history.
This leaves **96 fully learned evaluation decisions, 1 July–16 November 2026**.
Those dates are selected by availability of prior training evidence, not by
their returns. It would be misleading to call all two years out-of-sample while
using that same period to train and learn the weights.

## Results on those same 96 decisions

|Method|Close Brier ↓|Close accuracy|Intraday Brier ↓|Intraday accuracy|
|---|---:|---:|---:|---:|
|neutral|0.25000|49.0%|0.25000|50.0%|
|rolling frequency|0.25057|47.9%|0.25114|50.0%|
|equal groups|0.24788|55.2%|0.24823|54.2%|
|adaptive groups|0.25005|46.9%|0.25131|49.0%|
|calibrated adaptive|0.25165|44.8%|0.25322|45.8%|

The neutral reference has Brier 0.25000. Its displayed direction accuracy merely
uses the code's 50%-tie-as-up convention; the neutral method makes no directional
call. The learned blend does not establish an edge. Equal-group close accuracy
is 55.2%, but its paired Brier-improvement interval includes zero, and the
predeclared primary method is not replaced after examining that result.
Calibration worsens this run as well. The sample is small and was already
examined in earlier exploratory work.

On exactly these 96 dates, the primary two-year close Brier is
0.25165, versus
0.25077 for the longer-history
model. That is a matched-date descriptive comparison, not an independent test.
All 222 post-training forecasts, both evaluation halves, calibration bins and
the 95-decision subset excluding Monday's provisional target are saved in
[validation.json](artifacts/nifty_forecast/2026-11-17/two-year-v1/validation.json).

## Files and checks

- [Frozen forecast](artifacts/nifty_forecast/2026-11-17/two-year-v1/forecast.json)
- [Group weights](artifacts/nifty_forecast/2026-11-17/two-year-v1/group-weights.csv)
- [Individual input coefficients](artifacts/nifty_forecast/2026-11-17/two-year-v1/input-coefficients.csv)
- [Window and data audit](artifacts/nifty_forecast/2026-11-17/two-year-v1/data-audit.json)
- [Fixed rerun design](research/nifty_forecast/TWO_YEAR_PROTOCOL.md)

Five focused checks verify that pre-window price changes cannot affect any
feature, all used series and training labels stay within the boundary, future
labels cannot change earlier expert fits, allocations sum to one, and the prior
forecast remains unchanged. The original data-vintage, conservative global-clock
and institutional-publication assumptions remain in force.

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast.verify_two_year
.\.venv\Scripts\python.exe -m research.nifty_forecast.two_year --out artifacts/nifty_forecast/2026-11-17/two-year-reproduction-01
.\.venv\Scripts\python.exe -m research.nifty_forecast.score --run artifacts/nifty_forecast/2026-11-17/two-year-v1
```

The score command remains pending until the target daily candle is published.
Earlier forecasts are preserved as separate experiments.
