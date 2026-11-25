# V21 Index Return Reconstruction

The official monthly weight reconstruction uses prior free-float capitalization and compounds each stock’s earlier price moves before computing the next portfolio weight. Under the five-session guard, the daily matched MAE is **0.424 basis points** on **396** dates, correlation **0.999872**. The five-session MAE is **1.383 basis points** and the 21-session MAE is **4.323 basis points**. These are tracking errors after component returns have occurred. They measure feasibility of reconstruction before forecasting.

| horizon | model | dates | bias | mae | rmse | tracking error | annualized tracking error | correlation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | january_dated_index_float_cap | 396 | 0.000048 | 0.000898 | 0.001439 | 0.001440 | 0.022864 | 0.984970 |
| 1 | january_equal240 | 396 | 0.000186 | 0.004269 | 0.005652 | 0.005656 | 0.089794 | 0.842867 |
| 1 | january_liquidity240 | 396 | 0.000159 | 0.003199 | 0.004243 | 0.004245 | 0.067393 | 0.899677 |
| 1 | january_sector_balanced | 396 | 0.000274 | 0.002694 | 0.004050 | 0.004046 | 0.064227 | 0.891693 |
| 1 | nifty50_guarded_no_action | 396 | -0.000315 | 0.000339 | 0.003620 | 0.003610 | 0.057315 | 0.920679 |
| 1 | nifty50_monthly_drift_lag0 | 396 | -0.000017 | 0.000030 | 0.000121 | 0.000120 | 0.001898 | 0.999899 |
| 1 | nifty50_monthly_drift_lag1 | 396 | -0.000016 | 0.000031 | 0.000121 | 0.000120 | 0.001910 | 0.999898 |
| 1 | nifty50_monthly_drift_lag10 | 396 | -0.000019 | 0.000053 | 0.000147 | 0.000146 | 0.002317 | 0.999853 |
| 1 | nifty50_monthly_drift_lag5 | 396 | -0.000018 | 0.000042 | 0.000136 | 0.000135 | 0.002142 | 0.999872 |
| 1 | nifty50_monthly_no_drift | 396 | -3.82e-06 | 0.000153 | 0.000245 | 0.000246 | 0.003897 | 0.999572 |
| 1 | nifty50_without_five_heaviest | 396 | 0.000067 | 0.001761 | 0.002211 | 0.002212 | 0.035122 | 0.965735 |
| 1 | sector_equal | 396 | 0.000183 | 0.002009 | 0.002620 | 0.002617 | 0.041547 | 0.949693 |
| 1 | sector_simplex | 396 | 0.000074 | 0.001419 | 0.001907 | 0.001908 | 0.030291 | 0.973789 |
| 1 | sector_train_pca3 | 396 | 3.82e-07 | 0.001719 | 0.002256 | 0.002259 | 0.035866 | 0.963564 |
| 5 | january_dated_index_float_cap | 392 | 0.000266 | 0.002014 | 0.003062 | 0.003054 | 0.021685 | 0.987022 |
| 5 | january_equal240 | 392 | 0.000936 | 0.009501 | 0.012301 | 0.012281 | 0.087185 | 0.848307 |
| 5 | january_liquidity240 | 392 | 0.000805 | 0.007068 | 0.009190 | 0.009167 | 0.065077 | 0.906205 |
| 5 | january_sector_balanced | 392 | 0.001412 | 0.005732 | 0.008244 | 0.008133 | 0.057739 | 0.908691 |
| 5 | nifty50_guarded_no_action | 392 | -0.001575 | 0.001627 | 0.008077 | 0.007932 | 0.056311 | 0.929748 |
| 5 | nifty50_monthly_drift_lag0 | 392 | -0.000078 | 0.000118 | 0.000282 | 0.000272 | 0.001928 | 0.999911 |
| 5 | nifty50_monthly_drift_lag1 | 392 | -0.000077 | 0.000125 | 0.000289 | 0.000279 | 0.001984 | 0.999904 |
| 5 | nifty50_monthly_drift_lag10 | 392 | -0.000089 | 0.000146 | 0.000298 | 0.000285 | 0.002020 | 0.999901 |
| 5 | nifty50_monthly_drift_lag5 | 392 | -0.000087 | 0.000138 | 0.000308 | 0.000296 | 0.002103 | 0.999890 |
| 5 | nifty50_monthly_no_drift | 392 | -9.48e-06 | 0.000356 | 0.000521 | 0.000522 | 0.003706 | 0.999623 |
| 5 | nifty50_without_five_heaviest | 392 | 0.000398 | 0.003808 | 0.004926 | 0.004917 | 0.034904 | 0.965864 |
| 5 | sector_equal | 392 | 0.001002 | 0.004522 | 0.005703 | 0.005622 | 0.039909 | 0.954912 |
| 5 | sector_simplex | 392 | 0.000407 | 0.003170 | 0.004125 | 0.004110 | 0.029180 | 0.976316 |
| 5 | sector_train_pca3 | 392 | 0.000086 | 0.003593 | 0.004842 | 0.004847 | 0.034411 | 0.967941 |
| 21 | january_dated_index_float_cap | 376 | 0.001616 | 0.004614 | 0.006288 | 0.006085 | 0.021078 | 0.986824 |
| 21 | january_equal240 | 376 | 0.005427 | 0.020869 | 0.029563 | 0.029099 | 0.100803 | 0.781646 |
| 21 | january_liquidity240 | 376 | 0.004249 | 0.015371 | 0.021136 | 0.020732 | 0.071818 | 0.868783 |
| 21 | january_sector_balanced | 376 | 0.007483 | 0.014498 | 0.020421 | 0.019026 | 0.065908 | 0.879633 |
| 21 | nifty50_guarded_no_action | 376 | -0.006941 | 0.007019 | 0.017655 | 0.016255 | 0.056310 | 0.913951 |
| 21 | nifty50_monthly_drift_lag0 | 376 | -0.000283 | 0.000405 | 0.000620 | 0.000553 | 0.001914 | 0.999902 |
| 21 | nifty50_monthly_drift_lag1 | 376 | -0.000274 | 0.000431 | 0.000646 | 0.000586 | 0.002031 | 0.999890 |
| 21 | nifty50_monthly_drift_lag10 | 376 | -0.000326 | 0.000400 | 0.000584 | 0.000485 | 0.001679 | 0.999927 |
| 21 | nifty50_monthly_drift_lag5 | 376 | -0.000320 | 0.000432 | 0.000646 | 0.000563 | 0.001949 | 0.999895 |
| 21 | nifty50_monthly_no_drift | 376 | -0.000064 | 0.000771 | 0.001042 | 0.001041 | 0.003606 | 0.999615 |
| 21 | nifty50_without_five_heaviest | 376 | 0.002657 | 0.009126 | 0.011000 | 0.010688 | 0.037026 | 0.958710 |
| 21 | sector_equal | 376 | 0.005026 | 0.010821 | 0.013483 | 0.012528 | 0.043397 | 0.942987 |
| 21 | sector_simplex | 376 | 0.002061 | 0.006365 | 0.008254 | 0.008003 | 0.027723 | 0.977154 |
| 21 | sector_train_pca3 | 376 | 0.000758 | 0.007797 | 0.010605 | 0.010592 | 0.036691 | 0.962592 |

