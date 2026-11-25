# 08 — Fair comparisons and failure diagnosis

**No independently validated winner exists.** All historical dates are exposed;
none of 170 simultaneous weekly contrasts excludes zero improvement, and monthly
independent evaluation is too small. The table's MAE/distribution columns belong
to each method's independently fitted return outputs; do not assume its classifier
probability and quantile distribution form a calibrated joint forecast.

|Model|Horizon|OOS origins|Effective sample|Brier|Accuracy|MAE|Interval coverage|Baseline improvement|
|---|---|---|---|---|---|---|---|---|
|Z_neutral|5|92|19 disjoint / ESS23.5|0.25000|NO CALL|1.637%|50:50.0%;80:72.8%|+0.00000 vs neutral|
|Z_momentum|5|92|19 disjoint / ESS23.5|0.25141|51.1%|1.637%|50:50.0%;80:72.8%|-0.00141 vs neutral|
|B00_empirical|5|92|19 disjoint / ESS23.5|0.25830|57.6%|1.637%|50:50.0%;80:72.8%|-0.00830 vs neutral|
|M00_ridge_price|5|92|19 disjoint / ESS23.5|0.24586|55.4%|1.561%|50:40.2%;80:62.0%|+0.00414 vs neutral|
|M01_ridge_full|5|92|19 disjoint / ESS23.5|0.31369|55.4%|1.679%|50:43.5%;80:57.6%|-0.06369 vs neutral|
|A00_sector|5|92|19 disjoint / ESS23.5|0.23301|63.0%|1.489%|50:46.7%;80:67.4%|+0.01699 vs neutral|
|A01_nofo|5|92|19 disjoint / ESS23.5|0.27124|54.3%|1.531%|50:46.7%;80:64.1%|-0.02124 vs neutral|
|A02_proxy [RESEARCH-ONLY PROXY]|5|92|19 disjoint / ESS23.5|0.30229|56.5%|1.687%|50:42.4%;80:57.6%|-0.05229 vs neutral|
|M05_lgbm|5|92|19 disjoint / ESS23.5|0.22605|66.3%|1.519%|50:42.4%;80:63.0%|+0.02395 vs neutral|
|S_direction|5|92|19 disjoint / ESS23.5|0.25612|63.0%|1.616%|50:43.5%;80:63.0%|-0.00612 vs neutral|
|S_return|5|92|19 disjoint / ESS23.5|0.26540|48.9%|1.617%|50:44.6%;80:66.3%|-0.01540 vs neutral|
|S_distribution|5|92|19 disjoint / ESS23.5|0.26905|48.9%|1.624%|50:45.7%;80:64.1%|-0.01905 vs neutral|
|S_volatility|5|92|19 disjoint / ESS23.5|0.25694|54.3%|1.638%|50:37.0%;80:63.0%|-0.00694 vs neutral|
|S_tail|5|92|19 disjoint / ESS23.5|0.24861|47.8%|1.581%|50:47.8%;80:69.6%|+0.00139 vs neutral|
|Best independently validated candidate: NONE|5|NOT AVAILABLE|NOT VALIDATED|NOT AVAILABLE|NOT AVAILABLE|NOT AVAILABLE|NOT VALIDATED|NONE DEMONSTRATED|
|Z_neutral|21|76|4 disjoint / ESS6.0|0.25000|NO CALL|3.739%|50:26.3%;80:61.8%|+0.00000 vs neutral|
|Z_momentum|21|76|4 disjoint / ESS6.0|0.25118|51.3%|3.739%|50:26.3%;80:61.8%|-0.00118 vs neutral|
|B00_empirical|21|76|4 disjoint / ESS6.0|0.27928|40.8%|3.739%|50:26.3%;80:61.8%|-0.02928 vs neutral|
|M00_ridge_price|21|76|4 disjoint / ESS6.0|0.29122|42.1%|3.665%|50:2.6%;80:50.0%|-0.04122 vs neutral|
|M01_ridge_full|21|76|4 disjoint / ESS6.0|0.32993|51.3%|4.245%|50:23.7%;80:34.2%|-0.07993 vs neutral|
|A00_sector|21|76|4 disjoint / ESS6.0|0.29397|53.9%|3.421%|50:27.6%;80:39.5%|-0.04397 vs neutral|
|A01_nofo|21|76|4 disjoint / ESS6.0|0.25923|56.6%|4.172%|50:23.7%;80:30.3%|-0.00923 vs neutral|
|A02_proxy [RESEARCH-ONLY PROXY]|21|76|4 disjoint / ESS6.0|0.33561|50.0%|4.424%|50:19.7%;80:32.9%|-0.08561 vs neutral|
|M05_lgbm|21|76|4 disjoint / ESS6.0|0.30662|38.2%|4.203%|50:26.3%;80:39.5%|-0.05662 vs neutral|
|S_direction|21|76|4 disjoint / ESS6.0|0.24220|60.5%|3.359%|50:27.6%;80:52.6%|+0.00780 vs neutral|
|S_return|21|76|4 disjoint / ESS6.0|0.33243|44.7%|4.065%|50:10.5%;80:35.5%|-0.08243 vs neutral|
|S_distribution|21|76|4 disjoint / ESS6.0|0.35293|36.8%|4.024%|50:10.5%;80:31.6%|-0.10293 vs neutral|
|S_volatility|21|76|4 disjoint / ESS6.0|0.28021|27.6%|3.563%|50:27.6%;80:60.5%|-0.03021 vs neutral|
|S_tail|21|76|4 disjoint / ESS6.0|0.30644|51.3%|3.823%|50:27.6%;80:39.5%|-0.05644 vs neutral|
|Best independently validated candidate: NONE|21|NOT AVAILABLE|NOT VALIDATED|NOT AVAILABLE|NOT AVAILABLE|NOT AVAILABLE|NOT VALIDATED|NONE DEMONSTRATED|

