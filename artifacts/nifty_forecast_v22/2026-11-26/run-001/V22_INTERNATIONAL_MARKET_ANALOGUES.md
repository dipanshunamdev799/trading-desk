# V22 International market analogues

The retrieval atlas contains 6,748 weighted path laws and 307,992 mapped empirical OHLC scenarios.
Market-state matching uses earlier normalized trend, drawdown, level and change of volatility, efficiency, relative strength,
breadth and sector proxies, cross-market dispersion, synchronization, VIX and global state. Nearest, covariance-shrunken
Mahalanobis, regularized magnitude-metric, four-factor, trailing path, and sector-weighted distance are distinct arms.
Their location and scaling statistics use eligible source states only. Random retrieval and a volatility-only India match
are explicit controls.

Source paths must have entirely matured before the target Indian issue. A mapped path divides every relative log OHLC
mark by its own earlier daily RMS volatility and multiplies by India's earlier volatility. The method retains each entire
local path, its internal OHLC ordering and terminal sign. The diversity rule takes at most two windows per global calendar
week, at most one per country within that week, and at most 24 of 48 from a foreign region. Equal week mass limits repetition.
The uncapped control retains closest neighbours without these limits. We report the realized region weight with Kish effective mass.

## Analogue comparison across the original NIFTY dates

| horizon | model | n | terminal crps | rv mae | range crps | drawdown crps | expand brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | domestic_history | 265 | 0.011412 | 0.045367 | 0.007242 | 0.006706 | 0.213058 |
| 5 | foreign_nearest | 265 | 0.011866 | 0.042659 | 0.006733 | 0.006690 | 0.202073 |
| 5 | foreign_outside_asia | 265 | 0.012068 | 0.042632 | 0.006674 | 0.006827 | 0.201168 |
| 5 | foreign_stress | 265 | 0.033148 | 0.185967 | 0.038096 | 0.016231 | 0.698113 |
| 5 | foreign_uncapped | 265 | 0.011764 | 0.040609 | 0.006568 | 0.006603 | 0.204222 |
| 5 | india_nearest | 265 | 0.011914 | 0.044919 | 0.007284 | 0.007101 | 0.215144 |
| 5 | india_volatility | 265 | 0.011428 | 0.047839 | 0.007404 | 0.006701 | 0.230526 |
| 5 | mixed_factor | 265 | 0.011978 | 0.043298 | 0.006891 | 0.006707 | 0.195254 |
| 5 | mixed_mahalanobis | 265 | 0.011721 | 0.043299 | 0.006723 | 0.006677 | 0.210705 |
| 5 | mixed_metric | 265 | 0.011706 | 0.042451 | 0.006671 | 0.006598 | 0.200016 |
| 5 | mixed_nearest | 265 | 0.011688 | 0.041991 | 0.006693 | 0.006574 | 0.197221 |
| 5 | mixed_path | 265 | 0.011726 | 0.041269 | 0.006580 | 0.006616 | 0.193085 |
| 5 | mixed_sector | 265 | 0.011718 | 0.042644 | 0.006830 | 0.006649 | 0.203932 |
| 5 | random_eligible | 265 | 0.011678 | 0.045822 | 0.007277 | 0.006793 | 0.215240 |
| 21 | domestic_history | 217 | 0.027394 | 0.052102 | 0.019781 | 0.017139 | 0.275110 |
| 21 | foreign_nearest | 217 | 0.029868 | 0.046107 | 0.017449 | 0.016461 | 0.252312 |
| 21 | foreign_outside_asia | 217 | 0.029788 | 0.046967 | 0.018065 | 0.016641 | 0.277281 |
| 21 | foreign_stress | 217 | 0.088483 | 0.119976 | 0.096410 | 0.026639 | 0.533981 |
| 21 | foreign_uncapped | 217 | 0.029876 | 0.044960 | 0.017967 | 0.016551 | 0.247851 |
| 21 | india_nearest | 217 | 0.027332 | 0.050719 | 0.019206 | 0.017066 | 0.272351 |
| 21 | india_volatility | 217 | 0.027736 | 0.050962 | 0.019438 | 0.017036 | 0.272889 |
| 21 | mixed_factor | 217 | 0.030018 | 0.046529 | 0.017914 | 0.016625 | 0.243456 |
| 21 | mixed_mahalanobis | 217 | 0.028854 | 0.046071 | 0.017192 | 0.015843 | 0.248053 |
| 21 | mixed_metric | 217 | 0.029352 | 0.044525 | 0.017151 | 0.015962 | 0.239329 |
| 21 | mixed_nearest | 217 | 0.029257 | 0.045303 | 0.017300 | 0.016021 | 0.243286 |
| 21 | mixed_path | 217 | 0.029791 | 0.046222 | 0.018321 | 0.016208 | 0.225493 |
| 21 | mixed_sector | 217 | 0.029115 | 0.046305 | 0.017443 | 0.016085 | 0.250116 |
| 21 | random_eligible | 217 | 0.029501 | 0.052307 | 0.019693 | 0.016650 | 0.267690 |

