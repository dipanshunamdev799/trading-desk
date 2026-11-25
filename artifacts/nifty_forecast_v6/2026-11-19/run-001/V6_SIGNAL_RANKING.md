# NIFTY V6 — Signal Ranking

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Rank incremental information separately from fitted systems

This is an evidence ordering, not a causal feature ranking or a custom numerical score. Complete-system ranks by Brier/CRPS are in their own tables. Incremental gains below are measured against each immediate parent on the same dates; some effects trade off probability quality and distribution quality. The selected native family itself was discovered through V1–V5 exposed-history work.

1. **Correlated defensive-group representation/penalty** is the strongest mechanism lead. Deletion, train-only whitened1PC and division of standardized group fields bysqrt(6) all yield weekly Brier near.170 versus.182047. Similar outcomes under three representations support redundancy/penalty geometry, without proving economic irrelevance or a future effect. The group-normalized candidate keeps all57 inputs and has a smaller estimated change-uncertainty than pure deletion.
2. **Auto relative-strength removal plus actual ETF activity** is the best distribution point-score lead. W2_NOAUTO_VOLUME reachesCRPS.009755832 versusL01.009962817 while maintainingBrier.178802 and75% accuracy. It is a later adaptive cross, not an independently preregistered discovery. ETF volume improves its auto-deletion parent's CRPS but worsens its Brier.
3. **Size-column exclusion** explains most of I03 versusI00's measured Brier improvement. Aggregate recomputation alone does not. Mid-cap exclusion helps more than small-cap exclusion, which worsens scores; Smallcap500's short initial history and changing inclusion are material. Do not infer a universal anti-smallcap rule.
4. **Existing cyclical/risk/IT relationships** remain useful conditional pieces of the native reference in family-deletion diagnostics. Their influence and stable coefficients are descriptive; they are not standalone causally identified signals.
5. **Multi-scale/evolution/correlation/early-warning additions** are weak or inconsistent increments over57 native fields. Compact versions can beat weak small controls without beating the established reference.
6. **Global→Indian-sector corrections** offer tiny weekly IT/energy MAE gains, weak bank/magnitude and negative monthly results, with no robust downstream NIFTY increment. Feed identity/timestamps constrain interpretation.
7. **Monthly weekly-state interaction** has striking point accuracy but competitive corrupted-state controls, undercoverage and only four outcome windows. It remains an unpassed mechanism lead, not the strongest proven monthly information source.

## Numerical parent effects

| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| H_MULTISCALE | I03_nosize | brier | 92 | -0.001839 |
| H_MULTISCALE | I03_nosize | crps | 92 | -0.000110 |
| H_DYNAMIC | I03_nosize | brier | 92 | -0.001190 |
| H_DYNAMIC | I03_nosize | crps | 92 | -0.000011 |
| H_WARNINGS | I03_nosize | brier | 92 | 0.000048 |
| H_WARNINGS | I03_nosize | crps | 92 | -0.000027 |
| H_CORRELATION | I03_nosize | brier | 92 | -0.003633 |
| H_CORRELATION | I03_nosize | crps | 92 | -0.000006 |
| H_ROTATION | I03_nosize | brier | 92 | -0.001855 |
| H_ROTATION | I03_nosize | crps | 92 | -0.000068 |
| Q_ETF_VOLUME | I03_nosize | brier | 92 | -0.001151 |
| Q_ETF_VOLUME | I03_nosize | crps | 92 | 0.000262 |
| G_DIRECT | G_MATCHED | brier | 92 | 0.009530 |
| G_DIRECT | G_MATCHED | crps | 92 | 0.000242 |
| G_MEDIATED | G_MATCHED | brier | 92 | -0.000157 |
| G_MEDIATED | G_MATCHED | crps | 92 | -0.000104 |
| W2_NODEF_VOLUME | F_NO_DEFENSIVE | brier | 92 | -0.005509 |
| W2_NODEF_VOLUME | F_NO_DEFENSIVE | crps | 92 | 0.000194 |
| W2_NOAUTO_VOLUME | F_DROP_TOP3 | brier | 92 | -0.007534 |
| W2_NOAUTO_VOLUME | F_DROP_TOP3 | crps | 92 | 0.000239 |
| W2_DEF_PC | I03_nosize | brier | 92 | 0.011838 |
| W2_DEF_PC | I03_nosize | crps | 92 | -0.000107 |
| W2_DEF_NORM | I03_nosize | brier | 92 | 0.012184 |
| W2_DEF_NORM | I03_nosize | crps | 92 | 0.000104 |


## Conditional information versus influence

All feature weights are saved per cutoff in `all-reference-feature-weights.csv`. Exact train-median effects are in `exact-feature-effects.csv`, coefficient signs in `coefficient-stability.csv` and development-only residualized tests in `conditional-feature-information.csv`. Fourteen of114 conditional tests meet within-family nominalq<.05 (min.040512), but the selected family, correlated targets and wider search exposure prevent an independent discovery claim. A large coefficient/median-replacement effect can reflect unstable/duplicated representation; several influential variables become harmful in the combined fitted model.

Any future signal ranking should be judged by a frozen parent increment, proper-score tradeoff, source availability, stability and eventual truly new observations. This study does not assign causal explanatory percentages that sum to100.

The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.
