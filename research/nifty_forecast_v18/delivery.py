"""Verify linked deliverables and hash the frozen V18 study and its new sources."""
import re
import sqlite3
from .common import *

RECEIPTS=('financial-listing-receipt.json','structured-document-receipt.json','attachment-source-receipts.json',
          'non-price-sources.json','macro-release-receipt.json','event-path-archive.json','forward-ledger.json')

def references(x):
    if isinstance(x,dict):
        if x.get('file') and x.get('sha256'):
            yield x['file'],x['sha256']
        for u in x.values():
            if isinstance(u,(list,dict)):
                yield from references(u)
    if isinstance(x,list):
        for z in x:
            yield from references(z)

def run():
    p=[OUT/(f'V18_{key}.md') for key in REPORTS]
    assert len(p)==19 and all(x.is_file() for x in p)
    links=0
    for path in [OUT/'README.md',OUT/'NIFTY_V18_RESEARCH.md',*p]:
        for label in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf8')):
            if label!='manifest.json' and not label.startswith(('https://','http://')):
                assert (path.parent/label).is_file(),(path.name,label)
                links+=1
    verified={}
    for book in RECEIPTS:
        filebook=read(book)
        k=0
        for file,expected in references(filebook):
            path=OUT/file
            assert path.is_file() and sha(path)==expected,(book,file)
            k+=1
        verified[book]=k
    for ir in read('announcement-inventory.json')['source']:
        assert sha(ROOT/ir['file'])==ir['sha256']
    previous=read('predecessor-protection.json')
    assert sha(V17/'manifest.json')==previous['v17_manifest']
    with sqlite3.connect(OUT/'corporate-information.sqlite') as db:
        assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
    f=read('forward-ledger.json')
    receipt=read('validation-receipt.json')
    assert len(f['records'])==6 and receipt['chronological_sentinels']>=16
    save('delivery-receipt.json',dict(at=now(),reports=len(p),local_links=links,source_hashes=verified,prior_v17_hashes=previous['artifacts'],
         protected_v17_manifest=previous['v17_manifest'],published_forward_at=f['checked_at'],new_issues=f['new_v18_issues']))
    rows=[]
    for z in sorted(OUT.rglob('*')):
        if z.is_file() and z.name!='manifest.json' and z.suffix not in ('.partial','.part'):
            rows.append(dict(file=z.relative_to(OUT).as_posix(),bytes=z.stat().st_size,sha256=sha(z)))
    source=[dict(file=z.relative_to(ROOT).as_posix(),sha256=sha(z),bytes=z.stat().st_size) for z in sorted(SRC.glob('*.py'))]
    save('manifest.json',dict(study='NIFTY V18',frozen_scope=[FIRST,FREEZE],reports=19,file_count=len(rows),
                            bytes=sum(r['bytes'] for r in rows),files=rows,source_files=source,
                            immutable_V17_manifest=previous['v17_manifest']))
    print('Verified',len(p),'reports,',links,'local links and',len(rows),'artifact hashes',flush=True)

if __name__=='__main__':
    run()
