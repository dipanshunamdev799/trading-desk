# V16 Gap absorption and reversal

A session can end on the gap side of the previous close while its intraday return partially retraces the gap. V16 separately tests close-to-close side, open-to-close continuation, remaining-session continuation, the next regular trading day's close-to-close return and first touch of a 50% retracement or full gap fill. Time-to-event scoring uses the authenticated 75-bar five-minute regular session. At 09:25 each case already supplied one bar. At 10:20 it supplied twelve. A level touched by that checkpoint is already resolved and is excluded from the corresponding risk set. The open can be the initial condition, and an untouched level has a right-censored mass at bar 76. The fitted rules use only eligible earlier labels and do not use the final day’s open as a feature before the first bar. The archive contains **12,324** continuation forecast scores and **1,653** survival scores.

## Continuation targets

| cutoff | target | model | n | actual | p | brier | log loss |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | close_beyond_previous_close_in_gap_direction | cash_prefix_only | 257 | 0.731518 | 0.733190 | 0.197084 | 0.582756 |
| 09:25 | close_beyond_previous_close_in_gap_direction | gap_sign_size | 257 | 0.731518 | 0.733712 | 0.196061 | 0.583248 |
| 09:25 | close_beyond_previous_close_in_gap_direction | history | 257 | 0.731518 | 0.731469 | 0.197100 | 0.583528 |
| 09:25 | close_beyond_previous_close_in_gap_direction | sector_offshore_full | 257 | 0.731518 | 0.733245 | 0.197650 | 0.584239 |
| 09:25 | next_regular_day_same_direction | cash_prefix_only | 256 | 0.519531 | 0.497657 | 0.246950 | 0.686987 |
| 09:25 | next_regular_day_same_direction | gap_sign_size | 256 | 0.519531 | 0.505550 | 0.255949 | 0.705180 |
| 09:25 | next_regular_day_same_direction | history | 256 | 0.519531 | 0.508081 | 0.253592 | 0.700343 |
| 09:25 | next_regular_day_same_direction | sector_offshore_full | 256 | 0.519531 | 0.496404 | 0.247092 | 0.687261 |
| 09:25 | open_to_close_continuation | cash_prefix_only | 257 | 0.536965 | 0.537460 | 0.253386 | 0.699982 |
| 09:25 | open_to_close_continuation | gap_sign_size | 257 | 0.536965 | 0.540515 | 0.253784 | 0.701205 |
| 09:25 | open_to_close_continuation | history | 257 | 0.536965 | 0.543729 | 0.249887 | 0.692944 |
| 09:25 | open_to_close_continuation | sector_offshore_full | 257 | 0.536965 | 0.538619 | 0.254325 | 0.701960 |
| 09:25 | remaining_same_gap_direction | cash_prefix_only | 257 | 0.544747 | 0.566600 | 0.252737 | 0.698922 |
| 09:25 | remaining_same_gap_direction | gap_sign_size | 257 | 0.544747 | 0.566435 | 0.255413 | 0.704837 |
| 09:25 | remaining_same_gap_direction | history | 257 | 0.544747 | 0.569824 | 0.249997 | 0.693227 |
| 09:25 | remaining_same_gap_direction | sector_offshore_full | 257 | 0.544747 | 0.569271 | 0.252918 | 0.699408 |
| 10:20 | close_beyond_previous_close_in_gap_direction | cash_prefix_only | 257 | 0.731518 | 0.732548 | 0.197200 | 0.583016 |
| 10:20 | close_beyond_previous_close_in_gap_direction | gap_sign_size | 257 | 0.731518 | 0.733712 | 0.196061 | 0.583248 |
| 10:20 | close_beyond_previous_close_in_gap_direction | history | 257 | 0.731518 | 0.731469 | 0.197100 | 0.583528 |
| 10:20 | close_beyond_previous_close_in_gap_direction | sector_offshore_full | 257 | 0.731518 | 0.732055 | 0.198472 | 0.586072 |
| 10:20 | next_regular_day_same_direction | cash_prefix_only | 256 | 0.519531 | 0.496357 | 0.247348 | 0.687788 |
| 10:20 | next_regular_day_same_direction | gap_sign_size | 256 | 0.519531 | 0.505550 | 0.255949 | 0.705180 |
| 10:20 | next_regular_day_same_direction | history | 256 | 0.519531 | 0.508081 | 0.253592 | 0.700343 |
| 10:20 | next_regular_day_same_direction | sector_offshore_full | 256 | 0.519531 | 0.495520 | 0.247442 | 0.688029 |
| 10:20 | open_to_close_continuation | cash_prefix_only | 257 | 0.536965 | 0.535762 | 0.253206 | 0.699609 |
| 10:20 | open_to_close_continuation | gap_sign_size | 257 | 0.536965 | 0.540515 | 0.253784 | 0.701205 |
| 10:20 | open_to_close_continuation | history | 257 | 0.536965 | 0.543729 | 0.249887 | 0.692944 |
| 10:20 | open_to_close_continuation | sector_offshore_full | 257 | 0.536965 | 0.536465 | 0.256890 | 0.707143 |
| 10:20 | remaining_same_gap_direction | cash_prefix_only | 257 | 0.540856 | 0.543521 | 0.255615 | 0.705069 |
| 10:20 | remaining_same_gap_direction | gap_sign_size | 257 | 0.540856 | 0.532548 | 0.254515 | 0.702593 |
| 10:20 | remaining_same_gap_direction | history | 257 | 0.540856 | 0.536226 | 0.249667 | 0.692494 |
| 10:20 | remaining_same_gap_direction | sector_offshore_full | 257 | 0.540856 | 0.544410 | 0.256583 | 0.707166 |

