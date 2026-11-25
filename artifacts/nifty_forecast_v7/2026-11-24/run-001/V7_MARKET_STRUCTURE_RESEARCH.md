# NIFTY V7 · Market Structure Research

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

The 21-session correlation matrix of nine authentic Indian sector indices supplies average pair correlation, dispersion, share of variance in the largest eigenvalue, entropy effective factor count and the fraction of pairs above .65. We also measured implied volatility synchronization from correlations of trailing five-session realized standard deviations, participation signs, five-session rank persistence and leadership concentration. Volatility synchronization refers to the observed rolling realized-volatility features. The sequence uses causal rolling windows ending at the origin. No individual stock contributes an extra NIFTY outcome. The V6 defensive-deletion regression is the immediate parent of the structural additions.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_NO_DEF | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| S_SIMPLE | 92 | 0.597826 | 0.623851 | 0.231392 | 0.654108 | 0.011196 | 0.015249 | 0.015039 | 0.020872 | 0.347826 | 0.706522 | 0.037992 |
| S_NETWORK | 92 | 0.750000 | 0.762700 | 0.172971 | 0.526632 | 0.009986 | 0.013015 | 0.012740 | 0.019452 | 0.554348 | 0.793478 | 0.039281 |
| S_LEADERSHIP | 92 | 0.782609 | 0.791001 | 0.170160 | 0.523376 | 0.010104 | 0.013154 | 0.012620 | 0.019733 | 0.543478 | 0.793478 | 0.038923 |
| S_LEVEL | 92 | 0.760870 | 0.768747 | 0.175319 | 0.532980 | 0.010030 | 0.013122 | 0.012654 | 0.019680 | 0.576087 | 0.771739 | 0.038273 |
| S_STATE | 92 | 0.782609 | 0.794388 | 0.181259 | 0.546605 | 0.010350 | 0.013340 | 0.012954 | 0.020236 | 0.532609 | 0.793478 | 0.038281 |
| S_STATE_LAG | 92 | 0.728261 | 0.733672 | 0.197292 | 0.582443 | 0.010602 | 0.013938 | 0.013518 | 0.020778 | 0.521739 | 0.793478 | 0.037765 |
| S_STATE_ACCEL | 92 | 0.760870 | 0.768747 | 0.170173 | 0.521355 | 0.009851 | 0.012809 | 0.012492 | 0.019384 | 0.565217 | 0.782609 | 0.037953 |
| S_ROTATION | 92 | 0.793478 | 0.800435 | 0.164548 | 0.510719 | 0.010041 | 0.012926 | 0.012534 | 0.019425 | 0.554348 | 0.815217 | 0.040028 |
| T_ROT_DOMESTIC | 92 | 0.804348 | 0.809869 | 0.162145 | 0.505266 | 0.009927 | 0.012893 | 0.012447 | 0.019361 | 0.543478 | 0.815217 | 0.038873 |
| T_ROT_OTHER | 92 | 0.782609 | 0.787615 | 0.169046 | 0.521320 | 0.010164 | 0.013157 | 0.012692 | 0.019697 | 0.532609 | 0.815217 | 0.040604 |
| T_ROT_LAG5 | 92 | 0.793478 | 0.803822 | 0.164382 | 0.510143 | 0.010040 | 0.012945 | 0.012558 | 0.019537 | 0.532609 | 0.815217 | 0.040523 |
| T_ROT_FOREIGN_LAG | 92 | 0.804348 | 0.809869 | 0.165296 | 0.511864 | 0.009942 | 0.012885 | 0.012366 | 0.019330 | 0.532609 | 0.815217 | 0.039127 |
| T_ROT_REV | 92 | 0.793478 | 0.800435 | 0.164176 | 0.509953 | 0.010037 | 0.012919 | 0.012522 | 0.019415 | 0.554348 | 0.815217 | 0.040059 |
| T_ROT_WINDOW | 92 | 0.586957 | 0.614417 | 0.223615 | 0.636175 | 0.011297 | 0.014687 | 0.014614 | 0.021507 | 0.565217 | 0.760870 | 0.043067 |
| T_ROT_EMBARGO | 92 | 0.826087 | 0.835510 | 0.164792 | 0.510975 | 0.009935 | 0.012898 | 0.012447 | 0.019147 | 0.565217 | 0.793478 | 0.040823 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| C_NO_DEF | C_RAW | brier | 92 | 0.012244 |
| C_NO_DEF | C_RAW | crps | 92 | 0.000131 |
| S_LEADERSHIP | C_NO_DEF | brier | 92 | -0.000357 |
| S_LEADERSHIP | C_NO_DEF | crps | 92 | -0.000036 |
| S_LEVEL | C_NO_DEF | brier | 92 | -0.005516 |
| S_LEVEL | C_NO_DEF | crps | 92 | 0.000038 |
| S_NETWORK | C_NO_DEF | brier | 92 | -0.003169 |
| S_NETWORK | C_NO_DEF | crps | 92 | 0.000082 |
| S_ROTATION | C_NO_DEF | brier | 92 | 0.005255 |
| S_ROTATION | C_NO_DEF | crps | 92 | 0.000027 |
| S_SIMPLE | C_NO_DEF | brier | 92 | -0.061589 |
| S_SIMPLE | C_NO_DEF | crps | 92 | -0.001128 |
| S_STATE | S_LEVEL | brier | 92 | -0.005940 |
| S_STATE | S_LEVEL | crps | 92 | -0.000320 |
| S_STATE_ACCEL | S_LEVEL | brier | 92 | 0.005146 |
| S_STATE_ACCEL | S_LEVEL | crps | 92 | 0.000179 |
| S_STATE_LAG | S_LEVEL | brier | 92 | -0.021973 |
| S_STATE_LAG | S_LEVEL | crps | 92 | -0.000572 |
| T_ROT_DOMESTIC | C_NO_DEF | brier | 92 | 0.007658 |
| T_ROT_DOMESTIC | C_NO_DEF | crps | 92 | 0.000141 |
| T_ROT_EMBARGO | S_ROTATION | brier | 92 | -0.000245 |
| T_ROT_EMBARGO | S_ROTATION | crps | 92 | 0.000105 |
| T_ROT_FOREIGN_LAG | S_ROTATION | brier | 92 | -0.000748 |
| T_ROT_FOREIGN_LAG | S_ROTATION | crps | 92 | 0.000099 |
| T_ROT_LAG5 | S_ROTATION | brier | 92 | 0.000166 |
| T_ROT_LAG5 | S_ROTATION | crps | 92 | 0.000000 |
| T_ROT_OTHER | C_NO_DEF | brier | 92 | 0.000757 |
| T_ROT_OTHER | C_NO_DEF | crps | 92 | -0.000096 |
| T_ROT_REV | S_ROTATION | brier | 92 | 0.000372 |
| T_ROT_REV | S_ROTATION | crps | 92 | 0.000004 |
| T_ROT_WINDOW | S_ROTATION | brier | 92 | -0.059067 |
| T_ROT_WINDOW | S_ROTATION | crps | 92 | -0.001256 |


