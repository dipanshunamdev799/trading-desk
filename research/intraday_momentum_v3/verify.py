"""Reconcile existing artifacts and frozen provenance without broker/DB writes."""
from collections import Counter
import json,unittest,io
import pandas as pd
from .common import ROOT,OUT,SOURCE,dump,sha,now
from .readiness import freeze


def main():
    protocol=freeze();inventory=json.loads((OUT/'archive-inventory.json').read_text());matrix=pd.read_csv(OUT/'archive-coverage.csv');depth=pd.read_csv(OUT/'archive-depth-type-sample.csv')
    meta=json.loads((OUT/'metadata-reconciliation.json').read_text());audit=json.loads((OUT/'metadata-audit.json').read_text())
    assert inventory['complete'] and inventory['successful_chunks']==inventory['chunks']==4
    assert int(matrix.rows.sum())==inventory['summary']['archive_rows']==32_370_042
    assert int(matrix[matrix.segment.eq('NSE_EQ')].rows.sum())==5_506_783
    assert matrix[matrix.segment.eq('NSE_EQ')].instrument_key.nunique()==50
    assert int(depth.sampled_rows.sum())==inventory['summary']['depth_sample_rows']
    assert dict(Counter(r['execution_state'] for r in meta))==audit['states']
    assert not any(r['execution_state']=='CONFLICT_QUARANTINE' for r in meta)
    preserved={}
    delivery=ROOT/'artifacts/intraday_momentum_v2/delivery-manifest.json'
    for name,entry in json.loads(delivery.read_text())['files'].items():
        file=delivery.parent/name;preserved[name]=file.exists() and sha(file)==entry['sha256']
    assert all(preserved.values()),'Existing V2 delivery changed'
    documents=json.loads((delivery.parent/'document-provenance.json').read_text());source_docs={}
    for name,entry in documents.items():
        source=__import__('pathlib').Path(entry['source']);source_docs[name]=source.exists() and sha(source)==entry['sha256']
    assert all(source_docs.values()),'Existing V2 source document changed'
    frozen_code=json.loads((delivery.parent/'research-manifest.json').read_text())['code']
    source_code={name:(ROOT/name).exists() and sha(ROOT/name)==value for name,value in frozen_code.items()}
    assert all(source_code.values()),'Existing V1/V2 frozen source changed'
    stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_intraday*.py');result=unittest.TextTestRunner(stream=stream).run(suite)
    verification=dict(checked_at=now().isoformat(),protocol_sha256=sha(OUT/'protocol-frozen.json'),
        tests_run=result.testsRun,tests_passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),
        archive_totals_reconciled=True,metadata_states_reconciled=True,v2_delivery_preserved=preserved,v2_source_documents_preserved=source_docs,v1_v2_frozen_source_preserved=source_code,
        no_orders=True,scheduler_enabled=False,test_source_sha256=sha(ROOT/'tests/test_intraday_v3.py'))
    dump(OUT/'test-output.json',dict(output=stream.getvalue()));dump(OUT/'verification.json',verification)
    sources=[dict(title='Analytics Token',url='https://upstox.com/developer/api-documentation/analytics-token/'),
        dict(title='V3 feed modes and limits',url='https://upstox.com/developer/api-documentation/v3/get-market-data-feed/'),
        dict(title='Inactive segment error',url='https://upstox.com/developer/api-documentation/get-profile/'),
        dict(title='Authorized feed URL',url='https://upstox.com/developer/api-documentation/get-market-data-feed-authorize-v3/'),
        dict(title='Current charge schedule',url='https://upstox.com/brokerage-charges/'),
        dict(title='V2 discontinuation',url='https://upstox.com/developer/api-documentation/announcements/v2-websocket-discontinued/')]
    dump(OUT/'source-provenance.json',dict(checked_at=now().isoformat(),primary_sources=sources,metadata_sources=audit['sources'],
        interpretation='Broker response evidence is distinct from documentation. Raw metadata and per-run source/receipt/commit records retain their own retrieval times.'))
    files={}
    for root in (OUT,SOURCE):
        for file in root.rglob('*'):
            if file.is_file() and file.suffix in ('.py','.md','.json','.csv','.png') and '__pycache__' not in str(file) and file.name!='delivery-manifest.json':
                files[str(file.relative_to(ROOT))]=dict(sha256=sha(file),bytes=file.stat().st_size)
    dump(OUT/'delivery-manifest.json',dict(checked_at=now().isoformat(),files=files,protocol_frozen_at=protocol['frozen_at'],no_real_orders=True))
    print(json.dumps({k:v for k,v in verification.items() if k not in ('v2_delivery_preserved','v2_source_documents_preserved')},indent=2))
    if not result.wasSuccessful():raise SystemExit(1)


if __name__=='__main__':main()
