"""Replay all34 historical configurations in a new folder, without source refetch."""
import argparse,subprocess,sys,shutil,os
from .common import *
def run():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);a=parser.parse_args();dest=a.out.resolve()
    if not dest.is_relative_to(ROOT):raise ValueError('Output must remain in workspace')
    dest.mkdir(parents=True,exist_ok=False)
    for n,digest in read('dataset-manifest.json')['files'].items():
        if sha(OUT/n)!=digest:raise ValueError('Frozen dataset changed: '+n)
        shutil.copy2(OUT/n,dest/n)
    for name in ['feature-definitions.json','liquidity-acquisition.json','dataset-manifest.json'] :shutil.copy2(OUT/name,dest/name)
    for folder in ['liquidity','metadata'] :shutil.copytree(OUT/folder,dest/folder)
    (dest/'sources').mkdir()
    for p in (OUT/'sources').glob('*.json'):shutil.copy2(p,dest/'sources'/p.name)
    env=dict(os.environ);env['NIFTY_V5_OUT']=str(dest);env['NIFTY_V5_REPLAY']='1'
    commands=[['experiment','register'],['experiment','stage1'],['experiment','stage2'],['expansion'],['liquidity'],['attribution']]
    for command in commands:subprocess.run([sys.executable,'-u','-m','research.nifty_forecast_v5.'+command[0],*command[1:]],cwd=ROOT,env=env,check=True)
    old=pd.read_csv(OUT/'all-predictions.csv');new=pd.concat([pd.read_csv(p) for p in dest.glob('predictions-stage*.csv')],ignore_index=True)
    keys=['horizon','model','origin'];old=old.sort_values(keys).reset_index(drop=True);new=new.sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(old[keys],new[keys])
    deltas={}
    for c in ['p','predicted_mean','predicted_median','brier','crps','coverage50','coverage80','pinball']:
        np.testing.assert_allclose(old[c],new[c],atol=1e-10,rtol=1e-10);deltas[c]=float(np.max(abs(old[c]-new[c])))
    save('full-reproduction.json',{'completed':now(),'destination':str(dest.relative_to(ROOT)),'systems':new.model.nunique(),'records':len(new),'max_abs_differences':deltas,'new_source_acquisition':False,'fresh_forecast_reissued':False,
        'note':'Current hardened code fixes unused Indian-forest metadata directly; original failed attempts remain in original run, reproduction has no need to repeat that bug. This is repeatability, not independent validation.'})
    print('Reproduced all historical predictions',len(new),'systems',new.model.nunique(),flush=True)
if __name__=='__main__':run()
