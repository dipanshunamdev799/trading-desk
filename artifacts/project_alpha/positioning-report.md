# Project Alpha: previous-session positioning research

872 frozen intraday signal trades; 513 have exactly the prior NIFTY session's dated archive, yielding 1026 expiry-policy feature rows. 359 signals lack that prior archive and remain explicit rejections. Sources span 2025-10-13–2026-11-05 across 260 archived sessions.

This adds a valid EOD positioning experiment; it does not reconstruct intraday historical OI updates. Each decision uses only the immediately preceding NIFTY session, never current-session closing OI or a stale older chain. The source file was retrieved later; publication before the next open is assumed and historical release timestamps were not independently archived.

Frozen phase-one entries/exits are retained. The baseline is the same covered price-only opportunity set. All returns are underlying index points after2/5 illustrative points, not option-premium expectancy. Filtered-minus-baseline differences compare subsets and are observational, not causal treatment estimates.

Nearest future expiry and month-end listed-expiry proxy are fixed from the prior dated universe. Same-expiry common-contract PCR change matches token, strike, side and lot across the preceding two NIFTY sessions. OI is counted once per leg; ratios do not require guessing trade direction. Volume PCR is separately calculated and cannot identify whether puts were bought or written. OI walls/maxpain are hypotheses, never guaranteed support, resistance or attraction.

|Family|Expiry bucket|Filter|Final N|Baseline N|Net2 points|Net2 ordinary95%interval|Change vs covered baseline|Change ordinary95%interval|
|---|---|---|---:|---:|---:|---|---:|---|
|donchian|month_end_proxy|baseline|39|39|8.70|-8.55 to 28.92|0.00|0.00 to 0.00|
|donchian|month_end_proxy|pcr_level_align|11|39|14.98|-10.95 to 41.66|6.28|-22.83 to 30.01|
|donchian|month_end_proxy|pcr_level_contrarian|28|39|6.23|-13.43 to 32.33|-2.47|-14.39 to 7.77|
|donchian|month_end_proxy|pcr_change_align|17|39|-6.11|-24.84 to 12.93|-14.81|-33.55 to 0.19|
|donchian|month_end_proxy|volume_pcr_align|18|39|11.59|-16.34 to 38.47|2.89|-20.55 to 22.50|
|donchian|month_end_proxy|avoid_near_oi_wall|39|39|8.70|-8.55 to 28.92|0.00|0.00 to 0.00|
|donchian|month_end_proxy|maxpain_direction_align|14|39|-15.99|-35.18 to 2.86|-24.69|-45.62 to -4.21|
|donchian|nearest_nonexpiry_day|baseline|39|39|8.70|-8.55 to 28.92|0.00|0.00 to 0.00|
|donchian|nearest_nonexpiry_day|pcr_level_align|16|39|34.71|-2.25 to 77.10|26.01|1.50 to 55.86|
|donchian|nearest_nonexpiry_day|pcr_level_contrarian|23|39|-9.40|-23.36 to 5.54|-18.10|-37.83 to -0.88|
|donchian|nearest_nonexpiry_day|pcr_change_align|21|39|7.79|-17.89 to 45.15|-0.91|-14.54 to 19.50|
|donchian|nearest_nonexpiry_day|volume_pcr_align|17|39|3.20|-16.86 to 24.49|-5.50|-26.53 to 14.04|
|donchian|nearest_nonexpiry_day|avoid_near_oi_wall|39|39|8.70|-8.55 to 28.92|0.00|0.00 to 0.00|
|donchian|nearest_nonexpiry_day|maxpain_direction_align|12|39|-20.70|-43.57 to 0.35|-29.39|-53.18 to -6.50|
|ema_trend|month_end_proxy|baseline|66|66|7.78|-6.00 to 22.01|0.00|0.00 to 0.00|
|ema_trend|month_end_proxy|pcr_level_align|25|66|-1.19|-31.90 to 26.23|-8.97|-32.61 to 10.01|
|ema_trend|month_end_proxy|pcr_level_contrarian|41|66|13.26|-0.16 to 29.85|5.47|-7.15 to 17.54|
|ema_trend|month_end_proxy|pcr_change_align|37|66|2.26|-12.23 to 17.95|-5.52|-19.21 to 5.82|
|ema_trend|month_end_proxy|volume_pcr_align|34|66|14.60|-4.38 to 31.15|6.82|-9.13 to 18.45|
|ema_trend|month_end_proxy|avoid_near_oi_wall|66|66|7.78|-6.00 to 22.01|0.00|0.00 to 0.00|
|ema_trend|month_end_proxy|maxpain_direction_align|19|66|0.49|-13.65 to 13.38|-7.29|-26.07 to 9.42|
|ema_trend|nearest_nonexpiry_day|baseline|66|66|7.78|-6.00 to 22.01|0.00|0.00 to 0.00|
|ema_trend|nearest_nonexpiry_day|pcr_level_align|36|66|12.93|-12.05 to 38.42|5.14|-8.25 to 18.07|
|ema_trend|nearest_nonexpiry_day|pcr_level_contrarian|30|66|1.61|-9.55 to 11.96|-6.17|-23.37 to 8.75|
|ema_trend|nearest_nonexpiry_day|pcr_change_align|41|66|8.09|-9.66 to 30.35|0.30|-10.27 to 13.34|
|ema_trend|nearest_nonexpiry_day|volume_pcr_align|28|66|9.12|-3.33 to 22.29|1.33|-14.77 to 16.22|
|ema_trend|nearest_nonexpiry_day|avoid_near_oi_wall|66|66|7.78|-6.00 to 22.01|0.00|0.00 to 0.00|
|ema_trend|nearest_nonexpiry_day|maxpain_direction_align|13|66|-7.70|-22.48 to 8.11|-15.48|-35.73 to 4.77|
|pullback|month_end_proxy|baseline|57|57|6.12|-7.18 to 21.19|0.00|0.00 to 0.00|
|pullback|month_end_proxy|pcr_level_align|22|57|-9.65|-37.55 to 16.86|-15.77|-38.99 to 3.59|
|pullback|month_end_proxy|pcr_level_contrarian|35|57|16.03|1.61 to 36.40|9.91|-2.45 to 24.05|
|pullback|month_end_proxy|pcr_change_align|28|57|4.15|-8.63 to 18.27|-1.97|-17.94 to 11.84|
|pullback|month_end_proxy|volume_pcr_align|27|57|14.80|-3.92 to 32.75|8.68|-10.22 to 25.23|
|pullback|month_end_proxy|avoid_near_oi_wall|57|57|6.12|-7.18 to 21.19|0.00|0.00 to 0.00|
|pullback|month_end_proxy|maxpain_direction_align|20|57|-5.25|-20.16 to 9.27|-11.37|-29.20 to 5.67|
|pullback|nearest_nonexpiry_day|baseline|57|57|6.12|-7.18 to 21.19|0.00|0.00 to 0.00|
|pullback|nearest_nonexpiry_day|pcr_level_align|29|57|16.91|-9.97 to 45.09|10.79|-5.09 to 27.10|
|pullback|nearest_nonexpiry_day|pcr_level_contrarian|28|57|-5.06|-16.65 to 7.00|-11.18|-27.98 to 4.95|
|pullback|nearest_nonexpiry_day|pcr_change_align|31|57|11.20|-7.17 to 34.97|5.08|-6.78 to 19.47|
|pullback|nearest_nonexpiry_day|volume_pcr_align|23|57|13.98|-0.79 to 28.64|7.86|-11.02 to 25.38|
|pullback|nearest_nonexpiry_day|avoid_near_oi_wall|57|57|6.12|-7.18 to 21.19|0.00|0.00 to 0.00|
|pullback|nearest_nonexpiry_day|maxpain_direction_align|16|57|-12.61|-28.03 to 1.96|-18.73|-37.30 to -0.32|

