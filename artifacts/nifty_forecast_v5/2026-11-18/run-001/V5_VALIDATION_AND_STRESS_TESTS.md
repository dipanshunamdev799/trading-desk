# V5 validation and stress tests

Only2025–2026 observations; all historical dates remain research-exposed. No
random seed, alternate split or new source vintage creates independent evidence.
The main comparison uses identical V3/V4 outer origins:92 weekly/19 disjoint,
76 monthly/four disjoint. Outcome-ACF effective sample is about 23.45/5.96;
disjoint and effective-size counts are diagnostics, not independence guarantees.
The updated historical NIFTY closes match old source closes exactly (max0points).

Monthly refits follow original prequential origins, matured endpoints strictly
before refit origin, min126 fitting labels, latest 42 inner residual origins and
purged inner fitting. Preprocessing/PCA/correlation thresholds are trained within
past data. Sector/stock panels and auxiliary tasks are grouped by date and label
maturity; a thousand same-date instruments are not a thousand NIFTY outcomes.

916 paired comparisons across both horizons;458 contrasts per horizon include
all 34 systems, five proper/point scores, unconditional and strongest prior V4
benchmarks, fixed neutral/reversion, and explicit source ablations. Weekly intervals
use10-session blocks,2000 resamples and standardized max-deviation family adjustment.
Monthly intervals are withheld because76<168 rows needed for the 42-session block.
The strongest prior benchmark was itself identified on exposed historical scores;
that postselection is disclosed rather than treated as untouched evidence.

15 adjusted weekly comparison lower bounds are positive: improvements
against E00, neutral, or the weak V5 price-only model. **None establishes positive
adjusted improvement over the strongest prior V4 coherent model.** No adjusted
CRPS superiority qualifies the leaders; no model becomes independently validated.
These are conditional bootstrap intervals with finite-sample/nonstationarity risks,
not a guarantee that nominal familywise coverage is exact for this short history.

September exclusion (explicitly distinguishes empirical from stronger V4 controls):

|model|metric|gain vs empirical|gain vs prior|prior|
|---|---|---|---|---|
|I00|brier|+0.068350|+0.029929|D03_residual_shrunk|
|I00|crps|+0.002226|+0.000019|D02_student_shrunk|
|I03_nosize|brier|+0.071685|+0.033264|D03_residual_shrunk|
|I03_nosize|crps|+0.002253|+0.000046|D02_student_shrunk|
|L01|brier|+0.055737|+0.017317|D03_residual_shrunk|
|L01|crps|+0.002505|+0.000298|D02_student_shrunk|

The new internal lead survives September exclusion descriptively, unlike the
earlier tree's reversion-relative result. All individual months, alternate starting
phases of disjoint windows and deletion of 1/3/5/10 favorable overlapping origins
are saved. Overlap means deletion counts are not counts of independent weeks.
Timing lag, size removal, legacy-only, global-delay and rolling126 are separate
registered stress configurations, not quietly retuned parameters.

|horizon|seed|n|brier|crps|accuracy|
|---|---|---|---|---|---|
|5|301|92|0.30276052107638546|0.014078826413866999|0.41304347826086957|
|5|907|92|0.27943339413059914|0.013124953405688464|0.45652173913043476|
|21|301|76|0.3879514945598123|0.03433812523627155|0.2236842105263158|
|21|907|76|0.42292950516585787|0.03581145371248271|0.21052631578947367|

Randomized matured training labels do not reproduce the lead. Development lead/lag
BH family has 976 tests and no q<.05. Conditional subgroups form a separate
descriptive family and are not used for qualification.

27 verification tests passed: complete V1–V4 preservation/ledger,
source/model/dataset hashes, same evaluation dates/outcomes, mature/embargo labels,
DST/global availability, hostile future-source perturbations, registered and
aliased future-oracle rejection, independent native-model refit, weighted CRPS,
fresh-source prefix identity/official close, coherent probabilities/buckets/prices,
pre-target issue, unfinished-US-close exclusion, exact issued source archive,
research-only proxy exclusion, original failure/repair records and monthly-CI guard.

Schema/availability/maturity guards were added after discovery fits as documented
hardening. Exact initial fit code and exact issued code are separately archived;
an independent I00 refit verifies the same numerical forecast. No settings changed
to improve a score. Metadata error repair concerned an unused global field in an
Indian-only forest, not a new outcome-selected architecture. Sources still lack
complete historical actual receipt/revision proof; these limits cannot be tested
away. No trades, deployment, V4 ledger changes or automatic schedule occurred.

The complete34-system historical replay was executed from frozen inputs in a new
directory; all 11,992 rows reproduced numerically. full-reproduction.json records
all tolerances/differences. An initial replay packaging error omitted the dataset
manifest, failed before fitting, and was fixed in a new retained directory.
The frozen-forecast manual scorer was exercised before maturity and correctly
made no network request or ledger mutation. A separately timestamped baseline
supplement was frozen before the first target session without editing the issue.
Later scoring appends only to V5's own evaluation ledger on matched target dates.
