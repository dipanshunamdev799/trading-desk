# V4 prospective validation protocol

**NO DEPLOYMENT.** First primary evidence begins only with a genuinely new,
on-time frozen prediction and later fully resolved outcome. Current primary
predictions=0, diagnostic issuances=1, resolved
horizons=0. A late diagnostic is never
silently promoted into premarket evidence. All historical studies are exposed.

Decision09:10 IST, start09:00–09:10, complete09:10–09:12; every newly retrieved
required input must have arrived by09:10. Start early enough for source checks and
fitting; an overrun skips the origin. Previous complete NSE session is reference;
five/21 future exchange sessions define endpoints. No same-day live candle enters
the feature panel. Monthly training anchor, feature definitions and hyperparameters
are the frozen V3 rules. Inputs, acquired raw responses, availability, models,
source code, registry/data hashes and coherent atoms are retained before issue.

The append-only JSONL ledger has exclusive writer locking, canonical hashing,
previous-event hashes, duplicate issuance/resolution rejection and fsync. It never
rewrites a forecast. Damaged or partially written ledgers halt; lock recovery after
a crash requires review, not silent deletion. Status verifies every referenced
artifact. File hashes/local clocks are not external notarization; preserve a trusted
copy of the head before making independent-evidence claims.

Before any primary issue, a PROTOCOL_FREEZE event pins registry, stop rules,
power assumptions, operational source and V3 helpers by hash. Primary execution
verifies that event's files. Statistics refuses to change thresholds after the
freeze. The weekly planning gate was revised from 8550 to 14421 before any primary
issue because all three primary weekly comparisons, not only tree-vs-reversion,
must have their pilot variances assessed; protocol-amendment.json records this.
The earlier late operational rehearsal does not count as primary evidence.

Resolution runs no earlier than endpoint18:00 IST, fetches actual completed
daily candles, verifies exact target session sequence, reports revised reference
separately but scores against the originally frozen close, and appends matched
candidate/baseline Brier/logloss and coherent-distribution scores. No incomplete
label is trained/scored; missing endpoint causes a halt. Duplicate resolutions
are skipped. Experimental late issues remain separate through scoring.

Primary family: weekly M05 vs reversion, M05 vs sector, sector vs reversion
(Brier), and monthly D03 vs D00 (CRPS). Neutral/frequency/logloss/accuracy/balanced
accuracy/calibration/confidence coverage and all distribution metrics remain
mandatory secondary reporting. No learned selector is introduced.

Power planning: N=ceil(((z_(1-.05/(2*4))+z_.8)*pairedSD/effect)^2),80% power,
family alpha.05 across 4 primary comparisons. Pilot variance comes from 19 disjoint
weekly/four monthly exposed outcomes and is highly uncertain. SDx1.5 is a
sensitivity scenario, not a statistically certified upper bound. Estimates assume
stationary approximately independent paired disjoint losses; drift/dependence
can require more evidence. They are not a promise of sufficient sample size.

|horizon|comparison|effect|pilot disjoint|paired SD|SD inflation|required disjoint N|
|---|---|---|---|---|---|---|
|5|M05_lgbm vs Z_reversion|0.01|19|0.184590|1.0|3800|
|5|M05_lgbm vs Z_reversion|0.01|19|0.184590|1.5|8550|
|5|M05_lgbm vs Z_reversion|0.02|19|0.184590|1.0|950|
|5|M05_lgbm vs Z_reversion|0.02|19|0.184590|1.5|2138|
|5|M05_lgbm vs Z_reversion|0.02319|19|0.184590|1.0|707|
|5|M05_lgbm vs Z_reversion|0.02319|19|0.184590|1.5|1590|
|5|M05_lgbm vs A00_sector|0.01|19|0.218605|1.0|5329|
|5|M05_lgbm vs A00_sector|0.01|19|0.218605|1.5|11990|
|5|M05_lgbm vs A00_sector|0.02|19|0.218605|1.0|1333|
|5|M05_lgbm vs A00_sector|0.02|19|0.218605|1.5|2998|
|5|M05_lgbm vs A00_sector|0.02319|19|0.218605|1.0|991|
|5|M05_lgbm vs A00_sector|0.02319|19|0.218605|1.5|2230|
|5|A00_sector vs Z_reversion|0.01|19|0.239738|1.0|6410|
|5|A00_sector vs Z_reversion|0.01|19|0.239738|1.5|14421|
|5|A00_sector vs Z_reversion|0.02|19|0.239738|1.0|1603|
|5|A00_sector vs Z_reversion|0.02|19|0.239738|1.5|3606|
|5|A00_sector vs Z_reversion|0.02319|19|0.239738|1.0|1192|
|5|A00_sector vs Z_reversion|0.02319|19|0.239738|1.5|2682|
|21|D03_residual_shrunk vs D00_empirical|0.001|4|0.006628|1.0|490|
|21|D03_residual_shrunk vs D00_empirical|0.001|4|0.006628|1.5|1103|
|21|D03_residual_shrunk vs D00_empirical|0.002|4|0.006628|1.0|123|
|21|D03_residual_shrunk vs D00_empirical|0.002|4|0.006628|1.5|276|
|21|D03_residual_shrunk vs D00_empirical|0.005|4|0.006628|1.0|20|
|21|D03_residual_shrunk vs D00_empirical|0.005|4|0.006628|1.5|45|

Conservative fixed final planning gates: weekly 14421
disjoint outcomes for .01 Brier improvement, monthly 1103
for .001 CRPS improvement. These are planning gates, not guaranteed sample sizes.
Even the observed weekly effect≈.02319 needs707 windows under the uninflated
pilot assumptions. Smaller30/12 counts are descriptive interims only, with no
qualification or optional significance stopping. Remaining2026 cannot supply
these samples. The experiment therefore cannot establish the requested independent
edge within the existing calendar boundary; that limitation does not weaken gates.

At fixed final N, require family-adjusted positive matched proper-score improvement,
noninferior logloss, acceptable calibration and 50/80% coverage within 10 percentage
points of nominal with Wilson intervals, stable subperiod signs, no leakage and
robust perturbation results. No automatic deployment even after qualification.
Failures in timing/source/ledger integrity halt or skip. Any source/model/calibration
change gets a distinct version/cohort; prospective outcomes never tune the existing
candidate. Stop before any target enters2027, and do not resolve outside2026 under
this frozen protocol. Extending the scope needs user instruction.

From the workspace root, using the existing venv and configured Upstox token:

```powershell
# Start at 09:00–09:09 IST on an eligible future session; no scheduler was installed.
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.prospective run
# Explicitly late, excluded research cohort only (refuses duplicate origin):
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.prospective diagnostic-late
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.prospective resolve
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.prospective status
```

The on-time command was executed today after the deadline and correctly rejected
without fetching or issuing. Resolution was executed and correctly found no mature
horizons without a network request or ledger mutation. No unattended task, trade
or production setting was created.
