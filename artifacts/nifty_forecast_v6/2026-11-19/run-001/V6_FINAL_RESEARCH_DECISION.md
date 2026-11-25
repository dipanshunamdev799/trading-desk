# NIFTY V6 — Final Research Decision

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Decision

We found improved **exploratory weekly candidates** and a clearer mechanism hypothesis, but no independently validated NIFTY forecasting edge. The strongest probability point score is F_NO_DEFENSIVE Brier.169802948, down0.012243573 (6.73%) fromI03.182046521, with72/92=78.26% accuracy. Group-normalized W2_DEF_NORM is nearly equal at.169862492 and78.26% accuracy while retaining the57 native inputs. The strongest distribution point score is W2_NOAUTO_VOLUME CRPS.009755832, down0.000206985 (2.08%) fromL01.009962817; Brier.178801754,accuracy69/92=75%,80% intervalcoverage71/92=77.17%.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| L01 | 92 | 0.663043 | 0.653362 | 0.197610 | 0.582153 | 0.009963 | 0.013409 | 0.019166 | 0.543478 | 0.771739 | 0.036633 |
| F_NO_DEFENSIVE | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| W2_DEF_NORM | 92 | 0.782609 | 0.791001 | 0.169862 | 0.522778 | 0.010095 | 0.013198 | 0.019755 | 0.521739 | 0.782609 | 0.038263 |
| W2_DEF_PC | 92 | 0.782609 | 0.791001 | 0.170208 | 0.523784 | 0.010306 | 0.013416 | 0.020118 | 0.510870 | 0.793478 | 0.039198 |
| W2_NOAUTO_VOLUME | 92 | 0.750000 | 0.755926 | 0.178802 | 0.541915 | 0.009756 | 0.013051 | 0.018979 | 0.532609 | 0.771739 | 0.037657 |
| W2_NODEF_VOLUME | 92 | 0.760870 | 0.765360 | 0.175312 | 0.533128 | 0.009873 | 0.013138 | 0.018992 | 0.521739 | 0.782609 | 0.038203 |


## Retained candidate set and reason

Retain fixed I03 and L01 as untouched references. Retain W2_DEF_NORM as the representation/penalty hypothesis candidate, F_NO_DEFENSIVE as its deletion comparator, and W2_NOAUTO_VOLUME as the distribution/activity candidate. Do not merge these into a claimed universal winner. W2_DEF_NORM divides six standardized defensive inputs bysqrt(6) before fixedRidge100; W2_NOAUTO_VOLUME removes auto21 relative strength and addsfive genuine ETF activity ratios. Every candidate outputs a coherent endpoint distribution.

The mechanism finding is narrower than “sector X predicts NIFTY.” Correlated native inputs alter effective Ridge regularization. Removing columns, changing group weight or compressing them can improve retrospective losses without adding information. Size removal's gain arises mainly from dropping columns, not recomputing breadth aggregates. Smallcap500's late-start missingness matters, and excluding only small caps hurts. Native sector rotation, conditional reversion and price risk appear in the coefficients, but their causal transmission is not identified.

## Uncertainty prevents an edge claim

| model | baseline | metric | n | mean_improvement | simultaneous95 |
| --- | --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | I03_nosize | brier | 92 | 0.012244 | [-0.03628352133406396, 0.06077066764186246] |
| F_NO_DEFENSIVE | L01 | crps | 92 | -0.000105 | [-0.0023467642852621263, 0.002137010447939685] |
| W2_DEF_NORM | I03_nosize | brier | 92 | 0.012184 | [-0.016753008369891072, 0.04112106597940832] |
| W2_DEF_NORM | L01 | crps | 92 | -0.000132 | [-0.002182881043229771, 0.0019182971675615042] |
| W2_NOAUTO_VOLUME | I03_nosize | brier | 92 | 0.003245 | [-0.023123454077230363, 0.029612987088502504] |
| W2_NOAUTO_VOLUME | L01 | crps | 92 | 0.000207 | [-0.0009254942438870747, 0.0013394645825983394] |


All relevant weekly search-adjusted improvement ranges include zero. These approximate simultaneous intervals cover the within-V6 family, not the whole adaptiveV1–V6 history. The92 weekly origins overlap into19 disjoint windows. Native/ETF data is reconstructed from archived provider histories rather than authenticated historical receipt logs. A full replay can establish numerical reproducibility; it cannot make the exposed history independent.

## Monthly decision — four disjoint windows

M_WEEKSTATE's81.58% accuracy/Brier.178345/CRPS.024823 and one-extra-lag Brier.175091/CRPS.024530 look strong, but80% intervalcoverage is65.79%/60.53%. A21-session shuffled-state diagnostic obtainsbetterBrier.160615, and afive-session shiftbetterCRPS.022269. Exact dated state information is therefore not established as the driver. Keep those leads INCONCLUSIVE; no monthly winner is forced, no narrow interval is manufactured, and no prospective operational model is selected from four windows. RegularizedStudent/risk-panel alternatives remain comparisons, not validated solutions.

Global mediation, larger evolving feature libraries, nonlinear architectures and learned mixtures did not deliver a dependable improvement over the strongest matched prior controls. Preserve their negative results. Ten-/15-session experiments are additional diagnostics, not new primary horizons selected after seeing attractive outcomes.

## Delivery and next action boundary

All13 requested reports, frozen feature/configuration files, per-origin outputs, fitted model artifacts, exact source archives, failed-fit reasons, null results, matched comparisons and reproducible scripts are included. V1–V5 and the V4 prospective ledger are unchanged. No live trade, deployment or automation was performed. No new V6 forward snapshot was issued: allthree official19November source probes failed at acquisition, and this historical run does not silently substitute stale/current data. A future research-only snapshot must acquire a complete, timestamped source set and record its own version/hash/issuance time.

The useful discovery is a smaller, testable candidate set and an evidence-backed representation hypothesis. The unresolved question is whether those improvements survive genuinely new weekly observations with stable source availability. That question has not been answered by this exposed-history research.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.

[Standalone research figure](weekly-results.png)
