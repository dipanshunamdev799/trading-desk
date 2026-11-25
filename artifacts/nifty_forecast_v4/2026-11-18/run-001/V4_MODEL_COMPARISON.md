# V4 model comparison

## Reproduced frozen binary candidates

|horizon|candidate|origins|disjoint|Brier|log loss|accuracy|status|
|---|---|---|---|---|---|---|---|
|5|M05_lgbm|92|19|0.226049|0.645492|66.30%|REPRODUCED / EXPOSED|
|5|A00_sector|92|19|0.233006|0.695555|63.04%|REPRODUCED / EXPOSED|
|5|Z_reversion|92|19|0.249239|0.691629|53.26%|REPRODUCED / EXPOSED|
|5|Z_neutral|92|19|0.250000|0.693147|NO CALL|REPRODUCED / EXPOSED|
|5|B00_empirical|92|19|0.258296|0.709964|57.61%|REPRODUCED / EXPOSED|
|21|B00_empirical|76|4|0.279282|0.752849|40.79%|REPRODUCED / EXPOSED|
|21|S_direction|76|4|0.242200|0.683027|60.53%|REPRODUCED / EXPOSED|

Neutral accuracy is NO CALL; always-up/down class controls remain in original V3
artifacts. Monthly selected-policy row is reproduced diagnosis, not a V4 frozen
monthly nonlinear candidate. All binary rows use identical origin dates per horizon.
No independently validated candidate exists.

## New coherent endpoint laws (exploratory)

|horizon|model|n/disjoint|CRPS|Brier|mean MAE|mean RMSE|median MAE|50 coverage|80 coverage|80 width|
|---|---|---|---|---|---|---|---|---|---|---|
|5|D00_empirical|92/19|0.012210|0.258296|1.637%|2.321%|1.643%|50.0%|72.8%|3.994%|
|5|D01_regime_shrunk|92/19|0.012304|0.266327|1.622%|2.345%|1.681%|53.3%|79.3%|4.338%|
|5|D02_student_shrunk|92/19|0.010896|0.219759|1.471%|2.013%|1.471%|41.3%|67.4%|3.325%|
|5|D03_residual_shrunk|92/19|0.011882|0.206257|1.469%|2.278%|1.481%|48.9%|67.4%|3.129%|
|21|D00_empirical|76/4|0.028363|0.279282|3.739%|4.879%|3.833%|26.3%|61.8%|7.275%|
|21|D01_regime_shrunk|76/4|0.028395|0.269010|3.824%|4.788%|3.648%|31.6%|55.3%|9.008%|
|21|D02_student_shrunk|76/4|0.027553|0.260640|3.511%|4.292%|3.511%|30.3%|39.5%|6.392%|
|21|D03_residual_shrunk|76/4|0.030587|0.283320|3.641%|4.808%|3.996%|32.9%|44.7%|6.341%|

MAE/RMSE/width columns use return units displayed as percentage points. D00 mean
and median are the historical point-estimate controls. Full mean/median errors,
pinball, bucket Brier and bucket calibration are in distribution-metrics.json and
the per-origin CSV. Every law's classifier probability and point/interval outputs
are mathematically consistent within that law, without mixing models.

## Calibration diagnostics (not activated)

|model|method|Brier|log loss|accuracy|flips|correct→wrong|wrong→correct|
|---|---|---|---|---|---|---|---|
|A00_sector|OFFSET|0.210617|0.631036|69.57%|18|6|12|
|A00_sector|RAW|0.233006|0.695555|63.04%|0|0|0|
|A00_sector|SHRINK50|0.224712|0.641082|65.22%|4|1|3|
|M05_lgbm|OFFSET|0.244450|0.685616|60.87%|7|6|1|
|M05_lgbm|RAW|0.226049|0.645492|66.30%|0|0|0|
|M05_lgbm|SHRINK50|0.234658|0.662231|59.78%|6|6|0|

## Uncertainty and status

V4 uncertainty includes30 weekly contrasts across frozen direction, calibration,
eight stress variants and distribution target types, plus15 monthly distribution
contrasts. Each weekly interval uses10-session blocks/2000 resamples with a
standardized simultaneous maximum-deviation correction across that whole family.
No adjusted weekly lower bound is positive. Monthly intervals are withheld because
of insufficient dependent rows. These are conditional exposed-history diagnostics;
they do not become independent confirmation because V4 uses a smaller family than
V3. All point leaders remain exploratory. Exact effect sizes, unadjusted paired
and family-adjusted intervals are in v4-uncertainty.json.

|Evidence class|Count/status|
|---|---|
|Reproduction|45 candidate/fold probability vectors;2 independent refits|
|New exposed-history endpoint records|1,928|
|New tree stress forecasts|736 (8x92)|
|Calibration records|552 (2models x3methods x92)|
|Primary prospective predictions|0|
|Late diagnostic issuance|1 issue containing both horizons|
|Resolved prospective horizons|0|
|Independent validation|NONE|

NO DEPLOYMENT is the only supported practical decision.
