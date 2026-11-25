# NIFTY V6 — Validation And Leakage Audit

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Frozen scope and chronology

The run began on19November2026 and its reports were finalized at the actual timestamp above; run-directory date is a version identity, not a claim that later validation/report generation happened on19November. Inputs are frozen to the inherited17November historical cutoff. No20November observations or pre2025 warmup are added. There are403 aligned feature origins, with raw native history starting1January2025; the first aligned origin is2April2025. Fully resolved outer samples contain92 weekly/76 monthly origins. A separate V5 official18November snapshot is a prior artifact, not a V6 evaluation extension.

Training endpoints must be strictly earlier than each model cutoff. Monthly outer refits retain their original first-origin/anchor schedule, which often lies on the preceding month's final trading day. The last42 mature observations form the validation residual segment; earlier fitting labels ending on/after its first origin are purged. The endpoint<cutoff condition supplies a full target-maturity gap; no additional arbitrary future-data embargo is asserted. Every inner/full preprocessing object is fitted separately on its allowed training rows. Simple experts, defensive PCA, median thresholds and sparse intermediates follow the same causal partitions.

Historical source-time reconstruction inherits V5's domestic after-close/next-morning convention and foreign timezone/DST/conservative-delay rules. No actual2025 receipt log exists. Causal feature transforms and availability guard tests do not make archived data point-in-time immutable. Source identities, monthly feature missingness and publication uncertainty remain material leakage risks.

## Reproduction, source reconstruction and guards

81 named V5/V4 model-fold vectors reproduced, plus two independent V5 parent refits;336 V6 parent outer forecasts have zero probability discrepancy. All964 cached parent laws retain full atoms/weights and are chronologically reconstructed, not historically issued. Matrix hashes, model hashes, feature-schema allowlists, future-availability/oracle-alias guards, matured-target guards, endpoint-alignment checks, weighted CRPS brute-force checks, ordered quantile checks and future-source perturbation invariance are exercised by `verify.py`. A schema allowlist does not prove arbitrary values within an allowed column are legitimate; source reconstruction and provenance supply complementary checks.

Full candidate replay status at report generation: True. The replay refits fitted candidate batches in a fresh V6 directory against frozen parent/mediator input artifacts, then compares per-origin probabilities, means, CRPS and other recorded fields at1e-10. It does not reacquire the provider histories or independently regenerate every frozen parent/mediator input. Their separate refits/provenance checks are explicitly documented. `replay-verification.json` gives exact row counts/differences. Numerical verification status at report generation: True; final invocation requires both replay and all13 reports.

The precise original source versions are retained in `source-at-forensic-batch/` (6 matching files) and `source-at-model-batch/` (9 matching files), with archive hashes matching the original registries. Later guards and defensive PC/normalization branches do not silently replace that historical code record. `operational-amendments.json` records their chronology. No frozen past registry is rewritten to imply an earlier preregistration.

## Search accounting and uncertainty

There are74 distinct candidate system IDs,135 primary system/horizon cells (65weekly/70monthly),11164 primary prediction rows and 592 primary/diagnostic fitted-batch ledger entries. Auxiliary mediation has200 fit records; parent reconstruction50; mixture-weight learning45. These counts exclude many prior V1–V5 searches and some inner/control fits, so they are lower bounds on total scientific search exposure. Initial33 forensic configurations were followed by a registered model batch and explicitly later outcome-informed monthly/weekly follow-ups. “Registered before fitting a batch” does not mean unseen history or independent confirmation.

Every primary candidate is compared on matched dates against eight controls: I03,I00,L01,V4D02,V4D03,V4M05,neutral and historical. Three loss contrasts (Brier,CRPS,return MAE) give3240 comparisons:1560weekly and1680monthly. Weekly uncertainty uses shared chronological10-origin moving blocks,2000 replicates and a max-standardized simultaneous critical value across all1560 candidate/score/control contrasts. Structural missing cohorts are retained on the common calendar. These are approximate dependence/search-aware exposed-history intervals, not a correction for the entire adaptive V1–V6 research program or future distribution shifts. The CI family itself does not include every confidence slice, permutation or feature test. No claim of global familywise protection is made.

Monthly intervals are withheld:76<8×21=168. The descriptive return-ACF effective-N estimates are 12.363 weekly and 4.699 monthly for these exact cohorts; they are estimators with their own uncertainty, not literal counts of independent events. Disjoint-window counts are19/four. Reported phase/leave-month/origin-removal checks show sensitivity but are not additional independent replications.

## Negative controls, revisions and preserved failures

Weekly target rolls are materially worse. Several monthly block controls remain attractive; the weekly-state mechanism therefore remains unpassed. Grouped query-month permutations are diagnostic and noncausal by construction; they cannot be forecast candidates. Actual overlapping domestic archived closes show zero changes between inspected source vintages; synthetic1bp perturbation is labeled separately. One-/two-session lag tests diagnose source/origin fragility; no historical receipt certainty is invented.

| horizon | fold | model | status | reason |
| --- | --- | --- | --- | --- |
| 5 | 2026-07 | F_OMIT_SIDEWAYS | failed | ValueError:Too few observations after registered regime exclusion |
| 21 | 2026-07 | F_OMIT_SIDEWAYS | failed | ValueError:Too few observations after registered regime exclusion |
| 21 | 2026-08 | F_OMIT_SIDEWAYS | failed | ValueError:Too few observations after registered regime exclusion |
| 21 | 2026-07 | G_MATCHED | failed | ValueError:Insufficient honest intermediate-state history |
| 21 | 2026-07 | G_DIRECT | failed | ValueError:Insufficient honest intermediate-state history |
| 21 | 2026-07 | G_MEDIATED | failed | ValueError:Insufficient honest intermediate-state history |


Three regime-excluded andthree global-monthly fits are non-estimable; no min-sample threshold is relaxed to fill them. The July M2_HUBER_WINDOW convergence warning is documented in `numerical-warning-audit.json`; the candidate is not promoted. All failed/weak experiments, including slope-only monthly, nonlinear weekly, size residualization and competitive nulls, remain reviewable.

## Preservation and forward handling

`prior-preservation.json` freezes6040 V1–V5 files, plus the exact prior report/source inventory; `verify.py` rehashes every protected file. The V4 prospective ledger is untouched and remains separate. No broker order, deployment, UI change or automation was created. The official19November index/cash/FO source probe failed for allthree requests at16:19IST on19November (`forward-source-probe.json`); we therefore did not backdate a forward snapshot or substitute stale source inputs for a current prediction. No V6 forward snapshot was issued. Acquiring a complete source set and freezing a new actual timestamp are prerequisites to any future research-only snapshot.

The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

## Complete recovered endpoint outputs

`distribution-audit.json` records recovery of all 11,164 primary endpoint laws from frozen models/caches, with zero discrepancy in probability, mean, median, Brier and CRPS. `full-endpoint-predictions.csv` contains all seven quantiles, seven bucket probabilities, expected absolute return, endpoint standard deviation and endpoint downside probabilities. `retained-distributions.jsonl` preserves all276 weekly laws for the three retained candidate systems; these are reconstructed historical laws, not forward issuances. `retained-candidate-feature-weights.csv` contains845 actual per-refit coefficients, training imputation/centering/scaling values and defensive-group scaling factors. Return-regression coefficients are not additive probability weights or causal explanatory shares. Endpoint-path risks remain unavailable.
