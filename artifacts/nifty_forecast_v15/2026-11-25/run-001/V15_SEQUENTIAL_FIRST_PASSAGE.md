# V15 first passage, survival and opposite barriers

The five fixed upper and lower barrier pairs are 0.5%, 1%, 2%, 3% and 5% from the initial close. The four IV-relative pairs use the issue-time volatility scale multiplied by 0.5, 1.0, 1.5 and 2.0. **2,046,356** eligible model rows score only levels untouched by the decision. **27,170** previously resolved side checkpoints were removed from the risk sets before comparing models. The initial historical laws supply unconditional passage from the current price. Empirical analogue reweighting supplies conditional historical passage and the earlier fixed law can be conditioned on survival through the current step. Order has four outcomes for upper, lower, ambiguous same-candle, and neither. An opening outside a barrier can establish the first hit when both levels occur within a daily candle. The original resolved order is pinned at later checkpoints.

## Touch and integrated time Brier

| horizon | stage | group | model | n | origins | actual | p | brier | integrated brier | passage log loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | updated | opposite after hit | analogue | 2,926 | 263 | 0.144566 | 0.127634 | 0.090972 | 0.070973 | 0.436326 |
| 5 | updated | opposite after hit | frozen | 2,926 | 263 | 0.144566 | 0.207005 | 0.116757 | 0.092177 | 0.523434 |
| 5 | updated | opposite after hit | gjr_restart | 2,926 | 263 | 0.144566 | 0.119504 | 0.093027 | 0.071520 | 0.453949 |
| 5 | updated | opposite after hit | historical | 2,926 | 263 | 0.144566 | 0.128319 | 0.096822 | 0.074745 | 0.497801 |
| 5 | updated | opposite after hit | hybrid | 2,926 | 263 | 0.144566 | 0.125960 | 0.088903 | 0.068958 | 0.428051 |
| 5 | updated | opposite after hit | iv_restart | 2,926 | 263 | 0.144566 | 0.134126 | 0.089017 | 0.069481 | 0.425416 |
| 5 | updated | opposite after hit | particle | 2,926 | 263 | 0.144566 | 0.118540 | 0.088649 | 0.068852 | 0.437458 |
| 5 | updated | opposite after hit | vol_state | 2,926 | 263 | 0.144566 | 0.128339 | 0.089808 | 0.069762 | 0.430620 |
| 21 | updated | opposite after hit | analogue | 14,096 | 217 | 0.180122 | 0.166254 | 0.099498 | 0.067591 | 0.795724 |
| 21 | updated | opposite after hit | frozen | 14,096 | 217 | 0.180122 | 0.215321 | 0.117813 | 0.082862 | 0.822824 |
| 21 | updated | opposite after hit | gjr_restart | 14,096 | 217 | 0.180122 | 0.140775 | 0.094057 | 0.066016 | 0.729432 |
| 21 | updated | opposite after hit | historical | 14,096 | 217 | 0.180122 | 0.151954 | 0.107784 | 0.072712 | 0.845285 |
| 21 | updated | opposite after hit | hybrid | 14,096 | 217 | 0.180122 | 0.147032 | 0.093249 | 0.064978 | 0.721321 |
| 21 | updated | opposite after hit | iv_restart | 14,096 | 217 | 0.180122 | 0.170264 | 0.089826 | 0.062955 | 0.715908 |
| 21 | updated | opposite after hit | particle | 14,096 | 217 | 0.180122 | 0.135187 | 0.097671 | 0.067669 | 0.752819 |
| 21 | updated | opposite after hit | vol_state | 14,096 | 217 | 0.180122 | 0.152553 | 0.091481 | 0.063885 | 0.714961 |
| 5 | issue | fixed thresholds | analogue | 2,650 | 265 | 0.327170 | 0.308295 | 0.147768 | 0.122311 | 0.905453 |
| 5 | issue | fixed thresholds | frozen | 2,650 | 265 | 0.327170 | 0.303694 | 0.145105 | 0.120214 | 0.877932 |
| 5 | issue | fixed thresholds | gjr_restart | 2,650 | 265 | 0.327170 | 0.290895 | 0.148396 | 0.122458 | 0.920260 |
| 5 | issue | fixed thresholds | historical | 2,650 | 265 | 0.327170 | 0.301947 | 0.157444 | 0.130425 | 0.975301 |
| 5 | issue | fixed thresholds | hybrid | 2,650 | 265 | 0.327170 | 0.305519 | 0.144009 | 0.119656 | 0.885373 |
| 5 | issue | fixed thresholds | iv_restart | 2,650 | 265 | 0.327170 | 0.316073 | 0.144592 | 0.120264 | 0.888996 |
| 5 | issue | fixed thresholds | particle | 2,650 | 265 | 0.327170 | 0.303542 | 0.144644 | 0.119940 | 0.881549 |
| 5 | issue | fixed thresholds | vol_state | 2,650 | 265 | 0.327170 | 0.307535 | 0.144889 | 0.120220 | 0.890180 |
| 21 | issue | fixed thresholds | analogue | 2,170 | 217 | 0.564977 | 0.525175 | 0.196720 | 0.166100 | 2.099381 |
| 21 | issue | fixed thresholds | frozen | 2,170 | 217 | 0.564977 | 0.510559 | 0.183636 | 0.160668 | 1.931649 |
| 21 | issue | fixed thresholds | gjr_restart | 2,170 | 217 | 0.564977 | 0.508939 | 0.183861 | 0.161061 | 1.982683 |
| 21 | issue | fixed thresholds | historical | 2,170 | 217 | 0.564977 | 0.512396 | 0.202738 | 0.174555 | 2.192737 |
| 21 | issue | fixed thresholds | hybrid | 2,170 | 217 | 0.564977 | 0.515287 | 0.183449 | 0.159418 | 1.969694 |
| 21 | issue | fixed thresholds | iv_restart | 2,170 | 217 | 0.564977 | 0.549699 | 0.183126 | 0.159269 | 1.986935 |
| 21 | issue | fixed thresholds | particle | 2,170 | 217 | 0.564977 | 0.510671 | 0.184357 | 0.160993 | 1.985488 |
| 21 | issue | fixed thresholds | vol_state | 2,170 | 217 | 0.564977 | 0.521468 | 0.183015 | 0.159466 | 1.959612 |
| 5 | updated | fixed thresholds | analogue | 8,239 | 265 | 0.134361 | 0.121777 | 0.078626 | 0.061384 | 0.384688 |
| 5 | updated | fixed thresholds | frozen | 8,239 | 265 | 0.134361 | 0.120288 | 0.097318 | 0.078114 | 0.457724 |
| 5 | updated | fixed thresholds | gjr_restart | 8,239 | 265 | 0.134361 | 0.111126 | 0.078923 | 0.061419 | 0.389404 |
| 5 | updated | fixed thresholds | historical | 8,239 | 265 | 0.134361 | 0.128620 | 0.082857 | 0.064322 | 0.418586 |
| 5 | updated | fixed thresholds | hybrid | 8,239 | 265 | 0.134361 | 0.118653 | 0.076868 | 0.060072 | 0.373440 |
| 5 | updated | fixed thresholds | iv_restart | 8,239 | 265 | 0.134361 | 0.124482 | 0.076845 | 0.060229 | 0.373024 |
| 5 | updated | fixed thresholds | particle | 8,239 | 265 | 0.134361 | 0.114592 | 0.077334 | 0.060376 | 0.379230 |
| 5 | updated | fixed thresholds | vol_state | 8,239 | 265 | 0.134361 | 0.119982 | 0.076942 | 0.060181 | 0.375005 |
| 21 | updated | fixed thresholds | analogue | 25,342 | 217 | 0.254992 | 0.224942 | 0.136992 | 0.094209 | 1.115617 |
| 21 | updated | fixed thresholds | frozen | 25,342 | 217 | 0.254992 | 0.216208 | 0.159624 | 0.113241 | 1.130120 |
| 21 | updated | fixed thresholds | gjr_restart | 25,342 | 217 | 0.254992 | 0.207540 | 0.129480 | 0.091479 | 1.022411 |
| 21 | updated | fixed thresholds | historical | 25,342 | 217 | 0.254992 | 0.229059 | 0.140952 | 0.097892 | 1.150448 |
| 21 | updated | fixed thresholds | hybrid | 25,342 | 217 | 0.254992 | 0.214559 | 0.128787 | 0.090667 | 1.011975 |
| 21 | updated | fixed thresholds | iv_restart | 25,342 | 217 | 0.254992 | 0.238078 | 0.127207 | 0.089520 | 1.012497 |
| 21 | updated | fixed thresholds | particle | 25,342 | 217 | 0.254992 | 0.203191 | 0.132284 | 0.093063 | 1.043109 |
| 21 | updated | fixed thresholds | vol_state | 25,342 | 217 | 0.254992 | 0.220967 | 0.127313 | 0.089714 | 1.004866 |

