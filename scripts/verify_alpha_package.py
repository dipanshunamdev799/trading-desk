"""Final artifact, source-version and persisted-result checks for Project Alpha."""
import hashlib,json,re
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'/'project_alpha'


def read(name):return json.loads((OUT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks=[];hashes=0;versions=[]
    for path in sorted(OUT.glob('*preregister.json')):
        obj=json.loads(path.read_text())
        mapping=obj.get('input_sha256',{})
        for name,digest in mapping.items():
            source=ROOT/name
            if sha(source)!=digest:
                archived=OUT/'exit-stream-original-script.py'
                assert Path(name).name=='research_alpha_streams.py' and sha(archived)==digest,(path.name,name)
                versions.append({'protocol':path.name,'original_source':name,'archived_source':str(archived.relative_to(ROOT)),'sha256':digest})
            hashes+=1
    checks.append('Preregistered inputs and original/extended stream code versions match retained bytes')
    phases=read('phase-audit.json');assert [r['phase'] for r in phases]==list(range(13))
    for r in phases:assert (ROOT/r['artifact']).exists()
    hypotheses=read('hypotheses.json')
    assert len(hypotheses)==10
    for r in hypotheses:assert all(r[k] for k in ['mechanism','test_specification','baseline','falsifier']) and (ROOT/r['evidence']).exists()
    checks.append('All thirteen phases and ten falsifiable hypotheses have resolving evidence artifacts')
    for r in read('experiment-registry.json')['experiments']:
        assert sha(ROOT/r['code_path'])==r['code_sha256']
        assert sha(ROOT/r['dataset_or_result_path'])==r['dataset_or_result_sha256']
        assert (ROOT/r['results']).exists()
    checks.append('Experiment code/data hashes and results reconcile')
    config=read('alpha-config.json');assert not config['production_enabled'] and not config['broker_orders_enabled'] and config['primary_validated_strategy'] is None
    live=read('signal-engine-live-check-v2.json');assert live['action']=='NO TRADE' and live['lots']==0 and not live['broker_order_sent']
    assert live['code_sha256']==sha(ROOT/'scripts'/'alpha_signal_engine.py')
    inputs=read('signal-engine-live-check-v2.inputs.json');assert live['input_sha256']==hashlib.sha256(json.dumps(inputs['candles'],sort_keys=True).encode()).hexdigest()
    checks.append('Current live check is reproducible, has current code hash and remains gated')
    review=read('review-metrics-signal-timeframe.json')
    for name,digest in review['reviewed_source_sha256'].items():assert sha(ROOT/name)==digest
    assert review['independent_metric_assertions']==546 and review['independent_timeframe_assertions']==6684
    checks.append('Independent metrics/timeframe/safety review matches current source versions')
    risks=pd.read_csv(OUT/'risk-feasibility.csv');assert len(risks)==384
    assert (risks[risks.capital.isin([100000,250000])].taken==0).all()
    checks.append('Reported whole-lot risk feasibility agrees with all384persisted scenarios')
    snapshot=pd.read_csv(OUT/'exit-stream-trades.csv');good=snapshot[(snapshot.execution_mode=='frame_snapshot')&(snapshot.status=='observed_bid_ask_snapshot_proxy')]
    baseline=good[good.configuration=='ATM|time60|lat250|wait2000'];assert len(baseline)==3 and np.isclose(baseline.illustrative_net_rupees_per_lot.mean(),466.264833333334)
    assert (snapshot[snapshot.execution_mode=='verified_exchange_book'].status!='observed_bid_ask_snapshot_proxy').all()
    checks.append('Recorded-spread reference result has3outcomes; strict-book mode never claims fills')
    delta=read('exit-stream-delta-v2-verification.json');assert delta['ATM_control_matches_original'] and delta['all_new_input_hashes_match'] and delta['independent_checks_passed']==713
    checks.append('Received-Greeks extension preserves ATM control and has independent source-quote checks')
    for path in [ROOT/'PROJECT_ALPHA_RESULTS.md',OUT/'rulebook.md',OUT/'forward-protocol.md']:
        content=path.read_text(encoding='utf-8')
        for target in re.findall(r'\]\((C:/[^)]+)\)',content):assert Path(target).exists(),target
        # Table rendering: all rows in a contiguous table must have equal column counts.
        width=None
        for line in content.splitlines():
            if line.startswith('|'):
                count=len(re.split(r'(?<!\\)\|',line))
                if width is None:width=count
                assert count==width,(path.name,line)
            else:width=None
    checks.append('User-facing local links resolve and Markdown tables have consistent columns')
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name not in ['verification.json','manifest.json'] and '__pycache__' not in p.parts]
    files += [ROOT/'PROJECT_ALPHA_RESULTS.md'] + list((ROOT/'scripts').glob('*alpha*.py'))
    files=sorted(set(files))
    manifest={'report_date':'2026-11-10','historical_cutoff':'2026-11-08','files':{str(p.relative_to(ROOT)):sha(p) for p in files},'registered_original_code_versions':versions}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    result={'passed_groups':len(checks),'registered_input_hashes_verified':hashes,'manifest_files':len(files),'checks':checks,'original_code_versions':versions}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
