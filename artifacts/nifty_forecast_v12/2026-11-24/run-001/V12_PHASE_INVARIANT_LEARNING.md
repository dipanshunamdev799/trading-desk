# V12 Phase Invariant Learning

The deterministic calendar anchor is **2025-04-02**, the first date of the inherited frozen market matrix. Each observed session position modulo 5 or 21 defines one phase. Every phase is evaluated on the same historical origins where its inner and outer samples have enough matured rows. The full phase ensemble assigns equal weight to each fitted complete law. Averaging predicted locations and calibrating residuals once is a different comparison. Shared coefficients use phase-normalized equations and a block-average prior, while pooled coefficients combine block fits and the phase average.

| horizon | model | n | disjoint | brier | crps | accuracy | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | PH_NATIVE_00 | 265 | 53 | 0.231728 | 0.011001 | 0.626415 | 0.784906 | 0.042772 |
| 5 | PH_NATIVE_02 | 265 | 53 | 0.234918 | 0.011203 | 0.618868 | 0.758491 | 0.042172 |
| 5 | PH_NATIVE_01 | 265 | 53 | 0.237022 | 0.011344 | 0.633962 | 0.769811 | 0.043146 |
| 5 | PH_NATIVE_04 | 265 | 53 | 0.245017 | 0.011573 | 0.607547 | 0.769811 | 0.043343 |
| 5 | PH_NATIVE_03 | 265 | 53 | 0.254655 | 0.011555 | 0.603774 | 0.747170 | 0.042233 |
| 21 | PH_NATIVE_06 | 217 | 11 | 0.240585 | 0.026814 | 0.594470 | 0.654378 | 0.080494 |
| 21 | PH_NATIVE_08 | 217 | 11 | 0.264861 | 0.028791 | 0.566820 | 0.622120 | 0.090460 |
| 21 | PH_NATIVE_07 | 217 | 11 | 0.267709 | 0.029236 | 0.516129 | 0.612903 | 0.084511 |
| 21 | PH_NATIVE_04 | 217 | 11 | 0.268564 | 0.028275 | 0.622120 | 0.612903 | 0.081501 |
| 21 | PH_NATIVE_05 | 217 | 11 | 0.279013 | 0.028487 | 0.580645 | 0.658986 | 0.086062 |
| 21 | PH_NATIVE_02 | 217 | 11 | 0.286039 | 0.029660 | 0.488479 | 0.506912 | 0.069424 |
| 21 | PH_NATIVE_03 | 217 | 11 | 0.297847 | 0.029235 | 0.576037 | 0.580645 | 0.076879 |
| 21 | PH_NATIVE_09 | 217 | 11 | 0.302631 | 0.030278 | 0.488479 | 0.548387 | 0.085758 |
| 21 | PH_NATIVE_01 | 217 | 11 | 0.309472 | 0.030366 | 0.460829 | 0.548387 | 0.077215 |
| 21 | PH_NATIVE_16 | 217 | 11 | 0.316228 | 0.031648 | 0.539171 | 0.543779 | 0.085474 |
| 21 | PH_NATIVE_19 | 217 | 11 | 0.320871 | 0.032575 | 0.451613 | 0.506912 | 0.085003 |
| 21 | PH_NATIVE_17 | 217 | 11 | 0.323446 | 0.033372 | 0.520737 | 0.511521 | 0.082214 |
| 21 | PH_NATIVE_11 | 217 | 11 | 0.328651 | 0.033458 | 0.502304 | 0.539171 | 0.088226 |
| 21 | PH_NATIVE_20 | 217 | 11 | 0.329258 | 0.031480 | 0.451613 | 0.506912 | 0.080686 |
| 21 | PH_NATIVE_18 | 217 | 11 | 0.336612 | 0.032632 | 0.516129 | 0.516129 | 0.083505 |
| 21 | PH_NATIVE_12 | 217 | 11 | 0.341934 | 0.033469 | 0.479263 | 0.543779 | 0.088338 |
| 21 | PH_NATIVE_10 | 217 | 11 | 0.344088 | 0.032990 | 0.428571 | 0.511521 | 0.089049 |
| 21 | PH_NATIVE_13 | 217 | 11 | 0.350644 | 0.036295 | 0.483871 | 0.557604 | 0.097408 |
| 21 | PH_NATIVE_00 | 217 | 11 | 0.365147 | 0.033337 | 0.387097 | 0.506912 | 0.082565 |
| 21 | PH_NATIVE_15 | 217 | 11 | 0.371492 | 0.033510 | 0.419355 | 0.488479 | 0.083016 |
| 21 | PH_NATIVE_14 | 217 | 11 | 0.387478 | 0.036268 | 0.428571 | 0.520737 | 0.095773 |

