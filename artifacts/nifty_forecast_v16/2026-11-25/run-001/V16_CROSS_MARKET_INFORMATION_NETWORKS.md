# V16 Cross-market information networks

The stage-one targets are the next official IT, bank, financial-services, energy and broad-index open versus their own prior official close, their daily relative return versus NIFTY, and NIFTY regular-session realized risk. Foreign mapping uses technology, genuine XLF/XLK traded sector proxies, S&P/Dow, Asian participation, VIX, Treasury levels, USD/INR and Brent/WTI. The targeted model compares equal availability with domestic-only and its own delayed block. The ETF refinement uses archived SPY, RSP, XLF and XLK from Nasdaq through their exchange time zone with a one-hour publication allowance. It tests a US-equity return plus FX proxy, finance versus technology, and equal-weight minus cap-weight. Observations across markets are assayed for predictive association.

## Sector and realized risk models

| exercise | target | model | n | brier | crps | mae | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| etf_transmission | bank_gap | ETF_only | 258 | 0.232734 | 0.003407 | 0.004291 | 0.654582 |
| etf_transmission | bank_gap | delayed_foreign_ETF | 258 | 0.253497 | 0.003605 | 0.004534 | 0.584776 |
| etf_transmission | bank_gap | direct_foreign_ETF | 258 | 0.231533 | 0.003440 | 0.004329 | 0.643398 |
| etf_transmission | bank_gap | domestic | 258 | 0.249515 | 0.003594 | 0.004511 | 0.569264 |
| etf_transmission | bank_relative | ETF_only | 258 | 0.251597 | 0.002793 | 0.003817 | 0.485383 |
| etf_transmission | bank_relative | delayed_foreign_ETF | 258 | 0.260833 | 0.002849 | 0.003889 | 0.541865 |
| etf_transmission | bank_relative | direct_foreign_ETF | 258 | 0.257411 | 0.002831 | 0.003863 | 0.554586 |
| etf_transmission | bank_relative | domestic | 258 | 0.258262 | 0.002832 | 0.003856 | 0.530827 |
| etf_transmission | broad_gap | ETF_only | 258 | 0.191361 | 0.002638 | 0.003338 | 0.698033 |
| etf_transmission | broad_gap | delayed_foreign_ETF | 258 | 0.261037 | 0.003104 | 0.003913 | 0.563320 |
| etf_transmission | broad_gap | direct_foreign_ETF | 258 | 0.195753 | 0.002667 | 0.003374 | 0.692569 |
| etf_transmission | broad_gap | domestic | 258 | 0.258127 | 0.003083 | 0.003864 | 0.568783 |
| etf_transmission | energy_gap | ETF_only | 258 | 0.222294 | 0.002415 | 0.003065 | 0.582209 |
| etf_transmission | energy_gap | delayed_foreign_ETF | 258 | 0.247741 | 0.002616 | 0.003319 | 0.524340 |
| etf_transmission | energy_gap | direct_foreign_ETF | 258 | 0.231205 | 0.002455 | 0.003123 | 0.563636 |
| etf_transmission | energy_gap | domestic | 258 | 0.247638 | 0.002610 | 0.003319 | 0.498143 |
| etf_transmission | financial_gap | ETF_only | 258 | 0.228156 | 0.003506 | 0.004432 | 0.650638 |
| etf_transmission | financial_gap | delayed_foreign_ETF | 258 | 0.252558 | 0.003712 | 0.004711 | 0.573303 |
| etf_transmission | financial_gap | direct_foreign_ETF | 258 | 0.229019 | 0.003527 | 0.004481 | 0.621088 |
| etf_transmission | financial_gap | domestic | 258 | 0.253019 | 0.003706 | 0.004707 | 0.561808 |
| etf_transmission | it_gap | ETF_only | 258 | 0.237860 | 0.004960 | 0.006507 | 0.593057 |
| etf_transmission | it_gap | delayed_foreign_ETF | 258 | 0.260991 | 0.005319 | 0.006949 | 0.524590 |
| etf_transmission | it_gap | direct_foreign_ETF | 258 | 0.242945 | 0.005031 | 0.006616 | 0.571119 |
| etf_transmission | it_gap | domestic | 258 | 0.261910 | 0.005311 | 0.006943 | 0.510608 |
| etf_transmission | it_relative | ETF_only | 258 | 0.251092 | 0.008439 | 0.011405 | 0.532586 |
| etf_transmission | it_relative | delayed_foreign_ETF | 258 | 0.265729 | 0.008604 | 0.011723 | 0.482196 |
| etf_transmission | it_relative | direct_foreign_ETF | 258 | 0.262776 | 0.008595 | 0.011683 | 0.539206 |
| etf_transmission | it_relative | domestic | 258 | 0.264583 | 0.008593 | 0.011709 | 0.489995 |
| etf_transmission | session_risk | ETF_only | 257 | — | 0.001630 | 0.002231 | — |
| etf_transmission | session_risk | delayed_foreign_ETF | 257 | — | 0.001345 | 0.001917 | — |
| etf_transmission | session_risk | direct_foreign_ETF | 257 | — | 0.001356 | 0.001928 | — |
| etf_transmission | session_risk | domestic | 257 | — | 0.001353 | 0.001930 | — |
| sector_network | bank_gap | domestic | 258 | 0.249515 | 0.003594 | 0.004511 | 0.569264 |
| sector_network | bank_gap | targeted_block | 258 | 0.217232 | 0.003341 | 0.004239 | 0.659091 |
| sector_network | bank_gap | targeted_stale | 258 | 0.256477 | 0.003612 | 0.004544 | 0.557720 |
| sector_network | bank_relative | domestic | 258 | 0.258262 | 0.002832 | 0.003856 | 0.530827 |
| sector_network | bank_relative | targeted_block | 258 | 0.262389 | 0.002856 | 0.003902 | 0.515308 |
| sector_network | bank_relative | targeted_stale | 258 | 0.260050 | 0.002846 | 0.003888 | 0.538586 |
| sector_network | broad_gap | domestic | 258 | 0.258127 | 0.003083 | 0.003864 | 0.568783 |
| sector_network | broad_gap | targeted_block | 258 | 0.208384 | 0.002728 | 0.003448 | 0.673385 |
| sector_network | broad_gap | targeted_stale | 258 | 0.267734 | 0.003119 | 0.003949 | 0.532783 |
| sector_network | energy_gap | domestic | 258 | 0.247638 | 0.002610 | 0.003319 | 0.498143 |
| sector_network | energy_gap | targeted_block | 258 | 0.202395 | 0.002301 | 0.002911 | 0.647312 |
| sector_network | energy_gap | targeted_stale | 258 | 0.250329 | 0.002630 | 0.003354 | 0.501466 |
| sector_network | energy_relative | domestic | 258 | 0.261540 | 0.004750 | 0.006418 | 0.537323 |
| sector_network | energy_relative | targeted_block | 258 | 0.257671 | 0.004723 | 0.006381 | 0.547639 |
| sector_network | energy_relative | targeted_stale | 258 | 0.264076 | 0.004786 | 0.006462 | 0.518045 |
| sector_network | it_gap | domestic | 258 | 0.261910 | 0.005311 | 0.006943 | 0.510608 |
| sector_network | it_gap | targeted_block | 258 | 0.237461 | 0.004910 | 0.006509 | 0.599807 |
| sector_network | it_gap | targeted_stale | 258 | 0.262329 | 0.005332 | 0.006953 | 0.507775 |
| sector_network | it_relative | domestic | 258 | 0.264583 | 0.008593 | 0.011709 | 0.489995 |
| sector_network | it_relative | targeted_block | 258 | 0.265971 | 0.008621 | 0.011726 | 0.487002 |
| sector_network | it_relative | targeted_stale | 258 | 0.263675 | 0.008581 | 0.011692 | 0.499607 |
| sector_network | session_risk | domestic | 257 | — | 0.001353 | 0.001930 | — |
| sector_network | session_risk | targeted_block | 257 | — | 0.001366 | 0.001940 | — |
| sector_network | session_risk | targeted_stale | 257 | — | 0.001353 | 0.001926 | — |