## The earlier failures were reproduced, not discarded

Original monthly calibrated accuracy was 16.67% versus 52.78% raw; Brier .307490
versus .268606. Calibration flipped 17 predictions:15 correct-to-wrong and only 2
wrong-to-correct. Mean probability shifted from 52.29% to 52.96% while actual up
frequency was 36.11%; small average shifts hide damaging threshold crossings.
Weekly calibration flipped 26 calls with 13 improvements and 13 deteriorations,
but worsened Brier from .247161 to .249527. Overlapping-label prevalence shifts,
limited calibration diversity and nonstationarity explain plausible failure
mechanisms; this is not proof of a single causal explanation.

The exact old architecture was also refit using only 2025 onward, no old fitted
state. Its stringent252-training+126-OOS gates leave just 54 fully learned weekly
origins (11 disjoint) and 6 monthly origins (one disjoint). This demonstrates why
the old monthly model could not be reliably validated under this constraint.

Learned allocations can lose to equal groups because correlated errors plus
small effective meta samples produce unstable trust estimates. V3 tests raw
joint models and interactions without forcing the old group architecture or
its posthoc calibration. Some point scores improve, but nonlinear mechanisms
do not survive the current qualification standard. The joint FO+FII ablation
often improves the full linear model when removed; obtaining more authentic
data did not itself prove incremental predictive value. This does not isolate
FO from sparse FII or prove derivatives are universally uninformative.

Weekly and monthly rankings differ. Volatility/returns/distributions have
different leaders and different selectors. An attractive postselected volatility
score does not validate direction, interval coverage or a risk strategy. Current
member-basket proxies cannot establish true historical breadth skill, even if a
proxy ablation improves one score. Training feature gain and importance are not
causal effects.

Model selection can also overfit a 42-origin inner set, particularly when monthly
outcomes overlap. The nested baseline selector itself performs poorly; it is not
used as the sole benchmark. Fixed neutral/momentum/reversion and the strongest
fixed baseline are disclosed alongside it. Selective forecasts report coverage,
matched baselines and small counts; no favorable subgroup is promoted after inspection.

Statistical details: paired-comparisons.json, simultaneous-uncertainty.json,
feature-family-ablations.json, conditional-diagnostics.json, selective-forecasting.json,
legacy-artifact-reproduction.json and legacy-2025-only-reproduction.json.
