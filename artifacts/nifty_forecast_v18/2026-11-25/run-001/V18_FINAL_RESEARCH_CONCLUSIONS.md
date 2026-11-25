# NIFTY V18 — Final research conclusions

**V18 established a historically timestamped corporate information universe.** The study retains **345,226** raw exchange announcements, **52,121** deduplicated timed publications in the historically eligible company cohort, and **10,621** verified financial facts from **1,278** document reports. Original opening-price prediction reproduced at **0.100841 Brier**. The event question after that opening was evaluated with known price reaction, risk, sector states, original horizon references, and event-only controls.

**Original-horizon evidence.** The table shows the largest point gains within each cutoff, target and score against the V17 structural benchmark. The score intervals retain the selection adjustment and show the precision of each gain. The protected **0.228529 weekly** and **0.245042 monthly** direction scores and the original **0.010457 and 0.024694** strongest archived distribution scores remain distinct references. Compare clock-equivalent alternatives before changing forecasts. The established origin sets contain only **53 and 11 disjoint index windows**, respectively.

The fundamental overlay changed the native V14 weekly Brier from **0.228529 to 0.223481**. Its gain interval of **-0.010429 to +0.020526** includes zero. The corresponding monthly overlay scored **0.259808** against **0.245042**. At 08:55 the official delivery, derivatives-positioning and deal controls gave a weekly Brier of **0.232338** against **0.238274** for the structural parent on **265** common dates. The adjusted gain interval from **-0.014517 to +0.026389** also includes zero. These are separate historical candidates at their documented clocks.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | preauction_0855 | additional_nonprice | clock_structural | brier | 217 | 11 | 0.281552 | 0.302805 | 0.021253 | -0.046521 | 0.089028 |
| 21 | previous_1700 | fundamental_only | clock_structural | brier | 217 | 11 | 0.285929 | 0.300452 | 0.014523 | -0.093546 | 0.122592 |
| 5 | preauction_0855 | additional_nonprice | clock_structural | brier | 265 | 53 | 0.232338 | 0.238274 | 0.005936 | -0.014517 | 0.026389 |
| 5 | previous_1700 | participant_positions | clock_structural | brier | 265 | 53 | 0.233698 | 0.238605 | 0.004907 | -0.011103 | 0.020916 |
| 21 | previous_1700 | fundamental_only | clock_structural | crps | 217 | 11 | 0.027118 | 0.028321 | 0.001203 | -0.004242 | 0.006648 |
| 21 | preauction_0855 | fundamental_only | clock_structural | crps | 217 | 11 | 0.027676 | 0.028519 | 0.000843 | -0.004568 | 0.006253 |
| 5 | preauction_0855 | additional_nonprice | clock_structural | crps | 265 | 53 | 0.010352 | 0.010658 | 0.000307 | -0.000418 | 0.001031 |
| 5 | previous_1700 | additional_nonprice | clock_structural | crps | 265 | 53 | 0.010431 | 0.010721 | 0.000290 | -0.000569 | 0.001150 |

**Risk, post-event diffusion and transfer.** The new risk inputs can be scored separately for realized volatility, transitions, ranges, and barriers when comparable earlier forecast laws exist. The results below compare the strongest descriptive gains with the parent at the same clock. Survival-conditioned barriers and the V16/V17 risk and path controls remain available separately. Transfer confidence depends on matched company-date clusters. A successful stock-level relationship is a stronger case for further research when it separately appears in later index returns.

