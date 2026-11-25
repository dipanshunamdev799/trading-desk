# NIFTY V7 · Feature Redundancy

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

The first weekly fit used 300 matured target dates. The 38 native relative-return columns formed 25 training-only clusters using average linkage on 1 minus absolute Pearson correlation, cut at .25. Their entropy effective rank was 12.47; the first principal direction explained 26.9% of training variance. After removing price and NIFTY risk covariation with Ridge100, the rank was 13.12. Conditional correlations are residual associations and depend on that choice of controls.

| a | b | corr | price_residual_corr | same_lookback | identical_standardized_series |
| --- | --- | --- | --- | --- | --- |
| i_idx_Nifty_100_rel21 | i_idx_Nifty_Next_50_rel21 | 0.999391 | 0.999380 | True | False |
| i_idx_Nifty_100_rel5 | i_idx_Nifty_Next_50_rel5 | 0.999207 | 0.999116 | True | False |
| i_idx_Nifty_200_rel21 | i_idx_Nifty_500_rel21 | 0.980102 | 0.975638 | True | False |
| i_idx_Nifty_200_rel5 | i_idx_Nifty_500_rel5 | 0.975123 | 0.971062 | True | False |
| i_idx_NIFTY_HEALTHCARE_rel21 | i_nifty_pharma_rel21 | 0.971772 | 0.939720 | True | False |
| i_idx_NIFTY_HEALTHCARE_rel5 | i_nifty_pharma_rel5 | 0.964601 | 0.954758 | True | False |
| i_idx_Nifty_100_rel5 | i_idx_Nifty_200_rel5 | 0.919414 | 0.905012 | True | False |
| i_idx_Nifty_200_rel5 | i_idx_Nifty_Next_50_rel5 | 0.918518 | 0.904997 | True | False |
| i_idx_Nifty_100_rel21 | i_idx_Nifty_200_rel21 | 0.916759 | 0.901722 | True | False |
| i_idx_Nifty_200_rel21 | i_idx_Nifty_Next_50_rel21 | 0.911926 | 0.898441 | True | False |
| i_idx_Nifty_100_rel21 | i_idx_Nifty_500_rel21 | 0.897192 | 0.896421 | True | False |
| i_idx_Nifty_500_rel21 | i_idx_Nifty_Next_50_rel21 | 0.894038 | 0.895420 | True | False |
| i_bank_nifty_rel21 | i_nifty_financial_rel21 | 0.891908 | 0.901464 | True | False |
| i_idx_Nifty_100_rel5 | i_idx_Nifty_500_rel5 | 0.890261 | 0.876570 | True | False |
| i_idx_Nifty_500_rel5 | i_idx_Nifty_Next_50_rel5 | 0.889558 | 0.876639 | True | False |
| i_bank_nifty_rel5 | i_nifty_financial_rel5 | 0.829214 | 0.832047 | True | False |


| matrix | a | b | corr | last_date |
| --- | --- | --- | --- | --- |
| sector-volatility5.csv | bank_nifty | nifty_financial | 0.973418 | 2026-06-29 |
| sector-returns.csv | bank_nifty | nifty_financial | 0.965949 | 2026-06-29 |
| sector-momentum5.csv | bank_nifty | nifty_financial | 0.965847 | 2026-06-29 |
| sector-returns.csv | nifty_energy | nifty_metal | 0.783683 | 2026-06-29 |
| sector-momentum5.csv | nifty_auto | nifty_financial | 0.764848 | 2026-06-29 |
| sector-volatility5.csv | bank_nifty | nifty_auto | 0.759944 | 2026-06-29 |
| sector-momentum5.csv | nifty_energy | nifty_realty | 0.755708 | 2026-06-29 |
| sector-momentum5.csv | nifty_energy | nifty_metal | 0.754223 | 2026-06-29 |
| sector-momentum5.csv | nifty_financial | nifty_realty | 0.753251 | 2026-06-29 |
| sector-volatility5.csv | nifty_energy | nifty_metal | 0.751547 | 2026-06-29 |
| sector-volatility5.csv | nifty_auto | nifty_financial | 0.742760 | 2026-06-29 |
| sector-returns.csv | nifty_auto | nifty_financial | 0.732750 | 2026-06-29 |
| sector-returns.csv | bank_nifty | nifty_auto | 0.731405 | 2026-06-29 |
| sector-returns.csv | nifty_financial | nifty_realty | 0.710284 | 2026-06-29 |
| sector-volatility5.csv | nifty_financial | nifty_realty | 0.694865 | 2026-06-29 |


The native feature matrix contains common benchmark subtraction and overlapping five- and 21-session transformations. This creates mechanical dependence in addition to real economic correlation. Bank and financial services indices can share constituents and exposures. The available current instrument inventory does not reconstruct changing historical constituent weights, so these results measure realized covariance rather than the fraction of historical overlap attributable to constituents. No inferred index weights were used as data. `feature-correlations.csv` includes both same-lookback and cross-lookback pairs and checks exact duplicate standardized series. `sector-correlation-map.csv` independently compares sector daily returns, five-session momentum and five-session rolling volatility.

The cluster map uses training data at the first weekly cutoff. Per-fold cluster definitions, all pairwise values and signed loadings are saved. No outer outcome or outer feature observation enters a fold’s transform. [Training cluster map](feature-cluster-map.png)

Exact duplicate columns have a predictable Ridge effect. If one standardized feature has two copies, coefficients can split equally while preserving their combined prediction. The squared coefficient penalty on that combined weight is halved. Scaling both copies by 1/√2 restores the original penalty. The copy intervention changes representation while holding informational content and targets fixed, which distinguishes it from correlations between two related economic series.
