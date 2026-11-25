# V10 Overlapping Label Research

Adjacent five-session labels share up to four daily changes. Adjacent 21-session labels share up to 20. V10 kept the actual daily return calendar and counted unique covered sessions, greedy disjoint windows and equivalent sample size for each fit. The analytical return covariance uses C(i,j) = max(1 − distance(i,j)/h, 0), where distances are observed session indices. Uniform or positive trained weights are summarized by Kish ESS 1/Σw² and overlap ESS 1/(wᵀCw). These are measures under stated assumptions. They do not account for every source of serial correlation or non-stationarity. Evaluation outcome ESS uses observed return autocorrelation and has a different interpretation.

V10 compared ordinary overlapping losses, two fixed disjoint phases, equally weighted fits across all staggered phases, inverse-overlap weighting, generalized least squares with 65% and 85% theoretical covariance, and phase-agnostic time-block aggregate regressions. The empirical covariance follow-up adds a lag-one residual AR kernel fitted on matured inside-fold residual pairs, shrunk toward both the theoretical kernel and identity. Each phase represents a different view of the same market move. Pooled staggered predictions carry measured between-phase variance. GLS diagnostics record overlap support and matrix conditioning. The ridge scale is normalized against constant-intercept information, and the fitted covariance never uses query returns.

## Weekly Brier and CRPS

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| OMAX_BLOCKMEAN | 0.267867 | 0.245911 | 0.260245 | 0.011642 | 0.011694 | 0.011660 |
| OMAX_PHASE0 | 0.272980 | 0.258731 | 0.268033 | 0.011902 | 0.011898 | 0.011901 |
| OMAX_OVERLAP_WEIGHT | 0.282906 | 0.255535 | 0.273403 | 0.012018 | 0.012178 | 0.012074 |
| OMAX_PHASE1 | 0.281934 | 0.257865 | 0.273578 | 0.011869 | 0.012300 | 0.012019 |
| OMAX_STAGGERED | 0.284310 | 0.254341 | 0.273906 | 0.011963 | 0.012105 | 0.012012 |
| EC_MAX_PLAIN | 0.285113 | 0.256111 | 0.275044 | 0.012005 | 0.012152 | 0.012056 |
| OMAX_PLAIN | 0.285113 | 0.256111 | 0.275044 | 0.012005 | 0.012152 | 0.012056 |
| O126_BLOCKMEAN | 0.282456 | 0.264903 | 0.276362 | 0.013021 | 0.012724 | 0.012918 |
| O126_STAGGERED | 0.282716 | 0.290298 | 0.285348 | 0.012723 | 0.013272 | 0.012913 |
| O126_PHASE0 | 0.280262 | 0.299968 | 0.287104 | 0.012605 | 0.013178 | 0.012804 |
| EC_126_PLAIN | 0.285919 | 0.294744 | 0.288983 | 0.012790 | 0.013330 | 0.012978 |
| O126_PLAIN | 0.285919 | 0.294744 | 0.288983 | 0.012790 | 0.013330 | 0.012978 |
| O126_OVERLAP_WEIGHT | 0.285544 | 0.296230 | 0.289254 | 0.012884 | 0.013399 | 0.013063 |
| O126_PHASE1 | 0.287528 | 0.300746 | 0.292116 | 0.012708 | 0.013288 | 0.012909 |
| OMAX_GLS | 0.301587 | 0.291073 | 0.297937 | 0.012901 | 0.013535 | 0.013121 |
| O85_PHASE0 | 0.265750 | 0.358747 | 0.298036 | 0.012161 | 0.014824 | 0.013086 |
| O85_BLOCKMEAN | 0.278626 | 0.334804 | 0.298129 | 0.012331 | 0.014101 | 0.012946 |
| OMAX_GLS_STRONG | 0.304021 | 0.310982 | 0.306438 | 0.013112 | 0.013954 | 0.013404 |
| EC_MAX_GLS_EMPIRICAL | 0.305382 | 0.309139 | 0.306686 | 0.013221 | 0.013927 | 0.013466 |
| O85_PHASE1 | 0.285700 | 0.360571 | 0.311693 | 0.012546 | 0.014536 | 0.013237 |
| O85_STAGGERED | 0.280733 | 0.370811 | 0.312005 | 0.012492 | 0.014739 | 0.013272 |
| O85_OVERLAP_WEIGHT | 0.279973 | 0.376263 | 0.313402 | 0.012695 | 0.014823 | 0.013433 |
| O126_GLS | 0.292876 | 0.356507 | 0.314966 | 0.013392 | 0.014517 | 0.013783 |
| EC_85_PLAIN | 0.282169 | 0.376831 | 0.315033 | 0.012609 | 0.014860 | 0.013391 |
| O85_PLAIN | 0.282169 | 0.376831 | 0.315033 | 0.012609 | 0.014860 | 0.013391 |
| O126_GLS_STRONG | 0.295147 | 0.370018 | 0.321140 | 0.013456 | 0.014828 | 0.013932 |
| EC_126_GLS_EMPIRICAL | 0.299057 | 0.365260 | 0.322041 | 0.013744 | 0.014799 | 0.014110 |
| O85_GLS_STRONG | 0.285794 | 0.414894 | 0.330613 | 0.013265 | 0.016418 | 0.014360 |
| O85_GLS | 0.289103 | 0.411167 | 0.331480 | 0.013165 | 0.016051 | 0.014167 |
| EC_85_GLS_EMPIRICAL | 0.291034 | 0.412370 | 0.333158 | 0.013447 | 0.016316 | 0.014443 |

## Later training support by horizon

