"""Isolated V13 run paths and immutable research settings."""
import json
import os
from pathlib import Path

from research.nifty_forecast_v12.common import ROOT, V5, V6, V7, V8, V10, V11, pd, np, sha, now, matrix

SRC = Path(__file__).parent
V12 = ROOT / 'artifacts/nifty_forecast_v12/2026-11-24/run-001'
BASE = ROOT / 'artifacts/nifty_forecast_v13'
OUT = Path(os.environ.get('NIFTY_V13_OUT', BASE / '2026-11-25/run-001')).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('V13 output must remain in its own artifact tree')
FREEZE = '2026-11-17'
SEED = 131125
HORIZONS = (5, 21)
THRESHOLDS = (.005, .01, .02, .03, .05)
N_PATHS = 512
N_BOOT = 1500
REFERENCE = ['V12_STAT', 'V12_NATIVE_RV', 'J12_Q_GROUP', 'O_NATIVE_PHASE0', 'J11_EXCLUDE_B_ROT',
             'PH_NATIVE_PHASE_MIXTURE', 'PH_NATIVE_POOLED', 'B_CHANGE', 'J11_BREADTH_ALL',
             'J10_STRUCTURAL_BLEND', 'J12_GROUP_BALANCED', 'NEUTRAL', 'V8_R_RESIDUAL',
             'V8_W_STRUCT_EMBARGO_EQ', 'Q12_RAW', 'P12_Q_PHYSICAL_MIX']

def save(path, obj):
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(obj, indent=2, default=str, allow_nan=False), encoding='utf-8')

def write(path, data, **kwargs):
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(dest, **kwargs)

def loads(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def register():
    file = OUT / 'initial-registry.json'
    if not file.exists():
        save(file.name, dict(registered=now(), through=FREEZE, horizons=HORIZONS, barriers=THRESHOLDS,
            paths=N_PATHS, seed=SEED, block_draws=N_BOOT, block_lengths=[5, 10, 21, 42],
            evaluation='Frozen shared V12 origins, fully matured labels strictly before each origin, matched eligibility, no tuning on evaluation.',
            hypotheses=['range-based EWMA HAR ARCH/GARCH EGARCH GJR versus raw ATM IV',
                        'calendar-to-session IV and simple fixed variance blends',
                        'constant maturity shape, PCA, risk pricing gaps, unsigned OI, offshore volatility',
                        'empirical OHLC, risk-scaled OHLC, state nearest-neighbor OHLC, diffusion',
                        'separate direction location, confidence scaling and asymmetry'],
            decision='MAE/QLIKE, range/pinball, barrier Brier and endpoint Brier/CRPS are distinct. Report gains versus strong matched baselines and both cohorts. Expand only to diagnose timing, missingness, benchmark performance or a competing mechanism. Label follow-ups.'))
