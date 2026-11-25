# V21 Cross Sectional Return Forecasting

Equity forecasts cover absolute return, market-relative return, sector-relative return, volatility-normalized return, probability of outperforming NIFTY, absolute return magnitude, realized volatility and factor-residual return. Marginal Gaussian laws use the archived location and an earlier volatility-based scale. Outperformance uses a separately estimated Bernoulli head. Stocks with missing realized prices retain their issuance eligibility and are absent from that score’s realized comparison. Losses are averaged within date first, giving each tested date one unit of weight. Rank correlation is also calculated within date before averaging. The Brier columns on strictly positive magnitude and volatility outcomes have no directional interpretation. Their comparative scores are MAE, RMSE, CRPS and interval calibration.

| horizon | model | target | dates | stock cases | rank corr | mae | rmse | brier | crps | coverage | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | factor_residual | absolute | 265 | 65,785 | -0.013173 | 0.034550 | 0.047657 | 0.252557 | 0.025300 | 0.786793 | 0.111298 |
| 5 | factor_residual | market_relative | 265 | 65,785 | -0.008793 | 0.030494 | 0.042678 | 0.253518 | 0.022445 | 0.742394 | 0.086813 |
| 5 | factor_residual | sector_relative | 265 | 65,785 | -0.019620 | 0.029222 | 0.041495 | 0.253050 | 0.021626 | 0.731334 | 0.080135 |
| 5 | history | absolute | 265 | 65,785 | 0.021325 | 0.034773 | 0.047882 | 0.254095 | 0.025432 | 0.785268 | 0.111298 |
| 5 | history | market_relative | 265 | 65,785 | 0.021239 | 0.030613 | 0.042867 | 0.254697 | 0.022543 | 0.739672 | 0.086813 |
| 5 | history | sector_relative | 265 | 65,785 | 0.020426 | 0.029310 | 0.041648 | 0.253608 | 0.021699 | 0.730285 | 0.080135 |
| 5 | independent | absolute | 265 | 65,785 | 0.008086 | 0.035717 | 0.049497 | 0.259333 | 0.026136 | 0.777611 | 0.111298 |
| 5 | independent | market_relative | 265 | 65,785 | 0.008586 | 0.031605 | 0.044552 | 0.263150 | 0.023317 | 0.730749 | 0.086813 |
| 5 | independent | sector_relative | 265 | 65,785 | 0.008458 | 0.030312 | 0.043302 | 0.263558 | 0.022479 | 0.720316 | 0.080135 |
| 5 | observed_reaction | absolute | 265 | 65,785 | -0.021203 | 0.034867 | 0.048096 | 0.255244 | 0.025510 | 0.782359 | 0.111298 |
| 5 | observed_reaction | market_relative | 265 | 65,785 | -0.011778 | 0.030496 | 0.042677 | 0.253467 | 0.022445 | 0.742303 | 0.086813 |
| 5 | observed_reaction | sector_relative | 265 | 65,785 | -0.023993 | 0.029224 | 0.041497 | 0.253002 | 0.021628 | 0.731410 | 0.080135 |
| 5 | partial_sector | absolute | 265 | 65,785 | -0.017132 | 0.034857 | 0.048090 | 0.255214 | 0.025506 | 0.782133 | 0.111298 |
| 5 | partial_sector | market_relative | 265 | 65,785 | -0.008450 | 0.030509 | 0.042695 | 0.253728 | 0.022457 | 0.742361 | 0.086813 |
| 5 | partial_sector | sector_relative | 265 | 65,785 | -0.012581 | 0.029228 | 0.041502 | 0.253142 | 0.021631 | 0.731336 | 0.080135 |
| 5 | pooled | absolute | 265 | 65,785 | -0.014346 | 0.034854 | 0.048081 | 0.255160 | 0.025502 | 0.782072 | 0.111298 |
| 5 | pooled | market_relative | 265 | 65,785 | -0.008793 | 0.030494 | 0.042678 | 0.253518 | 0.022445 | 0.742394 | 0.086813 |
| 5 | pooled | sector_relative | 265 | 65,785 | -0.019620 | 0.029222 | 0.041495 | 0.253050 | 0.021626 | 0.731334 | 0.080135 |
| 5 | random_aux_labels | absolute | 265 | 65,785 | -0.040601 | 0.034868 | 0.048060 | 0.255150 | 0.025502 | 0.782813 | 0.111298 |
| 5 | random_aux_labels | market_relative | 265 | 65,785 | -0.029268 | 0.030511 | 0.042652 | 0.253745 | 0.022450 | 0.741694 | 0.086813 |
| 5 | random_aux_labels | sector_relative | 265 | 65,785 | -0.021052 | 0.029210 | 0.041448 | 0.252831 | 0.021612 | 0.731593 | 0.080135 |
| 5 | technical | absolute | 265 | 65,785 | -0.020677 | 0.034865 | 0.048094 | 0.255226 | 0.025509 | 0.782390 | 0.111298 |
| 5 | technical | market_relative | 265 | 65,785 | -0.011672 | 0.030495 | 0.042677 | 0.253462 | 0.022445 | 0.742318 | 0.086813 |
| 5 | technical | sector_relative | 265 | 65,785 | -0.023801 | 0.029223 | 0.041497 | 0.252992 | 0.021627 | 0.731303 | 0.080135 |
| 21 | factor_residual | absolute | 217 | 53,784 | -0.015684 | 0.076355 | 0.102409 | 0.254157 | 0.055282 | 0.755488 | 0.232796 |
| 21 | factor_residual | market_relative | 217 | 53,784 | -0.023149 | 0.068037 | 0.094073 | 0.257850 | 0.049936 | 0.710107 | 0.181581 |
| 21 | factor_residual | sector_relative | 217 | 53,784 | -0.057797 | 0.065258 | 0.091368 | 0.256706 | 0.048125 | 0.699229 | 0.167613 |
| 21 | history | absolute | 217 | 53,784 | 0.027036 | 0.077779 | 0.104850 | 0.258823 | 0.056426 | 0.747042 | 0.232796 |
| 21 | history | market_relative | 217 | 53,784 | 0.027565 | 0.069533 | 0.096084 | 0.266112 | 0.051124 | 0.700484 | 0.181581 |
| 21 | history | sector_relative | 217 | 53,784 | 0.022253 | 0.066200 | 0.092859 | 0.261889 | 0.048931 | 0.691031 | 0.167613 |
| 21 | independent | absolute | 217 | 53,784 | 0.031978 | 0.083695 | 0.115833 | 0.274031 | 0.060813 | 0.726505 | 0.232796 |
| 21 | independent | market_relative | 217 | 53,784 | 0.028611 | 0.075540 | 0.107475 | 0.287411 | 0.055960 | 0.671030 | 0.181581 |
| 21 | independent | sector_relative | 217 | 53,784 | 0.020697 | 0.072403 | 0.104291 | 0.288831 | 0.053949 | 0.658515 | 0.167613 |
| 21 | observed_reaction | absolute | 217 | 53,784 | -0.026510 | 0.075518 | 0.102859 | 0.247732 | 0.054913 | 0.762520 | 0.232796 |
| 21 | observed_reaction | market_relative | 217 | 53,784 | -0.024501 | 0.068010 | 0.094026 | 0.257757 | 0.049917 | 0.710147 | 0.181581 |
| 21 | observed_reaction | sector_relative | 217 | 53,784 | -0.057751 | 0.065236 | 0.091326 | 0.256639 | 0.048107 | 0.699136 | 0.167613 |
| 21 | partial_sector | absolute | 217 | 53,784 | -0.013462 | 0.075693 | 0.103075 | 0.248839 | 0.055056 | 0.761219 | 0.232796 |
| 21 | partial_sector | market_relative | 217 | 53,784 | -0.010005 | 0.068201 | 0.094231 | 0.258849 | 0.050045 | 0.708849 | 0.181581 |
| 21 | partial_sector | sector_relative | 217 | 53,784 | -0.039461 | 0.065377 | 0.091486 | 0.257407 | 0.048201 | 0.697709 | 0.167613 |
| 21 | pooled | absolute | 217 | 53,784 | -0.025418 | 0.075526 | 0.102877 | 0.247727 | 0.054919 | 0.762744 | 0.232796 |
| 21 | pooled | market_relative | 217 | 53,784 | -0.023149 | 0.068037 | 0.094073 | 0.257850 | 0.049936 | 0.710107 | 0.181581 |
| 21 | pooled | sector_relative | 217 | 53,784 | -0.057797 | 0.065258 | 0.091368 | 0.256706 | 0.048125 | 0.699229 | 0.167613 |
| 21 | random_aux_labels | absolute | 217 | 53,784 | 0.000901 | 0.075427 | 0.102487 | 0.247512 | 0.054781 | 0.763491 | 0.232796 |
| 21 | random_aux_labels | market_relative | 217 | 53,784 | 0.013568 | 0.067875 | 0.093576 | 0.258124 | 0.049792 | 0.710109 | 0.181581 |
| 21 | random_aux_labels | sector_relative | 217 | 53,784 | 0.009720 | 0.064991 | 0.090768 | 0.255946 | 0.047881 | 0.698989 | 0.167613 |
| 21 | technical | absolute | 217 | 53,784 | -0.026399 | 0.075517 | 0.102859 | 0.247729 | 0.054913 | 0.762577 | 0.232796 |
| 21 | technical | market_relative | 217 | 53,784 | -0.024675 | 0.068008 | 0.094024 | 0.257744 | 0.049916 | 0.710165 | 0.181581 |
| 21 | technical | sector_relative | 217 | 53,784 | -0.058328 | 0.065235 | 0.091325 | 0.256635 | 0.048106 | 0.699135 | 0.167613 |

