# NIFTY V18 — Expectations and market repricing

The daily reaction was known only after the first scored cash session closed. On the next eligible open we compared the observed gap and regular return with directional cues from the filing, published profit expectation errors, remaining uncertainty and peer reaction. Cohorts identify positive news with falling, rising or muted prices and the symmetric negative-news cases. A muted price response is a first-session move within **±0.30%**. Stock forecasts compare these interactions with an equivalent chronological price-reaction parent. Index forecasts use recent documented reactions, breadth disagreement and positive or adverse fundamental surprise, scored on exactly the same subsequent target.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | expectation_repricing | market_reaction_only | brier | 265 | 53 | 0.243264 | 0.241734 | -0.001530 | -0.021201 | 0.018140 |
| 5 | preauction_0855 | expectation_repricing | market_reaction_only | crps | 265 | 53 | 0.011068 | 0.010774 | -0.000294 | -0.000916 | 0.000327 |
| 5 | preauction_0855 | expectation_repricing | market_reaction_only | down_brier | 265 | 53 | 0.206752 | 0.202194 | -0.004558 | -0.017044 | 0.007927 |
| 5 | preauction_0855 | expectation_repricing | market_reaction_only | up_brier | 265 | 53 | 0.187225 | 0.175706 | -0.011520 | -0.030987 | 0.007947 |
| 5 | previous_1700 | expectation_repricing | market_reaction_only | brier | 265 | 53 | 0.242793 | 0.243224 | 0.000431 | -0.018801 | 0.019663 |
| 5 | previous_1700 | expectation_repricing | market_reaction_only | crps | 265 | 53 | 0.011141 | 0.010847 | -0.000295 | -0.000959 | 0.000369 |
| 5 | previous_1700 | expectation_repricing | market_reaction_only | down_brier | 265 | 53 | 0.209109 | 0.204834 | -0.004275 | -0.019020 | 0.010471 |
| 5 | previous_1700 | expectation_repricing | market_reaction_only | up_brier | 265 | 53 | 0.186915 | 0.176424 | -0.010491 | -0.028654 | 0.007673 |
| 21 | preauction_0855 | expectation_repricing | market_reaction_only | brier | 217 | 11 | 0.304356 | 0.342336 | 0.037980 | -0.022035 | 0.097995 |
| 21 | preauction_0855 | expectation_repricing | market_reaction_only | crps | 217 | 11 | 0.029786 | 0.030962 | 0.001177 | -0.001981 | 0.004334 |
| 21 | preauction_0855 | expectation_repricing | market_reaction_only | down_brier | 217 | 11 | 0.305970 | 0.344037 | 0.038067 | -0.030285 | 0.106419 |
| 21 | preauction_0855 | expectation_repricing | market_reaction_only | up_brier | 217 | 11 | 0.245145 | 0.271033 | 0.025888 | -0.018902 | 0.070678 |
| 21 | previous_1700 | expectation_repricing | market_reaction_only | brier | 217 | 11 | 0.301053 | 0.343247 | 0.042194 | -0.024629 | 0.109018 |
| 21 | previous_1700 | expectation_repricing | market_reaction_only | crps | 217 | 11 | 0.029415 | 0.030846 | 0.001431 | -0.002033 | 0.004894 |
| 21 | previous_1700 | expectation_repricing | market_reaction_only | down_brier | 217 | 11 | 0.299508 | 0.340965 | 0.041456 | -0.032774 | 0.115687 |
| 21 | previous_1700 | expectation_repricing | market_reaction_only | up_brier | 217 | 11 | 0.243895 | 0.272956 | 0.029061 | -0.019662 | 0.077783 |

