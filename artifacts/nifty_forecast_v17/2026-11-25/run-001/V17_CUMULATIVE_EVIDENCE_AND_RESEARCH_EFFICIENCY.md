# NIFTY V17 — Cumulative evidence and research efficiency

V17 registered six research mechanisms before the new feature scores, with two original horizons, eight intraday decisions, two dedicated joint-risk clocks, fixed shrinkage, no expansion to additional years, and equal-eligible-date tests. It reused the V14 risk laws, V15 session timing and GJR state, and V16 opening, first-passage and date-block machinery. The result archive includes **288,013** post-open forecasts. The post-open chronologies come from at most 400 market dates. Returns and risk at different clocks overlap within each day. Many five- and 21-session labels overlap across dates. Date and disjoint support are included in the score files.

| Evidence class | What carries forward |
| --- | --- |
| Reproduced historical association | Eligible GIFT price changes reveal the opening gap. Near-open timestamps and contract uncertainty remain material. |
| Demonstrated methodology | Forecast timestamp and target start differ. Residuals from chronological forecasts and day-one first-passage conditioning can be audited exactly. |
| Cohort-dependent | Shorter, date-matched risk corrections can show a gain with a weak directional signal on the same sample. Check stronger same-clock and falsification parents. |
| Failed model family on this record | Many stock and surprise residual corrections, original monthly structural variants and unconditional GIFT extrapolation beyond opening. Preserve the benchmark and losing cases. |
| Unresolved mechanism | Stock-level lead and transmission can reflect shared factor exposure. ETF tracking behavior, actual quote pressure, and genuine stock-specific information require instrument-level evidence. |
| Distinct new hypothesis | Independent company dissemination times and matched ETF/underlying leg attribution are observable inputs. They can be prospectively registered at one clock. |

There are 3 distinct return-target rows with a positive adjusted 21-session-block interval and positive early and later estimates in the selected Brier/CRPS/QLIKE grid. Some rows share the same market movements. The study has no independent final model-selection holdout across the V1–V17 work.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | remaining_3 | gap_size_only | price_only | brier | 255 | 86 | 0.252572 | 0.256417 | 0.003845 | 0.000334 | 0.007355 |
| 09:25 | remaining_3 | gap_size_only | price_only | crps | 255 | 86 | 0.007846 | 0.007919 | 0.000072 | 0.000015 | 0.000129 |
| 09:25 | remaining_5 | gap_size_only | price_only | crps | 253 | 51 | 0.010568 | 0.010616 | 0.000048 | 2.44e-06 | 0.000094 |
| 09:35 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000917 | 0.000932 | 0.000015 | 1.40e-06 | 0.000029 |
| 09:25 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000959 | 0.000974 | 0.000015 | 6.03e-07 | 0.000029 |
| 11:30 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000785 | 0.000796 | 0.000011 | 2.16e-06 | 0.000019 |
| 09:25 | remaining_vol | stock_direct | native_control | qlike | 257 | 257 | 0.214034 | 0.218998 | 0.004964 | 0.000068 | 0.009860 |

[Research registration and budget](registration.json) · [Falsification](V17_VALIDATION_AND_FALSIFICATION.md) · [Complete cross-source evidence](multiscale-information-matrix.csv) · [Protected chain](predecessor-protection.json)
