# V5 derivatives intelligence

467 dated official archives retain actual contract/expiry identities. Futures
basis, common-scale OI changes, same-contract/lot OI evolution, roll flag, DTE,
log OI/volume PCR, concentration/wall/maxpain distances and matched-contract PCR
changes follow the audited V3 definitions, with an extra domestic-session lag.
Absolute contract IDs/OI/lot levels are not falsely treated as normalized predictors.

New engineered relationships: price x OI change; concentration x origin RV;
positioning divided by1+DTE; causal63-session basis and OI-change z-scores.
These explore trend/positioning/expiry/volatility hypotheses. They do not infer
writer intent or claim basis is more than carry. No historical IV/Greeks are added.

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|P00|92/19|0.272343|0.740884|54.35%|47.51%|0.012893|1.706%|2.424%|48.9%|68.5%|
|D00|92/19|0.286450|0.772935|54.35%|49.20%|0.012988|1.721%|2.438%|45.7%|69.6%|
|I00|92/19|0.186099|0.558036|76.09%|75.18%|0.010224|1.354%|1.985%|55.4%|76.1%|
|C00|92/19|0.202619|0.591175|68.48%|67.22%|0.010946|1.417%|2.043%|56.5%|77.2%|
|D01|92/19|0.207246|0.601303|67.39%|65.94%|0.010980|1.436%|2.066%|58.7%|79.3%|
|D02_rawonly|92/19|0.207925|0.601657|64.13%|63.11%|0.011040|1.443%|2.071%|58.7%|78.3%|

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|E00|76/4|0.279282|0.752849|40.79%|50.00%|0.028363|3.739%|4.879%|26.3%|61.8%|
|D00|76/4|0.409257|1.077310|35.53%|35.52%|0.036044|4.774%|5.574%|11.8%|46.1%|
|C00|76/4|0.326823|0.862906|36.84%|45.16%|0.030806|3.944%|4.840%|31.6%|52.6%|
|D01|76/4|0.336433|0.889496|43.42%|51.22%|0.031537|4.005%|4.952%|30.3%|48.7%|
|D02_rawonly|76/4|0.337066|0.891347|42.11%|49.61%|0.031369|3.999%|4.928%|31.6%|50.0%|

|hypothesis|metric|gain|simultaneous95|
|---|---|---|---|
|Derivative increment beyond joint state|brier|-0.004627|[-0.017695494054909187, 0.008440620003839449]|
|Derivative increment beyond joint state|crps|-0.000034|[-0.0005045125400407778, 0.00043653385872186333]|

Price-plus-derivatives alone is weak; adding the derivative block to joint state
does not improve Brier or CRPS. Removing the five new transformations does not
uncover a convincing advantage. This rejects these tested implementations, not
all derivatives information. Institutional positioning remains short/incomplete
in the prior audit and was not fabricated into a full2025 panel. Near-expiry and
high-volatility conditions are tested with matched exact-condition baselines in
the conditional study; no narrow subgroup is promoted as an independent edge.
