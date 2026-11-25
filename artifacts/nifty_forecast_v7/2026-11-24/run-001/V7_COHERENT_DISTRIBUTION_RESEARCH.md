# NIFTY V7 · Coherent Distribution Research

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

The reference laws combine purged inner residual atoms with mature historical empirical returns using 65/35 mass. Tests compare Student df5 residuals, risk-scaled residuals, sorted/interpolated quantiles, fixed complete-law mixtures, training-optimized complete-law mixtures and reweighting positive return atoms. Quantile forecasts sort five fitted quantiles and clamp the sampled interpolation tails outside .10/.90. This can distort tail probabilities. Record-level endpoint mean, median, quantiles, buckets and p(up) always come from the same finite law. `expected_endpoint` rescales the mean by the actual origin close. Path probabilities are outside the return-law interpretation.

Mixture and tilt estimates use the latest 42 reconstructed forecasts with outcomes maturing strictly before their current fit anchor. We constrain the joint weight to [.1,.9] and penalize deviations from .5. The objective is mean CRPS/.02 plus Brier/.25 plus .25(w−.5)². Sign tilt multiplies positive atom weights by exp(shift), with shift in [−.5,.5], selecting by Brier plus .15 times squared shift. These calibrations use historical-only past forecasts reconstructed in this run, with actual prequential timing checked in `integration-ledger.json`.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V6_BRIER | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| V6_CRPS | 92 | 0.750000 | 0.755926 | 0.178802 | 0.541915 | 0.009756 | 0.013051 | 0.012609 | 0.018979 | 0.532609 | 0.771739 | 0.037657 |
| D_SPARSE | 92 | 0.619565 | 0.669811 | 0.220960 | 0.631158 | 0.010387 | 0.014611 | 0.014544 | 0.019243 | 0.456522 | 0.815217 | 0.043259 |
| D_RISK | 92 | 0.771739 | 0.771408 | 0.180257 | 0.546517 | 0.010532 | 0.013752 | 0.013301 | 0.020892 | 0.500000 | 0.760870 | 0.037268 |
| D_QUANTILE | 92 | 0.706522 | 0.731737 | 0.213886 | 0.619923 | 0.011139 | 0.015011 | 0.014866 | 0.020666 | 0.510870 | 0.673913 | 0.037451 |
| D_ETF_STUDENT | 92 | 0.706522 | 0.738510 | 0.202834 | 0.593504 | 0.009720 | 0.013646 | 0.013456 | 0.018252 | 0.510870 | 0.782609 | 0.041844 |
| J_EQUAL | 92 | 0.771739 | 0.778181 | 0.172391 | 0.527888 | 0.009825 | 0.012994 | 0.012434 | 0.019218 | 0.521739 | 0.804348 | 0.038983 |
| J_JOINT | 92 | 0.782609 | 0.791001 | 0.171066 | 0.525238 | 0.009865 | 0.013053 | 0.012460 | 0.019341 | 0.521739 | 0.793478 | 0.038514 |
| J_TILT | 92 | 0.793478 | 0.800435 | 0.168143 | 0.517776 | 0.010074 | 0.013077 | 0.012706 | 0.019761 | 0.510870 | 0.793478 | 0.038929 |
| L_DAILY | 92 | 0.782609 | 0.791001 | 0.166724 | 0.515487 | 0.009893 | 0.012946 | 0.012465 | 0.019186 | 0.532609 | 0.804348 | 0.038713 |
| C_ELASTIC | 92 | 0.771739 | 0.757862 | 0.184607 | 0.554242 | 0.009695 | 0.012635 | 0.011999 | 0.018339 | 0.532609 | 0.804348 | 0.042881 |
| T_ELASTIC_EMBARGO | 92 | 0.728261 | 0.699806 | 0.184134 | 0.552228 | 0.009665 | 0.012308 | 0.011505 | 0.017693 | 0.576087 | 0.815217 | 0.047453 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V6_MONTH_STATE | 76 | 0.815789 | 0.834409 | 0.178345 | 0.543811 | 0.024823 | 0.033410 | 0.033957 | 0.043058 | 0.381579 | 0.657895 | 0.076202 |
| V6_MONTH_LAG1 | 76 | 0.750000 | 0.763799 | 0.175091 | 0.534801 | 0.024530 | 0.032281 | 0.033132 | 0.043442 | 0.328947 | 0.605263 | 0.072894 |
| D_SPARSE | 76 | 0.473684 | 0.555556 | 0.291302 | 0.786637 | 0.027613 | 0.037141 | 0.038108 | 0.045455 | 0.263158 | 0.539474 | 0.081476 |
| D_RISK | 76 | 0.500000 | 0.537634 | 0.304178 | 0.824189 | 0.031830 | 0.039464 | 0.039649 | 0.051165 | 0.263158 | 0.447368 | 0.059944 |
| D_QUANTILE | 76 | 0.460526 | 0.524373 | 0.279117 | 0.757580 | 0.027856 | 0.035503 | 0.035718 | 0.044634 | 0.157895 | 0.421053 | 0.047546 |
| D_ETF_STUDENT | 76 | 0.526316 | 0.594982 | 0.279880 | 0.762436 | 0.026552 | 0.035697 | 0.036414 | 0.044398 | 0.328947 | 0.539474 | 0.081608 |
| J_EQUAL | 76 | 0.565789 | 0.598208 | 0.264065 | 0.727239 | 0.030025 | 0.038672 | 0.037270 | 0.049480 | 0.315789 | 0.513158 | 0.073877 |
| J_JOINT | 76 | 0.565789 | 0.598208 | 0.266381 | 0.732497 | 0.030190 | 0.038853 | 0.037548 | 0.049723 | 0.315789 | 0.513158 | 0.073739 |
| J_TILT | 76 | 0.434211 | 0.467025 | 0.319371 | 0.854639 | 0.032273 | 0.041155 | 0.040103 | 0.052140 | 0.315789 | 0.500000 | 0.069485 |


