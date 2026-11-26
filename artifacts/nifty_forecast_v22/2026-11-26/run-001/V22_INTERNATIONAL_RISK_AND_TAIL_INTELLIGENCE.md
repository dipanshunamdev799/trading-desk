# V22 International risk and tail intelligence

The protected point-risk benchmarks reproduced exactly within rounding. Weekly ATM IV obtained 0.037814 MAE, offshore
and domestic features 0.036469 MAE, and the IV/RV transition probability 0.152707 Brier. Monthly GJR obtained 0.033179 MAE and
0.199677 variance QLIKE. Monthly Student EGARCH expansion scored 0.172872 Brier. The original native monthly Student-t GJR
distribution scored 0.015422 range CRPS. Its separately replayed 08:55 GJR path reference scored 0.015488.

The GARCH transfer trial evaluates five causal volatility parameter triplets and averages them using earlier performance.
Date-balanced foreign risk, India-only risk and partially pooled variance forecasts are scored. IV or GJR anchored point
hybrids retain the protected expansion probability unless explicitly recalibrated. The calibrated path arms rescale every
OHLC trajectory consistently, including the heavy-tail monotone mapping. Path ranges, high and low touches, drawdown, tails
and expansion and contraction are all recomputed from those same empirical weights. Expansion and contraction events use
the protected V14 trailing reference, with exact V16 realized-volatility and V20 same-clock range checks.

## Point-risk leaderboard

| horizon | model | n | vol mae | qlike | expand brier | p expand | actual expand |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | GJR | 265 | 0.040318 | 0.359870 | 0.188310 | 0.336164 | 0.328302 |
| 5 | V14_IV_GJR | 265 | 0.037978 | 0.287184 | 0.165100 | 0.349398 | 0.328302 |
| 5 | fixed_iv_rv | 265 | 0.038484 | 0.286114 | 0.152707 | 0.327067 | 0.328302 |
| 5 | offshore_plus_domestic | 265 | 0.036469 | 0.290334 | 0.160327 | 0.340298 | 0.328302 |
| 5 | raw_iv | 265 | 0.037814 | 0.276187 | 0.155657 | 0.356195 | 0.328302 |
| 5 | student_EGARCH | 265 | 0.039960 | 0.327199 | 0.177866 | 0.380665 | 0.328302 |
| 5 | v22_garch_foreign | 265 | 0.042687 | 0.352127 | 0.152707 | 0.327067 | 0.328302 |
| 5 | v22_garch_local | 265 | 0.041768 | 0.344632 | 0.152707 | 0.327067 | 0.328302 |
| 5 | v22_garch_shrunk | 265 | 0.042073 | 0.347038 | 0.152707 | 0.327067 | 0.328302 |
| 5 | v22_iv_gjr_calibrated | 265 | 0.037798 | 0.338328 | 0.161152 | 0.314618 | 0.328302 |
| 5 | v22_iv_gjr_shrink | 265 | 0.036670 | 0.283155 | 0.152707 | 0.327067 | 0.328302 |
| 5 | v22_loco_risk | 265 | 0.043838 | 0.427230 | 0.227804 | 0.246841 | 0.328302 |
| 21 | GJR | 217 | 0.033179 | 0.199677 | 0.198788 | 0.292719 | 0.373272 |
| 21 | V14_IV_GJR | 217 | 0.033780 | 0.247374 | 0.211163 | 0.239138 | 0.373272 |
| 21 | fixed_iv_rv | 217 | 0.040894 | 0.257953 | 0.194367 | 0.225716 | 0.373272 |
| 21 | offshore_plus_domestic | 217 | 0.049953 | 0.484730 | 0.207382 | 0.240543 | 0.373272 |
| 21 | raw_iv | 217 | 0.039406 | 0.267623 | 0.186036 | 0.278692 | 0.373272 |
| 21 | student_EGARCH | 217 | 0.035730 | 0.207684 | 0.172872 | 0.287098 | 0.373272 |
| 21 | v22_garch_foreign | 217 | 0.047018 | 0.362698 | 0.172872 | 0.287098 | 0.373272 |
| 21 | v22_garch_local | 217 | 0.045983 | 0.347212 | 0.172872 | 0.287098 | 0.373272 |
| 21 | v22_garch_shrunk | 217 | 0.046335 | 0.352809 | 0.172872 | 0.287098 | 0.373272 |
| 21 | v22_iv_gjr_calibrated | 217 | 0.036052 | 0.200780 | 0.194595 | 0.386979 | 0.373272 |
| 21 | v22_iv_gjr_shrink | 217 | 0.033902 | 0.206673 | 0.172872 | 0.287098 | 0.373272 |
| 21 | v22_loco_risk | 217 | 0.049369 | 0.457306 | 0.292725 | 0.224654 | 0.373272 |

