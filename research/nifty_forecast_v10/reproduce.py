"""Exact V9 learning-curve and complete-law replays, including the learned gate."""
import joblib
from sklearn.linear_model import Ridge
from .common import *
from research.nifty_forecast_v9.run_models import inputs,fit_variant,cohort_queries
from research.nifty_forecast_v9.reliability import EXPERTS,mixture
from research.nifty_forecast_v8.models import Scale,Distribution


def preserve():
    old=read('preservation.json',V9)['files']
    newer={str(Path(k)):v for k,v in read('delivery-manifest.json',V9)['files'].items()}
    manifest=V9/'delivery-manifest.json';newer[str(manifest.relative_to(ROOT))]=sha(manifest)
    paths=[ROOT/'NIFTY_V9_RESEARCH.md',*V9.glob('V9_*.md'),*V9.glob('*registry.json'),V9/'all-predictions.csv',V9/'verification.json',V9/'expert-laws.jsonl']
    paths+=sorted((ROOT/'research/nifty_forecast_v9').glob('*.py'))
    reviewed=[{'file':p.relative_to(ROOT).as_posix(),'bytes':len(p.read_text(encoding='utf-8').encode()),'sha256':sha(p)} for p in paths]
    save('preservation.json',{'started':now(),'files':old|newer,'review':reviewed})


def run():
    if (OUT/'reproduction.json').exists():raise FileExistsError('Use a new V10 run directory')
    preserve()
    registry=read('experiment-registry.json',V9);x,_=inputs();out=pd.read_csv(V9/'all-predictions.csv');out=out[out.horizon==5]
    frozen=out.set_index(['cohort','model','origin']).sort_index();y=matrix('labels-5.csv');fields=['p','predicted_mean','predicted_median','brier','crps']
    selected={f'L_ROT_{i}' for i in [85,126,189,252,300,'MAX']}|{'P_HIST','P_CLUSTER'}
    selections=[];scores=[]
    def record(name,cohort,fold,origins,dist):
        frame=pd.DataFrame(law.score(y.loc[d,'return']) for d,law in zip(origins,dist))
        old=frozen.xs((cohort,name),level=[0,1]).loc[origins]
        np.testing.assert_allclose(frame[fields],old[fields],atol=1e-12,rtol=1e-12)
        selections.append({'model':name,'cohort':cohort,'fold':fold,'rows':len(origins),'max_error':float(abs(frame[fields].to_numpy()-old[fields].to_numpy()).max())})
        for d,r in zip(origins,frame.to_dict('records')):scores.append({'model':name,'cohort':cohort,'origin':d,'endpoint':old.loc[d,'endpoint'],'fold':fold,**r})
    for r in registry['attempts']:
        n=r.get('model');cohort=r.get('cohort');h=r.get('horizon')
        if r.get('status')!='ok' or h!=5 or n not in selected or n.startswith('L_') and cohort!='later':continue
        path=V9/r['model_file'];assert sha(path)==r['sha256'];m=joblib.load(path);s=registry['specifications'][n]
        _,_,_,ds=fit_variant(s,x[s['frame']],y,m['tr'],m['ii'],m['vv'],m['q'])
        record(n,cohort,r['fold'],m['q'],ds)
    cache={}
    with (V9/'expert-laws.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line)
            if r['horizon']==5 and r['model'] in EXPERTS:cache[r['origin'],r['model']]=Distribution(r['atoms'],r['weights'])
    stored=pd.read_csv(V9/'expert-weights.csv');stored=stored[stored.horizon==5].set_index(['model','origin'])
    base=out[out.model.isin(EXPERTS)];bs=base.pivot(index='origin',columns='model',values='brier').reindex(columns=EXPERTS)
    cs=base.pivot(index='origin',columns='model',values='crps').reindex(columns=EXPERTS)
    loss=(bs.sub(bs.P_HIST,axis=0)/.25+cs.sub(cs.P_HIST,axis=0)/.02)
    meta=matrix('reliability-features-5.csv',V9).filter(regex='^(?!q_)');q=cohort_queries(5)
    for r in read('reliability-ledger.json',V9):
        if r['horizon']!=5:continue
        dates=q[(q.split==r['cohort'])&(q.fold==r['fold'])].origin.tolist();train=r['training_origins'];gate=None
        if r['used_gate']:
            assert y.loc[train,'endpoint'].max()<r['cutoff']
            scale=Scale().fit(meta.loc[train]);gate=Ridge(alpha=50).fit(scale.transform(meta.loc[train]),loss.loc[train]);g=gate.predict(scale.transform(meta.loc[dates]))
        for name in ['J9_STATIC','J9_REL_SHRINK']:
            ds=[]
            for j,d in enumerate(dates):
                weight=.5 if name=='J9_STATIC' or gate is None else (.65 if g[j,1]<0 else .20)
                w=np.full(len(EXPERTS),weight/len(EXPERTS));w[-1]+=1-weight
                np.testing.assert_allclose(w,stored.loc[(name,d),EXPERTS],atol=1e-12)
                ds.append(mixture([cache[d,n] for n in EXPERTS],w))
            record(name,r['cohort'],r['fold'],dates,ds)
    # Fresh fits against the two protected V8 weekly records.
    from research.nifty_forecast_v8.experiments import frames
    from research.nifty_forecast_v8.models import fit,location,predict
    x8,_=frames();r8=read('search-ledger.json',V8)
    p8=pd.read_csv(V8/'all-predictions.csv');r8rows=0
    for r in r8['fit_attempts'] if 'fit_attempts' in r8 else r8['fold_attempts']:
        n=r.get('model')
        if r['status']!='ok' or r['horizon']!=5 or n not in ['R_RESIDUAL','W_STRUCT_EMBARGO']:continue
        cfg=r8['configurations'][n];blob=joblib.load(V8/r['artifact']);a=x8[cfg['frame']];tr,ii,vv,q=(blob[k] for k in ['training','inner_dates','validation','queries'])
        m=fit(cfg,a.loc[tr],y.loc[tr,'return'].to_numpy());m0=fit(cfg,a.loc[ii],y.loc[ii,'return'].to_numpy())
        res=y.loc[vv,'return'].to_numpy()-location(m0,a.loc[vv]);risk=a.loc[vv,'p_rv21'].to_numpy();rot=a.loc[vv,'r_bank_change'].to_numpy() if 'r_bank_change' in a else np.zeros(len(vv))
        got=pd.DataFrame(law.score(y.loc[d,'return']) for d,law in zip(q,predict(m,a.loc[q],res,risk,rot)))[fields]
        ref=p8[(p8.model==n)&(p8.horizon==5)].set_index('origin').loc[q,fields]
        np.testing.assert_allclose(got,ref,atol=1e-12,rtol=1e-12);r8rows+=len(q)
    write('reproduced-origin-scores.csv',pd.DataFrame(scores));save('reproduction.json',{'passed':True,'V9_forecasts':len(scores),'V8_leading_forecasts':r8rows,
          'folds':selections,'maximum_discrepancy':max(x['max_error'] for x in selections),'protected_files':len(read('preservation.json')['files'])})
    print('Reproduced',len(scores),'V9 scores and',r8rows,'V8 leader scores',flush=True)


if __name__=='__main__':run()
