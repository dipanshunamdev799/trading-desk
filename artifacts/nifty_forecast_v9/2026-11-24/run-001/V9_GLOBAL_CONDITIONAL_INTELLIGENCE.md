# NIFTY V9 · Global Conditional Intelligence

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

V9 treats foreign observations as five separate candidate roles: a direct directional contribution, cross-market residual and correlation change, a forecasting gate, a volatility predictor and a conditional residual weighting signal. Reused snapshots include V8 FRED Nasdaq Composite, US ten-year yield and VIX, and the V5 as-of Upstox global-equity, FX and oil series. FRED rows were made eligible after the V8 two-US-business-day plus 23:00 New York availability buffer. Inherited cash/futures availability rules remain documented. No same-day foreign closing information after a domestic decision is assumed. [NASDAQ Composite source](https://fred.stlouisfed.org/series/NASDAQCOM) · [Upstox historical data](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)

The direct block uses India-versus-global residual, rolling correlation change and global shock. `T_GLOBAL_LOCATION` holds fixed the predictors used by `T_GLOBAL_LAW`, differing only in residual-law weighting. `J9_GLOBAL_GATE` adds six foreign series and divergence/shock statistics to the identical domestic reliability gate. The global risk regression uses that same domestic-plus-global feature set against the actual future path RMS, with historical realized outcomes prior to the gate. These are predictive comparisons against domestic parents rather than evidence of foreign causality.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_COMPACT | 92 | 19 | 12.363138 | 0.554348 | 0.538703 | 0.252389 | 0.699219 | 0.011908 | 0.015752 | 0.022145 | 0.005906 | 0.369565 | 0.706522 | 0.034588 |
| T_GLOBAL_DIRECT | 92 | 19 | 12.363138 | 0.565217 | 0.548137 | 0.248303 | 0.690360 | 0.011825 | 0.015666 | 0.022015 | 0.005879 | 0.380435 | 0.717391 | 0.035805 |
| T_GLOBAL_LOCATION | 92 | 19 | 12.363138 | 0.543478 | 0.529269 | 0.253520 | 0.701751 | 0.011971 | 0.015887 | 0.022189 | 0.005922 | 0.380435 | 0.695652 | 0.035907 |
| T_GLOBAL_LAW | 92 | 19 | 12.363138 | 0.554348 | 0.535317 | 0.259633 | 0.717315 | 0.012060 | 0.015820 | 0.022435 | 0.006004 | 0.358696 | 0.695652 | 0.035348 |
| J9_DOMESTIC_GATE | 92 | 19 | 12.363138 | 0.815217 | 0.819303 | 0.188234 | 0.565092 | 0.010372 | 0.013682 | 0.020460 | 0.005212 | 0.554348 | 0.793478 | 0.040532 |
| J9_GLOBAL_GATE | 92 | 19 | 12.363138 | 0.793478 | 0.797049 | 0.189435 | 0.567980 | 0.010442 | 0.013825 | 0.020618 | 0.005243 | 0.543478 | 0.793478 | 0.040781 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_COMPACT | 173 | 35 | 28.982745 | 0.462428 | 0.482996 | 0.323155 | 0.873586 | 0.013434 | 0.017990 | 0.024756 | 0.006685 | 0.445087 | 0.699422 | 0.043751 |
| T_GLOBAL_DIRECT | 173 | 35 | 28.982745 | 0.473988 | 0.492375 | 0.324741 | 0.874285 | 0.013579 | 0.018208 | 0.024825 | 0.006758 | 0.462428 | 0.693642 | 0.043963 |
| T_GLOBAL_LOCATION | 173 | 35 | 28.982745 | 0.473988 | 0.493522 | 0.323618 | 0.872457 | 0.013524 | 0.018109 | 0.024790 | 0.006725 | 0.450867 | 0.699422 | 0.043986 |
| T_GLOBAL_LAW | 173 | 35 | 28.982745 | 0.473988 | 0.494669 | 0.320671 | 0.867279 | 0.013607 | 0.018258 | 0.024734 | 0.006768 | 0.439306 | 0.710983 | 0.043907 |
| J9_DOMESTIC_GATE | 173 | 35 | 28.982745 | 0.514451 | 0.533806 | 0.274797 | 0.752603 | 0.011778 | 0.016359 | 0.022223 | 0.005856 | 0.479769 | 0.803468 | 0.049754 |
| J9_GLOBAL_GATE | 173 | 35 | 28.982745 | 0.520231 | 0.539069 | 0.273725 | 0.749953 | 0.011732 | 0.016335 | 0.022133 | 0.005834 | 0.479769 | 0.797688 | 0.049764 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| J9_GLOBAL_GATE | J9_DOMESTIC_GATE | brier | 92 | -0.001201 |
| J9_GLOBAL_GATE | J9_DOMESTIC_GATE | crps | 92 | -0.000071 |
| T_GLOBAL_DIRECT | P_COMPACT | brier | 92 | 0.004086 |
| T_GLOBAL_DIRECT | P_COMPACT | crps | 92 | 0.000083 |
| T_GLOBAL_LAW | T_GLOBAL_LOCATION | brier | 92 | -0.006114 |
| T_GLOBAL_LAW | T_GLOBAL_LOCATION | crps | 92 | -0.000089 |
| T_GLOBAL_LOCATION | P_COMPACT | brier | 92 | -0.001131 |
| T_GLOBAL_LOCATION | P_COMPACT | crps | 92 | -0.000063 |


| cohort | horizon | assessed | dom_vol_mae | global_vol_mae |
| --- | --- | --- | --- | --- |
| early | 5 | 120 | 0.074563 | 0.066883 |
| early | 21 | 79 | 0.102450 | 0.096693 |
| later | 5 | 92 | 0.055356 | 0.056184 |
| later | 21 | 76 | 0.043957 | 0.046798 |


The global gate gives a tiny combined weekly advantage relative to the domestic gate and marginally worsens later weekly Brier and CRPS. Earlier annualized volatility MAE improves from **.074563 to .066883** weekly and **.102450 to .096693** monthly, but later weekly/later monthly volatility MAE worsens. Those are matched prior-gate eligible date sets, and the later reversal in risk gains is a reason to preserve the global-risk hypothesis as conditional and exploratory. Global timing receipts were reconstructed from frozen archives, with newer completed domestic sessions scored in a separated cohort.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
