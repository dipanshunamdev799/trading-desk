# NIFTY V17 — Domestic information networks

The network study connected synchronized stock observations from banking, finance, and IT sleeves with later, independent sector-minus-cash movement and later NIFTY returns, range and volatility. A bank/finance/IT future native segment starts at the first actual native bar open on or after the cutoff and ends 25 minutes later. NIFTY’s reference segment must have the same start and end and contiguous observations. Its own return, volatility and native-sector controls are known by the decision. This eliminates shared price movement inside an outcome interval as a source of apparent earlier prediction. The dated daily stock networks are predictive diagnostics. Individual live index contribution would require contemporaneous official free-float weights and was outside the verifiable inputs.

| cutoff | target | source | aligned | lead r | one day old r | partial r | partial n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | bank_relative | bank_own_last5 | 400 | -0.040980 | -0.051060 | -0.008081 | 368 |
| 09:25 | bank_relative | finance_own_last5 | 400 | 0.113519 | -0.034943 | 0.140303 | 368 |
| 09:25 | finance_relative | bank_own_last5 | 400 | -0.094090 | -0.006648 | -0.034926 | 368 |
| 09:25 | finance_relative | finance_own_last5 | 400 | 0.013817 | -0.023743 | 0.074646 | 368 |
| 09:25 | it_relative | it_own_last5 | 400 | 0.111763 | 0.013310 | 0.083751 | 368 |
| 09:25 | nifty_later | bank_own_last5 | 400 | 0.076759 | -0.080710 | 0.065247 | 368 |
| 09:25 | nifty_later | finance_own_last5 | 400 | 0.070444 | -0.085856 | 0.099440 | 368 |
| 09:25 | nifty_later | it_own_last5 | 400 | 0.014863 | 0.005838 | -0.005454 | 368 |
| 09:25 | nifty_range | bank_own_last5 | 400 | -0.028077 | 0.011178 | -0.023700 | 368 |
| 09:25 | nifty_range | stock_sync | 400 | 0.147145 | 0.104077 | 0.007120 | 368 |
| 09:25 | nifty_volatility | bank_own_last5 | 400 | 0.027257 | -0.011952 | 0.055560 | 368 |
| 09:25 | nifty_volatility | stock_sync | 400 | 0.198821 | 0.139553 | 0.020742 | 368 |
| 09:55 | bank_relative | bank_own_last5 | 400 | 0.029509 | 0.025282 | -0.026218 | 368 |
| 09:55 | bank_relative | finance_own_last5 | 400 | 0.013075 | -0.081707 | 0.001718 | 368 |
| 09:55 | finance_relative | bank_own_last5 | 400 | -0.004665 | 0.024210 | -0.049132 | 368 |
| 09:55 | finance_relative | finance_own_last5 | 400 | 0.040504 | -0.082020 | 0.017118 | 368 |
| 09:55 | it_relative | it_own_last5 | 400 | -0.087617 | 0.006128 | -0.109292 | 368 |
| 09:55 | nifty_later | bank_own_last5 | 400 | -0.048256 | -0.026267 | -0.033458 | 368 |
| 09:55 | nifty_later | finance_own_last5 | 400 | -0.088391 | -0.015621 | -0.123697 | 368 |
| 09:55 | nifty_later | it_own_last5 | 400 | 0.002860 | 0.002653 | 0.038139 | 368 |
| 09:55 | nifty_range | bank_own_last5 | 400 | -0.009134 | -0.085624 | 0.028419 | 368 |
| 09:55 | nifty_range | stock_sync | 400 | 0.165590 | 0.096912 | 0.130831 | 368 |
| 09:55 | nifty_volatility | bank_own_last5 | 400 | -0.085407 | -0.082287 | -0.000960 | 368 |
| 09:55 | nifty_volatility | stock_sync | 400 | 0.149485 | 0.119811 | 0.099604 | 368 |
| 10:20 | bank_relative | bank_own_last5 | 400 | -0.006882 | 0.080910 | -0.028215 | 368 |
| 10:20 | bank_relative | finance_own_last5 | 400 | -0.038393 | -0.035601 | -0.021883 | 368 |
| 10:20 | finance_relative | bank_own_last5 | 400 | 0.072561 | 0.111696 | 0.061680 | 368 |
| 10:20 | finance_relative | finance_own_last5 | 400 | -0.000660 | -0.023962 | 0.014537 | 368 |
| 10:20 | it_relative | it_own_last5 | 400 | 0.068259 | 0.061828 | 0.076352 | 368 |
| 10:20 | nifty_later | bank_own_last5 | 400 | -0.089111 | 0.117784 | -0.033981 | 368 |
| 10:20 | nifty_later | finance_own_last5 | 400 | -0.017159 | 0.035822 | -0.042725 | 368 |
| 10:20 | nifty_later | it_own_last5 | 400 | -0.067850 | 0.011655 | -0.068981 | 368 |
| 10:20 | nifty_range | bank_own_last5 | 400 | 0.004941 | 0.041561 | -0.054470 | 368 |
| 10:20 | nifty_range | stock_sync | 400 | 0.125141 | 0.071656 | 0.028526 | 368 |
| 10:20 | nifty_volatility | bank_own_last5 | 400 | 0.031142 | 0.023203 | -0.025293 | 368 |

