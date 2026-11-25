# Weekly V3 forecasting research

Horizon=5 actual NSE sessions. Outer origins=92, non-overlapping windows=
19, outcome-ACF ESS=23.45.
Selector policy accuracy=63.04%, balanced accuracy=66.91%,
Brier=0.256118, log loss=0.748320. Always-up accuracy=
42.39%; always-down=57.61%.

|target|nested selector loss|nested baseline loss|outer descriptive leader|leader loss|
|---|---|---|---|---|
|direction|0.256118|0.270750|M05_lgbm|0.226049|
|return|0.016173|0.016064|A00_sector|0.014888|
|distribution|0.011281|0.012180|A00_sector|0.011112|
|volatility|0.549317|0.390983|S_return|0.254154|
|tail|0.138133|0.127401|M05_lgbm|0.121363|

The descriptive leader is selected after observing outer scores and is not
independent validation. Target selectors are different policies; do not quote
a return-selector's volatility success as if it were selected for volatility.
All scores are matched on identical origins. Subperiod/regime and selective
coverage diagnostics are saved even when unfavorable.

The shallow boosted model is an exploratory lead: 66.30% accuracy, Brier .226049,
log loss .64549, versus neutral .250000 and momentum .251413. The best fixed
probability control is reversion (.249239), so its Brier improvement is .023190.
The simultaneous 95% block interval is -.093033 to +.139413, crossing zero. The
adaptive inner direction selector scores worse (.256118) than neutral despite
63.04% accuracy, illustrating that accuracy alone is inadequate. Boosted nominal
80% interval coverage is 63.04%, so distribution reliability does not follow from
its better direction point estimate. No genuine advantage is demonstrated.

Current numerical scenarios and their late-issued timing are in 09_FINAL_FORECASTS.
No high-confidence label or trading recommendation is attached. Target/feature
availability assumptions, exposed-history status and corporate-action proxy
limitations apply to all candidate comparisons.
