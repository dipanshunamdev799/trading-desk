"""Rebuild and archive full predictive laws for every successfully fitted V11 model."""
from concurrent.futures import ProcessPoolExecutor
import joblib
from .common import *
from .engine import inputs,frame_for,distributions,target_store,Distribution


def bundle(batch):
    ratings=pd.read_csv(OUT/f'{batch}-predictions.csv',float_precision='round_trip').set_index(['horizon','model','origin'])
    frames,_,state,price,broad,pos,_=inputs()
    labels={h:matrix(f'labels-{h}.csv') for h in [5,21]}
    stores={h:target_store(h,y,price,broad) for h,y in labels.items()}
    specs=read(f'{batch}-registry.json')['models']
    index=[];atoms=[];weights=[];offset=[0];expected_scores=['p','predicted_mean','predicted_median','brier','crps']
    for row in read(f'{batch}-ledger.json'):
        if row['status']!='ok':continue
        obj=joblib.load(OUT/row['file'])
        h=row['horizon'];name=row['model'];s=specs[name];x=frame_for(s,frames)
        settings={**s,'_scale_cols':list(frames[s['plus'][0]]) if s.get('scale_only') else []}
        plan=(pd.Index(obj['train']),pd.Index(obj['inner_dates']),pd.Index(obj['validation']),pd.Index(obj['pool']),row['inner_cutoff'])
        ds,_,_=distributions(settings,x,labels[h],stores[h],pos,state,h,row['cutoff'],plan,obj['query'])
        for origin,d in zip(obj['query'],ds):
            t=ratings.loc[h,name,origin];a=d.score(t.realized_return)
            np.testing.assert_allclose([a[k] for k in expected_scores],t[expected_scores].to_numpy(float),atol=2e-11,rtol=1e-11,
                                       err_msg=f'{batch} {name} {origin}')
            index.append((h,name,origin,t.endpoint));offset.append(offset[-1]+len(d.a));atoms.append(d.a);weights.append(d.w)
    assert len(index)==len(ratings)
    path=OUT/'distribution-archive';path.mkdir(exist_ok=True)
    np.savez_compressed(path/f'{batch}.npz',keys=np.array(index),offsets=np.array(offset),atoms=np.concatenate(atoms),weights=np.concatenate(weights))
    print(batch,len(index),'verified full-law atom vectors archived',flush=True)
    return {'batch':batch,'forecasts':len(index),'atoms':offset[-1],'path':f'distribution-archive/{batch}.npz','sha256':sha(path/f'{batch}.npz')}


def run():
    families=['breadth','distribution','memory','overlap','disjoint','international']
    with ProcessPoolExecutor(max_workers=4) as pool:parts=list(pool.map(bundle,families))
    for batch in ['legacy','ensemble','ensemble-exact']:
        path=OUT/f'{batch}-laws.jsonl'
        with path.open(encoding='utf-8') as f:n=sum(1 for _ in f)
        parts.append({'batch':batch,'forecasts':n,'path':path.name,'sha256':sha(path)})
    count=sum(p['forecasts'] for p in parts)
    assert count==sum(len(pd.read_csv(OUT/f'{b}-predictions.csv',usecols=['p'])) for b in families+['legacy','ensemble','ensemble-exact'])
    save('full-law-archive.json',{'forecast_count':count,'parts':parts,
                                 'layout':'Keys are horizon, model, origin, endpoint. Atoms and weights for row i use offsets[i]:offsets[i+1].'})


if __name__=='__main__':run()
