# V16 Opening-gap reproduction and timing audit

V16 rebuilt **2,575** V15 forecasts from raw historical data, including all **258** same-morning and **257** next-opening cases for each parent–candidate comparison. Maximum absolute difference across probabilities, Brier, point/interval estimates, CRPS and log loss was **6.94e-18**. The original fit uses penalty 95, up to 160 strictly matured training outcomes and 70% of its estimated ridge location, added to a median-centered empirical log-gap law. The comparison called the domestic baseline in the brief was the previous domestic state with older inherited global risk, FX, oil and US breadth. The pure domestic parent was also rebuilt.

## The original 09:10 forecasts

| target | model | parent | metric | n | candidate | control | gain | early gain | later gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| immediate_open | offshore_fresh | offshore_prior_only | crps | 258 | 0.002920 | 0.003241 | 0.000321 | 0.000466 | 0.000183 | 0.000036 | 0.000607 |
| immediate_open | offshore_fresh | offshore_prior_only | brier | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| immediate_open | offshore_fresh | offshore_prior_only | log_loss | 258 | 0.651813 | 0.729289 | 0.077476 | 0.109091 | 0.047298 | -0.002025 | 0.156977 |
| immediate_open | offshore_prior_only | domestic_prior | crps | 258 | 0.003241 | 0.003240 | -0.000001 | 0.000001 | -0.000003 | -0.000074 | 0.000072 |
| immediate_open | offshore_prior_only | domestic_prior | brier | 258 | 0.265168 | 0.260525 | -0.004642 | -0.007388 | -0.002021 | -0.016229 | 0.006944 |
| immediate_open | offshore_prior_only | domestic_prior | log_loss | 258 | 0.729289 | 0.718765 | -0.010524 | -0.016880 | -0.004457 | -0.035984 | 0.014935 |
| immediate_open | domestic_prior | price_zero | crps | 258 | 0.003240 | 0.003173 | -0.000067 | -0.000146 | 0.000008 | -0.000164 | 0.000029 |
| immediate_open | domestic_prior | price_zero | brier | 258 | 0.260525 | 0.250024 | -0.010501 | -0.025184 | 0.003515 | -0.031864 | 0.010862 |
| immediate_open | domestic_prior | price_zero | log_loss | 258 | 0.718765 | 0.693196 | -0.025568 | -0.059763 | 0.007072 | -0.074268 | 0.023131 |
| next_open_gap | offshore_fresh | offshore_prior_only | crps | 257 | 0.003201 | 0.003205 | 0.000004 | -0.000004 | 0.000012 | -0.000047 | 0.000056 |
| next_open_gap | offshore_fresh | offshore_prior_only | brier | 257 | 0.262746 | 0.260551 | -0.002195 | -0.007577 | 0.002982 | -0.015533 | 0.011143 |
| next_open_gap | offshore_fresh | offshore_prior_only | log_loss | 257 | 0.721779 | 0.717904 | -0.003876 | -0.015321 | 0.007133 | -0.032689 | 0.024937 |
| next_open_gap | offshore_prior_only | domestic_prior | crps | 257 | 0.003205 | 0.003200 | -0.000005 | -0.000012 | 0.000001 | -0.000056 | 0.000045 |
| next_open_gap | offshore_prior_only | domestic_prior | brier | 257 | 0.260551 | 0.256157 | -0.004394 | -0.012015 | 0.002936 | -0.016573 | 0.007784 |
| next_open_gap | offshore_prior_only | domestic_prior | log_loss | 257 | 0.717904 | 0.710230 | -0.007673 | -0.022320 | 0.006415 | -0.033530 | 0.018183 |
| next_open_gap | domestic_prior | price_zero | crps | 257 | 0.003200 | 0.003182 | -0.000018 | -0.000037 | 0.000001 | -0.000082 | 0.000046 |
| next_open_gap | domestic_prior | price_zero | brier | 257 | 0.256157 | 0.250037 | -0.006120 | -0.011097 | -0.001332 | -0.018808 | 0.006569 |
| next_open_gap | domestic_prior | price_zero | log_loss | 257 | 0.710230 | 0.693221 | -0.017009 | -0.032119 | -0.002476 | -0.049139 | 0.015121 |

The domestic opening process begins at 09:00 IST, with indicative index and constituent equilibrium prices disseminated during order entry. The later cash pre-open protocol applies from September 7, 2026. It restricts market orders after 09:05, may close order entry randomly in the final two minutes, and uses matching before continuous trading at 09:15. Under the earlier protocol 09:10 was also inside the pre-open process. The exchange determines eligible constituent opening prices through equilibrium matching, with first regular trades used when a price has yet to be discovered. The benchmark index aggregates NSE-priced constituent stocks using free-float weights. V16 used the official published NIFTY 50 open directly. All 403 official opens and closes agreed with the frozen V6 cash series. The main earlier study uses 08:55 with 08:30 and 08:45 sensitivities. The baseline and replay data trace contains previous domestic state, earlier derivative surface marks and eligible foreign closes. It excludes current-session NIFTY prices, constituent auction prices, indicative prints, and auction breadth at all four replayed clocks. The GIFT variant is a different input test, especially at 09:10, when its prices may already respond to the NSE auction. [NSE pre-open rules](https://www.nseindia.com/static/products-services/equity-market-pre-open) · [2026 protocol history](https://nsearchives.nseindia.com/web/mediaattachment/2026-10/FAQs_on_Closing_Auction_Session_CAS_in_the_CM_and_changes_in_FO_Segment_ver3_20261023220345.pdf) · [NIFTY index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)

## Pre-auction forecasts and source-release sensitivity

| cutoff | delay | n | candidate | control | gain | early gain | later gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 08:30 | 60 | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| 08:45 | 60 | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| 08:55 | 60 | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| 09:10 | 60 | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| 08:55 | 30 | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| 08:55 | 180 | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| 08:55 | 360 | 258 | 0.227947 | 0.265168 | 0.037220 | 0.050636 | 0.024415 | 0.003563 | 0.070877 |
| 08:55 | 1,440 | 258 | 0.266396 | 0.265168 | -0.001229 | -0.004235 | 0.001640 | -0.009316 | 0.006858 |

Moving the original model before the auction left the matched scores unchanged at 08:30, 08:45 and 08:55. The 30-, 60-, 180- and 360-minute close-delay variants selected the same input as the original. The additional full-day delay removed the gain. The stronger next-session-gap task stayed weak. The source snapshots are historical reconstructions from dated marks, with explicit delays where original receipt timestamps are missing. The more demanding GIFT and partial Asia tests use completed intraday vendor candles and a separate matched comparison. Normal cash sessions, weekends and special sessions retain their own tags.

## Snapshot support

| cutoff | days | eligible gift |
| --- | --- | --- |
| 08:30 | 402 | 385 |
| 08:45 | 402 | 387 |
| 08:55 | 402 | 387 |
| 09:10 | 402 | 385 |

[Per-origin exact reproduction](v15-replayed-gap-forecasts.csv.gz) · [Full benchmark replay evidence](v15-replayed-gap-evidence.csv) · [Exact archived laws](v15-replayed-gap-laws.npz) · [Official open reconciliation](cash-opening-reconciliation.csv) · [Timing by source](information-clock.csv.gz) · [Earlier V15 research](../../../nifty_forecast_v15/2026-11-25/run-001/NIFTY_V15_RESEARCH.md) · [More gap models](V16_ADVANCED_OPENING_GAP_FORECASTING.md)
