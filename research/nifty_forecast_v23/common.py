"""V23 frozen scope and shared archive utilities."""
from dataclasses import dataclass
from pathlib import Path
import datetime as dt
import gzip
import hashlib
import json
import os

import numpy as np
import pandas as pd

from research.nifty_forecast_v22 import common as v22

ROOT, FIRST, FREEZE, LAST, IST = v22.ROOT, v22.FIRST, v22.FREEZE, v22.LAST, v22.IST
V22 = v22.OUT
AREA = ROOT / 'artifacts/nifty_forecast_v23'
OUT = Path(os.environ.get('NIFTY_V23_OUT', AREA / '2026-11-26/run-001')).resolve()
assert OUT.is_relative_to(AREA)
SRC = Path(__file__).parent
BRIEF = Path('C:/Users/ME/.codex/attachments/8100746a-afc8-4d66-ba38-3dfde6b53149/Pasted text.txt')
HORIZONS = (5, 21)
CLOCKS = ('previous_1700', 'preauction_0855', 'native_0910')
COHORTS = {5: (173, 92, 53), 21: (141, 76, 11)}
SEED = 231126
DAY = 86_400_000_000_000
REPORTS = (
    'REPRODUCTION_AND_BENCHMARKS', 'MASTER_FORECAST_ARCHIVE', 'FORECAST_INFORMATION_GEOMETRY',
    'DISTRIBUTION_COMPONENT_INTELLIGENCE', 'ROBUST_FORECAST_AGGREGATION', 'MODEL_UNCERTAINTY_AND_DISAGREEMENT',
    'STABLE_PREDICTIVE_RELATIONSHIPS', 'HISTORICAL_PATH_SHAPE_RESEARCH', 'INTERNATIONAL_PATH_COMPLEMENTARITY',
    'ORIGINAL_HORIZON_FORECASTING', 'FORECAST_CALIBRATION_RESEARCH', 'SIMULATION_PRECISION_AND_NUMERICAL_AUDIT',
    'CUMULATIVE_SEARCH_RISK', 'VALIDATION_AND_FALSIFICATION', 'COMPLETE_MODEL_COMPARISON', 'FORWARD_RESEARCH_LEDGER',
    'FINAL_RESEARCH_CONCLUSIONS', 'NEXT_EXPERIMENTS',
)

now, sha, stamp, cash, utc_int = v22.now, v22.sha, v22.stamp, v22.cash, v22.utc_int


def root_for(version):
    base = ROOT / f'artifacts/nifty_forecast_v{version}'
    candidates = sorted(base.glob('*/run-*'))
    return candidates[-1] if candidates else base


def csv(name, root=OUT, **kw):
    return pd.read_csv(root / name, low_memory=False, **kw)


def read(name, root=OUT):
    p = root / name
    opener = gzip.open if p.suffix == '.gz' else open
    with opener(p, 'rt', encoding='utf-8-sig') as file:
        return json.load(file)


def save(name, obj):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, allow_nan=False, default=str), encoding='utf-8')


def write(name, frame):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(p, index=False)


