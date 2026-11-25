"""Independent V6 winner refits and matched per-origin diagnosis."""
from .common import *
from research.nifty_forecast_v6.engine import fit, means, predict
from research.nifty_forecast_v6.forensics import GROUPS
from research.nifty_forecast_v6.analyze import benchmark_frames
from research.nifty_forecast_v3.experiment import available, inner_split, nonoverlap


def references():
    native = matrix('native-reference.csv')
    volume = matrix('liquidity-reference.csv').filter(regex='_volume$')
    defensive = [c for c in native if GROUPS['DEFENSIVE'](c)]
    return native, volume, defensive


def run():
    if not (OUT / 'preservation.json').exists():
        preserve()
    from research.nifty_forecast_v6 import reproduce as legacy
    legacy.save = lambda name, value: save('legacy-' + name, value)
    legacy.run()
    native, volume, defensive = references()
    frames = {'F_NO_DEFENSIVE': native.drop(columns=defensive), 'W2_DEF_NORM': native,
              'W2_DEF_PC': native, 'W2_NOAUTO_VOLUME': pd.concat([native.drop(columns='i_nifty_auto_rel21'), volume], axis=1)}
    prior = pd.read_csv(V6 / 'all-predictions.csv')
    base = benchmark_frames()
    rows, ledger = [], []
    for name, x in frames.items():
        for h in ([5, 21] if name == 'F_NO_DEFENSIVE' else [5]):
            labels = matrix(f'labels-{h}.csv')
            g = prior[(prior.horizon == h) & (prior.model == name)]
            for fold, test in g.groupby('fold'):
                cutoff = test.origin.min()
                dates = available(labels, cutoff)
                inner, validation = inner_split(labels, dates)
                spec = {'kind': 'ridge', 'alpha': 100, 'defensive_norm': name == 'W2_DEF_NORM', 'defensive_pc': name == 'W2_DEF_PC'}
                context = fit(spec, x.loc[inner], labels, validation[0])
                residual = labels.loc[validation, 'return'].to_numpy() - means(context, x.loc[validation])
                model = fit(spec, x.loc[dates], labels, cutoff)
                laws = predict(model, x.loc[test.origin], residual)
                error = 0.
                for r, law in zip(test.itertuples(), laws):
                    scores = law.score(r.realized_return)
                    err = max(abs(scores[k] - getattr(r, k)) for k in ['p', 'predicted_mean', 'predicted_median', 'crps', 'brier'])
                    assert err < 1e-12
                    error = max(error, err)
                    a = base[h, 'I03_nosize'].loc[r.origin]
                    b = base[h, 'L01'].loc[r.origin]
                    rows.append({'horizon': h, 'model': name, 'fold': fold, 'origin': r.origin, 'endpoint': r.endpoint,
                                 'regime': r.regime, 'trend': r.trend, 'realized_return': r.realized_return, 'p': r.p,
                                 'I03_p': a.p, 'L01_p': b.p, 'delta_p_vs_I03': r.p-a.p,
                                 'Brier_gain_vs_I03': a.brier-r.brier, 'CRPS_gain_vs_L01': b.crps-r.crps})
                ledger.append({'horizon': h, 'model': name, 'fold': fold, 'cutoff': cutoff, 'n': len(test), 'spec': spec,
                               'columns': list(x), 'max_abs_difference': error})
    diff = pd.DataFrame(rows)
    diff.to_csv(OUT / 'v6-paired-diagnosis.csv', index=False)
    save('v6-reproduction.json', {'passed': True, 'folds': ledger, 'defensive_columns': defensive,
                                 'volume_columns': list(volume), 'auto_removed': 'i_nifty_auto_rel21', 'rows': len(diff)})
    print('Exactly reconstructed', len(diff), 'V6 winner/mechanism predictions', flush=True)


if __name__ == '__main__':
    run()
