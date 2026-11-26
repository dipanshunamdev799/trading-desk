# V23 Complete model comparison

The original weekly 173/92 and monthly 141/76 cohorts contain 265 and 217 outcomes, with 53 and 11 nonoverlapping
origins. Inference preserves that calendar. Forecast coverage and the fully active subset are reported separately.
Each active candidate is measured against a fresh selection of the protected parent's exact same cases.

The full leaderboards include Brier, log loss, CRPS, accuracy, balanced accuracy, MAE, RMSE, rank correlation,
variance QLIKE, calibration and tail scores. The Pareto frontier compares Brier, CRPS, absolute 80% coverage error,
worst-cohort CRPS and an ordinal construction cost. That cost groups fixed controls, fitted calibration, estimated
weights and multi-component laws. It is a reproducibility aid rather than a monetary or timing cost.

| comparison | file | content |
| --- | --- | --- |
| Weekly and monthly direction and distribution | [original-horizon-leaderboard.csv](original-horizon-leaderboard.csv) | Complete metrics by horizon, information clock and original cohort. |
| Same-date parents and active coverage | [original-horizon-matched-comparisons.csv.gz](original-horizon-matched-comparisons.csv.gz) | Original outcome matching, active subset and cohort differences. |
| Robust pooling and component evidence | [ensemble-date-weights.csv.gz](ensemble-date-weights.csv.gz) | Earlier fit registry, cases used and per-expert weights. |
| Volatility, expansion, range, drawdown and tails | [path-risk-leaderboard.csv](path-risk-leaderboard.csv) | Risk forecasts and protected point/path results. |
| Point-volatility and expansion references | [protected-volatility-and-expansion-leaderboard.csv](protected-volatility-and-expansion-leaderboard.csv) | Legacy point MAE, QLIKE and expansion Brier. |
| Conditional return calibration | [conditional-calibration.csv.gz](conditional-calibration.csv.gz) | Full condition with explicit bin coverage and origin counts. |
| Model quality and complexity frontier | [forecast-pareto-frontier.csv](forecast-pareto-frontier.csv) | Avoid forcing one score or common winner across targets. |
| Dependence-aware uncertainty | [original-horizon-search-adjusted-intervals.csv.gz](original-horizon-search-adjusted-intervals.csv.gz) | 21/42-day block inference and search-family adjustment. |

