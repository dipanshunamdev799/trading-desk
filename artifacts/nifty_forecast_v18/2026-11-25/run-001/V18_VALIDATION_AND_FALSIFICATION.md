# NIFTY V18 — Validation and falsification

The original return ledger has **31,812** predictions and full laws with strictly earlier maturity dates. The source audit checked the complete announcement clock inventory and exact-date corporate, fundamental, financial-release and stock-reaction availability. The dated fundamental comparison rejects prior-period inputs whose release was after the current report. Across **16** tests, future-data changes left the historical feature values and tested fits unchanged. Adding exact copies of an existing feature left the fitted residual forecast unchanged. Initial filings and amendments preserve their own availability. Meeting revisions change the event calendar only on publication. Earlier daily derivative and delivery observations have a separate EOD guard.

The primary source study removes publication duplicates. Falsifiers delay notice availability by **24 and 72 hours**, shift feature dates, rotate completed training observations, screen for materiality, remove dominant firms and clustered release bursts, exclude earnings, and test fixed alternative semantics. The event study uses same-date matched peer controls, and the transfer arm also reruns with different categories and issuer histories. Blocks of **5, 10, 21 and 42 sessions** and **1,500 draws** preserve dependence across overlapping index windows. Adjusted intervals cover the comparisons within each reported group. The **23** chronology-preserving null refits reselect the best of the same three event feature families across the two original horizons. They do not account for cumulative predecessor search.

