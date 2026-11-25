"""Re-evaluate original volatility benchmarks and model separately timed session risk."""
from scipy.stats import chi2
from .common import *
from .data import DOM, SETS
from .model import history, logistic_offset, predict_probability, fit
from .session_models import load, prepare


def get_components(p,h):
    g=np.log(p.open/p.close.shift()).to_numpy()
    r=np.log(p.close/p.open).to_numpy()
    k=252./h
    integrals=np.column_stack((g*g,r*r,2*g*r,(g+r)**2))
    volumes=np.stack([np.sum(integrals[i:i+h],axis=0)*k if i+h<=len(p) else np.full(4,np.nan) for i in range(1,len(p))])
    return volumes


def run():
    all_x,y_clock=load()
    p=matrix('cash-panel/cash.csv')
    days=y_clock.index.to_numpy()
    origins=y_clock.origin.to_numpy()
    new=[];fit_receipts=[]
    oldp=pd.read_csv(V15/'volatility-transition-scores.csv.gz')
    oldv=pd.read_csv(V15/'volatility-level-scores.csv')
    for h in HORIZONS:
        task='five' if h==5 else 'twentyone'
        labels=matrix(f'targets-{h}.csv',V14).reindex(origins)
        y=labels.volatility.to_numpy()
        tail=labels.trailing_at_origin.to_numpy()
        exp=(labels.event_expand.fillna(-1.).to_numpy()).astype(int)
        endpoints=y_clock['label_'+task].fillna('9999-12-31').to_numpy()
        mask=y_clock['cohort_'+task].ne('').to_numpy()
        same_dates=labels.index[mask]
        assert len(same_dates)==EXPECTED[h]
        assert np.array_equal(labels.endpoint.to_numpy()[mask],endpoints[mask])
        z=oldv[oldv.horizon.eq(h)].pivot(index='origin',columns='model',values='predicted').reindex(origins)
        z_p=oldp[oldp.horizon.eq(h)&oldp.event.eq('expand')].pivot(index='origin',columns='model',values='p').reindex(origins)
        cl=get_components(p,h)
        rr=matrix(f'features-{h}.csv',V14).reindex(origins).atm.to_numpy()
        np.testing.assert_allclose(np.sqrt(cl[mask,3]),y[mask],atol=2.e-13,rtol=0)
        groups={
            'offshore_risk':('vix_us','vix_move','vxn','us_mean','asia_mean','fx','brent'),
            'global_disagreement':('vix_move','vxn','foreign_sd','cross_sign','us_asia','equity_vix','equity_fx','oil_diverge'),
            'gift_risk':('gift_abs','cash_vs_gift','foreign_sd','vix_move','vix_us'),
            'offshore_plus_domestic':DOM+('vix_move','vxn','foreign_sd','cross_sign','fx_intraday','brent_intraday','gift_abs'),
        }
        for clk in ('08:55','09:25','10:20'):
            x=prepare(y_clock,all_x[all_x.cutoff.eq(clk)].set_index('day').reindex(y_clock.index))
            x['gift_abs']=x.gift_proxy.abs()
            y0=x.gap_visible.to_numpy()
            risk=rr.copy()
            methods=groups.copy()
            if clk!='08:55':
                methods['gap_only_adjustment']=('gap_scaled','abs_gap_scaled','cash_prefix_rv')
                methods['gap_plus_global']=('gap_scaled','abs_gap_scaled','cash_prefix_rv','vix_move','foreign_sd','us_asia','gift_abs')
                if clk=='10:20':
                    methods['gap_global_breadth']=('gap_scaled','abs_gap_scaled','cash_prefix_rv','vix_move','foreign_sd','open_breadth','open_dispersion','open_bank_lead')
            for i in np.flatnonzero(mask):
                current=days[i];origin=origins[i]
                if clk!='08:55' and not np.isfinite(y0[i]):
                    continue
                hist=history(days,endpoints,y,i,np.isfinite(rr)&np.isfinite(tail)&(exp>=0)&(np.isfinite(y0) if clk!='08:55' else True),n=185)
                if len(hist)<42:
                    continue
                sd0=risk[i]
                g_share=float(np.clip(np.mean(cl[hist,0]/np.maximum(cl[hist,3],1.e-8)),.05,1.20))
                g_mean=float(cl[hist,0].mean())
                known=float(y0[i]) if np.isfinite(y0[i]) else 0.
                base_adjust=.65*(252*known**2-g_mean)/h if clk!='08:55' else 0.
                post_simple=np.sqrt(np.clip(sd0**2+base_adjust,.55*sd0**2,1.65*sd0**2))
                forecasts={'raw_iv':(sd0,z_p.iloc[i]['iv_raw'],np.nan,np.nan),
                           'historical':(np.exp(np.mean(np.log(y[hist]))),z_p.iloc[i]['historical'],np.nan,np.nan),
                           'fixed_iv_rv':(z.iloc[i]['fixed_75IV25RV'],z_p.iloc[i]['fixed_75IV25RV'],np.nan,np.nan),
                           'GJR':(z.iloc[i]['V13_GJR'],z_p.iloc[i]['V13_GJR'],np.nan,np.nan),
                           'student_EGARCH':(z.iloc[i]['V14_EGARCH_t'],z_p.iloc[i]['V14_EGARCH_t'],np.nan,np.nan),
                           'V14_IV_GJR':(z.iloc[i]['V14_IV_GJR'],z_p.iloc[i]['V14_IV_GJR'],np.nan,np.nan)}
                cutoff=1.25*tail[i]
                if clk!='08:55':
                    forecasts['price_seen_risk_only']=(post_simple,float(chi2.sf(h*(cutoff/post_simple)**2,h)),np.nan,np.nan)
                p_train=chi2.sf(h*((1.25*tail[hist])/risk[hist])**2,h)
                for tag,cols in methods.items():
                    a=x.loc[:,list(cols)].to_numpy(float)
                    # Auxiliary targets use the two realized components and observed cross term only after the end date matures.
                    targets=np.column_stack((np.log(y[hist]/risk[hist]),
                              np.log(np.sqrt(cl[hist,0])/risk[hist]),np.log(np.sqrt(cl[hist,1])/risk[hist])))
                    models=fit(a[hist],np.clip(targets,-2.2,1.3),145)
                    values=models.values(a[i])
                    basevol=post_simple if tag.startswith('gap') else sd0
                    sd=float(basevol*np.exp(np.clip(.55*values[0],-.32,.32)))
                    pars=logistic_offset(a[hist],exp[hist].astype(float),p_train,120)
                    p1=float(predict_probability(pars,a[i],chi2.sf(h*(cutoff/basevol)**2,h),.82))
                    gr=float(sd0*np.exp(np.clip(values[1],-2.2,1.)))
                    re=float(sd0*np.exp(np.clip(values[2],-2.2,1.)))
                    forecasts[tag]=(sd,p1,gr,re)
                    if tag in ('offshore_risk','gap_plus_global','offshore_plus_domestic'):
                        fit_receipts.append(dict(horizon=h,day=current,origin=origin,target=endpoints[i],cutoff=clk,
                            model=tag,last_label_end=max(endpoints[hist].tolist()),overnight_share=g_share,
                            point=models.receipt(cols),event_coef=pars[1].tolist()))
                for name,(pred,prob,night,daytime) in forecasts.items():
                    vv=(y[i]/pred)**2
                    f0=np.clip(prob,.0005,.9995)
                    new.append(dict(horizon=h,origin=origin,day=current,cutoff=clk,target=endpoints[i],cohort=y_clock['cohort_'+task].iloc[i],
                         model=name,actual_vol=y[i],pred_vol=pred,mae=abs(y[i]-pred),qlike=vv-np.log(vv)-1,
                         actual_expand=exp[i],p=prob,brier=(prob-exp[i])**2,log_loss=-np.log(f0 if exp[i] else 1-f0),
                         first_gap_abs=abs(known) if clk!='08:55' else np.nan,actual_gap_rv=np.sqrt(cl[i,0]),
                         actual_regular_rv=np.sqrt(cl[i,1]),actual_cross=cl[i,2],pred_overnight=night,pred_regular=daytime,
                         night_mae=abs(np.sqrt(cl[i,0])-night),regular_mae=abs(np.sqrt(cl[i,1])-daytime),
                         last_training_end=max(endpoints[hist].tolist()),n_train=len(hist)))
    s=pd.DataFrame(new)
    assert s.last_training_end.lt(s.day).all() and s.pred_vol.gt(0).all()
    write('volatility-scores.csv.gz',s)
    g=s.groupby(['horizon','cutoff','model'],as_index=False).agg(n=('day','size'),realized=('actual_vol','mean'),volatility=('pred_vol','mean'),
         mae=('mae','mean'),qlike=('qlike','mean'),brier=('brier','mean'),log_loss=('log_loss','mean'),forecast_rate=('p','mean'),
         expansion_rate=('actual_expand','mean'),night_mae=('night_mae','mean'),regular_mae=('regular_mae','mean'))
    write('volatility-leaderboard.csv',g)
    save('volatility-fit-ledger.json',fit_receipts)
    # Reproduce issued benchmark probabilities on all original eligible dates and by cohort.
    tag='iv_raw'
    r=oldp[oldp.event.eq('expand')&oldp.model.isin(['historical',tag,'fixed_75IV25RV','V14_EGARCH_t'])]
    write('volatility-preserved-references.csv',r.groupby(['horizon','model'],as_index=False).agg(n=('origin','nunique'),
         brier=('brier','mean'),log_loss=('log_loss','mean'),rate=('actual','mean'),forecast_rate=('p','mean')))
    print('Session-aware risk scored',len(new),'observations',flush=True)

if __name__=='__main__':
    run()
