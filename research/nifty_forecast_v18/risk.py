"""Estimate event additions to point risk, expansion probabilities and coherent OHLC laws."""
from .common import *
from .aggregate import COUNT,TEXT,FUND,WEIGHT,DISAG,REACT,SCHEDULE,EXTRA
from .forecast import field_matrix,available
from research.nifty_forecast_v16.model import fit
from research.nifty_forecast_v16.paths import distance_crps
from research.nifty_forecast_v17.paths import cells,outcome,SCORECOLS
from research.nifty_forecast_v16 import paths as v16path
from research.nifty_forecast_v15.sequential import TICK,log_ticks,numpy_zip

ARMS={
 'price_volatility':('iv_type','known_iv','prior_rv','vix_level','iv_term'),
 'scheduled_risk':SCHEDULE,
 'event_counts_risk':COUNT,
 'fundamental_risk':FUND+TEXT,
 'material_events_risk':COUNT+TEXT+REACT+DISAG,
 'non_price_risk':EXTRA,
 'scheduled_then_fundamental':SCHEDULE+FUND+TEXT,
 'schedule_delayed':SCHEDULE,
}
RISK_INPUT=('known_iv','iv_prev','prior_rv','vix_level','iv_term')

def scalar_score(a,y,p,event):
    ar=np.sort(a)
    q10,q90=np.quantile(ar,[.1,.9])
    mu=ar.mean()
    ratio=(y/mu)**2
    return dict(actual=y,mean=mu,median=float(np.median(ar)),crps=float(distance_crps(ar,y)),
      abs_error=abs(mu-y),sq_error=(mu-y)**2,width=q90-q10,covered=int(q10<=y<=q90),
      qlike=ratio-np.log(ratio)-1,p=p,event=event,brier=(p-event)**2,
      log_loss=-np.log(p if event else 1.-p))

def ab0(p):
    return np.clip(p,.0005,.9995)

def conditioned(x,y,p,cut,ds,en,i,center=True):
    t=available(ds,en,i,y,cut)
    if len(t)<44:
        return 1.,0.,None,t,np.zeros(128)
    err=np.log(np.maximum(y[t],.014)/np.maximum(p[t],.03))
    shape=np.quantile(err-np.median(err),(np.arange(128)+.5)/128)
    est=fit(x[t],err,185.)
    mag=float(np.exp(np.clip(.56*est.values(x[i]),-.26,.26))) if center else 1.
    return mag,0.,est,t,shape

def after_open(v17):
    out=[]
    x=csv('event-aggregate-features.csv.gz')
    for (h,clock),q in v17.groupby(['horizon','cutoff']):
        g=x[x.cutoff.eq(clock)].set_index('day').sort_index()
        v=q[q.model.eq('cash_risk')].set_index('day').reindex(g.index)
        if v.empty or 'actual' not in v or not v.actual.notna().any():
            continue
        day=g.index.to_numpy()
        actual=v.actual.to_numpy(float)
        pred=v['mean'].to_numpy(float)
        end=v.target.fillna('9999-12-31').to_numpy()
        x0=field_matrix(g,FUND+TEXT+COUNT)
        z=v.expansion.to_numpy(float)
        base=v.p.to_numpy(float)
        for i in np.flatnonzero(np.isfinite(actual)):
            t=available(day,end,i,actual)
            if len(t)<38:continue
            err=np.log(np.maximum(actual[t],.014)/np.maximum(pred[t],.035))
            mdl=fit(x0[t],err,175.)
            scale=float(np.exp(np.clip(.52*mdl.values(x0[i]),-.20,.20)))
            tail=fit(x0[t],z[t]-base[t],190.)
            p=float(ab0(base[i]+.5*tail.values(x0[i])))
            a=actual[i]
            for m,w,r in [('V17_postopen_cash_risk',pred[i],base[i]),('postopen_event_risk',pred[i]*scale,p)]:
                qq=(a/w)**2
                out.append(dict(day=day[i],origin=v.origin.iloc[i],horizon=h,cutoff=clock,target_end=end[i],cohort=v.cohort.iloc[i],
                            last_mature=max(end[t]),model=m,parent='V17_postopen_cash_risk',actual=a,mean=w,p=r,event=z[i],
                            abs_error=abs(a-w),sq_error=(a-w)**2,qlike=qq-np.log(qq)-1,brier=(r-z[i])**2,
                            log_loss=-np.log(ab0(r) if z[i] else ab0(1-r)),law=-1))
    return out

