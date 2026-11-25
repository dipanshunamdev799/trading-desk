# V10 Coherent Forecasting

One weighted law supplies p(up), expected return, median return, quantiles, return buckets, expected endpoint and both central intervals. Every atom is a simple endpoint return. The endpoint estimate is origin close × (1 + the law's mean return). Interval endpoints derive from the law's 25th/75th and 10th/90th percentiles. Weighted finite approximations use 301 Student-t quantiles when applicable. Component fitting and de-normalization are performed before mixing. Paired shorter-path predictions preserve dependence through common residual draws. The empirical endpoint law does not identify every intervening path.

## Weekly full-law comparisons

| model | n | disjoint | brier | crps | log_loss | accuracy | balanced_accuracy | mae | median_mae | coverage80 | width80 | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J10_HISTORY_SHRINK | 265 | 53 | 0.242366 | 0.010892 | 0.678095 | 0.615094 | 0.627657 | 0.014988 | 0.014609 | 0.800000 | 0.045068 | 0.081103 |
| J9_REL_SHRINK | 265 | 53 | 0.248725 | 0.011014 | 0.691291 | 0.566038 | 0.576577 | 0.015100 | 0.014820 | 0.769811 | 0.041599 | 0.093883 |
| J10_STRUCTURAL_BLEND | 265 | 53 | 0.236181 | 0.011043 | 0.667575 | 0.637736 | 0.651507 | 0.015172 | 0.014723 | 0.815094 | 0.048713 | 0.081780 |
| NEUTRAL | 265 | 53 | 0.250000 | 0.011058 | 0.693147 | 0.528302 | 0.488190 | 0.015052 | 0.015062 | 0.735849 | 0.039228 | 0.058491 |
| J10_TARGET_BLEND | 265 | 53 | 0.255725 | 0.011242 | 0.706972 | 0.550943 | 0.543370 | 0.015346 | 0.015294 | 0.743396 | 0.039475 | 0.107991 |
| T_SIGNMAG | 265 | 53 | 0.257489 | 0.011259 | 0.710847 | 0.524528 | 0.514351 | 0.015137 | 0.015249 | 0.705660 | 0.037795 | 0.096094 |
| J10_SMALL_BLEND | 265 | 53 | 0.255845 | 0.011315 | 0.706213 | 0.554717 | 0.543168 | 0.015376 | 0.015160 | 0.735849 | 0.038322 | 0.103294 |
| J10_TRANSFER_BLEND | 265 | 53 | 0.259148 | 0.011321 | 0.712051 | 0.475472 | 0.471327 | 0.015591 | 0.015554 | 0.769811 | 0.043354 | 0.114838 |
| T_VOL_STUDENT | 265 | 53 | 0.254899 | 0.011323 | 0.705107 | 0.588679 | 0.587000 | 0.015627 | 0.015414 | 0.739623 | 0.041352 | 0.078344 |
| HISTORY | 265 | 53 | 0.259048 | 0.011340 | 0.711395 | 0.490566 | 0.499163 | 0.015448 | 0.015264 | 0.716981 | 0.037663 | 0.144278 |
| T_SPLIT | 265 | 53 | 0.280524 | 0.012346 | 0.766153 | 0.486792 | 0.484148 | 0.016631 | 0.016506 | 0.701887 | 0.039914 | 0.149838 |
| T_OVERNIGHT | 265 | 53 | 0.280524 | 0.012346 | 0.766153 | 0.486792 | 0.484148 | 0.016631 | 0.016506 | 0.701887 | 0.039914 | 0.149838 |
| T_RAW | 265 | 53 | 0.280763 | 0.012350 | 0.766742 | 0.490566 | 0.488421 | 0.016639 | 0.016510 | 0.701887 | 0.039912 | 0.145711 |
| T_VOL_RISK | 265 | 53 | 0.277829 | 0.012893 | 0.761800 | 0.547170 | 0.543572 | 0.017769 | 0.017825 | 0.716981 | 0.042679 | 0.166649 |

## Monthly full-law comparisons

| model | n | disjoint | brier | crps | log_loss | accuracy | balanced_accuracy | mae | median_mae | coverage80 | width80 | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NEUTRAL | 217 | 11 | 0.250000 | 0.025420 | 0.693147 | 0.511521 | 0.460742 | 0.033371 | 0.033392 | 0.635945 | 0.068179 | 0.062212 |
| T_SIGNMAG | 217 | 11 | 0.304078 | 0.027102 | 0.819166 | 0.465438 | 0.503624 | 0.035498 | 0.034203 | 0.552995 | 0.072466 | 0.218415 |
| HISTORY | 217 | 11 | 0.308418 | 0.027480 | 0.822832 | 0.437788 | 0.500000 | 0.035633 | 0.035609 | 0.585253 | 0.065591 | 0.213797 |
| J10_HISTORY_SHRINK | 217 | 11 | 0.288388 | 0.027539 | 0.781163 | 0.479263 | 0.510095 | 0.035862 | 0.034673 | 0.649770 | 0.085226 | 0.177770 |
| J10_TARGET_BLEND | 217 | 11 | 0.282285 | 0.027543 | 0.765207 | 0.470046 | 0.498404 | 0.037787 | 0.035415 | 0.594470 | 0.082115 | 0.148037 |
| J9_REL_SHRINK | 217 | 11 | 0.309326 | 0.027871 | 0.831365 | 0.437788 | 0.500000 | 0.035759 | 0.035921 | 0.599078 | 0.073155 | 0.262923 |
| J10_SMALL_BLEND | 217 | 11 | 0.321314 | 0.028849 | 0.863277 | 0.447005 | 0.479077 | 0.037083 | 0.036112 | 0.520737 | 0.073695 | 0.251603 |
| T_VOL_STUDENT | 217 | 11 | 0.266992 | 0.029111 | 0.729691 | 0.479263 | 0.486799 | 0.040148 | 0.041351 | 0.645161 | 0.089092 | 0.174313 |
| J10_STRUCTURAL_BLEND | 217 | 11 | 0.286258 | 0.030036 | 0.779483 | 0.497696 | 0.521829 | 0.040356 | 0.039793 | 0.645161 | 0.090629 | 0.211167 |
| J10_TRANSFER_BLEND | 217 | 11 | 0.310788 | 0.030230 | 0.833913 | 0.447005 | 0.458110 | 0.041680 | 0.040774 | 0.571429 | 0.086834 | 0.279000 |
| T_RAW | 217 | 11 | 0.349764 | 0.034527 | 0.976402 | 0.474654 | 0.485030 | 0.044357 | 0.044175 | 0.502304 | 0.081157 | 0.317624 |
| T_SPLIT | 217 | 11 | 0.349707 | 0.034657 | 0.976361 | 0.474654 | 0.485030 | 0.044556 | 0.044457 | 0.502304 | 0.081261 | 0.318052 |
| T_OVERNIGHT | 217 | 11 | 0.349707 | 0.034657 | 0.976361 | 0.474654 | 0.485030 | 0.044556 | 0.044457 | 0.502304 | 0.081261 | 0.318052 |
| T_VOL_RISK | 217 | 11 | 0.351298 | 0.035781 | 0.980454 | 0.474654 | 0.485030 | 0.048388 | 0.051926 | 0.548387 | 0.093189 | 0.324311 |

Five fixed mixture rules combine complete distributions. The structural law uses weights 0.40 base rotation, 0.30 sparse rotation and 0.30 volatility Student-t. The history-shrunk law gives half to that mixture and half to empirical history. The registry preserves the target, small-sample and transfer blends as well. These weights were registered as adaptive follow-ups to the initial batch results, and all relevant cohorts remain exposed. [Mixture recipe](mixture-registry.json) · [Weighted atoms](mixture-laws.jsonl) · [Calibration bins for all systems](calibration-bins.csv).
