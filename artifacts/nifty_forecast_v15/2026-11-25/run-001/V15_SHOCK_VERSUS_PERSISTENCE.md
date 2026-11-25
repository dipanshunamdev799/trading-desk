# V15 shocks versus persistence

Every latest close innovation is standardized relative to the previous path's location and risk. The two-sided CUSUM accumulates signed innovations with a 0.45 per-step allowance. A shock is flagged with absolute standardized innovation above 2.15 or CUSUM magnitude above 2.75. A persistent candidate also needs at least two observed periods, more than 65% sign agreement in up to three recent returns, and corroboration from breadth or financial leadership. These are ex-ante trigger states. They compare a scale-only update, an update with signed continuation or reversal drift, the unchanged restart, and incremental drift/risk filtering.

## Continuation and remaining-path outcomes

| horizon | trigger | model | n | origins | mean abs z | continuation | reversal | predicted continuation | signed brier | endpoint crps | vol mae | range crps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | ordinary | incremental | 1,007 | 265 | 0.717815 | 0.492552 | 0.506455 | 0.508251 | 0.249491 | 0.007230 | 0.023358 | 0.004088 |
| 5 | ordinary | iv_restart | 1,007 | 265 | 0.717815 | 0.492552 | 0.506455 | 0.502331 | 0.249269 | 0.007220 | 0.023751 | 0.004101 |
| 5 | ordinary | shock_persistence | 1,007 | 265 | 0.717815 | 0.492552 | 0.506455 | 0.479212 | 0.250672 | 0.007240 | 0.023842 | 0.004097 |
| 5 | ordinary | vol_only_shock | 1,007 | 265 | 0.717815 | 0.492552 | 0.506455 | 0.502331 | 0.249269 | 0.007218 | 0.023826 | 0.004093 |
| 5 | persistent candidate | incremental | 23 | 21 | 2.104660 | 0.521739 | 0.478261 | 0.513247 | 0.239008 | 0.009007 | 0.019207 | 0.006527 |
| 5 | persistent candidate | iv_restart | 23 | 21 | 2.104660 | 0.521739 | 0.478261 | 0.479789 | 0.245698 | 0.009108 | 0.017490 | 0.006395 |
| 5 | persistent candidate | shock_persistence | 23 | 21 | 2.104660 | 0.521739 | 0.478261 | 0.548913 | 0.249914 | 0.008995 | 0.018183 | 0.006209 |
| 5 | persistent candidate | vol_only_shock | 23 | 21 | 2.104660 | 0.521739 | 0.478261 | 0.479789 | 0.245698 | 0.009039 | 0.018089 | 0.006294 |
| 5 | shock | incremental | 30 | 28 | 2.243364 | 0.533333 | 0.466667 | 0.524089 | 0.243348 | 0.007309 | 0.017948 | 0.004813 |
| 5 | shock | iv_restart | 30 | 28 | 2.243364 | 0.533333 | 0.466667 | 0.506120 | 0.247214 | 0.007360 | 0.018866 | 0.004876 |
| 5 | shock | shock_persistence | 30 | 28 | 2.243364 | 0.533333 | 0.466667 | 0.447656 | 0.261273 | 0.007799 | 0.016993 | 0.004576 |
| 5 | shock | vol_only_shock | 30 | 28 | 2.243364 | 0.533333 | 0.466667 | 0.506120 | 0.247214 | 0.007336 | 0.016994 | 0.004508 |
| 21 | ordinary | incremental | 4,060 | 217 | 0.731784 | 0.480049 | 0.519951 | 0.515100 | 0.251367 | 0.016953 | 0.017587 | 0.009712 |
| 21 | ordinary | iv_restart | 4,060 | 217 | 0.731784 | 0.480049 | 0.519951 | 0.499819 | 0.249456 | 0.016919 | 0.018621 | 0.009907 |
| 21 | ordinary | shock_persistence | 4,060 | 217 | 0.731784 | 0.480049 | 0.519951 | 0.456298 | 0.253011 | 0.017098 | 0.018581 | 0.009879 |
| 21 | ordinary | vol_only_shock | 4,060 | 217 | 0.731784 | 0.480049 | 0.519951 | 0.499819 | 0.249456 | 0.016907 | 0.018574 | 0.009873 |
| 21 | persistent candidate | incremental | 157 | 97 | 1.777484 | 0.605096 | 0.394904 | 0.570735 | 0.232917 | 0.014757 | 0.019760 | 0.010420 |
| 21 | persistent candidate | iv_restart | 157 | 97 | 1.777484 | 0.605096 | 0.394904 | 0.494377 | 0.240421 | 0.015570 | 0.019709 | 0.010949 |
| 21 | persistent candidate | shock_persistence | 157 | 97 | 1.777484 | 0.605096 | 0.394904 | 0.603528 | 0.239348 | 0.014698 | 0.019055 | 0.010143 |
| 21 | persistent candidate | vol_only_shock | 157 | 97 | 1.777484 | 0.605096 | 0.394904 | 0.494377 | 0.240421 | 0.015523 | 0.019159 | 0.010690 |
| 21 | shock | incremental | 123 | 89 | 2.091760 | 0.552846 | 0.447154 | 0.569042 | 0.248154 | 0.017653 | 0.024291 | 0.012034 |
| 21 | shock | iv_restart | 123 | 89 | 2.091760 | 0.552846 | 0.447154 | 0.503874 | 0.247474 | 0.017742 | 0.026059 | 0.012542 |
| 21 | shock | shock_persistence | 123 | 89 | 2.091760 | 0.552846 | 0.447154 | 0.412570 | 0.267448 | 0.018828 | 0.024213 | 0.012138 |
| 21 | shock | vol_only_shock | 123 | 89 | 2.091760 | 0.552846 | 0.447154 | 0.503874 | 0.247474 | 0.017614 | 0.024248 | 0.011907 |

