# V15 extreme probabilities and separate scenario paths

The probabilistic comparisons use regular IV diffusion, a 22% path-level Student-t(6) innovation mixture, empirical asymmetry, sign-and-magnitude, a fixed issue-law baseline and a 25% historical tail mixture. Empirical histories are restricted to earlier matured samples and the tail mixture balances consecutive remaining-horizon blocks. PIT- and width-only diagnostics using resolved errors are stored in the causal error study. Absolute terminal extremes are 3% for five sessions and 5% for 21 sessions, alongside 1.5 times the as-of implied horizon scale. Event-rate, Brier and log loss retain separate tail directions. All independent extreme-event counts use merged overlapping episodes.

## Probabilistic tail comparisons

| horizon | event | model | n | p | actual | brier | log loss |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | down_fixed | state_risk_only | 265 | 0.044001 | 0.037736 | 0.035615 | 0.149136 |
| 5 | down_fixed | episode_tails | 265 | 0.053877 | 0.037736 | 0.036591 | 0.154436 |
| 5 | down_fixed | common_raw_iv | 265 | 0.053877 | 0.037736 | 0.036968 | 0.157767 |
| 5 | down_relative | state_risk_only | 265 | 0.060893 | 0.071698 | 0.065418 | 0.244899 |
| 5 | down_relative | episode_tails | 265 | 0.064519 | 0.071698 | 0.066132 | 0.253954 |
| 5 | down_relative | common_raw_iv | 265 | 0.064932 | 0.071698 | 0.066525 | 0.257531 |
| 5 | up_fixed | common_raw_iv | 265 | 0.058667 | 0.086792 | 0.072741 | 0.247288 |
| 5 | up_fixed | tail_t6_mixture | 265 | 0.058328 | 0.086792 | 0.073107 | 0.249113 |
| 5 | up_relative | fitted_risk_without_drift | 265 | 0.059744 | 0.071698 | 0.065262 | 0.248843 |
| 5 | up_relative | risk_matched_asymmetry | 265 | 0.045224 | 0.071698 | 0.065379 | 0.248103 |
| 5 | up_relative | common_raw_iv | 265 | 0.070563 | 0.071698 | 0.065736 | 0.251722 |
| 21 | down_fixed | state_risk_only | 217 | 0.068800 | 0.133641 | 0.122358 | 0.446756 |
| 21 | down_fixed | tail_t6_mixture | 217 | 0.087918 | 0.133641 | 0.131102 | 0.497894 |
| 21 | down_fixed | common_raw_iv | 217 | 0.088332 | 0.133641 | 0.131282 | 0.497457 |
| 21 | down_relative | state_risk_only | 217 | 0.055714 | 0.161290 | 0.140391 | 0.463386 |
| 21 | down_relative | tail_t6_mixture | 217 | 0.061204 | 0.161290 | 0.144000 | 0.493638 |
| 21 | down_relative | common_raw_iv | 217 | 0.061312 | 0.161290 | 0.144020 | 0.493941 |
| 21 | up_fixed | fitted_risk_without_drift | 217 | 0.096846 | 0.082949 | 0.068217 | 0.239997 |
| 21 | up_fixed | tail_t6_mixture | 217 | 0.099600 | 0.082949 | 0.068476 | 0.245340 |
| 21 | up_fixed | common_raw_iv | 217 | 0.100140 | 0.082949 | 0.068626 | 0.245948 |
| 21 | up_relative | empirical_sign_magnitude | 217 | 0.049431 | 0.046083 | 0.041875 | 0.165895 |
| 21 | up_relative | fitted_risk_without_drift | 217 | 0.069466 | 0.046083 | 0.043688 | 0.182808 |
| 21 | up_relative | common_raw_iv | 217 | 0.072257 | 0.046083 | 0.044160 | 0.188527 |

## Hypothetical OHLC stress paths

| scenario | horizon | endpoint | volatility | range | gap | drawdown |
| --- | --- | --- | --- | --- | --- | --- |
| sustained_upside | 5 | 0.033551 | 0.106015 | 0.040689 | 0.002000 | 0.000000 |
| sustained_upside | 21 | 0.093277 | 0.071388 | 0.098593 | 0.002000 | 0.000000 |
| sustained_downside | 5 | -0.033428 | 0.111348 | 0.042257 | 0.003000 | -0.033428 |
| sustained_downside | 21 | -0.088652 | 0.075582 | 0.095071 | 0.003000 | -0.088652 |
| sudden_risk_expansion | 5 | -0.004988 | 0.248069 | 0.040534 | 0.008000 | -0.020781 |
| sudden_risk_expansion | 21 | -0.023792 | 0.168777 | 0.040534 | 0.008000 | -0.023792 |
| large_opening_gap | 5 | -0.007968 | 0.125800 | 0.041171 | 0.035000 | -0.015873 |
| large_opening_gap | 21 | -0.028778 | 0.088353 | 0.042562 | 0.035000 | -0.028778 |
| broad_market_reversal | 5 | 0.019182 | 0.227953 | 0.055840 | 0.006000 | -0.024690 |
| broad_market_reversal | 21 | 0.041571 | 0.153821 | 0.084311 | 0.006000 | -0.024690 |
| concentration_breakdown | 5 | -0.033428 | 0.206002 | 0.056075 | 0.009000 | -0.042089 |
| concentration_breakdown | 21 | -0.081864 | 0.136759 | 0.101689 | 0.009000 | -0.090791 |
| persistent_high_risk | 5 | 0.015113 | 0.283883 | 0.044401 | 0.007000 | -0.019801 |
| persistent_high_risk | 21 | 0.070494 | 0.248653 | 0.094125 | 0.007000 | -0.019801 |
| foreign_shock | 5 | -0.020781 | 0.237482 | 0.038782 | 0.024000 | -0.040171 |
| foreign_shock | 21 | -0.066888 | 0.165489 | 0.060881 | 0.024000 | -0.066888 |

## Matching against unique serious misses

| horizon | n | entire box | stress maxima cover | typical distance |
| --- | --- | --- | --- | --- |
| 5 | 48 | 3 | 21 | 0.579452 |
| 21 | 60 | 24 | 27 | 0.587712 |

Eight explicit hypothetical paths describe repeated upside or downside, sudden volatility expansion, a large opening gap, a market reversal, concentrated leader weakness, sustained high volatility and a foreign repricing. A remaining calendar path is built from daily log steps, explicit opening gaps and stated intraday excursions. The 21-session scenario repeats the initial pattern at a stated attenuation. Scenario distances use the outcome vector of endpoint, annualized volatility, high–low range, largest absolute gap and drawdown, with units fixed in code. Stress maxima coverage tests all five adverse dimensions jointly. Our retrospective envelope leaves severe combinations outside its span and carries no calibrated occurrence probabilities, ranks or percentiles.

[Scenario assumptions and OHLC rows](scenario-paths.csv) [Nearest scenarios by severe window](scenario-severe-error-coverage.csv) [Complete tail scores](endpoint-tail-scores.csv.gz) [Extreme-event counts](V15_EPISODE_LEVEL_EVALUATION.md)
