# NIFTY V9 · Temporal Generalization Diagnosis

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

V9 first independently refit **2,949** V8 rows covering winners, earlier cohorts, monthly smoothed and shifted states, window stress, ETF/intraday increments and global corrections. It refit **644** additional protected weekly reference rows using their original designs. Most were numerically identical and the maximum V8 score difference was 0. V8 source, all 17 reports, data definitions, saved law outputs, fitted artifacts and registries are inventoried. The November 17 vintage stays frozen.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T_ROT_DOMESTIC | 92 | 19 | 12.363138 | 0.804348 | 0.809869 | 0.162145 | 0.505266 | 0.009927 | 0.012893 | 0.019361 | 0.004989 | 0.543478 | 0.815217 | 0.038873 |
| T_ELASTIC_EMBARGO | 92 | 19 | 12.363138 | 0.728261 | 0.699806 | 0.184134 | 0.552228 | 0.009665 | 0.012308 | 0.017693 | 0.004888 | 0.576087 | 0.815217 | 0.047453 |
| V8_R_RESIDUAL | 92 | 19 | 12.363138 | 0.804348 | 0.809869 | 0.159504 | 0.499670 | 0.009852 | 0.012801 | 0.019329 | 0.004980 | 0.521739 | 0.815217 | 0.038406 |
| V8_A_STRUCTURE_LEVEL | 92 | 19 | 12.363138 | 0.760870 | 0.765360 | 0.161756 | 0.502146 | 0.009587 | 0.012564 | 0.018940 | 0.004827 | 0.543478 | 0.804348 | 0.037959 |
| V8_A_STRUCTURE_CHANGE | 92 | 19 | 12.363138 | 0.782609 | 0.787615 | 0.162875 | 0.504776 | 0.009472 | 0.012361 | 0.018824 | 0.004784 | 0.576087 | 0.804348 | 0.038362 |
| V8_W_STRUCT_EMBARGO | 92 | 19 | 12.363138 | 0.782609 | 0.794388 | 0.163355 | 0.504982 | 0.009453 | 0.012395 | 0.018644 | 0.004783 | 0.543478 | 0.826087 | 0.039774 |
| V8_G_ROT_ELASTIC | 92 | 19 | 12.363138 | 0.739130 | 0.716014 | 0.164496 | 0.507809 | 0.009499 | 0.012158 | 0.018420 | 0.004758 | 0.608696 | 0.793478 | 0.039427 |


## What equalizing training length changes

The raw rotation model uses the same feature set, alpha and strictly matured labels across the two cohorts. At 85 training observations its Brier is **0.295111 earlier and 0.355902 later**. Expanding fits favor the later cohort. Holding both to 85 observations reverses that ranking. Separately, the historical baseline has a Brier gap of about .00115 across cohorts, so a large rotation gap is not explained by a comparable change in unconditional direction loss. The algebra below sums exactly to the observed expanding-model gap. The middle term still mixes time, unmeasured conditions and changes in training composition. It is not a causal estimate of market regime effects.

| loss | observed_earlier_minus_later | early_expanding_minus_85 | equal_85_date_regime_component | later_85_minus_expanding | historical_baseline_gap |
| --- | --- | --- | --- | --- | --- |
| brier | 0.134304 | 0.004425 | -0.060791 | 0.190670 | 0.001152 |
| crps | 0.003195 | -0.001249 | -0.001093 | 0.005537 | -0.001333 |


| cohort | model | n | training_min | training_max | inner_min | inner_max | brier | crps | brier_gain | crps_gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | L_ROT_126 | 173 | 126 | 126 | 94 | 126 | 0.307895 | 0.015009 | -0.048448 | -0.004132 |
| early | L_ROT_189 | 100 | 189 | 189 | 167 | 189 | 0.298903 | 0.016751 | -0.037410 | -0.002946 |
| early | L_ROT_252 | 40 | 252 | 252 | 227 | 246 | 0.227252 | 0.009893 | 0.024833 | 0.000438 |
| early | L_ROT_85 | 173 | 85 | 85 | 85 | 85 | 0.295111 | 0.014492 | -0.035663 | -0.003615 |
| early | L_ROT_MAX | 173 | 127 | 279 | 94 | 246 | 0.299536 | 0.013243 | -0.040088 | -0.002366 |
| later | L_ROT_126 | 92 | 126 | 126 | 126 | 126 | 0.213222 | 0.011160 | 0.045074 | 0.001050 |
| later | L_ROT_189 | 92 | 189 | 189 | 189 | 189 | 0.226963 | 0.011438 | 0.031333 | 0.000772 |
| later | L_ROT_252 | 92 | 252 | 252 | 252 | 252 | 0.210085 | 0.010848 | 0.048211 | 0.001362 |
| later | L_ROT_300 | 92 | 300 | 300 | 267 | 300 | 0.176506 | 0.010362 | 0.081790 | 0.001848 |
| later | L_ROT_85 | 92 | 85 | 85 | 85 | 85 | 0.355902 | 0.015585 | -0.097606 | -0.003375 |
| later | L_ROT_MAX | 92 | 300 | 385 | 267 | 352 | 0.165232 | 0.010048 | 0.093064 | 0.002162 |


