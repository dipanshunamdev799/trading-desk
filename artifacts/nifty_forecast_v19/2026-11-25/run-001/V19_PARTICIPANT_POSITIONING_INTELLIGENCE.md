# V19 Participant Positioning Intelligence

The report uses the exchange labels Client, DII, FII and Pro across index futures, stock futures, index calls, index puts, stock calls and stock puts. Participant files combine the exchange's index instruments. NIFTY-specific ordinary futures contracts have a separate source. Each family preserves long, short, net, gross, long-to-short ratio and gross-normalized exposure, with one-, five- and 21-session changes, an acceleration proxy and five-session persistence. The primary linear factor drops the mechanically dependent Client net. Side totals and observed four-category totals are both audited. There were 1 reported instrument-day total side mismatch and 378 report-level discrepancies between detailed category sums and published totals. The largest category-sum difference was 1 contract. The model uses the observed category denominator and suppresses net ratios with material imbalance.

The option features are separately signed call and put counts. Strike, maturity and Greeks by participant are unavailable in these reports. Concentration is a Herfindahl index of gross contract shares. Disagreement is cross-category dispersion. Treat the FII positions as derivatives observations and use the ordinary NIFTY OI, price, volatility and breadth controls for comparison. Open contracts and traded contracts measure different things.

| horizon | cutoff | model | n | active | brier | crps |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | changes_only | 265 | 265 | 0.240527 | 0.010747 |
| 5 | preauction_0855 | clock_structural | 265 | 265 | 0.238274 | 0.010658 |
| 5 | preauction_0855 | innovation_augmentation | 265 | 265 | 0.246402 | 0.010796 |
| 5 | preauction_0855 | levels_only | 265 | 265 | 0.242415 | 0.010692 |
| 5 | preauction_0855 | participant | 265 | 265 | 0.239255 | 0.010619 |
| 5 | preauction_0855 | participant_block_permuted | 265 | 265 | 0.241430 | 0.010661 |
| 5 | preauction_0855 | participant_delay1 | 265 | 265 | 0.244571 | 0.010754 |
| 5 | preauction_0855 | participant_delay5 | 265 | 265 | 0.245958 | 0.010871 |
| 5 | preauction_0855 | positions_beyond_oi | 265 | 221 | 0.246262 | 0.010718 |
| 5 | previous_1700 | changes_only | 265 | 265 | 0.234967 | 0.010733 |
| 5 | previous_1700 | clock_structural | 265 | 265 | 0.238605 | 0.010721 |
| 5 | previous_1700 | innovation_augmentation | 265 | 265 | 0.243070 | 0.010839 |
| 5 | previous_1700 | levels_only | 265 | 265 | 0.246754 | 0.010886 |
| 5 | previous_1700 | participant | 265 | 265 | 0.244187 | 0.010812 |
| 5 | previous_1700 | participant_block_permuted | 265 | 265 | 0.243801 | 0.010768 |
| 5 | previous_1700 | participant_delay1 | 265 | 265 | 0.247419 | 0.010866 |
| 5 | previous_1700 | participant_delay5 | 265 | 265 | 0.250527 | 0.010924 |
| 5 | previous_1700 | positions_beyond_oi | 265 | 220 | 0.249269 | 0.010886 |
| 21 | preauction_0855 | changes_only | 217 | 217 | 0.307441 | 0.028767 |
| 21 | preauction_0855 | clock_structural | 217 | 217 | 0.302805 | 0.028519 |
| 21 | preauction_0855 | innovation_augmentation | 217 | 217 | 0.317197 | 0.029417 |
| 21 | preauction_0855 | levels_only | 217 | 217 | 0.297679 | 0.029791 |
| 21 | preauction_0855 | participant | 217 | 217 | 0.285350 | 0.027800 |
| 21 | preauction_0855 | participant_block_permuted | 217 | 217 | 0.351503 | 0.031649 |
| 21 | preauction_0855 | participant_delay1 | 217 | 217 | 0.290813 | 0.027905 |
| 21 | preauction_0855 | participant_delay5 | 217 | 217 | 0.303937 | 0.028469 |
| 21 | preauction_0855 | positions_beyond_oi | 217 | 157 | 0.307493 | 0.029786 |
| 21 | previous_1700 | changes_only | 217 | 217 | 0.310045 | 0.028681 |
| 21 | previous_1700 | clock_structural | 217 | 217 | 0.300452 | 0.028321 |
| 21 | previous_1700 | innovation_augmentation | 217 | 217 | 0.312472 | 0.029196 |
| 21 | previous_1700 | levels_only | 217 | 217 | 0.298786 | 0.029663 |
| 21 | previous_1700 | participant | 217 | 217 | 0.289989 | 0.027816 |
| 21 | previous_1700 | participant_block_permuted | 217 | 217 | 0.354350 | 0.031618 |
| 21 | previous_1700 | participant_delay1 | 217 | 217 | 0.295718 | 0.027990 |
| 21 | previous_1700 | participant_delay5 | 217 | 217 | 0.304173 | 0.028577 |
| 21 | previous_1700 | positions_beyond_oi | 217 | 156 | 0.311230 | 0.029936 |

