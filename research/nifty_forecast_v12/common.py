"""Paths, shared research types and complete-law archive utilities."""
import json
import os
from pathlib import Path

from research.nifty_forecast_v11.common import ROOT,V5,V6,V7,V8,V9,V10,OUT as V11,sha,now,pd,np,matrix
from research.nifty_forecast_v10.estimators import Distribution

SRC=Path(__file__).parent
V12=ROOT/'artifacts/nifty_forecast_v12'
OUT=Path(os.environ.get('NIFTY_V12_OUT',V12/'2026-11-24/run-001')).resolve()
if not OUT.is_relative_to(V12):raise ValueError('V12 must stay inside its own artifact tree')
SEED=20261124
FREEZE='2026-11-17'


def read(name,folder=OUT):
    return json.loads((folder/name).read_text(encoding='utf-8'))


def save(name,body):
    path=OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(body,indent=2,default=str,allow_nan=False),encoding='utf-8')


def write(name,frame,index=False,**kwargs):
    path=OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(path,index=index,**kwargs)


def exact_law(atoms,weights):
    """Use archived normalized, sorted weights without rounding them a second time."""
    d=Distribution.__new__(Distribution)
    d.a=np.asarray(atoms,dtype=float)
    d.w=np.asarray(weights,dtype=float)
    return d


def mixture(laws,weights=None):
    weights=np.full(len(laws),1/len(laws)) if weights is None else np.asarray(weights,float)
    return Distribution(np.concatenate([d.a for d in laws]),np.concatenate([w*d.w for d,w in zip(laws,weights)]))


def pack_bundle(name,keys,laws):
    path=OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    sizes=np.array([len(a.a) for a in laws],dtype=np.int64)
    offsets=np.r_[0,np.cumsum(sizes,dtype=np.int64)]
    atoms=np.concatenate([a.a for a in laws]) if laws else np.empty(0)
    weights=np.concatenate([a.w for a in laws]) if laws else np.empty(0)
    width=len(keys[0]) if keys else 4
    np.savez_compressed(path,keys=np.asarray(keys,dtype=str).reshape(-1,width),offsets=offsets,atoms=atoms,weights=weights)
    return {'path':name,'forecasts':len(keys),'atoms':len(atoms),'sha256':sha(path)}


def bundle_entries(path):
    with np.load(path,allow_pickle=False) as z:
        off=z['offsets'];a=z['atoms'];w=z['weights']
        for i,key in enumerate(z['keys']):
            j,k=off[i:i+2]
            yield tuple(key),exact_law(a[j:k],w[j:k])


def original_laws(names):
    """Load required complete V11/V10 experts by exact saved keys."""
    found={}
    for rec in read('full-law-archive.json',V11)['parts']:
        if rec['path'].endswith('.npz'):
            for (h,n,d,e),law in bundle_entries(V11/rec['path']):
                if n in names:found[int(h),n,d]=law
        else:
            with (V11/rec['path']).open(encoding='utf-8') as f:
                for line in f:
                    r=json.loads(line)
                    if r['model'] in names:found[r['horizon'],r['model'],r['origin']]=exact_law(r['atoms'],r['weights'])
    remain=names-{n for (h,n,d) in found}
    if remain:
        for part in ['base-laws.jsonl','mixture-laws.jsonl','structure-laws.jsonl','target-laws.jsonl']:
            with (V10/part).open(encoding='utf-8') as f:
                for line in f:
                    r=json.loads(line)
                    if r['model'] in remain:
                        found[r['horizon'],r['model'],r['origin']]=exact_law(r['atoms'],r['weights'])
    return found