## Full-session realized retracements

| touch fraction | n | fill rate | conditional median bar |
| --- | --- | --- | --- |
| 0.500000 | 257 | 0.731518 | 1.000000 |
| 1.000000 | 257 | 0.536965 | 1.000000 |

## Forecasts conditional on no touch by the checkpoint

| cutoff | threshold | model | n | actual fill | forecast fill | brier | integrated brier | conditional abs minutes | median ess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | 0.500000 | calibrated_survival | 136 | 0.492647 | 0.553898 | 0.258177 | 0.236558 | 93.412006 | 95.858963 |
| 09:25 | 0.500000 | gap_matched_survival | 136 | 0.492647 | 0.576937 | 0.258543 | 0.237346 | 93.412006 | 95.858963 |
| 09:25 | 0.500000 | survivor_history | 136 | 0.492647 | 0.564107 | 0.258645 | 0.236353 | 92.224920 | 130.500000 |
| 09:25 | 1.000000 | calibrated_survival | 177 | 0.327684 | 0.368732 | 0.217341 | 0.169709 | 78.543368 | 111.570410 |
| 09:25 | 1.000000 | gap_matched_survival | 177 | 0.327684 | 0.371792 | 0.214533 | 0.168113 | 78.543368 | 111.570410 |
| 09:25 | 1.000000 | survivor_history | 177 | 0.327684 | 0.377182 | 0.224640 | 0.177868 | 85.177465 | 160.000000 |
| 10:20 | 0.500000 | calibrated_survival | 86 | 0.279070 | 0.288884 | 0.205746 | 0.110590 | 69.705976 | 59.011309 |
| 10:20 | 0.500000 | gap_matched_survival | 86 | 0.279070 | 0.310716 | 0.198614 | 0.108199 | 69.705976 | 59.011309 |
| 10:20 | 0.500000 | survivor_history | 86 | 0.279070 | 0.287953 | 0.203875 | 0.109240 | 69.853597 | 84.500000 |
| 10:20 | 1.000000 | calibrated_survival | 152 | 0.217105 | 0.223697 | 0.174262 | 0.114912 | 65.900001 | 102.864139 |
| 10:20 | 1.000000 | gap_matched_survival | 152 | 0.217105 | 0.228942 | 0.167881 | 0.111552 | 65.900001 | 102.864139 |
| 10:20 | 1.000000 | survivor_history | 152 | 0.217105 | 0.224090 | 0.171677 | 0.114831 | 67.262810 | 138.500000 |

## Matched integrated timing gains

| cutoff | threshold | candidate | n | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- |
| 09:25 | 0.500000 | gap_matched_survival | 136 | -0.000993 | -0.006860 | 0.004873 |
| 09:25 | 0.500000 | calibrated_survival | 136 | -0.000205 | -0.010684 | 0.010274 |
| 09:25 | 1.000000 | gap_matched_survival | 177 | 0.009755 | 0.001961 | 0.017549 |
| 09:25 | 1.000000 | calibrated_survival | 177 | 0.008159 | -0.000880 | 0.017199 |
| 10:20 | 0.500000 | gap_matched_survival | 86 | 0.001041 | -0.002795 | 0.004878 |
| 10:20 | 0.500000 | calibrated_survival | 86 | -0.001350 | -0.003373 | 0.000672 |
| 10:20 | 1.000000 | gap_matched_survival | 152 | 0.003278 | -0.000013 | 0.006570 |
| 10:20 | 1.000000 | calibrated_survival | 152 | -0.000082 | -0.002607 | 0.002443 |

The frequency models compare sign and training-defined gap size buckets, simple continuation and reversal rules, the observed price prefix, and a larger bank/breadth/foreign state. Those tests compare same-time risk sets. First-passage Brier tracks both end-of-session touch and the whole cumulative hitting curve. The time conditioned on a fill is summarized separately in minutes. A gap seen before regular trading and a subsequent intraday trade are separate measurement questions.

[Per-origin direction outcomes](session-continuation-scores.csv.gz) · [Survivor and actual time outcomes](first-touch-fill-scores.csv.gz) · [Probability by five-minute bar](gap-fill-time-laws.npz) · [Matched continuation comparisons](absorption-matched.csv) · [Training denominators](gap-fill-training-risks.csv)
