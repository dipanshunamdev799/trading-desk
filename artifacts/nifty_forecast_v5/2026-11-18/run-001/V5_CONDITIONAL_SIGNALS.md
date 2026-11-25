# V5 conditional signals

Five explicitly registered conditions: global weakness+narrow participation,
global weakness+broad participation, high volatility+near expiry, concentrated
rally, and rising oil+USD/INR+high volatility. Medians use training observations;
participation .5, near expiry<=2days, and trend>originRV*sqrt21 are fixed rules.
No progressively narrower subgroup search was conducted.

The exact same condition's matured historical return law plus30 unconditional
pseudoobservations supplies the regime-aware benchmark. conditional-training-
counts.json reports total/conditional/disjoint training counts for every fold.
320 matched model/condition/horizon comparisons were inspected across the 32
predictive systems before the two attribution controls. Full per-origin baseline
records are retained. Conditions do not create independent monthly samples.

|model|condition|n/disjoint|coverage|accuracy|Brier gain vs condition|CRPS gain|
|---|---|---|---|---|---|---|
|I00|concentrated_rally|5/2|5.4%|60.0%|+0.00051|-0.001384|
|L01|concentrated_rally|5/2|5.4%|40.0%|-0.02184|-0.001028|
|I00|global_weak_broad|12/7|13.0%|58.3%|+0.00321|-0.000390|
|L01|global_weak_broad|12/7|13.0%|25.0%|-0.04880|-0.000738|
|I00|global_weak_narrow|37/12|40.2%|78.4%|+0.09899|+0.002851|
|L01|global_weak_narrow|37/12|40.2%|67.6%|+0.08365|+0.003014|
|I00|highvol_nearexpiry|10/10|10.9%|80.0%|+0.08540|+0.002125|
|L01|highvol_nearexpiry|10/10|10.9%|70.0%|+0.09038|+0.002517|
|I00|oil_fx_up_highvol|19/5|20.7%|73.7%|+0.10558|+0.006165|
|L01|oil_fx_up_highvol|19/5|20.7%|68.4%|+0.10396|+0.007165|

These rows are descriptive, not selected conditional recommendations. Sparse
conditions and overlapping targets can produce impressive accuracy by chance.
Per-condition coverage, date counts, disjoint counts, proper-score improvements
and train-only baseline are reported even when adverse. Individual subgroup
block intervals are explicitly unadjusted and cannot qualify a conditional edge;
no subgroup wins the retrospective qualification standard through these scores.

Broader month/volatility/trend/global-risk/participation/expiry slices and fixed
abs(P(up)-.5)>=.15 selective forecasts are in conditional-signals.json. The
confidence threshold was not tuned to outer outcomes. Calibration buckets and
matched regime controls accompany accuracy. Any promising interaction needs a
separate frozen comparison on new evidence; no outcome-defined regime is used.
