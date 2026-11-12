# Performance metrics and capital feasibility

306 accepted adverse-first candle-proxy rows, 48 exit/contract configurations, 384 capital/risk scenarios. No winner selected.

Net expectancy, profit factor, average win/loss, realized reward/loss ratio, worst trade, consecutive losses, monthly outcomes, closed-trade drawdown and recovery duration are exported for every configuration. Profit factor is null when no losses occurred, with a status explaining that finite expectancy is not established. Curve reference capital INR250000 is illustrative, not a capital recommendation.

Risk fractions0.25%/0.5%, daily loss gate1%, weekly3% and one simultaneous position are hypotheses from the brief. Whole-lot/cash affordability can cause abstention. Gates act after losses are observed; gaps, missing exits and loss of the full premium can exceed a planned stop and daily limit. Position sizing cannot repair negative expectancy.

No-stop time exits reserve full premium at risk. Defined stops reserve planned loss plus a severe execution allowance; the separate full-premium scenario shows remaining exposure. Capital is fixed for risk budgeting; profits do not increase that budget. No averaging, martingale or doubling is implemented.

Monte Carlo resamples observed daily PnL blocks2000times. It measures uncertainty conditional on only five recent sessions. It is not an estimate of real-world ruin or future risk-limit-breach probability. Full-premium shocks are deterministic stress cases, not assigned empirical frequencies.

Intratrade equity and tick-level MAE/MFE are unsupported by these candle tests. Candle MAE/MFE bounds are provided by exit-trades.csv; cash/percentage drawdown here is measured at closes and can understate mark-to-market losses. Order failure frequency cannot be estimated from simulations; proxy coverage rejection rates are not broker rejection rates.

Outputs: metrics-leaderboard.csv,risk-feasibility.csv,risk-trades.csv,equity-curves.csv,monthly-performance.csv,monte-carlo.json. Account returns remain hypothetical, with asynchronous price proxies and illustrative costs. Historical, forward and execution gates remain unmet.