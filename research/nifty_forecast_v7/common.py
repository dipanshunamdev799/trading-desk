"""Versioned paths and read-only access to earlier research."""
from pathlib import Path
import hashlib
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).parent
BASE = ROOT / 'artifacts/nifty_forecast_v7'
OUT = Path(os.environ.get('NIFTY_V7_OUT', BASE / '2026-11-24/run-001')).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('V7 outputs must be inside the V7 artifact directory')
V6 = ROOT / 'artifacts/nifty_forecast_v6/2026-11-19/run-001'
V5 = ROOT / 'artifacts/nifty_forecast_v5/2026-11-18/run-001'
SEED = 20261124


def now():
    return datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, data):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str, allow_nan=False), encoding='utf-8')


def read(name, directory=OUT):
    return json.loads((directory / name).read_text(encoding='utf-8'))


def matrix(name, directory=V6):
    return pd.read_csv(directory / name, index_col=0)


def preserve():
    if (OUT / 'preservation.json').exists():
        raise FileExistsError('This run already has a preservation manifest')
    old = read('prior-preservation.json', V6)['files']
    paths = sorted(p for folder in [ROOT / 'research/nifty_forecast_v6', V6.parent, ROOT / 'artifacts/nifty_forecast_v6']
                   for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths = list(dict.fromkeys(paths + [ROOT / 'NIFTY_V6_RESEARCH.md']))
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    save('preservation.json', {'started': now(), 'files': old | hashes})
    reviewed = []
    for p in [ROOT / 'NIFTY_V6_RESEARCH.md', *sorted(V6.glob('V6_*.md')), *sorted((ROOT/'research/nifty_forecast_v6').glob('*.py'))]:
        content = p.read_text(encoding='utf-8')
        reviewed.append({'path': str(p.relative_to(ROOT)), 'bytes': len(content.encode()), 'sha256': sha(p)})
    save('reviewed-material.json', reviewed)
    print('Preservation manifest', len(old | hashes), 'files', flush=True)


if __name__ == '__main__':
    preserve()
