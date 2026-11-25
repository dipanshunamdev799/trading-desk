# V15 information arrival and Indian market sessions

The new offshore close block improved the pre-open immediate opening-gap Brier on **258** common observations from **0.265168** to **0.227947**. The gain was 0.037220, with the ten-session family-adjusted interval [0.007871, 0.066569] and early/later gains 0.050636/0.024415. The opening gap is the same morning's open relative to the previous official close. The next-session opening gap remains a separately forecast outcome after that morning's gap has occurred. Its denominator is the actual current session close, used to calculate the later label. Prefix forecasts of the actual remaining cash session use the latest eligible cash price.

## Cutoffs and reconstruction

| stage | session count | four sectors | new proxies |
| --- | --- | --- | --- |
| completed | 402 | 400 | 400 |
| midday | 400 | 400 | 400 |
| near_close | 400 | 400 | 400 |
| opening | 400 | 400 | 400 |
| pre_open | 402 | 0 | 0 |

IST decisions are 09:10, 10:05, 12:30, 15:10 and 17:00. The last eligible cash bar closes five minutes or more before each intraday decision. Upstox timestamps denote bar starts in this reconstruction. Stable cash OHLC labels come from the frozen daily series. 400 full five-minute sessions had an archived end-of-day bar available for reconciliation. 75 closed within 0.05 index points of the official daily mark. The official close anchors all labels and the 17:00 close-based forecast. Opening, midday and near-close use timestamp-filtered 5-minute cash bars and 25-minute sector, broad-index and ETF bars. Each sector return is measured against the latest same-bar cash index. Intraday market breadth is proxied by participation across sector indices, while authentic equal-weight breadth comes from the stable previous daily observation.

S&P 500, Dow, Nikkei, Hang Seng, DAX and FTSE use time-zone-converted cash closes, local daylight-saving rules and a 60-minute allowance. Vendor day labels stand in for historical publication receipts. The most recent eligible market close is carried through foreign holidays and weekends. The frozen global-risk, VIX, FX and oil observations retain their inherited earlier-day allowances. EOD NSE option quotes retain their verified earlier-day timestamps at each intraday checkpoint. A genuine intraday option-snapshot update remains untested. The fixed endpoint targets refer to the original previous-close window and also score residual same-session and next-session targets separately.

## Paired scores

