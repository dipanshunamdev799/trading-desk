"""Add official breadth to actual V8 and V9 parent implementations and partitions."""
import joblib
from .common import *
from .engine import cohort_queries,score_law
from research.nifty_forecast_v8 import experiments as e8,models as m8
from research.nifty_forecast_v9 import run_models as e9
from research.nifty_forecast_v10.targets import buckets


def run():
    p=matrix('price.csv').close;x8,_=e8.frames();x9,_=e9.inputs()
    y={h:matrix(f'labels-{h}.csv') for h in [5,21]}
    valid={h:cohort_queries(h).set_index('origin',drop=False) for h in y}
    r8=read('search-ledger.json',V8)
    reg9=read('base-registry.json',V9)['configuration']
    add=matrix('matrices/BREADTH.csv',OUT)
    refs=[('V8_R_RESIDUAL','R_RESIDUAL'),('V8_W_STRUCT_EMBARGO','W_STRUCT_EMBARGO'),('V8_A_STRUCTURE_CHANGE','A_STRUCTURE_CHANGE')]
    variants={f'{alias}_EQ':{'parent':alias,'sources':'previous completed session official equal-weight/cap-weight spreads'} for alias,n in refs}
    for n in ['P_CLUSTER','P_ROT','P_STRUCTURE']:variants[n+'_EQ']={'parent':n,'sources':'official breadth level/change pair'}
    save('legacy-registry.json',{'registered':now(),'models':variants,'code':sha(SRC/'legacy_breadth.py')})
    parent8=pd.read_csv(V8/'all-predictions.csv');parent9=pd.read_csv(V9/'all-predictions.csv')
    result=[];ledger=[];laws=[]
    def record(version,entry,name,x,s,adapt,typical,train,inner,val,query,reference):
        h=entry['horizon'];d=y[h];cohort='later' if entry['cohort']=='primary' else entry['cohort']
        eval_=valid[h].loc[query];expected=reference.set_index('origin').loc[query]
        m0,m1,res,original=adapt(x,d,train,inner,val,query,s)
        actual=pd.DataFrame(a.score(d.loc[o,'return']) for a,o in zip(original,query))
        fields=['p','predicted_mean','predicted_median','brier','crps']
        np.testing.assert_allclose(actual[fields],expected[fields],atol=1e-12,rtol=1e-12)
        assert d.loc[train,'endpoint'].max()<entry['cutoff'] and d.loc[inner,'endpoint'].max()<val[0]
        m0,m1,res,forecasts=adapt(x.join(add),d,train,inner,val,query,s)
        path=f"models/legacy-{h}-{cohort}-{entry['fold']}-{name}.joblib"
        joblib.dump({'outer':m0,'inner':m1,'train':list(train),'inner_dates':list(inner),'validation':list(val),'query':list(query),'residuals':res},OUT/path,compress=2)
        cut=np.quantile(d.loc[train[-252:],'return'],[.1,.3,.5,.7,.9])
        for q,a in zip(eval_.itertuples(),forecasts):
            result.append({**score_law(h,entry['fold'],name,q,a,float(p.loc[q.origin]),cohort),**buckets(a,q.realized_return,cut)})
            laws.append({'model':name,'horizon':h,'cohort':cohort,'origin':q.origin,'endpoint':q.endpoint,'atoms':a.a.tolist(),'weights':a.w.tolist()})
        ledger.append({'model':name,'parent':typical,'version':version,'status':'ok','horizon':h,'cohort':cohort,'fold':entry['fold'],
             'cutoff':entry['cutoff'],'training_endpoint':d.loc[train,'endpoint'].max(),'inner_endpoint':d.loc[inner,'endpoint'].max(),
             'inner_cutoff':val[0],'training':len(train),'queries':len(query),'file':path,'sha256':sha(OUT/path),
             'parent_max_replay_error':float(abs(actual[fields].to_numpy()-expected[fields].to_numpy()).max())})
    def fit8(x,y,tr,ii,vv,q,s):
        m=m8.fit(s,x.loc[tr],y.loc[tr,'return'].to_numpy());m0=m8.fit(s,x.loc[ii],y.loc[ii,'return'].to_numpy())
        err=y.loc[vv,'return'].to_numpy()-m8.location(m0,x.loc[vv])
        vol=x.loc[vv,'p_rv21'].to_numpy()
        rot=x.loc[vv,'r_bank_change'].to_numpy() if 'r_bank_change' in x else np.zeros(len(vv))
        return m,m0,err,m8.predict(m,x.loc[q],err,vol,rot)
    def fit9(x,y,tr,ii,vv,q,s):return e9.fit_variant(s,x,y,tr,ii,vv,q)
    (OUT/'models').mkdir(exist_ok=True)
    for alias,n in refs:
        for r in r8['fold_attempts']:
            if r.get('model')!=n or r['status']!='ok' or r['cohort']!='primary':continue
            s=r8['configurations'][n];obj=joblib.load(V8/r['artifact']);h=r['horizon']
            reference=parent8[(parent8.model.eq(n))&parent8.horizon.eq(h)&parent8.cohort.eq('primary')]
            record('V8',r,alias+'_EQ',x8[s['frame']],s,fit8,alias,obj['training'],obj['inner_dates'],obj['validation'],obj['queries'],reference)
    for r in read('base-ledger.json',V9):
        n=r['model'];h=r['horizon']
        if n not in ['P_CLUSTER','P_ROT','P_STRUCTURE'] or r['status']!='ok':continue
        s=reg9[n];obj=joblib.load(V9/r['model_file'])
        reference=parent9[(parent9.model.eq(n))&parent9.horizon.eq(h)&parent9.cohort.eq(r['cohort'])]
        record('V9',r,n+'_EQ',x9[s['frame']],s,fit9,n,obj['tr'],obj['ii'],obj['vv'],obj['q'],reference)
    write('legacy-predictions.csv',pd.DataFrame(result));save('legacy-ledger.json',ledger);cache('legacy-laws.jsonl',laws)
    print('Legacy parent additions',len(result),'with exact parent replay',flush=True)


if __name__=='__main__':run()
