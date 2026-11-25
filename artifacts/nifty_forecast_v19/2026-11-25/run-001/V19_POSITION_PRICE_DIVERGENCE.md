# V19 Position Price Divergence

The innovation test estimates same-day position changes from only earlier dated examples. State inputs include NIFTY return, recent momentum and volatility, front basis, term structure, time to expiry, ordinary OI changes, breadth, prior derivative exposure, ATM IV and skew available by the report clock. It stores the difference between the observed change and the ridge estimate. Each fit requires at least 40 past feature rows and uses at most 120. Separate innovations cover one and five session FII index futures, DII futures, index calls and index puts.

| horizon | model | n | active | brier | crps | rank corr |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | innovation_augmentation | 265 | 265 | 0.246402 | 0.010796 | 0.200030 |
| 5 | positions_beyond_oi | 265 | 221 | 0.246262 | 0.010718 | 0.276727 |
| 5 | positions_direct | 265 | 265 | 0.256639 | 0.011254 | 0.195820 |
| 5 | price_only | 265 | 265 | 0.253402 | 0.011271 | 0.092372 |
| 5 | price_ordinary_oi | 265 | 263 | 0.257997 | 0.011365 | 0.076823 |
| 5 | price_plus_disagreement | 265 | 263 | 0.254771 | 0.011285 | 0.157098 |
| 5 | price_plus_innovation | 265 | 263 | 0.262842 | 0.011435 | 0.060929 |
| 5 | price_plus_position_changes | 265 | 263 | 0.259534 | 0.011477 | 0.091273 |
| 5 | price_plus_position_level | 265 | 263 | 0.255412 | 0.011249 | 0.177979 |
| 21 | innovation_augmentation | 217 | 217 | 0.317197 | 0.029417 | -0.142887 |
| 21 | positions_beyond_oi | 217 | 157 | 0.307493 | 0.029786 | 0.026096 |
| 21 | positions_direct | 217 | 217 | 0.310747 | 0.028745 | -0.107819 |
| 21 | price_only | 217 | 217 | 0.316269 | 0.029159 | -0.091629 |
| 21 | price_ordinary_oi | 217 | 215 | 0.330218 | 0.029842 | -0.134093 |
| 21 | price_plus_disagreement | 217 | 215 | 0.312471 | 0.029000 | -0.059821 |
| 21 | price_plus_innovation | 217 | 215 | 0.322506 | 0.029367 | -0.089460 |
| 21 | price_plus_position_changes | 217 | 215 | 0.314332 | 0.028936 | -0.084436 |
| 21 | price_plus_position_level | 217 | 215 | 0.350512 | 0.030986 | -0.236193 |

| horizon | cutoff | cohort | model | parent | n | gain |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | active_matched | positions_beyond_oi | clock_with_oi_volume | 220 | -0.000238 |
| 5 | preauction_0855 | active_matched | positions_beyond_oi | clock_with_oi_volume | 220 | 0.000166 |
| 5 | preauction_0855 | away_from_expiry | positions_beyond_oi | clock_with_oi_volume | 199 | -0.003445 |
| 5 | preauction_0855 | away_from_expiry | positions_beyond_oi | clock_with_oi_volume | 199 | 0.000072 |
| 5 | preauction_0855 | active_matched | price_plus_disagreement | price_ordinary_oi | 263 | 0.003251 |
| 5 | preauction_0855 | active_matched | price_plus_disagreement | price_ordinary_oi | 263 | 0.000080 |
| 5 | preauction_0855 | away_from_expiry | price_plus_disagreement | price_ordinary_oi | 238 | 0.000815 |
| 5 | preauction_0855 | away_from_expiry | price_plus_disagreement | price_ordinary_oi | 238 | -6.54e-06 |
| 5 | preauction_0855 | active_matched | price_plus_innovation | price_ordinary_oi | 263 | -0.004882 |
| 5 | preauction_0855 | active_matched | price_plus_innovation | price_ordinary_oi | 263 | -0.000071 |
| 5 | preauction_0855 | away_from_expiry | price_plus_innovation | price_ordinary_oi | 238 | -0.004455 |
| 5 | preauction_0855 | away_from_expiry | price_plus_innovation | price_ordinary_oi | 238 | -0.000066 |
| 5 | previous_1700 | active_matched | positions_beyond_oi | clock_with_oi_volume | 219 | -0.003000 |
| 5 | previous_1700 | active_matched | positions_beyond_oi | clock_with_oi_volume | 219 | 0.000060 |
| 5 | previous_1700 | away_from_expiry | positions_beyond_oi | clock_with_oi_volume | 198 | -0.000110 |
| 5 | previous_1700 | away_from_expiry | positions_beyond_oi | clock_with_oi_volume | 198 | 0.000071 |
| 5 | previous_1700 | active_matched | price_plus_disagreement | price_ordinary_oi | 263 | -0.001646 |
| 5 | previous_1700 | active_matched | price_plus_disagreement | price_ordinary_oi | 263 | -0.000016 |
| 5 | previous_1700 | away_from_expiry | price_plus_disagreement | price_ordinary_oi | 238 | -0.002124 |
| 5 | previous_1700 | away_from_expiry | price_plus_disagreement | price_ordinary_oi | 238 | -0.000031 |
| 5 | previous_1700 | active_matched | price_plus_innovation | price_ordinary_oi | 263 | 0.000452 |
| 5 | previous_1700 | active_matched | price_plus_innovation | price_ordinary_oi | 263 | 1.71e-06 |
| 5 | previous_1700 | away_from_expiry | price_plus_innovation | price_ordinary_oi | 238 | 0.000981 |
| 5 | previous_1700 | away_from_expiry | price_plus_innovation | price_ordinary_oi | 238 | 0.000011 |

The price-only and position-only regressions make direct forecasts. The structural, residual and native weighted hypotheses score on their own historical controls. Applying a narrower maturity condition changes the training history, and the active-matched tables quantify that choice.

[position-innovation-fits.ndjson.gz](position-innovation-fits.ndjson.gz) · [positioning-daily-features.csv.gz](positioning-daily-features.csv.gz) · [endpoint-fit-receipts.ndjson.gz](endpoint-fit-receipts.ndjson.gz) · [matched-comparisons.csv](matched-comparisons.csv) · [episode-omission.csv](episode-omission.csv)
