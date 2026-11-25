# V16 Session-aware volatility

The transition target is a 25% rise in annualized close-to-close realized volatility relative to the trailing H-session level. The preserved frequency, raw IV, 75/25 IV/RV and Student-t EGARCH forecasts are re-evaluated at the exact V15 original origins. The point model decomposes log close-to-close risk into squared overnight gaps, squared regular returns and their cross term. Adjustments to log odds retain the raw-IV probability as an offset. The 09:25 and 10:20 price-seen control replaces a share of expected overnight variance with already observed opening information. It conservatively caps the variance adjustment. Models adding offshore volatility, disagreement, GIFT magnitude and later cash features are compared on the same target and eligibility. MAE measures volatility level, QLIKE measures the realized-to-forecast variance ratio, and proper transition probability loss is scored independently.

## Exact frozen expansion references

| horizon | model | n | rate | forecast rate | brier | log loss |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_EGARCH_t | 265 | 0.328302 | 0.380665 | 0.177866 | 0.514678 |
| 5 | fixed_75IV25RV | 265 | 0.328302 | 0.327067 | 0.152707 | 0.461636 |
| 5 | historical | 265 | 0.328302 | 0.329628 | 0.222296 | 0.636990 |
| 5 | iv_raw | 265 | 0.328302 | 0.356195 | 0.155657 | 0.466192 |
| 21 | V14_EGARCH_t | 217 | 0.373272 | 0.287098 | 0.172872 | 0.689982 |
| 21 | fixed_75IV25RV | 217 | 0.373272 | 0.225716 | 0.194367 | 0.831798 |
| 21 | historical | 217 | 0.373272 | 0.210386 | 0.299434 | 0.910763 |
| 21 | iv_raw | 217 | 0.373272 | 0.278692 | 0.186036 | 0.829771 |

## Before the auction

| horizon | model | n | realized | volatility | mae | qlike | brier | log loss | night mae | regular mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | fixed_iv_rv | 265 | 0.123981 | 0.130858 | 0.038484 | 0.286114 | 0.152707 | 0.461636 | — | — |
| 5 | gift_risk | 265 | 0.123981 | 0.121575 | 0.036867 | 0.295909 | 0.154689 | 0.465130 | 0.029700 | 0.033108 |
| 5 | global_disagreement | 265 | 0.123981 | 0.121834 | 0.036828 | 0.293215 | 0.155643 | 0.467080 | 0.031229 | 0.033707 |
| 5 | raw_iv | 265 | 0.123981 | 0.131751 | 0.037814 | 0.276187 | 0.155657 | 0.466192 | — | — |
| 5 | offshore_risk | 265 | 0.123981 | 0.120714 | 0.036815 | 0.297854 | 0.156922 | 0.469041 | 0.031388 | 0.033220 |
| 5 | offshore_plus_domestic | 265 | 0.123981 | 0.124803 | 0.036469 | 0.290334 | 0.160327 | 0.476147 | 0.033833 | 0.032554 |
| 5 | V14_IV_GJR | 265 | 0.123981 | 0.127865 | 0.037978 | 0.287184 | 0.165100 | 0.488979 | — | — |
| 5 | student_EGARCH | 265 | 0.123981 | 0.133987 | 0.039960 | 0.327199 | 0.177866 | 0.514678 | — | — |
| 5 | GJR | 265 | 0.123981 | 0.126852 | 0.040318 | 0.359870 | 0.188310 | 0.554745 | — | — |
| 5 | historical | 265 | 0.123981 | 0.097318 | 0.049549 | 0.990003 | 0.222296 | 0.636990 | — | — |
| 21 | student_EGARCH | 217 | 0.138004 | 0.135372 | 0.035730 | 0.207684 | 0.172872 | 0.689982 | — | — |
| 21 | raw_iv | 217 | 0.138004 | 0.133599 | 0.039406 | 0.267623 | 0.186036 | 0.829771 | — | — |
| 21 | fixed_iv_rv | 217 | 0.138004 | 0.133372 | 0.040894 | 0.257953 | 0.194367 | 0.831798 | — | — |
| 21 | GJR | 217 | 0.138004 | 0.128738 | 0.033179 | 0.199677 | 0.198788 | 0.769605 | — | — |
| 21 | global_disagreement | 217 | 0.138004 | 0.126822 | 0.041838 | 0.369758 | 0.205793 | 0.821999 | 0.041075 | 0.033391 |
| 21 | gift_risk | 217 | 0.138004 | 0.125534 | 0.042497 | 0.389662 | 0.207034 | 0.830133 | 0.041382 | 0.034727 |
| 21 | offshore_plus_domestic | 217 | 0.138004 | 0.136702 | 0.049953 | 0.484730 | 0.207382 | 0.824782 | 0.072537 | 0.043365 |
| 21 | offshore_risk | 217 | 0.138004 | 0.125874 | 0.042496 | 0.390101 | 0.208129 | 0.845016 | 0.042457 | 0.033341 |
| 21 | V14_IV_GJR | 217 | 0.138004 | 0.122337 | 0.033780 | 0.247374 | 0.211163 | 0.934906 | — | — |
| 21 | historical | 217 | 0.138004 | 0.104331 | 0.049010 | 0.936977 | 0.299434 | 0.910763 | — | — |

