# NIFTY V6 — Coherent Distributions

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Different leads describe different qualities

I03 is the prior probability lead (weekly Brier.182046521,accuracy76.09%); L01 has better distribution score (.009962817) but worse Brier(.197610292) and66.30% accuracy. L01's native family includes size plus15 ETF fields, whereas I03 excludes size and recomputes aggregates. Thus their difference is not attributable to one isolated factor. Mean error, expected absolute return, endpoint downside probabilities and bucket calibration are preserved per origin. Endpoint standard deviation is not forecast future realized path volatility. Endpoint probability below−2%/−5% is not probability of touching a drawdown barrier.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| L01 | 92 | 0.663043 | 0.653362 | 0.197610 | 0.582153 | 0.009963 | 0.013409 | 0.019166 | 0.543478 | 0.771739 | 0.036633 |
| J_EQUAL | 92 | 0.771739 | 0.771408 | 0.188184 | 0.562140 | 0.010013 | 0.013393 | 0.019428 | 0.543478 | 0.782609 | 0.037157 |
| J_BRIER | 92 | 0.760870 | 0.765360 | 0.188216 | 0.562009 | 0.010114 | 0.013510 | 0.019624 | 0.543478 | 0.760870 | 0.036272 |
| J_CRPS | 92 | 0.728261 | 0.726899 | 0.190551 | 0.566827 | 0.010073 | 0.013489 | 0.019518 | 0.554348 | 0.760870 | 0.036154 |
| J_COMBINED | 92 | 0.760870 | 0.765360 | 0.189529 | 0.564663 | 0.010124 | 0.013535 | 0.019628 | 0.543478 | 0.760870 | 0.035984 |
| J_SIGN | 92 | 0.760870 | 0.768747 | 0.183867 | 0.553231 | 0.010219 | 0.013568 | 0.019816 | 0.521739 | 0.750000 | 0.037707 |
| Q_ETF_VOLUME | 92 | 0.750000 | 0.759313 | 0.183198 | 0.551577 | 0.009936 | 0.013289 | 0.019186 | 0.500000 | 0.771739 | 0.038041 |
| W2_NOAUTO_VOLUME | 92 | 0.750000 | 0.755926 | 0.178802 | 0.541915 | 0.009756 | 0.013051 | 0.018979 | 0.532609 | 0.771739 | 0.037657 |


## Five integration experiments

J_EQUAL averages the two complete laws at50/50. J_BRIER/J_CRPS/J_COMBINED choose a weight only from the latest42 causally reconstructed parent forecasts whose outcomes ended strictly before the current cutoff. Weights are bounded.1–.9 and penalized toward.5 (Brier penalty.05,CRPS.002; joint CRPS/.015+Brier/.25+.25(w−.5)^2). A one-dimensional quadratic optimum is computed analytically; no evaluation-date weight grid is selected. Forty-two overlapping training outcomes do not represent42 independent weeks/months.

J_SIGN estimates a logisticC=.1 sign classifier on the native family and learns a beta bounded0–.75 from resolved prior forecast Brier with.05 shrinkage. It reallocates mass between actual positive/nonpositive return atoms; it does not graft a classifier probability onto an unrelated return forecast. Every final p(up), mean, median, quantile, seven return buckets and endpoint-tail probability comes from the same final weighted atoms. The other laws also clip simulated endpoint returns above the−100% bound; this numerical constraint is not tail validation.

The historical parent forecasts are causally reconstructed now, not actually timestamp-issued in2025. The phrase “honestly issued” in an initial registry means chronological out-of-training prediction only; `operational-amendments.json` and this report clarify that distinction. There is no independently sealed prequential experiment on these dates.

