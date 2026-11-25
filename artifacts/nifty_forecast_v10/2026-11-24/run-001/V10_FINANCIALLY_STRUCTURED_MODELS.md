# V10 Financially Structured Models

Trailing beta estimates use at most 63 dated sector return observations, with at least 35, and are shifted before applying the exposure. The common component is lagged beta times current benchmark return. Residual market structure includes mean relative momentum, cross-sector dispersion and a bank residual. The two views add separately to the same ten-input parent. Removing the bank residual and delaying the financial/defensive source pair by one observed session test model sensitivity. The factor-adjusted target simultaneously predicts the broad factor and residual, with a shrunk and bounded beta.

The state-transition experiment models volatility, trend, participation, liquidity and defensive and financial leadership using causal rolling AR(1) summaries with 42 observations, warmup 25 and coefficients clipped to ±0.9. Ordinary lagged states and existing levels provide direct controls. Further models compare slowly varying 21-session factors and strongly shrunk 0, 5, 10 and 21 session rotation lags. Returns and scale follow separate procedures in the Student and volatility-conditioned laws. Genuine weighted sector contribution would require dated effective memberships and weights capable of mapping a disjoint constituent set into NIFTY.

## Weekly values

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| T_VOL_STUDENT | 0.265704 | 0.234580 | 0.254899 | 0.011313 | 0.011341 | 0.011323 |
| T_STUDENT | 0.273342 | 0.232626 | 0.259207 | 0.011324 | 0.011549 | 0.011402 |
| S_DISTRIBUTED | 0.281516 | 0.254501 | 0.272137 | 0.011885 | 0.012066 | 0.011948 |
| S_STATE_LAG | 0.286139 | 0.247218 | 0.272627 | 0.012122 | 0.011940 | 0.012059 |
| S_RESID_FACTOR | 0.276791 | 0.268005 | 0.273741 | 0.011726 | 0.012663 | 0.012051 |
| S_LAG_ROTATION | 0.285666 | 0.253304 | 0.274431 | 0.012007 | 0.012191 | 0.012071 |
| BASE10 | 0.285113 | 0.256111 | 0.275044 | 0.012005 | 0.012152 | 0.012056 |
| S_COMMON | 0.286384 | 0.256155 | 0.275889 | 0.012309 | 0.012190 | 0.012268 |
| S_STATE_LEVEL | 0.287783 | 0.255840 | 0.276694 | 0.012048 | 0.012189 | 0.012097 |
| S_REMOVE_BANK | 0.285506 | 0.260195 | 0.276719 | 0.012011 | 0.012241 | 0.012091 |
| T_VOL_RISK | 0.291913 | 0.251344 | 0.277829 | 0.013169 | 0.012374 | 0.012893 |
| S_PERSIST | 0.283408 | 0.282397 | 0.283057 | 0.011800 | 0.012991 | 0.012214 |
| S_STATE_EXPECTED | 0.294009 | 0.265547 | 0.284128 | 0.012293 | 0.012406 | 0.012332 |

## Monthly values

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| T_VOL_STUDENT | 0.249400 | 0.299630 | 0.266992 | 0.028983 | 0.029349 | 0.029111 |
| T_STUDENT | 0.250319 | 0.310646 | 0.271448 | 0.026799 | 0.030018 | 0.027926 |
| S_STATE_LEVEL | 0.294279 | 0.454187 | 0.350283 | 0.029171 | 0.037732 | 0.032169 |
| T_VOL_RISK | 0.285138 | 0.474043 | 0.351298 | 0.034812 | 0.037579 | 0.035781 |
| S_STATE_LAG | 0.301204 | 0.460298 | 0.356924 | 0.029578 | 0.037696 | 0.032422 |
| BASE10 | 0.299569 | 0.471471 | 0.359775 | 0.029401 | 0.038252 | 0.032501 |
| S_LAG_ROTATION | 0.298723 | 0.474793 | 0.360388 | 0.029344 | 0.038358 | 0.032501 |
| S_DISTRIBUTED | 0.293326 | 0.484978 | 0.360448 | 0.028672 | 0.038211 | 0.032013 |
| S_REMOVE_BANK | 0.300737 | 0.474444 | 0.361575 | 0.029446 | 0.038337 | 0.032560 |
| S_STATE_EXPECTED | 0.313801 | 0.461570 | 0.365554 | 0.031313 | 0.037228 | 0.033385 |
| S_COMMON | 0.311884 | 0.482285 | 0.371564 | 0.030771 | 0.038371 | 0.033433 |
| S_RESID_FACTOR | 0.318753 | 0.493288 | 0.379880 | 0.030737 | 0.039542 | 0.033821 |
| S_PERSIST | 0.348047 | 0.439146 | 0.379952 | 0.032911 | 0.036475 | 0.034159 |

| horizon | cohort | model | baseline | metric | n | candidate | control | gain | block10_adjusted_low | block10_adjusted_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | S_LAG_ROTATION | BASE10 | brier | 265 | 0.274431 | 0.275044 | 0.000613 | -0.007516 | 0.008742 |
| 5 | combined | S_LAG_ROTATION | BASE10 | crps | 265 | 0.012071 | 0.012056 | -0.000014 | -0.000136 | 0.000107 |
| 5 | combined | S_REMOVE_BANK | BASE10 | brier | 265 | 0.276719 | 0.275044 | -0.001675 | -0.010283 | 0.006933 |
| 5 | combined | S_REMOVE_BANK | BASE10 | crps | 265 | 0.012091 | 0.012056 | -0.000034 | -0.000223 | 0.000154 |
| 5 | combined | S_RESID_FACTOR | BASE10 | brier | 265 | 0.273741 | 0.275044 | 0.001303 | -0.019553 | 0.022160 |
| 5 | combined | S_RESID_FACTOR | BASE10 | crps | 265 | 0.012051 | 0.012056 | 0.000005 | -0.000638 | 0.000648 |
| 5 | combined | S_STATE_EXPECTED | S_STATE_LAG | brier | 265 | 0.284128 | 0.272627 | -0.011501 | -0.032976 | 0.009974 |
| 5 | combined | S_STATE_EXPECTED | S_STATE_LAG | crps | 265 | 0.012332 | 0.012059 | -0.000273 | -0.000972 | 0.000425 |
