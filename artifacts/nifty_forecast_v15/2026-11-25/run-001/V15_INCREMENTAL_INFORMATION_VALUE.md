# V15 incremental information by block

The information ladder begins with the immutable earlier law (A), the price-anchored shortened forecast using issue IV (B), raw IV revised at the same clock (C), a domestic risk and location fit using breadth and rotation (D), and the complete eligible domestic, derivatives, foreign and liquidity model (E). A and B differ in the generator as well as elapsed time and known price movement. The exact lognormal decomposition holds the law and issue volatility constant to isolate those two mechanical effects. The other tests use equal decisions, current reference prices, remaining horizons and path draws. A second addition order fits derivatives first, then the full candidate. Within-model stale domestic, stale surface and stale foreign comparisons isolate the role of the newest available block. Randomized training blocks, five-session delays and delay-plus-noise inputs preserve active parent specifications. Model fit location and scale columns can correlate across blocks.

## Post-issue matched-window gains

| horizon | reference | candidate | attribution | metric | n | gain | early gain | later gain | family low10 | family high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | domestic | full | all eligible inputs | brier | 265 | -0.001542 | -0.000113 | -0.004228 | -0.010939 | 0.007855 |
| 5 | domestic | full | all eligible inputs | range_crps | 265 | -0.000071 | -0.000081 | -0.000051 | -0.000179 | 0.000038 |
| 5 | full_permuted | full | block-permuted fit control | brier | 265 | 0.000717 | 0.001912 | -0.001530 | -0.011012 | 0.012447 |
| 5 | full_permuted | full | block-permuted fit control | range_crps | 265 | -0.000052 | -0.000055 | -0.000046 | -0.000149 | 0.000046 |
| 5 | full_delayed | full | delayed control | brier | 265 | -0.000713 | 0.000983 | -0.003903 | -0.010695 | 0.009269 |
| 5 | full_delayed | full | delayed control | range_crps | 265 | -0.000021 | -0.000041 | 0.000016 | -0.000125 | 0.000082 |
| 5 | full_noise | full | delayed plus noise control | brier | 265 | 0.000184 | 0.001858 | -0.002963 | -0.010404 | 0.010772 |
| 5 | full_noise | full | delayed plus noise control | range_crps | 265 | -0.000022 | -0.000028 | -0.000011 | -0.000136 | 0.000092 |
| 5 | iv_restart | domestic | domestic addition | brier | 265 | 0.002484 | -0.000015 | 0.007182 | -0.008195 | 0.013162 |
| 5 | iv_restart | domestic | domestic addition | range_crps | 265 | -0.000151 | -0.000143 | -0.000167 | -0.000340 | 0.000037 |
| 5 | domestic_stale | domestic | fresh domestic | brier | 265 | 0.001444 | 0.003117 | -0.001701 | -0.005056 | 0.007945 |
| 5 | domestic_stale | domestic | fresh domestic | range_crps | 265 | -0.000001 | 0.000011 | -0.000022 | -0.000057 | 0.000056 |
| 5 | full_stale_global | full | fresh foreign | brier | 265 | 0.000910 | 0.002376 | -0.001847 | -0.004614 | 0.006434 |
| 5 | full_stale_global | full | fresh foreign | range_crps | 265 | -0.000006 | -0.000039 | 0.000055 | -0.000086 | 0.000074 |
| 5 | full_stale_surface | full | fresh surface | brier | 265 | -0.000727 | -0.001109 | -0.000009 | -0.004700 | 0.003247 |
| 5 | full_stale_surface | full | fresh surface | range_crps | 265 | -0.000008 | -0.000001 | -0.000023 | -0.000063 | 0.000046 |
| 5 | iv_restart | full | fully revised baseline | brier | 265 | 0.000942 | -0.000128 | 0.002954 | -0.013002 | 0.014885 |
| 5 | iv_restart | full | fully revised baseline | range_crps | 265 | -0.000222 | -0.000224 | -0.000218 | -0.000435 | -0.000009 |
| 5 | derivatives_first | full | other blocks after surface | brier | 265 | 0.005122 | 0.007890 | -0.000084 | -0.006001 | 0.016244 |
| 5 | derivatives_first | full | other blocks after surface | range_crps | 265 | -0.000004 | -0.000022 | 0.000030 | -0.000145 | 0.000138 |
| 5 | frozen | price_only | price and elapsed time | brier | 265 | 0.090429 | 0.077292 | 0.115131 | 0.068498 | 0.112360 |
| 5 | frozen | price_only | price and elapsed time | range_crps | 265 | 0.001687 | 0.001550 | 0.001945 | 0.000988 | 0.002387 |
| 5 | price_only | iv_restart | revised raw risk | brier | 265 | -0.000476 | -0.000417 | -0.000585 | -0.002999 | 0.002048 |
| 5 | price_only | iv_restart | revised raw risk | range_crps | 265 | -0.000010 | 0.000050 | -0.000122 | -0.000240 | 0.000220 |
| 5 | iv_restart | gjr_restart | state risk | brier | 265 | -0.003287 | -0.005197 | 0.000306 | -0.008689 | 0.002115 |
| 5 | iv_restart | gjr_restart | state risk | range_crps | 265 | -0.000292 | -0.000243 | -0.000386 | -0.000784 | 0.000199 |
| 5 | iv_restart | derivatives_first | surface first | brier | 265 | -0.004180 | -0.008019 | 0.003038 | -0.012489 | 0.004129 |
| 5 | iv_restart | derivatives_first | surface first | range_crps | 265 | -0.000218 | -0.000202 | -0.000248 | -0.000475 | 0.000038 |
| 21 | domestic | full | all eligible inputs | brier | 217 | -0.003929 | -0.006529 | 0.000895 | -0.013867 | 0.006010 |
| 21 | domestic | full | all eligible inputs | range_crps | 217 | 0.000124 | 0.000190 | 0.000002 | -0.000201 | 0.000450 |
| 21 | full_permuted | full | block-permuted fit control | brier | 217 | -0.002171 | -0.006134 | 0.005183 | -0.013481 | 0.009140 |
| 21 | full_permuted | full | block-permuted fit control | range_crps | 217 | 0.000047 | 0.000040 | 0.000060 | -0.000308 | 0.000403 |
| 21 | full_delayed | full | delayed control | brier | 217 | -0.001452 | -0.005869 | 0.006742 | -0.009817 | 0.006912 |
| 21 | full_delayed | full | delayed control | range_crps | 217 | 0.000009 | -0.000032 | 0.000085 | -0.000157 | 0.000175 |
| 21 | full_noise | full | delayed plus noise control | brier | 217 | -0.000743 | -0.005265 | 0.007648 | -0.009204 | 0.007718 |
| 21 | full_noise | full | delayed plus noise control | range_crps | 217 | 0.000005 | -0.000026 | 0.000062 | -0.000168 | 0.000177 |
| 21 | iv_restart | domestic | domestic addition | brier | 217 | -0.007694 | -0.015375 | 0.006554 | -0.033823 | 0.018434 |
| 21 | iv_restart | domestic | domestic addition | range_crps | 217 | -0.000896 | -0.001456 | 0.000142 | -0.001824 | 0.000031 |
| 21 | domestic_stale | domestic | fresh domestic | brier | 217 | 0.002882 | 0.000513 | 0.007276 | -0.005431 | 0.011195 |
| 21 | domestic_stale | domestic | fresh domestic | range_crps | 217 | 0.000032 | -0.000043 | 0.000172 | -0.000105 | 0.000169 |
| 21 | full_stale_global | full | fresh foreign | brier | 217 | 0.000834 | 0.000403 | 0.001635 | -0.005890 | 0.007558 |
| 21 | full_stale_global | full | fresh foreign | range_crps | 217 | -0.000014 | -0.000086 | 0.000118 | -0.000218 | 0.000189 |
| 21 | full_stale_surface | full | fresh surface | brier | 217 | -0.002313 | -0.003420 | -0.000257 | -0.005353 | 0.000728 |
| 21 | full_stale_surface | full | fresh surface | range_crps | 217 | -0.000043 | -0.000049 | -0.000032 | -0.000163 | 0.000077 |
| 21 | iv_restart | full | fully revised baseline | brier | 217 | -0.011623 | -0.021903 | 0.007449 | -0.038365 | 0.015119 |
| 21 | iv_restart | full | fully revised baseline | range_crps | 217 | -0.000772 | -0.001266 | 0.000144 | -0.001742 | 0.000198 |
| 21 | derivatives_first | full | other blocks after surface | brier | 217 | 0.002222 | 0.000520 | 0.005379 | -0.007655 | 0.012098 |
| 21 | derivatives_first | full | other blocks after surface | range_crps | 217 | -0.000100 | -0.000221 | 0.000125 | -0.000412 | 0.000212 |
| 21 | frozen | price_only | price and elapsed time | brier | 217 | 0.086346 | 0.068917 | 0.118681 | 0.052091 | 0.120601 |
| 21 | frozen | price_only | price and elapsed time | range_crps | 217 | 0.004087 | 0.004586 | 0.003162 | 0.001231 | 0.006944 |
| 21 | price_only | iv_restart | revised raw risk | brier | 217 | 0.000399 | 0.000459 | 0.000288 | -0.005237 | 0.006036 |
| 21 | price_only | iv_restart | revised raw risk | range_crps | 217 | 0.001315 | 0.001783 | 0.000448 | 0.000132 | 0.002499 |
| 21 | iv_restart | gjr_restart | state risk | brier | 217 | -0.003030 | -0.005414 | 0.001394 | -0.009683 | 0.003623 |
| 21 | iv_restart | gjr_restart | state risk | range_crps | 217 | -0.000141 | 0.000319 | -0.000995 | -0.001614 | 0.001333 |
| 21 | iv_restart | derivatives_first | surface first | brier | 217 | -0.013845 | -0.022424 | 0.002071 | -0.039139 | 0.011449 |
| 21 | iv_restart | derivatives_first | surface first | range_crps | 217 | -0.000672 | -0.001045 | 0.000020 | -0.001543 | 0.000198 |

