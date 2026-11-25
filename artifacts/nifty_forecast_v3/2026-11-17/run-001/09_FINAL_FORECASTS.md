# 09 — Final as-of research scenarios: NOT VALIDATED

**NOT A FRESH PREMARKET FORECAST.** Issued 2026-11-17T09:55:34.610340+05:30 after the 17 November
session had already opened. Reference=25,291.10, completed
session=2026-11-16, source bar timestamp=2026-11-16T00:00:00+05:30
(a session anchor, not proof of publication time). Actual latest acquisition=
2026-11-17T09:31:39.461160+05:30. Intended model
clock=00:30 IST following the completed session. No 17 November intraday prices
enter the feature panel. The first target session is already in progress.
This is a late-issued, revised-vintage as-of reconstruction, not fresh confirmation.

All numeric estimates below carry **NOT VALIDATED** status. No production or
trading-qualified model was found. The full machine record contains source/model
versions, probabilities, seven return buckets, baselines, policy and fixed-model
OOS scores, calibration/coverage histories, effective samples and unresolved outcomes.

## Week — 5 sessions, expected endpoint 2026-11-23

- Direction model: M05_lgbm; raw upward estimate
  72.37%, nonpositive 27.63%.
  This is not a historically calibrated or independently validated probability.
- Direct mean-return model: A01_nofo; point estimate
  +1.200%; endpoint 25,594.63.
- Distribution model: A01_nofo; median return
  -0.027%, endpoint 25,284.24.
- Nominal 50% interval: 24,969–25,657;
  nominal 80%: 24,823–26,332. Coverage of that distribution-selector policy
  was 45.7%/64.1%, not 50/80%.
- Volatility model: B03_vix_scaled; annualized point
  15.68%; sqrt-time move proxy
  2.21%. These are not validated expected-risk guarantees.
- Tail model: M05_lgbm; daily-close path-breach estimates
  below-2% 8.77%, below-5%
  0.44%.
- Seven endpoint bucket probabilities: {"below_-5pct": 0.0, "-5_to_-2pct": 0.0945, "-2_to_-0.5pct": 0.2886, "-0.5_to_+0.5pct": 0.2139, "+0.5_to_+2pct": 0.1642, "+2_to_+5pct": 0.1692, "above_+5pct": 0.0697}.
- Bullish/neutral/bearish scenarios use endpoint returns above+.5%, within±.5%,
  below-.5%. Distribution scenario estimates: {"bearish": 0.3831, "neutral": 0.2139, "bullish": 0.403}.
- Direction-selector OOS: n=92, accuracy=63.04%,
  Brier=0.25612; 19 disjoint
  windows and outcome-ACF ESS=23.45.
- Cross-target inconsistency: classifier P(up)=72.37%
  versus distribution-implied 49.75%.
  These independently selected targets do not form a calibrated coherent joint forecast.
- Main feature associations are training-only coefficients/gain in
  model-contributions.json; no contributing family has established independent
  incremental predictive importance. Future latent regime is NOT VALIDATED.

## Month — 21 sessions, expected endpoint 2026-12-16

- Direction model: Z_momentum; raw upward estimate
  55.00%, nonpositive 45.00%.
  This is not a historically calibrated or independently validated probability.
- Direct mean-return model: A00_sector; point estimate
  +1.225%; endpoint 25,600.80.
- Distribution model: A00_sector; median return
  -1.990%, endpoint 24,787.93.
- Nominal 50% interval: 24,330–25,935;
  nominal 80%: 23,800–26,939. Coverage of that distribution-selector policy
  was 10.5%/31.6%, not 50/80%.
- Volatility model: M00_ridge_price; annualized point
  7.32%; sqrt-time move proxy
  2.11%. These are not validated expected-risk guarantees.
- Tail model: B01_ewma; daily-close path-breach estimates
  below-2% 59.39%, below-5%
  19.66%.
- Seven endpoint bucket probabilities: {"below_-5pct": 0.1891, "-5_to_-2pct": 0.2886, "-2_to_-0.5pct": 0.1891, "-0.5_to_+0.5pct": 0.0697, "+0.5_to_+2pct": 0.0, "+2_to_+5pct": 0.0995, "above_+5pct": 0.1642}.
- Bullish/neutral/bearish scenarios use endpoint returns above+.5%, within±.5%,
  below-.5%. Distribution scenario estimates: {"bearish": 0.6667, "neutral": 0.0697, "bullish": 0.2637}.
- Direction-selector OOS: n=76, accuracy=60.53%,
  Brier=0.24220; 4 disjoint
  windows and outcome-ACF ESS=5.96.
- Cross-target inconsistency: classifier P(up)=55.00%
  versus distribution-implied 28.36%.
  These independently selected targets do not form a calibrated coherent joint forecast.
- Main feature associations are training-only coefficients/gain in
  model-contributions.json; no contributing family has established independent
  incremental predictive importance. Future latent regime is NOT VALIDATED.

Exact target session dates use the saved published NSE calendar. Unexpected
closures or missing candles require review. Means/medians can disagree, but the
size of these cross-target disagreements plus undercoverage is a reason to reject
precise forecast interpretation. The JSON does not suppress these inconsistencies.
All outcomes are unresolved. A genuinely fresh next premarket freeze requires
the 17 November completed session and its authenticated newly available inputs,
which did not exist at this research execution cutoff. No watcher was scheduled.
