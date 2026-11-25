# V20 Forward Research Ledger

The refresh at 2026-11-25T19:14:30.880328+05:30 verifies 5 cash sessions after the historical freeze. The original V4/V5 issue hashes and the exact V19 reference file are preserved. The November 25 V4 diagnostic recorded **+1.7010%**, from **25,387.40 to 25,819.25**, against LightGBM and sector up probabilities originally set at **70.84%** and **68.05%**. It preserves its late-diagnostic classification. Other original outcomes await their own confirmed target sequence and maturity.

| version | key | classification | horizon | target | reconciled | status | return  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V4 | 2026-11-17\|LATE_DIAGNOSTIC | prospective before endpoint; late first-session diagnostic | 21 | 2026-12-17 | 5 | pending completion and publication | — |
| V4 | 2026-11-17\|LATE_DIAGNOSTIC | prospective before endpoint; late first-session diagnostic | 5 | 2026-11-25 | 5 | resolved on original target | 0.017010 |
| V5 | h5-L01 | forward experimental before first target session | 5 | 2026-11-26 | 4 | pending completion and publication | — |
| V5 | h5-I03_nosize | forward experimental before first target session | 5 | 2026-11-26 | 4 | pending completion and publication | — |
| V5 | h21-E00 | forward experimental before first target session | 21 | 2026-12-18 | 4 | pending completion and publication | — |
| V5 | h21-I01_legacy | forward experimental before first target session | 21 | 2026-12-18 | 4 | pending completion and publication | — |

| model | issued at | horizon | target | status |
| --- | --- | --- | --- | --- |
| monthly_neutral_reference | 2026-11-25T16:56:31.987650+05:30 | 21 | 2026-12-24 | pending verified endpoint |
| cash_close_GJR_risk | 2026-11-25T16:56:31.987650+05:30 | 5 | 2026-12-02 | pending verified endpoint |
| cash_close_GJR_risk | 2026-11-25T16:56:31.987650+05:30 | 21 | 2026-12-24 | pending verified endpoint |

V20's evening references were frozen before the first target session. The weekly symmetric law has return quantiles. Raw ATM, IV/RV and EGARCH rows are annualized volatility quantiles. The raw ATM and blend use identified dated call and put marks and total-variance interpolation. The monthly EGARCH reference measures expansion relative to **1.25 times** currently eligible trailing volatility. V14, V18, V19 monthly positioning and GIFT opening preserve their specific morning issue guards. All targets fall in 2026.

| model | issued at | horizon | target | p up | q10 | median | q90 | p expansion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weekly_symmetric | 2026-11-25T19:14:38.156037+05:30 | 5 | 2026-12-02 | 0.500000 | -0.023282 | 0.000000 | 0.023282 | — |
| monthly_student_t_egarch_expansion | 2026-11-25T19:14:38.156037+05:30 | 21 | 2026-12-24 | — | 0.096277 | 0.140996 | 0.212471 | 0.067057 |
| cash_close_ATM_IV | 2026-11-25T19:14:38.156037+05:30 | 5 | 2026-12-02 | — | 0.095053 | 0.163690 | 0.318745 | — |
| cash_close_IV_RV_blend | 2026-11-25T19:14:38.156037+05:30 | 5 | 2026-12-02 | — | 0.097507 | 0.167915 | 0.326972 | — |

[forward-ledger.json](forward-ledger.json) · [forward-refresh-receipt.json](forward-refresh-receipt.json) · [forward/new-issues.json](forward/new-issues.json) · [forward/options-probes.json](forward/options-probes.json) · [NSE 2026 cash calendar](https://archives.nseindia.com/content/circulars/CMTR71775.pdf) · [Upstox option-chain specification](https://upstox.com/developer/api-documentation/get-pc-option-chain/)
