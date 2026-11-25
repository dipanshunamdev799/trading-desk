"""Fit event-conditioned NIFTY endpoint laws with exact, matched forecasting parents."""
from dataclasses import dataclass
from .common import *
from .aggregate import COUNT,TEXT,FUND,WEIGHT,REACT,DISAG,ALTS,SCHEDULE,EXTRA,STATE
from research.nifty_forecast_v16.model import fit
from research.nifty_forecast_v17 import weekly
from research.nifty_forecast_v17.gift import score
from research.nifty_forecast_v17.common import Q

@dataclass(frozen=True)
class Arm:
    name:str
    fields:tuple
    parent:str='clock_structural'
    kind:str='shift'

ARMS=(
    Arm('counts',COUNT),Arm('text_given_counts',COUNT+TEXT,'counts'),
    Arm('weighted_text',COUNT+WEIGHT[:2],'counts'),
    Arm('fundamental_only',FUND,kind='fund_only'),
    Arm('fundamental_augmentation',FUND+COUNT,'counts'),
    Arm('sector_liquidity_proxy',WEIGHT+FUND,'fundamental_augmentation'),
    Arm('market_reaction_only',REACT),
    Arm('expectation_repricing',REACT+TEXT+FUND+DISAG,'market_reaction_only'),
    Arm('multi_timescale',COUNT+TEXT+FUND+REACT+('count_shift',)),
    Arm('scheduled_location',SCHEDULE),
    Arm('additional_nonprice',EXTRA),
    Arm('delivery_only',EXTRA[:3]),Arm('participant_positions',EXTRA[3:5]),Arm('bulk_block_activity',EXTRA[5:8]),
    Arm('event_conditioned_law',TEXT+FUND+SCHEDULE,kind='shape'),
    Arm('fixed_event_mixture',COUNT+TEXT+FUND,kind='mix'),
    Arm('clock_component_event',COUNT+TEXT+FUND,'component_plus_residual',kind='component'),
    Arm('alternative_text',COUNT+(ALTS[0],),'counts'),Arm('omit_heavyweights',COUNT+(ALTS[1],),'counts'),
    Arm('omit_earnings',COUNT+(ALTS[2],),'counts'),Arm('delayed_24h',COUNT+(ALTS[3],),'counts'),
    Arm('delayed_72h',COUNT+(ALTS[4],),'counts'),Arm('material_only',COUNT+(ALTS[5],),'counts'),
    Arm('omit_large_arrivals',COUNT+(ALTS[6],),'counts'),
    Arm('shifted_inputs',COUNT+TEXT+FUND,kind='lag'),
    Arm('blocked_placebo',COUNT+TEXT+FUND,kind='permuted'))

def field_matrix(f,fields):
    return f.reindex(columns=list(dict.fromkeys(fields))).to_numpy(float)

def available(days,end,i,source,decision=None,limit=140):
    when=days[i] if decision is None else decision[i]
    return np.flatnonzero((end<when)&(np.arange(len(end))<i)&np.isfinite(source))[-limit:]

def fit_shift(x,resid,i,t,limit=.009,penalty=175.,mix=None):
    t=t[np.isfinite(resid[t])]
    if len(t)<38:return 0.,None,t
    train=x[t] if mix is None else x[np.roll(t,mix)]
    m=fit(train,resid[t],penalty)
    return float(np.clip(.58*m.values(x[i]),-limit,limit)),m,t

def build_clock(clock,h):
    z=csv('event-aggregate-features.csv.gz')
    e=csv('event-schedule-exposures.csv.gz')
    fine=z[z.cutoff.eq(clock)].merge(e[e.cutoff.eq(clock)&e.horizon.eq(h)].drop(columns=['horizon','cutoff']),on='day',validate='1:1')
    x=csv('original-feature-panel.csv.gz',V17)
    control=x[x.cutoff.eq(clock)].set_index('day')
    y=csv('original-target-panel.csv',V17).set_index('day')
    f=control.join(fine.set_index('day').drop(columns=['origin','cutoff']),how='left').reindex(y.index)
    return f,y

