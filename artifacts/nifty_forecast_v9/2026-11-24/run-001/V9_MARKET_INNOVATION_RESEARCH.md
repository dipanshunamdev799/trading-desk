# NIFTY V9 · Market Innovation Research

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

The innovation panel comprises bank divergence and defensive rotation, ETF turnover, NIFTY trailing realized volatility, lagged NSE futures basis, sector breadth, and domestic return residual versus global equities. Levels, ordinary five-session changes, AR(1) innovations and robust deviations are compared on the same compact price and risk parent. The AR expectation uses a 42-session trailing regression with its coefficients shifted one day. Robust surprises subtract a prior median and divide by the prior IQR-scale, capped at ±8. The global/domestic relative residual similarly estimates its beta in advance. No market-wide release surprise feed enters this experiment.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 92 | 19 | 12.363138 | 0.576087 | 0.557571 | 0.260247 | 0.716743 | 0.012161 | 0.016072 | 0.022797 | 0.006012 | 0.391304 | 0.695652 | 0.036504 |
| I_LEVEL | 92 | 19 | 12.363138 | 0.630435 | 0.618287 | 0.244527 | 0.686849 | 0.011660 | 0.015442 | 0.021671 | 0.005798 | 0.369565 | 0.728261 | 0.035358 |
| I_DELTA | 92 | 19 | 12.363138 | 0.663043 | 0.656749 | 0.232498 | 0.660890 | 0.011699 | 0.015218 | 0.022334 | 0.005884 | 0.456522 | 0.771739 | 0.037525 |
| I_AR | 92 | 19 | 12.363138 | 0.576087 | 0.557571 | 0.256369 | 0.709296 | 0.012064 | 0.015842 | 0.022466 | 0.005989 | 0.358696 | 0.695652 | 0.035764 |
| I_ROBUST | 92 | 19 | 12.363138 | 0.608696 | 0.589260 | 0.250827 | 0.699472 | 0.011898 | 0.015614 | 0.022332 | 0.005910 | 0.380435 | 0.684783 | 0.035079 |
| I_AR_NOGLOBAL | 92 | 19 | 12.363138 | 0.586957 | 0.570392 | 0.253364 | 0.702677 | 0.012039 | 0.015827 | 0.022457 | 0.005975 | 0.358696 | 0.695652 | 0.035649 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 173 | 35 | 28.982745 | 0.439306 | 0.458502 | 0.331330 | 0.891962 | 0.013642 | 0.018291 | 0.025002 | 0.006721 | 0.450867 | 0.693642 | 0.043349 |
| I_LEVEL | 173 | 35 | 28.982745 | 0.491329 | 0.508165 | 0.319570 | 0.864046 | 0.013374 | 0.017753 | 0.024604 | 0.006596 | 0.497110 | 0.693642 | 0.043217 |
| I_DELTA | 173 | 35 | 28.982745 | 0.462428 | 0.481849 | 0.317553 | 0.857503 | 0.013555 | 0.018165 | 0.024558 | 0.006670 | 0.450867 | 0.699422 | 0.045292 |
| I_AR | 173 | 35 | 28.982745 | 0.445087 | 0.463765 | 0.328575 | 0.885640 | 0.013676 | 0.018349 | 0.025126 | 0.006757 | 0.456647 | 0.687861 | 0.043235 |
| I_ROBUST | 173 | 35 | 28.982745 | 0.462428 | 0.481849 | 0.329138 | 0.887492 | 0.013659 | 0.018200 | 0.025092 | 0.006703 | 0.485549 | 0.693642 | 0.043577 |
| I_AR_NOGLOBAL | 173 | 35 | 28.982745 | 0.445087 | 0.462618 | 0.329090 | 0.887230 | 0.013714 | 0.018389 | 0.025088 | 0.006808 | 0.450867 | 0.693642 | 0.043820 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_BASE | 76 | 4 | 4.698728 | 0.144737 | 0.152330 | 0.522123 | 1.331502 | 0.040255 | 0.050431 | 0.060992 | 0.020540 | 0.118421 | 0.302632 | 0.058762 |
| I_LEVEL | 76 | 4 | 4.698728 | 0.131579 | 0.146237 | 0.521803 | 1.334182 | 0.040897 | 0.051869 | 0.062565 | 0.020655 | 0.105263 | 0.302632 | 0.061839 |
| I_DELTA | 76 | 4 | 4.698728 | 0.144737 | 0.167384 | 0.502597 | 1.288535 | 0.039530 | 0.049134 | 0.059509 | 0.020054 | 0.157895 | 0.315789 | 0.056479 |
| I_AR | 76 | 4 | 4.698728 | 0.131579 | 0.131183 | 0.527685 | 1.342865 | 0.040920 | 0.051602 | 0.061866 | 0.020813 | 0.092105 | 0.289474 | 0.060273 |
| I_ROBUST | 76 | 4 | 4.698728 | 0.144737 | 0.152330 | 0.539657 | 1.385896 | 0.041558 | 0.052534 | 0.063954 | 0.020989 | 0.092105 | 0.302632 | 0.060874 |
| I_AR_NOGLOBAL | 76 | 4 | 4.698728 | 0.131579 | 0.131183 | 0.531995 | 1.354213 | 0.040995 | 0.051667 | 0.061972 | 0.020885 | 0.105263 | 0.302632 | 0.059325 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| F_BASE | P_HIST | brier | 92 | -0.001951 |
| F_BASE | P_HIST | crps | 92 | 0.000049 |
| I_AR | I_LEVEL | brier | 92 | -0.011842 |
| I_AR | I_LEVEL | crps | 92 | -0.000404 |
| I_AR_NOGLOBAL | I_LEVEL | brier | 92 | -0.008836 |
| I_AR_NOGLOBAL | I_LEVEL | crps | 92 | -0.000379 |
| I_DELTA | I_LEVEL | brier | 92 | 0.012029 |
| I_DELTA | I_LEVEL | crps | 92 | -0.000039 |
| I_LEVEL | F_BASE | brier | 92 | 0.015720 |
| I_LEVEL | F_BASE | crps | 92 | 0.000501 |
| I_ROBUST | I_LEVEL | brier | 92 | -0.006299 |
| I_ROBUST | I_LEVEL | crps | 92 | -0.000239 |


The residuals are statistical surprises, not a measure of publicly unpriced information. Innovation rankings vary with the evaluation period. The same level parents and plain-change parents make this a test of feature construction rather than a search over unrelated inputs. Dropping the global innovation makes one incremental comparison, and no variant independently establishes gain beyond full historical rotation. Read the regime and stability files alongside retrospective point estimates.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
