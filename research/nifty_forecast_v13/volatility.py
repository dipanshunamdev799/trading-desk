"""Causal close-to-close volatility forecasts and exact V12 reference replay."""
from concurrent.futures import ThreadPoolExecutor

from scipy.optimize import minimize
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from .common import *
from .data import LOCAL, GLOBAL, DOMESTIC, POSITION
from research.nifty_forecast_v12.common import exact_law

RISK_REFS = {'V12_RV_PATH': 'prior_trailing', 'V12_RV_SCALE': 'prior_fitted_rv',
             'V12_IV_SCALE': 'prior_fitted_iv', 'V12_IV_LAG5': 'prior_fitted_lag5',
             'V12_ETF_SCALE': 'prior_etf', 'V12_INTRA_SCALE': 'prior_intraday'}
BASES = ['har5','har21','har63','ewma','ewma_fast','parkinson','parkinson_gap','garman_klass',
         'garman_klass_gap','rogers_satchell','rogers_satchell_gap','yang_zhang','intraday_1m','intraday_5m',
         'intraday_25m','iv_nearest','iv_bracket','iv_legacy_bracket','iv_session','iv_bracket_session','iv_exact','iv_lag2','iv_lag5',
         'iv_longer','iv_liquid','iv_settlement','iv_rate_zero','iv_rate_high','iv_smooth','iv_truncated',
         'iv_future_forward','iv_same_close']
LEVEL = ['iv_nearest','iv_bracket','satm_iv7','satm_iv14','satm_iv30','satm_iv45','term_slope','term_curve',
         'sskew_down30','sskew_up30','scurvature30','sdensity_q1030','sdensity_q9030','sdensity_five_pct_down30',
         'sup5_proxy30','simplied_skew_moment30','satm_call_put_iv_gap30','sstrip_var30','source_dte','roll_surface']
CHANGE = ['iv_same_contract_change','skew_acceleration','term_transition','satm_iv30_chg1','satm_iv30_chg5',
          'sskew_down30_chg1','sskew_down30_chg5','sskew_up30_chg5','scurvature30_chg5','term_slope_chg5',
          'term_curve_chg5','sdensity_five_pct_down30_chg5','sup5_proxy30_chg5','simplied_skew_moment30_chg5']
PREMIUM = ['variance_gap','iv_relative','iv_ratio_change','iv_breadth','iv_finance']
MODELS = {
    'har_rv': LOCAL[:3], 'range_ridge':['parkinson_gap','garman_klass_gap','rogers_satchell_gap','yang_zhang','ewma'],
    'intraday_ridge':LOCAL, 'har_iv':LOCAL[:3]+['iv_primary'], 'shape_level':['iv_primary']+LEVEL,
    'shape_change':['iv_primary']+CHANGE, 'shape_combined':['iv_primary']+LEVEL+CHANGE,
    'shape_pca':['iv_primary']+LEVEL+CHANGE, 'premium_ridge':['iv_primary']+PREMIUM,
    'position_ridge':['iv_primary']+LEVEL+POSITION+[k+'_chg5' for k in POSITION],
    'global_only':GLOBAL, 'global_plus_iv':['iv_primary']+GLOBAL,
    'global_divergence':['iv_primary']+GLOBAL+['global_iv_gap','global_breadth'],
    'domestic_iv':['iv_primary']+DOMESTIC, 'regime_iv':['iv_primary']+LOCAL+DOMESTIC+PREMIUM,
    'shape_shift21':['iv_primary']+LEVEL+CHANGE, 'shape_block_permute':['iv_primary']+LEVEL+CHANGE,
}


def maturity(y, day):
    selected = y.index[y.endpoint.lt(day)]
    assert selected.empty or y.loc[selected,'endpoint'].max() < day
    return selected


def rescale_features(train, test, fields):
    """Canonicalize exact feature copies on training values before regularization."""
    t = train.reindex(columns=fields)
    a = test.reindex(columns=fields)
    useful = t.columns[t.notna().sum().ge(12)]
    t,t2 = t[useful],a[useful]
    names = t.T.drop_duplicates().index
    t,t2 = t[names],t2[names]
    median = t.median()
    t,t2 = t.fillna(median),t2.fillna(median)
    if not len(names):
        raise ValueError('All regressors unavailable on training history')
    scaler = StandardScaler().fit(t)
    return scaler.transform(t).clip(-5,5),scaler.transform(t2).clip(-5,5),names.tolist(),median.tolist()


