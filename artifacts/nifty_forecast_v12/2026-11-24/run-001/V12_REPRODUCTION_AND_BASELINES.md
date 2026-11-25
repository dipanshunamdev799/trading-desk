# V12 Reproduction And Baselines

V12 retains the previously inspected 2025–2026 chronology and freezes data at **17 November 2026**. It reproduced **10,122** reference forecasts using the original V11 walk-forward fits and V10/V11 mixture recipes, with maximum discrepancy **1.39e-17**. These include original phase zero and its alternative or staggered phase designs, oldest/recent/spread memory, strong later breadth, native/sparse and shape components, and the original structural mixtures. A separate exact V11 replay reproduced **1,874** official-breadth forecasts based on authentic V8 and V9 parent designs and fit dates. The earlier protected replay recovered **1612 V9** and **184 V8** forecasts, and the symmetric monthly source was also rebuilt over 217 origins.

## Reference weekly Brier and CRPS

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| O_NATIVE_PHASE0 | 0.237586 | 0.220712 | 0.231728 | 0.010359 | 0.012207 | 0.011001 |
| J11_BREADTH_ALL | 0.263631 | 0.184437 | 0.236138 | 0.011521 | 0.009905 | 0.010960 |
| J10_STRUCTURAL_BLEND | 0.262428 | 0.186826 | 0.236181 | 0.011451 | 0.010275 | 0.011043 |
| P_CLUSTER | 0.260773 | 0.190529 | 0.236386 | 0.012473 | 0.010463 | 0.011775 |
| J11_BREADTH_ALL_HIST | 0.255993 | 0.215152 | 0.241814 | 0.010796 | 0.010840 | 0.010811 |
| J10_HISTORY_SHRINK | 0.255692 | 0.217307 | 0.242366 | 0.010797 | 0.011071 | 0.010892 |
| J11_EXCLUDE_B_ROT | 0.266670 | 0.202329 | 0.244333 | 0.011137 | 0.010102 | 0.010777 |
| B_CHANGE | 0.294583 | 0.156795 | 0.246747 | 0.012942 | 0.009851 | 0.011869 |
| P_HIST | 0.259447 | 0.258296 | 0.259048 | 0.010878 | 0.012210 | 0.011340 |
| V8_R_RESIDUAL | — | 0.159504 | — | — | 0.009852 | — |
| V8_W_STRUCT_EMBARGO | — | 0.163355 | — | — | 0.009453 | — |
| V8_W_STRUCT_EMBARGO_EQ | — | 0.161638 | — | — | 0.009262 | — |

The symmetric 21-session reference has **0.250000 Brier** and **0.025420 CRPS**. On later weekly origins, 0.156795 Brier and 0.009262 CRPS are V11 records from different designs. The V8 protected values are 0.159504 and 0.009453. Re-searching historical parameters provides additional evidence about model robustness on the same exposed data. The market-price comparisons use matched dates and independently scored outcomes.

[Exact replay ledger](exact-replay.json) · [Each replayed score](exact-replay.csv) · [Breadth replay](legacy-breadth-replay.json) · [Frozen artifact hashes](protected-verification.json).
