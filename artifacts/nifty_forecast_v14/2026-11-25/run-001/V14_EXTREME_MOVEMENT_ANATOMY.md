# V14 Extreme Movement Anatomy

Fixed targets span large positive and negative endpoints, high–low ranges, ±5% excursions and 1.2% opening gaps. Five-session endpoint limits are ±3%, and 21-session limits are ±5%. Fixed range levels are 5.5% and 10%. Relative tails use the 10th/90th training quantiles, and IV-relative endpoint tails use ±1.5 origin-time horizon standard deviations. A persistent extreme also requires at least 65% of daily moves to align with the final direction and a largest-shock share of absolute movement at or below one-half. Acceleration compares signed mean log changes in the first and last portions of the realized window. An episode merges overlapping positive-label windows. Greedy disjoint outcome counts are also retained.

| horizon | event | eligible | count | frequency | distinct_episodes | positive_disjoint | eligible_disjoint |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | upper_fixed | 265 | 23 | 0.086792 | 6 | 8 | 53 |
| 5 | lower_fixed | 265 | 10 | 0.037736 | 4 | 5 | 53 |
| 5 | range_fixed | 265 | 19 | 0.071698 | 4 | 7 | 53 |
| 5 | upper_excursion_fixed | 265 | 11 | 0.041509 | 3 | 4 | 53 |
| 5 | lower_excursion_fixed | 265 | 4 | 0.015094 | 2 | 3 | 53 |
| 5 | upper_relative | 265 | 35 | 0.132075 | 8 | 10 | 53 |
| 5 | lower_relative | 265 | 37 | 0.139623 | 7 | 11 | 53 |
| 5 | range_relative | 265 | 45 | 0.169811 | 6 | 13 | 53 |
| 5 | high_relative | 265 | 38 | 0.143396 | 9 | 12 | 53 |
| 5 | low_relative | 265 | 42 | 0.158491 | 7 | 12 | 53 |
| 5 | upper_iv_scaled | 265 | 19 | 0.071698 | 6 | 7 | 53 |
| 5 | lower_iv_scaled | 265 | 19 | 0.071698 | 5 | 7 | 53 |
| 5 | range_iv_scaled | 265 | 42 | 0.158491 | 11 | 15 | 53 |
| 5 | expand | 265 | 87 | 0.328302 | 23 | 28 | 53 |
| 5 | contract | 265 | 76 | 0.286792 | 21 | 24 | 53 |
| 5 | high_state | 265 | 96 | 0.362264 | 7 | 23 | 53 |
| 5 | enter_high | 170 | 42 | 0.247059 | 12 | 12 | 40 |
| 5 | exit_high | 95 | 41 | 0.431579 | 13 | 13 | 23 |
| 5 | persist_high | 265 | 53 | 0.200000 | 8 | 16 | 53 |
| 5 | rapid_risk | 265 | 35 | 0.132075 | 16 | 18 | 53 |
| 5 | variance_extreme | 265 | 44 | 0.166038 | 3 | 11 | 53 |
| 5 | persist_up | 265 | 19 | 0.071698 | 7 | 8 | 53 |
| 5 | persist_down | 265 | 18 | 0.067925 | 8 | 9 | 53 |
| 5 | gap_fixed | 265 | 49 | 0.184906 | 4 | 10 | 53 |
| 5 | gap_relative | 265 | 30 | 0.113208 | 2 | 7 | 53 |
| 5 | acceleration | 265 | 27 | 0.101887 | 18 | 18 | 53 |
| 21 | upper_fixed | 217 | 18 | 0.082949 | 2 | 2 | 11 |
| 21 | lower_fixed | 217 | 29 | 0.133641 | 2 | 2 | 11 |
| 21 | range_fixed | 217 | 34 | 0.156682 | 2 | 3 | 11 |
| 21 | upper_excursion_fixed | 217 | 28 | 0.129032 | 4 | 4 | 11 |
| 21 | lower_excursion_fixed | 217 | 55 | 0.253456 | 2 | 6 | 11 |
| 21 | upper_relative | 217 | 33 | 0.152074 | 3 | 3 | 11 |
| 21 | lower_relative | 217 | 48 | 0.221198 | 3 | 5 | 11 |
| 21 | range_relative | 217 | 76 | 0.350230 | 2 | 5 | 11 |
| 21 | high_relative | 217 | 34 | 0.156682 | 4 | 4 | 11 |
| 21 | low_relative | 217 | 50 | 0.230415 | 1 | 3 | 11 |
| 21 | upper_iv_scaled | 217 | 10 | 0.046083 | 1 | 1 | 11 |
| 21 | lower_iv_scaled | 217 | 35 | 0.161290 | 3 | 3 | 11 |
| 21 | range_iv_scaled | 217 | 63 | 0.290323 | 2 | 5 | 11 |
| 21 | expand | 217 | 81 | 0.373272 | 3 | 6 | 11 |
| 21 | contract | 217 | 51 | 0.235023 | 2 | 4 | 11 |
| 21 | high_state | 217 | 96 | 0.442396 | 2 | 6 | 11 |
| 21 | enter_high | 150 | 40 | 0.266667 | 2 | 2 | 8 |
| 21 | exit_high | 67 | 11 | 0.164179 | 1 | 1 | 5 |
| 21 | persist_high | 217 | 76 | 0.350230 | 2 | 5 | 11 |
| 21 | rapid_risk | 217 | 39 | 0.179724 | 3 | 5 | 11 |
| 21 | variance_extreme | 217 | 36 | 0.165899 | 1 | 2 | 11 |
| 21 | persist_up | 217 | 5 | 0.023041 | 2 | 2 | 11 |
| 21 | persist_down | 217 | 5 | 0.023041 | 2 | 2 | 11 |
| 21 | gap_fixed | 217 | 101 | 0.465438 | 2 | 7 | 11 |
| 21 | gap_relative | 217 | 55 | 0.253456 | 1 | 3 | 11 |
| 21 | acceleration | 217 | 40 | 0.184332 | 4 | 6 | 11 |

