# V10 Structured Transfer Learning

The walk-forward transfer panel contains **29 instruments** and **11,687 instrument-date rows** before target-specific masks. It combines Indian broad-market and sector indices, selected liquid equities directly observed in the vendor history, ETFs, the Nasdaq Composite, and unrelated US rate and volatility controls. The foreign equity transfer test covered one index with a frozen publication mapping. Current instrument availability can introduce survivorship in the named equities. Cash-index liquidity often lacks a usable volume measure. The bulk of panel input diversity does not increase the number of distinct NIFTY market outcomes.

Comparable feature columns use trailing instrument-volatility normalization for momentum and residual relative strength, lagged rolling beta, cross-sector dispersion, own risk and available turnover. Ridge fitting weights each market date equally by dividing its mass across eligible instruments. All comparisons, including NIFTY-only, use a 21-session maturity cutoff for shared tasks and purged chronological inner calibration. Foreign rows receive an additional two eligible-date buffers and use the archived publication mapping. The test compares pooled coefficients, sector-only and ETF-only parameters, foreign-only augmentation, shrinkable asset-specific intercepts, two shared supervised panel factors, and heavily shrunk NIFTY deviations from a pooled model. The multitask designs learn a rank-two basis across 1, 3, 5, 10, 15 and 21 sessions plus five-session realized risk and bank leadership, or use just the shortest return tasks with those same risk/leadership tasks. Final output layers use the target horizon.

## Instrument inventory

| instrument | group |
| --- | --- |
| NIFTY | nifty |
| idx_Nifty_100 | broad |
| idx_Nifty_500 | broad |
| idx_NIFTY_MIDCAP_100 | broad |
| bank_nifty | sectors |
| nifty_it | sectors |
| nifty_auto | sectors |
| nifty_financial | sectors |
| nifty_fmcg | sectors |
| nifty_pharma | sectors |
| nifty_energy | sectors |
| nifty_metal | sectors |
| s_RELIANCE | equities |
| s_HDFCBANK | equities |
| s_INFY | equities |
| s_ICICIBANK | equities |
| s_TCS | equities |
| s_SUNPHARMA | equities |
| s_AXISBANK | equities |
| niftybees | etfs |
| bankbees | etfs |
| financial_etf | etfs |
| psu_etf | etfs |
| insurance_hdfc | equities |
| insurance_sbi | equities |
| private_bank | equities |
| NASDAQCOM | global |
| VIXCLS | unrelated |
| DGS10 | unrelated |

## Weekly transfer results and falsifications

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| X_SHIFT | 0.257102 | 0.295531 | 0.270443 | 0.010590 | 0.013767 | 0.011693 |
| X_FACTORS | 0.258998 | 0.292772 | 0.270723 | 0.010575 | 0.013552 | 0.011608 |
| X_RANDOM | 0.258603 | 0.294780 | 0.271162 | 0.010569 | 0.013668 | 0.011645 |
| X_POOL | 0.260818 | 0.292584 | 0.271846 | 0.010668 | 0.013743 | 0.011736 |
| X_ADJUST | 0.261004 | 0.292584 | 0.271967 | 0.010670 | 0.013743 | 0.011737 |
| X_ADAPT | 0.261246 | 0.294400 | 0.272756 | 0.010754 | 0.013732 | 0.011788 |
| X_MULTI_SHORT | 0.260322 | 0.298474 | 0.273567 | 0.010605 | 0.013688 | 0.011675 |
| X_ONLY | 0.260823 | 0.298846 | 0.274024 | 0.010730 | 0.013760 | 0.011782 |
| X_SECTORS | 0.263780 | 0.293476 | 0.274090 | 0.010690 | 0.013668 | 0.011724 |
| X_GLOBAL | 0.267847 | 0.286022 | 0.274156 | 0.010941 | 0.013569 | 0.011853 |
| X_ETFS | 0.264038 | 0.294262 | 0.274531 | 0.010691 | 0.013740 | 0.011750 |
| X_UNRELATED | 0.258005 | 0.307873 | 0.275318 | 0.010499 | 0.014069 | 0.011739 |
| X_MULTI | 0.262309 | 0.301721 | 0.275991 | 0.010650 | 0.013754 | 0.011728 |

## Monthly transfer results and falsifications

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| X_GLOBAL | 0.306656 | 0.395071 | 0.337622 | 0.029425 | 0.035435 | 0.031530 |
| X_FACTORS | 0.298015 | 0.471285 | 0.358699 | 0.028999 | 0.035963 | 0.031438 |
| X_ONLY | 0.299461 | 0.482538 | 0.363580 | 0.030590 | 0.036466 | 0.032648 |
| X_SECTORS | 0.299016 | 0.484257 | 0.363893 | 0.028812 | 0.036206 | 0.031401 |
| X_SHIFT | 0.290979 | 0.501959 | 0.364871 | 0.028744 | 0.037141 | 0.031685 |
| X_RANDOM | 0.299506 | 0.486258 | 0.364912 | 0.029153 | 0.036259 | 0.031641 |
| X_ADAPT | 0.300547 | 0.488334 | 0.366316 | 0.030205 | 0.036499 | 0.032409 |
| X_MULTI | 0.305125 | 0.479849 | 0.366318 | 0.029841 | 0.036288 | 0.032099 |
| X_UNRELATED | 0.294402 | 0.502909 | 0.367428 | 0.028274 | 0.037004 | 0.031332 |
| X_ETFS | 0.301160 | 0.491288 | 0.367749 | 0.029682 | 0.036678 | 0.032133 |
| X_MULTI_SHORT | 0.303856 | 0.489254 | 0.368788 | 0.029432 | 0.036374 | 0.031863 |
| X_POOL | 0.302234 | 0.493695 | 0.369290 | 0.029242 | 0.036542 | 0.031799 |
| X_ADJUST | 0.302816 | 0.493749 | 0.369686 | 0.029249 | 0.036537 | 0.031801 |

The weekly direction gain from strongly regularized transfer changed sign across cohorts and its distribution improvement was small. The random and shifted auxiliary tasks also achieve some numerical gains. Compare all of them with the same-complexity NIFTY-only model. Monthly transfer failed to establish meaningful improvement over neutral or historical references. Auxiliary labels are randomly permuted in blocks or shifted only within previously matured training data for negative controls. [Panel](transfer-panel.csv) · [Transfer fit membership and diagnostics](transfer-ledger.json).
