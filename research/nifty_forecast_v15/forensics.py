"""Evaluate matured-error diagnostics and publish standalone stress scenarios."""
from collections import Counter

from scipy.special import expit, logit

from .common import *
from .fitting import fit
from .data import Daily


MECH=('breadth_change','f_resid_change','sector_sync','atm1','vrp','variance_gap','term_slope','e_impact','vix_move')
MARGINALS={'endpoint_return','range','volatility'}
SCENARIOS={
    'sustained_upside':dict(daily=(.007,.008,.007,.006,.005),gaps=(.001,.002,0.,.001,.001),intraday=.004,
        note='Repeated net buying and broad participation. Smaller gains persist after the first week.'),
    'sustained_downside':dict(daily=(-.009,-.007,-.008,-.006,-.004),gaps=(-.001,-.003,0.,-.002,-.001),intraday=.005,
        note='Repeated selling across the index. Direction persists after the first week, with weaker daily drift.'),
    'sudden_risk_expansion':dict(daily=(-.021,.019,-.017,.011,.003),gaps=(-.008,.008,-.006,.004,0.),intraday=.011,
        note='Two-sided intraday price movement and rapid short-tenor repricing.'),
    'large_opening_gap':dict(daily=(-.016,.003,.006,.002,-.003),gaps=(-.035,.001,.003,0.,-.001),intraday=.006,
        note='A large lower opening gap partly closes within the first regular session.'),
    'broad_market_reversal':dict(daily=(-.016,-.009,.018,.017,.009),gaps=(-.004,-.003,.006,.004,.002),intraday=.006,
        note='Early selling and a later breadth reversal produce a two-sided path.'),
    'concentration_breakdown':dict(daily=(.005,-.023,-.016,-.004,.004),gaps=(.001,-.009,-.007,-.002,.001),intraday=.007,
        note='A few index leaders weaken together before the wider index stabilizes.'),
    'persistent_high_risk':dict(daily=(.019,-.020,.018,-.017,.015),gaps=(.005,-.007,.005,-.004,.003),intraday=.012,
        note='Alternating directional moves and large intraday swings remain present after the first week.'),
    'foreign_shock':dict(daily=(-.028,-.013,.011,.006,.003),gaps=(-.024,-.010,.008,.002,.001),intraday=.010,
        note='An overseas repricing reaches NIFTY primarily through the next opening gaps.'),
}


