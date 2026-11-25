"""Honest prior forecasts for training mixture weights and weekly-state features."""
import joblib
from .common import *
from .engine import fit,means,predict
from research.nifty_forecast_v3.experiment import available,inner_split
from sklearn.linear_model import LogisticRegression
def run():
    if (OUT/'prequential-laws.jsonl').exists():raise FileExistsError('Prequential baseline cache exists')
    save('prequential-plan.json',{'registered_at':now(),'parents':['I03_nosize','L01'],'rule':'Exact original monthly prequential origins, fully matured/embargoed fitting; inner42 heldout residuals; cache every law before downstream mixture fitting',
        'classifier':'Native logisticC=.1, max_iter3000; independent probability diagnostic, never assigned to an invented return law',
        'mixture_training':'Only cached origin forecasts with endpoint strictly before current refit; latest42; regularized weights only, no test outcomes'})
    frames={'I03_nosize':pd.read_csv(OUT/'native-reference.csv',index_col=0),'L01':pd.read_csv(OUT/'liquidity-reference.csv',index_col=0)}
    old=pd.read_csv(V3/'predictions.csv');records=[];ledger=[];classifier_models={}
    (OUT/'models').mkdir(exist_ok=True)
    for h in [5,21]:
        labels=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0);query=old[(old.horizon==h)&(old.model=='B00_empirical')]
        for fold,g in query.groupby('fold'):
            cutoff=g.origin.min();ix=available(labels,cutoff);ii,vv=inner_split(labels,ix)
            for name,x in frames.items():
                spec={'kind':'ridge','alpha':100};inner=fit(spec,x.loc[ii],labels,vv[0]);res=labels.loc[vv,'return'].to_numpy()-means(inner,x.loc[vv]);model=fit(spec,x.loc[ix],labels,cutoff);ds=predict(model,x.loc[g.origin],res)
                path=OUT/'models'/f'baseline-h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'cutoff':cutoff,'inner_fit':list(ii),'inner_validation':list(vv)},path,compress=3)
                clf=None
                if name=='I03_nosize':
                    clf=LogisticRegression(C=.1,max_iter=3000,random_state=SEED).fit(model['scale'].transform(x.loc[ix]),labels.loc[ix,'return'].gt(0).astype(int));cp=clf.predict_proba(model['scale'].transform(x.loc[g.origin]))[:,1];classifier_models[f'{h}|{fold}']=clf
                for j,(r,d) in enumerate(zip(g.itertuples(),ds)):
                    records.append({'horizon':h,'fold':fold,'origin':r.origin,'endpoint':r.endpoint,'split':r.split,'model':name,'realized_return':r.realized_return,
                        'atoms':d.a.tolist(),'weights':d.w.tolist(),'p':d.stats()['p_up'],'classifier_p':float(cp[j]) if clf is not None else None,
                        'mean':d.stats()['mean_return'],'expected_absolute_return':d.stats()['expected_absolute_return'],'return_std':d.stats()['endpoint_return_std']})
                ledger.append({'horizon':h,'fold':fold,'model':name,'cutoff':cutoff,'last_endpoint':str(labels.loc[ix,'endpoint'].max()),'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
            print('Honest parent forecasts',h,fold,flush=True)
    path=OUT/'prequential-laws.jsonl';path.write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in records),encoding='utf-8');save('prequential-ledger.json',ledger)
    joblib.dump(classifier_models,OUT/'prequential-classifiers.joblib',compress=3)
    # Verify own baseline implementation numerically against every named outer forecast.
    v5=pd.read_csv(V5/'all-predictions.csv');differences=[]
    for r in records:
        if r['split']!='outer_exposed':continue
        expected=v5[(v5.horizon==r['horizon'])&(v5.model==r['model'])&(v5.origin==r['origin'])].iloc[0];diff=abs(r['p']-expected.p);differences.append(diff)
        if diff>1e-12:raise AssertionError('V6 reference differs from frozen V5')
    save('reference-engine-verification.json',{'passed':True,'outer_records':len(differences),'max_probability_difference':max(differences)})
    # Only historical h5-issued states; no backfill before the first honest forecast.
    index=frames['I03_nosize'].index;state=pd.DataFrame(index=index)
    for name in ['I03_nosize','L01']:
        source={r['origin']:r for r in records if r['horizon']==5 and r['model']==name}
        for field in ['p','mean','expected_absolute_return','return_std']:
            series=pd.Series({d:r[field] for d,r in source.items()}).reindex(index);state['w_'+name+'_'+field]=series
            state['w_'+name+'_'+field+'_slope5']=series.diff(5)/5
    state.to_csv(OUT/'state-features.csv')
    print('Cached prequential laws',len(records),'baseline maxp error',max(differences),flush=True)
if __name__=='__main__':run()
