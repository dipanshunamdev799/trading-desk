# V14 Forecast Failure Forensics

The casebook separates information visible at the origin from realized path decomposition. It lists the largest probability and distribution losses, unexpected upside and downside, range and volatility underestimates, and missed price levels. Cases repeated across origins may describe the same shock. The October 15 origin was fixed as a diagnostic example before the V14 comparisons. The realized upside case below is decomposed across days, overnight and regular trading without assuming a single causal explanation.

| horizon | up_days | largest_daily_log_move | overnight_log | regular_log | net_log |
| --- | --- | --- | --- | --- | --- |
| 5 | 1 | 0.011174 | 0.005648 | -0.023078 | -0.017429 |
| 21 | 13 | 0.023755 | 0.039914 | 0.055159 | 0.095074 |

| horizon | model | target | predicted_mean | q10 | q90 | q975 | actual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | constant_iv | endpoint_return | 0.000433 | -0.022845 | 0.025069 | 0.038399 | -0.017278 |
| 5 | gjr_iv | endpoint_return | 0.000396 | -0.021652 | 0.023267 | 0.035216 | -0.017278 |
| 5 | jump_diffusion | endpoint_return | -0.000017 | -0.021721 | 0.022101 | 0.033189 | -0.017278 |
| 5 | iv_scaled_blocks | endpoint_return | -0.002969 | -0.023128 | 0.018367 | 0.029589 | -0.017278 |
| 5 | path_mixture | endpoint_return | -0.000667 | -0.023070 | 0.023256 | 0.033768 | -0.017278 |
| 5 | joint_pit | endpoint_return | -0.000619 | -0.021711 | 0.022745 | 0.032724 | -0.017278 |
| 5 | joint_tail_width | endpoint_return | -0.000708 | -0.023070 | 0.023246 | 0.033137 | -0.017278 |
| 5 | constant_iv | range | 0.027370 | 0.017484 | 0.039556 | 0.049815 | 0.034928 |
| 5 | gjr_iv | range | 0.025833 | 0.016337 | 0.037672 | 0.048195 | 0.034928 |
| 5 | jump_diffusion | range | 0.025280 | 0.015768 | 0.036843 | 0.048252 | 0.034928 |
| 5 | iv_scaled_blocks | range | 0.026355 | 0.015964 | 0.039891 | 0.053068 | 0.034928 |
| 5 | path_mixture | range | 0.025958 | 0.016330 | 0.037444 | 0.045820 | 0.034928 |
| 5 | joint_pit | range | 0.025366 | 0.016058 | 0.036558 | 0.045134 | 0.034928 |
| 5 | joint_tail_width | range | 0.025750 | 0.016070 | 0.037499 | 0.046156 | 0.034928 |
| 21 | constant_iv | endpoint_return | 0.001939 | -0.045149 | 0.048321 | 0.076538 | 0.099740 |
| 21 | gjr_iv | endpoint_return | 0.001772 | -0.042510 | 0.044439 | 0.069830 | 0.099740 |
| 21 | jump_diffusion | endpoint_return | 0.001200 | -0.043056 | 0.044053 | 0.068611 | 0.099740 |
| 21 | iv_scaled_blocks | endpoint_return | -0.017815 | -0.078378 | 0.020946 | 0.037309 | 0.099740 |
| 21 | path_mixture | endpoint_return | -0.005665 | -0.057708 | 0.042321 | 0.068611 | 0.099740 |
| 21 | joint_pit | endpoint_return | -0.005369 | -0.054971 | 0.040571 | 0.067949 | 0.099740 |
| 21 | joint_tail_width | endpoint_return | -0.005616 | -0.057661 | 0.042321 | 0.069082 | 0.099740 |
| 21 | constant_iv | range | 0.058599 | 0.038760 | 0.082707 | 0.101372 | 0.132726 |
| 21 | gjr_iv | range | 0.055148 | 0.036370 | 0.078804 | 0.095200 | 0.132726 |
| 21 | jump_diffusion | range | 0.053977 | 0.034999 | 0.076485 | 0.096824 | 0.132726 |
| 21 | iv_scaled_blocks | range | 0.060337 | 0.030821 | 0.113245 | 0.133014 | 0.132726 |
| 21 | path_mixture | range | 0.057401 | 0.036957 | 0.082234 | 0.098169 | 0.132726 |
| 21 | joint_pit | range | 0.055839 | 0.036197 | 0.081952 | 0.098086 | 0.132726 |
| 21 | joint_tail_width | range | 0.057019 | 0.035667 | 0.082594 | 0.099450 | 0.132726 |

| origin | models | under | average_q90 | actual | horizon |
| --- | --- | --- | --- | --- | --- |
| 2026-10-30 | 8 | 8 | 0.038917 | 0.079091 | 5 |
| 2026-10-29 | 8 | 8 | 0.045243 | 0.073018 | 5 |
| 2026-11-02 | 8 | 8 | 0.040366 | 0.070350 | 5 |
| 2026-01-30 | 8 | 8 | 0.044240 | 0.069882 | 5 |
| 2026-01-28 | 8 | 8 | 0.049615 | 0.069821 | 5 |
| 2026-01-29 | 8 | 8 | 0.045656 | 0.069612 | 5 |
| 2026-02-01 | 8 | 8 | 0.052055 | 0.066939 | 5 |
| 2026-11-03 | 8 | 8 | 0.042969 | 0.060296 | 5 |
| 2026-10-27 | 8 | 8 | 0.049359 | 0.057722 | 5 |
| 2026-10-28 | 8 | 8 | 0.044436 | 0.057441 | 5 |
| 2026-10-12 | 9 | 9 | 0.082006 | 0.140225 | 21 |
| 2026-10-14 | 9 | 9 | 0.080637 | 0.134924 | 21 |
| 2026-10-13 | 9 | 9 | 0.086500 | 0.134335 | 21 |
| 2026-10-15 | 9 | 9 | 0.081379 | 0.132726 | 21 |
| 2026-02-19 | 9 | 9 | 0.073607 | 0.129652 | 21 |
| 2026-02-25 | 9 | 9 | 0.084590 | 0.129073 | 21 |
| 2026-02-20 | 9 | 9 | 0.079547 | 0.129059 | 21 |
| 2026-10-08 | 9 | 9 | 0.081493 | 0.127898 | 21 |
| 2026-10-09 | 9 | 9 | 0.084442 | 0.126259 | 21 |
| 2026-10-07 | 9 | 9 | 0.077488 | 0.126109 | 21 |

### As-of warning for an upper range miss

The simple warning model uses only prior resolved V13 forecast errors and dated features. Matched controls use earlier observed miss frequencies.

| horizon | n | warning_brier | historical_brier | rate |
| --- | --- | --- | --- | --- |
| 5 | 227 | 0.156330 | 0.139519 | 0.154185 |
| 21 | 153 | 0.263347 | 0.213845 | 0.111111 |

[Full failure casebook with observed and as-of values](failure-casebook.csv) · [Cross-model misses](synchronized-range-misses.csv) · [Historical episode removal](jump-episode-deletion.csv).
