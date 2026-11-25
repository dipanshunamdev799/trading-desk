# V20 Cumulative Information Registry

The registry specifies all 18 required information families. A raw price, report or contract count retains its source definition. Relative returns, exposure ratios, breadth and filing aggregates are constructed measures. The principal-component state and multi-output coefficients are fitted representations. The cross-version reference is stored alongside the **matched 08:55 V20 fresh-information comparison** so that the historical benchmark, live eligibility and source completeness remain inspectable.

| family | earlier versions | source and availability | known 1700 | known 0855 | archived matched evidence | classification |
| --- | --- | --- | --- | --- | --- | --- |
| offshore_gift | V16–V17 | Dated offshore index candles; conservative end-of-bar allowance | 392 | 393 | V16/V17 opening gap: 248 origins, Brier .100841, accuracy .887097 | Replicated retrospective association |
| global_equities | V5–V17 | Dated foreign market equity returns and time-zone release/close allowance | 0 | 402 | V11 RSP/SPY increment .004731 earlier and −.033262 later versus the US cap/sector parent | Cohort-dependent |
| domestic_internals | V1–V19 | Native price, defensive rotation and futures basis known at stated clock | 402 | 402 | V8 native panel later Brier gain .002208 and V11 native phase-zero .231728 on 265 overlapping weekly origins | Cohort-dependent |
| financial_rotation | V7–V19 | Published bank/finance indices and realized sector returns, guarded by release | 402 | 402 | V8 bank-only later Brier gain .008170 and V9 bank residual later .005741 | Cohort-dependent |
| equal_weight_breadth | V10–V19 | Official NIFTY 50/500 equal-weight relative changes as of the cash decision window | 402 | 402 | V11 V9 residual .003371 earlier and .004848 later Brier gains | Replicated retrospective association |
| stock_participation | V11–V19 | Dated NSE cash archive advance, distribution and lagged activity of eligible stocks | 401 | 402 | V17 date/ISIN breadth audit and V19 sector/stock controls. V19 monthly delivery-plus-price ranks −.02944 | Promising but inconclusive |
| corporate_announcements | V17–V19 | NSE filing eligibility clock with late or duplicate episode handling | 402 | 402 | V18 material and structured corporate residual: native weekly .223481 Brier vs V14 .228529 | Promising but inconclusive |
| structured_financials | V18–V19 | First valid firm/period figures and earlier matched filing comparisons | 334 | 335 | V18 1,063 first firm-period contexts and 870 QoQ revenue comparisons. Ordinary weekly augmentation Brier .248263 at 08:55 | Failed against strong controls |
| participant_futures | V18–V19 | Published NSE category net/gross contracts, next-session 08:15 guard proxy | 401 | 401 | V19 V14 monthly .245042 to .228199 Brier and .024989 to .024010 CRPS; earlier gain .026437, later −.000954 | Cohort-dependent |
| participant_options | V18–V19 | Call and put side aggregates, no usable strike-level participant Greeks | 401 | 401 | V19 monthly views include disagreement and category options counts, primarily reused through the joint candidate | Promising but inconclusive |
| participant_volume | V19 | 466 dated NSE participant-volume reports, opposite sides and market shares audited | 402 | 402 | V19 466 volume days independently audited from OI; conditional V19 risk combined weekly MAE .037158 | Methodologically established |
| delivery | V18–V19 | NSE EQ delivered quantities, percentage normalized using earlier issuer history | 401 | 401 | V19 1,439,636 archive rows. Weekly stock rank −.00318 to +.00300, monthly sector MAE .030702 to .030875 | Failed against strong controls |
| large_transactions | V18–V19 | Date/symbol/size/price grouped disclosures and matched two-leg heuristics | 402 | 402 | V19 2,969 unique legs across 151 dates. Weekly matched block excess .007225 falls to .000637 on size removal | Failed against strong controls |
| atm_iv | V12–V19 | Near-money dated option IV and separately measured actual future volatility | 402 | 402 | V16 raw weekly ATM IV MAE .037814, V16 combined risk .036469 | Replicated retrospective association |
| option_surface | V12–V19 | Authenticated strike surface and previous eligible option-day skew/term observations | 402 | 402 | V14 native Student-t GJR monthly range .015422 is a strong competing control; V12 risk-neutral and realized path outcomes differ | Promising but inconclusive |
| realized_volatility | V12–V19 | Past cash realized volatility and causal GARCH conditional variance | 402 | 402 | V16 monthly GJR MAE .033179 and variance QLIKE .199677; Student EGARCH expansion .172872 | Replicated retrospective association |
| intraday_structure | V8–V19 | Guarded earlier realized opening, midpoint, late profiles and separately timed post-open cases | 395 | 395 | V10 later directional Brier .254052 to .250365. V17 post-open risk snapshots use their own 09:25 and 10:20 windows | Cohort-dependent |
| institutional_flows | V18–V20 | Provisional exchange net and confirmed custodian/Fund populations have distinct clocks and units | 311 | 311 | V19 accepted 64 CDSL days, 36 sector fortnights and 22 AMFI months; 59 comparable daily-custody observations | Unresolved because of insufficient data |

