# V11 Structural Ensemble Research

The frozen mixture uses weights 40% base rotation, 30% sparse rotation and 30% volatility Student-t. V10 shrinkage allocates half to this mixture and half to empirical history. The strictly matched V11 breadth version adds official breadth to all three original component designs without changing their weights. Broader equal-weight, memory, historical shrinkage, ETF and derivatives mixtures test different inputs. Leave-one-expert-out fits test marginal value. Doubling the native expert counts its mass twice in a deliberate redundancy control.

The restricted simplex learns Brier- or CRPS-targeted weights using only mature, earlier archived outcomes. It uses at least 20 such outcomes, regularizes toward equal weights, and bounds individual weights from 2.5% to 55%. High-volatility weights draw 70% from the all-regime rule. Every assembled distribution produces its own direction, point, quantiles, buckets and endpoint. Forecast error correlation, shared bad dates and disagreement are more informative than feature-name differences alone.

| model | n | disjoint | brier | crps | log_loss | accuracy | balanced_accuracy | mae | median_mae | pinball | coverage50 | coverage80 | width80 | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J11_BREADTH_ALL | 265 | 53 | 0.236138 | 0.010960 | 0.667636 | 0.637736 | 0.650612 | 0.015003 | 0.014658 | 0.005452 | 0.535849 | 0.822642 | 0.050120 | 0.085824 |
| J11_FIXED_NATIVE_EQ | 265 | 53 | 0.237702 | 0.010866 | 0.671490 | 0.630189 | 0.640275 | 0.015002 | 0.014696 | 0.005399 | 0.520755 | 0.811321 | 0.050175 | 0.111183 |
| J11_EXCLUDE_D_EQ_SIGNMAG | 265 | 53 | 0.239610 | 0.010910 | 0.673519 | 0.630189 | 0.644751 | 0.015131 | 0.014656 | 0.005437 | 0.550943 | 0.822642 | 0.049384 | 0.102506 |
| J11_EXCLUDE_D_EQ_STUDENT | 265 | 53 | 0.240462 | 0.010898 | 0.675718 | 0.626415 | 0.640477 | 0.015017 | 0.014683 | 0.005419 | 0.528302 | 0.818868 | 0.047463 | 0.109656 |
| J11_FIXED_EQ | 265 | 53 | 0.241200 | 0.011112 | 0.678291 | 0.615094 | 0.628552 | 0.015442 | 0.015007 | 0.005506 | 0.528302 | 0.818868 | 0.051127 | 0.104367 |
| J11_BREADTH_ALL_HIST | 265 | 53 | 0.241814 | 0.010811 | 0.677018 | 0.603774 | 0.616626 | 0.014894 | 0.014638 | 0.005373 | 0.535849 | 0.815094 | 0.046144 | 0.087606 |
| J11_REDUNDANT | 265 | 53 | 0.243129 | 0.011067 | 0.681640 | 0.607547 | 0.620900 | 0.015343 | 0.014892 | 0.005517 | 0.498113 | 0.811321 | 0.046865 | 0.103810 |
| J11_EQUAL | 265 | 53 | 0.243246 | 0.010878 | 0.680977 | 0.600000 | 0.614143 | 0.015158 | 0.014813 | 0.005417 | 0.520755 | 0.811321 | 0.047809 | 0.124015 |
| J11_FIXED_HIST | 265 | 53 | 0.243642 | 0.010819 | 0.680705 | 0.607547 | 0.622690 | 0.015007 | 0.014688 | 0.005381 | 0.554717 | 0.815094 | 0.047176 | 0.093374 |
| J11_NO_BREADTH | 265 | 53 | 0.243664 | 0.010869 | 0.680791 | 0.603774 | 0.620207 | 0.015072 | 0.014661 | 0.005412 | 0.539623 | 0.803774 | 0.046335 | 0.087884 |
| J11_EXCLUDE_B_ROT | 265 | 53 | 0.244333 | 0.010777 | 0.682878 | 0.588679 | 0.602218 | 0.015044 | 0.014814 | 0.005343 | 0.539623 | 0.807547 | 0.048008 | 0.123974 |
| J11_EXCLUDE_HISTORY | 265 | 53 | 0.244419 | 0.011016 | 0.684910 | 0.603774 | 0.616626 | 0.015317 | 0.015005 | 0.005468 | 0.505660 | 0.803774 | 0.048335 | 0.111214 |
| J11_EXCLUDE_L_EQ_CONC | 265 | 53 | 0.245201 | 0.010820 | 0.684582 | 0.584906 | 0.599734 | 0.015129 | 0.014841 | 0.005357 | 0.535849 | 0.815094 | 0.048231 | 0.125042 |
| J11_HISTORY_MORE | 265 | 53 | 0.245233 | 0.010832 | 0.683935 | 0.600000 | 0.615933 | 0.015026 | 0.014767 | 0.005378 | 0.528302 | 0.803774 | 0.045007 | 0.088317 |
| J11_MEMORY | 265 | 53 | 0.246160 | 0.011451 | 0.687865 | 0.603774 | 0.617521 | 0.015716 | 0.015213 | 0.005693 | 0.475472 | 0.784906 | 0.043827 | 0.108740 |
| J11_DERIV_RISK | 265 | 53 | 0.246367 | 0.011052 | 0.687886 | 0.626415 | 0.642267 | 0.015540 | 0.015029 | 0.005498 | 0.520755 | 0.807547 | 0.048356 | 0.127389 |
| J11_ETF | 265 | 53 | 0.246409 | 0.011038 | 0.688091 | 0.622642 | 0.637994 | 0.015526 | 0.015002 | 0.005489 | 0.524528 | 0.811321 | 0.048582 | 0.127576 |
| J11_STACK_BRIER | 265 | 53 | 0.246590 | 0.011028 | 0.688212 | 0.600000 | 0.615038 | 0.015176 | 0.014916 | 0.005483 | 0.539623 | 0.811321 | 0.047711 | 0.119279 |
| J11_EXCLUDE_B_SPARSE_EQ | 265 | 53 | 0.248727 | 0.011048 | 0.692614 | 0.588679 | 0.600427 | 0.015502 | 0.015015 | 0.005510 | 0.483019 | 0.784906 | 0.044609 | 0.123126 |
| J11_STACK_CRPS | 265 | 53 | 0.248728 | 0.011023 | 0.692259 | 0.588679 | 0.604008 | 0.015309 | 0.015015 | 0.005486 | 0.520755 | 0.796226 | 0.046214 | 0.126765 |
| J11_STACK_REGIME | 265 | 53 | 0.248937 | 0.011005 | 0.692724 | 0.592453 | 0.607386 | 0.015297 | 0.015011 | 0.005471 | 0.520755 | 0.796226 | 0.045936 | 0.126685 |

