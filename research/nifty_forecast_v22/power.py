"""Controlled tests of effective sample size, overlap and parameter transfer."""
from .common import *


CASES=('stable_shared','country_specific','global_shocks_no_signal','temporary_shared',
       'structural_reversal','india_unrelated')
DESIGNS=('india_only','foreign_only','partially_pooled','ordinary_zero_shrink')


def correlated(rng,n,news_width,markets,features,scale):
    a=rng.normal(size=(n,1,features))
    b=rng.normal(size=(n,markets,features))
    core=np.sqrt(scale)*a+np.sqrt(1-scale)*b
    if news_width==1:
        return core
    c=np.concatenate([np.zeros((1,markets,features)),np.cumsum(core,axis=0)],axis=0)
    return (c[news_width:]-c[:-news_width])/np.sqrt(news_width)


def coefficients(case,rng,markets):
    signal=np.array([.20,-.14,.10])
    start=np.repeat(signal[None,:],markets,axis=0)
    post=start[0].copy()
    if case=='country_specific':
        start=rng.normal(0,.21,start.shape);post=start[0].copy()
    elif case=='global_shocks_no_signal':
        start*=0.;post*=0.
    elif case=='structural_reversal':
        post=-.85*post
    elif case=='india_unrelated':
        start[0]=0.;post*=0.
    return start,post


def ridge(x,y,penalty):
    return np.linalg.solve(x.T@x+penalty*len(x)*np.eye(x.shape[1]),x.T@y)


def once(case,h,budget,n_markets,independent,rng):
    countries=n_markets+1; m=budget+h-1
    true,post=coefficients(case,rng,countries)
    x=correlated(rng,m,1,countries,3,.32)[h-1:]
    error=correlated(rng,m,h,countries,1,.46)[:,:,0]
    coefficients_=np.broadcast_to(true,(budget,countries,3)).copy()
    if case=='temporary_shared':
        coefficients_[budget//2:]*=.25
        post*=0.
    y=np.einsum('ijk,ijk->ij',x,coefficients_)+.85*error
    xi=x[:,0,:];yi=y[:,0]
    common=ridge(x[:,1:,:].reshape(-1,3),y[:,1:].reshape(-1),.10)
    local=ridge(xi,yi,.10)
    shrunk=ridge(xi,yi,.90)
    joined=np.linalg.solve(xi.T@xi+.90*budget*np.eye(3),xi.T@yi+.90*budget*common)
    xt=correlated(rng,independent,1,1,3,.32)[:,0]
    noise=rng.normal(0,.85,independent)
    test=xt@post+noise
    fit=np.array([local,common,joined,shrunk])
    prediction=xt@fit.T
    return np.mean((test[:,None]-prediction)**2,axis=0),np.mean((fit-post)**2,axis=1)


def run():
    records=[]
    reps=240
    rng=np.random.default_rng(SEED+61)
    for h in ORIGINAL:
        n=EXPECTED[h][2]
        for budget in (60,120):
            for market_n in (1,8,19):
                for case in CASES:
                    trials=[once(case,h,budget,market_n,n,rng) for _ in range(reps)]
                    loss=np.array([a for a,_ in trials])
                    param=np.array([p for _,p in trials])
                    delta=loss[:,3:4]-loss
                    for j,model in enumerate(DESIGNS):
                        u=delta[:,j];q=np.quantile(u,[.1,.9])
                        records.append(dict(horizon=h,train_local_origins=budget,foreign_markets=market_n,independent_test_outcomes=n,
                              reps=reps,data_generator=case,model=model,test_mse=loss[:,j].mean(),parameter_rmse=np.sqrt(param[:,j].mean()),
                              mean_gain_vs_ordinary_shrink=u.mean(),p10_gain_vs_ordinary_shrink=q[0],p90_gain_vs_ordinary_shrink=q[1],
                              fraction_beating_ordinary_shrink=float(np.mean(u>0)),
                              monte_carlo_se_gain=u.std(ddof=1)/np.sqrt(reps)))
    write('synthetic-transfer-sample-efficiency.csv',pd.DataFrame(records))
    save('synthetic-transfer-design.json',dict(replicates_per_cell=reps,study_cells=2*2*3*len(CASES),
         aggregate_replicates=2*2*3*len(CASES)*reps,seed=SEED+61,models=DESIGNS,domains=(1,8,19),
         synthetic_only=True,global_residual_variance_share=.46,input_common_variance_share=.32,
         return_error='Gaussian overlapping 5/21-session sums, date-common and country-specific shocks. Evaluation draws are disjoint.',
         association='Three causal standardized inputs. Stable slopes [.20, -.14, .10]. Two independent-local budgets 60 and 120 consecutive origins.',
         effects='Country heterogeneity, zero conditional mean, temporary shrink to zero, post-train sign reversal, or a separate zero-slope India.'))
    print('Synthetic experiments:',len(records),'summary cells',flush=True)


if __name__=='__main__':
    run()
