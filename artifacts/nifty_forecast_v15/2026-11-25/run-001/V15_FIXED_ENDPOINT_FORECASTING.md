# V15 fixed-endpoint forecasts

The five-session experiment uses checkpoints 0–4. The 21-session experiment scores every daily checkpoint 0–20 and displays 0, 1, 5, 10, 15 and 20 as the registered comparison points. Each origin keeps its original reference price S₀ and the same terminal close Sᴴ throughout. A live-like conditional path uses the actual observed prefix and simulates from Sₜ. The original-horizon return is (Sₜ / S₀) × (Sᴴ / Sₜ) − 1. The remaining-return target is Sᴴ / Sₜ − 1. Whole-window polarity, range and volatility use the previously observed portion, and their remaining-only counterparts score the still-unknown part separately.

## Window and calendar coverage

| horizon | windows | fixed dates | calendar match | first target | last target |
| --- | --- | --- | --- | --- | --- |
| 5 | 265 | 265 | 263 | 2025-10-21 | 2026-11-16 |
| 21 | 217 | 217 | 203 | 2025-12-31 | 2026-11-16 |

The primary historical comparison uses V14's exact Hth observed-session outcomes. In 16 windows the archive-based schedule visible at issue projected a different calendar date. The literal-calendar sensitivity retains the other 466 windows, and the remaining-tenor forecast uses the schedule visible at the decision. Models never use the realized terminal calendar to select an earlier IV. All seven benchmark classes are represented by the old frozen law, deterministic zero remaining return, empirical history, raw IV and GJR restarts, same-time refit and incremental filtering. The price-only stochastic control anchors to the latest price and uses the issue IV. Lower scores are better except accuracy and coverage, where the relevant benchmark is the realized class balance or nominal coverage.

## Registered endpoints

