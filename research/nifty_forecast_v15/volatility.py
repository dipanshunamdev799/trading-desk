"""Chronological variance-level and transition estimation beyond the V14 replay."""
from scipy.special import expit, logit
from scipy.stats import chi2

from .common import *
from .fitting import fit

EXTRAS=('variance_gap','jump_share_5','downshare_5','breadth_change','sector_sync','term_slope',
        'vix_move','fx_shock','oil_shock','har5','har21','global_iv_gap')
EVENTS=('expand','expand50','contract','enter_high','persist_high')
TRANSFORMS={'iv_offset_intercept':(), 'iv_level':('atm',), 'iv_change_only':('atm1',),
            'iv_level_change':('atm','atm1'), 'iv_offsets_all':('atm','atm1',*EXTRAS),
            'iv_offsets_delayed':('atm','atm1',*EXTRAS), 'iv_offsets_random':('atm','atm1',*EXTRAS)}


def test_probability(event,scale,risk,hi,h):
    g1=h//2
    g2=h-g1
    if event=='persist_high':
        return chi2.sf(g1*(hi/scale)**2,g1)*chi2.sf(g2*(hi/scale)**2,g2)
    ratio={'expand':1.25*risk,'expand50':1.50*risk,'contract':.8*risk,'enter_high':hi}[event]
    s=h*(ratio/scale)**2
    return chi2.cdf(s,h) if event=='contract' else chi2.sf(s,h)


def prepare():
    p=pd.read_csv(V14/'process-risk-predictions.csv')
    p=p.pivot(index=['horizon','origin'],columns='model',values='prediction')
    q=pd.read_csv(OUT/'replay-volatility.csv').pivot(index=['horizon','origin'],columns='model',values='prediction')
    return p.join(q,rsuffix='_replay')


