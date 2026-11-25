"""Frozen OHLC labels, point-in-time features, and source quality checks."""
from .common import *
from research.nifty_forecast_v9.run_models import cohort_queries
from research.nifty_forecast_v5.data import load as older_universe

OHLC = ['open', 'high', 'low', 'close']
SHAPE = ['atm_iv', 'down_iv', 'up_iv', 'curvature', 'density_q10', 'density_q90',
         'implied_skew_moment', 'density_five_pct_down', 'strip_var']
POSITION = ['oi_hhi', 'oi_near', 'pc_oi', 'oi_flow', 'vol_oi', 'put_wall', 'call_wall', 'oi_roll_gap']
GLOBAL = ['vix_us', 'us_rv', 'asia_rv', 'nasdaq_rv', 'fx_rv', 'oil_rv', 'dgs10_change', 'intl_dispersion', 'q_corr_change']
DOMESTIC = ['finance', 'breadth5', 'breadth21', 'cash5', 'sector_dispersion', 'concentration']
LOCAL = ['har5', 'har21', 'har63', 'intraday_rv', 'overnight_rv', 'vix_level']


def valid_ohlc(frame):
    arr = frame[OHLC].to_numpy(float)
    return np.isfinite(arr).all(axis=1) & (arr > 0).all(axis=1) & (arr[:, 1] >= arr.max(axis=1)) & (arr[:, 2] <= arr.min(axis=1))


def daily():
    p = matrix('price.csv')[OHLC]
    official = matrix('official-index-closes.csv', V11).nifty50
    assert p.index.is_unique and p.index.is_monotonic_increasing and p.index.max() <= FREEZE
    assert p.index.min() >= '2025-01-01'
    assert valid_ohlc(p).all()
    return p, official


def intraday(p):
    records, grids = [], {}
    daily_index = p.index
    for interval in [1, 5, 25]:
        paths = (sorted((OUT / 'sources/upstox').glob(f'nifty-{interval}m-*.json')) if interval != 25 else
                 sorted((V7 / 'intraday-sources').glob('*.json')))
        for path in paths:
            data = loads(path)['data']['candles']
            f = pd.DataFrame(data, columns=['ts', *OHLC, 'volume', 'oi'])
            if f.empty:
                continue
            ts = pd.to_datetime(f.ts, utc=True).dt.tz_convert('Asia/Kolkata')
            f['day'] = ts.dt.strftime('%Y-%m-%d')
            f['minute'] = ts.dt.hour * 60 + ts.dt.minute
            expected = np.arange(555, 930, interval)
            for day, g in f.groupby('day'):
                if day not in daily_index:
                    continue
                g = g.sort_values('minute')
                complete = np.array_equal(g.minute.to_numpy(), expected) and valid_ohlc(g).all()
                a = g[OHLC].to_numpy()
                high_delta = a[:, 1].max() - p.high.at[day]
                low_delta = a[:, 2].min() - p.low.at[day]
                close_delta = a[-1, 3] - p.close.at[day]
                # Source revisions can change the extrema. Strict ordering uses the daily-reconciled grid.
                reconciled = complete and max(abs(high_delta), abs(low_delta)) <= 1.0
                rv = np.linalg.norm(np.diff(np.log(np.r_[a[0, 0], a[:, 3]]))) if complete else np.nan
                records.append(dict(day=day, interval=interval, bars=len(a), complete=bool(complete),
                                    reconciled_extrema=bool(reconciled), high_delta=high_delta, low_delta=low_delta,
                                    close_delta=close_delta, intraday_sd=rv, source=str(path.relative_to(ROOT))))
                if reconciled and day not in grids and interval <= 5:
                    grids[day] = a
    result = pd.DataFrame(records)
    write('intraday-audit.csv', result, index=False)
    return result, grids


