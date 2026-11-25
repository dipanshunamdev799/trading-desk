# V11 Market Concentration And Leadership

NIFTY Top 15 Equal Weight versus NIFTY 50 Equal Weight, NIFTY 50 versus NIFTY 500, sector return dispersion, sector rank changes, squared shares of absolute sector returns, and bank-relative moves are concentration or leadership proxies. They capture different features of a market that may be driven by a few large names. The compact seven-state design uses breadth, concentration, financial leadership, defensive/cyclical rotation, volatility, liquidity and global relative strength. Compare levels, five-day changes, persistent states, and the no-financial feature ablation.

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| L_EQ_CONC | 0.285244 | 0.165938 | 0.243824 | 0.012654 | 0.009981 | 0.011726 |
| L_CONC | 0.285406 | 0.166672 | 0.244185 | 0.012715 | 0.010098 | 0.011806 |
| B_ROT_EQ | 0.294145 | 0.162215 | 0.248343 | 0.013020 | 0.009939 | 0.011951 |
| B_ROT | 0.296554 | 0.165528 | 0.251066 | 0.013094 | 0.010118 | 0.012061 |
| B_FIN_INTERACT | 0.303538 | 0.163087 | 0.254778 | 0.013655 | 0.009808 | 0.012319 |
| L_BASIC | 0.282580 | 0.239552 | 0.267642 | 0.011712 | 0.011875 | 0.011769 |
| L_NO_FIN | 0.281866 | 0.241374 | 0.267808 | 0.011685 | 0.011834 | 0.011737 |
| L_CHANGE | 0.265361 | 0.272509 | 0.267843 | 0.011332 | 0.012627 | 0.011782 |
| L_PERSIST | 0.255352 | 0.320648 | 0.278021 | 0.010610 | 0.014330 | 0.011902 |

Daily dated memberships and weights needed for actual constituent contribution remained unavailable. The index spread does not directly measure advancing stocks. The exact duplicate/affine alias check operates on the strong rotation and breadth representation across both horizons. [NSE constituent-data description](https://www.niftyindices.com/offerings/data-subscription) · [Conditional leadership slices](breadth-mechanism-slices.csv) · [Concentration matched results](incremental-comparisons.csv).
