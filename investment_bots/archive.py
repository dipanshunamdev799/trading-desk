"""Import supplied research provenance into PostgreSQL without executing its pipeline."""
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from .data import Inputs, canonical

FROZEN = {
    'phase5/sim5.py': 'ea13b4b83932de7c',
    'phase6/p6common.py': 'de078880d7513c11',
    'phase6/paper6.py': 'fe388b065c52952f',
    'phase7/p7common.py': '02cc5c95261e8fbd',
    'phase7/integrity.py': '0641588d14be8224',
    'phase7/paper7.py': '2881b43b130dace5',
}


def import_archive(path, inputs=None):
    inputs = inputs or Inputs()
    path = Path(path)
    archive_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    with ZipFile(path) as z:
        members = {n.removeprefix('swing_2025_2026/'): n for n in z.namelist()
                   if n.startswith('swing_2025_2026/') and not n.endswith('/')}
        if len(members) > 10000 or sum(i.file_size for i in z.infolist()) > 1_000_000_000:
            raise ValueError('Unexpected research archive size')
        if any('..' in PurePosixPath(n).parts for n in members):
            raise ValueError('Invalid archive member path')
        checks = {}
        for n, expected in FROZEN.items():
            checks[n] = hashlib.sha256(z.read(members[n])).hexdigest()[:16] == expected
        if not all(checks.values()):
            raise ValueError('Archive frozen-source hashes do not match the supplied strategy specifications')
        # Intraday and pickled search caches are irrelevant to daily portfolio
        # processing and are never deserialized or treated as daily inputs.
        selected = [n for n in members if n.endswith(('.py', '.md')) or
                    n.startswith('results/phase8/paper/') and n.endswith('.json') or
                    n in ('cache/panel25_meta.json', 'results/phase7/integrity.json')]
        inventory = dict(filename=path.name, sha256=archive_hash, frozen_hash_checks=checks,
                         files_imported=len(selected), daily_panel_present=False,
                         missing=['research/swing_mtf/phase2/dpanel.py and its frozen daily cache/metadata',
                                  'research/market_data.duckdb corporate_actions export'],
                         note='panel25.npz is an intraday cache for 643 instruments, not the 2,284-column daily panel')
        with inputs.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420191)')
            for n in selected:
                content = z.read(members[n])
                sha = hashlib.sha256(content).hexdigest()
                name = 'swing_2025_2026/' + n
                old = c.execute('SELECT sha256 FROM source_files WHERE name=%s', (name,)).fetchone()
                if old and old[0] != sha:
                    raise ValueError('Research provenance conflict: ' + name)
                c.execute('INSERT INTO source_files(name,sha256,content) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING',
                          (name, sha, content))
            c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload',
                      ('research_archive', canonical(inventory)))
    return inventory


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import supplied investment research archive provenance into PostgreSQL')
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    print(json.dumps(import_archive(args.archive), indent=2))