| cohort | largest_eligible_length | model | n | disjoint | brier | crps |
| --- | --- | --- | --- | --- | --- | --- |
| early | 126 | L_ROT_126 | 173 | 35 | 0.307895 | 0.015009 |
| early | 126 | L_ROT_85 | 173 | 35 | 0.295111 | 0.014492 |
| early | 126 | L_ROT_MAX | 173 | 35 | 0.299536 | 0.013243 |
| early | 189 | L_ROT_126 | 100 | 20 | 0.323061 | 0.020039 |
| early | 189 | L_ROT_189 | 100 | 20 | 0.298903 | 0.016751 |
| early | 189 | L_ROT_85 | 100 | 20 | 0.296839 | 0.018938 |
| early | 189 | L_ROT_MAX | 100 | 20 | 0.313517 | 0.017010 |
| later | 126 | L_ROT_126 | 92 | 19 | 0.213222 | 0.011160 |
| later | 126 | L_ROT_85 | 92 | 19 | 0.355902 | 0.015585 |
| later | 126 | L_ROT_MAX | 92 | 19 | 0.165232 | 0.010048 |
| later | 189 | L_ROT_126 | 92 | 19 | 0.213222 | 0.011160 |
| later | 189 | L_ROT_189 | 92 | 19 | 0.226963 | 0.011438 |
| later | 189 | L_ROT_85 | 92 | 19 | 0.355902 | 0.015585 |
| later | 189 | L_ROT_MAX | 92 | 19 | 0.165232 | 0.010048 |
| later | 300 | L_ROT_126 | 92 | 19 | 0.213222 | 0.011160 |
| later | 300 | L_ROT_189 | 92 | 19 | 0.226963 | 0.011438 |
| later | 300 | L_ROT_252 | 92 | 19 | 0.210085 | 0.010848 |
| later | 300 | L_ROT_300 | 92 | 19 | 0.176506 | 0.010362 |
| later | 300 | L_ROT_85 | 92 | 19 | 0.355902 | 0.015585 |
| later | 300 | L_ROT_MAX | 92 | 19 | 0.165232 | 0.010048 |


The 85, 126, 189, 252 and 300 lengths cap the final fit. The purged inner sample may be smaller because the common 28-observation residual partition is held separate. We report exact training and inner sizes rather than calling them identical. Some earlier cutoffs cannot reach 300. The 92 later dates support the full comparison. Using all later history materially outperforms 85 or 189 dates, while 300 dates approach the expanding score. The pattern is nonmonotone and depends on which training eras remain in the fit. [Matched learning curve](matched-learning-curves.png)

## Same data and different residual-estimation design

| cohort | model | n | brier | crps | brier_gain | crps_gain |
| --- | --- | --- | --- | --- | --- | --- |
| early | L_DESIGN_V28_A100 | 173 | 0.299536 | 0.013243 | -0.040088 | -0.002366 |
| early | L_DESIGN_V28_A150 | 173 | 0.295132 | 0.012991 | -0.035685 | -0.002114 |
| early | L_DESIGN_V42_A100 | 173 | 0.288199 | 0.013118 | -0.028752 | -0.002241 |
| early | L_DESIGN_V42_A150 | 173 | 0.286095 | 0.012802 | -0.026648 | -0.001924 |
| later | L_DESIGN_V28_A100 | 92 | 0.165232 | 0.010048 | 0.093064 | 0.002162 |
| later | L_DESIGN_V28_A150 | 92 | 0.169707 | 0.010268 | 0.088589 | 0.001942 |
| later | L_DESIGN_V42_A100 | 92 | 0.162294 | 0.009897 | 0.096002 | 0.002314 |
| later | L_DESIGN_V42_A150 | 92 | 0.166146 | 0.010094 | 0.092150 | 0.002116 |


Changing residual validation from 28 to 42 dates improves earlier expanding Brier, but it still loses to historical. Changing Ridge alpha affects both cohorts. V9 leaves warm-up, missingness and maturity rules fixed within the controlled comparisons. The primary V9 parent uses 28 origins for a common earlier/later fit. Comparisons against V8’s protected 42-origin fits remain matched by target and date with this design difference explicit.

## State matches and parameter drift

