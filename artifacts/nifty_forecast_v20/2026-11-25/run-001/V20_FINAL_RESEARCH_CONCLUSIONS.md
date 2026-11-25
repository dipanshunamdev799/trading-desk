# V20 Final Research Conclusions

The native timing audit confirmed that participant reports entered through a modeled 08:15 publication allowance, before the 08:55 overlay snapshot and original 09:10 issue. V19's original monthly Brier of **0.228199** and CRPS of **0.024010** reproduce on 217 cases, with 159 active cases representing eight disjoint windows. The original weekly V18 corporate result of **0.223481 Brier and 0.010318 CRPS** is the preserved earlier comparator.

The clearest descriptive lifetime difference was offshore pricing. At 08:55 the GIFT rank correlation was **0.830** with the opening gap, **0.589** with the first close-to-close return, and **-0.037** with sessions 6–21. In that pre-auction 6–21 return experiment, the fresh participant futures CRPS gain was **-0.000010** over the price parent on **217** origins, with earlier/later gains of **-0.000047** and **0.000058**. The corporate announcement gain was **-0.000305**. The dependence-adjusted intervals for those two late gains were **[-0.002805, 0.002786]** and **[-0.003021, 0.002410]**, respectively.

Against the stronger same-clock GJR path control, smoothed positioning after the first five sessions moved CRPS from **0.020084 to 0.019717** and Brier from **0.247618 to 0.245309** on **152** matched cases covering **10** disjoint 16-session windows. The earlier/later CRPS gains were **0.000996** and **-0.000262**. Its adjusted CRPS gain band was **[-0.004074, 0.004808]**. The post-week effect is an exploratory, cohort-dependent result.

The V20 full-population native weekly Brier point leader was **omit_latest_21_training_origins at 0.221693**, and the weekly CRPS point leader was **price_reaction at 0.010258**. The monthly native point leaders were **eight_calendar_day_embargo at 0.228088 Brier** and **smooth5 at 0.023786 CRPS**. The full-population scores include each candidate’s specified fallback. **4 of 4** search-adjusted intervals for gains over the earlier leaders include zero on paired active dates. Forecasts from different clocks remain distinct.

| horizon | model | parent | metric | n | disjoint | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | omit_latest_21_training_origins | v18_corporate_native | brier | 202 | 41 | 0.000387 | -0.017387 | 0.018160 |
| 5 | price_reaction | v18_corporate_native | crps | 223 | 45 | 0.000071 | -0.000969 | 0.001112 |
| 21 | eight_calendar_day_embargo | v19_position_native | brier | 154 | 8 | 0.002815 | -0.008539 | 0.014170 |
| 21 | smooth5 | v19_position_native | crps | 159 | 8 | 0.000305 | -0.000945 | 0.001555 |

| model | n | disjoint | brier | crps | log loss |
| --- | --- | --- | --- | --- | --- |
| G_fixed_specialized_mixture | 217 | 11 | 0.261585 | 0.026360 | 0.717663 |
| archived_joint_GJR | 217 | 11 | 0.251376 | 0.024694 | 0.695900 |
| archived_same_clock | 217 | 11 | 0.250000 | 0.025543 | 0.693147 |

The strongest same-clock distribution controls give a demanding comparison for separately fitted pooled, sparse and component architectures. The aged custody and fund group improved on the simple lifetime price model, while its pre-auction Brier of **0.307288** on matched origins remained above the neutral **0.250000**. V20 preserves risk and barrier references apart from the directional results. Additional dated macro releases, index membership notices and CDSL reports improve source provenance. The next identifiable test measures the new weekly variants and the monthly positioning and post-week components over independently accumulated dates with fixed guard clocks.

[V20_PREDICTIVE_INFORMATION_LIFETIMES.md](V20_PREDICTIVE_INFORMATION_LIFETIMES.md) · [V20_TEMPORAL_RETURN_DECOMPOSITION.md](V20_TEMPORAL_RETURN_DECOMPOSITION.md) · [V20_COMPLETE_MODEL_COMPARISON.md](V20_COMPLETE_MODEL_COMPARISON.md) · [V20_VALIDATION_AND_FALSIFICATION.md](V20_VALIDATION_AND_FALSIFICATION.md) · [V20_FORWARD_RESEARCH_LEDGER.md](V20_FORWARD_RESEARCH_LEDGER.md) · [information-lifetime-heatmap.png](information-lifetime-heatmap.png)
