# V4 final research decision

**NO DEPLOYMENT. No repeatable independent forecasting advantage is established.**
Keep exact weekly LightGBM as an exploratory lead; keep sector/reversion/neutral/
historical controls frozen. Do not activate retrospective calibrators or replace
the candidate using 75% posthoc removal accuracy. New endpoint laws are internally
coherent but their poor monthly coverage disqualifies precise forecasting use.

Main findings: reproduced weekly tree Brier.226049/66.30% accuracy; selected V3
policy .256118; tree advantage reverses when September is removed. Sector removal
harms its point score. Both simple corrections worsen the tree; sector offset
helps descriptively, with no supported adjusted improvement. No V4 simultaneous
weekly lower bound is positive. Monthly evidence still has four disjoint outcomes.

The first genuinely timestamped live rehearsal is saved at 2026-11-18T09:33:38.781325+05:30,
reference17 November close 25,387.40. It is
LATE_DIAGNOSTIC and excluded from the primary09:10 cohort. It has not matured.
Primary prospective count=0; independently validated count=0.
This is a successful operational rehearsal, not successful predictive validation.

|sessions|law|endpoint|P(up)|mean return|median return|mean endpoint|80 interval|
|---|---|---|---|---|---|---|---|
|21|D00_empirical|2026-12-17|48.81%|-0.789%|-0.042%|25,186.98|24,012–26,221|
|21|D03_residual_shrunk|2026-12-17|0.00%|-3.800%|-3.828%|24,422.64|23,697–24,983|
|5|D00_empirical|2026-11-25|41.27%|-0.223%|-0.342%|25,330.68|24,771–25,803|
|5|D03_residual_shrunk|2026-11-25|9.52%|-1.329%|-1.303%|25,050.12|24,695–25,361|

These are NOT VALIDATED research distributions. In particular monthly D03 has
zero fitted positive-return mass: this is a finite-support/model failure risk,
not certainty of a fall. Do not substitute the separate binary tree probability
into a D03 mean/interval: that would recreate V3's incoherence. Path breaches and
future realized volatility are explicitly unavailable from these endpoint laws.

22 verification tests passed, including immutable V3 preservation,
numerical reproduction, weighted-CRPS/endpoint identities, purging, timing and
scope rejection, ledger duplicate/tamper/partial-write/lock checks, parser regression,
cohort separation and unsupported-monthly-interval withholding. First-issue exact
code and subsequent hardening are separately preserved. No V1/V2/V3 artifact or
forecast was overwritten.

An auditable executable capture/issue/resolve process now exists. Adequate
prospective power is impossible in the remaining 2026 scope under the fixed gates;
there is no promise of a validated monthly edge. Further sample collection beyond
2026 requires an explicit scope change. No scheduler was installed and no trades
or live settings were changed. Source delivery/vintage, local-clock notarization,
calendar changes, missing institutional data and tail support remain limitations.

The eight reports, immutable registry, original-source review, per-origin CSVs,
model/input/source snapshots, hash-chain ledger, statistics, power assumptions,
stop rules and tests form the delivered research system. The result is better
evidence discipline and infrastructure, not a manufactured higher win rate.
