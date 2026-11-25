# V13 Reproduction And Benchmarks

Rebuilt the exact frozen target windows with the inherited cash reference and return convention. Annualized volatility is the square root of 252 times mean squared daily close-to-close log return. Raw IV uses ACT/365, and converted variants match the planned horizon total variance to H trading sessions. Decision timestamps retain next-session 09:10 IST and the V12 archive delay.

Replayed **3,320** V12 atom-level endpoint distributions, **3,558** additional protected laws and **2,890** volatility point forecasts from the original saved coefficients. The maximum risk replay difference was **0**. Verified **22,519** earlier-version files.

| horizon | cohort | model | n | disjoint | mae | rmse | qlike | bias | spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | iv_bracket | 265 | 53 | 0.038336 | 0.048394 | 0.277849 | 0.008045 | 0.609690 |
| 5 | combined | iv_nearest | 265 | 53 | 0.037814 | 0.048184 | 0.276187 | 0.007769 | 0.611711 |
| 5 | combined | prior_etf | 265 | 53 | 0.040642 | 0.056368 | 0.454474 | -0.021134 | 0.560265 |
| 5 | combined | prior_fitted_iv | 265 | 53 | 0.040918 | 0.057118 | 0.472947 | -0.022235 | 0.567662 |
| 5 | combined | prior_fitted_lag5 | 265 | 53 | 0.041674 | 0.057976 | 0.477762 | -0.022558 | 0.586473 |
| 5 | combined | prior_fitted_rv | 265 | 53 | 0.043246 | 0.060737 | 0.533594 | -0.022608 | 0.510969 |
| 5 | combined | prior_intraday | 263 | 53 | 0.040569 | 0.055933 | 0.440956 | -0.020346 | 0.553982 |
| 5 | combined | prior_trailing | 265 | 53 | 0.046394 | 0.061240 | 0.418006 | 0.001389 | 0.503901 |
| 21 | combined | iv_bracket | 217 | 11 | 0.039406 | 0.049414 | 0.267623 | -0.004405 | 0.444422 |
| 21 | combined | iv_nearest | 217 | 11 | 0.039639 | 0.049835 | 0.266465 | -0.003579 | 0.448765 |
| 21 | combined | prior_etf | 217 | 11 | 0.039290 | 0.055809 | 0.450064 | -0.028341 | 0.318725 |
| 21 | combined | prior_fitted_iv | 217 | 11 | 0.040178 | 0.056412 | 0.457758 | -0.029281 | 0.306180 |
| 21 | combined | prior_fitted_lag5 | 217 | 11 | 0.041475 | 0.058335 | 0.491035 | -0.030894 | 0.301668 |
| 21 | combined | prior_fitted_rv | 217 | 11 | 0.040910 | 0.058706 | 0.504587 | -0.029663 | 0.263429 |
| 21 | combined | prior_intraday | 217 | 11 | 0.039122 | 0.054761 | 0.419481 | -0.026428 | 0.337372 |
| 21 | combined | prior_trailing | 217 | 11 | 0.048044 | 0.062015 | 0.487043 | -0.008108 | 0.400273 |

