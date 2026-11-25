# 04 — Controlled model experiments

19 fitted configurations, independently trained at each horizon; five deterministic
controls (neutral, momentum, reversion, always-up/down); five nested target selectors
and five corresponding baseline selectors. There were 532 registered
configuration/fold evaluations, zero failed configurations. Each ledger row includes
both purged-inner and full-past fitting; compound tree models contain multiple
estimators, so 532 is not the count of individual elementary estimator fits.

|ID|algorithm|feature set|parameters|primary eligible|
|---|---|---|---|---|
|B00_empirical|empirical|price|{}|True|
|B01_ewma|ewma|price|{}|True|
|B02_rv_scaled|rv_scaled|price|{}|True|
|B03_vix_scaled|vix_scaled|price|{}|True|
|B04_momentum|momentum|price|{}|True|
|B05_reversion|reversion|price|{}|True|
|B06_regime|regime|price|{}|True|
|M00_ridge_price|ridge|price|{"alpha": 100}|True|
|M01_ridge_full|ridge|full|{"alpha": 100}|True|
|M02_elastic001|elastic|full|{"alpha": 0.001}|True|
|M03_elastic01|elastic|full|{"alpha": 0.01}|True|
|M04_corr_ridge|ridge|pruned|{"alpha": 100}|True|
|M05_lgbm|lgbm|full|{}|True|
|M06_analog30|analogue|full|{}|True|
|M07_sequence|ridge|sequence|{"alpha": 100}|True|
|A00_sector|ridge|sector|{"alpha": 100}|True|
|A01_nofo|ridge|nofo|{"alpha": 100}|True|
|A02_proxy|ridge|proxy|{"alpha": 100}|False|
|A03_interact|ridge|interaction|{"alpha": 100}|True|

LightGBM: depth2, four leaves, minimum40 samples/leaf, 80 trees, learning_rate .04,
L2=10, deterministic one-thread training. It fits direction, mean return, seven
quantiles, future volatility and two path-breach probabilities. Other linear
families independently fit direction, return, volatility and tail risks.
Training-only correlation pruning uses .9; ElasticNet has two alpha settings.
Analogue forecasts use 30 neighbors plus 30-observation unconditional shrinkage.
Regime conditioning uses causal trend sign and training-median volatility.
Structured lags test temporal information without a neural parameter budget.

No RNN/Transformer: 402 feature rows and limited independent monthly targets
cannot credibly validate a large sequence architecture. HMM, XGBoost and CatBoost
were not added as redundant unconstrained sweeps; causal regime distributions and
one shallow boosted implementation test the relevant mechanisms at a fixed budget.
Skipped families and the lack of formal conformal guarantees are explicit.

Experiment registry: registry-config.json, experiment-ledger.json and inner-validation.json.
All model artifacts are in models/. Failed hypotheses remain in the score tables.
No extra configurations were added after examining outer scores. Six diagnostic
randomized-direction runs (three fixed seeds per horizon) are negative controls,
not additional candidate searches.
