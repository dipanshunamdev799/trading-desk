# NIFTY V6 — Indian Internals Deep Dive

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Design and source identity

V6 prioritizes authentic native-index histories from the existing Upstox archives. It introduces no current-stock-membership proxy as an investable historical breadth series. The main source universe inherited from V5 includes25 domestic index/VIX histories,13 global series,150 current-stock proxy histories andfive ETFs; V6's selected native systems use the native indices and ETF histories only. Source identities and prior provenance remain in V5; V6 freezes403 aligned origins,57 native reference inputs,105 newly engineered native/evolution fields and64 retained global/cross-market reference fields. The105 fields were generated as a research library, then narrow hypothesis subsets were registered; they were not all simultaneously fed into every model.

The multi-scale library uses Bank Nifty, financial services, IT, auto, metal, pharma, FMCG, energy and Nifty500 at1/2/3/5/10/20 sessions. Relative changes are divided by trailing NIFTY21-session daily volatility times sqrt(horizon), with a .001 volatility floor. Additional variables include relative volatility, relative drawdown to21-session extrema, sector synchronization, average trailing21-session correlation, correlation change, defensive/cyclical and IT/financial rotation, bank deceleration, broad-index deterioration and concentration/dispersion changes. Indicators initialize from January2025 only. The early-April feature matrix boundary does not incorrectly restart their warmup; an initial implementation warmup issue was corrected before primary deep-model fits.

## Whole-system results

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| C_SMALL | 92 | 0.391304 | 0.373488 | 0.282224 | 0.760851 | 0.012719 | 0.016730 | 0.023788 | 0.489130 | 0.695652 | 0.039796 |
| H_MULTISCALE | 92 | 0.717391 | 0.697146 | 0.183885 | 0.549140 | 0.010308 | 0.013131 | 0.019636 | 0.565217 | 0.782609 | 0.039336 |
| H_WARNINGS | 92 | 0.782609 | 0.791001 | 0.181999 | 0.550119 | 0.010226 | 0.013503 | 0.019949 | 0.521739 | 0.771739 | 0.038329 |
| H_CORRELATION | 92 | 0.782609 | 0.794388 | 0.185679 | 0.557864 | 0.010205 | 0.013555 | 0.019947 | 0.565217 | 0.782609 | 0.037566 |
| H_ROTATION | 92 | 0.771739 | 0.774794 | 0.183902 | 0.553201 | 0.010267 | 0.013582 | 0.019907 | 0.532609 | 0.771739 | 0.037817 |
| H_DYNAMIC | 92 | 0.760870 | 0.768747 | 0.183237 | 0.552258 | 0.010210 | 0.013532 | 0.019947 | 0.597826 | 0.760870 | 0.037891 |
| H_DYNAMIC_CORE | 92 | 0.608696 | 0.572327 | 0.250697 | 0.699595 | 0.012260 | 0.016114 | 0.023595 | 0.478261 | 0.695652 | 0.038483 |
| Q_ETF_NOSIZE | 92 | 0.760870 | 0.768747 | 0.191477 | 0.569238 | 0.010074 | 0.013532 | 0.019376 | 0.565217 | 0.793478 | 0.037756 |
| Q_ETF_VOLUME | 92 | 0.750000 | 0.759313 | 0.183198 | 0.551577 | 0.009936 | 0.013289 | 0.019186 | 0.500000 | 0.771739 | 0.038041 |
| Q_ETF_PRICE | 92 | 0.760870 | 0.765360 | 0.195510 | 0.578393 | 0.010310 | 0.013718 | 0.019972 | 0.543478 | 0.782609 | 0.038265 |


## Immediate-parent increments

| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| H_MULTISCALE | I03_nosize | brier | 92 | -0.001839 |
| H_MULTISCALE | I03_nosize | crps | 92 | -0.000110 |
| H_WARNINGS | I03_nosize | brier | 92 | 0.000048 |
| H_WARNINGS | I03_nosize | crps | 92 | -0.000027 |
| H_CORRELATION | I03_nosize | brier | 92 | -0.003633 |
| H_CORRELATION | I03_nosize | crps | 92 | -0.000006 |
| H_ROTATION | I03_nosize | brier | 92 | -0.001855 |
| H_ROTATION | I03_nosize | crps | 92 | -0.000068 |
| Q_ETF_NOSIZE | I03_nosize | brier | 92 | -0.009430 |
| Q_ETF_NOSIZE | I03_nosize | crps | 92 | 0.000125 |
| Q_ETF_VOLUME | I03_nosize | brier | 92 | -0.001151 |
| Q_ETF_VOLUME | I03_nosize | crps | 92 | 0.000262 |
| Q_ETF_PRICE | I03_nosize | brier | 92 | -0.013463 |
| Q_ETF_PRICE | I03_nosize | crps | 92 | -0.000111 |