| horizon | cohort | model | n | disjoint | brier | log_loss | accuracy | balanced_accuracy | crps | mae | pinball | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | B_CHANGE | 265 | 53 | 0.246747 | 0.696972 | 0.596226 | 0.610765 | 0.011869 | 0.016103 | 0.005860 | 0.758491 | 0.042534 |
| 5 | later | B_CHANGE | 92 | 19 | 0.156795 | 0.493055 | 0.771739 | 0.774794 | 0.009851 | 0.012852 | 0.004975 | 0.771739 | 0.035836 |
| 5 | combined | J10_STRUCTURAL_BLEND | 265 | 53 | 0.236181 | 0.667575 | 0.637736 | 0.651507 | 0.011043 | 0.015172 | 0.005505 | 0.815094 | 0.048713 |
| 5 | combined | J11_BREADTH_ALL | 265 | 53 | 0.236138 | 0.667636 | 0.637736 | 0.650612 | 0.010960 | 0.015003 | 0.005452 | 0.822642 | 0.050120 |
| 5 | combined | J11_EXCLUDE_B_ROT | 265 | 53 | 0.244333 | 0.682878 | 0.588679 | 0.602218 | 0.010777 | 0.015044 | 0.005343 | 0.807547 | 0.048008 |
| 5 | combined | J12_Q_GROUP | 265 | 53 | 0.241437 | 0.676126 | 0.622642 | 0.637994 | 0.010677 | 0.014897 | 0.005290 | 0.803774 | 0.043636 |
| 5 | combined | NEUTRAL | 265 | 53 | 0.250000 | 0.693147 | 0.528302 | 0.488190 | 0.011058 | 0.015052 | 0.005498 | 0.735849 | 0.039228 |
| 5 | combined | O_NATIVE_PHASE0 | 265 | 53 | 0.231728 | 0.660781 | 0.626415 | 0.633316 | 0.011001 | 0.014687 | 0.005463 | 0.784906 | 0.042772 |
| 5 | combined | PH_NATIVE_PHASE_MIXTURE | 265 | 53 | 0.233211 | 0.661103 | 0.626415 | 0.636001 | 0.010980 | 0.015013 | 0.005444 | 0.777358 | 0.044137 |
| 5 | combined | V12_NATIVE_RV | 265 | 53 | 0.229715 | 0.655524 | 0.626415 | 0.633316 | 0.010896 | 0.014687 | 0.005405 | 0.781132 | 0.041415 |
| 5 | combined | V8_W_STRUCT_EMBARGO_EQ | 92 | 19 | 0.161638 | 0.501592 | 0.771739 | 0.781567 | 0.009262 | 0.012228 | 0.004673 | 0.804348 | 0.039726 |
| 5 | later | V8_W_STRUCT_EMBARGO_EQ | 92 | 19 | 0.161638 | 0.501592 | 0.771739 | 0.781567 | 0.009262 | 0.012228 | 0.004673 | 0.804348 | 0.039726 |
| 21 | combined | B_CHANGE | 217 | 11 | 0.332742 | 0.939315 | 0.493088 | 0.516566 | 0.032497 | 0.041961 | 0.016394 | 0.488479 | 0.074518 |
| 21 | combined | J10_STRUCTURAL_BLEND | 217 | 11 | 0.286258 | 0.779483 | 0.497696 | 0.521829 | 0.030036 | 0.040356 | 0.015057 | 0.645161 | 0.090629 |
| 21 | combined | J11_BREADTH_ALL | 217 | 11 | 0.299436 | 0.812371 | 0.456221 | 0.480285 | 0.031283 | 0.043138 | 0.015596 | 0.622120 | 0.094722 |
| 21 | combined | J11_EXCLUDE_B_ROT | 217 | 11 | 0.306090 | 0.831132 | 0.502304 | 0.536411 | 0.028994 | 0.038419 | 0.014686 | 0.626728 | 0.089992 |
| 21 | combined | J12_Q_GROUP | 199 | 11 | 0.300552 | 0.811255 | 0.487437 | 0.529224 | 0.028081 | 0.036410 | 0.014133 | 0.648241 | 0.085699 |
| 21 | combined | NEUTRAL | 217 | 11 | 0.250000 | 0.693147 | 0.511521 | 0.460742 | 0.025420 | 0.033371 | 0.012678 | 0.635945 | 0.068179 |
| 21 | combined | O_NATIVE_PHASE0 | 217 | 11 | 0.365147 | 0.983668 | 0.387097 | 0.399008 | 0.033337 | 0.042037 | 0.016908 | 0.506912 | 0.082565 |
| 21 | combined | PH_NATIVE_PHASE_MIXTURE | 217 | 11 | 0.290905 | 0.795663 | 0.456221 | 0.483779 | 0.029347 | 0.038706 | 0.014760 | 0.599078 | 0.095326 |
| 21 | combined | V12_NATIVE_RV | 217 | 11 | 0.363025 | 0.974514 | 0.345622 | 0.349310 | 0.032602 | 0.042037 | 0.016448 | 0.529954 | 0.074254 |

[Saved fit IDs and replay receipt](v12-fitted-replay.json) · [Exact V12 per-origin scores](reproduced-endpoint.csv) · [Earlier model replay](protected-endpoint-replay.json) · [V12 research](../../../nifty_forecast_v12/2026-11-24/run-001/NIFTY_V12_RESEARCH.md).