| horizon | checkpoint | model | n | brier | endpoint crps | remaining return crps | endpoint cov80 | endpoint width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0 | frozen | 265 | 0.252084 | 0.010771 | 0.010771 | 0.777358 | 0.043639 |
| 5 | 0 | gjr_restart | 265 | 0.250763 | 0.010922 | 0.010922 | 0.773585 | 0.042067 |
| 5 | 0 | incremental | 265 | 0.248531 | 0.010713 | 0.010713 | 0.796226 | 0.046623 |
| 5 | 0 | iv_restart | 265 | 0.248408 | 0.010682 | 0.010682 | 0.800000 | 0.047500 |
| 5 | 0 | price_only | 265 | 0.248408 | 0.010682 | 0.010682 | 0.800000 | 0.047500 |
| 5 | 1 | frozen | 265 | 0.252084 | 0.010771 | 0.010756 | 0.777358 | 0.043639 |
| 5 | 1 | gjr_restart | 265 | 0.228304 | 0.009666 | 0.009652 | 0.766038 | 0.037996 |
| 5 | 1 | incremental | 265 | 0.223657 | 0.009496 | 0.009483 | 0.800000 | 0.041886 |
| 5 | 1 | iv_restart | 265 | 0.222898 | 0.009471 | 0.009458 | 0.807547 | 0.042653 |
| 5 | 1 | price_only | 265 | 0.222718 | 0.009457 | 0.009445 | 0.811321 | 0.042667 |
| 5 | 2 | frozen | 265 | 0.252084 | 0.010771 | 0.010742 | 0.777358 | 0.043639 |
| 5 | 2 | gjr_restart | 265 | 0.186700 | 0.008436 | 0.008417 | 0.773585 | 0.033062 |
| 5 | 2 | incremental | 265 | 0.182627 | 0.008296 | 0.008279 | 0.815094 | 0.036134 |
| 5 | 2 | iv_restart | 265 | 0.182228 | 0.008280 | 0.008263 | 0.807547 | 0.036747 |
| 5 | 2 | price_only | 265 | 0.181173 | 0.008285 | 0.008269 | 0.807547 | 0.036818 |
| 5 | 3 | frozen | 265 | 0.252084 | 0.010771 | 0.010727 | 0.777358 | 0.043639 |
| 5 | 3 | gjr_restart | 265 | 0.148805 | 0.006720 | 0.006711 | 0.784906 | 0.027264 |
| 5 | 3 | incremental | 265 | 0.146173 | 0.006643 | 0.006637 | 0.818868 | 0.029566 |
| 5 | 3 | iv_restart | 265 | 0.145588 | 0.006652 | 0.006645 | 0.807547 | 0.030047 |
| 5 | 3 | price_only | 265 | 0.145114 | 0.006644 | 0.006638 | 0.811321 | 0.030138 |
| 5 | 4 | frozen | 265 | 0.252084 | 0.010771 | 0.010718 | 0.777358 | 0.043639 |
| 5 | 4 | gjr_restart | 265 | 0.097863 | 0.004682 | 0.004678 | 0.803774 | 0.019742 |
| 5 | 4 | incremental | 265 | 0.097668 | 0.004648 | 0.004645 | 0.811321 | 0.020915 |
| 5 | 4 | iv_restart | 265 | 0.097811 | 0.004655 | 0.004652 | 0.822642 | 0.021225 |
| 5 | 4 | price_only | 265 | 0.097616 | 0.004679 | 0.004677 | 0.822642 | 0.021368 |
| 21 | 0 | frozen | 217 | 0.253372 | 0.024788 | 0.024788 | 0.718894 | 0.083314 |
| 21 | 0 | gjr_restart | 217 | 0.251376 | 0.024694 | 0.024694 | 0.709677 | 0.083754 |
| 21 | 0 | incremental | 217 | 0.247623 | 0.024840 | 0.024840 | 0.760369 | 0.096071 |
| 21 | 0 | iv_restart | 217 | 0.247721 | 0.025027 | 0.025027 | 0.751152 | 0.098733 |
| 21 | 0 | price_only | 217 | 0.247721 | 0.025027 | 0.025027 | 0.751152 | 0.098733 |
| 21 | 1 | frozen | 217 | 0.253372 | 0.024788 | 0.024798 | 0.718894 | 0.083314 |
| 21 | 1 | gjr_restart | 217 | 0.241962 | 0.024220 | 0.024239 | 0.686636 | 0.081943 |
| 21 | 1 | incremental | 217 | 0.240118 | 0.024397 | 0.024418 | 0.728111 | 0.094001 |
| 21 | 1 | iv_restart | 217 | 0.241767 | 0.024591 | 0.024610 | 0.741935 | 0.096664 |
| 21 | 1 | price_only | 217 | 0.241733 | 0.024638 | 0.024657 | 0.746544 | 0.096417 |
| 21 | 5 | frozen | 217 | 0.253372 | 0.024788 | 0.024902 | 0.718894 | 0.083314 |
| 21 | 5 | gjr_restart | 217 | 0.221244 | 0.022025 | 0.022132 | 0.691244 | 0.073826 |
| 21 | 5 | incremental | 217 | 0.222079 | 0.022184 | 0.022284 | 0.764977 | 0.084241 |
| 21 | 5 | iv_restart | 217 | 0.218092 | 0.022203 | 0.022306 | 0.755760 | 0.086659 |
| 21 | 5 | price_only | 217 | 0.218198 | 0.022524 | 0.022625 | 0.732719 | 0.085851 |
| 21 | 10 | frozen | 217 | 0.253372 | 0.024788 | 0.025085 | 0.718894 | 0.083314 |
| 21 | 10 | gjr_restart | 217 | 0.178601 | 0.018725 | 0.018919 | 0.700461 | 0.061556 |
| 21 | 10 | incremental | 217 | 0.176964 | 0.018645 | 0.018818 | 0.783410 | 0.070696 |
| 21 | 10 | iv_restart | 217 | 0.173269 | 0.018509 | 0.018689 | 0.792627 | 0.072791 |
| 21 | 10 | price_only | 217 | 0.174910 | 0.019132 | 0.019316 | 0.732719 | 0.071016 |
| 21 | 15 | frozen | 217 | 0.253372 | 0.024788 | 0.025199 | 0.718894 | 0.083314 |
| 21 | 15 | gjr_restart | 217 | 0.137542 | 0.013367 | 0.013505 | 0.705069 | 0.046823 |
| 21 | 15 | incremental | 217 | 0.134905 | 0.013046 | 0.013175 | 0.760369 | 0.053071 |
| 21 | 15 | iv_restart | 217 | 0.132261 | 0.013080 | 0.013213 | 0.774194 | 0.054508 |
| 21 | 15 | price_only | 217 | 0.133400 | 0.013511 | 0.013648 | 0.741935 | 0.052859 |
| 21 | 20 | frozen | 217 | 0.253372 | 0.024788 | 0.025254 | 0.718894 | 0.083314 |
| 21 | 20 | gjr_restart | 217 | 0.044799 | 0.005039 | 0.005123 | 0.778802 | 0.020368 |
| 21 | 20 | incremental | 217 | 0.043511 | 0.005006 | 0.005089 | 0.788018 | 0.021852 |
| 21 | 20 | iv_restart | 217 | 0.044056 | 0.005016 | 0.005097 | 0.801843 | 0.022271 |
| 21 | 20 | price_only | 217 | 0.043775 | 0.005239 | 0.005333 | 0.755760 | 0.021552 |

