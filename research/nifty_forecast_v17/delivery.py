"""Check the delivered report indexes, source receipts and research archive hashes."""
import re
from .common import *


def verify_receipt(rows):
    count=0
    for r in rows:
        if r.get('file') and r.get('sha256'):
            name=OUT/r['file']
            assert name.is_file() and sha(name)==r['sha256'],name
            count+=1
    return count


def run():
    reports=[OUT/f'V17_{k}.md' for k in REPORTS]
    assert len(reports)==19 and all(x.is_file() for x in reports)
    main=[OUT/'NIFTY_V17_RESEARCH.md',OUT/'README.md',*reports]
    links=0
    for p in main:
        for ref in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf8')):
            if not ref.startswith(('https://','http://')) and ref!='manifest.json':
                assert (p.parent/ref).exists(),(p.name,ref)
                links+=1
    rosters={'official_equity':('official-equity-receipt.json','records'),'eligibility_seeds':('stock-eligibility-receipt.json','seeds'),
             'stock_candles':('stock-candle-receipt.json','records'),
             'extensions':('intraday-extensions-receipt.json','records'),'recovery':('stock-recovery-receipt.json','records'),
             'new_source_probes':('new-source-availability.json','probes'),'same_clock_paths':('retimed-path-archive.json','files'),
             'path_convergence':('path-convergence-archive.json','files'),'postopen_paths':('postopen-path-archive.json','rows')}
    count={k:verify_receipt(read(file)[key]) for k,(file,key) in rosters.items()}
    fwd=read('forward-ledger.json')
    count['forward_sessions']=verify_receipt(fwd['sessions'])
    prior=read('predecessor-protection.json')
    assert prior['passed'] and sha(V16/'manifest.json')==prior['v16_manifest']
    audit=read('validation-receipt.json')
    assert audit['sentinel_cases']>=10 and int(audit['original_cohorts']['5'])==265 and int(audit['original_cohorts']['21'])==217
    source=[]
    for p in sorted(SRC.glob('*.py')):
        source.append(dict(file=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    save('delivery-receipt.json',dict(verified_at=now(),requested_reports=len(reports),internal_links=links,verified_hashes_by_source=count,
         verified_predecessor_manifest=prior['v16_manifest'],frozen_scope=[FIRST,FREEZE],forward_check=fwd['checked_at'],
         prospective_issues=fwd['new_v17_issues']))
    files=[]
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name!='manifest.json' and p.suffix!='.part':
            files.append(dict(file=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    save('manifest.json',dict(study='NIFTY V17',frozen_scope=[FIRST,FREEZE],requested_reports=len(reports),file_count=len(files),
         bytes=sum(r['bytes'] for r in files),partition='Frozen historical study, source receipts and separately dated forward refresh',
         immutable_V16_manifest=prior['v16_manifest'],source_files=source,files=files))
    print('Delivered and hash checked',len(reports),'reports,',links,'links and',len(files),'files',flush=True)


if __name__=='__main__':
    run()
