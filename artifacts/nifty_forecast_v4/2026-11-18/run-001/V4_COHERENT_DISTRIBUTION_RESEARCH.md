# V4 coherent distribution research

Four fixed alternatives, no search expansion or outer-driven model selection:

|ID|definition|
|---|---|
|D00_empirical|Latest252 matured return atoms, uniform weights; baseline|
|D01_regime_shrunk|Latest252; causal ret21 sign x training-median RV21; conditional counts plus30 unconditional pseudoobservations|
|D02_student_shrunk|Fixed df5 Student quantile atoms501; location .5*sectorRidge+.5*historicalmean; RMS inner residual scale, floor .005*sqrt(h/5)|
|D03_residual_shrunk|Same shrunk location plus inner heldout sectorRidge residual atoms; no posthoc rescaling|

D00 is the full latest 252 weighted return law, not V3's201-quantile numerical
approximation. D01 uses the same observations and 30 unconditional pseudoobservations.
D02 uses501 fixed Student-t(df5) quantile atoms, scaled by inner residual RMS times
sqrt(3/5), floor .005*sqrt(h/5) before that t variance conversion. D02/D03 location
is .5*sector-Ridge mean+.5*training historical mean; D03 adds the 42 raw heldout
inner residuals. Those residuals are not 42 independent outcomes. Atoms at or below
-100% are floored to-.999999; outputs describe the actual finite law after flooring.
These are new exploratory definitions, not the exact V3 standalone classifier.

For sorted return atoms r_i and normalized weights w_i, all endpoint statistics
come from F: P(up)=sum(w_i for r_i>0), E[R]=sum(w_i*r_i), median/quantiles from the
weighted inverse CDF, buckets from the same weights, E[endpoint]=reference*(1+E[R]),
and expected absolute move=sum(w_i*abs(r_i)). Quantiles cannot cross. Zero empirical
bucket probability means no mass in the fitted finite support, not impossible
real-world outcomes. Log losses alone use1e-6 numerical clipping; displayed laws
are not altered to conceal an extreme probability.

Weighted CRPS=E|R-y|-.5*E|R-R'| is verified against its brute-force definition.
Probability, bucket, endpoint, quantile and magnitude identities are tested.
Future path breaches and future realized volatility are UNAVAILABLE from these
endpoint laws. Endpoint dispersion is labeled endpoint-return standard deviation.
No annualized path-risk estimate is invented from it.

1,928 predictions were scored over identical V3 prequential development/outer
origins. All model parameters and comparison rules were registered before this
new study's scores were inspected; historical dates were already exposed.

|horizon|model|n/disjoint|CRPS|Brier|mean MAE|mean RMSE|median MAE|50 coverage|80 coverage|80 width|
|---|---|---|---|---|---|---|---|---|---|---|
|5|D00_empirical|92/19|0.012210|0.258296|1.637%|2.321%|1.643%|50.0%|72.8%|3.994%|
|5|D01_regime_shrunk|92/19|0.012304|0.266327|1.622%|2.345%|1.681%|53.3%|79.3%|4.338%|
|5|D02_student_shrunk|92/19|0.010896|0.219759|1.471%|2.013%|1.471%|41.3%|67.4%|3.325%|
|5|D03_residual_shrunk|92/19|0.011882|0.206257|1.469%|2.278%|1.481%|48.9%|67.4%|3.129%|
|21|D00_empirical|76/4|0.028363|0.279282|3.739%|4.879%|3.833%|26.3%|61.8%|7.275%|
|21|D01_regime_shrunk|76/4|0.028395|0.269010|3.824%|4.788%|3.648%|31.6%|55.3%|9.008%|
|21|D02_student_shrunk|76/4|0.027553|0.260640|3.511%|4.292%|3.511%|30.3%|39.5%|6.392%|
|21|D03_residual_shrunk|76/4|0.030587|0.283320|3.641%|4.808%|3.996%|32.9%|44.7%|6.341%|

Weekly D02 CRPS improves descriptively; D03 binary Brier looks attractive, yet
both80% intervals cover only 67.4%. Monthly D02 coverage39.5% and D03 coverage44.7%
remain unacceptable. Coherence is achieved; calibration is not. None of the 45
V4 comparison lower bounds is positive under the applicable simultaneous family.
Monthly intervals are withheld (76<168 rows required), not reported as significant.

distribution-metrics.json also records pinball, bucket Brier and observed/predicted
frequency for every bucket. distribution-predictions.csv retains mean/median and
per-origin point errors; D00 supplies matched historical mean and median controls.
Separate development metrics are saved; no new winner is selected from outer
scores. Quantile regressions/extra mixtures are not added after seeing these results.
Finite-support tails, regime sparsity, drift and residual dependence remain limits.