| metric | observed selected gain | candidate | horizon | null replicates | null median selected gain | null 95 percentile | tail probability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| brier | -0.005563 | counts | 5 | 23 | -0.002228 | 0.028776 | 0.708333 |
| crps | -0.000216 | counts | 5 | 23 | -0.000128 | 0.000081 | 0.625000 |

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | alternative_text | counts | brier | 265 | 53 | 0.244871 | 0.243837 | -0.001034 | -0.002161 | 0.000093 |
| 5 | preauction_0855 | alternative_text | counts | crps | 265 | 53 | 0.010888 | 0.010874 | -0.000015 | -0.000060 | 0.000030 |
| 5 | preauction_0855 | omit_heavyweights | counts | brier | 265 | 53 | 0.243882 | 0.243837 | -0.000045 | -0.003150 | 0.003059 |
| 5 | preauction_0855 | omit_heavyweights | counts | crps | 265 | 53 | 0.010881 | 0.010874 | -7.42e-06 | -0.000074 | 0.000059 |
| 5 | preauction_0855 | omit_earnings | counts | brier | 265 | 53 | 0.243867 | 0.243837 | -0.000030 | -0.003078 | 0.003018 |
| 5 | preauction_0855 | omit_earnings | counts | crps | 265 | 53 | 0.010881 | 0.010874 | -7.31e-06 | -0.000074 | 0.000059 |
| 5 | preauction_0855 | delayed_24h | counts | brier | 265 | 53 | 0.245103 | 0.243837 | -0.001266 | -0.006873 | 0.004340 |
| 5 | preauction_0855 | delayed_24h | counts | crps | 265 | 53 | 0.010910 | 0.010874 | -0.000036 | -0.000170 | 0.000097 |
| 5 | preauction_0855 | delayed_72h | counts | brier | 265 | 53 | 0.246679 | 0.243837 | -0.002842 | -0.010322 | 0.004638 |
| 5 | preauction_0855 | delayed_72h | counts | crps | 265 | 53 | 0.010942 | 0.010874 | -0.000068 | -0.000235 | 0.000099 |
| 5 | preauction_0855 | material_only | counts | brier | 265 | 53 | 0.246663 | 0.243837 | -0.002826 | -0.011318 | 0.005665 |
| 5 | preauction_0855 | material_only | counts | crps | 265 | 53 | 0.010930 | 0.010874 | -0.000057 | -0.000255 | 0.000142 |
| 5 | preauction_0855 | omit_large_arrivals | counts | brier | 265 | 53 | 0.243861 | 0.243837 | -0.000024 | -0.003115 | 0.003068 |
| 5 | preauction_0855 | omit_large_arrivals | counts | crps | 265 | 53 | 0.010881 | 0.010874 | -7.46e-06 | -0.000074 | 0.000059 |
| 5 | preauction_0855 | shifted_inputs | clock_structural | brier | 265 | 53 | 0.249062 | 0.238274 | -0.010788 | -0.026590 | 0.005014 |
| 5 | preauction_0855 | shifted_inputs | clock_structural | crps | 265 | 53 | 0.011186 | 0.010658 | -0.000528 | -0.000896 | -0.000159 |
| 5 | preauction_0855 | blocked_placebo | clock_structural | brier | 265 | 53 | 0.245366 | 0.238274 | -0.007092 | -0.025067 | 0.010883 |
| 5 | preauction_0855 | blocked_placebo | clock_structural | crps | 265 | 53 | 0.010840 | 0.010658 | -0.000182 | -0.000796 | 0.000431 |
| 5 | preauction_0855 | alternative_text | clock_structural | brier | 265 | 53 | 0.244871 | 0.238274 | -0.006597 | -0.020744 | 0.007551 |
| 5 | preauction_0855 | alternative_text | clock_structural | crps | 265 | 53 | 0.010888 | 0.010658 | -0.000230 | -0.000526 | 0.000065 |
| 5 | preauction_0855 | omit_heavyweights | clock_structural | brier | 265 | 53 | 0.243882 | 0.238274 | -0.005608 | -0.019279 | 0.008063 |
| 5 | preauction_0855 | omit_heavyweights | clock_structural | crps | 265 | 53 | 0.010881 | 0.010658 | -0.000223 | -0.000509 | 0.000063 |
| 5 | preauction_0855 | omit_earnings | clock_structural | brier | 265 | 53 | 0.243867 | 0.238274 | -0.005592 | -0.019197 | 0.008012 |
| 5 | preauction_0855 | omit_earnings | clock_structural | crps | 265 | 53 | 0.010881 | 0.010658 | -0.000223 | -0.000508 | 0.000063 |
| 5 | preauction_0855 | delayed_24h | clock_structural | brier | 265 | 53 | 0.245103 | 0.238274 | -0.006829 | -0.019687 | 0.006030 |
| 5 | preauction_0855 | delayed_24h | clock_structural | crps | 265 | 53 | 0.010910 | 0.010658 | -0.000252 | -0.000539 | 0.000035 |
| 5 | preauction_0855 | delayed_72h | clock_structural | brier | 265 | 53 | 0.246679 | 0.238274 | -0.008404 | -0.021317 | 0.004509 |
| 5 | preauction_0855 | delayed_72h | clock_structural | crps | 265 | 53 | 0.010942 | 0.010658 | -0.000283 | -0.000594 | 0.000027 |
| 5 | preauction_0855 | material_only | clock_structural | brier | 265 | 53 | 0.246663 | 0.238274 | -0.008389 | -0.024683 | 0.007905 |
| 5 | preauction_0855 | material_only | clock_structural | crps | 265 | 53 | 0.010930 | 0.010658 | -0.000272 | -0.000600 | 0.000056 |
| 5 | preauction_0855 | omit_large_arrivals | clock_structural | brier | 265 | 53 | 0.243861 | 0.238274 | -0.005586 | -0.019274 | 0.008102 |
| 5 | preauction_0855 | omit_large_arrivals | clock_structural | crps | 265 | 53 | 0.010881 | 0.010658 | -0.000223 | -0.000509 | 0.000063 |
| 5 | previous_1700 | alternative_text | counts | brier | 265 | 53 | 0.245207 | 0.244096 | -0.001111 | -0.003096 | 0.000874 |
| 5 | previous_1700 | alternative_text | counts | crps | 265 | 53 | 0.010960 | 0.010935 | -0.000025 | -0.000066 | 0.000015 |
| 5 | previous_1700 | omit_heavyweights | counts | brier | 265 | 53 | 0.243981 | 0.244096 | 0.000115 | -0.004295 | 0.004525 |
| 5 | previous_1700 | omit_heavyweights | counts | crps | 265 | 53 | 0.010949 | 0.010935 | -0.000014 | -0.000119 | 0.000091 |
| 5 | previous_1700 | omit_earnings | counts | brier | 265 | 53 | 0.243918 | 0.244096 | 0.000178 | -0.004163 | 0.004520 |
| 5 | previous_1700 | omit_earnings | counts | crps | 265 | 53 | 0.010949 | 0.010935 | -0.000013 | -0.000118 | 0.000091 |
| 5 | previous_1700 | delayed_24h | counts | brier | 265 | 53 | 0.245343 | 0.244096 | -0.001247 | -0.006438 | 0.003944 |
| 5 | previous_1700 | delayed_24h | counts | crps | 265 | 53 | 0.010977 | 0.010935 | -0.000042 | -0.000192 | 0.000108 |
| 5 | previous_1700 | delayed_72h | counts | brier | 265 | 53 | 0.248064 | 0.244096 | -0.003968 | -0.013461 | 0.005526 |
| 5 | previous_1700 | delayed_72h | counts | crps | 265 | 53 | 0.011028 | 0.010935 | -0.000092 | -0.000297 | 0.000113 |
| 5 | previous_1700 | material_only | counts | brier | 265 | 53 | 0.247236 | 0.244096 | -0.003140 | -0.014174 | 0.007894 |
| 5 | previous_1700 | material_only | counts | crps | 265 | 53 | 0.011007 | 0.010935 | -0.000072 | -0.000326 | 0.000181 |

[Full timing and validation receipt](validation-receipt.json) · [Sentinel cases](future-information-sentinels.csv) · [Refit and reselection controls](refit-reselection-summary.csv) · [Cash categories and duplicate audit](archive-category-counts.csv) · [Point-in-time fundamentals](structured-financial-facts.csv.gz)
