"""Generate all requested V9 reports from frozen results."""
from .common import *


def table(data, columns):
    if isinstance(data,pd.DataFrame):data=data.to_dict('records')
    def cell(value):
        if value is None or isinstance(value,float) and np.isnan(value):return '—'
        if isinstance(value,(float,np.floating)):return f'{value:.6f}'
        if isinstance(value,list):return '['+', '.join(cell(x) for x in value)+']'
        return str(value).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']+
                     ['| '+' | '.join(cell(r.get(k)) for k in columns)+' |' for r in data])+'\n'


def run():
    metrics=pd.DataFrame(read('metrics.json'));cmp=pd.DataFrame(read('benchmark-comparisons.json'));reg=read('experiment-registry.json')
    inc=pd.read_csv(OUT/'parent-increments.csv');stress=pd.read_csv(OUT/'stability.csv');slices=pd.read_csv(OUT/'conditional-calibration.csv');preds=pd.read_csv(OUT/'all-predictions.csv')
    combined=pd.read_csv(OUT/'combined-cohort-leaderboard.csv');pareto=pd.read_csv(OUT/'temporal-pareto.csv');comb_int=read('combined-weekly-uncertainty.json')
    uncertainty=read('uncertainty.json');prior=read('reproduction.json');state=read('temporal-diagnostics.json');names=[]
    caption='Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.'
    fullcols=['model','n','disjoint','ESS','accuracy','balanced_accuracy','brier','log_loss','crps','mae','rmse','pinball','coverage50','coverage80','width80']
    common=['P_HIST','P_NATIVE','P_ROT','P_STRUCTURE','P_CLUSTER','P_LIQ','P_REVERT','P_MOMENTUM','P_COMPACT']
    adaptive=['T_EW90','T_EW45','T_KALMAN','T_KALMAN_SLOW','T_STATIC_BLEND','T_CHANGE_WINDOW','T_RECENT126','T_EXPERT_PARENT','T_VOL_EXPERT','T_TREND_EXPERT','T_BREADTH_EXPERT']
    mixer=['J9_EQUAL','J9_STATIC','J9_PERFORMANCE','J9_DOMESTIC_GATE','J9_GLOBAL_GATE','J9_OOD','J9_REGIME','J9_REL_SHRINK']
    def write_report(name,text):
        path=f'V9_{name}.md';names.append(path)
        (OUT/path).write_text(f'# NIFTY V9 · {name.replace("_"," ").title()}\n\nRun `2026-11-24/run-001`. Historical research using 2025–2026 observations.\n\n'+text.strip()+'\n\n'+caption+'\n',encoding='utf-8')
    def scores(ids,h=5,c='later'):
        m=metrics[(metrics.cohort==c)&(metrics.horizon==h)];z=m[m.model.isin(ids)].set_index('model').reindex(ids).dropna(subset=['n']).reset_index()
        return table(z,fullcols)
    def gains(ids,h=5,c='later'):
        return table(inc[inc.model.isin(ids)&(inc.horizon==h)&(inc.cohort==c)&inc.metric.isin(['brier','crps'])],['model','parent','metric','n','gain'])
    def conditional(ids,conditions,h=5,c='later'):
        return table(slices[slices.model.isin(ids)&slices['slice'].isin(conditions)&(slices.horizon==h)&(slices.cohort==c)],
               ['model','parent','slice','state','n','disjoint','Brier_gain','CRPS_gain','coverage80','width80'])
    def matched(ids,h=5,c='later',bases=('P_HIST','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO')):
        return table(cmp[cmp.model.isin(ids)&cmp.baseline.isin(bases)&(cmp.cohort==c)&(cmp.horizon==h)&cmp.metric.isin(['brier','crps'])],
                     ['model','baseline','metric','n','gain','adjusted95_block10'])
    def stability(ids,h=5,c='later'):
        v=stress[stress.model.isin(ids)&(stress.horizon==h)&(stress.cohort==c)&(stress.baseline=='P_HIST')]
        t=v.groupby(['model','metric','test'],as_index=False).gain.agg(minimum='min',maximum='max',positive=lambda x:f'{sum(x>0)}/{len(x)}')
        return table(t,['model','metric','test','minimum','maximum','positive'])
    def composite(ids,h=5):
        return table(combined[(combined.horizon==h)&combined.model.isin(ids)],['model','n','disjoint','brier','crps','early_Brier','late_Brier','early_CRPS','late_CRPS','abs_Brier_cohort_gap'])
    curves=pd.read_csv(OUT/'learning-curves.csv');like=pd.read_csv(OUT/'learning-common-dates.csv');gap=pd.read_csv(OUT/'gap-decomposition.csv')
    match=pd.read_csv(OUT/'market-state-matches.csv');near=match[match.within_caliper];profile=pd.read_csv(OUT/'cohort-market-profile.csv')
    old_v8=['T_ROT_DOMESTIC','T_ELASTIC_EMBARGO','V8_R_RESIDUAL','V8_A_STRUCTURE_LEVEL','V8_A_STRUCTURE_CHANGE','V8_W_STRUCT_EMBARGO','V8_G_ROT_ELASTIC']
    beta=pd.read_csv(OUT/'base-coefficients.csv');k=beta[(beta.horizon==5)&(beta.model=='P_ROT')&beta.feature.isin(['r_bank_residual','r_def_residual'])]
    write_report('TEMPORAL_GENERALIZATION_DIAGNOSIS',f'''
V9 first independently refit **{prior['v8_rows']:,}** V8 rows covering winners, earlier cohorts, monthly smoothed and shifted states, window stress, ETF/intraday increments and global corrections. It refit **{prior['older_weekly_rows']}** additional protected weekly reference rows using their original designs. Most were numerically identical and the maximum V8 score difference was {prior['max_abs_error']:.3g}. V8 source, all 17 reports, data definitions, saved law outputs, fitted artifacts and registries are inventoried. The November 17 vintage stays frozen.

{scores(old_v8)}

## What equalizing training length changes

The raw rotation model uses the same feature set, alpha and strictly matured labels across the two cohorts. At 85 training observations its Brier is **{curves.query('cohort=="early" and model=="L_ROT_85"').brier.iloc[0]:.6f} earlier and {curves.query('cohort=="later" and model=="L_ROT_85"').brier.iloc[0]:.6f} later**. Expanding fits favor the later cohort. Holding both to 85 observations reverses that ranking. Separately, the historical baseline has a Brier gap of about .00115 across cohorts, so a large rotation gap is not explained by a comparable change in unconditional direction loss. The algebra below sums exactly to the observed expanding-model gap. The middle term still mixes time, unmeasured conditions and changes in training composition. It is not a causal estimate of market regime effects.

{table(gap,list(gap.columns))}

{table(curves[curves.model.str.startswith('L_ROT')],['cohort','model','n','training_min','training_max','inner_min','inner_max','brier','crps','brier_gain','crps_gain'])}

{table(like[(like.family=='ROT')&like.largest_eligible_length.isin([126,189,300])],['cohort','largest_eligible_length','model','n','disjoint','brier','crps'])}

The 85, 126, 189, 252 and 300 lengths cap the final fit. The purged inner sample may be smaller because the common 28-observation residual partition is held separate. We report exact training and inner sizes rather than calling them identical. Some earlier cutoffs cannot reach 300. The 92 later dates support the full comparison. Using all later history materially outperforms 85 or 189 dates, while 300 dates approach the expanding score. The pattern is nonmonotone and depends on which training eras remain in the fit. [Matched learning curve](matched-learning-curves.png)

## Same data and different residual-estimation design

{table(curves[curves.model.str.startswith('L_DESIGN')],['cohort','model','n','brier','crps','brier_gain','crps_gain'])}

Changing residual validation from 28 to 42 dates improves earlier expanding Brier, but it still loses to historical. Changing Ridge alpha affects both cohorts. V9 leaves warm-up, missingness and maturity rules fixed within the controlled comparisons. The primary V9 parent uses 28 origins for a common earlier/later fit. Comparisons against V8’s protected 42-origin fits remain matched by target and date with this design difference explicit.

## State matches and parameter drift

{table(profile,['cohort','feature','n','mean','std'])}

The one-to-one state-matching exercise finds **{len(near)}** pairs within the predeclared distance cap out of {len(match)} potential matches. Among these, 85-observation Brier is **{near.early_brier.mean():.6f} earlier and {near.later_brier.mean():.6f} later**. Relative loss to the historical baseline is **{near.early_relative_brier.mean():.6f}** and **{near.later_relative_brier.mean():.6f}**. The early normalization and concurrent state similarity do not remove other time-varying differences. The limited matched conditions do not identify a market cause.

{table(k,['cohort','fold','cutoff','feature','coefficient'])}

The largest retrospective CUSUM deviation occurs at **{state['retrospective_max_abs_CUSUM']}**. That date uses all observed losses and is for diagnosis. `online-and-retrospective-breaks.csv` separately tracks a feasible alarm based on the latest 21 resolved losses against the preceding up-to-42 losses, plus rolling matured bank-residual/error correlation. It does not feed the ex-post CUSUM break back into historical forecasts. `base-coefficients.csv` preserves all per-cutoff coefficients and intercepts. Training support, changing conditional associations and experimental design all matter. The comparison cannot assign clean causal shares between them.
''')
    select=pd.read_csv(OUT/'selective-performance.csv');rel=pd.read_csv(OUT/'reliability-comparison.csv');gated=mixer
    write_report('PREDICTABILITY_DISCOVERY',f'''
V9 estimates the conditions under which an already issued historical reconstruction might be useful. The training outcomes are future Brier, CRPS, correct signs, central interval coverage and expert-vs-history loss differences, each computed from a prequential origin forecast and unseen until its endpoint matured. A reliability fit at a monthly anchor uses at most 126 prior resolved forecast origins and needs 35. This withholds assessment on the earliest windows. A separate origin-time recent-loss feature uses only labels ending strictly before that origin. Forecast probabilities and underlying financial conditions are archived with the assessment rows.

The domestic gate includes trend consistency, sector synchronization, breadth, concentration, banking/defensive leadership, volatility level/change, turnover, prior resolved losses, predictive disagreement and distance from prior feature states. The global gate adds jointly available foreign variables. To select forecasts, the predicted gain must exceed its training-time 60th-percentile threshold. Bullish and bearish subgroups use the rotation forecast’s 0.5 sign threshold. The follow-up post-forecast coverage is computed on the exact selected dates.

{table(select,['cohort','horizon','selection','n','disjoint','coverage_of_cohort','accuracy','brier','crps','matched_history_Brier','matched_history_CRPS','interval80_coverage'])}

Later weekly selection takes **52 of 92** dates, with **75%** accuracy and **.168859 Brier** compared with **.253088** for historical on those dates. The abstained 40 later dates actually have **85%** accuracy and **.158225** Brier for the same rotation model. About 35.26% of the earlier cohort is selected, and earlier selected Brier **.289555** loses to its matched historical **.268564**. Later selected bearish cases look attractive at **87.5%** on 24 origins, but only six disjoint targets and an earlier bearish slice of 20 origins make this descriptive. The later monthly gate selected only six origins and got zero directions right. Selective forecasting therefore failed as a generally reliable filter. Historical date-conditioned uncertainty is preserved with each slice, and no small-slice win rate is interpreted independently.

{table(rel,list(rel.columns))}
''')
    write_report('ADAPTIVE_MODEL_RESEARCH',f'''
Time-varying models use the same compact domestic rotation inputs and prequential date calendar across both cohorts. Exponentially weighted Ridge uses fixed half-lives of 45 or 90 fitting observations and normalizes weights to preserve overall penalty scale. Regularized Kalman regression updates a small coefficient vector in matured same-horizon endpoint order. The process noise is fixed relative to training target variance, with a slower alternative. The historical calibration residuals are generated from a distinct purged inner fit. The threshold experts blend 40% of the applicable high/low volatility, trend or breadth expert with 60% pooled estimation. Training medians set thresholds. Short-window blending uses equal 126-date/expanding weights or chooses `.60` and `.15` on a predeclared causal feature-distribution threshold of `.75`. These are contemporaneous observed regimes. Hidden-state smoothing does not enter the experiment.

{scores(['P_HIST','P_COMPACT',*adaptive])}

{scores(['P_HIST','P_COMPACT',*adaptive],5,'early')}

The adaptive regressions did not automatically restore later performance. Compact representation itself is a different design from full native V8 and is explicitly controlled. The later native residual rotation and structure parents survive better than the compact dynamic alternatives. The earlier compact fits still tend to lose to the empirical benchmark. A true future regime-changing model remains unproven.

The expert layer uses seven complete law parents: native, residual rotation, structural changes, cluster-balanced Elastic Net, ETF activity, a simple reversion law and historical. `J9_EQUAL` is the equal-weight initial law and `J9_STATIC` then assigns half additional mass to history. Other options use recent strictly matured weighted losses, same-volatility past losses, regularized domestic/global reliability scores, or OOD shrinkage. Learned weights remain 60% equal and 40% soft estimates. Fall back to fixed weights below the fit threshold. See `expert-weights.csv` for every allocation.

{scores(gated)}

{scores(gated,5,'early')}

{composite(common+gated)}

The recent-performance combination improves combined Brier/CRPS versus equal weighting, and OOD/history blends reduce early losses for relatively modest later deterioration against equal weighting. The frozen later rotation benchmark remains better on the later sample. A simple fixed fallback is as competitive as more elaborate reliability weighting for combined CRPS. These comparisons favor keeping shrinkage as a control when evaluating adaptation rather than assuming learning helps.
''')
    fin=['F_BASE','F_BANK_LEVEL','F_BANK_CHANGE','F_BANK_RESID42','F_BANK_RESID63','F_BANK_RESID84','F_FINANCIAL_PERSISTENCE','F_FINANCIAL_PANEL','F_FINANCIAL_PANEL_NO_SIZE','F_FINANCIAL_TRADE','F_FINANCIAL_LAG','F_FINANCIAL_REDUCED','F_CLUSTER','F_REMOVAL']
    acq=read('acquisition.json');fin_obs=read('feature-manifest.json')['financial_observed']
    write_report('FINANCIAL_SECTOR_INTELLIGENCE',f'''
Financial-sector coverage now includes native Bank Nifty, Financial Services, PSU Bank and authenticated Private Bank. BANKBEES, PSU Bank BeES and FINIETF supply actual ETF observations, and SBI Life, HDFC Life, and ICICI Prudential Life cover three documented insurance equity proxies. They are individual instrument histories. Dated constituent weights and a complete historical insurance index input were unavailable. NIFTY 50 and NIFTY 500 provide distinct benchmarks. Sidecar sources have separate receipt, key and checksum records, and no pre-2025 data are loaded. [Upstox historical daily data](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)

{table([r for r in acq['requests'] if r['start']=='2025-01-01'],['name','key','rows','first','last','status'])}

The financial feature set separately measures the bank-minus-financial five-session momentum level, five-session change and acceleration, 21-session persistence, lagged beta adjustment at fixed 42/63/84 lookbacks, volatility-adjusted change, correlation change, rank change and dispersion. Private/PSU spreads and ETF tracking are richer additions. Every rolling beta is lagged one session. Removing the private/PSU spread and the entire native banking feature group supplies removal controls. The stronger-regularization financial variant keeps the canonical design and adds alpha170. The full feature count is {len(fin_obs)} and one-to-one inclusion counts are in the frozen feature manifest.

{scores(fin)}

{scores(fin,5,'early')}

{gains(fin)}

{conditional(['F_BANK_RESID63','F_FINANCIAL_PANEL'],['volatility_high','uptrend','financial_spread_positive'])}

The 42/63/84 choices are fixed adjacent residualization windows rather than an optimized parameter surface. No compact financial representation beats both historical early metrics and later full native rotation. In the later sample, eliminating banks from the full native features compromises some of the native improvement. Coupled with the matched raw-rotation training-size curve, this suggests financial information can be useful inside a trained representation without establishing a broadly transferable financial-only forecast. Fit, feature-lag and family removal conclusions all remain retrospective.
''')
    innov=['F_BASE','I_LEVEL','I_DELTA','I_AR','I_ROBUST','I_AR_NOGLOBAL']
    write_report('MARKET_INNOVATION_RESEARCH',f'''
The innovation panel comprises bank divergence and defensive rotation, ETF turnover, NIFTY trailing realized volatility, lagged NSE futures basis, sector breadth, and domestic return residual versus global equities. Levels, ordinary five-session changes, AR(1) innovations and robust deviations are compared on the same compact price and risk parent. The AR expectation uses a 42-session trailing regression with its coefficients shifted one day. Robust surprises subtract a prior median and divide by the prior IQR-scale, capped at ±8. The global/domestic relative residual similarly estimates its beta in advance. No market-wide release surprise feed enters this experiment.

{scores(innov)}

{scores(innov,5,'early')}

{scores(innov,21)}

{gains(innov)}

The residuals are statistical surprises, not a measure of publicly unpriced information. Innovation rankings vary with the evaluation period. The same level parents and plain-change parents make this a test of feature construction rather than a search over unrelated inputs. Dropping the global innovation makes one incremental comparison, and no variant independently establishes gain beyond full historical rotation. Read the regime and stability files alongside retrospective point estimates.
''')
    write_report('GLOBAL_CONDITIONAL_INTELLIGENCE',f'''
V9 treats foreign observations as five separate candidate roles: a direct directional contribution, cross-market residual and correlation change, a forecasting gate, a volatility predictor and a conditional residual weighting signal. Reused snapshots include V8 FRED Nasdaq Composite, US ten-year yield and VIX, and the V5 as-of Upstox global-equity, FX and oil series. FRED rows were made eligible after the V8 two-US-business-day plus 23:00 New York availability buffer. Inherited cash/futures availability rules remain documented. No same-day foreign closing information after a domestic decision is assumed. [NASDAQ Composite source](https://fred.stlouisfed.org/series/NASDAQCOM) · [Upstox historical data](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)

The direct block uses India-versus-global residual, rolling correlation change and global shock. `T_GLOBAL_LOCATION` holds fixed the predictors used by `T_GLOBAL_LAW`, differing only in residual-law weighting. `J9_GLOBAL_GATE` adds six foreign series and divergence/shock statistics to the identical domestic reliability gate. The global risk regression uses that same domestic-plus-global feature set against the actual future path RMS, with historical realized outcomes prior to the gate. These are predictive comparisons against domestic parents rather than evidence of foreign causality.

{scores(['P_COMPACT','T_GLOBAL_DIRECT','T_GLOBAL_LOCATION','T_GLOBAL_LAW','J9_DOMESTIC_GATE','J9_GLOBAL_GATE'])}

{scores(['P_COMPACT','T_GLOBAL_DIRECT','T_GLOBAL_LOCATION','T_GLOBAL_LAW','J9_DOMESTIC_GATE','J9_GLOBAL_GATE'],5,'early')}

{gains(['T_GLOBAL_DIRECT','T_GLOBAL_LOCATION','T_GLOBAL_LAW','J9_GLOBAL_GATE'])}

{table(rel,['cohort','horizon','assessed','dom_vol_mae','global_vol_mae'])}

The global gate gives a tiny combined weekly advantage relative to the domestic gate and marginally worsens later weekly Brier and CRPS. Earlier annualized volatility MAE improves from **.074563 to .066883** weekly and **.102450 to .096693** monthly, but later weekly/later monthly volatility MAE worsens. Those are matched prior-gate eligible date sets, and the later reversal in risk gains is a reason to preserve the global-risk hypothesis as conditional and exploratory. Global timing receipts were reconstructed from frozen archives, with newer completed domestic sessions scored in a separated cohort.
''')
    panel=['F_BASE','P_COMPACT','X_NATIVE_PANEL','X_ROT_PANEL','X_STOCK_PROXY']
    write_report('CROSS_SECTIONAL_STRUCTURE',f'''
The primary panel uses nine native sector index histories. Each daily sector return is residualized against NIFTY with a lagged 63-session beta. A date-level representation aggregates five-session residual mean, dispersion and breadth, cross-sector rank change, common risk and residual acceleration. The fit sees one row per NIFTY origin. `X_ROT_PANEL` isolates the added panel from the exact same compact rotation parent. The current-selected stock proxy uses up to **{read('feature-manifest.json')['stock_proxy_count']}** equities on a date and is a survivorship-exposed diagnostic. It is not authenticated historical membership. Individual ETF/insurance/banking coverage is audited independently.

{scores(panel)}

{scores(panel,5,'early')}

{scores(panel,21)}

{gains(panel)}

{conditional(['X_ROT_PANEL'],['volatility_high','broad_participation','concentrated'])}

Native residual aggregation can improve the compact counterpart in some slices, but neither a full panel head nor the stock proxy is a reliable improvement across horizons and cohorts. No stock-date or sector-date observation counts as a fresh independent NIFTY target. The separately fitted rank-two multi-horizon model shares location coefficients across horizons using fully matured targets. It supplies a related low-dimensional learning test whose monthly results are reported in the monthly chapter.
''')
    month=['P_HIST','P_REVERT','P_MOMENTUM','P_CLUSTER','M_FAST','M_SLOW','M_FAST_SLOW','M_DISTRIBUTED','M_MULTITASK','M_SLOW_MATCH','M_SMOOTH','M_STATE_LAGS','PATH_EMPIRICAL','PATH_REGIME','PATH_AR_REGIME','V8_MS_WINDOW','V8_MS_ROLL']
    placebo=metrics[(metrics.cohort=='later')&(metrics.horizon==21)&metrics.model.str.startswith(('M_SHIFT','M_PERM'))]
    path=pd.read_csv(OUT/'path-conditional-risk.csv');path['vol_mae']=abs(path.actual_realized_vol-path.estimated_realized_vol)
    path_stats=path.groupby(['horizon','cohort','model'],as_index=False).agg(n=('origin','size'),vol_mae=('vol_mae','mean'),barrier_brier=('touch_brier','mean'),mean_atom_ESS=('weight_ESS','mean'))
    write_report('MONTHLY_MULTISCALE_RESEARCH',f'''
V8's prominent published monthly candidate, smoothed weekly state with the 126-date fit, scored **.132367 Brier, .020474 CRPS and 85.53%** nominal-80 coverage, but rolling the smoothed inputs produced **.108239 Brier**. V9 newly separates fast contemporaneous factors from 21-session trailing leadership, breadth, synchronization and risk averages. Distributed-lag Ridge adds authentic 0/5/10/21-session financial rotation lags. A second distribution uses previously reconstructed weekly state averages at delayed 0/5/21-session offsets. For multi-task learning, a two-factor reduced-rank Ridge fit shares location across 1/3/5/10/15/21-session returns. All auxiliary labels have ended by the longest-horizon fit boundary. The point prediction shrinks the shared estimate halfway toward ordinary direct monthly Ridge. Neither shared labels nor simulations multiply observed NIFTY outcomes.

{scores(month,21,'early')}

{scores(month,21)}

## Placebo distribution and availability

The placebo family shifts only historical training states by nine predeclared offsets in both directions and adds three block permutations. It retains query features and genuine price controls. Availability matching requires full 21-session smooth states and a genuinely lagged history. Most earlier monthly fits cannot meet the common state history requirement. Later matched states therefore use fewer dates than the principal 76-origin cohort. Every insufficient fold remains visible. Reversal, momentum and empirical history supply persistence benchmarks.

{table(placebo,['model','n','disjoint','brier','crps','coverage80'])}

{stability(['M_SLOW','M_DISTRIBUTED','M_MULTITASK','M_SMOOTH','PATH_REGIME'],21)}

## Path-derived distributions

One model reuses contiguous historical log-return blocks. A second reweights them by similar initial trend/risk using normalized distances. A third fits a modest AR(2) daily mean and recursively simulates contiguous historical residual blocks. Every full block ends before the forecast anchor. Daily log returns are compounded into endpoint laws, and every path weight is preserved for sample reconstruction. The separate risk outcomes are future daily RMS and **daily-close** path touches below −2%, with no tick-level barrier inference. Raw block sampling reproduces the empirical endpoint law. Conditioning does not broadly improve endpoint scores or resolve the V8 monthly timing question.

{table(path_stats[path_stats.horizon==21],['cohort','model','n','vol_mae','barrier_brier','mean_atom_ESS'])}

The later monthly cohort contains only four disjoint returns. The earlier monthly cohort has more origins and different behavior, which remains research-exposed. V9 does not replace V8's exploratory state system with a validated monthly model.
''')
    write_report('FORECAST_RELIABILITY',f'''
We measured three different uncertainties. The predictive return law supplies expected width, entropy and return risk. Approximate parameter uncertainty comes from an innovation-scale-adjusted Ridge leverage calculation in a compact feature space. Applicability uses Ledoit–Wolf Mahalanobis distance, mean Euclidean distance to the eight nearest historical rows, recent-versus-expanding covariance shift, disagreement and recently resolved loss. These are calculated from historical state geometry rather than forecast outcomes still in progress. The Ridge posterior-style scale is an approximation. It is not a confidence guarantee for the fitted model.

{table(rel,['cohort','horizon','assessed','IC_predicted_brier','IC_predicted_crps','IC_mahalanobis','IC_expert_p_disagreement','IC_parameter_uncertainty','IC_predicted_interval_coverage'])}

{table(select[select.selection.isin(['familiar','unfamiliar'])],['cohort','horizon','selection','n','disjoint','accuracy','brier','crps','matched_history_Brier','matched_history_CRPS','interval80_coverage'])}

Unfamiliar earlier weekly states have Brier **.346634** versus **.248577** in familiar states. Their CRPS and interval failures also worsen. Earlier 5-session parameter-uncertainty rank correlation with CRPS is **.400438**, and Mahalanobis rank correlation with Brier **.286651**. These relationships do not transfer cleanly to the later cohort. A reliability rule can diagnose a riskier subset without producing a higher aggregate payoff after fallback. The OOD-weighted complete law is a more balanced candidate than pure rotation for the combined weekly dates but does not dominate fixed fallback or the frozen later leader. This is a prospective research hypothesis. Model disagreement also can be higher in a period containing useful active forecasts, so low agreement should not be interpreted automatically as lack of skill.
''')
    cfig=pd.DataFrame(comb_int['rows']);lawsets=['P_HIST','P_ROT','P_STRUCTURE','T_STUDENT','T_RISK_STUDENT','T_RISK_LAW','PATH_EMPIRICAL','PATH_REGIME','PATH_AR_REGIME','J9_STATIC','J9_REL_SHRINK','J9_OOD']
    write_report('ADAPTIVE_DISTRIBUTIONS',f'''
All endpoint outputs come from one probability measure. The 65/35 residual/empirical law, adaptive Student-t shape, same-volatility residual weighting, and regime-reweighted block paths produce ordered return quantiles and normalized bucket probabilities. Location/scale adjustments remain within their own coherent law. A blend stacks the atoms of its complete constituent distributions with nonnegative weights summing to one. Its p(up), expected/median NIFTY close, central intervals and tails therefore agree mathematically. Forecast return and realized path-volatility scores are evaluated separately.

{scores(lawsets)}

{scores(lawsets,5,'early')}

{composite(lawsets)}

{table(cfig[cfig.model.isin(['P_CLUSTER','P_ROT','P_STRUCTURE','J9_STATIC','J9_REL_SHRINK','J9_PERFORMANCE','J9_OOD'])],['model','metric','n','gain','adjusted95_block10'])}

`J9_REL_SHRINK` is the combined weekly CRPS point leader at **.011014** against **.011340** for history, while losing slightly to that benchmark earlier. `J9_STATIC` follows at **.011029**, roughly .000015 worse using fixed weights and simplifying the interpretation of adaptation risk. Both give up sharp later-cohort CRPS relative to structural rotation. The three earlier dynamic-location laws and Student scales do not systematically beat history. Path models supply independently interpretable conditional volatility and barrier forecasts, retaining serially ordered blocks, but their endpoint scores remain weaker than the best direct later weekly laws.

{table(path_stats[path_stats.horizon==5],['cohort','model','n','vol_mae','barrier_brier','mean_atom_ESS'])}
''')
    e=read('extended-coverage.json');q=preds.groupby(['cohort','horizon'],as_index=False).agg(unique_origins=('origin','nunique'),first=('origin','min'),last_origin=('origin','max'),last_endpoint=('endpoint','max'))
    write_report('EXTENDED_HISTORICAL_EVALUATION',f'''
We preserve the frozen November 17 vintage for V8 reproduction. In a separate acquisition directory Upstox returned completed November 18, 19, 20 and 23, 2026 daily bars. The four NIFTY closes agree with the NSE daily index archive to displayed precision. The older overlap days and every difference are separately recorded in `source-overlap.csv`. Acquisition receipts, URLs, instrument keys and content hashes stay next to the new payloads. [Upstox daily historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [NSE daily archives](https://www.nseindia.com/all-reports)

{table(acq['official_crosscheck'],['origin','status','upstox_close','official_close','delta'])}

{table(q,['cohort','horizon','unique_origins','first','last_origin','last_endpoint'])}

The four sessions resolve four additional prior origins at each horizon. They are reconstructed after outcomes, with mature input labels only and a separate fit calendar for the newly resolved subset. There were fewer than five completed post-vintage sessions, so none of the truly new feature-origin rows was given a fully resolved five/21-session score. The score rows below originate on preexisting historical dates with refreshed endpoints. Their substantial path overlap precludes a new validation claim.

{scores(['E9_HIST','E9_ROT','E9_STRUCT','E9_COMPACT'],5,'refresh')}

{scores(['E9_HIST','E9_ROT','E9_STRUCT','E9_COMPACT'],21,'refresh')}

The main combined leaderboards require the exact same model, feature definition, eligibility and maturity design on all **265 weekly** or **217 monthly** origins. Discontinuous date exposure, missed earlier state eligibility and trailing-month changes are visible. We do not pool partial or refresh samples into the combined leaderboard. Mature dates are frozen per vintage. The combined chronology retains **53** disjoint weekly and **11** disjoint monthly windows under the greedy selection rule, while the later 21-session subset still has four.
''')
    cumulative=read('historical-search-accounting.json');null=pd.read_csv(OUT/'null-search-maxima.csv');d=null[null.draw>=0];n0=null[null.draw==-1].iloc[0]
    write_report('CUMULATIVE_SEARCH_AUDIT',f'''
We recovered **{cumulative['registry_and_manifest_files']}** earlier registry/manifest files, **{cumulative['parsed_config_records']}** parsed configuration entries and **{cumulative['scored_model_horizon_vectors']}** protected model/horizon forecast vectors. There are **{cumulative['exact_config_hashes']}** exact normalized JSON payload fingerprints, **{cumulative['candidate_shape_hashes']}** restricted parameter signatures and **{cumulative['distinct_vector_fingerprints']}** distinct stored prediction fingerprints at the hash precision. Those counts are an auditable lower-bound inventory. V1–V2 formats and some older workflow configurations are heterogeneous, and payload differences are not always substantive estimator differences. `historical-config-inventory.csv`, `historical-prediction-fingerprints.csv`, and the registry index identify the repeated and distinct records. Cross-system pairs of probability, residual error, Brier and CRPS correlation are available in `prediction-and-error-correlations.csv`.

The largest prior wins are not stable to material protocol changes. V8 raw rotation reproduces the same earlier deterioration; the V9 common fitting curve shows that the later advantage collapses when kept at the same 85-date window. V7 and V8 monthly state winners weaken or are equaled by certain alignment controls. Such changes are observed failures under design/cohort alterations. They are not independent consecutive prospective tests.

## Refit the search under block nulls

We reran eight actual competing V9 heads on all later weekly dates, including rotation, residual rotation, structure, compact native, financial panel, innovation, exponentially weighted Ridge and cluster-balanced Elastic Net. Twenty-four seeded block-permuted training/inner/validation target draws use blocks of 5, 10 and 15 observations. Each draw refits each model and reselects the best per-score improvement against the same genuine historical benchmark. The outer outcomes and their date order remain untouched. This tests a bounded search family rather than shuffling one already-selected winner.

The genuine eight-model search finds **{n0.best_brier_gain:.6f}** Brier and **{n0.best_crps_gain:.6f}** CRPS gains over the historical fallback on the later dates. Null maxima range **{d.best_brier_gain.min():.6f} to {d.best_brier_gain.max():.6f}** for Brier and **{d.best_crps_gain.min():.6f} to {d.best_crps_gain.max():.6f}** for CRPS. **{int((d.best_brier_gain>0).sum())}/24** draws appear to improve Brier, and **{int((d.best_crps_gain>0).sum())}/24** appear to improve CRPS. These distributions illustrate search risk without supplying a p-value covering eight prior research versions. The strongest prior forecasting systems are much tougher benchmarks than simple historical returns on the later dates.

{table(null,['draw','block','best_brier_gain','best_crps_gain','brier_winner','crps_winner'])}

Within V9, shared moving origin-block bootstraps use 2,000 draws and 5/10/15-session length sensitivity. Earlier weekly family size is **{uncertainty['early']['contrasts']:,}** and later weekly family size **{uncertainty['later']['contrasts']:,}**. The combined full-coverage weekly family has **{comb_int['contrasts']}** contrasts. Some draws lack dates for small eligible subsets; the algorithm ignores missing bootstrap estimates while retaining cohort-specific validity and reports the matched count. Monthly and refresh uncertainty is descriptive. Past fitting, maturity, duplicate invariance and all retained failures are independently checked in `verification.json`. No adjustment reconstructs all adaptive V1–V9 choices.
''')
    w=metrics[(metrics.horizon==5)&(metrics.cohort=='later')].sort_values('brier')
    m=metrics[(metrics.horizon==21)&(metrics.cohort=='later')].sort_values('crps')
    write_report('COMPLETE_MODEL_COMPARISON',f'''
Direction and distribution are ranked separately and within cohort. V4 coherent distributions, older V5 and V6 point leaders, V7 rotation and Elastic Net, and V8 winners and monthly controls remain available in the frozen score listings. `direction-leaderboard.csv`, `distribution-leaderboard.csv`, `temporal-stability-leaderboard.csv`, `selective-performance.csv`, and `combined-cohort-leaderboard.csv` contain full metrics and conditional rows. `benchmark-comparisons.csv` and `parent-increments.csv` retain exact matched-origin parent and strong-benchmark gains. Time, calibration, coverage, and width are retained rather than collapsed into a weighted headline score.

## Later weekly and monthly model comparison

{table(w,fullcols+['status'])}

{table(m,fullcols+['status'])}

## Combined chronology Pareto representation

The full-cohort Pareto set minimizes earlier and later Brier and CRPS individually. Model ties, including empirically identical historical path and endpoint laws, remain shown. It excludes labeled diagnostic and partial-date systems. A later winner that gets worse earlier remains visible alongside models that compromise. That is the intended selection criterion.

{table(pareto,['horizon','model','n','disjoint','brier','crps','early_Brier','late_Brier','early_CRPS','late_CRPS','abs_Brier_cohort_gap'])}

{matched(['P_ROT','P_STRUCTURE','P_CLUSTER','J9_REL_SHRINK'])}

{matched(['P_CLUSTER','J9_STATIC','J9_REL_SHRINK'],5,'early',('P_HIST','V8_E_HIST','V8_E_FULL_ROT'))}

{stability(['P_ROT','P_STRUCTURE','P_CLUSTER','J9_REL_SHRINK'])}
''')
    write_report('SIGNAL_DISCOVERIES',f'''
1. **Fit history interacts with date.** Matching exactly 85 mature training observations makes later rotation worse instead of better. Later expanding training explains a large component of the gap, with window composition, past outcomes and regime still correlated. The identical-date 300-observation control is stronger than 85, 126, 189 and 252 later. That ordering is not a monotone learning law.
2. **Model risk can be diagnosed more easily than exploited.** Earlier-weekly distance and parameter-uncertainty proxies relate to worse losses, but a selector takes 52 later dates on which the same model actually performs worse than on the dates it would abstain. More uncertain path scale is separate from poor applicability.
3. **Cluster balance and conservative fallback are useful combined-cohort tradeoffs.** A cluster-balanced rotation law improves pooled Brier. Reliability/history shrinkage and the fixed fallback improve pooled CRPS, with no clear earlier superiority and large sacrifice versus later V8 rotation.
4. **Financial divergence, innovation, and panel effects depend on representation and period.** Native market-adjusted finance is meaningful within the larger model. Narrow financial heads and statistical surprises do not reliably beat the matched domestic control in both cohorts. Historical index exposures and public announcement surprises were not identified by these tests.
5. **Global context can change risk estimates without fixing direction.** The earlier volatility MAE gains disappear later and the global reliability gate makes small tradeoffs. Intraday and ETF evidence is guarded by exact V8 reproductions; the wider V9 liquidity law supplies a pooled expert rather than a new standalone edge.
6. **Monthly states and paths are inconclusive.** Slow factors, rank-two multi-horizon learning, historical block paths, and AR blocks change the architecture substantially. None establishes superiority over the strong monthly or historical controls. State-placebo results and disjoint-window limits remain beside all scores.

{gains(['P_ROT','P_STRUCTURE','P_CLUSTER','T_KALMAN','F_BANK_RESID63','I_AR','X_ROT_PANEL','J9_REL_SHRINK'])}
''')
    cc=combined[combined.horizon==5].set_index('model');historical=cc.loc['P_HIST'];best=cc.loc['P_CLUSTER'];law=cc.loc['J9_REL_SHRINK'];
    write_report('FINAL_RESEARCH_CONCLUSIONS',f'''
The V9 diagnosis favors **training support and careful fallback** as the useful discoveries. V8's later probability and distribution point records remain superior on their own later dates. V9's later identical-design residual rotation reaches **.164236 Brier** and market structure reaches **.009608 CRPS**. Attempts to adapt aggressively through Kalman, recency, regimes and meta-learning mostly fail. Giving forecasts more historical support and using a conservative blend reduces the difficulty of combining periods, without creating an independent predictive edge.

The identical-design **265-origin weekly** comparison gives cluster-balanced rotation **{best.brier:.6f} Brier** versus **{historical.brier:.6f}** historical, and the reliability/history blend **{law.crps:.6f} CRPS** versus **{historical.crps:.6f}** historical. On the earlier cohort, the two candidate losses are **{best.early_Brier:.6f} Brier** and **{law.early_CRPS:.6f} CRPS**, both slightly worse than the historical scores **{historical.early_Brier:.6f}** and **{historical.early_CRPS:.6f}**. Hence the combined gains partly reflect later strength, not earlier robustness. The fixed fallback is almost tied for pooled CRPS. The full uncertainty ranges, including the weaker earlier and later comparisons, are below.

{composite(['P_HIST','P_CLUSTER','P_ROT','P_STRUCTURE','J9_REL_SHRINK','J9_STATIC','J9_PERFORMANCE'])}

{table(cfig[cfig.model.isin(['P_CLUSTER','P_ROT','P_STRUCTURE','J9_REL_SHRINK','J9_STATIC'])],['model','metric','n','gain','adjusted95_block10'])}

Keep historical fallback, V8 protected rotation/structure, cluster-balanced rotation and a simple complete-law blend as separate candidate hypotheses. For monthly retain empirical/reversion and protected V8 smoothing as controls. V9 robust paths and distributed lags did not yield a monthly model that merits promotion. The four acquired sessions resolve four old origins per target, which provide no meaningful new disjoint evaluation. The null search shows that a selected small gain over history can appear even after disrupting fit alignment. No forward V9 forecast, trading or deployment was performed.
''')
    write_report('NEXT_EXPERIMENTS',f'''
Freeze later V8 reference laws, the fixed historical law, one cluster-balanced rotation candidate and one static fallback blend. Compare them on genuinely newer, timestamped research evaluations with primary scores and sample-size rules chosen in advance. Record cold-start training length and whether actual V8 source receipts and later source revisions are known. Evaluate equal training lengths on each new period before deciding that a regime has changed.

For reliability research, preregister out-of-distribution diagnostics separately from abstention. Check whether Mahalanobis distance, regime-local width or recent resolved loss predicts absolute calibration error. Compare any conditional fallback with the simple fixed history mixture at equal coverage. Continue only if improvements survive date matching and leave-period tests.

For financial information, retain one fixed lagged-beta residual and separately track private versus PSU strength, with dated composition if available. Compare genuine statistical innovation against direct levels and changes on the same dates. Selected financial ETFs and insurance names can inform aggregated states but cannot create more NIFTY return observations. Global research should prioritize timing quality and risk conditioning over adding more direct direction inputs.

For monthly continue evaluating slow factors and truly pre-issued estimates on additional disjoint outcomes before selecting a state timing rule. Retain the full registered placebo distribution. Study path forecasts as separate risk distributions where close-based barrier and realized-volatility validation is meaningful. If the simple historical model remains strongest on new outcomes, preserve that result as a model-selection outcome.
''')
    save('report-manifest.json',{n:sha(OUT/n) for n in names})
    if OUT==DEFAULT:
        rel=OUT.relative_to(ROOT).as_posix();lines=['# NIFTY V9 research','','Training length reversal, pooled forecasting tradeoffs, and predictability diagnostics on exposed 2025–2026 data.','']
        lines.extend(f'- [{n[3:-3].replace("_"," ").title()}]({rel}/{n})' for n in names)
        lines.extend(['',f'[Combined leaderboard]({rel}/combined-cohort-leaderboard.csv) · [Temporal Pareto]({rel}/temporal-pareto.csv) · [All predictions]({rel}/all-predictions.csv) · [Verification]({rel}/verification.json) · [Replay instructions](research/nifty_forecast_v9/README.md)',
                      '',f'[Training-size figure]({rel}/matched-learning-curves.png) · [Cohort comparison figure]({rel}/weekly-cohort-tradeoffs.png)'])
        (ROOT/'NIFTY_V9_RESEARCH.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Rendered',len(names),'requested V9 reports',flush=True)


if __name__=='__main__':run()
