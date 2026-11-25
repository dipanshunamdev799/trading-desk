# V19 Positioning And Risk Intelligence

Volatility expansion compares future annualized realized volatility with 1.25 times the eligible trailing reference. Contraction compares it with 0.8 times the trailing state. Entry to a high-volatility state starts below the 80th percentile from matured history, then scores a threshold crossing. The point tables keep absolute error and variance QLIKE with Brier probabilities, calibration and proper distribution scores. The protected V16 weekly point leader MAE is 0.036469 and weekly expansion benchmark Brier is 0.152707. The protected monthly GJR MAE is 0.033179 and Student EGARCH expansion Brier is 0.172872.

| horizon | model | n | abs error | qlike | brier | contraction brier | high entry brier | crps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined_positioning_risk | 265 | 0.037158 | 0.307856 | 0.159762 | 0.132202 | 0.069081 | 0.026249 |
| 5 | crowding_on_price | 265 | 0.037801 | 0.308174 | 0.162240 | 0.132286 | 0.071809 | 0.026527 |
| 5 | price_and_oi | 265 | 0.037853 | 0.316511 | 0.161602 | 0.133783 | 0.075769 | 0.026772 |
| 5 | protected_GJR | 265 | 0.040318 | 0.359870 | 0.188310 | — | — | — |
| 5 | protected_fixed_iv_rv | 265 | 0.038484 | 0.286114 | 0.152707 | — | — | — |
| 5 | protected_offshore_plus_domestic | 265 | 0.036469 | 0.290334 | 0.160327 | — | — | — |
| 5 | protected_raw_iv | 265 | 0.037814 | 0.276187 | 0.155657 | — | — | — |
| 5 | protected_student_EGARCH | 265 | 0.039960 | 0.327199 | 0.177866 | — | — | — |
| 5 | risk_calibrated_iv | 265 | 0.037785 | 0.278256 | 0.156619 | 0.131555 | 0.080129 | 0.026149 |
| 21 | combined_positioning_risk | 217 | 0.057095 | 0.524257 | 0.275973 | 0.239972 | 0.118591 | 0.040210 |
| 21 | crowding_on_price | 217 | 0.058676 | 0.526514 | 0.271387 | 0.233222 | 0.125050 | 0.040970 |
| 21 | price_and_oi | 217 | 0.060029 | 0.523280 | 0.267795 | 0.233031 | 0.133265 | 0.041208 |
| 21 | protected_GJR | 217 | 0.033179 | 0.199677 | 0.198788 | — | — | — |
| 21 | protected_fixed_iv_rv | 217 | 0.040894 | 0.257953 | 0.194367 | — | — | — |
| 21 | protected_offshore_plus_domestic | 217 | 0.049953 | 0.484730 | 0.207382 | — | — | — |
| 21 | protected_raw_iv | 217 | 0.039406 | 0.267623 | 0.186036 | — | — | — |
| 21 | protected_student_EGARCH | 217 | 0.035730 | 0.207684 | 0.172872 | — | — | — |
| 21 | risk_calibrated_iv | 217 | 0.048310 | 0.341146 | 0.221396 | 0.171915 | 0.116619 | 0.031821 |

| horizon | cutoff | model | n | endpoint crps | range crps | vol mae | touch brier | integrated brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | position_on_GJR | 265 | 0.010931 | 0.006510 | 0.040003 | 0.148460 | 0.122601 |
| 5 | preauction_0855 | position_on_IV | 265 | 0.010670 | 0.005692 | 0.036111 | 0.144420 | 0.120310 |
| 5 | preauction_0855 | same_clock_GIFT_first | 265 | 0.010493 | 0.006209 | 0.038994 | 0.132201 | 0.100551 |
| 5 | preauction_0855 | same_clock_GJR | 265 | 0.010922 | 0.006493 | 0.040097 | 0.148396 | 0.122458 |
| 5 | preauction_0855 | same_clock_IV | 265 | 0.010672 | 0.005768 | 0.036801 | 0.144562 | 0.120331 |
| 5 | previous_1700 | position_on_GJR | 265 | 0.010927 | 0.006528 | 0.040211 | 0.148614 | 0.122645 |
| 5 | previous_1700 | position_on_IV | 265 | 0.010666 | 0.005716 | 0.036158 | 0.144418 | 0.120343 |
| 5 | previous_1700 | same_clock_GJR | 265 | 0.010922 | 0.006493 | 0.040097 | 0.148396 | 0.122458 |
| 5 | previous_1700 | same_clock_IV | 265 | 0.010672 | 0.005768 | 0.036801 | 0.144562 | 0.120331 |
| 21 | preauction_0855 | position_on_GJR | 217 | 0.024801 | 0.016512 | 0.041073 | 0.186580 | 0.163336 |
| 21 | preauction_0855 | position_on_IV | 217 | 0.025161 | 0.017142 | 0.039843 | 0.185053 | 0.160413 |
| 21 | preauction_0855 | same_clock_GIFT_first | 217 | 0.027288 | 0.018570 | 0.044048 | 0.184421 | 0.149470 |
| 21 | preauction_0855 | same_clock_GJR | 217 | 0.024694 | 0.015488 | 0.037244 | 0.183861 | 0.161061 |
| 21 | preauction_0855 | same_clock_IV | 217 | 0.025198 | 0.017179 | 0.040023 | 0.184372 | 0.159680 |
| 21 | previous_1700 | position_on_GJR | 217 | 0.024851 | 0.016588 | 0.041083 | 0.186636 | 0.163421 |
| 21 | previous_1700 | position_on_IV | 217 | 0.025199 | 0.017156 | 0.039549 | 0.185300 | 0.160563 |
| 21 | previous_1700 | same_clock_GJR | 217 | 0.024694 | 0.015488 | 0.037244 | 0.183861 | 0.161061 |
| 21 | previous_1700 | same_clock_IV | 217 | 0.025198 | 0.017179 | 0.040023 | 0.184372 | 0.159680 |

