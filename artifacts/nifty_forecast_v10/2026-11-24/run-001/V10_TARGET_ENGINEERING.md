# V10 Target Engineering

All target representations used the same eligibility mask and returns on the same endpoint calendar. V10 compared raw returns, log returns, log returns divided by origin-known trailing realized volatility, log returns relative to the last 63 previously mature same-horizon outcomes, and a jointly predicted broad-market factor plus NIFTY residual. Multi-output forecasts pair residual vectors from the same purged validation origins. The shorter paths split into sessions 1 + 4 for weekly and 5 + 16 for monthly and sum predicted log-return components. Overnight and regular-session log returns are predicted jointly. The true intermediate move is reserved for evaluation. Each complete distribution converts to simple endpoint returns before evaluation.

Sign-and-magnitude estimates positive mass by regularized logistic regression shrunk 35% to the training sign rate. It fits shrunk magnitude adjustments separately within the two signs and combines the conditional samples with that same mass. The empirical and Student-t alternatives use a regularized blend of fitting-history and purged-validation information. The risk-specific empirical model reweights validation residuals conditional on the query's causal volatility bracket.

## Weekly target effects on identical dates

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| T_VOL_STUDENT | 0.265704 | 0.234580 | 0.254899 | 0.011313 | 0.011341 | 0.011323 |
| T_SIGNMAG | 0.271809 | 0.230562 | 0.257489 | 0.011227 | 0.011318 | 0.011259 |
| T_STUDENT | 0.273342 | 0.232626 | 0.259207 | 0.011324 | 0.011549 | 0.011402 |
| T_VOL_RISK | 0.291913 | 0.251344 | 0.277829 | 0.013169 | 0.012374 | 0.012893 |
| T_VOL | 0.283377 | 0.268556 | 0.278232 | 0.012762 | 0.012904 | 0.012811 |
| T_SPLIT | 0.285761 | 0.270677 | 0.280524 | 0.012157 | 0.012701 | 0.012346 |
| T_FACTOR | 0.285761 | 0.270677 | 0.280524 | 0.012157 | 0.012701 | 0.012346 |
| T_LOG | 0.285761 | 0.270677 | 0.280524 | 0.012157 | 0.012701 | 0.012346 |
| T_OVERNIGHT | 0.285761 | 0.270677 | 0.280524 | 0.012157 | 0.012701 | 0.012346 |
| T_RAW | 0.285984 | 0.270945 | 0.280763 | 0.012162 | 0.012703 | 0.012350 |
| T_CENTERED | 0.288521 | 0.284337 | 0.287068 | 0.012371 | 0.013160 | 0.012645 |

## Monthly target effects on identical dates

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| T_VOL_STUDENT | 0.249400 | 0.299630 | 0.266992 | 0.028983 | 0.029349 | 0.029111 |
| T_STUDENT | 0.250319 | 0.310646 | 0.271448 | 0.026799 | 0.030018 | 0.027926 |
| T_SIGNMAG | 0.283906 | 0.341502 | 0.304078 | 0.025359 | 0.030337 | 0.027102 |
| T_FACTOR | 0.282421 | 0.474538 | 0.349707 | 0.031716 | 0.040113 | 0.034657 |
| T_SPLIT | 0.282421 | 0.474538 | 0.349707 | 0.031716 | 0.040113 | 0.034657 |
| T_OVERNIGHT | 0.282421 | 0.474538 | 0.349707 | 0.031716 | 0.040113 | 0.034657 |
| T_LOG | 0.282421 | 0.474538 | 0.349707 | 0.031716 | 0.040113 | 0.034657 |
| T_RAW | 0.282984 | 0.473657 | 0.349764 | 0.031733 | 0.039711 | 0.034527 |
| T_VOL | 0.283264 | 0.477268 | 0.351210 | 0.034308 | 0.038535 | 0.035789 |
| T_VOL_RISK | 0.285138 | 0.474043 | 0.351298 | 0.034812 | 0.037579 | 0.035781 |
| T_CENTERED | 0.293841 | 0.513590 | 0.370804 | 0.035443 | 0.048522 | 0.040024 |

## Calibration of all six train-defined return buckets

