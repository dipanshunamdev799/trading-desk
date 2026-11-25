# NIFTY V18 — Corporate event studies

The stock study matched **6,563** eligible issuer-session episodes and kept **64,227** rows across forecast stages and horizons. It uses genuine observed exchange open and close prices, point-in-time ticker/ISIN checks, and explicit timing strata for releases before the open, during trading, after the close or during a non-trading day. Each unobserved interval starts after dissemination plus the guard. The full-session studies measure **1, 3, 5, 10 and 21 sessions** from the first eligible full cash open and again from the open after the initial reaction was complete. We compare raw stock returns, same-window NIFTY and native sector returns, prior-only beta residuals, ex-ante volatility-normalized residuals, and same-date matched non-event stocks. Peer matching used up to four stocks with similar past volatility, five-session momentum and trading value. A peer was excluded for a recent announcement already known at that decision. In the liquid intraday set, **653** stock/bar observations supported synchronized five-minute, 30-minute or remaining-session tests.

| stage | timing | family | horizon | metric | n | different dates | issuers | mean | low | high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| after_reaction | after_close | credit | 1 | beta_residual | 376 | 234 | 104 | -0.001342 | -0.003221 | 0.000538 |
| after_reaction | after_close | credit | 1 | matched_abnormal | 226 | 175 | 51 | -0.000704 | -0.002532 | 0.001124 |
| after_reaction | after_close | credit | 5 | beta_residual | 376 | 234 | 104 | -0.001404 | -0.005979 | 0.003170 |
| after_reaction | after_close | credit | 5 | matched_abnormal | 226 | 175 | 51 | -0.001779 | -0.005769 | 0.002211 |
| after_reaction | after_close | credit | 21 | beta_residual | 360 | 224 | 101 | -0.003775 | -0.014297 | 0.006747 |
| after_reaction | after_close | credit | 21 | matched_abnormal | 218 | 168 | 49 | -0.004217 | -0.015280 | 0.006846 |
| after_reaction | after_close | earnings | 1 | beta_residual | 647 | 183 | 146 | -0.001702 | -0.003486 | 0.000082 |
| after_reaction | after_close | earnings | 1 | matched_abnormal | 356 | 156 | 76 | 0.001074 | -0.000975 | 0.003122 |
| after_reaction | after_close | earnings | 5 | beta_residual | 634 | 181 | 145 | -0.002819 | -0.006984 | 0.001346 |
| after_reaction | after_close | earnings | 5 | matched_abnormal | 349 | 154 | 75 | 0.002438 | -0.002611 | 0.007486 |
| after_reaction | after_close | earnings | 21 | beta_residual | 568 | 167 | 145 | -0.004232 | -0.013308 | 0.004845 |
| after_reaction | after_close | earnings | 21 | matched_abnormal | 314 | 141 | 75 | 0.003876 | -0.005576 | 0.013328 |
| after_reaction | after_close | fundraising | 1 | beta_residual | 85 | 79 | 35 | 0.001418 | -0.004172 | 0.007007 |
| after_reaction | after_close | fundraising | 1 | matched_abnormal | 48 | 47 | 17 | 0.000542 | -0.004944 | 0.006029 |
| after_reaction | after_close | fundraising | 5 | beta_residual | 84 | 78 | 34 | -0.000836 | -0.013423 | 0.011750 |
| after_reaction | after_close | fundraising | 5 | matched_abnormal | 48 | 47 | 17 | -0.000500 | -0.017408 | 0.016408 |
| after_reaction | after_close | fundraising | 21 | beta_residual | 82 | 76 | 34 | -0.006705 | -0.030374 | 0.016965 |
| after_reaction | after_close | fundraising | 21 | matched_abnormal | 47 | 46 | 17 | 0.000828 | -0.026755 | 0.028411 |
| after_reaction | after_close | order_win | 1 | beta_residual | 111 | 90 | 19 | -0.005261 | -0.008907 | -0.001616 |
| after_reaction | after_close | order_win | 1 | matched_abnormal | 18 | 18 | 9 | 0.006815 | -0.008911 | 0.022541 |
| after_reaction | after_close | order_win | 5 | beta_residual | 111 | 90 | 19 | -0.013635 | -0.021648 | -0.005621 |
| after_reaction | after_close | order_win | 5 | matched_abnormal | 18 | 18 | 9 | 0.006056 | -0.013633 | 0.025745 |
| after_reaction | after_close | order_win | 21 | beta_residual | 109 | 88 | 19 | -0.011455 | -0.030889 | 0.007980 |
| after_reaction | after_close | order_win | 21 | matched_abnormal | 18 | 18 | 9 | 0.000581 | -0.042013 | 0.043174 |
| after_reaction | after_close | regulatory | 1 | beta_residual | 234 | 158 | 71 | -0.001340 | -0.003727 | 0.001047 |
| after_reaction | after_close | regulatory | 1 | matched_abnormal | 165 | 125 | 34 | -0.001031 | -0.003820 | 0.001758 |
| after_reaction | after_close | regulatory | 5 | beta_residual | 233 | 157 | 71 | 0.003512 | -0.000964 | 0.007987 |
| after_reaction | after_close | regulatory | 5 | matched_abnormal | 165 | 125 | 34 | 0.001091 | -0.004491 | 0.006673 |
| after_reaction | after_close | regulatory | 21 | beta_residual | 224 | 149 | 71 | 0.004366 | -0.006861 | 0.015593 |
| after_reaction | after_close | regulatory | 21 | matched_abnormal | 162 | 122 | 34 | 0.009832 | -0.007958 | 0.027621 |
| after_reaction | before_open | credit | 1 | beta_residual | 11 | 11 | 7 | -0.003277 | -0.008825 | 0.002270 |
| after_reaction | before_open | credit | 1 | matched_abnormal | 5 | 5 | 4 | -0.005835 | -0.009038 | -0.002633 |
| after_reaction | before_open | credit | 5 | beta_residual | 11 | 11 | 7 | -0.001079 | -0.021571 | 0.019413 |
| after_reaction | before_open | credit | 5 | matched_abnormal | 5 | 5 | 4 | -0.013705 | -0.029473 | 0.002062 |
| after_reaction | before_open | credit | 21 | beta_residual | 11 | 11 | 7 | 0.016435 | -0.020685 | 0.053555 |
| after_reaction | before_open | credit | 21 | matched_abnormal | 5 | 5 | 4 | -0.031011 | -0.056166 | -0.005855 |
| after_reaction | before_open | order_win | 1 | beta_residual | 19 | 19 | 11 | -0.002850 | -0.008467 | 0.002768 |
| after_reaction | before_open | order_win | 1 | matched_abnormal | 10 | 10 | 5 | 0.004555 | -0.000270 | 0.009380 |
| after_reaction | before_open | order_win | 5 | beta_residual | 18 | 18 | 11 | -0.007584 | -0.034418 | 0.019250 |
| after_reaction | before_open | order_win | 5 | matched_abnormal | 9 | 9 | 5 | 0.009018 | -0.027018 | 0.045055 |

Every displayed interval uses day and company clustering. Cases within the same market date or issuer episode share exposure. A price move in the first reaction window is an outcome of that descriptive study and only enters forecasts made after the move was observable.

[Every stock episode and matched outcome](stock-event-pairs.csv.gz) · [Event-time definitions](event-panel-receipt.json) · [Daily event study](corporate-event-study.csv) · [Intraday shared timestamps](intraday-event-responses.csv.gz) · [Intraday event study](intraday-event-summary.csv)
