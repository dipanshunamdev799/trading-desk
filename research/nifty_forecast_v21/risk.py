"""Test realized-volatility forecasts from weighted equity covariance and shared risk."""
from .common import *
from .learning import MODELS
from research.nifty_forecast_v20.modeling import block_intervals,fit_slope,weighted_store


def risk_vectors(panel,forecasts,h):
    r=panel['daily_return'];bx=panel['beta'];w=panel['weights'];daily=cash().nifty50.pct_change(fill_method=None).to_numpy(float)
    stock_risk=forecasts[f'mean{h}'][MODELS.index('pooled'),:,:,6]
    out=np.full((len(r),8),np.nan);receipts=[]
    for i in range(65,len(r)):
        q=w[i]
        if not np.isfinite(q).all():
            continue
        included=q>0
        b=q[included]
        tr=slice(i-63,i)
        raw=r[tr][:,included]
        common=daily[tr]
        beta=np.nan_to_num(bx[i,included],nan=1.)
        complete=np.where(np.isfinite(raw),raw,common[:,None]*beta)
        x=np.clip(complete,-.27,.27)
        cov=np.cov(x,rowvar=False)
        shrink=.8*cov+.2*np.diag(np.diag(cov))
        v=float(b@cov@b); d=float(np.square(b)@np.diag(cov))
        q_vol=np.sqrt(252*v)
        q_s=np.sqrt(252*b@shrink@b)
        diag=np.sqrt(252*d)
        s=stock_risk[i,included]
        recent=np.sqrt(252*np.mean((x[-15:]@b)**2))
        semi=np.sqrt(252*np.mean(np.minimum(x@b,0.)**2))
        weighted_expected_risk=np.nan_to_num(s,nan=float(np.sqrt(252*np.diag(cov))@b))@b
        relative=q_vol/max(.0001,float(np.sqrt(252*np.diag(cov))@b))
        out[i]=[q_vol,q_s,diag,recent,semi,weighted_expected_risk,relative,float(np.std(np.sqrt(252*np.diag(cov))))]
        receipts.append(dict(day=panel['days'][i],horizon=h,n_daily=len(x),last_cash=panel['days'][i-1],assets=int(included.sum()),
                            observed_stock_return_fraction=float(np.isfinite(raw).mean()),projected_common_variance=float(v/max(d,1.e-10))))
    return out,pd.DataFrame(receipts)


def score(vol,prob,actual,event):
    ratio=(actual/vol)**2
    return dict(mae=abs(vol-actual),squared_error=(vol-actual)**2,qlike=ratio-np.log(ratio)-1,
                brier=(prob-event)**2,log_loss=-np.log(np.clip(prob if event else 1-prob,.0005,1.)))


