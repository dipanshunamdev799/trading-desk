"""Weekly/monthly brief and a standalone forecast comparison figure."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter,StrMethodFormatter
from .engine import BASE,ROOT,digest

NAMES={'neutral':'Neutral baseline','other_sectors':'Other sector leadership','participation':'Participation/breadth proxy'}
METHODS={'neutral':'Neutral 50/50','rolling_frequency':'Matured-label frequency','equal_groups':'Equal eligible groups',
    'adaptive_groups':'Learned weights','calibrated_adaptive':'Learned weights + calibration (primary)'}


def main():
    run=BASE/'horizons-v2';path=run/'forecast.json';original=digest(path)
    call=json.loads(path.read_text());validation=json.loads((run/'validation.json').read_text())
    forecast=call['forecasts'];week=forecast['week'];month=forecast['month']
    weight_rows=[f"|{NAMES[g]}|{week['group_weights'][g]:.2%}|{month['group_weights'][g]:.2%}|" for g in NAMES]
    forecasts=[];scores=[]
    for name,f in forecast.items():
        q=f['closing_level_quantiles'];r=f['return_distribution']
        forecasts.append(f"|{name.title()}|{f['horizon_sessions']}|{f['expected_endpoint_date']}|{f['up_probability']['calibrated_adaptive']:.2%}|"+
            f"{f['projected_median_level']:,.0f} ({r['quantiles']['0.5']:+.2%})|{q['0.25']:,.0f}–{q['0.75']:,.0f}|{q['0.1']:,.0f}–{q['0.9']:,.0f}|")
        for method,label in METHODS.items():
            s=validation[name]['fully_learned']['methods'][method]
            accuracy='—' if method=='neutral' else f"{s['accuracy']:.1%}"
            scores.append(f"|{name}|{label}|{s['brier']:.5f}|{accuracy}|")
    w=validation['week']['fully_learned'];m=validation['month']['fully_learned']
    wp=w['methods']['calibrated_adaptive'];mp=m['methods']['calibrated_adaptive']
    text=f'''# NIFTY: one-week and one-month experiment

**Working call: roughly flat with a slight downward weekly lean, and roughly
flat with a slight upward monthly lean. Neither is an established edge.**
The separate models estimate **{week['up_probability']['calibrated_adaptive']:.1%} upward over
5 trading sessions** and **{month['up_probability']['calibrated_adaptive']:.1%} upward over
21 sessions**. The monthly validation is poor and too small to support a confident call.

Issued **{call['issued_at']}**, using the same frozen pre-market context and the
**25,291.10 close on 16 November 2026**. The entire input, indicator-initialization,
training and prediction-error history remains limited to **17 November 2024–16
November 2026**: 495 NIFTY sessions, 475 eligible feature rows, 71 features and
12 input groups. Earlier daily calls remain unchanged.

![Week and month comparison](artifacts/nifty_forecast/2026-11-17/horizons-v2/horizon-summary.png)

## Frozen forecasts

|Horizon|Trading sessions|Expected endpoint close|Estimated probability above 25,291.10|Model median endpoint|Nominal central 50% scenario band|Nominal central 80% scenario band|
|---|---:|---|---:|---:|---:|---:|
{chr(10).join(forecasts)}

These are **model scenario quantiles, not validated coverage probabilities**.
They describe the endpoint, not the within-period high/low. Historical 80% band
coverage was only **{w['central80_coverage']:.1%} weekly** and
**{m['central80_coverage']:.1%} monthly**. In particular, the monthly band must
not be described as having a demonstrated 80% chance of containing the outcome.

The dates account for the 24 November NSE holiday, using a frozen Upstox calendar
corroborated by the [official NSE 2026 circular](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf).
The outcome definition is the next 5/21 actual trading sessions; unexpected
calendar changes or missing candles require review before scoring a changed date.

The means differ from the medians because of tail sizes. The weekly mixture
mean is {week['projected_mean_level']:,.0f} ({week['return_distribution']['mean']:+.2%}),
while the monthly mean is {month['projected_mean_level']:,.0f}
({month['return_distribution']['mean']:+.2%}). Frequent small gains can coexist
with a negative mean if down moves are larger. These tiny central moves and broad,
poorly validated distributions support low confidence rather than precise targets.

## Horizon-specific learned weights

|Group|Week allocation|Month allocation|
|---|---:|---:|
{chr(10).join(weight_rows)}

All other groups have zero current allocation. Each horizon retrains its input
coefficients, group trust and calibration; the daily estimate is not compounded
or stretched. Zero fitted allocation is not a statement of economic irrelevance.
Institutional groups remain below the evidence gate. Full
[group weights](artifacts/nifty_forecast/2026-11-17/horizons-v2/group-weights.csv) and
[individual coefficients](artifacts/nifty_forecast/2026-11-17/horizons-v2/input-coefficients.csv)
are saved for both horizons.

## Outcome maturity and move-size estimation

For an origin after session t's close, the return is **C[t+h]/C[t] − 1**. An
earlier forecast may teach the model only after its endpoint has closed.
Yesterday's monthly forecast is still unresolved today. This restriction applies
to expert fitting, group-weight learning, calibration and magnitude history.

The earlier fixed penalties, feature groups and recency half-lives are retained.
Historical experts refit monthly; the current call gets a fresh fit. The first
expert forecast waits for 252 matured training labels, and primary weighting and
calibration each need 126 matured OOS errors. No parameter grid was searched.
The [fixed design](research/nifty_forecast/HORIZON_PROTOCOL.md) and dated fits record this.

Move sizes use up to 252 matured returns at the appropriate horizon. Positive
and nonpositive historical sizes receive total mass p and 1−p from the fitted
upward estimate. This assumes historical conditional sizes persist. It is not
a separately fitted price regressor. Quantiles use an empirical inverse CDF;
no unfinished weekly/monthly return enters the distribution.

## Historical results and overlapping outcomes

After expert startup there are {validation['week']['all_after_expert_training']['n']}
resolved weekly and {validation['month']['all_after_expert_training']['n']} resolved
monthly forecasts. Fully learned weights/calibration leave:

|Horizon|Daily forecast origins|Origin dates|Endpoint dates|Non-overlapping windows|
|---|---:|---|---|---:|
|Week|{w['n']}|{' to '.join(w['origin_period'])}|{' to '.join(w['endpoint_period'])}|{w['nonoverlapping_n']}|
|Month|{m['n']}|{' to '.join(m['origin_period'])}|{' to '.join(m['endpoint_period'])}|{m['nonoverlapping_n']}|

Adjacent weekly forecasts share four daily returns; adjacent monthly forecasts
share twenty. They are **not independent experiments**. The greedy non-overlapping
subset avoids reusing return days but is not guaranteed statistically independent.
There are only **two** such fully learned monthly test windows.

|Horizon|Method|Brier score ↓|Direction accuracy|
|---|---|---:|---:|
{chr(10).join(scores)}

Weekly primary accuracy is **{wp['accuracy']:.1%}**, equal to the always-down
control's {w['always_down_accuracy']:.1%}. Its **{wp['brier']:.5f}** Brier is only
marginally better than neutral 0.25000. The 10-session-block paired improvement
interval **{wp['paired_ci95'][0]:+.5f} to {wp['paired_ci95'][1]:+.5f}** spans zero.
On the 17 non-overlapping windows, its Brier is
{validation['week']['fully_learned_nonoverlapping']['methods']['calibrated_adaptive']['brier']:.5f},
worse than neutral. A weekly advantage is not established.

The monthly primary is **poor** here: **{mp['accuracy']:.1%}** accuracy across
overlapping origins, Brier **{mp['brier']:.5f}**, versus neutral 0.25000. The raw
uncalibrated blend also fails to beat neutral. A monthly confidence interval is
withheld because two non-overlapping windows are inadequate; the fixed
42-session bootstrap block requires more history. Its scenario bands also
under-cover heavily. **Treat the monthly forecast as a very weak experimental hypothesis.**

The predeclared primary is retained instead of selecting a better-looking control
after inspection. Both chronological halves, move-size MAE, non-overlapping results
and subsets excluding the provisional 16 November endpoint appear in
[validation.json](artifacts/nifty_forecast/2026-11-17/horizons-v2/validation.json).
This is exploratory reuse of the same historical period.

## Checks and later scoring

Ten checks pass: exact horizon endpoints, holidays/special sessions, exclusion
of unfinished labels, invariance of earlier models/weights/calibration/ranges to
unfinished outcome changes, empirical median sign, disjoint test windows,
withholding unsupported monthly intervals, matured update endpoints and weight
sums, horizon-specific scoring, and source/previous-call hashes.

```powershell
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.verify_horizons
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.horizons --out artifacts/nifty_forecast/2026-11-17/horizons-reproduction-01
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.score_horizons --run artifacts/nifty_forecast/2026-11-17/horizons-v2
```

The scorer can resolve the week while the month remains pending. It uses
published daily candles and writes a separate outcome artifact, preserving the
[frozen forecasts](artifacts/nifty_forecast/2026-11-17/horizons-v2/forecast.json).
No unattended watcher or scheduled task was created. The earlier source-vintage,
conservative global-clock, institutional-publication and provisional-quote
limitations remain in force.
'''
    report=ROOT/'NIFTY_WEEK_MONTH_2026-11-17.md';report.write_text(text,encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#f7f8fa','axes.facecolor':'#f7f8fa'})
    fig,ax=plt.subplots(1,2,figsize=(13,4.7),layout='constrained')
    fig.suptitle('NIFTY · Week and month forecasts\nTwo years of inputs · weak evidence, especially for the month',fontsize=18,x=.03,ha='left')
    for y,name,color in zip([1,0],['week','month'],['#087e8b','#8055a4']):
        f=forecast[name];p=f['up_probability']['calibrated_adaptive'];q=f['closing_level_quantiles']
        ax[0].barh(y,p,height=.5,color=color);ax[0].text(p+.015,y,f'{p:.1%} estimated up',va='center')
        ax[1].hlines(y,q['0.1'],q['0.9'],lw=15,color='#cbd7e3')
        ax[1].hlines(y,q['0.25'],q['0.75'],lw=15,color=color)
        ax[1].scatter([f['projected_median_level']],[y],color='#172333',s=40,zorder=3)
    ax[0].set_yticks([1,0],['Week · 5 sessions\n23 November','Month · 21 sessions\n16 December'])
    ax[0].set_xlim(0,1);ax[0].axvline(.5,color='#6b7685',ls='--');ax[0].xaxis.set_major_formatter(PercentFormatter(1))
    ax[0].set_title('Separate horizon models',loc='left',pad=12)
    ax[1].set_yticks([1,0],['Week','Month']);ax[1].set_ylim(-.5,1.5)
    ax[1].axvline(call['reference_close'],color='#6b7685',ls='--')
    ax[1].xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'));ax[1].set_title('Nominal scenario bands · not reliable coverage',loc='left',pad=12)
    ax[1].set_xlabel('Color = central 50%; gray = 80%; dot = median',fontsize=9)
    image=run/'horizon-summary.png';fig.savefig(image,dpi=160,bbox_inches='tight',pad_inches=.15);plt.close(fig)
    if digest(path)!=original:raise AssertionError('Frozen forecast changed')
    print(json.dumps({'report':str(report),'figure':str(image),'forecast_unchanged':True}))


if __name__=='__main__':main()
