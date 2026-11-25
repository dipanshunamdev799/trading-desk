# NIFTY V17 — Opening surprise and residual returns

Opening surprise equals the official opening return in arithmetic units less the 08:55 forecast mean. Its z-score uses the pre-auction predictive standard deviation with a 0.10 percentage-point lower floor. There were 343 eligible chronological forecast errors. Every one of the 400 matched official opens equaled the first stored 09:15 bar open, so the proxy-open sensitivity preserves the same raw outcome on these dates. Brier differences can still arise from feature-set changes in the proxy model. A realized surprise enters a later decision only. Positive surprises and negative surprises can have different subsequent behavior. The tail subgroup statistics use the fixed ±0.75 surprise thresholds and count consecutive-day episodes separately.

| cutoff | group | n | episodes | closing gap mean | return30 bps | remaining return bps | remaining risk bps | rising30 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | z > 0.75 | 62 | 53 | 0.002027 | 1.400857 | 2.670027 | 55.806182 | 0.548387 |
| 09:25 | z < -0.75 | 53 | 45 | -0.002400 | 4.447020 | 7.710637 | 54.524951 | 0.547170 |
| 09:25 | \|z\| <= 0.75 | 228 | 79 | 0.000298 | -0.153333 | -1.535165 | 48.400156 | 0.513158 |
| 09:25 | z > 0.75, breadth >= 65% | 7 | 7 | 0.001550 | 1.416609 | -20.089393 | 64.074611 | 0.428571 |
| 09:25 | z > 0.75, breadth <= 45% | 38 | 34 | 0.001294 | 0.613324 | 4.684862 | 57.378898 | 0.605263 |
| 09:25 | z < -0.75, breadth <= 35% | 10 | 8 | -0.007083 | 13.415326 | 9.003113 | 73.505779 | 0.700000 |
| 09:25 | z < -0.75, breadth >= 55% | 30 | 27 | -0.001308 | 1.795503 | 6.463237 | 50.710270 | 0.500000 |
| 10:20 | z > 0.75 | 62 | 53 | 0.002027 | 0.001883 | 2.641812 | 48.258502 | 0.532258 |
| 10:20 | z < -0.75 | 53 | 45 | -0.002400 | -0.714926 | 4.042204 | 46.749812 | 0.528302 |
| 10:20 | \|z\| <= 0.75 | 228 | 79 | 0.000298 | -0.798803 | -2.619565 | 41.964454 | 0.473684 |
| 10:20 | z > 0.75, breadth >= 65% | 10 | 9 | 0.003058 | -1.168430 | 13.349159 | 50.927999 | 0.500000 |
| 10:20 | z > 0.75, breadth <= 45% | 39 | 39 | 0.002878 | 1.075567 | 1.821165 | 49.719445 | 0.615385 |
| 10:20 | z < -0.75, breadth <= 35% | 10 | 10 | -0.006282 | 2.978104 | 5.199462 | 57.204719 | 0.500000 |
| 10:20 | z < -0.75, breadth >= 55% | 27 | 25 | -0.000767 | -2.874151 | 4.809931 | 45.369656 | 0.444444 |

