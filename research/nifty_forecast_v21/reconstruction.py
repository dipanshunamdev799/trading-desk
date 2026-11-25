"""Compare constituent tracking, fixed proxy baskets and constrained sector mixes."""
from scipy.optimize import minimize

from .common import *

MAIN = 'nifty50_monthly_drift_lag5'
SECTOR_BASE = 'sector_simplex'


def weights_from(x):
    a=np.asarray(x,float)
    return a/a.sum(axis=-1,keepdims=True)


def simplex(x,y,prior):
    scale=max(1.e-6, np.var(y))
    a=x.T@x/(len(y)*scale)+.06*np.eye(x.shape[1])
    b=x.T@y/(len(y)*scale)+.06*prior
    res=minimize(lambda w:0.5*(w@a@w)-b@w,prior,jac=lambda w:a@w-b,method='SLSQP',
                bounds=[(0,1)]*len(prior), constraints=[{'type':'eq','fun':lambda w:w.sum()-1,'jac':lambda w:np.ones_like(w)}],
                options={'maxiter':90,'ftol':1.e-11})
    return weights_from(np.maximum(0,res.x)) if res.success else prior.copy()


def sectors_fit(prices,official):
    a=prices[list(SECTORS.values())].to_numpy(float)
    b=np.full_like(a,np.nan)
    y=official.to_numpy(float)
    p=np.full(len(y),np.nan)
    receipts=[]
    prior=np.full(a.shape[1],1/a.shape[1])
    for i in range(70,len(a)):
        ix=np.flatnonzero(np.isfinite(a[:i]).all(axis=1)&np.isfinite(y[:i]))[-140:]
        if len(ix)<65:
            continue
        w=simplex(a[ix],y[ix],prior)
        b[i]=w
        az=a[ix]
        base=az.mean(axis=0)
        sd=az.std(axis=0).clip(.001)
        u=(az-base)/sd
        _,_,v=np.linalg.svd(u,full_matrices=False)
        v=v[:3].T
        features=u@v
        beta=np.linalg.solve(features.T@features+8*np.eye(3),features.T@(y[ix]-y[ix].mean()))
        p[i]=y[ix].mean()+((a[i]-base)/sd)@v@beta
        receipts.append(dict(day=official.index[i],last_training=official.index[ix[-1]],n=len(ix),
                             **{s:w[j] for j,s in enumerate(SECTORS)}))
    write('sector-tracking-weights.csv',pd.DataFrame(receipts))
    return a,b,p


def cash_portfolio(w,r):
    valid=np.isfinite(w).all(axis=1)
    q=np.einsum('ij,ij->i',w,np.nan_to_num(r,nan=0.))
    q[~valid]=np.nan
    return q


def price_comparison(raw,ends):
    t=csv('multi-horizon-targets.csv',V20).set_index('day').reindex(raw.index)
    rows=[];cases=[]
    for h in (1,*HORIZONS):
        g=raw if h==1 else np.expm1(np.log1p(raw).rolling(h,min_periods=h).sum().shift(1-h))
        mask=np.isfinite(g[[MAIN,SECTOR_BASE,'actual']]).all(axis=1)
        tt=ends.shift(1-h)
        if h in HORIZONS:
            known=t[f'end_0_{h}'].notna()
            assert t.loc[known,f'end_0_{h}'].eq(tt[known]).all()
        early=raw.index<'2026-06-30' if h==1 else t[f'cohort_{h}'].eq('early')
        later=(raw.index>='2026-06-30') if h==1 else t[f'cohort_{h}'].eq('later')
        for name in g.columns.difference(['actual']):
            valid=g[name].notna()&g.actual.notna()
            blocks={'available':valid,'matched':mask&valid,'earlier':valid&early,'later':valid&later,
                    'large_market_move':valid&mask&g.actual.abs().ge(g.actual[mask].abs().quantile(.92))}
            if h in HORIZONS:
                blocks['primary_origins']=valid&(early|later)
            for group,use in blocks.items():
                v=g.loc[use,[name,'actual']]
                if len(v)<4:
                    continue
                e=v[name]-v.actual
                rows.append(dict(horizon=h,model=name,scope=group,dates=len(v),bias=e.mean(),mae=e.abs().mean(),
                       rmse=np.sqrt(e.pow(2).mean()),tracking_error=e.std(),annualized_tracking_error=e.std()*np.sqrt(252/h),
                       correlation=v[name].corr(v.actual),primary_origins=group=='primary_origins'))
            for a,b,c,day,target in zip(g[name][valid],g.actual[valid],early[valid],g.index[valid],tt[valid]):
                cases.append(dict(horizon=h,day=day,target_end=target,model=name,actual=b,estimate=a,earlier=bool(c),error=a-b))
    return pd.DataFrame(rows),pd.DataFrame(cases)


