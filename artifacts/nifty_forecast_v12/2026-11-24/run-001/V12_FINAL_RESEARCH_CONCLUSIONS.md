# V12 Final Research Conclusions

V12 reconstructed **19,389** accepted risk-neutral expiry laws across the declared methods from authenticated historical option prices. Main traded-mark curves had **2,468** supported date-expiries. The bounded convex-price interpolation, exact mass normalization and forward constraint are reproducible. Option-price shape and forecasts of realized returns remain distinct estimands.

On full combined weekly coverage, the strongest V12 point Brier is **0.229715** from **V12_NATIVE_RV**, and the strongest V12 point CRPS is **0.010677** from **J12_Q_GROUP**. The gain against the original native phase-zero Brier is 0.002013, with adjusted interval -0.002952 to +0.006979. The matched CRPS gain versus V11 is 0.000101, with block-10 adjusted interval -0.000622 to +0.000824. The weekly Brier leader scales the frozen native phase-zero law by realized-risk information. A repeated prior phase under a new ID should be read as a replay. The complete equal-phase mixture produces **0.233211 / 0.010980**. Weekly V12_ETF_SCALE has annualized path-volatility MAE 0.040642 over 265 origins. Monthly V12_INTRA_SCALE has annualized path-volatility MAE 0.039122 over 217 origins. These rankings answer different questions.

The simple weekly nearest-expiry at-the-money IV observable had annualized realized-volatility MAE **0.037814** against **0.046394** for trailing realized volatility on the same 265 origins. Adding the IV inputs to the fitted realized-risk model changed MAE from **0.043246 to 0.040918**. The search-adjusted gain interval was **-0.002096 to +0.006751**. The sign probability and full-distribution scores assess the endpoint return, while these risk scores assess the path of returns to that endpoint. [Market observables](V12_EXPECTATION_VS_REALITY.md).

## Path-volatility increments against exact eligible parents

| horizon | cohort | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | V12_ETF_SCALE | V12_IV_SCALE | path_volatility_mae | 265 | 53 | 0.040642 | 0.040918 | 0.000276 | -0.001791 | 0.002342 |
| 5 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | path_volatility_mae | 265 | 53 | 0.041031 | 0.040918 | -0.000113 | -0.001266 | 0.001039 |
| 5 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | path_volatility_mae | 265 | 53 | 0.040877 | 0.040918 | 0.000041 | -0.002654 | 0.002737 |
| 5 | combined | V12_INTRA_SCALE | V12_IV_SCALE | path_volatility_mae | 263 | 53 | 0.040569 | 0.041008 | 0.000439 | -0.001161 | 0.002039 |
| 5 | combined | V12_IV_BRACKET | V12_IV_SCALE | path_volatility_mae | 264 | 53 | 0.041010 | 0.040790 | -0.000220 | -0.000723 | 0.000283 |
| 5 | combined | V12_IV_LEVEL | V12_RV_SCALE | path_volatility_mae | 265 | 53 | 0.041503 | 0.043246 | 0.001742 | -0.001058 | 0.004543 |
| 5 | combined | V12_IV_SCALE | V12_IV_LEVEL | path_volatility_mae | 265 | 53 | 0.040918 | 0.041503 | 0.000585 | -0.001953 | 0.003123 |
| 21 | combined | V12_ETF_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.039290 | 0.040178 | 0.000888 | — | — |
| 21 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.041006 | 0.040178 | -0.000828 | — | — |
| 21 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.041936 | 0.040178 | -0.001758 | — | — |
| 21 | combined | V12_INTRA_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.039122 | 0.040178 | 0.001056 | — | — |
| 21 | combined | V12_IV_BRACKET | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.039542 | 0.040178 | 0.000636 | — | — |
| 21 | combined | V12_IV_LEVEL | V12_RV_SCALE | path_volatility_mae | 217 | 11 | 0.039995 | 0.040910 | 0.000914 | — | — |
| 21 | combined | V12_IV_SCALE | V12_IV_LEVEL | path_volatility_mae | 217 | 11 | 0.040178 | 0.039995 | -0.000182 | — | — |

