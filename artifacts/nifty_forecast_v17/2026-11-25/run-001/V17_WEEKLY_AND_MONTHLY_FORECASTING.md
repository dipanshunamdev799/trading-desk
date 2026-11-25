# NIFTY V17 — Weekly and monthly forecasting

The original reference is the previous official cash close. The horizon ends at the official close of session number five or 21. V17 asserts case-level equality to the original V14 realized return and preserves **265 weekly and 217 monthly** origins. The D 17:00 IST reconstruction uses earlier foreign observations and domestic snapshot variables, with D 17:00 GIFT where available. The following morning at 08:55 can incorporate the completed US session, Asia inputs where independently timestamped and the latest pre-auction GIFT forecast. The V14 standalone forecast’s native 09:10 guard stays attached to its exact weighted atom archive. Comparing V16 08:55 to the native V14 book addresses published historical performance. Testing models against same-clock parents addresses the value of newly observable data. Later post-open figures in the research cover fixed original endpoints from their own later reference.

| horizon | cutoff | model | n | disjoint | brier | crps | accuracy | balanced accuracy | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | clock_structural | 265 | 53 | 0.238274 | 0.010658 | 0.569811 | 0.571004 | 0.766038 | 0.041040 |
| 5 | preauction_0855 | component_plus_residual | 265 | 53 | 0.238003 | 0.010309 | 0.577358 | 0.575970 | 0.758491 | 0.041019 |
| 5 | preauction_0855 | fixed_structural_mixture | 265 | 53 | 0.237205 | 0.010497 | 0.592453 | 0.593959 | 0.777358 | 0.041811 |
| 5 | preauction_0855 | historical | 265 | 53 | 0.251387 | 0.010913 | 0.494340 | 0.484638 | 0.758491 | 0.041019 |
| 5 | preauction_0855 | low_rank_sector_risk | 265 | 53 | 0.244958 | 0.010911 | 0.562264 | 0.550820 | 0.758491 | 0.041026 |
| 5 | preauction_0855 | low_rank_tasks | 265 | 53 | 0.242100 | 0.010815 | 0.577358 | 0.567914 | 0.766038 | 0.041024 |
| 5 | preauction_0855 | neutral | 265 | 53 | 0.250000 | 0.011089 | 0.441509 | 0.500000 | 0.754717 | 0.042146 |
| 5 | preauction_0855 | stock_direct | 265 | 53 | 0.240400 | 0.010725 | 0.566038 | 0.565835 | 0.777358 | 0.041030 |
| 5 | preauction_0855 | stock_residual | 265 | 53 | 0.246238 | 0.010951 | 0.543396 | 0.545565 | 0.754717 | 0.041030 |
| 5 | previous_1700 | clock_structural | 265 | 53 | 0.238605 | 0.010721 | 0.577358 | 0.578656 | 0.762264 | 0.040973 |
| 5 | previous_1700 | component_plus_residual | 265 | 53 | 0.236585 | 0.010658 | 0.615094 | 0.610649 | 0.766038 | 0.040965 |
| 5 | previous_1700 | fixed_structural_mixture | 265 | 53 | 0.239099 | 0.010758 | 0.611321 | 0.610851 | 0.769811 | 0.041149 |
| 5 | previous_1700 | historical | 265 | 53 | 0.250408 | 0.010907 | 0.490566 | 0.481260 | 0.758491 | 0.040953 |
| 5 | previous_1700 | low_rank_sector_risk | 265 | 53 | 0.251625 | 0.011199 | 0.535849 | 0.534332 | 0.728302 | 0.041005 |
| 5 | previous_1700 | low_rank_tasks | 265 | 53 | 0.247342 | 0.011045 | 0.543396 | 0.540194 | 0.743396 | 0.040995 |
| 5 | previous_1700 | neutral | 265 | 53 | 0.250000 | 0.011089 | 0.441509 | 0.500000 | 0.762264 | 0.042115 |
| 5 | previous_1700 | stock_direct | 265 | 53 | 0.240942 | 0.010759 | 0.562264 | 0.563352 | 0.773585 | 0.040963 |
| 5 | previous_1700 | stock_residual | 265 | 53 | 0.246955 | 0.011018 | 0.558491 | 0.559078 | 0.747170 | 0.040961 |
| 21 | preauction_0855 | clock_structural | 217 | 11 | 0.302805 | 0.028519 | 0.470046 | 0.440164 | 0.663594 | 0.089469 |
| 21 | preauction_0855 | component_plus_residual | 217 | 11 | 0.300952 | 0.028698 | 0.516129 | 0.490466 | 0.617512 | 0.089434 |
| 21 | preauction_0855 | fixed_structural_mixture | 217 | 11 | 0.307067 | 0.028915 | 0.470046 | 0.442494 | 0.640553 | 0.088608 |
| 21 | preauction_0855 | historical | 217 | 11 | 0.294519 | 0.026743 | 0.313364 | 0.332269 | 0.682028 | 0.090738 |
| 21 | preauction_0855 | low_rank_sector_risk | 217 | 11 | 0.293771 | 0.029057 | 0.479263 | 0.458844 | 0.640553 | 0.089469 |
| 21 | preauction_0855 | low_rank_tasks | 217 | 11 | 0.299928 | 0.029259 | 0.460829 | 0.436626 | 0.640553 | 0.089509 |
| 21 | preauction_0855 | neutral | 217 | 11 | 0.250000 | 0.025543 | 0.437788 | 0.500000 | 0.691244 | 0.078299 |
| 21 | preauction_0855 | stock_direct | 217 | 11 | 0.299336 | 0.028226 | 0.497696 | 0.470578 | 0.663594 | 0.089493 |
| 21 | preauction_0855 | stock_residual | 217 | 11 | 0.323762 | 0.030023 | 0.493088 | 0.473469 | 0.635945 | 0.089434 |
| 21 | previous_1700 | clock_structural | 217 | 11 | 0.300452 | 0.028321 | 0.479263 | 0.450690 | 0.658986 | 0.089081 |
| 21 | previous_1700 | component_plus_residual | 217 | 11 | 0.299021 | 0.028360 | 0.488479 | 0.458887 | 0.654378 | 0.089079 |
| 21 | previous_1700 | fixed_structural_mixture | 217 | 11 | 0.305447 | 0.028753 | 0.474654 | 0.445427 | 0.640553 | 0.088262 |
| 21 | previous_1700 | historical | 217 | 11 | 0.294085 | 0.026695 | 0.317972 | 0.337532 | 0.682028 | 0.090320 |
| 21 | previous_1700 | low_rank_sector_risk | 217 | 11 | 0.292466 | 0.028756 | 0.497696 | 0.475237 | 0.649770 | 0.089064 |
| 21 | previous_1700 | low_rank_tasks | 217 | 11 | 0.306004 | 0.029421 | 0.465438 | 0.438395 | 0.626728 | 0.089051 |
| 21 | previous_1700 | neutral | 217 | 11 | 0.250000 | 0.025545 | 0.437788 | 0.500000 | 0.691244 | 0.078141 |
| 21 | previous_1700 | stock_direct | 217 | 11 | 0.295224 | 0.027996 | 0.511521 | 0.486368 | 0.663594 | 0.089110 |
| 21 | previous_1700 | stock_residual | 217 | 11 | 0.321644 | 0.029834 | 0.493088 | 0.473469 | 0.635945 | 0.089041 |

