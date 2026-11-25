# NIFTY V6 — Monthly Research

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Four disjoint evaluation windows

The76 origins span only approximately four nonoverlapping21-session outcomes. They have heavily overlapping return paths and substantial prior model-search exposure. There is no monthly confidence interval: the predeclared minimum8H origins is168, versus76 available. Small-sample uncertainty is not converted into precise claims by repeated cross-sectional observations or by an attractive accuracy percentage.

## Weekly-state aggregation and persistent-state alternatives

M_WEEKSTATE uses four price/risk fields plus16 reconstructed weekly forecast-state levels/slopes: p(up), mean, expected absolute return and endpoint standard deviation for I03/L01, each with a five-session slope. States are generated before their own outcomes, not compounded probabilities. Empty early history remains empty; dates before first valid reconstructed forecasts are excluded from training rather than filled with hindsight. M_PERSIST uses four slow state/persistence/transition fields instead. Later attribution controls share the same state-eligible training dates, distinguish levels from slopes, introduce one extra state lag, and try a robust native model on that same shorter window.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| L01 | 76 | 0.447368 | 0.518280 | 0.313912 | 0.837404 | 0.029553 | 0.036865 | 0.046465 | 0.328947 | 0.486842 | 0.073482 |
| V4_D02_student_shrunk | 76 | 0.500000 | 0.557706 | 0.260640 | 0.717106 | 0.027553 | 0.035114 | 0.042924 | 0.302632 | 0.394737 | 0.063923 |
| E00 | 76 | 0.407895 | 0.500000 | 0.279282 | 0.752849 | 0.028363 | 0.037393 | 0.048794 | 0.263158 | 0.618421 | 0.072749 |
| M_WEEKSTATE | 76 | 0.815789 | 0.834409 | 0.178345 | 0.543811 | 0.024823 | 0.033410 | 0.043058 | 0.381579 | 0.657895 | 0.076202 |
| M2_STATE_LAG1 | 76 | 0.750000 | 0.763799 | 0.175091 | 0.534801 | 0.024530 | 0.032281 | 0.043442 | 0.328947 | 0.605263 | 0.072894 |
| M2_WINDOW_SMALL | 76 | 0.394737 | 0.483871 | 0.405100 | 1.067923 | 0.034675 | 0.042316 | 0.053362 | 0.250000 | 0.407895 | 0.079178 |
| M2_WINDOW_NATIVE | 76 | 0.407895 | 0.500000 | 0.402937 | 1.068168 | 0.043235 | 0.056652 | 0.061003 | 0.236842 | 0.434211 | 0.100164 |
| M2_LEVELS | 76 | 0.657895 | 0.706093 | 0.217249 | 0.623238 | 0.027121 | 0.036278 | 0.044157 | 0.342105 | 0.552632 | 0.076441 |
| M2_SLOPES | 76 | 0.407895 | 0.494982 | 0.377544 | 1.003980 | 0.033571 | 0.041555 | 0.052009 | 0.223684 | 0.407895 | 0.076604 |
| M2_HUBER_WINDOW | 76 | 0.763158 | 0.734767 | 0.186174 | 0.563472 | 0.047917 | 0.066887 | 0.082585 | 0.578947 | 0.750000 | 0.157716 |
| M_PERSIST | 76 | 0.552632 | 0.562007 | 0.275664 | 0.754286 | 0.029292 | 0.038198 | 0.048625 | 0.210526 | 0.578947 | 0.061087 |
| A_STUDENT | 76 | 0.513158 | 0.588889 | 0.279302 | 0.758737 | 0.026064 | 0.035402 | 0.043329 | 0.328947 | 0.552632 | 0.082517 |
| M_RISK_PANEL | 76 | 0.513158 | 0.588889 | 0.256160 | 0.705653 | 0.026727 | 0.035602 | 0.045155 | 0.368421 | 0.578947 | 0.078354 |


M_WEEKSTATE achieves62/76=81.58% accuracy, Brier.178345 and CRPS.024823. Its nominal80% interval covers only65.79%, and50% interval38.16%. One extra lag lowers Brier to.175091 and CRPS.024530 but80% coverage falls to60.53%,50% to32.89%. These are not well-calibrated monthly confidence statements. The price-only and full-native date-matched controls are much worse, but levels alone and slopes alone are also worse: the interaction between representation, training window and shrinkage is not isolated by their aggregate accuracy.

## Falsification changed the decision