def ridge_risk(train, test, target, fields, model, rng):
    a,b,names,medians = rescale_features(train,test,list(dict.fromkeys(fields)))
    if model == 'shape_pca':
        pca = PCA(n_components=min(a.shape[1],4),svd_solver='full').fit(a)
        a,b = pca.transform(a), pca.transform(b)
    if model == 'shape_block_permute' and a.shape[1] > 1:
        chunks = np.array_split(a[:,1:], max(2,len(a)//12))
        a[:,1:] = np.concatenate([chunks[i] for i in rng.permutation(len(chunks))])
    base = 'iv_primary' in fields
    anchor = train.iv_primary.fillna(train.har21).to_numpy() if base else np.ones(len(train))
    anchor_test = test.iv_primary.fillna(test.har21).to_numpy() if base else np.ones(len(test))
    model_fit = Ridge(alpha=210 if base else 105).fit(a,np.log(target.clip(.015)/anchor))
    return np.clip(np.exp(model_fit.predict(b))*anchor_test,.025,.7), {
        'columns':names,'medians':medians,'scaled_coef':model_fit.coef_.tolist(),
        'intercept':float(model_fit.intercept_),'alpha':model_fit.alpha,'anchored':base}


def params(z, method):
    omega = np.exp(z[0])
    weights = np.exp(np.r_[z[1:],0] - max(0,max(z[1:])))
    shares = weights[:-1]/weights.sum()*.995
    if method=='arch':
        return omega, shares[0], 0., 0.
    if method=='garch':
        return omega, shares[0],shares[1],0.
    return omega, shares[0],shares[1],2*shares[2]


def filter_variance(r, method, z, last=False):
    if method == 'egarch':
        center, alpha, beta, gamma = z
        lvalue = np.log(np.mean(r[:20]**2) + .01)
        v = np.empty(len(r)+1)
        for i,e in enumerate(r):
            v[i] = np.exp(lvalue)
            shock = np.clip(e/np.sqrt(v[i]),-8,8)
            lvalue = np.clip((1-beta)*center + beta*lvalue + alpha*(abs(shock)-np.sqrt(2/np.pi)) + gamma*shock,-7.,7.)
        v[-1] = np.exp(lvalue)
    else:
        omega, alpha, beta, gamma = params(z,method)
        v = np.empty(len(r)+1)
        v[0] = np.mean(r[:20]**2)+.01
        for i,e in enumerate(r):
            v[i+1] = omega + (alpha + gamma*(e<0))*e*e + beta*v[i]
    return v[-1] if last else v[:-1]


def garch_fit(e, method):
    e = np.asarray(e)
    if method=='egarch':
        initial,bounds = [np.log(np.mean(e**2)),.16,.91,-.06],[(-5,5),(.001,.75),(.05,.98),(-.5,.5)]
    else:
        initial = {'arch':[-1.,.4],'garch':[-3.,.7,2.2],'gjr':[-3.,.45,2.2,-.35]}[method]
        bounds = [(-7.,3.)]+[(-5.,5.)]*(len(initial)-1)
    def objective(z):
        variance=filter_variance(e,method,z)
        return .5*np.mean(np.log(variance)+e*e/variance)+.001*np.sum(np.square(z[1:]))
    fit=minimize(objective,initial,bounds=bounds,method='L-BFGS-B',options={'maxiter':75})
    return fit.x, bool(fit.success)


def volatility_model(e, h, method, z):
    value = filter_variance(np.asarray(e),method,z,last=True)
    if method=='egarch':
        center,_,beta,_=z
        v=np.exp(center+beta**np.arange(h)*(np.log(value)-center))
    else:
        w,a,b,g=params(z,method)
        persistence=a+b+g/2
        long=w/(1-persistence)
        v=long+(value-long)*persistence**np.arange(h)
    return np.sqrt(v.mean()*252)/100


def historical_scores():
    p = pd.read_csv(V12/'all-predictions.csv',float_precision='round_trip',low_memory=False)
    endpoint = p[p.model.isin(REFERENCE)].copy()
    replayed = set()
    compact = []
    for part in loads(V12/'full-law-archive.json')['parts']:
        path = V12/part['path']
        assert sha(path) == part['sha256']
        with np.load(path,allow_pickle=False) as z:
            keys = z['keys']
            take = np.flatnonzero(np.isin(keys[:,1],REFERENCE))
            off, atoms, weights = z['offsets'], z['atoms'],z['weights']
            book=endpoint.set_index(['horizon','model','origin'])
            for i in take:
                h,n,d,e=keys[i]
                k=(int(h),n,d)
                if k not in book.index:
                    continue
                row=book.loc[k]
                a,w=atoms[off[i]:off[i+1]],weights[off[i]:off[i+1]]
                law=exact_law(a,w)
                sc=law.score(row.realized_return)
                assert row.endpoint == e
                np.testing.assert_allclose([sc['brier'],sc['crps'],sc['p']],[row.brier,row.crps,row.p],rtol=1e-11,atol=2e-11)
                cdf=np.cumsum(w)
                # Selected rescaling families use a common quantile grid plus the exact archived moments.
                grid=np.linspace(0,1,513)[1:]-1/1024
                compact.append((int(h),n,d,a[np.searchsorted(cdf,grid)],float(a@w),float(np.sqrt((a-a@w)**2@w))))
                replayed.add(k)
    assert len(replayed) == len(endpoint)
    np.savez_compressed(OUT/'prior-endpoint-quantiles.npz',keys=np.array([(h,n,d) for h,n,d,*_ in compact]),
                        values=np.stack([a for _,_,_,a,_,_ in compact]),
                        means=np.array([m for _,_,_,_,m,_ in compact]),sd=np.array([s for _,_,_,_,_,s in compact]))
    write('reproduced-endpoint.csv',endpoint,index=False)
    use = p[p.model.isin(RISK_REFS) & p.forecast_path_volatility.notna()]
    output=[]
    for (h,model),g in use.groupby(['horizon','model']):
        target=pd.read_csv(OUT/f'targets-{h}.csv',index_col=0).loc[g.origin]
        np.testing.assert_allclose(target.volatility,g.realized_path_volatility,atol=2e-12)
        np.testing.assert_allclose(abs(g.forecast_path_volatility-g.realized_path_volatility),g.path_volatility_mae,atol=2e-12)
        output.extend(g.rename(columns={'forecast_path_volatility':'prediction'}).assign(model=RISK_REFS[model]).loc[:,['horizon','model','origin','prediction']].to_dict('records'))
    write('prior-volatility.csv',pd.DataFrame(output),index=False)
    save('replay.json',dict(complete_laws=len(replayed),volatility_rows=len(output),source_parts=loads(V12/'full-law-archive.json')['parts'],
         method='Independently rescore exact endpoint atoms and V12 per-origin fitted volatility forecasts against rebuilt OHLC labels.'))
    print('Reproduced',len(replayed),'exact endpoint laws and',len(output),'fitted risk point forecasts',flush=True)


def fit_risk():
    risk_rows=[]; fit_notes=[]; diagnostics=[]
    for h in HORIZONS:
        x=pd.read_csv(OUT/f'features-{h}.csv',index_col=0)
        y=pd.read_csv(OUT/f'targets-{h}.csv',index_col=0)
        q=y[y.cohort.notna()]
        raw='iv_nearest' if h==5 else 'iv_bracket'
        x['iv_primary']=x[raw]
        x['shape_shift_src']=x.iv_primary.shift(21)
        x['india_vix']=x.vix_level.where(x.vix_level.lt(1),x.vix_level/100)
        for feed in ('sstrip_var7','sstrip_var30'):
            x[feed+'_sd']=np.sqrt(x[feed].clip(lower=0))
        seen={}
        rng=np.random.default_rng(SEED+h)
        for d in q.index:
            a=x.loc[d]
            t=maturity(y,d)
            selected = t[-180:]
            fields=BASES+['india_vix','sstrip_var7_sd','sstrip_var30_sd']
            predictions={k:a[k] for k in fields if k in a}
            for w in [.25,.50,.75]:
                predictions[f'fixed_iv_rv_{w:.2f}']=np.sqrt(w*a.iv_primary**2+(1-w)*a.har21**2)
            # A learned one-parameter mixture anchored to the simple 50/50 variance blend.
            clean=selected[x.loc[selected,['iv_primary','har21']].notna().all(axis=1)]
            if len(clean)>=30:
                adj=(x.loc[clean,'iv_primary']**2-x.loc[clean,'har21']**2).to_numpy()
                residual=y.loc[clean,'volatility'].pow(2)-x.loc[clean,'har21'].pow(2)
                weight=np.clip((adj@residual+.025)/(adj@adj+.05),0,1)
                predictions['adaptive_variance_mix']=np.sqrt(weight*a.iv_primary**2+(1-weight)*a.har21**2)
                correction=np.clip(np.exp(np.median(np.log(y.loc[clean,'volatility']/x.loc[clean,'iv_primary']))),.72,1.28)
                predictions['iv_calibrated']=a.iv_primary*correction
            predictions['shifted_raw_iv']=a.shape_shift_src
            for name,fields in MODELS.items():
                if len(selected)<40:
                    continue
                train=x.loc[selected].copy()
                test=x.loc[[d]].copy()
                if name=='shape_shift21':
                    payload=[k for k in fields if k!='iv_primary']
                    shifted=x.reindex(columns=payload).shift(21)
                    train[payload]=shifted.loc[selected]
                    test[payload]=shifted.loc[[d]]
                try:
                    values,note=ridge_risk(train,test,y.loc[selected,'volatility'],fields,name,rng)
                except ValueError as exc:
                    diagnostics.append(dict(horizon=h,origin=d,model=name,error=str(exc)))
                    continue
                predictions[name]=values[0]
                fit_notes.append(dict(horizon=h,origin=d,model=name,training=len(selected),start=selected.min(),last=selected.max(),
                                      max_endpoint=y.loc[selected,'endpoint'].max(),parameters=note))
            available=x.loc[:d,'market_return'].dropna()*100
            for name in ['arch','garch','egarch','gjr']:
                month=d[:7]
                if (name,month) not in seen:
                    z,ok=garch_fit(available,name)
                    seen[name,month]=z
                    fit_notes.append(dict(horizon=h,origin=d,model=name,training=len(available),start=available.index[0],
                                          last=available.index[-1],parameters=z.tolist(),optimizer_success=ok))
                predictions[name]=volatility_model(available,h,name,seen[name,month])
            risk_rows.extend(dict(horizon=h,origin=d,model=name,prediction=float(value)) for name,value in predictions.items()
                             if value is not None and np.isfinite(value) and value>0)
        print(h,'sessions',len(q),'volatility fits evaluated',flush=True)
    write('volatility-predictions.csv',pd.DataFrame(risk_rows),index=False)
    save('volatility-fit-ledger.json',{'models':MODELS,'fits':fit_notes,'failed':diagnostics})


def protected():
    previous=loads(V12/'protected-inputs.json')['files']
    manifest=loads(V12/'manifest.json')
    targets={ROOT/r:v for r,v in previous.items()}
    targets.update({V12/r:v for r,v in manifest['files'].items()})
    targets.update({ROOT/r:v for r,v in manifest['research_code'].items()})
    targets[V12/'manifest.json']=sha(V12/'manifest.json')
    def verify(item):
        path, known=item
        return None if path.is_file() and sha(path)==known else str(path)
    with ThreadPoolExecutor(max_workers=7) as pool:
        problems=[x for x in pool.map(verify,targets.items()) if x]
    save('protection.json',{'files':len(targets),'invalid':problems,'v12_manifest':targets[V12/'manifest.json']})
    assert not problems, problems[:8]
    print('Verified earlier study files',len(targets),flush=True)


if __name__=='__main__':
    import sys
    {'replay':historical_scores,'risk':fit_risk,'protect':protected}[sys.argv[1]]()
