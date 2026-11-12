# Benchmarks and historical expansion diagnosis

All earlier research is preserved. The benchmark design was written before these calculations. This is a small controlled diagnosis: two fixed signal controls and 20 frozen random seeds, not another indicator search. There were 176 original-model executions and 44 audit-corrected replays. The calendar is already contaminated by earlier project research.

## Published total-return indices

| index | stage | total_return_pct | max_drawdown_pct | sharpe |
| --- | --- | --- | --- | --- |
| Nifty 50 | development | 6.8813 | 10.6327 | 0.6060 |
| Nifty 50 | validation | -5.0117 | 15.0823 | -0.5880 |
| Nifty 50 | final | 4.4916 | 10.2093 | 0.7437 |
| Nifty 50 | two_year | 6.0848 | 15.0823 | 0.2901 |
| Nifty 500 | development | 4.9216 | 14.7276 | 0.4248 |
| Nifty 500 | validation | -1.5289 | 14.6915 | -0.1021 |
| Nifty 500 | final | 2.6517 | 9.8748 | 0.4764 |
| Nifty 500 | two_year | 6.0572 | 14.7276 | 0.2802 |
| Nifty Bank | development | 13.1403 | 10.7261 | 1.0103 |
| Nifty Bank | validation | -4.4340 | 18.3189 | -0.3654 |
| Nifty Bank | final | 8.7200 | 7.6171 | 1.1858 |
| Nifty Bank | two_year | 17.5522 | 18.3189 | 0.6035 |
| Nifty IT | development | -14.4375 | 28.8967 | -0.6381 |
| Nifty IT | validation | -15.7060 | 27.2736 | -1.2867 |
| Nifty IT | final | 11.5330 | 17.1829 | 0.9098 |
| Nifty IT | two_year | -19.5579 | 42.0016 | -0.3377 |
| Nifty Pharma | development | -0.9587 | 15.6970 | 0.0241 |
| Nifty Pharma | validation | 9.0188 | 7.5194 | 1.2456 |
| Nifty Pharma | final | 20.2745 | 6.8306 | 2.7865 |
| Nifty Pharma | two_year | 29.8648 | 15.6970 | 0.9333 |

**Verified fact:** these are official observed total-return index levels, including dividend reinvestment under the publisher methodology. They are not price-index substitutes. Each comparison uses the last published close before the segment start as its base. Fully invested index exposure is 100%; ETF costs, replicating turnover, capacity and investor tax are not inferred from the index.

**Statistical observation:** the final six months contained a particularly strong pharmaceutical-sector rally (+20.2745%), while the full two years showed a large difference between Pharma (+29.8648%) and IT (−19.5579%). This is relevant context for the prior historical Pharma stock winners. It does not prove that selecting Pharma in advance would have produced an independent strategy edge. Only Bank, IT and Pharma sector benchmarks were acquired; these do not cover every sector.

## Same-assumption stock buy-and-hold

| stage | dividend_model | total_return_pct | max_drawdown_pct | sharpe | average_invested_nav_pct | two_sided_turnover_capital_multiple |
| --- | --- | --- | --- | --- | --- | --- |
| development | original_dividends | 0.9444 | 20.8055 | 0.1415 | 97.2665 | 1.9558 |
| validation | original_dividends | 1.1993 | 15.0752 | 0.2256 | 93.9738 | 1.9038 |
| final | original_dividends | -1.7390 | 11.4551 | -0.1824 | 96.0480 | 1.9072 |
| two_year | original_dividends | 2.1786 | 20.8055 | 0.1492 | 96.8917 | 1.9586 |
| development | corrected_multicomponent_dividends | 0.9711 | 20.8016 | 0.1431 | 97.2540 | 1.9558 |
| validation | corrected_multicomponent_dividends | 1.2043 | 15.0703 | 0.2261 | 93.9709 | 1.9038 |
| final | corrected_multicomponent_dividends | -1.7281 | 11.4534 | -0.1808 | 96.0409 | 1.9072 |
| two_year | corrected_multicomponent_dividends | 2.2188 | 20.8016 | 0.1504 | 96.8695 | 1.9586 |

**Verified fact:** the original buy-and-hold results reproduced. Replaying the audited multi-component dividend fixes changes full two-year return from +2.1786% to +2.2188% and final return from −1.7390% to −1.7281%. Original buy-hold is reproduced to floating precision, and independently instrumented NAV matches its day-by-day values within ₹1e−8. Same-day statutory-tax fixes are immaterial to this carried buy-hold control; it is not a sequence of intraday round trips.

This control starts separate ₹10 lakh accounts, buys once at the first qualifying open subject to the same lagged liquidity/volume capacity and fees, retains idle cash, accrues cash dividends economically on ex-date, adjusts modeled splits and liquidates at the terminal close. It does not reinvest dividends or reconstitute membership. Corrected two-year average invested NAV was 96.87%, with two-sided turnover 1.9586 times initial capital and mean fees ₹2,249.06 per stock account. The equal-capital dated stock cohort is different from a capitalization-weighted reconstituted TRI, so their return difference is not an alpha estimate.

## Simple signal controls under the original risk/exit wrapper

| control | stage | total_return_pct | max_drawdown_pct | sharpe | exposure_pct | n_trades | two_sided_turnover_capital_multiple |
| --- | --- | --- | --- | --- | --- | --- | --- |
| simple_trend_ema200 | final | -0.3409 | 0.5173 | -1.5302 | 46.1049 | 3425 | 1.1127 |
| simple_trend_ema200 | two_year | -1.4174 | 1.6662 | -1.5262 | 45.2040 | 12833 | 4.2360 |
| simple_momentum60 | final | -0.3760 | 0.5602 | -1.4279 | 52.5163 | 3810 | 1.2408 |
| simple_momentum60 | two_year | -1.4258 | 1.5890 | -1.4339 | 47.1623 | 13257 | 4.3849 |

