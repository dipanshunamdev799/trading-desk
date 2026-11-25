"""Native-clock mechanism, coherent residual and activation tests."""
from .common import *
from .panel import POSITION,CORPORATE,MONTHLY,WEEKLY,cash,dedup
from .modeling import fit,matrix,timed,variant_matrix,blend_laws,direction_weights,logit_shift,sample_law,weighted_store
from research.nifty_forecast_v17.weekly import evaluate
from research.nifty_forecast_v19.forecast import POSITION as V19_POSITION,INNOV as V19_INNOV
from research.nifty_forecast_v18.forecast import COUNT,FUND

def native_books():
    z=csv('v18-native-exact-replay.csv',V19).set_index(['horizon','day','model'])
    w=np.load(V19/'v18-native-replayed-laws.npz',allow_pickle=False)
    a,b,o=[w[x] for x in ('atoms','weights','offsets')]
    laws={}
    for i,r in z.iterrows():
        k=int(r.law_index)
        laws[i]=(a[o[k]:o[k+1]],b[o[k]:o[k+1]])
    return laws

def magnitude(a,w,delta,scale=1.,skew=0.):
    x=np.log1p(a)
    center=float(w@x)
    err=x-center
    adjusted=center+delta+err*scale*(1+skew*np.sign(err))
    return np.expm1(adjusted),w

def build_design(f,h):
    if h==5:
        m={**CORPORATE,'corporate_v18_feature_set':COUNT+FUND,'positioning_only':V19_POSITION+V19_INNOV,
           'corporate_plus_positioning':dedup(COUNT+FUND+V19_POSITION+V19_INNOV)}
        m['corporate_robust_market']=dedup(CORPORATE['counts']+CORPORATE['structured']+CORPORATE['price_reaction']+WEEKLY[:6])
        anchor='corporate_v18_feature_set'
    else:
        m={**POSITION,'positions_v19_feature_set':V19_POSITION+V19_INNOV,
           'changes_plus_analogue':POSITION['fii_changes']+POSITION['new_innovations'],
           'positions_and_market_state':dedup(V19_POSITION+V19_INNOV+MONTHLY[:8])}
        anchor='positions_v19_feature_set'
    x={k:matrix(f,v) for k,v in m.items()}
    dates=cash().index
    aged=variant_matrix(f,m[anchor],dates,ages=('lag1','lag3','lag5','lag10','lag21','smooth5'))
    for k,v in aged.items():
        x[k]=v
        m[k]=m[anchor]
    return x,m,anchor

def training_delta(x,response,r,pool,cap,shrink=.58,penalty=175,mode='location'):
    if len(pool)<38 or not np.isfinite(x[r]).any():
        return 0.,None
    md=fit(x[pool],response[pool],penalty)
    if not len(md.active):return 0.,None
    dv=md.values(x[r])
    if mode=='slopes':dv-=md.coefficient[0]
    return float(np.clip(dv*shrink,-cap,cap)),md

def activity_rank(x,i,past):
    hist=x[past];v=x[i]
    hist=hist[np.isfinite(hist)]
    return ((hist<v).sum()+.5)/(len(hist)+1.) if len(hist)>=20 and np.isfinite(v) else np.nan