def causal_errors():
    data=Daily.load()
    b=pd.read_csv(V14/'path-marginals.csv.gz',usecols=['horizon','origin','cohort','model','target','predicted_mean',
                  'q10','q50','q90','actual','p_up','interval_score80'])
    b=b[b.target.isin(MARGINALS)]
    point=pd.read_csv(V14/'process-risk-predictions.csv').pivot(index=['horizon','origin'],columns='model',values='prediction')
    refs=pd.read_csv(V14/'endpoint-attribution.csv',usecols=['horizon','origin','model','p_up'])
    e=[]; info=[]
    utable=read('joint-update-receipts.json')
    # Use only the issue checkpoint for disagreements and analogue availability.
    diag={(q['horizon'],q['origin']):q for q in utable if q['checkpoint']==0}
    for h,model in PREDECESSOR_PATH.items():
        y=data.labels[h]
        gp=b[b.horizon.eq(h) & b.model.eq(model)].copy()
        g0=gp[gp.target.eq('range')].set_index('origin').sort_index()
        risks=point.loc[h].reindex(g0.index)
        loc=refs[refs.horizon.eq(h)].pivot(index='origin',columns='model',values='p_up').reindex(g0.index)
        x=data.features.reindex(g0.index)[list(MECH)].copy()
        x['risk_disagreement']=risks.std(axis=1)
        x['endpoint_disagreement']=loc.std(axis=1)
        x['analogue_ess']=[diag[h,day]['analogue_ess'] for day in x.index]
        surprise=np.log(g0.actual.clip(.0001)/g0.predicted_mean.clip(.0001))
        x['feature_shift']=x[list(MECH)].divide(x[list(MECH)].shift().rolling(60,min_periods=22).std().clip(.0001)).abs().mean(axis=1)
        x['risk_parameter_shift']=risks.gjr_student.pct_change(5,fill_method=None)
        for target,g in gp.groupby('target'):
            z=g.set_index('origin').sort_index()
            endpoints=y.loc[z.index,'endpoint']
            assert len(z)==EXPECTED[h]
            scale=((z.q90-z.q10)/2).clip(.0001)
            error=(z.actual-z.q50)/scale
            f0=(z.actual<z.q10).astype(int)
            f1=(z.actual>z.q90).astype(int)
            for day,row in z.iterrows():
                avail=endpoints[endpoints.lt(day)].index[-120:]
                recent=avail[-12:]
                if len(avail)<25:
                    continue
                hold=x.loc[avail]
                now_x=x.loc[day]
                # Lagged features are independently reconstructed for each training forecast as well.
                def augment(days):
                    out=[]
                    for t in days:
                        prior=endpoints[endpoints.lt(t)].index[-12:]
                        vals=error.loc[prior]
                        rz=surprise.loc[prior]
                        out.append([vals.mean(),vals.abs().mean(),rz.mean(),(vals>1).mean(),(vals< -1).mean()])
                    return np.array(out)
                a=np.column_stack((hold,augment(avail)))
                c=np.r_[now_x.to_numpy(),augment([day])[0]]
                ratio_scale=float(scale[day])
                for side,label in [('underestimated_upper',f1),('overestimated_lower',f0)]:
                    ya=label.loc[avail].to_numpy()
                    truth=int(label[day])
                    freq=(ya.sum()+1)/(len(ya)+10)
                    recent_rate=(label.loc[recent].sum()+1)/(len(recent)+10)
                    fm=fit(a,ya-freq,170)
                    q=np.clip(freq+.60*float(fm.values(c)),.02,.80)
                    scores={'nominal_fixed':.10,'matured_frequency':freq,'recent_frequency':recent_rate,
                            'causal_error_features':q}
                    for name,p in scores.items():
                        e.append(dict(horizon=h,origin=day,target_date=endpoints[day],cohort=row.cohort,variable=target,
                            task=side,model=name,prob=p,actual=truth,brier=(p-truth)**2,
                            log_loss=-np.log(p if truth else 1-p),last_mature=endpoints.loc[avail].max(),n=len(avail),
                            interval_score=np.nan,covered=np.nan,width=np.nan))
                    info.append(dict(horizon=h,origin=day,variable=target,task=side,last_mature=endpoints.loc[avail].max(),
                        **fm.receipt([*x.columns,'recent_standard_error','recent_abs_error','recent_range_surprise',
                                      'recent_upper_error','recent_lower_error'])))
                # Re-center over the archived median using the matured residual quantiles. Archive asymmetric and width-only estimates.
                ev=error.loc[avail].clip(-6,6)
                lo,hi=np.quantile(ev,[.1,.9])
                sw=np.quantile(ev.abs(),.80)
                if target=='endpoint_return':
                    truth=int(row.actual>0)
                    actual_up=(z.actual.loc[avail]>0).to_numpy()
                    prior_mean=(actual_up.sum()+2.)/(len(actual_up)+4.)
                    prior_predictions=z.loc[avail,'p_up'].to_numpy()
                    past_gap=float(np.mean(actual_up-prior_predictions))
                    ps={'original_direction':row.p_up,'probability_shrink':.80*row.p_up+.20*prior_mean,
                        'matured_direction_bias':np.clip(row.p_up+.55*past_gap,.005,.995)}
                    for name,p in ps.items():
                        p=np.clip(p,.0005,.9995)
                        e.append(dict(horizon=h,origin=day,target_date=endpoints[day],cohort=row.cohort,variable=target,
                            task='direction',model=name,prob=p,actual=truth,brier=(p-truth)**2,
                            log_loss=-np.log(p if truth else 1-p),last_mature=endpoints.loc[avail].max(),n=len(avail),
                            interval_score=np.nan,covered=np.nan,width=np.nan))
                bounds={
                    'original_interval':(row.q10,row.q90),
                    'asymmetric_error_quantiles':(row.q50+ratio_scale*(.45*lo-.55),row.q50+ratio_scale*(.45*hi+.55)),
                    'width_only':(row.q50-ratio_scale*(.45*sw+.55),row.q50+ratio_scale*(.45*sw+.55)),
                }
                for name,(a0,a1) in bounds.items():
                    if target!='endpoint_return':
                        a0=max(0.,a0)
                    q=a1-a0+10*(max(0.,a0-row.actual)+max(0.,row.actual-a1))
                    e.append(dict(horizon=h,origin=day,target_date=endpoints[day],cohort=row.cohort,variable=target,
                        task='interval80',model=name,prob=np.nan,actual=row.actual,brier=np.nan,log_loss=np.nan,
                        last_mature=endpoints.loc[avail].max(),n=len(avail),interval_score=q,
                        covered=int(a0<=row.actual<=a1),width=a1-a0))
    e=pd.DataFrame(e)
    assert e.last_mature.lt(e.origin).all()
    write('causal-error-scores.csv.gz',e)
    save('causal-error-fit-ledger.json',info)
    groups=['horizon','variable','task','model']
    summary=e.groupby(groups,as_index=False).agg(cases=('n','size'),brier=('brier','mean'),log_loss=('log_loss','mean'),
                                           width=('width','mean'),coverage=('covered','mean'),interval_score=('interval_score','mean'))
    write('causal-error-evidence.csv',summary)


