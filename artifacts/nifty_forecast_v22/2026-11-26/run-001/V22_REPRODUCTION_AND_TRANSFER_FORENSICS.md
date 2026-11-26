# V22 Reproduction and transfer forensics

Recomputed Brier, log loss, CRPS, mean and sign probability from 3,591 original weighted laws.
Verified the SHA-256 of 234 V21 artifacts and 15 V21 source files before reuse.
The replay uses the exact original weekly and monthly endpoints. Native 09:10 forecasts and rebuilt 08:55 forecasts retain their own clocks.

## Native reference scores

| horizon | model | n | brier | crps |
| --- | --- | --- | --- | --- |
| 5 | anchor_asymmetry | 265 | 0.222129 | 0.010167 |
| 5 | exact_v14 | 265 | 0.228529 | 0.010457 |
| 5 | omit_latest_21_training_origins | 265 | 0.221693 | 0.010274 |
| 5 | price_reaction | 265 | 0.223384 | 0.010258 |
| 5 | v18_corporate_native | 265 | 0.223481 | 0.010318 |
| 21 | anchor_aggregate_position | 217 | 0.223819 | 0.023184 |
| 21 | eight_calendar_day_embargo | 217 | 0.228088 | 0.024003 |
| 21 | exact_v14 | 217 | 0.245042 | 0.024989 |
| 21 | smooth5 | 217 | 0.228602 | 0.023786 |
| 21 | v19_position_native | 217 | 0.228199 | 0.024010 |

The V21 aggregate monthly correction improved the early cohort and lost ground in the later cohort.
The table measures V20 smooth5 loss minus V21 aggregate-position loss, so positive gains favor V21.

| cohort | brier | crps | dates |
| --- | --- | --- | --- |
| early | 0.019699 | 0.001281 | 141 |
| later | -0.022891 | -0.000658 | 76 |

## Dated constituent reconstruction

V21 lagged monthly constituent weights retained very close arithmetic tracking. These are realized reconstruction errors, in basis points.

| horizon | mae bp |
| --- | --- |
| 1 | 0.424416 |
| 5 | 1.383281 |
| 21 | 4.323498 |

## Transfer forensics

V5 treated timed global markets as NIFTY predictors. Its 176 inputs included 52 aligned global features and used a timezone guard.
The dated V5 laws and losses were rescored directly. V9 used nine sector residuals with an earlier 63-session beta and a
150-name currently selected proxy universe. The rotation-plus-panel result scored 0.304341 Brier in 173 early cases and
0.233628 in 92 later cases. Its target and universe limited portability.

V10's weekly pooled research scored 0.271846 Brier versus 0.274024 for its NIFTY-only lane. Its shifted control scored
0.270443. V18's company-level pooled event MAE was 0.012112 versus 0.011992 for the price-only reference. V21's stock
pooling reconstructed realized index contributions but added little forecast information after aggregation. Its combined monthly
market-relative pooled CRPS was 0.054919 versus 0.054781 for randomized auxiliary labels. V22 changes the unit of
auxiliary supervision to a comparable local-market task, holds out entire countries or regions, and maps observed OHLC
paths only after their own targets have matured.

[v5-cross-market-recomputed.csv](v5-cross-market-recomputed.csv) · [v9-cross-sectional-research-archive.csv](v9-cross-sectional-research-archive.csv) · [v10-transfer-replay.csv](v10-transfer-replay.csv) · [v18-event-transfer-replay.csv](v18-event-transfer-replay.csv) · [v21-transfer-recomputed.csv](v21-transfer-recomputed.csv) · [v21-monthly-cohort-reproduction.csv](v21-monthly-cohort-reproduction.csv) · [v21-protected-tracking.csv](v21-protected-tracking.csv) · [predecessor-receipt.json](predecessor-receipt.json) · [protected-india-return-laws.npz](protected-india-return-laws.npz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
