# V10 Training Data Intelligence

The 85- and 126-row experiments kept feature definitions, calendar, query folds, ridge penalty and pooled calibration reference fixed. Each comparison changed chronological selection or weights. Selectors tested most recent, earliest, systematic spread, distributed adjacent blocks, balanced volatility/trend/financial-rotation quartiles, nearest analogues, and representatives spread across similarity ranks. Distances use training-fit median and standard deviation of the available state vector. Weighted versions place 40% mass uniformly and 60% on the predeclared recency, similarity, regime-balance or joint analogue–recency rule. V9's weak analogue/reliability transfer motivated the mass floor.

The later weekly 85-recent Brier was **0.376831**. The earliest 85 produced **0.242128** and spread produced **0.243061**. On that exact sample, spread CRPS was **0.011906** versus **0.014860**. Median overlap-adjusted training support rose from **17.326** recent to **62.392** spread. The median distinct sessions rose from **89** to **348** and disjoint train windows from **17** to **44**. The earliest 85 retained **17.326** effective observations and still cut loss. Date composition accounts for a separate source of sensitivity beyond the overlap calculation. Earlier weekly point scores improved modestly over the recent-window parent and still trailed symmetric neutral by Brier. Earliest history and broad temporal coverage are leads about the fitting procedure.

## All weekly composition comparisons

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| C85_EARLIEST | 0.269837 | 0.242128 | 0.260217 | 0.011495 | 0.011937 | 0.011649 |
| C126_EARLIEST | 0.268818 | 0.253684 | 0.263564 | 0.011450 | 0.012127 | 0.011685 |
| C85_SPREAD | 0.274811 | 0.243061 | 0.263788 | 0.011610 | 0.011906 | 0.011713 |
| C126_BALANCE_VOL | 0.280034 | 0.251848 | 0.270249 | 0.011833 | 0.012197 | 0.011960 |
| C85_BALANCE_ROTATION | 0.269348 | 0.272131 | 0.270314 | 0.011530 | 0.012738 | 0.011949 |
| C126_BALANCE_ROTATION | 0.279804 | 0.264351 | 0.274439 | 0.011661 | 0.012400 | 0.011918 |
| C85_BLOCKS | 0.283848 | 0.267548 | 0.278189 | 0.011986 | 0.012744 | 0.012249 |
| C126_SPREAD | 0.281238 | 0.273524 | 0.278560 | 0.011827 | 0.012718 | 0.012137 |
| C126_BALANCE_TREND | 0.282489 | 0.274092 | 0.279574 | 0.011971 | 0.012541 | 0.012169 |
| C126_BLOCKS | 0.271468 | 0.295144 | 0.279688 | 0.011483 | 0.013519 | 0.012190 |
| C85_BALANCE_TREND | 0.282150 | 0.277555 | 0.280555 | 0.011688 | 0.012798 | 0.012073 |
| C126_ANALOGUES | 0.280268 | 0.291252 | 0.284081 | 0.011808 | 0.013098 | 0.012256 |
| C85_BALANCE_VOL | 0.294499 | 0.275503 | 0.287904 | 0.012332 | 0.012895 | 0.012527 |
| C126_RECENT | 0.285919 | 0.294744 | 0.288983 | 0.012790 | 0.013330 | 0.012978 |
| C126_REPRESENTATIVE | 0.287600 | 0.292718 | 0.289376 | 0.012171 | 0.013077 | 0.012485 |
| C126_W_BALANCE | 0.281334 | 0.304998 | 0.289549 | 0.012576 | 0.013535 | 0.012909 |
| C85_REPRESENTATIVE | 0.282755 | 0.302481 | 0.289603 | 0.011907 | 0.013405 | 0.012427 |
| C85_ANALOGUES | 0.287847 | 0.293994 | 0.289981 | 0.011991 | 0.013443 | 0.012495 |
| C85_OMIT_M2 | 0.282691 | 0.315919 | 0.294227 | 0.012340 | 0.013685 | 0.012807 |
| C85_OMIT_M1 | 0.274663 | 0.335704 | 0.295855 | 0.012112 | 0.014267 | 0.012860 |
| C126_W_RECENCY | 0.286589 | 0.322128 | 0.298927 | 0.013038 | 0.013751 | 0.013285 |
| C85_OMIT_M3 | 0.276639 | 0.344414 | 0.300168 | 0.012789 | 0.014103 | 0.013245 |
| C126_W_ANALOGUE_RECENCY | 0.288147 | 0.326092 | 0.301320 | 0.013240 | 0.013920 | 0.013476 |
| C126_W_SIMILARITY | 0.288374 | 0.326485 | 0.301605 | 0.013117 | 0.013980 | 0.013417 |
| C85_RECENT | 0.282169 | 0.376831 | 0.315033 | 0.012609 | 0.014860 | 0.013391 |

## Later weekly training support and concentration

