# NIFTY V6 — Global Incremental Research

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Narrow transmission hypotheses and availability

V6 does not rerun the indiscriminate global-plus-domestic block. It tests four intermediates first: US technology returns to Indian IT; Brent/USDINR/oil–FX to Indian energy; global mean/dispersion to bank-relative returns; and global volatility/dispersion to NIFTY return magnitude. Each intermediate has a domestic own-state Ridge100 control and an own-state-plus-sparse-global Ridge100 model. Intermediate forecasts are constructed chronologically; their incremental forecast correction enters G_MEDIATED. G_DIRECT uses seven sparse raw global fields. G_MATCHED uses the same compact domestic inputs and the same dates eligible for intermediate training. A weak-breadth/global-shock interaction is included in the mediated set.

The inherited `IXIX` feed is a provider US Tech100 proxy, not a verified Nasdaq Composite cash-index history. Accordingly, this is not a definitive Nasdaq→IT test. No FRED or US Treasury series is invented to fill previously failed acquisitions. Known foreign cash sessions retain exchange/IANA timezone/DST close plus two-hour availability; uncertain CFD/futures/FX daily conventions use a conservative two-UTC-day delay. We inherit the frozen provider/date audit rather than treating same-date foreign bars as already known in India. These conservative rules can sacrifice signal; original historical receipt timestamps are unavailable. An actual market-specific release-time study therefore remains constrained by source provenance, even where the transformation is causal.

## Intermediate out-of-sample reconstruction results

| horizon | target | n | base_mae | global_mae | mae_improvement | base_rmse | global_rmse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | BANKREL | 92 | 0.008826 | 0.008850 | -0.000024 | 0.011464 | 0.011674 |
| 5 | ENERGY | 92 | 0.014920 | 0.014645 | 0.000275 | 0.019696 | 0.019157 |
| 5 | IT | 92 | 0.030192 | 0.030020 | 0.000172 | 0.041299 | 0.041204 |
| 5 | MAGNITUDE | 92 | 0.010468 | 0.010721 | -0.000253 | 0.016232 | 0.016424 |
| 21 | BANKREL | 76 | 0.012800 | 0.012963 | -0.000163 | 0.016360 | 0.016697 |
| 21 | ENERGY | 76 | 0.035269 | 0.035745 | -0.000476 | 0.040810 | 0.040986 |
| 21 | IT | 76 | 0.090119 | 0.090587 | -0.000468 | 0.105544 | 0.106863 |
| 21 | MAGNITUDE | 76 | 0.024048 | 0.024776 | -0.000728 | 0.033414 | 0.033582 |


Weekly IT MAE improves by .000171611 (about.57% of its base MAE); energy improves .000274846 (about1.84%). Bank-relative performance worsens .000024064 and magnitude worsens .000253193. All four monthly intermediate MAEs worsen. These tiny and inconsistent sector increments do not establish economic causation or dependable transmission to NIFTY.

## Direct versus mediated NIFTY results

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G_MATCHED | 92 | 0.456522 | 0.430092 | 0.276661 | 0.748638 | 0.012795 | 0.017077 | 0.023670 | 0.489130 | 0.728261 | 0.041221 |
| G_DIRECT | 92 | 0.445652 | 0.427431 | 0.267131 | 0.730576 | 0.012553 | 0.016427 | 0.022740 | 0.489130 | 0.728261 | 0.043497 |
| G_MEDIATED | 92 | 0.489130 | 0.465167 | 0.276818 | 0.749465 | 0.012899 | 0.017263 | 0.023771 | 0.467391 | 0.728261 | 0.044116 |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G_MATCHED | 53 | 0.037736 | 0.076923 | 0.537279 | 1.359104 | 0.050519 | 0.064945 | 0.070222 | 0.018868 | 0.169811 | 0.087358 |
| G_DIRECT | 53 | 0.037736 | 0.076923 | 0.540988 | 1.368063 | 0.050028 | 0.063377 | 0.070164 | 0.018868 | 0.169811 | 0.079907 |
| G_MEDIATED | 53 | 0.056604 | 0.115385 | 0.539370 | 1.370263 | 0.050899 | 0.065496 | 0.070440 | 0.018868 | 0.169811 | 0.089883 |
| I03_nosize | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| G_DIRECT | G_MATCHED | brier | 92 | 0.009530 |
| G_DIRECT | G_MATCHED | crps | 92 | 0.000242 |
| G_MEDIATED | G_MATCHED | brier | 92 | -0.000157 |
| G_MEDIATED | G_MATCHED | crps | 92 | -0.000104 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| G_DIRECT | G_MATCHED | brier | 53 | -0.003709 |
| G_DIRECT | G_MATCHED | crps | 53 | 0.000492 |
| G_MEDIATED | G_MATCHED | brier | 53 | -0.002090 |
| G_MEDIATED | G_MATCHED | crps | 53 | -0.000380 |


The first monthly fold of all three G systems is non-estimable: the honest intermediate forecasts do not supply enough past inner-fit history for the frozen60-observation requirement. Their monthly scores use53 origins, not76, and strong controls are reindexed to those exact53 origins for comparisons. No retrospective fitted sector outcomes are backfilled to manufacture availability. Earlier weekly intermediate training and later monthly folds remain estimated as recorded.

| model | baseline | metric | n | mean_improvement | simultaneous95 |
| --- | --- | --- | --- | --- | --- |
| G_DIRECT | I03_nosize | brier | 92 | -0.085085 | [-0.16936242299149695, -0.000806810785309045] |
| G_DIRECT | L01 | crps | 92 | -0.002590 | [-0.006524132033931922, 0.0013444601124587546] |
| G_MEDIATED | I03_nosize | brier | 92 | -0.094772 | [-0.18119570953943367, -0.008347433786018432] |
| G_MEDIATED | L01 | crps | 92 | -0.002936 | [-0.006931942995526086, 0.0010604357585014051] |


## Diagnosis and disposition

Domestic variables may already reflect much global information, but this remains a hypothesis rather than a proven explanation. The measured sector increments are small, source identities are imperfect, uncertain daily timestamps require conservative lags, and the two-year sample cannot support many regime-specific interactions. This batch provides no robust incremental NIFTY improvement from the narrowed global paths. Retain the IT/energy mediator hypotheses as exploratory and the negative magnitude/bank/monthly results as evidence against immediate expansion. A cleaner US cash-index timestamped history is more valuable than adding another broad global block. No global causal transmission is claimed.

The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.