| family | h5 matched | h5 disjoint | h5 gain | h5 earlier gain | h5 later gain | h21 matched | h21 disjoint | h21 gain | h21 earlier gain | h21 later gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| offshore_gift | 256 | 53 | 0.000173 | 0.000239 | 0.000048 | 212 | 11 | 0.000054 | 0.000051 | 0.000058 |
| global_equities | 265 | 53 | -0.000080 | -0.000105 | -0.000033 | 217 | 11 | -0.000042 | -0.000218 | 0.000284 |
| domestic_internals | 265 | 53 | 0.000052 | -0.000089 | 0.000317 | 217 | 11 | -0.000705 | -0.001459 | 0.000695 |
| financial_rotation | 265 | 53 | 0.000064 | 0.000056 | 0.000080 | 217 | 11 | -0.000822 | 0.000378 | -0.003049 |
| equal_weight_breadth | 265 | 53 | 0.000112 | -0.000047 | 0.000411 | 217 | 11 | -0.000591 | -0.000798 | -0.000207 |
| stock_participation | 265 | 53 | -0.000096 | -0.000034 | -0.000213 | 217 | 11 | -0.000743 | -0.000826 | -0.000588 |
| corporate_announcements | 265 | 53 | -0.000123 | -0.000085 | -0.000194 | 217 | 11 | -0.000666 | -0.001711 | 0.001273 |
| structured_financials | 265 | 53 | -0.000118 | -0.000095 | -0.000161 | 217 | 11 | -0.001104 | -0.001637 | -0.000115 |
| participant_futures | 265 | 53 | 0.000272 | 0.000429 | -0.000023 | 217 | 11 | 0.000645 | 0.000441 | 0.001023 |
| participant_options | 265 | 53 | -0.000051 | -0.000086 | 0.000015 | 217 | 11 | 0.001240 | 0.001309 | 0.001112 |
| participant_volume | 265 | 53 | 4.27e-06 | -0.000039 | 0.000085 | 217 | 11 | -0.000382 | -0.000464 | -0.000230 |
| delivery | 264 | 53 | -0.000065 | -0.000180 | 0.000152 | 216 | 11 | -0.000644 | -0.000835 | -0.000285 |
| large_transactions | 265 | 53 | -0.000153 | -0.000190 | -0.000084 | 217 | 11 | -0.000589 | -0.000769 | -0.000254 |
| atm_iv | 265 | 53 | -0.000197 | -0.000411 | 0.000205 | 217 | 11 | -0.001851 | -0.003205 | 0.000663 |
| option_surface | 265 | 53 | -0.000034 | -0.000136 | 0.000158 | 217 | 11 | -0.000984 | -0.001838 | 0.000600 |
| realized_volatility | 265 | 53 | -0.000223 | -0.000366 | 0.000046 | 217 | 11 | -0.002454 | -0.004632 | 0.001586 |
| intraday_structure | 263 | 53 | -0.000078 | -0.000065 | -0.000103 | 217 | 11 | -0.000065 | -0.000105 | 0.000010 |
| institutional_flows | 208 | 42 | 0.000133 | 0.000083 | 0.000197 | 168 | 8 | 0.000075 | -0.000877 | 0.001227 |

The downloadable registry includes exact field lists, known redundancies, the parent and enhanced losses, shifted controls, adjusted bands, failure mechanisms and next questions. The V12 inventory adds historically tested training-memory, overlap, duplicate-feature and distribution-construction mechanisms. The reproducibility of data publication and model arithmetic does not promote a retrospective signal to an independent validation.

[cumulative-information-registry.csv](cumulative-information-registry.csv) · [cumulative-v12-predecessor-registry.csv](cumulative-v12-predecessor-registry.csv) · [registry-receipt.json](registry-receipt.json) · [feature-definitions.json](feature-definitions.json) · [feature-coverage.csv](feature-coverage.csv) · [information-lifetime-matrix.csv](information-lifetime-matrix.csv) · [complementarity-feature-redundancy.csv](complementarity-feature-redundancy.csv)
