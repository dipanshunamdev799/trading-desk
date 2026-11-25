# NIFTY V7 · V6 Reproduction And Diagnosis

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

V6’s weekly Brier winner was `F_NO_DEFENSIVE`. It left out six 5- and 21-session relative-return features. V6’s CRPS winner `W2_NOAUTO_VOLUME` removed Auto 21-session relative return and added five ETF volume ratios. `W2_DEF_NORM` kept all six defensive inputs and scaled their standardized values by 1/√6. `W2_DEF_PC` used one whitened principal component for the same six columns. The underlying return regression used Ridge alpha 100 with train-median imputation and train standardization, clipping at ±5. The laws assign 65% to the conditional mean plus purged inner validation residuals and 35% to the last 252 or fewer matured historical returns.

The protected V6 index, all 13 reports, source modules, result and fit registries were inventoried in `reviewed-material.json` and `preservation.json`. V7 refit the four variants over 444 saved predictions across 24 model and fold combinations, with maximum error 0 across direction, location and proper scores. The inherited exact reconstruction also reproduced 81 V4/V5 prediction vectors and two independent V5 refits. The coherent V4 laws and separate LightGBM classifier maintain their original definitions. The prospective ledger is outside the historical comparison.

Defensive columns are i_idx_NIFTY_HEALTHCARE_rel5, i_idx_NIFTY_HEALTHCARE_rel21, i_nifty_fmcg_rel5, i_nifty_fmcg_rel21, i_nifty_pharma_rel5, i_nifty_pharma_rel21. The ETF features are p_liq_GOLDBEES_volume, p_liq_SILVERBEES_volume, p_liq_MON100_volume, p_liq_HNGSNGBEES_volume, p_liq_NIFTYBEES_volume. `v6-reproduction.json` records all fitted inputs and cutoffs.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V6_BRIER | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| V6_CRPS | 92 | 0.750000 | 0.755926 | 0.178802 | 0.541915 | 0.009756 | 0.013051 | 0.012609 | 0.018979 | 0.532609 | 0.771739 | 0.037657 |
| V6_DEF_NORM | 92 | 0.782609 | 0.791001 | 0.169862 | 0.522778 | 0.010095 | 0.013198 | 0.012637 | 0.019755 | 0.521739 | 0.782609 | 0.038263 |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.012959 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| I00 | 92 | 0.760870 | 0.751814 | 0.186099 | 0.558036 | 0.010224 | 0.013539 | 0.013235 | 0.019852 | 0.554348 | 0.760870 | 0.037708 |
| L01 | 92 | 0.663043 | 0.653362 | 0.197610 | 0.582153 | 0.009963 | 0.013409 | 0.013162 | 0.019166 | 0.543478 | 0.771739 | 0.036633 |
| V4_D02_student_shrunk | 92 | 0.608696 | 0.656991 | 0.219759 | 0.629825 | 0.010896 | 0.014707 | 0.014707 | 0.020132 | 0.413043 | 0.673913 | 0.033246 |
| V4_D03_residual_shrunk | 92 | 0.684783 | 0.648524 | 0.206257 | 0.607870 | 0.011882 | 0.014686 | 0.014814 | 0.022780 | 0.489130 | 0.673913 | 0.031291 |
| V4_M05_lgbm | 92 | 0.663043 | 0.633043 | 0.226049 | 0.645492 | 0.011817 | 0.015190 | 0.015464 | 0.021320 | 0.423913 | 0.630435 | 0.033626 |
| V4_Z_neutral | 92 | 0.423913 | 0.500000 | 0.250000 | 0.693147 | 0.012207 | 0.016374 | 0.016435 | 0.023210 | 0.500000 | 0.728261 | 0.039943 |
| E00 | 92 | 0.576087 | 0.500000 | 0.258296 | 0.709964 | 0.012210 | 0.016374 | 0.016435 | 0.023210 | 0.500000 | 0.728261 | 0.039943 |


| model | n | mean_P_change | brier_gain | crps_gain |
| --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | 92 | 0.080241 | 0.012244 | -0.000105 |
| W2_DEF_NORM | 92 | 0.053662 | 0.012184 | -0.000132 |
| W2_DEF_PC | 92 | 0.062241 | 0.011838 | -0.000343 |
| W2_NOAUTO_VOLUME | 92 | 0.046092 | 0.003245 | 0.000207 |


| model | regime | n | mean_P_change | brier_gain | crps_gain |
| --- | --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | high_vol | 52 | 0.086905 | 0.009636 | -0.000904 |
| F_NO_DEFENSIVE | low_vol | 40 | 0.071577 | 0.015633 | 0.000934 |
| W2_DEF_NORM | high_vol | 52 | 0.055357 | 0.010123 | -0.000831 |
| W2_DEF_NORM | low_vol | 40 | 0.051458 | 0.014864 | 0.000776 |
| W2_DEF_PC | high_vol | 52 | 0.066071 | 0.007631 | -0.001243 |
| W2_DEF_PC | low_vol | 40 | 0.057262 | 0.017308 | 0.000827 |
| W2_NOAUTO_VOLUME | high_vol | 52 | 0.031845 | 0.010417 | -0.000228 |
| W2_NOAUTO_VOLUME | low_vol | 40 | 0.064613 | -0.006079 | 0.000772 |


`v6-paired-diagnosis.csv` records each change. `v6-diagnosis-stress.csv` measures robustness against the prior V5 leaders after dropping each month and the five largest individual gains. The last omission is shown below. `stability-stress.csv` extends these checks to the V7 candidates and alternate disjoint sets. `F_DEF_LAG`, `F_DEF_EMBARGO`, and `F_DEF_REV` vary extra delay, earlier label maturity and minor native-price corrections. Their limited score changes do not resolve point-in-time receipt uncertainty.

| model | loss_difference | omission | n | gain |
| --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | Brier_gain_vs_I03 | five largest positive contributions | 87 | 0.001348 |
| F_NO_DEFENSIVE | CRPS_gain_vs_L01 | five largest positive contributions | 87 | -0.000485 |
| W2_DEF_NORM | Brier_gain_vs_I03 | five largest positive contributions | 87 | 0.003958 |
| W2_DEF_NORM | CRPS_gain_vs_L01 | five largest positive contributions | 87 | -0.000438 |
| W2_DEF_PC | Brier_gain_vs_I03 | five largest positive contributions | 87 | 0.002237 |
| W2_DEF_PC | CRPS_gain_vs_L01 | five largest positive contributions | 87 | -0.000696 |
| W2_NOAUTO_VOLUME | Brier_gain_vs_I03 | five largest positive contributions | 87 | -0.004535 |
| W2_NOAUTO_VOLUME | CRPS_gain_vs_L01 | five largest positive contributions | 87 | -0.000012 |


The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history. Brier and log loss score sign probabilities. CRPS scores the entire endpoint return distribution. Lower scores are better. CRPS, MAE and interval widths are in fractional return units. A width of .04 spans four percentage points. Gain means matched control loss minus candidate loss.