| horizon | cutoff | model | parent | n | disjoint | gain |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | changes_only | clock_structural | 265 | 53 | -0.000089 |
| 5 | preauction_0855 | innovation_augmentation | clock_structural | 265 | 53 | -0.000138 |
| 5 | preauction_0855 | levels_only | clock_structural | 265 | 53 | -0.000034 |
| 5 | preauction_0855 | participant | clock_structural | 265 | 53 | 0.000040 |
| 5 | preauction_0855 | positions_beyond_oi | clock_with_oi_volume | 220 | 45 | 0.000166 |
| 5 | previous_1700 | changes_only | clock_structural | 265 | 53 | -0.000011 |
| 5 | previous_1700 | innovation_augmentation | clock_structural | 265 | 53 | -0.000117 |
| 5 | previous_1700 | levels_only | clock_structural | 265 | 53 | -0.000164 |
| 5 | previous_1700 | participant | clock_structural | 265 | 53 | -0.000091 |
| 5 | previous_1700 | positions_beyond_oi | clock_with_oi_volume | 219 | 45 | 0.000060 |
| 21 | preauction_0855 | changes_only | clock_structural | 217 | 11 | -0.000248 |
| 21 | preauction_0855 | innovation_augmentation | clock_structural | 217 | 11 | -0.000898 |
| 21 | preauction_0855 | levels_only | clock_structural | 217 | 11 | -0.001271 |
| 21 | preauction_0855 | participant | clock_structural | 217 | 11 | 0.000719 |
| 21 | preauction_0855 | positions_beyond_oi | clock_with_oi_volume | 156 | 8 | 0.001323 |
| 21 | previous_1700 | changes_only | clock_structural | 217 | 11 | -0.000360 |
| 21 | previous_1700 | innovation_augmentation | clock_structural | 217 | 11 | -0.000875 |
| 21 | previous_1700 | levels_only | clock_structural | 217 | 11 | -0.001342 |
| 21 | previous_1700 | participant | clock_structural | 217 | 11 | 0.000504 |
| 21 | previous_1700 | positions_beyond_oi | clock_with_oi_volume | 155 | 8 | 0.001094 |

[participants.csv.gz](participants.csv.gz) · [positioning-daily-features.csv.gz](positioning-daily-features.csv.gz) · [model-leaderboards.csv](model-leaderboards.csv) · [matched-comparisons.csv](matched-comparisons.csv) · [mechanism-sensitivities.csv.gz](mechanism-sensitivities.csv.gz) · [sector-transfer-leaderboard.csv](sector-transfer-leaderboard.csv) · [NSE derivatives file specification](https://archives.nseindia.com/content/press/EOD_FAO.pdf)