## Matched updated-window gains versus restarted IV

| horizon | candidate | metric | n | model | control | gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | gjr_restart | brier | 265 | 0.165418 | 0.162131 | -0.003287 | -0.008205 | 0.001631 |
| 5 | gjr_restart | endpoint_crps | 265 | 0.007376 | 0.007264 | -0.000112 | -0.000267 | 0.000044 |
| 5 | gjr_restart | remaining_return_crps | 265 | 0.007365 | 0.007255 | -0.000110 | -0.000264 | 0.000044 |
| 5 | gjr_restart | vol_mae | 265 | 0.023734 | 0.023477 | -0.000257 | -0.002935 | 0.002421 |
| 5 | gjr_restart | range_crps | 265 | 0.004465 | 0.004173 | -0.000292 | -0.000749 | 0.000165 |
| 5 | gjr_restart | joint_energy | 265 | 0.458911 | 0.448150 | -0.010761 | -0.027595 | 0.006073 |
| 5 | full | brier | 265 | 0.161190 | 0.162131 | 0.000942 | -0.011126 | 0.013010 |
| 5 | full | endpoint_crps | 265 | 0.007496 | 0.007264 | -0.000231 | -0.000725 | 0.000263 |
| 5 | full | remaining_return_crps | 265 | 0.007487 | 0.007255 | -0.000232 | -0.000728 | 0.000264 |
| 5 | full | vol_mae | 265 | 0.022906 | 0.023477 | 0.000571 | -0.001347 | 0.002489 |
| 5 | full | range_crps | 265 | 0.004395 | 0.004173 | -0.000222 | -0.000434 | -0.000010 |
| 5 | full | joint_energy | 265 | 0.464088 | 0.448150 | -0.015937 | -0.042046 | 0.010171 |
| 5 | historical | brier | 265 | 0.166870 | 0.162131 | -0.004738 | -0.014546 | 0.005069 |
| 5 | historical | endpoint_crps | 265 | 0.007601 | 0.007264 | -0.000337 | -0.000755 | 0.000082 |
| 5 | historical | remaining_return_crps | 265 | 0.007592 | 0.007255 | -0.000337 | -0.000756 | 0.000082 |
| 5 | historical | vol_mae | 265 | 0.029093 | 0.023477 | -0.005616 | -0.014260 | 0.003028 |
| 5 | historical | range_crps | 265 | 0.005012 | 0.004173 | -0.000839 | -0.002127 | 0.000449 |
| 5 | historical | joint_energy | 265 | 0.491348 | 0.448150 | -0.043198 | -0.106190 | 0.019794 |
| 5 | refit | brier | 265 | 0.160464 | 0.162131 | 0.001667 | -0.008631 | 0.011965 |
| 5 | refit | endpoint_crps | 265 | 0.007412 | 0.007264 | -0.000148 | -0.000605 | 0.000309 |
| 5 | refit | remaining_return_crps | 265 | 0.007405 | 0.007255 | -0.000150 | -0.000610 | 0.000310 |
| 5 | refit | vol_mae | 265 | 0.023012 | 0.023477 | 0.000465 | -0.001476 | 0.002406 |
| 5 | refit | range_crps | 265 | 0.004384 | 0.004173 | -0.000211 | -0.000415 | -0.000008 |
| 5 | refit | joint_energy | 265 | 0.460358 | 0.448150 | -0.012208 | -0.037022 | 0.012606 |
| 5 | incremental | brier | 265 | 0.162531 | 0.162131 | -0.000400 | -0.002021 | 0.001221 |
| 5 | incremental | endpoint_crps | 265 | 0.007270 | 0.007264 | -0.000006 | -0.000057 | 0.000045 |
| 5 | incremental | remaining_return_crps | 265 | 0.007261 | 0.007255 | -0.000006 | -0.000057 | 0.000044 |
| 5 | incremental | vol_mae | 265 | 0.023114 | 0.023477 | 0.000363 | -0.000552 | 0.001277 |
| 5 | incremental | range_crps | 265 | 0.004161 | 0.004173 | 0.000012 | -0.000094 | 0.000117 |
| 5 | incremental | joint_energy | 265 | 0.447559 | 0.448150 | 0.000592 | -0.003255 | 0.004438 |
| 5 | hybrid | brier | 265 | 0.164585 | 0.162131 | -0.002453 | -0.005430 | 0.000523 |
| 5 | hybrid | endpoint_crps | 265 | 0.007291 | 0.007264 | -0.000027 | -0.000112 | 0.000058 |
| 5 | hybrid | remaining_return_crps | 265 | 0.007281 | 0.007255 | -0.000027 | -0.000112 | 0.000058 |
| 5 | hybrid | vol_mae | 265 | 0.022952 | 0.023477 | 0.000525 | -0.001141 | 0.002192 |
| 5 | hybrid | range_crps | 265 | 0.004167 | 0.004173 | 0.000006 | -0.000170 | 0.000182 |
| 5 | hybrid | joint_energy | 265 | 0.450300 | 0.448150 | -0.002150 | -0.011261 | 0.006962 |
| 5 | vol_state | brier | 265 | 0.163227 | 0.162131 | -0.001096 | -0.003008 | 0.000817 |
| 5 | vol_state | endpoint_crps | 265 | 0.007280 | 0.007264 | -0.000015 | -0.000075 | 0.000045 |
| 5 | vol_state | remaining_return_crps | 265 | 0.007269 | 0.007255 | -0.000015 | -0.000075 | 0.000045 |
| 5 | vol_state | vol_mae | 265 | 0.023081 | 0.023477 | 0.000396 | -0.000914 | 0.001707 |
| 5 | vol_state | range_crps | 265 | 0.004183 | 0.004173 | -0.000010 | -0.000165 | 0.000145 |
| 5 | vol_state | joint_energy | 265 | 0.448505 | 0.448150 | -0.000355 | -0.006990 | 0.006280 |
| 5 | analogue | brier | 265 | 0.165709 | 0.162131 | -0.003578 | -0.010506 | 0.003350 |
| 5 | analogue | endpoint_crps | 265 | 0.007491 | 0.007264 | -0.000227 | -0.000561 | 0.000107 |
| 5 | analogue | remaining_return_crps | 265 | 0.007481 | 0.007255 | -0.000226 | -0.000557 | 0.000105 |
| 5 | analogue | vol_mae | 265 | 0.023775 | 0.023477 | -0.000298 | -0.003637 | 0.003042 |
| 5 | analogue | range_crps | 265 | 0.004353 | 0.004173 | -0.000180 | -0.000516 | 0.000157 |
| 5 | analogue | joint_energy | 265 | 0.464707 | 0.448150 | -0.016556 | -0.039494 | 0.006381 |
| 21 | gjr_restart | brier | 217 | 0.169657 | 0.166627 | -0.003030 | -0.009673 | 0.003614 |
| 21 | gjr_restart | endpoint_crps | 217 | 0.016949 | 0.016893 | -0.000056 | -0.000564 | 0.000451 |
| 21 | gjr_restart | remaining_return_crps | 217 | 0.017073 | 0.017010 | -0.000063 | -0.000564 | 0.000439 |
| 21 | gjr_restart | vol_mae | 217 | 0.018841 | 0.018871 | 0.000030 | -0.005019 | 0.005078 |
| 21 | gjr_restart | range_crps | 217 | 0.010160 | 0.010019 | -0.000141 | -0.001823 | 0.001541 |
| 21 | gjr_restart | joint_energy | 217 | 0.502234 | 0.498345 | -0.003888 | -0.031348 | 0.023571 |
| 21 | full | brier | 217 | 0.178250 | 0.166627 | -0.011623 | -0.040062 | 0.016815 |
| 21 | full | endpoint_crps | 217 | 0.018636 | 0.016893 | -0.001743 | -0.005110 | 0.001624 |
| 21 | full | remaining_return_crps | 217 | 0.018787 | 0.017010 | -0.001776 | -0.005215 | 0.001662 |
| 21 | full | vol_mae | 217 | 0.020801 | 0.018871 | -0.001930 | -0.005303 | 0.001443 |
| 21 | full | range_crps | 217 | 0.010791 | 0.010019 | -0.000772 | -0.001948 | 0.000404 |
| 21 | full | joint_energy | 217 | 0.551250 | 0.498345 | -0.052904 | -0.144924 | 0.039116 |
| 21 | historical | brier | 217 | 0.190981 | 0.166627 | -0.024354 | -0.048392 | -0.000315 |
| 21 | historical | endpoint_crps | 217 | 0.018285 | 0.016893 | -0.001392 | -0.003538 | 0.000753 |
| 21 | historical | remaining_return_crps | 217 | 0.018424 | 0.017010 | -0.001413 | -0.003587 | 0.000760 |
| 21 | historical | vol_mae | 217 | 0.024269 | 0.018871 | -0.005398 | -0.016172 | 0.005376 |
| 21 | historical | range_crps | 217 | 0.011808 | 0.010019 | -0.001789 | -0.005044 | 0.001466 |
| 21 | historical | joint_energy | 217 | 0.560344 | 0.498345 | -0.061999 | -0.154483 | 0.030485 |
| 21 | refit | brier | 217 | 0.177144 | 0.166627 | -0.010517 | -0.038816 | 0.017783 |
| 21 | refit | endpoint_crps | 217 | 0.018554 | 0.016893 | -0.001661 | -0.005070 | 0.001749 |
| 21 | refit | remaining_return_crps | 217 | 0.018707 | 0.017010 | -0.001697 | -0.005181 | 0.001787 |
| 21 | refit | vol_mae | 217 | 0.020826 | 0.018871 | -0.001955 | -0.005392 | 0.001482 |
| 21 | refit | range_crps | 217 | 0.010745 | 0.010019 | -0.000726 | -0.001818 | 0.000365 |
| 21 | refit | joint_energy | 217 | 0.549231 | 0.498345 | -0.050886 | -0.143143 | 0.041372 |
| 21 | incremental | brier | 217 | 0.168683 | 0.166627 | -0.002056 | -0.008021 | 0.003908 |
| 21 | incremental | endpoint_crps | 217 | 0.016893 | 0.016893 | -0.000000 | -0.000653 | 0.000653 |
| 21 | incremental | remaining_return_crps | 217 | 0.017008 | 0.017010 | 0.000002 | -0.000664 | 0.000668 |
| 21 | incremental | vol_mae | 217 | 0.017856 | 0.018871 | 0.001015 | -0.001020 | 0.003050 |
| 21 | incremental | range_crps | 217 | 0.009803 | 0.010019 | 0.000216 | -0.000160 | 0.000592 |
| 21 | incremental | joint_energy | 217 | 0.494864 | 0.498345 | 0.003482 | -0.011634 | 0.018597 |
| 21 | hybrid | brier | 217 | 0.170410 | 0.166627 | -0.003783 | -0.009514 | 0.001947 |
| 21 | hybrid | endpoint_crps | 217 | 0.016962 | 0.016893 | -0.000069 | -0.000489 | 0.000351 |
| 21 | hybrid | remaining_return_crps | 217 | 0.017085 | 0.017010 | -0.000074 | -0.000492 | 0.000343 |
| 21 | hybrid | vol_mae | 217 | 0.018357 | 0.018871 | 0.000514 | -0.004978 | 0.006005 |
| 21 | hybrid | range_crps | 217 | 0.010026 | 0.010019 | -0.000007 | -0.001428 | 0.001414 |
| 21 | hybrid | joint_energy | 217 | 0.501069 | 0.498345 | -0.002724 | -0.027895 | 0.022448 |
| 21 | vol_state | brier | 217 | 0.168162 | 0.166627 | -0.001535 | -0.005772 | 0.002702 |
| 21 | vol_state | endpoint_crps | 217 | 0.016880 | 0.016893 | 0.000013 | -0.000309 | 0.000335 |
| 21 | vol_state | remaining_return_crps | 217 | 0.017001 | 0.017010 | 0.000009 | -0.000311 | 0.000330 |
| 21 | vol_state | vol_mae | 217 | 0.018007 | 0.018871 | 0.000864 | -0.003776 | 0.005504 |
| 21 | vol_state | range_crps | 217 | 0.009947 | 0.010019 | 0.000072 | -0.001045 | 0.001189 |
| 21 | vol_state | joint_energy | 217 | 0.497222 | 0.498345 | 0.001124 | -0.019254 | 0.021502 |
| 21 | analogue | brier | 217 | 0.186115 | 0.166627 | -0.019488 | -0.041464 | 0.002489 |
| 21 | analogue | endpoint_crps | 217 | 0.018280 | 0.016893 | -0.001387 | -0.003408 | 0.000634 |
| 21 | analogue | remaining_return_crps | 217 | 0.018413 | 0.017010 | -0.001402 | -0.003431 | 0.000626 |
| 21 | analogue | vol_mae | 217 | 0.020191 | 0.018871 | -0.001321 | -0.005256 | 0.002615 |
| 21 | analogue | range_crps | 217 | 0.010948 | 0.010019 | -0.000929 | -0.002180 | 0.000323 |
| 21 | analogue | joint_energy | 217 | 0.543204 | 0.498345 | -0.044859 | -0.098696 | 0.008978 |

