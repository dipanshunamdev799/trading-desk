# V16 Overnight and intraday return decomposition

Close-to-close log return is the sum of the prior-close-to-official-open gap and the official-open-to-close regular return. The exact arithmetic identity was tested on every eligible morning. The variance decomposition includes the covariance term. At 08:55 the full gap and regular-session component are both unknown. At 09:25 the separate study can use the first completed five-minute bar, its recorded open as the gap proxy and earlier known basis; the 10:20 study additionally uses the first hour and synchronized sector prefix. The after-first-bar target uses the first bar's close and the remaining-session target uses the 10:15 completed cash mark. Foreign arrivals, domestic gap, prior eligible derivatives and observed sector/ETF proxies enter under explicit clocks.

## Realized variation by component

| cohort | n | overnight sd | regular sd | total sd | overnight variance share | regular variance share | cross variance share | correlation | same sign | close same side |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| combined | 258 | 0.006660 | 0.006619 | 0.008937 | 0.555444 | 0.548549 | -0.103993 | -0.094199 | 0.534884 | 0.728682 |
| early | 126 | 0.008221 | 0.006808 | 0.009854 | 0.696060 | 0.477305 | -0.173365 | -0.150387 | 0.555556 | 0.753968 |
| later | 132 | 0.004699 | 0.006427 | 0.007940 | 0.350244 | 0.655217 | -0.005461 | -0.005700 | 0.515152 | 0.704545 |

## Before the auction

| target | model | n | brier | crps | mae | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| firsthour | domestic | 257 | 0.263165 | 0.002164 | 0.002946 | 0.512970 |
| firsthour | eq_fresh | 257 | 0.263098 | 0.002167 | 0.002949 | 0.528121 |
| firsthour | gift_conditional | 248 | 0.259900 | 0.002179 | 0.002988 | 0.529729 |
| firsthour | rich_fresh | 257 | 0.266911 | 0.002186 | 0.002973 | 0.523909 |
| gap | domestic | 258 | 0.257213 | 0.003238 | 0.004115 | 0.576983 |
| gap | eq_fresh | 258 | 0.239192 | 0.003053 | 0.003934 | 0.635457 |
| gap | gift_conditional | 248 | 0.152550 | 0.002305 | 0.002874 | 0.822581 |
| gap | rich_fresh | 258 | 0.194386 | 0.002544 | 0.003324 | 0.705469 |
| next_next_close | domestic | 257 | 0.252646 | 0.004985 | 0.006708 | 0.548304 |
| next_next_close | eq_fresh | 257 | 0.253810 | 0.004992 | 0.006725 | 0.544367 |
| next_next_close | gift_conditional | 247 | 0.254430 | 0.005060 | 0.006785 | 0.558295 |
| next_next_close | rich_fresh | 257 | 0.256367 | 0.005005 | 0.006734 | 0.524319 |
| one | domestic | 258 | 0.254857 | 0.005007 | 0.006763 | 0.522536 |
| one | eq_fresh | 258 | 0.248569 | 0.004892 | 0.006634 | 0.550060 |
| one | gift_conditional | 248 | 0.207457 | 0.004226 | 0.005776 | 0.733984 |
| one | rich_fresh | 258 | 0.221361 | 0.004398 | 0.006015 | 0.635577 |
| regular | domestic | 258 | 0.249278 | 0.003693 | 0.005046 | 0.524170 |
| regular | eq_fresh | 258 | 0.249995 | 0.003702 | 0.005057 | 0.524531 |
| regular | gift_conditional | 248 | 0.246197 | 0.003651 | 0.004966 | 0.567330 |
| regular | rich_fresh | 258 | 0.244809 | 0.003711 | 0.005035 | 0.548701 |
| remaining | domestic | 257 | 0.251255 | 0.002956 | 0.004003 | 0.552750 |
| remaining | eq_fresh | 257 | 0.252707 | 0.002961 | 0.004012 | 0.533339 |
| remaining | gift_conditional | 248 | 0.248952 | 0.002908 | 0.003947 | 0.552419 |
| remaining | rich_fresh | 257 | 0.257842 | 0.003006 | 0.004080 | 0.517533 |

## After the first cash bar or hour

