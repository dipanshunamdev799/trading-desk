"""The ten required V3 reports, matched comparison tables and delivery manifest."""
import json,re
from pathlib import Path
import numpy as np
import pandas as pd
from .audit import ROOT,OUT,sha,save
from .models import SPECS

def readable(text):
    # Repair prose spacing without changing model IDs, file names or data fields.
    words='the|The|all|of|from|to|and|with|only|just|its|a|an|has|is|was|at|using|after|before|No|no|not|nominal|Nominal|versus|flipped|destroyed|correcting|span|spans|supply|overlapping|non-overlapping|remaining|into|user\'s|scores|estimate|monthly|Phase'
    text=re.sub(r'\b('+words+r')(?=\d)',r'\1 ',text)
    text=re.sub(r'(?<=\d)(?=November\b)',' ',text)
    return text.replace('pre2025','pre-2025').replace('in09_FINAL_FORECASTS','in 09_FINAL_FORECASTS')

def emit(name,text):
    (OUT/name).write_text(readable(text.strip())+'\n',encoding='utf-8')

def main():
    metrics=json.loads((OUT/'metrics.json').read_text());outer=[r for r in metrics if r['split']=='outer_exposed']
    predictions=pd.read_csv(OUT/'predictions.csv');call=json.loads((OUT/'09_FINAL_FORECASTS.json').read_text())
    legacy=json.loads((OUT/'legacy-artifact-reproduction.json').read_text());repro=json.loads((OUT/'legacy-2025-only-reproduction.json').read_text())
    definitions=json.loads((OUT/'feature-definitions.json').read_text());manifest=json.loads((OUT/'dataset-manifest.json').read_text())
    information=pd.read_csv(OUT/'development-feature-information.csv');stability=pd.read_csv(OUT/'development-stability-selection.csv')
    paired=json.loads((OUT/'paired-comparisons.json').read_text());simult=json.loads((OUT/'simultaneous-uncertainty.json').read_text())
    ledger=json.loads((OUT/'experiment-ledger.json').read_text());verification=json.loads((OUT/'verification.json').read_text())
    def metric(h,name):return next(r for r in outer if r['horizon']==h and r['model']==name)
    def table(rows,columns):
        return '|'+ '|'.join(columns)+'|\n|'+'|'.join(['---']*len(columns))+'|\n'+'\n'.join('|'+ '|'.join(str(r.get(c,'NOT MEASURED')) for c in columns)+'|' for r in rows)
    family=[]
    for key,group in pd.DataFrame(definitions).groupby('family'):
        family.append({'family':key,'features':len(group),'median missing':f"{group.missing_fraction.median():.1%}",
                       'classification':group.classification.iloc[0]})
    top=information.sort_values('bh_q').head(12)
    emit('02_FEATURE_DISCOVERY.md',f'''# 02 — Feature discovery and availability

The dataset has {manifest['eligible_feature_rows']} eligible origins, {manifest['first_origin']} through
{manifest['last_origin']}, and {manifest['feature_count']} features. No value or indicator initialization before
2025-01-01 was used. Native index/ETF data, 465 dated official FO sessions, complete
prior-session intraday summaries and six conservatively lagged global series
replace the earlier restriction to 71 indicators.

{table(family,['family','features','median missing','classification'])}

The 12 current-member-basket features are research-only. No historical NIFTY
constituent membership or index-weight reconstruction was recovered for the full
period. Only A02_proxy uses them; they are excluded from all primary selectors.
Stock breadth is not silently relabeled genuine historical index participation.
ETF volume is real; NIFTY spot volume remains zero. No spot VWAP was invented.

FO features include nearest non-expired futures basis, relative OI change,
same-contract/lot OI log change, explicit roll indicator, DTE, log OI/volume PCR,
call/put OI concentration, wall distances, max-pain distance and matched-contract
PCR change. Roll/lot changes do not create synthetic OI increments. Contract IDs
are metadata, never numeric predictors. FO and institutional inputs have an
extra domestic-session publication lag. Historical IV/Greeks were not fabricated.

Development-only discovery uses labels matured before 2026-07-01: 238 eligible
feature/horizon IC tests, 200 temporal circular-shift nulls per test, BH adjustment,
2,261 monthly univariate OOS folds, MI representatives versus 20 shifted nulls,
and 30 temporal-block ElasticNet stability fits per horizon. These diagnostics
do not select features on the final outer period.

Lowest adjusted q-value is {information.bh_q.min():.4f}; **zero features pass BH q<.05**.
Monthly ETF volume/turnover has rank IC near +.263 and stable positive half-sample
signs, but adjusted q near .296. VIX change and sector participation show
conditional associations, not validated independent information.

{top[['horizon','feature','rank_ic','first_half_ic','second_half_ic','bh_q']].round(4).to_markdown(index=False) if False else table(top.round(4).to_dict('records'),['horizon','feature','rank_ic','first_half_ic','second_half_ic','bh_q'])}

Full results: development-feature-information.csv, development-univariate-oos.csv,
development-mutual-information.json, development-stability-selection.csv and
feature-definitions.json. Linear full-context minus FO/FII is a **joint block**
ablation; it cannot identify which individual derivative variable causes a change.
Associations, coefficient stability and tree gain are not causal effects.''')
    emit('03_TARGET_RESEARCH.md',f'''# 03 — Independently defined prediction targets

Weekly=5 and monthly=21 actual observed NSE sessions. Endpoint return is
C[t+h]/C[t]-1. Separate evaluated targets: direction, direct mean return, median,
absolute magnitude, full return distribution, annualized future RMS volatility,
and path breaches below -2% and -5%. Seven fixed endpoint-return buckets use
-5%, -2%, -.5%, +.5%, +2%, +5% boundaries. None was chosen using outer outcomes.

All labels carry endpoint dates. A row can train any layer only when its endpoint
is **strictly earlier** than the new decision's completed-session origin. The
extra-session embargo applies inside inner validation too. Actual session bars,
including valid special sessions, define horizon length; future dates use the
published NSE calendar. Known 2025/2026 historical index calendars were checked
in earlier audits; the fresh complete 465-session index agrees with official FO
underlying on all 465 dates, maximum difference 0 points.

Volatility is sqrt(252*mean(future daily log-return squared)). A path breach is
min(future daily closes)/origin close-1, not a reconstructed intraday drawdown.
The future trend/transition state is **NOT VALIDATED**: V3 tests causal origin-
regime-conditioned return forecasts, not a certified forecast of latent regimes.

Return models regress future returns directly. Linear residual distributions
use purged inner held-out residuals; boosted models directly fit seven quantiles.
Quantile crossings are sorted and counted. Beyond 5/95 percentiles, tail
extrapolation is explicitly NOT VALIDATED. This replaces the earlier sign-only
mixture, but it does not guarantee coverage. Independent target selectors can
disagree; no joint coherence or calibrated probability claim is made.

Direction: Brier/log loss/accuracy/balanced accuracy/calibration. Returns:
MAE/RMSE/median MAE. Distribution: empirical CRPS, pinball, seven-bucket Brier,
50/80% interval coverage and width. Risk: volatility MAE/QLIKE and path-tail Brier.
Origin regimes use only observed trend, training-median RV, participation, expiry,
global risk-off and preceding large moves. Conditional diagnostics are descriptive;
no favorable slice becomes an independently validated subgroup edge.

Novel insight: different targets prefer different methods, and selecting a model
for return MAE does not establish direction, volatility or interval skill. Current
cross-target inconsistencies are recorded in the final JSON rather than hidden.''')
    spec_rows=[{'ID':k,'algorithm':v['kind'],'feature set':v['features'],'parameters':json.dumps(v['parameters']),
                'primary eligible':not v['research_only']} for k,v in SPECS.items()]
    emit('04_MODEL_EXPERIMENTS.md',f'''# 04 — Controlled model experiments

19 fitted configurations, independently trained at each horizon; five deterministic
controls (neutral, momentum, reversion, always-up/down); five nested target selectors
and five corresponding baseline selectors. There were {len(ledger)} registered
configuration/fold evaluations, zero failed configurations. Each ledger row includes
both purged-inner and full-past fitting; compound tree models contain multiple
estimators, so 532 is not the count of individual elementary estimator fits.

{table(spec_rows,['ID','algorithm','feature set','parameters','primary eligible'])}

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
not additional candidate searches.''')
    emit('05_VALIDATION_AND_LEAKAGE_AUDIT.md',f'''# 05 — Validation, leakage and uncertainty audit

History strictly 2025-01-01 through 2026-11-16. First feature origin is
{manifest['first_origin']} after 63-session warmup inside the permitted period.
No pre-2025 trained state is imported. All dates were already research-exposed
by previous studies: **no historical split is called untouched confirmation**.

Monthly chronological refits use only matured endpoints plus one-session embargo.
The latest42 eligible origins form inner validation. Inner fitting purges any
label whose endpoint reaches that inner period. Inner training must have80 labels,
and outer fitting at least126 matured labels; this necessarily delays the first
monthly development forecast. Targets independently choose configurations using
inner Brier, MAE, CRPS, QLIKE or tail Brier. Outer stress origins begin2026-07-01.
Scaling, imputation, correlation pruning, risk thresholds and selective-forecast
thresholds are training-only. Provider-launch missingness indicators are not used.

Weekly outer evaluation has92 overlapping origins, 19 non-overlapping windows
and outcome-autocorrelation ESS about23.45. Monthly has76 origins, four disjoint
windows and ESS about5.96. Neither count guarantees independence. Monthly paired
intervals are withheld: 76<168 required origins for the prespecified 42-session
block. Weekly blocks have10 sessions and2,000 resamples. Simultaneous intervals
span170 model/policy-and-target contrasts; **none has a positive lower bound**.
The strongest fixed baseline is identified on outer data and marked postselected;
inner-only baseline selectors are also reported and can themselves overfit.

{verification['tests']} focused tests passed. They check source/data hashes,
unchanged old calls, exact fitted-source archive, rejection of pre-2025 values,
registered future-oracle availability and unregistered future columns, unfinished
labels, inner purging, future-source/target perturbation invariance, cached feature
reproduction, representative model reproduction, horizon labels, proxy exclusion,
non-overlap, official FO identity/date checks, zero index volume, partial intraday
rejection and withholding unsupported monthly confidence intervals.

Six independently randomized-direction controls show no positive direction skill:
weekly Brier approximately .3359/.2840/.3575 and monthly .3448/.2809/.3285,
all worse than neutral .25. One randomized weekly accuracy is54.9%; that isolated
accuracy does not create proper-score skill. Temporal-shift nulls are additionally
used in development feature discovery. Volatility is deliberately not randomized
in the direction controls and no claim is made that they test every target.

Hardening amendment: schema/time checks, explicit exclusion of a parsed contract
ID from numerical features and invalid-intraday-day checks were added after the
first batch. This is disclosed, not hidden as original pre-registration. Exact
initial fit code is archived in source-at-first-fit; tests confirm exact cached
features and representative ridge/LightGBM predictions are numerically unchanged.
No parameter/model selection changed. guard-amendment.json and verification.json
record this. Current source and exact fitted source are separately traceable.

Historical publication clocks and vendor revision vintages remain assumptions.
One extra session lag for FO/FII and conservative global joins reduce timing risk
but cannot manufacture an as-delivered archive. Current-basket proxy results are
ineligible for primary claims. Any apparent improvement remains conditional on
those source limitations.''')
    for h,title,filename in [(5,'Weekly','06_WEEKLY_FORECAST_RESEARCH.md'),(21,'Monthly','07_MONTHLY_FORECAST_RESEARCH.md')]:
        a=metric(h,'S_direction');candidate=metric(h,'M05_lgbm' if h==5 else 'S_direction')
        best=[r for r in outer if r['horizon']==h and not r['research_only']]
        rows=[]
        for target,loss in [('direction','brier'),('return','mae'),('distribution','crps'),('volatility','qlike'),('tail','tail02_brier')]:
            selected=metric(h,'S_'+target);base=metric(h,'C_'+target);leader=min(best,key=lambda r:r[loss])
            rows.append({'target':target,'nested selector loss':f"{selected[loss]:.6f}",'nested baseline loss':f"{base[loss]:.6f}",
                'outer descriptive leader':leader['model'],'leader loss':f"{leader[loss]:.6f}"})
        text=f'''# {title} V3 forecasting research

Horizon={h} actual NSE sessions. Outer origins={a['n']}, non-overlapping windows=
{a['nonoverlapping_n']}, outcome-ACF ESS={a['outcome_autocorrelation_ess']:.2f}.
Selector policy accuracy={a['accuracy']:.2%}, balanced accuracy={a['balanced_accuracy']:.2%},
Brier={a['brier']:.6f}, log loss={a['log_loss']:.6f}. Always-up accuracy=
{a['always_up_accuracy']:.2%}; always-down={a['always_down_accuracy']:.2%}.

{table(rows,['target','nested selector loss','nested baseline loss','outer descriptive leader','leader loss'])}

The descriptive leader is selected after observing outer scores and is not
independent validation. Target selectors are different policies; do not quote
a return-selector's volatility success as if it were selected for volatility.
All scores are matched on identical origins. Subperiod/regime and selective
coverage diagnostics are saved even when unfavorable.
'''
        if h==5:text+='''
The shallow boosted model is an exploratory lead: 66.30% accuracy, Brier .226049,
log loss .64549, versus neutral .250000 and momentum .251413. The best fixed
probability control is reversion (.249239), so its Brier improvement is .023190.
The simultaneous 95% block interval is -.093033 to +.139413, crossing zero. The
adaptive inner direction selector scores worse (.256118) than neutral despite
63.04% accuracy, illustrating that accuracy alone is inadequate. Boosted nominal
80% interval coverage is63.04%, so distribution reliability does not follow from
its better direction point estimate. No genuine advantage is demonstrated.
'''
        else:text+='''
The new no-posthoc-calibration direction selector is better than the old failed
monthly study descriptively: 60.53% accuracy, Brier .242200, versus neutral .25,
momentum .251184 and always-down59.21% accuracy. Four non-overlapping windows
cannot establish independent skill or robust significance. Its nominal80% return
coverage is52.63%; the independently selected distribution policy covers only31.58%.
The sector model has an attractive volatility QLIKE point score .088307, but the
actual nested volatility selector scores .218972 versus baseline selector .179324.
Selecting the sector model after this result would be post-selection. Confidence
intervals are NOT ESTIMATED for the small monthly outer sample.
'''
        text+='''
Current numerical scenarios and their late-issued timing are in09_FINAL_FORECASTS.
No high-confidence label or trading recommendation is attached. Target/feature
availability assumptions, exposed-history status and corporate-action proxy
limitations apply to all candidate comparisons.
''';emit(filename,text)
    compare_rows=[]
    chosen=['Z_neutral','Z_momentum','B00_empirical','M00_ridge_price','M01_ridge_full','A00_sector','A01_nofo','A02_proxy','M05_lgbm','S_direction','S_return','S_distribution','S_volatility','S_tail']
    for h in [5,21]:
        for model in chosen:
            a=metric(h,model);base=metric(h,'Z_neutral')
            compare_rows.append({'Model':model+(' [RESEARCH-ONLY PROXY]' if a['research_only'] else ''),'Horizon':h,
                'OOS origins':a['n'],'Effective sample':f"{a['nonoverlapping_n']} disjoint / ESS{a['outcome_autocorrelation_ess']:.1f}",
                'Brier':f"{a['brier']:.5f}",'Accuracy':'NO CALL' if model=='Z_neutral' else f"{a['accuracy']:.1%}",
                'MAE':f"{100*a['mae']:.3f}%",'Interval coverage':f"50:{a['coverage50']:.1%};80:{a['coverage80']:.1%}",
                'Baseline improvement':f"{base['brier']-a['brier']:+.5f} vs neutral"})
        compare_rows.append({'Model':'Best independently validated candidate: NONE','Horizon':h,'OOS origins':'NOT AVAILABLE',
            'Effective sample':'NOT VALIDATED','Brier':'NOT AVAILABLE','Accuracy':'NOT AVAILABLE','MAE':'NOT AVAILABLE',
            'Interval coverage':'NOT VALIDATED','Baseline improvement':'NONE DEMONSTRATED'})
    pd.DataFrame(compare_rows).to_csv(OUT/'final-model-comparison.csv',index=False)
    emit('08_MODEL_COMPARISON.md',f'''# 08 — Fair comparisons and failure diagnosis

**No independently validated winner exists.** All historical dates are exposed;
none of170 simultaneous weekly contrasts excludes zero improvement, and monthly
independent evaluation is too small. The table's MAE/distribution columns belong
to each method's independently fitted return outputs; do not assume its classifier
probability and quantile distribution form a calibrated joint forecast.

{table(compare_rows,['Model','Horizon','OOS origins','Effective sample','Brier','Accuracy','MAE','Interval coverage','Baseline improvement'])}

## The earlier failures were reproduced, not discarded

Original monthly calibrated accuracy was16.67% versus52.78% raw; Brier .307490
versus .268606. Calibration flipped17 predictions:15 correct-to-wrong and only2
wrong-to-correct. Mean probability shifted from52.29% to52.96% while actual up
frequency was36.11%; small average shifts hide damaging threshold crossings.
Weekly calibration flipped26 calls with13 improvements and13 deteriorations,
but worsened Brier from .247161 to .249527. Overlapping-label prevalence shifts,
limited calibration diversity and nonstationarity explain plausible failure
mechanisms; this is not proof of a single causal explanation.

The exact old architecture was also refit using only2025 onward, no old fitted
state. Its stringent252-training+126-OOS gates leave just54 fully learned weekly
origins (11 disjoint) and6 monthly origins (one disjoint). This demonstrates why
the old monthly model could not be reliably validated under this constraint.

Learned allocations can lose to equal groups because correlated errors plus
small effective meta samples produce unstable trust estimates. V3 tests raw
joint models and interactions without forcing the old group architecture or
its posthoc calibration. Some point scores improve, but nonlinear mechanisms
do not survive the current qualification standard. The joint FO+FII ablation
often improves the full linear model when removed; obtaining more authentic
data did not itself prove incremental predictive value. This does not isolate
FO from sparse FII or prove derivatives are universally uninformative.

Weekly and monthly rankings differ. Volatility/returns/distributions have
different leaders and different selectors. An attractive postselected volatility
score does not validate direction, interval coverage or a risk strategy. Current
member-basket proxies cannot establish true historical breadth skill, even if a
proxy ablation improves one score. Training feature gain and importance are not
causal effects.

Model selection can also overfit a42-origin inner set, particularly when monthly
outcomes overlap. The nested baseline selector itself performs poorly; it is not
used as the sole benchmark. Fixed neutral/momentum/reversion and the strongest
fixed baseline are disclosed alongside it. Selective forecasts report coverage,
matched baselines and small counts; no favorable subgroup is promoted after inspection.

Statistical details: paired-comparisons.json, simultaneous-uncertainty.json,
feature-family-ablations.json, conditional-diagnostics.json, selective-forecasting.json,
legacy-artifact-reproduction.json and legacy-2025-only-reproduction.json.''')
    forecast_text=f'''# 09 — Final as-of research scenarios: NOT VALIDATED

**NOT A FRESH PREMARKET FORECAST.** Issued {call['issued_at']} after the17November
session had already opened. Reference={call['reference_close']:,.2f}, completed
session={call['reference_session']}, source bar timestamp={call['reference_source_timestamp']}
(a session anchor, not proof of publication time). Actual latest acquisition=
{call['information_cutoff']['actual_source_acquisition_last']}. Intended model
clock=00:30 IST following the completed session. No17November intraday prices
enter the feature panel. The first target session is already in progress.
This is a late-issued, revised-vintage as-of reconstruction, not fresh confirmation.

All numeric estimates below carry **NOT VALIDATED** status. No production or
trading-qualified model was found. The full machine record contains source/model
versions, probabilities, seven return buckets, baselines, policy and fixed-model
OOS scores, calibration/coverage histories, effective samples and unresolved outcomes.
'''
    for name,f in call['forecasts'].items():
        hist=f['specific_selector_policy_oos'];q=f['central80_endpoint_interval']
        forecast_text+=f'''
## {name.title()} — {f['horizon_trading_sessions']} sessions, expected endpoint {f['expected_endpoint_date']}

- Direction model: {f['selected_models']['direction']}; raw upward estimate
  {f['positive_return_probability']:.2%}, nonpositive {f['nonpositive_return_probability']:.2%}.
  This is not a historically calibrated or independently validated probability.
- Direct mean-return model: {f['selected_models']['return']}; point estimate
  {f['expected_return_regression']:+.3%}; endpoint {f['expected_endpoint_price']:,.2f}.
- Distribution model: {f['selected_models']['distribution']}; median return
  {f['median_return_distribution']:+.3%}, endpoint {f['median_endpoint_price']:,.2f}.
- Nominal50% interval: {f['central50_endpoint_interval'][0]:,.0f}–{f['central50_endpoint_interval'][1]:,.0f};
  nominal80%: {q[0]:,.0f}–{q[1]:,.0f}. Coverage of that distribution-selector policy
  was {hist['distribution']['coverage50']:.1%}/{hist['distribution']['coverage80']:.1%}, not50/80%.
- Volatility model: {f['selected_models']['volatility']}; annualized point
  {f['annualized_volatility_point']:.2%}; sqrt-time move proxy
  {f['sqrt_time_horizon_move_proxy']:.2%}. These are not validated expected-risk guarantees.
- Tail model: {f['selected_models']['tail']}; daily-close path-breach estimates
  below-2% {f['path_breach_below_minus2_probability']:.2%}, below-5%
  {f['path_breach_below_minus5_probability']:.2%}.
- Seven endpoint bucket probabilities: {json.dumps({k:round(v,4) for k,v in f['return_bucket_probabilities'].items()})}.
- Bullish/neutral/bearish scenarios use endpoint returns above+.5%, within±.5%,
  below-.5%. Distribution scenario estimates: {json.dumps({k:round(v,4) for k,v in f['scenario_probabilities_from_distribution'].items()})}.
- Direction-selector OOS: n={hist['direction']['n']}, accuracy={hist['direction']['accuracy']:.2%},
  Brier={hist['direction']['brier']:.5f}; {f['effective_evaluation']['nonoverlapping']} disjoint
  windows and outcome-ACF ESS={f['effective_evaluation']['outcome_acf_ess']:.2f}.
- Cross-target inconsistency: classifier P(up)={f['cross_target_consistency']['classifier_p_up']:.2%}
  versus distribution-implied {f['cross_target_consistency']['distribution_p_up']:.2%}.
  These independently selected targets do not form a calibrated coherent joint forecast.
- Main feature associations are training-only coefficients/gain in
  model-contributions.json; no contributing family has established independent
  incremental predictive importance. Future latent regime is NOT VALIDATED.
'''
    forecast_text+='''
Exact target session dates use the saved published NSE calendar. Unexpected
closures or missing candles require review. Means/medians can disagree, but the
size of these cross-target disagreements plus undercoverage is a reason to reject
precise forecast interpretation. The JSON does not suppress these inconsistencies.
All outcomes are unresolved. A genuinely fresh next premarket freeze requires
the17November completed session and its authenticated newly available inputs,
which did not exist at this research execution cutoff. No watcher was scheduled.
''';emit('09_FINAL_FORECASTS.md',forecast_text)
    emit('10_NEXT_RESEARCH_PRIORITIES.md','''# 10 — What is missing and what would change the conclusion

1. Freeze one small weekly hypothesis prospectively: shallow nonlinear interactions
   versus neutral/reversion and a price+sector control, with unchanged features,
   parameters, decision clock and stop rule. The66.3% exposed weekly result is a
   lead to investigate, not independent validation. Do not retune it on this outer set.
2. Capture true source delivery times and revision identities for every daily,
   global, FO and institutional input; retain both event and received clocks.
   Extra-day lags are assumptions, not substitutes for a delivery archive.
3. Acquire genuinely dated NIFTY constituent membership and weights, including
   additions/removals and corporate-action identities. Until then, keep today's
   basket out of primary breadth claims. Do not import pre2025 market warmup.
4. Independently validate volatility/tail forecasts before any exposure decision.
   Direct quantiles still under-cover. Study low-dimensional price/sector risk
   models with a fixed distribution calibration protocol on fresh evidence;
   overlapping42-origin residual windows do not supply42 independent months.
5. Separate FO from institutional ablations on **development or new** data.
   The tested no-FO configuration removes both blocks, so a harmful joint result
   cannot identify the causal source. No new postselected sweep is justified here.
6. Record calibration threshold flips and rolling prevalence drift. The old
   monthly mapping destroyed15 correct calls while correcting2. Do not enforce
   calibration merely because it sounds statistically sophisticated.
7. Model selection needs more than a short inner overlap-heavy window. A baseline
   selector can also overfit. Keep fixed neutral/momentum/reversion benchmarks
   alongside any adaptive selector; preregister primary metrics and family budgets.

No model passes the current simultaneous qualification threshold, no evaluation
is genuinely untouched, and monthly independent counts are inadequate. Therefore
practical trading/exposure/fee optimization is **NOT QUALIFIED** under Phase10;
none was run or represented as profitable. This avoids reusing forecasting
discovery observations to manufacture a trading-strategy success.

Planning evidence targets, not statistical guarantees: accumulate at least30–50
new non-overlapping weekly and12–24 monthly outcomes for a very small frozen
comparison, with a dependence-aware power calculation using the realized paired
loss variance and declared model budget. The correct required N cannot be promised
in advance from this noisy sample. Within the remaining2026 scope, only about
six non-overlapping5-session windows and one21-session window remain. These cannot
settle the current monthly question. Extending collection/evaluation into2027
would require an explicit change to the user's2025–2026 constraint; no such
extension or automation is silently created.

A valid research outcome here is the precise null/inconclusive finding, authentic
new derivatives coverage, reproducible comparisons, rejected hypotheses and a
prospective evidence plan. More columns, more trees or a larger displayed
probability cannot supply the missing independent observations.''')
    # Lightweight standalone research figure.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for ax,h in zip(axes,[5,21]):
        names=['Z_neutral','Z_momentum','M05_lgbm','S_direction'];vals=[metric(h,n)['brier'] for n in names]
        ax.barh(names[::-1],vals[::-1],color=['#087e8b','#8055a4','#a5afbc','#c4cbd3'])
        ax.axvline(.25,color='#6b7685',ls='--');ax.set_xlim(0,.36)
        ax.set_title(f'{h} sessions: '+('19' if h==5 else '4')+' disjoint outer windows')
        ax.set_xlabel('Brier loss · lower is better')
        for i,value in enumerate(vals[::-1]):ax.text(value+.003,i,f'{value:.4f}',va='center')
    fig.suptitle('NIFTY V3 · Better point scores, no independently established edge',fontsize=16)
    fig.savefig(OUT/'v3-model-comparison.png',dpi=150,bbox_inches='tight');plt.close(fig)
    report_names=['01_DATA_AUDIT.md','02_FEATURE_DISCOVERY.md','03_TARGET_RESEARCH.md','04_MODEL_EXPERIMENTS.md',
        '05_VALIDATION_AND_LEAKAGE_AUDIT.md','06_WEEKLY_FORECAST_RESEARCH.md','07_MONTHLY_FORECAST_RESEARCH.md',
        '08_MODEL_COMPARISON.md','09_FINAL_FORECASTS.md','10_NEXT_RESEARCH_PRIORITIES.md']
    base=OUT.relative_to(ROOT).as_posix()
    links='\n'.join(f'- [{name}]({base}/{name})' for name in report_names)
    index=f'''# NIFTY V3 research — 2025–2026

**No independently established predictive edge.** The controlled study improves
data coverage and some exploratory scores, but no weekly model/target comparison
survives the170-contrast simultaneous uncertainty family; monthly evaluation
contains only four non-overlapping outer windows. All historical dates are exposed.

New data: 70 successful Upstox histories, 465 official NSE FO sessions, all 465
underlying closes exactly corroborated, 129 features and 402 eligible origins.
Batch: 19 fitted configurations plus five deterministic controls, independently
trained at two horizons;532 configuration/fold evaluations, no failed configs;
six randomized-direction diagnostics;15 verification checks passed.

Exploratory weekly LightGBM:66.3% accuracy, Brier .22605; simultaneous improvement
interval versus strongest fixed baseline -.09303 to+.13941. The actual nested
direction selector scores63.0% with Brier .25612, worse than neutral .25.
Monthly selector:60.5%, Brier .24220; sample too small for a supported interval.
No model is called independently validated. Returns/volatility/tail leaders differ.

Final numeric scenarios are **NOT VALIDATED and late-issued** at{call['issued_at']},
using16November completed-session inputs after17November open. They are not fresh
premarket evidence: weekly direction estimate72.4% and monthly55.0%, with substantial
cross-target inconsistencies and under-covering distributions. Do not interpret
these as calibrated odds or a coherent trading signal.

![Comparison]({base}/v3-model-comparison.png)

{links}

[Final comparison CSV]({base}/final-model-comparison.csv) ·
[Frozen scenarios]({base}/09_FINAL_FORECASTS.json) ·
[Verification]({base}/verification.json)

Reproduce in a new directory:

```powershell
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast_v3.reproduce --out artifacts/nifty_forecast_v3/2026-11-17/reproduction-002
```

Exact initial fitted source is archived separately from documented guard hardening.
All earlier reports and forecasts are preserved. No trading settings, orders or
unattended automation were created. Source/target assumptions and skipped research
families are documented, and extending evidence into2027 requires a scope change.
'''
    (ROOT/'NIFTY_V3_RESEARCH.md').write_text(readable(index),encoding='utf-8')
    save('research-status.json',{'phases_01_to_09':'Completed feasible audit/experiments/validation with explicit limitations',
        'phase10':'NOT QUALIFIED: no supported forecasting skill to justify trading optimization',
        'phase11':'Late-issued as-of scenarios frozen; fresh premarket confirmation NOT AVAILABLE at current clock',
        'phase12':'All ten reports and traceable artifacts saved','independent_edge':'NOT DEMONSTRATED',
        'missing_fresh_evidence':'Prospective complete horizons; current 2025–2026 restriction limits monthly validation',
        'report_files':report_names})
    save('delivery-manifest.json',{'root_summary':{'path':str(ROOT/'NIFTY_V3_RESEARCH.md'),'sha256':sha(ROOT/'NIFTY_V3_RESEARCH.md')},
        'reports':{name:sha(OUT/name) for name in report_names},'frozen_forecast_sha256':sha(OUT/'09_FINAL_FORECASTS.json'),
        'current_source':{p.name:sha(p) for p in Path(__file__).parent.glob('*.py')},
        'research_docs':{p.name:sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ['.md','.txt']},
        'fitted_model_source_archive':str(OUT/'source-at-first-fit'),
        'machine_artifacts':{p.name:sha(p) for p in OUT.glob('*') if p.is_file() and p.suffix in ['.json','.csv'] and p.name!='delivery-manifest.json'}})
    print('Wrote all ten reports and',ROOT/'NIFTY_V3_RESEARCH.md',flush=True)
if __name__=='__main__':main()
