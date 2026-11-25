"""Fixed-parameter, chronological NIFTY probability experiment (no execution)."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

# Small dense linear algebra should not oversubscribe the user's desktop.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
import pandas as pd
import sys
sys.path[:0] = [str(Path(__file__).resolve().parents[2]/'backend')]
from app.services.nifty_analytics import option_snapshot

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'artifacts/nifty_forecast/2026-11-17'
SEED = 20261117
MODELS = ['climatology', 'yesterday', 'trend20', 'price_logistic',
          'context_logistic', 'analog60', 'nonlinear64', 'ensemble']


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False, default=str), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(folder):
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        expected = expected['sha256'] if isinstance(expected, dict) else expected
        if digest(folder/name) != expected:
            raise ValueError(f'Input hash changed: {name}')
    return manifest


def read_bars(path, target_date, reject_invalid=False):
    source = json.loads(path.read_text(encoding='utf-8'))
    if not source['ok']:
        return pd.DataFrame(), {'unavailable': source.get('error')}
    rows = source['payload'].get('candles', [])
    frame = pd.DataFrame([r[:7] for r in rows], columns=['ts','open','high','low','close','volume','oi'])
    if frame.empty:
        return frame, {'rows': 0}
    frame['day'] = pd.to_datetime(frame.ts, utc=True).dt.tz_convert('Asia/Kolkata').dt.strftime('%Y-%m-%d')
    frame = frame[frame.day < target_date].copy()
    valid = (np.isfinite(frame[['open','high','low','close']]).all(axis=1)
             & (frame[['open','high','low','close']] > 0).all(axis=1)
             & frame.high.ge(frame[['open','close','low']].max(axis=1))
             & frame.low.le(frame[['open','close','high']].min(axis=1)))
    invalid_count = int((~valid).sum())
    if invalid_count and not reject_invalid:
        raise ValueError(f'Invalid OHLC: {path.name}')
    frame = frame.loc[valid].copy()
    duplicates = frame[frame.duplicated('day', keep=False)]
    conflict_days = int(sum(g[['open','high','low','close']].drop_duplicates().shape[0] > 1
                            for _, g in duplicates.groupby('day')))
    # Deterministic canonicalization: prefer midnight daily bars to 09:15 duplicates.
    frame = frame.sort_values('ts').drop_duplicates('day', keep='first').set_index('day').sort_index()
    return frame, {'raw_rows': len(rows), 'sessions': len(frame), 'invalid_rows_rejected':invalid_count,
                   'duplicate_rows': len(rows)-invalid_count-len(frame),
                   'conflicting_duplicate_sessions': conflict_days, 'first': frame.index[0], 'last': frame.index[-1]}


def latest_observations(retained, fresh):
    rows = [r['payload'] for r in retained['observations']] + fresh['observations']
    selected = {}
    for row in rows:
        # Unknown publisher times must not outrank dated readings silently.
        rank = (pd.Timestamp(row['reported_at']).timestamp() if row.get('reported_at') else float('-inf'),
                pd.Timestamp(row['observed_at']).timestamp() if row.get('observed_at') else float('-inf'))
        factor = row['factor_id']
        if factor not in selected or rank >= selected[factor][0]:
            selected[factor] = rank, row
    result = {k: v[1] for k, v in selected.items()}
    if fresh.get('option_chain'):
        for key,metric in option_snapshot(fresh['option_chain']).items():
            result[key] = {**metric, 'factor_id':key,'reported_at':None,
                'observed_at':fresh['collected_at'],'expiry':fresh['option_chain'][0]['expiry'],
                'source':'Upstox option chain','source_url':'https://upstox.com/developer/api-documentation/get-pc-option-chain/',
                'basis':'Derived from the newly acquired snapshot; provider market time is unknown'}
    return result


def load_panel(inputs, supplement, target_date):
    check_manifest(inputs)
    check_manifest(supplement)
    retained = json.loads((inputs/'dashboard-retained.json').read_text(encoding='utf-8'))
    fresh = json.loads((inputs/'dashboard-fresh.json').read_text(encoding='utf-8'))
    bars, audits = {}, {}
    # These quotes were acquired after the Indian close; daily history has not
    # published the same date. Keep the reconstruction explicitly provisional.
    quotes = {r['factor_id']: r for r in fresh['observations']
              if r['source'] == 'Upstox' and isinstance(r.get('context'), dict)
              and r['context'].get('ohlc')}
    provisional = []
    for path in sorted(inputs.glob('daily-*.json')):
        name = path.stem.removeprefix('daily-')
        frame, audits[name] = read_bars(path, target_date)
        if frame.empty:
            continue
        row = quotes.get(name)
        if row and row.get('reported_at'):
            stamp = pd.Timestamp(row['reported_at']).tz_convert('Asia/Kolkata')
            day = stamp.strftime('%Y-%m-%d')
            quote = row['context']['ohlc']
            if frame.index[-1] < day < target_date and (stamp.hour,stamp.minute) >= (15,30):
                if abs(float(row['previous_value'])-float(frame.close.iloc[-1])) > .51:
                    raise ValueError(f'{name}: quote prior close disagrees with history')
                values = [float(quote[k]) for k in ['open','high','low','close']]
                if values[1] < max(values) or values[2] > min(values) or min(values)<=0:
                    raise ValueError(f'{name}: invalid provisional quote OHLC')
                frame.loc[day] = [stamp.isoformat(), *values, quote.get('volume',0), 0]
                provisional.append({'factor': name, 'day': day, 'reported_at': row['reported_at'],
                                    'basis': 'Post-close quote OHLC; daily endpoint still ends on prior session'})
        bars[name] = frame
    globals_ = {}
    for path in sorted(supplement.glob('daily-*.json')):
        name = path.stem.removeprefix('daily-')
        globals_[name], audits['global_'+name] = read_bars(path, target_date, reject_invalid=True)
    if 'nifty_spot' not in bars:
        raise ValueError('No NIFTY daily history')
    return bars, globals_, audits, provisional, retained, fresh


def global_features(frame, target_days):
    """Strict date join prevents the unfinished preceding US session leaking."""
    result = np.full((len(target_days), 3), np.nan)
    if frame.empty:
        return result
    dates = pd.to_datetime(frame.index).to_numpy()
    close = frame.close.astype(float)
    history = np.column_stack([close.pct_change().to_numpy(), close.pct_change(5).to_numpy(),
                               close.pct_change().rolling(20).std().to_numpy()])
    for i, day in enumerate(target_days):
        threshold = np.datetime64(pd.Timestamp(day)-pd.Timedelta(days=1), 'ns')
        j = np.searchsorted(dates, threshold, side='left')-1
        if j >= 0:
            age = (pd.Timestamp(day)-pd.Timestamp(dates[j])).days
            if age <= 7:
                result[i] = history[j]
    return result


def make_features(bars, globals_, target_date):
    d = bars['nifty_spot'].copy()
    d[['open','high','low','close']] = d[['open','high','low','close']].astype(float)
    previous = d.close.shift()
    ret = d.close.pct_change()
    rv = ret.rolling(20).std().clip(lower=.001)
    tr = pd.concat([d.high-d.low,(d.high-previous).abs(),(d.low-previous).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    x = pd.DataFrame(index=d.index)
    for n in [1,2,5,10,20]:
        x[f'return{n}_risk_scaled'] = d.close.pct_change(n)/(rv*np.sqrt(n))
    for n in [10,20,50,200]:
        x[f'ema{n}_distance'] = (d.close/d.close.ewm(span=n, adjust=False).mean()-1)/rv
    up = d.close.diff().clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    down = (-d.close.diff().clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    x['rsi14'] = up/(up+down)
    x['daily_range'] = (d.high-d.low)/atr
    x['body'] = (d.close-d.open)/atr
    x['close_location'] = (d.close-d.low)/(d.high-d.low).replace(0,np.nan)
    x['previous_gap'] = (d.open/previous-1)/rv
    x['realized_vol20'] = rv
    x['vol_ratio5_20'] = ret.rolling(5).std()/rv
    x['atr_pct'] = atr/d.close
    core = list(x.columns)
    next_days = list(d.index[1:])+[target_date]
    sectors = [k for k in bars if k not in ['nifty_spot','india_vix','nifty_500']]
    sector_returns = []
    for name in sectors+['nifty_500']:
        if name not in bars:
            continue
        series = bars[name].close.astype(float).reindex(d.index)
        r1 = series.pct_change(fill_method=None)
        r5 = series.pct_change(5,fill_method=None)
        x[f'{name}_relative1'] = (r1-ret)/rv
        x[f'{name}_relative5'] = (r5-d.close.pct_change(5))/(rv*np.sqrt(5))
        if name in sectors:
            sector_returns.append(r1)
    sector_frame = pd.concat(sector_returns, axis=1)
    x['sector_positive_fraction'] = sector_frame.gt(0).sum(axis=1)/sector_frame.notna().sum(axis=1).replace(0,np.nan)
    x['sector_dispersion'] = sector_frame.std(axis=1)/rv
    vix = bars.get('india_vix', pd.DataFrame()).get('close', pd.Series(dtype=float)).astype(float).reindex(d.index)
    x['vix_level'] = vix
    x['vix_change1'] = vix.pct_change(fill_method=None)
    x['vix_change5'] = vix.pct_change(5,fill_method=None)
    for name, frame in globals_.items():
        values = global_features(frame, next_days)
        for j,suffix in enumerate(['return1','return5','vol20']):
            x[f'lagged_global_{name}_{suffix}'] = values[:,j]
    x = x.replace([np.inf,-np.inf],np.nan)
    # Row t's features know through t's close; the label belongs to t+1.
    labels = pd.DataFrame({'decision_day': d.index, 'target_day': next_days,
        'reference_close': d.close.to_numpy(),
        'close_return': (d.close.shift(-1)/d.close-1).to_numpy(),
        'intraday_return': (d.close.shift(-1)/d.open.shift(-1)-1).to_numpy(),
        'high_excursion': (d.high.shift(-1)/d.close-1).to_numpy(),
        'low_excursion': (d.low.shift(-1)/d.close-1).to_numpy()})
    valid = x[core].notna().all(axis=1).to_numpy()
    return x.loc[valid].reset_index(drop=True), labels.loc[valid].reset_index(drop=True), core


class Scale:
    def fit(self, raw):
        self.median = np.array([np.median(c[np.isfinite(c)]) if np.isfinite(c).any() else 0 for c in raw.T])
        filled = np.where(np.isfinite(raw), raw, self.median)
        self.mean = filled.mean(axis=0)
        self.std = filled.std(axis=0)
        self.std[self.std<1e-8] = 1
        return self

    def transform(self, raw):
        missing = ~np.isfinite(raw)
        z = np.clip((np.where(missing,self.median,raw)-self.mean)/self.std,-5,5)
        return np.column_stack([z,missing.astype(float)])


def sigmoid(value):
    return 1/(1+np.exp(-np.clip(value,-35,35)))


def fit_logistic(raw, labels, penalty):
    a = np.column_stack([np.ones(len(raw)), raw])
    beta = np.zeros(a.shape[1])
    reg = np.eye(a.shape[1])*penalty
    reg[0,0] = 1e-6
    for _ in range(30):
        p = sigmoid(a@beta)
        curvature = (a.T*(p*(1-p)))@a+reg
        step = np.linalg.solve(curvature, a.T@(p-labels)+reg@beta)
        beta -= step
        if np.max(np.abs(step)) < 1e-7:
            break
    return beta


def predict_logistic(raw, beta):
    return np.clip(sigmoid(np.column_stack([np.ones(len(raw)),raw])@beta),.05,.95)


def fit_predict(train, train_y, query, core_indices, raw_query, train_returns):
    full_scaler = Scale().fit(train)
    train_z, query_z = full_scaler.transform(train),full_scaler.transform(query)
    core_scaler = Scale().fit(train[:,core_indices])
    tc = core_scaler.transform(train[:,core_indices])
    qc = core_scaler.transform(query[:,core_indices])
    frequency = (train_y.sum()+1)/(len(train_y)+2)
    predicted = {'climatology': np.full(len(query),frequency),
        'yesterday': np.where(raw_query['return1_risk_scaled'].to_numpy()>0,.55,.45),
        'trend20': np.where(raw_query['return20_risk_scaled'].to_numpy()>0,.55,.45)}
    core_beta = fit_logistic(tc,train_y,10)
    context_beta = fit_logistic(train_z,train_y,10)
    predicted['price_logistic'] = predict_logistic(qc,core_beta)
    predicted['context_logistic'] = predict_logistic(query_z,context_beta)
    rng = np.random.default_rng(SEED)
    weights = rng.normal(size=(train_z.shape[1],64))/np.sqrt(train_z.shape[1])
    phase = rng.uniform(0,2*np.pi,size=64)
    tf = np.sqrt(2)*np.cos(train_z@weights+phase)
    qf = np.sqrt(2)*np.cos(query_z@weights+phase)
    predicted['nonlinear64'] = predict_logistic(qf,fit_logistic(tf,train_y,20))
    analog, distributions = [], []
    for q in query_z:
        dist = np.mean((train_z-q)**2,axis=1)
        idx = np.argsort(dist,kind='stable')[:60]
        w = 1/(np.sqrt(dist[idx])+.25)
        w /= w.sum()
        # Ten effective pseudo-observations shrink small analogue samples.
        analog.append((60*np.dot(w,train_y[idx])+10*frequency)/70)
        distributions.append({'indices':idx.tolist(),'weights':w.tolist(),
                              'returns': train_returns[idx].tolist(),
                              'distance':dist[idx].tolist()})
    predicted['analog60'] = np.clip(analog,.05,.95)
    predicted['ensemble'] = np.mean([predicted[k] for k in ['context_logistic','analog60','nonlinear64']],axis=0)
    return predicted, distributions, {'coefficients': context_beta.tolist(),
        'scaled_query': query_z.tolist(), 'feature_means':full_scaler.mean.tolist(),
        'feature_stds':full_scaler.std.tolist(), 'feature_medians':full_scaler.median.tolist()}


def walk_forward(x, labels, core, label_name, sessions=504):
    resolved = labels[label_name].notna().to_numpy()
    indices = np.flatnonzero(resolved)
    test = indices[-sessions:]
    if test[0]<504:
        raise ValueError('Insufficient chronological training history')
    xraw=x.to_numpy(dtype=float)
    core_indices=[x.columns.get_loc(c) for c in core]
    y=(labels[label_name].to_numpy()>0).astype(float)
    output=[]
    months=labels.loc[test,'target_day'].str[:7]
    for month in months.unique():
        query_idx=test[months.to_numpy()==month]
        first=int(query_idx[0])
        train_idx=indices[indices<first][-1260:]
        if labels.target_day.iloc[train_idx[-1]] > labels.decision_day.iloc[first]:
            raise AssertionError('Training outcome not resolved before decision')
        predicted,_,_=fit_predict(xraw[train_idx],y[train_idx],xraw[query_idx],core_indices,
                                  x.iloc[query_idx],labels[label_name].to_numpy()[train_idx])
        for j,i in enumerate(query_idx):
            row={'i':int(i),'target_day':labels.target_day.iloc[i],'decision_day':labels.decision_day.iloc[i],
                 'outcome':int(y[i]),'return':float(labels[label_name].iloc[i]),
                 'training_last_target':labels.target_day.iloc[train_idx[-1]],
                 'training_n':len(train_idx)}
            row.update({k:float(v[j]) for k,v in predicted.items()})
            # Rolling empirical intervals use all outcomes resolved at decision.
            history=labels[label_name].iloc[:i].dropna().to_numpy()[-252:]
            row.update({f'q{int(q*100)}':float(np.quantile(history,q)) for q in [.1,.25,.75,.9]})
            output.append(row)
    return pd.DataFrame(output)


def block_interval(values):
    rng=np.random.default_rng(SEED)
    n=len(values);length=10
    starts=rng.integers(0,n-length+1,(2000,int(np.ceil(n/length))))
    indices=(starts[:,:,None]+np.arange(length)).reshape(2000,-1)[:,:n]
    return np.quantile(np.asarray(values)[indices].mean(axis=1),[.025,.975]).tolist()


def score(frame):
    y=frame.outcome.to_numpy()
    baseline=(frame.climatology.to_numpy()-y)**2
    results={}
    for name in MODELS:
        p=frame[name].to_numpy()
        loss=(p-y)**2
        results[name]={'n':len(y),'accuracy':float(np.mean((p>=.5)==y)),
            'brier':float(loss.mean()),'log_loss':float(np.mean(-y*np.log(p)-(1-y)*np.log(1-p))),
            'brier_improvement_vs_baseline':float(np.mean(baseline-loss)),
            'paired_improvement_ci95':block_interval(baseline-loss),
            'first_half_brier':float(loss[:len(y)//2].mean()),
            'second_half_brier':float(loss[len(y)//2:].mean())}
    p=frame.ensemble.to_numpy()
    bins=[]
    for lower,upper in zip([0,.4,.45,.5,.55,.6],[.4,.45,.5,.55,.6,1.0001]):
        m=(p>=lower)&(p<upper)
        if m.any():
            bins.append({'lower':lower,'upper':min(upper,1),'n':int(m.sum()),
                         'mean_predicted':float(p[m].mean()),'observed_up':float(y[m].mean())})
    strong=(p>=.6)|(p<=.4)
    return {'period':[frame.target_day.iloc[0],frame.target_day.iloc[-1]],'up_frequency':float(y.mean()),
        'models':results,'ensemble_calibration':bins,'strong_call_sessions':int(strong.sum()),
        'strong_call_accuracy':float(np.mean((p[strong]>=.5)==y[strong])) if strong.any() else None,
        'empirical50_coverage':float(((frame['return']>=frame.q25)&(frame['return']<=frame.q75)).mean()),
        'empirical80_coverage':float(((frame['return']>=frame.q10)&(frame['return']<=frame.q90)).mean())}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--inputs',type=Path,default=BASE/'inputs-v2')
    parser.add_argument('--supplement',type=Path,default=BASE/'supplement-v1')
    parser.add_argument('--out',type=Path,default=BASE/'run-v1')
    parser.add_argument('--date',default='2026-11-17')
    args=parser.parse_args()
    if args.out.exists():
        raise FileExistsError('Choose a new output folder; prior forecasts are immutable')
    args.out.mkdir(parents=True)
    bars,globals_,audits,provisional,retained,fresh=load_panel(args.inputs,args.supplement,args.date)
    x,labels,core=make_features(bars,globals_,args.date)
    x.to_csv(args.out/'feature-panel.csv',index=False)
    labels.to_csv(args.out/'labels.csv',index=False)
    write_json(args.out/'data-audit.json',{'series':audits,'provisional_bars':provisional,
        'feature_count':len(x.columns),'core_features':core,'context_features':list(x.columns[len(core):])})
    outcomes={}
    forecasts={}
    analogues=[]
    for target in ['close_return','intraday_return']:
        replay=walk_forward(x,labels,core,target)
        replay.to_csv(args.out/f'walk-forward-{target}.csv',index=False)
        outcomes[target]=score(replay)
        n=len(x)-1
        train_idx=np.flatnonzero(labels[target].notna().to_numpy())[-1260:]
        pred,dist,fit=fit_predict(x.to_numpy()[train_idx],(labels[target].to_numpy()[train_idx]>0).astype(float),
            x.to_numpy()[[n]],[x.columns.get_loc(c) for c in core],x.iloc[[n]],labels[target].to_numpy()[train_idx])
        history=labels[target].iloc[train_idx].to_numpy()[-252:]
        forecasts[target]={'up_probability':{k:float(v[0]) for k,v in pred.items()},
            'prior252_mean':float(history.mean()),'prior252_median':float(np.median(history)),
            'prior252_quantiles':{str(q):float(np.quantile(history,q)) for q in [.1,.25,.5,.75,.9]},
            'analog60_mean':float(np.dot(dist[0]['weights'],dist[0]['returns'])),
            'analog60_quantiles_unweighted':{str(q):float(np.quantile(dist[0]['returns'],q)) for q in [.1,.25,.5,.75,.9]},
            'training_last_target':labels.target_day.iloc[train_idx[-1]],'training_n':len(train_idx)}
        if target=='close_return':
            for j,weight,distance in zip(dist[0]['indices'],dist[0]['weights'],dist[0]['distance']):
                idx=train_idx[j]
                analogues.append({'decision_day':labels.decision_day.iloc[idx],
                    'target_day':labels.target_day.iloc[idx],'weight':weight,'distance':distance,
                    'close_return':float(labels.close_return.iloc[idx]),
                    'intraday_return':float(labels.intraday_return.iloc[idx])})
            coefficients=np.asarray(fit['coefficients'])[1:]
            scaled=np.asarray(fit['scaled_query'])[0]
            names=list(x.columns)+[c+'_missing' for c in x.columns]
            contributions=sorted([{'feature':name,'log_odds_contribution':float(a*b),'coefficient':float(a)}
                for name,a,b in zip(names,coefficients,scaled)],key=lambda r:abs(r['log_odds_contribution']),reverse=True)
            write_json(args.out/'context-model-contributions.json',{'intercept':fit['coefficients'][0],
                'note':'Conditional model contributions; correlated features prevent causal attribution',
                'contributions':contributions})
            write_json(args.out/'context-model-fit.json',fit)
    write_json(args.out/'validation.json',outcomes)
    pd.DataFrame(analogues).to_csv(args.out/'analogues.csv',index=False)
    reference=float(labels.reference_close.iloc[-1])
    forecasts['close_return']['closing_level_quantiles']={k:reference*(1+v) for k,v in forecasts['close_return']['prior252_quantiles'].items()}
    last252=labels.iloc[:-1].tail(252)
    price=bars['nifty_spot']
    levels={'reference_close':reference,'reference_day':price.index[-1],
        'previous_session_high':float(price.high.iloc[-1]),'previous_session_low':float(price.low.iloc[-1]),
        'previous_session_open':float(price.open.iloc[-1]),
        'prior20_high':float(price.high.iloc[-20:].max()),'prior20_low':float(price.low.iloc[-20:].min()),
        'median_high_excursion_level':reference*(1+float(last252.high_excursion.median())),
        'median_low_excursion_level':reference*(1+float(last252.low_excursion.median()))}
    latest=latest_observations(retained,fresh)
    factors=[]
    for definition in retained['factors']:
        row=latest.get(definition['id'])
        numeric_or_text=row and row.get('value') is not None
        status='dated_context' if numeric_or_text and row.get('reported_at') else 'undated_context' if numeric_or_text else 'unavailable'
        if row and row.get('quality_note'):
            status='quality_excluded'
        factors.append({'id':definition['id'],'label':definition['label'],'section_id':definition['section_id'],
                        'status':status,'observation':row,
                        'trained_price_series':definition['id'] in bars or definition['id'] in globals_,
                        'reported_age_hours':float((pd.Timestamp.now(tz='UTC')-pd.Timestamp(row['reported_at'])).total_seconds()/3600)
                            if row and row.get('reported_at') else None})
    write_json(args.out/'factor-inventory.json',factors)
    forecast={'experiment':'NIFTY pre-market ensemble v1','target_date':args.date,
        'issued_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),
        'input_freeze_times':[json.loads((f/'manifest.json').read_text())['frozen_at'] for f in [args.inputs,args.supplement]],
        'input_manifests':{str(p):digest(p) for p in [args.inputs/'manifest.json',args.supplement/'manifest.json']},
        'source_code_hashes':{p.name:digest(p) for p in [Path(__file__),Path(__file__).with_name('PROTOCOL.md')]},
        'features':list(x.columns),'levels':levels,'forecasts':forecasts,
        'provisional_reference':True,'provisional_bars':provisional,
        'outcome':{'official_close':None,'official_open':None,'close_direction_correct':None,'intraday_direction_correct':None},
        'limits':['Exploratory historical reconstruction, not a vintage replay',
            'Monday inputs reconstructed from post-close quotes while daily endpoint ends Friday',
            'Global fitted features use safely completed daily sessions; current partial US session is commentary only',
            'Unknown-time options and unverified cash units are not fitted predictors',
            'Probability estimates are not independently established calibrated confidence']}
    write_json(args.out/'forecast.json',forecast)
    print(json.dumps({'out':str(args.out),'features':len(x.columns),'sessions':len(x),'reference':reference,
        'forecast':forecasts,'validation':{k:{'period':v['period'],'baseline':v['models']['climatology'],
            'ensemble':v['models']['ensemble']} for k,v in outcomes.items()}},indent=2),flush=True)


if __name__=='__main__':
    main()
