# NIFTY V6 — Market State Evolution

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Registered hypotheses

The eight-variable core is bank short/long relative deceleration, Nifty500 short/long deterioration, defensive/cyclical rotation, five-session sector-correlation change, first difference in sector synchronization, correlation slope, second difference in IT/financial rotation, and cyclical weakness. The wider feature library also stores first differences, second differences and five-session slopes for six state measures; persistent trend, risk and defensive conditions; and a trailing63-session transition frequency of an observable synchronization state. This transition frequency is an empirical past-state hazard, not a fitted latent-state oracle or a validated future regime probability.

H_DYNAMIC adds the eight fields to57 native inputs. H_DYNAMIC_CORE uses four price/risk fields plus these eight instead of the larger static library. H_WARNINGS, H_CORRELATION and H_ROTATION test three-field early-warning blocks. H_MULTISCALE uses20 selected normalized bank/financial/IT/Nifty500 divergences. Parameters remain Ridge100 and the same coherent65/35 residual/historical law; refit dates and mature-label rules match I03.

## Weekly and monthly scores

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| C_SMALL | 92 | 0.391304 | 0.373488 | 0.282224 | 0.760851 | 0.012719 | 0.016730 | 0.023788 | 0.489130 | 0.695652 | 0.039796 |
| H_DYNAMIC | 92 | 0.760870 | 0.768747 | 0.183237 | 0.552258 | 0.010210 | 0.013532 | 0.019947 | 0.597826 | 0.760870 | 0.037891 |
| H_DYNAMIC_CORE | 92 | 0.608696 | 0.572327 | 0.250697 | 0.699595 | 0.012260 | 0.016114 | 0.023595 | 0.478261 | 0.695652 | 0.038483 |
| H_WARNINGS | 92 | 0.782609 | 0.791001 | 0.181999 | 0.550119 | 0.010226 | 0.013503 | 0.019949 | 0.521739 | 0.771739 | 0.038329 |
| H_CORRELATION | 92 | 0.782609 | 0.794388 | 0.185679 | 0.557864 | 0.010205 | 0.013555 | 0.019947 | 0.565217 | 0.782609 | 0.037566 |
| H_ROTATION | 92 | 0.771739 | 0.774794 | 0.183902 | 0.553201 | 0.010267 | 0.013582 | 0.019907 | 0.532609 | 0.771739 | 0.037817 |
| H_MULTISCALE | 92 | 0.717391 | 0.697146 | 0.183885 | 0.549140 | 0.010308 | 0.013131 | 0.019636 | 0.565217 | 0.782609 | 0.039336 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| C_SMALL | 76 | 0.144737 | 0.152330 | 0.436234 | 1.116123 | 0.035988 | 0.046680 | 0.055953 | 0.118421 | 0.394737 | 0.066162 |
| H_DYNAMIC | 76 | 0.578947 | 0.624373 | 0.260266 | 0.722791 | 0.029653 | 0.039032 | 0.048257 | 0.289474 | 0.500000 | 0.074820 |
| H_DYNAMIC_CORE | 76 | 0.302632 | 0.305735 | 0.368125 | 0.970969 | 0.032987 | 0.042504 | 0.051398 | 0.131579 | 0.526316 | 0.065270 |
| H_WARNINGS | 76 | 0.565789 | 0.618280 | 0.259555 | 0.716699 | 0.029584 | 0.038919 | 0.048361 | 0.302632 | 0.500000 | 0.077433 |
| H_CORRELATION | 76 | 0.592105 | 0.635484 | 0.243229 | 0.682540 | 0.029307 | 0.038819 | 0.048246 | 0.302632 | 0.513158 | 0.077359 |
| H_ROTATION | 76 | 0.578947 | 0.629391 | 0.256639 | 0.712455 | 0.029600 | 0.038973 | 0.048260 | 0.289474 | 0.513158 | 0.075355 |
| H_MULTISCALE | 76 | 0.763158 | 0.759857 | 0.187396 | 0.564924 | 0.026989 | 0.035611 | 0.047247 | 0.407895 | 0.644737 | 0.080586 |
| M_PERSIST | 76 | 0.552632 | 0.562007 | 0.275664 | 0.754286 | 0.029292 | 0.038198 | 0.048625 | 0.210526 | 0.578947 | 0.061087 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| H_DYNAMIC | I03_nosize | brier | 92 | -0.001190 |
| H_DYNAMIC | I03_nosize | crps | 92 | -0.000011 |
| H_DYNAMIC_CORE | C_SMALL | brier | 92 | 0.031527 |
| H_DYNAMIC_CORE | C_SMALL | crps | 92 | 0.000459 |
| H_WARNINGS | I03_nosize | brier | 92 | 0.000048 |
| H_WARNINGS | I03_nosize | crps | 92 | -0.000027 |
| H_CORRELATION | I03_nosize | brier | 92 | -0.003633 |
| H_CORRELATION | I03_nosize | crps | 92 | -0.000006 |
| H_ROTATION | I03_nosize | brier | 92 | -0.001855 |
| H_ROTATION | I03_nosize | crps | 92 | -0.000068 |


