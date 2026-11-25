# V15 research conclusions

Forecasts improved as newly realized price moved the current anchor toward the original endpoint. The most consistent evidence is for updating what is already known and for explicitly targeting risk. Additional regressions must improve the same-time control. Direction, residual returns, volatility, range, and time-to-event conclusions answer separate questions, with monthly inference constrained by **11** greedily disjoint windows. At weekly issue, the delayed-plus-noise placebo scored Brier 0.246351, ahead of the best substantive new weekly model. No independent directional edge is established by the frozen 2025–2026 replay.

## Original weekly and monthly direction and CRPS

| horizon | original brier model | original brier | protected v14 brier | original crps model | original crps | protected v14 crps |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | full | 0.247450 | 0.228529 | iv_restart | 0.010682 | 0.010457 |
| 21 | heavy_tail | 0.247524 | 0.245042 | gjr_restart | 0.024694 | 0.024750 |

## Mechanical progress versus prediction of the remaining return

| horizon | checkpoint | frozen brier | price only brier | raw iv brier | raw iv remaining brier | raw iv remaining crps |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 0 | 0.252084 | 0.248408 | 0.248408 | 0.248408 | 0.010682 |
| 5 | 4 | 0.252084 | 0.097616 | 0.097811 | 0.247583 | 0.004652 |
| 21 | 0 | 0.253372 | 0.247721 | 0.247721 | 0.247721 | 0.025027 |
| 21 | 20 | 0.253372 | 0.043775 | 0.044056 | 0.247910 | 0.005097 |

## 25% expansion and honest same-vintage controls

| horizon | historical brier | raw iv brier | best model | best brier | raw iv log loss | best log loss | raw iv gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.222296 | 0.155657 | fixed_75IV25RV | 0.152707 | 0.466192 | 0.461636 | 0.002949 | -0.009143 | 0.015042 |
| 21 | 0.299434 | 0.186036 | V14_EGARCH_t | 0.172872 | 0.829771 | 0.689982 | 0.013164 | -0.074974 | 0.101302 |

The clearest timestamp-specific return result was the immediate NIFTY opening gap. On 258 common mornings, the offshore block moved Brier from 0.265168 to 0.227947. The 21-session family interval for this gain was [0.003563, 0.070877]. This is a distinct intraday target and diagnostic reconstruction with conservative release assumptions. Sector, breadth, derivatives and foreign revisions produce varying results at the original endpoint. Same-time changes to risky paths can help range, risk, and timing scores without enhancing the original directional probability.

## Best post-issue matched point estimates and uncertainty

| horizon | metric | candidate | n | model | control | gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | domestic | 265 | 0.159648 | 0.162131 | 0.002484 | -0.007784 | 0.012752 |
| 5 | brier | refit | 265 | 0.160464 | 0.162131 | 0.001667 | -0.008631 | 0.011965 |
| 5 | range_crps | vol_only_shock | 265 | 0.004152 | 0.004173 | 0.000021 | -0.000037 | 0.000079 |
| 5 | range_crps | incremental | 265 | 0.004161 | 0.004173 | 0.000012 | -0.000094 | 0.000117 |
| 5 | remaining_return_crps | vol_only_shock | 265 | 0.007251 | 0.007255 | 0.000003 | -0.000015 | 0.000021 |
| 5 | remaining_return_crps | heavy_tail | 265 | 0.007255 | 0.007255 | -0.000001 | -0.000007 | 0.000006 |
| 5 | vol_mae | derivatives_first | 265 | 0.022626 | 0.023477 | 0.000851 | -0.001039 | 0.002741 |
| 5 | vol_mae | domestic | 265 | 0.022649 | 0.023477 | 0.000828 | -0.000783 | 0.002440 |
| 21 | brier | vol_only_shock | 217 | 0.166696 | 0.166627 | -0.000069 | -0.000557 | 0.000418 |
| 21 | brier | heavy_tail | 217 | 0.166699 | 0.166627 | -0.000072 | -0.000255 | 0.000111 |
| 21 | range_crps | incremental | 217 | 0.009803 | 0.010019 | 0.000216 | -0.000160 | 0.000592 |
| 21 | range_crps | vol_state | 217 | 0.009947 | 0.010019 | 0.000072 | -0.001045 | 0.001189 |
| 21 | remaining_return_crps | vol_only_shock | 217 | 0.016995 | 0.017010 | 0.000016 | -0.000034 | 0.000066 |
| 21 | remaining_return_crps | vol_state | 217 | 0.017001 | 0.017010 | 0.000009 | -0.000311 | 0.000330 |
| 21 | vol_mae | incremental | 217 | 0.017856 | 0.018871 | 0.001015 | -0.001020 | 0.003050 |
| 21 | vol_mae | vol_state | 217 | 0.018007 | 0.018871 | 0.000864 | -0.003776 | 0.005504 |

## Surviving first-passage time forecasts

| horizon | candidate | n | origins | candidate loss | reference loss | average episode gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | hybrid | 15,430 | 265 | 0.060308 | 0.060591 | 0.000181 | -0.000772 | 0.001135 |
| 5 | particle | 15,430 | 265 | 0.060450 | 0.060591 | -0.000043 | -0.001288 | 0.001202 |
| 21 | vol_state | 54,600 | 217 | 0.072209 | 0.072306 | -0.000134 | -0.002162 | 0.001895 |
| 21 | shock_persistence | 54,600 | 217 | 0.072494 | 0.072306 | -0.000183 | -0.000949 | 0.000584 |

The historical error casebook and scenario tests map important failure modes and the limited independent tail evidence. The same-target replay and conditional path tools are reproducible, with separated point-risk, event, joint path and standalone endpoint evidence. Further prospectively timestamped comparisons are the required test for realized research gains.

[Complete model comparison](V15_COMPLETE_MODEL_COMPARISON.md) [Episode sensitivity](V15_EPISODE_LEVEL_EVALUATION.md) [Immutable forward ledger](V15_FORWARD_RESEARCH_LEDGER.md) [Historical illustrative case](historical-fixed-endpoint-updates.png)