def original():
    old=csv('original-clock-forecasts.csv.gz',V17)
    a=[]
    meta=[]
    fits=[]
    legacy=[]
    controls=weekly.load_legacy()
    null=[]
    with np.load(V17/'original-clock-laws.npz',allow_pickle=False) as p:
        stored=p['atoms'].astype(float)
    for clock in ('previous_1700','preauction_0855'):
        for h in HORIZONS:
            f,y=build_clock(clock,h)
            day=y.index.to_numpy()
            decision=f.decision.str[:10].to_numpy()
            target=y['original'+str(h)].to_numpy(float)
            end=y['end_original'+str(h)].fillna('9999-12-31').to_numpy()
            groups=y['cohort_'+str(h)]
            official=np.flatnonzero(groups.notna())
            org=old[old.cutoff.eq(clock)&old.horizon.eq(h)].set_index(['day','model'])
            expected=weekly.chronology(f,weekly.ORIGINAL_BASE,target,end,decision)
            error=target-expected
            fields={r.name:tuple(dict.fromkeys(r.fields)) for r in ARMS}
            X={t:field_matrix(f,z) for t,z in fields.items()}
            X['shifted_inputs']=pd.DataFrame(X['shifted_inputs']).shift(5).to_numpy()
            ey=np.full(len(target),np.nan)
            for i in official:
                _,v,w=controls[h,y.origin.iloc[i]]
                ey[i]=target[i]-np.log1p(w@v)
            for i in official:
                t=available(day,end,i,target,decision)
                q0=org.loc[(day[i],'clock_structural')]
                q1=org.loc[(day[i],'component_plus_residual')]
                atoms=stored[int(q0.law)]
                base=atoms-np.median(atoms)
                comp=stored[int(q1.law)]
                hist=target[t]
                where=dict(day=day[i],origin=y.origin.iloc[i],target_end=end[i],horizon=h,cutoff=clock,
                           cohort=groups.iloc[i],last_mature=max(end[t]),decision=f.decision.iloc[i])
                for reference in ('clock_structural','component_plus_residual','neutral','historical','stock_direct','stock_residual','low_rank_sector_risk'):
                    r=org.loc[(day[i],reference)]
                    a.append(stored[int(r.law)].astype(np.float32))
                    out=score(a[-1],target[i])
                    if reference=='neutral':out.update(p=.50,brier=.25,log_loss=np.log(2),correct=int(target[i]>0))
                    meta.append(dict(**where,model=reference,parent='clock_structural',law=len(a)-1,
                                     adapted=0,**out))
                for arm in ARMS:
                    x=X[arm.name]
                    ans,m,t1=fit_shift(x,error,i,t,limit=.009 if h==5 else .014,mix=(17 if arm.kind=='permuted' else None))
                    law=atoms+ans
                    if arm.kind=='fund_only':
                        fitted=fit(x[t],target[t],150.)
                        loc=.68*fitted.values(x[i])+.32*np.median(hist)
                        law=base+float(np.clip(loc,-.04,.04))
                    elif arm.kind=='shape' and len(t1)>=38:
                        ref=max(.004,np.median(abs(error[t1])))
                        z=np.log(np.maximum(abs(error[t1]),.0005)/ref)
                        v=fit(x[t1],z,175.)
                        scale=np.exp(np.clip(.43*v.values(x[i]),-.25,.25))
                        sign_choice=np.clip(.35*ans/ref,-.11,.11)
                        law=np.median(atoms)+ans+base*scale*np.where(base>0,1.+sign_choice,1.-sign_choice)
                    elif arm.kind=='mix':
                        law=np.r_[atoms[::2],(atoms+ans)[1::2]]
                    elif arm.kind=='component':
                        law=comp+ans
                    a.append(np.asarray(law,np.float32))
                    meta.append(dict(**where,law=len(a)-1,model=arm.name,parent=arm.parent,adapted=int(m is not None),**score(law,target[i])))
                    if m is not None:
                        fits.append(dict(law=len(a)-1,used_n=len(t1),training_end=max(end[t1]),penalty=175.,
                                         **m.receipt(fields[arm.name])))
                if clock=='preauction_0855':
                    # V14's native guard remains later. The incremental event features themselves are frozen at 08:55.
                    _,v,w=controls[h,y.origin.iloc[i]]
                    shift,m,u=fit_shift(X['fundamental_augmentation'],ey,i,t,limit=.012)
                    for name,dv in [('V14_exact',0.),('V14_event_overlay',shift)]:
                        adv=(1+v)*np.exp(dv)-1
                        detail=weekly.evaluate(adv,w,np.expm1(target[i]))
                        detail['abs_error']=abs(detail['actual']-detail['median'])
                        detail['sq_error']=detail['squared_error']
                        legacy.append(dict(**(where|{'cutoff':'native_v14_guard'}),model=name,parent='V14_exact',law_shift=dv,
                                           adapted=int(name=='V14_event_overlay' and m is not None),**detail))
                    for seed in range(23):
                        for group in ('counts','text_given_counts','fundamental_augmentation'):
                            rotated=(seed+3)*7
                            shift0,_,_=fit_shift(X[group],error,i,t,limit=.009 if h==5 else .014,mix=rotated)
                            tmp=score(atoms+shift0,target[i])
                            null.append(dict(day=day[i],horizon=h,seed=seed,arm=group,brier_gain=q0.brier-tmp['brier'],crps_gain=q0.crps-tmp['crps']))
            print('Original endpoint laws',clock,h,'sessions',flush=True)
    d=pd.DataFrame(meta)
    assert d.last_mature.le(d.day).all()
    assert d.last_mature.lt(d.decision.str[:10]).all()
    write('original-event-forecasts.csv.gz',d)
    write('protected-v14-event-overlays.csv.gz',pd.DataFrame(legacy))
    write('refit-null-case-gains.csv.gz',pd.DataFrame(null))
    with gzip.open(OUT/'original-event-fits.ndjson.gz','wt',encoding='utf8') as q:
        for r in fits:q.write(json.dumps(r,allow_nan=False,default=str)+'\n')
    np.savez_compressed(OUT/'original-event-laws.npz',atoms=np.stack(a))
    print('Archived original endpoint forecasts',len(meta),flush=True)

