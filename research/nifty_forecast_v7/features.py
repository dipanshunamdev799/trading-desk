"""Causal sector structure, liquidity and specified data perturbations."""
import warnings
from .common import *
from research.nifty_forecast_v5.data import load
from research.nifty_forecast_v5.features import build
from research.nifty_forecast_v5.expansion import variant

SECTORS = ['bank_nifty','nifty_financial','nifty_it','nifty_auto','nifty_metal',
           'nifty_pharma','nifty_fmcg','nifty_energy','nifty_realty']
LEVELS = ['lambda_share','effective_rank','mean_corr','corr_dispersion','network_density',
          'rv_sync','leader_persistence','participation','concentration','financial_spread',
          'defensive_dispersion','breadth_relative']
CHANGE_BASE = ['mean_corr','lambda_share','rv_sync','participation','concentration','financial_spread']


def structure(raw, index):
    price = raw['nifty_spot']
    closes = pd.DataFrame({name: raw[name].close.reindex(price.index) for name in SECTORS})
    daily = closes.pct_change(fill_method=None)
    mom = closes.pct_change(5, fill_method=None)
    rv = daily.rolling(5).std()
    out = pd.DataFrame(index=price.index, columns=LEVELS, dtype=float)
    mask = np.triu_indices(len(SECTORS), k=1)
    vectors = {}
    for j in range(20, len(daily)):
        sample = daily.iloc[j-20:j+1]
        if sample.isna().any().any():
            continue
        cor = sample.corr().to_numpy()
        risk_corr = rv.iloc[j-20:j+1].corr().to_numpy()[mask]
        eigen, loading = np.linalg.eigh(cor)
        shares = np.maximum(eigen, 1e-12)/eigen.sum()
        vec = loading[:, -1]
        vectors[j] = vec
        out.iloc[j, :6] = [shares[-1], np.exp(-shares @ np.log(shares)), cor[mask].mean(), cor[mask].std(),
                          (cor[mask]>.65).mean(), np.mean(risk_corr)]
    out['loading_drift'] = [1-abs(vectors[j] @ vectors[j-5]) if j in vectors and j-5 in vectors else np.nan for j in range(len(out))]
    out['leader_persistence'] = mom.rank(axis=1).corrwith(mom.shift(5).rank(axis=1), axis=1)
    out['participation'] = mom.gt(0).sum(axis=1)/mom.notna().sum(axis=1).replace(0,np.nan)
    out['concentration'] = mom.abs().max(axis=1)/mom.abs().sum(axis=1).replace(0,np.nan)
    out['financial_spread'] = mom.bank_nifty-mom.nifty_financial
    out['defensive_dispersion'] = mom[['nifty_fmcg','nifty_pharma']].mean(axis=1)-mom[['nifty_auto','nifty_metal','nifty_energy']].mean(axis=1)
    out['breadth_relative'] = mom.mean(axis=1)-price.close.pct_change(5)
    for col in CHANGE_BASE:
        out[col+'_change5'] = out[col].diff(5)
        out[col+'_accel'] = out[col].diff(5).diff(5)
    # Observed high-correlation state, transition matrix from transitions with both dates observed.
    state = (out.mean_corr > .60).where(out.mean_corr.notna())
    prev = state.shift(1)
    variables = {}
    for current in [False, True]:
        tried = ((prev == current) & state.notna()).rolling(63,min_periods=40).sum()
        success = ((prev == current) & (state == True)).rolling(63,min_periods=40).sum()
        variables[current] = (success + 2)/(tried + 4)
    out['p_high_corr_next'] = variables[True].where(state == True, variables[False]).where(state.notna())
    out['participation_persist'] = out.participation.rolling(21).mean()
    out['correlation_persist'] = out.mean_corr.rolling(21).mean()
    out['vol_sync_persist'] = out.rv_sync.rolling(21).mean()
    return out.reindex(index), daily, mom, rv


