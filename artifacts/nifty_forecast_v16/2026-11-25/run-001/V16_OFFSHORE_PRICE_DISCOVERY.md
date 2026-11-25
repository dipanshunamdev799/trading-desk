# V16 Offshore price discovery

Authenticated Upstox history exposed the GIFT NIFTY vendor alias GLOBAL_INDEX|SGX NIFTY with actual five-minute bars. At 08:55 there were **387** source-eligible snapshots including training dates. The predictive value tested is the percentage change in that vendor series between an earlier NIFTY reference-day mark ending by 15:30 and the latest eligible current-morning bar. For an index points basis, an approximately stable futures-to-cash relationship cancels when taking that relative change. All signal calculations use the archived offshore prices. The vendor alias carries neither an auditable contract expiry nor a dated switch policy. Raw GIFT scores are therefore a vendor-series experiment. The exercise makes no per-contract fill or returns claim. NSE IX specifies a USD cash-settled futures contract, with a USD multiplier separate from the reported index points. The documented expiry convention changed during 2025, and the November 2, 2026 hours extension covered 03:15 IST through 02:45 IST the next day. The broad month-transition screen leaves out the final seven and first two calendar days, independently of realized marks. [NSE IX contract specification](https://www.nseix.com/markets/about-our-products/equity-derivatives-updated) · [March 2025 expiry revision](https://www.nseix.com/api/content/circulars/NSEIFSC_TRADE_2056.pdf) · [July 2025 expiry revision](https://www.nseix.com/api/content/circulars/NSEIFSC_TRADE_2199.pdf) · [Hours extension](https://www.nseix.com/web/pressrelease/2026-11/PR_CC_03112026_20261103101702.pdf)

## Deadlines and contractual rollover sensitivity

| cutoff | model | n | brier | crps | mae | correct | covered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 08:30 | gift_calibrated | 247 | 0.105061 | 0.001468 | 0.001988 | 0.854251 | 0.777328 |
| 08:30 | gift_plus_global | 247 | 0.107667 | 0.001494 | 0.002015 | 0.850202 | 0.748988 |
| 08:30 | gift_raw | 247 | 0.105095 | 0.001468 | 0.001988 | 0.858300 | 0.757085 |
| 08:30 | gift_roll_screened | 180 | 0.101224 | 0.001231 | 0.001700 | 0.855556 | 0.777778 |
| 08:45 | gift_calibrated | 248 | 0.101526 | 0.001440 | 0.001958 | 0.875000 | 0.782258 |
| 08:45 | gift_plus_global | 248 | 0.103504 | 0.001467 | 0.001982 | 0.866935 | 0.770161 |
| 08:45 | gift_raw | 248 | 0.101678 | 0.001443 | 0.001957 | 0.875000 | 0.770161 |
| 08:45 | gift_roll_screened | 180 | 0.097482 | 0.001199 | 0.001662 | 0.872222 | 0.794444 |
| 08:55 | gift_calibrated | 248 | 0.100937 | 0.001451 | 0.001959 | 0.870968 | 0.778226 |
| 08:55 | gift_plus_global | 248 | 0.102878 | 0.001482 | 0.001992 | 0.866935 | 0.766129 |
| 08:55 | gift_raw | 248 | 0.100841 | 0.001459 | 0.001965 | 0.887097 | 0.766129 |
| 08:55 | gift_roll_screened | 180 | 0.095052 | 0.001203 | 0.001667 | 0.888889 | 0.800000 |
| 09:10 | gift_calibrated | 246 | 0.093105 | 0.001271 | 0.001721 | 0.861789 | 0.756098 |
| 09:10 | gift_plus_global | 246 | 0.094992 | 0.001304 | 0.001755 | 0.869919 | 0.719512 |
| 09:10 | gift_raw | 246 | 0.092611 | 0.001289 | 0.001740 | 0.882114 | 0.735772 |
| 09:10 | gift_roll_screened | 179 | 0.086748 | 0.001067 | 0.001489 | 0.877095 | 0.765363 |

## Basis anchor alternatives at 08:55

| model | n | brier | crps | mae | accuracy | reference basis points |
| --- | --- | --- | --- | --- | --- | --- |
| prior_basis_median5 | 248 | 0.093905 | 0.001545 | 0.002059 | 0.895161 | 43.850000 |
| prior_1530 | 248 | 0.100841 | 0.001459 | 0.001965 | 0.887097 | 43.850000 |
| prior_1540 | 248 | 0.101554 | 0.001449 | 0.001952 | 0.879032 | 43.850000 |
| prior_1515 | 248 | 0.102593 | 0.001516 | 0.002026 | 0.870968 | 43.850000 |
| earlier_quote_buffer | 248 | 0.104765 | 0.001464 | 0.001982 | 0.862903 | 43.850000 |
| vendor_daily_lag | 258 | 0.252701 | 0.003198 | 0.004070 | 0.453488 | 43.850000 |

## Matched exclusions and the broader global addition

| model | control | case filter | n | loss | base | gain |
| --- | --- | --- | --- | --- | --- | --- |
| gift_raw | equal_six | all | 248 | 0.100841 | 0.233717 | 0.132876 |
| gift_raw | equal_six | ordinary | 248 | 0.100841 | 0.233717 | 0.132876 |
| gift_raw | equal_six | no_large_gaps | 229 | 0.109204 | 0.238798 | 0.129594 |
| gift_raw | equal_six | non_roll | 180 | 0.097792 | 0.236406 | 0.138614 |
| gift_raw | equal_six | holiday_or_special | 16 | 0.118220 | 0.233170 | 0.114950 |
| gift_raw | equal_six | strict_ordinary_non_roll | 170 | 0.094003 | 0.237271 | 0.143268 |
| gift_raw | single_US | all | 248 | 0.100841 | 0.225386 | 0.124545 |
| gift_raw | single_US | ordinary | 248 | 0.100841 | 0.225386 | 0.124545 |
| gift_raw | single_US | no_large_gaps | 229 | 0.109204 | 0.231534 | 0.122330 |
| gift_raw | single_US | non_roll | 180 | 0.097792 | 0.229473 | 0.131681 |
| gift_raw | single_US | holiday_or_special | 16 | 0.118220 | 0.220902 | 0.102682 |
| gift_raw | single_US | strict_ordinary_non_roll | 170 | 0.094003 | 0.228581 | 0.134578 |
| gift_plus_global | gift_calibrated | all | 248 | 0.102878 | 0.100937 | -0.001941 |
| gift_plus_global | gift_calibrated | ordinary | 248 | 0.102878 | 0.100937 | -0.001941 |
| gift_plus_global | gift_calibrated | no_large_gaps | 229 | 0.111409 | 0.109307 | -0.002102 |
| gift_plus_global | gift_calibrated | non_roll | 180 | 0.099961 | 0.097069 | -0.002892 |
| gift_plus_global | gift_calibrated | holiday_or_special | 16 | 0.120969 | 0.115428 | -0.005541 |
| gift_plus_global | gift_calibrated | strict_ordinary_non_roll | 170 | 0.096258 | 0.093318 | -0.002940 |

To check source timing and changing cash-close protocols, prior futures anchors at 15:15, 15:30 or 15:40, an earlier morning quote and a five-date rolling basis were evaluated on persistent historical support. Eligibility requires the same dated morning, sufficient publication buffer and a fresh bar; a missing bar prevents an implied-gap forecast for that case. The 09:10 alias is eligible for the comparison during NSE price discovery. The primary pre-auction cutoff is 08:55. Spread/carry variation, vendor rolling and exact receipt times remain sources of uncertainty. The simple futures change performed strongly before the auction and the broad foreign block did not consistently improve it. [NSE cash closing-auction protocol](https://www.nseindia.com/static/products-services/closing-auction-session)

[Every quote anchor and basis check](offshore-anchor-identity.csv) · [Basis and publication audit](offshore-roll-and-clock-audit.json) · [Futures candle retrieval](foreign-intraday-acquisition.json) · [Forecast-date sensitivity](opening-gap-sensitivity.csv) · [Month and large-event deletion](opening-gap-deletion.csv)
