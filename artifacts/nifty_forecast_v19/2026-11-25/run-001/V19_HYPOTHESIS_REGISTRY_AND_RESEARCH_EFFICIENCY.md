# V19 Hypothesis Registry And Research Efficiency

V19 registered 11 primary hypotheses at 2026-11-25T16:25:55.344456+05:30. Each machine-readable record preserves economic rationale, information source, target, forecast cutoff, parent, metric, eligibility, negative control, computational budget and follow-up criteria. Candidate variants were kept to fixed shrinkage rules and specific controls. Positive fit weights support a local standardized association with past errors for a given model residual. Units and contribution depend on the model regularization and training window.

| hypothesis | source | target | primary metric | negative control | follow up |
| --- | --- | --- | --- | --- | --- |
| Participant position levels | NSE participant OI | Original 5 and 21 sessions | Brier and CRPS | Drop dependent Client nets and separate instrument families | Positive matched gains across cohorts |
| Position changes versus levels | Date-verified net balance and gross counts | Original 5 and 21 sessions and rotation | CRPS and paired squared error | One- and five-session delays, then blocked nulls | Matched benefit over levels and OI |
| Position-price innovation | Causal ridge residual with basis, expiry and OHLC state | Original returns and magnitude | CRPS and MAE | Variance normalization alternative and shifted predictors | Stable incremental contribution over raw positions |
| Crowding and contraction proxy | Count-based HHI, training-only ranks and known expiry | Volatility, reversal, future NIFTY futures OI reduction | Brier and QLIKE | Expiry and rollover exclusions, date episodes | Matched effect outside expiry and dominant episodes |
| Delivery activity | Full NSE security-delivery reports and cash archive | Stock-relative and original NIFTY returns | CRPS, Brier and paired stock error | Alternative windows, ex-action screens, and random eligible subsets | Matched gains in more than one cohort |
| Delivery breadth and rotation | NSE delivery and dated native sector indexes | 5- and 21-session sector excess and index returns | MAE, Brier and CRPS | Sector weighting and top-name removal | Sector predictive gains beyond market state |
| Large deals | NSE historical bulk and block windows | Issuer relative returns, sector rotation and index risk | Paired excess return and CRPS | Date shifts, exact duplicate and size exclusions | Event and parent comparison beyond matched turnover |
| Institutional cash activity | Official dated source only | 5- and 21-session original returns and risk | Brier, CRPS and QLIKE | Verify arithmetic and test chronological delay | Estimable matched increments and coverage |
| Fundamental and position interaction | V18 published fundamentals and genuine positioning measurements | Original 5 and 21 sessions | Brier and CRPS | Alternative addition orders, block rotation and delayed inputs | Increment through both addition orders and comparable cohorts |
| Native and decomposition residuals | Exact V14/V18 weighted laws and V17 decomposition | Original endpoint distributions | Brier and CRPS | Neutral correction, empirical shape and episode omissions | Positive adjusted directional and distribution evidence |
| Positioning-informed risk laws | Audited positioning, delivery and risk states | Point volatility, transitions, range and barrier risks | MAE, QLIKE, CRPS and Brier | Delay, expiry exclusions and comparison to IV-only | Improvement in coherent laws or clearly labeled standalone forecasts |

| feature | fits | mean standardized coefficient | median standardized coefficient | positive share |
| --- | --- | --- | --- | --- |
| FII_index_futures_d21 | 159 | -0.006469 | -0.007695 | 0.081761 |
| Pro_index_futures_level | 159 | 0.005047 | 0.005425 | 1.000000 |
| index_futures_detail_hhi_z | 159 | 0.004131 | 0.004807 | 1.000000 |
| DII_index_futures_level | 159 | -0.003971 | -0.004627 | 0.050314 |
| FII_index_futures_level | 159 | -0.004008 | -0.004421 | 0.000000 |
| index_calls_disagree | 159 | 0.003339 | 0.003479 | 1.000000 |
| index_futures_disagree | 159 | 0.003136 | 0.003438 | 0.993711 |
| DII_index_futures_d5 | 159 | 0.002511 | 0.002690 | 0.905660 |
| innovation_dii | 159 | 0.002255 | 0.002232 | 0.911950 |
| FII_index_futures_d5 | 159 | -0.001200 | -0.001273 | 0.000000 |

The monthly native candidate is the strongest follow-up hypothesis. Weekly native participant correction, the extra rebuilt monthly directions, the direct risk candidates against protected point models, ambiguous transactions and broad daily generalizations are all tracked in the failed or indeterminate cells.

[registration.json](registration.json) · [native-positioning-weight-summary.csv](native-positioning-weight-summary.csv) · [native-positioning-fits.ndjson.gz](native-positioning-fits.ndjson.gz) · [native-mechanism-summary.csv](native-mechanism-summary.csv) · [native-refit-null-summary.csv](native-refit-null-summary.csv) · [model-leaderboards.csv](model-leaderboards.csv) · [matched-comparisons.csv](matched-comparisons.csv)