Separate rows show lag zero as an ex-post month-end check, one and ten completed-session timing sensitivities, static monthly weights, unadjusted price returns, and loss of the five highest-weight holdings. Fixed equal, historical liquidity, float-cap snapshot and sector-balanced cohorts are explicit research portfolios. Twelve random January-eligible baskets accompany them. Sector weights from a nonnegative simplex and training-only three-component model are statistical coefficients. The reconstruction fits those coefficients using earlier daily observations only.

The combined split and bonus for Bajaj Finance on June 16, 2025 required a price-unit factor of **one tenth**. The routine multiplies simultaneous dated ratios, following the exchange-confirmed factor of **10**. Tata Motors’ October 14 surviving quote is rebased to the special-session open. Complete daily dummy-leg accounting is unavailable across the spin-off interval. The remaining largest weighted reconstruction error is retained in the dated episode file, including the November 12 listing of the spun-off company. Exact daily membership, divisor and first-publication history would further tighten reconstruction.

[index-tracking-leaderboard.csv](index-tracking-leaderboard.csv) · [index-tracking-cases.csv.gz](index-tracking-cases.csv.gz) · [daily-index-reconstruction.csv](daily-index-reconstruction.csv) · [daily-constituent-weight-coverage.csv](daily-constituent-weight-coverage.csv) · [tracking-official-episodes.csv](tracking-official-episodes.csv) · [sector-tracking-weights.csv](sector-tracking-weights.csv) · [tracking-config.json](tracking-config.json) · [tracking-and-dependence.png](tracking-and-dependence.png) · [sources/actions/2025-06-13.pdf](sources/actions/2025-06-13.pdf) · [sources/actions/2025-10-07.pdf](sources/actions/2025-10-07.pdf) · [sources/actions/2025-11-13.pdf](sources/actions/2025-11-13.pdf) · [NSE equity-index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