Control definitions were fixed: (1) completed close above SMA-seeded EMA 200, or (2) positive preceding 60-session stock return. Both use next-open entries, the original 2 ATR stop, fee-aware 2R target, 10-session holding cap, 0.5% initial cash risk, 1% lagged-volume cap and baseline 5 bps adverse fills. The table corrects multi-component dividends and actual same-day STT/stamp treatment. These are entry controls within the existing wrapper, not a canonical buy-until-trend-reverses or ranked momentum portfolio.

**Statistical observation:** both simple conditions lose money under that wrapper. In the original-model zero-fee/zero-slippage reruns, two-year trend and momentum returns were still negative (−0.6175% and −0.5613%). Thus reducing transaction costs alone did not rescue these particular controls. These are full counterfactual reruns: sizing, fee-aware targets, fills and subsequent opportunities change, so the differences are not pure fixed-trade cost subtraction.

## Random-entry null context

| stage | random_seeds | random_mean_return_pct | random_q05_return_pct | random_q95_return_pct | random_min_return_pct | random_max_return_pct | random_positive_seeds | random_mean_stockday_exposure_pct | random_mean_trades | frozen48_mean_return_pct | frozen48_median_return_pct | frozen48_mean_stockday_exposure_pct | frozen48_mean_trades |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final | 20 | -0.0842 | -0.1133 | -0.0377 | -0.1232 | -0.0265 | 0 | 13.2716 | 965.1500 | -0.0816 | -0.0480 | 12.4486 | 844.9375 |
| two_year | 20 | -0.3463 | -0.4253 | -0.2576 | -0.4776 | -0.2286 | 0 | 13.4851 | 3780.1500 | -0.2670 | -0.1919 | 11.5234 | 2984.8333 |

Each seed generates completed-day Bernoulli entries. Each stock’s fixed probability is its mean raw signal frequency across the 48 already-frozen representative rules during development. The same probability is carried to later segments; no seed is selected. All rules retain identical cash/risk/stop/target/hold constraints. Seeds 20261111 through 20261130 were fixed in the design.

**Statistical observation:** all 20 audited random paths were negative in both final and two-year windows. Final mean return was −0.0842%; mean return across the 48 audited frozen rules was −0.0816%. Their stock-day exposures were 13.27% and 12.45%, respectively. This suggests similar aggregate economics under this execution wrapper in that segment. It does not establish equality or prove that every indicator signal is random.

**Limitation:** random rates match mean raw entry frequency, not each family’s executed trade count, clustering, conditional volatility or capital exposure. The KAMA leader had only 347 final trades versus mean 965.15 random trades, so the random distribution is not an exactly matched test of that single sparse rule. RNG seed quantiles describe variation conditional on one market history; they are not independent-market confidence intervals. The representative family set itself came from prior research, so development-calibrated event frequency does not create a pristine holdout.

`exposure_pct` for sleeve controls is the original engine’s fraction of observed stock-days with a position. It is not the fraction of cash deployed; buy-hold invested-NAV percentage measures a different quantity. Two-sided turnover is actual buy plus sell filled notional divided by total initial sleeve capital. Published-index turnover is unavailable rather than invented.

## Research implications

- **Verified fact:** multi-component dividends and same-day tax assumptions require corrections, but corrected benchmark replays do not turn these simple/random controls into profitable systems.
- **Hypothesis:** the common protective/target/time-exit wrapper and selection of entry regimes deserve controlled isolation before expanding indicator complexity. The controls do not identify which component is responsible; root-controlled exit ablations address that separately.
- **Hypothesis:** causal sector/regime conditioning may matter more than choosing MACD versus PPO in this window. Sector hindsight must not become the stock-selection rule.
- **Exact next null experiment:** before any new candidate is evaluated, preregister per-family random placebo opportunities matched by stock, calendar block, lagged volatility, actual position/holding constraints and expected turnover. Use common-date block inference, correct across tested candidates, and retain all placebo seeds. This would answer a sharper signal-value question than the generic null here.
- **Unresolved:** whether the candidate survives genuine future data, a funded cash-constrained portfolio and measured execution costs. The present independent sleeves cannot answer that alone.

## Reproduction and artifacts

Run `scripts/diagnosis_fetch_indices.py` (cached by default), `scripts/diagnosis_history.py`, `scripts/diagnosis_benchmarks.py`, then `scripts/diagnosis_benchmarks_corrected.py`. The corrected runs require the auditor’s `audit-dividend-corrected.npz` and `audit_engine.py`. No old research source or results are overwritten.

[Frozen design](benchmark-design.md), [original controls](benchmark-controls.csv), [audited controls](benchmark-controls-corrected.csv), [original random quantiles](benchmark-random-distribution.csv), [audited final random quantiles](benchmark-random-corrected-final.csv), [audited full-period quantiles](benchmark-random-corrected-two_year.csv), [benchmark integrity summary](benchmark-results-summary.json), [official TRI comparisons](benchmark-tri-comparison.csv), [buy-hold correction](benchmark-buyhold-correction.csv), [historical feasibility and primary-source links](history-feasibility.md), [raw source hashes](benchmark-source-fingerprints.json).
