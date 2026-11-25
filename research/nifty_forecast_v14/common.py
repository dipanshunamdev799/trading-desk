"""Run identity, immutable source paths, and pre-score research settings."""
import json
import os
from pathlib import Path

from research.nifty_forecast_v13.common import ROOT, V5, V6, V8, V10, V11, V12, sha, now, pd, np

SRC = Path(__file__).parent
V13 = ROOT / 'artifacts/nifty_forecast_v13/2026-11-25/run-001'
BASE = ROOT / 'artifacts/nifty_forecast_v14'
OUT = Path(os.environ.get('NIFTY_V14_OUT', BASE / '2026-11-25/run-001')).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('V14 outputs belong under the V14 artifact tree')

FIRST = '2025-01-01'
FREEZE = '2026-11-17'
HORIZONS = (5, 21)
SEED = 141125
N = 2048
STEPS = 24
BARRIERS = (.005, .01, .02, .03, .05)
SCALED = (.5, 1., 1.5, 2.)
COVERAGE = (.50, .80, .90, .95)
QUANTILES = np.array([.025, .05, .10, .25, .5, .75, .90, .95, .975])
BOOT = 1600
BLOCKS = (5, 10, 21, 42)
DEMO = '2026-10-15'

RISK_MODELS = ('garch_gauss','gjr_gauss','gjr_student','gjr_skew','egarch_student','gjr_ivx','gjr_vixx',
               'gjr_t_short','gjr_t_perturbed','blend_gjr_iv','latent_kalman','latent_iv','two_state',
               'component_risk','har','har_iv','intraday_har','overnight_decomposition','offshore_gap')
PATH_MODELS = ('constant_iv','calibrated_iv','gjr_gauss','gjr_iv','gjr_student','gjr_skew','latent_sv',
               'regime_state','historical_innov','separate_gap','jump_diffusion','jump_1m','jump_shift',
               'jump_no_episode','widened_gauss','trend_persistent','trend_shrink','simple_drift',
               'iv_scaled_blocks','trend_blocks','intraday_blocks','path_mixture','joint_pit','joint_tail_width')
EVENT_MODELS = ('historical','persist','iv_raw','gjr_control','iv_scaled_hist','domestic','surface','surface_lag5',
                'surface_shift21','surface_permuted','surface_liquid','surface_truncated','intraday',
                'jump_1m','jump_shift21','offshore_opening','domestic_global_interaction','markov_state',
                'gaussian_process','student_process','empirical_joint','calibrated_joint','logistic_barrier')

def save(name, obj):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str, allow_nan=False), encoding='utf-8')

def write(name, frame, index=False):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=index)

def read(name, root=OUT):
    return json.loads((root / name).read_text(encoding='utf-8'))

def matrix(name, root=OUT):
    return pd.read_csv(root / name, index_col=0, low_memory=False)

def mature(labels, origin, limit=None):
    i = np.flatnonzero(labels.endpoint.lt(origin).to_numpy())
    return i if limit is None else i[-limit:]

def register():
    if (OUT / 'registration.json').exists():
        return
    save('registration.json',dict(timestamp=now(), vintage=FREEZE, first_observation=FIRST,
        frequency='observed NSE cash sessions', reference='official origin close; next session 09:10 IST cutoff',
        horizons=HORIZONS, original_n={5:265,21:217}, earliest_only_mature='target endpoint strictly before origin',
        fixed_barriers=BARRIERS, iv_relative_barriers=SCALED, coverage=COVERAGE, quantiles=QUANTILES.tolist(),
        main_paths=N, random_seed=SEED, session_steps=STEPS, convergence_paths=[512,2048,8192],
        convergence_steps=[12,24,48,96], block_resamples=BOOT, block_lengths=BLOCKS,
        risks=RISK_MODELS, paths=PATH_MODELS, events=EVENT_MODELS,
        calibration=['asymmetric normalized residual','rolling conformal-style','risk-conditioned intervals',
                     'reweight complete paths by rolling PIT ranks','learn modest width from matured outcomes'],
        search='Run both horizons on pre-existing origins. Keep exact denominators. Re-evaluate against the strongest relevant V13 baselines. '
               'Use separate direction, endpoint, variance, path, passage, calibration and joint-quality losses. '
               'Representative fixed-budget null selects within family; extend only to audit an identified mechanism.'))
