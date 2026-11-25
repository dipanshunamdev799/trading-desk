# NIFTY V6 — Winner Forensics

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Reproduction and actual model

Exactly reproduced 81 named model/fold vectors for I03_nosize, I00, I01_legacy, I02_newindices, L01, L02, V4 D02/D03 and M05. Probability, mean and median were compared at 1e-12 where available; M05's separate legacy classifier was checked as such. Two fresh July fits reproduced I03 and L01, and the independent V6 engine reproduced all 336 outer I03/L01 forecasts with maximum probability difference zero. See `reproduction.json` and `reference-engine-verification.json`.

I03 retains 57 native price/risk/index features. It standardizes with training-only imputation/centering/scaling, clips standardized inputs at ±5, and fits Ridge(alpha=100). Columns require at least 30 finite training values. Each monthly refit uses only labels whose endpoint is strictly before its cutoff. The latest 42 mature training-origin returns form an inner validation segment; the fitting segment is purged against the first validation origin. Conditional residual atoms from that inner fit receive 65% mass; the latest at-most-252 mature historical target returns receive 35%. Probability, mean and quantiles derive from that single distribution. These constants were inherited, not optimized on V6 evaluation scores.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I03_nosize | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| I00 | 92 | 0.760870 | 0.751814 | 0.186099 | 0.558036 | 0.010224 | 0.013539 | 0.019852 | 0.554348 | 0.760870 | 0.037708 |
| I01_legacy | 92 | 0.728261 | 0.720126 | 0.188888 | 0.564913 | 0.010750 | 0.013958 | 0.020603 | 0.565217 | 0.750000 | 0.037541 |
| I02_newindices | 92 | 0.663043 | 0.643203 | 0.200000 | 0.587242 | 0.010231 | 0.013682 | 0.019860 | 0.565217 | 0.760870 | 0.037466 |
| L01 | 92 | 0.663043 | 0.653362 | 0.197610 | 0.582153 | 0.009963 | 0.013409 | 0.019166 | 0.543478 | 0.771739 | 0.036633 |
| L02 | 92 | 0.630435 | 0.618287 | 0.203245 | 0.591604 | 0.010531 | 0.013944 | 0.019649 | 0.576087 | 0.793478 | 0.041287 |
| V4_D02_student_shrunk | 92 | 0.608696 | 0.656991 | 0.219759 | 0.629825 | 0.010896 | 0.014707 | 0.020132 | 0.413043 | 0.673913 | 0.033246 |
| V4_D03_residual_shrunk | 92 | 0.684783 | 0.648524 | 0.206257 | 0.607870 | 0.011882 | 0.014686 | 0.022780 | 0.489130 | 0.673913 | 0.031291 |
| V4_M05_lgbm | 92 | 0.663043 | 0.633043 | 0.226049 | 0.645492 | 0.011817 | 0.015190 | 0.021320 | 0.423913 | 0.630435 | 0.033626 |


I03's 76.086957% equals 70/92 correct: predicted up on 47 origins, actual up on 39; 32 true positives, 15 false positives, 38 true negatives and seven false negatives. Thus it is not an always-bullish classifier. Up recall is 32/39=82.05%; down recall 38/53=71.70%. I00 also gets 70 correct but predicts up only 37 times (27 TP,10 FP,43 TN,12 FN). L01 predicts up38 times and gets61/92 correct. Their identical or different accuracy can conceal materially different probability losses. `direction-confusion.json` contains exact counts.

## What removing size actually did

V5's I03 simultaneously removed eight possible size columns and recomputed five index aggregates. V6 separates these interventions. July I00 actually entered only six size columns: the two Smallcap500 series did not yet meet the 30-observation requirement. Its actual 63 entered columns must not be described as 65 fully observed inputs.

| variant | n | brier | crps | gain_vs_I00 | probability_change_mean_abs | flips | correct_to_wrong | wrong_to_correct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_SIZE_COLS | 92 | 0.181370 | 0.010150 | 0.004729 | 0.034149 | 8 | 5 | 3 |
| F_SIZE_AGG | 92 | 0.186804 | 0.010256 | -0.000706 | 0.012953 | 6 | 1 | 5 |
| F_SMALL_ONLY | 92 | 0.192898 | 0.010446 | -0.006799 | 0.024392 | 7 | 5 | 2 |
| F_MID_ONLY | 92 | 0.179398 | 0.010034 | 0.006701 | 0.039195 | 11 | 5 | 6 |
| F_SIZE_ORTHO | 92 | 0.195862 | 0.010390 | -0.009763 | 0.022037 | 2 | 2 | 0 |


