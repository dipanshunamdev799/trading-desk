# V22 Transferable market relationships

V22 estimates transferable relationships from each market's own mature target. The common model minimizes date-balanced
ridge loss, with one unit of aggregate fitting weight per available origin date. Test blocks are ten UTC calendar days.
The last 255 days of eligible pooled training and up to 190 days of eligible local rows drive identical forecasting blocks.
Every training window finishes before the beginning of its test block. A rank-two map shares estimated structure across
four return heads. Partial pooling shrinks local slopes toward foreign coefficients while the local intercept is
fitted on the local window. The contextual pooled rows may see earlier labels from the evaluated foreign market and are
interpretable as chronological pooling. LOCO and LORO are the strict geography experiments.

Five mechanism fits test momentum and reversal, drawdown and recovery, volatility clustering, synchronization and relative
strength, and breadth and leadership. The table shows later country-average scores. Each negative control retains the original
decision dates. Date-country shuffling permutes responses within a date. The core time control moves blocks of date-level
common responses. Delayed transfer evaluates five-session-old state inputs. The concentration control omits the United
States, Japan and Germany from training.

| horizon | model | brier | crps | rv mae | qlike | range mae | expansion brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | country_shuffle | 0.251587 | 0.013314 | 0.061783 | 0.537316 | 0.011839 | 0.191710 |
| 5 | date_block_null | 0.253457 | 0.013405 | 0.062440 | 0.596518 | 0.011880 | 0.191277 |
| 5 | delayed_transfer | 0.255631 | 0.013340 | 0.061210 | 0.541793 | 0.011639 | 0.189202 |
| 5 | dominant_excluded | 0.252904 | 0.013394 | 0.060318 | 0.542885 | 0.011615 | 0.192359 |
| 5 | local_own_only | 0.270286 | 0.014485 | 0.061014 | 0.510163 | 0.011631 | 0.188995 |
| 5 | local_persistence | 0.250000 | 0.013225 | 0.066422 | 0.491587 | 0.014128 | 0.199562 |
| 5 | loco_transfer | 0.255071 | 0.013310 | 0.060185 | 0.533778 | 0.011460 | 0.189858 |
| 5 | loro_transfer | 0.257939 | 0.013415 | 0.059617 | 0.550560 | 0.011347 | 0.191042 |
| 5 | low_rank_shared | 0.252337 | 0.013378 | 0.060312 | 0.525400 | 0.011530 | 0.190368 |
| 5 | mechanism_breadth_leadership | 0.251180 | 0.013356 | 0.063130 | 0.569650 | 0.012055 | 0.191696 |
| 5 | mechanism_drawdown_recovery | 0.254774 | 0.013338 | 0.062626 | 0.557068 | 0.012083 | 0.191773 |
| 5 | mechanism_momentum_reversal | 0.254964 | 0.013344 | 0.063107 | 0.566932 | 0.012162 | 0.192711 |
| 5 | mechanism_synchronization_relative | 0.252902 | 0.013306 | 0.062889 | 0.560354 | 0.012065 | 0.192815 |
| 5 | mechanism_volatility_clustering | 0.253459 | 0.013286 | 0.061311 | 0.566571 | 0.011634 | 0.189939 |
| 5 | partial_country | 0.270575 | 0.014494 | 0.060000 | 0.491900 | 0.011467 | 0.187937 |
| 21 | country_shuffle | 0.283909 | 0.030531 | 0.055112 | 0.326630 | 0.029339 | 0.184432 |
| 21 | date_block_null | 0.266998 | 0.029726 | 0.055445 | 0.347853 | 0.028943 | 0.181238 |
| 21 | delayed_transfer | 0.272593 | 0.029114 | 0.051831 | 0.323081 | 0.026684 | 0.180464 |
| 21 | dominant_excluded | 0.284596 | 0.030909 | 0.053600 | 0.329237 | 0.029023 | 0.186193 |
| 21 | local_own_only | 0.321614 | 0.036719 | 0.055384 | 0.307595 | 0.030267 | 0.212864 |
| 21 | local_persistence | 0.250000 | 0.028659 | 0.055364 | 0.339569 | 0.029863 | 0.224233 |
| 21 | loco_transfer | 0.276787 | 0.029458 | 0.051992 | 0.328826 | 0.026486 | 0.182066 |
| 21 | loro_transfer | 0.285418 | 0.030322 | 0.049091 | 0.318257 | 0.024490 | 0.178956 |
| 21 | low_rank_shared | 0.281487 | 0.030728 | 0.053282 | 0.323539 | 0.028331 | 0.184745 |
| 21 | mechanism_breadth_leadership | 0.262915 | 0.029140 | 0.057637 | 0.342500 | 0.030261 | 0.182695 |
| 21 | mechanism_drawdown_recovery | 0.270758 | 0.029461 | 0.058112 | 0.363248 | 0.029774 | 0.189567 |
| 21 | mechanism_momentum_reversal | 0.271286 | 0.029540 | 0.058249 | 0.369908 | 0.029832 | 0.190408 |
| 21 | mechanism_synchronization_relative | 0.269503 | 0.029448 | 0.057025 | 0.336138 | 0.029674 | 0.182036 |
| 21 | mechanism_volatility_clustering | 0.274046 | 0.029704 | 0.053351 | 0.325286 | 0.027799 | 0.175815 |
| 21 | partial_country | 0.324036 | 0.037039 | 0.053755 | 0.285647 | 0.029296 | 0.211619 |

