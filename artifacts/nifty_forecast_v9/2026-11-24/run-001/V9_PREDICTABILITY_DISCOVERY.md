# NIFTY V9 · Predictability Discovery

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

V9 estimates the conditions under which an already issued historical reconstruction might be useful. The training outcomes are future Brier, CRPS, correct signs, central interval coverage and expert-vs-history loss differences, each computed from a prequential origin forecast and unseen until its endpoint matured. A reliability fit at a monthly anchor uses at most 126 prior resolved forecast origins and needs 35. This withholds assessment on the earliest windows. A separate origin-time recent-loss feature uses only labels ending strictly before that origin. Forecast probabilities and underlying financial conditions are archived with the assessment rows.

The domestic gate includes trend consistency, sector synchronization, breadth, concentration, banking/defensive leadership, volatility level/change, turnover, prior resolved losses, predictive disagreement and distance from prior feature states. The global gate adds jointly available foreign variables. To select forecasts, the predicted gain must exceed its training-time 60th-percentile threshold. Bullish and bearish subgroups use the rotation forecast’s 0.5 sign threshold. The follow-up post-forecast coverage is computed on the exact selected dates.

| cohort | horizon | selection | n | disjoint | coverage_of_cohort | accuracy | brier | crps | matched_history_Brier | matched_history_CRPS | interval80_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | 5 | all_assessed | 120 | 24 | 0.693642 | 0.516667 | 0.297606 | 0.015521 | 0.265770 | 0.013158 | 0.708333 |
| early | 5 | selected | 61 | 17 | 0.352601 | 0.508197 | 0.289555 | 0.011437 | 0.268564 | 0.010639 | 0.770492 |
| early | 5 | abstain | 59 | 16 | 0.341040 | 0.525424 | 0.305930 | 0.019744 | 0.262882 | 0.015763 | 0.644068 |
| early | 5 | unfamiliar | 60 | 14 | 0.346821 | 0.433333 | 0.346634 | 0.018570 | 0.274200 | 0.015467 | 0.533333 |
| early | 5 | familiar | 60 | 17 | 0.346821 | 0.600000 | 0.248577 | 0.012473 | 0.257341 | 0.010849 | 0.883333 |
| early | 5 | selected_bullish | 41 | 12 | 0.236994 | 0.365854 | 0.330560 | 0.012742 | 0.256809 | 0.010565 | 0.731707 |
| early | 5 | selected_bearish | 20 | 8 | 0.115607 | 0.800000 | 0.205495 | 0.008762 | 0.292663 | 0.010791 | 0.850000 |
| early | 21 | all_assessed | 79 | 4 | 0.560284 | 0.683544 | 0.237775 | 0.026166 | 0.247186 | 0.020374 | 0.696203 |
| early | 21 | selected | 30 | 3 | 0.212766 | 0.600000 | 0.294484 | 0.025125 | 0.227585 | 0.021550 | 0.500000 |
| early | 21 | abstain | 49 | 3 | 0.347518 | 0.734694 | 0.203055 | 0.026803 | 0.259186 | 0.019655 | 0.816327 |
| early | 21 | unfamiliar | 27 | 2 | 0.191489 | 0.629630 | 0.279449 | 0.035584 | 0.231846 | 0.030195 | 0.259259 |
| early | 21 | familiar | 52 | 3 | 0.368794 | 0.711538 | 0.216137 | 0.021276 | 0.255151 | 0.015275 | 0.923077 |
| early | 21 | selected_bullish | 26 | 2 | 0.184397 | 0.653846 | 0.273988 | 0.024338 | 0.231727 | 0.023481 | 0.500000 |
| early | 21 | selected_bearish | 4 | 1 | 0.028369 | 0.250000 | 0.427710 | 0.030240 | 0.200669 | 0.009000 | 0.500000 |
| later | 5 | all_assessed | 92 | 19 | 1.000000 | 0.793478 | 0.164236 | 0.009995 | 0.258296 | 0.012210 | 0.771739 |
| later | 5 | selected | 52 | 13 | 0.565217 | 0.750000 | 0.168859 | 0.010404 | 0.253088 | 0.012740 | 0.826923 |
| later | 5 | abstain | 40 | 11 | 0.434783 | 0.850000 | 0.158225 | 0.009464 | 0.265066 | 0.011522 | 0.700000 |
| later | 5 | unfamiliar | 10 | 3 | 0.108696 | 0.700000 | 0.170945 | 0.025808 | 0.297573 | 0.028427 | 0.500000 |
| later | 5 | familiar | 82 | 17 | 0.891304 | 0.804878 | 0.163417 | 0.008067 | 0.253506 | 0.010233 | 0.804878 |
| later | 5 | selected_bullish | 28 | 7 | 0.304348 | 0.642857 | 0.212421 | 0.015576 | 0.268794 | 0.017924 | 0.714286 |
| later | 5 | selected_bearish | 24 | 6 | 0.260870 | 0.875000 | 0.118037 | 0.004371 | 0.234765 | 0.006691 | 0.958333 |
| later | 21 | all_assessed | 76 | 4 | 1.000000 | 0.473684 | 0.302623 | 0.031609 | 0.279282 | 0.028363 | 0.486842 |
| later | 21 | selected | 6 | 2 | 0.078947 | 0.000000 | 0.452296 | 0.042105 | 0.296939 | 0.033195 | 0.000000 |
| later | 21 | abstain | 70 | 4 | 0.921053 | 0.514286 | 0.289794 | 0.030710 | 0.277769 | 0.027948 | 0.528571 |
| later | 21 | familiar | 76 | 4 | 1.000000 | 0.473684 | 0.302623 | 0.031609 | 0.279282 | 0.028363 | 0.486842 |
| later | 21 | selected_bullish | 5 | 1 | 0.065789 | 0.000000 | 0.466259 | 0.030372 | 0.317523 | 0.020334 | 0.000000 |
| later | 21 | selected_bearish | 1 | 1 | 0.013158 | 0.000000 | 0.382483 | 0.100771 | 0.194019 | 0.097501 | 0.000000 |


