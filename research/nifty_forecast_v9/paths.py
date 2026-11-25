"""Volatility-conditioned block paths and regularized daily autoregression."""
from sklearn.linear_model import Ridge
from .common import *
from .models import Distribution
from .run_models import cohort_queries, indices, score_law
from research.nifty_forecast_v5.data import load


def run():
    specs={'PATH_EMPIRICAL':{'parent':'P_HIST','hypothesis':'Historical intact close-to-close log return blocks'},
           'PATH_REGIME':{'parent':'PATH_EMPIRICAL','hypothesis':'Reweight contiguous paths by query versus historical trend and volatility'},
           'PATH_AR_REGIME':{'parent':'PATH_REGIME','hypothesis':'Ridge AR(2) daily recursion with contiguous residual blocks and regime weights'}}
    save('paths-registry.json',{'at':now(),'configuration':specs,'seed':SEED})
    raw,_=load();close=raw['nifty_spot'].close;price=matrix('price.csv').close;logret=np.log(close).diff()
    a=pd.DataFrame({'lag1':logret.shift(),'lag2':logret.shift(2)});ctx=matrix('state-context.csv',OUT)
    rows=[];ledger=[];path_stats=[];saved=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv');q=cohort_queries(h)
        for (cohort,fold),g in q.groupby(['split','fold'],sort=False):
            cutoff=g.origin.min();tr,ii,vv,bound=indices(y,cutoff,{})
            dates=tr[-252:];locs=close.index.get_indexer(dates)
            index=locs[:,None]+np.arange(1,h+1)
            if any(close.index[j]>=cutoff for j in index[:,-1]):raise AssertionError('Future constituent day in path block')
            np.testing.assert_array_equal(close.index.to_numpy()[index[:,-1]],y.loc[dates,'endpoint'])
            paths=logret.to_numpy()[index];assert np.isfinite(paths).all()
            train=a.loc[:cutoff].iloc[:-1].dropna().index
            ar=Ridge(alpha=.03).fit(a.loc[train],logret.loc[train]);alpha=ar.coef_;intercept=ar.intercept_
            err=logret.reindex(a.index)-pd.Series(ar.predict(a.fillna(0)),index=a.index)
            residual=err.to_numpy()[index]
            center=ctx.loc[dates,['s_trend','s_vol']].median().to_numpy()
            hist=ctx.loc[dates,['s_trend','s_vol']].fillna(pd.Series(center,index=['s_trend','s_vol'])).to_numpy()
            spread=np.maximum(hist.std(axis=0),[.1,.0005]);weights=np.ones(len(paths))/len(paths)
            for r in g.itertuples():
                target=ctx.loc[r.origin,['s_trend','s_vol']].to_numpy();target=np.where(np.isfinite(target),target,center)
                distance=np.sum(((hist-target)/spread)**2,axis=1)
                local=np.exp(-.25*np.minimum(distance,50));w=.45*weights+.55*local/local.sum()
                simulated=np.empty_like(residual);last=np.full(len(dates),logret.loc[r.origin]);prev=np.full(len(dates),logret.shift().loc[r.origin]);
                for j in range(h):
                    simulated[:,j]=intercept+alpha[0]*last+alpha[1]*prev+residual[:,j];prev,last=last,simulated[:,j]
                for name,arr,prob in [('PATH_EMPIRICAL',paths,weights),('PATH_REGIME',paths,w),('PATH_AR_REGIME',simulated,w)]:
                    gross=np.exp(np.cumsum(arr,axis=1));ends=gross[:,-1]-1;d=Distribution(ends,prob)
                    rows.append(score_law(h,fold,name,r,d,float(price.loc[r.origin]),cohort))
                    rv=np.sqrt(np.mean(arr**2,axis=1))*np.sqrt(252);actual=logret.loc[r.origin:r.endpoint].iloc[1:]
                    pdown=float(prob[gross.min(axis=1)<.98].sum());touch=float(np.exp(actual.cumsum()).min()<.98)
                    path_stats.append({'model':name,'horizon':h,'cohort':cohort,'fold':fold,'origin':r.origin,'endpoint':r.endpoint,
                                      'estimated_realized_vol':float(prob@rv),'actual_realized_vol':float(np.sqrt(np.mean(actual**2))*np.sqrt(252)),
                                      'p_touch_minus2':pdown,'realized_touch_minus2':touch,'touch_brier':(pdown-touch)**2,'weight_ESS':float(1/(prob@prob))})
                    if r.origin==g.origin.min():saved.append({'model':name,'horizon':h,'origin':r.origin,'source_endpoints':y.loc[dates,'endpoint'].tolist(),
                                         'log_return_paths':arr.tolist(),'weights':prob.tolist()})
            for name in specs:ledger.append({'model':name,'horizon':h,'cohort':cohort,'fold':fold,'cutoff':cutoff,'status':'ok','n':len(g),
                                              'last_endpoint':y.loc[dates,'endpoint'].max(),'ar_last_observation':train[-1],
                                              'ar_intercept':float(intercept),'ar_coefficients':alpha.tolist(),'block_count':len(dates)})
    write('paths-predictions.csv',pd.DataFrame(rows));write('path-conditional-risk.csv',pd.DataFrame(path_stats));save('paths-ledger.json',ledger)
    save('path-reconstruction-samples.json',saved)
    print('Path laws on',len(rows),'origin/model combinations',flush=True)


if __name__=='__main__':run()