def run():
    p=np.load(OUT/'equity-panel.npz',allow_pickle=False)
    history=cash()
    days=history.index
    names=p['symbols']
    assert np.array_equal(days,p['days'])
    adj=p['return_adjusted'];raw=p['return_raw'];ex=p['return_exchange']
    actual=history.pct_change(fill_method=None)
    original=actual.nifty50.copy()
    w=p['weight_lag5']
    daily=pd.DataFrame(index=days)
    daily['actual']=original
    for lag in (0,1,5,10):
        daily[f'nifty50_monthly_drift_lag{lag}']=cash_portfolio(p[f'weight_lag{lag}'],adj)
    daily['nifty50_guarded_no_action']=cash_portfolio(w,raw)
    daily['nifty50_guarded_exchange_prev']=cash_portfolio(w,ex)
    wt=csv('dated-weights.csv.gz')
    base=wt[wt.flavor.eq('official_monthly_csv')&wt.index_name.eq('NIFTY 50')]
    static=np.full_like(w,np.nan)
    for when,snap in base.groupby('eligible_lag5'):
        static[days.get_loc(when):]=snap.set_index('symbol').mcap_weight.reindex(names).fillna(0).to_numpy()
    daily['nifty50_monthly_no_drift']=cash_portfolio(static,adj)
    seed=csv('january-liquidity-universe.csv').set_index('symbol').reindex(names)
    s=seed.median_turnover.notna().to_numpy()
    first=np.flatnonzero(days>SEED_END)[0]
    rng=np.random.default_rng(SEED)
    subsets=[]
    for k in range(12):
        subset=rng.choice(np.flatnonzero(s),50,replace=False)
        v=np.zeros(len(names));v[subset]=.02
        subsets.append((f'january_random50_{k+1:02}',v))
    cap=wt[wt.month.eq('2025-01-31')&wt.flavor.eq('official_monthly_csv')].drop_duplicates('symbol').set_index('symbol').mcap_crore
    cap=cap.reindex(names).fillna(0).to_numpy()
    # The dated cap basket observes the same five completed sessions as the monthly source.
    cap_ready=days.get_loc(base.loc[base.month.eq('2025-01-31'),'eligible_lag5'].iloc[0])
    weights=[('january_equal240',s.astype(float)),('january_liquidity240',seed.median_turnover.fillna(0).to_numpy()),
             ('january_liquid50',seed.liquidity_rank.le(50).to_numpy(float)),('january_dated_index_float_cap',cap),*subsets]
    for key,value in weights:
        w0=weights_from(value)
        daily[key]=np.nan_to_num(adj)@w0
        daily.iloc[:(cap_ready if key=='january_dated_index_float_cap' else first),daily.columns.get_loc(key)]=np.nan
    weight_by_sector=np.zeros_like(w)
    groups=p['sector']
    for i in range(cap_ready,len(w)):
        sector=groups[i]
        for j in np.unique(sector[s]):
            now=s&(sector==j)
            weight_by_sector[i,now]=1/now.sum()
        weight_by_sector[i]=weights_from(weight_by_sector[i])
    weight_by_sector[:cap_ready]=np.nan
    daily['january_sector_balanced']=cash_portfolio(weight_by_sector,adj)
    reduced=w.copy()
    for i in range(len(reduced)):
        if np.isfinite(w[i]).all():
            reduced[i,np.argsort(w[i])[-5:]]=0
            reduced[i]=weights_from(reduced[i])
    daily['nifty50_without_five_heaviest']=cash_portfolio(reduced,adj)
    ret,coef,stat=sectors_fit(actual,original)
    daily[SECTOR_BASE]=cash_portfolio(coef,ret)
    daily['sector_equal']=np.mean(ret,axis=1)
    daily['sector_train_pca3']=stat
    coverage=np.einsum('ij,ij->i',w,np.isfinite(adj))
    eligibility=pd.DataFrame(dict(day=days,month=p['vintage_lag5'],received_weight=coverage,expected_constituents=(w>0).sum(axis=1),
                                  missing_weight=1-coverage,heavy5=np.sort(w,axis=1)[:,-5:].sum(axis=1),
                                  weight_hhi=np.square(w).sum(axis=1)))
    rec,all_cases=price_comparison(daily,pd.Series(days,index=days))
    write('index-tracking-leaderboard.csv',rec)
    write('index-tracking-cases.csv.gz',all_cases)
    write('daily-index-reconstruction.csv',daily.reset_index())
    write('daily-constituent-weight-coverage.csv',eligibility)
    np.savez_compressed(OUT/'tracking-factors.npz',sector_returns=ret,sector_weights=coef)
    write('tracking-official-episodes.csv',all_cases[(all_cases.model.eq(MAIN))&(all_cases.horizon.eq(1))]
          .assign(absolute=lambda x:x.error.abs()).nlargest(18,'absolute'))
    save('tracking-config.json',dict(primary=MAIN,sector=SECTOR_BASE,vintage='Monthly free-float market cap shares admitted after five completed cash sessions',
         action_policy='Dated split/bonus ratios or verified cash exchange reset. No cash-dividend reinvestment. Missing price carries the last mark.',
         distinct='Lag zero is an ex-post month-end reconstruction. Lag one and lag ten are timing sensitivities.',
         sector_fit='Nonnegative simplex using up to 140 prior official daily returns. Ridge toward equal, with no future covariance.',
         proxy='January baskets are documented research portfolios. They rebalance to fixed risk weights daily.'))
    print('Measured tracking:',rec.query("horizon == 1 and scope == 'matched' and model == @MAIN").mae.to_list(),flush=True)


if __name__ == '__main__':
    run()