def stress():
    path=[]; profiles=[]
    for name,z in SCENARIOS.items():
        for h in HORIZONS:
            closes=[1.]; last=1.; highs=[]; lows=[]; gaps=[]
            for j in range(h):
                n=j%5
                fac=1. if j<5 else .83 if name=='persistent_high_risk' else .53
                gap=z['gaps'][n]*fac
                o=last*np.exp(gap)
                c=last*np.exp(z['daily'][n]*fac)
                a=max(o,c)*np.exp(z['intraday']*fac)
                b=min(o,c)*np.exp(-z['intraday']*fac)
                path.append(dict(scenario=name,horizon=h,session=j+1,open=o,high=a,low=b,close=c,assumption=z['note']))
                closes.append(c)
                highs.append(a)
                lows.append(b)
                gaps.append(abs(gap))
                last=c
            ret=np.diff(np.log(closes))
            profiles.append(dict(scenario=name,horizon=h,endpoint=closes[-1]-1.,
                 volatility=np.sqrt(252*np.mean(ret**2)),range=max(highs)-min(lows),gap=max(gaps),
                 drawdown=np.min(closes/np.maximum.accumulate(closes)-1.)))
    write('scenario-paths.csv',pd.DataFrame(path))
    s=pd.DataFrame(profiles)
    write('scenario-envelope.csv',s)
    failures=pd.read_csv(V14/'failure-casebook.csv')
    assert len(failures)==712
    by=failures.groupby(['horizon','kind']).agg(rows=('origin','size'),origins=('origin','nunique'),
        worst=('loss','max'),first=('origin','min'),last=('origin','max')).reset_index()
    write('severe-error-inventory.csv',by)
    fields=['endpoint','volatility','range','gap','drawdown']
    cases=failures.drop_duplicates(['horizon','origin']).copy()
    obs=['realized_endpoint_return','realized_volatility','realized_range','realized_max_gap','realized_drawdown']
    rho=[]
    for h,g in cases.groupby('horizon'):
        a=s[s.horizon.eq(h)].set_index('scenario')
        m=a[fields].to_numpy()
        z=g[obs].to_numpy()
        unit=np.array([.03,.10,.035,.012,.025])*np.array([np.sqrt(h/5),1,np.sqrt(h/5),1,np.sqrt(h/5)])
        fit0=np.linalg.norm((z[:,None,:]-m[None,:,:])/unit,axis=2)/np.sqrt(len(unit))
        idx=np.argmin(fit0,axis=1)
        all_within=np.all((z>=m.min(axis=0))&(z<=m.max(axis=0)),axis=1)
        adverse=np.column_stack([z[:,0]>=m[:,0].min(),z[:,0]<=m[:,0].max(),z[:,1]<=m[:,1].max(),
                         z[:,2]<=m[:,2].max(),z[:,3]<=m[:,3].max(),z[:,4]>=m[:,4].min()])
        for j,origin in enumerate(g.origin):
            rho.append(dict(horizon=h,origin=origin,nearest_scenario=a.index[idx[j]],distance=fit0[j,idx[j]],
                  entire_box=int(all_within[j]),stress_maxima_cover=int(adverse[j].all()),**dict(zip(fields,z[j]))))
    match=pd.DataFrame(rho)
    write('scenario-severe-error-coverage.csv',match)
    save('forensics-receipt.json',dict(severe_record_count=len(failures),unique_windows=len(cases),scenarios=len(SCENARIOS),
       descriptive_matches=match.groupby('horizon').agg(n=('origin','size'),entire_box=('entire_box','sum'),
         stress_maxima_cover=('stress_maxima_cover','sum'),typical_distance=('distance','median')).reset_index().to_dict('records'),
       scenario_priors='Hypothetical relative OHLC paths. Descriptive severity and similarity only.'))


if __name__=='__main__':
    causal_errors()
    stress()
    print('Finished causal error diagnostics and eight transparent stress families',flush=True)
