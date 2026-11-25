"""Summarize the strict two-calendar-year rerun without changing its forecast."""
import json
import pandas as pd
from .engine import BASE,ROOT,digest


def main():
    run=BASE/'two-year-v1';original=digest(run/'forecast.json')
    call=json.loads((run/'forecast.json').read_text())
    result=json.loads((run/'validation.json').read_text())
    groups=pd.read_csv(run/'group-weights.csv')
    close=groups[groups.target=='close_return'].set_index('group')
    intra=groups[groups.target=='intraday_return'].set_index('group')
    rows=[]
    for name in close.index:
        if close.loc[name,'weight']>0 or intra.loc[name,'weight']>0:
            rows.append(f"|{name.replace('_',' ')}|{close.loc[name,'weight']:.2%}|{intra.loc[name,'weight']:.2%}|")
    scores=[]
    for method in ['neutral','rolling_frequency','equal_groups','adaptive_groups','calibrated_adaptive']:
        a=result['close_return']['fully_learned_evaluation']['methods'][method]
        b=result['intraday_return']['fully_learned_evaluation']['methods'][method]
        scores.append(f"|{method.replace('_',' ')}|{a['brier']:.5f}|{a['accuracy']:.1%}|{b['brier']:.5f}|{b['accuracy']:.1%}|")
    comparisons={}
    for target in ['close_return','intraday_return']:
        new=pd.read_csv(run/f'evaluation-{target}.csv')
        old=pd.read_csv(BASE/f'adaptive-v2/prequential-{target}.csv')
        joined=new[['target_day','outcome','calibrated_adaptive']].merge(old[['target_day','calibrated_adaptive']],on='target_day',suffixes=('_two_year','_longer'),validate='one_to_one')
        comparisons[target]={'matched_n':len(joined),
            'two_year_brier':float(((joined.calibrated_adaptive_two_year-joined.outcome)**2).mean()),
            'longer_history_brier':float(((joined.calibrated_adaptive_longer-joined.outcome)**2).mean())}
    (run/'matched-window-comparison.json').write_text(json.dumps(comparisons,indent=2),encoding='utf-8')
    c=call['forecasts']['close_return']['up_probability']
    i=call['forecasts']['intraday_return']['up_probability']
    report=f'''# NIFTY: strictly the last two years

Only **17 November 2024–16 November 2026** contributes to this run. The first
available session is 18 November 2024. There are **495 NIFTY sessions**, including
Monday's previously disclosed provisional quote-derived bar, and **475 eligible
feature rows** after indicator warmup.

Every Indian/global series was clipped **before** calculating returns, EMAs,
RSI, volatility or other features. No older indicator initialization, fitted
coefficient, historical prediction or analogue statistic was imported. Source
archives retain older records, but those records do not enter this model.
The dated source freeze is reused so this isolates the history-window change.

## Updated 17 November call

**Neutral:** {c['calibrated_adaptive']:.2%} estimated probability of a close above
Monday's 25,291.10 reference; {i['calibrated_adaptive']:.2%} probability of closing
above today's open. Before calibration, those estimates are
{c['adaptive_groups']:.2%} and {i['adaptive_groups']:.2%}. These are model estimates,
not established success probabilities. Issued {call['issued_at']}.

## Current learned allocations

|Group|Close vs previous close|Open to close|
|---|---:|---:|
{chr(10).join(rows)}

All other groups have zero allocation in this fit. Cash/FII groups retain their
73 historical out-of-sample predictions and remain below the existing evidence
gate. GIFT uses conservatively lagged completed sessions; volatility combines
India VIX and realized measures. These allocations are conditional model weights,
not permanent economic importance.

## What fits into two years

The same feature groups, penalties, recency half-lives and evidence gates are
retained. The overall startup holdoff changes from 504 rows to the existing
252-row expert training minimum, because 504 initial rows cannot fit inside this
window. Monthly expert refits and daily prior-error weight learning remain.

There are **222 chronological predictions after initial expert training**,
23 December 2025–16 November 2026. The first 126 supply error-learning history.
This leaves **96 fully learned evaluation decisions, 1 July–16 November 2026**.
Those dates are selected by availability of prior training evidence, not by
their returns. It would be misleading to call all two years out-of-sample while
using that same period to train and learn the weights.

## Results on those same 96 decisions

|Method|Close Brier ↓|Close accuracy|Intraday Brier ↓|Intraday accuracy|
|---|---:|---:|---:|---:|
{chr(10).join(scores)}

The neutral reference has Brier 0.25000. Its displayed direction accuracy merely
uses the code's 50%-tie-as-up convention; the neutral method makes no directional
call. The learned blend does not establish an edge. Equal-group close accuracy
is 55.2%, but its paired Brier-improvement interval includes zero, and the
predeclared primary method is not replaced after examining that result.
Calibration worsens this run as well. The sample is small and was already
examined in earlier exploratory work.

On exactly these 96 dates, the primary two-year close Brier is
{comparisons['close_return']['two_year_brier']:.5f}, versus
{comparisons['close_return']['longer_history_brier']:.5f} for the longer-history
model. That is a matched-date descriptive comparison, not an independent test.
All 222 post-training forecasts, both evaluation halves, calibration bins and
the 95-decision subset excluding Monday's provisional target are saved in
[validation.json](artifacts/nifty_forecast/2026-11-17/two-year-v1/validation.json).

## Files and checks

- [Frozen forecast](artifacts/nifty_forecast/2026-11-17/two-year-v1/forecast.json)
- [Group weights](artifacts/nifty_forecast/2026-11-17/two-year-v1/group-weights.csv)
- [Individual input coefficients](artifacts/nifty_forecast/2026-11-17/two-year-v1/input-coefficients.csv)
- [Window and data audit](artifacts/nifty_forecast/2026-11-17/two-year-v1/data-audit.json)
- [Fixed rerun design](research/nifty_forecast/TWO_YEAR_PROTOCOL.md)

Five focused checks verify that pre-window price changes cannot affect any
feature, all used series and training labels stay within the boundary, future
labels cannot change earlier expert fits, allocations sum to one, and the prior
forecast remains unchanged. The original data-vintage, conservative global-clock
and institutional-publication assumptions remain in force.

```powershell
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.verify_two_year
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.two_year --out artifacts/nifty_forecast/2026-11-17/two-year-reproduction-01
.\\.venv\\Scripts\\python.exe -m research.nifty_forecast.score --run artifacts/nifty_forecast/2026-11-17/two-year-v1
```

The score command remains pending until the target daily candle is published.
Earlier forecasts are preserved as separate experiments.
'''
    path=ROOT/'NIFTY_TWO_YEAR_2026-11-17.md';path.write_text(report,encoding='utf-8')
    if digest(run/'forecast.json')!=original:raise AssertionError('Frozen call changed')
    print(json.dumps({'report':str(path),'matched_comparison':comparisons}))


if __name__=='__main__':main()
