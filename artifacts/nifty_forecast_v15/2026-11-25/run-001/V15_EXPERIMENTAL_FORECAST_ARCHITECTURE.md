# V15 experimental forecast architecture

The research pipeline stores 5,882 historical decision records, 152,932 per-law score rows and 2,046,356 eligible first-passage rows. A fixed forecast holds the same outcome and original reference price until maturity. Data alignment and observation, the mathematical distribution, falsification and validation are independently reproducible stages. Decisions preserve timestamps and input revisions.

1. Market state pulls the verified latest cash return, official equal-weight breadth, rotations, liquidity, option-implied levels and international risk observations through the availability audit.
2. The endpoint layer preserves the strongest prior forecasts and produces new same-time restarted, directional shrinkage, normalized return-location and full fitted laws.
3. The volatility layer experiments with earlier ATM IV, forecast tenor, same-horizon history, GJR states, anchored hybrids, EGARCH references and transition recalibration.
4. The conditional path layer joins observed OHLC to complete forecast suffixes, then calculates the endpoint, risk, range, extrema, drawdown, rebound and touch outcomes on the same atoms.
5. The updating layer includes immutable, price-only, risk-only, domestic, full, partial-observation, particle, analogue and lagged/permuted/noisy controls.
6. Scenario research archives explicit price paths, assumptions and case similarity scores independently of forecast weights.
7. Evidence records matched and adjusted skill, data sufficiency, known outcomes, clock receipts, benchmark support and dependence-sensitive uncertainty.

The integrated objects are the 25 new joint OHLC laws per decision and the original frozen V14 joint baseline. Standalone event probabilities, earlier standalone endpoint laws, probability blends, separate point risk fits and the scenario envelope have distinct sources and evaluation. The evidence favors method selection by target where gains survive common-coverage and dependence checks. Model selection in the historical archive remains research-exposed.

[Pre-score joint registrations](registration.json) [Decision and target ledger](update-calendar.csv) [Law archive](joint-update-archive.json) [Fitted model receipts](fitted-update-models.ndjson.gz) [Validation receipts](validation-receipt.json)