The full dynamic addition worsens weekly Brier by .00119009 and CRPS by .00001099. Compact evolution beats its weak eight-static-input comparison in some metrics but remains weaker than the established native system. Because that compact pair also changes static variables, it is a system comparison, not an isolated effect of evolution. Monthly multiscale Brier .187396/CRPS .026989 is a retrospective lead, but with only four disjoint monthly outcomes and no convincing incremental state mechanism it cannot establish predictability.

## Causal reconstruction and failure diagnosis

All differences, slopes, correlations and persistence features use current/past prices only. A dedicated future-source perturbation check mutates later observations and verifies that earlier features do not change. No pre2025 observations initialize the indicators. Source availability is still inherited from archival reconstruction, with extra lag sensitivity tests; the check cannot prove that a historical vendor payload was actually received at the assumed time.

Weekly forecast-state aggregation is a separate monthly experiment. Those states are causally reconstructed historical prequential forecasts fitted without their own outcomes, not forecasts actually issued at those historical dates. No states are backfilled before the first available reconstructed forecast. Replaying them now preserves chronological fit logic but does not create a new untouched sample. One additional lag improves monthly point scores, and five-/21-session shifted-state diagnostics remain competitive, so exact-date evolution is not isolated as the driver.

| model | score | test | min_gain | max_gain | positive_cases | cases |
| --- | --- | --- | --- | --- | --- | --- |
| H_DYNAMIC | brier | leave_month_out | -0.002885 | 0.000946 | 1 | 5 |
| H_DYNAMIC | brier | disjoint_phase | -0.009735 | 0.005529 | 3 | 5 |
| H_DYNAMIC | brier | remove_best_overlapping_origins | -0.008832 | -0.002141 | 0 | 4 |
| H_DYNAMIC | crps | leave_month_out | -0.000502 | -0.000006 | 0 | 5 |
| H_DYNAMIC | crps | disjoint_phase | -0.000587 | 0.000305 | 1 | 5 |
| H_DYNAMIC | crps | remove_best_overlapping_origins | -0.000666 | -0.000306 | 0 | 4 |
| H_MULTISCALE | brier | leave_month_out | -0.012623 | 0.004800 | 2 | 5 |
| H_MULTISCALE | brier | disjoint_phase | -0.009362 | 0.011191 | 2 | 5 |
| H_MULTISCALE | brier | remove_best_overlapping_origins | -0.015353 | -0.004080 | 0 | 4 |
| H_MULTISCALE | crps | leave_month_out | -0.000454 | -0.000187 | 0 | 5 |
| H_MULTISCALE | crps | disjoint_phase | -0.000880 | 0.000077 | 1 | 5 |
| H_MULTISCALE | crps | remove_best_overlapping_origins | -0.000746 | -0.000400 | 0 | 4 |
| H_DYNAMIC_CORE | brier | leave_month_out | -0.083969 | -0.053425 | 0 | 5 |
| H_DYNAMIC_CORE | brier | disjoint_phase | -0.093515 | -0.037248 | 0 | 5 |
| H_DYNAMIC_CORE | brier | remove_best_overlapping_origins | -0.110342 | -0.075096 | 0 | 4 |
| H_DYNAMIC_CORE | crps | leave_month_out | -0.002909 | -0.001454 | 0 | 5 |
| H_DYNAMIC_CORE | crps | disjoint_phase | -0.003025 | -0.001208 | 0 | 5 |
| H_DYNAMIC_CORE | crps | remove_best_overlapping_origins | -0.003124 | -0.002429 | 0 | 4 |


Retain the hypotheses and their failed results. A larger dynamic library has not produced a robust weekly improvement over I03. Evolution may describe current regime drift better than future returns in this sample; low sample capacity, correlated inputs and training-window changes are alternative explanations requiring an independent future check.

The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.