## Paired value at each origin

The return track tested direct ridge with stock inputs, stock residual corrections, a decomposition into first overnight, initial regular session and future cumulative movement, two-factor fits across gap, regular, and multi-horizon return targets, and a fixed model mixture. The auxiliary task variant also learns the bank-relative session return and session risk using complete matured rows. All prior labels resolve before the model’s date guard. The mixture pools evenly spaced atoms from three component distributions. The component experiment adds the first-return locations before sharing the structural residual shape. Exact historical V14 laws were shifted in a separate past-error overlay. Early correction coverage matters because an exact protected reference is available for fewer prior days than the continually rebuilt parent.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | stock_direct | clock_structural | brier | 265 | 53 | 0.240400 | 0.238274 | -0.002125 | -0.007131 | 0.002881 |
| 5 | preauction_0855 | stock_direct | clock_structural | crps | 265 | 53 | 0.010725 | 0.010658 | -0.000066 | -0.000205 | 0.000072 |
| 5 | preauction_0855 | component_plus_residual | clock_structural | brier | 265 | 53 | 0.238003 | 0.238274 | 0.000271 | -0.016045 | 0.016587 |
| 5 | preauction_0855 | component_plus_residual | clock_structural | crps | 265 | 53 | 0.010309 | 0.010658 | 0.000350 | -0.000319 | 0.001018 |
| 5 | preauction_0855 | low_rank_tasks | clock_structural | brier | 265 | 53 | 0.242100 | 0.238274 | -0.003826 | -0.027081 | 0.019430 |
| 5 | preauction_0855 | low_rank_tasks | clock_structural | crps | 265 | 53 | 0.010815 | 0.010658 | -0.000157 | -0.000790 | 0.000477 |
| 5 | preauction_0855 | low_rank_sector_risk | clock_structural | brier | 265 | 53 | 0.244958 | 0.238274 | -0.006684 | -0.034699 | 0.021332 |
| 5 | preauction_0855 | low_rank_sector_risk | clock_structural | crps | 265 | 53 | 0.010911 | 0.010658 | -0.000253 | -0.001017 | 0.000511 |
| 5 | preauction_0855 | stock_residual | clock_structural | brier | 265 | 53 | 0.246238 | 0.238274 | -0.007963 | -0.014922 | -0.001004 |
| 5 | preauction_0855 | stock_residual | clock_structural | crps | 265 | 53 | 0.010951 | 0.010658 | -0.000292 | -0.000516 | -0.000069 |
| 5 | preauction_0855 | fixed_structural_mixture | clock_structural | brier | 265 | 53 | 0.237205 | 0.238274 | 0.001069 | -0.005566 | 0.007704 |
| 5 | preauction_0855 | fixed_structural_mixture | clock_structural | crps | 265 | 53 | 0.010497 | 0.010658 | 0.000161 | -0.000112 | 0.000434 |
| 5 | previous_1700 | stock_direct | clock_structural | brier | 265 | 53 | 0.240942 | 0.238605 | -0.002337 | -0.007904 | 0.003229 |
| 5 | previous_1700 | stock_direct | clock_structural | crps | 265 | 53 | 0.010759 | 0.010721 | -0.000038 | -0.000181 | 0.000106 |
| 5 | previous_1700 | component_plus_residual | clock_structural | brier | 265 | 53 | 0.236585 | 0.238605 | 0.002020 | -0.009628 | 0.013668 |
| 5 | previous_1700 | component_plus_residual | clock_structural | crps | 265 | 53 | 0.010658 | 0.010721 | 0.000063 | -0.000262 | 0.000388 |
| 5 | previous_1700 | low_rank_tasks | clock_structural | brier | 265 | 53 | 0.247342 | 0.238605 | -0.008738 | -0.037946 | 0.020471 |
| 5 | previous_1700 | low_rank_tasks | clock_structural | crps | 265 | 53 | 0.011045 | 0.010721 | -0.000324 | -0.001244 | 0.000596 |
| 5 | previous_1700 | low_rank_sector_risk | clock_structural | brier | 265 | 53 | 0.251625 | 0.238605 | -0.013020 | -0.044631 | 0.018590 |
| 5 | previous_1700 | low_rank_sector_risk | clock_structural | crps | 265 | 53 | 0.011199 | 0.010721 | -0.000478 | -0.001536 | 0.000580 |
| 5 | previous_1700 | stock_residual | clock_structural | brier | 265 | 53 | 0.246955 | 0.238605 | -0.008351 | -0.015687 | -0.001014 |
| 5 | previous_1700 | stock_residual | clock_structural | crps | 265 | 53 | 0.011018 | 0.010721 | -0.000297 | -0.000535 | -0.000058 |
| 5 | previous_1700 | fixed_structural_mixture | clock_structural | brier | 265 | 53 | 0.239099 | 0.238605 | -0.000494 | -0.005216 | 0.004228 |
| 5 | previous_1700 | fixed_structural_mixture | clock_structural | crps | 265 | 53 | 0.010758 | 0.010721 | -0.000037 | -0.000159 | 0.000086 |
| 21 | preauction_0855 | stock_direct | clock_structural | brier | 217 | 11 | 0.299336 | 0.302805 | 0.003469 | -0.005376 | 0.012314 |
| 21 | preauction_0855 | stock_direct | clock_structural | crps | 217 | 11 | 0.028226 | 0.028519 | 0.000293 | -0.000178 | 0.000764 |
| 21 | preauction_0855 | component_plus_residual | clock_structural | brier | 217 | 11 | 0.300952 | 0.302805 | 0.001853 | -0.016682 | 0.020388 |
| 21 | preauction_0855 | component_plus_residual | clock_structural | crps | 217 | 11 | 0.028698 | 0.028519 | -0.000179 | -0.001080 | 0.000721 |
| 21 | preauction_0855 | low_rank_tasks | clock_structural | brier | 217 | 11 | 0.299928 | 0.302805 | 0.002877 | -0.014454 | 0.020208 |
| 21 | preauction_0855 | low_rank_tasks | clock_structural | crps | 217 | 11 | 0.029259 | 0.028519 | -0.000740 | -0.002253 | 0.000772 |
| 21 | preauction_0855 | low_rank_sector_risk | clock_structural | brier | 217 | 11 | 0.293771 | 0.302805 | 0.009034 | -0.014375 | 0.032442 |
| 21 | preauction_0855 | low_rank_sector_risk | clock_structural | crps | 217 | 11 | 0.029057 | 0.028519 | -0.000538 | -0.002387 | 0.001311 |
| 21 | preauction_0855 | stock_residual | clock_structural | brier | 217 | 11 | 0.323762 | 0.302805 | -0.020957 | -0.043793 | 0.001879 |
| 21 | preauction_0855 | stock_residual | clock_structural | crps | 217 | 11 | 0.030023 | 0.028519 | -0.001504 | -0.003067 | 0.000060 |
| 21 | preauction_0855 | fixed_structural_mixture | clock_structural | brier | 217 | 11 | 0.307067 | 0.302805 | -0.004262 | -0.016072 | 0.007547 |
| 21 | preauction_0855 | fixed_structural_mixture | clock_structural | crps | 217 | 11 | 0.028915 | 0.028519 | -0.000395 | -0.001058 | 0.000268 |
| 21 | previous_1700 | stock_direct | clock_structural | brier | 217 | 11 | 0.295224 | 0.300452 | 0.005228 | -0.004514 | 0.014971 |
| 21 | previous_1700 | stock_direct | clock_structural | crps | 217 | 11 | 0.027996 | 0.028321 | 0.000324 | -0.000194 | 0.000843 |
| 21 | previous_1700 | component_plus_residual | clock_structural | brier | 217 | 11 | 0.299021 | 0.300452 | 0.001432 | -0.009242 | 0.012105 |
| 21 | previous_1700 | component_plus_residual | clock_structural | crps | 217 | 11 | 0.028360 | 0.028321 | -0.000039 | -0.000492 | 0.000413 |
| 21 | previous_1700 | low_rank_tasks | clock_structural | brier | 217 | 11 | 0.306004 | 0.300452 | -0.005552 | -0.018865 | 0.007762 |
| 21 | previous_1700 | low_rank_tasks | clock_structural | crps | 217 | 11 | 0.029421 | 0.028321 | -0.001100 | -0.002688 | 0.000487 |
| 21 | previous_1700 | low_rank_sector_risk | clock_structural | brier | 217 | 11 | 0.292466 | 0.300452 | 0.007986 | -0.009410 | 0.025382 |
| 21 | previous_1700 | low_rank_sector_risk | clock_structural | crps | 217 | 11 | 0.028756 | 0.028321 | -0.000435 | -0.002126 | 0.001256 |
| 21 | previous_1700 | stock_residual | clock_structural | brier | 217 | 11 | 0.321644 | 0.300452 | -0.021191 | -0.044224 | 0.001841 |
| 21 | previous_1700 | stock_residual | clock_structural | crps | 217 | 11 | 0.029834 | 0.028321 | -0.001513 | -0.003044 | 0.000017 |
| 21 | previous_1700 | fixed_structural_mixture | clock_structural | brier | 217 | 11 | 0.305447 | 0.300452 | -0.004995 | -0.015123 | 0.005134 |
| 21 | previous_1700 | fixed_structural_mixture | clock_structural | crps | 217 | 11 | 0.028753 | 0.028321 | -0.000432 | -0.001032 | 0.000167 |