def path_metrics(paths):
    """Absolute price paths normalized to the reference close. Drawdowns use closes in time order."""
    close = paths[:, :, 3]
    hi, lo = paths[:, :, 1].max(axis=1), paths[:, :, 2].min(axis=1)
    history = np.column_stack([np.ones(len(paths)), close])
    cc = np.diff(np.log(history), axis=1)
    overnight = np.log(paths[:, :, 0] / history[:, :-1])
    regular = np.log(close / paths[:, :, 0])
    return dict(endpoint_return=close[:, -1] - 1, abs_return=abs(close[:, -1] - 1),
        volatility=np.sqrt(252 * np.mean(cc**2, axis=1)), high=hi - 1, low=lo - 1, range=hi - lo,
        close_high=close.max(axis=1) - 1, close_low=close.min(axis=1) - 1,
        drawdown=np.min(history / np.maximum.accumulate(history, axis=1) - 1, axis=1),
        rebound=np.max(history / np.minimum.accumulate(history, axis=1) - 1, axis=1),
        positive_days=(cc > 0).sum(axis=1), max_daily=np.abs(cc).max(axis=1),
        overnight_sd=np.sqrt(252 * np.mean(overnight**2, axis=1)), regular_sd=np.sqrt(252 * np.mean(regular**2, axis=1)))


def paths_for(p, h):
    a = p[OHLC].to_numpy()
    block = np.stack([a[i+1:i+1+h] / a[i, 3] for i in range(len(a) - h)])
    index = p.index[:-h]
    labels = pd.DataFrame(path_metrics(block), index=index)
    labels['endpoint'] = p.index[h:]
    labels['reference'] = p.close.loc[index]
    old = matrix(f'labels-{h}.csv').loc[index]
    np.testing.assert_array_equal(labels.endpoint, old.endpoint)
    np.testing.assert_allclose(labels.endpoint_return, old['return'], atol=2e-12)
    np.testing.assert_allclose(labels.volatility, old.volatility, atol=2e-12)
    return block, labels


def barrier_order(daily_path, dates, intrabars, ref, level):
    hit_u = np.flatnonzero(daily_path[:, 1] >= 1 + level)
    hit_d = np.flatnonzero(daily_path[:, 2] <= 1 - level)
    if not len(hit_u):
        return ('lower' if len(hit_d) else 'neither'), 'daily'
    if not len(hit_d) or hit_u[0] < hit_d[0]:
        return 'upper', 'daily'
    if hit_d[0] < hit_u[0]:
        return 'lower', 'daily'
    i = hit_u[0]
    day = dates[i]
    start = daily_path[i, 0]
    if start >= 1 + level or start <= 1 - level:
        return ('upper' if start >= 1 + level else 'lower'), 'open'
    if day in intrabars:
        bars = intrabars[day] / ref
        u = np.flatnonzero(bars[:, 1] >= 1 + level)
        d = np.flatnonzero(bars[:, 2] <= 1 - level)
        if len(u) and len(d) and u[0] != d[0]:
            return ('upper' if u[0] < d[0] else 'lower'), 'intraday'
        if len(u) and len(d):
            op = bars[u[0], 0]
            if op >= 1 + level or op <= 1 - level:
                return ('upper' if op >= 1 + level else 'lower'), 'intraday-open'
    return 'ambiguous', 'same candle'


def estimators(p, intra):
    o, hi, lo, c = (np.log(p[k]) for k in OHLC)
    cc = c.diff()
    gap = o - c.shift()
    oc = c - o
    out = pd.DataFrame(index=p.index)
    var = cc**2
    for n in [5, 10, 21, 42, 63]:
        out[f'har{n}'] = np.sqrt(252 * var.rolling(n, min_periods=min(n, 21)).mean())
    out['ewma'] = np.sqrt(252 * var.ewm(alpha=.06, adjust=False, min_periods=16).mean())
    out['ewma_fast'] = np.sqrt(252 * var.ewm(alpha=.14, adjust=False, min_periods=16).mean())
    rs = (hi - o) * (hi - c) + (lo - o) * (lo - c)
    for key, s in {'parkinson': (hi-lo)**2 / (4*np.log(2)),
                   'garman_klass': .5*(hi-lo)**2 - (2*np.log(2)-1)*oc**2,
                   'rogers_satchell': rs}.items():
        out[key] = np.sqrt(252 * s.rolling(21, min_periods=15).mean().clip(lower=0))
        out[key + '_gap'] = np.sqrt(out[key]**2 + 252 * gap.pow(2).rolling(21, min_periods=15).mean())
    k = .34 / (1.34 + 22/20)
    out['yang_zhang'] = np.sqrt(252 * (gap.rolling(21).var() + k*oc.rolling(21).var() + (1-k)*rs.rolling(21).mean()))
    out['overnight_rv'] = np.sqrt(252 * gap.pow(2).rolling(21).mean())
    if not intra.empty:
        for size in [1, 5, 25]:
            sd = intra.loc[intra.complete & intra.interval.eq(size)].set_index('day').intraday_sd.reindex(p.index)
            out[f'intraday_{size}m'] = np.sqrt(252 * (sd.pow(2) + gap.pow(2)).rolling(21, min_periods=15).mean())
    if 'intraday_5m' in out:
        # Keep one bar resolution through time. The full model uses the five-minute estimator.
        out['intraday_rv'] = out.intraday_5m
    else:
        out['intraday_rv'] = out.get('intraday_25m', np.nan)
    out['market_return'] = cc
    return out


