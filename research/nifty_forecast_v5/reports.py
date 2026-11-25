"""Fourteen V5 reports, complete hypothesis ranking, figures and delivery manifest."""
import json,re
from .common import *
from .models import SPECS
from .expansion import VARIANTS

REPORTS=['V5_DATA_UNIVERSE.md','V5_GLOBAL_MARKET_RESEARCH.md','V5_INDIAN_MARKET_INTERNALS.md','V5_DERIVATIVES_INTELLIGENCE.md','V5_CROSS_MARKET_FEATURES.md','V5_ADVANCED_MODEL_EXPERIMENTS.md','V5_CONDITIONAL_SIGNALS.md','V5_VALIDATION_AND_STRESS_TESTS.md','V5_SIGNAL_RANKING.md','V5_WEEKLY_MODEL_RESEARCH.md','V5_MONTHLY_MODEL_RESEARCH.md','V5_FINAL_COMPARISON.md','V5_RESEARCH_CONCLUSIONS.md','V5_NEXT_HYPOTHESES.md']
def table(rows,columns):return '|'+ '|'.join(columns)+'|\n|'+'|'.join(['---']*len(columns))+'|\n'+'\n'.join('|'+ '|'.join(str(r.get(c,'UNAVAILABLE')) for c in columns)+'|' for r in rows)
def emit(name,text):
    text=re.sub(r'\b(the|The|all|All|of|from|to|and|with|only|has|is|was|at|using|after|before|No|no|not|nominal|versus|monthly|weekly|within|least|across|generated|contains|last|latest|first|than|about|around|additional|inner|validation|power|alpha|decision|depth|leaves|accuracy|Brier|origin|origins|horizon|rows|beyond|into|expanded|retains|includes|produced|minimum|about|population)(?=\d)',r'\1 ',text)
    text=re.sub(r'(?<=\d)(?=November\b|December\b|April\b|July\b)',' ',text)
    text=re.sub(r'(?<=%)(?=\d)',' ',text)
    (OUT/name).write_text(text.strip()+'\n',encoding='utf-8')