def postopen():
    a=csv('event-aggregate-features.csv.gz')
    rows=[]
    for clock in ('09:25','10:20'):
        z=a[a.cutoff.eq(clock)].set_index('day')
        post=csv('residual-'+clock.replace(':','')+'-scores.csv.gz',V17)
        with np.load(V17/('residual-'+clock.replace(':','')+'-laws.npz'),allow_pickle=False) as book:
            atoms=book['atoms']
        for target in ('remaining_5','remaining_21','r30','regular_residual'):
            u=post[post.target.eq(target)&post.model.eq('frozen_parent_residual_history')].set_index('day').reindex(z.index)
            if u.law.notna().sum()==0:continue
            day=z.index.to_numpy()
            end=u.target_end.fillna('9999-12-31').to_numpy()
            y=np.log1p(u.actual.to_numpy(float))
            vals=np.full(len(u),np.nan)
            for j in np.flatnonzero(u.law.notna().to_numpy()):vals[j]=np.mean(atoms[int(u.law.iloc[j])])
            error=y-vals
            X={name:field_matrix(z,field) for name,field in [('counts',COUNT),('text',COUNT+TEXT),('fundamental',FUND),('expectation',REACT+DISAG)]}
            for i in np.flatnonzero(np.isfinite(error)):
                tr=available(day,end,i,error)
                if len(tr)<38:continue
                law=atoms[int(u.law.iloc[i])]
                name='V17_postopen_parent'
                all_=dict(day=day[i],origin=u.origin.iloc[i],cutoff=clock,target=target,target_end=end[i],
                          cohort=u.cohort.iloc[i],last_mature=max(end[tr]),source_law=int(u.law.iloc[i]))
                rows.append(dict(**all_,model=name,parent=name,shift=0.,**score(law,y[i])))
                for name,x in X.items():
                    delta,_,_=fit_shift(x,error,i,tr,.009)
                    rows.append(dict(**all_,model=name,parent='V17_postopen_parent',shift=delta,**score(law+delta,y[i])))
    write('postopen-event-overlays.csv.gz',pd.DataFrame(rows))

if __name__=='__main__':
    original()
    postopen()
