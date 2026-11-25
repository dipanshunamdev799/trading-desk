"""Protected point risk and coherent horizon-specific path comparisons."""
from .common import *
from .modeling import fit,matrix,timed
from .panel import CORE,CORPORATE,POSITION
from .joint import archived,paths_index,outcome_series
from research.nifty_forecast_v16 import paths as v16
from research.nifty_forecast_v17.paths import outcome
from research.nifty_forecast_v15.sequential import TICK

REFERENCE={'raw_iv','offshore_plus_domestic','GJR','student_EGARCH','fixed_iv_rv','V14_IV_GJR'}
PATHS=('same_clock_IV','same_clock_GJR')
SHIFT={5:CORPORATE['counts']+CORPORATE['structured'][:4],21:POSITION['fii_changes']+POSITION['pro_level']+POSITION['concentration']}
RISK=('iv_prev','trailing_vol','normalized_cash_vol','iv_term','iv_skew','index_futures_detail_hhi_z','count9','fund_dispersion')

def weighted_score(q,y,p,event):
    r=(y/max(.005,q))**2
    p=float(np.clip(p,.0005,.9995))
    return dict(q_like=r-np.log(r)-1,mae=abs(y-q),sq_error=(y-q)**2,brier=(p-event)**2,log_loss=-np.log(p if event else 1-p))

def recovered():
    original=csv('volatility-scores.csv.gz',V16)
    q=original[original.cutoff.eq('08:55')&original.model.isin(REFERENCE)].copy()
    keys={'raw_iv':(5,'mae',.037814),'offshore_plus_domestic':(5,'mae',.036469),'GJR':(21,'mae',.033179),
          'student_EGARCH':(21,'brier',.172872),'fixed_iv_rv':(5,'brier',.152707)}
    for m,(h,k,v) in keys.items():
        assert abs(q[q.model.eq(m)&q.horizon.eq(h)][k].mean()-v)<1.e-6
    assert abs(q[q.model.eq('GJR')&q.horizon.eq(21)].qlike.mean()-.199677)<1.e-6
    z=csv('protected-native-joint-models.csv',V19)
    assert abs(z[z.horizon.eq(21)&z.model.eq('V14_gjr_student')].range_crps.iloc[0]-.015422)<1.e-6
    y=csv('joint-path-cases.csv.gz',V19)
    assert abs(y[y.horizon.eq(5)&y.model.eq('same_clock_GIFT_first')].touch_brier.mean()-.132201)<1.e-6
    write('protected-point-risk-cases.csv.gz',q)
    write('protected-joint-benchmarks.csv',z)
    return q

def point(r,panel,targets):
    rows=[]
    for h in HORIZONS:
        q=r[r.horizon.eq(h)]
        active=panel[panel.cutoff.eq('preauction_0855')].set_index('day')
        y=targets.reindex(active.index)
        day=active.index.to_numpy(dtype='U10')
        end=y[f'end_0_{h}'].fillna('9999-12-31').to_numpy(dtype='U10')
        x=matrix(active,RISK)
        refs=('offshore_plus_domestic','fixed_iv_rv') if h==5 else ('GJR','student_EGARCH')
        for m in set(refs):
            f=q[q.model.eq(m)].set_index('day').reindex(day)
            vol=f.actual_vol.to_numpy(float)
            pred=f.pred_vol.to_numpy(float)
            prob=f.p.to_numpy(float)
            evt=f.actual_expand.to_numpy(float)
            err=np.log(np.maximum(vol,.014)/np.maximum(pred,.02))
            for i in np.flatnonzero(np.isfinite(vol)):
                t=timed(end,day,i,err)
                ok=len(t)>=38
                mv=fit(x[t],err[t],200) if ok else None
                mp=fit(x[t],evt[t]-prob[t],270) if ok else None
                level=np.exp(np.clip(.50*(mv.values(x[i])-mv.coefficient[0]),-.20,.20)) if ok else 1.
                p2=np.clip(prob[i]+.40*(mp.values(x[i])-mp.coefficient[0]),.015,.985) if ok else prob[i]
                for name,v,p1 in [(m,pred[i],prob[i]),(m+'+risk_level',pred[i]*level,prob[i]),
                                  (m+'+transition',pred[i],p2)]:
                    a=weighted_score(v,vol[i],p1,evt[i])
                    rows.append(dict(track='retained_point_risk',horizon=h,cutoff='preauction_0855',day=day[i],origin=y.origin.iloc[i],
                        target_end=end[i],cohort=f.cohort.iloc[i],model=name,parent=m,actual=vol[i],mean=v,event=int(evt[i]),p=p1,
                        active=int(ok or name==m),n_train=len(t),last_mature=max(end[t]) if len(t) else None,**a))
    write('position-and-corporate-risk-cases.csv.gz',pd.DataFrame(rows))

def transform(tick,location,scale,skew):
    log=tick.astype(float)*TICK
    phase=np.arange(1,log.shape[1]+1)[None,:,None]/log.shape[1]
    arr=log*scale*(1+skew*np.sign(log))+location*phase
    assert (arr[:,:,1]>=np.maximum(arr[:,:,0],arr[:,:,3])).all()
    assert (arr[:,:,2]<=np.minimum(arr[:,:,0],arr[:,:,3])).all()
    return np.exp(arr)