| model | shift | n | accuracy | brier | crps | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DIAGNOSTIC_STATE | 5 | 76 | 0.723684 | 0.180286 | 0.022269 | 0.723684 | 0.080597 |
| DIAGNOSTIC_STATE | 21 | 76 | 0.828947 | 0.160615 | 0.024866 | 0.763158 | 0.089907 |
| DIAGNOSTIC_STATE | 42 | 76 | 0.513158 | 0.255189 | 0.027352 | 0.552632 | 0.072982 |
| DIAGNOSTIC_TARGET | 21 | 76 | 0.473684 | 0.384946 | 0.037052 | 0.473684 | 0.077296 |
| DIAGNOSTIC_TARGET | 42 | 76 | 0.263158 | 0.487970 | 0.045121 | 0.407895 | 0.090630 |
| DIAGNOSTIC_TARGET | 63 | 76 | 0.210526 | 0.460830 | 0.038678 | 0.394737 | 0.090225 |


All state-input rolls preserve broad temporal structure and use only training partitions; they are diagnostic corruptions rather than eligible forecasting systems. The21-session state roll produces Brier.160615, better than the actual state model. Thefive-session roll has CRPS.022269, also better. These retain genuine price controls and marginal regime information, so competitive results do not prove leakage. They do show that exact dated weekly-state information has not been established as the source of the gain. M_WEEKSTATE and M2_STATE_LAG1 remain INCONCLUSIVE / monthly block-null mechanism not passed.

The earlier native-target nulls are also cautionary: weekly3H/7H/11H rolls give bad Brier(.280229/.263407/.305512), while one monthly11H roll still gives Brier.216351 and CRPS.023929. A favorable monthly corruption is plausible with four outcome windows and regime drift; we do not claim all monthly nulls failed as desired. No null is selected as a real model.

## Broader risk panel without pseudo-replication

M_RISK_PANEL learns future21-session sector RMS/origin trailing-volatility log ratios using native sector histories, five risk/state inputs, and inverse count-per-date sample weights. The target ratio is clipped to[1/3,3], the predicted ratio to[.5,2]. Its NIFTY mean is half native conditional mean/half historical mean, with Studentdf5 endpoint atoms and35% historical shrinkage. Sector-date rows enrich estimation of a common risk relationship; they do not become independent monthly NIFTY outcomes. Each training row's21-session endpoint must mature before cutoff.

On76 NIFTY outcomes the separate risk auxiliary has mean annualized-volatility MAE 0.043687 and QLIKE 0.404976; endpoint CRPS.026727/Brier.256160. Future realized volatility and endpoint-return standard deviation remain different quantities. This panel is a limited risk-estimation diagnostic, not evidence of monthly directional edge; no separate matched auxiliary risk benchmark was established, so its raw auxiliary losses do not demonstrate an improvement.

## Intermediate horizon diagnostics

| horizon | model | n | disjoint_n | accuracy | brier | crps | relative_crps_gain | normalized_brier_gain | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | A_STUDENT | 76 | 8 | 0.526316 | 0.250546 | 0.012052 | -0.039107 | 0.000170 | 0.776316 |
| 10 | H_DYNAMIC_CORE | 76 | 8 | 0.394737 | 0.310169 | 0.012989 | -0.119937 | -0.059453 | 0.776316 |
| 10 | J_EQUAL | 76 | 8 | 0.460526 | 0.266242 | 0.011864 | -0.022919 | -0.015526 | 0.736842 |
| 10 | R_I03 | 76 | 8 | 0.486842 | 0.259331 | 0.011822 | -0.019294 | -0.008615 | 0.710526 |
| 15 | A_STUDENT | 76 | 6 | 0.486842 | 0.272523 | 0.017379 | 0.013813 | -0.015667 | 0.723684 |
| 15 | H_DYNAMIC_CORE | 76 | 6 | 0.447368 | 0.295927 | 0.019222 | -0.090789 | -0.039072 | 0.605263 |
| 15 | J_EQUAL | 76 | 6 | 0.486842 | 0.260182 | 0.018819 | -0.067908 | -0.003326 | 0.605263 |
| 15 | R_I03 | 76 | 6 | 0.526316 | 0.267956 | 0.019511 | -0.107205 | -0.011100 | 0.697368 |


Ten-/15-session comparisons use the same76 original monthly origins, their own correctly aligned targets, own matured training and own historical return baselines. Relative CRPS gain normalizes by that horizon's historical loss; raw CRPS is not directly a horizon-invariant predictability measure. The eight diagnostic model/horizon cells are exploratory and do not redefine the primary five-/21-session objectives. Some results change sharply rather than smoothly, but the limited common dates cannot distinguish a true predictability boundary from regime/target overlap.

## Decision

Keep the monthly state interaction as a falsified/inconclusive mechanism lead and retain the simpler Student/risk-panel distributions as research comparisons. Do not operationally promote the best monthly accuracy, infer narrow probabilities from these four windows, or claim the global mediators fixed monthly forecasting. All monthly fit failures, bad slopes/Huber variants, undercoverage and competitive corrupted controls are retained.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.

[Standalone research figure](monthly-falsification.png)