| horizon | cohort | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | V12_CONTROL_NOISE | V12_RV_SCALE | path_volatility_mae | 265 | 53 | 0.043260 | 0.043246 | -0.000015 | -0.000551 | 0.000522 |
| 5 | combined | V12_CONTROL_NOISE | V12_RV_PATH | path_volatility_mae | 265 | 53 | 0.043260 | 0.046394 | 0.003134 | -0.015841 | 0.022108 |
| 5 | combined | V12_INTRA_SCALE | V12_RV_SCALE | path_volatility_mae | 263 | 53 | 0.040569 | 0.043344 | 0.002774 | -0.002802 | 0.008351 |
| 5 | combined | V12_INTRA_SCALE | V12_RV_PATH | path_volatility_mae | 263 | 53 | 0.040569 | 0.046384 | 0.005815 | -0.011989 | 0.023618 |
| 5 | combined | V12_IV_BRACKET | V12_RV_SCALE | path_volatility_mae | 264 | 53 | 0.041010 | 0.043109 | 0.002099 | -0.001879 | 0.006078 |
| 5 | combined | V12_IV_BRACKET | V12_RV_PATH | path_volatility_mae | 264 | 53 | 0.041010 | 0.046267 | 0.005257 | -0.012846 | 0.023361 |
| 5 | combined | V12_IV_LAG5 | V12_RV_SCALE | path_volatility_mae | 265 | 53 | 0.041674 | 0.043246 | 0.001571 | -0.000605 | 0.003748 |
| 5 | combined | V12_IV_LAG5 | V12_RV_PATH | path_volatility_mae | 265 | 53 | 0.041674 | 0.046394 | 0.004720 | -0.013393 | 0.022832 |
| 5 | combined | V12_IV_SCALE | V12_RV_SCALE | path_volatility_mae | 265 | 53 | 0.040918 | 0.043246 | 0.002328 | -0.002096 | 0.006751 |
| 5 | combined | V12_IV_SCALE | V12_RV_PATH | path_volatility_mae | 265 | 53 | 0.040918 | 0.046394 | 0.005476 | -0.012423 | 0.023375 |
| 5 | combined | V12_RV_SCALE | V12_RV_PATH | path_volatility_mae | 265 | 53 | 0.043246 | 0.046394 | 0.003148 | -0.015969 | 0.022265 |
| 5 | combined | V12_STRADDLE_SCALE | V12_RV_SCALE | path_volatility_mae | 265 | 53 | 0.041507 | 0.043246 | 0.001738 | -0.001381 | 0.004858 |
| 5 | combined | V12_STRADDLE_SCALE | V12_RV_PATH | path_volatility_mae | 265 | 53 | 0.041507 | 0.046394 | 0.004887 | -0.013345 | 0.023118 |
| 21 | combined | V12_CONTROL_NOISE | V12_RV_SCALE | path_volatility_mae | 217 | 11 | 0.040964 | 0.040910 | -0.000054 | — | — |
| 21 | combined | V12_CONTROL_NOISE | V12_RV_PATH | path_volatility_mae | 217 | 11 | 0.040964 | 0.048044 | 0.007080 | — | — |
| 21 | combined | V12_INTRA_SCALE | V12_RV_SCALE | path_volatility_mae | 217 | 11 | 0.039122 | 0.040910 | 0.001788 | — | — |
| 21 | combined | V12_INTRA_SCALE | V12_RV_PATH | path_volatility_mae | 217 | 11 | 0.039122 | 0.048044 | 0.008923 | — | — |
| 21 | combined | V12_IV_BRACKET | V12_RV_SCALE | path_volatility_mae | 217 | 11 | 0.039542 | 0.040910 | 0.001368 | — | — |
| 21 | combined | V12_IV_BRACKET | V12_RV_PATH | path_volatility_mae | 217 | 11 | 0.039542 | 0.048044 | 0.008503 | — | — |
| 21 | combined | V12_IV_LAG5 | V12_RV_SCALE | path_volatility_mae | 217 | 11 | 0.041475 | 0.040910 | -0.000565 | — | — |
| 21 | combined | V12_IV_LAG5 | V12_RV_PATH | path_volatility_mae | 217 | 11 | 0.041475 | 0.048044 | 0.006570 | — | — |
| 21 | combined | V12_IV_SCALE | V12_RV_SCALE | path_volatility_mae | 217 | 11 | 0.040178 | 0.040910 | 0.000732 | — | — |
| 21 | combined | V12_IV_SCALE | V12_RV_PATH | path_volatility_mae | 217 | 11 | 0.040178 | 0.048044 | 0.007867 | — | — |
| 21 | combined | V12_RV_SCALE | V12_RV_PATH | path_volatility_mae | 217 | 11 | 0.040910 | 0.048044 | 0.007135 | — | — |
| 21 | combined | V12_STRADDLE_SCALE | V12_RV_SCALE | path_volatility_mae | 217 | 11 | 0.039700 | 0.040910 | 0.001210 | — | — |
| 21 | combined | V12_STRADDLE_SCALE | V12_RV_PATH | path_volatility_mae | 217 | 11 | 0.039700 | 0.048044 | 0.008344 | — | — |

