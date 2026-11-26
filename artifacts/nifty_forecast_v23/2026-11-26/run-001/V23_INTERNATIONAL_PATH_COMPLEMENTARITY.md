# V23 International path complementarity

V22's 0.015488 GJR range CRPS fell to 0.014409 from scaled India-only paths and 0.014195 from mixed paths.
V23 fixes the comparison more tightly. Each Indian origin selects 24 distinct earlier global weeks with one domestic
window per week. The mixed candidate replaces up to six windows inside those same weeks. Both laws have equal weight
per episode and the same volatility anchor. The strict arm admits foreign donors only when every daily OHLC bar
and the opening cash reference agree within 10 basis points across the two vendors. The pure-foreign sensitivity is
separated when it cannot fill the same 24 weeks. Random foreign paths, volatility-only matches and region exclusions
use the same construction.

The independently extracted Upstox histories cover the same bounded interval as Yahoo. Nonlocal dates, suspect
offsets, stale or missing bars, variant and currency distinctions and the DAX total-return control remain in the
source audit. FRED close requests timed out and a close-only feed would not verify high/low excursions. Same-day
broker agreement qualified 355 full five-session and 146 full 21-session donor windows before the Indian issue-time
test. Source verification is a retrospective provenance audit, with each admitted outcome additionally constrained
by its historical maturity date.
[Upstox daily candles and timestamp definition](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [FRED S&P 500](https://fred.stlouisfed.org/series/SP500) · [FRED Nikkei 225](https://fred.stlouisfed.org/series/NIKKEI225)

| code | paired | only broker | only primary | within 006 | strict dates | median close bps | return corr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| us | 470 | 19 | 1 | 0 | 0 | 31.219786 | 0.974038 |
| japan | 364 | 92 | 91 | 6 | 37 | 68.547890 | 0.217335 |
| hong_kong | 447 | 13 | 15 | 362 | 360 | 0.003953 | 0.956363 |
| uk | 475 | 10 | 1 | 152 | 333 | 4.278436 | 0.975342 |
| france | 479 | 3 | 1 | 225 | 211 | 1.124661 | 0.980444 |
| dax_total | 477 | 9 | 1 | 8 | 0 | 8.370309 | 0.978635 |

## Equal-episode results and foreign donor mix

| horizon | model | n | foreign paths | range crps | drawdown crps | upper range tail brier | expansion brier | persistent direction brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | analogue_global_on_IV_GJR | 265 | — | 0.006155 | 0.006205 | — | 0.157521 | — |
| 5 | analogue_india_on_IV_GJR | 265 | — | 0.006159 | 0.006139 | — | 0.155508 | — |
| 5 | foreign_only_same_episodes | 233 | 24.000000 | 0.006518 | 0.006597 | 0.120321 | 0.165422 | 0.228451 |
| 5 | foreign_only_unmatched_episodes | 32 | 24.000000 | 0.004638 | 0.004064 | 0.023763 | 0.102322 | 0.273329 |
| 5 | india_state_matched | 265 | 0.000000 | 0.006343 | 0.006194 | 0.108838 | 0.160515 | 0.236760 |
| 5 | mixed_broad | 265 | 6.000000 | 0.006300 | 0.006289 | 0.107469 | 0.154036 | 0.232252 |
| 5 | mixed_omit_asia | 265 | 6.000000 | 0.006378 | 0.006241 | 0.110515 | 0.160764 | 0.235331 |
| 5 | mixed_omit_disputed | 265 | 6.000000 | 0.006304 | 0.006276 | 0.109165 | 0.154389 | 0.233536 |
| 5 | mixed_random_foreign | 265 | 6.000000 | 0.006254 | 0.006313 | 0.107940 | 0.159002 | 0.233156 |
| 5 | mixed_strict | 265 | 6.000000 | 0.006434 | 0.006267 | 0.115533 | 0.160541 | 0.234093 |
| 5 | mixed_strict_omit_asia | 265 | 5.818868 | 0.006456 | 0.006275 | 0.113057 | 0.160843 | 0.236648 |
| 5 | mixed_vol_only | 265 | 6.000000 | 0.006295 | 0.006242 | 0.108039 | 0.161806 | 0.230706 |
| 21 | analogue_global_on_IV_GJR | 217 | — | 0.014195 | 0.013894 | — | 0.186368 | — |
| 21 | analogue_india_on_IV_GJR | 217 | — | 0.014409 | 0.013974 | — | 0.195207 | — |
| 21 | foreign_only_same_episodes | 192 | 24.000000 | 0.015139 | 0.015351 | 0.156793 | 0.174995 | 0.000868 |
| 21 | foreign_only_unmatched_episodes | 25 | 24.000000 | 0.012327 | 0.008324 | 0.020000 | 0.295000 | 0.038333 |
| 21 | india_state_matched | 217 | 0.000000 | 0.014230 | 0.013709 | 0.136633 | 0.198725 | 0.013113 |
| 21 | mixed_broad | 217 | 6.000000 | 0.014217 | 0.013921 | 0.139305 | 0.188668 | 0.009481 |
| 21 | mixed_omit_asia | 217 | 6.000000 | 0.014289 | 0.013850 | 0.139281 | 0.195589 | 0.010809 |
| 21 | mixed_omit_disputed | 217 | 6.000000 | 0.014176 | 0.013901 | 0.138545 | 0.187644 | 0.009985 |
| 21 | mixed_random_foreign | 217 | 6.000000 | 0.014310 | 0.013767 | 0.131400 | 0.194012 | 0.009561 |
| 21 | mixed_strict | 217 | 5.474654 | 0.014536 | 0.013849 | 0.138457 | 0.196165 | 0.008129 |
| 21 | mixed_strict_omit_asia | 217 | 5.078341 | 0.014337 | 0.013835 | 0.139737 | 0.197229 | 0.007168 |
| 21 | mixed_vol_only | 217 | 6.000000 | 0.014534 | 0.013829 | 0.140849 | 0.198925 | 0.011217 |

| horizon | model | market | donors | distinct paths | weeks |
| --- | --- | --- | --- | --- | --- |
| 5 | mixed_strict | france | 67 | 20 | 10 |
| 5 | mixed_strict | hong_kong | 944 | 117 | 42 |
| 5 | mixed_strict | uk | 579 | 106 | 39 |
| 5 | mixed_strict_omit_asia | france | 168 | 20 | 10 |
| 5 | mixed_strict_omit_asia | uk | 1,374 | 132 | 41 |
| 21 | mixed_strict | hong_kong | 463 | 42 | 10 |
| 21 | mixed_strict | uk | 725 | 77 | 22 |
| 21 | mixed_strict_omit_asia | uk | 1,102 | 84 | 22 |

| model | metric | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- |
| mixed_broad | range_crps | 217 | 0.000013 | -0.000607 | 0.000633 |
| mixed_omit_disputed | range_crps | 217 | 0.000054 | -0.000508 | 0.000617 |
| mixed_random_foreign | range_crps | 217 | -0.000080 | -0.000540 | 0.000379 |
| mixed_strict | range_crps | 217 | -0.000306 | -0.000976 | 0.000364 |
| mixed_broad | drawdown_crps | 217 | -0.000212 | -0.000868 | 0.000444 |
| mixed_omit_disputed | drawdown_crps | 217 | -0.000192 | -0.000850 | 0.000466 |
| mixed_random_foreign | drawdown_crps | 217 | -0.000058 | -0.000299 | 0.000183 |
| mixed_strict | drawdown_crps | 217 | -0.000140 | -0.000840 | 0.000560 |
| mixed_broad | expansion_brier | 217 | 0.010057 | -0.013180 | 0.033293 |
| mixed_omit_disputed | expansion_brier | 217 | 0.011081 | -0.012653 | 0.034815 |
| mixed_random_foreign | expansion_brier | 217 | 0.004712 | -0.015252 | 0.024677 |
| mixed_strict | expansion_brier | 217 | 0.002560 | -0.010333 | 0.015454 |
| mixed_broad | upper_range_tail_brier | 217 | -0.002672 | -0.013811 | 0.008467 |
| mixed_omit_disputed | upper_range_tail_brier | 217 | -0.001912 | -0.012764 | 0.008940 |
| mixed_random_foreign | upper_range_tail_brier | 217 | 0.005232 | -0.004969 | 0.015434 |
| mixed_strict | upper_range_tail_brier | 217 | -0.001824 | -0.012782 | 0.009133 |
| mixed_broad | persistent_direction_brier | 217 | 0.003632 | -0.000572 | 0.007837 |
| mixed_omit_disputed | persistent_direction_brier | 217 | 0.003128 | -0.000279 | 0.006535 |
| mixed_random_foreign | persistent_direction_brier | 217 | 0.003552 | -0.000238 | 0.007343 |
| mixed_strict | persistent_direction_brier | 217 | 0.004984 | 0.001255 | 0.008714 |

On the monthly target, the broad mixed library improved range CRPS by about 0.000013 over equal-size India history. The strict mixed library lost about 0.000306. Expansion and persistence have different rankings, and the paired uncertainty remains wide. Verified foreign paths can expand the scenario collection even when their inclusion fails the score comparison.

[foreign-source-receipts.json](foreign-source-receipts.json) · [foreign-session-offsets.csv](foreign-session-offsets.csv) · [foreign-full-ohlc-pairs.csv.gz](foreign-full-ohlc-pairs.csv.gz) · [path-risk-matched-intervals.csv.gz](path-risk-matched-intervals.csv.gz) · [path-donor-members.csv.gz](path-donor-members.csv.gz) · [path-risk-cohort-deltas.csv.gz](path-risk-cohort-deltas.csv.gz)

[Back to the research index](NIFTY_V23_RESEARCH.md)
