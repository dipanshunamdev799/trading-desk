# 05 — Validation, leakage and uncertainty audit

History strictly 2025-01-01 through 2026-11-16. First feature origin is
2025-04-02 after 63-session warmup inside the permitted period.
No pre-2025 trained state is imported. All dates were already research-exposed
by previous studies: **no historical split is called untouched confirmation**.

Monthly chronological refits use only matured endpoints plus one-session embargo.
The latest42 eligible origins form inner validation. Inner fitting purges any
label whose endpoint reaches that inner period. Inner training must have80 labels,
and outer fitting at least126 matured labels; this necessarily delays the first
monthly development forecast. Targets independently choose configurations using
inner Brier, MAE, CRPS, QLIKE or tail Brier. Outer stress origins begin2026-07-01.
Scaling, imputation, correlation pruning, risk thresholds and selective-forecast
thresholds are training-only. Provider-launch missingness indicators are not used.

Weekly outer evaluation has 92 overlapping origins, 19 non-overlapping windows
and outcome-autocorrelation ESS about23.45. Monthly has 76 origins, four disjoint
windows and ESS about5.96. Neither count guarantees independence. Monthly paired
intervals are withheld: 76<168 required origins for the prespecified 42-session
block. Weekly blocks have10 sessions and 2,000 resamples. Simultaneous intervals
span 170 model/policy-and-target contrasts; **none has a positive lower bound**.
The strongest fixed baseline is identified on outer data and marked postselected;
inner-only baseline selectors are also reported and can themselves overfit.

15 focused tests passed. They check source/data hashes,
unchanged old calls, exact fitted-source archive, rejection of pre-2025 values,
registered future-oracle availability and unregistered future columns, unfinished
labels, inner purging, future-source/target perturbation invariance, cached feature
reproduction, representative model reproduction, horizon labels, proxy exclusion,
non-overlap, official FO identity/date checks, zero index volume, partial intraday
rejection and withholding unsupported monthly confidence intervals.

Six independently randomized-direction controls show no positive direction skill:
weekly Brier approximately .3359/.2840/.3575 and monthly .3448/.2809/.3285,
all worse than neutral .25. One randomized weekly accuracy is 54.9%; that isolated
accuracy does not create proper-score skill. Temporal-shift nulls are additionally
used in development feature discovery. Volatility is deliberately not randomized
in the direction controls and no claim is made that they test every target.

Hardening amendment: schema/time checks, explicit exclusion of a parsed contract
ID from numerical features and invalid-intraday-day checks were added after the
first batch. This is disclosed, not hidden as original pre-registration. Exact
initial fit code is archived in source-at-first-fit; tests confirm exact cached
features and representative ridge/LightGBM predictions are numerically unchanged.
No parameter/model selection changed. guard-amendment.json and verification.json
record this. Current source and exact fitted source are separately traceable.

Historical publication clocks and vendor revision vintages remain assumptions.
One extra session lag for FO/FII and conservative global joins reduce timing risk
but cannot manufacture an as-delivered archive. Current-basket proxy results are
ineligible for primary claims. Any apparent improvement remains conditional on
those source limitations.
