# NIFTY V17 — Final research conclusions

**The clearest V17 finding is time-specific opening-price discovery.** At 08:55, the 15:30-anchored GIFT model scored **0.101285 Brier**, **0.001451 CRPS**, and **86.69% directional accuracy** on its eligible cohort. Relative to the same method issued D 17:00, the next-morning Brier gain was **0.164944** on **246** identical mornings. Historical gap surprise then had to beat observable cash movement, volatility and native sectors on a separate target. The stock and opening-surprise layers usually delivered smaller or adverse directional increments. The date-paired evidence below gives the representative core return tests before picking winners.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | r30 | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.250299 | 0.247738 | -0.002562 | -0.007601 | 0.002478 |
| 09:25 | r30 | stock_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.251053 | 0.248972 | -0.002081 | -0.005880 | 0.001718 |
| 09:25 | r30 | financial_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249848 | 0.248972 | -0.000876 | -0.004948 | 0.003196 |
| 09:25 | r30 | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250670 | 0.248972 | -0.001698 | -0.007988 | 0.004593 |
| 09:25 | r30 | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250314 | 0.248972 | -0.001342 | -0.006090 | 0.003407 |
| 09:25 | regular_residual | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.252806 | 0.248170 | -0.004636 | -0.009282 | 0.000010 |
| 09:25 | regular_residual | stock_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249490 | 0.247995 | -0.001495 | -0.004965 | 0.001975 |
| 09:25 | regular_residual | financial_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250638 | 0.247995 | -0.002643 | -0.007046 | 0.001761 |
| 09:25 | regular_residual | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249277 | 0.247995 | -0.001282 | -0.007601 | 0.005036 |
| 09:25 | regular_residual | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249682 | 0.247995 | -0.001687 | -0.006882 | 0.003508 |
| 09:25 | remaining_21 | surprise_residual | frozen_parent_residual_history | brier | 230 | 12 | 0.302861 | 0.292340 | -0.010521 | -0.049414 | 0.028371 |
| 09:25 | remaining_21 | stock_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.300222 | 0.289840 | -0.010382 | -0.051209 | 0.030444 |
| 09:25 | remaining_21 | financial_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.303583 | 0.289840 | -0.013744 | -0.059090 | 0.031603 |
| 09:25 | remaining_21 | liquidity_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.305786 | 0.289840 | -0.015946 | -0.051340 | 0.019449 |
| 09:25 | remaining_21 | cross_instrument_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.301239 | 0.289840 | -0.011399 | -0.053701 | 0.030904 |
| 09:25 | remaining_5 | surprise_residual | frozen_parent_residual_history | brier | 244 | 51 | 0.241120 | 0.240992 | -0.000128 | -0.008084 | 0.007828 |
| 09:25 | remaining_5 | stock_residual | frozen_parent_residual_history | brier | 253 | 51 | 0.242376 | 0.239042 | -0.003334 | -0.012839 | 0.006171 |
| 09:25 | remaining_5 | financial_residual | frozen_parent_residual_history | brier | 253 | 51 | 0.243263 | 0.239042 | -0.004221 | -0.014229 | 0.005786 |
| 09:25 | remaining_5 | liquidity_residual | frozen_parent_residual_history | brier | 253 | 51 | 0.243236 | 0.239042 | -0.004195 | -0.017042 | 0.008652 |
| 09:25 | remaining_5 | cross_instrument_residual | frozen_parent_residual_history | brier | 253 | 51 | 0.242291 | 0.239042 | -0.003249 | -0.012616 | 0.006119 |
| 10:20 | r30 | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.261404 | 0.260508 | -0.000895 | -0.006232 | 0.004442 |
| 10:20 | r30 | stock_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.264007 | 0.260102 | -0.003905 | -0.008220 | 0.000410 |
| 10:20 | r30 | financial_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.260704 | 0.260102 | -0.000602 | -0.005247 | 0.004042 |
| 10:20 | r30 | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.264868 | 0.260102 | -0.004766 | -0.008449 | -0.001084 |
| 10:20 | r30 | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.262813 | 0.260102 | -0.002711 | -0.008473 | 0.003051 |
| 10:20 | regular_residual | surprise_residual | frozen_parent_residual_history | brier | 248 | 248 | 0.251217 | 0.248326 | -0.002891 | -0.007610 | 0.001827 |
| 10:20 | regular_residual | stock_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.248930 | 0.247850 | -0.001081 | -0.008002 | 0.005841 |
| 10:20 | regular_residual | financial_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250245 | 0.247850 | -0.002395 | -0.006535 | 0.001744 |
| 10:20 | regular_residual | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.253292 | 0.247850 | -0.005442 | -0.012699 | 0.001815 |
| 10:20 | regular_residual | cross_instrument_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249182 | 0.247850 | -0.001332 | -0.007533 | 0.004869 |
| 10:20 | remaining_21 | surprise_residual | frozen_parent_residual_history | brier | 230 | 12 | 0.300526 | 0.288655 | -0.011871 | -0.051709 | 0.027966 |
| 10:20 | remaining_21 | stock_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.301752 | 0.286803 | -0.014949 | -0.055471 | 0.025574 |
| 10:20 | remaining_21 | financial_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.299888 | 0.286803 | -0.013085 | -0.056631 | 0.030462 |
| 10:20 | remaining_21 | liquidity_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.299455 | 0.286803 | -0.012651 | -0.053433 | 0.028131 |
| 10:20 | remaining_21 | cross_instrument_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.299056 | 0.286803 | -0.012253 | -0.055840 | 0.031334 |
| 10:20 | remaining_5 | surprise_residual | frozen_parent_residual_history | brier | 244 | 51 | 0.253123 | 0.251934 | -0.001189 | -0.011310 | 0.008932 |
| 10:20 | remaining_5 | stock_residual | frozen_parent_residual_history | brier | 253 | 51 | 0.255428 | 0.250678 | -0.004750 | -0.013614 | 0.004114 |