| horizon | model | target | dates | stock cases | rank corr | mae | rmse | brier | crps | coverage | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | history | factor_residual | 265 | 65,730 | 0.021653 | 0.029064 | 0.041387 | 0.254143 | 0.021559 | 0.718082 | 0.076809 |
| 5 | history | magnitude | 265 | 65,785 | 0.224906 | 0.023186 | 0.032478 | 0.024544 | 0.016956 | 0.836951 | 0.082361 |
| 5 | history | outperform_market | 265 | 65,785 | 0.041719 | 0.499516 | 0.501066 | 0.251067 | 0.251067 | 0.999939 | 1.281552 |
| 5 | history | realized_volatility | 265 | 65,785 | 0.438377 | 0.120196 | 0.168789 | 0.001512 | 0.088586 | 0.691638 | 0.316099 |
| 5 | history | vol_normalized | 265 | 65,755 | 0.032375 | 0.846636 | 1.156359 | 0.253062 | 0.620494 | 0.786385 | 2.563103 |
| 5 | pooled | factor_residual | 265 | 65,730 | -0.005024 | 0.028978 | 0.041221 | 0.253372 | 0.021483 | 0.718763 | 0.076809 |
| 5 | pooled | magnitude | 265 | 65,785 | 0.203444 | 0.022697 | 0.031803 | 0.022076 | 0.016546 | 0.857791 | 0.082361 |
| 5 | pooled | outperform_market | 265 | 65,785 | -0.007987 | 0.499666 | 0.500763 | 0.250763 | 0.250763 | 1.000000 | 1.281552 |
| 5 | pooled | realized_volatility | 265 | 65,785 | 0.395053 | 0.112807 | 0.159088 | 0.000761 | 0.082524 | 0.730606 | 0.316099 |
| 5 | pooled | vol_normalized | 265 | 65,755 | 0.012933 | 0.850476 | 1.160190 | 0.254771 | 0.623043 | 0.783970 | 2.563103 |
| 5 | random_aux_labels | factor_residual | 265 | 65,730 | -0.017236 | 0.028983 | 0.041196 | 0.253307 | 0.021479 | 0.719017 | 0.076809 |
| 5 | random_aux_labels | magnitude | 265 | 65,785 | 0.141127 | 0.023255 | 0.032500 | 0.024151 | 0.017002 | 0.832743 | 0.082361 |
| 5 | random_aux_labels | outperform_market | 265 | 65,785 | -0.017557 | 0.499720 | 0.500586 | 0.250586 | 0.250586 | 1.000000 | 1.281552 |
| 5 | random_aux_labels | realized_volatility | 265 | 65,785 | 0.240940 | 0.120821 | 0.169027 | 0.001569 | 0.089091 | 0.686731 | 0.316099 |
| 5 | random_aux_labels | vol_normalized | 265 | 65,755 | -0.010544 | 0.851572 | 1.160677 | 0.255234 | 0.623644 | 0.782992 | 2.563103 |
| 21 | history | factor_residual | 217 | 53,744 | 0.005971 | 0.066241 | 0.092685 | 0.265367 | 0.049006 | 0.670769 | 0.160656 |
| 21 | history | magnitude | 217 | 53,784 | 0.188713 | 0.049638 | 0.070453 | 0.023833 | 0.036375 | 0.828369 | 0.172269 |
| 21 | history | outperform_market | 217 | 53,784 | 0.053447 | 0.503334 | 0.508248 | 0.258316 | 0.258316 | 0.984022 | 1.281552 |
| 21 | history | realized_volatility | 217 | 53,784 | 0.613446 | 0.096440 | 0.132350 | 0.001217 | 0.071197 | 0.791293 | 0.322685 |
| 21 | history | vol_normalized | 217 | 53,759 | 0.038593 | 0.914885 | 1.214085 | 0.255789 | 0.664257 | 0.752235 | 2.563103 |
| 21 | pooled | factor_residual | 217 | 53,744 | -0.036678 | 0.064892 | 0.090842 | 0.255779 | 0.047884 | 0.680916 | 0.160656 |
| 21 | pooled | magnitude | 217 | 53,784 | 0.188639 | 0.048698 | 0.068393 | 0.019876 | 0.035425 | 0.843432 | 0.172269 |
| 21 | pooled | outperform_market | 217 | 53,784 | -0.010336 | 0.500962 | 0.503106 | 0.253116 | 0.253116 | 0.999666 | 1.281552 |
| 21 | pooled | realized_volatility | 217 | 53,784 | 0.540645 | 0.090269 | 0.123601 | 0.000537 | 0.067015 | 0.816735 | 0.322685 |
| 21 | pooled | vol_normalized | 217 | 53,759 | 0.006060 | 0.891373 | 1.186722 | 0.247714 | 0.647367 | 0.763627 | 2.563103 |
| 21 | random_aux_labels | factor_residual | 217 | 53,744 | 0.025059 | 0.064581 | 0.090276 | 0.255268 | 0.047649 | 0.682418 | 0.160656 |
| 21 | random_aux_labels | magnitude | 217 | 53,784 | 0.103174 | 0.049619 | 0.069828 | 0.022497 | 0.036245 | 0.825606 | 0.172269 |
| 21 | random_aux_labels | outperform_market | 217 | 53,784 | 0.009312 | 0.500066 | 0.501768 | 0.251771 | 0.251771 | 1.000000 | 1.281552 |
| 21 | random_aux_labels | realized_volatility | 217 | 53,784 | 0.327223 | 0.101119 | 0.137142 | 0.001319 | 0.074387 | 0.767403 | 0.322685 |
| 21 | random_aux_labels | vol_normalized | 217 | 53,759 | 0.042946 | 0.891358 | 1.184747 | 0.247451 | 0.646805 | 0.763605 | 2.563103 |

The stock-score archive retains company-group and event-present comparisons, and the calibration table follows both positive absolute returns and positive market-relative returns. A lower marginal CRPS can coexist with worse security ordering when most of the forecast benefit comes from a shared center or scale. The randomly aligned auxiliary model helps test that distinction.

[stock-leaderboard.csv](stock-leaderboard.csv) · [stock-sector-leaderboard.csv](stock-sector-leaderboard.csv) · [stock-date-scores.csv.gz](stock-date-scores.csv.gz) · [stock-sector-date-scores.csv.gz](stock-sector-date-scores.csv.gz) · [stock-probability-calibration.csv](stock-probability-calibration.csv) · [equity-forecast-laws.npz](equity-forecast-laws.npz) · [feature-definitions.json](feature-definitions.json)