| model | training | nominal_rows | distinct_return_sessions | disjoint_training_windows | kish_ESS | overlap_effective_count | maximum_training_weight | df | phase_prediction_variance | design_condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C126_EARLIEST | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 126.000000 | 25.524116 | 0.007937 | 5.161202 | 0.000000 | 4.316815 |
| C126_RECENT | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 126.000000 | 25.524116 | 0.007937 | 5.164207 | 0.000000 | 4.061804 |
| C126_SPREAD | 126.000000 | 126.000000 | 348.000000 | 63.000000 | 126.000000 | 66.482412 | 0.007937 | 5.411596 | 0.000000 | 3.658677 |
| C126_W_ANALOGUE_RECENCY | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 116.377529 | 23.906741 | 0.014022 | 5.050841 | 0.000000 | 3.903825 |
| C126_W_BALANCE | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 125.386737 | 25.472775 | 0.008730 | 5.166286 | 0.000000 | 4.045874 |
| C126_W_RECENCY | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 117.467067 | 23.908685 | 0.012619 | 5.109222 | 0.000000 | 4.174781 |
| C126_W_SIMILARITY | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 116.644839 | 24.118203 | 0.014344 | 5.032022 | 0.000000 | 3.875947 |
| C85_ANALOGUES | 85.000000 | 85.000000 | 164.000000 | 26.000000 | 85.000000 | 25.069396 | 0.011765 | 4.605347 | 0.000000 | 3.919132 |
| C85_BALANCE_ROTATION | 85.000000 | 85.000000 | 258.000000 | 44.000000 | 85.000000 | 42.550059 | 0.011765 | 4.517897 | 0.000000 | 4.234034 |
| C85_EARLIEST | 85.000000 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 | 0.011765 | 4.349440 | 0.000000 | 4.959620 |
| C85_RECENT | 85.000000 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 | 0.011765 | 4.360531 | 0.000000 | 4.564575 |
| C85_SPREAD | 85.000000 | 85.000000 | 348.000000 | 44.000000 | 85.000000 | 62.392055 | 0.011765 | 4.571055 | 0.000000 | 4.129271 |

## Leave recent training months out and replace the removed rows

| horizon | cohort | model | baseline | metric | n | candidate | control | gain | block10_adjusted_low | block10_adjusted_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | C85_OMIT_M1 | C85_RECENT | brier | 265 | 0.295855 | 0.315033 | 0.019178 | -0.020182 | 0.058538 |
| 5 | combined | C85_OMIT_M1 | C85_RECENT | crps | 265 | 0.012860 | 0.013391 | 0.000531 | -0.000314 | 0.001375 |
| 5 | early | C85_OMIT_M1 | C85_RECENT | brier | 173 | 0.274663 | 0.282169 | 0.007506 | -0.015654 | 0.030666 |
| 5 | early | C85_OMIT_M1 | C85_RECENT | crps | 173 | 0.012112 | 0.012609 | 0.000497 | -0.000387 | 0.001382 |
| 5 | later | C85_OMIT_M1 | C85_RECENT | brier | 92 | 0.335704 | 0.376831 | 0.041127 | -0.051142 | 0.133396 |
| 5 | later | C85_OMIT_M1 | C85_RECENT | crps | 92 | 0.014267 | 0.014860 | 0.000593 | -0.001079 | 0.002265 |
| 5 | combined | C85_OMIT_M2 | C85_RECENT | brier | 265 | 0.294227 | 0.315033 | 0.020806 | -0.037519 | 0.079130 |
| 5 | combined | C85_OMIT_M2 | C85_RECENT | crps | 265 | 0.012807 | 0.013391 | 0.000584 | -0.000727 | 0.001894 |
| 5 | early | C85_OMIT_M2 | C85_RECENT | brier | 173 | 0.282691 | 0.282169 | -0.000522 | -0.029511 | 0.028467 |
| 5 | early | C85_OMIT_M2 | C85_RECENT | crps | 173 | 0.012340 | 0.012609 | 0.000269 | -0.001077 | 0.001616 |
| 5 | later | C85_OMIT_M2 | C85_RECENT | brier | 92 | 0.315919 | 0.376831 | 0.060911 | -0.081059 | 0.202881 |
| 5 | later | C85_OMIT_M2 | C85_RECENT | crps | 92 | 0.013685 | 0.014860 | 0.001175 | -0.001436 | 0.003786 |
| 5 | combined | C85_OMIT_M3 | C85_RECENT | brier | 265 | 0.300168 | 0.315033 | 0.014864 | -0.026815 | 0.056544 |
| 5 | combined | C85_OMIT_M3 | C85_RECENT | crps | 265 | 0.013245 | 0.013391 | 0.000146 | -0.000832 | 0.001123 |
| 5 | early | C85_OMIT_M3 | C85_RECENT | brier | 173 | 0.276639 | 0.282169 | 0.005530 | -0.035091 | 0.046151 |
| 5 | early | C85_OMIT_M3 | C85_RECENT | crps | 173 | 0.012789 | 0.012609 | -0.000180 | -0.001345 | 0.000986 |
| 5 | later | C85_OMIT_M3 | C85_RECENT | brier | 92 | 0.344414 | 0.376831 | 0.032417 | -0.053067 | 0.117900 |
| 5 | later | C85_OMIT_M3 | C85_RECENT | crps | 92 | 0.014103 | 0.014860 | 0.000757 | -0.000589 | 0.002103 |

Months are ranked from the latest eligible month backward. These month removals and the realized-loss influence table are diagnostics. See the actual dates and maturities in the [fit ledger](composition-ledger.json) and sensitivity to eliminating top-scoring forecast origins in [calendar stress](temporal-and-disjoint-stress.csv).