| horizon | fold | model | I03_weight | sign_beta | latest_training_endpoint |
| --- | --- | --- | --- | --- | --- |
| 5 | 2026-07 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 5 | 2026-07 | J_BRIER | 0.385755 | 0.000000 | 2026-06-29 |
| 5 | 2026-07 | J_CRPS | 0.180077 | 0.000000 | 2026-06-29 |
| 5 | 2026-07 | J_COMBINED | 0.234117 | 0.000000 | 2026-06-29 |
| 5 | 2026-07 | J_SIGN | 0.500000 | 0.000000 | 2026-06-29 |
| 5 | 2026-08 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 5 | 2026-08 | J_BRIER | 0.476694 | 0.000000 | 2026-07-30 |
| 5 | 2026-08 | J_CRPS | 0.333534 | 0.000000 | 2026-07-30 |
| 5 | 2026-08 | J_COMBINED | 0.390560 | 0.000000 | 2026-07-30 |
| 5 | 2026-08 | J_SIGN | 0.500000 | 0.106654 | 2026-07-30 |
| 5 | 2026-09 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 5 | 2026-09 | J_BRIER | 0.631396 | 0.000000 | 2026-08-28 |
| 5 | 2026-09 | J_CRPS | 0.515324 | 0.000000 | 2026-08-28 |
| 5 | 2026-09 | J_COMBINED | 0.608221 | 0.000000 | 2026-08-28 |
| 5 | 2026-09 | J_SIGN | 0.500000 | 0.053385 | 2026-08-28 |
| 5 | 2026-10 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 5 | 2026-10 | J_BRIER | 0.821212 | 0.000000 | 2026-09-29 |
| 5 | 2026-10 | J_CRPS | 0.636933 | 0.000000 | 2026-09-29 |
| 5 | 2026-10 | J_COMBINED | 0.819442 | 0.000000 | 2026-09-29 |
| 5 | 2026-10 | J_SIGN | 0.500000 | 0.000000 | 2026-09-29 |
| 5 | 2026-11 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 5 | 2026-11 | J_BRIER | 0.692602 | 0.000000 | 2026-10-29 |
| 5 | 2026-11 | J_CRPS | 0.534388 | 0.000000 | 2026-10-29 |
| 5 | 2026-11 | J_COMBINED | 0.668122 | 0.000000 | 2026-10-29 |
| 5 | 2026-11 | J_SIGN | 0.500000 | 0.000000 | 2026-10-29 |
| 21 | 2026-07 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 21 | 2026-07 | J_BRIER | 0.481681 | 0.000000 | 2026-06-29 |
| 21 | 2026-07 | J_CRPS | 0.100000 | 0.000000 | 2026-06-29 |
| 21 | 2026-07 | J_COMBINED | 0.171438 | 0.000000 | 2026-06-29 |
| 21 | 2026-07 | J_SIGN | 0.500000 | 0.000000 | 2026-06-29 |
| 21 | 2026-08 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 21 | 2026-08 | J_BRIER | 0.566789 | 0.000000 | 2026-07-30 |
| 21 | 2026-08 | J_CRPS | 0.568583 | 0.000000 | 2026-07-30 |
| 21 | 2026-08 | J_COMBINED | 0.585614 | 0.000000 | 2026-07-30 |
| 21 | 2026-08 | J_SIGN | 0.500000 | 0.291267 | 2026-07-30 |
| 21 | 2026-09 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 21 | 2026-09 | J_BRIER | 0.703981 | 0.000000 | 2026-08-28 |
| 21 | 2026-09 | J_CRPS | 0.549778 | 0.000000 | 2026-08-28 |
| 21 | 2026-09 | J_COMBINED | 0.657689 | 0.000000 | 2026-08-28 |
| 21 | 2026-09 | J_SIGN | 0.500000 | 0.460190 | 2026-08-28 |
| 21 | 2026-10 | J_EQUAL | 0.500000 | 0.000000 | unavailable |
| 21 | 2026-10 | J_BRIER | 0.455339 | 0.000000 | 2026-09-29 |
| 21 | 2026-10 | J_CRPS | 0.100000 | 0.000000 | 2026-09-29 |
| 21 | 2026-10 | J_COMBINED | 0.225901 | 0.000000 | 2026-09-29 |
| 21 | 2026-10 | J_SIGN | 0.500000 | 0.000000 | 2026-09-29 |


## Calibration, asymmetry and uncertainty