I00 Brier is .186098807; column removal alone .181369971; aggregate replacement alone .186804328; I03 both .182046521. The measured improvement is driven by column removal; recomputed aggregates slightly reduce that improvement. Removing only mid-cap inputs yields .179397932; removing only small-cap inputs worsens it to .192898145. Residualizing size against other inputs worsens it to .195861945. Therefore the evidence does not support saying all mid/small-cap information is useless. Smallcap500 histories start 2026-05-11, have 132 raw observations, and only127/111 usable five-/21-session relative-return observations across403 origins. A family median missingness statistic had obscured this individual short history.

| feature | observed_training | missing_fraction | entered_original_full_model | max_abs_correlation_to_retained | raw_std |
| --- | --- | --- | --- | --- | --- |
| i_idx_NIFTY_MIDCAP_100_rel5 | 300 | 0.000000 | True | 0.935541 | 0.010912 |
| i_idx_NIFTY_MIDCAP_100_rel21 | 300 | 0.000000 | True | 0.940858 | 0.023127 |
| i_idx_NIFTY_MIDCAP_150_rel5 | 300 | 0.000000 | True | 0.951114 | 0.010548 |
| i_idx_NIFTY_MIDCAP_150_rel21 | 300 | 0.000000 | True | 0.963329 | 0.022151 |
| i_idx_Nifty_Midcap_50_rel5 | 300 | 0.000000 | True | 0.852540 | 0.010797 |
| i_idx_Nifty_Midcap_50_rel21 | 300 | 0.000000 | True | 0.871816 | 0.021652 |
| i_idx_Nifty_Smallcap_500_rel5 | 24 | 0.920000 | False | 0.858303 | 0.015027 |
| i_idx_Nifty_Smallcap_500_rel21 | 8 | 0.973333 | False | 0.985620 | 0.018828 |


Raw scale differences are handled by standardization; redundancy, missingness, relationship drift and Ridge penalty geometry remain plausible mechanisms. This study identifies operational contributors, not a unique causal economic explanation. Native sectors and size indices are correlated; adding multiple standardized proxies effectively changes the penalty on shared directions. Removing, compressing or normalizing a correlated defensive block all improves weekly Brier to about .170, which strengthens the penalty-geometry hypothesis. It does not establish the absence of economic information in those sectors.

## Influential inputs versus useful inputs

Exact query-date train-median replacements show the largest mean absolute probability changes from pharma21 (5.7408 percentage points), auto21(4.8556), healthcare21(4.7911), InfraLog21(4.6009), NIFTY ret10(4.5452), and IT21(4.4576). These are conditional model perturbations, not causal effects. The exact full table is `exact-feature-effects.csv`. The earlier `feature-influence.csv` field named `prediction_change_median_replacement` is a legacy mislabeled training-MEAN standardized-zero proxy; the exact-median table supersedes that interpretation.

| horizon | fold | feature | coefficient | training_observed |
| --- | --- | --- | --- | --- |
| 5 | 2026-07 | p_ret1 | -0.000971 | 300 |
| 5 | 2026-07 | p_ret3 | 0.000165 | 300 |
| 5 | 2026-07 | p_ret5 | -0.000224 | 300 |
| 5 | 2026-07 | p_ret10 | -0.002566 | 300 |
| 5 | 2026-07 | p_ret21 | -0.000545 | 300 |
| 5 | 2026-07 | p_ret63 | -0.002440 | 300 |
| 5 | 2026-07 | p_rv5 | 0.000888 | 300 |
| 5 | 2026-07 | p_rv21 | -0.000029 | 300 |
| 5 | 2026-07 | p_rv63 | 0.000350 | 300 |
| 5 | 2026-07 | p_trend | -0.001117 | 300 |
| 5 | 2026-07 | p_range | 0.000826 | 300 |
| 5 | 2026-07 | p_acceleration | 0.000040 | 300 |
| 5 | 2026-07 | p_vix | 0.001461 | 300 |
| 5 | 2026-07 | i_bank_nifty_rel5 | 0.001943 | 300 |
| 5 | 2026-07 | i_bank_nifty_rel21 | 0.000198 | 300 |