def register():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'registration.json').exists():
        return
    (OUT / 'MISSION.md').write_bytes(BRIEF.read_bytes())
    designs = [
        ('Forecast-family redundancy', 'Shared inputs and parents yield correlated losses and nearly equal laws',
         'Original returns', 'Best archived model at each clock', 'Loss effective rank and quantile distance',
         'Exact copies, affine signatures and independent simulation draws', 'One full-sample diagnostic and one mature-distance training family'),
        ('Component-level distributions', 'Location, scale, sign, skew and tails may come from distinct models',
         'Original returns and terminal tails', 'V22 Brier and CRPS leaders separately', 'CRPS, Brier and quantile scores',
         'Individually isolated transforms, fixed historical mixtures', 'One staged transform per component and one complete transformed law per clock'),
        ('Robust aggregation', 'Family balancing and bounded weights reduce concentrated model risk',
         'Original returns', 'Best archive, equal family and equal model', 'CRPS and worst cohort',
         'Zero weight, exact duplicate, near copy, randomized fixed weights', 'One robust scheme per mechanism, fixed 120-row memory, 36 minimum'),
        ('Uncertainty and disagreement', 'Between-family variance may forecast loss beyond IV and historical risk',
         'Errors, expansion, range and tails', 'ATM IV, rolling volatility, ordinary dispersion', 'MAE and calibrated Brier',
         'Delayed disagreement and centered null features', 'Four response heads, past-only base and augmented fits with equal penalties'),
        ('Stable coefficients', 'Small robust adaptations may survive changes in market state and training mix',
         'Original returns', 'Ordinary ridge on identical origins', 'Paired loss, worst cohort and coefficient spread',
         'Delayed features, blocked residual permutation, earlier/later contrast', 'One Huber, environment, hierarchical and conservative-group variant'),
        ('Historical path shape', 'At the same risk anchor, continuous episodes may better represent ranges and drawdowns',
         'Original risk, range and path', '08:55 protected IV and GJR paths', 'Range CRPS and drawdown CRPS',
         'Diffusion, Student GJR, shuffled chronology, IID days, constant scenario risk, widened scale', 'One fixed structural ablation per mechanism at two horizons'),
        ('International paths beyond India', 'A modest foreign contribution improves shape beyond a domestic library',
         'Mainly monthly range and tails', 'Equal India episodes and same GJR scale', 'Range CRPS, upper tail, drawdown and expansion',
         'Equal counts, random foreign, broad versus strict source, region and episode exclusions', '24 episodes and 25% target foreign replacement, no tuning to outcomes'),
        ('Forecast calibration', 'Conservative calibration can improve reliability without sacrificing resolution',
         'Original sign, PIT and tail events', 'Same-clock unmodified parent and fixed shrinkage', 'Log loss, Brier and interval score',
         'Training-only maps, fixed shrinkage, block permutation', 'One probability map and one monotone empirical PIT law per source'),
        ('Simulation precision', 'Sampling uncertainty can dominate small historical score gains',
         'Sign, expected return, interval, range, barriers', 'Exact finite weighted law', 'Absolute draw error and seed RMSE',
         'Common random prefixes and independent seeds', '256, 1024, 4096 and 16384 draws, eight seeds on stratified cases'),
        ('Cumulative search exposure', 'Repeated selection can produce a favorable retrospective winner under null information',
         'Original return and scale loss', 'Strongest archived model at its clock', 'Best refitted and reselected paired gain',
         'Null features, blocked residuals and randomized weights', '39 representative replicates per horizon with a bounded mechanism family'),
        ('Archive validity and chronology', 'Provenance and explicit time matching preserve exact admissibility',
         'All archived original targets', 'V22 verified law archive', 'Exact score differences and coverage',
         'Future timestamp poison and invalid date/window sentinels', 'Audit all recoverable source table schemas and case links plus dated archive replay'),
        ('Authentic prospective research', 'A small frozen panel can be staged with verifiable calendar and published inputs',
         'The original return and risk targets', 'Prior immutable issues and frozen native models', 'Valid issue, sources, complete law and settlement',
         'No backdating, incomplete-source gate and unchanged hashes', 'One due morning census, a bounded retry and separate settlement checks'),
    ]
    keys = ('mechanism', 'proposal', 'target', 'strong_parent', 'primary_metric', 'negative_control', 'computational_budget')
    save('registration.json', dict(registered_at=now(), seed=SEED, historical_bounds=[FIRST, FREEZE], final_forward_year=2026,
          original_cohorts=COHORTS, historical_exposure='Forecast model selection remains research-exposed',
          hypotheses=[dict(zip(keys, x), cutoff='Original archived cutoff. New paths use 08:55 IST with strictly earlier outcomes.') for x in designs]))


if __name__ == '__main__':
    register()
