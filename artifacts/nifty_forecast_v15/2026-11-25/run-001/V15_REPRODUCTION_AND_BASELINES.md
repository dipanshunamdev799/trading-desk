# V15 reproduction and baselines

The frozen V14 chain used **2025–2026** and finished on **2026-11-17**. V15 matched **3,374** risk rows, **964** expansion probabilities, **434** replayed joint-path marginals, **482** standalone endpoint rows and **4,820** fixed-barrier outcomes. Maximum numerical differences were 0.0 for the matched volatility point predictions and 0.0 for the expansion probabilities. V14 used 2,048 coherent 21-session OHLC paths at 265 origins, with weekly paths taken from their first five steps. V15 preserves the individual benchmark laws, including the separately fitted point and endpoint models.

## Volatility

| horizon | model | origins | mae | variance qlike |
| --- | --- | --- | --- | --- |
| 5 | V13_75IV25RV | 265 | 0.038196 | 0.273634 |
| 5 | V13_GJR | 265 | 0.040318 | 0.359870 |
| 5 | V13_calibrated_IV | 265 | 0.037517 | 0.338910 |
| 5 | V13_raw_ATM | 265 | 0.037814 | 0.276187 |
| 5 | V13_trailing | 265 | 0.046394 | 0.418006 |
| 5 | blend_gjr_iv | 265 | 0.037978 | 0.287184 |
| 5 | gjr_ivx | 265 | 0.037402 | 0.299575 |
| 21 | V13_75IV25RV | 217 | 0.040894 | 0.257953 |
| 21 | V13_GJR | 217 | 0.033179 | 0.199677 |
| 21 | V13_bracketed_IV | 217 | 0.039406 | 0.267623 |
| 21 | V13_calibrated_IV | 217 | 0.040652 | 0.586417 |
| 21 | V13_trailing | 217 | 0.048044 | 0.487043 |
| 21 | blend_gjr_iv | 217 | 0.033780 | 0.247374 |
| 21 | gjr_ivx | 217 | 0.037160 | 0.310001 |

## Expansion

| horizon | model | origins | brier | forecast rate | actual rate |
| --- | --- | --- | --- | --- | --- |
| 5 | historical | 265 | 0.222296 | 0.329628 | 0.328302 |
| 5 | iv_raw | 265 | 0.155657 | 0.356195 | 0.328302 |
| 21 | historical | 217 | 0.299434 | 0.210386 | 0.373272 |
| 21 | iv_raw | 217 | 0.186036 | 0.278692 | 0.373272 |

For horizon H, raw IV uses the chi-square survival probability evaluated at H × (1.25 × trailing H-session annualized RV / ATM IV)² with H degrees of freedom. The historical benchmark uses the most recent 185 prior rows from the fold-month sample, retaining eligible labels that matured before that fold. Its frequency is (events + 0.75) / (observations + 1.50). Weekly and monthly variance levels and event probabilities retain the original basis, definitions and as-of rules.

## Endpoints

| horizon | model | origins | brier | endpoint crps |
| --- | --- | --- | --- | --- |
| 5 | sign_shrinkage | 265 | 0.228529 | 0.010457 |
| 21 | domestic_location_gjr_scale | 217 | 0.245042 | 0.024989 |

## Joint-path marginals

| horizon | model | target | origins | crps | coverage80 |
| --- | --- | --- | --- | --- | --- |
| 21 | gjr_student | range | 217 | 0.015422 | 0.764977 |
| 21 | regime_state | endpoint_return | 217 | 0.024750 | 0.741935 |

The weekly V13 diffusion range reference of **0.005793** comes from the individually archived V13 diffusion range scores in V14. The monthly Student-GJR range reference comes from independently re-scoring the original V14 joint atoms.

## Fixed-barrier touch

| horizon | model | cases | origins | brier |
| --- | --- | --- | --- | --- |
| 5 | trend_shrink | 2,650 | 265 | 0.143371 |
| 21 | trend_persistent | 2,170 | 217 | 0.181085 |

[Replay receipt](benchmark-replay.json) [Archived range replay](replay-path.csv) [Original V14 research index](../../../nifty_forecast_v14/2026-11-25/run-001/NIFTY_V14_RESEARCH.md) [CRPS and proper scoring rules](https://doi.org/10.1198/016214506000001437)