## Dedicated ETF block versus domestic predictors

| target | metric | n | candidate loss | control loss | gain | early gain | later gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| it_gap | brier | 258 | 0.242945 | 0.261910 | 0.018965 | 0.039875 | -0.000994 | -0.003329 | 0.041260 |
| it_gap | crps | 258 | 0.005031 | 0.005311 | 0.000280 | 0.000466 | 0.000103 | 0.000036 | 0.000524 |
| bank_gap | brier | 258 | 0.231533 | 0.249515 | 0.017982 | 0.012074 | 0.023621 | 0.003005 | 0.032959 |
| bank_gap | crps | 258 | 0.003440 | 0.003594 | 0.000154 | 0.000132 | 0.000175 | 0.000056 | 0.000252 |
| financial_gap | brier | 258 | 0.229019 | 0.253019 | 0.024000 | 0.016283 | 0.031367 | 0.013096 | 0.034905 |
| financial_gap | crps | 258 | 0.003527 | 0.003706 | 0.000179 | 0.000148 | 0.000208 | 0.000088 | 0.000269 |
| broad_gap | brier | 258 | 0.195753 | 0.258127 | 0.062374 | 0.085016 | 0.040761 | 0.039629 | 0.085119 |
| broad_gap | crps | 258 | 0.002667 | 0.003083 | 0.000417 | 0.000541 | 0.000298 | 0.000216 | 0.000617 |
| energy_gap | brier | 258 | 0.231205 | 0.247638 | 0.016432 | 0.015297 | 0.017517 | -0.003294 | 0.036159 |
| energy_gap | crps | 258 | 0.002455 | 0.002610 | 0.000155 | 0.000180 | 0.000132 | 0.000004 | 0.000307 |
| it_relative | brier | 258 | 0.262776 | 0.264583 | 0.001807 | 0.000265 | 0.003279 | -0.001883 | 0.005498 |
| it_relative | crps | 258 | 0.008595 | 0.008593 | -0.000003 | -0.000023 | 0.000017 | -0.000076 | 0.000071 |
| bank_relative | brier | 258 | 0.257411 | 0.258262 | 0.000851 | 0.001222 | 0.000496 | -0.003139 | 0.004841 |
| bank_relative | crps | 258 | 0.002831 | 0.002832 | 0.000001 | 0.000004 | -0.000002 | -0.000026 | 0.000028 |
| session_risk | crps | 257 | 0.001356 | 0.001353 | -0.000003 | -0.000003 | -0.000002 | -0.000011 | 0.000005 |

