"""Earlier eligible GIFT quotes and reproducible opening distribution calibration."""
from .common import *
from research.nifty_forecast_v16.model import history, fit
from research.nifty_forecast_v16.data import extra_daily
from research.nifty_forecast_v16.evidence import pairs


def score(atoms,y,arithmetic=True):
    a=np.sort(np.expm1(atoms) if arithmetic else np.asarray(atoms))
    actual=float(np.expm1(y) if arithmetic else y)
    n=len(a)
    q10,q25,q50,q75,q90=np.quantile(a,[.10,.25,.50,.75,.90])
    p=float((np.count_nonzero(a>0)+.5)/(n+1))
    u=actual>0
    return dict(actual=actual,p=p,brier=(p-u)**2,log_loss=-np.log(p if u else 1-p),correct=int((p>=.5)==u),
      crps=np.abs(a-actual).mean()-a@(2*np.arange(n)-n+1)/n**2,mean=float(a.mean()),median=float(q50),
      abs_error=abs(actual-q50),mean_abs_error=abs(actual-a.mean()),sq_error=(actual-a.mean())**2,
      width=q90-q10,covered=int(q10<=actual<=q90),lo=q10,hi=q90,
      quantile_loss=float(np.mean(np.maximum((actual-np.array([q10,q25,q50,q75,q90]))*np.array([.1,.25,.5,.75,.9]),
                    (np.array([q10,q25,q50,q75,q90])-actual)*np.array([.9,.75,.5,.25,.1])))),
      interval_score=q90-q10+10*(max(q10-actual,0)+max(actual-q90,0)),
      up05=float((a>=.005).mean()),down05=float((a<=-.005).mean()),up1=float((a>=.01).mean()),down1=float((a<=-.01).mean()))


def clock_panel():
    bars=pd.read_csv(V16/'sources/normalized/gift-bars.csv.gz',low_memory=False)
    for col in ['t','last_possible_end','available']:
        bars[col]=pd.to_datetime(bars[col],utc=True,format='mixed').dt.tz_convert(IST)
    bars=bars.sort_values('t').set_index('t')
    us,_=extra_daily()
    us=us['spx']
    y=matrix('session-targets.csv',V16)
    out=[]
    for i,r in enumerate(y.itertuples()):
        d=r.Index
        prev=r.origin
        us_idx=pd.DatetimeIndex(us.available).searchsorted(stamp(d,'08:30'),side='right')-1
        us_cut=us.available.iloc[us_idx] if us_idx>=0 else pd.NaT
        for clock in GAP_CLOCKS:
            at=stamp(prev,'17:00') if clock=='prior_close' else us_cut if clock=='us_complete' else stamp(d,clock)
            if pd.isna(at) or not stamp(prev,'17:00')<=at<stamp(d,'09:00'):continue
            i1=bars.available.searchsorted(at,side='right')-1
            if i1<0:continue
            latest=bars.iloc[i1]
            age=(at-latest.last_possible_end).total_seconds()/60
            strict=20 if clock not in ('prior_close','us_complete') else 75
            # Earlier US snapshots may be from a preceding calendar date; require a quote
            # after the Indian reference close and before the observed US release cutoff.
            if age>strict or (clock not in ('prior_close','us_complete') and latest.name.strftime('%Y-%m-%d')!=d):
                continue
            if latest.last_possible_end<stamp(prev,'15:25'):continue
            key=dict(day=d,origin=prev,clock=clock,decision=at.isoformat(),latest_start=latest.name.isoformat(),
                     latest_bar_end=latest.last_possible_end.isoformat(),latest_available=latest.available.isoformat(),
                     age_minutes=age,gift=float(latest.close),official_prev=float(r.previous_close),cohort=r.cohort,
                     weekend_cash=int(pd.Timestamp(d).weekday()>=5),regular=int(r.regular_weekday),
                     final7_first2_roll=int(pd.Timestamp(d).day<=2 or pd.Timestamp(d).days_in_month-pd.Timestamp(d).day<=6),
                     gap=float(r.gap))
            for hh in ('15:15','15:30','15:40','17:00'):
                t=stamp(prev,hh)
                i0=bars.last_possible_end.searchsorted(t,side='right')-1
                if i0<0:continue
                base=bars.iloc[i0]
                # The reference and the signal have their own known-availability deadlines.
                if base.name.strftime('%Y-%m-%d')!=prev or base.available>at or base.last_possible_end>latest.last_possible_end:
                    continue
                if (t-base.last_possible_end).total_seconds()/60>25:continue
                k=hh.replace(':','')
                key['return_'+k]=float(np.log(latest.close/base.close))
                key['anchor_'+k]=float(base.close)
                key['anchor_end_'+k]=base.last_possible_end.isoformat()
            n0=bars.available.searchsorted(at-pd.Timedelta(minutes=15),side='right')-1
            if n0>=0 and 'anchor_1530' in key:
                b=bars.iloc[n0]
                if (at-b.last_possible_end).total_seconds()/60<=45 and b.last_possible_end>=stamp(prev,'15:25'):
                    key['delay15']=float(np.log(b.close/key['anchor_1530']))
            # Previous dated GIFT close before the midnight boundary is a stale overnight control.
            j0=bars.available.searchsorted(stamp(d,'00:00'),side='right')-1
            if j0>=0 and bars.index[j0]>stamp(prev,'15:30') and bars.available.iloc[j0]<=at:
                key['last_night_relative_cash']=float(np.log(latest.close/bars.close.iloc[j0]))
            key['raw_cash_level']=float(np.log(latest.close/r.previous_close))
            out.append(key)
    f=pd.DataFrame(out)
    f['cohort']=f.cohort.fillna('')
    assert pd.to_datetime(f.latest_available,utc=True,format='mixed').le(pd.to_datetime(f.decision,utc=True,format='mixed')).all()
    assert f.latest_start.str[:10].between(FIRST,FREEZE).all()
    write('gift-decision-clock.csv',f)
    return f


