"""Validate the complete delivery and record checksums without touching predecessors."""
import re
from urllib.parse import unquote

from .common import *

REQUIRED=('NIFTY_V15_RESEARCH.md','README.md','registration.json','benchmark-replay.json','validation-receipt.json',
  'forward-ledger.json','joint-update-archive.json','joint-update-receipts.json','historical-fixed-endpoint-updates.png',
  'sequential-scores.csv.gz','sequential-passage.csv.gz','sequential-order.csv.gz','fitted-update-models.ndjson.gz',
  'matched-window-evidence.csv','session-evidence.csv','volatility-transition-evidence.csv','scenario-envelope.csv',
  'causal-error-evidence.csv','mechanical-same-law-evidence.csv')


def run():
    mission=(OUT/'MISSION.md').read_text(encoding='utf-8-sig')
    needed=set(re.findall(r'`(V15_[A-Z_]+\.md)`',mission))
    rendered={p.name for p in OUT.glob('V15_*.md')}
    assert len(needed)==20 and needed==rendered
    assert all((OUT/name).stat().st_size>0 for name in REQUIRED)
    # Index links to the manifest, created below.
    checked_links=0
    for file in [*OUT.glob('V15_*.md'),OUT/'README.md',OUT/'NIFTY_V15_RESEARCH.md']:
        source=file.read_text(encoding='utf-8')
        assert '�' not in source and source.startswith('# ')
        for target in re.findall(r'\[[^\[\]\n]+\]\(([^\s)]+)\)',source):
            if '://' in target or target=='manifest.json':
                continue
            assert (file.parent/unquote(target)).exists(), (file.name,target)
            checked_links+=1
    assert read('validation-receipt.json')['passed']
    assert read('benchmark-replay.json')['passed']
    assert read('protected-receipt.json')['valid']
    n=read('sequential-score-counts.json')
    assert n['scores']==sum(h*EXPECTED[h] for h in HORIZONS)*len(MODELS)
    bins=list((OUT/'updated-paths').glob('*.npz'))
    assert len(bins)==sum(EXPECTED.values())
    info=dict(verified_at=now(),frozen_vintage=FREEZE,report_count=len(rendered),verified_relative_links=checked_links,
              archived_joint_window_files=len(bins),score_counts=n,passed=True)
    save('delivery-receipt.json',info)
    manifest={}
    for path in sorted(OUT.rglob('*')):
        if path.is_file() and path.name!='manifest.json':
            assert path.stat().st_size>0
            manifest[path.relative_to(OUT).as_posix()]=dict(sha256=sha(path),bytes=path.stat().st_size)
    saved={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(SRC.glob('*.py'))}
    source={q.relative_to(ROOT).as_posix():sha(q) for q in (V13/'manifest.json',V14/'manifest.json',
             V13/'frozen-source-receipt.json',V14/'registration.json',V12/'manifest.json') if q.exists()}
    save('manifest.json',dict(**info,artifacts=manifest,source_code=saved,predecessor_manifests=source))
    saved_manifest=read('manifest.json')
    assert saved_manifest['artifacts']['NIFTY_V15_RESEARCH.md']['sha256']==sha(OUT/'NIFTY_V15_RESEARCH.md')
    print('Verified',len(rendered),'reports,',checked_links,'links and',len(manifest),'artifact hashes',flush=True)


if __name__=='__main__':
    run()
