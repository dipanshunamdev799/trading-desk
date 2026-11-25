# V11 Persistent Market Relationships

The long fit is expanding, the unconstrained recent fit uses 85 and the 65/35 estimator combines their locations. The temporary residual fit uses a penalty of 650 and half weight on its recent adjustment. A more flexible hierarchical variation uses a 325 penalty and a centered recent component. The historical-block architecture pools three past episode fits and half the long history, with a separate variant including official breadth persistence. The early and late results show the price of changing the balance between a long relationship and a short adjustment.

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| B_ROT | 0.296554 | 0.165528 | 0.251066 | 0.013094 | 0.010118 | 0.012061 |
| P_BLOCK_EXPERTS | 0.290322 | 0.179797 | 0.251951 | 0.012312 | 0.010462 | 0.011670 |
| P_RECENT_SHRINK | 0.296280 | 0.178253 | 0.255305 | 0.013337 | 0.010481 | 0.012345 |
| P_HIER | 0.298976 | 0.176158 | 0.256337 | 0.013416 | 0.010385 | 0.012364 |
| P_BREADTH_PERSIST | 0.300485 | 0.175285 | 0.257019 | 0.013337 | 0.010259 | 0.012268 |
| P_LONG_SHORT | 0.295498 | 0.214722 | 0.267455 | 0.013241 | 0.011485 | 0.012631 |
| P_RECENT_FREE | 0.291540 | 0.358692 | 0.314853 | 0.014007 | 0.015234 | 0.014433 |
| P_SHORT | 0.291540 | 0.358692 | 0.314853 | 0.014007 | 0.015234 | 0.014433 |

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| B_ROT | 0.348614 | 0.304701 | 0.333234 | 0.032054 | 0.031628 | 0.031905 |
| P_BLOCK_EXPERTS | 0.339073 | 0.372871 | 0.350910 | 0.031400 | 0.033124 | 0.032004 |
| P_BREADTH_PERSIST | 0.361974 | 0.353739 | 0.359090 | 0.034797 | 0.033556 | 0.034362 |
| P_HIER | 0.356045 | 0.367361 | 0.360008 | 0.033437 | 0.034065 | 0.033657 |
| P_RECENT_SHRINK | 0.361866 | 0.373960 | 0.366102 | 0.034110 | 0.034673 | 0.034307 |
| P_LONG_SHORT | 0.364367 | 0.449060 | 0.394029 | 0.035312 | 0.038121 | 0.036296 |
| P_RECENT_FREE | 0.385514 | 0.484864 | 0.420310 | 0.041649 | 0.046600 | 0.043383 |
| P_SHORT | 0.385514 | 0.484864 | 0.420310 | 0.041649 | 0.046600 | 0.043383 |

Ten block perturbations recompute probabilities, expected returns, widths, lower quantiles and score losses on each chosen forecast date. A small 85-row sample and a two-episode long-history diagnostic with 20% block dropout have different sources of dispersion. A complete-law mixture is also scored across these perturbations. Coefficient sign consistency measures descriptive estimation stability.

| horizon | expert | p | mean | width80 | q10 | brier | crps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | base | 0.120792 | 0.005434 | 0.004006 | 0.005872 | 0.116293 | 0.003165 |
| 5 | breadth | 0.115746 | 0.005600 | 0.003690 | 0.005976 | 0.118412 | 0.003193 |
| 5 | complete_law_mix | 0.088791 | 0.004148 | 0.002884 | 0.004992 | 0.088296 | 0.002596 |
| 5 | long | 0.052140 | 0.001912 | 0.002021 | 0.001951 | 0.038016 | 0.001553 |
| 21 | base | 0.111705 | 0.007612 | 0.006683 | 0.007964 | 0.122088 | 0.005822 |
| 21 | breadth | 0.125369 | 0.007992 | 0.006699 | 0.008446 | 0.138867 | 0.006148 |
| 21 | complete_law_mix | 0.083610 | 0.005847 | 0.006688 | 0.006968 | 0.094220 | 0.004309 |
| 21 | long | 0.029364 | 0.003381 | 0.003485 | 0.003232 | 0.048069 | 0.002701 |

[Coefficient stability](coefficient-stability.csv) · [Original model coefficients](memory-coefficients.csv) · [Perturbation detail](block-perturbation.csv).