Pharma, healthcare and auto 21-session relative-strength coefficients are negative in all five weekly refits; IT21 is positive in all five. That suggests a mixture of conditional reversion/sector rotation and risk conditioning, rather than one pure momentum rule. Crucially, removing some of the most influential defensive/auto variables improves outer scores. Stable coefficients and influence do not establish incremental forecast usefulness. Development-only price-residual conditional Spearman tests cover114 selected feature/horizon cases with200 block shifts and within-family Benjamini–Hochberg adjustment: 14 have nominal q<.05, minimum q=0.040511727. This selected native family and its surrounding model search are exposed; those14 are not independently confirmed features, causal discoveries, or directly comparable to V5's differently defined test family.

## Structural stress results

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| W2_DEF_NORM | 92 | 0.782609 | 0.791001 | 0.169862 | 0.522778 | 0.010095 | 0.013198 | 0.019755 | 0.521739 | 0.782609 | 0.038263 |
| W2_DEF_PC | 92 | 0.782609 | 0.791001 | 0.170208 | 0.523784 | 0.010306 | 0.013416 | 0.020118 | 0.510870 | 0.793478 | 0.039198 |
| F_DROP_TOP3 | 92 | 0.793478 | 0.793662 | 0.171268 | 0.526385 | 0.009995 | 0.013184 | 0.019580 | 0.554348 | 0.750000 | 0.037123 |
| F_NO_CYCLICAL | 92 | 0.641304 | 0.637881 | 0.212184 | 0.612711 | 0.010989 | 0.014530 | 0.020899 | 0.532609 | 0.706522 | 0.035646 |
| F_NO_PRICE_RISK | 92 | 0.684783 | 0.685776 | 0.210102 | 0.610965 | 0.010881 | 0.014238 | 0.020813 | 0.521739 | 0.728261 | 0.037492 |
| F_NO_IT | 92 | 0.728261 | 0.743832 | 0.192481 | 0.571103 | 0.010620 | 0.013927 | 0.020402 | 0.510870 | 0.771739 | 0.038786 |
| F_NO_AGGREGATES | 92 | 0.804348 | 0.806483 | 0.178840 | 0.542845 | 0.010060 | 0.013382 | 0.019553 | 0.532609 | 0.771739 | 0.037934 |
| F_ROLL126 | 92 | 0.695652 | 0.708757 | 0.214846 | 0.622393 | 0.011160 | 0.015206 | 0.021541 | 0.543478 | 0.815217 | 0.046136 |
| F_ROLL189 | 92 | 0.663043 | 0.687228 | 0.220732 | 0.631432 | 0.011210 | 0.014807 | 0.021171 | 0.554348 | 0.750000 | 0.041578 |
| F_ALPHA30 | 92 | 0.739130 | 0.729560 | 0.188018 | 0.560849 | 0.010087 | 0.013247 | 0.019198 | 0.543478 | 0.760870 | 0.039183 |
| F_ALPHA300 | 92 | 0.728261 | 0.730285 | 0.190670 | 0.569058 | 0.010694 | 0.014096 | 0.020715 | 0.521739 | 0.750000 | 0.036814 |
| F_INTERNAL_LAG1 | 92 | 0.782609 | 0.780842 | 0.189065 | 0.565732 | 0.010465 | 0.013755 | 0.020145 | 0.565217 | 0.728261 | 0.037684 |
| F_INTERNAL_LAG2 | 92 | 0.641304 | 0.651427 | 0.216532 | 0.622118 | 0.011144 | 0.015014 | 0.021109 | 0.467391 | 0.717391 | 0.038154 |
| F_ALL_LAG1 | 92 | 0.760870 | 0.748428 | 0.195955 | 0.581302 | 0.010630 | 0.014146 | 0.020234 | 0.576087 | 0.728261 | 0.037725 |
| F_SYNTH_REV1BP | 92 | 0.760870 | 0.768747 | 0.181618 | 0.548401 | 0.010196 | 0.013501 | 0.019806 | 0.521739 | 0.760870 | 0.037720 |