def run():
    from .forecast import build_clock
    records=[];fitrows=[];pathrows=[];barriers=[];law=[];archive=[]
    scalefile=csv('volatility-scores.csv.gz',V16)
    references=[]
    for (h,c,m),u in scalefile.groupby(['horizon','cutoff','model']):
        if m not in ('GJR','V14_IV_GJR','fixed_iv_rv','offshore_plus_domestic','raw_iv','student_EGARCH'):continue
        references.append(u)
    write('protected-risk-predictions.csv.gz',pd.concat(references,ignore_index=True))
    v17=csv('postopen-volatility-scores.csv.gz',V17)
    if len(v17):write('protected-v17-postopen-risk.csv.gz',v17)
    file_keys={(r['horizon'],r['origin']):r for r in read('retimed-path-archive.json',V17)['files']}
    oldpaths=v16path.Paths()
    for clock in ('previous_1700','preauction_0855'):
        for h in HORIZONS:
            f,y=build_clock(clock,h)
            v=csv(f'targets-{h}.csv',V14).set_index('day').reindex(f.origin)
            v.index=f.index
            ds=f.index.to_numpy()
            cut=f.decision.str[:10].to_numpy()
            en=y['end_original'+str(h)].fillna('9999-12-31').to_numpy()
            cohort=y['cohort_'+str(h)].fillna('')
            f['prior_rv']=v.trailing_at_origin
            # Trailing realized state and same-date official files are eligible only through the original input guard.
            f['known_iv']=f.iv_prev.fillna(f.trailing_vol).fillna(.13).clip(.04,.55)
            iv=f.known_iv.to_numpy()
            vol=v.volatility.to_numpy(float)
            event=v.event_expand.fillna(0).astype(int).to_numpy()
            design={k:tuple(dict.fromkeys(RISK_INPUT+fields)) for k,fields in ARMS.items()}
            xx={k:field_matrix(f,fields) for k,fields in design.items()}
            a=field_matrix(f,RISK_INPUT)
            s=field_matrix(f,SCHEDULE)
            xx['schedule_delayed'][:,len(RISK_INPUT):]=pd.DataFrame(s).shift(10).to_numpy()
            native=scalefile[scalefile.horizon.eq(h)&scalefile.cutoff.eq('08:55')].set_index(['day','model'])
            # Point and event controls have their own archived forecasts. The previous-close IV-only control is fitted separately.
            for i in np.flatnonzero(cohort.ne('').to_numpy()):
                ori=y.origin.iloc[i]; d=ds[i]
                info=dict(horizon=h,day=d,origin=ori,cutoff=clock,cohort=cohort.iloc[i],target_end=en[i])
                mag,_,est,t,shape=conditioned(a,vol,iv,cut,ds,en,i,center=False)
                assert len(t)>=44
                state=np.log(np.maximum(vol,.014)/iv)
                expansion=v.trailing_at_origin.iloc[i]*1.25
                ctl=iv[i]*np.exp(shape+np.median(state[t])*.35)
                empir=ab0((ctl>=expansion).mean())
                raw=iv[i]*np.exp(shape)
                out={'raw_atm_same_clock':(raw,ab0((raw>=expansion).mean())),
                     'risk_calibrated_iv':(ctl,empir)}
                for m,x in xx.items():
                    mat,_,mod,tr,temp=conditioned(x,vol,iv,cut,ds,en,i,center=True)
                    ar=ctl*mat
                    q=np.log(np.maximum(iv[tr],.03)/np.maximum(v.trailing_at_origin.iloc[tr].to_numpy(float),.03))
                    baseline_q=np.clip(.3+.17*q,.06,.95)
                    pfit=fit(np.column_stack((x[tr],q)),event[tr]-baseline_q,195.)
                    now_q=np.log(iv[i]/max(.03,v.trailing_at_origin.iloc[i]))
                    p1=ab0(.3+.17*now_q+.63*pfit.values(np.r_[x[i],now_q]))
                    # Primary probabilities use a tail on the same volatility law. The offset-probability experiment is also kept.
                    out[m]=(ar,ab0((ar>=expansion).mean()))
                    sr=scalar_score(ar,vol[i],p1,event[i])
                    records.append(dict(**info,model=m+'_transition',parent='risk_calibrated_iv',law=-1,last_mature=max(en[tr]),**sr))
                    if mod is not None:
                        fitrows.append(dict(**info,model=m,n=len(tr),last_mature=max(en[tr]),scale=mat,**mod.receipt(design[m])))
                if clock=='preauction_0855':
                    for ref in ('raw_iv','GJR','fixed_iv_rv','student_EGARCH','offshore_plus_domestic','V14_IV_GJR'):
                        k=native.loc[(d,ref)]
                        assert abs(k.actual_vol-vol[i])<1.e-13 and k.actual_expand==event[i]
                        records.append(dict(**info,model='protected_'+ref,parent='protected_'+ref,law=-1,last_mature=k.last_training_end,
                         actual=k.actual_vol,mean=k.pred_vol,abs_error=k.mae,sq_error=k.mae**2,qlike=k.qlike,p=k.p,event=k.actual_expand,brier=k.brier,log_loss=k.log_loss))
                for k,(r,pr) in out.items():
                    ix=len(law)
                    law.append(r.astype(np.float32))
                    records.append(dict(**info,model=k,parent='risk_calibrated_iv',law=ix,last_mature=max(en[t]),**scalar_score(r,vol[i],pr,event[i])))
                rec=file_keys[h,ori]
                act=outcome(oldpaths,rec)
                with np.load(V17/rec['file'],allow_pickle=False) as z:
                    pa={k:z[clock+'_'+k].copy() for k in ('same_clock_IV','same_clock_GJR')}
                if clock=='preauction_0855':
                    with np.load(V16/rec['v16_reference'],allow_pickle=False) as z:
                        pa['same_clock_GIFT_first']=z['decomposed_gift'].copy()
                for k,target in [('event_scale_on_IV','same_clock_IV'),('schedule_scale_on_GJR','same_clock_GJR')]:
                    spec='scheduled_then_fundamental' if k=='event_scale_on_IV' else 'scheduled_risk'
                    shape_scaler=float(np.mean(out[spec][0])/np.mean(ctl))
                    pa[k]=log_ticks(pa[target].astype(float)*TICK*shape_scaler)
                    assert (pa[k][:,:,1]>=np.maximum(pa[k][:,:,0],pa[k][:,:,3])).all()
                    assert (pa[k][:,:,2]<=np.minimum(pa[k][:,:,0],pa[k][:,:,3])).all()
                path=OUT/'event-joint-paths'/f'{clock}-{h}-{ori}.npz'
                path.parent.mkdir(exist_ok=True)
                numpy_zip(path,{k:v for k,v in pa.items() if k.startswith(('event_','schedule_'))})
                archive.append(dict(**info,file=path.relative_to(OUT).as_posix(),sha256=sha(path),matched_parent=rec['file'],tick=TICK))
                for name,array in pa.items():
                    vals,e=cells(np.exp(array*TICK),act,h)
                    parent='same_clock_GJR' if name=='schedule_scale_on_GJR' else 'same_clock_IV'
                    pathrows.append(dict(**info,model=name,parent=parent,**{k:vals[k] for k in SCORECOLS}))
                    barriers.extend(info|dict(model=name,parent=parent)|w for w in e.to_dict('records'))
            print('Risk and path laws',clock,h,flush=True)
    records.extend(after_open(v17))
    write('event-volatility-predictions.csv.gz',pd.DataFrame(records))
    write('event-path-scores.csv.gz',pd.DataFrame(pathrows))
    write('event-barrier-scores.csv.gz',pd.DataFrame(barriers))
    np.savez_compressed(OUT/'event-volatility-laws.npz',atoms=np.stack(law))
    save('event-path-archive.json',archive)
    save('event-risk-fits.json',fitrows)
    print('Archived risk and path cohorts',len(records),len(pathrows),len(barriers),flush=True)

