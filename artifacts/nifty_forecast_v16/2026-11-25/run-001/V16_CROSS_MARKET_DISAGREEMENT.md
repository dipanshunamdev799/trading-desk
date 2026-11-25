# V16 Cross-market disagreement

Disagreement features include dispersion and sign agreement in the six-market basket, relative strength of US and Asian closes, technology against the broad market, the equity–volatility and equity–FX interactions, oil versus equity changes, global versus prior domestic return, and the offshore futures signal minus the global average. The ETF follow-up measures technology versus finance and domestic official breadth versus US equal-weight/cap-weight market spread. Medians and normalizing scales come from the matured fitting sample. The power products and signed relative values are prespecified continuous measures rather than thresholds picked by the best future score. Feature comparisons keep the price and risk anchor fixed, including once the cash gap is observable.

## Disagreement versus average, additive and GIFT baselines

| exercise | cutoff | target | candidate | control | metric | n | gain | early gain | later gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| opening_gap | 08:30 | gap | gift_disagreement | gift_calibrated | brier | 247 | 0.001899 | 0.003322 | 0.000533 | -0.003512 | 0.007310 |
| opening_gap | 08:30 | gap | gift_disagreement | gift_calibrated | crps | 247 | 0.000006 | 0.000007 | 0.000005 | -0.000014 | 0.000025 |
| opening_gap | 08:45 | gap | gift_disagreement | gift_calibrated | brier | 248 | 0.000773 | 0.003269 | -0.001606 | -0.004747 | 0.006292 |
| opening_gap | 08:45 | gap | gift_disagreement | gift_calibrated | crps | 248 | -0.000002 | 0.000002 | -0.000006 | -0.000024 | 0.000020 |
| opening_gap | 08:55 | gap | disagreement | domestic_equal | brier | 258 | 0.009129 | 0.020768 | -0.001981 | -0.008265 | 0.026523 |
| opening_gap | 08:55 | gap | disagreement | domestic_equal | crps | 258 | 0.000090 | 0.000186 | -0.000001 | -0.000071 | 0.000251 |
| opening_gap | 08:55 | gap | gift_disagreement | gift_calibrated | brier | 248 | 0.001345 | 0.002252 | 0.000481 | -0.003472 | 0.006161 |
| opening_gap | 08:55 | gap | gift_disagreement | gift_calibrated | crps | 248 | -0.000006 | -0.000005 | -0.000006 | -0.000030 | 0.000019 |
| opening_gap | 09:10 | gap | disagreement | domestic_equal | brier | 258 | 0.009129 | 0.020768 | -0.001981 | -0.008326 | 0.026583 |
| opening_gap | 09:10 | gap | disagreement | domestic_equal | crps | 258 | 0.000090 | 0.000186 | -0.000001 | -0.000070 | 0.000251 |
| opening_gap | 09:10 | gap | gift_disagreement | gift_calibrated | brier | 246 | 0.001433 | 0.001208 | 0.001647 | -0.003597 | 0.006462 |
| opening_gap | 09:10 | gap | gift_disagreement | gift_calibrated | crps | 246 | -0.000016 | -0.000019 | -0.000012 | -0.000046 | 0.000015 |
| pre_session_decay | 08:55 | gap | disagreement | eq_fresh | brier | 258 | 0.009129 | 0.020768 | -0.001981 | -0.006408 | 0.024665 |
| pre_session_decay | 08:55 | gap | disagreement | eq_fresh | crps | 258 | 0.000090 | 0.000186 | -0.000001 | -0.000052 | 0.000233 |
| pre_session_decay | 08:55 | regular | disagreement | eq_fresh | brier | 258 | 0.000576 | 0.003546 | -0.002258 | -0.007901 | 0.009054 |
| pre_session_decay | 08:55 | regular | disagreement | eq_fresh | crps | 258 | -0.000025 | 0.000017 | -0.000065 | -0.000098 | 0.000047 |
| pre_session_decay | 08:55 | remaining | disagreement | eq_fresh | brier | 257 | -0.002284 | -0.003035 | -0.001560 | -0.010411 | 0.005844 |
| pre_session_decay | 08:55 | remaining | disagreement | eq_fresh | crps | 257 | -0.000024 | -0.000016 | -0.000031 | -0.000078 | 0.000031 |
| pre_session_decay | 08:55 | one | disagreement | eq_fresh | brier | 258 | 0.001011 | 0.012165 | -0.009635 | -0.015464 | 0.017487 |
| pre_session_decay | 08:55 | one | disagreement | eq_fresh | crps | 258 | 0.000059 | 0.000236 | -0.000110 | -0.000189 | 0.000306 |
| pre_session_decay | 08:55 | five | disagreement | eq_fresh | brier | 265 | 0.001648 | 0.004244 | -0.003233 | -0.011439 | 0.014735 |
| pre_session_decay | 08:55 | five | disagreement | eq_fresh | crps | 265 | 0.000118 | 0.000161 | 0.000036 | -0.000189 | 0.000425 |
| pre_session_decay | 08:55 | twentyone | disagreement | eq_fresh | brier | 217 | -0.007278 | -0.010921 | -0.000519 | -0.023706 | 0.009150 |
| pre_session_decay | 08:55 | twentyone | disagreement | eq_fresh | crps | 217 | -0.000351 | -0.000401 | -0.000257 | -0.001387 | 0.000686 |
| after_absorption | 09:25 | five | disagreement | eq_fresh | brier | 263 | -0.001364 | 0.000175 | -0.004274 | -0.012564 | 0.009836 |
| after_absorption | 09:25 | five | disagreement | eq_fresh | crps | 263 | 0.000049 | 0.000070 | 0.000008 | -0.000186 | 0.000284 |
| after_absorption | 10:20 | remaining | disagreement | eq_fresh | brier | 257 | -0.003558 | -0.003628 | -0.003491 | -0.011042 | 0.003926 |
| after_absorption | 10:20 | remaining | disagreement | eq_fresh | crps | 257 | -0.000027 | -0.000022 | -0.000032 | -0.000081 | 0.000027 |
| after_absorption | 10:20 | five | disagreement | eq_fresh | brier | 263 | -0.001697 | -0.000847 | -0.003304 | -0.011406 | 0.008012 |
| after_absorption | 10:20 | five | disagreement | eq_fresh | crps | 263 | -0.000016 | 0.000007 | -0.000061 | -0.000216 | 0.000184 |
| ETF_NIFTY_link | 08:55 | gap | ETF_disagreement | additive_ETFs | brier | 258 | 0.001380 | 0.001386 | 0.001373 | -0.005373 | 0.008132 |
| ETF_NIFTY_link | 08:55 | gap | ETF_disagreement | additive_ETFs | crps | 258 | 0.000001 | -0.000012 | 0.000013 | -0.000035 | 0.000037 |
| ETF_NIFTY_link | 08:55 | regular | ETF_disagreement | additive_ETFs | brier | 258 | -0.000513 | 0.002263 | -0.003163 | -0.004654 | 0.003627 |
| ETF_NIFTY_link | 08:55 | regular | ETF_disagreement | additive_ETFs | crps | 258 | -0.000004 | 0.000009 | -0.000017 | -0.000036 | 0.000028 |
| ETF_NIFTY_link | 08:55 | one | ETF_disagreement | additive_ETFs | brier | 258 | -0.001052 | -0.003561 | 0.001343 | -0.003695 | 0.001591 |
| ETF_NIFTY_link | 08:55 | one | ETF_disagreement | additive_ETFs | crps | 258 | -0.000017 | -0.000032 | -0.000003 | -0.000049 | 0.000015 |
| ETF_NIFTY_link | 08:55 | five | ETF_disagreement | additive_ETFs | brier | 265 | -0.001733 | -0.001941 | -0.001343 | -0.005451 | 0.001985 |
| ETF_NIFTY_link | 08:55 | five | ETF_disagreement | additive_ETFs | crps | 265 | -0.000082 | -0.000075 | -0.000095 | -0.000149 | -0.000014 |
| ETF_NIFTY_link | 08:55 | twentyone | ETF_disagreement | additive_ETFs | brier | 217 | -0.007197 | -0.011933 | 0.001591 | -0.020192 | 0.005799 |
| ETF_NIFTY_link | 08:55 | twentyone | ETF_disagreement | additive_ETFs | crps | 217 | -0.000384 | -0.000589 | -0.000003 | -0.000953 | 0.000185 |

The candidate rows offer tests of conditional associations at different times and outcome lengths. Regime claims require agreement across early and later cohorts and across closed-session, fresh-Asia and delayed-input controls. The overnight level from offshore futures remains a demanding parent for judging whether market disagreements add direction or finer gap magnitude.

[Full risk and direction scores](session-matched-evidence.csv) · [Joint risk transition results](volatility-matched.csv) · [Global feature and session receipts](information-clock.csv.gz)
