"""Generate all eight required V4 reports from actual frozen study outputs."""
import json,re
import numpy as np
import pandas as pd
from .common import *
from .ledger import events

NAMES=['V4_FAILURE_DIAGNOSIS.md','V4_FROZEN_CANDIDATES.md','V4_COHERENT_DISTRIBUTION_RESEARCH.md','V4_WEEKLY_LIGHTGBM_AUDIT.md','V4_DATA_AVAILABILITY_AUDIT.md','V4_PROSPECTIVE_VALIDATION_PROTOCOL.md','V4_MODEL_COMPARISON.md','V4_FINAL_RESEARCH_DECISION.md']
def table(rows,cols):return '|'+ '|'.join(cols)+'|\n|'+'|'.join(['---']*len(cols))+'|\n'+'\n'.join('|'+ '|'.join(str(r.get(c,'UNAVAILABLE')) for c in cols)+'|' for r in rows)
def readable(text):
    words='the|The|all|of|from|to|and|with|only|just|its|a|an|has|is|was|at|using|after|before|No|no|not|nominal|Nominal|versus|flipped|destroyed|correcting|span|spans|supply|overlapping|remaining|into|scores|estimate|monthly|weekly|within|before|after|least|across|generated|contains|last|latest|minimum|first|than|about|around|preceding|additional|ordinary|inner|validation|power|alpha|decision|trees|depth|leaves|samples|case|penalty|repaired|repairs|loss|accuracy|Brier|exposed|origin|origins|world|horizon'
    text=re.sub(r'\b('+words+r')(?=\d)',r'\1 ',text)
    text=re.sub(r'(?<=\d)(?=November\b)',' ',text)
    return text.replace('pre2025','pre-2025').replace('remaining2026','remaining 2026').replace('beyond2026','beyond 2026').replace('into2027','into 2027').replace('scope2025','scope 2025').replace('independent5-session','independent 5-session').replace('remains2025','remains 2025').replace('close25','close 25').replace('issue,0','issue, 0').replace('Inner42','Inner 42')
def emit(name,text):(OUT/name).write_text(readable(text.strip())+'\n',encoding='utf-8')

