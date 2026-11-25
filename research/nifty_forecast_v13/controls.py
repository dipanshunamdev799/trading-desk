"""Exact empirical frequencies and continuous diffusion reflection controls."""
from scipy.special import ndtr

from .common import *
from .paths import path_metrics, path_barriers, barrier_actual, score_distribution, TARGETS
from .volatility import maturity


def run():
    path_rows=[]; barrier_rows=[]
    for h in HORIZONS:
        y=matrix(f'targets-{h}.csv',OUT)
        x=matrix(f'features-{h}.csv',OUT)
        with np.load(OUT/f'observed-paths-{h}.npz',allow_pickle=False) as z:
            observed=z['paths']
        for day,row in y[y.cohort.notna()].iterrows():
            t=maturity(y,day)[-210:]
            j=y.index.get_loc(day)
            hist=observed[y.index.get_indexer(t)]
            metrics=path_metrics(hist)
            iv=x.at[day,'iv_nearest' if h==5 else 'iv_bracket']
            sd=iv*np.sqrt(h/252.)
            for field in TARGETS:
                path_rows.append(dict(horizon=h,origin=day,model='empirical_exact',target=field,actual=row[field],
                                      **score_distribution(metrics[field],row[field])))
            levels=[(str(i),k,i) for i,k in enumerate(THRESHOLDS)]
            levels += [(f'iv{m}',m*sd,None) for m in [.5,1.,1.5,2.]]
            for label,k,index in levels:
                actual=barrier_actual(row,observed,j,k,index)
                for key,p in path_barriers(hist,metrics,k).items():
                    barrier_rows.append(dict(horizon=h,origin=day,model='empirical_exact',barrier=label,threshold=k,
                                             event=key,p=p,actual=int(actual[key])))
                # Driftless log-price Brownian motion with constant raw-IV scale.
                # One-sided reflection gives twice the endpoint tail probability.
                for key,z in [('upper',np.log1p(k)/sd),('lower',-np.log1p(-k)/sd)]:
                    p=float(ndtr(-z))
                    for suffix,mult in [('touch',2),('endpoint',1)]:
                        event=f'{key}_{suffix}'
                        barrier_rows.append(dict(horizon=h,origin=day,model='analytic_iv_diffusion',barrier=label,
                                                 threshold=k,event=event,p=mult*p,actual=int(actual[event])))
    write('exact-and-analytic-path-controls.csv',pd.DataFrame(path_rows),index=False)
    write('exact-and-analytic-barrier-controls.csv',pd.DataFrame(barrier_rows),index=False)


if __name__=='__main__':
    run()