| horizon | event | clock | measurement | positive_avg | negative_avg | positive_n | negative_n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | upper_fixed | realized decomposition | peak_shock_share | 0.456281 | 0.397056 | 23 | 242 |
| 5 | upper_fixed | realized decomposition | aligned_fraction | 0.791304 | 0.628926 | 23 | 242 |
| 5 | upper_fixed | realized decomposition | net_overnight | 0.023190 | -0.001125 | 23 | 242 |
| 5 | upper_fixed | realized decomposition | net_intraday | 0.022047 | -0.003430 | 23 | 242 |
| 5 | upper_fixed | available at origin | atm1 | 0.002690 | 0.000101 | 23 | 242 |
| 5 | upper_fixed | available at origin | finance | -0.005094 | 0.000298 | 23 | 242 |
| 5 | upper_fixed | available at origin | breadth5 | -0.002519 | 0.000179 | 23 | 242 |
| 5 | upper_fixed | available at origin | sector_sync | 0.443823 | 0.426024 | 23 | 240 |
| 5 | lower_fixed | realized decomposition | peak_shock_share | 0.321862 | 0.405347 | 10 | 255 |
| 5 | lower_fixed | realized decomposition | aligned_fraction | 0.700000 | 0.640784 | 10 | 255 |
| 5 | lower_fixed | realized decomposition | net_overnight | -0.028278 | 0.002133 | 10 | 255 |
| 5 | lower_fixed | realized decomposition | net_intraday | -0.012627 | -0.000772 | 10 | 255 |
| 5 | lower_fixed | available at origin | atm1 | 0.004949 | 0.000145 | 10 | 255 |
| 5 | lower_fixed | available at origin | finance | -0.000872 | -0.000142 | 10 | 255 |
| 5 | lower_fixed | available at origin | breadth5 | 0.000821 | -0.000089 | 10 | 255 |
| 5 | lower_fixed | available at origin | sector_sync | 0.553991 | 0.422584 | 10 | 253 |
| 5 | range_relative | realized decomposition | peak_shock_share | 0.379693 | 0.406799 | 45 | 220 |
| 5 | range_relative | realized decomposition | aligned_fraction | 0.653333 | 0.640909 | 45 | 220 |
| 5 | range_relative | realized decomposition | net_overnight | -0.000262 | 0.001241 | 45 | 220 |
| 5 | range_relative | realized decomposition | net_intraday | 0.000056 | -0.001480 | 45 | 220 |
| 5 | range_relative | available at origin | atm1 | 0.004201 | -0.000467 | 45 | 220 |
| 5 | range_relative | available at origin | finance | -0.003167 | 0.000443 | 45 | 220 |
| 5 | range_relative | available at origin | breadth5 | -0.000712 | 0.000080 | 45 | 220 |
| 5 | range_relative | available at origin | sector_sync | 0.525962 | 0.407272 | 45 | 218 |
| 5 | persist_up | realized decomposition | peak_shock_share | 0.391126 | 0.403051 | 19 | 246 |
| 5 | persist_up | realized decomposition | aligned_fraction | 0.863158 | 0.626016 | 19 | 246 |
| 5 | persist_up | realized decomposition | net_overnight | 0.019855 | -0.000472 | 19 | 246 |
| 5 | persist_up | realized decomposition | net_intraday | 0.020972 | -0.002933 | 19 | 246 |
| 5 | persist_up | available at origin | atm1 | -0.003434 | 0.000616 | 19 | 246 |
| 5 | persist_up | available at origin | finance | -0.006774 | 0.000340 | 19 | 246 |
| 5 | persist_up | available at origin | breadth5 | -0.004178 | 0.000264 | 19 | 246 |
| 5 | persist_up | available at origin | sector_sync | 0.490195 | 0.422705 | 19 | 244 |
| 5 | persist_down | realized decomposition | peak_shock_share | 0.352745 | 0.405800 | 18 | 247 |
| 5 | persist_down | realized decomposition | aligned_fraction | 0.811111 | 0.630769 | 18 | 247 |
| 5 | persist_down | realized decomposition | net_overnight | -0.014681 | 0.002128 | 18 | 247 |
| 5 | persist_down | realized decomposition | net_intraday | -0.015165 | -0.000203 | 18 | 247 |
| 5 | persist_down | available at origin | atm1 | 0.000550 | 0.000310 | 18 | 247 |
| 5 | persist_down | available at origin | finance | -0.002370 | -0.000009 | 18 | 247 |
| 5 | persist_down | available at origin | breadth5 | 0.003109 | -0.000285 | 18 | 247 |
| 5 | persist_down | available at origin | sector_sync | 0.490557 | 0.422954 | 18 | 245 |
| 21 | upper_fixed | realized decomposition | peak_shock_share | 0.144000 | 0.142607 | 18 | 199 |
| 21 | upper_fixed | realized decomposition | aligned_fraction | 0.584656 | 0.561857 | 18 | 199 |
| 21 | upper_fixed | realized decomposition | net_overnight | 0.027700 | -0.001391 | 18 | 199 |
| 21 | upper_fixed | realized decomposition | net_intraday | 0.051718 | -0.015119 | 18 | 199 |
| 21 | upper_fixed | available at origin | atm1 | 0.000355 | 0.000156 | 18 | 199 |
| 21 | upper_fixed | available at origin | finance | 0.000518 | -0.000153 | 18 | 199 |
| 21 | upper_fixed | available at origin | breadth5 | 0.000495 | 0.001856 | 18 | 199 |
| 21 | upper_fixed | available at origin | sector_sync | 0.457786 | 0.413946 | 18 | 199 |
| 21 | lower_fixed | realized decomposition | peak_shock_share | 0.118837 | 0.146407 | 29 | 188 |
| 21 | lower_fixed | realized decomposition | aligned_fraction | 0.535304 | 0.568136 | 29 | 188 |
| 21 | lower_fixed | realized decomposition | net_overnight | -0.052318 | 0.009250 | 29 | 188 |
| 21 | lower_fixed | realized decomposition | net_intraday | -0.030551 | -0.006340 | 29 | 188 |
| 21 | lower_fixed | available at origin | atm1 | 0.000652 | 0.000098 | 29 | 188 |
| 21 | lower_fixed | available at origin | finance | -0.001045 | 0.000049 | 29 | 188 |
| 21 | lower_fixed | available at origin | breadth5 | 0.002274 | 0.001661 | 29 | 188 |
| 21 | lower_fixed | available at origin | sector_sync | 0.407353 | 0.419161 | 29 | 188 |
| 21 | range_relative | realized decomposition | peak_shock_share | 0.140769 | 0.143775 | 76 | 141 |
| 21 | range_relative | realized decomposition | aligned_fraction | 0.558271 | 0.566700 | 76 | 141 |
| 21 | range_relative | realized decomposition | net_overnight | 0.000507 | 0.001299 | 76 | 141 |
| 21 | range_relative | realized decomposition | net_intraday | -0.008558 | -0.010124 | 76 | 141 |
| 21 | range_relative | available at origin | atm1 | 0.002085 | -0.000859 | 76 | 141 |
| 21 | range_relative | available at origin | finance | 0.000088 | -0.000197 | 76 | 141 |
| 21 | range_relative | available at origin | breadth5 | 0.000376 | 0.002481 | 76 | 141 |
| 21 | range_relative | available at origin | sector_sync | 0.496383 | 0.375108 | 76 | 141 |
| 21 | persist_up | realized decomposition | peak_shock_share | 0.137409 | 0.142848 | 5 | 212 |
| 21 | persist_up | realized decomposition | aligned_fraction | 0.676190 | 0.561096 | 5 | 212 |
| 21 | persist_up | realized decomposition | net_overnight | 0.028698 | 0.000369 | 5 | 212 |
| 21 | persist_up | realized decomposition | net_intraday | 0.014935 | -0.010153 | 5 | 212 |
| 21 | persist_up | available at origin | atm1 | -0.000538 | 0.000189 | 5 | 212 |
| 21 | persist_up | available at origin | finance | -0.002764 | -0.000034 | 5 | 212 |
| 21 | persist_up | available at origin | breadth5 | 0.007682 | 0.001603 | 5 | 212 |
| 21 | persist_up | available at origin | sector_sync | 0.552314 | 0.414405 | 5 | 212 |
| 21 | persist_down | realized decomposition | peak_shock_share | 0.148296 | 0.142591 | 5 | 212 |
| 21 | persist_down | realized decomposition | aligned_fraction | 0.685714 | 0.560872 | 5 | 212 |
| 21 | persist_down | realized decomposition | net_overnight | -0.000013 | 0.001046 | 5 | 212 |
| 21 | persist_down | realized decomposition | net_intraday | -0.040036 | -0.008857 | 5 | 212 |
| 21 | persist_down | available at origin | atm1 | -0.001762 | 0.000218 | 5 | 212 |
| 21 | persist_down | available at origin | finance | -0.006105 | 0.000044 | 5 | 212 |
| 21 | persist_down | available at origin | breadth5 | 0.001145 | 0.001757 | 5 | 212 |
| 21 | persist_down | available at origin | sector_sync | 0.296010 | 0.420450 | 5 | 212 |

Conditional associations use matched cohort histories. Future path components explain realized moves after the fact. The predictors in the as-of rows were available when forecasts were issued.

[All episodes and dates](distinct-extreme-episodes.csv) · [All cohort and antecedent contrasts](extreme-anatomy-contrasts.csv) · [Event definitions and chronology](thresholds-5.csv).