def run():
    metrics=read('metrics.json');unc=read('uncertainty.json');stability=read('stability.json');rank=read('signal-ranking.json');inv=read('data-inventory.json');defs=read('feature-definitions.json');reg=read('registry.json');fits=read('experiment-registry.json');discovery=read('discovery-summary.json');call=read('experimental-forecasts.json');verify=read('verification.json');controls=read('legacy-matched-controls.json')
    def m(h,n):return next(r for r in metrics if r['horizon']==h and r['model']==n)
    def compare(h,a,b,metric):return next(r for r in unc if r['horizon']==h and r['model']==a and r['baseline']==b and r['metric']==metric)
    def comp_rows(h,names):return [{'model':n,'n/disjoint':f"{m(h,n)['n']}/{m(h,n)['disjoint']['n']}",'Brier':f"{m(h,n)['brier']:.6f}",'logloss':f"{m(h,n)['log_loss']:.6f}",'accuracy':f"{m(h,n)['accuracy']:.2%}",'balanced':f"{m(h,n)['balanced_accuracy']:.2%}",'CRPS':f"{m(h,n)['crps']:.6f}",'mean MAE':f"{m(h,n)['mae']:.3%}",'RMSE':f"{m(h,n)['rmse']:.3%}",'50 cover':f"{m(h,n)['coverage50']:.1%}",'80 cover':f"{m(h,n)['coverage80']:.1%}"} for n in names]
    def comparisons(h,pairs):
        return [{'hypothesis':hyp,'metric':metric,'gain':f"{compare(h,a,b,metric)['mean_improvement']:+.6f}",'simultaneous95':compare(h,a,b,metric)['simultaneous95']} for a,b,hyp in pairs for metric in ['brier','crps']]
    def short_table(h,names):
        rows=comp_rows(h,names);return table(rows,list(rows[0]))
    # A hypothesis ranking distinguishes a good whole model from a source's incremental value.
    hypotheses=[('Indian native internals','I00','P00','Genuine sector/broad index state adds participation/leadership information','25 native index/VIX histories; no present-day stock weights','Freeze native-only coherent controls; independently test sector leadership'),
      ('New indices beyond legacy','I00','I01_legacy','Broad/style/size information unavailable in old sector block','New native broad/size/style indices','Separate native breadth innovation from coherent-law changes'),
      ('Mid/small-cap increment','I00','I03_nosize','Size-segment participation predicts subsequent NIFTY movement','Native midcap/smallcap indices','Ablate individual size families on new/development evidence'),
      ('Global increment','C00','I00','Global-to-India transmission adds information beyond domestic internals','13 authenticated Upstox globals; no available bond/FRED panel','Investigate source timing and low-dimensional regional shocks, not a larger same-data sweep'),
      ('Derivatives increment','D01','C00','Positioning conditions future returns beyond equity/global state','467 dated NSE FO sessions, extra1-session lag','Separate price/OI/expiry mechanisms on fresh or development-only evidence'),
      ('ETF activity increment','L01','I00','Activity and cross-asset ETF prices improve conditional return law','NIFTYBEES plus four gold/silver/foreign-equity ETFs','Separate volume from metal/foreign-equity exposure'),
      ('Sector transfer','T00','I00','Shared security dynamics transfer to NIFTY','Nine native sector panels; date-grouped weights','Investigate why pooled coefficients fail before adding larger panels'),
      ('Stock transfer','T01','I00','Shared stock dynamics transfer to the index','150 current stock identities; survivorship-exposed','Authenticate historical investable universe/corporate actions'),
      ('Joint factors','F00','C00','Common factors remove redundant cross-market dimensions','Five train-only principal components','Try targeted factors only under a separately registered study'),
      ('Rolling loading adaptation','F01','F00','Recent loadings adapt changing asset relationships','126-row rolling PCA, regression on prior observations','Formal dynamic state models require identification/independent evidence'),
      ('Nonlinear joint states','N01','C00','Shallow conditional leaves capture interactions','64 ExtraTrees,depth3,minleaf30','Keep kernel/additive failures; investigate stable mechanisms'),
      ('Sequence evolution','S00','C00','Recent global/participation sequences add state-change information','Structured1/3/5-session lags','No neural expansion justified by the current date count'),
      ('Historical analogues','A00','E00','Similar joint states have informative return laws','Cosine40-neighbor joint Indian/global/FO state','Study rare-state behavior with fixed distance/coverage protocol'),
      ('Auxiliary horizons','M00','P00','Shared normalized1/3/5/21-session tasks help primary horizons','Date-grouped multi-horizon targets','Test auxiliary-task relevance rather than assuming transfer'),
      ('Current-stock breadth proxy','BR00','C00','Wider participation improves index forecasts','150-current-name breadth, research-only','Acquire dated membership; no index contribution claims'),
      ('Stock volume proxy','L03','L02','High-activity participation provides a liquidity signal','150-current-name volume ratios, research-only','Authenticate sample selection and separate ETF effects')]
    hrows=[]
    for h in [5,21]:
        for title,a,b,rationale,sources,nextstep in hypotheses:
            aa=m(h,a);bb=m(h,b);db=bb['brier']-aa['brier'];dc=bb['crps']-aa['crps'];state='EXPLORATORY LEAD' if db>0 and dc>0 else 'REJECTED' if db<0 and dc<0 else 'INCONCLUSIVE'
            if title in ['New indices beyond legacy','ETF activity increment']:state='INCONCLUSIVE' # Small/mixed incremental evidence is not a family-level claim.
            ss=[s for s in stability if s['horizon']==h and s['model']==a and s['test']=='leave_month_out' and s['metric']=='crps'];frac=float(np.mean([s['mean_improvement_E00']>0 for s in ss]))
            hrows.append({'horizon':h,'hypothesis':title,'candidate':a,'incremental_baseline':b,'rationale':rationale,'sources':sources,'timeframe':'Daily completed-session/09:10 historical reconstruction',
                'coverage':'2025–2026 only; feature origins2Apr2025–17Nov2026','origins':aa['n'],'disjoint':aa['disjoint']['n'],'brier_increment':db,'crps_increment':dc,
                'leave_month_crps_positive_vs_empirical_fraction':frac,'status':state,'complexity':reg['specifications'].get(a,{}).get('kind','Registered ablation/ETF extension'),
                'missingness_leakage_risk':'Revised publication vintage; CURRENT-BASKET SURVIVORSHIP' if a in ['BR00','T01','L03'] else 'Actual old source receipt/revision clocks unverified; conservative joins',
                'uncertainty':'No monthly CI; exposed-history simultaneous intervals in uncertainty.json; no independent confirmation','next_experiment':nextstep})
    save('hypothesis-ranking.json',hrows);pd.DataFrame(hrows).to_csv(OUT/'hypothesis-ranking.csv',index=False)
    # Data universe report.
    inventory=[{'identity':r['name'],'family':r['family'],'valid':r['valid'],'first':r['first'],'last':r['last'],'invalid':r['invalid'],'duplicate':r['duplicates']} for r in inv]
    families=pd.DataFrame(defs).groupby('family').agg(features=('name','count'),median_missing=('missing_fraction','median')).reset_index()
    emit(REPORTS[0],f'''# V5 data universe

V5 independently acquired189 Upstox identities:25 domestic index/VIX series,
13 actual listed global instruments,150 stocks and NIFTYBEES; all189 requests
succeeded. A registered liquidity extension acquired four additional ETFs,
bringing the successful daily-price universe to193 instruments. The stocks are
the old50 current names plus the alphabetically first100 eligible current
Nifty500 names outside that basket. This is an explicitly survivorship-exposed
research sample, not historically authenticated index membership or a claim that
these are the150 most liquid stocks. No current index weights are invented.

Official FO coverage is467 compact sessions (V3's465 plus17/18November). Official
18November index OHLC and cash-market bhavcopy resolve the broker's delayed
daily publication. NIFTY reference25,227.95 matches the FO underlying exactly.
All25 domestic identities are explicitly mapped to the official index names;
index/cash source dates and OHLC identities are checked. Published index Volume
is constituent-aggregate activity, not traded NIFTY spot volume, and was not
mixed with genuine ETF traded volume.

The main frozen historical matrix has403 origins,176 features,2Apr2025–17Nov2026;
the separate authenticated latest-input snapshot extends through18Nov. Main
historical feature/price prefixes remain numerically unchanged. Additional ETF
and research-only stock-volume features live in separate files, not a silently
changed initial dataset. Median missingness of primary families is measured below;
missing values use train-only medians, not future/backward fills.

{table(families.round(5).to_dict('records'),['family','features','median_missing'])}

The available global catalogue contains S&P500, Dow Jones, FTSE100,DAX,CAC40,
Hang Seng,Nikkei225,US Tech100,GIFT NIFTY,US30,Brent,WTI and USD/INR. US Tech100 is
the provider's instrument, not relabeled Nasdaq Composite or a pure technology
sector index; US30/GIFT/commodity instruments retain futures/CFD ambiguity and
roll risks. There is no authenticated Russell,Shanghai,CSI,KOSPI,Taiwan,US sector,
credit-spread,DXY,USVIX or yield panel in the successful Upstox downloads.

Four bounded public FRED downloads (DGS10,DGS2,DTWEXBGS,VIXCLS) failed; correct
official Treasury2025/2026 feed probes timed out. They are documented as unavailable,
not zero-valued features or failed economic theories. No key/access restriction
was bypassed. Gold/silver and US/HongKong exposures were obtained as actual
INR-traded ETFs; their returns contain currency/tracking/premium effects and are
not commodity spot or foreign exchange closing-index observations. Historical
IV surfaces/Greeks/news sentiment were not manufactured.

Read-only database schema/method/identity coverage is in database-audit.json;
the current instrument masters and official current membership list are retained
with URLs/acquisition clocks/hashes. These catalogues are metadata, not historical
membership proof. Complete V1–V4 reports/source were read and2727 existing artifacts
hashed for preservation; V4's ledger/protocol remain unchanged.

Ranked information priorities: (1) native sector/broad index leadership, strongest
usable lead; (2) genuine ETF activity/cross-asset proxies, mixed incremental evidence;
(3) global regional/relative-state structure, available but no incremental gain;
(4) authentic FO interactions, available but no increment; (5) wider stock panels,
rich but survivorship-exposed and poor transfer; (6) bond/USD-risk/IV/news information,
not currently authenticated/accessed as historical panels.

Instrument documentation: [Upstox instruments](https://upstox.com/developer/api-documentation/instruments/),
[Historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).
Official latest input URLs are in latest-sources/acquisition.json; FRED/Treasury
failures and attempted bounded URLs are retained separately. No pre2025 market
observations or warmup state enter the study.

{table(inventory,['identity','family','valid','first','last','invalid','duplicate'])}''')
    gtable=short_table(5,['E00','G00','I00','C00','F00','F01','C01_delayglobal'])
    emit(REPORTS[1],f'''# V5 global-to-NIFTY research

New research beyond V4: all13 actually listed global instruments, regional
dispersion/relative strength/correlation evolution, causal lead/lag tests,
train-only joint factors, global-only versus Indian-only versus joint models,
and an extra-session global/relationship delay stress. Global inputs are not
assumed useful merely because they expand the feature matrix.

{gtable}

{short_table(21,['E00','G00','I00','C00','F00','F01'])}

Global-only ridge is worse than unconditional history at both horizons. Combined
weekly C00 is better than a weak price-only model but worse than Indian-only I00;
the incremental global claim must be judged against I00, not just neutral or price.
Monthly joint/factor models are poor. Static PCA5 and rolling126 PCA5 do not rescue
the predictive relationship. They estimate variance factors, not guaranteed return
predictors. Rolling PCA is a causal loading-adaptation proxy, not a fully identified
latent state-space dynamic-factor model.

{table(comparisons(5,[('C00','I00','Global increment beyond Indian internals')]),['hypothesis','metric','gain','simultaneous95'])}

Development-only lead/lag discovery evaluated{discovery['tests']} feature/lag/target
combinations, lags0/1/3/5, NIFTY and Indian IT targets at5/21 sessions; labels matured
before1July2026.200 separated circular-shift nulls per test and BH across the entire
family produced minimum q={discovery['min_bh_q']:.6f}, with{discovery['q_under_05']}
q<.05. These are predictive-association diagnostics, not causation or Granger proof.
The US Tech100/Indian IT proxy relationship was actually tested; bond-yield and
dollar-index hypotheses were not testable because those historical downloads failed.
Oil/FX, global weakness conditional on participation, regional dispersion and
rolling correlation changes were included as explicit hypotheses, not findings.

Top development associations, their half-sample signs, source features and lags
are in global-lead-lag-discovery.csv; no final outer feature ranking selected the
initial models. Additional retrospective stages were registered before their own
tests and remain exposed. No accessible global source has established independent
incremental predictive value in this study.''')
    emit(REPORTS[2],f'''# V5 Indian internals and cross-sectional learning

Native historical index participation is distinct from a current stock basket.
The primary internal block uses23 domestic price indices (excluding spot and VIX),
relative5/21 returns, participation, dispersion, concentration, leadership-rank
persistence and defensive/cyclical rotation. Broad100/200/500,Next50 and size/style
indices materially expand the original sector-only information set.

{short_table(5,['P00','I00','I01_legacy','I02_newindices','I03_nosize','I04_delay','I05_rolling126','T00','T01','BR00'])}

The weekly I00 Brier.186099/76.09% accuracy is an exposed-history lead. Dropping
mid/small-cap indices improves Brier to.182047, so the gain cannot be attributed
to adding every size series. Legacy-sector-only .188888 remains strong; the exact
increment from new indices is small/uncertain. One-session internal delay and
rolling126 reduce the point advantage; neither is quietly substituted into a
frozen earlier candidate. Current-stock breadth does not improve the joint model.

{table(comparisons(5,[('I00','P00','Native internals beyond index price'),('I00','I01_legacy','New indices beyond old sectors'),('I00','I03_nosize','Mid/small-cap contribution')]),['hypothesis','metric','gain','simultaneous95'])}

Transfer learning was actually executed:3,627 native sector-date rows from nine
sectors and60,450 stock-date rows from150 current stock identities. Shared Ridge
models use own return/trend/RV and common global/participation context, normalize
targets by origin RV*sqrt(h), and give all securities on a date total weight1.
Training dates and label endpoints are grouped/purged by date, never random stock
rows. Only matured endpoints enter any fit; no current membership weights aggregate
security forecasts into a purported historical NIFTY basket. Targets above50%
absolute return are quarantined in transfer training; this is a known tail/sample
selection limitation, not proof such moves cannot occur. No pre2025 state is used.

T00/T01 fail to improve the native internal model; stock-date abundance did not
create extra independent NIFTY outcomes. T01 and BR00 remain survivorship-exposed,
ineligible for the selected primary experimental systems. Monthly transfer is
especially poor. Native index composition may itself change historically, but
the published index series is used directly; today's stock membership is not
backcast as the index universe.''')
    emit(REPORTS[3],f'''# V5 derivatives intelligence

467 dated official archives retain actual contract/expiry identities. Futures
basis, common-scale OI changes, same-contract/lot OI evolution, roll flag, DTE,
log OI/volume PCR, concentration/wall/maxpain distances and matched-contract PCR
changes follow the audited V3 definitions, with an extra domestic-session lag.
Absolute contract IDs/OI/lot levels are not falsely treated as normalized predictors.

New engineered relationships: price x OI change; concentration x origin RV;
positioning divided by1+DTE; causal63-session basis and OI-change z-scores.
These explore trend/positioning/expiry/volatility hypotheses. They do not infer
writer intent or claim basis is more than carry. No historical IV/Greeks are added.

{short_table(5,['P00','D00','I00','C00','D01','D02_rawonly'])}

{short_table(21,['E00','D00','C00','D01','D02_rawonly'])}

{table(comparisons(5,[('D01','C00','Derivative increment beyond joint state')]),['hypothesis','metric','gain','simultaneous95'])}

Price-plus-derivatives alone is weak; adding the derivative block to joint state
does not improve Brier or CRPS. Removing the five new transformations does not
uncover a convincing advantage. This rejects these tested implementations, not
all derivatives information. Institutional positioning remains short/incomplete
in the prior audit and was not fabricated into a full2025 panel. Near-expiry and
high-volatility conditions are tested with matched exact-condition baselines in
the conditional study; no narrow subgroup is promoted as an independent edge.''')
    emit(REPORTS[4],f'''# V5 cross-market features and time alignment

The initial matrix has176 features:13 price/risk,52 native internals,52 aligned
global returns,19 derivative/transformed,18 structured lags,12 fixed cross-market
relationships and10 research-only stock-breadth features. Separate liquidity
files add15 ETF and three research-only wider-stock volume features.

Global relationships include equal-weight available-market return/dispersion,
Indian-minus-global relative returns, oil x USD/INR, global return x participation,
US Tech100 versus Indian IT performance, Asia-minus-Europe divergence, equity/oil
divergence,21-session Indian/global and inter-global correlations, correlation
changes and cross-asset movement variability. No huge interaction-grid optimizer
was used. These features can be correlated and are not independent signals.

Premarket historical clock09:10 IST follows the completed Indian reference.
Known spot markets use IANA NewYork/London/Berlin/Paris/HongKong/Tokyo exchange
closing clocks plus a conservative two-hour publication allowance, handling DST.
Foreign daily bar dates remain source-session assumptions; receipt/revision
history is not authenticated. Unknown futures/CFD/FX conventions use a full extra
UTC-day completion buffer (source midnight+2days), not a fabricated exact close.
Actual available bars/holidays are respected by as-of joins; gaps over seven days
are missing, not indefinitely forward-filled. All assumed completion timestamps
are <=the recorded historical decision. No actual as-delivered vintage is claimed.

The extra global-delay stress C01_delayglobal adds an Indian-session lag to the
global/relationship block and stays exploratory. European/US close assumptions
and daily-anchor semantics remain a risk even with timezone-aware code; causal
code alone does not authenticate vendor publication history.

ETF proxies add GOLDBEES,SILVERBEES,MON100,HNGSNGBEES and NIFTYBEES returns,
realized variation and volume/prior21median. Gold/silver exposure is INR ETF
exposure, not spot; foreign ETFs carry tracking/premium/currency effects. The
price-only, native-only and joint liquidity ablations isolate the whole new block,
not each ETF's causal effect. Wider-stock median activity/active advances/volume
dispersion remain research-only current-basket proxies.

New-information attribution uses a2x2 experiment with cached estimators: exact
old sector features versus new native internals, and old V4 residual-shrunk law
versus V5's65% conditional/35% unconditional law. It is necessary because a better
forecast construction must not be advertised as proof of a new data source.

{short_table(5,['AT00_old_newlaw','AT01_new_oldlaw','I00'])}

The old/old reference is V4 D03 Brier.206257/CRPS.011882. Both changed feature
structure and changed distribution construction contribute descriptively; neither
crossed cell is independent validation. Additional global/broad/ETF increments
must still be judged with their matched ablations and uncertainty.''')
    algorithms=[{'ID':n,'mechanism':s[0],'inputs':s[1],'hypothesis':s[2]} for n,s in SPECS.items()]
    emit(REPORTS[5],f'''# V5 advanced model experiments

The program ran20 initially registered configurations, eight registered native/
timing/window follow-ups, four registered liquidity extensions and two cached
feature/law attribution cells:34 distinct evaluated systems, independently at
5/21 sessions. The searchable registry records{len(fits)} configuration/fold
attempts:11 original Indian-only-forest metadata failures are preserved and all11
were repaired without changing model parameters. Attribution evaluations reuse
cached estimators, so the ledger count is not the number of elementary model fits.

{table(algorithms,['ID','mechanism','inputs','hypothesis'])}

Regularized Ridge alpha100; train-only median/standardization/clipping±5;
PCA5(static or causal recent126 loading fit); additive quadratic splines with
three knots; RBF KernelRidge alpha10,gamma1/d; ExtraTrees64/depth3/minleaf30/
maxfeatures.7; cosine/L1 analogues40 neighbors; causal global-sign x training-
median-RV regime distributions with50 unconditional pseudoobservations.
Most endpoint laws mix65% conditional heldout-residual or leaf/analogue mass
with35% unconditional historical mass. This reduces unsupported finite-support
certainty but is a fixed heuristic, not certified calibration. All parameters
were fixed within each registered batch; no automatic hyperparameter search.

Multi-horizon M00 shares1/3/5/21 targets normalized bysqrt(h) with a log-horizon
coordinate, date-balanced tasks and individually matured labels. It fails to
improve primary horizons. Structured cross-market lags were actually tested.
Small temporal CNN/RNN/attention/Transformer models were not run:403 daily origins
and four disjoint monthly windows cannot validate an additional neural search.
Millions of intraday snapshots do not change that. XGBoost/CatBoost duplicate
sweeps were not added; new additive/kernel/conditional-forest mechanisms already
test nonlinear alternatives. Formal HMM/Markov and latent dynamic-factor models
were not claimed: causal observed regimes and rolling factors are narrower tests.

V5 did not stop after failed global/transfer/factor results. It followed the
domestic lead with registered source ablations and then genuinely new ETF/liquidity
inputs. Every inspected expansion adds to the multiple-comparison family. Failed
results remain in experiment-registry.csv/json, with exact model artifact hashes.
No V4 candidate, source code, protocol or prospective ledger was modified.

Full numerical reproduction completed in a new isolated directory without market
data requests: all34 systems and11,992 historical records matched. Probability
and Brier differences were exactly0; maximum CRPS difference was below7e-18.
This verifies repeatability, not independent validation. Original failed attempts
remain preserved; corrected code need not repeat the metadata bug in the replay.
Nonlinear comparisons also differ in representations, so a losing kernel/additive
implementation does not identify an architecture's universal causal weakness.''')
    cond=read('conditional-hypotheses.json');selected=[]
    for r in cond:
        if r['horizon']==5 and r['model'] in ['I00','L01']:
            selected.append({'model':r['model'],'condition':r['condition'],'n/disjoint':f"{r['n']}/{r['disjoint_n']}",'coverage':f"{r['coverage']:.1%}",'accuracy':f"{r['metrics']['accuracy']:.1%}",'Brier gain vs condition':f"{r['brier_improvement']:+.5f}",'CRPS gain':f"{r['crps_improvement']:+.6f}"})
    emit(REPORTS[6],f'''# V5 conditional signals

Five explicitly registered conditions: global weakness+narrow participation,
global weakness+broad participation, high volatility+near expiry, concentrated
rally, and rising oil+USD/INR+high volatility. Medians use training observations;
participation .5, near expiry<=2days, and trend>originRV*sqrt21 are fixed rules.
No progressively narrower subgroup search was conducted.

The exact same condition's matured historical return law plus30 unconditional
pseudoobservations supplies the regime-aware benchmark. conditional-training-
counts.json reports total/conditional/disjoint training counts for every fold.
320 matched model/condition/horizon comparisons were inspected across the32
predictive systems before the two attribution controls. Full per-origin baseline
records are retained. Conditions do not create independent monthly samples.

{table(selected,list(selected[0]))}

These rows are descriptive, not selected conditional recommendations. Sparse
conditions and overlapping targets can produce impressive accuracy by chance.
Per-condition coverage, date counts, disjoint counts, proper-score improvements
and train-only baseline are reported even when adverse. Individual subgroup
block intervals are explicitly unadjusted and cannot qualify a conditional edge;
no subgroup wins the retrospective qualification standard through these scores.

Broader month/volatility/trend/global-risk/participation/expiry slices and fixed
abs(P(up)-.5)>=.15 selective forecasts are in conditional-signals.json. The
confidence threshold was not tuned to outer outcomes. Calibration buckets and
matched regime controls accompany accuracy. Any promising interaction needs a
separate frozen comparison on new evidence; no outcome-defined regime is used.''')
    positive=[r for r in unc if r['simultaneous95'] and r['simultaneous95'][0]>0]
    stressrows=[{'model':r['model'],'metric':r['metric'],'gain vs empirical':f"{r['mean_improvement_E00']:+.6f}",'gain vs prior':f"{r['mean_improvement_prior']:+.6f}",'prior':r['prior_baseline']} for r in stability if r['horizon']==5 and r['model'] in ['I00','I03_nosize','L01'] and r['test']=='leave_month_out' and r['excluded']=='2026-09']
    emit(REPORTS[7],f'''# V5 validation and stress tests

Only2025–2026 observations; all historical dates remain research-exposed. No
random seed, alternate split or new source vintage creates independent evidence.
The main comparison uses identical V3/V4 outer origins:92 weekly/19 disjoint,
76 monthly/four disjoint. Outcome-ACF effective sample is about23.45/5.96;
disjoint and effective-size counts are diagnostics, not independence guarantees.
The updated historical NIFTY closes match old source closes exactly (max0points).

Monthly refits follow original prequential origins, matured endpoints strictly
before refit origin, min126 fitting labels, latest42 inner residual origins and
purged inner fitting. Preprocessing/PCA/correlation thresholds are trained within
past data. Sector/stock panels and auxiliary tasks are grouped by date and label
maturity; a thousand same-date instruments are not a thousand NIFTY outcomes.

916 paired comparisons across both horizons;458 contrasts per horizon include
all34 systems, five proper/point scores, unconditional and strongest prior V4
benchmarks, fixed neutral/reversion, and explicit source ablations. Weekly intervals
use10-session blocks,2000 resamples and standardized max-deviation family adjustment.
Monthly intervals are withheld because76<168 rows needed for the42-session block.
The strongest prior benchmark was itself identified on exposed historical scores;
that postselection is disclosed rather than treated as untouched evidence.

{len(positive)} adjusted weekly comparison lower bounds are positive: improvements
against E00, neutral, or the weak V5 price-only model. **None establishes positive
adjusted improvement over the strongest prior V4 coherent model.** No adjusted
CRPS superiority qualifies the leaders; no model becomes independently validated.
These are conditional bootstrap intervals with finite-sample/nonstationarity risks,
not a guarantee that nominal familywise coverage is exact for this short history.

September exclusion (explicitly distinguishes empirical from stronger V4 controls):

{table(stressrows,list(stressrows[0]))}

The new internal lead survives September exclusion descriptively, unlike the
earlier tree's reversion-relative result. All individual months, alternate starting
phases of disjoint windows and deletion of1/3/5/10 favorable overlapping origins
are saved. Overlap means deletion counts are not counts of independent weeks.
Timing lag, size removal, legacy-only, global-delay and rolling126 are separate
registered stress configurations, not quietly retuned parameters.

{table(read('negative-controls.json'),['horizon','seed','n','brier','crps','accuracy'])}

Randomized matured training labels do not reproduce the lead. Development lead/lag
BH family has976 tests and no q<.05. Conditional subgroups form a separate
descriptive family and are not used for qualification.

{verify['tests']} verification tests passed: complete V1–V4 preservation/ledger,
source/model/dataset hashes, same evaluation dates/outcomes, mature/embargo labels,
DST/global availability, hostile future-source perturbations, registered and
aliased future-oracle rejection, independent native-model refit, weighted CRPS,
fresh-source prefix identity/official close, coherent probabilities/buckets/prices,
pre-target issue, unfinished-US-close exclusion, exact issued source archive,
research-only proxy exclusion, original failure/repair records and monthly-CI guard.

Schema/availability/maturity guards were added after discovery fits as documented
hardening. Exact initial fit code and exact issued code are separately archived;
an independent I00 refit verifies the same numerical forecast. No settings changed
to improve a score. Metadata error repair concerned an unused global field in an
Indian-only forest, not a new outcome-selected architecture. Sources still lack
complete historical actual receipt/revision proof; these limits cannot be tested
away. No trades, deployment, V4 ledger changes or automatic schedule occurred.

The complete34-system historical replay was executed from frozen inputs in a new
directory; all11,992 rows reproduced numerically. full-reproduction.json records
all tolerances/differences. An initial replay packaging error omitted the dataset
manifest, failed before fitting, and was fixed in a new retained directory.
The frozen-forecast manual scorer was exercised before maturity and correctly
made no network request or ledger mutation. A separately timestamped baseline
supplement was frozen before the first target session without editing the issue.
Later scoring appends only to V5's own evaluation ledger on matched target dates.''')
    rankrows=[{'horizon':r['horizon'],'model':r['model'],'status':r['status'],'ranking score':round(r['ranking_score'],4),'CRPS gain%':round(100*r['relative_crps_gain'],2),'Brier gain%':round(100*r['relative_brier_gain'],2),'leave-month positive':f"{r['leave_month_crps_positive_fraction']:.0%}",'proxy':r['research_only']} for r in rank]
    emit(REPORTS[8],f'''# V5 signal ranking

Rank whole systems separately from incremental information hypotheses. A combined
model can beat unconditional history while an added global block harms the Indian
control. A useful whole-system point score does not prove a source's incremental
value or a feature's causal influence.

System ranking score=.4*relativeCRPSgain+.3*relativeBriergain+.2*positive leave-month
CRPS fraction-.1*(50/80coverage absolute gaps)-.1 for survivorship-only systems.
This is a transparent descriptive prioritization rule, not a significance level
or a portfolio weight. Gains are relative to E00. Source incremental comparisons
use the actual parent model and are kept in hypothesis-ranking.csv/json, including
rationale/source/timeframe/coverage/horizon/counts/stability/risk/complexity/uncertainty/
next experiment. Status REJECTED applies to a tested implementation, not proof
that its economic family can never contain a signal.

{table(rankrows,list(rankrows[0]))}

INDEPENDENTLY VALIDATED count=0. No candidate passes the full registered robust
retrospective gate: coherent distribution calibration and stronger prior-model
proper-score uncertainty remain inadequate. Native internals and coherent-law/
ETF systems are EXPLORATORY LEADS. New-index and ETF *incremental* attribution is
INCONCLUSIVE; global/derivatives/transfer/factor implementations generally fail.
Monthly flags reflect tiny independent samples. No forced winner is created.

{table([{'h':r['horizon'],'hypothesis':r['hypothesis'],'candidate/parent':r['candidate']+'/'+r['incremental_baseline'],'Brier gain':round(r['brier_increment'],6),'CRPS gain':round(r['crps_increment'],6),'status':r['status']} for r in hrows],['h','hypothesis','candidate/parent','Brier gain','CRPS gain','status'])}''')
    # Frozen fresh distributions: each gets its own full coherent statistics.
    def forecast_table(h):
        rows=[]
        for key,f in call['forecasts'].items():
            if f['horizon']!=h:continue
            s=f['statistics'];rows.append({'model':f['model'],'endpoint':f['endpoint'],'P(up)':f"{s['p_up']:.2%}",'mean return':f"{s['mean_return']:+.3%}",'median return':f"{s['median_return']:+.3%}",'mean endpoint':f"{s['expected_endpoint']:,.2f}",'50 interval':f"{s['interval50'][0]:,.0f}–{s['interval50'][1]:,.0f}",'80 interval':f"{s['interval80'][0]:,.0f}–{s['interval80'][1]:,.0f}"})
        return table(rows,list(rows[0]))
    emit(REPORTS[9],f'''# V5 weekly model research

Best whole-law CRPS point candidate L01 (native internals+ETF activity) has
Brier{m(5,'L01')['brier']:.6f},CRPS{m(5,'L01')['crps']:.6f},accuracy{m(5,'L01')['accuracy']:.2%},
50/80coverage{m(5,'L01')['coverage50']:.2%}/{m(5,'L01')['coverage80']:.2%}.
Direction/Brier alternative I03_nosize has Brier.182047,76.09% accuracy,CRPS.010199;
it is a postselected removal stress and retains EXPLORATORY status.
The initial native lead I00 is .186099/.010224/76.09%. All92origins overlap into
19 disjoint windows; effective-size diagnostic23.45 does not guarantee independence.

{short_table(5,['E00','P00','I00','C00','D01','N01','L01','I03_nosize'])}

Global and derivatives blocks do not add incremental value to the strongest
Indian control. ETF addition improves CRPS descriptively but worsens I00 Brier;
neither incremental interval excludes zero after full search adjustment. The
strongest prior V4 comparisons also include zero. Some Brier improvements versus
neutral/unconditional/price are positive under the exploratory family adjustment,
which is a narrower and more useful finding than claiming every test failed.

Fresh experimental snapshot issued{call['issued_at']}; reference18November
official NIFTY close25,227.95, corroborated independently by FO underlying. First
target session{call['first_target_session']}; five-session endpoint26November.
The exchange calendar, including closures, supplies exact dates in JSON.
Unlike the earlier late V3/V4 scenarios, this experimental issue precedes the
first target session. It has not resolved or independently validated anything.
Source files were acquired before issue. US18November's unfinished close is
excluded, and historical features through17November were not changed.

{forecast_table(5)}

**All numbers are uncalibrated model estimates, NOT VALIDATED.** L01 and I03 are
distinct laws; do not attach one probability to the other's mean/interval. Each
JSON law includes up/nonpositive probabilities, mean, median, seven buckets,
noncrossing quantiles, endpoint intervals, expected absolute movement and endpoint
dispersion. Expected future path volatility/breaches are UNAVAILABLE from endpoint
laws. Nominal intervals are not coverage guarantees. Live fitting is a distinct
V5 latest-as-of refit using mature endpoints; it does not change V4's monthly-refit
protocol or qualify as its primary prospective cohort. No trade is recommended.''')
    emit(REPORTS[10],f'''# V5 monthly model research

Monthly research still has76 overlapping origins/four disjoint windows, effective
size diagnostic5.96. Richer data and pooled stock-date rows do not manufacture
independent months. All uncertainty intervals are withheld at this sample size.

{short_table(21,['E00','G00','I00','C00','D01','F00','N01','T00','M00','A00','I01_legacy','I03_nosize'])}

I01_legacy is V5's lowest exposed monthly CRPS point score.027620, but nominal80%
coverage48.68% is unacceptable, and it does not beat V4 D02's .027553 CRPS. Global,
factor, transfer, kernel/additive and auxiliary-task models are generally worse.
The lowest V5 monthly Brier can come from a different model and still fails neutral
or adequate distribution calibration. No coherent system dominates every metric.

The simple E00 historical law remains the conservative experimental default,
alongside separately displayed I01_legacy research output. Even E00's nominal80%
historical coverage61.84% is not calibrated. Monthly complexity should not be
increased because an exposed point ranking looks attractive.

Fresh experimental reference18November25,227.95, issue{call['issued_at']},
21-session endpoint18December2026; first target is19November per the saved calendar.

{forecast_table(21)}

These are distinct NOT VALIDATED endpoint laws. They disagree because models
disagree; no output combines their statistics. All target dates remain within2026.
No 2027 extension, resolved new horizon, independent validation or deployment
is claimed. Future path risk/realized volatility remain unavailable.''')
    allrows=[]
    for h in [5,21]:
        for r in sorted([v for v in metrics if v['horizon']==h],key=lambda v:v['crps']):
            allrows.append({'h':h,'model':r['model'],'origin/disjoint':f"{r['n']}/{r['disjoint']['n']}",'ESS':f"{r['effective_n_return_acf']:.2f}",'Brier':f"{r['brier']:.6f}",'accuracy':f"{r['accuracy']:.1%}",'CRPS':f"{r['crps']:.6f}",'MAE':f"{r['mae']:.3%}",'RMSE':f"{r['rmse']:.3%}",'80 cover':f"{r['coverage80']:.1%}",'80 width':f"{r['width80']:.3%}",'status':'PROXY ONLY' if r['research_only'] else 'EXPOSED / EXPLORATORY'})
    pd.DataFrame(allrows).to_csv(OUT/'final-comparison.csv',index=False)
    priorrows=[{'h':r['horizon'],'model':r['model'],'Brier':f"{r['brier']:.6f}",'accuracy':('NO CALL' if 'Z_neutral' in r['model'] else f"{r['accuracy']:.1%}"),'CRPS':f"{r['crps']:.6f}",'80 cover':f"{r['coverage80']:.1%}"} for r in controls]
    emit(REPORTS[11],f'''# V5 final comparison

Every V5 system below uses matched92 weekly/76 monthly outer dates. Main native
NIFTY closes match the old vintage exactly; foreign/new-source revision histories
are still imperfect. Old controls are reproduced saved forecasts, not retuned
against V5. Different mean/median/direction leaders do not imply a coherent joint
winner; each V5 endpoint law is internally coherent on its own.

{table(allrows,list(allrows[0]))}

## Existing V4 frozen and coherent controls on identical dates

{table(priorrows,list(priorrows[0]))}

Full logloss/balanced accuracy,mean/median errors,RMSE,pinball,bucket Brier,bucket
calibration,50/80coverage/width and confidence calibration bins are in metrics.json;
per-origin values in all-predictions.csv. final-comparison.csv is searchable.
The entire attempted experiment ledger is experiment-registry.csv/json; it includes
failures and cached-estimator attribution evaluations, not just successful leaders.
No model is INDEPENDENTLY VALIDATED; no robust monthly interval is manufactured.''')
    emit(REPORTS[12],f'''# V5 research conclusions

**V5 discovered stronger retrospective hypotheses, not an independently validated
forecasting edge. Continue research; NO DEPLOYMENT.**

What is new: expanded193-instrument universe, native broad/size/style internals,
13-global timezone-aware lead/lag and relative-state study, nine-sector and150-stock
date-grouped transfer, static/rolling factors, additive/kernel/conditional-forest
models, cross-market analogues/sequences, multi-horizon auxiliary learning, ETF/
volume expansion, conditional exact-regime baselines and feature-versus-law attribution.
All34 systems and expansions were registered before their own evaluation, with
no automatic hyperparameter mining. The later expansions were motivated by exposed
results and explicitly do not become predeclared independent confirmation.

What improved historically: I00 weekly Brier.186099 and76.09% accuracy; no-size
stress.182047; ETF/native L01 CRPS.009963 with77.17%80%-interval coverage. The
native lead survives September exclusion descriptively. Fifteen weekly adjusted
comparison lower bounds are positive against weaker empirical/neutral/price
benchmarks under the458-contrast family. None establishes adjusted superiority
over the strongest prior V4 coherent model; no adjusted distribution-score gain
qualifies a robust retrospective candidate. All historical dates remain exposed.

What did not improve: global increment beyond native internals; derivatives
increment beyond joint state; pooled sector/stock transfer; PCA loading adaptation;
most nonlinear/kernel/additive and auxiliary models; monthly calibration. Newly
added broad indices have small/uncertain incremental value over legacy sectors.
ETF CRPS gains coexist with worse Brier relative to I00. Current-stock proxies
cannot establish historically accurate NIFTY breadth. No individually significant
global lead/lag feature survives976-test BH correction.

Important attribution: even exact old sector estimators improve with the new
distribution construction (weekly AT00 Brier.199665), and new features under the
old law produce.198850. The joint new system .186099 cannot be described as proof
that global, derivatives or a larger feature count caused the improvement.

What remains missing: authenticated historical source receipt/revision clocks,
dated stock membership/weights/corporate-action vintages, accessible US bond/USD/
risk panels, enough independent monthly outcomes, and frozen genuinely new resolved
forecasts. This run did not abandon discovery merely because confirmation is absent.

Fresh experimental forecasts were frozen{call['issued_at']} using official
18November close25,227.95 before19November target start. They are postselected,
uncalibrated and unresolved. They do not enter/modify V4's ledger. All V1–V4 artifacts
are preserved;{verify['tests']} meaningful verification checks passed. Initial source,
issued source, source/model/input hashes, failures/repairs and guard amendments
are archived. No trades, live settings or automatic schedules were created.

The defensible output is an auditable ranking and a few frozen exploratory
systems. It is not a promise that the next week rises or that a monthly forecast
has reliable probabilities.''')
    emit(REPORTS[13],'''# V5 next hypotheses

1. Freeze the native-only coherent system versus old-feature/new-law and existing
   V4 controls on genuinely new outcomes. Separate model-construction benefits
   from data-family benefits. Keep September exclusions and date-grouped metrics.
2. Isolate ETF volume from gold/silver/foreign-equity price exposure in a new
   registered study. L01's CRPS gain but worse I00-relative Brier is mixed evidence,
   not a reason to optimize mixture weights on the same outer period.
3. Investigate published NSE native-index aggregate constituent Volume/turnover
   archives. The18November official file supplies a distinct aggregate activity
   source that the broker's zero index-volume field did not. Authenticate full
   historical coverage/definition before using it; never call it traded index volume.
4. Acquire actual as-delivered global/vintage archives and accessible documented
   Treasury/USD-risk sources. Bond/yield hypotheses were not tested here; download
   failure is not economic rejection. Do not bypass access restrictions or invent data.
5. Explain domestic leadership with a smaller fixed native-sector representation.
   Removing mid/small-cap inputs improves the point score; broad index count is
   not automatically useful information. Authenticate composition changes.
6. Diagnose transfer failures using date-balanced normalized residuals and asset
   heterogeneity, not larger same-date row counts. Obtain dated investable stock
   universes/corporate actions before making genuine historical index-breadth claims.
7. Investigate calibrated distributions with fixed prospective coverage monitoring.
   Monthly E00 and the best new/old parametric candidates still under-cover badly.
   Any conformal/mixture change must be a separately registered exploratory model;
   finite-support zero probability is not physical impossibility.
8. Keep only a small number of new hypotheses for eventual independent evaluation.
   V4 power assumptions remain a warning about limited independent dates, not a
   reason to cease retrospective discovery or pretend34 models were validated.
   Remaining2026 cannot establish a dependable monthly edge; extending collection
   into2027 requires a user-approved scope change. Nothing is scheduled implicitly.

No further unregistered sweep was run after this report. Weak/failed global,
factor, transfer, nonlinear and derivative implementations remain preserved.
All current forecast outputs are experimental and NO DEPLOYMENT remains in force.''')
    # A standalone scientific figure; no interactive product/dashboard changes.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    names=['E00','G00','I00','C00','L01']
    for ax,h in zip(axes,[5,21]):
        values=[m(h,n)['brier'] for n in names];ax.barh(names[::-1],values[::-1],color=['#0b7285','#64748b','#8055a4','#aab6c3','#cbd2db']);ax.axvline(.25,ls='--',color='#495057');ax.set_title(f'{h} sessions · '+('19' if h==5 else '4')+' disjoint windows');ax.set_xlim(0,.45);ax.set_xlabel('Brier loss · lower is better')
        for i,v in enumerate(values[::-1]):ax.text(v+.003,i,f'{v:.4f}',va='center')
    fig.suptitle('NIFTY V5 · Native internals lead retrospectively; no independent validation',fontsize=13);fig.savefig(OUT/'v5-comparison.png',dpi=150,bbox_inches='tight');plt.close(fig)
    base=OUT.relative_to(ROOT).as_posix();links='\n'.join(f'- [{n}]({base}/{n})' for n in REPORTS)
    text=f'''# NIFTY V5 research

**New retrospective leads; no independently validated edge. NO DEPLOYMENT.**

193 instrument histories,176 initial features plus separate liquidity inputs,
34 evaluated systems,976 global/IT lead-lag tests,320 exact-condition comparisons.
Native weekly internals:76.09% accuracy/Brier.18610; no-size removal.18205;
ETF/native system CRPS.009963 and77.2% coverage for nominal80% intervals.
Global/derivative additions and panel transfer did not establish incremental value.

Some adjusted gains beat weak baselines, but none establishes superiority over
the strongest prior V4 coherent forecasts. Monthly independent sample remains4.
All historical dates are exposed. A fresh experimental snapshot was frozen at
{call['issued_at']} from official18November NIFTY close25,227.95, before the first
target session. It is postselected, uncalibrated and unresolved; V4 ledger unchanged.

![Comparison]({base}/v5-comparison.png)

{links}

[Complete comparison CSV]({base}/final-comparison.csv) ·
[Searchable registry]({base}/experiment-registry.csv) ·
[Frozen experimental laws]({base}/experimental-forecasts.json) ·
[{verify['tests']} passing verification checks]({base}/verification.json) ·
[Source and reproduction](research/nifty_forecast_v5/README.md)

No trades, deployment, automatic schedules or silent extension beyond2025–2026.
'''
    (ROOT/'NIFTY_V5_RESEARCH.md').write_text(text,encoding='utf-8')
    save('research-decision.json',{'decision':'NO DEPLOYMENT; continue independent hypothesis validation','independent_edge':False,'systems':34,'reports':REPORTS,'fresh_experimental_issue':call['issued_at'],'tests_passed':verify['passed'],'initial_fit_failures_preserved':11,'initial_failed_candidate_repaired':True,'scope':[START,'2026-12-31']})
    save('delivery-manifest.json',{'generated_at':now(),'root_summary_sha256':sha(ROOT/'NIFTY_V5_RESEARCH.md'),'reports':{n:sha(OUT/n) for n in REPORTS},
        'current_source':{p.name:sha(p) for p in SRC.iterdir() if p.is_file()},'frozen_forecast_sha256':sha(OUT/'experimental-forecasts.json'),
        'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='delivery-manifest.json'}})
    print('Wrote14 reports, complete rankings, figure and root summary',flush=True)
if __name__=='__main__':run()