The equal mixture obtains weekly Brier.188184 and CRPS.010013, and is a useful restraint benchmark: learned weights do not automatically improve on it, I03 probability quality or L01 CRPS. Tails remain lightly sampled; direct-quantile laws clamp the.10/.90 interpolation tails, and no conditional extreme-tail validation is claimed. `metrics.json` contains probability-bin observed versus predicted frequencies, expected calibration error, seven-bucket calibration, pinball losses, interval coverage/width and magnitude errors. These descriptive bins are not independent calibration tests, especially after subgroup/search exposure.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| L01 | 76 | 0.447368 | 0.518280 | 0.313912 | 0.837404 | 0.029553 | 0.036865 | 0.046465 | 0.328947 | 0.486842 | 0.073482 |
| J_EQUAL | 76 | 0.460526 | 0.529391 | 0.276319 | 0.751998 | 0.029066 | 0.036976 | 0.046859 | 0.315789 | 0.526316 | 0.078074 |
| J_BRIER | 76 | 0.552632 | 0.607168 | 0.265658 | 0.728822 | 0.028565 | 0.036434 | 0.046463 | 0.328947 | 0.539474 | 0.078193 |
| J_CRPS | 76 | 0.513158 | 0.573835 | 0.281191 | 0.761576 | 0.028605 | 0.036238 | 0.046103 | 0.342105 | 0.526316 | 0.075610 |
| J_COMBINED | 76 | 0.539474 | 0.596057 | 0.273841 | 0.745867 | 0.028443 | 0.036049 | 0.046082 | 0.355263 | 0.539474 | 0.075900 |
| J_SIGN | 76 | 0.539474 | 0.596057 | 0.284887 | 0.775611 | 0.030452 | 0.039773 | 0.049093 | 0.289474 | 0.500000 | 0.075941 |
| A_STUDENT | 76 | 0.513158 | 0.588889 | 0.279302 | 0.758737 | 0.026064 | 0.035402 | 0.043329 | 0.328947 | 0.552632 | 0.082517 |


Monthly comparisons have only four disjoint windows. Full coherence is necessary to interpret probabilities and intervals, but it does not guarantee predictive accuracy or calibration. The chosen exploratory weekly distribution candidate W2_NOAUTO_VOLUME improves point CRPS while its80% interval covers77.17%; the strongest directional candidate has different probability/interval behavior. Retain separate candidates and avoid claiming one integrated system solves every objective.

| model | baseline | metric | n | mean_improvement | simultaneous95 |
| --- | --- | --- | --- | --- | --- |
| J_BRIER | I03_nosize | brier | 92 | -0.006170 | [-0.022905329269465393, 0.010565795836979874] |
| J_BRIER | L01 | crps | 92 | -0.000152 | [-0.0011724117667076912, 0.0008692921216276894] |
| J_COMBINED | I03_nosize | brier | 92 | -0.007482 | [-0.027165281376903515, 0.012201268026218286] |
| J_COMBINED | L01 | crps | 92 | -0.000161 | [-0.0011436118726603187, 0.0008209879027070467] |
| J_CRPS | I03_nosize | brier | 92 | -0.008505 | [-0.030829503024736027, 0.013820299671271718] |
| J_CRPS | L01 | crps | 92 | -0.000110 | [-0.0008745816440011813, 0.0006549236277046146] |
| J_EQUAL | I03_nosize | brier | 92 | -0.006138 | [-0.02375207602061854, 0.011476394310736514] |
| J_EQUAL | L01 | crps | 92 | -0.000050 | [-0.0007720032767250316, 0.0006712842915570789] |
| J_SIGN | I03_nosize | brier | 92 | -0.001820 | [-0.006489930216719069, 0.002849219379062027] |
| J_SIGN | L01 | crps | 92 | -0.000256 | [-0.001712360272143115, 0.0012002433750354013] |
| W2_NOAUTO_VOLUME | I03_nosize | brier | 92 | 0.003245 | [-0.023123454077230363, 0.029612987088502504] |
| W2_NOAUTO_VOLUME | L01 | crps | 92 | 0.000207 | [-0.0009254942438870747, 0.0013394645825983394] |


The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.

## Complete recovered endpoint outputs

`distribution-audit.json` records recovery of all 11,164 primary endpoint laws from frozen models/caches, with zero discrepancy in probability, mean, median, Brier and CRPS. `full-endpoint-predictions.csv` contains all seven quantiles, seven bucket probabilities, expected absolute return, endpoint standard deviation and endpoint downside probabilities. `retained-distributions.jsonl` preserves all276 weekly laws for the three retained candidate systems; these are reconstructed historical laws, not forward issuances. `retained-candidate-feature-weights.csv` contains845 actual per-refit coefficients, training imputation/centering/scaling values and defensive-group scaling factors. Return-regression coefficients are not additive probability weights or causal explanatory shares. Endpoint-path risks remain unavailable.