| model | score | test | min_gain | max_gain | positive_cases | cases |
| --- | --- | --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | brier | leave_month_out | 0.004644 | 0.030530 | 5 | 5 |
| F_NO_DEFENSIVE | brier | disjoint_phase | -0.002484 | 0.035583 | 4 | 5 |
| F_NO_DEFENSIVE | brier | remove_best_overlapping_origins | -0.008313 | 0.009870 | 3 | 4 |
| F_NO_DEFENSIVE | crps | leave_month_out | -0.000578 | 0.000204 | 2 | 5 |
| F_NO_DEFENSIVE | crps | disjoint_phase | -0.000388 | 0.000487 | 1 | 5 |
| F_NO_DEFENSIVE | crps | remove_best_overlapping_origins | -0.000786 | -0.000199 | 0 | 4 |
| W2_DEF_NORM | brier | leave_month_out | 0.007746 | 0.022858 | 5 | 5 |
| W2_DEF_NORM | brier | disjoint_phase | -0.001096 | 0.027007 | 4 | 5 |
| W2_DEF_NORM | brier | remove_best_overlapping_origins | -0.002146 | 0.010177 | 3 | 4 |
| W2_DEF_NORM | crps | leave_month_out | -0.000489 | 0.000155 | 2 | 5 |
| W2_DEF_NORM | crps | disjoint_phase | -0.000512 | 0.000406 | 2 | 5 |
| W2_DEF_NORM | crps | remove_best_overlapping_origins | -0.000707 | -0.000197 | 0 | 4 |
| W2_NOAUTO_VOLUME | brier | leave_month_out | -0.001807 | 0.009371 | 3 | 5 |
| W2_NOAUTO_VOLUME | brier | disjoint_phase | -0.005761 | 0.011100 | 3 | 5 |
| W2_NOAUTO_VOLUME | brier | remove_best_overlapping_origins | -0.010596 | 0.001301 | 1 | 4 |
| W2_NOAUTO_VOLUME | crps | leave_month_out | -0.000070 | 0.000498 | 4 | 5 |
| W2_NOAUTO_VOLUME | crps | disjoint_phase | -0.000116 | 0.000511 | 4 | 5 |
| W2_NOAUTO_VOLUME | crps | remove_best_overlapping_origins | -0.000169 | 0.000153 | 2 | 4 |


Month exclusions here are evaluation stress diagnostics, not retroactive month-selection trades. Regime omission is an actual training refit; the sideways-excluded July weekly and July/August monthly fits are non-estimable under the frozen minimum80 outer/60 inner rule. `group-permutation.csv` applies common within-month five-session circular family shifts; it is a dependence-preserving diagnostic with noncausal rearranged query inputs, never an eligible forecasting candidate. `rolling-performance.csv`, `regime-slices.json`, `stability.json` and the per-fold source details retain all results, including deterioration.

Actual observed V3→V5 overlapping domestic closes show zero revisions in the retained source vintages. Synthetic one-basis-point time-varying source perturbations are separately labeled sensitivity scenarios; zero observed revisions does not establish immutable vendor history. Additional one-/two-session feature lags test origin fragility; original source receipts from 2025 were not archived, so historical availability remains a reconstruction.

| model | baseline | metric | n | mean_improvement | simultaneous95 |
| --- | --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | I03_nosize | brier | 92 | 0.012244 | [-0.03628352133406396, 0.06077066764186246] |
| F_NO_DEFENSIVE | L01 | crps | 92 | -0.000105 | [-0.0023467642852621263, 0.002137010447939685] |
| W2_DEF_NORM | I03_nosize | brier | 92 | 0.012184 | [-0.016753008369891072, 0.04112106597940832] |
| W2_DEF_NORM | L01 | crps | 92 | -0.000132 | [-0.002182881043229771, 0.0019182971675615042] |
| W2_NOAUTO_VOLUME | I03_nosize | brier | 92 | 0.003245 | [-0.023123454077230363, 0.029612987088502504] |
| W2_NOAUTO_VOLUME | L01 | crps | 92 | 0.000207 | [-0.0009254942438870747, 0.0013394645825983394] |


The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history. None of these new leads has a search-adjusted positive improvement interval over the relevant strongest prior control. See the validation report for the scope of the adjustment.

## All 57 native reference columns