def run():
    register()
    d=clock_panel()
    cash=matrix('session-targets.csv',V16)
    g=cash.index.to_numpy()
    true=cash.gap.to_numpy(float)
    results=[]; atom=[]; expected=[]; fittings=[]
    groups=[('anchored_1530','return_1530'),('raw_overnight','return_1530'),('anchored_1515','return_1515'),('anchored_1540','return_1540'),
            ('anchored_1700','return_1700'),('raw_cash_level','raw_cash_level'),('last_night_move','last_night_relative_cash'),
            ('delayed_15','delay15'),('roll_guarded','return_1530'),('mapped_linear','return_1530'),('variance_scaled','return_1530'),
            ('rolling_basis','raw_cash_level')]
    for clk in GAP_CLOCKS:
        t=d[d.clock.eq(clk)].set_index('day').reindex(cash.index)
        if t.decision.notna().sum()<35:
            continue
        x=t.return_1530.to_numpy(float)
        rough_bias=(np.log(t.anchor_1530)-np.log(t.official_prev)).rolling(7,min_periods=4).median().to_numpy()
        prior_error=np.full(len(x),np.nan)
        prior_mapped=np.full(len(x),np.nan)
        for i in range(len(x)):
            past=history(g,g,true,i,np.isfinite(x),n=160)
            if len(past)<MIN or not np.isfinite(x[i]):continue
            fitter=fit(x[past,None],true[past],35.)
            prior_mapped[i]=fitter.values(x[i,None])
            prior_error[i]=true[i]-prior_mapped[i]
        for name,field in groups:
            z=t[field].to_numpy(float)
            store=np.isfinite(z)
            if name=='roll_guarded':
                store&=t.final7_first2_roll.eq(0).to_numpy()
            if name=='rolling_basis':
                z=z-rough_bias
                store&=np.isfinite(z)
            for i in np.flatnonzero(store):
                ii=history(g,g,true,i,store,n=160)
                if len(ii)<MIN:continue
                delta=true[ii]-z[ii]
                if name in ('mapped_linear','variance_scaled'):
                    if not np.isfinite(prior_mapped[i]):continue
                    eligible=ii[np.isfinite(prior_error[ii])]
                    if len(eligible)<38:continue
                    v=prior_error[eligible]
                    if name=='variance_scaled':
                        # Standardize earlier genuine out-of-sample errors with the earlier, observable offshore state.
                        # Strong shrinkage caps any conditional width adjustment.
                        cov=np.log1p(abs(x[eligible])/.005)[:,None]
                        raw=np.log(np.maximum(abs(v),.0002))
                        vol=fit(cov,raw,110.)
                        scales=np.exp(np.clip(vol.values(cov)-np.median(raw),-.6,.6))
                        k=np.log1p(abs(x[i])/.005)
                        scale=np.exp(np.clip(vol.values(np.array([k]))-np.median(raw),-.4,.4))
                        a=prior_mapped[i]+scale*np.quantile(v/scales,Q)
                    else:
                        a=prior_mapped[i]+np.quantile(v,Q)
                else:
                    if name in ('raw_cash_level','last_night_move','raw_overnight'):
                        delta=delta-np.median(delta)
                    a=z[i]+np.quantile(delta,Q)
                if name=='anchored_1530' and clk=='08:55':
                    tr=np.expm1(a)
                    expected.append(dict(day=g[i],origin=cash.origin.iloc[i],decision=t.decision.iloc[i],model=name,
                                  expected_gap=float(tr.mean()),pred_gap_std=float(tr.std(ddof=0)),expected_log_gap=float(a.mean()),
                                  forecast_log_std=float(a.std(ddof=0)),eligibility_age_min=float(t.age_minutes.iloc[i]),
                                  expected_median_gap=float(np.median(tr)),expected_up=float((tr>0).mean()),train_n=len(ii),
                                  last_matured=g[ii[-1]],matched_gift=1))
                group=cash.cohort.iloc[i]
                if pd.isna(group) or not group:continue
                k=len(atom)
                v=score(a,true[i])
                results.append(dict(law=k,day=g[i],origin=cash.origin.iloc[i],decision=t.decision.iloc[i],cutoff=clk,cohort=group,
                    model=name,age_minutes=t.age_minutes.iloc[i],roll=int(t.final7_first2_roll.iloc[i]),
                    n_train=len(ii),last_train_end=g[ii[-1]],**v))
                atom.append(a.astype(np.float32))
                if name in ('mapped_linear','variance_scaled'):
                    fitter=fit(x[ii,None],true[ii],35.)
                    fittings.append(dict(law=k,n=len(eligible),eligible_last=g[eligible[-1]],**fitter.receipt(['gift_prior_mark'])))
    pred=pd.DataFrame(results)
    ex=pd.DataFrame(expected)
    assert ex.last_matured.lt(ex.day).all()
    assert pred.last_train_end.lt(pred.day).all()
    np.savez_compressed(OUT/'opening-laws.npz',atoms=np.stack(atom),units='log gap')
    write('opening-forecasts.csv.gz',pred)
    write('opening-baseline-expectation.csv',ex)
    save('opening-fit-receipt.json',fittings)
    write('opening-timing-scores.csv',pred.groupby(['cutoff','model'],as_index=False).agg(n=('day','size'),Brier=('brier','mean'),
        CRPS=('crps','mean'),log_loss=('log_loss','mean'),accuracy=('correct','mean'),MAE=('abs_error','mean'),
        MdAE=('abs_error','median'),RMSE=('sq_error',lambda z:np.sqrt(z.mean())),coverage80=('covered','mean'),width80=('width','mean'),
        interval80=('interval_score','mean'),median_age=('age_minutes','median')))
    def refs(key,g):
        return [(m,'anchored_1530') for m in g.model.unique() if m!='anchored_1530']
    write('opening-matched.csv',pairs(pred,['cutoff'],['brier','crps','interval_score','abs_error'],refs))
    before=pred[pred.model.eq('anchored_1530')].copy()
    before['model']=before.cutoff
    def cut_refs(*_):
        return [(c,'08:55') for c in GAP_CLOCKS if c!='08:55']
    before['track']='fixed gap target'
    write('opening-clock-matched.csv',pairs(before,['track'],['brier','crps','abs_error'],cut_refs))
    main=pred[pred.cutoff.eq('08:55') & pred.model.isin(['raw_overnight','anchored_1530','mapped_linear','variance_scaled'])].copy()
    elapsed=(pd.to_datetime(main.day)-pd.to_datetime(main.origin)).dt.days
    anchors=main[main.model.eq('anchored_1530')].set_index('day').actual.abs().sort_values(ascending=False)
    mask={'all':np.ones(len(main),bool),'not_roll':main.roll.eq(0),'age_5_or_less':main.age_minutes.le(5),
          'ordinary_calendar_day':elapsed.eq(1),'after_weekend_or_holiday':elapsed.gt(1),
          **{f'excluding_largest_{k}':~main.day.isin(anchors.iloc[:k].index) for k in [5,10,20]}}
    sensitivity=pd.concat([main.loc[x].assign(screen=k) for k,x in mask.items()],ignore_index=True)
    write('opening-clock-sensitivity.csv',sensitivity.groupby(['screen','model'],as_index=False).agg(
        n=('day','size'),brier=('brier','mean'),crps=('crps','mean'),accuracy=('correct','mean'),coverage80=('covered','mean'),width80=('width','mean')))
    definitions={'positive':('p',0.),'up05':('up05',.005),'down05':('down05',-.005),'up1':('up1',.01),'down1':('down1',-.01)}
    hist=[]
    for k,(col,level) in definitions.items():
        a=pred.copy()
        a['bucket']=pd.cut(a[col],bins=np.linspace(0,1,11),include_lowest=True,labels=False)
        a['hit']=a.actual.ge(level) if 'down' not in k else a.actual.le(level)
        hist.append(a.groupby(['cutoff','model','bucket'],as_index=False).agg(n=('day','size'),prob=(col,'mean'),realized=('hit','mean')).assign(event=k))
    write('opening-calibration.csv',pd.concat(hist,ignore_index=True))
    print('Opening clocks and calibrated distributions:',len(pred),'forecasts;',len(ex),'earlier expected gaps for the post-open audit',flush=True)

if __name__=='__main__':
    run()