## Surviving barrier outcomes by trigger

| horizon | trigger | model | cases | touch brier | integrated brier |
| --- | --- | --- | --- | --- | --- |
| 5 | ordinary | iv_restart | 14,806 | 0.079767 | 0.061394 |
| 5 | ordinary | shock_persistence | 14,806 | 0.079900 | 0.061453 |
| 5 | ordinary | vol_only_shock | 14,806 | 0.079682 | 0.061342 |
| 5 | persistent candidate | iv_restart | 262 | 0.033891 | 0.033896 |
| 5 | persistent candidate | shock_persistence | 262 | 0.033195 | 0.033615 |
| 5 | persistent candidate | vol_only_shock | 262 | 0.034015 | 0.034209 |
| 5 | shock | iv_restart | 362 | 0.057729 | 0.047079 |
| 5 | shock | shock_persistence | 362 | 0.057940 | 0.047168 |
| 5 | shock | vol_only_shock | 362 | 0.055497 | 0.045880 |
| 21 | ordinary | iv_restart | 51,603 | 0.110905 | 0.073758 |
| 21 | ordinary | shock_persistence | 51,603 | 0.111450 | 0.073886 |
| 21 | ordinary | vol_only_shock | 51,603 | 0.110737 | 0.073663 |
| 21 | persistent candidate | iv_restart | 1,665 | 0.067105 | 0.040627 |
| 21 | persistent candidate | shock_persistence | 1,665 | 0.061437 | 0.039932 |
| 21 | persistent candidate | vol_only_shock | 1,665 | 0.067324 | 0.041378 |
| 21 | shock | iv_restart | 1,332 | 0.076338 | 0.055644 |
| 21 | shock | shock_persistence | 1,332 | 0.084614 | 0.059269 |
| 21 | shock | vol_only_shock | 1,332 | 0.074795 | 0.054611 |

Continuation means the later remaining-window return shares the sign of the latest observed session. Directional loss uses the conditional remaining return. The same-law risk and range outputs include the observed original-window prefix and are separately checked in the remaining-only score columns. Corroboration is a predictive design assumption. A lasting change in expected returns would require stable improvement over the same-time risk-only control, evidence across disjoint episodes and absence of comparable gains from lagged or randomized input blocks.

[Post-shock touch evidence](shock-touch-evidence.csv) [Conditional trigger outcomes](shock-response-evidence.csv) [CUSUM states, innovations and latest inputs](joint-update-receipts.json)
