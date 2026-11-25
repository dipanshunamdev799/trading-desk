# NIFTY V17 — Residual return forecasting

The baseline is re-estimated as it actually would have been on each prior dated origin from earlier matured targets. Each historical residual subtracts that origin’s original model forecast. Subsequent fits use only residual outcomes whose endpoint precedes the current decision date. A regularized correction changes the baseline center, with a common past-only standardized residual distribution around it. A zero correction retains the same forecast shape. Neutral, matured history, price only, volatility only, price-plus-volatility, official equal-weight and native-sector models separate ordinary state information from stock or surprise corrections. Direct models solve the full return task on eligible inputs. Orthogonal variants predict each candidate feature from the strong parent state using earlier dates and carry forward the unexplained feature. These are tests of incremental prediction after the specified statistical controls. Hypotheses and comparisons remain retrospective.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | r30 | financial_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249848 | 0.248972 | -0.000876 | -0.004948 | 0.003196 |
| 09:25 | r30 | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250314 | 0.248972 | -0.001342 | -0.006090 | 0.003407 |
| 09:25 | r30 | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250670 | 0.248972 | -0.001698 | -0.007988 | 0.004593 |
| 09:25 | r30 | stock_direct | native_control | brier | 257 | 257 | 0.250968 | 0.249154 | -0.001814 | -0.006071 | 0.002443 |
| 09:25 | r30 | stock_orthogonal | frozen_parent_residual_history | brier | 257 | 257 | 0.250993 | 0.248972 | -0.002021 | -0.005440 | 0.001398 |
| 09:25 | r30 | stock_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.251053 | 0.248972 | -0.002081 | -0.005880 | 0.001718 |
| 09:25 | r30 | surprise_orthogonal | frozen_parent_residual_history | brier | 248 | 248 | 0.250262 | 0.247738 | -0.002524 | -0.009888 | 0.004839 |
| 09:25 | r30 | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.250299 | 0.247738 | -0.002562 | -0.007601 | 0.002478 |
| 09:25 | r30 | joint_stock_native | native_control | brier | 257 | 257 | 0.254599 | 0.249154 | -0.005445 | -0.012878 | 0.001988 |
| 09:25 | r30 | financial_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001259 | 0.001256 | -2.73e-06 | -0.000017 | 0.000012 |
| 09:25 | r30 | surprise_residual | frozen_parent_residual_history | crps | 248 | 248 | 0.001286 | 0.001280 | -6.40e-06 | -0.000019 | 6.63e-06 |
| 09:25 | r30 | surprise_orthogonal | frozen_parent_residual_history | crps | 248 | 248 | 0.001286 | 0.001280 | -6.61e-06 | -0.000026 | 0.000013 |
| 09:25 | r30 | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001263 | 0.001256 | -7.07e-06 | -0.000024 | 9.90e-06 |
| 09:25 | r30 | stock_direct | native_control | crps | 257 | 257 | 0.001253 | 0.001246 | -7.29e-06 | -0.000020 | 5.69e-06 |
| 09:25 | r30 | stock_orthogonal | frozen_parent_residual_history | crps | 257 | 257 | 0.001264 | 0.001256 | -8.00e-06 | -0.000021 | 5.05e-06 |
| 09:25 | r30 | stock_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001265 | 0.001256 | -8.35e-06 | -0.000022 | 5.15e-06 |
| 09:25 | r30 | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001265 | 0.001256 | -8.98e-06 | -0.000026 | 7.73e-06 |
| 09:25 | r30 | joint_stock_native | native_control | crps | 257 | 257 | 0.001266 | 0.001246 | -0.000020 | -0.000040 | -1.27e-07 |
| 10:20 | r30 | surprise_orthogonal | frozen_parent_residual_history | brier | 248 | 248 | 0.260085 | 0.260508 | 0.000423 | -0.006986 | 0.007832 |
| 10:20 | r30 | financial_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.260704 | 0.260102 | -0.000602 | -0.005247 | 0.004042 |
| 10:20 | r30 | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.261404 | 0.260508 | -0.000895 | -0.006232 | 0.004442 |
| 10:20 | r30 | stock_direct | native_control | brier | 257 | 257 | 0.261617 | 0.259793 | -0.001823 | -0.006674 | 0.003027 |
| 10:20 | r30 | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.262813 | 0.260102 | -0.002711 | -0.008473 | 0.003051 |
| 10:20 | r30 | stock_orthogonal | frozen_parent_residual_history | brier | 257 | 257 | 0.263369 | 0.260102 | -0.003267 | -0.008280 | 0.001747 |
| 10:20 | r30 | stock_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.264007 | 0.260102 | -0.003905 | -0.008220 | 0.000410 |
| 10:20 | r30 | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.264868 | 0.260102 | -0.004766 | -0.008449 | -0.001084 |
| 10:20 | r30 | joint_stock_native | native_control | brier | 257 | 257 | 0.265093 | 0.259793 | -0.005299 | -0.016941 | 0.006342 |
| 10:20 | r30 | surprise_orthogonal | frozen_parent_residual_history | crps | 248 | 248 | 0.000800 | 0.000801 | 8.78e-07 | -0.000013 | 0.000014 |
| 10:20 | r30 | surprise_residual | frozen_parent_residual_history | crps | 248 | 248 | 0.000801 | 0.000801 | -2.64e-07 | -9.70e-06 | 9.17e-06 |
| 10:20 | r30 | financial_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000817 | 0.000813 | -3.50e-06 | -0.000013 | 6.49e-06 |
| 10:20 | r30 | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000818 | 0.000813 | -4.31e-06 | -0.000015 | 6.70e-06 |
| 10:20 | r30 | stock_direct | native_control | crps | 257 | 257 | 0.000808 | 0.000803 | -4.48e-06 | -0.000017 | 8.16e-06 |
| 10:20 | r30 | stock_orthogonal | frozen_parent_residual_history | crps | 257 | 257 | 0.000819 | 0.000813 | -5.41e-06 | -0.000015 | 4.65e-06 |
| 10:20 | r30 | stock_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000819 | 0.000813 | -5.96e-06 | -0.000014 | 1.73e-06 |
| 10:20 | r30 | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000821 | 0.000813 | -7.30e-06 | -0.000015 | 3.21e-07 |
| 10:20 | r30 | joint_stock_native | native_control | crps | 257 | 257 | 0.000821 | 0.000803 | -0.000018 | -0.000042 | 7.21e-06 |
| 09:25 | regular_residual | stock_orthogonal | frozen_parent_residual_history | brier | 257 | 257 | 0.247944 | 0.247995 | 0.000051 | -0.005089 | 0.005192 |
| 09:25 | regular_residual | stock_direct | native_control | brier | 257 | 257 | 0.250368 | 0.249434 | -0.000934 | -0.005265 | 0.003398 |
| 09:25 | regular_residual | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249277 | 0.247995 | -0.001282 | -0.007601 | 0.005036 |
| 09:25 | regular_residual | stock_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249490 | 0.247995 | -0.001495 | -0.004965 | 0.001975 |
| 09:25 | regular_residual | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249682 | 0.247995 | -0.001687 | -0.006882 | 0.003508 |
| 09:25 | regular_residual | financial_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250638 | 0.247995 | -0.002643 | -0.007046 | 0.001761 |
| 09:25 | regular_residual | surprise_orthogonal | frozen_parent_residual_history | brier | 248 | 248 | 0.251109 | 0.248170 | -0.002939 | -0.008846 | 0.002968 |
| 09:25 | regular_residual | joint_stock_native | native_control | brier | 257 | 257 | 0.253512 | 0.249434 | -0.004077 | -0.014855 | 0.006700 |
| 09:25 | regular_residual | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.252806 | 0.248170 | -0.004636 | -0.009282 | 0.000010 |
| 09:25 | regular_residual | stock_direct | native_control | crps | 257 | 257 | 0.003487 | 0.003484 | -2.15e-06 | -0.000041 | 0.000037 |

The case files contain location, Brier, log loss, mean and median absolute error, CRPS, interval score, quantile loss and predictive width. Every predicted distribution and the training-end receipt can be retrieved by law index. Reported CRPS is positive and lower is better. Gains are parent loss minus amended forecast loss. The 128-atom law gives a smoothed direction probability. Risk laws use nonnegative support.

[Full matched residual results](postopen-matched-evidence.csv) · [Chronological baseline/residual ledger at 09:25](residual-0925-baseline-residual-ledger.csv.gz) · [Residual fitting receipts at 09:25](residual-0925-fit-receipt.ndjson.gz) · [Residual distributions at 09:25](residual-0925-laws.npz) · [Falsification and calendar checks](V17_VALIDATION_AND_FALSIFICATION.md)