The weekly native phase-zero result **0.231728 / 0.011001** reproduces V11. The all-phase weekly law achieves **0.233211 / 0.010980**. The monthly all-phase law reaches **0.290905 / 0.029347**. The lowest monthly phase Brier is a hindsight comparison and requires its own CRPS, alternative phase results and bounded null-reselection check.

![Weekly and monthly scores by fixed training phase](C:/Users/ME/Desktop/trading-desk/artifacts/nifty_forecast_v12/2026-11-24/run-001/phase-sensitivity.png)

Both the 85- and 126-row tests include fixed recent/spread dates, historical state diversity, random contiguous blocks, and approximately equal phase coverage. The following support estimates distinguish copied rolling labels from distinct underlying return dates. The phase location and coefficient dispersion measures are calculated within each fit. Across-phase tests still share the same period history.

| horizon | model | training | nominal_rows | distinct_return_sessions | disjoint_training_windows | overlap_effective_count | member_location_sd | member_coefficient_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | PH_MEM85_DIVERSE_PHASE_MIXTURE | 85.000000 | 85.000000 | 257.000000 | 41.000000 | 42.954816 | 0.008320 | 0.000588 |
| 5 | PH_MEM85_PHASE_BALANCE_PLAIN | 85.000000 | 85.000000 | 153.000000 | 17.000000 | 25.000000 | 0.006334 | 0.000589 |
| 5 | PH_MEM85_RANDOM_BLOCKS_PHASE_MIXTURE | 85.000000 | 85.000000 | 137.000000 | 17.000000 | 22.507788 | 0.004852 | 0.000464 |
| 5 | PH_MEM85_RECENT_PLAIN | 85.000000 | 85.000000 | 89.000000 | 17.000000 | 17.326139 | 0.006951 | 0.000371 |
| 5 | PH_MEM85_SPREAD_PLAIN | 85.000000 | 85.000000 | 348.000000 | 44.000000 | 62.392055 | 0.007994 | 0.000687 |
| 5 | PH_NATIVE_00 | 344.000000 | 69.000000 | 345.000000 | 69.000000 | 69.000000 | 0.004794 | 0.000640 |
| 5 | PH_NATIVE_PHASE_MIXTURE | 344.000000 | 344.000000 | 348.000000 | 69.000000 | 69.121495 | 0.004794 | 0.000640 |
| 5 | PH_NATIVE_PLAIN | 344.000000 | 344.000000 | 348.000000 | 69.000000 | 69.121495 | 0.004794 | 0.000640 |
| 5 | PH_NATIVE_POOLED | 344.000000 | 344.000000 | 348.000000 | 69.000000 | 69.121495 | 0.004794 | 0.000640 |
| 21 | PH_MEM85_DIVERSE_PHASE_MIXTURE | 85.000000 | 85.000000 | 324.000000 | 13.500000 | 13.872417 | 0.015349 | 0.001225 |
| 21 | PH_MEM85_PHASE_BALANCE_PLAIN | 85.000000 | 85.000000 | 214.500000 | 7.000000 | 6.351785 | 0.018018 | 0.001166 |
| 21 | PH_MEM85_RANDOM_BLOCKS_PHASE_MIXTURE | 85.000000 | 85.000000 | 235.000000 | 9.000000 | 9.011006 | 0.013100 | 0.001006 |
| 21 | PH_MEM85_RECENT_PLAIN | 85.000000 | 85.000000 | 105.000000 | 5.000000 | 4.409969 | 0.014402 | 0.000933 |
| 21 | PH_MEM85_SPREAD_PLAIN | 85.000000 | 85.000000 | 337.500000 | 15.000000 | 15.491215 | 0.017010 | 0.001243 |
| 21 | PH_NATIVE_00 | 317.500000 | 15.500000 | 325.500000 | 15.500000 | 15.500000 | 0.018096 | 0.001991 |
| 21 | PH_NATIVE_06 | 317.500000 | 15.500000 | 325.500000 | 15.500000 | 15.500000 | 0.018096 | 0.001991 |
| 21 | PH_NATIVE_PHASE_MIXTURE | 317.500000 | 317.500000 | 337.500000 | 15.500000 | 15.459114 | 0.018096 | 0.001991 |
| 21 | PH_NATIVE_PLAIN | 317.500000 | 317.500000 | 337.500000 | 15.500000 | 15.459114 | 0.018096 | 0.001991 |
| 21 | PH_NATIVE_POOLED | 317.500000 | 317.500000 | 337.500000 | 15.500000 | 15.459114 | 0.018096 | 0.001991 |

[All phases](leaderboard.csv) · [Matured training samples and row budgets](phase-ledger.json) · [Disjoint phases and episode deletion](phase-and-episode-stress.csv).