| horizon | subset | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | full | V14_stock_overlay | V14_sign_shrinkage | brier | 265 | 53 | 0.229520 | 0.228529 | -0.000992 | -0.009335 | 0.007352 |
| 5 | full | V14_stock_overlay | V14_sign_shrinkage | crps | 265 | 53 | 0.010528 | 0.010457 | -0.000071 | -0.000414 | 0.000272 |
| 5 | full | V14_stock_overlay | V14_sign_shrinkage | log_loss | 265 | 53 | 0.651942 | 0.648943 | -0.002999 | -0.020802 | 0.014804 |
| 21 | full | V14_stock_overlay | V14_domestic_GJR | brier | 217 | 11 | 0.255805 | 0.245042 | -0.010763 | -0.045465 | 0.023940 |
| 21 | full | V14_stock_overlay | V14_domestic_GJR | crps | 217 | 11 | 0.025210 | 0.024989 | -0.000221 | -0.001667 | 0.001226 |
| 21 | full | V14_stock_overlay | V14_domestic_GJR | log_loss | 217 | 11 | 0.704862 | 0.683095 | -0.021767 | -0.095494 | 0.051960 |
| 5 | adapted | V14_stock_overlay | V14_sign_shrinkage | brier | 223 | 45 | 0.225707 | 0.224529 | -0.001178 | -0.011582 | 0.009225 |
| 5 | adapted | V14_stock_overlay | V14_sign_shrinkage | crps | 223 | 45 | 0.011323 | 0.011239 | -0.000085 | -0.000502 | 0.000333 |
| 5 | adapted | V14_stock_overlay | V14_sign_shrinkage | log_loss | 223 | 45 | 0.644462 | 0.640898 | -0.003564 | -0.025666 | 0.018538 |
| 21 | adapted | V14_stock_overlay | V14_domestic_GJR | brier | 159 | 8 | 0.255983 | 0.241294 | -0.014689 | -0.061092 | 0.031715 |
| 21 | adapted | V14_stock_overlay | V14_domestic_GJR | crps | 159 | 8 | 0.025347 | 0.025046 | -0.000301 | -0.002196 | 0.001593 |
| 21 | adapted | V14_stock_overlay | V14_domestic_GJR | log_loss | 159 | 8 | 0.705257 | 0.675550 | -0.029707 | -0.129377 | 0.069962 |

