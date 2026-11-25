"""Freeze hashes for the completed study package."""
from importlib.metadata import version
from platform import python_version
import re
from .common import *


def run():
    v=read('verification.json');assert v['passed'] and len(read('report-manifest.json'))==17
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='delivery-manifest.json']
    files += [p for p in SRC.iterdir() if p.is_file()]
    if OUT==DEFAULT:
        index=ROOT/'NIFTY_V8_RESEARCH.md'
        assert all((ROOT/ref).is_file() for ref in re.findall(r'\]\(([^)]+)\)',index.read_text(encoding='utf-8')))
        files.append(index)
    save('delivery-manifest.json',{'completed_at':now(),'python':python_version(),'research_only':True,
         'packages':{p:version(p) for p in ['numpy','pandas','scipy','scikit-learn','lightgbm','joblib','matplotlib','requests']},
         'files':{p.relative_to(ROOT).as_posix():sha(p) for p in files},'verification':v})
    print('Hashed',len(files),'delivered files',flush=True)


if __name__=='__main__':run()
