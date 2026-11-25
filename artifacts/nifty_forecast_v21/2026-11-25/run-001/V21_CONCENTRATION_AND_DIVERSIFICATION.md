# V21 Concentration And Diversification

Concentration is measured in beginning-index weights, predicted signed contributions and subsequent realized signed contributions. Their effective counts use the square of the sum of absolute contributions divided by the sum of squares. Beginning-weight effective count reduces to the inverse Herfindahl index. Realized contribution concentration is an outcome diagnostic. Forward regime thresholds use only earlier observed values. The high state uses the prior **66th percentile** over up to **100** previous origins and needs at least **35**. NIFTY breadth, IV and observed cross-stock synchronization supply separate comparisons.

| horizon | n | median weight top5 | median effective weights | median expected effective | median realized effective | mean covered weight | median common share proxy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 265 | 0.375583 | 23.168585 | 21.359840 | 18.605076 | 0.998957 | 0.344356 |
| 21 | 217 | 0.374483 | 23.317193 | 21.401809 | 18.626830 | 0.999858 | 0.331867 |

| horizon | group | regime | n | disjoint | up rate | average actual rv | anchor brier | pooled brier | anchor crps | pooled crps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | weight_top5 | high | 39 | 10 | 0.641026 | 0.099896 | 0.250522 | 0.264882 | 0.008404 | 0.008175 |
| 5 | weight_top5 | typical | 191 | 40 | 0.382199 | 0.137996 | 0.214149 | 0.273118 | 0.011329 | 0.013298 |
| 5 | effective_expected_contributors | high | 76 | 30 | 0.302632 | 0.143540 | 0.178029 | 0.295931 | 0.010711 | 0.015120 |
| 5 | effective_expected_contributors | typical | 154 | 40 | 0.487013 | 0.125611 | 0.241186 | 0.259774 | 0.010894 | 0.011101 |
| 5 | prior_synchronization | high | 79 | 30 | 0.518987 | 0.150608 | 0.226625 | 0.296406 | 0.011884 | 0.014027 |
| 5 | prior_synchronization | typical | 151 | 41 | 0.377483 | 0.121557 | 0.217016 | 0.258808 | 0.010283 | 0.011593 |
| 5 | prior_breadth | high | 78 | 34 | 0.435897 | 0.147156 | 0.217273 | 0.265475 | 0.012257 | 0.013825 |
| 5 | prior_breadth | typical | 152 | 41 | 0.421053 | 0.123519 | 0.221879 | 0.274927 | 0.010102 | 0.011713 |
| 5 | prior_iv | high | 89 | 22 | 0.516854 | 0.177422 | 0.236184 | 0.299166 | 0.016197 | 0.018118 |
| 5 | prior_iv | typical | 141 | 33 | 0.368794 | 0.102571 | 0.210301 | 0.254399 | 0.007447 | 0.008838 |
| 5 | sector_dispersion | high | 98 | 27 | 0.397959 | 0.146680 | 0.218903 | 0.295463 | 0.011023 | 0.013746 |
| 5 | sector_dispersion | typical | 132 | 31 | 0.446970 | 0.120292 | 0.221366 | 0.254096 | 0.010692 | 0.011451 |
| 21 | weight_top5 | high | 15 | 2 | 0.866667 | 0.118193 | 0.192778 | 0.231827 | 0.016067 | 0.017312 |
| 21 | weight_top5 | typical | 167 | 9 | 0.431138 | 0.146672 | 0.225448 | 0.230426 | 0.026891 | 0.028202 |
| 21 | effective_expected_contributors | high | 62 | 8 | 0.500000 | 0.144452 | 0.247190 | 0.237644 | 0.030427 | 0.031003 |
| 21 | effective_expected_contributors | typical | 120 | 9 | 0.450000 | 0.144259 | 0.210130 | 0.226872 | 0.023711 | 0.025393 |
| 21 | prior_synchronization | high | 57 | 8 | 0.526316 | 0.169201 | 0.238121 | 0.239441 | 0.029622 | 0.031202 |
| 21 | prior_synchronization | typical | 125 | 9 | 0.440000 | 0.132981 | 0.215748 | 0.226484 | 0.024347 | 0.025526 |
| 21 | prior_breadth | high | 61 | 8 | 0.442623 | 0.155260 | 0.207948 | 0.219633 | 0.024827 | 0.026904 |
| 21 | prior_breadth | typical | 121 | 9 | 0.479339 | 0.138812 | 0.230220 | 0.236041 | 0.026590 | 0.027506 |
| 21 | prior_iv | high | 74 | 5 | 0.500000 | 0.184527 | 0.202645 | 0.217771 | 0.032227 | 0.035156 |
| 21 | prior_iv | typical | 108 | 7 | 0.444444 | 0.116779 | 0.236534 | 0.239292 | 0.021732 | 0.021924 |
| 21 | sector_dispersion | high | 65 | 6 | 0.492308 | 0.190755 | 0.210376 | 0.236583 | 0.033963 | 0.037870 |
| 21 | sector_dispersion | typical | 117 | 7 | 0.452991 | 0.118530 | 0.229632 | 0.227185 | 0.021575 | 0.021434 |

| horizon | signal | realized vol rank | absolute index rank |
| --- | --- | --- | --- |
| 5 | weight_top5 | -0.147922 | -0.217209 |
| 5 | effective_expected_contributors | 0.126732 | 0.141449 |
| 5 | prior_synchronization | 0.128404 | -0.009954 |
| 5 | prior_breadth | 0.096616 | 0.070461 |
| 5 | prior_iv | 0.611711 | 0.324672 |
| 5 | sector_dispersion | 0.430749 | 0.252294 |
| 21 | weight_top5 | 0.131466 | -0.255870 |
| 21 | effective_expected_contributors | 0.034523 | 0.057056 |
| 21 | prior_synchronization | 0.242202 | 0.070360 |
| 21 | prior_breadth | 0.013401 | 0.013618 |
| 21 | prior_iv | 0.462996 | 0.025422 |
| 21 | sector_dispersion | 0.334761 | 0.026478 |

The five-heavyweight removal, January random baskets and alternate weighting rules probe whether the same information persists under changing constituent exposure. Canceled stock contributions can reduce the expected aggregate signal even when equity forecasts differ materially. Sector dispersion and cross-stock synchronization are also evaluated against conditional realized volatility.

[concentration-cases.csv](concentration-cases.csv) · [concentration-regime-results.csv](concentration-regime-results.csv) · [concentration-association.csv](concentration-association.csv) · [daily-constituent-weight-coverage.csv](daily-constituent-weight-coverage.csv) · [index-tracking-leaderboard.csv](index-tracking-leaderboard.csv) · [daily-portfolio-risk-features.csv](daily-portfolio-risk-features.csv)
