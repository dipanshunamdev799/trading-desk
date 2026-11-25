# NIFTY V8 · Reproduction And Winner Diagnosis

Run `2026-11-24/run-001`. Retrospective research.

All **644** requested weekly forecasts were freshly refit from their actual saved model configurations and cutoff dates. The maximum absolute difference in probability, conditional mean, median, Brier or CRPS was **2.78e-17**. The earlier reconstruction also recovered 81 V4/V5 stored model/fold vectors. `preservation.json` inventories the reviewed V7 index, fifteen reports, registry, full prediction and comparison files, cluster definitions, verification and sources.

The V7 rotation parents use the V6 51-column native set after removing six defensive relative-return columns. The domestic variant adds two five-session spread changes. The embargo and lag variants use the four-input rotation set with the global-relative change and ETF activity change as well. The former places both outer and inner label maturity boundaries three sessions earlier. The latter delays all four additional inputs by five observed sessions. The ETF variant adds the mean abnormal volume and its five-session change. The Elastic Net variant retains the full native set with learned cluster balancing, alpha .0006 and L1 ratio .3, and uses the three-session earlier cutoff. V6 CRPS removes `i_nifty_auto_rel21` and adds five ETF-volume ratios. Train medians impute missing fields after the 30-observation inclusion screen, followed by centering, scaling and ±5 clipping.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T_ROT_DOMESTIC | 92 | 19 | 0.804348 | 0.809869 | 0.162145 | 0.505266 | 0.009927 | 0.012893 | 0.019361 | 0.004989 | 0.543478 | 0.815217 | 0.038873 |
| T_ROT_EMBARGO | 92 | 19 | 0.826087 | 0.835510 | 0.164792 | 0.510975 | 0.009935 | 0.012898 | 0.019147 | 0.004976 | 0.565217 | 0.793478 | 0.040823 |
| T_ROT_LAG5 | 92 | 19 | 0.793478 | 0.803822 | 0.164382 | 0.510143 | 0.010040 | 0.012945 | 0.019537 | 0.005102 | 0.532609 | 0.815217 | 0.040523 |
| T_DAY_ETF | 92 | 19 | 0.782609 | 0.791001 | 0.166525 | 0.515537 | 0.009974 | 0.013004 | 0.019415 | 0.005035 | 0.521739 | 0.804348 | 0.038902 |
| T_ELASTIC_EMBARGO | 92 | 19 | 0.728261 | 0.699806 | 0.184134 | 0.552228 | 0.009665 | 0.012308 | 0.017693 | 0.004888 | 0.576087 | 0.815217 | 0.047453 |
| V6_BRIER | 92 | 19 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.019635 | 0.005068 | 0.510870 | 0.793478 | 0.039009 |
| V6_CRPS | 92 | 19 | 0.750000 | 0.755926 | 0.178802 | 0.541915 | 0.009756 | 0.013051 | 0.018979 | 0.004879 | 0.532609 | 0.771739 | 0.037657 |
| I03_nosize | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| I00 | 92 | 19 | 0.760870 | 0.751814 | 0.186099 | 0.558036 | 0.010224 | 0.013539 | 0.019852 | 0.005143 | 0.554348 | 0.760870 | 0.037708 |
| L01 | 92 | 19 | 0.663043 | 0.653362 | 0.197610 | 0.582153 | 0.009963 | 0.013409 | 0.019166 | 0.004975 | 0.543478 | 0.771739 | 0.036633 |
| V4_D02_student_shrunk | 92 | 19 | 0.608696 | 0.656991 | 0.219759 | 0.629825 | 0.010896 | 0.014707 | 0.020132 | 0.005441 | 0.413043 | 0.673913 | 0.033246 |
| V4_D03_residual_shrunk | 92 | 19 | 0.684783 | 0.648524 | 0.206257 | 0.607870 | 0.011882 | 0.014686 | 0.022780 | 0.006042 | 0.489130 | 0.673913 | 0.031291 |
| V4_M05_lgbm | 92 | 19 | 0.663043 | 0.633043 | 0.226049 | 0.645492 | 0.011817 | 0.015190 | 0.021320 | 0.005852 | 0.423913 | 0.630435 | 0.033626 |
| V4_Z_neutral | 92 | 19 | 0.423913 | 0.500000 | 0.250000 | 0.693147 | 0.012207 | 0.016374 | 0.023210 | 0.006138 | 0.500000 | 0.728261 | 0.039943 |
| E00 | 92 | 19 | 0.576087 | 0.500000 | 0.258296 | 0.709964 | 0.012210 | 0.016374 | 0.023210 | 0.006135 | 0.500000 | 0.728261 | 0.039943 |


