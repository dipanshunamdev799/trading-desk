# NIFTY V17 — Reproduction and baselines

The published opening-direction benchmark reproduced on all **248** common mornings. Before the auction, raw GIFT scored **0.100841 Brier**, **88.71% accuracy**, **0.001459 CRPS**, and **0.1965% median absolute error**. Its published adjusted Brier gain interval was **+0.095394 to +0.163392**. The original V15 opening experiment evaluated 258 mornings. V17 regenerated its 6,180 individual rows across all configured cutoffs and compared the four earlier V16 opening-clock batches, totaling 6,739 rows, with exact agreement on the saved forecast probabilities, scores and intervals. 08:30 1,545 rows · 08:45 1,545 rows · 08:55 1,545 rows · 09:10 1,545 rows. The archived 09:10 batch is preserved separately because opening price discovery is already underway.

| experiment | model | n | brier | crps |
| --- | --- | --- | --- | --- |
| 248 matched opening | gift_raw | 248 | 0.100841 | 0.001459 |
| 248 matched opening | equal_six | 248 | 0.233717 | 0.003075 |
| 248 matched opening | single_US | 248 | 0.225386 | 0.003058 |
| 248 matched opening | V15_offshore_fresh | 248 | 0.230235 | 0.002985 |
| 08:55 all | gift_raw | 248 | 0.100841 | 0.001459 |
| 08:55 no_large_gaps | gift_raw | 229 | 0.109204 | 0.001321 |
| 08:55 non_roll | gift_raw | 180 | 0.097792 | 0.001230 |
| 08:55 strict_ordinary_non_roll | gift_raw | 170 | 0.094003 | 0.001186 |

The verification included 1,240 saved anchor values with zero differences, 24,253 original decay forecasts, 12,324 continuation probabilities, and 1,653 first-passage laws. Gap-fill replay differences were at most 1.83e-08. Opening sensitivity screens remove known calendar sets and the largest realized gaps separately. Largest-gap deletion is a hindsight stress test.

## Fixed original endpoint benchmarks

The best protected weekly and monthly direction scores remain **0.228529** and **0.245042** before the V17 tests. Their comparison sets contain 265 and 217 origins. The separate strongest archived return laws scored **0.010457** and **0.024694 CRPS**. The 50/50 monthly probability gives **0.250000 Brier** by construction. Preserve each model, its guard, and the metric for which it earned its result.

| horizon | model | n | brier | endpoint crps | endpoint mae | endpoint coverage80 | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_sign_shrinkage | 265 | 0.228529 | 0.010457 | 0.014842 | 0.826415 | 0.636001 |
| 5 | V15_gjr_restart | 265 | 0.250763 | 0.010922 | 0.015006 | 0.773585 | 0.573516 |
| 5 | decomposed_gift | 265 | 0.242618 | 0.010493 | 0.014275 | 0.750943 | 0.608166 |
| 5 | neutral | 265 | 0.250000 | 0.011055 | 0.015068 | 0.758491 | 0.500000 |
| 5 | session_state | 265 | 0.239546 | 0.010466 | 0.014084 | 0.777358 | 0.598724 |
| 21 | V14_domestic_GJR | 217 | 0.245042 | 0.024989 | 0.033042 | 0.668203 | 0.502675 |
| 21 | V15_gjr_restart | 217 | 0.251376 | 0.024694 | 0.033162 | 0.705069 | 0.524072 |
| 21 | decomposed_gift | 217 | 0.273803 | 0.027288 | 0.037349 | 0.654378 | 0.501553 |
| 21 | neutral | 217 | 0.250000 | 0.025435 | 0.033408 | 0.682028 | 0.500000 |
| 21 | session_state | 217 | 0.270103 | 0.027116 | 0.036967 | 0.654378 | 0.507420 |

## Risk and first passage

At 08:55 the fixed IV/RV blend scored **0.152707** weekly expansion Brier and Student-t EGARCH scored **0.172872** monthly expansion Brier. The older monthly GJR risk study reported **0.033179 volatility MAE** and the V14 Student-t GJR joint range reported **0.015422 CRPS**. The GIFT-first weekly comparison achieved **0.132201** full-horizon barrier Brier and **0.139330** on the subsequent outcome conditional on surviving session one. The archived implementations retain their own risk targets, simulation laws and issue clocks.

| horizon | model | n | mae | qlike | brier | log loss |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | GJR | 265 | 0.040318 | 0.359870 | 0.188310 | 0.554745 |
| 5 | fixed_iv_rv | 265 | 0.038484 | 0.286114 | 0.152707 | 0.461636 |
| 5 | offshore_plus_domestic | 265 | 0.036469 | 0.290334 | 0.160327 | 0.476147 |
| 5 | raw_iv | 265 | 0.037814 | 0.276187 | 0.155657 | 0.466192 |
| 5 | student_EGARCH | 265 | 0.039960 | 0.327199 | 0.177866 | 0.514678 |
| 21 | GJR | 217 | 0.033179 | 0.199677 | 0.198788 | 0.769605 |
| 21 | fixed_iv_rv | 217 | 0.040894 | 0.257953 | 0.194367 | 0.831798 |
| 21 | offshore_plus_domestic | 217 | 0.049953 | 0.484730 | 0.207382 | 0.824782 |
| 21 | raw_iv | 217 | 0.039406 | 0.267623 | 0.186036 | 0.829771 |
| 21 | student_EGARCH | 217 | 0.035730 | 0.207684 | 0.172872 | 0.689982 |

| horizon | metric | candidate | control | n | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | touch_brier | decomposed_gift | V14_trend_shrink | 265 | 0.132201 | 0.143371 | 0.011169 | 0.002519 | 0.019820 |
| 5 | integrated_brier | decomposed_gift | V14_trend_shrink | 265 | 0.100551 | 0.119424 | 0.018873 | 0.009628 | 0.028119 |
| 5 | brier_by_1 | decomposed_gift | V14_trend_shrink | 265 | 0.054292 | 0.081827 | 0.027535 | 0.012251 | 0.042819 |
| 5 | brier_by_3 | decomposed_gift | V14_trend_shrink | 265 | 0.106793 | 0.125427 | 0.018635 | 0.010231 | 0.027038 |
| 5 | brier_by_5 | decomposed_gift | V14_trend_shrink | 265 | 0.132201 | 0.143371 | 0.011169 | 0.002519 | 0.019820 |
| 5 | conditional_brier | decomposed_gift | V14_trend_shrink | 265 | 0.139330 | 0.141434 | 0.002104 | -0.004448 | 0.008657 |

[Replay receipt](opening-reproduction.json) · [Session and first-passage receipt](session-baseline-reproduction.json) · [Continuation](reproduced-continuation.csv) · [Gap-fill risk sets](reproduced-survival.csv) · [Preserved endpoints](protected-original-scores.csv.gz)
