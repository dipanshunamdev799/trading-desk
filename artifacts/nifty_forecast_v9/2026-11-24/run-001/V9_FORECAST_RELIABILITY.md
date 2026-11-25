# NIFTY V9 · Forecast Reliability

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

We measured three different uncertainties. The predictive return law supplies expected width, entropy and return risk. Approximate parameter uncertainty comes from an innovation-scale-adjusted Ridge leverage calculation in a compact feature space. Applicability uses Ledoit–Wolf Mahalanobis distance, mean Euclidean distance to the eight nearest historical rows, recent-versus-expanding covariance shift, disagreement and recently resolved loss. These are calculated from historical state geometry rather than forecast outcomes still in progress. The Ridge posterior-style scale is an approximation. It is not a confidence guarantee for the fitted model.

| cohort | horizon | assessed | IC_predicted_brier | IC_predicted_crps | IC_mahalanobis | IC_expert_p_disagreement | IC_parameter_uncertainty | IC_predicted_interval_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | 5 | 120 | -0.135736 | 0.214661 | 0.286651 | 0.125265 | 0.400438 | -0.188686 |
| early | 21 | 79 | -0.244187 | 0.436173 | -0.259125 | 0.204951 | 0.297980 | -0.135185 |
| later | 5 | 92 | 0.026180 | 0.090501 | -0.096510 | -0.422450 | -0.005410 | 0.143841 |
| later | 21 | 76 | 0.115210 | 0.065072 | 0.340414 | -0.577891 | -0.626029 | 0.166200 |


| cohort | horizon | selection | n | disjoint | accuracy | brier | crps | matched_history_Brier | matched_history_CRPS | interval80_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | 5 | unfamiliar | 60 | 14 | 0.433333 | 0.346634 | 0.018570 | 0.274200 | 0.015467 | 0.533333 |
| early | 5 | familiar | 60 | 17 | 0.600000 | 0.248577 | 0.012473 | 0.257341 | 0.010849 | 0.883333 |
| early | 21 | unfamiliar | 27 | 2 | 0.629630 | 0.279449 | 0.035584 | 0.231846 | 0.030195 | 0.259259 |
| early | 21 | familiar | 52 | 3 | 0.711538 | 0.216137 | 0.021276 | 0.255151 | 0.015275 | 0.923077 |
| later | 5 | unfamiliar | 10 | 3 | 0.700000 | 0.170945 | 0.025808 | 0.297573 | 0.028427 | 0.500000 |
| later | 5 | familiar | 82 | 17 | 0.804878 | 0.163417 | 0.008067 | 0.253506 | 0.010233 | 0.804878 |
| later | 21 | familiar | 76 | 4 | 0.473684 | 0.302623 | 0.031609 | 0.279282 | 0.028363 | 0.486842 |


Unfamiliar earlier weekly states have Brier **.346634** versus **.248577** in familiar states. Their CRPS and interval failures also worsen. Earlier 5-session parameter-uncertainty rank correlation with CRPS is **.400438**, and Mahalanobis rank correlation with Brier **.286651**. These relationships do not transfer cleanly to the later cohort. A reliability rule can diagnose a riskier subset without producing a higher aggregate payoff after fallback. The OOD-weighted complete law is a more balanced candidate than pure rotation for the combined weekly dates but does not dominate fixed fallback or the frozen later leader. This is a prospective research hypothesis. Model disagreement also can be higher in a period containing useful active forecasts, so low agreement should not be interpreted automatically as lack of skill.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
