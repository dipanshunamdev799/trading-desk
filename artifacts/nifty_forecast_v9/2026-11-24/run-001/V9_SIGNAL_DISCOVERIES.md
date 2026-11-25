# NIFTY V9 · Signal Discoveries

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

1. **Fit history interacts with date.** Matching exactly 85 mature training observations makes later rotation worse instead of better. Later expanding training explains a large component of the gap, with window composition, past outcomes and regime still correlated. The identical-date 300-observation control is stronger than 85, 126, 189 and 252 later. That ordering is not a monotone learning law.
2. **Model risk can be diagnosed more easily than exploited.** Earlier-weekly distance and parameter-uncertainty proxies relate to worse losses, but a selector takes 52 later dates on which the same model actually performs worse than on the dates it would abstain. More uncertain path scale is separate from poor applicability.
3. **Cluster balance and conservative fallback are useful combined-cohort tradeoffs.** A cluster-balanced rotation law improves pooled Brier. Reliability/history shrinkage and the fixed fallback improve pooled CRPS, with no clear earlier superiority and large sacrifice versus later V8 rotation.
4. **Financial divergence, innovation, and panel effects depend on representation and period.** Native market-adjusted finance is meaningful within the larger model. Narrow financial heads and statistical surprises do not reliably beat the matched domestic control in both cohorts. Historical index exposures and public announcement surprises were not identified by these tests.
5. **Global context can change risk estimates without fixing direction.** The earlier volatility MAE gains disappear later and the global reliability gate makes small tradeoffs. Intraday and ETF evidence is guarded by exact V8 reproductions; the wider V9 liquidity law supplies a pooled expert rather than a new standalone edge.
6. **Monthly states and paths are inconclusive.** Slow factors, rank-two multi-horizon learning, historical block paths, and AR blocks change the architecture substantially. None establishes superiority over the strong monthly or historical controls. State-placebo results and disjoint-window limits remain beside all scores.

| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| F_BANK_RESID63 | F_BASE | brier | 92 | 0.005741 |
| F_BANK_RESID63 | F_BASE | crps | 92 | 0.000171 |
| I_AR | I_LEVEL | brier | 92 | -0.011842 |
| I_AR | I_LEVEL | crps | 92 | -0.000404 |
| J9_REL_SHRINK | J9_STATIC | brier | 92 | -0.003880 |
| J9_REL_SHRINK | J9_STATIC | crps | 92 | -0.000019 |
| P_CLUSTER | P_ROT | brier | 92 | -0.026294 |
| P_CLUSTER | P_ROT | crps | 92 | -0.000468 |
| P_ROT | P_NATIVE | brier | 92 | 0.010506 |
| P_ROT | P_NATIVE | crps | 92 | 0.000280 |
| P_STRUCTURE | P_ROT | brier | 92 | -0.001101 |
| P_STRUCTURE | P_ROT | crps | 92 | 0.000388 |
| T_KALMAN | P_COMPACT | brier | 92 | -0.002689 |
| T_KALMAN | P_COMPACT | crps | 92 | -0.000134 |
| X_ROT_PANEL | P_COMPACT | brier | 92 | 0.018761 |
| X_ROT_PANEL | P_COMPACT | crps | 92 | 0.000421 |

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
