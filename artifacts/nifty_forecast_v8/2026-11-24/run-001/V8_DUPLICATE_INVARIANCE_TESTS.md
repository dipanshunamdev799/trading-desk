# NIFTY V8 · Duplicate Invariance Tests

Run `2026-11-24/run-001`. Retrospective research.

The initial suite varies order, positive affine units, equivalent affine formula, one exact copy, three exact copies, and an affine duplicate with altered units. The compensating Ridge test divides the original and three replicas by 2. We compare complete probability, mean, return atoms and atom weights over the same five folds. The canonical rule finds matches using **unclipped** standardized training histories with identical missingness masks at tolerance 1e-11. Canonical order is stable by name. The prediction tolerance is 1e-10. Positive affine transforms are the tested equivalence class. Similar correlations, nonlinear transforms and future values that merely happened to match during training require separate assessment.

The secondary suite names the synthetic copies as native sector columns so they enter clustering itself. This addresses the initial generic synthetic name test, where uncanonicalized copies could sit outside the sector cluster parser. The combined suites pass **125 required** complete-law checks, with maximum error **6.47e-16**. The original unbalanced replicated Elastic Net controls emitted some optimizer convergence warnings. They remain sensitivity examples and the required canonical checks passed. Additional copy stress on rotation and structure winners recovers identical results for canonical fits using the three larger input designs.

| model | variant | folds | passes | max_law_error | max_probability_change | aliases |
| --- | --- | --- | --- | --- | --- | --- |
| IS_canonical_cluster_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| IS_canonical_cluster_one_copy | one_copy | 5 | 5 | 0.000000 | 0.000000 | 6 |
| IS_canonical_cluster_three_copies | three_copies | 5 | 5 | 0.000000 | 0.000000 | 18 |
| IS_cluster_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| IS_cluster_one_copy | one_copy | 5 | 5 | 0.000000 | 0.000000 | 0 |
| IS_cluster_three_copies | three_copies | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_cluster_affine_copy | affine_copy | 5 | 5 | 0.000000 | 0.000000 | 6 |
| I_canonical_cluster_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_cluster_equivalent_formula | equivalent_formula | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_cluster_equivalent_units | equivalent_units | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_cluster_one_copy | one_copy | 5 | 5 | 0.000000 | 0.000000 | 6 |
| I_canonical_cluster_reordered | reordered | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_cluster_three_copies | three_copies | 5 | 5 | 0.000000 | 0.000000 | 18 |
| I_canonical_elastic_affine_copy | affine_copy | 5 | 5 | 0.000000 | 0.000000 | 6 |
| I_canonical_elastic_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_elastic_equivalent_formula | equivalent_formula | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_elastic_equivalent_units | equivalent_units | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_elastic_one_copy | one_copy | 5 | 5 | 0.000000 | 0.000000 | 6 |
| I_canonical_elastic_reordered | reordered | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_elastic_three_copies | three_copies | 5 | 5 | 0.000000 | 0.000000 | 18 |
| I_canonical_ridge_affine_copy | affine_copy | 5 | 5 | 0.000000 | 0.000000 | 6 |
| I_canonical_ridge_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_ridge_equivalent_formula | equivalent_formula | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_ridge_equivalent_units | equivalent_units | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_ridge_one_copy | one_copy | 5 | 5 | 0.000000 | 0.000000 | 6 |
| I_canonical_ridge_reordered | reordered | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_canonical_ridge_three_copies | three_copies | 5 | 5 | 0.000000 | 0.000000 | 18 |
| I_cluster_affine_copy | affine_copy | 5 | 0 | 0.123810 | 0.123810 | 0 |
| I_cluster_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_cluster_equivalent_formula | equivalent_formula | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_cluster_equivalent_units | equivalent_units | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_cluster_one_copy | one_copy | 5 | 0 | 0.123810 | 0.123810 | 0 |
| I_cluster_reordered | reordered | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_cluster_three_copies | three_copies | 5 | 0 | 0.216667 | 0.216667 | 0 |
| I_elastic_affine_copy | affine_copy | 5 | 0 | 0.015476 | 0.015476 | 0 |
| I_elastic_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_elastic_equivalent_formula | equivalent_formula | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_elastic_equivalent_units | equivalent_units | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_elastic_one_copy | one_copy | 5 | 0 | 0.015476 | 0.015476 | 0 |
| I_elastic_reordered | reordered | 5 | 0 | 0.014087 | 0.000000 | 0 |
| I_elastic_three_copies | three_copies | 5 | 0 | 0.015476 | 0.015476 | 0 |
| I_ridge_affine_copy | affine_copy | 5 | 0 | 0.077381 | 0.077381 | 0 |
| I_ridge_as_is | as_is | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_ridge_balanced_three | balanced_three | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_ridge_equivalent_formula | equivalent_formula | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_ridge_equivalent_units | equivalent_units | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_ridge_one_copy | one_copy | 5 | 0 | 0.077381 | 0.077381 | 0 |
| I_ridge_reordered | reordered | 5 | 5 | 0.000000 | 0.000000 | 0 |
| I_ridge_three_copies | three_copies | 5 | 0 | 0.123810 | 0.123810 | 0 |


`invariance-effects.csv` and `sector-alias-effects.csv` keep the fold-level numerical errors. An exact duplicate identified in training is treated as equivalent by design. Misidentification risk if two feeds split apart outside training is a provenance issue rather than tested invariance to that changed economic signal.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
