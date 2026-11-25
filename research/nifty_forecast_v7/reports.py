"""Render all deliverables from saved V7 results."""
from .common import *


def table(rows, columns):
    if isinstance(rows,pd.DataFrame):rows=rows.to_dict('records')
    def cell(value):
        if value is None or isinstance(value,float) and np.isnan(value):return '—'
        if isinstance(value,(float,np.floating)):return f'{value:.6f}'
        if isinstance(value,list):return '['+', '.join(cell(v) for v in value)+']'
        return str(value).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']+
                     ['| '+' | '.join(cell(row.get(c)) for c in columns)+' |' for row in rows])+'\n'


def run():
    metrics=pd.DataFrame(read('metrics.json'));index=metrics.set_index(['horizon','model']);contrasts=pd.read_csv(OUT/'benchmark-contrasts.csv')
    inc=pd.read_csv(OUT/'parent-increments.csv');stress=pd.read_csv(OUT/'stability-stress.csv');regime=pd.read_csv(OUT/'regime-calibration.csv')
    registry=read('experiment-registry.json');cfg=registry['configurations'];allp=pd.read_csv(OUT/'all-predictions.csv')
    auxiliary=pd.read_csv(OUT/'auxiliary-comparison.csv');num=read('v6-reproduction.json');unc=read('uncertainty.json');names=[]
    caution='The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history.'
    units='Brier and log loss score sign probabilities. CRPS scores the entire endpoint return distribution. Lower scores are better. CRPS, MAE and interval widths are in fractional return units. A width of .04 spans four percentage points. Gain means matched control loss minus candidate loss.'
    def write(name,body):
        fname=f'V7_{name}.md';names.append(fname)
        (OUT/fname).write_text(f'# NIFTY V7 · {name.replace("_"," ").title()}\n\nRun `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.\n\n'+body.strip()+'\n',encoding='utf-8')
    def scores(ids,h=5):
        rows=metrics[(metrics.horizon==h)&metrics.model.isin(ids)].set_index('model').reindex(ids).dropna(subset=['n']).reset_index()
        return table(rows,['model','n','accuracy','balanced_accuracy','brier','log_loss','crps','mae','median_mae','rmse','coverage50','coverage80','width80'])
    def cmp(ids,h=5,bases=('V6_BRIER','V6_CRPS')):
        rows=contrasts[(contrasts.horizon==h)&contrasts.model.isin(ids)&contrasts.baseline.isin(bases)&contrasts.metric.isin(['brier','crps'])]
        return table(rows,['model','baseline','metric','n','gain','adjusted95_block10'])
    def increments(ids,h=5):
        rows=inc[(inc.horizon==h)&inc.model.isin(ids)&inc.metric.isin(['brier','crps'])]
        return table(rows,['model','parent','metric','n','gain'])
    def stability(ids,h=5):
        baseline={'brier':'V6_BRIER','crps':'V6_CRPS' if h==5 else 'V6_MONTH_STATE'}
        rows=[]
        for name in ids:
            for score,base in baseline.items():
                for test in ['omit_fold','omit_largest_gains','disjoint_phase']:
                    z=stress[(stress.horizon==h)&(stress.model==name)&(stress.baseline==base)&(stress.metric==score)&(stress.test==test)]
                    if len(z):rows.append({'model':name,'score':score,'test':test,'least_gain':z.gain.min(),'most_gain':z.gain.max(),'positive':f'{sum(z.gain>0)}/{len(z)}'})
        return table(rows,['model','score','test','least_gain','most_gain','positive'])
    root_ids=['V6_BRIER','V6_CRPS','V6_DEF_NORM','I03_nosize','I00','L01','V4_D02_student_shrunk','V4_D03_residual_shrunk','V4_M05_lgbm','V4_Z_neutral','E00']
    diagnosis=pd.read_csv(OUT/'v6-paired-diagnosis.csv');vg=diagnosis[(diagnosis.horizon==5)].copy();vg['absolute_p_change']=vg.delta_p_vs_I03.abs()
    by=vg.groupby(['model','regime'],as_index=False).agg(n=('origin','size'),mean_P_change=('absolute_p_change','mean'),brier_gain=('Brier_gain_vs_I03','mean'),crps_gain=('CRPS_gain_vs_L01','mean'))
    changes=vg.groupby('model',as_index=False).agg(n=('origin','size'),mean_P_change=('absolute_p_change','mean'),brier_gain=('Brier_gain_vs_I03','mean'),crps_gain=('CRPS_gain_vs_L01','mean'))
    max_repro=max(r['max_abs_difference'] for r in num['folds'])
    concentration=[]
    for name,group in vg.groupby('model'):
        for score in ['Brier_gain_vs_I03','CRPS_gain_vs_L01']:
            for fold in group.fold.unique():
                left=group[group.fold!=fold]
                concentration.append({'model':name,'loss_difference':score,'omission':fold,'n':len(left),'gain':left[score].mean()})
            last=group.nsmallest(len(group)-5,score)
            concentration.append({'model':name,'loss_difference':score,'omission':'five largest positive contributions','n':len(last),'gain':last[score].mean()})
    pd.DataFrame(concentration).to_csv(OUT/'v6-diagnosis-stress.csv',index=False)
    write('V6_REPRODUCTION_AND_DIAGNOSIS',f'''
V6’s weekly Brier winner was `F_NO_DEFENSIVE`. It left out six 5- and 21-session relative-return features. V6’s CRPS winner `W2_NOAUTO_VOLUME` removed Auto 21-session relative return and added five ETF volume ratios. `W2_DEF_NORM` kept all six defensive inputs and scaled their standardized values by 1/√6. `W2_DEF_PC` used one whitened principal component for the same six columns. The underlying return regression used Ridge alpha 100 with train-median imputation and train standardization, clipping at ±5. The laws assign 65% to the conditional mean plus purged inner validation residuals and 35% to the last 252 or fewer matured historical returns.

The protected V6 index, all 13 reports, source modules, result and fit registries were inventoried in `reviewed-material.json` and `preservation.json`. V7 refit the four variants over 444 saved predictions across {len(num['folds'])} model and fold combinations, with maximum error {max_repro:.3g} across direction, location and proper scores. The inherited exact reconstruction also reproduced 81 V4/V5 prediction vectors and two independent V5 refits. The coherent V4 laws and separate LightGBM classifier maintain their original definitions. The prospective ledger is outside the historical comparison.

Defensive columns are {', '.join(num['defensive_columns'])}. The ETF features are {', '.join(num['volume_columns'])}. `v6-reproduction.json` records all fitted inputs and cutoffs.

{scores(root_ids)}

{table(changes,['model','n','mean_P_change','brier_gain','crps_gain'])}

{table(by,['model','regime','n','mean_P_change','brier_gain','crps_gain'])}

`v6-paired-diagnosis.csv` records each change. `v6-diagnosis-stress.csv` measures robustness against the prior V5 leaders after dropping each month and the five largest individual gains. The last omission is shown below. `stability-stress.csv` extends these checks to the V7 candidates and alternate disjoint sets. `F_DEF_LAG`, `F_DEF_EMBARGO`, and `F_DEF_REV` vary extra delay, earlier label maturity and minor native-price corrections. Their limited score changes do not resolve point-in-time receipt uncertainty.

{table([r for r in concentration if r['omission']=='five largest positive contributions'],['model','loss_difference','omission','n','gain'])}

{caution} {units}
''')
    corr=pd.read_csv(OUT/'feature-correlations.csv');first=corr[(corr.horizon==5)&(corr.fold=='2026-07')].copy();first['abs_corr']=first['corr'].abs()
    fact=pd.read_csv(OUT/'factor-stability.csv');row=fact.iloc[0];sector=pd.read_csv(OUT/'sector-correlation-map.csv')
    tests=['C_RAW','C_DUP','C_DUP_BALANCED','C_DEF','C_NO_DEF','C_BANK_DEF','C_PRUNE','C_REPRESENT','C_CLUSTER_MEAN','C_CLUSTER_BAL','C_FACTOR_GROUPS','C_PCA','C_PCA_WHITE','C_PCA_LW','C_PCA_ROLL','C_SPARSE','C_GROUP_LASSO','C_ELASTIC']
    write('FEATURE_REDUNDANCY',f'''
The first weekly fit used {int(row.training_n)} matured target dates. The 38 native relative-return columns formed {int(row.clusters)} training-only clusters using average linkage on 1 minus absolute Pearson correlation, cut at .25. Their entropy effective rank was {row.effective_rank:.2f}; the first principal direction explained {row.first_share:.1%} of training variance. After removing price and NIFTY risk covariation with Ridge100, the rank was {row.residual_rank:.2f}. Conditional correlations are residual associations and depend on that choice of controls.

{table(first.nlargest(16,'abs_corr'),['a','b','corr','price_residual_corr','same_lookback','identical_standardized_series'])}

{table(sector.assign(abs_corr=sector['corr'].abs()).sort_values('abs_corr',ascending=False).groupby('matrix').head(5),['matrix','a','b','corr','last_date'])}

The native feature matrix contains common benchmark subtraction and overlapping five- and 21-session transformations. This creates mechanical dependence in addition to real economic correlation. Bank and financial services indices can share constituents and exposures. The available current instrument inventory does not reconstruct changing historical constituent weights, so these results measure realized covariance rather than the fraction of historical overlap attributable to constituents. No inferred index weights were used as data. `feature-correlations.csv` includes both same-lookback and cross-lookback pairs and checks exact duplicate standardized series. `sector-correlation-map.csv` independently compares sector daily returns, five-session momentum and five-session rolling volatility.

The cluster map uses training data at the first weekly cutoff. Per-fold cluster definitions, all pairwise values and signed loadings are saved. No outer outcome or outer feature observation enters a fold’s transform. [Training cluster map](feature-cluster-map.png)

Exact duplicate columns have a predictable Ridge effect. If one standardized feature has two copies, coefficients can split equally while preserving their combined prediction. The squared coefficient penalty on that combined weight is halved. Scaling both copies by 1/√2 restores the original penalty. The copy intervention changes representation while holding informational content and targets fixed, which distinguishes it from correlations between two related economic series.
''')
    write('COMPRESSION_EXPERIMENTS',f'''
The initial batch compared {len(tests)} controlled configurations. Group definitions and unsupervised transforms were learnt separately in outer and purged inner fits. Greedy pruning at |r|≥.90 retained a deterministic first representative. Average linkage at .75 similarity gave the medoid, sign-aligned means and balance variants. Cluster balance divides standardized features by √cluster size. Economic aggregation uses the named sector families. Six-component PCA replaces the 38 relative-return inputs and retains the remaining risk, price and participation inputs. PCA whitening and Ledoit–Wolf whitening are separate treatments. Because Ledoit–Wolf shrinks toward a scaled identity, it preserves sample eigenvectors and changes the scale in this construction. [Ledoit and Wolf’s covariance estimator](https://www.ledoit.net/Well-conditioned2004.pdf)

{scores(tests)}

{scores(tests,21)}

Doubling the six defensive inputs increased weekly Brier from .182047 to .188090. Giving both copies the compensating 1/√2 weight returned the original forecasts numerically. Deletion and targeted normalization reach .169803 and .169862. Extending normalization to banks yields .171428. Greedy pruning helps relative to the raw reference at .174006, although it misses the defensive-specific scores. Broad PCA and sparse PCA fail to improve the original Brier or CRPS. Their retained directions explain input variance, which does not isolate useful conditional return information.

Cluster-balanced Elastic Net improves weekly CRPS from .009756 for the V6 distribution winner to .009695, while Brier worsens from .178802 to .184607. On the identical raw features, Elastic Net without balancing gives Brier .245135 and CRPS .011334. This contrast isolates the importance of feature scaling for this fitted objective. The embargo sensitivity variant records CRPS .009665. It was selected after seeing initial results and must be treated as a follow-up. It collapses to CRPS .014315 under the shorter-window stress. Economic group lasso has weekly Brier .201743 and CRPS .010910.

{cmp(['C_ELASTIC','T_ELASTIC_EMBARGO','C_PRUNE','C_CLUSTER_BAL'])}

{caution} {units}
''')
    write('FACTOR_STABILITY',f'''
Each fold uses an expanding supervised fit. For diagnostics, loadings also come from the first and latest 126 matured training-origin observations. PC signs are oriented by their largest absolute loading for display. Structural drift is measured using an absolute first-factor dot product and principal angles for the six-dimensional subspaces, both insensitive to sign. Cluster stability uses the Jaccard similarity of pairs assigned to a common cluster at successive cutoffs.

{table(fact,['horizon','fold','training_n','clusters','effective_rank','residual_rank','first_share','early_rank','recent_rank','early_recent_top_factor_abs_cosine','early_recent_max_principal_angle_deg','prior_fold_cluster_pair_jaccard'])}

The first weekly fold has first-factor cosine {row.early_recent_top_factor_abs_cosine:.3f} between early and recent training windows and worst six-factor angle {row.early_recent_max_principal_angle_deg:.1f}°. The cluster groupings can stay relatively stable while factor directions drift. The windows compare overlapping market histories across folds, so these are descriptive structural diagnostics.

{scores(['C_RAW','C_PCA','C_PCA_ROLL','C_PCA_WHITE','C_PCA_LW','C_SPARSE'])}

Rolling PCA estimates directions from the latest 126 observations while keeping the supervised regression training dates fixed. The weekly Brier rises from .192759 with full training PCA to .207871 with recent directions. At 21 sessions it rises from .292750 to .402258. Adaptation did not overcome estimated loading variation in this cohort. Generalization to a future break is unresolved. `factor-loadings.csv`, `factor-stability.csv` and `cluster-definitions.json` retain the loadings and reconstruction details. A feature map can identify recurring redundancy without resolving stable predictive factors.

{caution}
''')
    struct_names=['C_NO_DEF','S_SIMPLE','S_NETWORK','S_LEADERSHIP','S_LEVEL','S_STATE','S_STATE_LAG','S_STATE_ACCEL','S_ROTATION','T_ROT_DOMESTIC','T_ROT_OTHER','T_ROT_LAG5','T_ROT_FOREIGN_LAG','T_ROT_REV','T_ROT_WINDOW','T_ROT_EMBARGO']
    write('MARKET_STRUCTURE_RESEARCH',f'''
The 21-session correlation matrix of nine authentic Indian sector indices supplies average pair correlation, dispersion, share of variance in the largest eigenvalue, entropy effective factor count and the fraction of pairs above .65. We also measured implied volatility synchronization from correlations of trailing five-session realized standard deviations, participation signs, five-session rank persistence and leadership concentration. Volatility synchronization refers to the observed rolling realized-volatility features. The sequence uses causal rolling windows ending at the origin. No individual stock contributes an extra NIFTY outcome. The V6 defensive-deletion regression is the immediate parent of the structural additions.

{scores(struct_names)}

{increments(struct_names)}

V7’s lowest weekly Brier came after the exposed four-input rotation lead was split into domestic and cross-market/activity blocks. `T_ROT_DOMESTIC` adds only five-session changes in Bank Nifty minus financial services momentum and defensive minus cyclical momentum. It reaches Brier .162145 and 74/92 correct. The full four-field `S_ROTATION` reaches .164548. The global-relative plus ETF subblock alone reaches .169046. Simple correlation levels and broad network measures produce weaker gains. The full four-field lag control reaches .164382 when the four added inputs are set back five sessions, which leaves the interpretation of current rotation timing unresolved. A shorter 189-origin training window raises Brier to .223615.

{stability(['T_ROT_DOMESTIC','S_ROTATION','S_STATE_ACCEL'])}

{cmp(['T_ROT_DOMESTIC','S_ROTATION','S_NETWORK','S_STATE_ACCEL'])}

The best direction score is an adaptive finding with a simultaneous interval spanning zero. Largest-origin removal and matched regime splits matter because nearby origins share return paths. See `regime-calibration.csv` and the origin-level files. {caution}
''')
    risk=auxiliary[(auxiliary.family=='state')&(auxiliary.regime=='all')]
    write('STATE_TRANSITION_RESEARCH',f'''
The matched levels parent uses mean correlation, first eigenvalue share, volatility synchronization, participation, concentration and bank/financial spread. The state model adds five-session differences, five-session loading drift and a regularized next-session high-correlation transition frequency. The high-correlation state uses mean pair correlation >.60. The transition estimate conditions on the observed current state, counts transitions ending by the origin over a trailing 63-session window, and uses Beta(2,2) smoothing. The acceleration model adds second differences with a five-session spacing. Added changes are delayed five sessions in the placebo. The frozen labels remain endpoint returns at 5 and 21 trading sessions.

{scores(['S_LEVEL','S_STATE','S_STATE_LAG','S_STATE_ACCEL','S_ROTATION'])}

{scores(['S_LEVEL','S_STATE','S_STATE_LAG','S_STATE_ACCEL','S_ROTATION','M_PERSIST'],21)}

{table(risk,['horizon','target','method','n','mae','rmse','actual_mean'])}

The risk comparisons add matched changes beyond their own corresponding levels. For 21-session realized volatility, change inputs reduce annualized volatility MAE from .022377 to .021716. For five-session absolute returns, MAE increases from .010454 to .010747. The large-move target is |return| above 2% at five sessions or 4% at 21 sessions. Its probabilities are bounded Ridge estimates and RMSE squared is Brier. Both large-move changes are weaker by MAE. The risk tests score dependent dates and provide no independent evidence of regime-break skill. Absolute-return forecasts and forward realized volatility are separate targets with distinct units.

{caution}
''')
    intra=read('intraday-audit.json');day=matrix('intraday-features.csv',OUT);glob=auxiliary[auxiliary.family=='global']
    write('GLOBAL_AND_LIQUIDITY_RESEARCH',f'''
The frozen V5 availability map contains {read('source-audit.json')['availability_rows']} selected foreign origin/series rows. Every selected source availability time precedes its recorded decision. Known cash-index series use exchange time zones and a two-hour close buffer. Uncertain CFD and FX conventions use a two-UTC-day delay. Historical receipt timestamps remain reconstructed. `IXIX` is a provider US technology proxy. Verified Nasdaq cash-index and US yield histories were unavailable in the retained input set, so the tested technology link is narrower than an exchange-authenticated Nasdaq transmission study.

The registered intermediate tests add limited foreign inputs to own-state controls. Targets include IT and energy future relative returns, endpoint sector synchrony and breadth, absolute return, future realized volatility and large moves. The breadth branch uses HSI/Nikkei five-session returns and their absolute divergence. Each correction uses only matured targets in its historical monthly refit. A fixed .60 correlation gate and past-training-median volatility split assess whether performance is concentrated in identifiable regimes. `auxiliary-comparison.csv` contains those slices. Downstream direct and reconstructed intermediate corrections share the same eligible training and query dates.

{table(glob[glob.regime=='all'],['horizon','target','method','n','mae','rmse'])}

{scores(['G_BASE5','G_DIRECT5','G_INTERMEDIATE5','V6_BRIER'])}

{scores(['G_BASE21','G_DIRECT21','G_INTERMEDIATE21','V6_BRIER'],21)}

Weekly energy MAE falls only by about 0.000008. The other weekly overall intermediates and every monthly overall intermediate worsen. The NIFTY models lose to their own eligible-date controls. Three July monthly downstream fits lack the minimum purged intermediate history and remain unestimated. The resulting monthly comparison has 53 origins. These are predictive transmission tests with regime and sample restrictions. They do not identify economic causation.

## Domestic activity and actual intraday candles

Upstox supplied {sum(r['rows'] for r in intra['requests']):,} archived 25-minute index bars across eight bounded requests. Exact 15-bar regular-session grid and OHLC checks retained {len(day)} sessions from the 403 aligned daily dates and excluded {len(intra['rejected'])} observed sessions with invalid or nonregular grids. The median difference between the last intraday bar and the daily close was {day.close_difference_points.abs().median():.2f} points in absolute terms, and the max was {day.close_difference_points.abs().max():.2f}. We use intraday increments, 50-minute opening and closing behavior, and leave the official daily return target anchored to archived daily closes. Index volume is excluded. Daily opening/closing features use gap and open-to-close logs, trailing range, and actual traded ETF volume ratios. Positioning inputs come from the inherited NSE daily derivatives archives with one-session lag. The liquid-stock panel is a marked survivorship-exposed proxy study using real historical observations from a later selected basket. [Upstox historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [NSE archive reports](https://www.nseindia.com/all-reports)

{scores(['C_NO_DEF','L_ETF','L_DAILY','L_INTRADAY_BASE','L_INTRADAY','L_POSITION','L_STOCK_PROXY','T_DAY_OC','T_DAY_ETF','T_DAY_LAG','T_DAY_WINDOW'])}

The intraday result has 91 weekly matched origins and is slightly worse than its identical-availability control. Positioning and the stock-proxy additions do not improve the weekly Brier benchmark. Daily opening/closing and ETF terms jointly give Brier .166724, CRPS .009893 and 80.43% interval coverage. The open-close and activity feature sets are individually competitive. A shorter training window reduces both. The activity evidence is a representation lead, not proof of a liquidity premium.

{caution}
''')
    adv=[n for n,s in cfg.items() if s['batch']=='advanced']
    write('ADVANCED_MODEL_RESEARCH',f'''
Configuration-level tests compare structured Ridge, Elastic Net, economic group lasso, Bayesian Ridge, Huber, quadratic splines, shallow forest, shallow histogram gradient boosting, a residual boosting correction, two fixed interactions and volatility-gated Ridge experts. All fitted transforms use only allowed historical rows. The residual model fits on training residuals then adds half its predicted correction. Experts retain 60% of the pooled Ridge location with 40% from the historical high/low-risk expert. Fixed-knot GAM-style splines and the shallow-tree and forest parameters are in `models.py`. Forecast error comparisons keep the common empirical law across location architectures.

{scores(['C_RAW','C_NO_DEF','C_PCA_WHITE','C_ELASTIC','C_GROUP_LASSO',*adv,'T_RAW_ELASTIC'])}

{scores(['C_RAW','C_NO_DEF','C_PCA_WHITE','C_ELASTIC','C_GROUP_LASSO',*adv],21)}

The learned representation mattered more than searching for additional tree or sequence estimators. Sparse compressed regression did better at some scores, while broad factor compression and flexible residual models struggled. Since clustered Elastic Net outperformed raw Elastic Net here, a separate regularization change can improve prediction with the same underlying market inputs. Parameters were held fixed per family. V7 keeps the existing V4 LightGBM vector as a strong frozen benchmark. XGBoost, CatBoost, neural temporal models and an extra hyperparameter grid were not run. The sample contains 19 weekly and four monthly disjoint windows. Training and numerical warnings appear in `fit-ledger.csv`.

{units}
''')
    write('COHERENT_DISTRIBUTION_RESEARCH',f'''
The reference laws combine purged inner residual atoms with mature historical empirical returns using 65/35 mass. Tests compare Student df5 residuals, risk-scaled residuals, sorted/interpolated quantiles, fixed complete-law mixtures, training-optimized complete-law mixtures and reweighting positive return atoms. Quantile forecasts sort five fitted quantiles and clamp the sampled interpolation tails outside .10/.90. This can distort tail probabilities. Record-level endpoint mean, median, quantiles, buckets and p(up) always come from the same finite law. `expected_endpoint` rescales the mean by the actual origin close. Path probabilities are outside the return-law interpretation.

Mixture and tilt estimates use the latest 42 reconstructed forecasts with outcomes maturing strictly before their current fit anchor. We constrain the joint weight to [.1,.9] and penalize deviations from .5. The objective is mean CRPS/.02 plus Brier/.25 plus .25(w−.5)². Sign tilt multiplies positive atom weights by exp(shift), with shift in [−.5,.5], selecting by Brier plus .15 times squared shift. These calibrations use historical-only past forecasts reconstructed in this run, with actual prequential timing checked in `integration-ledger.json`.

{scores(['V6_BRIER','V6_CRPS','D_SPARSE','D_RISK','D_QUANTILE','D_ETF_STUDENT','J_EQUAL','J_JOINT','J_TILT','L_DAILY','C_ELASTIC','T_ELASTIC_EMBARGO'])}

{scores(['V6_MONTH_STATE','V6_MONTH_LAG1','D_SPARSE','D_RISK','D_QUANTILE','D_ETF_STUDENT','J_EQUAL','J_JOINT','J_TILT'],21)}

The equal mixture yields Brier .172391, CRPS .009825 and 80.43% interval coverage. Joint tuning improves Brier to .171066 relative to equal weighting but raises CRPS to .009865. Sign tilting has Brier .168143 and CRPS .010074. These mixture variants do not deliver joint dominance over the separate V6 winners. The best new point-score distribution is the later Elastic Net embargo sensitivity with .009665 CRPS, .184134 Brier and 81.52% coverage. Its gain over V6 CRPS is approximately .000090, with a 10-session-block simultaneous interval spanning −.001986 to .002167. Raw proper and pinball losses, regime coverage, widths and probability bin calibration remain available in the saved tables.

{table(regime[(regime.horizon==5)&regime.model.isin(['C_ELASTIC','T_ELASTIC_EMBARGO','L_DAILY','T_ROT_DOMESTIC'])&(regime.regime_type=='regime')],['model','state','n','disjoint','brier','crps','coverage80','nominal_width80'])}

{caution} {units}
''')
    month=['V6_MONTH_STATE','V6_MONTH_LAG1','V6_BRIER','I03_nosize','L01','E00','V4_Z_neutral','M_STATE_BASE','M_STATE','M_STATE_LAG5','M_STATE_LAG21','M_STATE_SHIFT5','M_STATE_SHIFT21','M_STATE_126','M_PERSIST','C_ELASTIC']
    norm=pd.read_csv(OUT/'intermediate-normalized.csv').groupby(['horizon','model'],as_index=False).agg(n=('origin','size'),brier_gain=('brier_gain','mean'),crps_gain=('crps_gain','mean'),hist_crps=('hist_crps','mean'))
    norm['relative_crps_gain']=norm.crps_gain/norm.hist_crps
    monthly=allp[(allp.horizon==21)&(allp.model=='M_STATE_LAG21')]
    write('MONTHLY_FALSIFICATION',f'''
The earlier 81.58% figure came from 62 of 76 overlapping origins. Those forecasts comprise only four disjoint outcomes. V7 rebuilds weekly forecast levels and slopes on genuine past data, using V6’s frozen historical reconstruction. The current, lagged, longer-window, and shuffled-state comparisons share origins and restrict training to dates where a 21-session lag and current state inputs both existed. Consequently `M_STATE` is a changed eligibility refit. The exact earlier recipe retains the frozen `V6_MONTH_STATE` result. None of the historical states were issued prospectively.

{scores(month,21)}

The stricter matched-date current state achieves .239924 Brier, .029723 CRPS and 44.74% coverage. Taking the features back by a full 21 sessions reaches .171774 Brier, 58/76 correct and 84.21% nominal-80% coverage, but CRPS .025530 is worse than V6’s .024530 one-lag candidate. Circularly rolling the training state by five or 21 observations leaves the genuine price features intact, breaks exact state/label alignment and beats the current-state CRPS. The attractive lagged result can reflect persistent regimes and selected history. Neutral and historical forecasts are controls for base rates. Observed up frequency is {monthly.outcome.mean():.2%} on the 76 dates. An always-majority classifier would get {max(monthly.outcome.mean(),1-monthly.outcome.mean()):.2%}, below the retrospective lagged rate. This comparison does not remove label overlap or narrow-period dependence.

{stability(['M_STATE','M_STATE_LAG21','C_ELASTIC'],21)}

{table(norm,['horizon','model','n','brier_gain','crps_gain','hist_crps','relative_crps_gain'])}

Ten- and 15-session forecasts use the same 76 original monthly origins with respective maturity windows and own historical benchmarks. Their results remain diagnostic. Expanding horizons increases score units and dependence, so relative CRPS gain normalizes by the appropriate historical-law loss. No redefinition of either primary horizon follows from these observations. All monthly intervals are withheld given four disjoint windows. The lagged state is retained as a persistence hypothesis, and the information-timing mechanism remains unresolved.
''')
    failures=[r for r in registry['fit_attempts'] if r['status']=='failed']
    primary=metrics[metrics.horizon.isin([5,21])&metrics.status.ne('frozen reference')]
    write('VALIDATION_AND_SEARCH_AUDIT',f'''
Historical decisions follow the original frozen evaluation calendar. Intraday grid, foreign completion times, source overlap revisions and feature truncation invariance are documented separately. Training requires the full target endpoint strictly before the fold cutoff. The last 42 mature training observations form an inner residual-validation window. Its fitting labels must end strictly before that window. Alternative cutoffs move both maturity boundaries three observed sessions earlier. Training-only scale, clustering, factor directions and estimation are refitted in each partition. Initial raw histories begin in 2025. The model cohort is fixed to the V6 historical origins and no newer labels are added.

Actual cross-vintage close revisions are in `source-audit.json` and the synthetic revisions exercise one-basis-point perturbations through feature reconstruction. Exact duplicate tests, joint query perturbation, financial/cyclical block removal, five-session placebo inputs, earlier cutoffs and shifted targets are recorded as falsification or sensitivity experiments. The weekly target displacement gives Brier .271782. Training dates were not chosen to exclude difficult outer outcomes. Historical sources lack authenticated original receipts and exact historical constituent composition. The current stock sample is separately marked as a research-only survivorship proxy.

V7 scored {len(primary)} primary candidate/horizon cells and {len(metrics[(metrics.horizon.isin([10,15]))])} 10/15-session cells. There are {len(allp):,} saved prediction rows and {len(contrasts):,} matched strong-control comparisons, of which {unc['weekly_family_contrasts']:,} enter the weekly simultaneous bootstrap family. Two thousand circular block draws are shared across cells, with 5-, 10- and 15-session length sensitivity. The maximum standardized bootstrap deviation supplies the simultaneous critical value for the family at each length. Unadjusted 10-session block intervals are retained separately. Model selection from V1–V6 and interpretation of additional slices are outside the covered family. All forecasts remain research-exposed.

{table([{'block':int(k),'critical_value':v} for k,v in unc['critical_values'].items()],['block','critical_value'])}

{cmp(['T_ROT_DOMESTIC','L_DAILY','C_ELASTIC','T_ELASTIC_EMBARGO'])}

The original global/integration attempt selected the V5 I03 origins, which contained outer rows only. Its 27 unestimable downstream fits and first outputs are archived. The corrected run uses the frozen V3 development and outer calendar. An intervening metadata join failure is recorded. The corrected current global batch retains three July monthly insufficiencies. Adaptive rotation/activity and Elastic Net follow-ups were motivated by the exposed initial results and included in the V7 search family. Numerical warning text, status, and SHA-256 model hashes are in `fit-ledger.csv`; no failures are filled with estimated scores.

{table(failures,['horizon','fold','model','status','reason'])}

`prior-integrity-verification.json`, `verification.json` and `report-manifest.json` record repeat checks over the preserved artifacts, data alignment, selected candidate replay and reports. No V7 forward issuance, trade or deployment occurred. {caution}
''')
    combo=metrics[metrics.horizon.isin([5,21])]
    full_cols=['model','status','n','disjoint_n','ESS','accuracy','balanced_accuracy','brier','log_loss','crps','mae','rmse','coverage50','coverage80','width50','width80']
    comp=combo.copy()
    for score,base in [('brier','V6_BRIER'),('crps','V6_CRPS')]:
        sub=contrasts[(contrasts.metric==score)&(contrasts.baseline==base)][['horizon','model','gain','adjusted95_block10']].rename(columns={'gain':f'{score}_gain_vs_{base}','adjusted95_block10':f'{score}_adjusted95_vs_{base}'})
        comp=comp.merge(sub,on=['horizon','model'],how='left')
    span=stress[(stress.test=='omit_fold')&(stress.metric=='brier')&(stress.baseline=='V6_BRIER')].groupby(['horizon','model'],as_index=False).agg(leave_month_worst_gain=('gain','min'),leave_month_best_gain=('gain','max'))
    comp.merge(span,on=['horizon','model'],how='left').drop(columns=['calibration_bins','bucket_calibration'],errors='ignore').to_csv(OUT/'complete-comparison.csv',index=False)
    write('COMPLETE_COMPARISON',f'''
Complete system results use separate probability and distribution loss rankings. Diagnostic duplicate, target-roll, stock-membership, lagged and shifted controls remain marked in the registry. The legacy LightGBM benchmark keeps its original separate classifier and quantile definitions. V6 CRPS and group-normalized leaders were computed only for the weekly horizon. Monthly V6 controls include the original state and extra-lag experiments, in addition to the monthly defensive-deletion fit. Cohort-matched comparisons are in `benchmark-contrasts.csv` and `complete-comparison.csv` adds leave-month ranges, eligible adjusted intervals, representation and leakage metadata. View smaller-cohort estimates as paired tests on their own dates.

{caution} {units}

## Five sessions sorted by Brier

{table(combo[combo.horizon==5].sort_values('brier'),full_cols)}

## Twenty-one sessions sorted by CRPS

{table(combo[combo.horizon==21].sort_values('crps'),full_cols)}

The direction and distribution CSVs enable alternate ordering on the same raw values. `regime-calibration.csv` provides conditional coverage and interval width. `metrics.json` retains calibration-bin counts and probabilities. `benchmark-contrasts.json` stores search-adjusted intervals with each weekly block sensitivity. Monthly comparative uncertainty remains descriptive.
''')
    write('SIGNAL_DISCOVERIES',f'''
1. Defensive duplication changes the fitted Ridge law without any new information. Weekly Brier changes .182047 → .188090. Compensating copy weights restore .182047. Targeted six-feature downweighting works better historically than generic PCA, supporting the V6 regularization explanation. It does not resolve the economic value of the underlying defensive indices.
2. Domestic rotation differences give the best V7 probability point result. The domestic two-feature addition gains .007658 Brier against the frozen V6 Brier leader. Its short-window failure and the competitive lagged broader rotation control limit the timing inference.
3. Cluster-balanced Elastic Net and the earlier-cutoff sensitivity improve distribution score while giving up direction quality. Raw Elastic Net is much worse in the directly matched scaling contrast. Shorter training is a material failure mode.
4. Daily opening/closing and actual ETF activity are a complementary weekly lead. Direct intraday realized-volatility and position data do not presently add value to their matched controls. Current-stock results require historical membership verification.
5. Current sector topology, rolling factors, global correction models and most nonlinear alternatives give weak or negative additions. The smaller domain-specific representation outperformed broad unsupervised compression in weekly direction.
6. Monthly lagged-state probability gains survive some comparisons but shifted controls remain competitive in CRPS. Separate persistent factors, Student laws and the global block do not establish robust monthly performance.

{increments(['C_DEF','C_PRUNE','C_CLUSTER_BAL','C_ELASTIC','T_ROT_DOMESTIC','T_DAY_OC','T_DAY_ETF','L_DAILY','G_DIRECT5','G_INTERMEDIATE5','S_STATE','S_STATE_ACCEL'])}

This ordering is an interpretation of paired experiments, separate from the numerical whole-system leaderboards. Each hypothesis retains its immediate control. A higher full-system rank can come from weaker regularization, sample restriction or several jointly changed inputs. {caution}
''')
    write('FINAL_RESEARCH_CONCLUSIONS',f'''
V7 improves the retrospective weekly point scores. It finds a direct regularization effect for exact correlated duplication and a narrower candidate based on relative sector rotation. Neither improvement establishes an independent forecasting edge. The rotation Brier winner and the Elastic Net CRPS winner are different systems and neither beats the other on both objectives.

{scores(['V6_BRIER','V6_CRPS','T_ROT_DOMESTIC','L_DAILY','C_ELASTIC','T_ELASTIC_EMBARGO','J_EQUAL','J_JOINT'])}

The best weekly Brier is .162145 versus V6 .169803, a 4.51% relative gain. The adaptive domestic rotation model gets 74 of 92 directions correct, 80.43%, with 81.52% coverage for its nominal 80% interval. Its 10-session-block adjusted improvement interval is approximately [−.006942,.022257]. The best CRPS is .009665 versus V6 .009756, a gain of about .93%. It comes from the earlier maturity cutoff in the cluster-balanced Elastic Net follow-up. It loses to V6 on Brier and has an adjusted CRPS gain interval of [−.001986,.002167]. The original clustered fit at .009695 offers a cleaner comparison before the adaptive cutoff test.

Retain the frozen V6 controls, domestic rotation, clustered Elastic Net and daily opening/closing plus ETF activity as separate hypotheses. The best weekly probability result deteriorates with a shorter revised training window. Exact duplication identifies how weighting changes fitted output. It cannot establish that the same effects will produce reliable gains outside this cohort. Rolled, delayed and matched weak controls remain visible in the delivery.

Monthly `M_STATE_LAG21` improves the point Brier to .171774 and interval coverage to 84.21%, while CRPS .025530 trails the earlier .024530 monthly exploratory law. Shifted state controls with CRPS .023773 and .024168 undermine the interpretation of date-specific information. Four disjoint return windows are insufficient to promote a monthly model. Weekly and monthly remain the primary horizons at five and 21 sessions.

{caution} {units}
''')
    write('NEXT_EXPERIMENTS',f'''
Freeze the domestic two-feature change model, fixed group-normalized Ridge, cluster-balanced Elastic Net and daily OHLC/ETF model with the original V6 controls before evaluating truly new outcomes. Retain the exact distribution and fit cutoff chosen in advance. Treat the embargo sensitivity as a registered comparison. Use the repeated-date forecast archive for scores and disjoint windows for dependence diagnostics. Capture exact input receipts and use a separate versioned research-only forward record for any future study.

Test the two domestic rotation features independently and together on the same eligible dates, with five-session lag and level-only controls. Report shorter-window stress before inspecting new outcomes. Scale exact duplicates by matched penalties when comparing redundancy across estimators. A small penalty comparison can test whether the V7 mechanism holds across defense and financial exposures. Historical point-in-time index weights would let us distinguish common constituents from co-movement and common benchmark subtraction.

For risk, prospectively compare the small structural-volatility increment against a historical realized-volatility control and the daily OHLC/ETF law against the V6 distribution. The incremental intraday series should use independently archived regular and special session schedules and explicit close-vintage reconciliation. Acquire verified historical global cash/yield data before repeating the targeted sector tests. Use available source windows and matched cohorts to control coverage.

For the monthly state failure, freeze no-state, current-state, and one-month-lag systems plus block controls. Assess whether the matched improvement persists on new disjoint 21-session periods and check probability calibration and wider interval calibration jointly. Keep intermediate 10/15-session results diagnostic and preserve the original versions. A larger model search would not create more independent monthly outcomes.
''')
    save('report-manifest.json',{name:sha(OUT/name) for name in names})
    rel=OUT.relative_to(ROOT).as_posix()
    content=['# NIFTY V7 research','',f'Completed on {now()}. The research is retrospective and limited to 2025–2026 observations.',
        '', 'The best weekly Brier was **0.162145** on 92 origins. The best weekly CRPS was **0.009665**. Search-adjusted gain intervals include zero. The monthly state mechanism remains unresolved.', '']
    content += [f'- [{n.removeprefix("V7_").removesuffix(".md").replace("_"," ").title()}]({rel}/{n})' for n in names]
    content+=['',f'[Complete comparison]({rel}/complete-comparison.csv) · [Predictions]({rel}/all-predictions.csv) · [Cluster map]({rel}/feature-cluster-map.png) · [Verification]({rel}/verification.json) · [Reproduction instructions](research/nifty_forecast_v7/README.md)','']
    if OUT == BASE/'2026-11-24/run-001':
        (ROOT/'NIFTY_V7_RESEARCH.md').write_text('\n'.join(content),encoding='utf-8')
    print('Rendered',len(names),'V7 reports',flush=True)


if __name__=='__main__':
    run()