The strongest direct native distribution benchmarks below cover the same original outcomes. The standalone analogue laws use 08:55 information.

| horizon | model | n | brier | crps |
| --- | --- | --- | --- | --- |
| 5 | anchor_asymmetry | 265 | 0.222129 | 0.010167 |
| 21 | anchor_aggregate_position | 217 | 0.223819 | 0.023184 |

## Diversity and effective number of analogues

| horizon | model | mean ess | mean origin dates | mean episodes | mean regions | mean largest episode | max single episode | mean largest region |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | domestic_history | 46.211321 | 46.211321 | 46.211321 | 1.000000 | 0.021685 | 0.026316 | 1.000000 |
| 5 | foreign_nearest | 43.702004 | 38.690566 | 28.079245 | 3.000000 | 0.035731 | 0.040000 | 0.458072 |
| 5 | foreign_outside_asia | 43.184473 | 39.158491 | 29.260377 | 2.000000 | 0.034300 | 0.040000 | 0.539846 |
| 5 | foreign_stress | 21.405817 | 20.894340 | 16.890566 | 2.939623 | 0.059411 | 0.062500 | 0.697367 |
| 5 | foreign_uncapped | 47.716486 | 30.483019 | 17.158491 | 3.000000 | 0.197176 | 0.577330 | 0.516930 |
| 5 | india_nearest | 46.211321 | 46.211321 | 46.211321 | 1.000000 | 0.021685 | 0.026316 | 1.000000 |
| 5 | india_volatility | 46.211321 | 46.211321 | 46.211321 | 1.000000 | 0.021685 | 0.026316 | 1.000000 |
| 5 | mixed_factor | 43.571760 | 39.358491 | 28.237736 | 3.943396 | 0.035537 | 0.040000 | 0.454099 |
| 5 | mixed_mahalanobis | 43.680897 | 38.290566 | 28.086792 | 3.849057 | 0.035706 | 0.041667 | 0.444844 |
| 5 | mixed_metric | 43.623241 | 38.871698 | 28.226415 | 3.932075 | 0.035545 | 0.040000 | 0.432725 |
| 5 | mixed_nearest | 43.723285 | 38.883019 | 28.083019 | 3.913208 | 0.035736 | 0.040000 | 0.437329 |
| 5 | mixed_path | 43.122648 | 42.049057 | 29.392453 | 3.932075 | 0.034120 | 0.040000 | 0.458908 |
| 5 | mixed_sector | 43.791570 | 37.962264 | 27.913208 | 3.867925 | 0.035939 | 0.040000 | 0.443763 |
| 5 | random_eligible | 42.804487 | 44.920755 | 32.830189 | 3.905660 | 0.030546 | 0.035714 | 0.452091 |
| 21 | domestic_history | 43.511521 | 43.511521 | 43.511521 | 1.000000 | 0.022986 | 0.024390 | 1.000000 |
| 21 | foreign_nearest | 43.863965 | 38.529954 | 27.668203 | 3.000000 | 0.036229 | 0.040000 | 0.459640 |
| 21 | foreign_outside_asia | 43.237942 | 39.000000 | 29.073733 | 2.000000 | 0.034519 | 0.040000 | 0.540838 |
| 21 | foreign_stress | 21.576649 | 21.373272 | 17.520737 | 2.000000 | 0.057537 | 0.071429 | 0.849071 |
| 21 | foreign_uncapped | 47.704845 | 30.414747 | 16.612903 | 3.000000 | 0.195309 | 0.542866 | 0.537064 |
| 21 | india_nearest | 43.511521 | 43.511521 | 43.511521 | 1.000000 | 0.022986 | 0.024390 | 1.000000 |
| 21 | india_volatility | 43.511521 | 43.511521 | 43.511521 | 1.000000 | 0.022986 | 0.024390 | 1.000000 |
| 21 | mixed_factor | 43.662589 | 39.345622 | 27.898618 | 3.921659 | 0.035932 | 0.040000 | 0.454977 |
| 21 | mixed_mahalanobis | 43.918835 | 38.170507 | 27.594470 | 3.866359 | 0.036324 | 0.040000 | 0.442988 |
| 21 | mixed_metric | 43.896994 | 38.612903 | 27.594470 | 3.921659 | 0.036321 | 0.040000 | 0.436633 |
| 21 | mixed_nearest | 43.893252 | 38.751152 | 27.635945 | 3.917051 | 0.036274 | 0.040000 | 0.438015 |
| 21 | mixed_path | 43.212212 | 42.059908 | 29.023041 | 3.963134 | 0.034545 | 0.040000 | 0.455446 |
| 21 | mixed_sector | 43.963443 | 37.930876 | 27.543779 | 3.898618 | 0.036400 | 0.040000 | 0.441785 |
| 21 | random_eligible | 42.774028 | 44.870968 | 31.926267 | 3.917051 | 0.031398 | 0.035714 | 0.456894 |

