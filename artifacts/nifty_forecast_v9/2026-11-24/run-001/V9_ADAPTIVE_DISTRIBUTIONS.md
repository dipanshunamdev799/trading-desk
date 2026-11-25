# NIFTY V9 · Adaptive Distributions

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

All endpoint outputs come from one probability measure. The 65/35 residual/empirical law, adaptive Student-t shape, same-volatility residual weighting, and regime-reweighted block paths produce ordered return quantiles and normalized bucket probabilities. Location/scale adjustments remain within their own coherent law. A blend stacks the atoms of its complete constituent distributions with nonnegative weights summing to one. Its p(up), expected/median NIFTY close, central intervals and tails therefore agree mathematically. Forecast return and realized path-volatility scores are evaluated separately.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_HIST | 92 | 19 | 12.363138 | 0.576087 | 0.500000 | 0.258296 | 0.709964 | 0.012210 | 0.016374 | 0.023210 | 0.006135 | 0.500000 | 0.728261 | 0.039943 |
| P_ROT | 92 | 19 | 12.363138 | 0.793478 | 0.797049 | 0.164236 | 0.508472 | 0.009995 | 0.012962 | 0.019627 | 0.005056 | 0.510870 | 0.771739 | 0.035799 |
| P_STRUCTURE | 92 | 19 | 12.363138 | 0.771739 | 0.764635 | 0.165337 | 0.509874 | 0.009608 | 0.012492 | 0.019184 | 0.004846 | 0.543478 | 0.793478 | 0.036154 |
| T_STUDENT | 92 | 19 | 12.363138 | 0.608696 | 0.636672 | 0.229195 | 0.650008 | 0.011024 | 0.015027 | 0.020790 | 0.005447 | 0.456522 | 0.750000 | 0.038814 |
| T_RISK_STUDENT | 92 | 19 | 12.363138 | 0.586957 | 0.614417 | 0.236590 | 0.665699 | 0.011003 | 0.015027 | 0.020790 | 0.005425 | 0.413043 | 0.750000 | 0.039425 |
| T_RISK_LAW | 92 | 19 | 12.363138 | 0.597826 | 0.586599 | 0.237638 | 0.669421 | 0.011543 | 0.015344 | 0.021564 | 0.005739 | 0.358696 | 0.717391 | 0.034251 |
| PATH_EMPIRICAL | 92 | 19 | 12.363138 | 0.576087 | 0.500000 | 0.258296 | 0.709964 | 0.012210 | 0.016374 | 0.023210 | 0.006132 | 0.500000 | 0.728261 | 0.039943 |
| PATH_REGIME | 92 | 19 | 12.363138 | 0.434783 | 0.384132 | 0.263398 | 0.720259 | 0.012326 | 0.016471 | 0.023359 | 0.006183 | 0.500000 | 0.728261 | 0.040481 |
| PATH_AR_REGIME | 92 | 19 | 12.363138 | 0.434783 | 0.380745 | 0.263594 | 0.720654 | 0.012324 | 0.016466 | 0.023352 | 0.006180 | 0.500000 | 0.728261 | 0.040462 |
| J9_STATIC | 92 | 19 | 12.363138 | 0.760870 | 0.751814 | 0.221214 | 0.634997 | 0.011211 | 0.015054 | 0.021888 | 0.005594 | 0.576087 | 0.782609 | 0.042314 |
| J9_REL_SHRINK | 92 | 19 | 12.363138 | 0.706522 | 0.680939 | 0.225095 | 0.642610 | 0.011230 | 0.015123 | 0.021816 | 0.005595 | 0.576087 | 0.771739 | 0.042474 |
| J9_OOD | 92 | 19 | 12.363138 | 0.750000 | 0.742380 | 0.195789 | 0.580989 | 0.010556 | 0.013937 | 0.021020 | 0.005326 | 0.521739 | 0.793478 | 0.040832 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_HIST | 173 | 35 | 28.982745 | 0.445087 | 0.482119 | 0.259447 | 0.712156 | 0.010878 | 0.014956 | 0.019931 | 0.005409 | 0.473988 | 0.710983 | 0.036450 |
| P_ROT | 173 | 35 | 28.982745 | 0.514451 | 0.528070 | 0.298696 | 0.817949 | 0.013232 | 0.018256 | 0.024730 | 0.006460 | 0.410405 | 0.745665 | 0.047470 |
| P_STRUCTURE | 173 | 35 | 28.982745 | 0.508671 | 0.526248 | 0.296317 | 0.812451 | 0.013358 | 0.018478 | 0.025091 | 0.006535 | 0.404624 | 0.757225 | 0.048868 |
| T_STUDENT | 173 | 35 | 28.982745 | 0.502890 | 0.523279 | 0.295275 | 0.803839 | 0.012265 | 0.016768 | 0.022851 | 0.006060 | 0.468208 | 0.716763 | 0.044495 |
| T_RISK_STUDENT | 173 | 35 | 28.982745 | 0.502890 | 0.523279 | 0.287725 | 0.782353 | 0.012070 | 0.016768 | 0.022851 | 0.005975 | 0.473988 | 0.757225 | 0.047643 |
| T_RISK_LAW | 173 | 35 | 28.982745 | 0.473988 | 0.496964 | 0.327623 | 0.884712 | 0.013858 | 0.018309 | 0.025160 | 0.006862 | 0.439306 | 0.705202 | 0.043984 |
| PATH_EMPIRICAL | 173 | 35 | 28.982745 | 0.445087 | 0.482119 | 0.259447 | 0.712156 | 0.010878 | 0.014956 | 0.019931 | 0.005410 | 0.473988 | 0.710983 | 0.036450 |
| PATH_REGIME | 173 | 35 | 28.982745 | 0.427746 | 0.462888 | 0.262187 | 0.717795 | 0.010903 | 0.015025 | 0.020110 | 0.005438 | 0.479769 | 0.716763 | 0.037580 |
| PATH_AR_REGIME | 173 | 35 | 28.982745 | 0.427746 | 0.462888 | 0.262614 | 0.718649 | 0.010913 | 0.015038 | 0.020125 | 0.005445 | 0.485549 | 0.716763 | 0.037566 |
| J9_STATIC | 173 | 35 | 28.982745 | 0.485549 | 0.507490 | 0.259548 | 0.713391 | 0.010933 | 0.015204 | 0.020492 | 0.005428 | 0.491329 | 0.797688 | 0.045704 |
| J9_REL_SHRINK | 173 | 35 | 28.982745 | 0.491329 | 0.513900 | 0.261291 | 0.717179 | 0.010899 | 0.015088 | 0.020097 | 0.005404 | 0.479769 | 0.768786 | 0.041135 |
| J9_OOD | 173 | 35 | 28.982745 | 0.491329 | 0.512753 | 0.264420 | 0.726925 | 0.011463 | 0.016047 | 0.021236 | 0.005695 | 0.508671 | 0.791908 | 0.048717 |


