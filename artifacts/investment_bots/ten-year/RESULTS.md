# Investment bots — ten-year research replay

Run: `tenyear-efec7d11b451fd650c15`. PostgreSQL is the source and primary result store.

Test: 2016-11-15 to 2026-11-13. Indicator warmup starts 2015-11-16.

**These are survivorship-biased, retrospective reference results. They do not establish an executable trading edge.**

| Strategy | CAGR | Total return | Max drawdown | ₹10 lakh became | Closed positions |
|---|---:|---:|---:|---:|---:|
| C2-S | 23.32% | 712.60% | -45.91% | ₹8,125,990 | 8785 |
| C0-R | 22.69% | 671.64% | -42.06% | ₹7,716,443 | 1746 |
| C1-R | 15.44% | 319.90% | -26.64% | ₹4,199,043 | 1780 |
| NIFTY 50 PR | 11.99% | 210.10% | -38.44% | ₹3,101,000 | — |
| NIFTY 500 PR | 13.13% | 243.16% | -38.30% | ₹3,431,558 | — |

C0-R-X: no valid ten-year execution-gated backtest is possible without the historical auction observations.

## Interpretation limits

- Survivorship bias: frozen retained stock list; delisted securities are not comprehensively represented
- Static industry labels and frozen panel admission use later information
- Price returns only; dividends, spinoff entitlements and cash interest are not credited
- 617 corporate-action records cover only a recent feed window; older split/demerger validation is incomplete
- Official-opening-price fills are theoretical, not observed executable fills
- C0-R-X cannot be validated without historical auction evidence
- Reference engine replay: missing-bar sessions retain last valid marks; this is not a claim that all paper operational gates would have permitted uninterrupted processing
- Retrospective versioned research; not an unbiased live-performance estimate

## Source-data audit

3 sessions exceeded the 2% missing prior-universe data limit. The baseline reference engine carries last marks; the paper application would pause processing. A whole-day missing-price stress is reported separately.

| Session | Missing required instruments | Required instruments |
|---|---:|---:|
| 2017-10-19 | 296 | 300 |
| 2018-11-07 | 297 | 300 |
| 2018-11-09 | 2 | 23 |

The AURUM/formerly-Majesco price gap on 23 Dec 2020 coincides with a large cash distribution. The issuer confirmed a ₹974/share dividend. This price-only engine omits the cash credit; that gap must not be interpreted as the investor's total economic loss. [Issuer dividend notice](https://strapi.aurumproptech.in/uploads/Majesco_Communication_on_TDS_on_Dividend_d6479330ee.pdf).

## Robustness checks

| Strategy | Five-phase CAGR range | Double-cost CAGR | Whole-share CAGR | Missing-day stress CAGR |
|---|---:|---:|---:|---:|
| C0-R | 22.69%–23.69% | 18.95% | 23.34% | 23.01% |
| C1-R | 13.99%–15.44% | 11.11% | 15.46% | 15.02% |
| C2-S | 23.32%–23.50% | 18.85% | 23.55% | 23.34% |

Price-index benchmarks exclude reinvested cash dividends. [NSE Indices explains price versus total-return indices](https://www.niftyindices.com/resources/index-concepts/total-return-index).

Annual results, cost stress, five rebalance phases, whole-share sensitivity, suspicious large price moves and rolling returns are in the accompanying JSON/CSV exports. Phase 0 is always the headline; no winning phase or parameter was selected.