## Complete risk paths at 08:55

| horizon | track | model | n | risk mae | range crps | drawdown crps | expansion | contraction | range cover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | calibrated_paths | analogue_global_calibrated | 265 | 0.037798 | 0.006441 | 0.006279 | 0.163769 | 0.152477 | 0.773585 |
| 5 | calibrated_paths | analogue_global_heavy_tail | 265 | 0.036469 | 0.006224 | 0.006248 | 0.158893 | 0.152203 | 0.879245 |
| 5 | calibrated_paths | analogue_global_on_IV_GJR | 265 | 0.036469 | 0.006155 | 0.006205 | 0.157521 | 0.145096 | 0.815094 |
| 5 | calibrated_paths | analogue_global_shock_conditioned | 265 | 0.036469 | 0.006182 | 0.006205 | 0.157994 | 0.139460 | 0.826415 |
| 5 | calibrated_paths | analogue_india_on_IV_GJR | 265 | 0.036469 | 0.006159 | 0.006139 | 0.155508 | 0.140539 | 0.864151 |
| 5 | calibrated_paths | analogue_mix_unscaled | 265 | 0.042451 | 0.006671 | 0.006598 | 0.170106 | 0.153582 | 0.769811 |
| 5 | same_clock_parent_paths | asymmetric_specialized | 265 | 0.036793 | 0.005768 | 0.005917 | 0.157989 | 0.131501 | 0.739623 |
| 5 | same_clock_parent_paths | coherent_all | 265 | 0.037318 | 0.005862 | 0.005873 | 0.160950 | 0.128894 | 0.743396 |
| 5 | same_clock_parent_paths | location_specialized | 265 | 0.036803 | 0.005760 | 0.005899 | 0.157837 | 0.131261 | 0.732075 |
| 5 | same_clock_parent_paths | same_clock_GJR | 265 | 0.040097 | 0.006493 | 0.005956 | 0.184671 | 0.148193 | 0.766038 |
| 5 | same_clock_parent_paths | same_clock_IV | 265 | 0.036801 | 0.005768 | 0.005926 | 0.157940 | 0.131133 | 0.735849 |
| 5 | same_clock_parent_paths | scale_specialized | 265 | 0.037325 | 0.005868 | 0.005871 | 0.160432 | 0.128721 | 0.743396 |
| 21 | calibrated_paths | analogue_global_calibrated | 217 | 0.036052 | 0.014701 | 0.014071 | 0.187727 | 0.121249 | 0.797235 |
| 21 | calibrated_paths | analogue_global_heavy_tail | 217 | 0.033179 | 0.014335 | 0.013993 | 0.186646 | 0.121829 | 0.824885 |
| 21 | calibrated_paths | analogue_global_on_IV_GJR | 217 | 0.033179 | 0.014195 | 0.013894 | 0.186368 | 0.115088 | 0.792627 |
| 21 | calibrated_paths | analogue_global_shock_conditioned | 217 | 0.033179 | 0.014263 | 0.013909 | 0.189388 | 0.112109 | 0.797235 |
| 21 | calibrated_paths | analogue_india_on_IV_GJR | 217 | 0.033103 | 0.014409 | 0.013974 | 0.195207 | 0.117691 | 0.861751 |
| 21 | calibrated_paths | analogue_mix_unscaled | 217 | 0.044525 | 0.017151 | 0.015962 | 0.239329 | 0.168196 | 0.612903 |
| 21 | same_clock_parent_paths | asymmetric_specialized | 217 | 0.037397 | 0.015467 | 0.014132 | 0.208439 | 0.145944 | 0.737327 |
| 21 | same_clock_parent_paths | coherent_all | 217 | 0.038408 | 0.016012 | 0.014906 | 0.217803 | 0.176200 | 0.741935 |
| 21 | same_clock_parent_paths | location_specialized | 217 | 0.037172 | 0.015246 | 0.014380 | 0.207248 | 0.146892 | 0.741935 |
| 21 | same_clock_parent_paths | same_clock_GJR | 217 | 0.037244 | 0.015488 | 0.014113 | 0.207983 | 0.146967 | 0.737327 |
| 21 | same_clock_parent_paths | same_clock_IV | 217 | 0.040023 | 0.017179 | 0.015369 | 0.203507 | 0.169197 | 0.585253 |
| 21 | same_clock_parent_paths | scale_specialized | 217 | 0.038346 | 0.016231 | 0.014580 | 0.217634 | 0.178094 | 0.737327 |

