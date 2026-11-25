# NIFTY V9 · Final Research Conclusions

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

The V9 diagnosis favors **training support and careful fallback** as the useful discoveries. V8's later probability and distribution point records remain superior on their own later dates. V9's later identical-design residual rotation reaches **.164236 Brier** and market structure reaches **.009608 CRPS**. Attempts to adapt aggressively through Kalman, recency, regimes and meta-learning mostly fail. Giving forecasts more historical support and using a conservative blend reduces the difficulty of combining periods, without creating an independent predictive edge.

The identical-design **265-origin weekly** comparison gives cluster-balanced rotation **0.236386 Brier** versus **0.259048** historical, and the reliability/history blend **0.011014 CRPS** versus **0.011340** historical. On the earlier cohort, the two candidate losses are **0.260773 Brier** and **0.010899 CRPS**, both slightly worse than the historical scores **0.259447** and **0.010878**. Hence the combined gains partly reflect later strength, not earlier robustness. The fixed fallback is almost tied for pooled CRPS. The full uncertainty ranges, including the weaker earlier and later comparisons, are below.

| model | n | disjoint | brier | crps | early_Brier | late_Brier | early_CRPS | late_CRPS | abs_Brier_cohort_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_CLUSTER | 265 | 53 | 0.236386 | 0.011775 | 0.260773 | 0.190529 | 0.012473 | 0.010463 | 0.070243 |
| J9_PERFORMANCE | 265 | 53 | 0.241228 | 0.011151 | 0.270750 | 0.185713 | 0.011606 | 0.010297 | 0.085037 |
| J9_STATIC | 265 | 53 | 0.246239 | 0.011029 | 0.259548 | 0.221214 | 0.010933 | 0.011211 | 0.038333 |
| J9_REL_SHRINK | 265 | 53 | 0.248725 | 0.011014 | 0.261291 | 0.225095 | 0.010899 | 0.011230 | 0.036197 |
| P_STRUCTURE | 265 | 53 | 0.250845 | 0.012056 | 0.296317 | 0.165337 | 0.013358 | 0.009608 | 0.130980 |
| P_ROT | 265 | 53 | 0.252015 | 0.012108 | 0.298696 | 0.164236 | 0.013232 | 0.009995 | 0.134460 |
| P_HIST | 265 | 53 | 0.259048 | 0.011340 | 0.259447 | 0.258296 | 0.010878 | 0.012210 | 0.001152 |


| model | metric | n | gain | adjusted95_block10 |
| --- | --- | --- | --- | --- |
| P_CLUSTER | brier | 265 | 0.022661 | [-0.040440, 0.085762] |
| P_CLUSTER | crps | 265 | -0.000435 | [-0.003528, 0.002658] |
| J9_STATIC | brier | 265 | 0.012808 | [-0.011301, 0.036918] |
| J9_STATIC | crps | 265 | 0.000311 | [-0.000528, 0.001150] |
| J9_REL_SHRINK | brier | 265 | 0.010323 | [-0.011107, 0.031752] |
| J9_REL_SHRINK | crps | 265 | 0.000327 | [-0.000372, 0.001025] |
| P_STRUCTURE | brier | 265 | 0.008203 | [-0.062776, 0.079182] |
| P_STRUCTURE | crps | 265 | -0.000716 | [-0.003566, 0.002134] |
| P_ROT | brier | 265 | 0.007032 | [-0.064811, 0.078876] |
| P_ROT | crps | 265 | -0.000768 | [-0.003441, 0.001905] |


Keep historical fallback, V8 protected rotation/structure, cluster-balanced rotation and a simple complete-law blend as separate candidate hypotheses. For monthly retain empirical/reversion and protected V8 smoothing as controls. V9 robust paths and distributed lags did not yield a monthly model that merits promotion. The four acquired sessions resolve four old origins per target, which provide no meaningful new disjoint evaluation. The null search shows that a selected small gain over history can appear even after disrupting fit alignment. No forward V9 forecast, trading or deployment was performed.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