Raw lead correlations, one-day-shifted correlations and partial correlations are preserved separately. Partial features learned a training-only prediction of the stock information from market and sector conditions. The direct distributed-lag model combines current and previous-session signals. The sparse variant chooses two residual features on earlier training data at each date. The old-input variant tests delayed features. The predictive comparison uses exact common dates and block intervals. These results support conditional prediction tests. Directional transmission as an economic mechanism needs evidence independent of shared market shocks.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | it_relative | distributed_ridge | own_state | crps | 320 | 320 | 0.001614 | 0.001631 | 0.000017 | -4.00e-06 | 0.000038 |
| 09:25 | nifty_range | distributed_ridge | own_state | crps | 320 | 320 | 0.002064 | 0.002079 | 0.000015 | -0.000034 | 0.000064 |
| 09:25 | finance_relative | distributed_ridge | own_state | crps | 320 | 320 | 0.000594 | 0.000600 | 6.11e-06 | -3.92e-06 | 0.000016 |
| 09:25 | nifty_volatility | distributed_ridge | own_state | crps | 320 | 320 | 0.000931 | 0.000936 | 5.87e-06 | -0.000028 | 0.000039 |
| 09:25 | finance_relative | sparse_residual | own_state | crps | 320 | 320 | 0.000595 | 0.000600 | 5.01e-06 | -5.15e-06 | 0.000015 |
| 10:20 | bank_relative | distributed_ridge | own_state | crps | 320 | 320 | 0.000496 | 0.000499 | 3.05e-06 | -1.53e-06 | 7.63e-06 |
| 09:25 | finance_relative | factor_residual | own_state | crps | 320 | 320 | 0.000597 | 0.000600 | 2.89e-06 | -5.28e-06 | 0.000011 |
| 09:25 | bank_relative | distributed_ridge | own_state | crps | 320 | 320 | 0.000660 | 0.000662 | 2.80e-06 | -4.82e-06 | 0.000010 |
| 10:20 | finance_relative | distributed_ridge | own_state | crps | 320 | 320 | 0.000421 | 0.000422 | 1.67e-06 | -3.73e-06 | 7.08e-06 |
| 10:20 | bank_relative | old_input | own_state | crps | 320 | 320 | 0.000499 | 0.000499 | 3.87e-07 | -3.61e-06 | 4.39e-06 |
| 10:20 | finance_relative | old_input | own_state | crps | 320 | 320 | 0.000422 | 0.000422 | -1.06e-07 | -4.26e-06 | 4.05e-06 |
| 09:25 | finance_relative | old_input | own_state | crps | 320 | 320 | 0.000600 | 0.000600 | -1.08e-07 | -5.66e-06 | 5.45e-06 |
| 10:20 | bank_relative | factor_residual | own_state | crps | 320 | 320 | 0.000500 | 0.000499 | -3.63e-07 | -4.16e-06 | 3.43e-06 |
| 10:20 | nifty_later | distributed_ridge | own_state | crps | 320 | 320 | 0.000786 | 0.000786 | -4.07e-07 | -0.000011 | 0.000010 |
| 09:25 | nifty_volatility | old_input | own_state | crps | 320 | 320 | 0.000938 | 0.000936 | -1.14e-06 | -0.000056 | 0.000053 |
| 09:25 | bank_relative | factor_residual | own_state | crps | 320 | 320 | 0.000664 | 0.000662 | -1.94e-06 | -9.23e-06 | 5.36e-06 |
| 10:20 | finance_relative | factor_residual | own_state | crps | 320 | 320 | 0.000424 | 0.000422 | -1.94e-06 | -6.83e-06 | 2.95e-06 |
| 10:20 | it_relative | sparse_residual | own_state | crps | 320 | 320 | 0.001189 | 0.001187 | -2.00e-06 | -0.000016 | 0.000012 |
| 10:20 | finance_relative | sparse_residual | own_state | crps | 320 | 320 | 0.000424 | 0.000422 | -2.03e-06 | -6.57e-06 | 2.52e-06 |
| 09:25 | bank_relative | sparse_residual | own_state | crps | 320 | 320 | 0.000665 | 0.000662 | -2.23e-06 | -7.99e-06 | 3.52e-06 |
| 10:20 | it_relative | factor_residual | own_state | crps | 320 | 320 | 0.001190 | 0.001187 | -2.44e-06 | -0.000017 | 0.000012 |
| 10:20 | bank_relative | sparse_residual | own_state | crps | 320 | 320 | 0.000502 | 0.000499 | -2.52e-06 | -5.94e-06 | 8.89e-07 |
| 10:20 | nifty_later | old_input | own_state | crps | 320 | 320 | 0.000788 | 0.000786 | -2.63e-06 | -9.73e-06 | 4.46e-06 |
| 09:25 | it_relative | factor_residual | own_state | crps | 320 | 320 | 0.001634 | 0.001631 | -2.70e-06 | -0.000019 | 0.000013 |
| 09:25 | bank_relative | old_input | own_state | crps | 320 | 320 | 0.000666 | 0.000662 | -3.39e-06 | -8.19e-06 | 1.42e-06 |
| 09:25 | nifty_later | sparse_residual | own_state | crps | 320 | 320 | 0.001182 | 0.001177 | -5.08e-06 | -0.000016 | 5.61e-06 |
| 10:20 | it_relative | old_input | own_state | crps | 320 | 320 | 0.001193 | 0.001187 | -5.29e-06 | -0.000015 | 4.30e-06 |
| 10:20 | it_relative | distributed_ridge | own_state | crps | 320 | 320 | 0.001193 | 0.001187 | -5.77e-06 | -0.000019 | 7.10e-06 |
| 10:20 | nifty_later | sparse_residual | own_state | crps | 320 | 320 | 0.000791 | 0.000786 | -5.79e-06 | -0.000013 | 1.09e-06 |
| 09:25 | it_relative | sparse_residual | own_state | crps | 320 | 320 | 0.001637 | 0.001631 | -5.89e-06 | -0.000021 | 9.57e-06 |
| 09:25 | nifty_volatility | factor_residual | own_state | crps | 320 | 320 | 0.000943 | 0.000936 | -6.71e-06 | -0.000058 | 0.000045 |
| 10:20 | nifty_volatility | distributed_ridge | own_state | crps | 320 | 320 | 0.000834 | 0.000826 | -7.56e-06 | -0.000027 | 0.000012 |
| 09:25 | nifty_later | old_input | own_state | crps | 320 | 320 | 0.001185 | 0.001177 | -7.59e-06 | -0.000017 | 1.51e-06 |
| 09:25 | nifty_later | factor_residual | own_state | crps | 320 | 320 | 0.001185 | 0.001177 | -7.91e-06 | -0.000021 | 5.37e-06 |

[Exact segment timestamps](network-observed-segments.csv.gz) · [All lead and partial correlations](network-correlations.csv) · [Date-paired predictive tests](network-matched.csv) · [Network fits and sparse selections](network-fits.json) · [Joint original horizon results](original-timed-matched.csv)