| model | horizon | bucket | count | mean_probability | observed | component_Brier |
| --- | --- | --- | --- | --- | --- | --- |
| T_RAW | 5 | 0 | 265 | 0.127570 | 0.154717 | 0.145685 |
| T_RAW | 5 | 1 | 265 | 0.180865 | 0.200000 | 0.168091 |
| T_RAW | 5 | 2 | 265 | 0.176267 | 0.207547 | 0.171735 |
| T_RAW | 5 | 3 | 265 | 0.205680 | 0.177358 | 0.153330 |
| T_RAW | 5 | 4 | 265 | 0.187698 | 0.132075 | 0.119981 |
| T_RAW | 5 | 5 | 265 | 0.121920 | 0.128302 | 0.124176 |
| T_SIGNMAG | 5 | 0 | 265 | 0.109934 | 0.154717 | 0.135321 |
| T_SIGNMAG | 5 | 1 | 265 | 0.207330 | 0.200000 | 0.159928 |
| T_SIGNMAG | 5 | 2 | 265 | 0.189884 | 0.207547 | 0.165348 |
| T_SIGNMAG | 5 | 3 | 265 | 0.195713 | 0.177358 | 0.148900 |
| T_SIGNMAG | 5 | 4 | 265 | 0.179033 | 0.132075 | 0.117166 |
| T_SIGNMAG | 5 | 5 | 265 | 0.118107 | 0.128302 | 0.107910 |
| T_VOL_STUDENT | 5 | 0 | 265 | 0.120429 | 0.154717 | 0.137429 |
| T_VOL_STUDENT | 5 | 1 | 265 | 0.183675 | 0.200000 | 0.158030 |
| T_VOL_STUDENT | 5 | 2 | 265 | 0.186903 | 0.207547 | 0.161958 |
| T_VOL_STUDENT | 5 | 3 | 265 | 0.216826 | 0.177358 | 0.149185 |
| T_VOL_STUDENT | 5 | 4 | 265 | 0.161403 | 0.132075 | 0.116722 |
| T_VOL_STUDENT | 5 | 5 | 265 | 0.130763 | 0.128302 | 0.109571 |
| T_RAW | 21 | 0 | 217 | 0.179530 | 0.211982 | 0.211635 |
| T_RAW | 21 | 1 | 217 | 0.152157 | 0.276498 | 0.259224 |
| T_RAW | 21 | 2 | 217 | 0.107949 | 0.142857 | 0.128171 |
| T_RAW | 21 | 3 | 217 | 0.105758 | 0.096774 | 0.086165 |
| T_RAW | 21 | 4 | 217 | 0.200298 | 0.105991 | 0.109874 |
| T_RAW | 21 | 5 | 217 | 0.254308 | 0.165899 | 0.217772 |
| T_SIGNMAG | 21 | 0 | 217 | 0.124165 | 0.211982 | 0.191969 |
| T_SIGNMAG | 21 | 1 | 217 | 0.183277 | 0.276498 | 0.204729 |
| T_SIGNMAG | 21 | 2 | 217 | 0.199789 | 0.142857 | 0.130403 |
| T_SIGNMAG | 21 | 3 | 217 | 0.196545 | 0.096774 | 0.099774 |
| T_SIGNMAG | 21 | 4 | 217 | 0.192908 | 0.105991 | 0.107841 |
| T_SIGNMAG | 21 | 5 | 217 | 0.103315 | 0.165899 | 0.138619 |
| T_VOL_STUDENT | 21 | 0 | 217 | 0.186787 | 0.211982 | 0.208073 |
| T_VOL_STUDENT | 21 | 1 | 217 | 0.213874 | 0.276498 | 0.211758 |
| T_VOL_STUDENT | 21 | 2 | 217 | 0.166078 | 0.142857 | 0.126168 |
| T_VOL_STUDENT | 21 | 3 | 217 | 0.126671 | 0.096774 | 0.088563 |
| T_VOL_STUDENT | 21 | 4 | 217 | 0.168784 | 0.105991 | 0.103316 |
| T_VOL_STUDENT | 21 | 5 | 217 | 0.137806 | 0.165899 | 0.130634 |

Bucket cutoffs are the 10th, 30th, 50th, 70th and 90th training percentiles for each fold. Both extremes are evaluated alongside ordinary movement. Normalization improved some proper scores relative to the compact direct parent after Student scaling. The volatility Student-t law and the sign/magnitude system experienced different Brier, CRPS and calibration tradeoffs. Full distribution results and per-origin laws are in [target predictions](target-predictions.csv) and [target atom weights](target-laws.jsonl).