def option_features():
    s = pd.read_csv(V12 / 'surface-quality.csv', low_memory=False)
    s = s.loc[s.method.eq('TRADE') & s.iv_status.eq('accepted')].copy()
    strikes = pd.read_csv(V12 / 'strike-implied-volatility.csv.gz', low_memory=False)
    strips = []
    for (d, e), a in strikes[strikes.iv_valid].groupby(['day', 'expiry']):
        a = a.sort_values('moneyness_forward')
        k = np.r_[a.moneyness_forward.to_numpy(float)]
        if len(k) < 20 or not (k.min() < .97 and k.max() > 1.03):
            continue
        tau = (pd.Timestamp(e) - pd.Timestamp(d)).days / 365.
        # The forward kink lies inside the observed strip. The observed wings truncate the variance integral.
        value = 2 / tau * np.trapezoid(a.premium_fraction_forward_undiscounted / k**2, k)
        strips.append((d, e, value))
    s = s.merge(pd.DataFrame(strips, columns=['day', 'expiry', 'strip_var']), on=['day', 'expiry'], how='left')
    s['skew_down'] = s.down_iv - s.atm_iv
    s['skew_up'] = s.up_iv - s.atm_iv
    s['up5_proxy'] = np.nan
    from research.nifty_forecast_v12.common import bundle_entries
    tails = {(d,e): float(law.w[law.a >= .05].sum())
             for (d,e,m),law in bundle_entries(V12 / 'option-density-atoms.npz') if m == 'TRADE'}
    s['up5_proxy'] = [tails.get((d,e), np.nan) for d,e in zip(s.day,s.expiry)]
    fields = SHAPE + ['skew_down', 'skew_up', 'up5_proxy', 'atm_call_put_iv_gap']
    samples = []
    for day, g in s.groupby('day'):
        g = g.sort_values('dte')
        row = {'day': day}
        for tenor in (7, 14, 30, 45):
            left = g[g.dte.le(tenor)].tail(1)
            right = g[g.dte.ge(tenor)].head(1)
            if left.empty or right.empty:
                continue
            a,b = left.iloc[0],right.iloc[0]
            if b.total_variance + 1e-12 < a.total_variance:
                continue
            weight = (tenor-a.dte)/(b.dte-a.dte) if b.dte>a.dte else 0.
            for k in fields:
                row[f's{k}{tenor}'] = (1-weight)*a[k]+weight*b[k]
            row[f'satm_iv{tenor}'] = np.sqrt(((1-weight)*a.total_variance+weight*b.total_variance)*365/tenor)
        samples.append(row)
    shape = pd.DataFrame(samples).set_index('day')
    shape['term_slope'] = shape.satm_iv30 - shape.satm_iv7
    shape['term_curve'] = shape.satm_iv30 - shape.satm_iv14 - (shape.satm_iv14-shape.satm_iv7)*16/7
    shape['skew_acceleration'] = shape.sskew_down30.diff().diff()
    shape['term_transition'] = np.sign(shape.term_slope).diff()
    change = ['satm_iv7','satm_iv30','sskew_down30','sskew_up30','scurvature30','term_slope','term_curve',
              'sdensity_five_pct_down30','sup5_proxy30','simplied_skew_moment30']
    shape = shape.join(shape[change].diff().add_suffix('_chg1')).join(shape[change].diff(5).add_suffix('_chg5'))
    write('constant-maturity-surface.csv', shape, index=True)
    return s, shape