## Matched date-level contrasts against persistence

The gain is reference minus challenger loss. Adjusted bounds account for the compared families within that horizon and metric. Negative countries count markets where the challenger increased the loss.

| horizon | model | metric | observed origins | n | gain | adjusted low | adjusted high | negative countries | countries observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | loco_transfer | brier | 1,775 | 96 | -0.005111 | -0.018394 | 0.008172 | 13 | 19 |
| 5 | loro_transfer | brier | 1,775 | 96 | -0.007922 | -0.021443 | 0.005599 | 16 | 19 |
| 5 | partial_country | brier | 1,775 | 96 | -0.020583 | -0.034358 | -0.006807 | 15 | 19 |
| 5 | loco_transfer | rv_mae | 1,763 | 96 | 0.005886 | -0.001478 | 0.013249 | 2 | 19 |
| 5 | loro_transfer | rv_mae | 1,763 | 96 | 0.006474 | -0.002430 | 0.015378 | 3 | 19 |
| 5 | partial_country | rv_mae | 1,763 | 96 | 0.006034 | 0.000601 | 0.011467 | 7 | 19 |
| 5 | loco_transfer | expansion_brier | 1,763 | 96 | 0.009641 | 0.002615 | 0.016667 | 2 | 19 |
| 5 | loro_transfer | expansion_brier | 1,763 | 96 | 0.008724 | -0.000228 | 0.017675 | 4 | 19 |
| 5 | partial_country | expansion_brier | 1,763 | 96 | 0.011353 | 0.002572 | 0.020134 | 5 | 19 |
| 21 | loco_transfer | brier | 1,474 | 80 | -0.026892 | -0.096247 | 0.042463 | 15 | 19 |
| 21 | loro_transfer | brier | 1,474 | 80 | -0.035391 | -0.099560 | 0.028777 | 14 | 19 |
| 21 | partial_country | brier | 1,474 | 80 | -0.074505 | -0.120606 | -0.028403 | 14 | 19 |
| 21 | loco_transfer | rv_mae | 1,437 | 80 | 0.002448 | -0.003875 | 0.008771 | 9 | 19 |
| 21 | loro_transfer | rv_mae | 1,437 | 80 | 0.004870 | -0.006408 | 0.016148 | 8 | 19 |
| 21 | partial_country | rv_mae | 1,437 | 80 | 0.000512 | -0.005652 | 0.006677 | 12 | 19 |
| 21 | loco_transfer | expansion_brier | 1,437 | 80 | 0.041248 | 0.009007 | 0.073490 | 4 | 19 |
| 21 | loro_transfer | expansion_brier | 1,437 | 80 | 0.044473 | 0.009038 | 0.079907 | 3 | 19 |
| 21 | partial_country | expansion_brier | 1,437 | 80 | 0.011888 | -0.010989 | 0.034766 | 10 | 19 |