def run():
    rows=[]; levels=[]; fitted=[]; old=prepare()
    for h in HORIZONS:
        x=matrix(f'features-{h}.csv',V14)
        y=matrix(f'targets-{h}.csv',V14)
        th=matrix(f'thresholds-{h}.csv',V14)
        accepted=y.cohort.notna()
        y['event_expand50']=y.volatility.ge(1.5*y.trailing_at_origin).astype(float).where(y.event_expand.notna())
        aligned=x.reindex(y.index)
        scale=aligned.atm.clip(.027,.90)
        for day,row in y[accepted].iterrows():
            hist=y.index[y.endpoint.lt(day)][-185:]
            z=old.loc[h,day]
            raw=float(scale[day])
            risk0=row.trailing_at_origin
            levels_dict={
                'same_horizon_trailing':risk0,'persistence_ewma':aligned.at[day,'ewma_fast'],
                'India_VIX':aligned.at[day,'vix_level'],'iv_raw':raw,
                'fixed_75IV25RV':np.sqrt(.75*raw**2+.25*risk0**2),
                'V13_GJR':z.V13_GJR,'V14_GJR_t':z.gjr_student,'V14_GJR_IVx':z.gjr_ivx,
                'V14_EGARCH_t':z.egarch_student,'V14_IV_GJR':z.blend_gjr_iv,
            }
            # Fit volatility magnitude separately, with a fixed modest adjustment on log volatility.
            predictors=('atm','atm1',*EXTRAS)
            valid=hist[scale.loc[hist].notna()]
            tr=aligned.loc[valid,list(predictors)].to_numpy()
            gain=np.log(y.loc[valid,'volatility']/scale.loc[valid]).clip(-1.2,1.2).to_numpy()
            mm=fit(tr,gain,120)
            levels_dict['iv_level_change_risk']=raw*np.exp(np.clip(.65*mm.values(aligned.loc[day,list(predictors)].to_numpy(float)),-.40,.40))
            fitted.append(dict(horizon=h,origin=day,task='volatility_level',model='iv_level_change_risk',
                               n=len(valid),last_mature=y.loc[valid,'endpoint'].max(),**mm.receipt(predictors)))
            for model,sd in levels_dict.items():
                if np.isfinite(sd) and sd>1.2:  # India VIX uses percentage points in some source vintages.
                    sd/=100
                if not np.isfinite(sd) or sd<=0:
                    continue
                ratio=(row.volatility/sd)**2
                levels.append(dict(horizon=h,origin=day,target=row.endpoint,cohort=row.cohort,model=model,
                               predicted=sd,actual=row.volatility,mae=abs(sd-row.volatility),qlike=ratio-np.log(ratio)-1,
                               vol_change_mae=abs((sd-risk0)-(row.volatility-risk0))))
            for event in EVENTS:
                actual=row['event_'+event]
                if pd.isna(actual):
                    continue
                use=hist[y.loc[hist,'event_'+event].notna()&scale.loc[hist].notna()&
                         th.loc[hist,'high_risk'].notna()]
                ye=y.loc[use,'event_'+event].to_numpy()
                prior=(ye.sum()+.75)/(len(ye)+1.5)
                # Preserve the reproduction control with fold-month fit; compare it with daily-matured updates.
                month=y[accepted & y.index.str.startswith(day[:7])].index[0]
                hist0=y[y.endpoint.lt(month)].tail(185)['event_'+event].dropna()
                forecasts={'hist_daily':prior,'historical':(hist0.sum()+.75)/(len(hist0)+1.50)}
                for model,sd in levels_dict.items():
                    if sd>1.2:
                        sd/=100
                    if np.isfinite(sd) and sd>0.:
                        forecasts[model]=float(test_probability(event,sd,risk0,th.at[day,'high_risk'],h))
                p0=forecasts['iv_raw']
                if len(use)>=23:
                    base=test_probability(event,scale.loc[use].to_numpy(),y.loc[use,'trailing_at_origin'].to_numpy(),
                                          th.loc[use,'high_risk'].to_numpy(),h)
                    rawlog=logit(np.clip(base,.008,.992))
                    # Newton ridge on a log-odds offset. Intercept-only separates pure calibration from fresh predictors.
                    for model,cols in TRANSFORMS.items():
                        a=aligned.loc[use,list(cols)].to_numpy()
                        c=aligned.loc[day,list(cols)].to_numpy(float)
                        if model.endswith('delayed'):
                            shifted=aligned[list(cols)].shift(5)
                            a=shifted.loc[use].to_numpy()
                            c=shifted.loc[day].to_numpy(float)
                        s=fit(a,ye,115)
                        t=(np.where(np.isfinite(a[:,s.active]),a[:,s.active],s.median)-s.center)/s.sd
                        current=(np.where(np.isfinite(c[s.active]),c[s.active],s.median)-s.center)/s.sd
                        a=np.column_stack((np.ones(len(t)),t.clip(-5,5)))
                        current=np.r_[1.,current.clip(-5,5)]
                        rng=np.random.default_rng(SEED+h*10000+int(day.replace('-','')))
                        if model.endswith('random'):
                            orders=np.array_split(np.arange(len(a)),max(2,len(a)//10))
                            a[:,1:]=a[np.concatenate([orders[j] for j in rng.permutation(len(orders))]),1:]
                        reg=np.diag([18.]+[85.]*(a.shape[1]-1))
                        b=np.zeros(len(current))
                        for _ in range(8):
                            p=expit(rawlog+a@b)
                            denom=p*(1-p)
                            b-=np.linalg.solve((a.T*denom)@a+reg,a.T@(p-ye)+reg@b)
                        val=expit(logit(np.clip(p0,.008,.992))+.8*current@b)
                        forecasts[model]=float(val)
                        receipt=s.receipt(cols)
                        receipt['parameters']=b.tolist()
                        fitted.append(dict(horizon=h,origin=day,task=event,model=model,last_mature=y.loc[use,'endpoint'].max(),
                                           n=len(use),**receipt))
                    forecasts['iv_frequency_mix']=.88*p0+.12*prior
                for model,p in forecasts.items():
                    prob=np.clip(p,.0005,.9995)
                    rows.append(dict(horizon=h,origin=day,target=row.endpoint,cohort=row.cohort,event=event,model=model,actual=actual,p=p,
                                brier=(p-actual)**2,log_loss=-np.log(prob if actual else 1-prob)))
    v=pd.DataFrame(rows)
    a=pd.DataFrame(levels)
    assert all(z['last_mature']<z['origin'] for z in fitted)
    ref=pd.read_csv(OUT/'replay-expansion.csv')
    rep=v[v.event.eq('expand')].merge(ref,on=['horizon','origin','model'],suffixes=('','_benchmark'))
    np.testing.assert_allclose(rep.p,rep.p_benchmark,atol=1.e-12)
    write('volatility-transition-scores.csv.gz',v)
    write('volatility-level-scores.csv',a)
    save('volatility-transition-fit-ledger.json',fitted)
    vals=v.merge(v[v.model.eq('iv_raw')][['horizon','origin','event','brier','log_loss']],
                 on=['horizon','origin','event'],suffixes=('','_iv'))
    vals['brier_gain']=vals.brier_iv-vals.brier
    vals['log_loss_gain']=vals.log_loss_iv-vals.log_loss
    calib=vals.groupby(['horizon','event','model'],as_index=False).agg(n=('actual','size'),p=('p','mean'),actual_rate=('actual','mean'),
                      brier=('brier','mean'),log_loss=('log_loss','mean'),brier_gain=('brier_gain','mean'),log_loss_gain=('log_loss_gain','mean'))
    write('volatility-transition-evidence.csv',calib)
    write('volatility-level-evidence.csv',a.groupby(['horizon','model'],as_index=False).agg(n=('mae','size'),
          forecast_vol=('predicted','mean'),true_vol=('actual','mean'),mae=('mae','mean'),qlike=('qlike','mean')))
    print('Scored',len(v),'transition probabilities and',len(a),'volatility levels',flush=True)


if __name__=='__main__':
    run()