| horizon | model | training | nominal_rows | distinct_return_sessions | disjoint_training_windows | kish_ESS | overlap_effective_count | maximum_training_weight | df | phase_prediction_variance | design_condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | EC_126_GLS_EMPIRICAL | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 126.000000 | 25.524116 | 0.007937 | 7.370965 | 0.000000 | 7.783458 |
| 21 | EC_126_GLS_EMPIRICAL | 126.000000 | 126.000000 | 146.000000 | 6.000000 | 126.000000 | 6.352094 | 0.007937 | 9.619155 | 0.000000 | 44.910833 |
| 5 | EC_MAX_GLS_EMPIRICAL | 344.000000 | 344.000000 | 348.000000 | 69.000000 | 344.000000 | 69.121495 | 0.002907 | 9.231641 | 0.000000 | 9.477377 |
| 21 | EC_MAX_GLS_EMPIRICAL | 317.500000 | 317.500000 | 337.500000 | 15.500000 | 317.500000 | 15.459114 | 0.003153 | 10.336436 | 0.000000 | 46.162141 |
| 5 | O126_GLS | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 126.000000 | 25.524116 | 0.007937 | 7.048216 | 0.000000 | 6.647758 |
| 21 | O126_GLS | 126.000000 | 126.000000 | 146.000000 | 6.000000 | 126.000000 | 6.352094 | 0.007937 | 9.296866 | 0.000000 | 34.240947 |
| 5 | O126_PLAIN | 126.000000 | 126.000000 | 130.000000 | 26.000000 | 126.000000 | 25.524116 | 0.007937 | 5.164207 | 0.000000 | 4.061804 |
| 21 | O126_PLAIN | 126.000000 | 126.000000 | 146.000000 | 6.000000 | 126.000000 | 6.352094 | 0.007937 | 5.160582 | 0.000000 | 3.873333 |
| 5 | O85_BLOCKMEAN | 85.000000 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 | 0.011765 | 3.220289 | 0.000000 | 4.073689 |
| 21 | O85_BLOCKMEAN | 85.000000 | 85.000000 | 105.000000 | 5.000000 | 85.000000 | 4.409969 | 0.011765 | 2.110995 | 0.000000 | 4.658045 |
| 5 | O85_GLS | 85.000000 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 | 0.011765 | 6.266581 | 0.000000 | 7.514537 |
| 21 | O85_GLS | 85.000000 | 85.000000 | 105.000000 | 5.000000 | 85.000000 | 4.409969 | 0.011765 | 8.728257 | 0.000000 | 36.111740 |
| 5 | O85_PHASE0 | 85.000000 | 17.000000 | 85.000000 | 17.000000 | 17.000000 | 17.000000 | 0.058824 | 4.348559 | 0.000000 | 5.130965 |
| 21 | O85_PHASE0 | 85.000000 | 4.000000 | 84.000000 | 4.000000 | 4.000000 | 4.000000 | 0.250000 | 2.947915 | 0.000000 | 14.633353 |
| 5 | O85_PHASE1 | 85.000000 | 17.000000 | 85.000000 | 17.000000 | 17.000000 | 17.000000 | 0.058824 | 3.859809 | 0.000000 | 4.658526 |
| 21 | O85_PHASE1 | 85.000000 | 4.000000 | 84.000000 | 4.000000 | 4.000000 | 4.000000 | 0.250000 | 2.879201 | 0.000000 | 12.934943 |
| 5 | O85_PLAIN | 85.000000 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 | 0.011765 | 4.360531 | 0.000000 | 4.564575 |
| 21 | O85_PLAIN | 85.000000 | 85.000000 | 105.000000 | 5.000000 | 85.000000 | 4.409969 | 0.011765 | 4.339646 | 0.000000 | 4.523841 |
| 5 | O85_STAGGERED | 85.000000 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 | 0.011765 | 4.129186 | 0.000010 | 5.601381 |
| 21 | O85_STAGGERED | 85.000000 | 85.000000 | 105.000000 | 5.000000 | 85.000000 | 4.409969 | 0.011765 | 2.781212 | 0.000189 | 21.816199 |
| 5 | OMAX_BLOCKMEAN | 344.000000 | 344.000000 | 348.000000 | 69.000000 | 344.000000 | 69.121495 | 0.002907 | 6.553995 | 0.000000 | 5.848468 |
| 21 | OMAX_BLOCKMEAN | 317.500000 | 317.500000 | 337.500000 | 15.500000 | 317.500000 | 15.459114 | 0.003153 | 3.905809 | 0.000000 | 5.205374 |
| 5 | OMAX_PLAIN | 344.000000 | 344.000000 | 348.000000 | 69.000000 | 344.000000 | 69.121495 | 0.002907 | 7.564650 | 0.000000 | 5.827535 |
| 21 | OMAX_PLAIN | 317.500000 | 317.500000 | 337.500000 | 15.500000 | 317.500000 | 15.459114 | 0.003153 | 7.361175 | 0.000000 | 5.700644 |
| 5 | OMAX_STAGGERED | 344.000000 | 344.000000 | 348.000000 | 69.000000 | 344.000000 | 69.121495 | 0.002907 | 7.427494 | 0.000007 | 6.467242 |
| 21 | OMAX_STAGGERED | 317.500000 | 317.500000 | 337.500000 | 15.500000 | 317.500000 | 15.459114 | 0.003153 | 6.212204 | 0.000259 | 12.341436 |

Expanding block equations improved the ten-input weekly parent in both cohorts. The combined Brier was **0.260245** versus **0.275044**, with CRPS **0.011660** versus **0.012056**. GLS and disjoint phases shifted the fitted probability substantially and their results varied across periods and horizons. The block method still trailed the strongest weekly references. [Every fit and phase size](training-information-by-fold.csv) · [Paired disjoint tests](temporal-and-disjoint-stress.csv).