| horizon | clock | model | n | disjoint | episodes | brier | crps | log loss | accuracy | balanced accuracy | mae | rmse | rank corr | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | residual_worst_environment | 265 | 53 | 57 | 0.218097 | 0.010116 | 0.626754 | 0.649057 | 0.650006 | 0.014181 | 0.020064 | 0.414238 | 0.822642 | 0.045790 |
| 5 | native_0910 | residual_ordinary_ridge | 265 | 53 | 57 | 0.218641 | 0.010150 | 0.628151 | 0.645283 | 0.645732 | 0.014218 | 0.020158 | 0.414063 | 0.818868 | 0.045790 |
| 5 | native_0910 | residual_environment_balanced | 265 | 53 | 57 | 0.218789 | 0.010152 | 0.628604 | 0.641509 | 0.642354 | 0.014214 | 0.020165 | 0.415392 | 0.818868 | 0.045790 |
| 5 | native_0910 | component_location_only | 265 | 53 | 57 | 0.220248 | 0.010090 | 0.631442 | 0.641509 | 0.640564 | 0.014264 | 0.020008 | 0.406595 | 0.830189 | 0.045829 |
| 5 | native_0910 | fixed_20pct_neutral | 265 | 53 | 57 | 0.223891 | 0.010093 | 0.639382 | 0.645283 | 0.645732 | 0.014199 | 0.019766 | 0.403171 | 0.826415 | 0.045766 |
| 5 | native_0910 | fixed_neutral_sign | 265 | 53 | 57 | 0.223891 | 0.010104 | 0.639382 | 0.645283 | 0.645732 | 0.014307 | 0.019870 | 0.402229 | 0.830189 | 0.046284 |
| 5 | preauction_0855 | complementary_residual_component | 265 | 53 | 57 | 0.232348 | 0.010294 | 0.654594 | 0.630189 | 0.627743 | 0.014264 | 0.019589 | 0.295044 | 0.815094 | 0.045648 |
| 5 | preauction_0855 | component_coherent_joint | 265 | 53 | 57 | 0.232653 | 0.010371 | 0.655577 | 0.637736 | 0.632710 | 0.014342 | 0.019757 | 0.271122 | 0.826415 | 0.047125 |
| 5 | preauction_0855 | component_location_only | 265 | 53 | 57 | 0.232821 | 0.010361 | 0.655647 | 0.626415 | 0.624365 | 0.014369 | 0.019657 | 0.262739 | 0.766038 | 0.041808 |
| 5 | preauction_0855 | fixed_20pct_neutral | 265 | 53 | 57 | 0.236091 | 0.010206 | 0.663185 | 0.581132 | 0.580244 | 0.014133 | 0.019245 | 0.293652 | 0.777358 | 0.042485 |
| 5 | preauction_0855 | residual_delayed_5 | 265 | 53 | 57 | 0.236987 | 0.010214 | 0.666568 | 0.584906 | 0.584517 | 0.014224 | 0.019232 | 0.304985 | 0.773585 | 0.041802 |
| 5 | preauction_0855 | fixed_neutral_sign | 265 | 53 | 57 | 0.236091 | 0.010217 | 0.663185 | 0.581132 | 0.580244 | 0.014188 | 0.019257 | 0.293465 | 0.769811 | 0.042075 |
| 5 | previous_1700 | component_coherent_joint | 263 | 53 | 56 | 0.238843 | 0.010804 | 0.670097 | 0.581749 | 0.572150 | 0.014800 | 0.020860 | 0.163334 | 0.821293 | 0.047949 |
| 5 | previous_1700 | complementary_residual_component | 263 | 53 | 56 | 0.239190 | 0.010808 | 0.670908 | 0.574144 | 0.566363 | 0.014833 | 0.020894 | 0.179059 | 0.813688 | 0.046186 |
| 5 | previous_1700 | component_iv_gjr_scale_only | 263 | 53 | 56 | 0.239301 | 0.010708 | 0.671011 | 0.608365 | 0.607432 | 0.014779 | 0.020629 | 0.180021 | 0.787072 | 0.043903 |
| 5 | previous_1700 | fixed_20pct_neutral | 263 | 53 | 56 | 0.239935 | 0.010681 | 0.672559 | 0.608365 | 0.607432 | 0.014694 | 0.020426 | 0.178212 | 0.787072 | 0.042355 |
| 5 | previous_1700 | agg_redundancy | 263 | 53 | 56 | 0.240301 | 0.010694 | 0.673530 | 0.566540 | 0.565423 | 0.014647 | 0.020461 | 0.187392 | 0.790875 | 0.042500 |
| 5 | previous_1700 | agg_loss_robust | 263 | 53 | 56 | 0.240256 | 0.010697 | 0.673453 | 0.574144 | 0.573149 | 0.014666 | 0.020489 | 0.186805 | 0.790875 | 0.042460 |
| 21 | native_0910 | component_historical_shape_only | 217 | 11 | 46 | 0.210496 | 0.022911 | 0.605351 | 0.709677 | 0.732485 | 0.029248 | 0.042508 | 0.461349 | 0.705069 | 0.071099 |
| 21 | native_0910 | residual_worst_environment | 217 | 11 | 46 | 0.218108 | 0.023122 | 0.624068 | 0.599078 | 0.627135 | 0.029607 | 0.043735 | 0.393177 | 0.723502 | 0.071612 |
| 21 | native_0910 | residual_delayed_5 | 217 | 11 | 46 | 0.218900 | 0.022977 | 0.628996 | 0.603687 | 0.630069 | 0.029631 | 0.043098 | 0.453615 | 0.723502 | 0.071571 |
| 21 | native_0910 | complementary_residual_component | 217 | 11 | 46 | 0.221205 | 0.023010 | 0.635743 | 0.608295 | 0.638827 | 0.029426 | 0.043066 | 0.473929 | 0.760369 | 0.084013 |
| 21 | preauction_0855 | residual_hierarchical | 217 | 11 | 46 | 0.240990 | 0.024253 | 0.673330 | 0.502304 | 0.507291 | 0.032847 | 0.044789 | 0.052860 | 0.741935 | 0.083420 |
| 21 | preauction_0855 | residual_worst_environment | 217 | 11 | 46 | 0.241321 | 0.024251 | 0.673830 | 0.465438 | 0.464021 | 0.032916 | 0.044823 | 0.032697 | 0.741935 | 0.083390 |
| 21 | preauction_0855 | complementary_residual_component | 217 | 11 | 46 | 0.241909 | 0.024345 | 0.675980 | 0.497696 | 0.499698 | 0.033161 | 0.045026 | -0.043735 | 0.764977 | 0.092998 |
| 21 | preauction_0855 | residual_delayed_5 | 217 | 11 | 46 | 0.248165 | 0.024326 | 0.688545 | 0.456221 | 0.452330 | 0.033055 | 0.044398 | 0.038937 | 0.728111 | 0.083347 |
| 21 | previous_1700 | protected_direction | 216 | 11 | 46 | 0.250000 | 0.025642 | 0.693147 | 0.435185 | 0.500000 | 0.033553 | 0.044980 | 0.151149 | 0.699074 | 0.080992 |
| 21 | previous_1700 | fixed_20pct_neutral | 216 | 11 | 46 | 0.285015 | 0.027478 | 0.778101 | 0.476852 | 0.446547 | 0.037566 | 0.049623 | -0.135280 | 0.703704 | 0.089753 |
| 21 | previous_1700 | fixed_neutral_sign | 216 | 11 | 46 | 0.285015 | 0.027868 | 0.778101 | 0.476852 | 0.446547 | 0.038336 | 0.050474 | -0.139843 | 0.699074 | 0.093171 |
| 21 | previous_1700 | history_only | 216 | 11 | 46 | 0.300768 | 0.027334 | 0.801600 | 0.314815 | 0.332403 | 0.035499 | 0.047058 | -0.324432 | 0.717593 | 0.091647 |

