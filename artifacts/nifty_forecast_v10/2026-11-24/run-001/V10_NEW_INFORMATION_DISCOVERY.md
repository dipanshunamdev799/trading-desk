# V10 New Information Discovery

**Authoritative equal-weight leadership.** V10 retrieved **466** daily observations each for NIFTY 50 Equal Weight, NIFTY500 Equal Weight and their two cap-weight companions from the NSE daily index archives. Over **403** frozen comparable spot dates the largest vendor–official NIFTY close difference was **0.0000 index points**, with **0** above one point. Inputs are trailing five- and 21-session relative returns. Dated daily historical constituent weights were unavailable in the authenticated inputs. We retained official equal-weight index evidence and left constituent contribution and heavyweight attribution unestimated. [NSE indices historical data](https://www.niftyindices.com/reports/historical-data) · [NSE index data subscriptions](https://www.niftyindices.com/offerings/data-subscription) · [Index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf).

**Synchronized intraday.** The Upstox V3 historical endpoint returned **27,888** 25-minute Bank, Financial, IT and Auto index bars. The panel validated **458** complete aligned regular sessions with all 15 candles per instrument. Opening and closing breadth use the first and last 50 minutes. Additional fields capture synchronized direction, open-to-close leadership shifts and late volatility concentration. Features are available after the last bar closes. The exact eligibility mask applies to both the candidate and matched parent. [Upstox historical candle API](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [Intraday audit](intraday-source-audit.json).

**Derivatives.** Inherited official EOD reports supply lagged near-future basis, OI change, put/call positioning and strike concentration. V10 tested the trailing-median basis residual and ETF-turnover-normalized OI, then parsed the archived instrument and expiry IDs for **466** sessions with two or more dated futures contracts and **22** changes in the front contract. The new features include same-contract futures-minus-cash log returns, prior-lot-matched OI changes per traded underlying unit, OI roll shifts, nearby futures activity and tenor-scaled net carry. The latter measures a combined carry proxy given the absence of an authenticated funding and dividend decomposition. Matched traded near-ATM straddles provide **466** dated premium observations. The premium divided by spot and scaled to a 21-calendar-day tenor represents option-priced risk. V10 compares it with a common dated parent and omits inferred realized direction probabilities. Derivatives input dates use one completed observed-session lag. [NSE archive reports](https://www.nseindia.com/all-reports) · [Dated contract inputs](dated-derivatives-inputs.csv) · [Source checks](dated-derivatives-audit.json).

**Global risk.** The repaired monthly and weekly comparisons use identical eligible target masks, the same causal volatility reconstruction, and extra foreign risk/divergence features drawn from conservatively timed publications. The initial two global-risk fits omitted a target volatility completeness mask and failed across 50 folds. The failures remain logged and the corrected comparisons have distinct names.

## Matched source increments

| horizon | cohort | model | baseline | metric | n | candidate | control | gain | block10_adjusted_low | block10_adjusted_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | early | DATED_FUTURES | DATED_FUTURES_PARENT | brier | 173 | 0.286275 | 0.285113 | -0.001163 | -0.023743 | 0.021418 |
| 5 | early | DATED_FUTURES | DATED_FUTURES_PARENT | crps | 173 | 0.012151 | 0.012005 | -0.000146 | -0.000826 | 0.000535 |
| 5 | later | DATED_FUTURES | DATED_FUTURES_PARENT | brier | 92 | 0.253935 | 0.256111 | 0.002176 | -0.023173 | 0.027525 |
| 5 | later | DATED_FUTURES | DATED_FUTURES_PARENT | crps | 92 | 0.012082 | 0.012152 | 0.000070 | -0.000572 | 0.000712 |
| 5 | early | DATED_STRADDLE | DATED_STRADDLE_PARENT | brier | 173 | 0.289953 | 0.285113 | -0.004840 | -0.030526 | 0.020846 |
| 5 | early | DATED_STRADDLE | DATED_STRADDLE_PARENT | crps | 173 | 0.012415 | 0.012005 | -0.000410 | -0.001356 | 0.000536 |
| 5 | later | DATED_STRADDLE | DATED_STRADDLE_PARENT | brier | 92 | 0.252350 | 0.256111 | 0.003761 | -0.007774 | 0.015296 |
| 5 | later | DATED_STRADDLE | DATED_STRADDLE_PARENT | crps | 92 | 0.012098 | 0.012152 | 0.000054 | -0.000154 | 0.000261 |
| 5 | early | N_DERIV_RAW | BASE10 | brier | 173 | 0.285546 | 0.285113 | -0.000433 | -0.011888 | 0.011021 |
| 5 | early | N_DERIV_RAW | BASE10 | crps | 173 | 0.012047 | 0.012005 | -0.000042 | -0.000314 | 0.000230 |
| 5 | later | N_DERIV_RAW | BASE10 | brier | 92 | 0.265099 | 0.256111 | -0.008988 | -0.039366 | 0.021391 |
| 5 | later | N_DERIV_RAW | BASE10 | crps | 92 | 0.012238 | 0.012152 | -0.000086 | -0.000787 | 0.000616 |
| 5 | early | N_DERIV_STRUCT | N_DERIV_RAW | brier | 173 | 0.284913 | 0.285546 | 0.000633 | -0.007523 | 0.008789 |
| 5 | early | N_DERIV_STRUCT | N_DERIV_RAW | crps | 173 | 0.012044 | 0.012047 | 0.000003 | -0.000198 | 0.000204 |
| 5 | later | N_DERIV_STRUCT | N_DERIV_RAW | brier | 92 | 0.271939 | 0.265099 | -0.006841 | -0.019255 | 0.005574 |
| 5 | later | N_DERIV_STRUCT | N_DERIV_RAW | crps | 92 | 0.012414 | 0.012238 | -0.000177 | -0.000434 | 0.000080 |
| 5 | early | N_EQ_CONTROL | BASE10 | brier | 173 | 0.285113 | 0.285113 | 0.000000 | -0.000000 | 0.000000 |
| 5 | early | N_EQ_CONTROL | BASE10 | crps | 173 | 0.012005 | 0.012005 | 0.000000 | -0.000000 | 0.000000 |
| 5 | later | N_EQ_CONTROL | BASE10 | brier | 92 | 0.256111 | 0.256111 | 0.000000 | -0.000000 | 0.000000 |
| 5 | later | N_EQ_CONTROL | BASE10 | crps | 92 | 0.012152 | 0.012152 | 0.000000 | -0.000000 | 0.000000 |
| 5 | early | N_EQ_OFFICIAL | N_EQ_CONTROL | brier | 173 | 0.281286 | 0.285113 | 0.003827 | -0.014633 | 0.022287 |
| 5 | early | N_EQ_OFFICIAL | N_EQ_CONTROL | crps | 173 | 0.011878 | 0.012005 | 0.000127 | -0.000526 | 0.000780 |
| 5 | later | N_EQ_OFFICIAL | N_EQ_CONTROL | brier | 92 | 0.231236 | 0.256111 | 0.024875 | -0.020740 | 0.070490 |
| 5 | later | N_EQ_OFFICIAL | N_EQ_CONTROL | crps | 92 | 0.011661 | 0.012152 | 0.000491 | -0.000848 | 0.001831 |
| 5 | early | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | brier | 173 | 0.297161 | 0.291913 | -0.005248 | -0.015245 | 0.004750 |
| 5 | early | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | crps | 173 | 0.013448 | 0.013169 | -0.000279 | -0.000647 | 0.000090 |
| 5 | later | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | brier | 92 | 0.253235 | 0.251344 | -0.001891 | -0.014060 | 0.010279 |
| 5 | later | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | crps | 92 | 0.012318 | 0.012374 | 0.000056 | -0.000080 | 0.000192 |
| 5 | early | N_INTRA_CONTROL | BASE10 | brier | 172 | 0.287940 | 0.285708 | -0.002232 | -0.006247 | 0.001783 |
| 5 | early | N_INTRA_CONTROL | BASE10 | crps | 172 | 0.012144 | 0.012053 | -0.000091 | -0.000194 | 0.000012 |
| 5 | later | N_INTRA_CONTROL | BASE10 | brier | 91 | 0.254052 | 0.253995 | -0.000058 | -0.003191 | 0.003076 |
| 5 | later | N_INTRA_CONTROL | BASE10 | crps | 91 | 0.012173 | 0.012164 | -0.000009 | -0.000032 | 0.000013 |
| 5 | early | N_INTRA_PANEL | N_INTRA_CONTROL | brier | 172 | 0.287136 | 0.287940 | 0.000804 | -0.009637 | 0.011246 |
| 5 | early | N_INTRA_PANEL | N_INTRA_CONTROL | crps | 172 | 0.012283 | 0.012144 | -0.000139 | -0.000425 | 0.000147 |
| 5 | later | N_INTRA_PANEL | N_INTRA_CONTROL | brier | 91 | 0.250365 | 0.254052 | 0.003687 | -0.007587 | 0.014962 |
| 5 | later | N_INTRA_PANEL | N_INTRA_CONTROL | crps | 91 | 0.012175 | 0.012173 | -0.000002 | -0.000249 | 0.000245 |
| 5 | early | N_RISK_MATCHED | T_VOL_RISK | brier | 173 | 0.291913 | 0.291913 | 0.000000 | -0.000000 | 0.000000 |
| 5 | early | N_RISK_MATCHED | T_VOL_RISK | crps | 173 | 0.013169 | 0.013169 | 0.000000 | -0.000000 | 0.000000 |
| 5 | later | N_RISK_MATCHED | T_VOL_RISK | brier | 92 | 0.251344 | 0.251344 | 0.000000 | -0.000000 | 0.000000 |
| 5 | later | N_RISK_MATCHED | T_VOL_RISK | crps | 92 | 0.012374 | 0.012374 | 0.000000 | -0.000000 | 0.000000 |
| 21 | early | DATED_FUTURES | DATED_FUTURES_PARENT | brier | 141 | 0.292838 | 0.299569 | 0.006732 | — | — |
| 21 | early | DATED_FUTURES | DATED_FUTURES_PARENT | crps | 141 | 0.029107 | 0.029401 | 0.000293 | — | — |
| 21 | later | DATED_FUTURES | DATED_FUTURES_PARENT | brier | 76 | 0.429335 | 0.471471 | 0.042137 | — | — |
| 21 | later | DATED_FUTURES | DATED_FUTURES_PARENT | crps | 76 | 0.037107 | 0.038252 | 0.001146 | — | — |
| 21 | early | DATED_STRADDLE | DATED_STRADDLE_PARENT | brier | 141 | 0.293137 | 0.299569 | 0.006432 | — | — |
| 21 | early | DATED_STRADDLE | DATED_STRADDLE_PARENT | crps | 141 | 0.028632 | 0.029401 | 0.000769 | — | — |
| 21 | later | DATED_STRADDLE | DATED_STRADDLE_PARENT | brier | 76 | 0.467582 | 0.471471 | 0.003889 | — | — |
| 21 | later | DATED_STRADDLE | DATED_STRADDLE_PARENT | crps | 76 | 0.038035 | 0.038252 | 0.000218 | — | — |
| 21 | early | N_DERIV_RAW | BASE10 | brier | 141 | 0.296357 | 0.299569 | 0.003213 | — | — |
| 21 | early | N_DERIV_RAW | BASE10 | crps | 141 | 0.029303 | 0.029401 | 0.000098 | — | — |
| 21 | later | N_DERIV_RAW | BASE10 | brier | 76 | 0.467051 | 0.471471 | 0.004421 | — | — |
| 21 | later | N_DERIV_RAW | BASE10 | crps | 76 | 0.038333 | 0.038252 | -0.000081 | — | — |
| 21 | early | N_DERIV_STRUCT | N_DERIV_RAW | brier | 141 | 0.294706 | 0.296357 | 0.001650 | — | — |
| 21 | early | N_DERIV_STRUCT | N_DERIV_RAW | crps | 141 | 0.028978 | 0.029303 | 0.000325 | — | — |
| 21 | later | N_DERIV_STRUCT | N_DERIV_RAW | brier | 76 | 0.477547 | 0.467051 | -0.010496 | — | — |
| 21 | later | N_DERIV_STRUCT | N_DERIV_RAW | crps | 76 | 0.038831 | 0.038333 | -0.000498 | — | — |
| 21 | early | N_EQ_CONTROL | BASE10 | brier | 141 | 0.299569 | 0.299569 | 0.000000 | — | — |
| 21 | early | N_EQ_CONTROL | BASE10 | crps | 141 | 0.029401 | 0.029401 | 0.000000 | — | — |
| 21 | later | N_EQ_CONTROL | BASE10 | brier | 76 | 0.471471 | 0.471471 | 0.000000 | — | — |
| 21 | later | N_EQ_CONTROL | BASE10 | crps | 76 | 0.038252 | 0.038252 | 0.000000 | — | — |
| 21 | early | N_EQ_OFFICIAL | N_EQ_CONTROL | brier | 141 | 0.316267 | 0.299569 | -0.016697 | — | — |
| 21 | early | N_EQ_OFFICIAL | N_EQ_CONTROL | crps | 141 | 0.030506 | 0.029401 | -0.001105 | — | — |
| 21 | later | N_EQ_OFFICIAL | N_EQ_CONTROL | brier | 76 | 0.398163 | 0.471471 | 0.073308 | — | — |
| 21 | later | N_EQ_OFFICIAL | N_EQ_CONTROL | crps | 76 | 0.034518 | 0.038252 | 0.003734 | — | — |
| 21 | early | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | brier | 141 | 0.282306 | 0.285138 | 0.002832 | — | — |
| 21 | early | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | crps | 141 | 0.034775 | 0.034812 | 0.000037 | — | — |
| 21 | later | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | brier | 76 | 0.478830 | 0.474043 | -0.004787 | — | — |
| 21 | later | N_GLOBAL_RISK_MATCHED | N_RISK_MATCHED | crps | 76 | 0.037697 | 0.037579 | -0.000117 | — | — |
| 21 | early | N_INTRA_CONTROL | BASE10 | brier | 141 | 0.297442 | 0.299569 | 0.002127 | — | — |
| 21 | early | N_INTRA_CONTROL | BASE10 | crps | 141 | 0.029432 | 0.029401 | -0.000031 | — | — |
| 21 | later | N_INTRA_CONTROL | BASE10 | brier | 76 | 0.475611 | 0.471471 | -0.004140 | — | — |
| 21 | later | N_INTRA_CONTROL | BASE10 | crps | 76 | 0.038276 | 0.038252 | -0.000024 | — | — |
| 21 | early | N_INTRA_PANEL | N_INTRA_CONTROL | brier | 141 | 0.313154 | 0.297442 | -0.015712 | — | — |
| 21 | early | N_INTRA_PANEL | N_INTRA_CONTROL | crps | 141 | 0.030635 | 0.029432 | -0.001203 | — | — |
| 21 | later | N_INTRA_PANEL | N_INTRA_CONTROL | brier | 76 | 0.474861 | 0.475611 | 0.000750 | — | — |
| 21 | later | N_INTRA_PANEL | N_INTRA_CONTROL | crps | 76 | 0.037986 | 0.038276 | 0.000289 | — | — |
| 21 | early | N_RISK_MATCHED | T_VOL_RISK | brier | 141 | 0.285138 | 0.285138 | 0.000000 | — | — |
| 21 | early | N_RISK_MATCHED | T_VOL_RISK | crps | 141 | 0.034812 | 0.034812 | 0.000000 | — | — |
| 21 | later | N_RISK_MATCHED | T_VOL_RISK | brier | 76 | 0.474043 | 0.474043 | 0.000000 | — | — |
| 21 | later | N_RISK_MATCHED | T_VOL_RISK | crps | 76 | 0.037579 | 0.037579 | 0.000000 | — | — |

The contract and straddle additions improved both proper scores versus their compact parent in the monthly cohorts. Their weekly gains are concentrated in the later cohort. All monthly proper scores for these additions are weaker than symmetric neutral, and the straddle premium may contain variance risk premia and pricing effects.