def positioning(s):
    a = pd.read_csv(V12/'sources/nifty-udiff.csv.gz', usecols=['day','kind','expiry','side','strike','oi','oi_change','volume'])
    a = a[a.kind.eq('IDO') & a.oi.ge(0)]
    a = a.merge(s[['day','expiry','forward','dte']], on=['day','expiry'], how='inner')
    a['distance'] = np.log(a.strike / a.forward)
    rows = []
    for (day, expiry), g in a.groupby(['day','expiry']):
        total = g.oi.sum()
        if not total:
            continue
        c = g[g.side.eq('CE')]
        p = g[g.side.eq('PE')]
        if c.empty or p.empty:
            continue
        rows.append(dict(day=day, expiry=expiry, dte=int(g.dte.iloc[0]), oi_hhi=np.square(g.oi/total).sum(),
                         oi_near=g.loc[g.distance.abs().le(.02),'oi'].sum()/total,
                         pc_oi=p.oi.sum()/total, oi_flow=g.oi_change.sum()/total,
                         vol_oi=g.volume.sum()/total, put_wall=p.loc[p.oi.idxmax(),'distance'],
                         call_wall=c.loc[c.oi.idxmax(),'distance']))
    details = pd.DataFrame(rows)
    write('unsigned-strike-positioning.csv', details, index=False)
    return details


def global_risk(index):
    data,_ = older_universe()
    a = pd.read_csv(V5/'global-availability.csv')
    a = a[a.source_day.lt(a.origin) & pd.to_datetime(a.available_assumption, utc=True, format='mixed').le(pd.to_datetime(a.decision, utc=True, format='mixed'))]
    risk = pd.DataFrame(index=index)
    clocks = []
    for col, raw in [('us','g_^GSPC'),('asia','g_^N225'),('hk','g_^HSI'),('nasdaq','g_IXIX'),
                     ('fx','g_USDINR'),('oil','g_BZUSD')]:
        if raw not in data:
            continue
        close = data[raw].close.loc['2025-01-01':FREEZE].dropna()
        returns = np.log(close).diff()
        stamps = a[a.series.eq(raw)].drop_duplicates('origin').set_index('origin').source_day.reindex(index)
        risk[col+'_rv'] = stamps.map(np.sqrt(252*returns.pow(2).rolling(15,min_periods=10).mean()))
        risk[col+'_shock'] = stamps.map(returns.abs())
        clocks.append(a[a.series.eq(raw)].loc[:,['origin','source_day','decision','available_assumption','series']])
    if clocks:
        write('foreign-risk-clock.csv', pd.concat(clocks), index=False)
    shock = risk[[c for c in ['us_shock','asia_shock','hk_shock','nasdaq_shock'] if c in risk]]
    risk['intl_dispersion'] = shock.std(axis=1)
    return risk


