# NIFTY V6 — Model Architectures

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Controlled alternatives, not an algorithm count contest

The main batch has25 estimator configurations (23 weekly,25 monthly) andfive coherent integration laws per horizon. The complete study has74 distinct system IDs and135 primary system/horizon rows after33 forensic variants, monthly risk, six monthly attribution systems andfour weekly follow-ups. Auxiliary intermediate targets, two diagnostic horizons, permutations, block nulls and sensitivity fits are separately counted and retained; those135 rows understate the wider research-search exposure.

Most architecture comparisons use the same57 native fields and monthly refit origins. Ridge alpha100 is the reference. Elastic Net uses alpha.001,l1ratio.5,max5000. Huber uses alpha10,epsilon1.35,max1000. BayesianRidge supplies normal predictive atoms. Random forest uses64 trees,depth3,minleaf30,maxfeatures.7,seed20261119 and actual conditional training-leaf atoms. LightGBM uses80 rounds,depth2,4leaves,minleaf40,rate.04,L2=10,single-thread deterministic seed20261119, with five direct quantiles. Linear quantile regression uses alpha.005 at .10/.25/.50/.75/.90. The compact additive spline model uses three knots,degree2 and Ridge100. Student laws use df5, a residual/historical scale blend and65/35 empirical shrinkage. Volatility and trend experts mix a global Ridge with a matching expert mean at50/50 when each training group has at least40 observations; gates depend only on training/current observable conditions.

## Weekly

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| A_ELASTIC | 92 | 0.771739 | 0.781567 | 0.189880 | 0.566313 | 0.010092 | 0.013600 | 0.019292 | 0.489130 | 0.760870 | 0.040242 |
| A_HUBER | 92 | 0.543478 | 0.529269 | 0.292455 | 0.793220 | 0.016774 | 0.023307 | 0.027879 | 0.489130 | 0.728261 | 0.062323 |
| A_BAYES | 92 | 0.652174 | 0.694727 | 0.227388 | 0.644755 | 0.010241 | 0.014064 | 0.018422 | 0.456522 | 0.760870 | 0.041837 |
| A_FOREST | 92 | 0.608696 | 0.640058 | 0.238094 | 0.669056 | 0.011518 | 0.015972 | 0.021822 | 0.467391 | 0.739130 | 0.043279 |
| A_LGBM_QUANT | 92 | 0.576087 | 0.577891 | 0.236405 | 0.665564 | 0.011828 | 0.015859 | 0.021951 | 0.456522 | 0.630435 | 0.033467 |
| A_QUANTILE | 92 | 0.619565 | 0.642719 | 0.223349 | 0.639367 | 0.010418 | 0.013855 | 0.018464 | 0.434783 | 0.663043 | 0.035587 |
| A_GAM | 92 | 0.576087 | 0.500000 | 0.282571 | 0.763186 | 0.013045 | 0.017344 | 0.024481 | 0.445652 | 0.684783 | 0.039314 |
| A_STUDENT | 92 | 0.673913 | 0.713595 | 0.208509 | 0.604811 | 0.010031 | 0.013905 | 0.018749 | 0.521739 | 0.782609 | 0.042388 |
| R_VOL | 92 | 0.750000 | 0.759313 | 0.184349 | 0.554710 | 0.010366 | 0.013799 | 0.020319 | 0.521739 | 0.782609 | 0.038434 |
| R_TREND | 92 | 0.804348 | 0.799710 | 0.178155 | 0.542273 | 0.010306 | 0.013512 | 0.019695 | 0.532609 | 0.750000 | 0.038140 |


