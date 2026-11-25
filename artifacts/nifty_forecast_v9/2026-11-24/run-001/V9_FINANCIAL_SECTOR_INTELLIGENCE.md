# NIFTY V9 · Financial Sector Intelligence

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

Financial-sector coverage now includes native Bank Nifty, Financial Services, PSU Bank and authenticated Private Bank. BANKBEES, PSU Bank BeES and FINIETF supply actual ETF observations, and SBI Life, HDFC Life, and ICICI Prudential Life cover three documented insurance equity proxies. They are individual instrument histories. Dated constituent weights and a complete historical insurance index input were unavailable. NIFTY 50 and NIFTY 500 provide distinct benchmarks. Sidecar sources have separate receipt, key and checksum records, and no pre-2025 data are loaded. [Upstox historical daily data](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)

| name | key | rows | first | last | status |
| --- | --- | --- | --- | --- | --- |
| private_bank | NSE_INDEX/Nifty Pvt Bank | 470 | 2025-01-01 | 2026-11-23 | ok |
| bankbees | NSE_EQ/INF204KB15I9 | 470 | 2025-01-01 | 2026-11-23 | ok |
| psu_etf | NSE_EQ/INF204KB16I7 | 470 | 2025-01-01 | 2026-11-23 | ok |
| financial_etf | NSE_EQ/INF109KC17L8 | 470 | 2025-01-01 | 2026-11-23 | ok |
| insurance_sbi | NSE_EQ/INE123W01016 | 470 | 2025-01-01 | 2026-11-23 | ok |
| insurance_hdfc | NSE_EQ/INE795G01014 | 470 | 2025-01-01 | 2026-11-23 | ok |