The ordinary gap is already included in the cash/native parent and the gap-size-only comparison. All incremental measures below compare identical eligible dates and targets. The return for a cutoff starts at a later independent event, and original residual endpoints end on the fixed original reference’s session count. Positive gains favor the candidate.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | next_session | surprise_direct | native_control | brier | 247 | 125 | 0.260124 | 0.257257 | -0.002867 | -0.007081 | 0.001347 |
| 09:25 | next_session | surprise_direct | native_control | crps | 247 | 125 | 0.005094 | 0.005066 | -0.000028 | -0.000066 | 9.72e-06 |
| 09:25 | next_session | surprise_residual | frozen_parent_residual_history | brier | 247 | 125 | 0.259099 | 0.256481 | -0.002618 | -0.006086 | 0.000851 |
| 09:25 | next_session | surprise_residual | frozen_parent_residual_history | crps | 247 | 125 | 0.005220 | 0.005183 | -0.000038 | -0.000073 | -1.78e-06 |
| 09:25 | r15 | surprise_direct | native_control | brier | 248 | 248 | 0.252977 | 0.253106 | 0.000130 | -0.005917 | 0.006177 |
| 09:25 | r15 | surprise_direct | native_control | crps | 248 | 248 | 0.000951 | 0.000955 | 4.16e-06 | -0.000015 | 0.000024 |
| 09:25 | r15 | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.251096 | 0.251603 | 0.000507 | -0.005522 | 0.006537 |
| 09:25 | r15 | surprise_residual | frozen_parent_residual_history | crps | 248 | 248 | 0.000962 | 0.000965 | 3.05e-06 | -0.000013 | 0.000019 |
| 09:25 | r30 | surprise_direct | native_control | brier | 248 | 248 | 0.251143 | 0.247852 | -0.003291 | -0.009367 | 0.002785 |
| 09:25 | r30 | surprise_direct | native_control | crps | 248 | 248 | 0.001277 | 0.001268 | -8.77e-06 | -0.000028 | 0.000011 |
| 09:25 | r30 | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.250299 | 0.247738 | -0.002562 | -0.007601 | 0.002478 |
| 09:25 | r30 | surprise_residual | frozen_parent_residual_history | crps | 248 | 248 | 0.001286 | 0.001280 | -6.40e-06 | -0.000019 | 6.63e-06 |
| 09:25 | r30 | proxy_open_surprise | frozen_parent_residual_history | brier | 248 | 248 | 0.247123 | 0.247738 | 0.000614 | -0.003635 | 0.004864 |
| 09:25 | r30 | proxy_open_surprise | frozen_parent_residual_history | crps | 248 | 248 | 0.001276 | 0.001280 | 3.24e-06 | -0.000018 | 0.000024 |
| 09:25 | r30 | participation_term | frozen_parent_residual_history | brier | 248 | 248 | 0.249197 | 0.247738 | -0.001459 | -0.008268 | 0.005351 |
| 09:25 | r30 | participation_term | frozen_parent_residual_history | crps | 248 | 248 | 0.001282 | 0.001280 | -2.89e-06 | -0.000021 | 0.000015 |
| 09:25 | regular_residual | surprise_direct | native_control | brier | 248 | 248 | 0.253922 | 0.249301 | -0.004622 | -0.011327 | 0.002083 |
| 09:25 | regular_residual | surprise_direct | native_control | crps | 248 | 248 | 0.003494 | 0.003472 | -0.000022 | -0.000074 | 0.000030 |
| 09:25 | regular_residual | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.252806 | 0.248170 | -0.004636 | -0.009282 | 0.000010 |
| 09:25 | regular_residual | surprise_residual | frozen_parent_residual_history | crps | 248 | 248 | 0.003534 | 0.003517 | -0.000017 | -0.000050 | 0.000016 |
| 09:25 | regular_residual | proxy_open_surprise | frozen_parent_residual_history | brier | 248 | 248 | 0.249597 | 0.248170 | -0.001427 | -0.004178 | 0.001323 |
| 09:25 | regular_residual | proxy_open_surprise | frozen_parent_residual_history | crps | 248 | 248 | 0.003518 | 0.003517 | -9.57e-07 | -0.000027 | 0.000025 |
| 09:25 | regular_residual | participation_term | frozen_parent_residual_history | brier | 248 | 248 | 0.251144 | 0.248170 | -0.002974 | -0.007115 | 0.001168 |
| 09:25 | regular_residual | participation_term | frozen_parent_residual_history | crps | 248 | 248 | 0.003526 | 0.003517 | -9.14e-06 | -0.000040 | 0.000021 |
| 09:25 | remaining_21 | surprise_direct | native_control | brier | 230 | 12 | 0.303579 | 0.306834 | 0.003255 | -0.004443 | 0.010954 |
| 09:25 | remaining_21 | surprise_direct | native_control | crps | 230 | 12 | 0.029036 | 0.028965 | -0.000071 | -0.000853 | 0.000712 |
| 09:25 | remaining_21 | surprise_residual | frozen_parent_residual_history | brier | 230 | 12 | 0.302861 | 0.292340 | -0.010521 | -0.049414 | 0.028371 |
| 09:25 | remaining_21 | surprise_residual | frozen_parent_residual_history | crps | 230 | 12 | 0.031902 | 0.030172 | -0.001730 | -0.004568 | 0.001108 |
| 09:25 | remaining_21 | proxy_open_surprise | frozen_parent_residual_history | brier | 230 | 12 | 0.300776 | 0.292340 | -0.008436 | -0.052877 | 0.036004 |
| 09:25 | remaining_21 | proxy_open_surprise | frozen_parent_residual_history | crps | 230 | 12 | 0.031119 | 0.030172 | -0.000947 | -0.003147 | 0.001253 |
| 09:25 | remaining_21 | participation_term | frozen_parent_residual_history | brier | 230 | 12 | 0.304143 | 0.292340 | -0.011804 | -0.052048 | 0.028440 |
| 09:25 | remaining_21 | participation_term | frozen_parent_residual_history | crps | 230 | 12 | 0.031984 | 0.030172 | -0.001812 | -0.004646 | 0.001021 |
| 09:25 | remaining_5 | surprise_direct | native_control | brier | 244 | 51 | 0.242629 | 0.242906 | 0.000277 | -0.005040 | 0.005593 |
| 09:25 | remaining_5 | surprise_direct | native_control | crps | 244 | 51 | 0.010632 | 0.010632 | 4.97e-07 | -0.000196 | 0.000197 |
| 09:25 | remaining_5 | surprise_residual | frozen_parent_residual_history | brier | 244 | 51 | 0.241120 | 0.240992 | -0.000128 | -0.008084 | 0.007828 |
| 09:25 | remaining_5 | surprise_residual | frozen_parent_residual_history | crps | 244 | 51 | 0.010904 | 0.010904 | -1.75e-07 | -0.000387 | 0.000387 |
| 09:25 | remaining_5 | proxy_open_surprise | frozen_parent_residual_history | brier | 244 | 51 | 0.242928 | 0.240992 | -0.001937 | -0.009206 | 0.005333 |
| 09:25 | remaining_5 | proxy_open_surprise | frozen_parent_residual_history | crps | 244 | 51 | 0.010854 | 0.010904 | 0.000050 | -0.000235 | 0.000335 |
| 09:25 | remaining_5 | participation_term | frozen_parent_residual_history | brier | 244 | 51 | 0.242594 | 0.240992 | -0.001602 | -0.009146 | 0.005942 |
| 09:25 | remaining_5 | participation_term | frozen_parent_residual_history | crps | 244 | 51 | 0.010953 | 0.010904 | -0.000049 | -0.000387 | 0.000289 |
| 10:20 | next_session | surprise_direct | native_control | brier | 247 | 125 | 0.258709 | 0.256510 | -0.002198 | -0.006846 | 0.002449 |
| 10:20 | next_session | surprise_direct | native_control | crps | 247 | 125 | 0.005080 | 0.005060 | -0.000020 | -0.000049 | 9.67e-06 |
| 10:20 | next_session | surprise_residual | frozen_parent_residual_history | brier | 247 | 125 | 0.256659 | 0.255435 | -0.001224 | -0.005552 | 0.003103 |
| 10:20 | next_session | surprise_residual | frozen_parent_residual_history | crps | 247 | 125 | 0.005184 | 0.005171 | -0.000013 | -0.000060 | 0.000034 |

[Expected gap ledger](opening-baseline-expectation.csv) · [Observed opening and first bar](observed-open_and_surprise.csv) · [Full return and risk comparisons](postopen-matched-evidence.csv) · [Replayed V16 continuation](reproduced-continuation.csv) · [Original gap-fill timing results](reproduced-survival.csv)
