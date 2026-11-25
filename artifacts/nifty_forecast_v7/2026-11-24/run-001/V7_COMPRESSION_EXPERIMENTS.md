# NIFTY V7 · Compression Experiments

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

The initial batch compared 18 controlled configurations. Group definitions and unsupervised transforms were learnt separately in outer and purged inner fits. Greedy pruning at |r|≥.90 retained a deterministic first representative. Average linkage at .75 similarity gave the medoid, sign-aligned means and balance variants. Cluster balance divides standardized features by √cluster size. Economic aggregation uses the named sector families. Six-component PCA replaces the 38 relative-return inputs and retains the remaining risk, price and participation inputs. PCA whitening and Ledoit–Wolf whitening are separate treatments. Because Ledoit–Wolf shrinks toward a scaled identity, it preserves sample eigenvectors and changes the scale in this construction. [Ledoit and Wolf’s covariance estimator](https://www.ledoit.net/Well-conditioned2004.pdf)

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_RAW | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.012959 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| C_DUP | 92 | 0.750000 | 0.752540 | 0.188090 | 0.562591 | 0.010317 | 0.013717 | 0.013217 | 0.019858 | 0.554348 | 0.771739 | 0.038691 |
| C_DUP_BALANCED | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.012959 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| C_DEF | 92 | 0.782609 | 0.791001 | 0.169862 | 0.522778 | 0.010095 | 0.013198 | 0.012637 | 0.019755 | 0.521739 | 0.782609 | 0.038263 |
| C_NO_DEF | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| C_BANK_DEF | 92 | 0.782609 | 0.794388 | 0.171428 | 0.526247 | 0.010047 | 0.013160 | 0.012649 | 0.019632 | 0.521739 | 0.771739 | 0.038584 |
| C_PRUNE | 92 | 0.760870 | 0.772134 | 0.174006 | 0.532046 | 0.010009 | 0.013169 | 0.012537 | 0.019519 | 0.554348 | 0.771739 | 0.037991 |
| C_REPRESENT | 92 | 0.750000 | 0.752540 | 0.186381 | 0.559175 | 0.010281 | 0.013487 | 0.013125 | 0.019851 | 0.565217 | 0.782609 | 0.038224 |
| C_CLUSTER_MEAN | 92 | 0.750000 | 0.759313 | 0.178519 | 0.542335 | 0.010102 | 0.013367 | 0.012841 | 0.019685 | 0.554348 | 0.771739 | 0.038252 |
| C_CLUSTER_BAL | 92 | 0.750000 | 0.759313 | 0.177513 | 0.540382 | 0.010195 | 0.013487 | 0.012862 | 0.019879 | 0.532609 | 0.782609 | 0.037611 |
| C_FACTOR_GROUPS | 92 | 0.695652 | 0.668118 | 0.211836 | 0.615000 | 0.011421 | 0.014903 | 0.014331 | 0.022078 | 0.521739 | 0.695652 | 0.037406 |
| C_PCA | 92 | 0.706522 | 0.714804 | 0.192759 | 0.573758 | 0.011034 | 0.014152 | 0.013829 | 0.021020 | 0.554348 | 0.760870 | 0.042095 |
| C_PCA_WHITE | 92 | 0.717391 | 0.714078 | 0.199695 | 0.588701 | 0.011275 | 0.014593 | 0.014104 | 0.021574 | 0.510870 | 0.739130 | 0.038624 |
| C_PCA_LW | 92 | 0.717391 | 0.714078 | 0.199401 | 0.588048 | 0.011266 | 0.014577 | 0.014092 | 0.021556 | 0.521739 | 0.739130 | 0.038765 |
| C_PCA_ROLL | 92 | 0.706522 | 0.714804 | 0.207871 | 0.606140 | 0.011273 | 0.014718 | 0.014295 | 0.021525 | 0.543478 | 0.760870 | 0.039362 |
| C_SPARSE | 92 | 0.717391 | 0.724238 | 0.198999 | 0.587460 | 0.011183 | 0.014516 | 0.013862 | 0.021522 | 0.554348 | 0.771739 | 0.040904 |
| C_GROUP_LASSO | 92 | 0.760870 | 0.745041 | 0.201743 | 0.593338 | 0.010910 | 0.014553 | 0.014253 | 0.021072 | 0.543478 | 0.750000 | 0.036402 |
| C_ELASTIC | 92 | 0.771739 | 0.757862 | 0.184607 | 0.554242 | 0.009695 | 0.012635 | 0.011999 | 0.018339 | 0.532609 | 0.804348 | 0.042881 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_RAW | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.037168 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| C_DUP | 76 | 0.552632 | 0.607168 | 0.256883 | 0.710023 | 0.029212 | 0.038633 | 0.037227 | 0.047723 | 0.315789 | 0.500000 | 0.077478 |
| C_DUP_BALANCED | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.037168 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| C_DEF | 76 | 0.552632 | 0.592115 | 0.258170 | 0.714102 | 0.030040 | 0.038735 | 0.037582 | 0.049054 | 0.302632 | 0.500000 | 0.072992 |
| C_NO_DEF | 76 | 0.539474 | 0.575986 | 0.264309 | 0.726979 | 0.030275 | 0.038624 | 0.037553 | 0.049682 | 0.315789 | 0.500000 | 0.071598 |
| C_BANK_DEF | 76 | 0.539474 | 0.581004 | 0.252902 | 0.701294 | 0.029437 | 0.037386 | 0.036303 | 0.048387 | 0.302632 | 0.526316 | 0.071422 |
| C_PRUNE | 76 | 0.605263 | 0.646595 | 0.243654 | 0.683581 | 0.029211 | 0.038453 | 0.036327 | 0.047774 | 0.302632 | 0.513158 | 0.074771 |
| C_REPRESENT | 76 | 0.592105 | 0.640502 | 0.244210 | 0.683973 | 0.028698 | 0.036828 | 0.035565 | 0.046851 | 0.289474 | 0.486842 | 0.068658 |
| C_CLUSTER_MEAN | 76 | 0.592105 | 0.640502 | 0.246663 | 0.690830 | 0.029151 | 0.037741 | 0.036431 | 0.047311 | 0.302632 | 0.500000 | 0.070933 |
| C_CLUSTER_BAL | 76 | 0.592105 | 0.640502 | 0.253136 | 0.705354 | 0.029434 | 0.038061 | 0.036762 | 0.047703 | 0.302632 | 0.513158 | 0.071572 |
| C_FACTOR_GROUPS | 76 | 0.236842 | 0.235125 | 0.379073 | 0.976473 | 0.032535 | 0.042820 | 0.043896 | 0.051297 | 0.131579 | 0.421053 | 0.065254 |
| C_PCA | 76 | 0.434211 | 0.436918 | 0.292750 | 0.787687 | 0.028864 | 0.038774 | 0.038604 | 0.047346 | 0.197368 | 0.526316 | 0.069859 |
| C_PCA_WHITE | 76 | 0.381579 | 0.387455 | 0.340176 | 0.896002 | 0.030872 | 0.041181 | 0.041514 | 0.049154 | 0.131579 | 0.500000 | 0.067004 |
| C_PCA_LW | 76 | 0.381579 | 0.387455 | 0.338709 | 0.892857 | 0.030800 | 0.041098 | 0.041433 | 0.049091 | 0.131579 | 0.486842 | 0.067032 |
| C_PCA_ROLL | 76 | 0.197368 | 0.221864 | 0.402258 | 1.030145 | 0.033040 | 0.043356 | 0.046349 | 0.050421 | 0.092105 | 0.342105 | 0.061585 |
| C_SPARSE | 76 | 0.381579 | 0.387455 | 0.322756 | 0.860137 | 0.029783 | 0.040074 | 0.040725 | 0.047889 | 0.144737 | 0.539474 | 0.070058 |
| C_GROUP_LASSO | 76 | 0.565789 | 0.603226 | 0.245426 | 0.686586 | 0.029693 | 0.039128 | 0.036803 | 0.048524 | 0.289474 | 0.513158 | 0.073188 |
| C_ELASTIC | 76 | 0.657895 | 0.670968 | 0.201414 | 0.591339 | 0.029193 | 0.040274 | 0.041771 | 0.049925 | 0.447368 | 0.750000 | 0.099270 |


Doubling the six defensive inputs increased weekly Brier from .182047 to .188090. Giving both copies the compensating 1/√2 weight returned the original forecasts numerically. Deletion and targeted normalization reach .169803 and .169862. Extending normalization to banks yields .171428. Greedy pruning helps relative to the raw reference at .174006, although it misses the defensive-specific scores. Broad PCA and sparse PCA fail to improve the original Brier or CRPS. Their retained directions explain input variance, which does not isolate useful conditional return information.

Cluster-balanced Elastic Net improves weekly CRPS from .009756 for the V6 distribution winner to .009695, while Brier worsens from .178802 to .184607. On the identical raw features, Elastic Net without balancing gives Brier .245135 and CRPS .011334. This contrast isolates the importance of feature scaling for this fitted objective. The embargo sensitivity variant records CRPS .009665. It was selected after seeing initial results and must be treated as a follow-up. It collapses to CRPS .014315 under the shorter-window stress. Economic group lasso has weekly Brier .201743 and CRPS .010910.

| model | baseline | metric | n | gain | adjusted95_block10 |
| --- | --- | --- | --- | --- | --- |
| C_CLUSTER_BAL | V6_BRIER | brier | 92 | -0.007710 | [-0.047866828572194486, 0.03244604371235682] |
| C_CLUSTER_BAL | V6_BRIER | crps | 92 | -0.000127 | [-0.0011173148082629987, 0.0008629471771723517] |
| C_CLUSTER_BAL | V6_CRPS | brier | 92 | 0.001288 | [-0.023461091447961442, 0.02603791988465013] |
| C_CLUSTER_BAL | V6_CRPS | crps | 92 | -0.000439 | [-0.0014651764903398634, 0.0005870846832155103] |
| C_ELASTIC | V6_BRIER | brier | 92 | -0.014804 | [-0.07759060726150645, 0.047982646927614434] |
| C_ELASTIC | V6_BRIER | crps | 92 | 0.000373 | [-0.0019226779503525877, 0.0026677950218058355] |
| C_ELASTIC | V6_CRPS | brier | 92 | -0.005805 | [-0.04292618376714074, 0.031315836729775066] |
| C_ELASTIC | V6_CRPS | crps | 92 | 0.000061 | [-0.0013021855237257253, 0.0014235784191452669] |
| C_PRUNE | V6_BRIER | brier | 92 | -0.004203 | [-0.0419500253082012, 0.03354465953870499] |
| C_PRUNE | V6_BRIER | crps | 92 | 0.000059 | [-0.0008548521143480275, 0.0009721513728718576] |
| C_PRUNE | V6_CRPS | brier | 92 | 0.004796 | [-0.01581904474398849, 0.025411292271018623] |
| C_PRUNE | V6_CRPS | crps | 92 | -0.000253 | [-0.0009009809191684651, 0.00039455600165858924] |
| T_ELASTIC_EMBARGO | V6_BRIER | brier | 92 | -0.014331 | [-0.07465766607260821, 0.04599618411871554] |
| T_ELASTIC_EMBARGO | V6_BRIER | crps | 92 | 0.000402 | [-0.0025711607215019184, 0.0033755923705106623] |
| T_ELASTIC_EMBARGO | V6_CRPS | brier | 92 | -0.005332 | [-0.03612272176476268, 0.025458853107396356] |
| T_ELASTIC_EMBARGO | V6_CRPS | crps | 92 | 0.000090 | [-0.0019859773940986555, 0.0021666848670736927] |


The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history. Brier and log loss score sign probabilities. CRPS scores the entire endpoint return distribution. Lower scores are better. CRPS, MAE and interval widths are in fractional return units. A width of .04 spans four percentage points. Gain means matched control loss minus candidate loss.