V7’s lowest weekly Brier came after the exposed four-input rotation lead was split into domestic and cross-market/activity blocks. `T_ROT_DOMESTIC` adds only five-session changes in Bank Nifty minus financial services momentum and defensive minus cyclical momentum. It reaches Brier .162145 and 74/92 correct. The full four-field `S_ROTATION` reaches .164548. The global-relative plus ETF subblock alone reaches .169046. Simple correlation levels and broad network measures produce weaker gains. The full four-field lag control reaches .164382 when the four added inputs are set back five sessions, which leaves the interpretation of current rotation timing unresolved. A shorter 189-origin training window raises Brier to .223615.

| model | score | test | least_gain | most_gain | positive |
| --- | --- | --- | --- | --- | --- |
| T_ROT_DOMESTIC | brier | omit_fold | 0.003918 | 0.011499 | 5/5 |
| T_ROT_DOMESTIC | brier | omit_largest_gains | -0.002876 | 0.006458 | 3/4 |
| T_ROT_DOMESTIC | brier | disjoint_phase | -0.008357 | 0.021166 | 3/5 |
| T_ROT_DOMESTIC | crps | omit_fold | -0.000228 | -0.000075 | 0/5 |
| T_ROT_DOMESTIC | crps | omit_largest_gains | -0.000619 | -0.000246 | 0/4 |
| T_ROT_DOMESTIC | crps | disjoint_phase | -0.000540 | 0.000078 | 1/5 |
| S_ROTATION | brier | omit_fold | 0.000611 | 0.010868 | 5/5 |
| S_ROTATION | brier | omit_largest_gains | -0.006027 | 0.003587 | 2/4 |
| S_ROTATION | brier | disjoint_phase | -0.017255 | 0.019603 | 3/5 |
| S_ROTATION | crps | omit_fold | -0.000419 | -0.000219 | 0/5 |
| S_ROTATION | crps | omit_largest_gains | -0.000750 | -0.000356 | 0/4 |
| S_ROTATION | crps | disjoint_phase | -0.000585 | -0.000056 | 0/5 |
| S_STATE_ACCEL | brier | omit_fold | -0.006071 | 0.005436 | 2/5 |
| S_STATE_ACCEL | brier | omit_largest_gains | -0.017007 | -0.002653 | 0/4 |
| S_STATE_ACCEL | brier | disjoint_phase | -0.013386 | 0.012637 | 2/5 |
| S_STATE_ACCEL | crps | omit_fold | -0.000285 | 0.000049 | 1/5 |
| S_STATE_ACCEL | crps | omit_largest_gains | -0.000429 | -0.000138 | 0/4 |
| S_STATE_ACCEL | crps | disjoint_phase | -0.000243 | -0.000012 | 0/5 |