The larger feature library does not automatically improve weekly proper scores. Selected multi-scale divergences worsen weekly Brier by .001839 and CRPS by .00010956 versus I03. The full eight-variable evolution addition also slightly worsens both losses. Compact dynamic models are comparisons between different feature sets: H_DYNAMIC_CORE uses four price/risk inputs plus eight evolving variables, whereas C_SMALL includes eight static inputs. Its improvement over C_SMALL is not a clean one-variable treatment effect and does not beat the57-input native reference.

## Sector redundancy and ETF decomposition

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| W2_DEF_NORM | 92 | 0.782609 | 0.791001 | 0.169862 | 0.522778 | 0.010095 | 0.013198 | 0.019755 | 0.521739 | 0.782609 | 0.038263 |
| W2_DEF_PC | 92 | 0.782609 | 0.791001 | 0.170208 | 0.523784 | 0.010306 | 0.013416 | 0.020118 | 0.510870 | 0.793478 | 0.039198 |
| F_DROP_TOP3 | 92 | 0.793478 | 0.793662 | 0.171268 | 0.526385 | 0.009995 | 0.013184 | 0.019580 | 0.554348 | 0.750000 | 0.037123 |
| Q_ETF_VOLUME | 92 | 0.750000 | 0.759313 | 0.183198 | 0.551577 | 0.009936 | 0.013289 | 0.019186 | 0.500000 | 0.771739 | 0.038041 |
| W2_NODEF_VOLUME | 92 | 0.760870 | 0.765360 | 0.175312 | 0.533128 | 0.009873 | 0.013138 | 0.018992 | 0.521739 | 0.782609 | 0.038203 |
| W2_NOAUTO_VOLUME | 92 | 0.750000 | 0.755926 | 0.178802 | 0.541915 | 0.009756 | 0.013051 | 0.018979 | 0.532609 | 0.771739 | 0.037657 |
| L01 | 92 | 0.663043 | 0.653362 | 0.197610 | 0.582153 | 0.009963 | 0.013409 | 0.019166 | 0.543478 | 0.771739 | 0.036633 |


Defensive-group deletion, a train-only whitened first principal component, and standardized-group normalization all give similar weekly Brier (.169803/.170208/.169862). Group normalization divides the six standardized defensive fields by sqrt(6), changing the effective Ridge penalty; PCA is fitted separately within each inner/full training partition. This is evidence about representation/regularization, not evidence that defensive sectors are economically irrelevant. Auto21 removal was defined from July training coefficients, then crossed with five genuine ETF volume-ratio inputs in an explicitly later exposed-data batch.

L01 inherits full I00 native fields, including size, plus15 ETF inputs. Q_ETF_NOSIZE isolates I03 plus all15; Q_ETF_VOLUME uses onlyfive activity ratios; Q_ETF_PRICE uses theten return/variation variables. Volume ratios are reported ETF traded activity, not constituent breadth or native-index traded volume. This decomposition distinguishes activity from cross-asset exposure. The best distribution point score is W2_NOAUTO_VOLUME CRPS .009755832,75% accuracy,Brier .178802,80% coverage77.17%,mean80% width3.7657 percentage points. It improves L01 CRPS by .000206985 (about2.08%) on the same92 origins; the simultaneous95% gain interval includes zero. Adding volume improves CRPS relative to its auto-deletion parent but worsens that parent's Brier, so it is not a universal upgrade.

| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| W2_NODEF_VOLUME | F_NO_DEFENSIVE | brier | 92 | -0.005509 |
| W2_NODEF_VOLUME | F_NO_DEFENSIVE | crps | 92 | 0.000194 |
| W2_NOAUTO_VOLUME | F_DROP_TOP3 | brier | 92 | -0.007534 |
| W2_NOAUTO_VOLUME | F_DROP_TOP3 | crps | 92 | 0.000239 |
| W2_DEF_PC | I03_nosize | brier | 92 | 0.011838 |
| W2_DEF_PC | I03_nosize | crps | 92 | -0.000107 |
| W2_DEF_NORM | I03_nosize | brier | 92 | 0.012184 |
| W2_DEF_NORM | I03_nosize | crps | 92 | 0.000104 |


## What we learned and retained

Native cross-index representation remains the strongest research family. Some broad, bank, cyclical, risk and IT relationships matter within the fitted model, while large sets of fresh divergences do not offer dependable increments. Keep the fixed I03/L01 references and the compact group-normalized/auto-volume candidates for future versioned research. Do not interpret constituent-proxy or ETF effects as genuine exchange-wide breadth without an appropriate historical universe. Detailed feature definitions, raw missing fractions and every tested column list remain in `feature-definitions.json`, `forensic-registry.json`, `model-registry.json` and the Python feature generator.

The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.
