# NIFTY V7 · Final Research Conclusions

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

V7 improves the retrospective weekly point scores. It finds a direct regularization effect for exact correlated duplication and a narrower candidate based on relative sector rotation. Neither improvement establishes an independent forecasting edge. The rotation Brier winner and the Elastic Net CRPS winner are different systems and neither beats the other on both objectives.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V6_BRIER | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| V6_CRPS | 92 | 0.750000 | 0.755926 | 0.178802 | 0.541915 | 0.009756 | 0.013051 | 0.012609 | 0.018979 | 0.532609 | 0.771739 | 0.037657 |
| T_ROT_DOMESTIC | 92 | 0.804348 | 0.809869 | 0.162145 | 0.505266 | 0.009927 | 0.012893 | 0.012447 | 0.019361 | 0.543478 | 0.815217 | 0.038873 |
| L_DAILY | 92 | 0.782609 | 0.791001 | 0.166724 | 0.515487 | 0.009893 | 0.012946 | 0.012465 | 0.019186 | 0.532609 | 0.804348 | 0.038713 |
| C_ELASTIC | 92 | 0.771739 | 0.757862 | 0.184607 | 0.554242 | 0.009695 | 0.012635 | 0.011999 | 0.018339 | 0.532609 | 0.804348 | 0.042881 |
| T_ELASTIC_EMBARGO | 92 | 0.728261 | 0.699806 | 0.184134 | 0.552228 | 0.009665 | 0.012308 | 0.011505 | 0.017693 | 0.576087 | 0.815217 | 0.047453 |
| J_EQUAL | 92 | 0.771739 | 0.778181 | 0.172391 | 0.527888 | 0.009825 | 0.012994 | 0.012434 | 0.019218 | 0.521739 | 0.804348 | 0.038983 |
| J_JOINT | 92 | 0.782609 | 0.791001 | 0.171066 | 0.525238 | 0.009865 | 0.013053 | 0.012460 | 0.019341 | 0.521739 | 0.793478 | 0.038514 |


The best weekly Brier is .162145 versus V6 .169803, a 4.51% relative gain. The adaptive domestic rotation model gets 74 of 92 directions correct, 80.43%, with 81.52% coverage for its nominal 80% interval. Its 10-session-block adjusted improvement interval is approximately [−.006942,.022257]. The best CRPS is .009665 versus V6 .009756, a gain of about .93%. It comes from the earlier maturity cutoff in the cluster-balanced Elastic Net follow-up. It loses to V6 on Brier and has an adjusted CRPS gain interval of [−.001986,.002167]. The original clustered fit at .009695 offers a cleaner comparison before the adaptive cutoff test.

Retain the frozen V6 controls, domestic rotation, clustered Elastic Net and daily opening/closing plus ETF activity as separate hypotheses. The best weekly probability result deteriorates with a shorter revised training window. Exact duplication identifies how weighting changes fitted output. It cannot establish that the same effects will produce reliable gains outside this cohort. Rolled, delayed and matched weak controls remain visible in the delivery.

Monthly `M_STATE_LAG21` improves the point Brier to .171774 and interval coverage to 84.21%, while CRPS .025530 trails the earlier .024530 monthly exploratory law. Shifted state controls with CRPS .023773 and .024168 undermine the interpretation of date-specific information. Four disjoint return windows are insufficient to promote a monthly model. Weekly and monthly remain the primary horizons at five and 21 sessions.

The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history. Brier and log loss score sign probabilities. CRPS scores the entire endpoint return distribution. Lower scores are better. CRPS, MAE and interval widths are in fractional return units. A width of .04 spans four percentage points. Gain means matched control loss minus candidate loss.
