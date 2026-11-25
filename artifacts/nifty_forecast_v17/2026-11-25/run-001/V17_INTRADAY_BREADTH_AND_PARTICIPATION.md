# NIFTY V17 — Intraday breadth and participation

Participation tests use **3,200 decision snapshots from 400 market days**. The eight clocks run from 09:25 to 15:00 IST. At each clock, the latest observed five-minute bar is eligible at its end plus five minutes. Actual stock-count advance, percent above the open, and percent outperforming synchronized NIFTY come from observed traded stock prices. Same-sector deviations use each sleeve’s contemporaneous stock median. Equal-weight average return, median, dispersion, tail concentration, banking breadth, acceleration and observed stock synchronization enter the comparisons. Financial leadership is a sleeve-relative return. Above-VWAP participation uses the traded-instrument candle proxy described in the liquidity report. Open surprise × breadth and open surprise × financial leadership are frozen interactions. To control for deterioration of support later in the day, every reported gain uses the same model/parent dates at a single clock. The effects below are exploratory and sorted within the reported track. The full file preserves unfavorable results and timing sensitivities.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10:20 | regular_residual | official_EW_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.247757 | 0.247850 | 0.000093 | -0.005818 | 0.006003 |
| 09:25 | remaining_range | stock_direct | native_control | crps | 257 | 257 | 0.002199 | 0.002218 | 0.000019 | -0.000027 | 0.000065 |
| 12:30 | remaining_range | stock_direct | native_control | crps | 257 | 257 | 0.001519 | 0.001535 | 0.000016 | -8.69e-06 | 0.000041 |
| 09:25 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000959 | 0.000974 | 0.000015 | 6.03e-07 | 0.000029 |
| 12:30 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000705 | 0.000716 | 0.000011 | -2.07e-06 | 0.000024 |
| 09:25 | remaining_vol | joint_stock_native | native_control | crps | 257 | 257 | 0.000964 | 0.000974 | 0.000010 | -0.000018 | 0.000038 |
| 10:20 | remaining_vol | joint_stock_native | native_control | crps | 257 | 257 | 0.000865 | 0.000874 | 9.29e-06 | -7.16e-06 | 0.000026 |
| 10:20 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000865 | 0.000874 | 8.94e-06 | -9.19e-07 | 0.000019 |
| 10:20 | remaining_range | stock_direct | native_control | crps | 257 | 257 | 0.002010 | 0.002017 | 7.01e-06 | -0.000027 | 0.000041 |
| 10:20 | remaining_range | joint_stock_native | native_control | crps | 257 | 257 | 0.002011 | 0.002017 | 6.85e-06 | -0.000055 | 0.000069 |
| 14:00 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000609 | 0.000612 | 3.17e-06 | -4.60e-06 | 0.000011 |
| 09:25 | r30 | official_EW_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001255 | 0.001256 | 1.16e-06 | -0.000027 | 0.000029 |
| 14:00 | remaining_range | stock_direct | native_control | crps | 257 | 257 | 0.001131 | 0.001131 | 1.95e-07 | -0.000020 | 0.000020 |
| 14:00 | r30 | financial_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000846 | 0.000844 | -2.13e-06 | -0.000017 | 0.000013 |
| 09:25 | regular_residual | stock_direct | native_control | crps | 257 | 257 | 0.003487 | 0.003484 | -2.15e-06 | -0.000041 | 0.000037 |
| 09:25 | r30 | financial_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001259 | 0.001256 | -2.73e-06 | -0.000017 | 0.000012 |
| 10:20 | r30 | financial_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000817 | 0.000813 | -3.50e-06 | -0.000013 | 6.49e-06 |
| 12:30 | regular_residual | official_EW_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002292 | 0.002288 | -3.88e-06 | -0.000037 | 0.000029 |
| 12:30 | r30 | official_EW_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000832 | 0.000828 | -4.10e-06 | -0.000013 | 4.99e-06 |
| 09:25 | remaining_range | joint_stock_native | native_control | crps | 257 | 257 | 0.002222 | 0.002218 | -4.16e-06 | -0.000095 | 0.000087 |
| 10:20 | r30 | stock_direct | native_control | crps | 257 | 257 | 0.000808 | 0.000803 | -4.48e-06 | -0.000017 | 8.16e-06 |
| 10:20 | r30 | stock_neutralized | frozen_parent_residual_history | crps | 257 | 257 | 0.000818 | 0.000813 | -4.85e-06 | -0.000012 | 2.59e-06 |
| 12:30 | r30 | financial_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000833 | 0.000828 | -4.93e-06 | -0.000011 | 9.70e-07 |
| 09:25 | r30 | stock_neutralized | frozen_parent_residual_history | crps | 257 | 257 | 0.001261 | 0.001256 | -5.13e-06 | -0.000017 | 6.78e-06 |
| 14:00 | regular_residual | official_EW_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001728 | 0.001722 | -5.25e-06 | -0.000037 | 0.000026 |
| 10:20 | regular_residual | official_EW_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002927 | 0.002921 | -5.39e-06 | -0.000054 | 0.000043 |
| 14:00 | r30 | stock_direct | native_control | crps | 257 | 257 | 0.000843 | 0.000838 | -5.68e-06 | -0.000017 | 5.85e-06 |
| 10:20 | r30 | stock_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000819 | 0.000813 | -5.96e-06 | -0.000014 | 1.73e-06 |
| 14:00 | r30 | stock_neutralized | frozen_parent_residual_history | crps | 257 | 257 | 0.000851 | 0.000844 | -6.75e-06 | -0.000022 | 8.53e-06 |
| 09:25 | r30 | stock_direct | native_control | crps | 257 | 257 | 0.001253 | 0.001246 | -7.29e-06 | -0.000020 | 5.69e-06 |
| 12:30 | r30 | stock_neutralized | frozen_parent_residual_history | crps | 257 | 257 | 0.000835 | 0.000828 | -7.34e-06 | -0.000013 | -1.42e-06 |
| 14:00 | regular_residual | stock_neutralized | frozen_parent_residual_history | crps | 257 | 257 | 0.001730 | 0.001722 | -8.18e-06 | -0.000027 | 0.000010 |
| 12:30 | remaining_vol | stock_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000731 | 0.000723 | -8.20e-06 | -0.000054 | 0.000038 |
| 10:20 | r30 | official_EW_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000821 | 0.000813 | -8.20e-06 | -0.000017 | 9.53e-07 |

[Breadth feature values](intraday-feature-panel.csv.gz) · [Separate future return and risk targets](intraday-target-panel.csv.gz) · [All matched tests and alternatives](postopen-matched-evidence.csv) · [Volume methodology](V17_VOLUME_LIQUIDITY_AND_ORDER_FLOW.md)