def run():
    p=csv('asof-features.csv.gz')
    date=cash().index
    y0=csv('multi-horizon-targets.csv').set_index('day')
    f=p[p.cutoff.eq('preauction_0855')].set_index('day')
    e=p[p.cutoff.eq('previous_1700')].set_index('day').reindex(f.index)
    y=y0.reindex(f.index)
    arc=native_books()
    verified=csv('native-audit-cases.csv.gz').query("track == 'parent_replay'").set_index(['horizon','day','model'])
    out=[];fit_notes=[];regimes=[];laws=[];notes=[]
    d=f.index.to_numpy(dtype='U10');cut=f.decision.str[:10].to_numpy(dtype='U10')
    for h in HORIZONS:
        group=f'cohort_{h}'
        r=y[f'return_0_{h}'].to_numpy(float)
        end=y[f'end_0_{h}'].fillna('9999-12-31').to_numpy(dtype='U10')
        ids=np.flatnonzero(y[group].notna())
        x,design,anchor=build_design(f,h)
        x['preceding_evening']=matrix(e,design[anchor])
        design['preceding_evening']=design[anchor]
        err=np.full(len(y),np.nan)
        event_prob=np.full(len(y),np.nan)
        gates=np.full((len(y),8),np.nan)
        realized_gains=np.full(len(y),np.nan)
        yescorp=h==5
        for i in ids:
            a,w=arc[h,d[i],'V14_exact']
            err[i]=r[i]-np.log1p(w@a)
            event_prob[i]=w@(a>0)
        cap=.009 if h==5 else .012
        for i in ids:
            date_=d[i]
            a,w=arc[h,date_,'V14_exact']
            ac,wc=arc[h,date_,'V14_event_overlay']
            row=verified.loc[h,date_]
            # V19's exact scored distributions for both original comparisons are indexed independently.
            v19m=row.loc['V14_plus_positions']
            actual=np.expm1(r[i])
            past=timed(end,cut,i,err)
            stable_hist=np.flatnonzero(d<d[i])[-100:]
            activated=len(past)>=38
            age_ok=f.source_release.iloc[i]<=f.decision.iloc[i]
            assert age_ok
            parent_score=evaluate(a,w,actual)
            bias=float(np.clip(.58*np.mean(err[past]),-cap,cap)) if activated else 0.
            moves={}
            compare={
              'exact_v14':(a,w,True,0.,1.,0.,'exact_v14'),
              'v18_corporate_native':(ac,wc,True,float(row.loc['V14_event_overlay','shift']),1.,0.,'exact_v14'),
              'v19_position_native':(*magnitude(a,w,float(v19m['shift'])),bool(v19m.active),float(v19m['shift']),1.,0.,'exact_v14'),
              'bias_only':(*magnitude(a,w,bias),activated,bias,1.,0.,'exact_v14'),
            }
            latest={}
            for name,z in x.items():
                t=past[np.isfinite(z[past]).any(axis=1)]
                dv,md=training_delta(z,err,i,t,cap)
                moves[name]=(dv,md,t)
                compare[name]=(*magnitude(a,w,dv),md is not None,dv,1.,0.,'exact_v14')
                if md is not None:
                    assert max(end[t])<cut[i]
                    latest[name]=max(end[t])
                    if name==anchor or (i in ids[::9]):
                        fit_notes.append(dict(horizon=h,model=name,day=date_,n=len(t),last_mature=latest[name],
                                              used_first=d[t[0]],**md.receipt(design[name])))
            dv,base,t=moves[anchor]
            okay=base is not None
            z=x[anchor]
            if okay:
                slope=float(np.clip(.58*(base.values(z[i])-base.coefficient[0]),-cap,cap))
                scaled,m2=training_delta(z,err,i,t,cap,mode='slopes')
                assert abs(slope-scaled)<1.e-12
                fold=t[-70:]
                short,_=training_delta(z,err,i,fold,cap)
                newest=set(d[t[-21:]])
                te=np.array([k for k in t if d[k] not in newest],int)
                omitted,m3=training_delta(z,err,i,te,cap)
                gap=(pd.Timestamp(cut[i])-pd.Timedelta(days=8)).date().isoformat()
                e_tr=t[end[t]<gap]
                embargo,m4=training_delta(z,err,i,e_tr,cap)
                size=np.maximum(abs(err[t]),.001)
                v=fit(z[t],np.log(size),210)
                logscale=.45*(v.values(z[i])-v.coefficient[0])
                mul=float(np.exp(np.clip(logscale,-.20,.20)))
                asym=fit(z[t],np.clip(np.sign(err[t])*size/np.median(size),-4,4),220)
                skew=float(np.clip(.16*(asym.values(z[i])-asym.coefficient[0]),-.13,.13))
                biaslog=np.clip(event_prob[t],.018,.982)
                flag=(r[t]>0).astype(float)
                prober=fit(z[t],flag-biaslog,240.)
                dp=float(np.clip(.6*prober.values(z[i]),-.12,.12))
                new_p=np.clip(event_prob[i]+dp,.02,.98)
            else:
                slope=short=omitted=embargo=skew=0.
                mul=1.;new_p=event_prob[i]
                m3=m4=None
            risk_only=magnitude(a,w,0.,mul)
            asy_only=magnitude(a,w,0.,1.,skew)
            combo=magnitude(a,w,dv,mul,skew)
            translated=magnitude(a,w,dv)
            half=magnitude(a,w,.5*dv)
            compare |={
               'slopes_without_intercept':(*magnitude(a,w,slope),okay,slope,1.,0.,'exact_v14'),
               'short_training70':(*magnitude(a,w,short),okay and len(t)>=38,short,1.,0.,'exact_v14'),
               'omit_latest_21_training_origins':(*magnitude(a,w,omitted),m3 is not None,omitted,1.,0.,'exact_v14'),
               'eight_calendar_day_embargo':(*magnitude(a,w,embargo),m4 is not None,embargo,1.,0.,'exact_v14'),
               'scale_only':(*risk_only,okay,0.,mul,0.,'exact_v14'),
               'asymmetry_only':(*asy_only,okay,0.,1.,skew,'exact_v14'),
               'location_scale_asymmetry':(*combo,okay,dv,mul,skew,'exact_v14'),
               'probability_only':(a,direction_weights(a,w,new_p),okay,0.,1.,0.,'exact_v14'),
               'fixed_half_shift':(*half,okay,.5*dv,1.,0.,'exact_v14'),
               'fixed_half_law_mixture':(*blend_laws(a,w,*translated,.5),okay,.5*dv,1.,0.,'exact_v14'),
            }
            vol=f.iv_prev.iloc[i]
            announce=activity_rank(f.count9.to_numpy(float),i,stable_hist)
            crowd=activity_rank(f.index_futures_detail_hhi_z.to_numpy(float),i,stable_hist)
            volatility=activity_rank(f.iv_prev.to_numpy(float),i,stable_hist)
            trend=activity_rank(f.prior_ret21.to_numpy(float),i,stable_hist)
            distilled=evaluate(*translated,actual)
            age_price=bool(f.days_to_expiry.iloc[i]<=3 or f.roll_event.iloc[i]==1)
            dist=float(np.nanmean(abs((z[i,base.active]-base.center)/base.sd))) if okay else np.nan
            if okay:
                dist=np.nan if not np.isfinite(dist) else dist
            fit_stability=abs(dv-short) if okay else np.nan
            gates[i]=[announce,crowd,volatility,trend,abs(dv),dist,len(t),fit_stability]
            gate_good=announce>=.70 if yescorp else (crowd>=.48 and volatility<=.82 and not age_price)
            eligible=t if okay else t[:0]
            known=timed(end,cut,i,realized_gains)
            loss=parent_score['brier']-distilled['brier']
            realized_gains[i]=loss if okay else np.nan
            m=fit(gates[known],realized_gains[known],260.) if len(known)>=40 else None
            predicted_gain=float(m.values(gates[i])) if m is not None else 0.
            do=okay and m is not None and predicted_gain>.001
            chosen=float(np.clip((np.mean(realized_gains[known])+.015)/.05,0,.75)) if len(known)>=40 else 0.
            compare|={
             'predeclared_activation':(*translated,True,dv,1.,0.,'exact_v14') if okay and gate_good else (a,w,False,0.,1.,0.,'exact_v14'),
             'learned_activation':(*translated,True,dv,1.,0.,'exact_v14') if do else (a,w,False,0.,1.,0.,'exact_v14'),
             'learned_history_law_mixture':(*blend_laws(a,w,*translated,chosen),okay and chosen>0,chosen*dv,1.,0.,'exact_v14'),
            }
            regimes.append(dict(horizon=h,day=date_,cohort=y[group].iloc[i],target_end=end[i],active=okay,eligible_past=len(t),
              near_expiry_or_roll=age_price,announcement_rank=announce,concentration_rank=crowd,volatility_rank=volatility,
              trend_rank=trend,feature_distance=dist,shift_uncertainty_proxy=fit_stability,model_disagreement=abs((wc @ (ac>0))-event_prob[i]),
              source_complete=int(np.isfinite(z[i]).sum()),training_weight=chosen,learned_gain=predicted_gain,
              v19_brier_gain=parent_score['brier']-float(v19m.brier),v19_crps_gain=parent_score['crps']-float(v19m.crps),
              mechanism_brier_gain=loss,mechanism_crps_gain=parent_score['crps']-distilled['crps'],
              FII_level=f.FII_index_futures_level.iloc[i],IV=vol,rolling_return=f.prior_ret21.iloc[i],
              derivative_oi=f.ordinary_oi.iloc[i],basis=f.front_basis.iloc[i]))
            for name,(a1,w1,act,dv1,mul1,skew1,pr) in compare.items():
                val=evaluate(a1,w1,actual)
                laws.append((a1,w1))
                out.append(dict(track='native',horizon=h,cutoff=NATIVE,decision=date_+'T09:10:00+05:30',snapshot=f.decision.iloc[i],
                  origin=f.origin.iloc[i],day=date_,target_end=end[i],cohort=y[group].iloc[i],reference_close=y.reference_close.iloc[i],
                  model=name,parent=pr,active=int(act),fit_n=len(moves[name][2]) if name in moves else len(eligible),
                  last_mature=latest.get(name,max(end[eligible]) if len(eligible) else None),
                  last_activation_train=max(end[known]) if len(known) else None,shift=dv1,scale=mul1,skew=skew1,law=len(laws)-1,**val))
        notes.append(dict(horizon=h,models=len(compare),candidate=anchor,cases=len(ids)))
        print('Native mechanism and activation arms completed',h,len(ids),flush=True)
    write('native-mechanism-cases.csv.gz',pd.DataFrame(out))
    write('mechanism-regime-audit.csv',pd.DataFrame(regimes))
    receipt('native-fit-receipts.ndjson.gz',fit_notes)
    weighted_store('native-mechanism-laws.npz',laws)
    save('native-config.json',dict(notes=notes,corporate=CORPORATE,position=POSITION,issue=NATIVE,
         fitted='Past outcomes of the published historical prediction, never fitted residuals from the original in-sample model.',
         recent_training='70 origins. Sensitivity omits 21 latest training origins or adds an eight-calendar-day embargo.',
         contemporaneous='V20 reproduces V19 08:55 feature snapshot and 09:10 original use time; preceding evening is a freshness sensitivity evaluated with the same native law at 09:10.',
         transform='Log location shifts, centered log scale/skew, sign-mass reweighting and complete-law mixtures. All published summary quantities implied by stored atoms and weights.',
         gate='Weekly announcement rank >=0.70. Monthly concentration rank >=0.48, volatility rank <=0.82, three days clear of expiry and rollover. Learned gate uses fully matured paired historical Brier gains.',
         active='Min 38 matched matured forecast errors plus available feature block. Fallback is the exact native law.'))

if __name__=='__main__':
    run()