## Monthly — only four disjoint outcome windows

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| A_ELASTIC | 76 | 0.710526 | 0.715412 | 0.192872 | 0.573411 | 0.027391 | 0.036822 | 0.047175 | 0.447368 | 0.736842 | 0.090774 |
| A_HUBER | 76 | 0.750000 | 0.758781 | 0.189168 | 0.560586 | 0.027211 | 0.035578 | 0.048135 | 0.539474 | 0.736842 | 0.098386 |
| A_BAYES | 76 | 0.473684 | 0.550538 | 0.330971 | 0.893942 | 0.031521 | 0.040374 | 0.048555 | 0.250000 | 0.460526 | 0.068391 |
| A_FOREST | 76 | 0.407895 | 0.500000 | 0.293314 | 0.784205 | 0.027901 | 0.037518 | 0.046477 | 0.263158 | 0.526316 | 0.068177 |
| A_LGBM_QUANT | 76 | 0.394737 | 0.453763 | 0.286406 | 0.771634 | 0.028583 | 0.037162 | 0.046418 | 0.236842 | 0.407895 | 0.053249 |
| A_QUANTILE | 76 | 0.539474 | 0.606093 | 0.306317 | 0.848916 | 0.029783 | 0.036225 | 0.044609 | 0.184211 | 0.434211 | 0.050070 |
| A_GAM | 76 | 0.157895 | 0.168459 | 0.433547 | 1.123750 | 0.035069 | 0.044181 | 0.054728 | 0.184211 | 0.447368 | 0.066100 |
| A_STUDENT | 76 | 0.513158 | 0.588889 | 0.279302 | 0.758737 | 0.026064 | 0.035402 | 0.043329 | 0.328947 | 0.552632 | 0.082517 |
| R_VOL | 76 | 0.618421 | 0.642652 | 0.208701 | 0.607097 | 0.026982 | 0.033631 | 0.045620 | 0.381579 | 0.552632 | 0.068470 |
| R_TREND | 76 | 0.460526 | 0.534409 | 0.279055 | 0.757896 | 0.030191 | 0.039810 | 0.049460 | 0.289474 | 0.460526 | 0.081544 |


Quantile crossings are sorted before a201-point bounded interpolation; this creates an ordered endpoint law but is not simultaneous noncrossing estimation, and endpoint truncation makes extreme-tail claims unsupported. Forest laws pool actual training returns from matching leaves with35% historical mass. Bayesian/Student laws have401 deterministic atoms before shrinkage. These numerical representations make scores reproducible but do not validate tail shape or conditional calibration.

Huber and elastic monthly classification point scores can look better while their distribution/interval results remain weak. The later M2_HUBER_WINDOW monthly attribution variant obtains76.32% accuracy and Brier.186174 yet CRPS.047917, substantially worse than the proper-score leads. Its July Huber fitting reached the1000-iteration cap; that warning is retained in the replay log and final numerical-warning audit, and it is not promoted. The original main-batch captured warning lists are preserved in `model-ledger.json`.

## Deliberate scope limits and inference

We tested shallow boosting, forest, additive, sparse, robust, Bayesian, quantile, Student and simple experts. XGBoost/CatBoost and neural sequence/temporal-convolution searches were not added: they are optional examples in the mission, not evidence-generating necessities, and 92 overlapping weekly/four monthly windows cannot justify a large hyperparameter search. Lag sensitivity and observed-state evolution supply controlled temporal alternatives. No winner is inferred from testing more algorithms. All failed/non-estimable fits remain in `experiment-registry.json` with their actual reasons. The new best weekly leads arise from representation/regularization and actual ETF activity, rather than the nonlinear architecture alternatives.

| model | baseline | metric | n | mean_improvement | simultaneous95 |
| --- | --- | --- | --- | --- | --- |
| A_FOREST | I03_nosize | brier | 92 | -0.056047 | [-0.12256737482736133, 0.01047308323482607] |
| A_FOREST | L01 | crps | 92 | -0.001555 | [-0.003770002598393042, 0.0006592381285389953] |
| A_LGBM_QUANT | I03_nosize | brier | 92 | -0.054358 | [-0.09440913413412028, -0.014306829222573703] |
| A_LGBM_QUANT | L01 | crps | 92 | -0.001866 | [-0.004523053562452884, 0.00079203604700655] |
| A_STUDENT | I03_nosize | brier | 92 | -0.026463 | [-0.08658947107188303, 0.033664362821842195] |
| A_STUDENT | L01 | crps | 92 | -0.000068 | [-0.001998347359689269, 0.0018623211409092293] |
| R_VOL | I03_nosize | brier | 92 | -0.002302 | [-0.026679741183198293, 0.022075067187996348] |
| R_VOL | L01 | crps | 92 | -0.000403 | [-0.002553019228635335, 0.001747133226330837] |


The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.
