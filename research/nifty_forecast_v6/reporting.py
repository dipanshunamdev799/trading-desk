"""Build the thirteen V6 reports directly from frozen numerical evidence."""
import shutil, platform, importlib.metadata
from .common import *
from .analyze import benchmark_frames
from .experiments import SPECS
from research.nifty_forecast_v5.analyze import summary
from research.nifty_forecast_v3.experiment import nonoverlap,effective_n

REPORTS=['WINNER_FORENSICS','INDIAN_INTERNALS_DEEP_DIVE','MARKET_STATE_EVOLUTION',
 'GLOBAL_INCREMENTAL_RESEARCH','MODEL_ARCHITECTURES','COHERENT_DISTRIBUTIONS',
 'MONTHLY_RESEARCH','CONDITIONAL_FORECASTING','VALIDATION_AND_LEAKAGE_AUDIT',
 'COMPLETE_MODEL_COMPARISON','SIGNAL_RANKING','FINAL_RESEARCH_DECISION','NEXT_EXPERIMENTS']

def table(rows,columns):
    if isinstance(rows,pd.DataFrame):rows=rows.to_dict('records')
    def cell(v):
        if v is None:return 'unavailable'
        if isinstance(v,(float,np.floating)):return f'{v:.6f}'
        if isinstance(v,(list,dict)):return json.dumps(v,default=str)
        return str(v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'+'\n'.join('| '+' | '.join(cell(r.get(c)) for c in columns)+' |' for r in rows)+'\n'

def run():
    stamp=now();metrics=read('metrics.json');by={(r['horizon'],r['model']):r for r in metrics};pred=pd.read_csv(OUT/'all-predictions.csv');bench=benchmark_frames();comparisons=read('strong-benchmark-comparisons.json');stability=read('stability.json');confidence=read('confidence-slices.json');inc=read('incremental-hypotheses.json')
    controls=[]
    for (h,name),g in bench.items():
        g=g.reset_index().sort_values('origin')
        if 'bucket_y' not in g:g['bucket_y']=np.digitize(g.realized_return,[-.05,-.02,-.005,.005,.02,.05])
        r={'horizon':h,'model':name,**summary(g),'disjoint_n':len(nonoverlap(g)),'ESS_return_acf':effective_n(g.realized_return,h)};controls.append(r);by[h,name]=r
    save('benchmark-metrics.json',controls);pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,(list,dict))} for r in controls]).to_csv(OUT/'benchmark-metrics.csv',index=False)
    cols=['model','n','accuracy','balanced_accuracy','brier','log_loss','crps','mae','rmse','coverage50','coverage80','width80']
    def scores(names,h=5):return table([by[h,n] for n in names if (h,n) in by],cols)
    def effects(names,h=5):return table([r for r in inc if r['horizon']==h and r['model'] in names and r['metric'] in ['brier','crps']],['model','parent','metric','n','gain'])
    def paired(names,h=5):
        return table([r for r in comparisons if r['horizon']==h and r['model'] in names and (r['baseline'],r['metric']) in [('I03_nosize','brier'),('L01','crps')]],['model','baseline','metric','n','mean_improvement','simultaneous95'])
    def stress(names,h=5):
        rows=[]
        for name in names:
            for score in ['brier','crps']:
                for test in ['leave_month_out','disjoint_phase','remove_best_overlapping_origins']:
                    z=[r['gain'] for r in stability if r['horizon']==h and r['model']==name and r['metric']==score and r['test']==test]
                    if z:rows.append({'model':name,'score':score,'test':test,'min_gain':min(z),'max_gain':max(z),'positive_cases':sum(v>0 for v in z),'cases':len(z)})
        return table(rows,['model','score','test','min_gain','max_gain','positive_cases','cases'])
    def write(name,body):
        title='NIFTY V6 — '+name.replace('_',' ').title()
        pre=f'# {title}\n\nGenerated {stamp}. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.\n\n'
        (OUT/f'V6_{name}.md').write_text(pre+body.strip()+'\n',encoding='utf-8')
    caution='The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.'
    units='Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.'
    native=pd.read_csv(OUT/'native-reference.csv',index_col=0)
    influence=pd.read_csv(OUT/'coefficient-stability.csv');exact=pd.read_csv(OUT/'exact-feature-effects.csv');featurecols=list(native)
    # Preserve all original standardized weights rather than offer one misleading fixed weight vector.
    weightfile=pd.read_csv(OUT/'feature-influence.csv').rename(columns={'prediction_change_median_replacement':'training_mean_replacement_proxy'})
    weightfile.to_csv(OUT/'all-reference-feature-weights.csv',index=False)
    exactrank=exact[exact.horizon==5].groupby('feature').mean(numeric_only=True).reset_index()
    effectcol=next((c for c in exactrank if 'probability' in c or 'p_change' in c),None)
    if effectcol:exactrank=exactrank.sort_values(effectcol,ascending=False)
    weightpreview=influence[influence.horizon==5].head(15)
    size=read('size-factorial-decomposition.json');details=read('forensic-details/h5-2026-07.json');fa=read('forensic-audit-summary.json')
    write('WINNER_FORENSICS',f'''
## Reproduction and actual model

Exactly reproduced 81 named model/fold vectors for I03_nosize, I00, I01_legacy, I02_newindices, L01, L02, V4 D02/D03 and M05. Probability, mean and median were compared at 1e-12 where available; M05's separate legacy classifier was checked as such. Two fresh July fits reproduced I03 and L01, and the independent V6 engine reproduced all 336 outer I03/L01 forecasts with maximum probability difference zero. See `reproduction.json` and `reference-engine-verification.json`.

I03 retains 57 native price/risk/index features. It standardizes with training-only imputation/centering/scaling, clips standardized inputs at ±5, and fits Ridge(alpha=100). Columns require at least 30 finite training values. Each monthly refit uses only labels whose endpoint is strictly before its cutoff. The latest 42 mature training-origin returns form an inner validation segment; the fitting segment is purged against the first validation origin. Conditional residual atoms from that inner fit receive 65% mass; the latest at-most-252 mature historical target returns receive 35%. Probability, mean and quantiles derive from that single distribution. These constants were inherited, not optimized on V6 evaluation scores.

{scores(['I03_nosize','I00','I01_legacy','I02_newindices','L01','L02','V4_D02_student_shrunk','V4_D03_residual_shrunk','V4_M05_lgbm'])}

I03's 76.086957% equals 70/92 correct: predicted up on 47 origins, actual up on 39; 32 true positives, 15 false positives, 38 true negatives and seven false negatives. Thus it is not an always-bullish classifier. Up recall is 32/39=82.05%; down recall 38/53=71.70%. I00 also gets 70 correct but predicts up only 37 times (27 TP,10 FP,43 TN,12 FN). L01 predicts up38 times and gets61/92 correct. Their identical or different accuracy can conceal materially different probability losses. `direction-confusion.json` contains exact counts.

## What removing size actually did

V5's I03 simultaneously removed eight possible size columns and recomputed five index aggregates. V6 separates these interventions. July I00 actually entered only six size columns: the two Smallcap500 series did not yet meet the 30-observation requirement. Its actual 63 entered columns must not be described as 65 fully observed inputs.

{table([r for r in size if r['horizon']==5],['variant','n','brier','crps','gain_vs_I00','probability_change_mean_abs','flips','correct_to_wrong','wrong_to_correct'])}

I00 Brier is .186098807; column removal alone .181369971; aggregate replacement alone .186804328; I03 both .182046521. The measured improvement is driven by column removal; recomputed aggregates slightly reduce that improvement. Removing only mid-cap inputs yields .179397932; removing only small-cap inputs worsens it to .192898145. Residualizing size against other inputs worsens it to .195861945. Therefore the evidence does not support saying all mid/small-cap information is useless. Smallcap500 histories start 2026-05-11, have 132 raw observations, and only127/111 usable five-/21-session relative-return observations across403 origins. A family median missingness statistic had obscured this individual short history.

{table(details['size_inputs'],['feature','observed_training','missing_fraction','entered_original_full_model','max_abs_correlation_to_retained','raw_std'])}

Raw scale differences are handled by standardization; redundancy, missingness, relationship drift and Ridge penalty geometry remain plausible mechanisms. This study identifies operational contributors, not a unique causal economic explanation. Native sectors and size indices are correlated; adding multiple standardized proxies effectively changes the penalty on shared directions. Removing, compressing or normalizing a correlated defensive block all improves weekly Brier to about .170, which strengthens the penalty-geometry hypothesis. It does not establish the absence of economic information in those sectors.

## Influential inputs versus useful inputs

Exact query-date train-median replacements show the largest mean absolute probability changes from pharma21 (5.7408 percentage points), auto21(4.8556), healthcare21(4.7911), InfraLog21(4.6009), NIFTY ret10(4.5452), and IT21(4.4576). These are conditional model perturbations, not causal effects. The exact full table is `exact-feature-effects.csv`. The earlier `feature-influence.csv` field named `prediction_change_median_replacement` is a legacy mislabeled training-MEAN standardized-zero proxy; the exact-median table supersedes that interpretation.

{table(weightpreview,list(weightpreview.columns))}

Pharma, healthcare and auto 21-session relative-strength coefficients are negative in all five weekly refits; IT21 is positive in all five. That suggests a mixture of conditional reversion/sector rotation and risk conditioning, rather than one pure momentum rule. Crucially, removing some of the most influential defensive/auto variables improves outer scores. Stable coefficients and influence do not establish incremental forecast usefulness. Development-only price-residual conditional Spearman tests cover114 selected feature/horizon cases with200 block shifts and within-family Benjamini–Hochberg adjustment: {fa['q_under_05']} have nominal q<.05, minimum q={fa['min_q']:.9f}. This selected native family and its surrounding model search are exposed; those14 are not independently confirmed features, causal discoveries, or directly comparable to V5's differently defined test family.

## Structural stress results

{scores(['F_NO_DEFENSIVE','W2_DEF_NORM','W2_DEF_PC','F_DROP_TOP3','F_NO_CYCLICAL','F_NO_PRICE_RISK','F_NO_IT','F_NO_AGGREGATES','F_ROLL126','F_ROLL189','F_ALPHA30','F_ALPHA300','F_INTERNAL_LAG1','F_INTERNAL_LAG2','F_ALL_LAG1','F_SYNTH_REV1BP'])}

{stress(['F_NO_DEFENSIVE','W2_DEF_NORM','W2_NOAUTO_VOLUME'])}

Month exclusions here are evaluation stress diagnostics, not retroactive month-selection trades. Regime omission is an actual training refit; the sideways-excluded July weekly and July/August monthly fits are non-estimable under the frozen minimum80 outer/60 inner rule. `group-permutation.csv` applies common within-month five-session circular family shifts; it is a dependence-preserving diagnostic with noncausal rearranged query inputs, never an eligible forecasting candidate. `rolling-performance.csv`, `regime-slices.json`, `stability.json` and the per-fold source details retain all results, including deterioration.

Actual observed V3→V5 overlapping domestic closes show zero revisions in the retained source vintages. Synthetic one-basis-point time-varying source perturbations are separately labeled sensitivity scenarios; zero observed revisions does not establish immutable vendor history. Additional one-/two-session feature lags test origin fragility; original source receipts from 2025 were not archived, so historical availability remains a reconstruction.

{paired(['F_NO_DEFENSIVE','W2_DEF_NORM','W2_NOAUTO_VOLUME'])}

{caution} None of these new leads has a search-adjusted positive improvement interval over the relevant strongest prior control. See the validation report for the scope of the adjustment.

## All 57 native reference columns

{table([{'feature':c} for c in featurecols],['feature'])}

Complete per-refit standardized weights are in `all-reference-feature-weights.csv`; weights vary by training cutoff and are not fixed percentage allocations of explanatory power.
''')
    write('INDIAN_INTERNALS_DEEP_DIVE',f'''
## Design and source identity

V6 prioritizes authentic native-index histories from the existing Upstox archives. It introduces no current-stock-membership proxy as an investable historical breadth series. The main source universe inherited from V5 includes25 domestic index/VIX histories,13 global series,150 current-stock proxy histories andfive ETFs; V6's selected native systems use the native indices and ETF histories only. Source identities and prior provenance remain in V5; V6 freezes403 aligned origins,57 native reference inputs,105 newly engineered native/evolution fields and64 retained global/cross-market reference fields. The105 fields were generated as a research library, then narrow hypothesis subsets were registered; they were not all simultaneously fed into every model.

The multi-scale library uses Bank Nifty, financial services, IT, auto, metal, pharma, FMCG, energy and Nifty500 at1/2/3/5/10/20 sessions. Relative changes are divided by trailing NIFTY21-session daily volatility times sqrt(horizon), with a .001 volatility floor. Additional variables include relative volatility, relative drawdown to21-session extrema, sector synchronization, average trailing21-session correlation, correlation change, defensive/cyclical and IT/financial rotation, bank deceleration, broad-index deterioration and concentration/dispersion changes. Indicators initialize from January2025 only. The early-April feature matrix boundary does not incorrectly restart their warmup; an initial implementation warmup issue was corrected before primary deep-model fits.

## Whole-system results

{scores(['I03_nosize','C_SMALL','H_MULTISCALE','H_WARNINGS','H_CORRELATION','H_ROTATION','H_DYNAMIC','H_DYNAMIC_CORE','Q_ETF_NOSIZE','Q_ETF_VOLUME','Q_ETF_PRICE'])}

## Immediate-parent increments

{effects(['H_MULTISCALE','H_WARNINGS','H_CORRELATION','H_ROTATION','Q_ETF_NOSIZE','Q_ETF_VOLUME','Q_ETF_PRICE'])}

The larger feature library does not automatically improve weekly proper scores. Selected multi-scale divergences worsen weekly Brier by .001839 and CRPS by .00010956 versus I03. The full eight-variable evolution addition also slightly worsens both losses. Compact dynamic models are comparisons between different feature sets: H_DYNAMIC_CORE uses four price/risk inputs plus eight evolving variables, whereas C_SMALL includes eight static inputs. Its improvement over C_SMALL is not a clean one-variable treatment effect and does not beat the57-input native reference.

## Sector redundancy and ETF decomposition

{scores(['F_NO_DEFENSIVE','W2_DEF_NORM','W2_DEF_PC','F_DROP_TOP3','Q_ETF_VOLUME','W2_NODEF_VOLUME','W2_NOAUTO_VOLUME','L01'])}

Defensive-group deletion, a train-only whitened first principal component, and standardized-group normalization all give similar weekly Brier (.169803/.170208/.169862). Group normalization divides the six standardized defensive fields by sqrt(6), changing the effective Ridge penalty; PCA is fitted separately within each inner/full training partition. This is evidence about representation/regularization, not evidence that defensive sectors are economically irrelevant. Auto21 removal was defined from July training coefficients, then crossed with five genuine ETF volume-ratio inputs in an explicitly later exposed-data batch.

L01 inherits full I00 native fields, including size, plus15 ETF inputs. Q_ETF_NOSIZE isolates I03 plus all15; Q_ETF_VOLUME uses onlyfive activity ratios; Q_ETF_PRICE uses theten return/variation variables. Volume ratios are reported ETF traded activity, not constituent breadth or native-index traded volume. This decomposition distinguishes activity from cross-asset exposure. The best distribution point score is W2_NOAUTO_VOLUME CRPS .009755832,75% accuracy,Brier .178802,80% coverage77.17%,mean80% width3.7657 percentage points. It improves L01 CRPS by .000206985 (about2.08%) on the same92 origins; the simultaneous95% gain interval includes zero. Adding volume improves CRPS relative to its auto-deletion parent but worsens that parent's Brier, so it is not a universal upgrade.

{effects(['W2_NODEF_VOLUME','W2_NOAUTO_VOLUME','W2_DEF_PC','W2_DEF_NORM'])}

## What we learned and retained

Native cross-index representation remains the strongest research family. Some broad, bank, cyclical, risk and IT relationships matter within the fitted model, while large sets of fresh divergences do not offer dependable increments. Keep the fixed I03/L01 references and the compact group-normalized/auto-volume candidates for future versioned research. Do not interpret constituent-proxy or ETF effects as genuine exchange-wide breadth without an appropriate historical universe. Detailed feature definitions, raw missing fractions and every tested column list remain in `feature-definitions.json`, `forensic-registry.json`, `model-registry.json` and the Python feature generator.

{caution}\n\n{units}
''')
    write('MARKET_STATE_EVOLUTION',f'''
## Registered hypotheses

The eight-variable core is bank short/long relative deceleration, Nifty500 short/long deterioration, defensive/cyclical rotation, five-session sector-correlation change, first difference in sector synchronization, correlation slope, second difference in IT/financial rotation, and cyclical weakness. The wider feature library also stores first differences, second differences and five-session slopes for six state measures; persistent trend, risk and defensive conditions; and a trailing63-session transition frequency of an observable synchronization state. This transition frequency is an empirical past-state hazard, not a fitted latent-state oracle or a validated future regime probability.

H_DYNAMIC adds the eight fields to57 native inputs. H_DYNAMIC_CORE uses four price/risk fields plus these eight instead of the larger static library. H_WARNINGS, H_CORRELATION and H_ROTATION test three-field early-warning blocks. H_MULTISCALE uses20 selected normalized bank/financial/IT/Nifty500 divergences. Parameters remain Ridge100 and the same coherent65/35 residual/historical law; refit dates and mature-label rules match I03.

## Weekly and monthly scores

{scores(['I03_nosize','C_SMALL','H_DYNAMIC','H_DYNAMIC_CORE','H_WARNINGS','H_CORRELATION','H_ROTATION','H_MULTISCALE'])}

{scores(['I03_nosize','C_SMALL','H_DYNAMIC','H_DYNAMIC_CORE','H_WARNINGS','H_CORRELATION','H_ROTATION','H_MULTISCALE','M_PERSIST'],21)}

{effects(['H_DYNAMIC','H_DYNAMIC_CORE','H_WARNINGS','H_CORRELATION','H_ROTATION'])}

The full dynamic addition worsens weekly Brier by .00119009 and CRPS by .00001099. Compact evolution beats its weak eight-static-input comparison in some metrics but remains weaker than the established native system. Because that compact pair also changes static variables, it is a system comparison, not an isolated effect of evolution. Monthly multiscale Brier .187396/CRPS .026989 is a retrospective lead, but with only four disjoint monthly outcomes and no convincing incremental state mechanism it cannot establish predictability.

## Causal reconstruction and failure diagnosis

All differences, slopes, correlations and persistence features use current/past prices only. A dedicated future-source perturbation check mutates later observations and verifies that earlier features do not change. No pre2025 observations initialize the indicators. Source availability is still inherited from archival reconstruction, with extra lag sensitivity tests; the check cannot prove that a historical vendor payload was actually received at the assumed time.

Weekly forecast-state aggregation is a separate monthly experiment. Those states are causally reconstructed historical prequential forecasts fitted without their own outcomes, not forecasts actually issued at those historical dates. No states are backfilled before the first available reconstructed forecast. Replaying them now preserves chronological fit logic but does not create a new untouched sample. One additional lag improves monthly point scores, and five-/21-session shifted-state diagnostics remain competitive, so exact-date evolution is not isolated as the driver.

{stress(['H_DYNAMIC','H_MULTISCALE','H_DYNAMIC_CORE'])}

Retain the hypotheses and their failed results. A larger dynamic library has not produced a robust weekly improvement over I03. Evolution may describe current regime drift better than future returns in this sample; low sample capacity, correlated inputs and training-window changes are alternative explanations requiring an independent future check.\n\n{caution}\n\n{units}
''')
    write('GLOBAL_INCREMENTAL_RESEARCH',f'''
## Narrow transmission hypotheses and availability

V6 does not rerun the indiscriminate global-plus-domestic block. It tests four intermediates first: US technology returns to Indian IT; Brent/USDINR/oil–FX to Indian energy; global mean/dispersion to bank-relative returns; and global volatility/dispersion to NIFTY return magnitude. Each intermediate has a domestic own-state Ridge100 control and an own-state-plus-sparse-global Ridge100 model. Intermediate forecasts are constructed chronologically; their incremental forecast correction enters G_MEDIATED. G_DIRECT uses seven sparse raw global fields. G_MATCHED uses the same compact domestic inputs and the same dates eligible for intermediate training. A weak-breadth/global-shock interaction is included in the mediated set.

The inherited `IXIX` feed is a provider US Tech100 proxy, not a verified Nasdaq Composite cash-index history. Accordingly, this is not a definitive Nasdaq→IT test. No FRED or US Treasury series is invented to fill previously failed acquisitions. Known foreign cash sessions retain exchange/IANA timezone/DST close plus two-hour availability; uncertain CFD/futures/FX daily conventions use a conservative two-UTC-day delay. We inherit the frozen provider/date audit rather than treating same-date foreign bars as already known in India. These conservative rules can sacrifice signal; original historical receipt timestamps are unavailable. An actual market-specific release-time study therefore remains constrained by source provenance, even where the transformation is causal.

## Intermediate out-of-sample reconstruction results

{table(read('intermediate-metrics.json'),['horizon','target','n','base_mae','global_mae','mae_improvement','base_rmse','global_rmse'])}

Weekly IT MAE improves by .000171611 (about.57% of its base MAE); energy improves .000274846 (about1.84%). Bank-relative performance worsens .000024064 and magnitude worsens .000253193. All four monthly intermediate MAEs worsen. These tiny and inconsistent sector increments do not establish economic causation or dependable transmission to NIFTY.

## Direct versus mediated NIFTY results

{scores(['G_MATCHED','G_DIRECT','G_MEDIATED','I03_nosize'])}

{scores(['G_MATCHED','G_DIRECT','G_MEDIATED','I03_nosize'],21)}

{effects(['G_DIRECT','G_MEDIATED'])}\n\n{effects(['G_DIRECT','G_MEDIATED'],21)}

The first monthly fold of all three G systems is non-estimable: the honest intermediate forecasts do not supply enough past inner-fit history for the frozen60-observation requirement. Their monthly scores use53 origins, not76, and strong controls are reindexed to those exact53 origins for comparisons. No retrospective fitted sector outcomes are backfilled to manufacture availability. Earlier weekly intermediate training and later monthly folds remain estimated as recorded.

{paired(['G_DIRECT','G_MEDIATED'])}

## Diagnosis and disposition

Domestic variables may already reflect much global information, but this remains a hypothesis rather than a proven explanation. The measured sector increments are small, source identities are imperfect, uncertain daily timestamps require conservative lags, and the two-year sample cannot support many regime-specific interactions. This batch provides no robust incremental NIFTY improvement from the narrowed global paths. Retain the IT/energy mediator hypotheses as exploratory and the negative magnitude/bank/monthly results as evidence against immediate expansion. A cleaner US cash-index timestamped history is more valuable than adding another broad global block. No global causal transmission is claimed.\n\n{caution}\n\n{units}
''')
    architecture=['I03_nosize','A_ELASTIC','A_HUBER','A_BAYES','A_FOREST','A_LGBM_QUANT','A_QUANTILE','A_GAM','A_STUDENT','R_VOL','R_TREND']
    write('MODEL_ARCHITECTURES',f'''
## Controlled alternatives, not an algorithm count contest

The main batch has25 estimator configurations (23 weekly,25 monthly) andfive coherent integration laws per horizon. The complete study has74 distinct system IDs and135 primary system/horizon rows after33 forensic variants, monthly risk, six monthly attribution systems andfour weekly follow-ups. Auxiliary intermediate targets, two diagnostic horizons, permutations, block nulls and sensitivity fits are separately counted and retained; those135 rows understate the wider research-search exposure.

Most architecture comparisons use the same57 native fields and monthly refit origins. Ridge alpha100 is the reference. Elastic Net uses alpha.001,l1ratio.5,max5000. Huber uses alpha10,epsilon1.35,max1000. BayesianRidge supplies normal predictive atoms. Random forest uses64 trees,depth3,minleaf30,maxfeatures.7,seed20261119 and actual conditional training-leaf atoms. LightGBM uses80 rounds,depth2,4leaves,minleaf40,rate.04,L2=10,single-thread deterministic seed20261119, with five direct quantiles. Linear quantile regression uses alpha.005 at .10/.25/.50/.75/.90. The compact additive spline model uses three knots,degree2 and Ridge100. Student laws use df5, a residual/historical scale blend and65/35 empirical shrinkage. Volatility and trend experts mix a global Ridge with a matching expert mean at50/50 when each training group has at least40 observations; gates depend only on training/current observable conditions.

## Weekly

{scores(architecture)}

## Monthly — only four disjoint outcome windows

{scores(architecture,21)}

Quantile crossings are sorted before a201-point bounded interpolation; this creates an ordered endpoint law but is not simultaneous noncrossing estimation, and endpoint truncation makes extreme-tail claims unsupported. Forest laws pool actual training returns from matching leaves with35% historical mass. Bayesian/Student laws have401 deterministic atoms before shrinkage. These numerical representations make scores reproducible but do not validate tail shape or conditional calibration.

Huber and elastic monthly classification point scores can look better while their distribution/interval results remain weak. The later M2_HUBER_WINDOW monthly attribution variant obtains76.32% accuracy and Brier.186174 yet CRPS.047917, substantially worse than the proper-score leads. Its July Huber fitting reached the1000-iteration cap; that warning is retained in the replay log and final numerical-warning audit, and it is not promoted. The original main-batch captured warning lists are preserved in `model-ledger.json`.

## Deliberate scope limits and inference

We tested shallow boosting, forest, additive, sparse, robust, Bayesian, quantile, Student and simple experts. XGBoost/CatBoost and neural sequence/temporal-convolution searches were not added: they are optional examples in the mission, not evidence-generating necessities, and 92 overlapping weekly/four monthly windows cannot justify a large hyperparameter search. Lag sensitivity and observed-state evolution supply controlled temporal alternatives. No winner is inferred from testing more algorithms. All failed/non-estimable fits remain in `experiment-registry.json` with their actual reasons. The new best weekly leads arise from representation/regularization and actual ETF activity, rather than the nonlinear architecture alternatives.

{paired(['A_FOREST','A_LGBM_QUANT','A_STUDENT','R_VOL'])}\n\n{caution}\n\n{units}
''')
    mixture=read('mixture-weight-ledger.json');weights=[{k:r.get(k) for k in ['horizon','fold','model','I03_weight','sign_beta','latest_training_endpoint']} for r in mixture]
    write('COHERENT_DISTRIBUTIONS',f'''
## Different leads describe different qualities

I03 is the prior probability lead (weekly Brier.182046521,accuracy76.09%); L01 has better distribution score (.009962817) but worse Brier(.197610292) and66.30% accuracy. L01's native family includes size plus15 ETF fields, whereas I03 excludes size and recomputes aggregates. Thus their difference is not attributable to one isolated factor. Mean error, expected absolute return, endpoint downside probabilities and bucket calibration are preserved per origin. Endpoint standard deviation is not forecast future realized path volatility. Endpoint probability below−2%/−5% is not probability of touching a drawdown barrier.

{scores(['I03_nosize','L01','J_EQUAL','J_BRIER','J_CRPS','J_COMBINED','J_SIGN','Q_ETF_VOLUME','W2_NOAUTO_VOLUME'])}

## Five integration experiments

J_EQUAL averages the two complete laws at50/50. J_BRIER/J_CRPS/J_COMBINED choose a weight only from the latest42 causally reconstructed parent forecasts whose outcomes ended strictly before the current cutoff. Weights are bounded.1–.9 and penalized toward.5 (Brier penalty.05,CRPS.002; joint CRPS/.015+Brier/.25+.25(w−.5)^2). A one-dimensional quadratic optimum is computed analytically; no evaluation-date weight grid is selected. Forty-two overlapping training outcomes do not represent42 independent weeks/months.

J_SIGN estimates a logisticC=.1 sign classifier on the native family and learns a beta bounded0–.75 from resolved prior forecast Brier with.05 shrinkage. It reallocates mass between actual positive/nonpositive return atoms; it does not graft a classifier probability onto an unrelated return forecast. Every final p(up), mean, median, quantile, seven return buckets and endpoint-tail probability comes from the same final weighted atoms. The other laws also clip simulated endpoint returns above the−100% bound; this numerical constraint is not tail validation.

The historical parent forecasts are causally reconstructed now, not actually timestamp-issued in2025. The phrase “honestly issued” in an initial registry means chronological out-of-training prediction only; `operational-amendments.json` and this report clarify that distinction. There is no independently sealed prequential experiment on these dates.

{table(weights,['horizon','fold','model','I03_weight','sign_beta','latest_training_endpoint'])}

## Calibration, asymmetry and uncertainty

The equal mixture obtains weekly Brier.188184 and CRPS.010013, and is a useful restraint benchmark: learned weights do not automatically improve on it, I03 probability quality or L01 CRPS. Tails remain lightly sampled; direct-quantile laws clamp the.10/.90 interpolation tails, and no conditional extreme-tail validation is claimed. `metrics.json` contains probability-bin observed versus predicted frequencies, expected calibration error, seven-bucket calibration, pinball losses, interval coverage/width and magnitude errors. These descriptive bins are not independent calibration tests, especially after subgroup/search exposure.

{scores(['I03_nosize','L01','J_EQUAL','J_BRIER','J_CRPS','J_COMBINED','J_SIGN','A_STUDENT'],21)}

Monthly comparisons have only four disjoint windows. Full coherence is necessary to interpret probabilities and intervals, but it does not guarantee predictive accuracy or calibration. The chosen exploratory weekly distribution candidate W2_NOAUTO_VOLUME improves point CRPS while its80% interval covers77.17%; the strongest directional candidate has different probability/interval behavior. Retain separate candidates and avoid claiming one integrated system solves every objective.

{paired(['J_EQUAL','J_BRIER','J_CRPS','J_COMBINED','J_SIGN','W2_NOAUTO_VOLUME'])}\n\n{caution}\n\n{units}
''')
    hd=read('intermediate-horizon-metrics.json');nulls=read('monthly-expanded-nulls-metrics.json');risk=pd.read_csv(OUT/'monthly-risk-predictions.csv')
    write('MONTHLY_RESEARCH',f'''
## Four disjoint evaluation windows

The76 origins span only approximately four nonoverlapping21-session outcomes. They have heavily overlapping return paths and substantial prior model-search exposure. There is no monthly confidence interval: the predeclared minimum8H origins is168, versus76 available. Small-sample uncertainty is not converted into precise claims by repeated cross-sectional observations or by an attractive accuracy percentage.

## Weekly-state aggregation and persistent-state alternatives

M_WEEKSTATE uses four price/risk fields plus16 reconstructed weekly forecast-state levels/slopes: p(up), mean, expected absolute return and endpoint standard deviation for I03/L01, each with a five-session slope. States are generated before their own outcomes, not compounded probabilities. Empty early history remains empty; dates before first valid reconstructed forecasts are excluded from training rather than filled with hindsight. M_PERSIST uses four slow state/persistence/transition fields instead. Later attribution controls share the same state-eligible training dates, distinguish levels from slopes, introduce one extra state lag, and try a robust native model on that same shorter window.

{scores(['I03_nosize','L01','V4_D02_student_shrunk','E00','M_WEEKSTATE','M2_STATE_LAG1','M2_WINDOW_SMALL','M2_WINDOW_NATIVE','M2_LEVELS','M2_SLOPES','M2_HUBER_WINDOW','M_PERSIST','A_STUDENT','M_RISK_PANEL'],21)}

M_WEEKSTATE achieves62/76=81.58% accuracy, Brier.178345 and CRPS.024823. Its nominal80% interval covers only65.79%, and50% interval38.16%. One extra lag lowers Brier to.175091 and CRPS.024530 but80% coverage falls to60.53%,50% to32.89%. These are not well-calibrated monthly confidence statements. The price-only and full-native date-matched controls are much worse, but levels alone and slopes alone are also worse: the interaction between representation, training window and shrinkage is not isolated by their aggregate accuracy.

## Falsification changed the decision

{table(nulls,['model','shift','n','accuracy','brier','crps','coverage80','width80'])}

All state-input rolls preserve broad temporal structure and use only training partitions; they are diagnostic corruptions rather than eligible forecasting systems. The21-session state roll produces Brier.160615, better than the actual state model. Thefive-session roll has CRPS.022269, also better. These retain genuine price controls and marginal regime information, so competitive results do not prove leakage. They do show that exact dated weekly-state information has not been established as the source of the gain. M_WEEKSTATE and M2_STATE_LAG1 remain INCONCLUSIVE / monthly block-null mechanism not passed.

The earlier native-target nulls are also cautionary: weekly3H/7H/11H rolls give bad Brier(.280229/.263407/.305512), while one monthly11H roll still gives Brier.216351 and CRPS.023929. A favorable monthly corruption is plausible with four outcome windows and regime drift; we do not claim all monthly nulls failed as desired. No null is selected as a real model.

## Broader risk panel without pseudo-replication

M_RISK_PANEL learns future21-session sector RMS/origin trailing-volatility log ratios using native sector histories, five risk/state inputs, and inverse count-per-date sample weights. The target ratio is clipped to[1/3,3], the predicted ratio to[.5,2]. Its NIFTY mean is half native conditional mean/half historical mean, with Studentdf5 endpoint atoms and35% historical shrinkage. Sector-date rows enrich estimation of a common risk relationship; they do not become independent monthly NIFTY outcomes. Each training row's21-session endpoint must mature before cutoff.

On76 NIFTY outcomes the separate risk auxiliary has mean annualized-volatility MAE {risk.aux_rv_mae.mean():.6f} and QLIKE {risk.aux_qlike.mean():.6f}; endpoint CRPS.026727/Brier.256160. Future realized volatility and endpoint-return standard deviation remain different quantities. This panel is a limited risk-estimation diagnostic, not evidence of monthly directional edge; no separate matched auxiliary risk benchmark was established, so its raw auxiliary losses do not demonstrate an improvement.

## Intermediate horizon diagnostics

{table(hd,['horizon','model','n','disjoint_n','accuracy','brier','crps','relative_crps_gain','normalized_brier_gain','coverage80'])}

Ten-/15-session comparisons use the same76 original monthly origins, their own correctly aligned targets, own matured training and own historical return baselines. Relative CRPS gain normalizes by that horizon's historical loss; raw CRPS is not directly a horizon-invariant predictability measure. The eight diagnostic model/horizon cells are exploratory and do not redefine the primary five-/21-session objectives. Some results change sharply rather than smoothly, but the limited common dates cannot distinguish a true predictability boundary from regime/target overlap.

## Decision

Keep the monthly state interaction as a falsified/inconclusive mechanism lead and retain the simpler Student/risk-panel distributions as research comparisons. Do not operationally promote the best monthly accuracy, infer narrow probabilities from these four windows, or claim the global mediators fixed monthly forecasting. All monthly fit failures, bad slopes/Huber variants, undercoverage and competitive corrupted controls are retained.

{units}
''')
    conditional=[]
    for r in confidence:
        if r['horizon']==5 and r['model'] in ['F_NO_DEFENSIVE','W2_DEF_NORM','W2_NOAUTO_VOLUME','Q_ETF_VOLUME'] and (r['rule'].startswith('either') or r['rule'] in ['agree_I03_L01','narrow80_vs_historical']):
            conditional.append({k:r[k] for k in ['model','rule','n','coverage','disjoint_n','I03_matched_brier','I03_matched_accuracy','L01_matched_crps']}|{k:r['metrics'][k] for k in ['accuracy','brier','crps','coverage80']})
    write('CONDITIONAL_FORECASTING',f'''
## Rules fixed for the analysis batch

Before computing this batch's slice scores, the analysis registry recorded directional confidence cutoffs.55/.65/.75 on both bullish and bearish sides, their either-side union, I03/L01 parent agreement, and a forecast80% interval narrower than.8 times the same-origin training historical interval. This is an exposed-history analysis plan, not a pre-history preregistration. All135 system/horizon rows were examined; these slices introduce further multiplicity beyond whole-system search.

“Agreement” refers to I03 and L01's signs; it does not guarantee that another candidate agrees with them. A narrow conditional interval measures model uncertainty, not independently validated reliability. Coverage below is the fraction of all eligible candidate origins selected by the rule; `coverage80` is interval coverage within those selected outcomes. They are different quantities.

{table(conditional,['model','rule','n','coverage','disjoint_n','accuracy','brier','crps','coverage80','I03_matched_accuracy','I03_matched_brier','L01_matched_crps'])}

Every displayed I03 accuracy/Brier and L01 CRPS is calculated on the candidate's exact selected dates. A selective accuracy can rise simply by selecting an easy market period for every method, so the matched control matters more than its unfiltered full-sample score. Small tail/high-conviction subsets have very few disjoint outcomes. No narrower confidence interval, optimized new threshold, annualized trading result or selective win-rate claim is inferred from them.

## Calibration and regime inspection

`confidence-slices.json` contains every nonempty bullish, bearish, either-side, agreement and narrow-interval slice, including unattractive ones and monthly slices. `regime-slices.json` separates the original predetermined volatility, trend and global-risk labels and reports sample size, disjoint count, coverage, proper scores and matched I03 Brier gain. Thresholds based on regime medians are derived from the corresponding training partition; no future regime assignment enters fits.

`metrics.json` includes fixed probability-bin counts, predicted versus observed rates and expected calibration error for every complete candidate. Conditional bins are descriptive, not independently calibrated confidence guarantees. High confidence with poor observed frequency can be worse than a modest probability even when classification accuracy looks attractive. There is no external calibration holdout because the entire available history has been used for research.

## Decision

Use the registered slices to specify future falsifiable questions, not to cherry-pick an attractive threshold. Retain coverage, matched control and interval calibration alongside accuracy. Weekly parent agreement and conservative group-regularized probabilities are leads for future collection; this sample does not establish a dependable selective forecasting policy. Monthly confidence claims remain especially weak with about four disjoint windows before subdivision. No signal is used to place orders or change the existing desk.

{caution}\n\n{units}
''')
    failed=[r for r in read('experiment-registry.json') if r.get('status')=='failed'];ledgerall=read('experiment-registry.json')
    archives={folder:read(folder+'/archive-checks.json') for folder in ['source-at-model-batch','source-at-forensic-batch']}
    numerical=[]
    import joblib
    for p in (OUT/'models').glob('*M2_HUBER_WINDOW.joblib'):
        a=joblib.load(p);est=a['model']['estimator'];numerical.append({'artifact':p.name,'outer_n_iter':int(est.n_iter_),'max_iter':int(est.max_iter),'iteration_cap_reached':bool(est.n_iter_>=est.max_iter)})
    save('numerical-warning-audit.json',{'records':numerical,'additional_observation':'A July inner/outer M2_HUBER_WINDOW fit emitted ConvergenceWarning in the original run; replay.log preserves warnings. Main model batch warnings were captured separately. Not promoted.'})
    registry=read('forensic-registry.json');replay=read('replay-verification.json') if (OUT/'replay-verification.json').exists() else {'passed':False,'status':'replay in progress; rerun reporting after verification'}
    checkdata=read('verification.json') if (OUT/'verification.json').exists() else {'passed':False,'status':'checks pending'}
    write('VALIDATION_AND_LEAKAGE_AUDIT',f'''
## Frozen scope and chronology

The run began on19November2026 and its reports were finalized at the actual timestamp above; run-directory date is a version identity, not a claim that later validation/report generation happened on19November. Inputs are frozen to the inherited17November historical cutoff. No20November observations or pre2025 warmup are added. There are403 aligned feature origins, with raw native history starting1January2025; the first aligned origin is2April2025. Fully resolved outer samples contain92 weekly/76 monthly origins. A separate V5 official18November snapshot is a prior artifact, not a V6 evaluation extension.

Training endpoints must be strictly earlier than each model cutoff. Monthly outer refits retain their original first-origin/anchor schedule, which often lies on the preceding month's final trading day. The last42 mature observations form the validation residual segment; earlier fitting labels ending on/after its first origin are purged. The endpoint<cutoff condition supplies a full target-maturity gap; no additional arbitrary future-data embargo is asserted. Every inner/full preprocessing object is fitted separately on its allowed training rows. Simple experts, defensive PCA, median thresholds and sparse intermediates follow the same causal partitions.

Historical source-time reconstruction inherits V5's domestic after-close/next-morning convention and foreign timezone/DST/conservative-delay rules. No actual2025 receipt log exists. Causal feature transforms and availability guard tests do not make archived data point-in-time immutable. Source identities, monthly feature missingness and publication uncertainty remain material leakage risks.

## Reproduction, source reconstruction and guards

81 named V5/V4 model-fold vectors reproduced, plus two independent V5 parent refits;336 V6 parent outer forecasts have zero probability discrepancy. All964 cached parent laws retain full atoms/weights and are chronologically reconstructed, not historically issued. Matrix hashes, model hashes, feature-schema allowlists, future-availability/oracle-alias guards, matured-target guards, endpoint-alignment checks, weighted CRPS brute-force checks, ordered quantile checks and future-source perturbation invariance are exercised by `verify.py`. A schema allowlist does not prove arbitrary values within an allowed column are legitimate; source reconstruction and provenance supply complementary checks.

Full candidate replay status at report generation: {replay.get('passed')}. The replay refits fitted candidate batches in a fresh V6 directory against frozen parent/mediator input artifacts, then compares per-origin probabilities, means, CRPS and other recorded fields at1e-10. It does not reacquire the provider histories or independently regenerate every frozen parent/mediator input. Their separate refits/provenance checks are explicitly documented. `replay-verification.json` gives exact row counts/differences. Numerical verification status at report generation: {checkdata.get('passed')}; final invocation requires both replay and all13 reports.

The precise original source versions are retained in `source-at-forensic-batch/` ({len(archives['source-at-forensic-batch'])} matching files) and `source-at-model-batch/` ({len(archives['source-at-model-batch'])} matching files), with archive hashes matching the original registries. Later guards and defensive PC/normalization branches do not silently replace that historical code record. `operational-amendments.json` records their chronology. No frozen past registry is rewritten to imply an earlier preregistration.

## Search accounting and uncertainty

There are74 distinct candidate system IDs,135 primary system/horizon cells (65weekly/70monthly),11164 primary prediction rows and {len(ledgerall)} primary/diagnostic fitted-batch ledger entries. Auxiliary mediation has200 fit records; parent reconstruction50; mixture-weight learning45. These counts exclude many prior V1–V5 searches and some inner/control fits, so they are lower bounds on total scientific search exposure. Initial33 forensic configurations were followed by a registered model batch and explicitly later outcome-informed monthly/weekly follow-ups. “Registered before fitting a batch” does not mean unseen history or independent confirmation.

Every primary candidate is compared on matched dates against eight controls: I03,I00,L01,V4D02,V4D03,V4M05,neutral and historical. Three loss contrasts (Brier,CRPS,return MAE) give3240 comparisons:1560weekly and1680monthly. Weekly uncertainty uses shared chronological10-origin moving blocks,2000 replicates and a max-standardized simultaneous critical value across all1560 candidate/score/control contrasts. Structural missing cohorts are retained on the common calendar. These are approximate dependence/search-aware exposed-history intervals, not a correction for the entire adaptive V1–V6 research program or future distribution shifts. The CI family itself does not include every confidence slice, permutation or feature test. No claim of global familywise protection is made.

Monthly intervals are withheld:76<8×21=168. The descriptive return-ACF effective-N estimates are {by[5,'I03_nosize']['ESS_return_acf']:.3f} weekly and {by[21,'I03_nosize']['ESS_return_acf']:.3f} monthly for these exact cohorts; they are estimators with their own uncertainty, not literal counts of independent events. Disjoint-window counts are19/four. Reported phase/leave-month/origin-removal checks show sensitivity but are not additional independent replications.

## Negative controls, revisions and preserved failures

Weekly target rolls are materially worse. Several monthly block controls remain attractive; the weekly-state mechanism therefore remains unpassed. Grouped query-month permutations are diagnostic and noncausal by construction; they cannot be forecast candidates. Actual overlapping domestic archived closes show zero changes between inspected source vintages; synthetic1bp perturbation is labeled separately. One-/two-session lag tests diagnose source/origin fragility; no historical receipt certainty is invented.

{table(failed,['horizon','fold','model','status','reason'])}

Three regime-excluded andthree global-monthly fits are non-estimable; no min-sample threshold is relaxed to fill them. The July M2_HUBER_WINDOW convergence warning is documented in `numerical-warning-audit.json`; the candidate is not promoted. All failed/weak experiments, including slope-only monthly, nonlinear weekly, size residualization and competitive nulls, remain reviewable.

## Preservation and forward handling

`prior-preservation.json` freezes6040 V1–V5 files, plus the exact prior report/source inventory; `verify.py` rehashes every protected file. The V4 prospective ledger is untouched and remains separate. No broker order, deployment, UI change or automation was created. The official19November index/cash/FO source probe failed for allthree requests at16:19IST on19November (`forward-source-probe.json`); we therefore did not backdate a forward snapshot or substitute stale source inputs for a current prediction. No V6 forward snapshot was issued. Acquiring a complete source set and freezing a new actual timestamp are prerequisites to any future research-only snapshot.

{caution}
''')
    # Extended machine-readable leaderboard includes all requested contextual fields.
    extended=[]
    for r in read('leaderboards.json'):
        h=r['horizon'];name=r['model'];ss=[s for s in stability if s['horizon']==h and s['model']==name and s['metric']=='brier' and s['test']=='leave_month_out'];r=dict(r)
        spec=SPECS.get(name,registry['configurations'].get(name,{}));r['feature_family']=spec.get('features','registered forensic/follow-up/native/ETF/risk/state law');r['architecture']=spec.get('kind',spec.get('parameters',{}).get('kind','Ridge/coherent empirical law; see frozen registry'))
        r['leave_month_min_brier_gain_vs_I03']=min(s['gain'] for s in ss) if ss else None;r['leave_month_max_brier_gain_vs_I03']=max(s['gain'] for s in ss) if ss else None
        for baseline,metric in [('I03_nosize','brier'),('L01','crps'),('V4_D02_student_shrunk','crps'),('V4_D03_residual_shrunk','brier'),('V4_M05_lgbm','brier')]:
            c=next(s for s in comparisons if s['horizon']==h and s['model']==name and s['baseline']==baseline and s['metric']==metric)
            r[f'gain_{metric}_vs_{baseline}']=c['mean_improvement'];r[f'CI_{metric}_vs_{baseline}']=json.dumps(c['simultaneous95'])
        r['leakage_risk']='Historical source receipt/revision uncertainty; research exposure; no observed target-alignment violation';r['uncertainty']='Search-wide approximate2H bootstrap' if h==5 else 'NOT ESTIMABLE: four disjoint windows'
        extended.append(r)
    pd.DataFrame(extended).to_csv(OUT/'complete-system-comparison.csv',index=False)
    write('COMPLETE_MODEL_COMPARISON',f'''
## Reading the comparison

{units} {caution}

There are74 distinct system identifiers and135 primary model/horizon rows, comprising65weekly/70monthly. Separate direction and distribution leaderboards sort Brier and CRPS; neither uses a custom composite rank. They include unpromising configurations. Six non-estimable model/fold rows remain in the experiment registry rather than being scored as predictions. Monthly G systems have53 origins, and the regime-excluded forensic system may have fewer origins; compare each with the supplied same-date controls, not raw full-cohort ranks.

`complete-system-comparison.csv` gives every system's horizon, family, architecture, n, disjoint count, return-ACF ESS, Brier, log loss, accuracy, balanced accuracy, CRPS, return MAE/RMSE,50%/80% interval coverage,width, leave-month gain range, strongest-V4/V5 gains and search-aware uncertainty/status. `strong-benchmark-comparisons.json` supplies all3240 exact-date contrasts across eight controls/three losses. `metrics.json` adds calibration/bucket/tail/magnitude details; `stability.json`, `regime-slices.json` and `rolling-performance.csv` retain granular time behavior. Architecture/feature specifics and per-fold warnings are in source and registries rather than compressed into a false single score.

## Frozen reference systems

{table(controls,['horizon','model','n','disjoint_n','ESS_return_acf','accuracy','brier','log_loss','crps','mae','rmse','coverage50','coverage80','width80'])}

M05 is the legacy separate classifier/quantile system: its classification scores are valid legacy controls, but its probability and return quantiles are not asserted to arise from a single coherent endpoint law. This limitation is retained rather than used as a reason to omit the strong baseline.

## Weekly systems, sorted by Brier

{table(sorted([r for r in extended if r['horizon']==5],key=lambda r:r['brier']),['model','n','disjoint','ESS','accuracy','balanced_accuracy','brier','log_loss','crps','mae','rmse','coverage50','coverage80','width80','status'])}

## Monthly systems, sorted by CRPS — only four disjoint windows

{table(sorted([r for r in extended if r['horizon']==21],key=lambda r:r['crps']),['model','n','disjoint','ESS','accuracy','balanced_accuracy','brier','log_loss','crps','mae','rmse','coverage50','coverage80','width80','status'])}

EXPLORATORY LEAD means a point improvement on either prior I03 Brier or L01 CRPS over its matched dates; it does not mean independent statistical confirmation, reliable deployment or joint dominance. Monthly state models carry an explicit unpassed mechanism status. Leave-regime/month stress variants are research diagnostics and are not automatically practical forecasting policies. Read the final decision report for the deliberately smaller retained candidate set.
''')
    write('SIGNAL_RANKING',f'''
## Rank incremental information separately from fitted systems

This is an evidence ordering, not a causal feature ranking or a custom numerical score. Complete-system ranks by Brier/CRPS are in their own tables. Incremental gains below are measured against each immediate parent on the same dates; some effects trade off probability quality and distribution quality. The selected native family itself was discovered through V1–V5 exposed-history work.

1. **Correlated defensive-group representation/penalty** is the strongest mechanism lead. Deletion, train-only whitened1PC and division of standardized group fields bysqrt(6) all yield weekly Brier near.170 versus.182047. Similar outcomes under three representations support redundancy/penalty geometry, without proving economic irrelevance or a future effect. The group-normalized candidate keeps all57 inputs and has a smaller estimated change-uncertainty than pure deletion.
2. **Auto relative-strength removal plus actual ETF activity** is the best distribution point-score lead. W2_NOAUTO_VOLUME reachesCRPS.009755832 versusL01.009962817 while maintainingBrier.178802 and75% accuracy. It is a later adaptive cross, not an independently preregistered discovery. ETF volume improves its auto-deletion parent's CRPS but worsens its Brier.
3. **Size-column exclusion** explains most of I03 versusI00's measured Brier improvement. Aggregate recomputation alone does not. Mid-cap exclusion helps more than small-cap exclusion, which worsens scores; Smallcap500's short initial history and changing inclusion are material. Do not infer a universal anti-smallcap rule.
4. **Existing cyclical/risk/IT relationships** remain useful conditional pieces of the native reference in family-deletion diagnostics. Their influence and stable coefficients are descriptive; they are not standalone causally identified signals.
5. **Multi-scale/evolution/correlation/early-warning additions** are weak or inconsistent increments over57 native fields. Compact versions can beat weak small controls without beating the established reference.
6. **Global→Indian-sector corrections** offer tiny weekly IT/energy MAE gains, weak bank/magnitude and negative monthly results, with no robust downstream NIFTY increment. Feed identity/timestamps constrain interpretation.
7. **Monthly weekly-state interaction** has striking point accuracy but competitive corrupted-state controls, undercoverage and only four outcome windows. It remains an unpassed mechanism lead, not the strongest proven monthly information source.

## Numerical parent effects

{effects(['W2_DEF_PC','W2_DEF_NORM','Q_ETF_VOLUME','W2_NOAUTO_VOLUME','W2_NODEF_VOLUME','H_MULTISCALE','H_DYNAMIC','H_WARNINGS','H_CORRELATION','H_ROTATION','G_DIRECT','G_MEDIATED'])}

## Conditional information versus influence

All feature weights are saved per cutoff in `all-reference-feature-weights.csv`. Exact train-median effects are in `exact-feature-effects.csv`, coefficient signs in `coefficient-stability.csv` and development-only residualized tests in `conditional-feature-information.csv`. Fourteen of114 conditional tests meet within-family nominalq<.05 (min.040512), but the selected family, correlated targets and wider search exposure prevent an independent discovery claim. A large coefficient/median-replacement effect can reflect unstable/duplicated representation; several influential variables become harmful in the combined fitted model.

Any future signal ranking should be judged by a frozen parent increment, proper-score tradeoff, source availability, stability and eventual truly new observations. This study does not assign causal explanatory percentages that sum to100.\n\n{caution}\n\n{units}
''')
    b_gain=by[5,'I03_nosize']['brier']-by[5,'F_NO_DEFENSIVE']['brier'];c_gain=by[5,'L01']['crps']-by[5,'W2_NOAUTO_VOLUME']['crps']
    write('FINAL_RESEARCH_DECISION',f'''
## Decision

We found improved **exploratory weekly candidates** and a clearer mechanism hypothesis, but no independently validated NIFTY forecasting edge. The strongest probability point score is F_NO_DEFENSIVE Brier.169802948, down{b_gain:.9f} (6.73%) fromI03.182046521, with72/92=78.26% accuracy. Group-normalized W2_DEF_NORM is nearly equal at.169862492 and78.26% accuracy while retaining the57 native inputs. The strongest distribution point score is W2_NOAUTO_VOLUME CRPS.009755832, down{c_gain:.9f} (2.08%) fromL01.009962817; Brier.178801754,accuracy69/92=75%,80% intervalcoverage71/92=77.17%.

{scores(['I03_nosize','L01','F_NO_DEFENSIVE','W2_DEF_NORM','W2_DEF_PC','W2_NOAUTO_VOLUME','W2_NODEF_VOLUME'])}

## Retained candidate set and reason

Retain fixed I03 and L01 as untouched references. Retain W2_DEF_NORM as the representation/penalty hypothesis candidate, F_NO_DEFENSIVE as its deletion comparator, and W2_NOAUTO_VOLUME as the distribution/activity candidate. Do not merge these into a claimed universal winner. W2_DEF_NORM divides six standardized defensive inputs bysqrt(6) before fixedRidge100; W2_NOAUTO_VOLUME removes auto21 relative strength and addsfive genuine ETF activity ratios. Every candidate outputs a coherent endpoint distribution.

The mechanism finding is narrower than “sector X predicts NIFTY.” Correlated native inputs alter effective Ridge regularization. Removing columns, changing group weight or compressing them can improve retrospective losses without adding information. Size removal's gain arises mainly from dropping columns, not recomputing breadth aggregates. Smallcap500's late-start missingness matters, and excluding only small caps hurts. Native sector rotation, conditional reversion and price risk appear in the coefficients, but their causal transmission is not identified.

## Uncertainty prevents an edge claim

{paired(['F_NO_DEFENSIVE','W2_DEF_NORM','W2_NOAUTO_VOLUME'])}

All relevant weekly search-adjusted improvement ranges include zero. These approximate simultaneous intervals cover the within-V6 family, not the whole adaptiveV1–V6 history. The92 weekly origins overlap into19 disjoint windows. Native/ETF data is reconstructed from archived provider histories rather than authenticated historical receipt logs. A full replay can establish numerical reproducibility; it cannot make the exposed history independent.

## Monthly decision — four disjoint windows

M_WEEKSTATE's81.58% accuracy/Brier.178345/CRPS.024823 and one-extra-lag Brier.175091/CRPS.024530 look strong, but80% intervalcoverage is65.79%/60.53%. A21-session shuffled-state diagnostic obtainsbetterBrier.160615, and afive-session shiftbetterCRPS.022269. Exact dated state information is therefore not established as the driver. Keep those leads INCONCLUSIVE; no monthly winner is forced, no narrow interval is manufactured, and no prospective operational model is selected from four windows. RegularizedStudent/risk-panel alternatives remain comparisons, not validated solutions.

Global mediation, larger evolving feature libraries, nonlinear architectures and learned mixtures did not deliver a dependable improvement over the strongest matched prior controls. Preserve their negative results. Ten-/15-session experiments are additional diagnostics, not new primary horizons selected after seeing attractive outcomes.

## Delivery and next action boundary

All13 requested reports, frozen feature/configuration files, per-origin outputs, fitted model artifacts, exact source archives, failed-fit reasons, null results, matched comparisons and reproducible scripts are included. V1–V5 and the V4 prospective ledger are unchanged. No live trade, deployment or automation was performed. No new V6 forward snapshot was issued: allthree official19November source probes failed at acquisition, and this historical run does not silently substitute stale/current data. A future research-only snapshot must acquire a complete, timestamped source set and record its own version/hash/issuance time.

The useful discovery is a smaller, testable candidate set and an evidence-backed representation hypothesis. The unresolved question is whether those improvements survive genuinely new weekly observations with stable source availability. That question has not been answered by this exposed-history research.\n\n{units}
''')
    write('NEXT_EXPERIMENTS',f'''
## Freeze before collecting genuinely new observations

Freeze I03,L01,W2_DEF_NORM,F_NO_DEFENSIVE andW2_NOAUTO_VOLUME with complete code/input/configuration hashes, the same horizon definitions and the same endpoint-maturity/refit rules. Use a separate append-only V6 research ledger with actual issuance/receipt timestamps; never edit V4's ledger or backdate a forecast. None is issued by this run. The official19November source acquisition failures are retained rather than filled with stale data.

Collect disjoint weekly outcomes while preserving daily forecast rows; report Brier,logloss,CRPS,calibration,interval coverage/width,matched controls and source staleness on every origin. Specify the target sample size and dependence-aware stopping/analysis rule before looking at those new results. A fixed untouched future sample can test an edge; another exposure of2025–2026 cannot.

## Highest-value mechanism experiments

First test a narrowly registered defensive-group penalty continuum using training-only nested selection against fixedRidge100. Compare deletion, whitening and a group penalty under identical dates and shrinkage. Explain whether improvements come from predictive information, duplicated representation or effective regularization; do not retrofit the best penalty to all exposed outcomes and call it confirmation.

Second isolate the auto/activity cross in a small2×2 design: auto21 present/absent × ETF volume present/absent, with matched-cohort Brier/CRPS and an announced primary score. The current study contains allfour point comparisons, but its final combination is adaptive. Audit ETF splits, activity shocks, missingness and vintage reliability before interpreting traded activity as economic information.

Third isolate size history. Compare midcap-only removal, smallcap-only removal and all-size removal on a fixed period where all selected histories genuinely existed and met minimum observations. Keep training sample changes distinct from input changes. Do not substitute today's constituent membership to backfill breadth.

## Monthly mechanism remains unresolved

Require the weekly-state model to beat fixed matched controls across a registered distribution of state-block shifts, block lengths, training windows and prospective new months, with calibrated interval coverage. The existingfewfixed shifts are diagnostic, not a full randomization p-value. Investigate why the level/slope combination helps while each alone fails and why one extra lag/shuffled states remain competitive. Keep every corruption separate from eligible forecasts. Fourdisjoint outcomes cannot support a confident monthly selection; no amount of sector-date pseudo-replication increases that count.

Keep10-/15-session targets diagnostic. If a new primary horizon is desired, choose it for an external use case and freeze it before independent evaluation, not because one retrospective normalized score looks favorable.

## Source quality before global model expansion

Acquire authenticated Nasdaq cash-index/US-sector histories with exact session definitions and reliable release times rather than calling a Tech100 proxy Nasdaq. Reconstruct Indian forecast availability through DST and holidays, verify commodity/FX bar conventions, and preserve actual source payload receipts. Then repeat only the sparseIT/energy intermediate hypotheses on a fixed registered design. Do not revive a giant global block because a sector MAE moved by a few basis points in exposed history.

## Architecture and distribution work

Use a small nested comparison of the established native representations, highly regularized Student/empirical shrinkage and uncertainty calibration. Investigate tail treatment in quantile laws, which currently clamp interpolation outside.10/.90; acquire enough independent tail observations before asserting barrier or extreme-tail probabilities. Preserve future realized-volatility risk as a separate target. Resolve or exclude Huber convergence failures under a preannounced numerical policy. Neural sequence models and additional algorithm grids should wait for more independent temporal information.

## Evidence that would change the decision

A candidate must show a stable proper-score improvement over both fixedI03/L01 and the strongV4controls on truly new matched origins, acceptable calibration/coverage, a source audit without hidden future availability, and an uncertainty analysis accounting for dependence and the announced comparisons. Improvement on a weak or differently dated baseline is insufficient. A negative prospective result should retire or simplify the hypothesis, not trigger an unrecorded reoptimization.\n\n{caution}
''')
    # Date attribution and conditional relationships remain descriptive, not event causation.
    monthrows=[];extremes=[]
    for h in [5,21]:
        g=bench[h,'I03_nosize'].reset_index().sort_values('origin')
        for fold,z in g.groupby('fold'):
            monthrows.append({'horizon':h,'fold':fold,'model':'I03_nosize','n':len(z),'accuracy':float(((z.p>=.5)==z.outcome).mean()),'brier':float(z.brier.mean()),'crps':float(z.crps.mean()),'mean_realized_return':float(z.realized_return.mean())})
        for name in ['F_NO_DEFENSIVE','W2_DEF_NORM','W2_NOAUTO_VOLUME']:
            z=pred[(pred.horizon==h)&(pred.model==name)].copy()
            if z.empty:continue
            z['gain_brier_vs_I03']=bench[h,'I03_nosize'].brier.reindex(z.origin).to_numpy()-z.brier.to_numpy()
            for direction,zz in [('largest_improvement',z.nlargest(5,'gain_brier_vs_I03')),('largest_deterioration',z.nsmallest(5,'gain_brier_vs_I03'))]:
                for r in zz.to_dict('records'):extremes.append({k:r[k] for k in ['horizon','model','origin','endpoint','regime','realized_return','gain_brier_vs_I03']}|{'selection':direction})
    pd.DataFrame(monthrows).to_csv(OUT/'reference-month-performance.csv',index=False);pd.DataFrame(extremes).to_csv(OUT/'largest-date-contributors.csv',index=False)
    cond=pd.read_csv(OUT/'conditional-feature-information.csv');nominal=cond[cond.bh_q<.05].sort_values(['horizon','bh_q','feature'])
    with (OUT/'V6_WINNER_FORENSICS.md').open('a',encoding='utf-8') as f:
        f.write('\n## Which periods and variables drive the fitted result?\n\n'+table(monthrows,['horizon','fold','model','n','accuracy','brier','crps','mean_realized_return']))
        f.write('\nThe largest individual path contributions are shown below; their overlapping endpoints make them dependent clusters. These dates identify sensitivity, not a causal news-event explanation. No independently sourced news-event attribution was audited. The complete top/bottom list is `largest-date-contributors.csv`; leave-month, rolling and regime details remain in their original machine-readable files.\n\n'+table([r for r in extremes if r['horizon']==5 and r['model'] in ['W2_DEF_NORM','W2_NOAUTO_VOLUME']],['model','selection','origin','endpoint','regime','realized_return','gain_brier_vs_I03']))
        f.write('\nNominal within-family conditional associations, with development half-sample signs exposed for stability assessment (not independently confirmed signals):\n\n'+table(nominal,['horizon','feature','n','price_conditioned_rank_ic','first_half_ic','second_half_ic','p_shift','bh_q']))
    recovered='\n## Complete recovered endpoint outputs\n\n`distribution-audit.json` records recovery of all 11,164 primary endpoint laws from frozen models/caches, with zero discrepancy in probability, mean, median, Brier and CRPS. `full-endpoint-predictions.csv` contains all seven quantiles, seven bucket probabilities, expected absolute return, endpoint standard deviation and endpoint downside probabilities. `retained-distributions.jsonl` preserves all276 weekly laws for the three retained candidate systems; these are reconstructed historical laws, not forward issuances. `retained-candidate-feature-weights.csv` contains845 actual per-refit coefficients, training imputation/centering/scaling values and defensive-group scaling factors. Return-regression coefficients are not additive probability weights or causal explanatory shares. Endpoint-path risks remain unavailable.\n'
    for name in ['COHERENT_DISTRIBUTIONS','COMPLETE_MODEL_COMPARISON','VALIDATION_AND_LEAKAGE_AUDIT']:
        with (OUT/f'V6_{name}.md').open('a',encoding='utf-8') as f:f.write(recovered)
    for name,figure in [('FINAL_RESEARCH_DECISION','weekly-results.png'),('MONTHLY_RESEARCH','monthly-falsification.png')]:
        with (OUT/f'V6_{name}.md').open('a',encoding='utf-8') as f:f.write('\n[Standalone research figure]('+figure+')\n')
    save('operational-amendments.json',{'recorded_at':stamp,'notes':[
        'Initial deep-feature warmup reindexed too early; corrected to Jan2025 raw history BEFORE primary deep-model fits.',
        'Feature schema/availability guards and expert branches were added after initial forensic fits; exact original forensic/model source hashes archived; original Ridge numerics unchanged and full replay checked.',
        'Defensive PC/normalization branches were added for the explicitly later follow-up batch; no old registry rewritten.',
        'Legacy influence field prediction_change_median_replacement is a training-mean proxy; exact train-median query effects saved separately.',
        'Honest/issued prequential wording means causally reconstructed out-of-training history, NOT actual historical timestamp issuance.',
        'Monthly/weekly attribution follow-ups were motivated by exposed results, not preregistered before seeing history.',
        'Reports finalized at actual timestamp, not backdated to run-directory date; no V6 forward snapshot issued.']})
    (SRC/'README.md').write_text('''# NIFTY V6 research

Research-only native-index study; no trading/deployment. Run outputs are versioned under `artifacts/nifty_forecast_v6/2026-11-19/run-001`. Reports were finalized at their actual timestamp. All history is exposed; scope is2025–2026, frozen history through17November2026.

The authoritative mission is in `MISSION.md`. Existing V1–V5 data/code/ledger files are read-only inputs. Output overrides must resolve inside `artifacts/nifty_forecast_v6` and must use a fresh directory. Existing fitted-batch registries refuse overwrite.

Use the repository `.venv` (Python3.15 plus existing pinned research packages). `environment.json` records actual versions; no dependency changes were made by V6.

To verify the delivered run from the repository root:

```powershell
.venv\\Scripts\\python.exe -m research.nifty_forecast_v6.verify --require-replay --require-reports
```

To replay all fitted candidate batches against frozen matrices/parent laws/mediator features into a NEW directory:

```powershell
.venv\\Scripts\\python.exe -m research.nifty_forecast_v6.replay --out artifacts/nifty_forecast_v6/2026-11-19/replay-your-id
```

The full original construction order is `common`, `reproduce`, `features`, `forensics`, `prequential`, `mediation`, `experiments`, `monthly`, `forensic_audit`, `monthly_followup`, `followups`, `analyze`, `distribution_audit`, `reporting`, `verify`. For an independent full construction, set `NIFTY_V6_OUT` to a fresh V6 folder first; retain the raw V3/V5 upstream inputs. `common` freezes prior hashes and `features` creates matrices. `forensic_audit` must run after forensics and prequential. Original batch-source archives preserve exact historical source hashes; later guards/PC additions are recorded amendments. The candidate replay deliberately uses frozen independently audited parent/mediator artifacts, so it is not a new provider-data acquisition test.

`reporting` derives the13 reports, expanded tables and root index from recorded results. `verify` checks preservation, source hashes, labels, causal transforms, fitted artifacts, mixtures, scores, retained failures and report delivery. It does not certify economic causation, future calibration or an independent edge. No API credentials, broker order code, automatic forward watcher or deployment is part of this module.
''',encoding='utf-8')
    index='# NIFTY V6 research\n\nCompleted research, not a validated trading edge. Historical universe:2025–2026 only; frozen input cutoff17November2026. Reports generated '+stamp+'.\n\n'
    index+='Best weekly probability point result: Brier **0.169803**, accuracy **78.26%** (72/92), versus V5 Brier0.182047. Best weekly distribution point result: CRPS **0.009756**, versus V5L01 0.009963. Search-adjusted intervals include no improvement. Monthly state-model accuracy81.58% did not pass mechanism falsification and showed undercoverage; there are onlyfourdisjoint monthly windows.\n\n'
    for n in REPORTS:index+=f'- [V6 {n.replace("_"," ").title()}](artifacts/nifty_forecast_v6/2026-11-19/run-001/V6_{n}.md)\n'
    index+='\n[Complete system comparison](artifacts/nifty_forecast_v6/2026-11-19/run-001/complete-system-comparison.csv) · [Reproducible scripts](research/nifty_forecast_v6/README.md) · [Verification](artifacts/nifty_forecast_v6/2026-11-19/run-001/verification.json) · [Replay](artifacts/nifty_forecast_v6/2026-11-19/run-001/replay-verification.json) · [Weekly figure](artifacts/nifty_forecast_v6/2026-11-19/run-001/weekly-results.png) · [Monthly falsification figure](artifacts/nifty_forecast_v6/2026-11-19/run-001/monthly-falsification.png)\n\nV1–V5 artifacts and the V4 prospective ledger remain unchanged. No new V6 forward forecast was issued; no trades or deployment occurred.\n'
    (ROOT/'NIFTY_V6_RESEARCH.md').write_text(index,encoding='utf-8')
    env={'recorded_at':stamp,'python':platform.python_version(),'platform':platform.platform(),'packages':{n:importlib.metadata.version(n) for n in ['numpy','pandas','scipy','scikit-learn','lightgbm','joblib']}}
    save('environment.json',env);save('report-manifest.json',{'generated_at':stamp,'reports':{f'V6_{n}.md':sha(OUT/f'V6_{n}.md') for n in REPORTS},'root_index_sha256':sha(ROOT/'NIFTY_V6_RESEARCH.md')})
    print('Generated',len(REPORTS),'reports and full comparison; generated_at',stamp,flush=True)

if __name__=='__main__':run()
