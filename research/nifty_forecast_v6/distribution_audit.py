"""Recover every candidate's full endpoint statistics and verify its saved scores.

Full weighted laws for retained weekly candidates are exported separately. No fit,
feature selection, source update or forward forecast is performed here.
"""
import warnings,joblib
from scipy.stats import t
from .common import *
from .engine import predict,means,mix,Distribution
from .experiments import datasets,SPECS,SMALL
from .forensics import build_variants,GROUPS
from .reproduce import frames

def run():
    pred=pd.read_csv(OUT/'all-predictions.csv');ds,_,state=datasets();native=ds['native'];deep=pd.read_csv(OUT/'deep-features.csv',index_col=0);volume=ds['etf_volume'].filter(regex='^p_liq_')
    xx,_,_,raw,_=frames();top=read('forensic-registry.json')['top_features']
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');variants={h:build_variants(xx,raw,native,{h:top[str(h)]},h) for h in [5,21]}
    weekly={
        'W2_NODEF_VOLUME':pd.concat([native.drop(columns=[c for c in native if GROUPS['DEFENSIVE'](c)]),volume],axis=1),
        'W2_NOAUTO_VOLUME':pd.concat([native.drop(columns=['i_nifty_auto_rel21']),volume],axis=1),
        'W2_DEF_PC':native,'W2_DEF_NORM':native}
    monthly={'M2_WINDOW_SMALL':native[SMALL[:4]],'M2_WINDOW_NATIVE':native,
        'M2_LEVELS':pd.concat([native[SMALL[:4]],state[[c for c in state if not c.endswith('_slope5')]]],axis=1),
        'M2_SLOPES':pd.concat([native[SMALL[:4]],state[[c for c in state if c.endswith('_slope5')]]],axis=1),
        'M2_STATE_LAG1':pd.concat([native[SMALL[:4]],state.shift(1)],axis=1),'M2_HUBER_WINDOW':native}
    cached={(r['horizon'],r['model'],r['origin']):r for r in [json.loads(s) for s in (OUT/'prequential-laws.jsonl').read_text().splitlines()]}
    weights={(r['horizon'],r['fold'],r['model']):r for r in read('mixture-weight-ledger.json')};rows=[];saved=[];maxerr=0.;coefficients=[]
    retained={'F_NO_DEFENSIVE','W2_DEF_NORM','W2_NOAUTO_VOLUME'}
    for (h,fold,name),g in pred.groupby(['horizon','fold','model'],sort=True):
        if name.startswith('J_'):
            cfg=weights[h,fold,name];laws=[]
            for r in g.itertuples():
                aa=cached[h,'I03_nosize',r.origin];bb=cached[h,'L01',r.origin];a=Distribution(aa['atoms'],aa['weights']);b=Distribution(bb['atoms'],bb['weights'])
                if name=='J_SIGN':
                    rawp=a.stats()['p_up'];p=(1-cfg['sign_beta'])*rawp+cfg['sign_beta']*aa['classifier_p'];tilt=np.where(a.a>0,p/max(rawp,1e-9),(1-p)/max(1-rawp,1e-9));laws.append(Distribution(a.a,a.w*tilt))
                else:laws.append(mix(a,b,cfg['I03_weight']))
        else:
            artifact=joblib.load(OUT/'models'/f'h{h}-{fold}-{name}.joblib')
            if name=='M_RISK_PANEL':
                current=pd.DataFrame({'own_rv':native.loc[g.origin,'p_rv21'].to_numpy(),'vix_daily':native.loc[g.origin,'p_vix'].to_numpy()/100/np.sqrt(252),'momentum':native.loc[g.origin,'p_ret21'].to_numpy(),'sync':deep.loc[g.origin,'q_sync'].to_numpy(),'correlation':deep.loc[g.origin,'q_sector_correlation'].to_numpy()})
                risk=artifact['risk'];s=artifact['scale'];parent=artifact['mean_parent']['model'];mu=means(parent,native.loc[g.origin]);pool=parent['pool'];ratio=np.clip(np.exp(risk.predict(s.transform(current))),.5,2);sigma=current.own_rv.to_numpy()*np.sqrt(21)*ratio;laws=[]
                for j in range(len(g)):
                    atoms=np.maximum(.5*mu[j]+.5*pool.mean()+sigma[j]*np.sqrt(3/5)*t.ppf((np.arange(401)+.5)/401,df=5),-.999999);laws.append(Distribution(np.r_[atoms,pool],np.r_[np.full(401,.65/401),np.full(len(pool),.35/len(pool))]))
            else:
                if name in variants[h]:x=variants[h][name][0]
                elif name in weekly:x=weekly[name]
                elif name in monthly:x=monthly[name]
                else:
                    key=SPECS[name]['features'];x=ds[f'{key}_{h}'] if key in ['mediated','global_direct'] else ds['small'] if key=='matched_small' else ds[key]
                model=artifact['model'];laws=predict(model,x.loc[g.origin],artifact['residual'])
                if h==5 and name in retained:
                    sc=model['scale'];coef=model['estimator'].coef_;idx=model.get('defensive_norm',[])
                    for j,c in enumerate(sc.cols):
                        factor=1/np.sqrt(len(idx)) if j in idx else 1.
                        coefficients.append({'horizon':h,'fold':fold,'model':name,'feature':c,'train_median':sc.med[j],'train_mean':sc.mu[j],'train_sd':sc.sd[j],
                            'extra_group_factor':factor,'ridge_coefficient_on_transformed_input':coef[j],'equivalent_coefficient_on_standardized_input':coef[j]*factor,'intercept':model['estimator'].intercept_,'cutoff':artifact['cutoff'],'clip_standardized_input_at':5})
        for r,d in zip(g.itertuples(),laws):
            score=d.score(r.realized_return);expected=np.array([getattr(r,c) for c in ['p','predicted_mean','predicted_median','crps','brier']]);actual=np.array([score[c] for c in ['p','predicted_mean','predicted_median','crps','brier']]);np.testing.assert_allclose(actual,expected,atol=1e-12,rtol=1e-12);maxerr=max(maxerr,float(abs(actual-expected).max()));s=d.stats();q=s['quantiles'];require=np.diff(list(q.values()))
            if (require<0).any():raise AssertionError('Crossed quantile')
            rows.append({'horizon':h,'fold':fold,'model':name,'origin':r.origin,'endpoint':r.endpoint,'p_up':s['p_up'],'mean_return':s['mean_return'],'median_return':s['median_return'],**q,
                **{f'bucket{i}_p':v for i,v in enumerate(s['buckets'])},'expected_absolute_return':s['expected_absolute_return'],'endpoint_return_std':s['endpoint_return_std'],
                'endpoint_below2':float(d.w[d.a<-.02].sum()),'endpoint_below5':float(d.w[d.a<-.05].sum()),'path_breach_probability':None,'future_realized_volatility':None})
            if h==5 and name in retained:saved.append({'horizon':h,'fold':fold,'model':name,'origin':r.origin,'endpoint':r.endpoint,'atoms':d.a.tolist(),'weights':d.w.tolist(),'status':'reconstructed exposed-history law; not a forward issuance'})
    pd.DataFrame(rows).to_csv(OUT/'full-endpoint-predictions.csv',index=False);pd.DataFrame(coefficients).to_csv(OUT/'retained-candidate-feature-weights.csv',index=False)
    (OUT/'retained-distributions.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in saved),encoding='utf-8')
    save('distribution-audit.json',{'completed_at':now(),'passed':True,'rows':len(rows),'max_score_difference':maxerr,'retained_laws':len(saved),'weights_rows':len(coefficients),
        'meaning':'Every primary law reconstructed from its saved model/cache; ordered quantiles and same-law probability/mean/median/proper scores checked. Path probabilities and future realized volatility intentionally unavailable.'})
    print('Recovered and verified',len(rows),'complete endpoint laws; max score difference',maxerr,flush=True)

if __name__=='__main__':run()
