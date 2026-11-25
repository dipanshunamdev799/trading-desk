# V21 Final Research Conclusions

**Dated weights reconstructed the realized index closely.** The newly recovered 22 dated constituent snapshots tracked cash NIFTY daily within **0.424 basis points MAE**, with **0.999872** correlation on matched dates. This establishes a much stronger index-contribution measurement than the earlier liquidity-basket proxy. Index forecasts still depend on future market returns, individual returns and shared risk. Strong realized tracking creates room to measure those errors directly.

**Pooled estimation reduced some security forecast errors.** It helped against many independent stock models, while date-level ranks stayed small and randomized stock alignment remained competitive. Pure stock and sector forecasts trailed the native directional anchors. The pre-auction shrunk-covariance stock model had **0.236048 Brier and 0.024729 CRPS**, versus **0.250000** neutral Brier and the same-clock GJR **0.024694 CRPS**. This leaves a limited earlier-clock result with explicit covariance and benchmark dependence.

**The best native monthly point result stayed anchored to the index and aggregate positioning.** It reached **0.223819 Brier and 0.023184 CRPS**. Weekly native asymmetry reached **0.010167 CRPS** and the prior V20 training-omission model still led weekly Brier. The monthly adjustment’s gain is concentrated in the earlier group. Its later group gave back both direction and distribution improvements. The table preserves those signs and the complete-population paired bands. The monthly result is based on **11** disjoint windows. Study-wide historical research exposure and adjustment limits still govern interpretation.

| horizon | metric | candidate | new | reference | prior | difference |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | omit_latest_21_training_origins | 0.221693 | omit_latest_21_training_origins | 0.221693 | 0.000000 |
| 5 | crps | anchor_asymmetry | 0.010167 | price_reaction | 0.010258 | 0.000091 |
| 21 | brier | anchor_aggregate_position | 0.223819 | eight_calendar_day_embargo | 0.228088 | 0.004269 |
| 21 | crps | anchor_aggregate_position | 0.023184 | smooth5 | 0.023786 | 0.000602 |

| scope | reference | metric | n | active | disjoint | gain |
| --- | --- | --- | --- | --- | --- | --- |
| early | smooth5 | brier | 141 | 76 | 7 | 0.019699 |
| later | smooth5 | brier | 76 | 76 | 4 | -0.022891 |
| early | smooth5 | crps | 141 | 76 | 7 | 0.001281 |
| later | smooth5 | crps | 76 | 76 | 4 | -0.000658 |
| early | smooth5 | log_loss | 141 | 76 | 7 | 0.045055 |
| later | smooth5 | log_loss | 76 | 76 | 4 | -0.078028 |

| horizon | model | reference | metric | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | anchor_asymmetry | price_reaction | brier | 265 | 0.001254 | -0.002336 | 0.004845 |
| 5 | anchor_asymmetry | price_reaction | crps | 265 | 0.000091 | -0.000158 | 0.000339 |
| 21 | anchor_aggregate_position | smooth5 | brier | 217 | 0.004783 | -0.049645 | 0.059211 |
| 21 | anchor_aggregate_position | smooth5 | crps | 217 | 0.000602 | -0.002026 | 0.003230 |

**Cross-stock dependence was consequential.** Independently aligned stock paths sharply under-covered actual index outcomes. Preserving joint shocks is essential for uncertainty, even when point forecasts add little. Equity covariance supplied a competitive monthly variance-loss point estimate after anchoring to GJR, while the archived MAE and volatility-transition controls were stronger. The genuine forward files give these results a route to testing on newly accrued dates under their original issue rules.

[V21_INDEX_RETURN_RECONSTRUCTION.md](V21_INDEX_RETURN_RECONSTRUCTION.md) · [V21_JOINT_EQUITY_RETURN_DISTRIBUTIONS.md](V21_JOINT_EQUITY_RETURN_DISTRIBUTIONS.md) · [V21_TOP_DOWN_VERSUS_BOTTOM_UP.md](V21_TOP_DOWN_VERSUS_BOTTOM_UP.md) · [V21_COMPLETE_MODEL_COMPARISON.md](V21_COMPLETE_MODEL_COMPARISON.md) · [V21_VALIDATION_AND_FALSIFICATION.md](V21_VALIDATION_AND_FALSIFICATION.md) · [V21_FORWARD_RESEARCH_LEDGER.md](V21_FORWARD_RESEARCH_LEDGER.md)
