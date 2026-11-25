# NIFTY V9 · Cross Sectional Structure

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

The primary panel uses nine native sector index histories. Each daily sector return is residualized against NIFTY with a lagged 63-session beta. A date-level representation aggregates five-session residual mean, dispersion and breadth, cross-sector rank change, common risk and residual acceleration. The fit sees one row per NIFTY origin. `X_ROT_PANEL` isolates the added panel from the exact same compact rotation parent. The current-selected stock proxy uses up to **150** equities on a date and is a survivorship-exposed diagnostic. It is not authenticated historical membership. Individual ETF/insurance/banking coverage is audited independently.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 92 | 19 | 12.363138 | 0.576087 | 0.557571 | 0.260247 | 0.716743 | 0.012161 | 0.016072 | 0.022797 | 0.006012 | 0.391304 | 0.695652 | 0.036504 |
| P_COMPACT | 92 | 19 | 12.363138 | 0.554348 | 0.538703 | 0.252389 | 0.699219 | 0.011908 | 0.015752 | 0.022145 | 0.005906 | 0.369565 | 0.706522 | 0.034588 |
| X_NATIVE_PANEL | 92 | 19 | 12.363138 | 0.576087 | 0.567731 | 0.245356 | 0.684450 | 0.011779 | 0.015651 | 0.022296 | 0.005790 | 0.456522 | 0.706522 | 0.035893 |
| X_ROT_PANEL | 92 | 19 | 12.363138 | 0.597826 | 0.586599 | 0.233628 | 0.659585 | 0.011487 | 0.015368 | 0.021583 | 0.005740 | 0.369565 | 0.739130 | 0.035450 |
| X_STOCK_PROXY | 92 | 19 | 12.363138 | 0.597826 | 0.589985 | 0.255625 | 0.706629 | 0.011963 | 0.015792 | 0.022452 | 0.005883 | 0.402174 | 0.695652 | 0.035868 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 173 | 35 | 28.982745 | 0.439306 | 0.458502 | 0.331330 | 0.891962 | 0.013642 | 0.018291 | 0.025002 | 0.006721 | 0.450867 | 0.693642 | 0.043349 |
| P_COMPACT | 173 | 35 | 28.982745 | 0.462428 | 0.482996 | 0.323155 | 0.873586 | 0.013434 | 0.017990 | 0.024756 | 0.006685 | 0.445087 | 0.699422 | 0.043751 |
| X_NATIVE_PANEL | 173 | 35 | 28.982745 | 0.491329 | 0.511606 | 0.308637 | 0.838466 | 0.013238 | 0.017978 | 0.024329 | 0.006584 | 0.450867 | 0.705202 | 0.043114 |
| X_ROT_PANEL | 173 | 35 | 28.982745 | 0.491329 | 0.512753 | 0.304341 | 0.827413 | 0.013011 | 0.017652 | 0.024077 | 0.006471 | 0.445087 | 0.705202 | 0.044064 |
| X_STOCK_PROXY | 173 | 35 | 28.982745 | 0.450867 | 0.470175 | 0.330933 | 0.891466 | 0.013694 | 0.018421 | 0.025132 | 0.006776 | 0.462428 | 0.687861 | 0.043663 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 76 | 4 | 4.698728 | 0.144737 | 0.152330 | 0.522123 | 1.331502 | 0.040255 | 0.050431 | 0.060992 | 0.020540 | 0.118421 | 0.302632 | 0.058762 |
| P_COMPACT | 76 | 4 | 4.698728 | 0.131579 | 0.131183 | 0.519581 | 1.325727 | 0.040170 | 0.050363 | 0.060888 | 0.020446 | 0.118421 | 0.302632 | 0.058834 |
| X_NATIVE_PANEL | 76 | 4 | 4.698728 | 0.157895 | 0.163441 | 0.516592 | 1.323227 | 0.039650 | 0.049654 | 0.059665 | 0.020030 | 0.131579 | 0.289474 | 0.058780 |
| X_ROT_PANEL | 76 | 4 | 4.698728 | 0.144737 | 0.142294 | 0.515863 | 1.322978 | 0.039545 | 0.049537 | 0.059528 | 0.019940 | 0.131579 | 0.289474 | 0.058721 |
| X_STOCK_PROXY | 76 | 4 | 4.698728 | 0.144737 | 0.157348 | 0.497592 | 1.266528 | 0.039653 | 0.049689 | 0.060559 | 0.020027 | 0.144737 | 0.328947 | 0.058695 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| F_BASE | P_HIST | brier | 92 | -0.001951 |
| F_BASE | P_HIST | crps | 92 | 0.000049 |
| P_COMPACT | P_HIST | brier | 92 | 0.005907 |
| P_COMPACT | P_HIST | crps | 92 | 0.000302 |
| X_NATIVE_PANEL | F_BASE | brier | 92 | 0.014891 |
| X_NATIVE_PANEL | F_BASE | crps | 92 | 0.000383 |
| X_ROT_PANEL | P_COMPACT | brier | 92 | 0.018761 |
| X_ROT_PANEL | P_COMPACT | crps | 92 | 0.000421 |
| X_STOCK_PROXY | F_BASE | brier | 92 | 0.004622 |
| X_STOCK_PROXY | F_BASE | crps | 92 | 0.000198 |


| model | parent | slice | state | n | disjoint | Brier_gain | CRPS_gain | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| X_ROT_PANEL | P_COMPACT | volatility_high | False | 60 | 13 | 0.017675 | 0.000205 | 0.816667 | 0.036617 |
| X_ROT_PANEL | P_COMPACT | volatility_high | True | 32 | 8 | 0.020796 | 0.000827 | 0.593750 | 0.033261 |
| X_ROT_PANEL | P_COMPACT | broad_participation | False | 52 | 14 | 0.039810 | 0.001082 | 0.730769 | 0.033873 |
| X_ROT_PANEL | P_COMPACT | broad_participation | True | 40 | 12 | -0.008603 | -0.000438 | 0.750000 | 0.037499 |
| X_ROT_PANEL | P_COMPACT | concentrated | False | 43 | 13 | 0.023358 | 0.000719 | 0.604651 | 0.035029 |
| X_ROT_PANEL | P_COMPACT | concentrated | True | 49 | 14 | 0.014726 | 0.000160 | 0.857143 | 0.035819 |


Native residual aggregation can improve the compact counterpart in some slices, but neither a full panel head nor the stock proxy is a reliable improvement across horizons and cohorts. No stock-date or sector-date observation counts as a fresh independent NIFTY target. The separately fitted rank-two multi-horizon model shares location coefficients across horizons using fully matured targets. It supplies a related low-dimensional learning test whose monthly results are reported in the monthly chapter.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
