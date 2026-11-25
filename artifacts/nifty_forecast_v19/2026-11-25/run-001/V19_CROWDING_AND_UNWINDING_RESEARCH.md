# V19 Crowding And Unwinding Research

The primary crowded state is an index-futures four-category gross-share HHI at least one deviation above its own trailing window. We also use stock-futures concentration, persistence, delivery-value concentration, observed financing-sector participation and narrowing equal-weight breadth. A true reduction in the sum of recorded NIFTY futures OI is an auditable target. The reduction event requires at least an 8% decline from the eligible report mark. Rollover, expiry and position changes across expiries can lower or raise raw counts. We screen origins with more than three days to the named front expiry and a quiet roll flag. That sensitivity conditions on information available at issue and preserves the issue cohorts.

| horizon | outcome | group | count | rate or mean | concentration rank |
| --- | --- | --- | --- | --- | --- |
| 5 | reversal | crowded | 112 | 0.580357 | -0.070231 |
| 5 | reversal | ordinary | 323 | 0.482972 | -0.025183 |
| 5 | reversal | crowded_weak_breadth | 51 | 0.627451 | -0.402258 |
| 5 | expansion | crowded | 112 | 0.491071 | 0.142801 |
| 5 | expansion | ordinary | 323 | 0.195046 | -0.178071 |
| 5 | expansion | crowded_weak_breadth | 51 | 0.588235 | 0.305853 |
| 5 | oi_reduction | crowded | 112 | 0.232143 | -0.041209 |
| 5 | oi_reduction | ordinary | 319 | 0.200627 | -0.040632 |
| 5 | oi_reduction | crowded_weak_breadth | 51 | 0.294118 | 0.099400 |
| 21 | reversal | crowded | 104 | 0.634615 | 0.036583 |
| 21 | reversal | ordinary | 315 | 0.485714 | 0.013831 |
| 21 | reversal | crowded_weak_breadth | 43 | 0.720930 | 0.162942 |
| 21 | expansion | crowded | 104 | 0.403846 | 0.167108 |
| 21 | expansion | ordinary | 315 | 0.212698 | -0.208166 |
| 21 | expansion | crowded_weak_breadth | 43 | 0.441860 | 0.381135 |
| 21 | oi_reduction | crowded | 103 | 0.456311 | 0.047858 |
| 21 | oi_reduction | ordinary | 312 | 0.230769 | -0.067317 |
| 21 | oi_reduction | crowded_weak_breadth | 43 | 0.581395 | 0.167142 |

| horizon | outcome | model | n | loss | gain |
| --- | --- | --- | --- | --- | --- |
| 5 | expansion | position_changes | 333 | 0.200179 | 0.002421 |
| 5 | expansion | position_crowding | 333 | 0.193748 | 0.008852 |
| 5 | expansion | position_crowding_delay5 | 333 | 0.198159 | 0.004441 |
| 5 | expansion | price_iv_oi | 333 | 0.202600 | 0.000000 |
| 5 | oi_reduction | position_changes | 347 | 0.131271 | -0.003066 |
| 5 | oi_reduction | position_crowding | 347 | 0.129404 | -0.001200 |
| 5 | oi_reduction | position_crowding_delay5 | 347 | 0.130120 | -0.001915 |
| 5 | oi_reduction | price_iv_oi | 347 | 0.128204 | 0.000000 |
| 5 | realized_vol | position_changes | 350 | 0.003827 | 0.000106 |
| 5 | realized_vol | position_crowding | 350 | 0.003688 | 0.000245 |
| 5 | realized_vol | position_crowding_delay5 | 350 | 0.003921 | 0.000012 |
| 5 | realized_vol | price_iv_oi | 350 | 0.003933 | 0.000000 |
| 5 | reversal | position_changes | 345 | 0.261136 | -0.001117 |
| 5 | reversal | position_crowding | 345 | 0.256661 | 0.003358 |
| 5 | reversal | position_crowding_delay5 | 345 | 0.260556 | -0.000537 |
| 5 | reversal | price_iv_oi | 345 | 0.260019 | 0.000000 |
| 21 | expansion | position_changes | 307 | 0.263002 | -0.009457 |
| 21 | expansion | position_crowding | 307 | 0.260556 | -0.007011 |
| 21 | expansion | position_crowding_delay5 | 307 | 0.260690 | -0.007145 |
| 21 | expansion | price_iv_oi | 307 | 0.253545 | 0.000000 |
| 21 | oi_reduction | position_changes | 320 | 0.200236 | 0.015062 |
| 21 | oi_reduction | position_crowding | 320 | 0.205192 | 0.010107 |
| 21 | oi_reduction | position_crowding_delay5 | 320 | 0.214767 | 0.000532 |
| 21 | oi_reduction | price_iv_oi | 320 | 0.215299 | 0.000000 |
| 21 | realized_vol | position_changes | 324 | 0.003740 | 0.000023 |
| 21 | realized_vol | position_crowding | 324 | 0.003586 | 0.000177 |
| 21 | realized_vol | position_crowding_delay5 | 324 | 0.003623 | 0.000141 |
| 21 | realized_vol | price_iv_oi | 324 | 0.003763 | 0.000000 |
| 21 | reversal | position_changes | 319 | 0.261872 | -0.001683 |
| 21 | reversal | position_crowding | 319 | 0.266692 | -0.006503 |
| 21 | reversal | position_crowding_delay5 | 319 | 0.266048 | -0.005858 |
| 21 | reversal | price_iv_oi | 319 | 0.260190 | 0.000000 |

The labels refer to realized OI and future price behavior. Forced liquidation, margin pressure and individual trades cannot be identified from the aggregate files.

[crowding-conditional-states.csv](crowding-conditional-states.csv) · [crowding-case-tests.csv.gz](crowding-case-tests.csv.gz) · [crowding-leaderboard.csv](crowding-leaderboard.csv) · [positioning-daily-features.csv.gz](positioning-daily-features.csv.gz) · [risk-cases.csv.gz](risk-cases.csv.gz)