| checkpoint | target | model | parent | n | brier | brier base | crps | crps base |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pre_open | immediate_open | offshore_fresh | offshore_prior_only | 258 | 0.227947 | 0.265168 | 0.002920 | 0.003241 |
| pre_open | monthly_endpoint | offshore_fresh | offshore_prior_only | 217 | 0.296958 | 0.299193 | 0.029122 | 0.029139 |
| pre_open | next_close | offshore_fresh | offshore_prior_only | 257 | 0.243222 | 0.248908 | 0.006863 | 0.006945 |
| pre_open | next_open_gap | offshore_fresh | offshore_prior_only | 257 | 0.262746 | 0.260551 | 0.003201 | 0.003205 |
| pre_open | same_session | offshore_fresh | offshore_prior_only | 258 | 0.247296 | 0.254387 | 0.004823 | 0.004957 |
| pre_open | weekly_endpoint | offshore_fresh | offshore_prior_only | 265 | 0.245910 | 0.242612 | 0.011027 | 0.010975 |
| opening | monthly_endpoint | offshore_fresh | offshore_prior_only | 217 | 0.286677 | 0.288154 | 0.028602 | 0.028723 |
| opening | monthly_endpoint | sector_leadership | market_prefix | 217 | 0.286619 | 0.286737 | 0.028528 | 0.028817 |
| opening | monthly_endpoint | sector_etf | sector_leadership | 217 | 0.282727 | 0.286619 | 0.028360 | 0.028528 |
| opening | monthly_endpoint | sector_placebo | sector_leadership | 217 | 0.295130 | 0.286619 | 0.028720 | 0.028528 |
| opening | same_session | offshore_fresh | offshore_prior_only | 257 | 0.259655 | 0.254001 | 0.003076 | 0.003051 |
| opening | same_session | sector_leadership | market_prefix | 257 | 0.263670 | 0.265567 | 0.003099 | 0.003110 |
| opening | same_session | sector_etf | sector_leadership | 257 | 0.265980 | 0.263670 | 0.003121 | 0.003099 |
| opening | same_session | sector_placebo | sector_leadership | 257 | 0.264333 | 0.263670 | 0.003108 | 0.003099 |
| opening | weekly_endpoint | offshore_fresh | offshore_prior_only | 263 | 0.228123 | 0.229471 | 0.010164 | 0.010203 |
| opening | weekly_endpoint | sector_leadership | market_prefix | 263 | 0.231418 | 0.229956 | 0.010276 | 0.010250 |
| opening | weekly_endpoint | sector_etf | sector_leadership | 263 | 0.227670 | 0.231418 | 0.010161 | 0.010276 |
| opening | weekly_endpoint | sector_placebo | sector_leadership | 263 | 0.228080 | 0.231418 | 0.010226 | 0.010276 |
| midday | next_open_gap | offshore_fresh | offshore_prior_only | 256 | 0.263577 | 0.260683 | 0.003210 | 0.003214 |
| midday | next_open_gap | sector_leadership | market_prefix | 256 | 0.256328 | 0.259099 | 0.003204 | 0.003202 |
| midday | next_open_gap | sector_etf | sector_leadership | 256 | 0.257327 | 0.256328 | 0.003211 | 0.003204 |
| midday | next_open_gap | sector_placebo | sector_leadership | 256 | 0.261160 | 0.256328 | 0.003224 | 0.003204 |
| near_close | monthly_endpoint | offshore_fresh | offshore_prior_only | 217 | 0.284117 | 0.286961 | 0.028930 | 0.028987 |
| near_close | monthly_endpoint | sector_leadership | market_prefix | 217 | 0.284203 | 0.281705 | 0.028624 | 0.028695 |
| near_close | monthly_endpoint | sector_etf | sector_leadership | 217 | 0.275556 | 0.284203 | 0.028221 | 0.028624 |
| near_close | monthly_endpoint | sector_placebo | sector_leadership | 217 | 0.280722 | 0.284203 | 0.028414 | 0.028624 |
| near_close | next_close | offshore_fresh | offshore_prior_only | 256 | 0.248259 | 0.254969 | 0.005060 | 0.005080 |
| near_close | next_close | sector_leadership | market_prefix | 256 | 0.247181 | 0.245828 | 0.005003 | 0.005001 |
| near_close | next_close | sector_etf | sector_leadership | 256 | 0.247929 | 0.247181 | 0.004991 | 0.005003 |
| near_close | next_close | sector_placebo | sector_leadership | 256 | 0.250964 | 0.247181 | 0.005051 | 0.005003 |
| near_close | weekly_endpoint | offshore_fresh | offshore_prior_only | 263 | 0.218370 | 0.215354 | 0.009869 | 0.009825 |
| near_close | weekly_endpoint | sector_leadership | market_prefix | 263 | 0.218707 | 0.217319 | 0.009871 | 0.009847 |
| near_close | weekly_endpoint | sector_etf | sector_leadership | 263 | 0.216972 | 0.218707 | 0.009839 | 0.009871 |
| near_close | weekly_endpoint | sector_placebo | sector_leadership | 263 | 0.218226 | 0.218707 | 0.009847 | 0.009871 |

Ridge location estimates used at most 160 earlier matured observations per decision and target. The common centered empirical outcome law isolates location. Sector timing support requires every feature in the stated group to have a usable record at the decision. The placebo permutes training blocks for the sector block and retains the same current inputs. Asian close availability can shift during the Indian session. European and US closes have their own, later clocks. Any gap result applies to the tested morning decision and target.

[Session forecasts](session-forecasts.csv.gz) [Bar clocks by decision](session-feature-receipts.csv) [Source audit](session-source-audit.json) [Complete paired session table](session-evidence.csv) [Session block intervals](session-dependence-evidence.csv) [Upstox historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) [NSE cash trading times](https://www.nseindia.com/resources/exchange-communication-holidays)
