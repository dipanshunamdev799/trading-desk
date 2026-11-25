# V21 Sector Contribution Forecasting

The sector lane ranks official sector outcomes using direct chronological forecasts, then compares bottom-up stock-to-sector locations under the same sector innovations. The index reconstruction weights on those sector paths come from the earlier-only daily simplex. Stock-level contribution estimates use the starting dated constituent weights. They preserve a separate unclassified or unmatched component where broad industry groups and official sector definitions diverge. Risk contributions use each simulated covariance with the aggregate portfolio, which can be signed. Sector outperformance is measured from the same simultaneous scenarios.

| horizon | sector | sector crps | stock to sector crps | mean relative | weighted return | weighted risk share | forward vol | statistical weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | auto | 0.017938 | 0.017295 | 0.005026 | 0.000122 | 0.084265 | 0.027403 | 0.105433 |
| 5 | bank | 0.013602 | 0.013337 | -0.000201 | 0.000096 | 0.309433 | 0.021228 | 0.175696 |
| 5 | consumer | 0.012846 | 0.012751 | -0.003368 | 0.000029 | 0.102237 | 0.018979 | 0.130973 |
| 5 | energy | 0.014594 | 0.014117 | 0.002698 | 0.000011 | 0.106121 | 0.022270 | 0.089660 |
| 5 | finance | 0.014695 | 0.014494 | -0.000064 | 0.000127 | 0.092808 | 0.022096 | 0.289081 |
| 5 | health | 0.011584 | 0.011518 | 0.002846 | -2.42e-06 | 0.029072 | 0.018841 | 0.058287 |
| 5 | it | 0.021376 | 0.020571 | -0.006010 | 0.000172 | 0.066469 | 0.033177 | 0.113899 |
| 5 | materials | 0.018561 | 0.018081 | 0.005162 | 0.000106 | 0.070433 | 0.028078 | 0.036971 |
| 21 | auto | 0.044313 | 0.038384 | 0.023375 | 0.000309 | 0.075625 | 0.053431 | 0.106364 |
| 21 | bank | 0.036653 | 0.029256 | 0.000354 | -0.000110 | 0.313510 | 0.044835 | 0.176251 |
| 21 | consumer | 0.031605 | 0.031002 | -0.010136 | -6.36e-06 | 0.100122 | 0.040322 | 0.131258 |
| 21 | energy | 0.028174 | 0.026001 | 0.012393 | -0.000078 | 0.095396 | 0.044518 | 0.099825 |
| 21 | finance | 0.035277 | 0.029787 | 0.000912 | 0.000274 | 0.100918 | 0.041827 | 0.283447 |
| 21 | health | 0.026495 | 0.028209 | 0.017715 | -0.000100 | 0.026030 | 0.033476 | 0.059004 |
| 21 | it | 0.071808 | 0.057230 | -0.041711 | 0.000508 | 0.062556 | 0.070348 | 0.111537 |
| 21 | materials | 0.046365 | 0.040832 | 0.023651 | 0.000245 | 0.064980 | 0.054304 | 0.032313 |

The dated stock weight file gives the beginning exposure, and the complete joint draws account for the terminal effect of drift without inserting subsequent holdings. These results separate the quality of absolute sector forecasts from the value of weighted sector-relative information. Changing the expected distribution of gains across sectors can have a small aggregate impact when stock-specific errors offset one another.

[sector-forecast-leaderboard.csv](sector-forecast-leaderboard.csv) · [sector-contribution-cases.csv.gz](sector-contribution-cases.csv.gz) · [constituent-contribution-cases.csv.gz](constituent-contribution-cases.csv.gz) · [joint-simultaneous-laws.npz](joint-simultaneous-laws.npz) · [sector-tracking-weights.csv](sector-tracking-weights.csv) · [market-factor-leaderboard.csv](market-factor-leaderboard.csv)