Monthly volatility-scaled mixed analogues scored 0.014195 range CRPS, versus 0.014409 for scaled India-only historical paths
and 0.015488 for the matched 08:55 parent. At five sessions, the strongest same-clock IV range model scored 0.005768 versus
0.006155 from the foreign mixture. The almost identical weekly IV-anchored volatility MAE replicates the anchor's scale,
while the monthly gains reflect measured differences in the path distribution. The multi-model adjusted intervals retain
uncertainty. The extreme-episode tail law stays a stress scenario.

| horizon | reference | metric | n | gain | low | high | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | same_clock_IV | range_crps | 265 | -0.000387 | -0.000785 | -0.000043 | -0.000827 | 0.000053 |
| 5 | same_clock_IV | drawdown_crps | 265 | -0.000279 | -0.000509 | -0.000079 | -0.000538 | -0.000021 |
| 5 | same_clock_IV | rv_mae | 265 | 0.000332 | -0.002469 | 0.002906 | -0.002757 | 0.003420 |
| 5 | same_clock_IV | expand_brier | 265 | 0.000418 | -0.021801 | 0.021288 | -0.024669 | 0.025505 |
| 21 | same_clock_GJR | range_crps | 217 | 0.001293 | -0.000259 | 0.003387 | -0.000903 | 0.003489 |
| 21 | same_clock_GJR | drawdown_crps | 217 | 0.000219 | -0.000669 | 0.001349 | -0.001026 | 0.001464 |
| 21 | same_clock_GJR | rv_mae | 217 | 0.004064 | -0.001416 | 0.010563 | -0.002932 | 0.011060 |
| 21 | same_clock_GJR | expand_brier | 217 | 0.021615 | -0.022494 | 0.071021 | -0.035423 | 0.078653 |

## Broker disagreement sensitivity

Reweighting the same matched paths after removing Us, Japan, Uk tests the strongest provider discrepancies. Those primary indices agreed within 0.06 price units on fewer than 10% of the overlapping Upstox daily sample. Surviving paths are rebalanced across weeks and rescaled to the same Indian volatility reference. This sensitivity describes dependence on the affected paths in the final laws. The earlier matching metric and retrieval candidate pool are fixed.

| horizon | model | n | range crps | drawdown crps | effective members |
| --- | --- | --- | --- | --- | --- |
| 5 | all_matched_sources | 265 | 0.006155 | 0.006205 | 43.623241 |
| 5 | drop_low_agreement_sources | 265 | 0.006196 | 0.006190 | 37.822915 |
| 21 | all_matched_sources | 217 | 0.014195 | 0.013894 | 43.896994 |
| 21 | drop_low_agreement_sources | 217 | 0.014260 | 0.013839 | 38.858508 |

[india-risk-and-tail-leaderboard.csv](india-risk-and-tail-leaderboard.csv) · [india-risk-matched-intervals.csv](india-risk-matched-intervals.csv) · [india-protected-native-path-benchmarks.csv](india-protected-native-path-benchmarks.csv) · [india-calibrated-risk-ohlc-laws.npz](india-calibrated-risk-ohlc-laws.npz) · [india-calibrated-risk-path-recipes.csv.gz](india-calibrated-risk-path-recipes.csv.gz) · [india-garch-pooling-receipts.csv.gz](india-garch-pooling-receipts.csv.gz) · [india-risk-analogue-source-sensitivity.csv](india-risk-analogue-source-sensitivity.csv)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