## Direct offshore transition gains against strong controls

| horizon | candidate | control | n | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | offshore_risk | raw_iv | 265 | 0.156922 | 0.155657 | -0.001266 | -0.011491 | 0.008959 |
| 5 | offshore_risk | fixed_iv_rv | 265 | 0.156922 | 0.152707 | -0.004215 | -0.012766 | 0.004336 |
| 5 | offshore_risk | student_EGARCH | 265 | 0.156922 | 0.177866 | 0.020944 | -0.018780 | 0.060667 |
| 5 | global_disagreement | raw_iv | 265 | 0.155643 | 0.155657 | 0.000013 | -0.011135 | 0.011161 |
| 5 | global_disagreement | fixed_iv_rv | 265 | 0.155643 | 0.152707 | -0.002936 | -0.010793 | 0.004921 |
| 5 | global_disagreement | student_EGARCH | 265 | 0.155643 | 0.177866 | 0.022223 | -0.018111 | 0.062556 |
| 5 | gift_risk | raw_iv | 265 | 0.154689 | 0.155657 | 0.000967 | -0.009115 | 0.011049 |
| 5 | gift_risk | fixed_iv_rv | 265 | 0.154689 | 0.152707 | -0.001982 | -0.008469 | 0.004505 |
| 5 | gift_risk | student_EGARCH | 265 | 0.154689 | 0.177866 | 0.023177 | -0.016311 | 0.062664 |
| 5 | offshore_plus_domestic | raw_iv | 265 | 0.160327 | 0.155657 | -0.004670 | -0.019558 | 0.010217 |
| 5 | offshore_plus_domestic | fixed_iv_rv | 265 | 0.160327 | 0.152707 | -0.007620 | -0.020275 | 0.005036 |
| 5 | offshore_plus_domestic | student_EGARCH | 265 | 0.160327 | 0.177866 | 0.017539 | -0.017314 | 0.052392 |
| 21 | offshore_risk | raw_iv | 217 | 0.208129 | 0.186036 | -0.022092 | -0.084731 | 0.040547 |
| 21 | offshore_risk | fixed_iv_rv | 217 | 0.208129 | 0.194367 | -0.013761 | -0.056927 | 0.029405 |
| 21 | offshore_risk | student_EGARCH | 217 | 0.208129 | 0.172872 | -0.035256 | -0.129197 | 0.058685 |
| 21 | global_disagreement | raw_iv | 217 | 0.205793 | 0.186036 | -0.019757 | -0.083108 | 0.043594 |
| 21 | global_disagreement | fixed_iv_rv | 217 | 0.205793 | 0.194367 | -0.011426 | -0.055510 | 0.032658 |
| 21 | global_disagreement | student_EGARCH | 217 | 0.205793 | 0.172872 | -0.032921 | -0.122366 | 0.056524 |
| 21 | gift_risk | raw_iv | 217 | 0.207034 | 0.186036 | -0.020998 | -0.084327 | 0.042331 |
| 21 | gift_risk | fixed_iv_rv | 217 | 0.207034 | 0.194367 | -0.012667 | -0.055181 | 0.029848 |
| 21 | gift_risk | student_EGARCH | 217 | 0.207034 | 0.172872 | -0.034162 | -0.126921 | 0.058597 |
| 21 | offshore_plus_domestic | raw_iv | 217 | 0.207382 | 0.186036 | -0.021346 | -0.078025 | 0.035334 |
| 21 | offshore_plus_domestic | fixed_iv_rv | 217 | 0.207382 | 0.194367 | -0.013014 | -0.060211 | 0.034182 |
| 21 | offshore_plus_domestic | student_EGARCH | 217 | 0.207382 | 0.172872 | -0.034509 | -0.123762 | 0.054743 |