## Raw and calibrated pricing laws against realized-return references

| horizon | cohort | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | P12_Q_HIST_FALLBACK | J11_EXCLUDE_B_ROT | brier | 265 | 53 | 0.245870 | 0.244333 | -0.001537 | -0.017049 | 0.013975 |
| 5 | combined | P12_Q_HIST_FALLBACK | J11_EXCLUDE_B_ROT | crps | 265 | 53 | 0.010727 | 0.010777 | 0.000050 | -0.000662 | 0.000762 |
| 5 | combined | P12_Q_HIST_FALLBACK | NEUTRAL | brier | 265 | 53 | 0.245870 | 0.250000 | 0.004130 | -0.031566 | 0.039826 |
| 5 | combined | P12_Q_HIST_FALLBACK | NEUTRAL | crps | 265 | 53 | 0.010727 | 0.011058 | 0.000330 | -0.001006 | 0.001667 |
| 5 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | brier | 265 | 53 | 0.244491 | 0.244333 | -0.000158 | -0.006134 | 0.005818 |
| 5 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | crps | 265 | 53 | 0.010704 | 0.010777 | 0.000073 | -0.000173 | 0.000319 |
| 5 | combined | P12_Q_PHYSICAL_MIX | NEUTRAL | brier | 265 | 53 | 0.244491 | 0.250000 | 0.005509 | -0.038353 | 0.049370 |
| 5 | combined | P12_Q_PHYSICAL_MIX | NEUTRAL | crps | 265 | 53 | 0.010704 | 0.011058 | 0.000353 | -0.001429 | 0.002135 |
| 5 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | brier | 265 | 53 | 0.268655 | 0.244333 | -0.024322 | -0.077598 | 0.028954 |
| 5 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | crps | 265 | 53 | 0.011151 | 0.010777 | -0.000374 | -0.002583 | 0.001836 |
| 5 | combined | Q12_RAW | NEUTRAL | brier | 265 | 53 | 0.268655 | 0.250000 | -0.018655 | -0.049098 | 0.011788 |
| 5 | combined | Q12_RAW | NEUTRAL | crps | 265 | 53 | 0.011151 | 0.011058 | -0.000093 | -0.001026 | 0.000839 |
| 21 | combined | P12_Q_HIST_FALLBACK | J11_EXCLUDE_B_ROT | brier | 199 | 11 | 0.306217 | 0.307581 | 0.001364 | — | — |
| 21 | combined | P12_Q_HIST_FALLBACK | J11_EXCLUDE_B_ROT | crps | 199 | 11 | 0.028165 | 0.029210 | 0.001045 | — | — |
| 21 | combined | P12_Q_HIST_FALLBACK | NEUTRAL | brier | 199 | 11 | 0.306217 | 0.250000 | -0.056217 | — | — |
| 21 | combined | P12_Q_HIST_FALLBACK | NEUTRAL | crps | 199 | 11 | 0.028165 | 0.025474 | -0.002691 | — | — |
| 21 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | brier | 199 | 11 | 0.307439 | 0.307581 | 0.000143 | — | — |
| 21 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | crps | 199 | 11 | 0.028819 | 0.029210 | 0.000392 | — | — |
| 21 | combined | P12_Q_PHYSICAL_MIX | NEUTRAL | brier | 199 | 11 | 0.307439 | 0.250000 | -0.057439 | — | — |
| 21 | combined | P12_Q_PHYSICAL_MIX | NEUTRAL | crps | 199 | 11 | 0.028819 | 0.025474 | -0.003345 | — | — |
| 21 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | brier | 199 | 11 | 0.283476 | 0.307581 | 0.024106 | — | — |
| 21 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | crps | 199 | 11 | 0.026814 | 0.029210 | 0.002396 | — | — |
| 21 | combined | Q12_RAW | NEUTRAL | brier | 199 | 11 | 0.283476 | 0.250000 | -0.033476 | — | — |
| 21 | combined | Q12_RAW | NEUTRAL | crps | 199 | 11 | 0.026814 | 0.025474 | -0.001340 | — | — |

The main evidence is conditional, historical and exposed. The full monthly symmetric forecast remains the primary reference. Point rankings over selected calendar phases or maturity subsets require their adjusted or disjoint checks. There is no independently validated prediction edge in this study. [Full comparisons](V12_COMPLETE_COMPARISON.md) · [Verified laws](verification.json).
