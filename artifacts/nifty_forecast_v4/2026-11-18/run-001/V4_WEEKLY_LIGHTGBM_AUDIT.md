# V4 weekly LightGBM audit

Exact V3 tree:92 overlapping origins/19 disjoint; accuracy 66.30%, Brier.226049,
logloss.645492. This remains an exposed-history lead, not independently validated.
Original V3 simultaneous improvement interval vs fixed reversion spans zero widely.

|variant|Brier|log loss|accuracy|
|---|---|---|---|
|drop_etf|0.226049|0.645492|66.30%|
|drop_fo|0.228148|0.649868|64.13%|
|drop_global|0.226212|0.649984|75.00%|
|drop_institution|0.226049|0.645492|66.30%|
|drop_intraday|0.226082|0.645730|65.22%|
|drop_risk|0.231396|0.657224|63.04%|
|drop_sector|0.242121|0.676261|51.09%|
|rolling126|0.240299|0.675190|63.04%|

Dropping globals raises threshold accuracy to 75% but does not improve Brier over
the original tree; it is not promoted. Dropping sectors worsens Brier to.242121
and accuracy to 51.09%. Rolling126 worsens Brier to.240299. Dropping institutions
or ETF leaves the original predictions unchanged in this sample, consistent with
no incremental fitted contribution here, not proof the economic sources are
universally useless. Risk/FO/global/intraday effects differ. Each perturbation
is a distinct retrospective study with unchanged original tree hyperparameters.

|removed_month|n|brier_improvement_vs_reversion|
|---|---|---|
|2026-07|69|0.06854320280355844|
|2026-08|71|0.002255000665437797|
|2026-09|71|-0.0041391295960158|
|2026-10|72|0.03760055667362565|
|2026-11|85|0.014482410644861773|

|remove_best_origins|remaining_mean_improvement|
|---|---|
|1|0.020688340153992398|
|3|0.015704628481683434|
|5|0.010591167889844844|
|10|-0.0023278883324420524|

Excluding September reverses the advantage; excluding the ten most favorable
overlapping origins also reverses it. Those ten are not ten independent weeks.
Five alternate starting phases of greedily disjoint5-session windows are saved,
alongside original per-origin predictions, month/volatility/trend/participation/
expiry/global-risk-off/large-prior-move slices and confidence buckets. Small
slices are descriptive and are not promoted into conditional edges.

For the raw tree's highest confidence bin (>=.65),13 overlapping origins have
mean probability72.35% and actual positive frequency61.54%; the .55–.65 bucket
has only 5 origins and 100% positives. Neither supports precise calibration claims.
Training family gain is in weekly-lightgbm-audit.json, explicitly noncausal.

Calibration: RAW, fixed50% shrinkage toward the matured training base rate, and
one bounded logit offset fitted on purged inner validation with 10*b²/2 penalty.
No slope fitting or isotonic search. All calibration remains DISABLED.

|model|method|Brier|log loss|accuracy|flips|correct→wrong|wrong→correct|
|---|---|---|---|---|---|---|---|
|A00_sector|OFFSET|0.210617|0.631036|69.57%|18|6|12|
|A00_sector|RAW|0.233006|0.695555|63.04%|0|0|0|
|A00_sector|SHRINK50|0.224712|0.641082|65.22%|4|1|3|
|M05_lgbm|OFFSET|0.244450|0.685616|60.87%|7|6|1|
|M05_lgbm|RAW|0.226049|0.645492|66.30%|0|0|0|
|M05_lgbm|SHRINK50|0.234658|0.662231|59.78%|6|6|0|

LightGBM shrinkage makes six correct calls wrong; offset makes six wrong and
repairs one. Sector offset improves descriptive Brier, but no adjusted lower
bound is positive. Thus calibration is not inherently beneficial or harmful;
its result depends on model and sample. Inner 42 origins contain far fewer
disjoint outcomes; fit ledger records those counts and inner/outer prevalence.
Multiple metrics and confidence bins are retained: lower Brier alone is not a
pure calibration measure, as discussed in the
[scikit-learn calibration documentation](https://scikit-learn.org/stable/modules/calibration.html).
No retrospective correction is applied to the frozen prospective cohort.