| cutoff | target | model | n | brier | crps | mae |
| --- | --- | --- | --- | --- | --- | --- |
| 09:25 | firsthour_residual | breadth_after_open | 257 | 0.255598 | 0.001537 | 0.002127 |
| 09:25 | firsthour_residual | cash_prefix | 257 | 0.255598 | 0.001537 | 0.002127 |
| 09:25 | firsthour_residual | eq_fresh | 257 | 0.256971 | 0.001541 | 0.002132 |
| 09:25 | firsthour_residual | foreign_after_gap | 257 | 0.257875 | 0.001549 | 0.002140 |
| 09:25 | firsthour_residual | gap_breadth_interaction | 257 | 0.255794 | 0.001538 | 0.002128 |
| 09:25 | five | breadth_after_open | 263 | 0.236472 | 0.010698 | 0.014257 |
| 09:25 | five | cash_prefix | 263 | 0.236472 | 0.010698 | 0.014257 |
| 09:25 | five | eq_fresh | 263 | 0.236451 | 0.010704 | 0.014266 |
| 09:25 | five | foreign_after_gap | 263 | 0.235278 | 0.010628 | 0.014175 |
| 09:25 | five | gap_breadth_interaction | 263 | 0.234927 | 0.010621 | 0.014131 |
| 09:25 | regular_after_bar | breadth_after_open | 257 | 0.251068 | 0.003451 | 0.004677 |
| 09:25 | regular_after_bar | cash_prefix | 257 | 0.251068 | 0.003451 | 0.004677 |
| 09:25 | regular_after_bar | eq_fresh | 257 | 0.252048 | 0.003458 | 0.004688 |
| 09:25 | regular_after_bar | foreign_after_gap | 257 | 0.251932 | 0.003466 | 0.004704 |
| 09:25 | regular_after_bar | gap_breadth_interaction | 257 | 0.251159 | 0.003452 | 0.004677 |
| 09:25 | three | breadth_after_open | 255 | 0.228337 | 0.008132 | 0.011207 |
| 09:25 | three | cash_prefix | 255 | 0.228337 | 0.008132 | 0.011207 |
| 09:25 | three | eq_fresh | 255 | 0.229121 | 0.008143 | 0.011229 |
| 09:25 | three | foreign_after_gap | 255 | 0.225913 | 0.008069 | 0.011153 |
| 09:25 | three | gap_breadth_interaction | 255 | 0.223844 | 0.008011 | 0.011028 |
| 10:20 | five | breadth_after_open | 263 | 0.233242 | 0.010603 | 0.013990 |
| 10:20 | five | cash_prefix | 263 | 0.236529 | 0.010688 | 0.014232 |
| 10:20 | five | eq_fresh | 263 | 0.236684 | 0.010695 | 0.014244 |
| 10:20 | five | foreign_after_gap | 263 | 0.231882 | 0.010532 | 0.013914 |
| 10:20 | five | gap_breadth_interaction | 263 | 0.231248 | 0.010500 | 0.013827 |
| 10:20 | remaining | breadth_after_open | 257 | 0.253618 | 0.002980 | 0.004028 |
| 10:20 | remaining | cash_prefix | 257 | 0.253009 | 0.002971 | 0.004028 |
| 10:20 | remaining | eq_fresh | 257 | 0.254075 | 0.002976 | 0.004038 |
| 10:20 | remaining | foreign_after_gap | 257 | 0.256418 | 0.002989 | 0.004052 |
| 10:20 | remaining | gap_breadth_interaction | 257 | 0.253915 | 0.002990 | 0.004043 |
| 10:20 | three | breadth_after_open | 255 | 0.224464 | 0.008044 | 0.011077 |
| 10:20 | three | cash_prefix | 255 | 0.225182 | 0.008067 | 0.011082 |
| 10:20 | three | eq_fresh | 255 | 0.226463 | 0.008082 | 0.011109 |
| 10:20 | three | foreign_after_gap | 255 | 0.222213 | 0.007987 | 0.011017 |
| 10:20 | three | gap_breadth_interaction | 255 | 0.219487 | 0.007945 | 0.010920 |

At the morning cutoff foreign information must predict before the official gap is recorded. At 09:25 and 10:20 the fresh-input test instead compares predictions on identical post-observation targets with the observed prefix supplied to both models. Any difference in the return to official close after accounting for the first bar uses the unresolved cash component. The official gap used as a realized target and the first-candle gap used as an observed predictor have separate identities. EOD option surface state enters from the earlier vintage. Authenticated intraday option books are unavailable in this study.

[Session outcome components](session-targets.csv) · [Cash bar identity and coverage](cash-bar-identity-audit.csv) · [Matched comparisons and post-auction variants](session-matched-evidence.csv) · [Clock map](information-clock.csv.gz)