def joint(panel,targets):
    index=paths_index()
    v=v16.Paths()
    fitted=[];scores=[]
    for clock in CLOCKS:
        archive=archived(clock)
        f=panel[panel.cutoff.eq(clock)].set_index('day')
        y=targets.reindex(f.index)
        decision=f.decision.str[:10].to_numpy(dtype='U10')
        xv=matrix(f,RISK)
        iv=f.iv_prev.fillna(f.trailing_vol).fillna(.12).to_numpy(float).clip(.04,.60)
        for h in HORIZONS:
            r,end=outcome_series(y,f'0_{h}')
            lookup=csv(f'targets-{h}.csv',V14).set_index('day').reindex(f.origin)
            realized=lookup.volatility.to_numpy(float)
            rv0=lookup.trailing_at_origin.to_numpy(float)
            err_risk=np.log(np.maximum(realized,.014)/iv)
            x=matrix(f,SHIFT[h])
            errs=np.full(len(y),np.nan)
            selected=np.flatnonzero(y[f'cohort_{h}'].notna())
            for i in selected:
                a,w=archive[h,f.index[i]]
                errs[i]=r[i]-np.log1p(w@a)
            for i in selected:
                date=f.index[i]
                last=timed(end,decision,i,errs)
                rt=timed(end,decision,i,err_risk)
                m=len(last)>=38
                loc_fit=fit(x[last],errs[last],195) if m else None
                dv=.60*(loc_fit.values(x[i])-loc_fit.coefficient[0]) if m else 0.
                loc=float(np.clip(dv,-.010,.010))
                rvmod=fit(xv[rt],err_risk[rt],190)
                scale=float(np.exp(np.clip(.5*(rvmod.values(xv[i])-rvmod.coefficient[0]),-.17,.17)))
                asym=0.
                if m:
                    ee=errs[last]/max(.003,np.median(abs(errs[last])))
                    qm=fit(x[last],np.clip(ee*abs(ee),-5,5),230)
                    asym=float(np.clip(.055*(qm.values(x[i])-qm.coefficient[0]),-.10,.10))
                row=index[h,y.origin.iloc[i]]
                act=outcome(v,row)
                tag='same_clock_IV' if h==5 else 'same_clock_GJR'
                catalog={k:(k,0.,1.,0.) for k in PATHS}
                catalog.update(location_specialized=(tag,loc,1.,0.),scale_specialized=(tag,0.,scale,0.),
                               asymmetric_specialized=(tag,0.,1.,asym),coherent_all=(tag,loc,scale,asym))
                meta=dict(track='joint_path',horizon=h,cutoff=clock,day=date,origin=y.origin.iloc[i],target_end=end[i],
                          cohort=y[f'cohort_{h}'].iloc[i],anchor=y.reference_close.iloc[i],last_location_label=max(end[last]) if len(last) else None,
                          last_scale_label=max(end[rt]),risk_baseline=tag)
                with np.load(V17/row['file'],allow_pickle=False) as stored:
                    for name,(parent,lm,sc,sk) in catalog.items():
                        key=clock+'_'+parent
                        ticks=stored[key]
                        p=transform(ticks,lm,sc,sk)
                        assert p.shape==(256,h,4)
                        score=v16.output_scores(p,act,h,{},[])
                        forecast=v16.profile(p[None,...],np.empty((0,4)),h,1.)['vol'][0]
                        actual_rv=score['actual_vol']
                        danger=(forecast>1.25*rv0[i]).mean()
                        narrow=(forecast<.8*rv0[i]).mean()
                        scores.append(meta|dict(model=name,parent=parent,active=int(m or name in PATHS),expansion_brier=(danger-(actual_rv>1.25*rv0[i]))**2,
                             contraction_brier=(narrow-(actual_rv<.8*rv0[i]))**2,p_expand=danger,p_contract=narrow,**score))
                        fitted.append(meta|dict(model=name,parent_file=row['file'],parent_sha256=row['sha256'],parent_key=key,
                            transform='monotone signed shape and positive scale in log units plus a shared per-session drift across all OHLC legs',
                            simulations=256,loc=lm,scale=sc,skew=sk))
            print('Coherent risk paths',clock,h,len(selected),flush=True)
    write('coherent-risk-path-cases.csv.gz',pd.DataFrame(scores))
    write('coherent-path-law-recipes.csv.gz',pd.DataFrame(fitted))
    ref=csv('retimed-path-scores.csv.gz',V17)
    keys=['day','horizon','cutoff','model']
    a=pd.DataFrame(scores)
    q=a[a.model.isin(PATHS)].merge(ref,on=keys,suffixes=('','_protected'),validate='1:1')
    cols=('endpoint_crps','range_crps','touch_brier','integrated_brier','variance_qlike')
    error=max(q[k].sub(q[k+'_protected']).abs().max() for k in cols)
    assert len(q)==1928 and error<1.e-9,(len(q),error)
    save('risk-receipt.json',dict(exact_path_parent_cases=len(q),maximum_path_score_difference=error,cases=len(a),
          data='V16 native point and transition laws at 08:55; separate V14 native GJR archive; separate V17 retimed IV/GJR laws.',
          coherence='All path outcomes and probabilities come from the same 256 transformed OHLC scenarios. The path recipe and hash of its inherited law reproduce every simulated atom.'))

if __name__=='__main__':
    panel=csv('asof-features.csv.gz')
    targets=csv('multi-horizon-targets.csv').set_index('day')
    point(recovered(),panel,targets)
    joint(panel,targets)

