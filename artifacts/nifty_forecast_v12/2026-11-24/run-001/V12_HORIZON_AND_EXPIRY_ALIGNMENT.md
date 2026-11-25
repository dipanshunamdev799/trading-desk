# V12 Horizon And Expiry Alignment

Planned endpoints use the published weekday, holiday and special-session schedule as known at each cash origin. Actual endpoint dates are independently retained from the frozen label calendar. The main option selection takes the nearest listed future expiry to the *planned* 5- or 21-session endpoint from a previous completed source date. The naturally aligned diagnostic is scored only when the selected expiry also equals the actual endpoint, and uses the quoted absolute-strike law divided by the later origin’s cash close. A longer-expiry variant requires an expiry at least four calendar days farther out than planned. [2025 NSE calendar](https://nsearchives.nseindia.com/content/circulars/CMTR65587.pdf) · [2026 NSE calendar](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf) · [Observed 2026 budget-session notice](https://nsearchives.nseindia.com/content/circulars/CMTR72349.pdf).

For bracketing expiries the interpolation operates on total variance and requires a non-decreasing pair. A missing or inverted bracket receives a flag, and the strict bracket comparison uses paired eligible dates. Approximate priced laws recenter the observed forward and scale log-strike shape by the square-root calendar tenor ratio. This explicitly reuses a different maturity shape and gives no model-free identification at the desired endpoint. Bracketing supplies a volatility measure only.

| horizon | version | queries | valid_iv | valid_density | exact_listed_actual | planned_equals_actual | bracketed_monotone | median_abs_gap_days | p90_abs_gap | nonmonotone_brackets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | BRACKET | 265 | 264 | 0 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | FUTURE_FORWARD | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | LAG2 | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | LAG5 | 265 | 265 | 263 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | LIQUID | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | LONGER | 265 | 265 | 262 | 0 | 263 | 264 | 6.000000 | 8.000000 | 0 |
| 5 | NATURAL | 265 | 55 | 55 | 55 | 263 | 55 | 0.000000 | 0.000000 | 0 |
| 5 | RATE_HIGH | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | RATE_ZERO | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | SAME_CLOSE | 265 | 265 | 265 | 55 | 263 | 228 | 1.000000 | 3.000000 | 0 |
| 5 | SETTLEMENT | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | SMOOTH | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | TRADE | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 5 | TRUNCATED | 265 | 265 | 265 | 55 | 263 | 264 | 1.000000 | 3.000000 | 0 |
| 21 | BRACKET | 217 | 217 | 0 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |
| 21 | FUTURE_FORWARD | 217 | 217 | 199 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |
| 21 | LAG2 | 217 | 217 | 200 | 15 | 203 | 217 | 4.000000 | 8.400000 | 0 |
| 21 | LAG5 | 217 | 217 | 210 | 11 | 203 | 217 | 7.000000 | 10.400000 | 0 |
| 21 | LIQUID | 217 | 217 | 208 | 11 | 203 | 217 | 7.000000 | 10.000000 | 0 |
| 21 | LONGER | 217 | 205 | 199 | 1 | 203 | 205 | 15.000000 | 27.000000 | 0 |
| 21 | NATURAL | 217 | 21 | 17 | 20 | 203 | 21 | 0.000000 | 0.000000 | 0 |
| 21 | RATE_HIGH | 217 | 217 | 199 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |
| 21 | RATE_ZERO | 217 | 217 | 199 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |
| 21 | SAME_CLOSE | 217 | 217 | 200 | 27 | 203 | 217 | 2.000000 | 7.000000 | 0 |
| 21 | SETTLEMENT | 217 | 217 | 194 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |
| 21 | SMOOTH | 217 | 217 | 199 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |
| 21 | TRADE | 217 | 217 | 199 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |
| 21 | TRUNCATED | 217 | 217 | 193 | 20 | 203 | 217 | 3.000000 | 8.000000 | 0 |

The table’s `valid_density` column measures usable curves at the forecast-time expiry choice. Scoring the `NATURAL` diagnostic additionally requires that the actual trading-session endpoint matches that expiry, leaving **55 weekly** and **16 monthly** origins, with **43** and **7** non-overlapping windows respectively. The December 26, 2025 forecast used the January 27, 2026 expiry, which matched the planned 21-session endpoint. The subsequently announced January 15 market holiday moved the actual endpoint to January 28, making that expiry ineligible for exact-match scoring. [Matched scores](V12_EXPECTATION_VS_REALITY.md) · [January 15 market holiday notice](https://nsearchives.nseindia.com/content/circulars/CMTR72260.pdf).

[Origin-by-origin dates including planned, actual, shorter and longer expiry](horizon-alignment.csv) · [Earlier and later coverage](alignment-coverage.csv) · [Calendar notices](calendar-audit.json).