def prepare():
    register()
    p, official = daily()
    intra, grids = intraday(p)
    s, shape = option_features()
    oi = positioning(s)
    global_x = global_risk(p.index)
    early = pd.DataFrame(loads(V5/'sources/nifty_spot.json')['rows']).set_index('day')[OHLC].sort_index()
    early = early.loc['2025-01-01':p.index[0]].iloc[:-1]
    risk = estimators(pd.concat([early,p]), intra).reindex(p.index)
    # The historical anchors use the exact inherited reference close and OHLC.
    audit = pd.DataFrame({'frozen_close':p.close,'official_close':official.reindex(p.index)})
    audit['difference'] = audit.frozen_close - audit.official_close
    write('daily-close-audit.csv', audit, index=True)
    for h in HORIZONS:
        block, labels = paths_for(p,h)
        q = cohort_queries(h).set_index('origin')
        assert q.index.isin(labels.index).all()
        labels['cohort'] = q.split
        f = pd.read_csv(V12/f'features/{h}-TRADE.csv',index_col=0).reindex(p.index)
        clock = pd.read_csv(V12/'horizon-alignment.csv')
        clock=clock[clock.horizon.eq(h)&clock.version.eq('TRADE')].set_index('origin').reindex(p.index)
        assert clock.option_source_day.dropna().lt(clock.option_source_day.dropna().index.to_series()).all()
        x = f.join(risk).join(global_x).join(shape.reindex(clock.option_source_day).set_axis(p.index)).copy()
        x['iv_session'] = x.iv_nearest * np.sqrt((clock.target_dte_at_origin / 365.)/(h/252.))
        x['iv_bracket_session'] = x.iv_bracket * np.sqrt((clock.target_dte_at_origin / 365.)/(h/252.))
        x['iv_exact'] = pd.read_csv(V12/f'features/{h}-NATURAL.csv',index_col=0).iv_nearest
        x['iv_legacy_bracket'] = pd.read_csv(V12/f'features/{h}-BRACKET.csv',index_col=0).iv_bracket
        x['variance_gap'] = x.iv_nearest**2 - x.har21**2
        x['iv_relative'] = np.log(x.iv_nearest / x.har21)
        x['iv_ratio_change'] = x.iv_relative.diff(5)
        x['iv_breadth'] = x.iv_relative * x.breadth5
        x['iv_finance'] = x.iv_relative * x.finance
        x['global_iv_gap'] = x.vix_us/100 - x.iv_nearest
        x['global_breadth'] = x.vix_us*x.breadth5/100
        nearest = clock[['option_source_day','expiry']].rename_axis('forecast_origin').reset_index().merge(
            oi,left_on=['option_source_day','expiry'],right_on=['day','expiry'],how='left').set_index('forecast_origin')
        other = oi.sort_values('dte').groupby('day').last().oi_hhi
        nearest['oi_roll_gap'] = nearest.oi_hhi - nearest.option_source_day.map(other)
        x = x.join(nearest[POSITION])
        x = x.join(x[POSITION].diff(5).add_suffix('_chg5'))
        x['roll_surface'] = clock.expiry.ne(clock.expiry.shift()).astype(float)
        x['expiry_gap'] = clock.maturity_gap_days
        x['source_dte'] = clock.source_dte
        x['option_day'] = clock.option_source_day
        x['iv_same_contract_change'] = clock.iv_nearest.diff().where(x.roll_surface.eq(0))
        for variant in ['LAG2','LAG5','RATE_ZERO','RATE_HIGH','LIQUID','SETTLEMENT','SMOOTH','TRUNCATED','FUTURE_FORWARD','LONGER','SAME_CLOSE']:
            z = pd.read_csv(V12/f'features/{h}-{variant}.csv',index_col=0)
            x[f'iv_{variant.lower()}'] = z.iv_nearest
        for t, level in enumerate(THRESHOLDS):
            labels[f'upper_touch_{t}'] = labels.high.ge(level)
            labels[f'lower_touch_{t}'] = labels.low.le(-level)
            labels[f'upper_close_{t}'] = labels.close_high.ge(level)
            labels[f'lower_close_{t}'] = labels.close_low.le(-level)
            labels[f'upper_endpoint_{t}'] = labels.endpoint_return.ge(level)
            labels[f'lower_endpoint_{t}'] = labels.endpoint_return.le(-level)
            ordered = [barrier_order(a,p.index[i+1:i+1+h],grids,p.close.iloc[i],level) for i,a in enumerate(block)]
            labels[f'ordering_{t}'], labels[f'ordering_source_{t}'] = zip(*ordered)
        write(f'targets-{h}.csv', labels, index=True)
        write(f'features-{h}.csv', x.replace([np.inf,-np.inf],np.nan), index=True)
        np.savez_compressed(OUT/f'observed-paths-{h}.npz', paths=block, origins=labels.index.to_numpy(str))
        print(h, 'sessions', len(q), 'frozen queries and',len(labels),'maturable OHLC paths',flush=True)
    save('data-quality.json', dict(daily_sessions=len(p), first=p.index.min(), last=p.index.max(),
         official_difference_gt_005=int(audit.difference.abs().gt(.05).sum()), current_intraday_reconciled=len(grids),
         intraday=intra.groupby('interval').agg(sessions=('day','size'),complete=('complete','sum'),
             reconciled=('reconciled_extrema','sum')).reset_index().to_dict('records'),
         global_inputs=list(global_x), implied_expiries=len(s), position_rows=len(oi), daily_source=str(V6/'price.csv')))


if __name__ == '__main__':
    prepare()