## Coefficient variation

| horizon | feature | head | n entities | median | iqr | sign agreement country | sign agreement time | near zero fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | drawdown | location | 20 | -0.006773 | 0.016511 | 1.000000 | 0.683019 | 0.965094 |
| 5 | drawdown | volatility | 20 | -0.020016 | 0.009856 | 1.000000 | 0.999057 | 0.937736 |
| 5 | drawdown | expansion | 20 | -0.008460 | 0.005585 | 1.000000 | 0.998113 | 1.000000 |
| 5 | mom5 | location | 20 | -0.005004 | 0.026838 | 1.000000 | 0.599057 | 0.893396 |
| 5 | mom5 | volatility | 20 | -0.016709 | 0.013144 | 1.000000 | 1.000000 | 0.687736 |
| 5 | mom5 | expansion | 20 | -0.009774 | 0.013674 | 1.000000 | 0.997170 | 0.928302 |
| 5 | vol_level | location | 20 | 0.000508 | 0.046591 | 0.500000 | 0.506604 | 0.583962 |
| 5 | vol_level | volatility | 20 | -0.038427 | 0.056666 | 1.000000 | 1.000000 | 0.029245 |
| 5 | vol_level | expansion | 20 | -0.027493 | 0.003965 | 1.000000 | 1.000000 | 0.248113 |
| 5 | vol_ratio | location | 20 | 0.016642 | 0.014495 | 1.000000 | 0.981132 | 0.795283 |
| 5 | vol_ratio | volatility | 20 | 0.016660 | 0.052591 | 1.000000 | 1.000000 | 0.547170 |
| 5 | vol_ratio | expansion | 20 | 0.009321 | 0.008899 | 1.000000 | 0.923585 | 0.927358 |
| 21 | drawdown | location | 20 | -0.021903 | 0.050130 | 1.000000 | 0.649020 | 0.537255 |
| 21 | drawdown | volatility | 20 | -0.008691 | 0.026829 | 1.000000 | 0.741176 | 0.700980 |
| 21 | drawdown | expansion | 20 | -0.002866 | 0.019755 | 1.000000 | 0.634314 | 0.999020 |
| 21 | mom5 | location | 20 | -0.012416 | 0.020625 | 1.000000 | 0.708824 | 0.984314 |
| 21 | mom5 | volatility | 20 | -0.005242 | 0.009448 | 1.000000 | 0.976471 | 0.999020 |
| 21 | mom5 | expansion | 20 | -0.002625 | 0.003024 | 1.000000 | 0.850980 | 1.000000 |
| 21 | vol_level | location | 20 | -0.016137 | 0.048122 | 1.000000 | 0.668627 | 0.393137 |
| 21 | vol_level | volatility | 20 | -0.047781 | 0.080455 | 1.000000 | 1.000000 | 0.011765 |
| 21 | vol_level | expansion | 20 | -0.044120 | 0.007479 | 1.000000 | 1.000000 | 0.000000 |
| 21 | vol_ratio | location | 20 | 0.000920 | 0.026533 | 0.700000 | 0.509804 | 0.915686 |
| 21 | vol_ratio | volatility | 20 | 0.022287 | 0.056907 | 1.000000 | 1.000000 | 0.529412 |
| 21 | vol_ratio | expansion | 20 | 0.013578 | 0.012599 | 1.000000 | 0.984314 | 0.851961 |

[international-model-leaderboard.csv](international-model-leaderboard.csv) · [international-matched-country-region.csv.gz](international-matched-country-region.csv.gz) · [international-matched-date-intervals.csv.gz](international-matched-date-intervals.csv.gz) · [transfer-coefficient-stability.csv](transfer-coefficient-stability.csv) · [international-coefficient-history.csv.gz](international-coefficient-history.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