## Opposite-barrier timing compared with raw restart

| horizon | candidate | n | origins | candidate loss | reference loss | average episode gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | refit | 2,926 | 263 | 0.070049 | 0.069481 | -0.001962 | -0.006005 | 0.002080 |
| 5 | vol_state | 2,926 | 263 | 0.069762 | 0.069481 | -0.000939 | -0.002776 | 0.000898 |
| 5 | analogue | 2,926 | 263 | 0.070973 | 0.069481 | -0.002828 | -0.007634 | 0.001978 |
| 5 | particle | 2,926 | 263 | 0.068852 | 0.069481 | 0.000132 | -0.003481 | 0.003746 |
| 5 | hybrid | 2,926 | 263 | 0.068958 | 0.069481 | 0.000171 | -0.001507 | 0.001849 |
| 5 | shock_persistence | 2,926 | 263 | 0.069683 | 0.069481 | 0.000123 | -0.000389 | 0.000635 |
| 21 | refit | 14,096 | 217 | 0.065528 | 0.062955 | -0.003249 | -0.008950 | 0.002452 |
| 21 | vol_state | 14,096 | 217 | 0.063885 | 0.062955 | -0.003307 | -0.008241 | 0.001626 |
| 21 | analogue | 14,096 | 217 | 0.067591 | 0.062955 | -0.008044 | -0.015073 | -0.001015 |
| 21 | particle | 14,096 | 217 | 0.067669 | 0.062955 | -0.011185 | -0.023142 | 0.000772 |
| 21 | hybrid | 14,096 | 217 | 0.064978 | 0.062955 | -0.005921 | -0.012975 | 0.001133 |
| 21 | shock_persistence | 14,096 | 217 | 0.063052 | 0.062955 | 0.000939 | -0.000951 | 0.002828 |