The financial feature set separately measures the bank-minus-financial five-session momentum level, five-session change and acceleration, 21-session persistence, lagged beta adjustment at fixed 42/63/84 lookbacks, volatility-adjusted change, correlation change, rank change and dispersion. Private/PSU spreads and ETF tracking are richer additions. Every rolling beta is lagged one session. Removing the private/PSU spread and the entire native banking feature group supplies removal controls. The stronger-regularization financial variant keeps the canonical design and adds alpha170. The full feature count is 18 and one-to-one inclusion counts are in the frozen feature manifest.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 92 | 19 | 12.363138 | 0.576087 | 0.557571 | 0.260247 | 0.716743 | 0.012161 | 0.016072 | 0.022797 | 0.006012 | 0.391304 | 0.695652 | 0.036504 |
| F_BANK_LEVEL | 92 | 19 | 12.363138 | 0.543478 | 0.525883 | 0.261582 | 0.719967 | 0.012210 | 0.016131 | 0.022892 | 0.006057 | 0.391304 | 0.706522 | 0.036451 |
| F_BANK_CHANGE | 92 | 19 | 12.363138 | 0.565217 | 0.541364 | 0.253503 | 0.703221 | 0.011981 | 0.015793 | 0.022383 | 0.005990 | 0.402174 | 0.750000 | 0.036460 |
| F_BANK_RESID42 | 92 | 19 | 12.363138 | 0.608696 | 0.585873 | 0.254923 | 0.707267 | 0.011997 | 0.015796 | 0.022358 | 0.005989 | 0.369565 | 0.717391 | 0.035329 |
| F_BANK_RESID63 | 92 | 19 | 12.363138 | 0.586957 | 0.563619 | 0.254507 | 0.705528 | 0.011990 | 0.015796 | 0.022429 | 0.005984 | 0.380435 | 0.728261 | 0.035696 |
| F_BANK_RESID84 | 92 | 19 | 12.363138 | 0.543478 | 0.515723 | 0.253524 | 0.703324 | 0.012013 | 0.015846 | 0.022476 | 0.005998 | 0.380435 | 0.728261 | 0.035762 |
| F_FINANCIAL_PERSISTENCE | 92 | 19 | 12.363138 | 0.532609 | 0.499516 | 0.257873 | 0.711729 | 0.012361 | 0.016301 | 0.022963 | 0.006233 | 0.369565 | 0.706522 | 0.035370 |
| F_FINANCIAL_PANEL | 92 | 19 | 12.363138 | 0.521739 | 0.490082 | 0.247576 | 0.690028 | 0.012316 | 0.015953 | 0.023384 | 0.006221 | 0.434783 | 0.673913 | 0.035381 |
| F_FINANCIAL_PANEL_NO_SIZE | 92 | 19 | 12.363138 | 0.543478 | 0.529269 | 0.244283 | 0.682448 | 0.012168 | 0.015854 | 0.023189 | 0.006144 | 0.434783 | 0.673913 | 0.034833 |
| F_FINANCIAL_TRADE | 92 | 19 | 12.363138 | 0.543478 | 0.508950 | 0.246770 | 0.687791 | 0.012342 | 0.016031 | 0.023497 | 0.006255 | 0.423913 | 0.673913 | 0.035922 |
| F_FINANCIAL_LAG | 92 | 19 | 12.363138 | 0.608696 | 0.589260 | 0.254641 | 0.705091 | 0.012349 | 0.016291 | 0.023368 | 0.006206 | 0.423913 | 0.673913 | 0.036157 |
| F_FINANCIAL_REDUCED | 92 | 19 | 12.363138 | 0.543478 | 0.478471 | 0.266401 | 0.730753 | 0.012823 | 0.016871 | 0.024007 | 0.006496 | 0.369565 | 0.706522 | 0.038016 |
| F_CLUSTER | 92 | 19 | 12.363138 | 0.521739 | 0.490082 | 0.249049 | 0.692449 | 0.012390 | 0.016113 | 0.023535 | 0.006267 | 0.402174 | 0.684783 | 0.035635 |
| F_REMOVAL | 92 | 19 | 12.363138 | 0.771739 | 0.781567 | 0.179212 | 0.543549 | 0.010283 | 0.013396 | 0.019845 | 0.005192 | 0.532609 | 0.750000 | 0.037036 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 173 | 35 | 28.982745 | 0.439306 | 0.458502 | 0.331330 | 0.891962 | 0.013642 | 0.018291 | 0.025002 | 0.006721 | 0.450867 | 0.693642 | 0.043349 |
| F_BANK_LEVEL | 173 | 35 | 28.982745 | 0.445087 | 0.464912 | 0.331841 | 0.893574 | 0.013651 | 0.018325 | 0.025006 | 0.006726 | 0.450867 | 0.693642 | 0.043443 |
| F_BANK_CHANGE | 173 | 35 | 28.982745 | 0.427746 | 0.450270 | 0.330325 | 0.889140 | 0.013578 | 0.018170 | 0.024922 | 0.006728 | 0.473988 | 0.699422 | 0.043242 |
| F_BANK_RESID42 | 173 | 35 | 28.982745 | 0.439306 | 0.460796 | 0.330393 | 0.890276 | 0.013579 | 0.018178 | 0.024928 | 0.006737 | 0.473988 | 0.699422 | 0.043253 |
| F_BANK_RESID63 | 173 | 35 | 28.982745 | 0.433526 | 0.455533 | 0.331155 | 0.891766 | 0.013579 | 0.018180 | 0.024921 | 0.006733 | 0.473988 | 0.699422 | 0.043233 |
| F_BANK_RESID84 | 173 | 35 | 28.982745 | 0.427746 | 0.450270 | 0.332489 | 0.895221 | 0.013583 | 0.018181 | 0.024917 | 0.006729 | 0.468208 | 0.699422 | 0.043209 |
| F_FINANCIAL_PERSISTENCE | 173 | 35 | 28.982745 | 0.450867 | 0.475911 | 0.326948 | 0.881703 | 0.013547 | 0.018106 | 0.024910 | 0.006715 | 0.479769 | 0.699422 | 0.043320 |
| F_FINANCIAL_PANEL | 173 | 35 | 28.982745 | 0.508671 | 0.525101 | 0.297151 | 0.806462 | 0.012804 | 0.017404 | 0.023663 | 0.006315 | 0.433526 | 0.687861 | 0.042025 |
| F_FINANCIAL_PANEL_NO_SIZE | 173 | 35 | 28.982745 | 0.491329 | 0.507018 | 0.301509 | 0.815106 | 0.012896 | 0.017579 | 0.023800 | 0.006352 | 0.433526 | 0.693642 | 0.042566 |
| F_FINANCIAL_TRADE | 173 | 35 | 28.982745 | 0.514451 | 0.531511 | 0.302396 | 0.822313 | 0.012828 | 0.017457 | 0.023863 | 0.006303 | 0.445087 | 0.687861 | 0.042758 |
| F_FINANCIAL_LAG | 173 | 35 | 28.982745 | 0.468208 | 0.484818 | 0.321020 | 0.863120 | 0.013484 | 0.018116 | 0.024483 | 0.006709 | 0.456647 | 0.705202 | 0.043941 |
| F_FINANCIAL_REDUCED | 173 | 35 | 28.982745 | 0.491329 | 0.501282 | 0.314489 | 0.853126 | 0.013233 | 0.017656 | 0.024497 | 0.006526 | 0.485549 | 0.693642 | 0.042526 |
| F_CLUSTER | 173 | 35 | 28.982745 | 0.514451 | 0.530364 | 0.294307 | 0.798688 | 0.012541 | 0.016977 | 0.023193 | 0.006192 | 0.450867 | 0.710983 | 0.040971 |
| F_REMOVAL | 173 | 35 | 28.982745 | 0.526012 | 0.542038 | 0.307307 | 0.841871 | 0.013574 | 0.018718 | 0.025434 | 0.006641 | 0.398844 | 0.728324 | 0.047127 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| F_BANK_CHANGE | F_BASE | brier | 92 | 0.006744 |
| F_BANK_CHANGE | F_BASE | crps | 92 | 0.000180 |
| F_BANK_LEVEL | F_BASE | brier | 92 | -0.001334 |
| F_BANK_LEVEL | F_BASE | crps | 92 | -0.000048 |
| F_BANK_RESID42 | F_BASE | brier | 92 | 0.005324 |
| F_BANK_RESID42 | F_BASE | crps | 92 | 0.000165 |
| F_BANK_RESID63 | F_BASE | brier | 92 | 0.005741 |
| F_BANK_RESID63 | F_BASE | crps | 92 | 0.000171 |
| F_BANK_RESID84 | F_BASE | brier | 92 | 0.006724 |
| F_BANK_RESID84 | F_BASE | crps | 92 | 0.000148 |
| F_BASE | P_HIST | brier | 92 | -0.001951 |
| F_BASE | P_HIST | crps | 92 | 0.000049 |
| F_CLUSTER | F_FINANCIAL_PANEL | brier | 92 | -0.001474 |
| F_CLUSTER | F_FINANCIAL_PANEL | crps | 92 | -0.000075 |
| F_FINANCIAL_LAG | F_BASE | brier | 92 | 0.005606 |
| F_FINANCIAL_LAG | F_BASE | crps | 92 | -0.000188 |
| F_FINANCIAL_PANEL | F_BASE | brier | 92 | 0.012672 |
| F_FINANCIAL_PANEL | F_BASE | crps | 92 | -0.000154 |
| F_FINANCIAL_PANEL_NO_SIZE | F_BASE | brier | 92 | 0.015964 |
| F_FINANCIAL_PANEL_NO_SIZE | F_BASE | crps | 92 | -0.000007 |
| F_FINANCIAL_PERSISTENCE | F_BASE | brier | 92 | 0.002374 |
| F_FINANCIAL_PERSISTENCE | F_BASE | crps | 92 | -0.000199 |
| F_FINANCIAL_REDUCED | F_BASE | brier | 92 | -0.006154 |
| F_FINANCIAL_REDUCED | F_BASE | crps | 92 | -0.000662 |
| F_FINANCIAL_TRADE | F_BASE | brier | 92 | 0.013478 |
| F_FINANCIAL_TRADE | F_BASE | crps | 92 | -0.000181 |
| F_REMOVAL | P_NATIVE | brier | 92 | -0.004470 |
| F_REMOVAL | P_NATIVE | crps | 92 | -0.000008 |