| feature |
| --- |
| p_ret1 |
| p_ret3 |
| p_ret5 |
| p_ret10 |
| p_ret21 |
| p_ret63 |
| p_rv5 |
| p_rv21 |
| p_rv63 |
| p_trend |
| p_range |
| p_acceleration |
| p_vix |
| i_bank_nifty_rel5 |
| i_bank_nifty_rel21 |
| i_idx_Nifty_100_rel5 |
| i_idx_Nifty_100_rel21 |
| i_idx_Nifty_200_rel5 |
| i_idx_Nifty_200_rel21 |
| i_idx_Nifty_500_rel5 |
| i_idx_Nifty_500_rel21 |
| i_idx_Nifty_Commodities_rel5 |
| i_idx_Nifty_Commodities_rel21 |
| i_idx_Nifty_Consumption_rel5 |
| i_idx_Nifty_Consumption_rel21 |
| i_idx_NIFTY_HEALTHCARE_rel5 |
| i_idx_NIFTY_HEALTHCARE_rel21 |
| i_idx_Nifty_Infra_rel5 |
| i_idx_Nifty_Infra_rel21 |
| i_idx_Nifty_InfraLog_rel5 |
| i_idx_Nifty_InfraLog_rel21 |
| i_idx_Nifty_Next_50_rel5 |
| i_idx_Nifty_Next_50_rel21 |
| i_nifty_auto_rel5 |
| i_nifty_auto_rel21 |
| i_nifty_energy_rel5 |
| i_nifty_energy_rel21 |
| i_nifty_financial_rel5 |
| i_nifty_financial_rel21 |
| i_nifty_fmcg_rel5 |
| i_nifty_fmcg_rel21 |
| i_nifty_it_rel5 |
| i_nifty_it_rel21 |
| i_nifty_metal_rel5 |
| i_nifty_metal_rel21 |
| i_nifty_pharma_rel5 |
| i_nifty_pharma_rel21 |
| i_nifty_psu_bank_rel5 |
| i_nifty_psu_bank_rel21 |
| i_nifty_realty_rel5 |
| i_nifty_realty_rel21 |
| i_participation |
| i_dispersion |
| i_acceleration |
| i_concentration |
| i_leadership_persistence |
| i_defensive_cyclical |


Complete per-refit standardized weights are in `all-reference-feature-weights.csv`; weights vary by training cutoff and are not fixed percentage allocations of explanatory power.

## Which periods and variables drive the fitted result?

| horizon | fold | model | n | accuracy | brier | crps | mean_realized_return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 2026-07 | I03_nosize | 23 | 0.695652 | 0.226633 | 0.008045 | 0.004190 |
| 5 | 2026-08 | I03_nosize | 21 | 0.857143 | 0.147709 | 0.003686 | -0.006257 |
| 5 | 2026-09 | I03_nosize | 21 | 0.857143 | 0.147232 | 0.009369 | -0.013832 |
| 5 | 2026-10 | I03_nosize | 20 | 0.650000 | 0.182490 | 0.011052 | 0.012883 |
| 5 | 2026-11 | I03_nosize | 7 | 0.714286 | 0.241737 | 0.036864 | 0.043626 |
| 21 | 2026-07 | I03_nosize | 23 | 0.782609 | 0.184149 | 0.012640 | 0.010686 |
| 21 | 2026-08 | I03_nosize | 21 | 0.095238 | 0.399489 | 0.032384 | -0.038135 |
| 21 | 2026-09 | I03_nosize | 21 | 0.666667 | 0.228438 | 0.021440 | -0.031387 |
| 21 | 2026-10 | I03_nosize | 11 | 0.818182 | 0.183939 | 0.074561 | 0.094101 |

The largest individual path contributions are shown below; their overlapping endpoints make them dependent clusters. These dates identify sensitivity, not a causal news-event explanation. No independently sourced news-event attribution was audited. The complete top/bottom list is `largest-date-contributors.csv`; leave-month, rolling and regime details remain in their original machine-readable files.