def run():
    with np.load(OUT/'component-panel.npz',allow_pickle=False) as x:
        p=dict(x.items())
    with np.load(OUT/'equity-forecast-laws.npz',allow_pickle=False) as x:
        forecasts={f'mean{h}':x[f'mean{h}'] for h in HORIZONS}
    raw=csv('protected-point-risk-cases.csv.gz',V20)
    checks={(5,'raw_iv','mae'):.037814,(5,'offshore_plus_domestic','mae'):.036469,(21,'GJR','mae'):.033179,
            (21,'GJR','qlike'):.199677,(5,'fixed_iv_rv','brier'):.152707,(21,'student_EGARCH','brier'):.172872}
    for (h,k,metric),v in checks.items():
        a=raw[raw.horizon.eq(h)&raw.model.eq(k)]
        assert abs(a[metric].mean()-v)<1.e-6
    rows=[];receipts=[];laws=[];derived=[]
    for h in HORIZONS:
        base='offshore_plus_domestic' if h==5 else 'GJR'
        risk_reference='fixed_iv_rv' if h==5 else 'student_EGARCH'
        dates=p['days']
        d=raw[raw.horizon.eq(h)&raw.model.eq(base)].set_index('day').reindex(dates)
        u=raw[raw.horizon.eq(h)&raw.model.eq(risk_reference)].set_index('day').reindex(dates)
        rt,rec=risk_vectors(p,forecasts,h)
        receipts.append(rec)
        end=p[f'end{h}'];fs=list(p['market_fields']);state=p['market_features']
        market=np.column_stack([rt,state[:,[fs.index(k) for k in ('advance','dispersion','market_sync','cross_downside','shared_iv','shared_finance')]]])
        pos=state[:,[fs.index(k) for k in ('position_level','position_change21','position_concentration')]]
        derived.append(pd.DataFrame(rt,columns=['covariance_vol','shrunk_covariance_vol','diagonal_vol','recent_proxy_vol','proxy_semivol',
                   'weighted_stock_vol','correlation_proxy','asset_vol_spread']).assign(day=dates,horizon=h))
        truth=d.actual_vol.to_numpy(float);fc=d.pred_vol.to_numpy(float);expand=u.actual_expand.to_numpy(float);pr=u.p.to_numpy(float)
        error=np.log(truth/np.maximum(fc,.01))
        for i in np.flatnonzero(d.actual_vol.notna()):
            targets=d.iloc[i];meta=dict(day=dates[i],horizon=h,origin=targets.origin,target_end=targets.target,cohort=targets.cohort,
                    cutoff='preauction_0855',actual=float(truth[i]),event=int(expand[i]))
            assert targets.target==end[i] and np.isfinite(truth[i])
            t=np.flatnonzero((end<dates[i])&(np.arange(len(dates))<i)&np.isfinite(error))[-130:]
            mean=float(np.mean(error[t])) if len(t) else 0.
            active=len(t)>=45
            overlay=lambda s:float(np.clip(.5*fit_slope(s[t],error[t],s[i],175)[0],-.25,.25)) if active else 0.
            transition=float(np.clip(.5*fit_slope(market[t],(expand-pr)[t],market[i],220)[0],-.23,.23)) if active else 0.
            candidates={base:(fc[i],pr[i],True),'iv_or_gjr_covariance':(fc[i]*np.exp(overlay(rt)),pr[i],active),
                'iv_or_gjr_cross_sectional':(fc[i]*np.exp(overlay(market)),pr[i],active),
                'iv_or_gjr_cross_sectional_plus_positions':(fc[i]*np.exp(overlay(np.c_[market,pos])),pr[i],active),
                'iv_or_gjr_bias_only':(fc[i]*np.exp(.35*mean) if active else fc[i],pr[i],active),
                'cross_sectional_transition':(fc[i],float(np.clip(pr[i]+transition,.005,.995)),active),
                'raw_stock_covariance':(rt[i,0],pr[i],True),'shrunk_stock_covariance':(rt[i,1],pr[i],True),
                'independent_equity_variance':(rt[i,2],pr[i],True),'recent_proxy_volatility':(rt[i,3],pr[i],True)}
            q=raw[raw.horizon.eq(h)&raw.day.eq(dates[i])]
            for name,old in q.set_index('model').iterrows():
                m=meta|dict(model=name,active=True,point=float(old.pred_vol),p=float(old.p),law=-1,
                             last_mature=old.last_training_end,mae=old.mae,squared_error=old.mae**2,qlike=old.qlike,brier=old.brier,log_loss=old.log_loss)
                rows.append(m)
            for name,(v,z,on) in candidates.items():
                if name==base:
                    continue
                v=float(np.clip(v,.005,2.))
                center=np.nanmedian(error[t]) if len(t)>=20 else 0.
                eps=np.quantile(error[t]-center,(np.arange(96)+.5)/96) if len(t)>=20 else np.linspace(-.54,.54,96)
                point=max(.005,v)
                lab=len(laws)
                laws.append((np.clip(point*np.exp(eps),0.,2.),np.full(len(eps),1/len(eps))))
                rows.append(meta|dict(model=name,point=point,p=float(z),active=bool(on),law=lab,last_mature=end[t[-1]] if len(t) else None,
                                     **score(point,z,truth[i],int(expand[i]))))
    data=pd.DataFrame(rows)
    write('risk-comparison-cases.csv.gz',data)
    write('risk-fit-receipts.csv',pd.concat(receipts,ignore_index=True))
    write('daily-portfolio-risk-features.csv',pd.concat(derived,ignore_index=True))
    weighted_store(OUT/'bottom-up-volatility-laws.npz',laws)
    write('risk-leaderboard.csv',pd.concat([data.assign(scope='combined'),data.assign(scope=data.cohort)]).groupby(
        ['horizon','scope','model'],as_index=False).agg(n=('day','size'),active=('active','sum'),mae=('mae','mean'),qlike=('qlike','mean'),
        brier=('brier','mean'),log_loss=('log_loss','mean'),mse=('squared_error','mean')).assign(rmse=lambda x:x.mse**.5))
    summary=[]
    for h in HORIZONS:
        chosen=data[data.horizon.eq(h)]
        base='offshore_plus_domestic' if h==5 else 'GJR'
        risk_reference='fixed_iv_rv' if h==5 else 'student_EGARCH'
        for m in ('mae','qlike','brier'):
            p0=chosen.pivot(index='day',columns='model',values=m)
            ref=risk_reference if m=='brier' else base
            d=p0.sub(p0[ref],axis=0).mul(-1)
            v=block_intervals(d.to_numpy(),21,1200,SEED+h).assign(horizon=h,metric=m,model=d.columns,reference=ref)
            summary.append(v)
    write('risk-paired-block-intervals.csv',pd.concat(summary,ignore_index=True))
    save('risk-config.json',dict(parent=list(checks),feature_basis='Up to 63 prior daily audited close returns, current guarded weights and shrunk covariance.',
          short_covariance='80% empirical, 20% diagonal. Missing historical stock legs imputed from the contemporaneous common return and prior beta.',
          target='Future realized index volatility from the unchanged V16 archived target. Terminal return variance remains a separate joint forecast quantity.',
          scores='Point estimates and event probabilities are separate. New volatility laws have 96 atoms; expansion probabilities come from the separately evaluated transition design.'))
    print('Verified six protected risk scores and tested',len(data),'risk model cases',flush=True)


if __name__ == '__main__':
    run()