| model | parent | slice | state | n | disjoint | Brier_gain | CRPS_gain | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BANK_RESID63 | F_BASE | volatility_high | False | 60 | 13 | 0.008570 | 0.000149 | 0.800000 | 0.036396 |
| F_BANK_RESID63 | F_BASE | volatility_high | True | 32 | 8 | 0.000436 | 0.000212 | 0.593750 | 0.034383 |
| F_BANK_RESID63 | F_BASE | uptrend | False | 48 | 11 | -0.000891 | -0.000006 | 0.645833 | 0.032663 |
| F_BANK_RESID63 | F_BASE | uptrend | True | 44 | 10 | 0.012975 | 0.000364 | 0.818182 | 0.039004 |
| F_BANK_RESID63 | F_BASE | financial_spread_positive | False | 43 | 12 | 0.005659 | 0.000117 | 0.674419 | 0.035738 |
| F_BANK_RESID63 | F_BASE | financial_spread_positive | True | 49 | 13 | 0.005813 | 0.000218 | 0.775510 | 0.035659 |
| F_FINANCIAL_PANEL | F_BASE | volatility_high | False | 60 | 13 | 0.019205 | -0.000281 | 0.716667 | 0.037268 |
| F_FINANCIAL_PANEL | F_BASE | volatility_high | True | 32 | 8 | 0.000422 | 0.000084 | 0.593750 | 0.031844 |
| F_FINANCIAL_PANEL | F_BASE | uptrend | False | 48 | 11 | -0.003078 | -0.000675 | 0.562500 | 0.032660 |
| F_FINANCIAL_PANEL | F_BASE | uptrend | True | 44 | 10 | 0.029853 | 0.000414 | 0.795455 | 0.038349 |
| F_FINANCIAL_PANEL | F_BASE | financial_spread_positive | False | 43 | 12 | -0.008720 | -0.000257 | 0.651163 | 0.035254 |
| F_FINANCIAL_PANEL | F_BASE | financial_spread_positive | True | 49 | 13 | 0.031444 | -0.000064 | 0.693878 | 0.035493 |


The 42/63/84 choices are fixed adjacent residualization windows rather than an optimized parameter surface. No compact financial representation beats both historical early metrics and later full native rotation. In the later sample, eliminating banks from the full native features compromises some of the native improvement. Coupled with the matched raw-rotation training-size curve, this suggests financial information can be useful inside a trained representation without establishing a broadly transferable financial-only forecast. Fit, feature-lag and family removal conclusions all remain retrospective.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