| model | selection | origin | endpoint | regime | realized_return | gain_brier_vs_I03 |
| --- | --- | --- | --- | --- | --- | --- |
| W2_DEF_NORM | largest_improvement | 2026-10-05 | 2026-10-12 | high_vol | -0.008530 | 0.194803 |
| W2_DEF_NORM | largest_improvement | 2026-11-04 | 2026-11-11 | high_vol | 0.054024 | 0.180132 |
| W2_DEF_NORM | largest_improvement | 2026-10-16 | 2026-10-26 | high_vol | -0.016977 | 0.147798 |
| W2_DEF_NORM | largest_improvement | 2026-09-17 | 2026-09-24 | low_vol | -0.008917 | 0.142338 |
| W2_DEF_NORM | largest_improvement | 2026-11-06 | 2026-11-13 | high_vol | 0.004552 | 0.111527 |
| W2_DEF_NORM | largest_deterioration | 2026-07-16 | 2026-07-23 | high_vol | -0.008439 | -0.115212 |
| W2_DEF_NORM | largest_deterioration | 2026-07-06 | 2026-07-13 | high_vol | -0.008979 | -0.115212 |
| W2_DEF_NORM | largest_deterioration | 2026-07-15 | 2026-07-22 | high_vol | -0.003416 | -0.111687 |
| W2_DEF_NORM | largest_deterioration | 2026-07-21 | 2026-07-28 | high_vol | -0.008366 | -0.105938 |
| W2_DEF_NORM | largest_deterioration | 2026-08-19 | 2026-08-26 | low_vol | 0.005376 | -0.096204 |
| W2_NOAUTO_VOLUME | largest_improvement | 2026-11-04 | 2026-11-11 | high_vol | 0.054024 | 0.180132 |
| W2_NOAUTO_VOLUME | largest_improvement | 2026-09-28 | 2026-10-06 | low_vol | -0.000182 | 0.154909 |
| W2_NOAUTO_VOLUME | largest_improvement | 2026-09-17 | 2026-09-24 | low_vol | -0.008917 | 0.123441 |
| W2_NOAUTO_VOLUME | largest_improvement | 2026-10-16 | 2026-10-26 | high_vol | -0.016977 | 0.118307 |
| W2_NOAUTO_VOLUME | largest_improvement | 2026-11-02 | 2026-11-08 | high_vol | 0.065936 | 0.116317 |
| W2_NOAUTO_VOLUME | largest_deterioration | 2026-10-01 | 2026-10-09 | low_vol | 0.004393 | -0.246219 |
| W2_NOAUTO_VOLUME | largest_deterioration | 2026-09-11 | 2026-09-21 | low_vol | 0.000692 | -0.227377 |
| W2_NOAUTO_VOLUME | largest_deterioration | 2026-08-21 | 2026-08-28 | low_vol | -0.003148 | -0.135582 |
| W2_NOAUTO_VOLUME | largest_deterioration | 2026-09-16 | 2026-09-23 | low_vol | 0.009872 | -0.124546 |
| W2_NOAUTO_VOLUME | largest_deterioration | 2026-09-15 | 2026-09-22 | low_vol | 0.009101 | -0.094208 |

Nominal within-family conditional associations, with development half-sample signs exposed for stability assessment (not independently confirmed signals):

| horizon | feature | n | price_conditioned_rank_ic | first_half_ic | second_half_ic | p_shift | bh_q |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | i_idx_NIFTY_HEALTHCARE_rel21 | 300 | -0.475072 | -0.439833 | -0.548609 | 0.004975 | 0.040512 |
| 5 | i_idx_Nifty_Commodities_rel21 | 300 | -0.321829 | -0.387347 | -0.184095 | 0.004975 | 0.040512 |
| 5 | i_idx_Nifty_Commodities_rel5 | 300 | -0.266394 | -0.377107 | -0.156208 | 0.004975 | 0.040512 |
| 5 | i_idx_Nifty_InfraLog_rel21 | 130 | -0.374996 | -0.349956 | -0.406600 | 0.004975 | 0.040512 |
| 5 | i_nifty_energy_rel21 | 300 | -0.314007 | -0.219560 | -0.317911 | 0.004975 | 0.040512 |
| 5 | i_nifty_pharma_rel21 | 300 | -0.478917 | -0.442098 | -0.478825 | 0.004975 | 0.040512 |
| 21 | i_idx_NIFTY_HEALTHCARE_rel5 | 284 | -0.298818 | -0.126618 | -0.470162 | 0.004975 | 0.040512 |
| 21 | i_idx_Nifty_Commodities_rel21 | 284 | -0.403571 | -0.143819 | -0.342159 | 0.004975 | 0.040512 |
| 21 | i_idx_Nifty_InfraLog_rel21 | 114 | -0.529649 | -0.684081 | -0.328688 | 0.004975 | 0.040512 |
| 21 | i_idx_Nifty_Infra_rel21 | 284 | -0.345747 | -0.056281 | -0.527573 | 0.004975 | 0.040512 |
| 21 | i_idx_Nifty_Infra_rel5 | 284 | -0.240423 | -0.090897 | -0.269806 | 0.004975 | 0.040512 |
| 21 | i_nifty_pharma_rel21 | 284 | -0.314626 | -0.170521 | -0.317644 | 0.004975 | 0.040512 |
| 21 | i_nifty_pharma_rel5 | 284 | -0.283819 | -0.082426 | -0.402654 | 0.004975 | 0.040512 |
| 21 | p_vix | 284 | 0.450050 | 0.317493 | 0.646699 | 0.004975 | 0.040512 |
