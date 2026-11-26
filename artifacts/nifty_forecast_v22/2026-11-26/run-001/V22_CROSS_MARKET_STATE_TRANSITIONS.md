# V22 Cross-market state transitions

We used an observed past state and the next completed local window. Expansion means a realized-volatility ratio above
1.25, contraction a ratio below 0.80. Momentum reversal is scored only when the preceding standardized five-session trend
is at least 0.35 in magnitude. Recovery is scored after a standardized drawdown below −0.55. Divergence is a local
innovation larger than 0.8 horizon-volatility units in a previously synchronized state. Breadth deterioration is an
available proxy moving down by more than 0.60 normalized units. Those event-specific opportunity sets remain explicit.

The simplest forecasting law uses trailing volatility and local historical event frequency. The pooled, held-country and
held-region conditional heads use earlier state variables and clamp event probabilities to the declared finite range.
The partial-country model shrinks local conditional coefficients toward foreign estimates. Tables use causal filtering
and fully matured responses. Cross-country breadth history is visibly thinner than cash OHLC or volatility history.

## Later equal-country transition results

| horizon | model | rv mae | qlike | expansion brier | contraction brier | reversal brier | recovery brier | divergence brier | breadth deterioration brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | country_shuffle | 0.089176 | 3.223065 | 0.167461 | 0.239847 | 0.249243 | 0.224942 | 0.218511 | 0.110855 |
| 1 | local_own_only | 0.088378 | 3.132914 | 0.167784 | 0.239547 | 0.259321 | 0.233153 | 0.210929 | 0.108089 |
| 1 | local_persistence | 0.104696 | 1.570700 | 0.171530 | 0.245678 | 0.253938 | 0.226635 | 0.211342 | 0.111018 |
| 1 | loco_transfer | 0.089046 | 3.288827 | 0.168071 | 0.239792 | 0.248238 | 0.224113 | 0.219892 | 0.110927 |
| 1 | loro_transfer | 0.089086 | 3.320538 | 0.168058 | 0.239808 | 0.248379 | 0.226026 | 0.242463 | 0.110649 |
| 1 | partial_country | 0.088167 | 3.081344 | 0.167718 | 0.239161 | 0.259437 | 0.230504 | 0.209984 | 0.107568 |
| 3 | country_shuffle | 0.066209 | 0.777192 | 0.186516 | 0.241341 | 0.253724 | 0.207875 | 0.202283 | 0.190795 |
| 3 | local_own_only | 0.064681 | 0.733611 | 0.182712 | 0.240360 | 0.264280 | 0.229029 | 0.197771 | 0.180749 |
| 3 | local_persistence | 0.073830 | 0.637301 | 0.191476 | 0.256268 | 0.256642 | 0.217421 | 0.194799 | 0.195671 |
| 3 | loco_transfer | 0.065652 | 0.791101 | 0.184474 | 0.240034 | 0.250663 | 0.212776 | 0.202336 | 0.180930 |
| 3 | loro_transfer | 0.065542 | 0.814582 | 0.185678 | 0.239318 | 0.251615 | 0.213327 | 0.220912 | 0.180308 |
| 3 | partial_country | 0.063876 | 0.716049 | 0.182003 | 0.239642 | 0.264627 | 0.227076 | 0.196874 | 0.177669 |
| 5 | country_shuffle | 0.061783 | 0.537316 | 0.191710 | 0.227842 | 0.254745 | 0.206921 | 0.207797 | 0.199141 |
| 5 | local_own_only | 0.061014 | 0.510163 | 0.188995 | 0.225750 | 0.266907 | 0.246713 | 0.205544 | 0.175340 |
| 5 | local_persistence | 0.066422 | 0.491587 | 0.199562 | 0.248731 | 0.259657 | 0.228644 | 0.201722 | 0.210780 |
| 5 | loco_transfer | 0.060185 | 0.533778 | 0.189858 | 0.223708 | 0.250702 | 0.211480 | 0.208394 | 0.190677 |
| 5 | loro_transfer | 0.059617 | 0.550560 | 0.191042 | 0.222573 | 0.250289 | 0.218243 | 0.222378 | 0.190074 |
| 5 | mechanism_drawdown_recovery | 0.062626 | 0.557068 | 0.191773 | 0.230604 | 0.251542 | 0.210064 | 0.205726 | 0.190552 |
| 5 | mechanism_volatility_clustering | 0.061311 | 0.566571 | 0.189939 | 0.226372 | 0.253517 | 0.207099 | 0.204788 | 0.205482 |
| 5 | partial_country | 0.060000 | 0.491900 | 0.187937 | 0.223028 | 0.266971 | 0.244986 | 0.205601 | 0.173785 |
| 10 | country_shuffle | 0.056516 | 0.387893 | 0.193803 | 0.198228 | 0.256037 | 0.212433 | 0.227834 | 0.223599 |
| 10 | local_own_only | 0.057598 | 0.360240 | 0.197704 | 0.197922 | 0.269377 | 0.280661 | 0.233044 | 0.200791 |
| 10 | local_persistence | 0.058014 | 0.377803 | 0.208250 | 0.232301 | 0.258232 | 0.262648 | 0.220367 | 0.226060 |
| 10 | loco_transfer | 0.054269 | 0.370973 | 0.190935 | 0.187913 | 0.256787 | 0.227567 | 0.229636 | 0.217287 |
| 10 | loro_transfer | 0.052852 | 0.375503 | 0.192244 | 0.184347 | 0.259356 | 0.244143 | 0.243278 | 0.216940 |
| 10 | partial_country | 0.056498 | 0.341112 | 0.195602 | 0.192372 | 0.270472 | 0.290377 | 0.233661 | 0.197536 |
| 21 | country_shuffle | 0.055112 | 0.326630 | 0.184432 | 0.167647 | 0.255659 | 0.237006 | 0.243388 | 0.220249 |
| 21 | local_own_only | 0.055384 | 0.307595 | 0.212864 | 0.182256 | 0.284693 | 0.337430 | 0.245401 | 0.207865 |
| 21 | local_persistence | 0.055364 | 0.339569 | 0.224233 | 0.219528 | 0.262117 | 0.322959 | 0.250460 | 0.223000 |
| 21 | loco_transfer | 0.051992 | 0.328826 | 0.182066 | 0.160866 | 0.269501 | 0.249278 | 0.252021 | 0.225197 |
| 21 | loro_transfer | 0.049091 | 0.318257 | 0.178956 | 0.155645 | 0.274630 | 0.282698 | 0.268416 | 0.225021 |
| 21 | mechanism_drawdown_recovery | 0.058112 | 0.363248 | 0.189567 | 0.178441 | 0.264239 | 0.243782 | 0.250150 | 0.214249 |
| 21 | mechanism_volatility_clustering | 0.053351 | 0.325286 | 0.175815 | 0.166755 | 0.251184 | 0.228017 | 0.237174 | 0.221274 |
| 21 | partial_country | 0.053755 | 0.285647 | 0.211619 | 0.175180 | 0.289466 | 0.325158 | 0.246762 | 0.207981 |

