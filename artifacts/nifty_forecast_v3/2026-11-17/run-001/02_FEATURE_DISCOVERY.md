# 02 — Feature discovery and availability

The dataset has 402 eligible origins, 2025-04-02 through
2026-11-16, and 129 features. No value or indicator initialization before
2025-01-01 was used. Native index/ETF data, 465 dated official FO sessions, complete
prior-session intraday summaries and six conservatively lagged global series
replace the earlier restriction to 71 indicators.

|family|features|median missing|classification|
|---|---|---|---|
|calendar|1|0.0%|usable with explicit limitations|
|etf|3|0.0%|usable with explicit limitations|
|fo|14|0.0%|usable with explicit limitations|
|global|18|0.0%|usable with explicit limitations|
|institution|9|61.4%|usable with explicit limitations|
|interaction|4|0.0%|usable with explicit limitations|
|intraday|5|0.7%|usable with explicit limitations|
|price|21|0.0%|usable with explicit limitations|
|proxy|12|0.0%|research-only current-basket proxy|
|risk|4|0.0%|usable with explicit limitations|
|sector|26|0.0%|usable with explicit limitations|
|sequence|12|0.0%|usable with explicit limitations|

The 12 current-member-basket features are research-only. No historical NIFTY
constituent membership or index-weight reconstruction was recovered for the full
period. Only A02_proxy uses them; they are excluded from all primary selectors.
Stock breadth is not silently relabeled genuine historical index participation.
ETF volume is real; NIFTY spot volume remains zero. No spot VWAP was invented.

FO features include nearest non-expired futures basis, relative OI change,
same-contract/lot OI log change, explicit roll indicator, DTE, log OI/volume PCR,
call/put OI concentration, wall distances, max-pain distance and matched-contract
PCR change. Roll/lot changes do not create synthetic OI increments. Contract IDs
are metadata, never numeric predictors. FO and institutional inputs have an
extra domestic-session publication lag. Historical IV/Greeks were not fabricated.

Development-only discovery uses labels matured before 2026-07-01: 238 eligible
feature/horizon IC tests, 200 temporal circular-shift nulls per test, BH adjustment,
2,261 monthly univariate OOS folds, MI representatives versus 20 shifted nulls,
and 30 temporal-block ElasticNet stability fits per horizon. These diagnostics
do not select features on the final outer period.

Lowest adjusted q-value is 0.2960; **zero features pass BH q<.05**.
Monthly ETF volume/turnover has rank IC near +.263 and stable positive half-sample
signs, but adjusted q near .296. VIX change and sector participation show
conditional associations, not validated independent information.

|horizon|feature|rank_ic|first_half_ic|second_half_ic|bh_q|
|---|---|---|---|---|---|
|21|etf_relative_turnover|0.2628|0.1724|0.3537|0.296|
|21|etf_relative_volume|0.2634|0.1729|0.3647|0.296|
|21|sequence_sector_participation_lag1|-0.1911|-0.0591|-0.4362|0.3947|
|21|risk_vix_change5|0.2302|0.2748|0.2445|0.4736|
|21|sector_nifty_it_rel5|0.2369|-0.0902|0.5567|0.4736|
|21|sector_participation|-0.2112|-0.0813|-0.462|0.4934|
|21|sequence_sector_participation_lag3|-0.1795|-0.0461|-0.3899|0.5075|
|21|global_dow_ret5|-0.1598|-0.2266|-0.1086|0.5382|
|21|proxy_above_ema5|-0.1982|-0.0926|-0.4248|0.5382|
|21|global_usdinr_rv21|-0.2513|-0.0747|-0.1636|0.5382|
|21|sequence_sector_participation_lag5|-0.1683|-0.0124|-0.3663|0.5382|
|21|sector_nifty_auto_rel5|-0.2252|-0.1511|-0.4078|0.5465|

Full results: development-feature-information.csv, development-univariate-oos.csv,
development-mutual-information.json, development-stability-selection.csv and
feature-definitions.json. Linear full-context minus FO/FII is a **joint block**
ablation; it cannot identify which individual derivative variable causes a change.
Associations, coefficient stability and tree gain are not causal effects.
