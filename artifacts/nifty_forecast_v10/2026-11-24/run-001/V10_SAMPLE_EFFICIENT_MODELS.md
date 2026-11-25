# V10 Sample Efficient Models

The predefined sample-efficient families include five-, ten- and twenty-input ridge, family-specific and cluster-specific shrinkage, cluster-balanced Elastic Net, zero-centered Bayesian ridge, family parameter pooling, factor-plus-residual pooling, and five principal directions from twenty causal inputs. Regularization, basis and median/scale transformations obey the fit boundary. The family group penalties incorporate slowly varying exposures only through the causal features. Every fit preserves the estimable standardized coefficients in the underlying feature basis.

## Weekly matched-complexity diagnostics

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| S_NATIVE_ROT | 0.264889 | 0.183938 | 0.236785 | 0.011579 | 0.010506 | 0.011207 |
| S_ELASTIC | 0.261862 | 0.201841 | 0.241025 | 0.012627 | 0.010861 | 0.012013 |
| S_GROUPS | 0.300209 | 0.189459 | 0.261760 | 0.012755 | 0.010548 | 0.011989 |
| S_RESIDUAL | 0.301194 | 0.189056 | 0.262263 | 0.012851 | 0.010799 | 0.012139 |
| S_HIERARCHY | 0.309479 | 0.199323 | 0.271236 | 0.013095 | 0.010932 | 0.012344 |
| S_LOWRANK | 0.291887 | 0.235117 | 0.272178 | 0.012517 | 0.011861 | 0.012289 |
| S_POOL | 0.312085 | 0.199843 | 0.273118 | 0.013316 | 0.011226 | 0.012590 |
| BASE10 | 0.285113 | 0.256111 | 0.275044 | 0.012005 | 0.012152 | 0.012056 |
| BASE20 | 0.302169 | 0.242351 | 0.281402 | 0.012822 | 0.011591 | 0.012395 |
| BASE5 | 0.289767 | 0.272880 | 0.283905 | 0.012242 | 0.012696 | 0.012400 |
| S_BAYES | 0.293124 | 0.271922 | 0.285763 | 0.013182 | 0.012287 | 0.012871 |

## Refit dispersion under twelve draws per origin

| horizon | mode | origins | median_rows | median_probability_sd | median_location_sd | mean_Brier |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | expanding_drop20 | 5 | 275.000000 | 0.049617 | 0.001266 | 0.212150 |
| 5 | small_blocks | 5 | 85.000000 | 0.095180 | 0.003708 | 0.238002 |
| 5 | small_individual | 5 | 85.000000 | 0.058106 | 0.001812 | 0.225976 |
| 21 | expanding_drop20 | 4 | 253.500000 | 0.044136 | 0.002685 | 0.487692 |
| 21 | small_blocks | 4 | 85.000000 | 0.111748 | 0.009718 | 0.443282 |
| 21 | small_individual | 4 | 85.000000 | 0.060953 | 0.003368 | 0.472952 |

Small individual random subsets, small contiguous blocks and expanding history with 20% block removal are measured on the same later-origin panel. Weekly probability standard deviations are medians across query origins. The refits also retain return-location dispersion and coefficients. Differences between block selection and individual selection show how strongly the particular market path matters. Larger effective historical support coincided with lower refit dispersion here. These comparisons do not identify the formal bias or variance of a data-generating process. [Refit dates and coefficients](training-perturbations.csv) · [Within-cohort coefficient variability](coefficient-stability.csv).
