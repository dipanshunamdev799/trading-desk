# V13 Coherent Market Path Models

Each ensemble has **512** OHLC paths. Empirical candidates draw contiguous matured windows, maintaining dependence between overnight gaps, regular-session returns, highs, lows and closes. State weights use training-scaled features. Rival specifications use historical and implied-risk scaling, domestic drift, asymmetric scale, event and offshore conditioning, or Gaussian diffusion at 24 intraday steps. Every high, low, endpoint, touch and drawdown prediction in a joint forecast derives from that ensemble. Separate regressions are labeled independently. Conditional binomial Monte Carlo error is at most **0.0221** for a hit probability. Statistical uncertainty comes from the historical block resampling.

| horizon | cohort | model | target | n | disjoint | mae | crps | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | diffusion_iv | endpoint_return | 265 | 53 | 0.015051 | 0.010695 | 0.005277 | 0.535849 | 0.815094 | 0.047355 |
| 5 | combined | event_iv | endpoint_return | 265 | 53 | 0.015206 | 0.011088 | 0.005482 | 0.505660 | 0.758491 | 0.043914 |
| 5 | combined | global_iv | endpoint_return | 265 | 53 | 0.015267 | 0.011091 | 0.005482 | 0.528302 | 0.762264 | 0.043695 |
| 5 | combined | random_state_iv | endpoint_return | 265 | 53 | 0.015281 | 0.011098 | 0.005506 | 0.516981 | 0.769811 | 0.044081 |
| 5 | combined | asymmetry_iv | endpoint_return | 265 | 53 | 0.015350 | 0.011103 | 0.005490 | 0.513208 | 0.754717 | 0.043897 |
| 5 | combined | iv_scaled | endpoint_return | 265 | 53 | 0.015409 | 0.011131 | 0.005508 | 0.505660 | 0.762264 | 0.043717 |
| 5 | combined | position_iv | endpoint_return | 265 | 53 | 0.015356 | 0.011140 | 0.005523 | 0.509434 | 0.754717 | 0.043403 |
| 5 | combined | shift_state_iv | endpoint_return | 265 | 53 | 0.015477 | 0.011169 | 0.005522 | 0.498113 | 0.758491 | 0.043655 |
| 5 | combined | hybrid_scaled | endpoint_return | 265 | 53 | 0.015466 | 0.011194 | 0.005553 | 0.498113 | 0.766038 | 0.045157 |
| 5 | combined | state_iv | endpoint_return | 265 | 53 | 0.015537 | 0.011244 | 0.005560 | 0.516981 | 0.758491 | 0.044483 |
| 5 | combined | rv_scaled | endpoint_return | 265 | 53 | 0.015551 | 0.011294 | 0.005615 | 0.494340 | 0.750943 | 0.046531 |
| 5 | combined | empirical_exact | endpoint_return | 265 | 53 | 0.015338 | 0.011319 | 0.005622 | 0.475472 | 0.735849 | 0.038511 |
| 5 | combined | surface_iv | endpoint_return | 265 | 53 | 0.015558 | 0.011334 | 0.005604 | 0.505660 | 0.750943 | 0.043380 |
| 5 | combined | empirical | endpoint_return | 265 | 53 | 0.015438 | 0.011362 | 0.005645 | 0.475472 | 0.713208 | 0.038455 |
| 5 | combined | domestic_drift | endpoint_return | 265 | 53 | 0.016213 | 0.011755 | 0.005810 | 0.456604 | 0.754717 | 0.043635 |
| 5 | combined | diffusion_iv | range | 265 | 53 | 0.008182 | 0.005793 | 0.002864 | 0.449057 | 0.716981 | 0.021638 |
| 5 | combined | asymmetry_iv | range | 265 | 53 | 0.008188 | 0.005955 | 0.002944 | 0.467925 | 0.762264 | 0.022973 |
| 5 | combined | domestic_drift | range | 265 | 53 | 0.008298 | 0.005959 | 0.002940 | 0.460377 | 0.769811 | 0.024011 |
| 5 | combined | iv_scaled | range | 265 | 53 | 0.008191 | 0.005961 | 0.002951 | 0.464151 | 0.766038 | 0.022660 |
| 5 | combined | global_iv | range | 265 | 53 | 0.008262 | 0.005970 | 0.002949 | 0.460377 | 0.769811 | 0.023160 |
| 5 | combined | random_state_iv | range | 265 | 53 | 0.008220 | 0.005982 | 0.002958 | 0.479245 | 0.773585 | 0.022762 |
| 5 | combined | position_iv | range | 265 | 53 | 0.008205 | 0.005982 | 0.002952 | 0.460377 | 0.766038 | 0.022896 |
| 5 | combined | surface_iv | range | 265 | 53 | 0.008252 | 0.005988 | 0.002960 | 0.471698 | 0.754717 | 0.022514 |
| 5 | combined | event_iv | range | 265 | 53 | 0.008300 | 0.005997 | 0.002955 | 0.471698 | 0.750943 | 0.023095 |
| 5 | combined | state_iv | range | 265 | 53 | 0.008267 | 0.006000 | 0.002967 | 0.456604 | 0.750943 | 0.022719 |
| 5 | combined | shift_state_iv | range | 265 | 53 | 0.008305 | 0.006005 | 0.002958 | 0.456604 | 0.758491 | 0.022579 |
| 5 | combined | hybrid_scaled | range | 265 | 53 | 0.008785 | 0.006295 | 0.003114 | 0.471698 | 0.732075 | 0.023512 |
| 5 | combined | rv_scaled | range | 265 | 53 | 0.009824 | 0.006910 | 0.003411 | 0.452830 | 0.743396 | 0.027269 |
| 5 | combined | empirical | range | 265 | 53 | 0.010329 | 0.007896 | 0.003973 | 0.467925 | 0.732075 | 0.027118 |
| 5 | combined | empirical_exact | range | 265 | 53 | 0.010385 | 0.007918 | 0.003972 | 0.464151 | 0.747170 | 0.027029 |
| 5 | combined | diffusion_iv | volatility | 265 | 53 | 0.036689 | 0.025784 | 0.012681 | 0.433962 | 0.762264 | 0.103894 |
| 5 | combined | surface_iv | volatility | 265 | 53 | 0.037612 | 0.027217 | 0.013348 | 0.384906 | 0.709434 | 0.101364 |
| 5 | combined | position_iv | volatility | 265 | 53 | 0.038037 | 0.027297 | 0.013315 | 0.392453 | 0.735849 | 0.101362 |
| 5 | combined | domestic_drift | volatility | 265 | 53 | 0.038359 | 0.027323 | 0.013387 | 0.373585 | 0.709434 | 0.100379 |
| 5 | combined | asymmetry_iv | volatility | 265 | 53 | 0.038181 | 0.027411 | 0.013394 | 0.373585 | 0.716981 | 0.100839 |
| 5 | combined | state_iv | volatility | 265 | 53 | 0.038190 | 0.027416 | 0.013425 | 0.396226 | 0.735849 | 0.099612 |
| 5 | combined | random_state_iv | volatility | 265 | 53 | 0.038141 | 0.027427 | 0.013443 | 0.388679 | 0.705660 | 0.099313 |
| 5 | combined | iv_scaled | volatility | 265 | 53 | 0.038225 | 0.027462 | 0.013429 | 0.373585 | 0.709434 | 0.098883 |
| 5 | combined | global_iv | volatility | 265 | 53 | 0.038460 | 0.027484 | 0.013445 | 0.403774 | 0.735849 | 0.101760 |
| 5 | combined | event_iv | volatility | 265 | 53 | 0.038809 | 0.027728 | 0.013566 | 0.381132 | 0.716981 | 0.101003 |
| 5 | combined | shift_state_iv | volatility | 265 | 53 | 0.039104 | 0.028071 | 0.013784 | 0.373585 | 0.705660 | 0.097714 |
| 5 | combined | hybrid_scaled | volatility | 265 | 53 | 0.039894 | 0.028214 | 0.013756 | 0.407547 | 0.728302 | 0.102602 |
| 5 | combined | rv_scaled | volatility | 265 | 53 | 0.043717 | 0.030453 | 0.014935 | 0.418868 | 0.743396 | 0.117755 |
| 5 | combined | empirical | volatility | 265 | 53 | 0.050144 | 0.037927 | 0.019159 | 0.407547 | 0.762264 | 0.129564 |
| 5 | combined | empirical_exact | volatility | 265 | 53 | 0.050301 | 0.037972 | 0.019070 | 0.418868 | 0.762264 | 0.130399 |
| 21 | combined | diffusion_iv | endpoint_return | 217 | 11 | 0.033688 | 0.025337 | 0.012639 | 0.516129 | 0.741935 | 0.098063 |
| 21 | combined | rv_scaled | endpoint_return | 217 | 11 | 0.035289 | 0.027124 | 0.013440 | 0.396313 | 0.640553 | 0.082741 |
| 21 | combined | surface_iv | endpoint_return | 217 | 11 | 0.035523 | 0.027207 | 0.013366 | 0.364055 | 0.695853 | 0.080976 |
| 21 | combined | hybrid_scaled | endpoint_return | 217 | 11 | 0.035354 | 0.027267 | 0.013519 | 0.391705 | 0.658986 | 0.081917 |
| 21 | combined | global_iv | endpoint_return | 217 | 11 | 0.035615 | 0.027323 | 0.013494 | 0.387097 | 0.663594 | 0.080719 |
| 21 | combined | position_iv | endpoint_return | 217 | 11 | 0.035566 | 0.027383 | 0.013484 | 0.377880 | 0.668203 | 0.082507 |
| 21 | combined | iv_scaled | endpoint_return | 217 | 11 | 0.035629 | 0.027393 | 0.013527 | 0.382488 | 0.658986 | 0.080307 |
| 21 | combined | random_state_iv | endpoint_return | 217 | 11 | 0.035878 | 0.027526 | 0.013592 | 0.387097 | 0.677419 | 0.081991 |
| 21 | combined | state_iv | endpoint_return | 217 | 11 | 0.035167 | 0.027554 | 0.013730 | 0.396313 | 0.654378 | 0.082181 |
| 21 | combined | event_iv | endpoint_return | 217 | 11 | 0.035819 | 0.027574 | 0.013645 | 0.336406 | 0.645161 | 0.077153 |
| 21 | combined | shift_state_iv | endpoint_return | 217 | 11 | 0.035590 | 0.027598 | 0.013788 | 0.350230 | 0.622120 | 0.073901 |
| 21 | combined | empirical | endpoint_return | 217 | 11 | 0.035880 | 0.027673 | 0.013603 | 0.304147 | 0.635945 | 0.071569 |
| 21 | combined | empirical_exact | endpoint_return | 217 | 11 | 0.035923 | 0.027681 | 0.013618 | 0.304147 | 0.631336 | 0.070800 |
| 21 | combined | asymmetry_iv | endpoint_return | 217 | 11 | 0.036430 | 0.027721 | 0.013749 | 0.364055 | 0.645161 | 0.080691 |
| 21 | combined | domestic_drift | endpoint_return | 217 | 11 | 0.040891 | 0.030739 | 0.015243 | 0.285714 | 0.599078 | 0.079956 |
| 21 | combined | diffusion_iv | range | 217 | 11 | 0.022336 | 0.016275 | 0.008039 | 0.313364 | 0.599078 | 0.045217 |
| 21 | combined | domestic_drift | range | 217 | 11 | 0.023986 | 0.017079 | 0.008433 | 0.396313 | 0.709677 | 0.059302 |
| 21 | combined | global_iv | range | 217 | 11 | 0.024601 | 0.018060 | 0.008953 | 0.373272 | 0.672811 | 0.055441 |
| 21 | combined | surface_iv | range | 217 | 11 | 0.024296 | 0.018073 | 0.008986 | 0.387097 | 0.663594 | 0.058120 |
| 21 | combined | random_state_iv | range | 217 | 11 | 0.024587 | 0.018107 | 0.008959 | 0.373272 | 0.668203 | 0.056193 |
| 21 | combined | position_iv | range | 217 | 11 | 0.024729 | 0.018140 | 0.009004 | 0.373272 | 0.695853 | 0.056975 |
| 21 | combined | iv_scaled | range | 217 | 11 | 0.024620 | 0.018162 | 0.008980 | 0.341014 | 0.695853 | 0.055644 |
| 21 | combined | asymmetry_iv | range | 217 | 11 | 0.024857 | 0.018251 | 0.009058 | 0.354839 | 0.682028 | 0.056649 |
| 21 | combined | shift_state_iv | range | 217 | 11 | 0.024596 | 0.018257 | 0.008969 | 0.331797 | 0.677419 | 0.052418 |
| 21 | combined | event_iv | range | 217 | 11 | 0.024756 | 0.018299 | 0.009053 | 0.359447 | 0.691244 | 0.054384 |
| 21 | combined | rv_scaled | range | 217 | 11 | 0.026264 | 0.018419 | 0.009041 | 0.299539 | 0.585253 | 0.064755 |
| 21 | combined | hybrid_scaled | range | 217 | 11 | 0.025806 | 0.018493 | 0.009056 | 0.336406 | 0.589862 | 0.058066 |
| 21 | combined | state_iv | range | 217 | 11 | 0.025364 | 0.018534 | 0.009225 | 0.359447 | 0.649770 | 0.057972 |
| 21 | combined | empirical_exact | range | 217 | 11 | 0.023677 | 0.019522 | 0.009963 | 0.502304 | 0.617512 | 0.058296 |
| 21 | combined | empirical | range | 217 | 11 | 0.023737 | 0.019572 | 0.009980 | 0.488479 | 0.622120 | 0.058525 |
| 21 | combined | diffusion_iv | volatility | 217 | 11 | 0.039190 | 0.029974 | 0.014852 | 0.129032 | 0.327189 | 0.052602 |
| 21 | combined | domestic_drift | volatility | 217 | 11 | 0.041398 | 0.030534 | 0.015145 | 0.433180 | 0.658986 | 0.095696 |
| 21 | combined | random_state_iv | volatility | 217 | 11 | 0.041561 | 0.030757 | 0.015294 | 0.428571 | 0.658986 | 0.095533 |
| 21 | combined | iv_scaled | volatility | 217 | 11 | 0.041537 | 0.030795 | 0.015245 | 0.428571 | 0.645161 | 0.094987 |
| 21 | combined | event_iv | volatility | 217 | 11 | 0.041799 | 0.030877 | 0.015278 | 0.442396 | 0.663594 | 0.094593 |
| 21 | combined | asymmetry_iv | volatility | 217 | 11 | 0.041734 | 0.030914 | 0.015315 | 0.437788 | 0.654378 | 0.095990 |
| 21 | combined | position_iv | volatility | 217 | 11 | 0.041759 | 0.030919 | 0.015369 | 0.414747 | 0.658986 | 0.094227 |
| 21 | combined | surface_iv | volatility | 217 | 11 | 0.041167 | 0.031128 | 0.015637 | 0.442396 | 0.645161 | 0.094122 |
| 21 | combined | global_iv | volatility | 217 | 11 | 0.041914 | 0.031589 | 0.015808 | 0.428571 | 0.635945 | 0.091761 |
| 21 | combined | shift_state_iv | volatility | 217 | 11 | 0.041291 | 0.031696 | 0.015758 | 0.414747 | 0.654378 | 0.087534 |
| 21 | combined | state_iv | volatility | 217 | 11 | 0.043065 | 0.031971 | 0.016030 | 0.410138 | 0.603687 | 0.093067 |
| 21 | combined | hybrid_scaled | volatility | 217 | 11 | 0.044492 | 0.032042 | 0.016060 | 0.317972 | 0.562212 | 0.098650 |
| 21 | combined | rv_scaled | volatility | 217 | 11 | 0.046123 | 0.032758 | 0.016342 | 0.322581 | 0.557604 | 0.109478 |
| 21 | combined | empirical | volatility | 217 | 11 | 0.045177 | 0.038951 | 0.019215 | 0.419355 | 0.774194 | 0.127621 |
| 21 | combined | empirical_exact | volatility | 217 | 11 | 0.045280 | 0.038954 | 0.019182 | 0.433180 | 0.778802 | 0.129234 |

| horizon | model | mean | max |
| --- | --- | --- | --- |
| 5 | diffusion_iv | 0.032636 | 0.148438 |
| 5 | iv_scaled | 0.031265 | 0.113281 |
| 21 | diffusion_iv | 0.035066 | 0.152344 |
| 21 | iv_scaled | 0.032087 | 0.132812 |

[Joint target atoms for five sessions](joint-path-target-atoms-5.npz) · [Joint target atoms for 21 sessions](joint-path-target-atoms-21.npz) · [Simulation seeds and hashes](path-ledger.json).
