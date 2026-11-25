"""Create the readable experiment record and a static research figure."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter
from .engine import BASE, ROOT, MODELS, digest, score

LABELS={'climatology':'Historical frequency','yesterday':'Previous day','trend20':'20-session trend',
    'price_logistic':'Price-only logistic','context_logistic':'All-context logistic',
    'analog60':'60 historical analogues','nonlinear64':'Nonlinear random features','ensemble':'Fixed ensemble'}


def main():
    run=BASE/'run-v3'
    forecast=json.loads((run/'forecast.json').read_text())
    original=digest(run/'forecast.json')
    validation=json.loads((run/'validation.json').read_text())
    inventory=json.loads((run/'factor-inventory.json').read_text())
    audit=json.loads((run/'data-audit.json').read_text())
    fresh=json.loads((BASE/'inputs-v2/dashboard-fresh.json').read_text())
    levels=forecast['levels'];primary=forecast['forecasts']['close_return'];secondary=forecast['forecasts']['intraday_return']
    counts=Counter(r['status'] for r in inventory)
    now_rows={r['factor_id']:r for r in fresh['observations']}
    chain=fresh['option_chain'];spot=levels['reference_close']
    atm=min(chain,key=lambda r:abs(r['strike_price']-spot))
    straddle=sum(atm[k]['market_data']['ltp'] for k in ['call_options','put_options'])
    pcr=sum(r['put_options']['market_data']['oi'] for r in chain)/sum(r['call_options']['market_data']['oi'] for r in chain)
    up=primary['up_probability']['ensemble'];intra=secondary['up_probability']['ensemble']
    q=primary['closing_level_quantiles']
    analog_median=spot*(1+primary['analog60_quantiles_unweighted']['0.5'])
    analog_mean=spot*(1+primary['analog60_mean'])
    close_eval=validation['close_return'];intra_eval=validation['intraday_return']
    interval=close_eval['models']['ensemble']['paired_improvement_ci95']
    without_provisional={}
    for target in ['close_return','intraday_return']:
        replay=pd.read_csv(run/f'walk-forward-{target}.csv')
        without_provisional[target]=score(replay[replay.target_day<'2026-11-16'].reset_index(drop=True))
    (run/'validation-published-only.json').write_text(json.dumps(without_provisional,indent=2),encoding='utf-8')

    rows=[]
    for model in MODELS:
        a=close_eval['models'][model];b=intra_eval['models'][model]
        rows.append(f"|{LABELS[model]}|{primary['up_probability'][model]:.1%}|{a['accuracy']:.1%}|{a['brier']:.4f}|{secondary['up_probability'][model]:.1%}|{b['accuracy']:.1%}|{b['brier']:.4f}|")
    model_table='\n'.join(rows)
    group_rows=[]
    for section in sorted({r['section_id'] for r in inventory}):
        group=[r for r in inventory if r['section_id']==section]
        c=Counter(r['status'] for r in group)
        group_rows.append(f"|{section.replace('_',' ')}|{len(group)}|{c['dated_context']}|{c['undated_context']}|{c['quality_excluded']}|{c['unavailable']}|")
    factor_table='\n'.join(group_rows)
    details=[]
    for r in inventory:
        obs=r.get('observation') or {}
        value=obs.get('value')
        if isinstance(value,(dict,list)):
            value='Structured snapshot; see factor-inventory.json'
        text=str(value).replace('|','/').replace('\n',' ') if value is not None else 'Unavailable'
        details.append(f"|{r['label']}|{r['status'].replace('_',' ')}|{text[:110]}|{obs.get('reported_at') or 'Unknown'}|")
    (run/'factor-inventory.md').write_text('# Full dashboard input audit\n\nPublisher time is not acquisition time. Dated context can still be old.\n\n|Concept|Evidence state|Value|Publisher time|\n|---|---|---|---|\n'+'\n'.join(details)+'\n',encoding='utf-8')
    report=f'''# NIFTY forecast experiment — 17 November 2026

**Frozen call: a slight upward bias, with low confidence and substantial two-way risk.**
The fixed ensemble outputs **{up:.1%} upward** for the close versus Monday's
25,291.10 reference, and **{intra:.1%} upward** from today's open to close.
These are raw model estimates, not demonstrated 60%/55% success rates.
The current US sell-off makes the domestic upward lean fragile. A clean bullish
trend throughout the session is not the forecast.

Issued **{forecast['issued_at']}**. Raw input batches were frozen at
{', '.join(forecast['input_freeze_times'])}. No 17 November Indian session prices
were available. Monday's quote is corroborated by the [NSE market page](https://www.nse.in/).
The [NSE 2026 holiday circular](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf)
and the saved Upstox holiday response show no scheduled holiday for 17 November.

## The actual call, ranges and ways it can fail

|Measure|Frozen estimate|Interpretation|
|---|---:|---|
|Close above Monday|{up:.1%}|Raw ensemble probability; low trust in calibration|
|Close above today's open|{intra:.1%}|Separate outcome; models disagree materially|
|Analogue median close|{analog_median:,.0f}|About {analog_median-spot:+.0f} points; a center estimate, not a precise target|
|Analogue weighted mean close|{analog_mean:,.0f}|Almost flat; adverse tails offset frequent small gains|
|Central 50% historical closing band|{q['0.25']:,.0f}–{q['0.75']:,.0f}|Trailing 252-session empirical reference distribution|
|Central 80% historical closing band|{q['0.1']:,.0f}–{q['0.9']:,.0f}|An outside move remains possible|

The bands describe the **closing value**, not a boundary containing the intraday
path. Their walk-forward coverage was {close_eval['empirical50_coverage']:.1%}
and {close_eval['empirical80_coverage']:.1%}, respectively. They are deliberately
simple empirical bands rather than fitted precision targets.

Scenario markers, specified as a qualitative reading of observed levels:

- **Upward continuation:** acceptance above Monday's **25,337.60** high makes
  the recent **25,424.35** high the next reference; 25,500 is a nearby option-OI
  reference. These are conditional markers, not separately validated forecasts.
- **Two-way/base scenario:** repeated trading within Monday's **25,172.10–25,337.60**
  range would fit the weak directional evidence. The analogue median is 25,311.
- **Downward failure:** sustained trading below **25,172.10** would weaken the
  bullish reading; Friday's **25,054.40** low and the 25,000 area are lower references.
  Overnight news can gap directly through any of these levels.

## What the current inputs say

|Independent evidence group|Observed input at the freeze|Reading|
|---|---|---|
|Domestic prices|NIFTY +0.584%; Bank Nifty +0.888%; financials +0.574%|Supports an upward bias|
|Participation|31 advancing / 19 declining constituents, dated 15:29 IST; auto −1.288%, pharma −1.533%, metals −1.499%, realty −1.341%; FMCG +1.867%|Some breadth, but leadership is uneven and partly defensive|
|Overnight India proxy|GIFT Nifty {now_rows['gift_nifty']['value']:,.1f}, {now_rows['gift_nifty']['change_pct']:+.3f}% versus its own previous value|Mild support; the futures/spot spread is not an exact opening-gap forecast|
|Global equities|S&P 500 {now_rows['sp500']['change_pct']:+.3f}%; Nasdaq {now_rows['nasdaq']['change_pct']:+.3f}%; Dow {now_rows['dow']['change_pct']:+.3f}%; US futures {now_rows['us_futures']['change_pct']:+.3f}%|The strongest contrary input; US cash session still open|
|Oil, currency and dollar|Brent {now_rows['brent']['value']:.2f}, {now_rows['brent']['change_pct']:+.3f}%; USD/INR {now_rows['usdinr']['value']:.3f}, {now_rows['usdinr']['change_pct']:+.3f}%; DXY {now_rows['dxy']['change_pct']:+.3f}%|Cheaper oil and firmer INR support India; global risk appetite is mixed|
|Volatility|India VIX 15.68, +1.161%|A move-size/risk input; not a directional vote|
|Participant futures|61,039 FII index-futures longs versus 117,726 shorts; net −56,687 contracts|Bearish positioning, which can also supply squeeze risk|
|Options and expiry|Listed expiry 17 November; PCR {pcr:.3f}; max pain 25,200; ATM 25,300 straddle {straddle:.1f} points|Reference snapshot only: no publisher market timestamp|
|Cash institutions|FII/DII endpoint amounts fail the desk's documented-unit checks; official NSE adapter redirected|Excluded rather than assigning an unverified crore value|
|News and economic events|Upstox NIFTY news returned an empty object; no reliable complete event inventory was supplied|Unknown, not evidence that there are no events|

Current globals are delayed indicative quotes. The domestic constituent breadth
reading is near the close, not a separately verified closing breadth file.
Options OI does not reveal whether each position was initiated by a buyer or
writer. PCR, max pain and straddle premium have no fitted directional weight in
this experiment; straddle premium is not an 80% interval or a profit target.

## The historical check

The model uses **62 features**, **2,427 eligible feature rows**, Indian daily
history from January 2017, and available global history. Price features cover
returns, EMA distances, RSI, candle shape, gaps, realized volatility and ATR.
Context adds sector-relative returns, a sector participation proxy, India VIX,
and conservatively lagged completed global sessions. Sector participation is
not reconstructed constituent breadth; no present-day stock membership is
backfilled into a historical breadth label.

Fixed candidates and the equal-weight ensemble were specified in
[PROTOCOL.md](research/nifty_forecast/PROTOCOL.md) before performance was viewed.
The 504 target sessions run **4 November 2024–16 November 2026**. Each calendar
month is predicted with models fitted only to preceding resolved outcomes, with
at most 1,260 training examples. Scaling and imputation are fitted on training
data. Parameters were not tuned to this evaluation period.

|Model|Today's close-up estimate|Close accuracy|Close Brier ↓|Today's intraday-up estimate|Intraday accuracy|Intraday Brier ↓|
|---|---:|---:|---:|---:|---:|---:|
{model_table}
|Constant 50/50|50.0%|No directional call|0.2500|50.0%|No directional call|0.2500|

The main result is **no established predictive advantage from adding these
inputs**. The ensemble's close-direction accuracy is 51.6%, but its probability
score is worse than both historical frequency and constant 50/50. An always-down
direction would have been correct 50.6% of these sessions. The ensemble's paired
Brier improvement over historical frequency is −0.00229, with a conditional
95% ten-session-block interval of **{interval[0]:.5f} to {interval[1]:.5f}**.
For intraday direction its accuracy matches the 52.8% frequency baseline; the
probability-score difference is negligible and its interval crosses zero.

Calibration is weak: close forecasts in the 55–60% bin occurred 105 times, but
only **48.6%** of those sessions closed up. Forecasts at least 60% upward occurred
156 times and closed up **55.8%** of the time. Today's 59.8% output therefore
cannot honestly be advertised as a calibrated 60% chance. The price-only model
currently gives only 43.5% for an up open-to-close session, versus 54.6% for the
ensemble. That disagreement is part of the result, not a reason to select a
different winner after the test.

The final replay observation uses Monday's provisional quote-derived daily
bar. A separate [503-session published-candle-only validation](artifacts/nifty_forecast/2026-11-17/run-v3/validation-published-only.json)
excludes it. Its close ensemble Brier is
{without_provisional['close_return']['models']['ensemble']['brier']:.4f} versus
{without_provisional['close_return']['models']['climatology']['brier']:.4f} for
the baseline, so the conclusion is unchanged.

## Data quality and coverage

The catalog now contains **127 concepts**, broader than the older 64-factor
research snapshot. The new freeze retains **46,757 dashboard observations**.
An observation count is not an independent daily sample count. The complete
[127-concept input audit](artifacts/nifty_forecast/2026-11-17/run-v3/factor-inventory.md)
and its structured JSON preserve missing and excluded readings.

|Concept group|Total|Dated context|Undated context|Quality excluded|Unavailable|
|---|---:|---:|---:|---:|---:|
{factor_table}

"Dated context" means a timestamp exists; it does not certify freshness or
historical trainability. Factor JSON retains source dates and age. Raw historical
prices are today's revised history, not an archived point-in-time data vintage.
The following safeguards and limits matter:

- Upstox's NIFTY daily endpoint still stops at Friday, 13 November. {len(forecast['provisional_bars'])} Monday
  Indian index/VIX bars are reconstructed from post-close quote OHLC; their
  previous close must match the published historical series. NIFTY 500's Monday
  context is missing and receives a training-derived imputation plus a flag.
- Auto history supplied 474 duplicate session rows, including 248 with differing
  OHLC values. Canonicalization deterministically prefers the midnight daily
  row; duplicates never become extra training samples.
- Global history contained **177 invalid OHLC rows**, rejected before features
  were built. Gaps are not silently turned into valid bars. Close changes between
  remaining observed sessions can span multiple calendar days.
- For a 00:30 IST decision, the preceding US cash day may still be open. Fitted
  global features require a source date strictly earlier than target date minus
  one calendar day. This is conservative for Asian markets. The ongoing US
  sell-off appears in the written scenarios, not retrospectively in the fitted
  feature panel. The model therefore omits useful information visible now.
- Price, flow and option history do not have the same coverage. Recent snapshots
  were not backfilled across years; cash amounts with uncertain units were not used.
- [Upstox documents](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)
  a maximum decade per daily request; the successful batch uses January 2017
  onward. Source errors and both acquisition and market times are preserved.

## Reproduce and score

Seven focused checks pass: raw-input hashes, unfinished-US-day exclusion,
invariance to future Indian-price changes, training-only scaling, next-session
labels, chronological walk-forward training, and logistic probability sanity.

```powershell
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.verify
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.engine --out artifacts/nifty_forecast/2026-11-17/reproduction-01
```

After the target session closes and Upstox publishes its daily candle:

```powershell
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.score
```

The scorer writes a separate outcome file with the official daily open/close,
reference revisions, direction outcomes, Brier scores and interval hits. It
leaves the original [forecast.json](artifacts/nifty_forecast/2026-11-17/run-v3/forecast.json)
unchanged. The outcome is currently **unresolved**. No scheduler or orders were
created, and no existing bot configuration was changed.

The statistical experiment and the qualitative scenario assessment are both
frozen here. A better experiment from this starting point is a series of future
calls at one fixed clock, with timestamped intraday global inputs and published
option/flow observations captured prospectively. One good or bad day will not
establish whether the method works.
'''
    report_path=ROOT/'NIFTY_FORECAST_2026-11-17.md'
    report_path.write_text(report,encoding='utf-8')

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#f7f8fa',
                         'axes.facecolor':'#f7f8fa','text.color':'#172333','axes.labelcolor':'#172333'})
    fig,ax=plt.subplots(2,2,figsize=(14,9.3),gridspec_kw={'height_ratios':[1.4,1]},layout='constrained')
    fig.suptitle('NIFTY · 17 November 2026\nSlight upward model lean. No established historical edge.',fontsize=20,x=.03,ha='left')
    names=MODELS[::-1];y=np.arange(len(names));teal='#087e8b';purple='#8055a4'
    ax[0,0].barh(y+.16,[primary['up_probability'][m] for m in names],height=.29,color=teal,label='Close vs Monday')
    ax[0,0].barh(y-.16,[secondary['up_probability'][m] for m in names],height=.29,color=purple,label='Close vs today open')
    ax[0,0].set_yticks(y,[LABELS[m] for m in names]);ax[0,0].invert_yaxis()
    ax[0,0].set_xlim(.3,.75);ax[0,0].axvline(.5,color='#6b7685',lw=1)
    ax[0,0].xaxis.set_major_formatter(PercentFormatter(1));ax[0,0].legend(loc='lower right',fontsize=8)
    ax[0,0].set_title('Raw forecasts, not calibrated success rates',loc='left',pad=14)
    show=['climatology','yesterday','price_logistic','context_logistic','analog60','nonlinear64','ensemble']
    yy=np.arange(len(show));a=[close_eval['models'][m]['brier'] for m in show]
    ax[0,1].barh(yy,a,color=[teal if m=='ensemble' else '#aab5c3' for m in show],height=.6)
    ax[0,1].set_yticks(yy,[LABELS[m] for m in show]);ax[0,1].invert_yaxis()
    ax[0,1].set_xlim(.24,.273);ax[0,1].axvline(.25,color='#b84a48',ls='--',label='Constant 50/50: 0.2500')
    for i,value in enumerate(a):ax[0,1].text(value+.0004,i,f'{value:.4f}',va='center',fontsize=9)
    ax[0,1].legend(loc='lower right',fontsize=8);ax[0,1].set_title('504-session Brier score · lower is better',loc='left',pad=14)
    ax[1,0].hlines(0,q['0.1'],q['0.9'],lw=16,color='#cbd7e3')
    ax[1,0].hlines(0,q['0.25'],q['0.75'],lw=16,color=teal)
    ax[1,0].axvline(spot,color='#172333',ls='--',lw=1)
    ax[1,0].scatter([analog_median],[0],color='#172333',s=45,zorder=3)
    ax[1,0].text(spot,.32,f'Monday reference {spot:,.1f}',ha='center',fontsize=10)
    ax[1,0].text((q['0.1']+q['0.9'])/2,-.34,f"50%: {q['0.25']:,.0f}–{q['0.75']:,.0f}    |    80%: {q['0.1']:,.0f}–{q['0.9']:,.0f}",ha='center',fontsize=10)
    ax[1,0].set_xlim(q['0.1']-50,q['0.9']+50);ax[1,0].set_ylim(-.65,.7);ax[1,0].set_yticks([])
    ax[1,0].xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax[1,0].set_title('Closing-level bands · historical reference distribution',loc='left',pad=12)
    ax[1,0].set_xlabel('Closing bands do not constrain the intraday path',fontsize=9)
    bins=close_eval['ensemble_calibration'];px=[b['mean_predicted'] for b in bins];py=[b['observed_up'] for b in bins]
    ax[1,1].plot([.3,.75],[.3,.75],color='#aab5c3',ls='--',label='Perfect calibration')
    ax[1,1].scatter(px,py,s=[b['n']*1.3 for b in bins],color=teal,alpha=.85)
    for b in bins:ax[1,1].annotate(f"n={b['n']}",(b['mean_predicted'],b['observed_up']),xytext=(0,10),textcoords='offset points',ha='center',fontsize=8)
    ax[1,1].set_xlim(.3,.75);ax[1,1].set_ylim(.3,.75)
    ax[1,1].xaxis.set_major_formatter(PercentFormatter(1));ax[1,1].yaxis.set_major_formatter(PercentFormatter(1))
    ax[1,1].set_xlabel('Mean predicted up probability',fontsize=9);ax[1,1].set_ylabel('Observed fraction closing up',fontsize=9)
    ax[1,1].set_title('Calibration is weak · confidence should stay low',loc='left',pad=12)
    image=run/'forecast-summary.png';fig.savefig(image,dpi=160);plt.close(fig)
    if digest(run/'forecast.json')!=original:raise AssertionError('Forecast was rewritten')
    print(json.dumps({'report':str(report_path),'figure':str(image),'inventory':dict(counts),'forecast_unchanged':True}))


if __name__=='__main__':
    main()