## Issue clock and the early barrier effect

The archived 265-origin GIFT-first model is an **08:55** next-morning comparison. V17 retimed its first component, previous-close domestic states and same-time GJR and ATM IV path controls. The previous-close result measures the value of the earlier available quote. Some reconstructed return-distribution differences are due to simple model structure, so the matched baseline matters for each claimed improvement.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | decomposed_gift | decomposed | brier | 265 | 53 | 0.242618 | 0.246549 | 0.003930 | -0.009611 | 0.017472 |
| 5 | preauction_0855 | decomposed_gift | decomposed | endpoint_crps | 265 | 53 | 0.010493 | 0.010870 | 0.000377 | -0.000183 | 0.000937 |
| 5 | preauction_0855 | decomposed_gift | decomposed | touch_brier | 265 | 53 | 0.132201 | 0.145973 | 0.013772 | 0.003970 | 0.023574 |
| 5 | preauction_0855 | decomposed_gift | same_clock_IV | brier | 265 | 53 | 0.242618 | 0.248408 | 0.005789 | -0.017574 | 0.029153 |
| 5 | preauction_0855 | decomposed_gift | same_clock_IV | endpoint_crps | 265 | 53 | 0.010493 | 0.010672 | 0.000179 | -0.000612 | 0.000970 |
| 5 | preauction_0855 | decomposed_gift | same_clock_IV | touch_brier | 265 | 53 | 0.132201 | 0.144562 | 0.012360 | 0.002607 | 0.022114 |
| 5 | preauction_0855 | decomposed_gift | same_clock_GJR | brier | 265 | 53 | 0.242618 | 0.250763 | 0.008144 | -0.016719 | 0.033008 |
| 5 | preauction_0855 | decomposed_gift | same_clock_GJR | endpoint_crps | 265 | 53 | 0.010493 | 0.010922 | 0.000429 | -0.000511 | 0.001368 |
| 5 | preauction_0855 | decomposed_gift | same_clock_GJR | touch_brier | 265 | 53 | 0.132201 | 0.148396 | 0.016195 | 0.006955 | 0.025435 |
| 5 | previous_1700 | decomposed_gift | decomposed | brier | 265 | 53 | 0.242379 | 0.247511 | 0.005132 | -0.004564 | 0.014828 |
| 5 | previous_1700 | decomposed_gift | decomposed | endpoint_crps | 265 | 53 | 0.010811 | 0.010918 | 0.000107 | -0.000121 | 0.000335 |
| 5 | previous_1700 | decomposed_gift | decomposed | touch_brier | 265 | 53 | 0.146161 | 0.147623 | 0.001462 | -0.003552 | 0.006475 |
| 5 | previous_1700 | decomposed_gift | same_clock_IV | brier | 265 | 53 | 0.242379 | 0.248408 | 0.006029 | -0.010537 | 0.022595 |
| 5 | previous_1700 | decomposed_gift | same_clock_IV | endpoint_crps | 265 | 53 | 0.010811 | 0.010672 | -0.000139 | -0.000988 | 0.000710 |
| 5 | previous_1700 | decomposed_gift | same_clock_IV | touch_brier | 265 | 53 | 0.146161 | 0.144562 | -0.001599 | -0.010125 | 0.006926 |
| 5 | previous_1700 | decomposed_gift | same_clock_GJR | brier | 265 | 53 | 0.242379 | 0.250763 | 0.008384 | -0.009740 | 0.026507 |
| 5 | previous_1700 | decomposed_gift | same_clock_GJR | endpoint_crps | 265 | 53 | 0.010811 | 0.010922 | 0.000111 | -0.000823 | 0.001045 |
| 5 | previous_1700 | decomposed_gift | same_clock_GJR | touch_brier | 265 | 53 | 0.146161 | 0.148396 | 0.002235 | -0.006016 | 0.010487 |
| 21 | preauction_0855 | decomposed_gift | decomposed | brier | 217 | 11 | 0.273803 | 0.269590 | -0.004213 | -0.017187 | 0.008761 |
| 21 | preauction_0855 | decomposed_gift | decomposed | endpoint_crps | 217 | 11 | 0.027288 | 0.026979 | -0.000310 | -0.000985 | 0.000366 |
| 21 | preauction_0855 | decomposed_gift | decomposed | touch_brier | 217 | 11 | 0.184421 | 0.185829 | 0.001408 | -0.008416 | 0.011231 |
| 21 | preauction_0855 | decomposed_gift | same_clock_IV | brier | 217 | 11 | 0.273803 | 0.247721 | -0.026082 | -0.105551 | 0.053387 |
| 21 | preauction_0855 | decomposed_gift | same_clock_IV | endpoint_crps | 217 | 11 | 0.027288 | 0.025198 | -0.002091 | -0.006865 | 0.002684 |
| 21 | preauction_0855 | decomposed_gift | same_clock_IV | touch_brier | 217 | 11 | 0.184421 | 0.184372 | -0.000049 | -0.036276 | 0.036178 |
| 21 | preauction_0855 | decomposed_gift | same_clock_GJR | brier | 217 | 11 | 0.273803 | 0.251376 | -0.022427 | -0.107154 | 0.062301 |
| 21 | preauction_0855 | decomposed_gift | same_clock_GJR | endpoint_crps | 217 | 11 | 0.027288 | 0.024694 | -0.002594 | -0.007668 | 0.002480 |
| 21 | preauction_0855 | decomposed_gift | same_clock_GJR | touch_brier | 217 | 11 | 0.184421 | 0.183861 | -0.000561 | -0.036790 | 0.035668 |
| 21 | previous_1700 | decomposed_gift | decomposed | brier | 217 | 11 | 0.275411 | 0.271859 | -0.003552 | -0.012185 | 0.005082 |
| 21 | previous_1700 | decomposed_gift | decomposed | endpoint_crps | 217 | 11 | 0.027127 | 0.027025 | -0.000103 | -0.000428 | 0.000222 |
| 21 | previous_1700 | decomposed_gift | decomposed | touch_brier | 217 | 11 | 0.186245 | 0.187188 | 0.000943 | -0.003699 | 0.005586 |
| 21 | previous_1700 | decomposed_gift | same_clock_IV | brier | 217 | 11 | 0.275411 | 0.247721 | -0.027690 | -0.111641 | 0.056261 |
| 21 | previous_1700 | decomposed_gift | same_clock_IV | endpoint_crps | 217 | 11 | 0.027127 | 0.025198 | -0.001930 | -0.006681 | 0.002821 |
| 21 | previous_1700 | decomposed_gift | same_clock_IV | touch_brier | 217 | 11 | 0.186245 | 0.184372 | -0.001872 | -0.036943 | 0.033199 |
| 21 | previous_1700 | decomposed_gift | same_clock_GJR | brier | 217 | 11 | 0.275411 | 0.251376 | -0.024034 | -0.113182 | 0.065114 |
| 21 | previous_1700 | decomposed_gift | same_clock_GJR | endpoint_crps | 217 | 11 | 0.027127 | 0.024694 | -0.002433 | -0.007466 | 0.002600 |
| 21 | previous_1700 | decomposed_gift | same_clock_GJR | touch_brier | 217 | 11 | 0.186245 | 0.183861 | -0.002384 | -0.037419 | 0.032652 |

[Original cutoff and maturity audit](original-cutoff-audit.csv) · [Original fitted laws](original-clock-laws.npz) · [Native protected-law overlay](protected-law-residual-overlays.csv.gz) · [Original same-cutoff comparison](original-timed-matched.csv) · [Retimed joint path archive](retimed-path-archive.json)