| cohort | feature | n | mean | std |
| --- | --- | --- | --- | --- |
| early | s_trend | 173 | -0.053199 | 0.918698 |
| later | s_trend | 92 | -0.319255 | 1.202355 |
| early | s_vol | 173 | 0.008338 | 0.003838 |
| later | s_vol | 92 | 0.007064 | 0.002013 |
| early | s_breadth | 173 | 0.510597 | 0.316055 |
| later | s_breadth | 92 | 0.467391 | 0.311032 |
| early | s_bank | 173 | 0.000929 | 0.006643 |
| later | s_bank | 92 | -0.000073 | 0.008016 |
| early | s_defensive | 173 | -0.003137 | 0.020375 |
| later | s_defensive | 92 | 0.002435 | 0.014214 |
| early | s_sector_dispersion | 173 | 0.016594 | 0.006214 |
| later | s_sector_dispersion | 92 | 0.015358 | 0.005149 |
| early | s_liquidity | 173 | 0.031161 | 0.393329 |
| later | s_liquidity | 92 | 0.003170 | 0.291704 |
| early | s_cross_corr | 173 | 0.004809 | 0.128099 |
| later | s_cross_corr | 92 | -0.013215 | 0.087696 |
| early | s_acf | 173 | 0.060944 | 0.156448 |
| later | s_acf | 92 | -0.036568 | 0.127334 |
| early | s_global_vol | 173 | -0.016243 | 3.010704 |
| later | s_global_vol | 92 | -0.036739 | 1.688418 |
| early | s_sync | 173 | 0.507325 | 0.094135 |
| later | s_sync | 92 | 0.343670 | 0.118510 |
| early | s_concentration | 173 | 0.273999 | 0.078750 |
| later | s_concentration | 92 | 0.286761 | 0.090788 |
| early | s_trend_consistency | 173 | 0.502615 | 0.098954 |
| later | s_trend_consistency | 92 | 0.463768 | 0.103481 |


The one-to-one state-matching exercise finds **88** pairs within the predeclared distance cap out of 92 potential matches. Among these, 85-observation Brier is **0.263884 earlier and 0.340891 later**. Relative loss to the historical baseline is **0.007663** and **0.086272**. The early normalization and concurrent state similarity do not remove other time-varying differences. The limited matched conditions do not identify a market cause.

| cohort | fold | cutoff | feature | coefficient |
| --- | --- | --- | --- | --- |
| early | 2025-10 | 2025-10-14 | r_bank_residual | -0.000290 |
| early | 2025-10 | 2025-10-14 | r_def_residual | 0.000539 |
| early | 2025-11 | 2025-10-31 | r_bank_residual | -0.000643 |
| early | 2025-11 | 2025-10-31 | r_def_residual | 0.000443 |
| early | 2025-12 | 2025-11-28 | r_bank_residual | -0.000727 |
| early | 2025-12 | 2025-11-28 | r_def_residual | 0.000689 |
| early | 2026-01 | 2025-12-31 | r_bank_residual | -0.000546 |
| early | 2026-01 | 2025-12-31 | r_def_residual | 0.000786 |
| early | 2026-02 | 2026-01-30 | r_bank_residual | -0.000910 |
| early | 2026-02 | 2026-01-30 | r_def_residual | 0.000540 |
| early | 2026-03 | 2026-02-27 | r_bank_residual | -0.000828 |
| early | 2026-03 | 2026-02-27 | r_def_residual | 0.000056 |
| early | 2026-04 | 2026-03-30 | r_bank_residual | -0.000529 |
| early | 2026-04 | 2026-03-30 | r_def_residual | 0.000399 |
| early | 2026-05 | 2026-04-30 | r_bank_residual | -0.002198 |
| early | 2026-05 | 2026-04-30 | r_def_residual | 0.000102 |
| early | 2026-06 | 2026-05-29 | r_bank_residual | -0.001945 |
| early | 2026-06 | 2026-05-29 | r_def_residual | -0.000084 |
| later | 2026-07 | 2026-06-30 | r_bank_residual | -0.001864 |
| later | 2026-07 | 2026-06-30 | r_def_residual | 0.000855 |
| later | 2026-08 | 2026-07-31 | r_bank_residual | -0.002301 |
| later | 2026-08 | 2026-07-31 | r_def_residual | 0.000732 |
| later | 2026-09 | 2026-08-31 | r_bank_residual | -0.002463 |
| later | 2026-09 | 2026-08-31 | r_def_residual | 0.000803 |
| later | 2026-10 | 2026-09-30 | r_bank_residual | -0.002420 |
| later | 2026-10 | 2026-09-30 | r_def_residual | 0.000720 |
| later | 2026-11 | 2026-10-30 | r_bank_residual | -0.002467 |
| later | 2026-11 | 2026-10-30 | r_def_residual | 0.001135 |


The largest retrospective CUSUM deviation occurs at **2026-05-20**. That date uses all observed losses and is for diagnosis. `online-and-retrospective-breaks.csv` separately tracks a feasible alarm based on the latest 21 resolved losses against the preceding up-to-42 losses, plus rolling matured bank-residual/error correlation. It does not feed the ex-post CUSUM break back into historical forecasts. `base-coefficients.csv` preserves all per-cutoff coefficients and intercepts. Training support, changing conditional associations and experimental design all matter. The comparison cannot assign clean causal shares between them.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
