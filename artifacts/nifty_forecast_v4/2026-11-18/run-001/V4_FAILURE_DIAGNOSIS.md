# V4 failure diagnosis

Decision: **NO DEPLOYMENT; no independent edge demonstrated**. V4 reproduces V3
before introducing a finite distribution study. Existing V3 files and source are
hashed and preserved, including all ten reports, registries, per-origin records,
model files, selection results and validation artifacts.

|horizon|candidate|origins|disjoint|Brier|log loss|accuracy|status|
|---|---|---|---|---|---|---|---|
|5|M05_lgbm|92|19|0.226049|0.645492|66.30%|REPRODUCED / EXPOSED|
|5|A00_sector|92|19|0.233006|0.695555|63.04%|REPRODUCED / EXPOSED|
|5|Z_reversion|92|19|0.249239|0.691629|53.26%|REPRODUCED / EXPOSED|
|5|Z_neutral|92|19|0.250000|0.693147|NO CALL|REPRODUCED / EXPOSED|
|5|B00_empirical|92|19|0.258296|0.709964|57.61%|REPRODUCED / EXPOSED|
|21|B00_empirical|76|4|0.279282|0.752849|40.79%|REPRODUCED / EXPOSED|
|21|S_direction|76|4|0.242200|0.683027|60.53%|REPRODUCED / EXPOSED|

45 candidate/fold probability vectors were recalculated from original model
artifacts and matched to 1e-12 tolerance. July weekly LightGBM and sector Ridge
were also independently refitted and matched. This is reproduction, not fresh
confirmation. V3 reported zero individually significant features after adjustment:
minimum q=0.296020.

|Failure|Evidence|Diagnosis and limits|
|---|---|---|
|Adaptive selection|Weekly selector Brier .256118 versus neutral .25; fixed tree .226049|A 42-origin overlapping inner window can misrank models; binary accuracy does not validate probabilities|
|Small independent sample|92 weekly origins/19 disjoint; 76 monthly/4 disjoint; V3 outcome ESS23.45/5.96|Overlap creates apparent sample abundance; these ESS estimates are not guarantees of independence|
|Search uncertainty|V3 tree improvement over fixed reversion .023190, simultaneous95% [-.093033,+.139413]|170 model/target contrasts and dependence; no positive qualified lower bound|
|Monthly class imbalance|60.53% selected accuracy versus 59.21% always-down|Only1.32 percentage points of raw gain, four disjoint windows|
|Distribution construction|Monthly distribution policy80% coverage31.58%;50%10.53%|Short overlap-heavy residual pools, temporal distribution changes and model bias are plausible; no single causal explanation proven|
|Incoherent endpoint outputs|Frozen V3 weekly classifier72.37% up versus distribution49.75%; monthly 55% versus 28.36%|Separate target selectors do not define one joint endpoint law|
|Calibration|Old monthly 17 flips:15 correct-to-wrong,2 repaired|Small correlated calibration samples and prevalence changes; V4 simple corrections help one model and hurt another|
|Data limitations|Revised histories, incomplete delivery archives, short institutional coverage, unavailable dated index membership|Conservative lags reduce timing risk but cannot prove original-vintage fidelity|

Architecture is part of the problem, not an exclusive cause: a coherent law fixes
algebraic contradictions but does not fix calibration. Monthly nonlinear V3
LightGBM remains poor; adding algorithms would not supply new independent months.
Regime slices, phase sensitivity, calibration buckets and individual-origin losses
are retained even when unfavorable. No new dates are relabeled untouched.

The original V3 statistical/selection artifacts are in v3-audit-inventory.json;
the actual source contents/definitions reviewed are in v3-source-review.json.
V4 also keeps source-level changes and operational failures visible.
