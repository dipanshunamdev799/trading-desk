# V19 Original Horizon Forecasting

Original forecasts measure price change from the prior NIFTY cash close over 5 or 21 exchange sessions. The exact calendar samples are 173 earlier and 92 later weekly observations, 141 earlier and 76 later monthly observations. Those overlapping samples yield 53 and 11 disjoint windows respectively. V14 and V18 native distributions preserve every empirical atom and weight. Rebuilt releases use separate previous 17:00 and next 08:55 archives. The 09:25 and 10:20 remaining-horizon forecasts get separate files and target definitions.

| horizon | model | n | active | brier | log loss | accuracy | balanced accuracy | crps | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_event_overlay | 265 | 265 | 0.223481 | 0.637789 | 0.641509 | 0.636983 | 0.010318 | 0.818868 | 0.045700 |
| 5 | V14_exact | 265 | 265 | 0.228529 | 0.648943 | 0.626415 | 0.636001 | 0.010457 | 0.826415 | 0.045780 |
| 5 | V14_plus_positions | 265 | 223 | 0.234786 | 0.662234 | 0.581132 | 0.585614 | 0.010547 | 0.818868 | 0.045758 |
| 5 | V18_plus_positions | 265 | 223 | 0.232431 | 0.658622 | 0.607547 | 0.611053 | 0.010467 | 0.781132 | 0.045724 |
| 21 | V14_event_overlay | 217 | 217 | 0.259808 | 0.713467 | 0.456221 | 0.436022 | 0.025409 | 0.677419 | 0.071355 |
| 21 | V14_exact | 217 | 217 | 0.245042 | 0.683095 | 0.511521 | 0.502675 | 0.024989 | 0.668203 | 0.071794 |
| 21 | V14_plus_positions | 217 | 159 | 0.228199 | 0.647076 | 0.543779 | 0.568637 | 0.024010 | 0.672811 | 0.071921 |
| 21 | V18_plus_positions | 217 | 159 | 0.234879 | 0.655320 | 0.506912 | 0.506730 | 0.024537 | 0.682028 | 0.071548 |

| horizon | cutoff | model | n | active | brier | crps | rank corr | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | decomposition_position | 265 | 265 | 0.240270 | 0.010264 | 0.352199 | 0.739623 | 0.041085 |
| 5 | preauction_0855 | component_plus_residual | 265 | 265 | 0.238003 | 0.010309 | 0.290602 | 0.758491 | 0.041019 |
| 5 | preauction_0855 | V18_nonprice_same_clock | 265 | 265 | 0.232338 | 0.010352 | 0.349311 | 0.769811 | 0.041058 |
| 5 | preauction_0855 | participant | 265 | 265 | 0.239255 | 0.010619 | 0.354567 | 0.735849 | 0.041111 |
| 5 | preauction_0855 | structural_position_mixture | 265 | 264 | 0.240213 | 0.010622 | 0.260785 | 0.762264 | 0.041225 |
| 5 | preauction_0855 | delivery + participant | 265 | 264 | 0.240225 | 0.010647 | 0.312951 | 0.735849 | 0.041096 |
| 5 | preauction_0855 | clock_structural | 265 | 265 | 0.238274 | 0.010658 | 0.205777 | 0.766038 | 0.041040 |
| 21 | preauction_0855 | neutral | 217 | 217 | 0.250000 | 0.025543 | 0.141568 | 0.691244 | 0.078299 |
| 21 | preauction_0855 | historical | 217 | 217 | 0.294519 | 0.026743 | -0.423964 | 0.682028 | 0.090738 |
| 21 | preauction_0855 | participant | 217 | 217 | 0.285350 | 0.027800 | 0.079265 | 0.654378 | 0.089951 |
| 21 | preauction_0855 | participant_delay1 | 217 | 217 | 0.290813 | 0.027905 | 0.069855 | 0.654378 | 0.089936 |
| 21 | preauction_0855 | delivery + participant | 217 | 216 | 0.287643 | 0.027917 | 0.087140 | 0.649770 | 0.089912 |
| 21 | preauction_0855 | participant + transactions | 217 | 217 | 0.287704 | 0.027955 | 0.067209 | 0.649770 | 0.089940 |
| 21 | preauction_0855 | delivery + participant + transactions | 217 | 216 | 0.290132 | 0.028048 | 0.074274 | 0.645161 | 0.089903 |

| horizon | model | cohort | metric | n | disjoint | gain |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_plus_positions | early | brier | 173 | 35 | -0.006904 |
| 5 | V14_plus_positions | early | crps | 173 | 35 | -0.000029 |
| 5 | V14_plus_positions | later | brier | 92 | 19 | -0.005040 |
| 5 | V14_plus_positions | later | crps | 92 | 19 | -0.000204 |
| 5 | V18_plus_positions | early | brier | 173 | 35 | -0.008329 |
| 5 | V18_plus_positions | early | crps | 173 | 35 | -0.000094 |
| 5 | V18_plus_positions | later | brier | 92 | 19 | -0.010118 |
| 5 | V18_plus_positions | later | crps | 92 | 19 | -0.000253 |
| 21 | V14_plus_positions | early | brier | 141 | 7 | 0.026437 |
| 21 | V14_plus_positions | early | crps | 141 | 7 | 0.001301 |
| 21 | V14_plus_positions | later | brier | 76 | 4 | -0.000954 |
| 21 | V14_plus_positions | later | crps | 76 | 4 | 0.000382 |
| 21 | V18_plus_positions | early | brier | 141 | 7 | 0.033814 |
| 21 | V18_plus_positions | early | crps | 141 | 7 | 0.001275 |
| 21 | V18_plus_positions | later | brier | 76 | 4 | 0.008445 |
| 21 | V18_plus_positions | later | crps | 76 | 4 | 0.000123 |

The direct models compare price, turnover, positioning and residuals. The structural overlays revise the center with shrinkage on matured labels. Location-scale allows a constrained scale and skew change. The fixed mixture interleaves atoms from the original law and corrected law, with no hindsight mixture selection. The decomposed parent uses the archived V17 same-clock law. Signed log shifts are applied coherently to weighted native laws, and unavailable training stays on each archived parent. Protected joint forecasts enforce a common distribution for OHLC-dependent risks.

[endpoint-config.json](endpoint-config.json) · [endpoint-cases.csv.gz](endpoint-cases.csv.gz) · [endpoint-laws.npz](endpoint-laws.npz) · [native-residual-cases.csv.gz](native-residual-cases.csv.gz) · [native-residual-laws.npz](native-residual-laws.npz) · [postopen-cases.csv.gz](postopen-cases.csv.gz) · [postopen-endpoint-laws.npz](postopen-endpoint-laws.npz) · [v18-native-exact-replay.csv](v18-native-exact-replay.csv)