**The original payoff remains horizon and clock dependent.** The lowest V17 pre-auction 5-session CRPS was **0.010309** from `component_plus_residual` with Brier **0.238003**. The decomposition’s adjusted CRPS gain interval against its same-clock parent was **-0.000319 to +0.001018**. The protected V14 model’s historical weekly Brier was **0.228529**, under its documented guard. The best newly tested 21-session pre-auction Brier was **0.250000** from `neutral`. The protected monthly direction score **0.245042** and V15 GJR return-law CRPS **0.024694** remain important references. The fixed cohorts contain **53 disjoint weekly windows and 11 disjoint monthly windows**.

**Risk evidence depends on how much of the path is already known.** Full weekly GIFT-first barriers retain a strong morning association. Performance changes at D 17:00 and conditioning on day-one survival. New post-open signals have to beat a parent with the known cash prefix and its IV or risk state. Retain favorable and unfavorable paired tests as priorities for genuinely prospective assessment.

Direct stock features were more useful for the remaining session’s volatility than for a persistent direction forecast. Their gains over the native control were small and appeared at several earlier or mid-session clocks.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000959 | 0.000974 | 0.000015 | 6.03e-07 | 0.000029 |
| 09:25 | remaining_vol | stock_direct | native_control | qlike | 257 | 257 | 0.214034 | 0.218998 | 0.004964 | 0.000068 | 0.009860 |
| 09:35 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000917 | 0.000932 | 0.000015 | 1.40e-06 | 0.000029 |
| 09:35 | remaining_vol | stock_direct | native_control | qlike | 257 | 257 | 0.213267 | 0.218011 | 0.004744 | -0.003475 | 0.012964 |
| 11:30 | remaining_vol | stock_direct | native_control | crps | 257 | 257 | 0.000785 | 0.000796 | 0.000011 | 2.16e-06 | 0.000019 |
| 11:30 | remaining_vol | stock_direct | native_control | qlike | 257 | 257 | 0.271647 | 0.273089 | 0.001442 | -0.006087 | 0.008970 |

| horizon | cutoff | screen | candidate | control | metric | n | side barrier cases | candidate loss | control loss | gain | lo21 | hi21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | original | decomposed_gift | same_clock_IV | touch_brier | 265 | 2,650 | 0.132201 | 0.144562 | 0.012360 | 0.004793 | 0.021383 |
| 5 | previous_1700 | original | decomposed_gift | same_clock_IV | touch_brier | 265 | 2,650 | 0.146161 | 0.144562 | -0.001599 | -0.008477 | 0.004842 |

