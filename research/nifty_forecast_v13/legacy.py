"""Resolve protected V8–V11 benchmark rows and rescale their archived distributions."""
from .common import *
from .paths import direction_forecasts
from research.nifty_forecast_v12.analysis import group_data
from research.nifty_forecast_v12.common import original_laws, exact_law, bundle_entries


def run():
    base=pd.read_csv(OUT/'reproduced-endpoint.csv',low_memory=False)
    protected=set(REFERENCE)-set(base.model)
    g=group_data(pd.read_csv(V12/'all-predictions.csv',low_memory=False))
    rows=[r.assign(model=n) for (c,h,n),r in g.items() if c in ('early','later') and n in protected]
    refs=pd.concat(rows,ignore_index=True)
    assert {'NEUTRAL','J11_EXCLUDE_B_ROT','O_NATIVE_PHASE0','B_CHANGE','J10_STRUCTURAL_BLEND'}.issubset(refs.model)
    assert not refs.duplicated(['horizon','model','origin']).any()
    # The original V11 law inventory includes priced and neutral control laws.
    laws=original_laws(set(refs.model)-{'V8_R_RESIDUAL','PH_NATIVE_POOLED'})
    with (V8/'retained-endpoint-laws.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line)
            if r['model']=='R_RESIDUAL':
                laws[int(r['horizon']),'V8_R_RESIDUAL',r['origin']]=exact_law(r['atoms'],r['weights'])
    if 'PH_NATIVE_POOLED' in protected:
        for (h,n,d,_),law in bundle_entries(V12/'laws/phase.npz'):
            if n=='PH_NATIVE_POOLED':
                laws[int(h),n,d]=law
    compact=[]
    unmatched=[]
    delta=0.
    grid=(np.arange(512)+.5)/512
    for row in refs.itertuples():
        key=(row.horizon,row.model,row.origin)
        if key not in laws:
            unmatched.append(key)
            continue
        d=laws[key]
        score=d.score(row.realized_return)
        difference=max(abs(score[k]-getattr(row,k)) for k in ('brier','crps','p'))
        assert difference < 2e-10,(key,difference)
        delta=max(delta,difference)
        m=float(d.w@d.a)
        v=float(np.sqrt(d.w@(d.a-m)**2))
        compact.append((key,d.quantile(grid),m,v))
    assert any(name=='NEUTRAL' for (_,name,_),*other in compact)
    path=OUT/'prior-endpoint-quantiles.npz'
    with np.load(path,allow_pickle=False) as a:
        arrays={k:a[k] for k in ['keys','values','means','sd']}
    # Use immutable original V12 replay output as the source for the current quantile archive.
    existing={tuple(a) for a in arrays['keys']}
    keep=[r for r in compact if (str(r[0][0]),*r[0][1:]) not in existing]
    if keep:
        np.savez_compressed(path,keys=np.concatenate([arrays['keys'],np.array([k for k,_,_,_ in keep])]),
                            values=np.vstack([arrays['values'],np.stack([v for _,v,_,_ in keep])]),
                            means=np.r_[arrays['means'],[m for _,_,m,_ in keep]],sd=np.r_[arrays['sd'],[s for _,_,_,s in keep]])
    write('protected-endpoint.csv',refs,index=False)
    previous=pd.read_csv(OUT/'distribution-predictions.csv',low_memory=False)
    known=set(previous.model)
    more=[]; log=[]
    for h in HORIZONS:
        y=matrix(f'targets-{h}.csv',OUT);x=matrix(f'features-{h}.csv',OUT).copy()
        x['finance_iv']=x.finance*x.iv_relative; x['breadth_iv']=x.breadth5*x.iv_relative
        new,ledger=direction_forecasts(x,y,y[y.cohort.notna()],h)
        more.extend(r for r in new if r['model'] not in known)
        log.extend(r for r in ledger if r['model'] not in known)
    write('protected-rescaled-endpoint.csv',pd.DataFrame(more),index=False)
    save('protected-endpoint-replay.json',dict(point_rows=len(refs),rescaled_rows=len(more),atom_laws_replayed=len(compact),
          missing_original_atoms=unmatched,maximum_replay_difference=delta,fit_attempts=log,
          models=sorted(refs.model.unique())))
    print('Replayed',len(compact),'protected laws and added',len(more),'risk-scaling variants',flush=True)


if __name__=='__main__':
    run()
