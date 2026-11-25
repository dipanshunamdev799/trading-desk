# Monthly V3 forecasting research

Horizon=21 actual NSE sessions. Outer origins=76, non-overlapping windows=
4, outcome-ACF ESS=5.96.
Selector policy accuracy=60.53%, balanced accuracy=61.65%,
Brier=0.242200, log loss=0.683027. Always-up accuracy=
40.79%; always-down=59.21%.

|target|nested selector loss|nested baseline loss|outer descriptive leader|leader loss|
|---|---|---|---|---|
|direction|0.242200|0.414176|S_direction|0.242200|
|return|0.040652|0.038717|S_direction|0.033593|
|distribution|0.035021|0.030158|S_volatility|0.026816|
|volatility|0.218973|0.179324|A00_sector|0.088307|
|tail|0.316395|0.316365|S_direction|0.244290|

The descriptive leader is selected after observing outer scores and is not
independent validation. Target selectors are different policies; do not quote
a return-selector's volatility success as if it were selected for volatility.
All scores are matched on identical origins. Subperiod/regime and selective
coverage diagnostics are saved even when unfavorable.

The new no-posthoc-calibration direction selector is better than the old failed
monthly study descriptively: 60.53% accuracy, Brier .242200, versus neutral .25,
momentum .251184 and always-down59.21% accuracy. Four non-overlapping windows
cannot establish independent skill or robust significance. Its nominal 80% return
coverage is 52.63%; the independently selected distribution policy covers only 31.58%.
The sector model has an attractive volatility QLIKE point score .088307, but the
actual nested volatility selector scores .218972 versus baseline selector .179324.
Selecting the sector model after this result would be post-selection. Confidence
intervals are NOT ESTIMATED for the small monthly outer sample.

Current numerical scenarios and their late-issued timing are in 09_FINAL_FORECASTS.
No high-confidence label or trading recommendation is attached. Target/feature
availability assumptions, exposed-history status and corporate-action proxy
limitations apply to all candidate comparisons.