| horizon | model | brier | crps | coverage error | worst cohort crps | complexity |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | calibration_pit_fit | 0.222437 | 0.010297 | 0.003774 | 0.010439 | 1 |
| 5 | calibration_sign_fit | 0.222078 | 0.010143 | 0.037736 | 0.010277 | 1 |
| 5 | component_location_only | 0.220248 | 0.010090 | 0.030189 | 0.010120 | 3 |
| 5 | fixed_20pct_history | 0.224221 | 0.010112 | 0.022642 | 0.010133 | 0 |
| 5 | fixed_20pct_neutral | 0.223891 | 0.010093 | 0.026415 | 0.010150 | 0 |
| 5 | fixed_neutral_sign | 0.223891 | 0.010104 | 0.030189 | 0.010118 | 1 |
| 5 | fixed_zero_weight | 0.222142 | 0.010121 | 0.022642 | 0.010241 | 0 |
| 5 | protected_direction | 0.220133 | 0.010180 | 0.026415 | 0.010311 | 0 |
| 5 | protected_distribution | 0.222142 | 0.010121 | 0.022642 | 0.010241 | 0 |
| 5 | residual_delayed_5 | 0.221343 | 0.010194 | 0.003774 | 0.010452 | 2 |
| 5 | residual_ordinary_ridge | 0.218641 | 0.010150 | 0.018868 | 0.010360 | 2 |
| 5 | residual_worst_environment | 0.218097 | 0.010116 | 0.022642 | 0.010322 | 2 |
| 21 | complementary_residual_component | 0.221205 | 0.023010 | 0.039631 | 0.026865 | 3 |
| 21 | component_coherent_joint | 0.225508 | 0.023243 | 0.021198 | 0.027153 | 3 |
| 21 | component_historical_shape_only | 0.210496 | 0.022911 | 0.094931 | 0.027895 | 3 |
| 21 | fixed_20pct_history | 0.230132 | 0.023484 | 0.076498 | 0.027221 | 0 |
| 21 | fixed_20pct_neutral | 0.222577 | 0.023298 | 0.085714 | 0.027215 | 0 |
| 21 | fixed_neutral_sign | 0.222577 | 0.023171 | 0.085714 | 0.027423 | 1 |
| 21 | protected_direction | 0.223431 | 0.023174 | 0.044240 | 0.027666 | 0 |
| 21 | residual_delayed_5 | 0.218900 | 0.022977 | 0.076498 | 0.026546 | 2 |
| 21 | residual_hierarchical | 0.219004 | 0.023168 | 0.067281 | 0.026564 | 2 |
| 21 | residual_huber | 0.220721 | 0.023141 | 0.071889 | 0.026939 | 2 |
| 21 | residual_worst_environment | 0.218108 | 0.023122 | 0.076498 | 0.026636 | 2 |

[path-risk-matched-intervals.csv.gz](path-risk-matched-intervals.csv.gz) · [path-risk-cohort-deltas.csv.gz](path-risk-cohort-deltas.csv.gz) · [probability-reliability-bins.csv.gz](probability-reliability-bins.csv.gz) · [forecast-calibration-leaderboard.csv](forecast-calibration-leaderboard.csv) · [domestic-shape-attribution-leaderboard.csv](domestic-shape-attribution-leaderboard.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