The equal mixture yields Brier .172391, CRPS .009825 and 80.43% interval coverage. Joint tuning improves Brier to .171066 relative to equal weighting but raises CRPS to .009865. Sign tilting has Brier .168143 and CRPS .010074. These mixture variants do not deliver joint dominance over the separate V6 winners. The best new point-score distribution is the later Elastic Net embargo sensitivity with .009665 CRPS, .184134 Brier and 81.52% coverage. Its gain over V6 CRPS is approximately .000090, with a 10-session-block simultaneous interval spanning −.001986 to .002167. Raw proper and pinball losses, regime coverage, widths and probability bin calibration remain available in the saved tables.

| model | state | n | disjoint | brier | crps | coverage80 | nominal_width80 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C_ELASTIC | high_vol | 52 | 11 | 0.207948 | 0.012182 | 0.788462 | 0.052475 |
| C_ELASTIC | low_vol | 40 | 8 | 0.154264 | 0.006462 | 0.825000 | 0.030409 |
| L_DAILY | high_vol | 52 | 11 | 0.191484 | 0.012898 | 0.750000 | 0.040997 |
| L_DAILY | low_vol | 40 | 8 | 0.134536 | 0.005986 | 0.875000 | 0.035743 |
| T_ELASTIC_EMBARGO | high_vol | 52 | 11 | 0.207139 | 0.012144 | 0.807692 | 0.056344 |
| T_ELASTIC_EMBARGO | low_vol | 40 | 8 | 0.154227 | 0.006443 | 0.825000 | 0.035894 |
| T_ROT_DOMESTIC | high_vol | 52 | 11 | 0.186732 | 0.012831 | 0.769231 | 0.041567 |
| T_ROT_DOMESTIC | low_vol | 40 | 8 | 0.130181 | 0.006152 | 0.875000 | 0.035370 |


The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history. Brier and log loss score sign probabilities. CRPS scores the entire endpoint return distribution. Lower scores are better. CRPS, MAE and interval widths are in fractional return units. A width of .04 spans four percentage points. Gain means matched control loss minus candidate loss.
