"""Quantify finite Monte Carlo noise using exact laws and common-random prefixes."""
from .common import *
from .laws import Law,loaded,piece
from research.nifty_forecast_v22.analogues import path_variables

BUDGETS=(256,1024,4096,16384)
SEEDS=8


def sample(law,u):
    return law.atoms[np.searchsorted(np.cumsum(law.weights),u,side='right').clip(0,len(law.atoms)-1)]


def scalars(law,y,kind,h):
    if kind=='return':
        up=law.positive()
        return dict(probability=up,mean=law.moments()[0],q10=law.quantiles(.1),q90=law.quantiles(.9),brier=(up-(y>0))**2,crps=law.crps(y))
    elif kind=='range':
        q=.04 if h==5 else .08
        p=1.-law.cdf(q)
        return dict(probability=p,mean=law.moments()[0],q10=law.quantiles(.1),q90=law.quantiles(.9),brier=(p-(y>q))**2,crps=law.crps(y))
    raise ValueError(kind)


def process(arms,h,day,true,kind,barriers=None):
    rows=[]
    truth={k:scalars(law,true,kind,h) for k,law in arms.items()}
    for seed in range(SEEDS):
        rng=np.random.default_rng(SEED+721*seed+pd.Timestamp(day).dayofyear+17*h)
        u=rng.random(max(BUDGETS))
        for key,law in arms.items():
            a=sample(law,u)
            for n in BUDGETS:
                q=Law.build(a[:n])
                sc=scalars(q,true,kind,h)
                for measure,v in sc.items():
                    exact=truth[key][measure]
                    rows.append(dict(horizon=h,day=day,track=kind,model=key,n=n,seed=seed,measure=measure,exact=exact,sample=v,error=v-exact))
            if barriers and key in barriers:
                # Index selection is based on complete joint paths, preserving range and barrier dependence.
                xs=barriers[key]
                j=(u*len(xs)).astype(int).clip(0,len(xs)-1)
                exact=float(xs.mean())
                for n in BUDGETS:
                    calc=float(xs[j[:n]].mean())
                    rows.append(dict(horizon=h,day=day,track='range',model=key,n=n,seed=seed,measure='high_touch_probability',
                                     exact=exact,sample=calc,error=calc-exact))
    return rows


def run():
    index=csv('precision-path-index.csv')
    all_paths=np.load(OUT/'precision-joint-paths.npz')
    rows=[]
    for (h,day),group in index.groupby(['horizon','day']):
        a={};b={}
        for r in group.itertuples(index=False):
            m=path_variables(all_paths[r.key].astype(float))
            a[r.model]=Law.build(m['range'])
            b[r.model]=m['path_high']>(.015 if h==5 else .04)
        rows+=process(a,h,day,float(group.actual_range.iloc[0]),'range',b)
    z=csv('v23-return-cases.csv.gz')
    a=loaded(OUT,'v23-return-laws.npz')
    for h,g in z[z.clock.eq('native_0910')].groupby('horizon'):
        dates=np.array(sorted(g.day.unique()))
        want=set(dates[np.linspace(0,len(dates)-1,12).astype(int)])
        g=g[g.day.isin(want)&g.model.isin(('protected_direction','protected_distribution','equal_families','component_coherent_joint'))]
        for day,p in g.groupby('day'):
            arm={r.model:piece(a,r.law) for r in p.itertuples(index=False)}
            rows+=process(arm,h,day,float(p.actual.iloc[0]),'return')
    a=pd.DataFrame(rows)
    a['abs_error']=a.error.abs();a['sq_error']=a.error**2
    write('simulation-precision-cases.csv.gz',a)
    summary=a.groupby(['horizon','track','n','measure'],as_index=False).agg(
        trials=('error','size'),mae=('abs_error','mean'),median_absolute=('abs_error','median'),
        mse=('sq_error','mean'),bias=('error','mean'),p90_abs=('abs_error',lambda x:x.quantile(.90)))
    summary['rmse']=np.sqrt(summary.pop('mse'))
    write('simulation-precision-summary.csv',summary)
    paired=[]
    for lane,before,after in [('range','india_state_matched','mixed_strict'),('return','protected_direction','equal_families')]:
        sub=a[a.track.eq(lane)&a.model.isin([before,after])&a.measure.isin(['brier','crps'])]
        v=sub.pivot(index=['horizon','day','n','seed','measure'],columns='model',values=['exact','sample']).dropna()
        p=pd.DataFrame(dict(exact_gain=v['exact'][before]-v['exact'][after],
             simulated_gain=v['sample'][before]-v['sample'][after])).reset_index()
        p['sign_inversion']=np.sign(p.exact_gain)!=np.sign(p.simulated_gain)
        p['gain_error']=abs(p.exact_gain-p.simulated_gain)
        for key,t in p.groupby(['horizon','n','measure']):
            paired.append(dict(horizon=key[0],n=key[1],measure=key[2],track=lane,parent=before,candidate=after,replicates=len(t),
                               exact_gain=t.exact_gain.mean(),simulated_gain=t.simulated_gain.mean(),gain_error_mae=t.gain_error.mean(),
                               sign_inversion_rate=t.sign_inversion.mean()))
    write('simulation-paired-gain-noise.csv',pd.DataFrame(paired))
    save('simulation-precision-design.json',dict(budgets=BUDGETS,seeds=SEEDS,n_return_days=24,n_path_days=24,
         exact='Weighted empirical atom evaluation and exact path event masses',
         draws='Prefix common uniforms shared across compared models at each origin and independent seeds across repetitions. Range and first-side probability are summaries of the same sampled joint paths.',
         precision_scope='This diagnostic measures resampling error conditional on the stored finite laws. It cannot quantify statistical error in the fitted market process.'))
    print('Numerical precision checked across',len(a),'score comparisons.',flush=True)


if __name__=='__main__':
    run()