## Additional loss comparisons

| horizon | candidate | attribution | metric | n | gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | iv_restart | revised raw risk | vol_mae | 265 | 0.000603 | -0.001285 | 0.002491 |
| 5 | iv_restart | revised raw risk | joint_energy | 265 | 0.000707 | -0.007800 | 0.009214 |
| 5 | domestic | fresh domestic | vol_mae | 265 | 0.000131 | -0.000250 | 0.000511 |
| 5 | domestic | fresh domestic | joint_energy | 265 | -0.001921 | -0.012896 | 0.009054 |
| 5 | full | all eligible inputs | vol_mae | 265 | -0.000257 | -0.000995 | 0.000480 |
| 5 | full | all eligible inputs | joint_energy | 265 | -0.004091 | -0.018186 | 0.010004 |
| 5 | full | fresh surface | vol_mae | 265 | -0.000050 | -0.000339 | 0.000238 |
| 5 | full | fresh surface | joint_energy | 265 | -0.004787 | -0.010620 | 0.001047 |
| 5 | full | fresh foreign | vol_mae | 265 | -0.000109 | -0.000557 | 0.000339 |
| 5 | full | fresh foreign | joint_energy | 265 | 0.002420 | -0.010104 | 0.014945 |
| 21 | iv_restart | revised raw risk | vol_mae | 217 | 0.004741 | 0.000924 | 0.008558 |
| 21 | iv_restart | revised raw risk | joint_energy | 217 | 0.029483 | -0.003265 | 0.062230 |
| 21 | domestic | fresh domestic | vol_mae | 217 | -0.000123 | -0.000637 | 0.000391 |
| 21 | domestic | fresh domestic | joint_energy | 217 | 0.002278 | -0.011934 | 0.016489 |
| 21 | full | all eligible inputs | vol_mae | 217 | 0.000387 | -0.001023 | 0.001796 |
| 21 | full | all eligible inputs | joint_energy | 217 | -0.003906 | -0.021790 | 0.013978 |
| 21 | full | fresh surface | vol_mae | 217 | 0.000020 | -0.000372 | 0.000413 |
| 21 | full | fresh surface | joint_energy | 217 | -0.003740 | -0.012938 | 0.005459 |
| 21 | full | fresh foreign | vol_mae | 217 | -0.000001 | -0.000344 | 0.000342 |
| 21 | full | fresh foreign | joint_energy | 217 | 0.003307 | -0.009323 | 0.015937 |