| model | fold | n | correct | brier_gain_vs_v6 | crps_gain_vs_v6 |
| --- | --- | --- | --- | --- | --- |
| T_DAY_ETF | 2026-07 | 23 | 13 | 0.003713 | -0.000002 |
| T_DAY_ETF | 2026-08 | 21 | 18 | 0.001623 | -0.000041 |
| T_DAY_ETF | 2026-09 | 21 | 19 | -0.003343 | 0.000098 |
| T_DAY_ETF | 2026-10 | 20 | 16 | 0.003310 | 0.000011 |
| T_DAY_ETF | 2026-11 | 7 | 6 | 0.026587 | 0.001033 |
| T_ELASTIC_EMBARGO | 2026-07 | 23 | 14 | 0.045872 | -0.000146 |
| T_ELASTIC_EMBARGO | 2026-08 | 21 | 16 | -0.050116 | -0.000991 |
| T_ELASTIC_EMBARGO | 2026-09 | 21 | 20 | 0.002151 | 0.000209 |
| T_ELASTIC_EMBARGO | 2026-10 | 20 | 14 | -0.029958 | 0.001895 |
| T_ELASTIC_EMBARGO | 2026-11 | 7 | 3 | -0.109580 | 0.002697 |
| T_ROT_DOMESTIC | 2026-07 | 23 | 13 | 0.018877 | 0.000361 |
| T_ROT_DOMESTIC | 2026-08 | 21 | 18 | 0.002903 | 0.000103 |
| T_ROT_DOMESTIC | 2026-09 | 21 | 20 | -0.005328 | -0.000329 |
| T_ROT_DOMESTIC | 2026-10 | 20 | 17 | 0.008888 | 0.000260 |
| T_ROT_DOMESTIC | 2026-11 | 7 | 6 | 0.020502 | 0.000603 |
| T_ROT_EMBARGO | 2026-07 | 23 | 13 | 0.012783 | 0.000115 |
| T_ROT_EMBARGO | 2026-08 | 21 | 18 | -0.002359 | -0.000307 |
| T_ROT_EMBARGO | 2026-09 | 21 | 20 | -0.016193 | -0.000484 |
| T_ROT_EMBARGO | 2026-10 | 20 | 18 | 0.018121 | 0.000890 |
| T_ROT_EMBARGO | 2026-11 | 7 | 7 | 0.027732 | 0.001193 |
| T_ROT_LAG5 | 2026-07 | 23 | 13 | 0.004587 | -0.000099 |
| T_ROT_LAG5 | 2026-08 | 21 | 18 | 0.006463 | -0.000063 |
| T_ROT_LAG5 | 2026-09 | 21 | 20 | 0.009703 | -0.000020 |
| T_ROT_LAG5 | 2026-10 | 20 | 16 | 0.006714 | 0.000467 |
| T_ROT_LAG5 | 2026-11 | 7 | 6 | -0.011505 | -0.000399 |
| V6_BRIER | 2026-07 | 23 | 13 | 0.000000 | 0.000000 |
| V6_BRIER | 2026-08 | 21 | 18 | 0.000000 | -0.000000 |
| V6_BRIER | 2026-09 | 21 | 19 | 0.000000 | -0.000000 |
| V6_BRIER | 2026-10 | 20 | 16 | 0.000000 | -0.000000 |
| V6_BRIER | 2026-11 | 7 | 6 | 0.000000 | 0.000000 |
| V6_CRPS | 2026-07 | 23 | 13 | 0.035620 | 0.000819 |
| V6_CRPS | 2026-08 | 21 | 17 | -0.021878 | 0.000171 |
| V6_CRPS | 2026-09 | 21 | 19 | -0.008698 | -0.000353 |
| V6_CRPS | 2026-10 | 20 | 15 | -0.036275 | 0.000376 |
| V6_CRPS | 2026-11 | 7 | 5 | -0.039940 | 0.000878 |


Every correct and incorrect call is in `winner-origin-diagnosis.csv`. Full atoms and probability masses are in `reproduced-endpoint-laws.jsonl`, with fitted weights in `winner-coefficients.csv`. `reproduction.json` carries all training, validation and query anchor information. The conditional endpoint law gives 65% mass to a modeled mean plus residuals from a purged 42-origin validation partition; 35% comes from at most 252 earlier matured outcomes. Source data come from frozen Upstox/NSE archives and inherited global time alignments. Reconstructed historical receipt times remain the main timestamp limitation. V8 computes spread changes over the underlying raw warmup. That permits five earlier values with sufficient raw history which V7's reindexed difference left missing. Consequently V8 `B_ROT` is a very close refit and the exact V7 result remains the directly replayed reference.

The primary weekly cohort has 92 overlapping origins, 19 disjoint windows and a return-ACF ESS of about 12.36. Monthly evaluation has 76 overlapping origins and approximately four disjoint windows. Dependence diagnostics are not independent trials.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
