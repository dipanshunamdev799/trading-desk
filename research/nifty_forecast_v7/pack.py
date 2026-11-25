"""Hash the delivered code, matrices, predictions, reports and fitted artifacts."""
from importlib.metadata import version
from platform import python_version
from .common import *


def run():
    verification=read('verification.json')
    if not verification['passed'] or len(read('report-manifest.json'))!=15:
        raise ValueError('Verified fifteen-report package required')
    key_files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='delivery-manifest.json']
    source_files=[p for p in SOURCE.glob('*') if p.is_file()]
    if OUT == BASE/'2026-11-24/run-001':
        index=ROOT/'NIFTY_V7_RESEARCH.md'
        import re
        assert all((ROOT/p).is_file() for p in re.findall(r'\]\(([^)]+)\)',index.read_text(encoding='utf-8')))
        source_files.append(index)
    upstream=[V6/n for n in ['native-reference.csv','liquidity-reference.csv','price.csv','global-reference.csv','state-features.csv',
            'labels-5.csv','labels-10.csv','labels-15.csv','labels-21.csv','all-predictions.csv']]
    save('delivery-manifest.json',{'completed_at':now(),'history':'2025–2026 exposed historical research',
         'python_version':python_version(),'versions':{x:version(x) for x in ['numpy','pandas','scipy','scikit-learn','lightgbm','joblib','matplotlib','requests']},
         'delivered':{p.relative_to(ROOT).as_posix():sha(p) for p in key_files+source_files},
         'upstream_inputs':{p.relative_to(ROOT).as_posix():sha(p) for p in upstream},'verified':verification})
    print('Packaged and hashed',len(key_files)+len(source_files),'artifacts',flush=True)


if __name__=='__main__':
    run()
