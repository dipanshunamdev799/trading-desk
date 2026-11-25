"""Build the seventeen V8 reports directly from frozen analytical results."""
from .common import *


def table(data, cols):
    if isinstance(data,pd.DataFrame):data=data.to_dict('records')
    def display(value):
        if value is None or isinstance(value,float) and np.isnan(value):return '—'
        if isinstance(value,(float,np.floating)):return f'{value:.6f}'
        if isinstance(value,list):return '['+', '.join(display(x) for x in value)+']'
        return str(value).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+
                     ['| '+' | '.join(display(row.get(c)) for c in cols)+' |' for row in data])+'\n'


def run():
    ms=pd.DataFrame(read('metrics.json'));comp=pd.DataFrame(read('comparisons.json'));registry=read('search-ledger.json')
    change=pd.read_csv(OUT/'parent-increments.csv');condition=pd.read_csv(OUT/'conditional-slices.csv');stress=pd.read_csv(OUT/'stress-results.csv')
    preds=pd.read_csv(OUT/'all-predictions.csv');unc=read('search-adjusted-uncertainty.json');names=[]
    caption='All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.'
    small='The primary weekly cohort has 92 overlapping origins, 19 disjoint windows and a return-ACF ESS of about 12.36. Monthly evaluation has 76 overlapping origins and approximately four disjoint windows. Dependence diagnostics are not independent trials.'
    columns=['model','n','disjoint','accuracy','balanced_accuracy','brier','log_loss','crps','mae','rmse','pinball','coverage50','coverage80','width80']
    def write_report(name,body):
        path=f'V8_{name}.md';names.append(path)
        (OUT/path).write_text(f'# NIFTY V8 · {name.replace("_"," ").title()}\n\nRun `2026-11-24/run-001`. Retrospective research.\n\n'+body.strip()+'\n\n'+caption+'\n',encoding='utf-8')
    def scores(models=None,h=5,cohort='primary'):
        rows=ms[(ms.cohort==cohort)&(ms.horizon==h)]
        if models is not None:
            rows=rows[rows.model.isin(models)].set_index('model').reindex(models).dropna(subset=['n']).reset_index()
        return table(rows,columns)
    def gains(models,h=5,cohort='primary'):
        return table(change[(change.horizon==h)&(change.cohort==cohort)&change.model.isin(models)&change.metric.isin(['brier','crps'])],['model','parent','metric','n','gain'])
    def comparison(models,h=5):
        bases=['T_ROT_DOMESTIC','T_ELASTIC_EMBARGO'] if h==5 else ['V6_MONTH_LAG1','V7_M_STATE_LAG21']
        return table(comp[(comp.horizon==h)&comp.model.isin(models)&comp.baseline.isin(bases)&comp.metric.isin(['brier','crps'])],
                     ['model','baseline','metric','n','gain','simultaneous95_block10'])
    def sensitivity(models,h=5):
        base='T_ROT_DOMESTIC' if h==5 else 'V6_MONTH_LAG1'
        z=stress[(stress.horizon==h)&stress.model.isin(models)&(stress.baseline==base)&stress.metric.isin(['brier','crps'])]
        g=z.groupby(['model','metric','kind'],as_index=False).gain.agg(min_gain='min',max_gain='max',positive=lambda y:f'{sum(y>0)}/{len(y)}')
        return table(g,['model','metric','kind','min_gain','max_gain','positive'])
    def slices(models,keys,h=5):
        part=condition[(condition.horizon==h)&condition.model.isin(models)&condition.condition.isin(keys)]
        return table(part,['model','condition','value','n','disjoint','brier_gain','CRPS_gain','leave_month_gain_min','leave_month_gain_max','coverage80'])
    refs=['T_ROT_DOMESTIC','T_ROT_EMBARGO','T_ROT_LAG5','T_DAY_ETF','T_ELASTIC_EMBARGO','V6_BRIER','V6_CRPS',
          'I03_nosize','I00','L01','V4_D02_student_shrunk','V4_D03_residual_shrunk','V4_M05_lgbm','V4_Z_neutral','E00']
    repro=read('reproduction.json');winner=pd.read_csv(OUT/'winner-origin-diagnosis.csv')
    per_period=winner.groupby(['model','fold'],as_index=False).agg(n=('origin','size'),correct=('correct','sum'),brier_gain_vs_v6=('brier_gain_vs_v6','mean'),crps_gain_vs_v6=('crps_gain_vs_v6','mean'))
    write_report('REPRODUCTION_AND_WINNER_DIAGNOSIS',f'''
All **644** requested weekly forecasts were freshly refit from their actual saved model configurations and cutoff dates. The maximum absolute difference in probability, conditional mean, median, Brier or CRPS was **{repro['max_error']:.3g}**. The earlier reconstruction also recovered 81 V4/V5 stored model/fold vectors. `preservation.json` inventories the reviewed V7 index, fifteen reports, registry, full prediction and comparison files, cluster definitions, verification and sources.

The V7 rotation parents use the V6 51-column native set after removing six defensive relative-return columns. The domestic variant adds two five-session spread changes. The embargo and lag variants use the four-input rotation set with the global-relative change and ETF activity change as well. The former places both outer and inner label maturity boundaries three sessions earlier. The latter delays all four additional inputs by five observed sessions. The ETF variant adds the mean abnormal volume and its five-session change. The Elastic Net variant retains the full native set with learned cluster balancing, alpha .0006 and L1 ratio .3, and uses the three-session earlier cutoff. V6 CRPS removes `i_nifty_auto_rel21` and adds five ETF-volume ratios. Train medians impute missing fields after the 30-observation inclusion screen, followed by centering, scaling and ±5 clipping.

{scores(refs)}

{table(per_period,['model','fold','n','correct','brier_gain_vs_v6','crps_gain_vs_v6'])}

Every correct and incorrect call is in `winner-origin-diagnosis.csv`. Full atoms and probability masses are in `reproduced-endpoint-laws.jsonl`, with fitted weights in `winner-coefficients.csv`. `reproduction.json` carries all training, validation and query anchor information. The conditional endpoint law gives 65% mass to a modeled mean plus residuals from a purged 42-origin validation partition; 35% comes from at most 252 earlier matured outcomes. Source data come from frozen Upstox/NSE archives and inherited global time alignments. Reconstructed historical receipt times remain the main timestamp limitation. V8 computes spread changes over the underlying raw warmup. That permits five earlier values with sufficient raw history which V7's reindexed difference left missing. Consequently V8 `B_ROT` is a very close refit and the exact V7 result remains the directly replayed reference.

{small}
''')
    geo=[n for n,s in registry['configurations'].items() if s['batch']=='geometry'];inv=pd.concat([pd.read_csv(OUT/'invariance-effects.csv'),pd.read_csv(OUT/'sector-alias-effects.csv')])
    joined=inv.groupby(['model','method','variant'],as_index=False).agg(max_law_error=('max_law_error','max'),max_probability_change=('max_probability_change','max'),passes=('passes_tolerance','sum'),folds=('fold','count'),aliases=('aliases','max'))
    write_report('REGULARIZATION_GEOMETRY',f'''
Exact copies identify a prediction effect without introducing a single market observation. In linear Ridge, if two standardized columns are copies, their two coefficients can sum to the original coefficient and each take half the original value. The sum of their squared penalties is then half the original. Four copies including the original reduce the effective penalty to one quarter. Dividing each standardized copy by √k restores the original direction's cost for k identical columns. This is why interacting sector representations can influence Ridge even when the signal set itself has not grown. Scaling duplicate features similarly is generally insufficient to preserve Elastic Net's mixed L1/L2 geometry.

{scores(['I_ridge_as_is','I_ridge_one_copy','I_ridge_three_copies','I_ridge_balanced_three','I_canonical_ridge_three_copies','I_elastic_as_is','I_elastic_three_copies','I_canonical_elastic_three_copies'])}

V8 eliminates exact standardized-copy families before constructing transformations, and proves numerical invariance by testing atoms and weights. It also compares covariance-aware coefficient scaling through `(I + 0.65 Σ_shrunk)^(-1/2)` and compounded cluster and sector-group penalties. Those choices change the cost of a fitted direction even with no actual copies. Covariance Ridge and the hierarchical penalty worsen the primary weekly Brier versus raw native Ridge in this study. The positive conclusion is representation invariance under known transformations. It does not require a selected post-hoc shrinkage geometry to also improve a proper score.

{scores(['B_FULL','G_CANON','G_CLUSTER','G_COV','G_HIERARCHICAL','G_RESID','G_ROT_CLUSTER','G_ROT_COV','G_ROT_ELASTIC'])}
''')
    maxerr=float(inv[inv.required_invariance].max_law_error.max())
    write_report('DUPLICATE_INVARIANCE_TESTS',f'''
The initial suite varies order, positive affine units, equivalent affine formula, one exact copy, three exact copies, and an affine duplicate with altered units. The compensating Ridge test divides the original and three replicas by 2. We compare complete probability, mean, return atoms and atom weights over the same five folds. The canonical rule finds matches using **unclipped** standardized training histories with identical missingness masks at tolerance 1e-11. Canonical order is stable by name. The prediction tolerance is 1e-10. Positive affine transforms are the tested equivalence class. Similar correlations, nonlinear transforms and future values that merely happened to match during training require separate assessment.

The secondary suite names the synthetic copies as native sector columns so they enter clustering itself. This addresses the initial generic synthetic name test, where uncanonicalized copies could sit outside the sector cluster parser. The combined suites pass **125 required** complete-law checks, with maximum error **{maxerr:.3g}**. The original unbalanced replicated Elastic Net controls emitted some optimizer convergence warnings. They remain sensitivity examples and the required canonical checks passed. Additional copy stress on rotation and structure winners recovers identical results for canonical fits using the three larger input designs.

{table(joined,['model','variant','folds','passes','max_law_error','max_probability_change','aliases'])}

`invariance-effects.csv` and `sector-alias-effects.csv` keep the fold-level numerical errors. An exact duplicate identified in training is treated as equivalent by design. Misidentification risk if two feeds split apart outside training is a provenance issue rather than tested invariance to that changed economic signal.
''')
    write_report('CLUSTER_AWARE_MODELS',f'''
The sector relative-return block uses training-only absolute correlations, average linkage at distance .25, and fixed representation alternatives. Inverse square-root cluster-size scaling keeps all distinct features. The Bayesian variant uses a global precision on cluster-scaled coordinates, which induces different original-coordinate priors by cluster size. The hierarchical variant compounds economic group size and data-driven cluster weights. Factor-plus-residual projection uses signed cluster means and Ridge10 to estimate factor exposures, then adds residuals with half their original scale. Representative selection makes a 75/25 blend of within-cluster centrality and past target correlation. Assignments for every fitted cutoff are saved in the fit ledgers and models.

{scores(geo)}

{scores(geo,21)}

Raw and canonical native Ridge are numerically equivalent on this matrix. Generic cluster balancing gives .177513 weekly Brier against .182047 raw, but targeted defensive deletion remains stronger at .169803. Cluster-balanced Elastic Net with rotation has .164496 Brier and .009499 CRPS, a joint point improvement over V6's CRPS system with tradeoffs against V7's Brier leader. Covariance penalties and generic hierarchical scaling are worse. Within-fold clustering cannot isolate which historical constituents created overlapping exposures. The observed designs also share NIFTY benchmark subtraction. Distinct sector residuals can carry information, as tested directly in the rotation wave, but generic unsupervised factor separation alone was weaker. {small}
''')
    rot=['B_NATIVE','B_ROT','R_BANK','R_DEF','R_LEVEL','R_LEVEL_CHANGE','R_RESIDUAL','R_NORMAL','R_SLOPE','R_ACCEL','R_SWITCH','R_EXTREME','R_INTERACT','R_LAG1','R_LAG5','R_LAG10','R_SMOOTH','R_WRAP']
    write_report('DOMESTIC_ROTATION_MECHANISMS',f'''
The smallest successful incremental feature is the five-session **change in the difference** between Bank Nifty and Financial Services five-session returns. It gives .161633 Brier by itself, versus .169803 for the same native base, .170473 for the defensive change by itself, and .162294 for the two raw differences together. The baseline still contains 51 native inputs, so “one feature” describes the addition rather than a single-input forecasting system. Defensive spread uses mean pharma and FMCG returns minus mean auto, metals and energy returns. The combined residual specification removes common market exposure using a trailing 63-session spread-on-NIFTY beta lagged one session before differencing. This gives the lowest unperturbed weekly Brier, **.159504**. It is a predictive residualization exercise. No constituent-level bank exposures or causal rotation mechanism were identified.

{scores(rot)}

{gains(rot)}

Levels alone are weaker than changes. Slope, scale normalization, acceleration, sign-crossing and extreme-event variants do not consistently beat the residualized result. Five-session-lagged raw changes still give .162741 Brier. Ten-session lag reaches .166941. Wrapping the fit-only rotation fields gives .176970, worse than genuine alignment. Delaying the residualized lead itself by five sessions gives .166000 and shrinking its window to 189 fits gives .223071. These contrasts support both short-run information and regime persistence as plausible explanations.

{slices(['R_RESIDUAL'],['historical_volatility_regime','trend_sign','market_breadth','financial_strength','defensive_leadership','global_strength','reversal_realized'])}

The reversal slice conditions on what actually happened, which cannot serve as a decision-time filter. Conditional tables report counts, disjoint counts and leave-month ranges as descriptive uncertainty. They do not furnish independent confidence intervals on thin strata.

{comparison(['R_BANK','R_RESIDUAL','R_LEVEL_CHANGE','B_ROT'])}

{small}
''')
    struct=['B_ROT','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','A_PARTICIPATION','A_RISK_STRUCTURE','A_NATIVE_PANEL','W_STRUCT_EMBARGO','W_STRUCT_WINDOW','W_STRUCT_LAG','W_STRUCT_PERTURB','W_STRUCT_TARGET_NULL']
    write_report('MARKET_STRUCTURE_DISCOVERY',f'''
The level block contains seven economically interpretable summaries: financial momentum relative to NIFTY, dispersion across cyclical and defensive sectors, NIFTY 500 leadership, relative sector volatility dispersion, sector correlation, concentration and rank-rotation speed. The changes treatment adds their five-session differences alongside the same levels. The breadth treatment uses participation trend, broad-index momentum and rank persistence. The risk structure treatment uses cross-sector downside variance, persistence/transition in correlation and change in implied risk relative to realized volatility. All are trailing transforms on authentic native index histories. Index participation remains a sector-index proxy for dispersion across traded names.

{scores(struct)}

{gains(struct)}

Levels reach **.161756 Brier and .009587 CRPS**, both improving V7's best point benchmarks across their different scores. Adding the corresponding differences lowers **CRPS to .009472** and raises Brier slightly to **.162875**. An adaptive earlier-cutoff stress fit reaches **.009453 CRPS**. Scaling deviations in the grouped inputs gives .009421 in a synthetic query perturbation. That is a sensitivity experiment, excluded from candidate selection. A 189-observation window yields .010671, a five-session lag .009833, and block-permuted targets .014678. The paired effects support investigating the few interpretable inputs further, with time and cohort dependence preserved.

{sensitivity(['A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','W_STRUCT_EMBARGO'])}

{comparison(['A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','W_STRUCT_EMBARGO'])}
''')
    distribution=['B_ROT','G_ROT_ELASTIC','D_STUDENT','D_RISK','D_FACTOR','D_QUANTILE','D_ELASTIC_RISK','J_EQUAL','J_LEARNED','J_ADJUSTED','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','W_STRUCT_EMBARGO']
    frontier=['J_GRID0','J_GRID1','J_GRID2','J_GRID3','J_GRID4']
    gate=pd.DataFrame([r for r in read('integration-ledger.json') if r['split']=='primary'])
    write_report('JOINT_PROBABILITY_DISTRIBUTION',f'''
All complete forecasts use one finite return law. Up probability, median, expected endpoint price, ordered quantiles, tail probabilities and bucket masses are computed from its atoms and weights. The empirical reference uses conditional residuals with 35% historical shrinkage. Alternatives include Student df5 with shrunk residual scale, heavier weight on validation residuals in the same volatility or rotation-magnitude state, and regularized five-quantile interpolation with bounded tails. The latter limitation matters for very rare outcomes. Interval coverage is a separate diagnostic from endpoint tail mass, and neither estimates time-to-barrier or intra-period drawdown.

{scores(distribution)}

{scores(frontier)}

The grid shows the full predeclared five-point tradeoff between a cluster-balanced Elastic parent and a domestic rotation Ridge parent. A weight of zero means all Elastic. The learned mixture uses up to 84 resolved past forecast origins. A purged earlier partition fits regularized weights and score preferences, then uses an 18-origin trailing calibration gate. A sign tilt and return spread adjustment are disabled in folds where the gate fails to improve the combined losses or worsens nominal-80 coverage calibration. The first integration pass preserved all outer cutoffs but omitted purging inside this calibration gate. It is archived, then replaced in the comparative analyses by the stricter refit. The corrected adjustment still scores worse on the pooled weekly cohort than the raw learned mixture. Consequently calibration is retained as a failed improvement here. The earlier-cutoff structure model and the direct structure levels model show the most interesting proper-score tradeoff without forced calibration.

{table(gate,['horizon','fold','weight','tilt','spread','enabled','n_early','n_gate','gate_first_origin','calibration_fit_last_endpoint'])}

{slices(['A_STRUCTURE_CHANGE','R_RESIDUAL'],['historical_volatility_regime'])}

`metrics.json` records probability-bin calibration, central coverage, sharpness, quantile loss and bucket scores. `all-predictions.csv` carries both endpoint tails, absolute return and the per-origin 5/10/25/50/75/90/95 quantiles. {small}
''')
    intra=read('intraday-reconciliation.json');ln=['B_ROT','T_DAY_ETF','A_ETF_ACTIVITY','A_ETF_EXPOSURE','A_ETF_GATE','A_INTRADAY_BASE','A_INTRADAY','A_INTRADAY_STRICT_BASE','A_INTRADAY_STRICT','A_POSITION']
    write_report('ETF_LIQUIDITY_INTRADAY',f'''
Turnover is close times traded ETF volume, normalized by its own lagged 21-session median. We test turnover, changes in abnormal volume, participation across five ETFs, NIFTYBEES versus its underlying return, ETF volatility and absolute-return-over-turnover price impact proxies. The interaction tests abnormal activity during strong normalized rotation. Lagged archive futures basis, OI changes and options concentrations provide a separate derivatives test. No native spot index volume is inferred.

{scores(ln)}

{gains(ln)}

The ETF activity increment improves CRPS slightly versus rotation but worsens Brier. Adding tracked-price exposures and activity interactions produces no decisive further gain. Leading results for intrinsic daily ETF state remain sensitive to the presence of the rotation parent. The new complete-session intraday reconstruction uses **{intra['received_bars']:,}** archived 25-minute Upstox candles, with exact IST regular-session grids and OHLC checks. **{intra['full_regular_sessions']}** aligned sessions pass, and **{len(intra['excluded_sessions'])}** observed nonregular or invalid sessions are excluded. Opening and closing features span 50 minutes each given bar resolution. The last intraday close differs from the frozen daily underlying close by **{intra['median_abs_close_difference']:.2f}** points at the median and **{intra['max_abs_close_difference']:.2f}** points at the maximum. **{intra['over_10bp']}** sessions exceed 10 basis points. Late range share, conditional downside variation, realized volatility and reversal use the intraday path with the daily reference kept separately. The discrepancy could include closing index calculation conventions or provider differences. No replacement daily label is justified. Intraday loses on both scores on the 91-origin complete-session subset and the stricter 89-origin reconciliation subset. [Upstox historical candle documentation](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [NSE archive reports](https://www.nseindia.com/all-reports)

{slices(['A_ETF_ACTIVITY','A_INTRADAY'],['historical_volatility_regime','rotation_intensity','recent_large_index_move','market_breadth','global_strength'])}
''')
    gi=pd.read_csv(OUT/'global-intermediate-predictions.csv');gg=gi[gi.split=='primary'].copy()
    gtable=gg.groupby(['horizon','target','method'],as_index=False).error.agg(n='size',MAE='mean');grows=['G_MATCH5','G_DIRECT5','G_MEDIATE5','G_CONDITIONAL5'];gm=['G_MATCH21','G_DIRECT21','G_MEDIATE21','G_CONDITIONAL21']
    write_report('GLOBAL_CONDITIONAL_SIGNALS',f'''
V8 acquired actual NASDAQ Composite close observations and constant-maturity US ten-year Treasury yields, rather than relying on the earlier technology CFD proxy for the direct hypothesis. FRED also provided the CBOE VIX close series. The acquisition captured 471 Nasdaq, 469 yield and 485 VIX observations in the allowed data window. All new foreign completion times were reconstructed conservatively with two US business days plus a 23:00 New York time buffer. The stored archive receipt times do not establish the original historical provider receipt timestamps. Inherited dated Upstox FX, oil and Asian cash-market features retain their configured conservative as-of rules. [Nasdaq via FRED](https://fred.stlouisfed.org/series/NASDAQCOM) · [Federal Reserve H.15 yields](https://fred.stlouisfed.org/series/DGS10) · [CBOE VIX via FRED](https://fred.stlouisfed.org/series/VIXCLS)

The intermediate designs test Nasdaq to Indian IT relative returns, global VIX to sector synchronization, Brent/USDINR to defensive-cyclical returns, US yields to Indian Financial Services relative returns, and Asian dispersion to future Indian participation. Each intermediate compares own-state Ridge against the same own-state inputs plus the specified foreign information. The downstream tests use maturity-matched own-state, direct fields, prequential corrections and corrections interacted with weak participation. Each prequential correction uses a refit before its own origin.

{table(gtable,['horizon','target','method','n','MAE'])}

{scores(grows)}

{scores(gm,21)}

{gains(grows)}

All five overall intermediate MAEs weaken at both horizons. Weekly mediated Brier improves a little versus its short-history counterpart while CRPS worsens, and both remain materially behind full-history domestic rotation. Four July monthly downstream fits were unestimated under the inner maturity requirement. The monthly 53-origin group must be read on its own matched dates. Conditional effects on high risk and weak breadth are preserved below and in the auxiliary per-origin files, with too few independent regime windows for causal transmission conclusions.

{slices(['G_MEDIATE5','G_CONDITIONAL5'],['historical_volatility_regime','market_breadth','global_strength'])}
''')
    mn=['V6_MONTH_STATE','V6_MONTH_LAG1','V7_M_STATE_LAG21','V7_M_STATE_SHIFT5','V7_M_STATE_SHIFT21','M_HIST','M_PRICE','M_ONLY_STATE','M_BOTH','M_LAG_STATE','M_LAG_PRICE','M_ROLL_STATE','M_BLOCK_TARGET','M_STATE_SMOOTH','M_INNOVATION','M_PERSIST','M_REVERT','M_CONTINUE','M_LAG_RETURN','MS_STATE_ONLY','MS_LAG5','MS_LAG21','MS_WINDOW','MS_ROLL','MS_PERMUTE','MS_EMBARGO','MS_MATCH_PRICE','MS_MATCH_NOW','MS_MATCH_LAG5','MS_MATCH_LAG21','MS_MATCH_ROLL']
    write_report('MONTHLY_PERSISTENCE_AND_FALSIFICATION',f'''
V8 finds a lower historical monthly point score after averaging each reconstructed weekly forecast state over its prior 21 sessions. With current price and risk inputs `M_STATE_SMOOTH` reaches **.136132 Brier**, **.021511 CRPS** and **78.95%** nominal-80 coverage. A 126-date fit variant improves those point losses to **.132367 and .020474** with **85.53%** coverage. They lie on a sample with four disjoint windows. The ordinary price-plus-current-weekly-state fit scores **.249270** Brier, state without price **.222769**, a 21-session lagged raw state plus current price **.171065**, and price only **.404564**. The simple price persistence, reversion and historical-frequency controls expose how much the state result depends on the regime and training eligibility dates.

{scores(mn,21)}

The smoothed-state timing mechanism fails scrutiny. A fit-only 21-session circular roll of the smoothed inputs gives **.108239 Brier** on the same 76 origins, although CRPS worsens to .024107. On the stricter 53-origin common availability cohort, the smoothed current model scores **.132208 Brier and .027468 CRPS** and the shifted-state placebo reaches **.080609 and .026153**. Genuine 21-session delayed smoothed states give **.336433** Brier there. Five-session delayed smoothed states hold up better. Unsurprisingly, older signals and altered dates can preserve broad persistent conditions. The circular controls wrap only allowed historical fitting rows and are labeled diagnostics. The target-block permutations disturb alignment without flattening all serial structure. They do not supply independent probability intervals. July on the stricter availability cohort and one earlier-cutoff smoothed fold did not fit under the inner sample requirement. V7's .024530 monthly CRPS remains a historical comparison; several new point estimates improve it, yet shifted controls and starting-date sensitivity still undermine independent conclusions.

{comparison(['M_STATE_SMOOTH','MS_WINDOW','MS_ROLL','MS_MATCH_NOW','MS_MATCH_ROLL'],21)}

{sensitivity(['M_STATE_SMOOTH','MS_WINDOW','MS_MATCH_NOW'],21)}

No monthly superiority claim follows from four disjoint windows. The 10- and 15-session diagnostics use the same monthly origin cohort and retain their own targets and empirical benchmarks. Shorter horizon gains do not replace the primary definitions. [Monthly persistence figure](monthly-persistence-falsification.png)
''')
    write_report('CROSS_SECTIONAL_RESEARCH',f'''
The date-level sector panel uses nine native NSE indices. NIFTY-conditional residuals remove a trailing 63-session sector market beta, used with one-session lag. Four aggregates capture common five-session return, residual return and residual dispersion across the nine sectors, and mean sector volatility. One observation per date enters the NIFTY target fit. The underlying panel contains repeated market dates and shared prices, so cross-sectional observations do not increase the count of independent NIFTY outcomes. A separate current-selected stock-basket proxy tests historical observed participation, volume and dispersion while retaining the selection/survivorship limitation. It is a diagnostic rather than a broad-market membership history.

{scores(['B_ROT','A_NATIVE_PANEL','A_STOCK_PROXY','A_PARTICIPATION'])}

{scores(['B_ROT','A_NATIVE_PANEL','A_STOCK_PROXY','A_PARTICIPATION'],21)}

{gains(['A_NATIVE_PANEL','A_STOCK_PROXY','A_PARTICIPATION'])}

The native residual panel reduces weekly Brier from .162294 to .160086 with similar CRPS. Matching dates shows a modest candidate increment. The monthly panel does not improve the stronger persistence controls. The current-selected stock proxy worsens both weekly rotation scores; original membership listings and historical weights remain necessary to interpret that family beyond sensitivity. Findings favor a compact native panel representation over pooling current constituent rows as labels.
''')
    early=['E_HIST','E_SMALL','E_ROT','E_SMALL_126','E_ROT_126','E_FULL_ROT'];inter=['K_HIST','K_BASE','K_ROT','K_STRUCTURE']
    o=preds.groupby(['cohort','horizon'],as_index=False).agg(origins=('origin','nunique'),first=('origin','min'),last=('origin','max'),last_endpoint=('endpoint','max'))
    write_report('HISTORICAL_COVERAGE_AND_SENSITIVITY',f'''
We reconstructed earlier V3-exposed origins with low-dimensional price/rotation designs, a fixed 85-date mature training minimum, 40-date purged fitting minimum, and 28-date residual validation. The simpler models use Ridge150. The rolling version caps both eligible fitting histories at 126. A full native rotation configuration and historical return law share the same earlier dates. The endpoint embargo conditions were unchanged. We retained the same earlier design at both horizons regardless of results. This adds 173 weekly and 141 monthly research origins, separated from the later 92/76 origin cohorts. These earlier dates are exposed research history.

{table(o,['cohort','horizon','origins','first','last','last_endpoint'])}

{scores(early,5,'early')}

{scores(early,21,'early')}

The earlier weekly historical law beats the full native rotation system by **.040089 Brier** and **.002365 CRPS**. The compact rotation addition barely improves its own expanding-window earlier control. At 21 sessions, the compact 126-date models improve earlier Brier over the historical law while delivering worse CRPS. The prominence of rotation in the later cohort therefore does not carry across these earlier dates. Training horizon and regime differ. This is evidence against robustness across design/cohort, with no universal explanation identified.

{scores(inter,10,'diagnostic')}

{scores(inter,15,'diagnostic')}

On the same 76 origins, the 10-session structure change improves CRPS versus the 10-session historical law, .010475 versus .011598. At 15 sessions it scores .018849, worse than the horizon-local historical .017622. These are dependence-limited diagnostic cohorts rather than a horizon selection rule. Important shorter-window fail cases for the weekly lead and extra-cutoff fits are preserved in `stress-results.csv` and `fit-attempts.csv`.
''')
    total_cells=len(preds.groupby(['cohort','horizon','model']));failure=[z for z in registry['fold_attempts'] if z['status'] in ['failed','unestimated']]
    refit=read('prior-verification.json');reg_count=len(registry['configurations']);rec_count=len(registry['fold_attempts']);weekly=['R_RESIDUAL','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','W_STRUCT_EMBARGO','G_ROT_ELASTIC']
    write_report('VALIDATION_AND_SEARCH_RISK',f'''
Every parent comparison joins on origin and validates the exact endpoint and realized return. The inner and outer fits require labels ending strictly before their respective fit anchors. The original training-only transformations apply separately to both partitions. Extra cutoff variants place the maturity boundary three observed sessions earlier. The source hash checks cover protected prior data, official reconciliation evidence, input CSVs and fitted model objects. Forecasts derived from historical reconstructions have the associated historical-release assumptions rather than authenticated original release receipts.

V8 registered **{reg_count} named configurations**, **{rec_count} fold or calibration attempts**, **{total_cells} fitted model/horizon/cohort cells**, **{len(preds):,} saved per-origin outputs**, and **{len(comp):,} matched reference contrasts**. The exact duplication tests, target permutations, sector revisions and query perturbations remain diagnostics. Rotation/structure stress and smoothed-state follow-ups were motivated by exposed V8 results, with their registrations retained before fitting. The first calibration pass lacked the inner gate purge and is archived separately. Only the corrected output enters the comparison. Original and matched-date later attempts remain traceable. The verified protected-file count is **{refit['files']:,}**, including the protected V4 ledger and issued snapshots.

The weekly simultaneous family covers **{unc['weekly_family']:,}** contrasts using **2,000** shared chronological circular origin-block draws and max standardized statistics. Block lengths 5, 10 and 15 test dependence assumptions, with raw percentile intervals separate from adjusted ranges. Some narrower cohorts are missing on certain dates; each paired score uses the same dates and the resampling preserves that calendar. This is an approximate within-V8 search adjustment. It does not cover all prior adaptive decisions, every slice, or repeated discovery over V1–V8. No monthly precision interval is reported. {small}

{comparison(weekly)}

{sensitivity(weekly)}

{table(failure,['batch','horizon','fold','model','status','error','reason'])}

Synthetic low-amplitude source revisions, coherent grouped query perturbations, fitting-window and alpha changes, sector lag tests, earlier label cutoffs, exact copies and randomized target blocks are recorded separately. The actual prior provider vintage audit found matching archived native closes where overlap was checked. That says nothing about unseen vendor revisions. The negative controls worsen weekly point results materially and remain unexpectedly competitive monthly. Their dependence is part of the reason the monthly outcome is inconclusive. See `verification.json` for exact replay evidence.
''')
    m=pd.read_csv(OUT/'direction-leaderboard.csv');write('fit-attempts.csv',pd.DataFrame(registry['fold_attempts']).drop(columns=['metadata','historical_origins'],errors='ignore'))
    write_report('COMPLETE_COMPARISON',f'''
Separate weekly probability and distribution leaderboards use Brier and CRPS. `direction-leaderboard.csv` and `distribution-leaderboard.csv` carry the complete rankings with classification, horizon, model family, parent, counts, disjoint count, return-ACF ESS, accuracy, balanced accuracy, log loss, Brier, CRPS, mean and median errors, quantile loss, coverage, interval width, adjusted paired differences and leave-month gains. All benchmark-pair differences and every parent increment are separate files. Diagnostic controls stay visible, including results with similar or lower point scores. Monthly comparisons include the frozen V7 lagged-state and shifted-state controls. A model estimated on 53 dates is compared to the corresponding dates of each benchmark. Earlier and intermediate cohorts are published separately in `other-cohorts.csv`.

## Weekly probability order

{table(m[m.horizon==5].sort_values('brier'),['model','classification','n','disjoint','ESS_return_ACF','accuracy','balanced_accuracy','brier','log_loss','crps','coverage80','width80','leave_month_min_Brier_gain','leave_month_max_Brier_gain'])}

## Monthly distribution order

{table(m[m.horizon==21].sort_values('crps'),['model','classification','n','disjoint','ESS_return_ACF','accuracy','balanced_accuracy','brier','log_loss','crps','coverage80','width80'])}

{small}
''')
    write_report('SIGNAL_DISCOVERIES',f'''
1. Exact duplicate removal gives provable prediction stability under the tested alias designs. This is a representation result with synthetic interventions, independent of any new forecasting score target. Generic reweighting alone can change forecasts even when all aliases enter the same broad feature family.
2. Bank-versus-financial-services momentum change explains more of the V7 directional gain than the defensive change in the simple matched test. Residualizing the spreads gives the best unperturbed weekly probability point score. Weak early-cohort generalization and stronger current-than-lagged residual performance are both part of the evidence.
3. Market-state changes improve CRPS over the otherwise identical state levels. The level-only model improves both historical prior lead scores marginally. Cluster-balanced Elastic Net with rotation also gives a valuable distribution tradeoff. The earlier-cutoff CRPS leader is a follow-up sensitivity rather than a standalone new independent discovery.
4. Native panel residuals add a modest direction increment. ETF activity contributes a small distribution increment with weaker Brier. Complete-session intraday and tighter close reconciliation fail to establish incremental weekly scores. Targeted foreign intermediates mostly worsen, including authenticated Nasdaq and yield paths.
5. Smoothed weekly forecast states improve some monthly historical metrics, but placebo alignment and strict common readiness weaken the timing explanation. The results support persistence as a plausible alternative mechanism, with too few disjoint monthly targets to conclude.

{gains(['R_BANK','R_DEF','R_RESIDUAL','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','G_ROT_ELASTIC','A_ETF_ACTIVITY','A_INTRADAY','A_NATIVE_PANEL','G_MEDIATE5'])}

The ranking above describes the strength and interpretation of controlled incremental comparisons. Whole-system Brier and CRPS ranks are separate.
''')
    write_report('FINAL_RESEARCH_CONCLUSIONS',f'''
V8 establishes exact duplicate invariance in the tested fitted laws. It improves selected historical weekly point scores. It does not establish independent forecasting superiority. Residualized domestic rotation gives an unperturbed **.159504 Brier** versus V7 **.162145**. The stronger early-cutoff structure-change law gives **.009453 CRPS** versus **.009665** in V7, with **.009472** as the first-stage structure-change result. The level-only state law gives **.161756 Brier and .009587 CRPS**, point improvements against both distinct prior leader scores, but small enough that neither provides confirmatory evidence. The synthetic perturbation rows are deliberately separate from practical candidate selection.

{scores(['T_ROT_DOMESTIC','T_ELASTIC_EMBARGO','R_RESIDUAL','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','W_STRUCT_EMBARGO','G_ROT_ELASTIC'])}

{comparison(weekly)}

Two constraints determine the research decision. Earlier-weekly rotation scores lose to a simple historical law, so the later lead has not shown chronological transfer. And monthly smoothed-state controls score comparably or better after deliberate misalignment, so the timing story lacks falsification support. Even the best monthly CRPS .020474 and nominal calibration at 85.53% are historical point estimates based on four disjoint outcomes. Keep the unperturbed weekly residual rotation, structural levels/change, and cluster-balanced rotation laws as distinct hypotheses. Keep the month model in falsification research. {small}

[Weekly proper-score tradeoff figure](weekly-proper-score-tradeoff.png)
''')
    write_report('NEXT_EXPERIMENTS',f'''
Freeze V7 leaders and the few original V8 rotation and structure laws before any genuinely new historical evaluation arrives. Prespecify whether Brier or CRPS is primary per experiment. Include the next disjoint-origin count, how gaps and special market sessions will be handled, and how actually received payloads will be recorded. Keep any future experimental issuance in its own version with an actual timestamp. The current run contains historical reconstruction only.

For duplicate handling, test separately the risk that near-duplicates diverge after training. For domestic rotation, retain the simple bank-change treatment, residualized spreads and price/breadth control as a small sequence. The shorter training-window losses and the earlier exposure cohort provide useful fixed failure checks. Expand only if those replication comparisons give more stable gains than another group of variants.

For return laws, compare the static structural state levels, their changes, and the cluster-balanced rotation law with one fixed calibration method and a purged predeclared gate. Archive the intermediate forecast distributions and timestamps. Use the same empirical control when testing interval width, coverage and tail scores.

For additional information, prioritize timestamp and price-reference quality before expanding intraday variants. The Nasdaq and yield intermediates can be retired for this particular delay/model scheme on current evidence. Historical constituent weights would enable a direct test of exposure redundancy distinct from co-movement on the native factor panel. The monthly tests should retain simple frequency/persistence and alignment controls, keep fewer model choices, and seek more genuinely disjoint outcomes before estimating statistical precision.
''')
    save('report-manifest.json',{name:sha(OUT/name) for name in names})
    if OUT==DEFAULT:
        relative=OUT.relative_to(ROOT).as_posix()
        lines=['# NIFTY V8 research','','2025–2026 exposed history. V8 tested exact-copy invariance, sector rotation and coherent endpoint laws.',
               '', 'Weekly best unperturbed Brier **.159504**. Best weekly candidate CRPS **.009453** in a later cutoff test. Adjusted gain intervals include zero. Monthly smoothed-state gains remain inconclusive after shifted-state controls.', '']
        lines.extend(f'- [{name[3:-3].replace("_"," ").title()}]({relative}/{name})' for name in names)
        lines+=['',f'[Probability leaderboard]({relative}/direction-leaderboard.csv) · [Distribution leaderboard]({relative}/distribution-leaderboard.csv) · [Predictions]({relative}/all-predictions.csv) · [Verification]({relative}/verification.json) · [Reproduction](research/nifty_forecast_v8/README.md)',
                '',f'[Weekly figure]({relative}/weekly-proper-score-tradeoff.png) · [Monthly falsification figure]({relative}/monthly-persistence-falsification.png)','']
        (ROOT/'NIFTY_V8_RESEARCH.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Wrote',len(names),'V8 reports',flush=True)


if __name__=='__main__':run()