def liquidity(raw, index):
    daily = raw['nifty_spot']; close = daily.close
    vol = matrix('liquidity-reference.csv').filter(regex='_volume$')
    level = vol.mean(axis=1)
    features = pd.DataFrame({'l_etf_average':level,'l_etf_delta5':level.diff(5),
         'l_overnight5': np.log(daily.open/close.shift()).rolling(5).sum(),
         'l_openclose5': np.log(close/daily.open).rolling(5).sum(),
         'l_range5':np.log(daily.high/daily.low).rolling(5).mean()}).reindex(index)
    previous = matrix('features.csv', V5)
    positions = previous[['d_fut_basis','d_fut_oi_log_change','d_oi_pcr','d_call_concentration','d_put_concentration']]
    stock = pd.DataFrame({n:f.close.reindex(close.index) for n,f in raw.items() if n.startswith('s_')})
    ret = stock.pct_change(fill_method=None).where(lambda a: a.abs()<=.35)
    trading = pd.DataFrame({n:f.volume.reindex(close.index) for n,f in raw.items() if n.startswith('s_')})
    ratio = np.log(trading.where(trading.gt(0))/trading.shift().rolling(21,min_periods=15).median().where(lambda a: a.gt(0)))
    proxy = pd.DataFrame({'proxy_dispersion':ret.std(axis=1),'proxy_participation':ret.gt(0).sum(axis=1)/ret.notna().sum(axis=1),
                         'proxy_volume':ratio.median(axis=1),'proxy_stock_count':ret.notna().sum(axis=1)}).reindex(index)
    return pd.concat([features,positions,proxy],axis=1)


def inputs():
    if not read('v6-reproduction.json')['passed']:
        raise RuntimeError('Run the reference reproduction first')
    raw, inventory = load()
    index = matrix('native-reference.csv').index
    struct, daily, momentum, vol = structure(raw,index)
    struct.to_csv(OUT/'market-structure.csv')
    liquidity(raw,index).to_csv(OUT/'liquidity.csv')
    for name, frame in [('returns',daily),('momentum5',momentum),('volatility5',vol)]:
        frame.to_csv(OUT/f'sector-{name}.csv')
    availability = pd.read_csv(V5/'global-availability.csv')
    delays = pd.to_datetime(availability.decision,utc=True) - pd.to_datetime(availability.available_assumption,utc=True)
    if (delays < pd.Timedelta(0)).any():
        raise ValueError('Inherited foreign availability exceeds decision')
    # Actual archived revisions and independent NSE underlying cross-check are distinct.
    revisions = read('actual-source-revision-audit.json',V6)
    source_files = list((V5/'sources').glob('*.json'))
    save('source-audit.json', {'raw_series':len(raw),'raw_inventory':inventory,
          'availability_rows':len(availability),'minimum_assumed_lag_minutes':float(delays.min().total_seconds()/60),
          'actual_receipts':'Old event-time receipts unavailable. All historical fits use reconstructed availability.',
          'scope': [min(f.index.min() for f in raw.values()),max(f.index.max() for f in raw.values())],
          'sources':{str(p.relative_to(ROOT)):sha(p) for p in source_files}, 'overlap_revisions':revisions})
    # Low-amplitude source rounding/revision sensitivity with common within-sector changes.
    revised = {n:f.copy() for n,f in raw.items()}
    for j,(name,frame) in enumerate(revised.items()):
        if name not in SECTORS:
            continue
        cols = ['open','high','low','close']
        multiplier = 1 + .0001*np.sin(np.arange(len(frame))/3 + j)
        frame[cols] = frame[cols].mul(multiplier,axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', pd.errors.PerformanceWarning)
        x,_,_ = build(revised,extra=False)
    revised_native = variant('I03_nosize',x,revised)
    native = matrix('native-reference.csv')
    revised_native.loc[native.index,native.columns].to_csv(OUT/'native-revision-1bp.csv')
    # Compare causal feature calculations to a recomputation with truncated raw sources.
    end = '2026-03-31'
    trunc = {name:frame.loc[:end] for name,frame in raw.items()}
    test,_,_,_ = structure(trunc,index[index<=end])
    np.testing.assert_allclose(test,struct.loc[:end],atol=1e-12,equal_nan=True)
    save('feature-checks.json',{'market_structure_truncation_invariant':True,'test_cutoff':end,
                               'columns':list(struct),'structure_rows':len(struct)})
    print('Causal structure/liquidity matrices produced', struct.shape, flush=True)


if __name__=='__main__':
    inputs()
