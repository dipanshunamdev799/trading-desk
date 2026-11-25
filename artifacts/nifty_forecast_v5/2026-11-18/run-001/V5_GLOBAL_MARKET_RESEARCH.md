# V5 global-to-NIFTY research

New research beyond V4: all 13 actually listed global instruments, regional
dispersion/relative strength/correlation evolution, causal lead/lag tests,
train-only joint factors, global-only versus Indian-only versus joint models,
and an extra-session global/relationship delay stress. Global inputs are not
assumed useful merely because they expand the feature matrix.

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|E00|92/19|0.258296|0.709964|57.61%|50.00%|0.012210|1.637%|2.321%|50.0%|72.8%|
|G00|92/19|0.283500|0.765130|46.74%|42.94%|0.013366|1.758%|2.475%|52.2%|72.8%|
|I00|92/19|0.186099|0.558036|76.09%|75.18%|0.010224|1.354%|1.985%|55.4%|76.1%|
|C00|92/19|0.202619|0.591175|68.48%|67.22%|0.010946|1.417%|2.043%|56.5%|77.2%|
|F00|92/19|0.254962|0.703702|53.26%|54.02%|0.012307|1.620%|2.319%|53.3%|73.9%|
|F01|92/19|0.263814|0.721422|48.91%|47.87%|0.012499|1.658%|2.341%|47.8%|73.9%|
|C01_delayglobal|92/19|0.207734|0.601366|64.13%|63.79%|0.010953|1.439%|2.029%|54.3%|71.7%|

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|E00|76/4|0.279282|0.752849|40.79%|50.00%|0.028363|3.739%|4.879%|26.3%|61.8%|
|G00|76/4|0.394812|1.041745|26.32%|30.75%|0.034234|4.510%|5.364%|25.0%|60.5%|
|I00|76/4|0.273006|0.747674|52.63%|57.99%|0.030211|3.866%|4.883%|30.3%|50.0%|
|C00|76/4|0.326823|0.862906|36.84%|45.16%|0.030806|3.944%|4.840%|31.6%|52.6%|
|F00|76/4|0.352079|0.924482|34.21%|38.92%|0.031367|4.014%|4.977%|22.4%|46.1%|
|F01|76/4|0.376892|0.985017|26.32%|31.25%|0.033654|4.221%|5.269%|19.7%|40.8%|

Global-only ridge is worse than unconditional history at both horizons. Combined
weekly C00 is better than a weak price-only model but worse than Indian-only I00;
the incremental global claim must be judged against I00, not just neutral or price.
Monthly joint/factor models are poor. Static PCA5 and rolling126 PCA5 do not rescue
the predictive relationship. They estimate variance factors, not guaranteed return
predictors. Rolling PCA is a causal loading-adaptation proxy, not a fully identified
latent state-space dynamic-factor model.

|hypothesis|metric|gain|simultaneous95|
|---|---|---|---|
|Global increment beyond Indian internals|brier|-0.016520|[-0.04922928301960008, 0.016189111637037408]|
|Global increment beyond Indian internals|crps|-0.000722|[-0.0015111480240205595, 6.686760144949803e-05]|

Development-only lead/lag discovery evaluated976 feature/lag/target
combinations, lags0/1/3/5, NIFTY and Indian IT targets at 5/21 sessions; labels matured
before 1July2026.200 separated circular-shift nulls per test and BH across the entire
family produced minimum q=0.346837, with 0
q<.05. These are predictive-association diagnostics, not causation or Granger proof.
The US Tech100/Indian IT proxy relationship was actually tested; bond-yield and
dollar-index hypotheses were not testable because those historical downloads failed.
Oil/FX, global weakness conditional on participation, regional dispersion and
rolling correlation changes were included as explicit hypotheses, not findings.

Top development associations, their half-sample signs, source features and lags
are in global-lead-lag-discovery.csv; no final outer feature ranking selected the
initial models. Additional retrospective stages were registered before their own
tests and remain exposed. No accessible global source has established independent
incremental predictive value in this study.
