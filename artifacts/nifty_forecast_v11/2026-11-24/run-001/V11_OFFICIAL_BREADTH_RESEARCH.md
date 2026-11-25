# V11 Official Breadth Research

V11 parsed **466** official NSE daily files containing **171** distinct index labels. The inventory covers equal-weight, cap-weight, broad, sector, quality, momentum, value, dividend, low-volatility and thematic families. It admits 22 documented close series and inventories the others outside the fitted panel. Launch or dated publication evidence supports admissibility. The two V10 equal-weight pairs match the frozen prices exactly. NIFTY 100 Equal Weight and Top 15 provide alternative documented breadth and leadership proxies. Top 10, NIFTY500 Quality 50 and NIFTY500 Low Volatility 50 carry a conservative July 2025 floor. Archive values enter the main experiments with a one-observed-session lag. An independent same-close diagnostic and documented launch windows reduce false backfill assumptions. Exact historical distribution timestamps and later data corrections remain unverified. [NSE index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf) · [NIFTY500 Equal Weight launch](https://www.niftyindices.com/Press_Release/ind_prs31052024.pdf) · [Top 15 launch](https://www.niftyindices.com/Factsheet/Factsheet_NiftyTop15EqualWeight.pdf) · [2025 benchmark publications](https://www.niftyindices.com/Nifty_Passive_Insights/Nifty%20Passive%20Insights%20Quarterly%20Update%20-%20April%2025%20to%20June%2025.pdf).

Five- and 21-session changes in official log-price relatives define the core breadth measures. We compare individual equal-weight and cap-weight returns, a separate NIFTY100 pair, breadth acceleration and persistence, interaction with bank rotation and prior risk, five-session lag, circular shifts of 21 or 42 dates, and block permutations. Explicit momentum removal and training-only residualization control common momentum, size and relative volatility. Index composition and rebalancing can still affect the spreads. Exact V8 and V9 augmentations retain their actual fit partitions and implementation. Weekly improvements in V9 residual rotation and structure coexist with weaker Brier in the cluster-balanced parent. Width, magnitude error, and calibrated probability are separate outcomes.

The combined weekly conditional slices did not show a simple continuation rule. The 140 origins with a positive broad-market spread had a 37.86% subsequent positive rate and −0.349% mean weekly return. The 125 remaining origins had a 51.20% positive rate and +0.385% mean return. The 50 narrow-rise cases had a 44.00% positive rate and +0.054% mean return. The 67 broad-rise cases had a 38.81% positive rate and +0.014% mean return. These descriptive groups overlap in time and have different volatility and sector states.

| horizon | cohort | model | baseline | metric | n | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | early | B_CAP_ONLY | B_ROT | brier | 173 | 0.298536 | 0.296554 | -0.001982 | -0.006954 | 0.002989 |
| 5 | early | B_CAP_ONLY | B_ROT | crps | 173 | 0.013123 | 0.013094 | -0.000029 | -0.000111 | 0.000053 |
| 5 | later | B_CAP_ONLY | B_ROT | brier | 92 | 0.165314 | 0.165528 | 0.000215 | -0.000543 | 0.000972 |
| 5 | later | B_CAP_ONLY | B_ROT | crps | 92 | 0.010119 | 0.010118 | -0.000000 | -0.000009 | 0.000009 |
| 5 | early | B_CHANGE | B_ROT | brier | 173 | 0.294583 | 0.296554 | 0.001971 | -0.016221 | 0.020162 |
| 5 | early | B_CHANGE | B_ROT | crps | 173 | 0.012942 | 0.013094 | 0.000152 | -0.000374 | 0.000678 |
| 5 | later | B_CHANGE | B_ROT | brier | 92 | 0.156795 | 0.165528 | 0.008734 | -0.013633 | 0.031100 |
| 5 | later | B_CHANGE | B_ROT | crps | 92 | 0.009851 | 0.010118 | 0.000268 | -0.000649 | 0.001185 |
| 5 | early | B_EQUAL_ONLY | B_ROT | brier | 173 | 0.297714 | 0.296554 | -0.001161 | -0.006406 | 0.004085 |
| 5 | early | B_EQUAL_ONLY | B_ROT | crps | 173 | 0.013107 | 0.013094 | -0.000013 | -0.000104 | 0.000078 |
| 5 | later | B_EQUAL_ONLY | B_ROT | brier | 92 | 0.165308 | 0.165528 | 0.000220 | -0.002745 | 0.003186 |
| 5 | later | B_EQUAL_ONLY | B_ROT | crps | 92 | 0.010065 | 0.010118 | 0.000053 | -0.000061 | 0.000168 |
| 5 | early | B_EQ_LAG5 | B_ROT | brier | 173 | 0.296178 | 0.296554 | 0.000375 | -0.027979 | 0.028730 |
| 5 | early | B_EQ_LAG5 | B_ROT | crps | 173 | 0.012986 | 0.013094 | 0.000108 | -0.000523 | 0.000738 |
| 5 | later | B_EQ_LAG5 | B_ROT | brier | 92 | 0.171449 | 0.165528 | -0.005921 | -0.020472 | 0.008630 |
| 5 | later | B_EQ_LAG5 | B_ROT | crps | 92 | 0.010207 | 0.010118 | -0.000088 | -0.000358 | 0.000181 |
| 5 | early | B_EQ_MOMO_DROP | B_MOMO_DROP | brier | 173 | 0.290759 | 0.291999 | 0.001240 | -0.023890 | 0.026371 |
| 5 | early | B_EQ_MOMO_DROP | B_MOMO_DROP | crps | 173 | 0.012398 | 0.012429 | 0.000031 | -0.000698 | 0.000760 |
| 5 | later | B_EQ_MOMO_DROP | B_MOMO_DROP | brier | 92 | 0.215583 | 0.261497 | 0.045914 | -0.025055 | 0.116883 |
| 5 | later | B_EQ_MOMO_DROP | B_MOMO_DROP | crps | 92 | 0.011669 | 0.012636 | 0.000968 | -0.001259 | 0.003194 |
| 5 | early | B_EQ_PERM | B_ROT | brier | 173 | 0.301591 | 0.296554 | -0.005037 | -0.021425 | 0.011351 |
| 5 | early | B_EQ_PERM | B_ROT | crps | 173 | 0.013719 | 0.013094 | -0.000625 | -0.001587 | 0.000336 |
| 5 | later | B_EQ_PERM | B_ROT | brier | 92 | 0.171129 | 0.165528 | -0.005600 | -0.022184 | 0.010983 |
| 5 | later | B_EQ_PERM | B_ROT | crps | 92 | 0.010405 | 0.010118 | -0.000286 | -0.000752 | 0.000179 |
| 5 | early | B_EQ_SHIFT21 | B_ROT | brier | 173 | 0.297169 | 0.296554 | -0.000615 | -0.011834 | 0.010603 |
| 5 | early | B_EQ_SHIFT21 | B_ROT | crps | 173 | 0.012961 | 0.013094 | 0.000133 | -0.000263 | 0.000529 |
| 5 | later | B_EQ_SHIFT21 | B_ROT | brier | 92 | 0.167814 | 0.165528 | -0.002285 | -0.012272 | 0.007701 |
| 5 | later | B_EQ_SHIFT21 | B_ROT | crps | 92 | 0.010181 | 0.010118 | -0.000063 | -0.000409 | 0.000283 |
| 5 | early | B_EQ_SHIFT42 | B_ROT | brier | 173 | 0.297818 | 0.296554 | -0.001264 | -0.018602 | 0.016075 |
| 5 | early | B_EQ_SHIFT42 | B_ROT | crps | 173 | 0.013280 | 0.013094 | -0.000187 | -0.000756 | 0.000383 |
| 5 | later | B_EQ_SHIFT42 | B_ROT | brier | 92 | 0.172387 | 0.165528 | -0.006859 | -0.020138 | 0.006420 |
| 5 | later | B_EQ_SHIFT42 | B_ROT | crps | 92 | 0.010399 | 0.010118 | -0.000281 | -0.000862 | 0.000301 |
| 5 | early | B_EQ_SIZE_RISK | B_SIZE_RISK | brier | 173 | 0.298536 | 0.297355 | -0.001181 | -0.024339 | 0.021977 |
| 5 | early | B_EQ_SIZE_RISK | B_SIZE_RISK | crps | 173 | 0.013219 | 0.013050 | -0.000169 | -0.000769 | 0.000431 |
| 5 | later | B_EQ_SIZE_RISK | B_SIZE_RISK | brier | 92 | 0.164146 | 0.167158 | 0.003012 | -0.008627 | 0.014652 |
| 5 | later | B_EQ_SIZE_RISK | B_SIZE_RISK | crps | 92 | 0.010081 | 0.010292 | 0.000212 | -0.000535 | 0.000959 |
| 5 | early | B_FIN_INTERACT | B_ROT_EQ | brier | 173 | 0.303538 | 0.294145 | -0.009393 | -0.044843 | 0.026057 |
| 5 | early | B_FIN_INTERACT | B_ROT_EQ | crps | 173 | 0.013655 | 0.013020 | -0.000635 | -0.001897 | 0.000628 |
| 5 | later | B_FIN_INTERACT | B_ROT_EQ | brier | 92 | 0.163087 | 0.162215 | -0.000872 | -0.012526 | 0.010783 |
| 5 | later | B_FIN_INTERACT | B_ROT_EQ | crps | 92 | 0.009808 | 0.009939 | 0.000132 | -0.000328 | 0.000592 |
| 5 | early | B_NATIVE_EQ | B_NATIVE | brier | 173 | 0.266294 | 0.264194 | -0.002100 | -0.019271 | 0.015070 |
| 5 | early | B_NATIVE_EQ | B_NATIVE | crps | 173 | 0.011581 | 0.011590 | 0.000009 | -0.000355 | 0.000373 |
| 5 | later | B_NATIVE_EQ | B_NATIVE | brier | 92 | 0.180880 | 0.186431 | 0.005550 | -0.007467 | 0.018568 |
| 5 | later | B_NATIVE_EQ | B_NATIVE | crps | 92 | 0.010453 | 0.010645 | 0.000192 | -0.000463 | 0.000846 |
| 5 | early | B_PAIR100 | B_ROT | brier | 173 | 0.296589 | 0.296554 | -0.000036 | -0.005572 | 0.005501 |
| 5 | early | B_PAIR100 | B_ROT | crps | 173 | 0.013089 | 0.013094 | 0.000005 | -0.000117 | 0.000126 |
| 5 | later | B_PAIR100 | B_ROT | brier | 92 | 0.164784 | 0.165528 | 0.000745 | -0.006681 | 0.008171 |
| 5 | later | B_PAIR100 | B_ROT | crps | 92 | 0.010194 | 0.010118 | -0.000075 | -0.000180 | 0.000029 |
| 5 | early | B_PERSIST | B_ROT | brier | 173 | 0.300979 | 0.296554 | -0.004425 | -0.020123 | 0.011273 |
| 5 | early | B_PERSIST | B_ROT | crps | 173 | 0.013160 | 0.013094 | -0.000066 | -0.000661 | 0.000529 |
| 5 | later | B_PERSIST | B_ROT | brier | 92 | 0.164030 | 0.165528 | 0.001499 | -0.007623 | 0.010620 |
| 5 | later | B_PERSIST | B_ROT | crps | 92 | 0.010081 | 0.010118 | 0.000037 | -0.000264 | 0.000339 |
| 5 | early | B_ROT_EQ | B_ROT | brier | 173 | 0.294145 | 0.296554 | 0.002409 | -0.014030 | 0.018848 |
| 5 | early | B_ROT_EQ | B_ROT | crps | 173 | 0.013020 | 0.013094 | 0.000073 | -0.000382 | 0.000528 |
| 5 | later | B_ROT_EQ | B_ROT | brier | 92 | 0.162215 | 0.165528 | 0.003313 | -0.009865 | 0.016491 |
| 5 | later | B_ROT_EQ | B_ROT | crps | 92 | 0.009939 | 0.010118 | 0.000179 | -0.000462 | 0.000821 |
| 5 | early | B_SPARSE_EQ | B_SPARSE | brier | 173 | 0.267798 | 0.261862 | -0.005936 | -0.033939 | 0.022068 |
| 5 | early | B_SPARSE_EQ | B_SPARSE | crps | 173 | 0.013336 | 0.012627 | -0.000709 | -0.002182 | 0.000763 |
| 5 | later | B_SPARSE_EQ | B_SPARSE | brier | 92 | 0.205880 | 0.201841 | -0.004039 | -0.035274 | 0.027196 |
| 5 | later | B_SPARSE_EQ | B_SPARSE | crps | 92 | 0.010480 | 0.010861 | 0.000381 | -0.000927 | 0.001688 |
| 5 | early | B_STUD_EQ | B_STUD | brier | 173 | 0.267789 | 0.265704 | -0.002084 | -0.017948 | 0.013779 |
| 5 | early | B_STUD_EQ | B_STUD | crps | 173 | 0.011375 | 0.011313 | -0.000062 | -0.000523 | 0.000400 |
| 5 | later | B_STUD_EQ | B_STUD | brier | 92 | 0.227287 | 0.234580 | 0.007293 | -0.015466 | 0.030051 |
| 5 | later | B_STUD_EQ | B_STUD | crps | 92 | 0.010874 | 0.011341 | 0.000467 | -0.000907 | 0.001842 |
| 5 | early | B_STYLE | B_STYLE_PARENT | brier | 120 | 0.321956 | 0.323473 | 0.001517 | -0.007230 | 0.010264 |
| 5 | early | B_STYLE | B_STYLE_PARENT | crps | 120 | 0.017097 | 0.017421 | 0.000324 | -0.000275 | 0.000923 |
| 5 | later | B_STYLE | B_STYLE_PARENT | brier | 92 | 0.242655 | 0.232878 | -0.009777 | -0.034311 | 0.014758 |
| 5 | later | B_STYLE | B_STYLE_PARENT | crps | 92 | 0.011545 | 0.011222 | -0.000323 | -0.000879 | 0.000232 |
| 5 | early | B_TEN_EQ | B_TEN | brier | 173 | 0.278863 | 0.285113 | 0.006250 | -0.018717 | 0.031217 |
| 5 | early | B_TEN_EQ | B_TEN | crps | 173 | 0.011880 | 0.012005 | 0.000125 | -0.000636 | 0.000886 |
| 5 | later | B_TEN_EQ | B_TEN | brier | 92 | 0.231291 | 0.256111 | 0.024820 | -0.017922 | 0.067562 |
| 5 | later | B_TEN_EQ | B_TEN | crps | 92 | 0.011623 | 0.012152 | 0.000529 | -0.000878 | 0.001936 |
| 5 | early | P_CLUSTER_EQ | P_CLUSTER | brier | 173 | 0.265919 | 0.260773 | -0.005147 | -0.044050 | 0.033757 |
| 5 | early | P_CLUSTER_EQ | P_CLUSTER | crps | 173 | 0.013115 | 0.012473 | -0.000642 | -0.002418 | 0.001135 |
| 5 | later | P_CLUSTER_EQ | P_CLUSTER | brier | 92 | 0.195168 | 0.190529 | -0.004639 | -0.023495 | 0.014218 |
| 5 | later | P_CLUSTER_EQ | P_CLUSTER | crps | 92 | 0.010203 | 0.010463 | 0.000261 | -0.000862 | 0.001384 |
| 5 | early | P_ROT_EQ | P_ROT | brier | 173 | 0.295325 | 0.298696 | 0.003371 | -0.017644 | 0.024386 |
| 5 | early | P_ROT_EQ | P_ROT | crps | 173 | 0.013136 | 0.013232 | 0.000096 | -0.000462 | 0.000654 |
| 5 | later | P_ROT_EQ | P_ROT | brier | 92 | 0.159388 | 0.164236 | 0.004848 | -0.008246 | 0.017942 |
| 5 | later | P_ROT_EQ | P_ROT | crps | 92 | 0.009786 | 0.009995 | 0.000209 | -0.000513 | 0.000932 |
| 5 | early | P_STRUCTURE_EQ | P_STRUCTURE | brier | 173 | 0.293906 | 0.296317 | 0.002411 | -0.011361 | 0.016183 |
| 5 | early | P_STRUCTURE_EQ | P_STRUCTURE | crps | 173 | 0.013304 | 0.013358 | 0.000055 | -0.000382 | 0.000492 |
| 5 | later | P_STRUCTURE_EQ | P_STRUCTURE | brier | 92 | 0.161804 | 0.165337 | 0.003532 | -0.009675 | 0.016740 |
| 5 | later | P_STRUCTURE_EQ | P_STRUCTURE | crps | 92 | 0.009443 | 0.009608 | 0.000164 | -0.000484 | 0.000813 |
| 5 | later | V8_A_STRUCTURE_CHANGE_EQ | V8_A_STRUCTURE_CHANGE | brier | 92 | 0.163496 | 0.162875 | -0.000621 | -0.012222 | 0.010979 |
| 5 | later | V8_A_STRUCTURE_CHANGE_EQ | V8_A_STRUCTURE_CHANGE | crps | 92 | 0.009294 | 0.009472 | 0.000179 | -0.000395 | 0.000753 |
| 5 | later | V8_R_RESIDUAL_EQ | V8_R_RESIDUAL | brier | 92 | 0.157722 | 0.159504 | 0.001782 | -0.007301 | 0.010865 |
| 5 | later | V8_R_RESIDUAL_EQ | V8_R_RESIDUAL | crps | 92 | 0.009635 | 0.009852 | 0.000217 | -0.000417 | 0.000852 |
| 5 | later | V8_W_STRUCT_EMBARGO_EQ | V8_W_STRUCT_EMBARGO | brier | 92 | 0.161638 | 0.163355 | 0.001718 | -0.006516 | 0.009951 |
| 5 | later | V8_W_STRUCT_EMBARGO_EQ | V8_W_STRUCT_EMBARGO | crps | 92 | 0.009262 | 0.009453 | 0.000191 | -0.000378 | 0.000760 |

[Archive coverage](official-index-inventory.csv) · [Sources and eligibility](official-source-audit.json) · [Narrow vs broad and high/low risk results](breadth-mechanism-slices.csv) · [Matched legacy fit replay](legacy-ledger.json).
