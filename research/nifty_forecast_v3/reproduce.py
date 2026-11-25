"""Repeat the frozen numerical batch in a separate folder; no source refetch."""
import argparse,os,shutil,subprocess,sys
from pathlib import Path
from .audit import ROOT,OUT,sha,save
import json
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    dest=args.out.resolve()
    if not dest.is_relative_to(ROOT):raise ValueError('Output must remain in the workspace')
    manifest=json.loads((OUT/'dataset-manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if sha(OUT/name)!=digest:raise ValueError('Frozen dataset changed: '+name)
    dest.mkdir(parents=True,exist_ok=False)
    files=['features.csv','price.csv','labels-5.csv','labels-21.csv','feature-definitions.json','dataset-manifest.json']
    for name in files:shutil.copy2(OUT/name,dest/name)
    (dest/'reproduction-source.json').write_text(json.dumps({'original_run':str(OUT),'source_hashes':{n:sha(OUT/n) for n in files},'independent_validation':False},indent=2))
    env=dict(os.environ);env['NIFTY_V3_OUT']=str(dest)
    subprocess.run([sys.executable,'-u','-m','research.nifty_forecast_v3.experiment'],cwd=ROOT,env=env,check=True)
    old=pd_read(OUT/'predictions.csv');new=pd_read(dest/'predictions.csv')
    import numpy as np
    for name in ['p','predicted_mean','brier','crps','qlike','tail02_p']:
        np.testing.assert_allclose(old[name],new[name],rtol=1e-10,atol=1e-12)
    print('Reproduced frozen predictions in',dest)
def pd_read(path):
    import pandas as pd
    return pd.read_csv(path)
if __name__=='__main__':main()
