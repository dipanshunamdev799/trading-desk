# V16 Final research conclusions

The original V15 opening-gap effect survived moving the decision before the NSE opening-price discovery process. Its score was unchanged at 08:30, 08:45 and 08:55, and delaying its completed foreign closes by an extra calendar day removed the gain. The strongest new directional evidence is the GIFT NIFTY vendor futures-change benchmark before the auction. At 08:55 on **248** matched mornings it improved Brier from **0.230235 to 0.100841** and arithmetic CRPS from **0.002985 to 0.001459**, with a 21-session family-adjusted Brier gain interval of **[0.095394, 0.163392]**. Directional accuracy for the point-in-time vendor probability was **88.71%**, and after the broad rollover exclusion its score was **0.095052** on **180** mornings. Its actual calculation uses a prior futures mark and conservatively completed morning bars. Exact contract mapping and original delivery receipts remain unknown. Directly adding a broader global block to the GIFT signal generally lowered performance.

The GIFT-first model improved weekly barrier-touch Brier at original issue from **0.143371 to 0.132201** at **265** origins, with an adjusted gain interval of **[0.002519, 0.019820]**. The day-one improvement was larger, from **0.081827 to 0.054292**. For levels still untouched after day one, Brier was **0.141434 versus 0.139330**, with [-0.004448, 0.008657] gain bounds. Forecasting when the first hit happens and which side the market finally closes on remain separate. Pre-open foreign sector signals were most effective at their respective intermediate Indian opens. Later relative and regular-session outcomes were harder. The later cash return in the gap direction was only about one half of cases. Volatility expansion retained the established weekly fixed-blend and monthly Student-t EGARCH Brier leads.

## Decay of a fitted GIFT contribution compared with domestic predictors

| target | n | control loss | candidate loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- |
| gap | 248 | 0.258776 | 0.152550 | 0.106226 | 0.058556 | 0.153897 |
| firsthour | 248 | 0.263130 | 0.259900 | 0.003230 | -0.000957 | 0.007417 |
| regular | 248 | 0.245936 | 0.246197 | -0.000261 | -0.004854 | 0.004332 |
| one | 248 | 0.254046 | 0.207457 | 0.046589 | 0.020369 | 0.072809 |
| next_next_close | 247 | 0.254242 | 0.254430 | -0.000188 | -0.005553 | 0.005177 |
| two | 247 | 0.254704 | 0.232798 | 0.021906 | 0.008571 | 0.035241 |
| three | 246 | 0.243484 | 0.228590 | 0.014894 | 0.004535 | 0.025253 |
| five | 253 | 0.248337 | 0.242828 | 0.005509 | -0.006691 | 0.017710 |
| ten | 241 | 0.291361 | 0.285699 | 0.005662 | -0.002701 | 0.014024 |
| twentyone | 210 | 0.297872 | 0.297077 | 0.000794 | -0.017558 | 0.019146 |

## Original weekly and monthly results

| horizon | model | n | brier | endpoint crps | log loss | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_sign_shrinkage | 265 | 0.228529 | 0.010457 | 0.648943 | 0.636001 |
| 5 | V15_gjr_restart | 265 | 0.250763 | 0.010922 | 0.694695 | 0.573516 |
| 5 | decomposed_gift | 265 | 0.242618 | 0.010493 | 0.681034 | 0.608166 |
| 5 | prev_mean_reversion | 265 | 0.252927 | 0.010927 | 0.699259 | 0.523504 |
| 5 | session_state | 265 | 0.239546 | 0.010466 | 0.673356 | 0.598724 |
| 21 | V14_domestic_GJR | 217 | 0.245042 | 0.024989 | 0.683095 | 0.502675 |
| 21 | V15_gjr_restart | 217 | 0.251376 | 0.024694 | 0.695900 | 0.524072 |
| 21 | decomposed_gift | 217 | 0.273803 | 0.027288 | 0.760809 | 0.501553 |
| 21 | prev_mean_reversion | 217 | 0.248912 | 0.025900 | 0.690913 | 0.496160 |
| 21 | session_state | 217 | 0.270103 | 0.027116 | 0.749273 | 0.507420 |

Evidence is strongest for a morning opening-gap forecast and early passage probabilities. Five- and 21-session original-issue directional gains remain unestablished against the strongest archived predictors. The archive tracks the completed refresh and only the original forward benchmark issues. The historical score confidence bands quantify this replay and require independent prospective validation.

[Full objective-specific leaderboards](V16_COMPLETE_MODEL_COMPARISON.md) · [Exact original-gap audit](V16_OPENING_GAP_REPRODUCTION_AND_TIMING_AUDIT.md) · [Offshore basis and rollover sensitivity](V16_OFFSHORE_PRICE_DISCOVERY.md) · [Forward status](V16_FORWARD_RESEARCH_LEDGER.md) · [Opening-gap and information decay figure](opening-gap-and-decay.png)
