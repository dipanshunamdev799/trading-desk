# NIFTY V17 — Cross-instrument price discovery

The direct cross-instrument tests measured observed NIFTYBEES relative to NIFTY and BANKBEES relative to BANK NIFTY at a common mark. A separate feature demeans tracking against earlier same-clock observations. Future ETF and underlying returns start after the decision and end at the same observed timestamp. Their difference distinguishes apparent tracking normalization from a forecast of later cash. The NIFTY pair uses 30 forward minutes. The bank pair uses an aligned 25-minute native interval where complete. Forecast returns are in arithmetic equivalents of synchronized log ratios. Same-day distributions, stale marks and the observed return differential can affect the basis. Relative stock and ETF comparisons have historical price/volume coverage, with wider uncertainty around actual spreads and fund distributions. Executable spread, financing carry and dividend impacts are unverified for the full intraday window.

| cutoff | target | source | aligned | lead r | one day old r | partial r | partial n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | nifty_cash_leg | nifty_etf_tracking | 400 | -0.003258 | 0.072513 | -0.033525 | 368 |
| 09:25 | nifty_etf_leg | nifty_etf_tracking | 400 | 0.105798 | 0.053752 | -0.014078 | 368 |
| 09:25 | nifty_basis_leg | nifty_etf_tracking | 400 | 0.338915 | -0.064935 | 0.074486 | 368 |
| 09:25 | bank_index_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 09:25 | bank_etf_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 09:25 | bank_basis_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 09:55 | nifty_cash_leg | nifty_etf_tracking | 400 | 0.069188 | 0.047649 | 0.016631 | 368 |
| 09:55 | nifty_etf_leg | nifty_etf_tracking | 400 | 0.084447 | 0.034529 | 0.005159 | 368 |
| 09:55 | nifty_basis_leg | nifty_etf_tracking | 400 | 0.049425 | -0.056296 | -0.052775 | 368 |
| 09:55 | bank_index_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 09:55 | bank_etf_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 09:55 | bank_basis_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 10:20 | nifty_cash_leg | nifty_etf_tracking | 400 | -0.107352 | 0.116395 | -0.039723 | 368 |
| 10:20 | nifty_etf_leg | nifty_etf_tracking | 400 | -0.084137 | 0.107001 | -0.049477 | 368 |
| 10:20 | nifty_basis_leg | nifty_etf_tracking | 400 | 0.104549 | -0.055510 | -0.037899 | 368 |
| 10:20 | bank_index_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 10:20 | bank_etf_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 10:20 | bank_basis_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 12:30 | nifty_cash_leg | nifty_etf_tracking | 400 | -0.023297 | -0.135800 | 0.011152 | 368 |
| 12:30 | nifty_etf_leg | nifty_etf_tracking | 400 | -0.032883 | -0.130038 | 0.001310 | 368 |
| 12:30 | nifty_basis_leg | nifty_etf_tracking | 400 | -0.031756 | 0.052956 | -0.049222 | 368 |
| 12:30 | bank_index_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 12:30 | bank_etf_leg | bank_etf_tracking | 0 | — | — | — | 0 |
| 12:30 | bank_basis_leg | bank_etf_tracking | 0 | — | — | — | 0 |

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | nifty_basis_leg | distributed_ridge | own_state | crps | 320 | 320 | 0.000291 | 0.000294 | 3.44e-06 | -6.61e-07 | 7.54e-06 |
| 09:25 | nifty_basis_leg | factor_residual | own_state | crps | 320 | 320 | 0.000295 | 0.000294 | -2.96e-07 | -3.60e-06 | 3.01e-06 |
| 09:25 | nifty_cash_leg | distributed_ridge | own_state | crps | 320 | 320 | 0.001185 | 0.001177 | -7.58e-06 | -0.000018 | 3.00e-06 |
| 09:25 | nifty_cash_leg | factor_residual | own_state | crps | 320 | 320 | 0.001183 | 0.001177 | -6.16e-06 | -0.000016 | 3.67e-06 |
| 09:25 | nifty_etf_leg | distributed_ridge | own_state | crps | 320 | 320 | 0.001099 | 0.001091 | -7.24e-06 | -0.000015 | 8.96e-07 |
| 09:25 | nifty_etf_leg | factor_residual | own_state | crps | 320 | 320 | 0.001099 | 0.001091 | -7.47e-06 | -0.000018 | 3.53e-06 |
| 10:20 | nifty_basis_leg | distributed_ridge | own_state | crps | 320 | 320 | 0.000217 | 0.000216 | -1.23e-06 | -3.26e-06 | 8.12e-07 |
| 10:20 | nifty_basis_leg | factor_residual | own_state | crps | 320 | 320 | 0.000217 | 0.000216 | -1.65e-06 | -3.66e-06 | 3.53e-07 |
| 10:20 | nifty_cash_leg | distributed_ridge | own_state | crps | 320 | 320 | 0.000786 | 0.000786 | -8.10e-08 | -8.69e-06 | 8.53e-06 |
| 10:20 | nifty_cash_leg | factor_residual | own_state | crps | 320 | 320 | 0.000792 | 0.000786 | -6.15e-06 | -0.000013 | 5.90e-07 |
| 10:20 | nifty_etf_leg | distributed_ridge | own_state | crps | 320 | 320 | 0.000744 | 0.000746 | 1.76e-06 | -7.47e-06 | 0.000011 |
| 10:20 | nifty_etf_leg | factor_residual | own_state | crps | 320 | 320 | 0.000752 | 0.000746 | -6.30e-06 | -0.000013 | 3.69e-07 |

