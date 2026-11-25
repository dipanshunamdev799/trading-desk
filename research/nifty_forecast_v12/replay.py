"""Read-only freeze and exact replay of the published reference models."""
from concurrent.futures import ThreadPoolExecutor
import joblib
from .common import *
from research.nifty_forecast_v11 import engine as old
from research.nifty_forecast_v11 import ensemble as old_mix

SELECT={'O_NATIVE_PHASE0','O_NATIVE_PHASE1','O_NATIVE_STAGGERED','O_ROT_PHASE1','M_RECENT_85','M_SPREAD_85','M_EARLIEST_85',
        'B_CHANGE','B_ROT_EQ','B_SPARSE_EQ','B_STUD_EQ','D_EQ_STUDENT','D_EQ_SIGNMAG','L_EQ_CONC','B_ROT','B_NATIVE_EQ'}
FIXED=['J11_BREADTH_ALL','J11_BREADTH_ALL_HIST','J11_EXCLUDE_B_ROT','J10_STRUCTURAL_BLEND','J10_HISTORY_SHRINK']
CHECK=['p','predicted_mean','predicted_median','brier','crps','log_loss']


def protect():
    files={str(Path(p)):h for p,h in read('protected-inputs.json',V11)['files'].items()}
    latest=read('manifest.json',V11)
    files.update({str((V11/p).relative_to(ROOT)):h for p,h in latest['files'].items()})
    files.update({str(Path(p)):h for p,h in latest['research_code'].items()})
    files[str((V11/'manifest.json').relative_to(ROOT))]=sha(V11/'manifest.json')
    reports=[V11/'NIFTY_V11_RESEARCH.md',*sorted(V11.glob('V11_*.md'))]
    inspected=[]
    for r in reports:
        t=r.read_text(encoding='utf-8').splitlines()
        inspected.append({'name':r.name,'sha256':sha(r),'lines':len(t),'headings':[s for s in t if s.startswith('#')]})
    assert len(inspected)==16
    save('protected-inputs.json',{'files':files,'reports':inspected,'reference_through':FREEZE})
    with ThreadPoolExecutor(max_workers=6) as pool:
        def check(item):
            path,h=item
            p=ROOT/path
            return path if not p.is_file() or sha(p)!=h else None
        bad=[s for s in pool.map(check,files.items()) if s]
    save('protected-verification.json',{'checked':len(files),'mismatch':bad,'passed':not bad})
    assert not bad,bad[:8]
    print('Protected inputs',len(files),'byte-exact',flush=True)


def direct():
    registry=read('registry.json',V11)
    target=pd.read_csv(V11/'all-predictions.csv',float_precision='round_trip').set_index(['horizon','model','origin'])
    frames,_,state,price,broad,pos,_=old.inputs()
    labels={h:matrix(f'labels-{h}.csv') for h in [5,21]}
    stores={h:old.target_store(h,y,price,broad) for h,y in labels.items()}
    fitted=[]
    for r in registry['attempts']:
        n=r['model'];h=r['horizon']
        if n not in SELECT or r['status']!='ok':continue
        path=V11/r['file']
        assert sha(path)==r['sha256']
        o=joblib.load(path);s=registry['configurations'][n];y=labels[h]
        tr,ii,vv,pp=(pd.Index(o[k]) for k in ['train','inner_dates','validation','pool'])
        assert y.loc[tr,'endpoint'].max()<r['cutoff'] and y.loc[ii,'endpoint'].max()<r['inner_cutoff']
        laws,_,_=old.distributions(s,old.frame_for(s,frames),y,stores[h],pos,state,h,r['cutoff'],
                                   (tr,ii,vv,pp,r['inner_cutoff']),o['query'])
        for date,law in zip(o['query'],laws):
            score=law.score(y.loc[date,'return'])
            ref=target.loc[h,n,date]
            got=np.asarray([score[k] for k in CHECK])
            np.testing.assert_allclose(got,ref[CHECK].to_numpy(float),atol=1e-12,rtol=1e-12)
            fitted.append({'horizon':h,'model':n,'origin':date,'cohort':r['cohort'],'endpoint':ref.endpoint,
                           'max_abs_delta':float(abs(got-ref[CHECK].to_numpy(float)).max()),**{k:score[k] for k in CHECK}})
    components=set(old_mix.CORE+['B_ROT_EQ','B_STUD_EQ','HISTORY','BASE_ROTATION','S_ELASTIC','T_VOL_STUDENT'])
    saved=original_laws(components)
    old_references=pd.read_csv(V10/'all-predictions.csv',float_precision='round_trip').set_index(['horizon','model','origin'])
    designs={
      'J11_BREADTH_ALL':(['B_ROT_EQ','B_SPARSE_EQ','B_STUD_EQ'],[.4,.3,.3]),
      'J11_BREADTH_ALL_HIST':(['B_ROT_EQ','B_SPARSE_EQ','B_STUD_EQ','HISTORY'],[.2,.15,.15,.50]),
      'J11_EXCLUDE_B_ROT':([n for n in old_mix.CORE if n!='B_ROT'],None),
      'J10_STRUCTURAL_BLEND':(['BASE_ROTATION','S_ELASTIC','T_VOL_STUDENT'],[.4,.3,.3]),
      'J10_HISTORY_SHRINK':(['BASE_ROTATION','S_ELASTIC','T_VOL_STUDENT','HISTORY'],[.2,.15,.15,.50]),
    }
    for n,(members,weights) in designs.items():
        source=old_references if n.startswith('J10') else target
        for (h,day),r in source.xs(n,level='model').iterrows():
            law=mixture([saved[h,k,day] for k in members],weights)
            score=law.score(r.realized_return)
            got=[score[k] for k in CHECK]
            ref=r[CHECK].to_numpy(float)
            np.testing.assert_allclose(got,ref,atol=1e-12,rtol=1e-12)
            fitted.append({'horizon':h,'model':n,'origin':day,'cohort':r.cohort,'endpoint':r.endpoint,
                           'max_abs_delta':float(np.max(abs(got-ref))),**{k:score[k] for k in CHECK}})
    res=pd.DataFrame(fitted)
    write('exact-replay.csv',res)
    f=res.groupby(['model','horizon','cohort']).agg(rows=('origin','size'),brier=('brier','mean'),
                                                  crps=('crps','mean'),max_error=('max_abs_delta','max')).reset_index()
    write('replay-summary.csv',f)
    save('exact-replay.json',{'passed':True,'forecasts':len(res),'direct_refit_models':sorted(SELECT),
                             'complete_law_recipes':designs,'max_abs_delta':res.max_abs_delta.max()})
    print('Fresh exact reference replays',len(res),flush=True)