| model | n | disjoint | brier | crps | early_Brier | late_Brier | early_CRPS | late_CRPS | abs_Brier_cohort_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J9_OOD | 265 | 53 | 0.240593 | 0.011148 | 0.264420 | 0.195789 | 0.011463 | 0.010556 | 0.068631 |
| J9_STATIC | 265 | 53 | 0.246239 | 0.011029 | 0.259548 | 0.221214 | 0.010933 | 0.011211 | 0.038333 |
| J9_REL_SHRINK | 265 | 53 | 0.248725 | 0.011014 | 0.261291 | 0.225095 | 0.010899 | 0.011230 | 0.036197 |
| P_STRUCTURE | 265 | 53 | 0.250845 | 0.012056 | 0.296317 | 0.165337 | 0.013358 | 0.009608 | 0.130980 |
| P_ROT | 265 | 53 | 0.252015 | 0.012108 | 0.298696 | 0.164236 | 0.013232 | 0.009995 | 0.134460 |
| PATH_EMPIRICAL | 265 | 53 | 0.259048 | 0.011340 | 0.259447 | 0.258296 | 0.010878 | 0.012210 | 0.001152 |
| P_HIST | 265 | 53 | 0.259048 | 0.011340 | 0.259447 | 0.258296 | 0.010878 | 0.012210 | 0.001152 |
| PATH_REGIME | 265 | 53 | 0.262608 | 0.011397 | 0.262187 | 0.263398 | 0.010903 | 0.012326 | 0.001211 |
| PATH_AR_REGIME | 265 | 53 | 0.262954 | 0.011403 | 0.262614 | 0.263594 | 0.010913 | 0.012324 | 0.000981 |
| T_RISK_STUDENT | 265 | 53 | 0.269973 | 0.011699 | 0.287725 | 0.236590 | 0.012070 | 0.011003 | 0.051135 |
| T_STUDENT | 265 | 53 | 0.272334 | 0.011834 | 0.295275 | 0.229195 | 0.012265 | 0.011024 | 0.066080 |
| T_RISK_LAW | 265 | 53 | 0.296383 | 0.013054 | 0.327623 | 0.237638 | 0.013858 | 0.011543 | 0.089985 |