## Revisions after the gap is observed

| horizon | cutoff | candidate | metric | n | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 09:25 | gap_only_adjustment | brier | 263 | 0.000569 | -0.008541 | 0.009679 |
| 5 | 09:25 | gap_only_adjustment | mae | 263 | 0.001528 | -0.002933 | 0.005989 |
| 5 | 09:25 | gap_plus_global | brier | 263 | 0.001403 | -0.007479 | 0.010285 |
| 5 | 09:25 | gap_plus_global | mae | 263 | 0.001178 | -0.003070 | 0.005427 |
| 5 | 10:20 | gap_only_adjustment | brier | 263 | 0.000427 | -0.008894 | 0.009749 |
| 5 | 10:20 | gap_only_adjustment | mae | 263 | 0.001467 | -0.003015 | 0.005949 |
| 5 | 10:20 | gap_plus_global | brier | 263 | 0.001508 | -0.007942 | 0.010957 |
| 5 | 10:20 | gap_plus_global | mae | 263 | 0.000930 | -0.003510 | 0.005369 |
| 5 | 10:20 | gap_global_breadth | brier | 263 | 0.000905 | -0.008237 | 0.010047 |
| 5 | 10:20 | gap_global_breadth | mae | 263 | 0.001354 | -0.002891 | 0.005599 |
| 21 | 09:25 | gap_only_adjustment | brier | 217 | -0.016975 | -0.080799 | 0.046850 |
| 21 | 09:25 | gap_only_adjustment | mae | 217 | -0.001369 | -0.007426 | 0.004689 |
| 21 | 09:25 | gap_plus_global | brier | 217 | -0.018315 | -0.082345 | 0.045714 |
| 21 | 09:25 | gap_plus_global | mae | 217 | -0.001997 | -0.007779 | 0.003785 |
| 21 | 10:20 | gap_only_adjustment | brier | 217 | -0.016396 | -0.078978 | 0.046186 |
| 21 | 10:20 | gap_only_adjustment | mae | 217 | -0.001601 | -0.007514 | 0.004313 |
| 21 | 10:20 | gap_plus_global | brier | 217 | -0.017816 | -0.081117 | 0.045484 |
| 21 | 10:20 | gap_plus_global | mae | 217 | -0.002172 | -0.007948 | 0.003604 |
| 21 | 10:20 | gap_global_breadth | brier | 217 | -0.018440 | -0.080569 | 0.043688 |
| 21 | 10:20 | gap_global_breadth | mae | 217 | -0.002067 | -0.007644 | 0.003509 |

The benchmark transition rankings favor the fixed blend weekly and Student-t EGARCH monthly. The best level, expansion or calibration model can differ. Post-auction risk revision results begin after the issue studied for the original endpoint. Monthly risk regimes remain strongly dependent across overlapping windows.

[Original V15 benchmark replay](volatility-preserved-references.csv) · [Dated volatility forecasts and component outcomes](volatility-scores.csv.gz) · [Complete model-specific loss ranks](volatility-leaderboard.csv) · [Matched adjustments and uncertainty](volatility-matched.csv) · [Matured risk fit parameters](volatility-fit-ledger.json)