| signal source | business | price reaction | horizon | metric | n | different dates | mean | low | high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exchange_text | positive business | stock fell | 1 | matched_abnormal | 5 | 5 | 0.003331 | -0.008742 | 0.015404 |
| exchange_text | positive business | stock fell | 1 | peer_excess | 5 | 5 | 0.003883 | -0.005371 | 0.013136 |
| exchange_text | positive business | stock fell | 5 | matched_abnormal | 5 | 5 | -0.047632 | -0.122325 | 0.027061 |
| exchange_text | positive business | stock fell | 5 | peer_excess | 5 | 5 | -0.000172 | -0.026772 | 0.026427 |
| exchange_text | positive business | stock fell | 21 | matched_abnormal | 5 | 5 | 0.007780 | -0.143135 | 0.158696 |
| exchange_text | positive business | stock fell | 21 | peer_excess | 5 | 5 | 0.005549 | -0.036455 | 0.047552 |
| exchange_text | positive business | stock rose | 1 | matched_abnormal | 11 | 11 | -0.002194 | -0.008982 | 0.004593 |
| exchange_text | positive business | stock rose | 1 | peer_excess | 9 | 9 | -0.001599 | -0.007765 | 0.004566 |
| exchange_text | positive business | stock rose | 5 | matched_abnormal | 11 | 11 | -0.019585 | -0.040206 | 0.001036 |
| exchange_text | positive business | stock rose | 5 | peer_excess | 9 | 9 | -0.005239 | -0.018188 | 0.007709 |
| exchange_text | positive business | stock rose | 21 | matched_abnormal | 11 | 11 | -0.063918 | -0.112484 | -0.015351 |
| exchange_text | positive business | stock rose | 21 | peer_excess | 9 | 9 | 0.021736 | -0.014090 | 0.057562 |
| structured | negative business | stock fell | 1 | matched_abnormal | 49 | 39 | 0.001071 | -0.003891 | 0.006034 |
| structured | negative business | stock fell | 1 | peer_excess | 49 | 39 | -0.001296 | -0.003768 | 0.001176 |
| structured | negative business | stock fell | 5 | matched_abnormal | 48 | 38 | -0.005016 | -0.017504 | 0.007473 |
| structured | negative business | stock fell | 5 | peer_excess | 48 | 38 | 0.003114 | -0.002151 | 0.008378 |
| structured | negative business | stock fell | 21 | matched_abnormal | 40 | 32 | -0.017401 | -0.045050 | 0.010247 |
| structured | negative business | stock fell | 21 | peer_excess | 40 | 32 | -0.004907 | -0.020651 | 0.010836 |
| structured | negative business | stock rose | 1 | matched_abnormal | 49 | 43 | 0.002276 | -0.002172 | 0.006723 |
| structured | negative business | stock rose | 1 | peer_excess | 49 | 43 | 0.001116 | -0.001078 | 0.003311 |
| structured | negative business | stock rose | 5 | matched_abnormal | 48 | 42 | 0.006618 | -0.005197 | 0.018432 |
| structured | negative business | stock rose | 5 | peer_excess | 48 | 42 | 0.001509 | -0.002536 | 0.005554 |
| structured | negative business | stock rose | 21 | matched_abnormal | 38 | 33 | 0.006513 | -0.019327 | 0.032353 |
| structured | negative business | stock rose | 21 | peer_excess | 38 | 33 | -0.006248 | -0.020680 | 0.008184 |
| structured | positive business | muted price | 1 | matched_abnormal | 12 | 11 | -0.007082 | -0.015855 | 0.001692 |
| structured | positive business | muted price | 1 | peer_excess | 12 | 11 | 0.002197 | -0.003553 | 0.007947 |
| structured | positive business | muted price | 5 | matched_abnormal | 12 | 11 | -0.017331 | -0.036011 | 0.001350 |
| structured | positive business | muted price | 5 | peer_excess | 12 | 11 | 0.002636 | -0.008977 | 0.014248 |
| structured | positive business | muted price | 21 | matched_abnormal | 11 | 10 | -0.022717 | -0.062155 | 0.016721 |
| structured | positive business | muted price | 21 | peer_excess | 11 | 10 | -0.015576 | -0.038346 | 0.007193 |
| structured | positive business | stock fell | 1 | matched_abnormal | 68 | 48 | -0.002086 | -0.008985 | 0.004813 |
| structured | positive business | stock fell | 1 | peer_excess | 68 | 48 | -0.001542 | -0.004079 | 0.000994 |
| structured | positive business | stock fell | 5 | matched_abnormal | 66 | 46 | -0.005151 | -0.014858 | 0.004555 |
| structured | positive business | stock fell | 5 | peer_excess | 66 | 46 | 0.001533 | -0.003350 | 0.006417 |

[Repricing and disagreement cohorts](announcement-repricing-cohorts.csv) · [Identical-date index forecasts](endpoint-paired-comparisons.csv) · [Post-open tests using known cash moves](postopen-event-matched.csv) · [Input clock audit](event-aggregate-features.csv.gz)