Domestic cash/front-future observations, previous same-contract differential, near-curve state and prior option parity came through the dated inherited daily archive. Intraday futures and expiry-conditioned leg attribution need an authenticated dated sample. Expiry and expired-future requests returned HTTP 401 with the available authentication. The study therefore tested lagged basis as a predictor and measured subsequent adjustment on synchronized ETF and underlying legs.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | r30 | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250314 | 0.248972 | -0.001342 | -0.006090 | 0.003407 |
| 09:25 | r30 | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001263 | 0.001256 | -7.07e-06 | -0.000024 | 9.90e-06 |
| 09:25 | regular_residual | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249682 | 0.247995 | -0.001687 | -0.006882 | 0.003508 |
| 09:25 | regular_residual | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.003538 | 0.003528 | -9.49e-06 | -0.000057 | 0.000038 |
| 09:25 | remaining_range | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002270 | 0.002238 | -0.000032 | -0.000132 | 0.000069 |
| 09:25 | remaining_range | cross_instrument_residual | native_control | crps | 257 | 257 | 0.002270 | 0.002218 | -0.000052 | -0.000159 | 0.000055 |
| 09:25 | remaining_vol | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000996 | 0.000989 | -6.23e-06 | -0.000083 | 0.000071 |
| 09:25 | remaining_vol | cross_instrument_residual | native_control | crps | 257 | 257 | 0.000996 | 0.000974 | -0.000022 | -0.000100 | 0.000056 |
| 09:25 | touch_down | etf_touch | native_control | brier | 257 | 257 | 0.229531 | 0.229799 | 0.000268 | -0.002449 | 0.002984 |
| 09:25 | touch_down | etf_touch | native_control | crps | 257 | 257 | 0.229531 | 0.229799 | 0.000268 | -0.002449 | 0.002984 |
| 09:25 | touch_up | etf_touch | native_control | brier | 257 | 257 | 0.214712 | 0.215722 | 0.001011 | -0.001833 | 0.003855 |
| 09:25 | touch_up | etf_touch | native_control | crps | 257 | 257 | 0.214712 | 0.215722 | 0.001011 | -0.001833 | 0.003855 |
| 10:20 | r30 | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.262813 | 0.260102 | -0.002711 | -0.008473 | 0.003051 |
| 10:20 | r30 | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000818 | 0.000813 | -4.31e-06 | -0.000015 | 6.70e-06 |
| 10:20 | regular_residual | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249182 | 0.247850 | -0.001332 | -0.007533 | 0.004869 |
| 10:20 | regular_residual | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002938 | 0.002921 | -0.000017 | -0.000060 | 0.000025 |
| 10:20 | remaining_range | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002097 | 0.002043 | -0.000054 | -0.000162 | 0.000054 |
| 10:20 | remaining_range | cross_instrument_residual | native_control | crps | 257 | 257 | 0.002097 | 0.002017 | -0.000080 | -0.000213 | 0.000053 |
| 10:20 | remaining_vol | cross_instrument_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000892 | 0.000888 | -3.42e-06 | -0.000073 | 0.000066 |
| 10:20 | remaining_vol | cross_instrument_residual | native_control | crps | 257 | 257 | 0.000892 | 0.000874 | -0.000017 | -0.000085 | 0.000050 |
| 10:20 | touch_down | etf_touch | native_control | brier | 257 | 257 | 0.220536 | 0.220445 | -0.000091 | -0.002421 | 0.002239 |
| 10:20 | touch_down | etf_touch | native_control | crps | 257 | 257 | 0.220536 | 0.220445 | -0.000091 | -0.002421 | 0.002239 |
| 10:20 | touch_up | etf_touch | native_control | brier | 257 | 257 | 0.169730 | 0.170104 | 0.000374 | -0.001789 | 0.002536 |
| 10:20 | touch_up | etf_touch | native_control | crps | 257 | 257 | 0.169730 | 0.170104 | 0.000374 | -0.001789 | 0.002536 |

[Matched ETF and index returns](network-observed-segments.csv.gz) · [All cross-instrument predictive comparisons](network-matched.csv) · [Source access receipts](new-source-availability.json) · [Upstox expired instruments API](https://upstox.com/developer/api-documentation/expired-instruments/)
