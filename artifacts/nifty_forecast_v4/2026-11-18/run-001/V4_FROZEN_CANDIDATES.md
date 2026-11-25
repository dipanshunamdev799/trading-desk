# V4 frozen candidates

Registered 2026-11-18T09:28:01.980256+05:30; registry SHA256 c368fa55953a0fac065fd626c9974bc211e48bd600ef3bf20dd330b3ceebfa60.
No V3 parameter is retuned. All historical evaluations remain research-exposed.

Weekly binary cohort: exact V3 M05_lgbm; exact A00_sector; fixed Z_reversion;
Z_neutral; B00_empirical. A00 is Ridge mean regression plus the original logistic
direction component, not a Ridge coefficient converted into a probability.
LightGBM uses depth 2/leaves 4/trees 80/minleaf40/lr.04/L2=10/seed20261117, unchanged
V3 preprocessing and ordinary 101 features; proxies, sequence and explicit extra
interactions remain excluded. Sector mode uses original price+sector definitions.
Ridge alpha 100, classifier C=.1. Reversion=.45 when ret5>0, otherwise.55;
neutral=.5. Historical frequency uses latest 252 matured labels and V3 clipping.

Exact monthly refit anchor is the completed origin before the first forecast
session of the month. Training endpoints must be strictly earlier than that
origin; min126 labels, latest 42 inner validation, purged inner fitting/min80.
No daily implicit refit, changed window or revised calibration is silently
substituted. A missed refit is not repaired using later data and backdated.

|horizon|candidate|origins|disjoint|Brier|log loss|accuracy|status|
|---|---|---|---|---|---|---|---|
|5|M05_lgbm|92|19|0.226049|0.645492|66.30%|REPRODUCED / EXPOSED|
|5|A00_sector|92|19|0.233006|0.695555|63.04%|REPRODUCED / EXPOSED|
|5|Z_reversion|92|19|0.249239|0.691629|53.26%|REPRODUCED / EXPOSED|
|5|Z_neutral|92|19|0.250000|0.693147|NO CALL|REPRODUCED / EXPOSED|
|5|B00_empirical|92|19|0.258296|0.709964|57.61%|REPRODUCED / EXPOSED|
|21|B00_empirical|76|4|0.279282|0.752849|40.79%|REPRODUCED / EXPOSED|
|21|S_direction|76|4|0.242200|0.683027|60.53%|REPRODUCED / EXPOSED|

Monthly prospective distribution comparison is fixed D03_residual_shrunk versus
D00_empirical regardless of their retrospective rank. D01 and D02 remain bounded
exploratory studies. D03 is retained to test a predeclared hypothesis, not promoted
as the best model. Its poor coverage and extreme current output prohibit use.

Eight tree perturbations and four nonraw calibration/model combinations are
diagnostics with distinct names. They cannot replace these frozen candidates.
Calibrators remain DISABLED; no favorable retrospective correction is activated.
Existing binary candidates are a separate experiment from coherent endpoint laws;
their probabilities are never attached to another model's mean or intervals.

V3 source hashes, specifications, dataset identity and V4 hypotheses are in
registry.json. Exact first-issue executable source is archived and hash-verified;
future issues snapshot their source before running. No model is production-ready.
