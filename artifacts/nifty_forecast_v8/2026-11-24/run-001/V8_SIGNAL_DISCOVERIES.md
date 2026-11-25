# NIFTY V8 · Signal Discoveries

Run `2026-11-24/run-001`. Retrospective research.

1. Exact duplicate removal gives provable prediction stability under the tested alias designs. This is a representation result with synthetic interventions, independent of any new forecasting score target. Generic reweighting alone can change forecasts even when all aliases enter the same broad feature family.
2. Bank-versus-financial-services momentum change explains more of the V7 directional gain than the defensive change in the simple matched test. Residualizing the spreads gives the best unperturbed weekly probability point score. Weak early-cohort generalization and stronger current-than-lagged residual performance are both part of the evidence.
3. Market-state changes improve CRPS over the otherwise identical state levels. The level-only model improves both historical prior lead scores marginally. Cluster-balanced Elastic Net with rotation also gives a valuable distribution tradeoff. The earlier-cutoff CRPS leader is a follow-up sensitivity rather than a standalone new independent discovery.
4. Native panel residuals add a modest direction increment. ETF activity contributes a small distribution increment with weaker Brier. Complete-session intraday and tighter close reconciliation fail to establish incremental weekly scores. Targeted foreign intermediates mostly worsen, including authenticated Nasdaq and yield paths.
5. Smoothed weekly forecast states improve some monthly historical metrics, but placebo alignment and strict common readiness weaken the timing explanation. The results support persistence as a plausible alternative mechanism, with too few disjoint monthly targets to conclude.

| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| A_ETF_ACTIVITY | B_ROT | brier | 92 | -0.002914 |
| A_ETF_ACTIVITY | B_ROT | crps | 92 | 0.000061 |
| A_INTRADAY | A_INTRADAY_BASE | brier | 91 | -0.005131 |
| A_INTRADAY | A_INTRADAY_BASE | crps | 91 | -0.000063 |
| A_NATIVE_PANEL | B_ROT | brier | 92 | 0.002208 |
| A_NATIVE_PANEL | B_ROT | crps | 92 | 0.000005 |
| A_STRUCTURE_CHANGE | A_STRUCTURE_LEVEL | brier | 92 | -0.001119 |
| A_STRUCTURE_CHANGE | A_STRUCTURE_LEVEL | crps | 92 | 0.000115 |
| A_STRUCTURE_LEVEL | B_ROT | brier | 92 | 0.000538 |
| A_STRUCTURE_LEVEL | B_ROT | crps | 92 | 0.000309 |
| G_MEDIATE5 | G_MATCH5 | brier | 92 | 0.004487 |
| G_MEDIATE5 | G_MATCH5 | crps | 92 | -0.000091 |
| G_ROT_ELASTIC | G_ROT_CLUSTER | brier | 92 | 0.002974 |
| G_ROT_ELASTIC | G_ROT_CLUSTER | crps | 92 | 0.000415 |
| R_BANK | B_NATIVE | brier | 92 | 0.008170 |
| R_BANK | B_NATIVE | crps | 92 | 0.000150 |
| R_DEF | B_NATIVE | brier | 92 | -0.000670 |
| R_DEF | B_NATIVE | crps | 92 | 0.000020 |
| R_RESIDUAL | B_ROT | brier | 92 | 0.002790 |
| R_RESIDUAL | B_ROT | crps | 92 | 0.000045 |


The ranking above describes the strength and interpretation of controlled incremental comparisons. Whole-system Brier and CRPS ranks are separate.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
