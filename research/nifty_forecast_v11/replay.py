"""Replay V8 to V10 references inside an isolated output tree."""
from .common import *

FIELDS=['p','predicted_mean','predicted_median','brier','crps','log_loss']
REPLAY=['NEUTRAL','BASE_ROTATION','S_ELASTIC','T_RAW','T_VOL_STUDENT','T_SIGNMAG','N_EQ_CONTROL','N_EQ_OFFICIAL',
        'C85_RECENT','C85_EARLIEST','C85_SPREAD','OMAX_PLAIN','OMAX_BLOCKMEAN','O126_GLS','O126_STAGGERED',
        'DATED_FUTURES_PARENT','DATED_FUTURES','DATED_STRADDLE_PARENT','DATED_STRADDLE']


def redirect(module,folder):
    p=OUT/folder;p.mkdir(parents=True,exist_ok=True)
    module.OUT=p
    module.save=lambda n,d:save(f'{folder}/{n}',d)
    module.write=lambda n,d,index=False:write(f'{folder}/{n}',d,index=index)


def freeze():
    v10=read('manifest.json',V10)
    protected=read('preservation.json',V10)['files']
    for local,h in v10['files'].items():protected[(V10/local).relative_to(ROOT).as_posix()]=h
    protected.update(v10['research_code'])
    protected[(V10/'manifest.json').relative_to(ROOT).as_posix()]=sha(V10/'manifest.json')
    for older in ['preservation.json']:
        assert (V10/older).exists()
    reports=[]
    for p in [V10/'NIFTY_V10_RESEARCH.md',*sorted(V10.glob('V10_*.md'))]:
        lines=p.read_text(encoding='utf-8').splitlines()
        reports.append({'path':p.name,'sha256':sha(p),'lines':len(lines),'headings':[s for s in lines if s.startswith('#')]})
    assert len(reports)==17
    save('protected-inputs.json',{'files':protected,'studied_reports':reports,'V10_vintage':'2026-11-17'})


def older():
    from research.nifty_forecast_v10 import reproduce as v10
    from research.nifty_forecast_v8 import invariance
    redirect(v10,'replay/older')
    v10.preserve=lambda:save('replay/older/preservation.json',{'files':read('protected-inputs.json')['files']})
    original=v10.read
    v10.read=lambda n,where=v10.OUT:original(n,where)
    v10.run()
    redirect(invariance,'replay/invariance')
    invariance.run()
    invariance.run(sector_alias=True)
    for batch in ['invariance','sector-alias']:
        a=pd.read_csv(V10/f'duplicate-replay/{batch}-effects.csv')
        b=pd.read_csv(OUT/f'replay/invariance/{batch}-effects.csv')
        pd.testing.assert_frame_equal(a,b,atol=1e-12,rtol=1e-12)


def dated():
    x=pd.read_csv(V10/'dated-derivatives-inputs.csv').set_index('day')
    cash=pd.read_csv(V10/'native-equal-weight-closes.csv').set_index('day').sort_index()
    d=x.reindex(cash.index).shift()
    a=['same_contract_excess_log_return','oi_change_over_volume','roll_open_interest_shift','near_oi_concentration',
       'next_volume_share','front_roll','net_carry_innovation','curve_30d']
    return d,{'DATED_FUTURES':a,'DATED_STRADDLE':['straddle_21day_scale']}


def v10():
    from research.nifty_forecast_v10 import experiments,transfer,mixtures
    from research.nifty_forecast_v10.features import cached
    redirect(experiments,'replay/v10')
    spec=read('experiment-registry.json',V10)['configurations']
    frames,masks,state=cached()
    d,di=dated()
    for n,cols in di.items():
        frames[n]=frames['ten'].join(d[cols])
        masks[n]=d[cols].notna().any(axis=1).reindex(frames['ten'].index).fillna(False)
    # Retain the original names, date rules, feature masks and distribution methods.
    for n in REPLAY:
        assert n in spec
    experiments.run('base',{n:spec[n] for n in REPLAY},custom=(frames,masks))
    redirect(transfer,'replay/transfer')
    selected=['X_ONLY','X_ADAPT','X_MULTI','X_SHIFT','X_RANDOM','X_UNRELATED']
    transfer.CONFIG={k:v for k,v in transfer.CONFIG.items() if k in selected}
    (transfer.OUT/'models').mkdir(exist_ok=True)
    transfer.run()
    a=pd.read_csv(V10/'all-predictions.csv')
    keys=['horizon','cohort','model','origin']
    checks=[]
    for group,file in [('models','replay/v10/base-predictions.csv'),('transfer','replay/transfer/transfer-predictions.csv')]:
        g=pd.read_csv(OUT/file);ref=a[a.model.isin(g.model)].set_index(keys).sort_index()
        res=g.set_index(keys).sort_index()
        pd.testing.assert_index_equal(ref.index,res.index)
        np.testing.assert_array_equal(ref.endpoint,res.endpoint)
        np.testing.assert_allclose(ref[FIELDS],res[FIELDS],atol=1e-12,rtol=1e-12)
        checks.append({'group':group,'rows':len(g),'models':sorted(g.model.unique()),'max_delta':float(abs(ref[FIELDS]-res[FIELDS]).max().max())})
    mix={}
    with (OUT/'replay/v10/base-laws.jsonl').open(encoding='utf-8') as f:
        for line in f:
            o=json.loads(line);mix[o['horizon'],o['origin'],o['model']]=o
    for line in (V10/'base-laws.jsonl').open(encoding='utf-8'):
        o=json.loads(line)
        if o['model']=='HISTORY':mix[o['horizon'],o['origin'],'HISTORY']=o
    from research.nifty_forecast_v10.estimators import Distribution
    references=a[a.model.isin(['J10_STRUCTURAL_BLEND','J10_HISTORY_SHRINK'])]
    found=[]
    for r in references.itertuples():
        names,weights,_=mixtures.MIX[r.model]
        laws=[mix[r.horizon,r.origin,n] for n in names]
        d=Distribution(np.concatenate([l['atoms'] for l in laws]),np.concatenate([w*np.array(l['weights']) for l,w in zip(laws,weights)]))
        s=d.score(r.realized_return)
        np.testing.assert_allclose([s[k] for k in FIELDS],[getattr(r,k) for k in FIELDS],atol=1e-12,rtol=1e-12)
        found.append({'model':r.model,'horizon':r.horizon,'origin':r.origin,'cohort':r.cohort,'endpoint':r.endpoint,**s})
    write('replay/v10/rebuilt-mixtures.csv',pd.DataFrame(found))
    save('v10-replay.json',{'passed':True,'checks':checks,'mixtures':len(found),'mixture_weights':mixtures.MIX})


if __name__=='__main__':
    import sys
    {'freeze':freeze,'older':older,'v10':v10}[sys.argv[1]]()