| horizon | model | side | barrier | touch brier | day one brier | survivor n | survivor brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | position_on_GJR | lower | 0.020000 | 0.197539 | 0.040978 | 253 | 0.185630 |
| 5 | position_on_GJR | lower | 0.050000 | 0.015247 | 4.61e-07 | 265 | 0.015227 |
| 5 | position_on_GJR | upper | 0.020000 | 0.135682 | 0.025840 | 257 | 0.125468 |
| 5 | position_on_GJR | upper | 0.050000 | 0.039250 | 5.76e-07 | 265 | 0.039256 |
| 5 | same_clock_GJR | lower | 0.020000 | 0.196228 | 0.040426 | 253 | 0.184982 |
| 5 | same_clock_GJR | lower | 0.050000 | 0.015191 | 4.61e-07 | 265 | 0.015171 |
| 5 | same_clock_GJR | upper | 0.020000 | 0.137310 | 0.025840 | 257 | 0.126766 |
| 5 | same_clock_GJR | upper | 0.050000 | 0.039252 | 5.76e-07 | 265 | 0.039258 |
| 21 | position_on_GJR | lower | 0.020000 | 0.259160 | 0.051164 | 205 | 0.262685 |
| 21 | position_on_GJR | lower | 0.050000 | 0.208175 | 2.11e-07 | 217 | 0.208154 |
| 21 | position_on_GJR | upper | 0.020000 | 0.233256 | 0.023036 | 211 | 0.236705 |
| 21 | position_on_GJR | upper | 0.050000 | 0.101467 | 2.81e-07 | 217 | 0.101500 |
| 21 | same_clock_GJR | lower | 0.020000 | 0.252982 | 0.049366 | 205 | 0.257541 |
| 21 | same_clock_GJR | lower | 0.050000 | 0.207219 | 5.63e-07 | 217 | 0.207173 |
| 21 | same_clock_GJR | upper | 0.020000 | 0.231070 | 0.022335 | 211 | 0.235394 |
| 21 | same_clock_GJR | upper | 0.050000 | 0.095843 | 7.03e-07 | 217 | 0.095945 |

The joint laws scale all four daily log-price legs around the same anchor using one issue-specific factor. Their 256 scenarios preserve daily ordering, endpoint/interval relations, monotone barrier-time CDFs and separate first-session and survivor Brier. Upper and lower excursions, drawdown and range use those same OHLC atoms. Native V14 Student-t GJR monthly range CRPS is 0.015422 at its original guard. V17 post-open volatility outputs are independently archived with 09:25 and 10:20 conditioning.

[risk-cases.csv.gz](risk-cases.csv.gz) · [volatility-laws.npz](volatility-laws.npz) · [risk-fits.ndjson.gz](risk-fits.ndjson.gz) · [risk-replay-receipt.json](risk-replay-receipt.json) · [joint-law-receipts.json](joint-law-receipts.json) · [joint-path-cases.csv.gz](joint-path-cases.csv.gz) · [barrier-leaderboard.csv](barrier-leaderboard.csv) · [barrier-cases.csv.gz](barrier-cases.csv.gz) · [postopen-risk-cases.csv.gz](postopen-risk-cases.csv.gz) · [postopen-risk-laws.npz](postopen-risk-laws.npz) · [protected-native-joint-models.csv](protected-native-joint-models.csv)
