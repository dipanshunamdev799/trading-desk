# Phase 2 preregistered research plan

Prepared 15 November 2026, before any v2 strategy returns. All 2025–2026
observations are research-exposed. Retrospective splits are not fresh forward
evidence. No execution bot, real orders or existing worker/control changes.

## Inherited evidence

The v1 late8/10% rules failed development selection; all primary full-window
returns were negative. Best primary10%/1%stop:417trades,−20.88%,PF0.76,
EODDD21.67%;25bpsstress−47.89%. Fixed-trade raw gross₹190513 was overwhelmed
by modeled slippage₹322769 and fees₹76536. This does not prove the trader's
discretion is unprofitable. Entry lateness, exhaustion and execution are hypotheses.

## Independent data and period

Evaluation only2025-01-01..2026-11-13. Earlier observations are indicator and
universe warmup only. Freeze top100 of the dated500cohort by prior63session
median close×volume as known2024-12-31, >=50observations, price>=₹50,
ADV>=₹5crore. Retain later failures. Download ALL Dec2024..Nov2026 months for
all100 and NIFTY, independent of later moves. Apply daily lagged liquidity and
known capital-action/dividend exclusions. Reuse certified local share-unit
restoration; never overwrite raw Upstox candles. PG is the only candle runtime
source. NSE metadata/derived features/results remain local. This narrower
liquid fixed cohort cannot establish performance for all NSE stocks.

## Search budget and causality

Four distinct candle families H1/H2/H4/H5 × three exits =12 primary candidates.
Four fixed ablations and two rejected-v1 baselines =6 nonselectable controls.
The12 mirrored short-only configurations are hypothetical diagnostics; dated
short/MIS/surveillance eligibility absent. H3 depth = FORWARD_DATA_REQUIRED.
Total30 portfolios plus fixed cost/latency/size stresses, not thousands of bots.
Every primary receives fixed5/25bps,one-extra-bar latency,quarterparticipation,
₹5lakh and₹20lakh capital sensitivities. These72stresses are nonselectable
scenarios (24cost +48latency/capacity), not additional discovered rules.
All features use completed5m bars; no optimized grid. Sector confirmation is
an equal-weight same-clock peer-return proxy using original2024 industry labels,
excluding the candidate and requiring >=3 observed peers. It is not an index.

Development2025-01-01..2025-09-30; validation2025-10-01..2026-03-31;
evaluation2026-04-01..2026-11-13. Development selects at most one primary rule
with >=100closedtrades, >=60active days, positive mean netbps AND funded return,
PF>=1.10, EODDD<=15%. Rank meanbps, smallerDD, stableID; freeze before later
returns. No replacement chosen on validation/evaluation. Freeze source, plan,
code and exact data fingerprints before model selection.

## Retrospective paper gate

Selected model only: validation AND evaluation positive funded return and
mean netbps, eachPF>=1.10; evaluation>=75closedtrades/>=50active sessions;
EODDD<=15%, worst realized day>=−2%, top5winner concentration<=50% of all
positive profits; profitable in >=2 of3 chronological evaluation chunks;
positive evaluation return under25bps/side, one5m additional latency and
quarter participation;20session-block95%lower return bound>0. Use2000common
session bootstrap draws, plus family-wise conservative Bonferroni lower-tail
alpha=.05/12 across the12primary hypotheses. Intervals remain conditional
retrospective diagnostics, not probabilities of future profit. No unresolved
accounting/source/exit failure. Broker execution eligibility and calibrated
fills must also be established. Without those, a statistical pass is at most
FORWARD_DATA_REQUIRED, never automatically RETROSPECTIVE_PAPER_CANDIDATE.
Thresholds favour adequate coverage and a modest economic margin; they are
research gates, not optimized production risk limits.

## Common execution

₹10lakh; no leverage; risk<=0.5%current equity, remaining1%opening-equity daily
loss room; whole shares; decision-bar1%volume cap; max3entries/day shared
portfolio; one position; no same-symbol reentry; no mandatory trade quota.
Next-open entry (9:35..13:30), <=0.3%adverse chase relative decisionclose,
planned quantity fixed before entry. Exit before15:10. Stop-first dual hits,
adverse open through stops, target receives no favourable gap improvement.
Unavailable exits fail the entire configuration; never delete a trade or
release unresolved cash. Baseline10bps/side ALL-IN friction, sensitivities
5/25bps: not a calibrated security-specific spread/impact model. Do not add
a separate spread charge on top. Historical partial fills cannot be identified
from candles; full modeled fills are provisional, not observed executions.
One-minute audit fixed first20chronologicaldevelopment H1-fixed trades,
regardless profitability, plus first20selecteddevelopment trades if different.
Replays fixed entries/quantities only, not an alternate selected portfolio.

## Questions and outputs

Compare stage/entry timing, pullback vs breakout, market/sector ablations,
fixed/structural/trailing exits, net/gross expectancy and cost attribution.
Segment time, NIFTYdirection/laggedvolatility, liquidity, price, industry,
gap vs intraday move, RVOL, causal trend-efficiency; show sparse groups and
dependence. Capital/participation sensitivity measures capacity, not leverage
rescue. H3 incremental price/volume/depth prediction/economics requires new
time-aligned observations; no invented historical book/aggressor flags.
Retain every trade/signal/rejection/day, hashes and failures. Classify each as
REJECTED, INCONCLUSIVE, FORWARD_DATA_REQUIRED or a qualified retrospective
candidate. NO STRATEGY QUALIFIED is an acceptable final result.
Full-window samples below30trades or20active sessions are INCONCLUSIVE rather
than economically rejected on an inadequate sample. This does not relax any
development or paper-candidate threshold.