| expert1 | expert2 | n | probability_corr | error_corr | crps_corr | classification_disagreement | shared_worst_decile | energy_distance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_SPARSE_EQ | D_EQ_SIGNMAG | 265 | 0.412447 | 0.896652 | 0.738138 | 0.350943 | 0.030189 | 0.006777 |
| B_SPARSE_EQ | HISTORY | 265 | 0.284859 | 0.898779 | 0.670545 | 0.501887 | 0.079245 | 0.007584 |
| B_ROT | B_SPARSE_EQ | 265 | 0.544729 | 0.904361 | 0.800271 | 0.320755 | 0.056604 | 0.006049 |
| B_SPARSE_EQ | D_EQ_STUDENT | 265 | 0.423869 | 0.905300 | 0.654151 | 0.313208 | 0.015094 | 0.007505 |
| B_ROT | HISTORY | 265 | 0.323092 | 0.915370 | 0.850051 | 0.475472 | 0.041509 | 0.004513 |
| L_EQ_CONC | HISTORY | 265 | 0.310420 | 0.918661 | 0.849432 | 0.437736 | 0.045283 | 0.004222 |
| B_SPARSE_EQ | L_EQ_CONC | 265 | 0.613778 | 0.919387 | 0.830286 | 0.290566 | 0.060377 | 0.005439 |
| HISTORY | D_EQ_SIGNMAG | 265 | 0.114625 | 0.934155 | 0.905232 | 0.566038 | 0.041509 | 0.002198 |
| B_ROT | D_EQ_SIGNMAG | 265 | 0.625327 | 0.940245 | 0.914057 | 0.301887 | 0.041509 | 0.003018 |
| L_EQ_CONC | D_EQ_SIGNMAG | 265 | 0.653904 | 0.946781 | 0.915683 | 0.279245 | 0.041509 | 0.002795 |
| B_ROT | D_EQ_STUDENT | 265 | 0.663817 | 0.947836 | 0.886214 | 0.264151 | 0.033962 | 0.003111 |
| D_EQ_STUDENT | L_EQ_CONC | 265 | 0.668170 | 0.950809 | 0.877759 | 0.241509 | 0.030189 | 0.003036 |
| D_EQ_STUDENT | HISTORY | 265 | 0.153639 | 0.955158 | 0.829438 | 0.566038 | 0.033962 | 0.003180 |
| D_EQ_STUDENT | D_EQ_SIGNMAG | 265 | 0.935130 | 0.991141 | 0.954561 | 0.128302 | 0.086792 | 0.001275 |
| B_ROT | L_EQ_CONC | 265 | 0.967532 | 0.993865 | 0.994678 | 0.060377 | 0.086792 | 0.000285 |

[Weight fit history](ensemble-ledger.json) · [Leave-one-out and full-law comparisons](incremental-comparisons.csv) · [Risk-conditional calibration](expert-conditional-calibration.csv) · [Exact breadth mixture](ensemble-exact-registry.json).