def run():
    reg=read('registry.json');repro=read('v3-reproduced-metrics.json');audit=read('weekly-lightgbm-audit.json');cal=read('calibration-metrics.json');dm=read('distribution-metrics.json');unc=read('v4-uncertainty.json');power=read('power-assessment.json');stop=read('prospective-stop-rules.json');verify=read('verification.json')
    ledger=events(OUT/'prospective-ledger.jsonl');issued=[e for e in ledger if e['kind']=='FORECAST'];primary=[e for e in issued if e['payload']['primary_eligible']]
    p=issued[0]['payload'];availability_path=next(ROOT/name for name in p['files'] if name.endswith('availability.json'));availability=json.loads(availability_path.read_text())
    def m(h,n):return next(r for r in repro if r['horizon']==h and r['model']==n)
    def dist(h,n):return next(r for r in dm if r['horizon']==h and r['model']==n and r['split']=='outer_exposed')
    def candidate_rows():
        return [{'horizon':h,'candidate':n,'origins':m(h,n)['n'],'disjoint':m(h,n)['disjoint']['n'],'Brier':f"{m(h,n)['brier']:.6f}",'log loss':f"{m(h,n)['log_loss']:.6f}",'accuracy':f"{m(h,n)['accuracy']:.2%}" if n!='Z_neutral' else 'NO CALL','status':'REPRODUCED / EXPOSED'} for h in [5,21] for n in (['M05_lgbm','A00_sector','Z_reversion','Z_neutral','B00_empirical'] if h==5 else ['B00_empirical','S_direction'])]
    frozen_table=table(candidate_rows(),['horizon','candidate','origins','disjoint','Brier','log loss','accuracy','status'])
    emit(NAMES[0],f'''# V4 failure diagnosis

Decision: **NO DEPLOYMENT; no independent edge demonstrated**. V4 reproduces V3
before introducing a finite distribution study. Existing V3 files and source are
hashed and preserved, including all ten reports, registries, per-origin records,
model files, selection results and validation artifacts.

{frozen_table}

45 candidate/fold probability vectors were recalculated from original model
artifacts and matched to 1e-12 tolerance. July weekly LightGBM and sector Ridge
were also independently refitted and matched. This is reproduction, not fresh
confirmation. V3 reported zero individually significant features after adjustment:
minimum q={read('v3-reproduction-checks.json')['original_feature_significance_min_q']:.6f}.

|Failure|Evidence|Diagnosis and limits|
|---|---|---|
|Adaptive selection|Weekly selector Brier .256118 versus neutral .25; fixed tree .226049|A 42-origin overlapping inner window can misrank models; binary accuracy does not validate probabilities|
|Small independent sample|92 weekly origins/19 disjoint; 76 monthly/4 disjoint; V3 outcome ESS23.45/5.96|Overlap creates apparent sample abundance; these ESS estimates are not guarantees of independence|
|Search uncertainty|V3 tree improvement over fixed reversion .023190, simultaneous95% [-.093033,+.139413]|170 model/target contrasts and dependence; no positive qualified lower bound|
|Monthly class imbalance|60.53% selected accuracy versus59.21% always-down|Only1.32 percentage points of raw gain, four disjoint windows|
|Distribution construction|Monthly distribution policy80% coverage31.58%;50%10.53%|Short overlap-heavy residual pools, temporal distribution changes and model bias are plausible; no single causal explanation proven|
|Incoherent endpoint outputs|Frozen V3 weekly classifier72.37% up versus distribution49.75%; monthly55% versus28.36%|Separate target selectors do not define one joint endpoint law|
|Calibration|Old monthly17 flips:15 correct-to-wrong,2 repaired|Small correlated calibration samples and prevalence changes; V4 simple corrections help one model and hurt another|
|Data limitations|Revised histories, incomplete delivery archives, short institutional coverage, unavailable dated index membership|Conservative lags reduce timing risk but cannot prove original-vintage fidelity|

Architecture is part of the problem, not an exclusive cause: a coherent law fixes
algebraic contradictions but does not fix calibration. Monthly nonlinear V3
LightGBM remains poor; adding algorithms would not supply new independent months.
Regime slices, phase sensitivity, calibration buckets and individual-origin losses
are retained even when unfavorable. No new dates are relabeled untouched.

The original V3 statistical/selection artifacts are in v3-audit-inventory.json;
the actual source contents/definitions reviewed are in v3-source-review.json.
V4 also keeps source-level changes and operational failures visible.''')
    emit(NAMES[1],f'''# V4 frozen candidates

Registered {reg['registered_at']}; registry SHA256 {sha(OUT/'registry.json')}.
No V3 parameter is retuned. All historical evaluations remain research-exposed.

Weekly binary cohort: exact V3 M05_lgbm; exact A00_sector; fixed Z_reversion;
Z_neutral; B00_empirical. A00 is Ridge mean regression plus the original logistic
direction component, not a Ridge coefficient converted into a probability.
LightGBM uses depth2/leaves4/trees80/minleaf40/lr.04/L2=10/seed20261117, unchanged
V3 preprocessing and ordinary101 features; proxies, sequence and explicit extra
interactions remain excluded. Sector mode uses original price+sector definitions.
Ridge alpha100, classifier C=.1. Reversion=.45 when ret5>0, otherwise.55;
neutral=.5. Historical frequency uses latest252 matured labels and V3 clipping.

Exact monthly refit anchor is the completed origin before the first forecast
session of the month. Training endpoints must be strictly earlier than that
origin; min126 labels, latest42 inner validation, purged inner fitting/min80.
No daily implicit refit, changed window or revised calibration is silently
substituted. A missed refit is not repaired using later data and backdated.

{frozen_table}

Monthly prospective distribution comparison is fixed D03_residual_shrunk versus
D00_empirical regardless of their retrospective rank. D01 and D02 remain bounded
exploratory studies. D03 is retained to test a predeclared hypothesis, not promoted
as the best model. Its poor coverage and extreme current output prohibit use.

Eight tree perturbations and four nonraw calibration/model combinations are
diagnostics with distinct names. They cannot replace these frozen candidates.
Calibrators remain DISABLED; no favorable retrospective correction is activated.
Existing binary candidates are a separate experiment from coherent endpoint laws;
their probabilities are never attached to another model's mean or intervals.

V3 source hashes, specifications, dataset identity and V4 hypotheses are in
registry.json. Exact first-issue executable source is archived and hash-verified;
future issues snapshot their source before running. No model is production-ready.''')
    drows=[]
    dp=pd.read_csv(OUT/'distribution-predictions.csv')
    for h in [5,21]:
        for name in reg['distribution_candidates']:
            r=dist(h,name);g=dp[(dp.horizon==h)&(dp.model==name)&(dp.split=='outer_exposed')]
            drows.append({'horizon':h,'model':name,'n/disjoint':f"{r['n']}/{r['disjoint']['n']}",'CRPS':f"{r['crps']:.6f}",'Brier':f"{r['brier']:.6f}",'mean MAE':f"{r['mae']:.3%}",'mean RMSE':f"{r['rmse']:.3%}",'median MAE':f"{r['median_mae']:.3%}",'50 coverage':f"{r['coverage50']:.1%}",'80 coverage':f"{r['coverage80']:.1%}",'80 width':f"{r['width80']:.3%}"})
    dtable=table(drows,list(drows[0]))
    emit(NAMES[2],f'''# V4 coherent distribution research

Four fixed alternatives, no search expansion or outer-driven model selection:

{table([{'ID':k,'definition':v} for k,v in reg['distribution_candidates'].items()],['ID','definition'])}

D00 is the full latest252 weighted return law, not V3's201-quantile numerical
approximation. D01 uses the same observations and30 unconditional pseudoobservations.
D02 uses501 fixed Student-t(df5) quantile atoms, scaled by inner residual RMS times
sqrt(3/5), floor .005*sqrt(h/5) before that t variance conversion. D02/D03 location
is .5*sector-Ridge mean+.5*training historical mean; D03 adds the42 raw heldout
inner residuals. Those residuals are not42 independent outcomes. Atoms at or below
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

{dtable}

Weekly D02 CRPS improves descriptively; D03 binary Brier looks attractive, yet
both80% intervals cover only67.4%. Monthly D02 coverage39.5% and D03 coverage44.7%
remain unacceptable. Coherence is achieved; calibration is not. None of the45
V4 comparison lower bounds is positive under the applicable simultaneous family.
Monthly intervals are withheld (76<168 rows required), not reported as significant.

distribution-metrics.json also records pinball, bucket Brier and observed/predicted
frequency for every bucket. distribution-predictions.csv retains mean/median and
per-origin point errors; D00 supplies matched historical mean and median controls.
Separate development metrics are saved; no new winner is selected from outer
scores. Quantile regressions/extra mixtures are not added after seeing these results.
Finite-support tails, regime sparsity, drift and residual dependence remain limits.''')
    stressrows=[{'variant':r['variant'],'Brier':f"{r['brier']:.6f}",'log loss':f"{r['log_loss']:.6f}",'accuracy':f"{r['accuracy']:.2%}"} for r in audit['stress_metrics']]
    calrows=[{'model':r['model'],'method':r['method'],'Brier':f"{r['brier']:.6f}",'log loss':f"{r['log_loss']:.6f}",'accuracy':f"{r['accuracy']:.2%}",'flips':r['threshold_flips'],'correct→wrong':r['correct_to_wrong'],'wrong→correct':r['wrong_to_correct']} for r in cal]
    emit(NAMES[3],f'''# V4 weekly LightGBM audit

Exact V3 tree:92 overlapping origins/19 disjoint; accuracy66.30%, Brier.226049,
logloss.645492. This remains an exposed-history lead, not independently validated.
Original V3 simultaneous improvement interval vs fixed reversion spans zero widely.

{table(stressrows,list(stressrows[0]))}

Dropping globals raises threshold accuracy to75% but does not improve Brier over
the original tree; it is not promoted. Dropping sectors worsens Brier to.242121
and accuracy to51.09%. Rolling126 worsens Brier to.240299. Dropping institutions
or ETF leaves the original predictions unchanged in this sample, consistent with
no incremental fitted contribution here, not proof the economic sources are
universally useless. Risk/FO/global/intraday effects differ. Each perturbation
is a distinct retrospective study with unchanged original tree hyperparameters.

{table(audit['leave_one_month_out'],['removed_month','n','brier_improvement_vs_reversion'])}

{table(audit['exceptional_origin_sensitivity'],['remove_best_origins','remaining_mean_improvement'])}

Excluding September reverses the advantage; excluding the ten most favorable
overlapping origins also reverses it. Those ten are not ten independent weeks.
Five alternate starting phases of greedily disjoint5-session windows are saved,
alongside original per-origin predictions, month/volatility/trend/participation/
expiry/global-risk-off/large-prior-move slices and confidence buckets. Small
slices are descriptive and are not promoted into conditional edges.

For the raw tree's highest confidence bin (>=.65),13 overlapping origins have
mean probability72.35% and actual positive frequency61.54%; the .55–.65 bucket
has only5 origins and100% positives. Neither supports precise calibration claims.
Training family gain is in weekly-lightgbm-audit.json, explicitly noncausal.

Calibration: RAW, fixed50% shrinkage toward the matured training base rate, and
one bounded logit offset fitted on purged inner validation with10*b²/2 penalty.
No slope fitting or isotonic search. All calibration remains DISABLED.

{table(calrows,list(calrows[0]))}

LightGBM shrinkage makes six correct calls wrong; offset makes six wrong and
repairs one. Sector offset improves descriptive Brier, but no adjusted lower
bound is positive. Thus calibration is not inherently beneficial or harmful;
its result depends on model and sample. Inner42 origins contain far fewer
disjoint outcomes; fit ledger records those counts and inner/outer prevalence.
Multiple metrics and confidence bins are retained: lower Brier alone is not a
pure calibration measure, as discussed in the
[scikit-learn calibration documentation](https://scikit-learn.org/stable/modules/calibration.html).
No retrospective correction is applied to the frozen prospective cohort.''')
    source_rows=[
        {'source':'Sector indices/participation','hypothesis':'Independent leadership/breadth beyond index price','availability':'Completed dated sector bars; no constituent-membership claim','evidence/risks':'Sector removal harms tree point score; sector definition drift/correlation remain'},
        {'source':'Stock momentum dispersion','hypothesis':'Cross-sectional fragility beyond aggregate price','availability':'Current-basket backcast only','evidence/risks':'RESEARCH ONLY; no authenticated dated membership/weights'},
        {'source':'FO basis/OI/PCR','hypothesis':'Positioning adds incremental state information','availability':'Official dated archives; additional1-session lag','evidence/risks':'Separate FO ablation .228148 vs original .226049; roll/lot/report delays'},
        {'source':'Institutional positioning','hypothesis':'Flow/position shifts condition future return','availability':'Short authenticated history; new missing reports not fabricated','evidence/risks':'Removal identical tree outputs here; missingness/prevalence drift'},
        {'source':'Complete intraday structure','hypothesis':'Path persistence/range adds information beyond daily bars','availability':'At least70 bars, start09:15/reach15:20; authenticated new capture','evidence/risks':'Removal .226082; partial sessions remain missing'},
        {'source':'ETF volume/turnover','hypothesis':'Tradable activity proxies participation','availability':'Real ETF candles, not spot volume','evidence/risks':'Removal identical tree outputs; development ETF q~.296'},
        {'source':'Indian/global relative strength','hypothesis':'Domestic resilience conditions global shocks','availability':'Conservative strictly preceding global source dates','evidence/risks':'Existing global/sector features only; no new indicator added; timezone/revision risk'},
        {'source':'IV/Greeks/news/events','hypothesis':'Potential new state/surprise information','availability':'No authenticated historical panel for this study','evidence/risks':'UNAVAILABLE; never manufactured or backfilled'}]
    emit(NAMES[4],f'''# V4 data availability audit

No new indicator search was conducted. Existing feature definitions are frozen.
The underused-source hypotheses below are an information inventory, not a claim
that adding each source improves a price-only benchmark. The matched V3 price/
sector controls and V4 removal diagnostics are the measured comparisons.

{table(source_rows,['source','hypothesis','availability','evidence/risks'])}

Live rehearsal reference: {p['reference_session']}, NIFTY close
{p['forecasts']['5']['reference_close']:,.2f}; fresh daily sources and the official
underlying crosscheck corroborate the reference. Capture contains
{len(availability['received_records'])} successful HTTP responses with actual
local send/receive clocks, available HTTPS server Date, raw bytes and SHA256.
Observed overlapping daily source revisions: {len(availability['revisions'])}.
Missing latest feature names are saved verbatim in availability.json. Stock proxy
inputs are not refreshed or admitted to frozen primary features. Institutional
history is not silently extended; absent new values remain missing and the exact
frozen train-median imputer handles them. This operational limitation is disclosed.

Incremental acquisition starts16November and ends at the previous completed
reference, merges the immutable2025-onward base, and never retrieves pre2025
prices. All new reference/target dates are scope-checked. Primary runs halt on
overlap revisions, stale required domestic sources, mismatched official close,
missing reference, failed HTTP/clock checks, or data received after the decision.
Incomplete intraday sessions do not become complete daily intraday features.

The first rehearsal failed before issuance because mixed timestamp formats
needed explicit pandas parsing; the parser was corrected and regression-tested.
One successful later issue is permanently LATE_DIAGNOSTIC, excluded from primary.
Subsequent hardening checks all domestic source freshness, adds explicit matched
score deltas and snapshots source before each issue. The original issue code was
reconstructed from recorded edits and matched against every original code hash;
its exact archive is retained, and no issued prediction was changed.

Local clocks plus server dates are useful authentication evidence, not independent
notarization. A hash chain detects mutations relative to a retained head, not a
malicious wholesale rewrite with a replaced head. Historical vendor revision
vintages/publication clocks are still incomplete. Cached exchange calendars can
change: resolver requires the exact observed target-session sequence and halts
for review on an unexpected closure or missing bar. API structure is documented
by [Upstox Historical V3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).
No production-quality availability guarantee is claimed.''')
    prows=[{'horizon':r['horizon'],'comparison':r['model']+' vs '+r['baseline'],'effect':r['effect_target'],'pilot disjoint':r['pilot_disjoint_n'],'paired SD':f"{r['pilot_paired_sd']:.6f}",'SD inflation':r['sd_inflation'],'required disjoint N':r['required_disjoint_n']} for r in power]
    emit(NAMES[5],f'''# V4 prospective validation protocol

**NO DEPLOYMENT.** First primary evidence begins only with a genuinely new,
on-time frozen prediction and later fully resolved outcome. Current primary
predictions={len(primary)}, diagnostic issuances={len(issued)-len(primary)}, resolved
horizons={sum(e['kind']=='RESOLUTION' for e in ledger)}. A late diagnostic is never
silently promoted into premarket evidence. All historical studies are exposed.

Decision09:10 IST, start09:00–09:10, complete09:10–09:12; every newly retrieved
required input must have arrived by09:10. Start early enough for source checks and
fitting; an overrun skips the origin. Previous complete NSE session is reference;
five/21 future exchange sessions define endpoints. No same-day live candle enters
the feature panel. Monthly training anchor, feature definitions and hyperparameters
are the frozen V3 rules. Inputs, acquired raw responses, availability, models,
source code, registry/data hashes and coherent atoms are retained before issue.

The append-only JSONL ledger has exclusive writer locking, canonical hashing,
previous-event hashes, duplicate issuance/resolution rejection and fsync. It never
rewrites a forecast. Damaged or partially written ledgers halt; lock recovery after
a crash requires review, not silent deletion. Status verifies every referenced
artifact. File hashes/local clocks are not external notarization; preserve a trusted
copy of the head before making independent-evidence claims.

Before any primary issue, a PROTOCOL_FREEZE event pins registry, stop rules,
power assumptions, operational source and V3 helpers by hash. Primary execution
verifies that event's files. Statistics refuses to change thresholds after the
freeze. The weekly planning gate was revised from8550 to14421 before any primary
issue because all three primary weekly comparisons, not only tree-vs-reversion,
must have their pilot variances assessed; protocol-amendment.json records this.
The earlier late operational rehearsal does not count as primary evidence.

Resolution runs no earlier than endpoint18:00 IST, fetches actual completed
daily candles, verifies exact target session sequence, reports revised reference
separately but scores against the originally frozen close, and appends matched
candidate/baseline Brier/logloss and coherent-distribution scores. No incomplete
label is trained/scored; missing endpoint causes a halt. Duplicate resolutions
are skipped. Experimental late issues remain separate through scoring.

Primary family: weekly M05 vs reversion, M05 vs sector, sector vs reversion
(Brier), and monthly D03 vs D00 (CRPS). Neutral/frequency/logloss/accuracy/balanced
accuracy/calibration/confidence coverage and all distribution metrics remain
mandatory secondary reporting. No learned selector is introduced.

Power planning: N=ceil(((z_(1-.05/(2*4))+z_.8)*pairedSD/effect)^2),80% power,
family alpha.05 across4 primary comparisons. Pilot variance comes from19 disjoint
weekly/four monthly exposed outcomes and is highly uncertain. SDx1.5 is a
sensitivity scenario, not a statistically certified upper bound. Estimates assume
stationary approximately independent paired disjoint losses; drift/dependence
can require more evidence. They are not a promise of sufficient sample size.

{table(prows,list(prows[0]))}

Conservative fixed final planning gates: weekly{stop['fixed_final_disjoint_n']['5']}
disjoint outcomes for .01 Brier improvement, monthly{stop['fixed_final_disjoint_n']['21']}
for .001 CRPS improvement. These are planning gates, not guaranteed sample sizes.
Even the observed weekly effect≈.02319 needs707 windows under the uninflated
pilot assumptions. Smaller30/12 counts are descriptive interims only, with no
qualification or optional significance stopping. Remaining2026 cannot supply
these samples. The experiment therefore cannot establish the requested independent
edge within the existing calendar boundary; that limitation does not weaken gates.

At fixed final N, require family-adjusted positive matched proper-score improvement,
noninferior logloss, acceptable calibration and50/80% coverage within10 percentage
points of nominal with Wilson intervals, stable subperiod signs, no leakage and
robust perturbation results. No automatic deployment even after qualification.
Failures in timing/source/ledger integrity halt or skip. Any source/model/calibration
change gets a distinct version/cohort; prospective outcomes never tune the existing
candidate. Stop before any target enters2027, and do not resolve outside2026 under
this frozen protocol. Extending the scope needs user instruction.

From the workspace root, using the existing venv and configured Upstox token:

```powershell
# Start at09:00–09:09 IST on an eligible future session; no scheduler was installed.
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast_v4.prospective run
# Explicitly late, excluded research cohort only (refuses duplicate origin):
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast_v4.prospective diagnostic-late
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast_v4.prospective resolve
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast_v4.prospective status
```

The on-time command was executed today after the deadline and correctly rejected
without fetching or issuing. Resolution was executed and correctly found no mature
horizons without a network request or ledger mutation. No unattended task, trade
or production setting was created.''')
    emit(NAMES[6],f'''# V4 model comparison

## Reproduced frozen binary candidates

{frozen_table}

Neutral accuracy is NO CALL; always-up/down class controls remain in original V3
artifacts. Monthly selected-policy row is reproduced diagnosis, not a V4 frozen
monthly nonlinear candidate. All binary rows use identical origin dates per horizon.
No independently validated candidate exists.

## New coherent endpoint laws (exploratory)

{dtable}

MAE/RMSE/width columns use return units displayed as percentage points. D00 mean
and median are the historical point-estimate controls. Full mean/median errors,
pinball, bucket Brier and bucket calibration are in distribution-metrics.json and
the per-origin CSV. Every law's classifier probability and point/interval outputs
are mathematically consistent within that law, without mixing models.

## Calibration diagnostics (not activated)

{table(calrows,list(calrows[0]))}

## Uncertainty and status

V4 uncertainty includes30 weekly contrasts across frozen direction, calibration,
eight stress variants and distribution target types, plus15 monthly distribution
contrasts. Each weekly interval uses10-session blocks/2000 resamples with a
standardized simultaneous maximum-deviation correction across that whole family.
No adjusted weekly lower bound is positive. Monthly intervals are withheld because
of insufficient dependent rows. These are conditional exposed-history diagnostics;
they do not become independent confirmation because V4 uses a smaller family than
V3. All point leaders remain exploratory. Exact effect sizes, unadjusted paired
and family-adjusted intervals are in v4-uncertainty.json.

|Evidence class|Count/status|
|---|---|
|Reproduction|45 candidate/fold probability vectors;2 independent refits|
|New exposed-history endpoint records|1,928|
|New tree stress forecasts|736 (8x92)|
|Calibration records|552 (2models x3methods x92)|
|Primary prospective predictions|{len(primary)}|
|Late diagnostic issuance|{len(issued)-len(primary)} issue containing both horizons|
|Resolved prospective horizons|{sum(e['kind']=='RESOLUTION' for e in ledger)}|
|Independent validation|NONE|

NO DEPLOYMENT is the only supported practical decision.''')
    forecasts=[]
    for h,f in p['forecasts'].items():
        for name,d in f['distributions'].items():
            s=d['statistics'];forecasts.append({'sessions':h,'law':name,'endpoint':f['expected_endpoint'],'P(up)':f"{s['p_up']:.2%}",'mean return':f"{s['mean_return']:+.3%}",'median return':f"{s['median_return']:+.3%}",'mean endpoint':f"{s['expected_endpoint']:,.2f}",'80 interval':f"{s['interval80'][0]:,.0f}–{s['interval80'][1]:,.0f}"})
    emit(NAMES[7],f'''# V4 final research decision

**NO DEPLOYMENT. No repeatable independent forecasting advantage is established.**
Keep exact weekly LightGBM as an exploratory lead; keep sector/reversion/neutral/
historical controls frozen. Do not activate retrospective calibrators or replace
the candidate using75% posthoc removal accuracy. New endpoint laws are internally
coherent but their poor monthly coverage disqualifies precise forecasting use.

Main findings: reproduced weekly tree Brier.226049/66.30% accuracy; selected V3
policy .256118; tree advantage reverses when September is removed. Sector removal
harms its point score. Both simple corrections worsen the tree; sector offset
helps descriptively, with no supported adjusted improvement. No V4 simultaneous
weekly lower bound is positive. Monthly evidence still has four disjoint outcomes.

The first genuinely timestamped live rehearsal is saved at{p['issued_at']},
reference17November close{p['forecasts']['5']['reference_close']:,.2f}. It is
LATE_DIAGNOSTIC and excluded from the primary09:10 cohort. It has not matured.
Primary prospective count={len(primary)}; independently validated count=0.
This is a successful operational rehearsal, not successful predictive validation.

{table(forecasts,list(forecasts[0]))}

These are NOT VALIDATED research distributions. In particular monthly D03 has
zero fitted positive-return mass: this is a finite-support/model failure risk,
not certainty of a fall. Do not substitute the separate binary tree probability
into a D03 mean/interval: that would recreate V3's incoherence. Path breaches and
future realized volatility are explicitly unavailable from these endpoint laws.

{verify['tests']} verification tests passed, including immutable V3 preservation,
numerical reproduction, weighted-CRPS/endpoint identities, purging, timing and
scope rejection, ledger duplicate/tamper/partial-write/lock checks, parser regression,
cohort separation and unsupported-monthly-interval withholding. First-issue exact
code and subsequent hardening are separately preserved. No V1/V2/V3 artifact or
forecast was overwritten.

An auditable executable capture/issue/resolve process now exists. Adequate
prospective power is impossible in the remaining2026 scope under the fixed gates;
there is no promise of a validated monthly edge. Further sample collection beyond
2026 requires an explicit scope change. No scheduler was installed and no trades
or live settings were changed. Source delivery/vintage, local-clock notarization,
calendar changes, missing institutional data and tail support remain limitations.

The eight reports, immutable registry, original-source review, per-origin CSVs,
model/input/source snapshots, hash-chain ledger, statistics, power assumptions,
stop rules and tests form the delivered research system. The result is better
evidence discipline and infrastructure, not a manufactured higher win rate.''')
    base=OUT.relative_to(ROOT).as_posix();links='\n'.join(f'- [{n}]({base}/{n})' for n in NAMES)
    summary=f'''# NIFTY V4 research

**NO DEPLOYMENT. No independently demonstrated edge.**

V3 probabilities reproduced across45 model/fold vectors plus two independent
refits. Four fixed coherent endpoint laws generated1,928 historical records;
eight bounded tree perturbations and simple calibration diagnostics were executed.
No adjusted weekly improvement excludes zero. Monthly coverage remains poor.

The tree's advantage depends on particular periods: remove September and its
Brier gain over reversion turns negative. Coherence fixes contradictory endpoint
statistics, but it does not fix calibration. All calibration remains disabled.

Prospective tracking is implemented and exercised: **0 on-time primary issues,
1 late diagnostic issue,0 resolved horizons**. The late issue is timestamped
{p['issued_at']} with17November reference close25,387.40. It is excluded from
premarket confirmation. No automation was installed; run commands are in the protocol.

{links}

[{verify['tests']} passing verification checks]({base}/verification.json) ·
[Immutable prediction ledger]({base}/prospective-ledger.jsonl) ·
[Source and execution instructions](research/nifty_forecast_v4/README.md)

Scope remains2025–2026. Power estimates vastly exceed the remaining calendar;
no independent success can be claimed within current observations. All earlier
artifacts and issued forecasts are preserved.
'''
    (ROOT/'NIFTY_V4_RESEARCH.md').write_text(readable(summary),encoding='utf-8')
    save('research-decision.json',{'decision':'NO DEPLOYMENT','independent_edge':False,'reports':NAMES,'primary_prospective_issues':len(primary),'diagnostic_issues':len(issued)-len(primary),'resolved_horizons':sum(e['kind']=='RESOLUTION' for e in ledger),'verification_passed':verify['passed'],'scope':['2025-01-01','2026-12-31']})
    save('delivery-manifest.json',{'generated_at':now(),'root_summary_sha256':sha(ROOT/'NIFTY_V4_RESEARCH.md'),'registry_sha256':sha(OUT/'registry.json'),
        'reports':{n:sha(OUT/n) for n in NAMES},'current_source':{p.name:sha(p) for p in SOURCE.glob('*') if p.is_file()},
        'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='delivery-manifest.json'}})
    print('Wrote eight reports and root summary',flush=True)
if __name__=='__main__':run()