## Matched date-level gains against the own-market ridge

| horizon | metric | model | observed origins | countries observed | negative countries | gain | low | high | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | expansion_brier | loco_transfer | 1,763 | 19 | 9 | -0.000689 | -0.008014 | 0.006151 | -0.010039 | 0.008662 |
| 5 | expansion_brier | loro_transfer | 1,763 | 19 | 10 | -0.001606 | -0.010013 | 0.006204 | -0.012601 | 0.009389 |
| 5 | contraction_brier | loco_transfer | 1,763 | 19 | 10 | 0.001899 | -0.009397 | 0.012441 | -0.012418 | 0.016216 |
| 5 | contraction_brier | loro_transfer | 1,763 | 19 | 8 | 0.002931 | -0.011457 | 0.015671 | -0.014993 | 0.020855 |
| 5 | reversal_brier | loco_transfer | 1,241 | 19 | 2 | 0.013876 | -0.001627 | 0.031398 | -0.008239 | 0.035991 |
| 5 | reversal_brier | loro_transfer | 1,241 | 19 | 2 | 0.014206 | -0.000345 | 0.030706 | -0.006327 | 0.034739 |
| 5 | recovery_brier | loco_transfer | 804 | 19 | 3 | 0.034403 | 0.014028 | 0.056485 | 0.006563 | 0.062242 |
| 5 | recovery_brier | loro_transfer | 804 | 19 | 3 | 0.031597 | 0.006173 | 0.058071 | -0.002707 | 0.065901 |
| 5 | divergence_brier | loco_transfer | 559 | 19 | 9 | -0.008106 | -0.025891 | 0.009089 | -0.029884 | 0.013672 |
| 5 | divergence_brier | loro_transfer | 559 | 19 | 12 | -0.019881 | -0.041250 | 0.000498 | -0.045416 | 0.005654 |
| 5 | breadth_deterioration_brier | loco_transfer | 278 | 3 | 3 | -0.015298 | -0.030949 | -0.000632 | -0.036178 | 0.005583 |
| 5 | breadth_deterioration_brier | loro_transfer | 278 | 3 | 3 | -0.014707 | -0.029822 | -0.000443 | -0.034771 | 0.005357 |
| 21 | expansion_brier | loco_transfer | 1,437 | 19 | 6 | 0.030504 | 0.002930 | 0.059935 | -0.005539 | 0.066547 |
| 21 | expansion_brier | loro_transfer | 1,437 | 19 | 6 | 0.033728 | 0.000769 | 0.067349 | -0.008227 | 0.075684 |
| 21 | contraction_brier | loco_transfer | 1,437 | 19 | 4 | 0.020486 | 0.010105 | 0.031381 | 0.006720 | 0.034251 |
| 21 | contraction_brier | loro_transfer | 1,437 | 19 | 5 | 0.024436 | 0.010674 | 0.041874 | 0.004063 | 0.044810 |
| 21 | reversal_brier | loco_transfer | 1,042 | 19 | 5 | 0.020272 | -0.007471 | 0.049224 | -0.016016 | 0.056561 |
| 21 | reversal_brier | loro_transfer | 1,042 | 19 | 7 | 0.015790 | -0.010009 | 0.041302 | -0.017541 | 0.049120 |
| 21 | recovery_brier | loco_transfer | 656 | 19 | 7 | 0.064208 | 0.000382 | 0.109812 | -0.003917 | 0.132333 |
| 21 | recovery_brier | loro_transfer | 656 | 19 | 7 | 0.033519 | -0.014829 | 0.075932 | -0.024035 | 0.091073 |
| 21 | divergence_brier | loco_transfer | 464 | 19 | 11 | 0.012948 | -0.046430 | 0.076886 | -0.061181 | 0.087077 |
| 21 | divergence_brier | loro_transfer | 464 | 19 | 11 | 0.002298 | -0.058288 | 0.068838 | -0.074922 | 0.079518 |
| 21 | breadth_deterioration_brier | loco_transfer | 230 | 3 | 2 | -0.014974 | -0.041525 | 0.013108 | -0.051035 | 0.021086 |
| 21 | breadth_deterioration_brier | loro_transfer | 230 | 3 | 2 | -0.014927 | -0.042030 | 0.014318 | -0.052239 | 0.022386 |

The risk gains concentrate in realized-volatility MAE and monthly expansion or contraction. Country-specific recovery, reversal and breadth remain sensitive to the opportunity cohort, comparison metric and geography.

[international-model-leaderboard.csv](international-model-leaderboard.csv) · [international-matched-date-intervals.csv.gz](international-matched-date-intervals.csv.gz) · [local-task-coverage.csv](local-task-coverage.csv) · [international-leave-global-episode-out.csv.gz](international-leave-global-episode-out.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