## Feeding earlier fitted sector forecasts into NIFTY models

| target | model | n | brier | crps | mae | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| five | ETF_disagreement | 265 | 0.244544 | 0.010980 | 0.014641 | 0.597829 |
| five | additive_ETFs | 265 | 0.242811 | 0.010898 | 0.014505 | 0.600312 |
| five | domestic | 265 | 0.244661 | 0.010992 | 0.014622 | 0.589282 |
| five | foreign_sector_stack | 265 | 0.247075 | 0.010981 | 0.014621 | 0.574180 |
| gap | ETF_disagreement | 258 | 0.228745 | 0.003017 | 0.003857 | 0.650541 |
| gap | additive_ETFs | 258 | 0.230124 | 0.003018 | 0.003855 | 0.646454 |
| gap | domestic | 258 | 0.257213 | 0.003238 | 0.004115 | 0.576983 |
| gap | foreign_sector_stack | 258 | 0.207725 | 0.002798 | 0.003601 | 0.673918 |
| one | ETF_disagreement | 258 | 0.250626 | 0.004879 | 0.006613 | 0.538582 |
| one | additive_ETFs | 258 | 0.249574 | 0.004862 | 0.006603 | 0.546394 |
| one | domestic | 258 | 0.254857 | 0.005007 | 0.006763 | 0.522536 |
| one | foreign_sector_stack | 258 | 0.233407 | 0.004639 | 0.006324 | 0.596514 |
| regular | ETF_disagreement | 258 | 0.250028 | 0.003707 | 0.005059 | 0.551227 |
| regular | additive_ETFs | 258 | 0.249514 | 0.003703 | 0.005056 | 0.567100 |
| regular | domestic | 258 | 0.249278 | 0.003693 | 0.005046 | 0.524170 |
| regular | foreign_sector_stack | 258 | 0.247401 | 0.003691 | 0.005046 | 0.532828 |
| twentyone | ETF_disagreement | 217 | 0.302129 | 0.031345 | 0.038813 | 0.515013 |
| twentyone | additive_ETFs | 217 | 0.294932 | 0.030962 | 0.038288 | 0.522606 |
| twentyone | domestic | 217 | 0.295068 | 0.031064 | 0.038430 | 0.495125 |
| twentyone | foreign_sector_stack | 217 | 0.297280 | 0.031445 | 0.038777 | 0.513848 |

The downstream stack's historical and current sector predictions are each built at their own past or current decision, using only sector labels already matured at that point. The domestic and direct-ETF benchmarks use the same target and dates. Complete intermediate returns and future foreign observations never enter the issue-time prediction layer. The IT and financial links can help with specific open targets without providing matching improvement after domestic price discovery or for the longer NIFTY endpoints.

[ETF provenance and market-local clocks](us-etf-source-receipt.json) · [Sector scores](network-sectors-scores.csv.gz) · [NIFTY direct and sector stack forecasts](network-nifty-scores.csv.gz) · [Matched gains and intervals](session-matched-evidence.csv)
