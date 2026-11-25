"""Freeze hashes for the complete V9 research delivery."""
from importlib.metadata import version
from platform import python_version
import re
from .common import *


def run():
    results=read('verification.json');assert results['passed'] and len(read('report-manifest.json'))==16
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='delivery-manifest.json']
    files.extend(p for p in SRC.iterdir() if p.is_file())
    if OUT==DEFAULT:
        index=ROOT/'NIFTY_V9_RESEARCH.md'
        assert all((ROOT/link).is_file() for link in re.findall(r'\]\(([^)]+)\)',index.read_text(encoding='utf-8')))
        files.append(index)
    save('delivery-manifest.json',{'finished_at':now(),'research_only':True,'python':python_version(),
         'packages':{p:version(p) for p in ['numpy','pandas','scipy','scikit-learn','joblib','matplotlib','requests']},
         'files':{p.relative_to(ROOT).as_posix():sha(p) for p in files},'verification':results})
    print('Packaged',len(files),'hashed files',flush=True)


if __name__=='__main__':run()