| horizon | cutoff | screen | candidate | control | metric | n | side barrier cases | candidate loss | control loss | gain | lo21 | hi21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 263 | 2,478 | 0.135569 | 0.134899 | -0.000670 | -0.003107 | 0.001345 |
| 5 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 263 | 2,424 | 0.130238 | 0.132186 | 0.001948 | 0.000209 | 0.003805 |
| 21 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 217 | 2,033 | 0.198405 | 0.198510 | 0.000104 | -0.002073 | 0.002290 |
| 21 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 217 | 1,990 | 0.197995 | 0.198789 | 0.000794 | -0.001815 | 0.003274 |

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 10:20 | opening_surprise | cash_risk | abs_error | 263 | 53 | 0.036206 | 0.038821 | 0.002615 | -0.001559 | 0.006789 |
| 5 | 09:25 | opening_surprise | cash_risk | abs_error | 263 | 53 | 0.036117 | 0.038648 | 0.002532 | -0.001499 | 0.006562 |
| 5 | 10:20 | participation | cash_risk | abs_error | 263 | 53 | 0.036545 | 0.038821 | 0.002276 | -0.001893 | 0.006444 |
| 5 | 10:20 | liquidity_disagreement | cash_risk | abs_error | 263 | 53 | 0.036549 | 0.038821 | 0.002272 | -0.001846 | 0.006390 |
| 5 | 09:25 | liquidity_disagreement | cash_risk | abs_error | 263 | 53 | 0.036550 | 0.038648 | 0.002098 | -0.001954 | 0.006150 |
| 5 | 09:25 | participation | cash_risk | abs_error | 263 | 53 | 0.036685 | 0.038648 | 0.001963 | -0.002070 | 0.005997 |
| 5 | 10:20 | option_surface | cash_risk | abs_error | 263 | 53 | 0.036930 | 0.038821 | 0.001890 | -0.002603 | 0.006384 |
| 5 | 09:25 | option_surface | cash_risk | abs_error | 263 | 53 | 0.036875 | 0.038648 | 0.001773 | -0.002631 | 0.006177 |
| 5 | 10:20 | raw_IV | cash_risk | abs_error | 263 | 53 | 0.038682 | 0.038821 | 0.000139 | -0.001486 | 0.001764 |
| 21 | 10:20 | raw_IV | cash_risk | abs_error | 217 | 11 | 0.048986 | 0.049105 | 0.000119 | -0.000455 | 0.000694 |
| 21 | 09:25 | raw_IV | cash_risk | abs_error | 217 | 11 | 0.049015 | 0.049118 | 0.000103 | -0.000434 | 0.000641 |
| 5 | 09:25 | raw_IV | cash_risk | abs_error | 263 | 53 | 0.038688 | 0.038648 | -0.000040 | -0.001633 | 0.001553 |
| 21 | 10:20 | liquidity_disagreement | cash_risk | abs_error | 217 | 11 | 0.050724 | 0.049105 | -0.001619 | -0.004002 | 0.000763 |
| 21 | 09:25 | liquidity_disagreement | cash_risk | abs_error | 217 | 11 | 0.051078 | 0.049118 | -0.001960 | -0.004144 | 0.000224 |
| 21 | 10:20 | opening_surprise | cash_risk | abs_error | 217 | 11 | 0.051193 | 0.049105 | -0.002088 | -0.004488 | 0.000313 |
| 21 | 09:25 | opening_surprise | cash_risk | abs_error | 217 | 11 | 0.051384 | 0.049118 | -0.002266 | -0.004539 | 6.83e-06 |
| 21 | 09:25 | participation | cash_risk | abs_error | 217 | 11 | 0.051888 | 0.049118 | -0.002770 | -0.004926 | -0.000614 |
| 21 | 10:20 | participation | cash_risk | abs_error | 217 | 11 | 0.051952 | 0.049105 | -0.002847 | -0.005225 | -0.000468 |

The research uses a historically eligible stock/ETF basket and NSE announcements. A complete dated index weight history, dated GIFT contract identity, historical executable spreads and actual cash/derivatives order flow remain unavailable in the verified data. Prospective research is separate from the 2025–2026 historical comparisons.

[Model comparison](V17_COMPLETE_MODEL_COMPARISON.md) · [Five- and 21-session detail](V17_WEEKLY_AND_MONTHLY_FORECASTING.md) · [Volatility and conditional paths](V17_VOLATILITY_AND_PATH_INTELLIGENCE.md) · [Forward status](V17_FORWARD_RESEARCH_LEDGER.md)
