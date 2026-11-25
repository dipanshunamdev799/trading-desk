"""Archive the completed v1 download plan and add the audited share-unit delta.

This is a pre-P&L data correction, not a new strategy search. Existing authentic
source jobs are reused only after exact request identities and hashes match.
"""
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.intraday_momentum.data import OUT,prepare,sha,dump


def main(out=OUT):
    out=Path(out)
    if (out/'research-manifest.json').exists():
        raise RuntimeError('Cannot amend a data plan after strategy research was frozen')
    old_plan=json.loads((out/'jobs-plan.json').read_text())
    old_manifest=json.loads((out/'acquisition-manifest.json').read_text())
    if old_plan['version']!='intraday-stock-data-v1':
        raise RuntimeError('This one-time amendment requires the original v1 plan')
    old_plan_sha=sha(out/'jobs-plan.json');old_manifest_sha=sha(out/'acquisition-manifest.json')
    if old_manifest['plan_sha256']!=old_plan_sha:
        raise RuntimeError('Source manifest is not bound to the original plan')
    original_jobs={j['id']:j for j in old_plan['jobs']}
    completed={j['id']:j for j in old_manifest['jobs']}
    if set(completed)!=set(original_jobs) or any(j['status']!='ok' for j in completed.values()):
        raise RuntimeError('Complete/retry the original acquisition before this amendment')
    for j in completed.values():
        if sha(j['path'])!=j['sha256']:raise RuntimeError('Original source hash mismatch')
    archive=out/'plan-versions/v1-before-unit-correction';archive.mkdir(parents=True,exist_ok=True)
    for name in ('jobs-plan.json','acquisition-manifest.json','daily-context.json'):
        dest=archive/name
        if dest.exists() and sha(dest)!=sha(out/name):
            raise RuntimeError('Refusing to overwrite different archived provenance')
        if not dest.exists():shutil.copy2(out/name,dest)
    new_plan=prepare(out)
    new_jobs={j['id']:j for j in new_plan['jobs']}
    if not set(original_jobs)<=set(new_jobs):raise RuntimeError('Amendment removed source requests')
    for ident,j in original_jobs.items():
        if new_jobs[ident]!=j:raise RuntimeError('Amendment changed an existing request identity')
    old_candidates={(r['key'],r['day']) for r in old_plan['candidates']}
    new_candidates={(r['key'],r['day']) for r in new_plan['candidates']}
    delta=json.loads((out/'unit-audit/plan-amendment-delta.json').read_text())
    expected_candidates={(r['key'],r['day']) for r in delta['added_candidates']}
    expected_jobs={r['key']+'|'+r['month'] for r in delta['added_jobs']}
    if new_candidates-old_candidates!=expected_candidates or old_candidates-new_candidates:
        raise RuntimeError('Unexpected change to audited candidate set')
    if set(new_jobs)-set(original_jobs)!=expected_jobs:
        raise RuntimeError('Unexpected change to audited acquisition jobs')
    lineage=dict(amended_at=datetime.now().astimezone().isoformat(),
        reason='Verified provider back-adjustment requires contemporaneous units for the lagged rupee price floor. Before all strategy P&L.',
        previous_plan_sha256=old_plan_sha,previous_manifest_sha256=old_manifest_sha,
        new_plan_sha256=sha(out/'jobs-plan.json'),archived_at=str(archive),
        added_jobs=sorted(expected_jobs),added_candidates=sorted(expected_candidates),
        reused_source_jobs=len(completed),old_requests_unchanged=True)
    dump(out/'plan-amendment.json',lineage)
    rebased={**old_manifest,'version':new_plan['version'],'plan_sha256':lineage['new_plan_sha256'],
             'lineage':old_manifest.get('lineage',[])+[lineage]}
    dump(out/'acquisition-manifest.json',rebased)
    print(f"Amended plan: {len(new_candidates)} candidates; reused {len(completed)} source jobs; {len(expected_jobs)} new jobs.",flush=True)


if __name__=='__main__':main()
