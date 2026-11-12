# Multi-session NIFTY directional study

2442 daily observations (2017-01-02 to 2026-11-08); 200 sessions reserved for warmup. 207 configurations across four families; 36 development/validation eligible; 4 frozen finalists.

Signals use completed daily bars; entry is next observed session open and exit is the close after 1, 3 or 5 sessions. Special sessions are included as published. No compounding, position sizing, stops or premium simulation. Index basis points (bps), not option returns; 5/10 bps friction is illustrative, not actual trading fees. Trades spanning chronological partitions are excluded.

|Partition|First|Last|Sessions|
|---|---|---|---:|
|development|2017-10-24|2023-03-24|1345|
|validation|2023-03-27|2025-01-15|448|
|holdout|2025-01-16|2026-11-08|449|

One winner per family selected solely by development/validation net5 means, requiring at least 50/20 trades and positive means in both. Historical holdout was not used to choose rules; it is not a prospective test and overlaps other inspected project history. Full grid publication is not permission to reselect using holdout.

|Family|Frozen rule|Hold sessions|Final N|Gross bps|Net5 bps|Net10 bps|Net5 95% block interval|Matched-long excess bps|
|---|---|---:|---:|---:|---:|---:|---|---:|
|ema_trend|10_30_gap0 / long_only|5|50|-5.66|-10.66|-15.66|-53.09, 33.18|0.00|
|donchian|lookback10_buffer0.25 / long_only|5|18|60.76|55.76|50.76|-35.25, 118.52|0.00|
|momentum|lookback20_atr0 / ema_aligned|5|75|-26.16|-31.16|-36.16|-69.91, 8.57|-45.65|
|rsi_reversion|rsi30 / none|1|37|5.15|0.15|-4.85|-12.19, 22.04|5.57|

Matched-long excess compares every selected entry/exit with buying the index at those identical times. Long-only rules necessarily have zero matched-long excess; this is a control for direction choice, not a complete test of entry timing skill.

|Baseline|Hold sessions|Final N|Gross bps|Net5 bps|Net5 95% interval|
|---|---:|---:|---:|---:|---|
|always_long|1|448|-0.38|-5.38|-10.87, -0.82|
|always_long|3|149|7.28|2.28|-22.41, 22.20|
|always_long|5|89|0.96|-4.04|-41.11, 32.00|
|always_short|1|448|0.38|-4.62|-9.18, 0.87|
|always_short|3|149|-7.28|-12.28|-32.20, 12.41|
|always_short|5|89|-0.96|-5.96|-42.00, 31.11|

Descriptive gate passes: 0 (final N>=30, net10>0, lower net5 interval>0). This is not a multiple-testing-adjusted result or a trading approval. 5 feature-prefix tests and 5425 exact timestamp/price/duration/nonoverlap/PnL assertions passed.

Interval estimates use 3,000 ten-session moving-block resamples by entry date. Weekly/monthly option expiries still require exact premiums, contemporaneous contract choice, IV, spreads and dated fees. No return or edge is established for options by this file.