## First-order and no additional hit

| horizon | model | order brier n | order brier | no additional brier n | no additional brier |
| --- | --- | --- | --- | --- | --- |
| 5 | analogue | 8,637 | 0.311582 | 11,563 | 0.107980 |
| 5 | gjr_restart | 8,637 | 0.312933 | 11,563 | 0.109874 |
| 5 | hybrid | 8,637 | 0.304890 | 11,563 | 0.104984 |
| 5 | iv_restart | 8,637 | 0.306683 | 11,563 | 0.105554 |
| 21 | analogue | 22,205 | 0.422175 | 36,301 | 0.139011 |
| 21 | gjr_restart | 22,205 | 0.394948 | 36,301 | 0.128836 |
| 21 | hybrid | 22,205 | 0.392717 | 36,301 | 0.127425 |
| 21 | iv_restart | 22,205 | 0.397862 | 36,301 | 0.127604 |

The time target is the first event within the remaining window, with the no-event mass at remaining H + 1. Integrated Brier averages the squared errors of the touch CDF at each remaining session. The event-time log loss uses the probability mass at the correct session or at the censoring category. Expected time given a hit is reported separately, with the corresponding subset count. Because that subset is selected by actual touch and forecast probability, it complements the proper all-at-risk score. Score weights for known ordering and for no additional hit after both levels are visited are excluded. The previous resolved side is handled separately from the probability of touching the opposite side.

[All first-touch rows](sequential-passage.csv.gz) [Matched risk sets and bootstrap](passage-matched-risk-sets.csv) [Timing conditional on a hit](conditional-time-given-touch.csv) [Survival curve example](historical-example-passage.csv) [First order and additional hits](sequential-order.csv.gz)