| model | metric | n | gain | adjusted95_block10 |
| --- | --- | --- | --- | --- |
| P_CLUSTER | brier | 265 | 0.022661 | [-0.040440, 0.085762] |
| P_CLUSTER | crps | 265 | -0.000435 | [-0.003528, 0.002658] |
| J9_OOD | brier | 265 | 0.018454 | [-0.020490, 0.057399] |
| J9_OOD | crps | 265 | 0.000192 | [-0.001243, 0.001627] |
| J9_PERFORMANCE | brier | 265 | 0.017820 | [-0.030487, 0.066126] |
| J9_PERFORMANCE | crps | 265 | 0.000189 | [-0.001559, 0.001937] |
| J9_STATIC | brier | 265 | 0.012808 | [-0.011301, 0.036918] |
| J9_STATIC | crps | 265 | 0.000311 | [-0.000528, 0.001150] |
| J9_REL_SHRINK | brier | 265 | 0.010323 | [-0.011107, 0.031752] |
| J9_REL_SHRINK | crps | 265 | 0.000327 | [-0.000372, 0.001025] |
| P_STRUCTURE | brier | 265 | 0.008203 | [-0.062776, 0.079182] |
| P_STRUCTURE | crps | 265 | -0.000716 | [-0.003566, 0.002134] |
| P_ROT | brier | 265 | 0.007032 | [-0.064811, 0.078876] |
| P_ROT | crps | 265 | -0.000768 | [-0.003441, 0.001905] |


`J9_REL_SHRINK` is the combined weekly CRPS point leader at **.011014** against **.011340** for history, while losing slightly to that benchmark earlier. `J9_STATIC` follows at **.011029**, roughly .000015 worse using fixed weights and simplifying the interpretation of adaptation risk. Both give up sharp later-cohort CRPS relative to structural rotation. The three earlier dynamic-location laws and Student scales do not systematically beat history. Path models supply independently interpretable conditional volatility and barrier forecasts, retaining serially ordered blocks, but their endpoint scores remain weaker than the best direct later weekly laws.

| cohort | model | n | vol_mae | barrier_brier | mean_atom_ESS |
| --- | --- | --- | --- | --- | --- |
| early | PATH_AR_REGIME | 173 | 0.048553 | 0.193142 | 171.561112 |
| early | PATH_EMPIRICAL | 173 | 0.051989 | 0.189483 | 199.537572 |
| early | PATH_REGIME | 173 | 0.048559 | 0.193071 | 171.561112 |
| later | PATH_AR_REGIME | 92 | 0.043361 | 0.129323 | 226.140029 |
| later | PATH_EMPIRICAL | 92 | 0.044810 | 0.131589 | 252.000000 |
| later | PATH_REGIME | 92 | 0.043362 | 0.129330 | 226.140029 |

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