def older():
    from research.nifty_forecast_v10 import reproduce as v10
    p=OUT/'replay/older'
    p.mkdir(parents=True,exist_ok=True)
    original=v10.read
    v10.OUT=p
    v10.save=lambda n,d:save('replay/older/'+n,d)
    v10.write=lambda n,d,index=False:write('replay/older/'+n,d,index=index)
    v10.read=lambda n,where=p:original(n,where)
    v10.preserve=lambda:save('replay/older/preservation.json',{'files':read('protected-inputs.json',V11)['files']})
    v10.run()
    p10=pd.read_csv(V10/'all-predictions.csv')
    from research.nifty_forecast_v10.experiments import fit_laws,common_indices,BASE_MODELS
    from research.nifty_forecast_v10.targets import target_store
    from research.nifty_forecast_v10.features import cached
    from research.nifty_forecast_v5.data import load
    from research.nifty_forecast_v9.run_models import cohort_queries
    x,_,state=cached();price=matrix('price.csv')
    raw,_=load();broad=raw['idx_Nifty_500'].close
    h=21;y=matrix('labels-21.csv');t=target_store(h,y,price,broad)
    positions=pd.Series(np.arange(len(price)),index=price.index)
    s=BASE_MODELS['NEUTRAL']
    ref=p10[p10.horizon.eq(21)&p10.model.eq('NEUTRAL')].set_index('origin')
    rows=[]
    for (cohort,fold),g in cohort_queries(h).groupby(['split','fold'],sort=False):
        first=g.origin.min()
        tr,ii,vv,ic,pool=common_indices(y,first,s,state)
        _,_,_,laws,_,_=fit_laws(s,x['five'],y,t,state,positions,h,first,tr,ii,vv,g.origin,pool)
        for r,d in zip(g.itertuples(),laws):
            s0=d.score(r.realized_return)
            np.testing.assert_allclose([s0[k] for k in CHECK],ref.loc[r.origin,CHECK].to_numpy(float),atol=1e-12)
            rows.append({'horizon':h,'cohort':cohort,'fold':fold,'model':'NEUTRAL','origin':r.origin,**s0})
    write('replay/neutral-monthly.csv',pd.DataFrame(rows))


def legacy_breadth():
    from shutil import copy2
    from research.nifty_forecast_v11 import legacy_breadth as prior
    out=OUT/'replay/legacy-breadth'
    (out/'matrices').mkdir(parents=True,exist_ok=True)
    copy2(V11/'matrices/BREADTH.csv',out/'matrices/BREADTH.csv')
    prior.OUT=out
    prior.write=lambda n,d,index=False:write('replay/legacy-breadth/'+n,d,index=index)
    prior.save=lambda n,d:save('replay/legacy-breadth/'+n,d)
    prior.cache=lambda n,rows:(out/n).write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    prior.run()
    key=['horizon','model','cohort','origin']
    a=pd.read_csv(out/'legacy-predictions.csv').set_index(key).sort_index()
    b=pd.read_csv(V11/'legacy-predictions.csv').set_index(key).sort_index()
    pd.testing.assert_index_equal(a.index,b.index)
    np.testing.assert_allclose(a[CHECK],b[CHECK],atol=1e-12,rtol=1e-12)
    save('legacy-breadth-replay.json',{'passed':True,'predictions':len(a),'model_ids':sorted(set(a.index.get_level_values('model'))),
                                     'maximum_delta':(a[CHECK]-b[CHECK]).abs().max().max()})


if __name__=='__main__':
    import sys
    {'protect':protect,'direct':direct,'older':older,'legacy':legacy_breadth}[sys.argv[1]]()