## Clean mechanical comparisons under one lognormal law

| horizon | checkpoint | model | n | brier | crps | remaining brier | remaining crps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0 | same_law_no_updates | 265 | 0.250000 | 0.010736 | 0.250000 | 0.010736 |
| 5 | 0 | same_law_price_and_shorter | 265 | 0.250000 | 0.010736 | 0.250000 | 0.010736 |
| 5 | 0 | same_law_shorter_only | 265 | 0.250000 | 0.010736 | 0.250000 | 0.010736 |
| 5 | 0 | same_law_with_fresh_IV | 265 | 0.250000 | 0.010736 | 0.250000 | 0.010736 |
| 5 | 4 | same_law_no_updates | 265 | 0.250000 | 0.010736 | 0.323157 | 0.010682 |
| 5 | 4 | same_law_price_and_shorter | 265 | 0.097484 | 0.004689 | 0.250000 | 0.004686 |
| 5 | 4 | same_law_shorter_only | 265 | 0.250000 | 0.011719 | 0.388455 | 0.011656 |
| 5 | 4 | same_law_with_fresh_IV | 265 | 0.097007 | 0.004666 | 0.250000 | 0.004663 |
| 21 | 0 | same_law_no_updates | 217 | 0.250000 | 0.025143 | 0.250000 | 0.025143 |
| 21 | 0 | same_law_price_and_shorter | 217 | 0.250000 | 0.025143 | 0.250000 | 0.025143 |
| 21 | 0 | same_law_shorter_only | 217 | 0.250000 | 0.025143 | 0.250000 | 0.025143 |
| 21 | 0 | same_law_with_fresh_IV | 217 | 0.250000 | 0.025143 | 0.250000 | 0.025143 |
| 21 | 20 | same_law_no_updates | 217 | 0.250000 | 0.025143 | 0.342176 | 0.025607 |
| 21 | 20 | same_law_price_and_shorter | 217 | 0.044540 | 0.005247 | 0.250000 | 0.005341 |
| 21 | 20 | same_law_shorter_only | 217 | 0.250000 | 0.029452 | 0.454778 | 0.030006 |
| 21 | 20 | same_law_with_fresh_IV | 217 | 0.045104 | 0.005029 | 0.250000 | 0.005109 |

## Interval score leaders at issue

| horizon | model | n | endpoint is80 | endpoint cov80 | endpoint width80 |
| --- | --- | --- | --- | --- | --- |
| 5 | iv_restart | 265 | 0.068489 | 0.800000 | 0.047500 |
| 5 | price_only | 265 | 0.068489 | 0.800000 | 0.047500 |
| 5 | shock_persistence | 265 | 0.068489 | 0.800000 | 0.047500 |
| 21 | gjr_restart | 217 | 0.167267 | 0.709677 | 0.083754 |
| 21 | frozen | 217 | 0.167613 | 0.718894 | 0.083314 |
| 21 | particle | 217 | 0.168319 | 0.700461 | 0.083348 |

[All daily checkpoint scores](checkpoint-leaderboard.csv) [Literal calendar sensitivity](literal-calendar-leaderboard.csv) [All matched evidence](matched-window-evidence.csv) [Fixed timestamps](update-calendar.csv) [Historical forecast case](historical-fixed-endpoint-updates.png) [Exact elapsed-time and price-anchor controls](mechanical-same-law-evidence.csv)
