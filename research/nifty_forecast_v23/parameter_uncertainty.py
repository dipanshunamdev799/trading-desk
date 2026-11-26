"""Keep parameter re-estimation, feature perturbation and market outcome spread distinct."""
from .common import *
from .forecast import F, asof_features, standardize, past_rows, ridge, MIN
from .laws import loaded,piece
from research.nifty_forecast_v20.modeling import block_counts,block_intervals


def probability_after_log_shifts(law,delta):
    t=np.expm1(-np.asarray(delta))
    cuts=np.searchsorted(law.atoms,t,side='right')
    return 1.-np.r_[0.,np.cumsum(law.weights)][cuts]


def run():
    f=csv('v23-return-cases.csv.gz')
    f=f[f.clock.isin(('native_0910','preauction_0855'))&f.model.eq('protected_distribution')]
    book=loaded(OUT,'v23-return-laws.npz')
    uncert=csv('model-uncertainty-cases.csv.gz')
    by=['horizon','clock','day']
    f=f.merge(uncert[by+['family_prob_spread','probability_parameter_se','ordinary_prob_spread','observed_trailing_vol','implied_volatility']],
              on=by,validate='1:1')
    rows=[];trials=[]
    for (h,clock),raw in f.groupby(['horizon','clock']):
        a=raw.sort_values('day').reset_index(drop=True)
        days=a.day.to_numpy()
        v=asof_features(days,clock)
        normalized_scale=np.sqrt(a['var'].to_numpy()).clip(.003)
        truth=(np.log1p(a.actual)-np.log1p(a['median']))/normalized_scale
        mature=a.mature_ns.to_numpy()
        issue=a.issue_ns.to_numpy()
        for i,t in a.iterrows():
            take=past_rows(mature,issue,int(issue[i]))
            if len(take)<MIN:
                continue
            x,point=standardize(v[take],v[i])
            y=truth.iloc[take].to_numpy(float)
            rng=np.random.default_rng(SEED+773*h+i+len(clock))
            scenarios=block_counts(len(take),min(21,max(5,h)),64,rng)
            laws=np.array([ridge(x,y,k,1.60) for k in scenarios])
            bet=ridge(x,y,np.ones(len(take)),1.60)
            law=piece(book,t.law)
            sh=.50*normalized_scale[i]
            delta=np.clip(sh*(laws@point),-.017,.017)
            p1=probability_after_log_shifts(law,delta)
            p0=float(probability_after_log_shifts(law,np.clip(sh*(bet@point),-.017,.017)))
            conf=np.quantile(p1,[.10,.50,.90])
            # The source perturbation is a declared scenario in robust standardized units.
            # Missing fields retain their original missing mask in every draw.
            noise=rng.standard_normal((64,len(F)))*.20*np.isfinite(v[i])*np.isfinite(v[take]).any(axis=0)
            probe=np.tile(point,(64,1));probe[:,1:]+=noise
            p2=probability_after_log_shifts(law,np.clip(sh*(probe@bet),-.017,.017))
            stable=take[-60:]
            xx,pp=standardize(v[stable],v[i])
            sec=ridge(xx,truth.iloc[stable].to_numpy(),np.ones(len(stable)),1.60)
            p3=float(probability_after_log_shifts(law,np.clip(sh*(pp@sec),-.017,.017)))
            rows.append(dict(horizon=h,clock=clock,day=t.day,cohort=t.cohort,n_train=len(take),issue_ns=int(issue[i]),
                 last_mature_ns=int(mature[take].max()),point_probability=p0,param_probability_sd=p1.std(ddof=1),
                 param_probability_p10=conf[0],param_probability_p50=conf[1],param_probability_p90=conf[2],
                 measurement_stress_probability_sd=p2.std(ddof=1),history_60_to_full_probability_change=abs(p3-p0),
                 weight_probability_sd=t.probability_parameter_se,family_probability_spread=t.family_prob_spread,
                 ordinary_expert_probability_spread=t.ordinary_prob_spread,market_return_sd=normalized_scale[i],
                 forecast_interval_width80=t.width80,known_iv=t.implied_volatility,known_rv=t.observed_trailing_vol,
                 forecast_brier=t.brier,forecast_crps=t.crps,abs_error=t.mae,target_maturity_ns=int(mature[i])))
    table=pd.DataFrame(rows)
    for (h,clock),g in table.groupby(['horizon','clock']):
        g=g.sort_values('day')
        feat=g[['known_iv','known_rv','ordinary_expert_probability_spread','weight_probability_sd','param_probability_sd',
                'measurement_stress_probability_sd','family_probability_spread']].to_numpy(float)
        u=g.issue_ns.to_numpy()
        m=g.target_maturity_ns.to_numpy()
        y=g.abs_error.to_numpy()
        for i in range(len(g)):
            take=past_rows(m,u,int(u[i]))
            if len(take)<MIN:
                continue
            for j,name in ((4,'IV_RV_and_weight_variation'),(5,'plus_fit_parameter_variation'),(7,'plus_family_and_measurement')):
                x,v=standardize(feat[take,:j],feat[i,:j])
                p=float(np.exp(v@ridge(x,np.log(np.maximum(.0002,y[take])),np.ones(len(take)),1.7)))
                trials.append(dict(horizon=h,clock=clock,day=g.day.iloc[i],model=name,forecast=p,actual=y[i],loss=abs(p-y[i])))
    p=pd.DataFrame(trials)
    bands=[]
    for (h,c),q in p.groupby(['horizon','clock']):
        g=q.pivot(index='day',columns='model',values='loss')
        d=g.rsub(g.IV_RV_and_weight_variation,axis=0)
        bands.append(block_intervals(d,21,1100,SEED+h).assign(horizon=h,clock=c,model=g.columns))
    write('parameter-and-source-uncertainty-cases.csv.gz',table)
    summary=table.groupby(['horizon','clock'],as_index=False).agg(n=('day','size'),probability_estimation_sd=('param_probability_sd','median'),
           weight_uncertainty_sd=('weight_probability_sd','median'),feature_stress_probability_sd=('measurement_stress_probability_sd','median'),
           training_span_sensitivity=('history_60_to_full_probability_change','median'),family_disagreement=('family_probability_spread','median'),
           future_return_sd=('market_return_sd','median'),market_interval_width=('forecast_interval_width80','median'))
    write('parameter-and-source-uncertainty-summary.csv',summary)
    write('parameter-uncertainty-warning-intervals.csv',pd.concat(bands,ignore_index=True))
    write('parameter-uncertainty-warning-cases.csv.gz',p)
    print('Separated parameter, measurement and outcome effects on',len(table),'earlier-eligible cases.',flush=True)


if __name__=='__main__':
    run()