Later weekly selection takes **52 of 92** dates, with **75%** accuracy and **.168859 Brier** compared with **.253088** for historical on those dates. The abstained 40 later dates actually have **85%** accuracy and **.158225** Brier for the same rotation model. About 35.26% of the earlier cohort is selected, and earlier selected Brier **.289555** loses to its matched historical **.268564**. Later selected bearish cases look attractive at **87.5%** on 24 origins, but only six disjoint targets and an earlier bearish slice of 20 origins make this descriptive. The later monthly gate selected only six origins and got zero directions right. Selective forecasting therefore failed as a generally reliable filter. Historical date-conditioned uncertainty is preserved with each slice, and no small-slice win rate is interpreted independently.

| cohort | horizon | n | assessed | IC_predicted_brier | IC_predicted_crps | IC_predicted_correctness | IC_predicted_interval_coverage | IC_mahalanobis | IC_expert_p_disagreement | IC_parameter_uncertainty | dom_vol_mae | global_vol_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | 5 | 173 | 120 | -0.135736 | 0.214661 | -0.022145 | -0.188686 | 0.286651 | 0.125265 | 0.400438 | 0.074563 | 0.066883 |
| early | 21 | 141 | 79 | -0.244187 | 0.436173 | -0.316284 | -0.135185 | -0.259125 | 0.204951 | 0.297980 | 0.102450 | 0.096693 |
| later | 5 | 92 | 92 | 0.026180 | 0.090501 | -0.105659 | 0.143841 | -0.096510 | -0.422450 | -0.005410 | 0.055356 | 0.056184 |
| later | 21 | 76 | 76 | 0.115210 | 0.065072 | -0.079282 | 0.166200 | 0.340414 | -0.577891 | -0.626029 | 0.043957 | 0.046798 |

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