| model | baseline | metric | n | gain | adjusted95_block10 |
| --- | --- | --- | --- | --- | --- |
| S_NETWORK | V6_BRIER | brier | 92 | -0.003169 | [-0.01824900422635472, 0.01191193679068479] |
| S_NETWORK | V6_BRIER | crps | 92 | 0.000082 | [-0.0003789237230577346, 0.0005426237042575178] |
| S_NETWORK | V6_CRPS | brier | 92 | 0.005830 | [-0.031661319288445046, 0.04332186514930147] |
| S_NETWORK | V6_CRPS | crps | 92 | -0.000230 | [-0.0012462702804242759, 0.0007862460855903527] |
| S_ROTATION | V6_BRIER | brier | 92 | 0.005255 | [-0.013221457129139165, 0.023731702290005444] |
| S_ROTATION | V6_BRIER | crps | 92 | 0.000027 | [-0.0005684132312421644, 0.0006225222294227556] |
| S_ROTATION | V6_CRPS | brier | 92 | 0.014254 | [-0.025383064482129295, 0.053890922939521926] |
| S_ROTATION | V6_CRPS | crps | 92 | -0.000285 | [-0.0012872248914011786, 0.0007176097135480636] |
| S_STATE_ACCEL | V6_BRIER | brier | 92 | -0.000370 | [-0.02070882531762824, 0.019968392671139677] |
| S_STATE_ACCEL | V6_BRIER | crps | 92 | 0.000217 | [-0.0006680088580989596, 0.0011019978303167235] |
| S_STATE_ACCEL | V6_CRPS | brier | 92 | 0.008629 | [-0.029965610678944453, 0.04722279132898224] |
| S_STATE_ACCEL | V6_CRPS | crps | 92 | -0.000095 | [-0.0010043805926547278, 0.0008146453888387855] |
| T_ROT_DOMESTIC | V6_BRIER | brier | 92 | 0.007658 | [-0.006941624860000021, 0.022257472817540522] |
| T_ROT_DOMESTIC | V6_BRIER | crps | 92 | 0.000141 | [-0.00028826412415899536, 0.0005701724353396215] |
| T_ROT_DOMESTIC | V6_CRPS | brier | 92 | 0.016657 | [-0.021007404552181873, 0.05432086580624873] |
| T_ROT_DOMESTIC | V6_CRPS | crps | 92 | -0.000171 | [-0.0011889794407813773, 0.0008471635759282974] |


The best direction score is an adaptive finding with a simultaneous interval spanning zero. Largest-origin removal and matched regime splits matter because nearby origins share return paths. See `regime-calibration.csv` and the origin-level files. The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history.