At 10:20 the event layer on V17's cash-risk model lowered five-session volatility MAE from **0.040524 to 0.038681** on **221** dates with mature fit histories. Its adjusted interval of **-0.003339 to +0.007023** also includes zero. The strongest archived weekly and monthly point-risk references remain **0.036469** and **0.033179 MAE** at their native clocks.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | fundamental_risk | risk_calibrated_iv | brier | 265 | 53 | 0.154673 | 0.156619 | 0.001946 | -0.035220 | 0.039113 |
| 5 | 10:20 | postopen_event_risk | V17_postopen_cash_risk | abs_error | 221 | 45 | 0.038681 | 0.040524 | 0.001842 | -0.003339 | 0.007023 |
| 5 | preauction_0855 | non_price_risk | risk_calibrated_iv | brier | 265 | 53 | 0.154819 | 0.156619 | 0.001800 | -0.030131 | 0.033732 |
| 5 | 09:25 | postopen_event_risk | V17_postopen_cash_risk | abs_error | 221 | 45 | 0.038717 | 0.040408 | 0.001691 | -0.003354 | 0.006735 |
| 5 | previous_1700 | non_price_risk | risk_calibrated_iv | brier | 265 | 53 | 0.156077 | 0.157572 | 0.001495 | -0.025237 | 0.028227 |
| 5 | preauction_0855 | fundamental_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.036944 | 0.037785 | 0.000841 | -0.004492 | 0.006174 |
| 5 | previous_1700 | non_price_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037063 | 0.037858 | 0.000795 | -0.003552 | 0.005143 |
| 5 | previous_1700 | fundamental_risk | risk_calibrated_iv | brier | 265 | 53 | 0.156939 | 0.157572 | 0.000633 | -0.031322 | 0.032589 |
| 5 | preauction_0855 | non_price_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037189 | 0.037785 | 0.000596 | -0.004754 | 0.005946 |
| 5 | previous_1700 | fundamental_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037485 | 0.037858 | 0.000374 | -0.004023 | 0.004771 |
| 5 | previous_1700 | non_price_risk | risk_calibrated_iv | crps | 265 | 53 | 0.026086 | 0.026176 | 0.000090 | -0.002729 | 0.002910 |
| 5 | previous_1700 | material_events_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037774 | 0.037858 | 0.000084 | -0.003838 | 0.004006 |
| 5 | preauction_0855 | material_events_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037713 | 0.037785 | 0.000072 | -0.004645 | 0.004789 |
| 5 | preauction_0855 | non_price_risk | risk_calibrated_iv | crps | 265 | 53 | 0.026249 | 0.026149 | -0.000100 | -0.003021 | 0.002821 |
| 5 | preauction_0855 | fundamental_risk | risk_calibrated_iv | crps | 265 | 53 | 0.026395 | 0.026149 | -0.000246 | -0.003376 | 0.002884 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.038379 | 0.037858 | -0.000521 | -0.004646 | 0.003605 |

| horizon | model | n | different dates | issuers | mae | mean | low | high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | ordinary_pooled | 2,873 | 359 | 88 | 0.026812 | -0.000224 | -0.000365 | -0.000083 |
| 5 | price_only | 2,873 | 359 | 88 | 0.026588 | 0.000000 | 0.000000 | 0.000000 |
| 5 | sector_issuer_partial_pool | 2,873 | 359 | 88 | 0.026966 | -0.000379 | -0.000546 | -0.000211 |
| 5 | sector_specific | 2,873 | 359 | 88 | 0.026815 | -0.000227 | -0.000387 | -0.000067 |
| 21 | ordinary_pooled | 2,610 | 327 | 88 | 0.058342 | -0.000542 | -0.000924 | -0.000160 |
| 21 | price_only | 2,610 | 327 | 88 | 0.057800 | 0.000000 | 0.000000 | 0.000000 |
| 21 | sector_issuer_partial_pool | 2,610 | 327 | 88 | 0.058880 | -0.001080 | -0.001660 | -0.000500 |
| 21 | sector_specific | 2,610 | 327 | 88 | 0.058269 | -0.000469 | -0.001087 | 0.000150 |

The source clock and copy-invariance checks passed on **16** sentinels. Publication provenance, April to November close comparisons and earlier years within 2025 are kept as recorded. Complete dated analyst consensus, company float weights and full market-depth records were unavailable. All historical comparisons remain exposed research. The forward ledger is dated separately.

[Full comparison](V18_COMPLETE_MODEL_COMPARISON.md) · [Weekly and monthly report](V18_EVENT_INFORMED_NIFTY_FORECASTING.md) · [Risk and joint path evidence](V18_FUNDAMENTAL_RISK_INTELLIGENCE.md) · [Validation](V18_VALIDATION_AND_FALSIFICATION.md) · [Forward research](V18_FORWARD_RESEARCH_LEDGER.md)
