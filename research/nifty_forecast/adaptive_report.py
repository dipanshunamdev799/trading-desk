"""Readable learned-weight research report and static diagnostic figure."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from .engine import BASE,ROOT,digest

NAMES={'neutral':'Neutral / uncertainty','trend':'Trend / momentum','short_term_price':'Short-term price / RSI',
    'candles_gaps':'Candle shape / gaps','volatility':'VIX / realized volatility',
    'banks_financials':'Banks / financials','other_sectors':'Other sectors','participation':'Participation',
    'global_equities':'Completed global equities','oil_currency':'Oil / currency',
    'gift_nifty':'Completed-session GIFT','institutional_cash':'Institutional cash ratios','fii_positioning':'FII derivative positioning'}
METHOD={'neutral':'Neutral 50/50','rolling_frequency':'Daily rolling frequency','equal_groups':'Equal eligible groups',
    'adaptive_groups':'Learned group weights','calibrated_adaptive':'Learned weights + calibration (primary)'}


def main():
    run=BASE/'adaptive-v2';frozen=digest(run/'forecast.json')
    call=json.loads((run/'forecast.json').read_text())
    validation=json.loads((run/'validation.json').read_text())
    old_validation=json.loads((BASE/'run-v3/validation.json').read_text())
    audit=json.loads((run/'data-audit.json').read_text())
    groups=pd.read_csv(run/'group-weights.csv');coeff=pd.read_csv(run/'input-sensitivity.csv')
    stability=pd.read_csv(run/'weight-stability.csv')
    compare=json.loads((run/'comparison-with-original.json').read_text())
    close=groups[groups.target=='close_return'].set_index('group')
    intra=groups[groups.target=='intraday_return'].set_index('group')
    probabilities={k:call['forecasts'][k]['up_probability'] for k in ['close_return','intraday_return']}
    allocation_rows=[]
    for name in close.index:
        allocation_rows.append(f"|{NAMES[name]}|{close.loc[name,'weight']:.2%}|{intra.loc[name,'weight']:.2%}|"+
            f"{close.loc[name,'expert_up_probability']:.1%}|{int(close.loc[name,'out_of_sample_n'])}|"+
            ('Shadow: short history|' if 'insufficient' in str(close.loc[name,'status']) else 'Eligible; zero can be selected|' if name!='neutral' else 'Fixed uncertainty anchor|'))
    performance_rows=[]
    for name in METHOD:
        a=validation['close_return']['all504']['methods'][name]
        b=validation['intraday_return']['all504']['methods'][name]
        performance_rows.append(f"|{METHOD[name]}|{a['brier']:.5f}|"+
            ('—|' if name=='neutral' else f"{a['accuracy']:.1%}|")+f"{b['brier']:.5f}|"+
            ('—|' if name=='neutral' else f"{b['accuracy']:.1%}|"))
    a=old_validation['close_return']['models']['ensemble'];b=old_validation['intraday_return']['models']['ensemble']
    performance_rows.append(f"|Original fixed ensemble|{a['brier']:.5f}|{a['accuracy']:.1%}|{b['brier']:.5f}|{b['accuracy']:.1%}|")
    feature_rows=[]
    for target in ['close_return','intraday_return']:
        selected=coeff[(coeff.target==target)&(coeff.group_weight>0)].copy()
        selected=selected.iloc[np.argsort(-selected.local_up_probability_change_pp_per_training_sd.abs().to_numpy())]
        for _,r in selected.iterrows():
            feature_rows.append(f"|{'Close vs previous close' if target=='close_return' else 'Open to close'}|{r['feature']}|{r['signed_logistic_coefficient']:+.4f}|{r['local_up_probability_change_pp_per_training_sd']:+.3f} pp|")
    pclose=probabilities['close_return']['calibrated_adaptive'];pintra=probabilities['intraday_return']['calibrated_adaptive']
    raw=probabilities['close_return']['adaptive_groups']
    primary=validation['close_return']['all504']['methods']['calibrated_adaptive']
    rawstats=validation['close_return']['all504']['methods']['adaptive_groups']
    current_fii=close.loc['institutional_cash']
    g_boot=stability[(stability.target=='close_return')&(stability.group=='gift_nifty')].iloc[0]
    ci=primary['paired_improvement_ci95'];raw_ci=rawstats['paired_improvement_ci95']
    text=f'''# NIFTY inputs weighted by historical prediction errors

**The learned-weight call for 17 November 2026 is neutral.** The primary estimate
is **{pclose:.2%}** for a close above the preceding close and **{pintra:.2%}** for
a close above today's open. This replaces the bullish interpretation of the
first experiment for this new version; the original timestamped 59.8% call is
preserved as a separate experiment. Neither call has an observed outcome yet.

Issued **{call['issued_at']}**. Reference: **25,291.10**. It reuses the earlier
pre-market price freeze, with a separately acquired institutional-history batch.
There are still no 17 November Indian-session prices in the model.

![Learned weights and historical diagnostics](artifacts/nifty_forecast/2026-11-17/adaptive-v2/learned-weights-summary.png)

## Actual learned allocations

These are probability-blend weights, before the final calibration step. Each
target has a separate set and its weights sum to 100%. A neutral expert always
predicts 50%; its high allocation shrinks weak evidence toward uncertainty.

|Input group|Close vs previous close weight|Open-to-close weight|Current group close-up estimate|Past OOS predictions|Eligibility|
|---|---:|---:|---:|---:|---|
{chr(10).join(allocation_rows)}

For the close forecast, the arithmetic is approximately
**70.03% × 50% + 29.97% × 52.73% = {raw:.2%}**, before calibration.
The calibrator, learned only from prior predictions and outcomes, moves it to
**{pclose:.2%}**. For open-to-close, the blend uses 70.52% neutral, 13.36% candle/gap
signals and 16.13% volatility signals, yielding 49.73% before calibration and
{pintra:.2%} afterward.

The GIFT allocation is applied to **completed-session historical GIFT return and
volatility features**, using the safe date lag from the first experiment. It is
not a fitted weight on the live after-hours GIFT quote. The ongoing US cash
sell-off remains qualitative context; final US closes cannot be inserted into
a 00:30 IST historical forecast whose US session was still open.

A zero weight has two meanings here. Eligible groups can receive zero when
their earlier predictions do not improve the joint, regularized blend. Groups
with inadequate evidence receive zero by an explicit sample-size gate. Neither
means the underlying market variable has no economic effect. Highly correlated
inputs can substitute for one another, so percentages are conditional on this
feature set, history window and shrinkage rule.

## How the machine assigns weights

The design is recorded in [ADAPTIVE_PROTOCOL.md](research/nifty_forecast/ADAPTIVE_PROTOCOL.md).
There are **71 raw features in 12 disjoint groups**. The feature and group layers
have different jobs:

1. **Learn each input's signed coefficient.** Every group has an L2 logistic
   expert. Monthly fits use only already resolved sessions, up to 1,260 rows,
   with a 252-session recency half-life and fixed penalty 25. Normalization and
   missing-value handling use only its own training data. Missingness has its
   own coefficients.
2. **Make historical predictions before seeing their answers.** For example, a
   prediction for session D uses only resolved targets before D. The actual D
   result becomes eligible for changing the next session's blend, not D's own
   forecast. Monthly experts stay frozen within their month; the current forward
   call receives a fresh fit with all outcomes now resolved.
3. **Learn group trust from those errors.** Before each decision, choose
   nonnegative weights summing to one to minimize Brier loss on up to the prior
   504 out-of-sample forecasts. Recent errors have a 126-session half-life. A
   fixed 0.005 squared penalty favors the neutral expert when evidence is weak.
   This joint fit accounts for overlap between experts rather than counting
   correlated indicators as independent votes.
4. **Fit calibration to previous forecasts.** A monotone logistic mapping learns
   from at most 252 preceding adaptive forecasts, with at least 126 required.
   It has penalty 10 toward no adjustment. Calibration is evaluated as a
   separate layer; it is not assumed to improve every test period.

No weights are chosen from the entire evaluation period and then applied back
to its beginning. Group allocations change daily as earlier results resolve.
[Daily weights](artifacts/nifty_forecast/2026-11-17/adaptive-v2/daily-weights-close_return.csv),
[historical expert predictions](artifacts/nifty_forecast/2026-11-17/adaptive-v2/expert-predictions-close_return.csv)
and the dated expert-fit files make that sequence inspectable.

## Weights on individual inputs

The [full coefficient table](artifacts/nifty_forecast/2026-11-17/adaptive-v2/input-coefficients.csv)
contains all 71 inputs for both outcomes, including inputs whose group currently
has zero allocation. Standardized coefficients act on log odds **inside each
expert**; they are not percentages of the overall forecast.

The table below shows inputs in groups with nonzero current allocations.
Sensitivity is the local change in the final upward estimate, in percentage
points, for a one-training-standard-deviation increase in that feature, holding
other features fixed. It includes both its group weight and the fitted
calibration slope. It is a mathematical local sensitivity, not a causal claim
or a guarantee that such an isolated market change can occur.

|Prediction target|Input|Signed expert coefficient|Local final sensitivity / training SD|
|---|---|---:|---:|
{chr(10).join(feature_rows)}

An expert's intercept, feature-missingness effects and neutral allocation remain
explicit. They are not relabeled as weights on named market inputs. Full values
and preprocessing are saved in the expert-fit JSON files.

## Institutional history: more data, carefully used

The [Upstox FII documentation](https://upstox.com/developer/api-documentation/get-fii-data/)
states that collection begins on 1 April 2026 and daily requests return at most
30 trading days. Overlapping requests and the saved current window recovered
**{audit['institutional']['observed_sessions']} unique source sessions**, 1 April–16 November,
with **155 aligned training rows** and no conflicting duplicate revisions.
Returned session timestamps, rather than the misleading request parameter name,
govern the join. One source date does not align to the NIFTY daily calendar.

The cash features are **(buy − sell)/(buy + sell)**, including five-session
averages. A common INR/crore scale cancels exactly; absolute crore values remain
unverified. Negative amounts, invalid values and a zero denominator are rejected.
Futures features use long/short and trade-contract imbalances; participant option
positioning uses normalized long-call/short-put versus long-put/short-call
exposure. That last measure is a contract-count proxy, not a delta-weighted book.

These experts have **{int(current_fii.out_of_sample_n)} genuine historical OOS predictions**
after their initial training requirement. The primary blend requires 126 such
predictions and 252 training rows. They therefore receive **0% primary weight**
and are retained in shadow, where their predictions and coefficients can be
scored as additional history arrives. Their current close-up estimates of
64.4% and 63.0% do not bypass that gate.

Institutional EOD values are assumed published before the next 00:30 IST
decision. The API's session timestamp does not prove a publication clock, so
this is reconstructed history rather than an archived publication-vintage replay.
Unknown-time chain PCR, IV, max pain, and unarchived macro/news concepts likewise
have no fitted primary weight; no synthetic years of observations were created.

## Did learning weights improve the predictions?

The evaluation contains **504 sessions, 4 November 2024–16 November 2026**.
The latest 126 and both chronological halves are reported in JSON. This period
was already examined in the first study, so it is an **exploratory reused
evaluation**, not an untouched confirmation set. Its individual forecasts still
obey historical information boundaries. The next actual session remains forward.

|Method|Close Brier ↓|Close accuracy|Intraday Brier ↓|Intraday accuracy|
|---|---:|---:|---:|---:|
{chr(10).join(performance_rows)}

The raw learned blend improves close Brier loss from the first ensemble's
0.25541 to **{rawstats['brier']:.5f}** and scores **{rawstats['accuracy']:.1%}** direction
accuracy. It remains essentially tied with the neutral 0.25000 reference. Its
paired improvement against neutral is {rawstats['brier_improvement_vs_neutral']:+.5f},
with conditional 95% block interval **{raw_ci[0]:+.5f} to {raw_ci[1]:+.5f}**.

The predeclared primary calibrated model scores **{primary['brier']:.5f}** and
**{primary['accuracy']:.1%}** close accuracy. Its improvement versus neutral is
{primary['brier_improvement_vs_neutral']:+.5f}, interval **{ci[0]:+.5f} to {ci[1]:+.5f}**.
**Calibration made this evaluation worse.** It is retained and disclosed as
specified, rather than replacing the primary method with whichever control won
after seeing the results. Intraday learned weighting and calibration also fail
to establish an advantage over the controls. The equal-group intraday control
has a better point estimate, with its uncertainty interval still crossing zero.

Thus weights have been learned and changed the forecast, but a reliable
directional edge has **not** been established. Improvement from an overconfident
first model is not the same as beating a neutral forecast. A separate
[503-session check](artifacts/nifty_forecast/2026-11-17/adaptive-v2/validation.json)
excludes Monday's provisional quote-derived target and reaches the same broad
conclusion. Both raw and calibrated estimates are frozen; a 49.7% estimate is
operationally neutral, not a high-confidence bearish call.

## How stable are the weights?

A diagnostic 300-resample, ten-session-block bootstrap refits the current stack
on resampled historical predictions. The close GIFT allocation ranges from
**{g_boot.weight_q025:.1%} to {g_boot.weight_q975:.1%}** across its central 95%
resample range, including zero. The neutral allocation's range is also broad.
These are conditional weight-stability diagnostics, not confidence bounds for
universal economic importance. The regularization and selected feature groups
remain fixed; historical stationarity is not guaranteed.

The correct reading of 29.97% is therefore "today's fitted allocation under the
specified method," not a permanent market constant. Full
[weight stability](artifacts/nifty_forecast/2026-11-17/adaptive-v2/weight-stability.csv),
[input sensitivity](artifacts/nifty_forecast/2026-11-17/adaptive-v2/input-sensitivity.csv)
and [paired comparison with the original](artifacts/nifty_forecast/2026-11-17/adaptive-v2/comparison-with-original.json)
are saved.

## Verification and the next observation

Eight additional checks pass: common-scale cash-ratio invariance, simplex
constraints, preference for the historically better expert, invariance of past
weights/calibration to future labels, zero allocation for missing or insufficient
history, invariance of earlier expert fits to future labels, monotone calibration,
and saved chronological boundaries/weight sums. The original seven checks remain
available. The original forecast's hash is preserved.

```powershell
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.verify_adaptive
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.adaptive --out artifacts/nifty_forecast/2026-11-17/adaptive-reproduction-01
```

After the target session's daily candle is published:

```powershell
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.score --run artifacts/nifty_forecast/2026-11-17/adaptive-v2
```

This writes a separate outcome file for the new
[frozen forecast](artifacts/nifty_forecast/2026-11-17/adaptive-v2/forecast.json).
The original experiment can be scored separately with the scorer's default run.
New-day reruns accept `--inputs`, `--supplement`, `--institutional`,
`--reference-run`, and a new `--out` path, so new resolved sessions can change
weights without rewriting earlier calls. Each needs a newly frozen reference
run and its dated input snapshots. No unattended watcher has been started.
'''
    report=ROOT/'NIFTY_LEARNED_WEIGHTS_2026-11-17.md';report.write_text(text,encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
        'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#f7f8fa',
        'axes.facecolor':'#f7f8fa','text.color':'#172333','axes.labelcolor':'#172333'})
    fig,axes=plt.subplots(2,2,figsize=(14,9),layout='constrained')
    fig.suptitle('NIFTY · Learning input weights from earlier errors\n17 November 2026: the learned forecast is neutral',fontsize=19,x=.025,ha='left')
    palette={'neutral':'#b4bfcb','gift_nifty':'#087e8b','candles_gaps':'#b77b35','volatility':'#8055a4'}
    cmap=plt.get_cmap('tab20')
    for i,name in enumerate(close.index):palette.setdefault(name,cmap((i*2)%20))
    active=[name for name in close.index if close.loc[name,'weight']>.001 or intra.loc[name,'weight']>.001]
    left=np.zeros(2)
    for name in active:
        values=np.array([close.loc[name,'weight'],intra.loc[name,'weight']])
        axes[0,0].barh([1,0],values,left=left,height=.5,color=palette[name],label=NAMES[name])
        for j,value in enumerate(values):
            if value>.07:axes[0,0].text(left[j]+value/2,1-j,f'{value:.1%}',ha='center',va='center',color='#172333' if name=='neutral' else 'white',fontsize=11)
        left+=values
    axes[0,0].set_yticks([1,0],['Close vs previous close','Open to close']);axes[0,0].set_xlim(0,1)
    axes[0,0].xaxis.set_major_formatter(PercentFormatter(1));axes[0,0].legend(loc='lower left',bbox_to_anchor=(0,-.25),ncol=2,fontsize=8)
    axes[0,0].set_title('Actual current probability-blend weights',loc='left',pad=13)
    values=[.5980412005062247,probabilities['close_return']['adaptive_groups'],pclose]
    axes[0,1].barh([2,1,0],values,color=['#c19a8f','#087e8b','#172333'],height=.55)
    axes[0,1].set_yticks([2,1,0],['Original fixed ensemble','Learned group weights','After calibration (primary)'])
    axes[0,1].set_xlim(.4,.65);axes[0,1].axvline(.5,color='#6b7685',ls='--')
    for j,value in enumerate(values):axes[0,1].text(value+.003,2-j,f'{value:.2%}',va='center')
    axes[0,1].xaxis.set_major_formatter(PercentFormatter(1));axes[0,1].set_title('Current close-up estimates · calibration is not proof',loc='left',pad=13)
    w=pd.read_csv(run/'daily-weights-close_return.csv').tail(505)
    dates=pd.to_datetime(w.target_day)
    meaningful=[name for name in close.index if w[name].max()>.03]
    tiny=[name for name in close.index if name not in meaningful and w[name].sum()>1e-9]
    if tiny:
        w['other_small']=w[tiny].sum(axis=1)
        meaningful.append('other_small');NAMES['other_small']='Other small allocations';palette['other_small']='#d2d6df'
    axes[1,0].stackplot(dates,*[w[name].to_numpy() for name in meaningful],colors=[palette[n] for n in meaningful],labels=[NAMES[n] for n in meaningful])
    axes[1,0].set_ylim(0,1);axes[1,0].yaxis.set_major_formatter(PercentFormatter(1));axes[1,0].tick_params(axis='x',rotation=25)
    axes[1,0].set_title('Close forecast weights changed using prior outcomes',loc='left',pad=13)
    axes[1,0].legend(loc='lower left',bbox_to_anchor=(0,-.42),ncol=3,fontsize=7)
    e=pd.read_csv(run/'evaluation-close_return.csv');dates=pd.to_datetime(e.target_day)
    for name,color in [('equal_groups','#a1aab8'),('adaptive_groups','#087e8b'),('calibrated_adaptive','#172333')]:
        loss=.25-(e[name]-e.outcome)**2
        axes[1,1].plot(dates,loss.rolling(63,min_periods=63).mean(),color=color,lw=1.5,label=METHOD[name])
    axes[1,1].axhline(0,color='#6b7685',lw=1,ls='--');axes[1,1].tick_params(axis='x',rotation=25)
    axes[1,1].set_title('63-session Brier improvement versus neutral',loc='left',pad=13)
    axes[1,1].set_ylabel('Above zero = better probability score');axes[1,1].legend(loc='lower left',bbox_to_anchor=(0,-.34),fontsize=8)
    image=run/'learned-weights-summary.png';fig.savefig(image,dpi=160,bbox_inches='tight',pad_inches=.15);plt.close(fig)
    if digest(run/'forecast.json')!=frozen:raise AssertionError('Frozen forecast changed')
    print(json.dumps({'report':str(report),'figure':str(image),'call_unchanged':True}))


if __name__=='__main__':main()