For the 2026-10-16 21-session mixed metric forecast, the most heavily weighted retrieved histories are shown below. Eligibility is certified through the underlying UTC maturity field.

| market | region | origin | endpoint | episode | weight | distance | mapped terminal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| australia | Asia Pacific | 2026-05-08 | 2026-06-05 | 2026-05-04/2026-05-10 | 0.037037 | 1.172978 | -0.049718 |
| us | North America | 2025-12-01 | 2025-12-30 | 2025-12-01/2025-12-07 | 0.037037 | 1.104684 | 0.007119 |
| canada | North America | 2026-05-26 | 2026-06-23 | 2026-05-25/2026-05-31 | 0.037037 | 1.436324 | 0.007088 |
| netherlands | Europe | 2026-07-17 | 2026-08-14 | 2026-07-13/2026-07-19 | 0.037037 | 1.216925 | 0.021398 |
| us | North America | 2026-04-09 | 2026-05-07 | 2026-04-06/2026-04-12 | 0.037037 | 0.996915 | 0.063956 |
| italy | Europe | 2026-09-14 | 2026-10-12 | 2026-09-14/2026-09-20 | 0.037037 | 0.864950 | -0.069170 |
| india | South Asia | 2026-08-03 | 2026-08-31 | 2026-08-03/2026-08-09 | 0.020927 | 0.577023 | -0.016092 |
| india | South Asia | 2026-02-09 | 2026-03-10 | 2026-02-09/2026-02-15 | 0.020757 | 0.569496 | -0.057862 |

The foreign stress arm retrieves extreme complete eligible histories. Its mass provides historical stress illustrations and
is intentionally excluded from ordinary forecasting conclusions. The ranked pure-return evidence includes the random and
domestic-history controls, so any claimed analogue advantage must exceed a similar eligible retrieval procedure.

[analogue-law-atlas.csv](analogue-law-atlas.csv) · [analogue-law-members.csv.gz](analogue-law-members.csv.gz) · [analogue-observed-path-laws.npz](analogue-observed-path-laws.npz) · [analogue-risk-cases.csv.gz](analogue-risk-cases.csv.gz) · [india-forecast-cases.csv.gz](india-forecast-cases.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