if __name__=='__main__':
    import sys
    if 'point_controls' not in sys.argv:
        run()
    else:
        z=csv('event-volatility-predictions.csv.gz')
        z=z[~z.model.str.startswith('protected_postopen_',na=False)&z.model.ne('raw_atm_point_same_clock')].copy()
        z.loc[z.model.eq('raw_atm_same_clock'),'model']='atm_centered_empirical_law'
        x=csv('original-feature-panel.csv.gz',V17,usecols=['day','cutoff','iv_prev','trailing_vol'])
        a=z[z.model.eq('atm_centered_empirical_law')].merge(x,on=['day','cutoff'],validate='m:1')
        a['mean']=a.iv_prev.fillna(a.trailing_vol).fillna(.13).clip(.04,.55)
        a['median']=np.nan
        a['model']='raw_atm_point_same_clock'
        a['parent']='raw_atm_point_same_clock'
        for k in ('crps','p','brier','log_loss','covered','width'):a[k]=np.nan
        a['law']=-1
        a['abs_error']=(a.actual-a['mean']).abs()
        a['sq_error']=a.abs_error**2
        ratio=(a.actual/a['mean'])**2
        a['qlike']=ratio-np.log(ratio)-1
        r=csv('protected-v17-postopen-risk.csv.gz')
        r=r.rename(columns={'mae':'abs_error','target':'target_end','expansion':'event'})
        r['model']='protected_postopen_'+r.model
        r['parent']=r.model
        r['law']=-1
        keys=list(z.columns)
        write('event-volatility-predictions.csv.gz',pd.concat([z,a.reindex(columns=keys),r.reindex(columns=keys)],ignore_index=True))
        print('Retained exact raw ATM point controls and',len(r),'archived post-open risk cases',flush=True)
