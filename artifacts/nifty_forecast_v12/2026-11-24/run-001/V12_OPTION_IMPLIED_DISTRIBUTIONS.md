# V12 Option Implied Distributions

V12 estimates an expiry forward using the median of up to 13 liquid near-money put-call-parity pairs. Call minus put over the discount factor plus strike gives the individual forwards. The same-expiry native futures contract is an audit and an alternative anchor where it exists. The central synthetic discount is 6% annual continuous with 0% and 9% sensitivities. A matched bank funding series and dividend schedule were unavailable. An option forward or cash–futures basis also contains carry and market frictions. There are **1,084** accepted main date-expiries with a traded corresponding future. The median absolute future–parity gap is **2.19 basis points** of the parity forward.

The Black-76 inversion works in forward units, uses the traded out-of-money side, rejects prices outside model bounds, checks two-sided coverage, and records the ATM, put/call, skew and curvature measures. An ATM-only lognormal is an explicit diagnostic fallback rather than a reconstructed smile. A Breeden–Litzenberger-style finite-difference procedure estimates vertical-spread probabilities, smooths and projects them to a non-increasing [0, 1] curve, differences to nonnegative interior mass, and treats the boundary mass as extrapolated. Two exterior atoms use bounded endpoint-premium extrapolation. A small exponential reweighting enforces the forward moment. The price-fit, support and mass-movement tests reject unreliable surfaces. The accepted law fits priced **risk-neutral** information. Atoms outside the observed strike region carry an explicit flag and their exact tails are unidentified. [Breeden and Litzenberger](https://doi.org/10.1086/296025).

| method | date-expiries | accepted IV | valid strike IV | attempted strike IV | accepted density | median ATM IV | median outside mass | median price RMSE (bp of forward) | q10 outside support count | q90 outside support count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FUTURE_FORWARD | 2799 | 2559 | 208868 | 208868 | 2469 | 0.123714 | 0.020689 | 0.690745 | 65 | 36 |
| LIQUID | 2799 | 2239 | 164854 | 164854 | 2169 | 0.123694 | 0.022603 | 0.432194 | 36 | 24 |
| RATE_HIGH | 2799 | 2559 | 208870 | 208870 | 2468 | 0.123955 | 0.020630 | 0.668967 | 66 | 37 |
| RATE_ZERO | 2799 | 2559 | 208867 | 208867 | 2470 | 0.123054 | 0.020777 | 0.665895 | 65 | 37 |
| SETTLEMENT | 2799 | 2559 | 208812 | 208812 | 2448 | 0.123665 | 0.018961 | 1.317128 | 62 | 37 |
| SMOOTH | 2799 | 2559 | 208870 | 208870 | 2468 | 0.123649 | 0.023952 | 1.058982 | 77 | 56 |
| TRADE | 2799 | 2559 | 208870 | 208870 | 2468 | 0.123649 | 0.020712 | 0.670840 | 65 | 35 |
| TRUNCATED | 2799 | 2559 | 208870 | 208870 | 2429 | 0.123649 | 0.077178 | 0.390109 | 112 | 69 |

The strike IV counts use the priced out-of-money strikes that passed the initial liquidity, parity and moneyness screens. The accepted-IV and accepted-density counts use all tested date-expiries as their denominator. The tighter volume screen, settlement marks, two alternate rates, actual-futures anchor, denser smoothing and narrower strike truncation rerun identical date-expiry candidates with separate coverage. The archived exercise prices, signed slopes, strike IVs, density masses and boundary flags are reproducible. [Expiry/shape quality and rejections](surface-quality.csv) · [Per-strike Black IV](strike-implied-volatility.csv.gz) · [Accepted priced laws](option-density-atoms.npz).

![Observed option marks, fitted curve and extrapolated priced tails](C:/Users/ME/Desktop/trading-desk/artifacts/nifty_forecast_v12/2026-11-24/run-001/option-curve-check.png)