## Barrier calibration on common surviving risk sets

| horizon | candidate | metric | n | origins | candidate loss | reference loss | average episode gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | refit | brier | 15,430 | 265 | 0.079543 | 0.078471 | -0.001237 | -0.003742 | 0.001268 |
| 5 | refit | integrated_brier | 15,430 | 265 | 0.061399 | 0.060591 | -0.000933 | -0.002211 | 0.000345 |
| 5 | vol_state | brier | 15,430 | 265 | 0.078419 | 0.078471 | -0.000061 | -0.001341 | 0.001219 |
| 5 | vol_state | integrated_brier | 15,430 | 265 | 0.060462 | 0.060591 | 0.000051 | -0.000850 | 0.000953 |
| 5 | analogue | brier | 15,430 | 265 | 0.079848 | 0.078471 | -0.001639 | -0.006023 | 0.002745 |
| 5 | analogue | integrated_brier | 15,430 | 265 | 0.061399 | 0.060591 | -0.000998 | -0.003838 | 0.001843 |
| 5 | particle | brier | 15,430 | 265 | 0.078531 | 0.078471 | -0.000287 | -0.002260 | 0.001685 |
| 5 | particle | integrated_brier | 15,430 | 265 | 0.060450 | 0.060591 | -0.000043 | -0.001288 | 0.001202 |
| 5 | hybrid | brier | 15,430 | 265 | 0.078278 | 0.078471 | 0.000058 | -0.001395 | 0.001511 |
| 5 | hybrid | integrated_brier | 15,430 | 265 | 0.060308 | 0.060591 | 0.000181 | -0.000772 | 0.001135 |
| 5 | shock_persistence | brier | 15,430 | 265 | 0.078592 | 0.078471 | -0.000136 | -0.000555 | 0.000282 |
| 5 | shock_persistence | integrated_brier | 15,430 | 265 | 0.060645 | 0.060591 | -0.000050 | -0.000295 | 0.000195 |
| 21 | refit | brier | 54,600 | 217 | 0.114713 | 0.108726 | -0.007080 | -0.022324 | 0.008165 |
| 21 | refit | integrated_brier | 54,600 | 217 | 0.075353 | 0.072306 | -0.003620 | -0.010854 | 0.003614 |
| 21 | vol_state | brier | 54,600 | 217 | 0.108246 | 0.108726 | 0.000016 | -0.004306 | 0.004337 |
| 21 | vol_state | integrated_brier | 54,600 | 217 | 0.072209 | 0.072306 | -0.000134 | -0.002162 | 0.001895 |
| 21 | analogue | brier | 54,600 | 217 | 0.116816 | 0.108726 | -0.008952 | -0.022238 | 0.004335 |
| 21 | analogue | integrated_brier | 54,600 | 217 | 0.076117 | 0.072306 | -0.004309 | -0.010047 | 0.001428 |
| 21 | particle | brier | 54,600 | 217 | 0.111679 | 0.108726 | -0.004046 | -0.013228 | 0.005136 |
| 21 | particle | integrated_brier | 54,600 | 217 | 0.074542 | 0.072306 | -0.002885 | -0.007493 | 0.001722 |
| 21 | hybrid | brier | 54,600 | 217 | 0.109147 | 0.108726 | -0.001061 | -0.006744 | 0.004622 |
| 21 | hybrid | integrated_brier | 54,600 | 217 | 0.072806 | 0.072306 | -0.000846 | -0.003559 | 0.001866 |
| 21 | shock_persistence | brier | 54,600 | 217 | 0.109270 | 0.108726 | -0.000568 | -0.002396 | 0.001261 |
| 21 | shock_persistence | integrated_brier | 54,600 | 217 | 0.072494 | 0.072306 | -0.000183 | -0.000949 | 0.000584 |

The fully refitted nesting uses absolute levels. The full sequential design gives feature groups matched level and revision terms. Their train-only risk-normalized location and realized-scale responses use up to 180 matured observations. Through-time differences in score are reported per original window, so repeated updates receive no added outcome weight. Raw volatility levels, dispersion calibrations and earlier-market timing results have dedicated controls and are tracked as separate objectives.

[Matching and ablations](matched-window-evidence.csv) [Per-update fitted parameters](fitted-update-models.ndjson.gz) [Overseas timing evidence](V15_INFORMATION_TIMING_AND_SESSIONS.md) [Surviving barrier rows](sequential-passage.csv.gz)
