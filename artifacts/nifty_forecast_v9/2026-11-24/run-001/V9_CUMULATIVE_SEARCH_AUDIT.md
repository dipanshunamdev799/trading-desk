# NIFTY V9 · Cumulative Search Audit

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

We recovered **44** earlier registry/manifest files, **466** parsed configuration entries and **672** protected model/horizon forecast vectors. There are **454** exact normalized JSON payload fingerprints, **437** restricted parameter signatures and **583** distinct stored prediction fingerprints at the hash precision. Those counts are an auditable lower-bound inventory. V1–V2 formats and some older workflow configurations are heterogeneous, and payload differences are not always substantive estimator differences. `historical-config-inventory.csv`, `historical-prediction-fingerprints.csv`, and the registry index identify the repeated and distinct records. Cross-system pairs of probability, residual error, Brier and CRPS correlation are available in `prediction-and-error-correlations.csv`.

The largest prior wins are not stable to material protocol changes. V8 raw rotation reproduces the same earlier deterioration; the V9 common fitting curve shows that the later advantage collapses when kept at the same 85-date window. V7 and V8 monthly state winners weaken or are equaled by certain alignment controls. Such changes are observed failures under design/cohort alterations. They are not independent consecutive prospective tests.

## Refit the search under block nulls

We reran eight actual competing V9 heads on all later weekly dates, including rotation, residual rotation, structure, compact native, financial panel, innovation, exponentially weighted Ridge and cluster-balanced Elastic Net. Twenty-four seeded block-permuted training/inner/validation target draws use blocks of 5, 10 and 15 observations. Each draw refits each model and reselects the best per-score improvement against the same genuine historical benchmark. The outer outcomes and their date order remain untouched. This tests a bounded search family rather than shuffling one already-selected winner.

The genuine eight-model search finds **0.094060** Brier and **0.002603** CRPS gains over the historical fallback on the later dates. Null maxima range **-0.050696 to 0.026161** for Brier and **-0.001788 to 0.000222** for CRPS. **10/24** draws appear to improve Brier, and **5/24** appear to improve CRPS. These distributions illustrate search risk without supplying a p-value covering eight prior research versions. The strongest prior forecasting systems are much tougher benchmarks than simple historical returns on the later dates.

| draw | block | best_brier_gain | best_crps_gain | brier_winner | crps_winner |
| --- | --- | --- | --- | --- | --- |
| -1 | 0 | 0.094060 | 0.002603 | residual | structure |
| 0 | 5 | -0.012941 | -0.000668 | fin_panel | ar_innovation |
| 1 | 10 | -0.020603 | -0.000652 | fin_panel | fin_panel |
| 2 | 15 | -0.007063 | -0.000787 | structure | weighted |
| 3 | 5 | -0.019770 | -0.000435 | fin_panel | weighted |
| 4 | 10 | 0.025434 | -0.000004 | fin_panel | fin_panel |
| 5 | 15 | 0.015387 | 0.000174 | structure | structure |
| 6 | 5 | -0.015326 | -0.000845 | structure | structure |
| 7 | 10 | -0.003594 | -0.000460 | balanced | fin_panel |
| 8 | 15 | -0.037563 | -0.001385 | fin_panel | fin_panel |
| 9 | 5 | 0.006574 | -0.000392 | structure | structure |
| 10 | 10 | -0.026334 | -0.001115 | fin_panel | fin_panel |
| 11 | 15 | -0.019583 | -0.000998 | weighted | weighted |
| 12 | 5 | 0.025501 | 0.000101 | fin_panel | fin_panel |
| 13 | 10 | -0.050696 | -0.001788 | compact | compact |
| 14 | 15 | 0.011646 | 0.000161 | structure | structure |
| 15 | 5 | 0.021297 | 0.000196 | fin_panel | fin_panel |
| 16 | 10 | -0.001313 | -0.000189 | fin_panel | fin_panel |
| 17 | 15 | -0.011707 | -0.000208 | weighted | weighted |
| 18 | 5 | -0.017003 | -0.000583 | fin_panel | weighted |
| 19 | 10 | 0.001279 | -0.000329 | compact | ar_innovation |
| 20 | 15 | -0.001631 | -0.000659 | balanced | balanced |
| 21 | 5 | 0.005967 | -0.000158 | raw | raw |
| 22 | 10 | 0.026161 | 0.000222 | structure | fin_panel |
| 23 | 15 | 0.000565 | -0.000251 | structure | weighted |


Within V9, shared moving origin-block bootstraps use 2,000 draws and 5/10/15-session length sensitivity. Earlier weekly family size is **2,487** and later weekly family size **5,739**. The combined full-coverage weekly family has **148** contrasts. Some draws lack dates for small eligible subsets; the algorithm ignores missing bootstrap estimates while retaining cohort-specific validity and reports the matched count. Monthly and refresh uncertainty is descriptive. Past fitting, maturity, duplicate invariance and all retained failures are independently checked in `verification.json`. No adjustment reconstructs all adaptive V1–V9 choices.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