Conditional gate passes: 0. Gate requires>=30final trades, positive lower net2 interval and positive lower improvement interval after approximate Bonferroni correction across72fixed contrasts. These intervals remain conditional on previously selected rules and do not correct phase-one strategy search. 20,000pairedfive-sessionblock draws are a Monte Carlo approximation, especially in extreme tails. No strategy is promoted.

The full CSV also discloses development/validation outcomes, ordinary and72-contrast intervals, and every rejection. Same expiry-policy selections can duplicate opportunities. Expiry-day, side and entry-hour breakdowns are descriptive, not additional selection criteria.

## Futures boundary
Existing raw NSE ZIPs also supply dated NIFTY futures close/OI. Where both immediately prior sessions contain the same token/expiry/lot, an exploratory prior-day price-and-OI buildup condition is reported on its own covered baseline. Close-to-close price/basis values are asynchronous EOD proxies. No continuous intraday futures or futures order-book data was manufactured.

|Family|Futures-covered final N|Covered baseline net2|Confirmed N|Confirmed net2|
|---|---:|---:|---:|---:|
|donchian|14|31.40|2|-18.299999999999272|
|ema_trend|25|31.86|6|14.158333333333454|
|pullback|20|33.67|3|46.633333333333816|

## Actual recent premium diagnostic
The same fixed prior-session filters were joined to 62 accepted recent intraday option-policy proxies; 62 had positioning features. All84 family/expiry/strike/filter cells are disclosed in positioning-option-ablations.csv and accepted feature-filtered rows in positioning-option-trades.csv.
This is a retrospective diagnostic on the previously inspected2–6November week. It is not a new holdout. Four-to-seven baseline trades per policy, often fewer after filtering, cannot establish positioning-dependent option expectancy. Premium proxy and cost limitations from the phase-two intraday study remain. No winner or confidence claim is made from these tiny cells.

3084 source/date/identity/PnL checks passed. All input hashes and source dates are in positioning-source-audit.json and positioning-preregister.json. Prior-data features can be reconstructed, but observed-at publication precision remains weaker than a contemporaneously captured intraday chain.

[NSE official derivatives reports](https://www.nseindia.com/all-reports-derivatives) provide dated EOD data; [NSE option-chain page](https://www.nseindia.com/option-chain) describes the current chain display. These are different data products.