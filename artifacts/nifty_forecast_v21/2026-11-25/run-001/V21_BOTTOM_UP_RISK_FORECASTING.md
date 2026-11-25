# V21 Bottom Up Risk Forecasting

The portfolio-risk study uses guarded constituent weights and covariance from up to **63 earlier daily rows**. It checks the full quadratic form, diagonal variance, and a shrinkage estimate retaining **80%** full covariance. Correlation, downside semi-volatility, recent index-proxy variance, variance breadth and stock-level volatility forecasts enter the causal risk correction separately from market-wide positioning. This evaluates the archived future realized-volatility target. The dispersion of terminal return scenarios serves a separate purpose.

The protected raw weekly ATM IV **0.037814 MAE**, weekly offshore/domestic **0.036469 MAE**, monthly GJR **0.033179 MAE and 0.199677 QLIKE**, and **0.152707 / 0.172872** expansion Brier anchors are recovered on their original dates. Equity covariance improves over the independence assumption by a substantial margin. The regularized covariance overlay’s best monthly QLIKE point estimate coexists with a worse MAE. Forecasts that borrow the fixed expansion probability receive a separate transition comparison below.

| horizon | model | n | active | mae | rmse | qlike |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | GJR | 265 | 265 | 0.040318 | 0.052756 | 0.359870 |
| 5 | independent_equity_variance | 265 | 265 | 0.079501 | 0.101639 | 6.739337 |
| 5 | iv_or_gjr_covariance | 265 | 216 | 0.037829 | 0.049081 | 0.292264 |
| 5 | iv_or_gjr_cross_sectional | 265 | 216 | 0.037883 | 0.049201 | 0.296590 |
| 5 | iv_or_gjr_cross_sectional_plus_positions | 265 | 216 | 0.037776 | 0.048956 | 0.297588 |
| 5 | offshore_plus_domestic | 265 | 265 | 0.036469 | 0.047773 | 0.290334 |
| 5 | raw_iv | 265 | 265 | 0.037814 | 0.048184 | 0.276187 |
| 5 | raw_stock_covariance | 265 | 265 | 0.053967 | 0.069879 | 0.545453 |
| 5 | recent_proxy_volatility | 265 | 265 | 0.045455 | 0.059236 | 0.383289 |
| 5 | shrunk_stock_covariance | 265 | 265 | 0.051521 | 0.068749 | 0.637395 |
| 21 | GJR | 217 | 217 | 0.033179 | 0.043304 | 0.199677 |
| 21 | independent_equity_variance | 217 | 217 | 0.091061 | 0.105814 | 7.987110 |
| 21 | iv_or_gjr_covariance | 217 | 152 | 0.036751 | 0.046134 | 0.198577 |
| 21 | iv_or_gjr_cross_sectional | 217 | 152 | 0.036891 | 0.046121 | 0.199329 |
| 21 | iv_or_gjr_cross_sectional_plus_positions | 217 | 152 | 0.037305 | 0.046558 | 0.207466 |
| 21 | offshore_plus_domestic | 217 | 217 | 0.049953 | 0.065614 | 0.484730 |
| 21 | raw_iv | 217 | 217 | 0.039406 | 0.049414 | 0.267623 |
| 21 | raw_stock_covariance | 217 | 217 | 0.059216 | 0.069188 | 0.557908 |
| 21 | recent_proxy_volatility | 217 | 217 | 0.045601 | 0.059832 | 0.448909 |
| 21 | shrunk_stock_covariance | 217 | 217 | 0.056906 | 0.068240 | 0.696644 |

| horizon | model | n | active | brier | log loss |
| --- | --- | --- | --- | --- | --- |
| 5 | cross_sectional_transition | 265 | 216 | 0.156178 | 0.470404 |
| 5 | fixed_iv_rv | 265 | 265 | 0.152707 | 0.461636 |
| 5 | student_EGARCH | 265 | 265 | 0.177866 | 0.514678 |
| 21 | cross_sectional_transition | 217 | 152 | 0.173267 | 0.638373 |
| 21 | fixed_iv_rv | 217 | 217 | 0.194367 | 0.831798 |
| 21 | student_EGARCH | 217 | 217 | 0.172872 | 0.689982 |

| horizon | model | reference | metric | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | iv_or_gjr_covariance | offshore_plus_domestic | mae | 265 | -0.001360 | -0.004923 | 0.002203 |
| 5 | iv_or_gjr_cross_sectional | offshore_plus_domestic | mae | 265 | -0.001414 | -0.004952 | 0.002124 |
| 5 | iv_or_gjr_cross_sectional_plus_positions | offshore_plus_domestic | mae | 265 | -0.001306 | -0.005219 | 0.002607 |
| 5 | iv_or_gjr_covariance | offshore_plus_domestic | qlike | 265 | -0.001930 | -0.036619 | 0.032759 |
| 5 | iv_or_gjr_cross_sectional | offshore_plus_domestic | qlike | 265 | -0.006256 | -0.048626 | 0.036114 |
| 5 | iv_or_gjr_cross_sectional_plus_positions | offshore_plus_domestic | qlike | 265 | -0.007254 | -0.057546 | 0.043039 |
| 21 | iv_or_gjr_covariance | GJR | mae | 217 | -0.003572 | -0.011377 | 0.004234 |
| 21 | iv_or_gjr_cross_sectional | GJR | mae | 217 | -0.003711 | -0.011577 | 0.004154 |
| 21 | iv_or_gjr_cross_sectional_plus_positions | GJR | mae | 217 | -0.004126 | -0.011868 | 0.003615 |
| 21 | iv_or_gjr_covariance | GJR | qlike | 217 | 0.001100 | -0.035874 | 0.038074 |
| 21 | iv_or_gjr_cross_sectional | GJR | qlike | 217 | 0.000348 | -0.036751 | 0.037448 |
| 21 | iv_or_gjr_cross_sectional_plus_positions | GJR | qlike | 217 | -0.007789 | -0.040839 | 0.025262 |

[risk-leaderboard.csv](risk-leaderboard.csv) · [risk-comparison-cases.csv.gz](risk-comparison-cases.csv.gz) · [risk-paired-block-intervals.csv](risk-paired-block-intervals.csv) · [daily-portfolio-risk-features.csv](daily-portfolio-risk-features.csv) · [risk-fit-receipts.csv](risk-fit-receipts.csv) · [bottom-up-volatility-laws.npz](bottom-up-volatility-laws.npz) · [risk-config.json](risk-config.json)
