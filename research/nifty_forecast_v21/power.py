"""Controlled simulations of what additional equities can and cannot identify."""
from .common import *

SCENARIOS={
    'shared_relationship':(.007,.0,.008,.010,.023,1.),
    'sector_specific_cancellation':(.0,.014,.008,.015,.023,1.),
    'pure_common_market_noise':(.0,.0,.030,.0,.008,1.),
    'correlated_idiosyncratic_noise':(.006,.0,.013,.025,.014,1.),
    'spurious_training_relationship':(.009,.006,.017,.012,.024,0.),
    'no_index_predictability_even_with_stock_signal':(.0,.010,.015,.010,.025,1.),
}


def fit_demo(x,y,sector):
    a=x.mean(axis=1);b=y.mean(axis=1)
    direct=(a@b)/(a@a+1.)
    dx=x-x.mean(axis=1,keepdims=True)
    dy=y-y.mean(axis=1,keepdims=True)
    w=(dx*dy).sum()/max(1.e-9,(dx*dx).sum()+x.shape[1])
    z=[]
    for g in range(8):
        yes=sector==g
        ax=dx[:,yes];by=dy[:,yes]
        z.append(.55*w+.45*np.sum(ax*by)/max(1.e-9,np.sum(ax*ax)+yes.sum()))
    return direct,w,np.array(z)


def run():
    rng=np.random.default_rng(SEED+1667)
    rows=[]
    iterations=300
    for h,history in ((5,53),(21,11)):
        for count in (8,32,128):
            sectors=np.arange(count)%8
            equal=np.full(count,1/count)
            side=np.array([-1,-1,-1,-1,1,1,1,1])[sectors]
            for label,(g,delta,s_common,s_sector,s_idio,after) in SCENARIOS.items():
                for rep in range(iterations):
                    n=history+128
                    state=rng.normal(size=(n,1))
                    xi=rng.normal(size=(n,count))
                    if label=='no_index_predictability_even_with_stock_signal':
                        xi=np.broadcast_to(xi[:,:1],xi.shape).copy()
                    a=.60*state+.80*xi
                    b=g+delta*side
                    shock=s_common*rng.normal(size=(n,1))+s_sector*rng.normal(size=(n,8))[:,sectors]+s_idio*rng.normal(size=(n,count))
                    mu=a*b
                    mu[history:]*=after
                    y=mu+shock
                    direct,pool,s=fit_demo(a[:history],y[:history],sectors)
                    out=a[history:];truth=y[history:]@equal
                    x={'neutral':np.zeros(len(out)), 'date_only':direct*(out@equal), 'shared_pool':pool*(out@equal),
                       'partial_sector':(out*s[sectors])@equal}
                    for name,pred in x.items():
                        v=np.array([0.] * count) if name=='neutral' else s[sectors] if name=='partial_sector' else np.full(count,direct if name=='date_only' else pool)
                        rows.append(dict(horizon=h,scenario=label,assets=count,market_windows=history,replicate=rep,model=name,
                                         index_mse=np.square(pred-truth).mean(),
                                         oracle_index_mse=np.square(pred-mu[history:]@equal).mean(),
                                         coefficient_mse=np.square(v-after*b).mean()))
    d=pd.DataFrame(rows)
    write('synthetic-power-cases.csv.gz',d)
    z=d.groupby(['horizon','scenario','assets','market_windows','model'],as_index=False).agg(
        replications=('replicate','nunique'),index_rmse=('index_mse',lambda x:np.sqrt(x.mean())),
        oracle_rmse=('oracle_index_mse',lambda x:np.sqrt(x.mean())),coef_rmse=('coefficient_mse',lambda x:np.sqrt(x.mean())))
    location=d.pivot(index=['horizon','scenario','assets','market_windows','replicate'],columns='model',values='index_mse')
    paired=location.sub(location.date_only,axis=0).mul(-1).reset_index().melt(
        id_vars=['horizon','scenario','assets','market_windows','replicate'],var_name='model',value_name='mse_gain')
    win=paired.groupby(['horizon','scenario','assets','market_windows','model'],as_index=False).agg(
        better_share=('mse_gain',lambda x:(x>0).mean()),gain_low=('mse_gain',lambda x:x.quantile(.05)),gain_high=('mse_gain',lambda x:x.quantile(.95)))
    cols=['horizon','scenario','assets','market_windows','model']
    write('synthetic-power-summary.csv',z.merge(win,on=cols,validate='1:1'))
    save('synthetic-power-config.json',dict(iterations=iterations,distinct_market_windows=[53,11],stock_counts=[8,32,128],groups=8,
      controls='Direct ridge on dates, within-date pooled slope, pooled plus 45% sector deviations, neutral zero. Independent synthetic windows are a simplifying assumption.',
      parameters={k:dict(shared_beta=a,sector_beta=b,market_noise=c,sector_noise=d,own_noise=e,test_signal_fraction=f) for k,(a,b,c,d,e,f) in SCENARIOS.items()},
      interpretation='Simulation assesses potential estimation gains conditional on these designs. Synthetic cases add no real NIFTY evidence.'))
    print('Simulated',len(d),'synthetic model scores',flush=True)


if __name__=='__main__':
    run()
