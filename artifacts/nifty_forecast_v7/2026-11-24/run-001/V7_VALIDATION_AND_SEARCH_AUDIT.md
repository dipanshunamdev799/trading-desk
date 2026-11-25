# NIFTY V7 · Validation And Search Audit

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

Historical decisions follow the original frozen evaluation calendar. Intraday grid, foreign completion times, source overlap revisions and feature truncation invariance are documented separately. Training requires the full target endpoint strictly before the fold cutoff. The last 42 mature training observations form an inner residual-validation window. Its fitting labels must end strictly before that window. Alternative cutoffs move both maturity boundaries three observed sessions earlier. Training-only scale, clustering, factor directions and estimation are refitted in each partition. Initial raw histories begin in 2025. The model cohort is fixed to the V6 historical origins and no newer labels are added.

Actual cross-vintage close revisions are in `source-audit.json` and the synthetic revisions exercise one-basis-point perturbations through feature reconstruction. Exact duplicate tests, joint query perturbation, financial/cyclical block removal, five-session placebo inputs, earlier cutoffs and shifted targets are recorded as falsification or sensitivity experiments. The weekly target displacement gives Brier .271782. Training dates were not chosen to exclude difficult outer outcomes. Historical sources lack authenticated original receipts and exact historical constituent composition. The current stock sample is separately marked as a research-only survivorship proxy.

V7 scored 143 primary candidate/horizon cells and 8 10/15-session cells. There are 12,605 saved prediction rows and 4,719 matched strong-control comparisons, of which 2,475 enter the weekly simultaneous bootstrap family. Two thousand circular block draws are shared across cells, with 5-, 10- and 15-session length sensitivity. The maximum standardized bootstrap deviation supplies the simultaneous critical value for the family at each length. Unadjusted 10-session block intervals are retained separately. Model selection from V1–V6 and interpretation of additional slices are outside the covered family. All forecasts remain research-exposed.

| block | critical_value |
| --- | --- |
| 5 | 3.725960 |
| 10 | 3.657648 |
| 15 | 3.507321 |


| model | baseline | metric | n | gain | adjusted95_block10 |
| --- | --- | --- | --- | --- | --- |
| C_ELASTIC | V6_BRIER | brier | 92 | -0.014804 | [-0.07759060726150645, 0.047982646927614434] |
| C_ELASTIC | V6_BRIER | crps | 92 | 0.000373 | [-0.0019226779503525877, 0.0026677950218058355] |
| C_ELASTIC | V6_CRPS | brier | 92 | -0.005805 | [-0.04292618376714074, 0.031315836729775066] |
| C_ELASTIC | V6_CRPS | crps | 92 | 0.000061 | [-0.0013021855237257253, 0.0014235784191452669] |
| L_DAILY | V6_BRIER | brier | 92 | 0.003079 | [-0.012488602425715593, 0.0186457017388708] |
| L_DAILY | V6_BRIER | crps | 92 | 0.000175 | [-0.00041725912226309506, 0.0007667165188672873] |
| L_DAILY | V6_CRPS | brier | 92 | 0.012077 | [-0.026998859533229693, 0.05115357214291125] |
| L_DAILY | V6_CRPS | crps | 92 | -0.000137 | [-0.001000818110328468, 0.0007265513308989543] |
| T_ELASTIC_EMBARGO | V6_BRIER | brier | 92 | -0.014331 | [-0.07465766607260821, 0.04599618411871554] |
| T_ELASTIC_EMBARGO | V6_BRIER | crps | 92 | 0.000402 | [-0.0025711607215019184, 0.0033755923705106623] |
| T_ELASTIC_EMBARGO | V6_CRPS | brier | 92 | -0.005332 | [-0.03612272176476268, 0.025458853107396356] |
| T_ELASTIC_EMBARGO | V6_CRPS | crps | 92 | 0.000090 | [-0.0019859773940986555, 0.0021666848670736927] |
| T_ROT_DOMESTIC | V6_BRIER | brier | 92 | 0.007658 | [-0.006941624860000021, 0.022257472817540522] |
| T_ROT_DOMESTIC | V6_BRIER | crps | 92 | 0.000141 | [-0.00028826412415899536, 0.0005701724353396215] |
| T_ROT_DOMESTIC | V6_CRPS | brier | 92 | 0.016657 | [-0.021007404552181873, 0.05432086580624873] |
| T_ROT_DOMESTIC | V6_CRPS | crps | 92 | -0.000171 | [-0.0011889794407813773, 0.0008471635759282974] |


The original global/integration attempt selected the V5 I03 origins, which contained outer rows only. Its 27 unestimable downstream fits and first outputs are archived. The corrected run uses the frozen V3 development and outer calendar. An intervening metadata join failure is recorded. The corrected current global batch retains three July monthly insufficiencies. Adaptive rotation/activity and Elastic Net follow-ups were motivated by the exposed initial results and included in the V7 search family. Numerical warning text, status, and SHA-256 model hashes are in `fit-ledger.csv`; no failures are filled with estimated scores.

| horizon | fold | model | status | reason |
| --- | --- | --- | --- | --- |
| 21 | 2026-07 | G_BASE21 | failed | ValueError: Fewer than 60 purged inner fit observations |
| 21 | 2026-07 | G_DIRECT21 | failed | ValueError: Fewer than 60 purged inner fit observations |
| 21 | 2026-07 | G_INTERMEDIATE21 | failed | ValueError: Fewer than 60 purged inner fit observations |


`prior-integrity-verification.json`, `verification.json` and `report-manifest.json` record repeat checks over the preserved artifacts, data alignment, selected candidate replay and reports. No V7 forward issuance, trade or deployment occurred. The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history.
