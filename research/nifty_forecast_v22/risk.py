"""Protected risk benchmarks, pooled variance dynamics and calibrated path experiments."""
from .common import *
from .analogues import path_variables,risk_values
from .learning import DAY,target_block,train

GARCH=((.10,.76,.14),(.08,.84,.10),(.05,.88,.07),(.04,.92,.06),(.10,.86,0.))
POINT={5:('offshore_plus_domestic','fixed_iv_rv'),21:('GJR','student_EGARCH')}


def garch_book(f,h):
    pred=np.full((len(f),len(GARCH)),np.nan)
    for positions in f.groupby('code',sort=False).indices.values():
        arr=f.observed_daily_return.iloc[positions].to_numpy(float)
        numeric=np.isfinite(arr)
        total=pd.Series(arr**2).rolling(63,min_periods=21).mean().to_numpy()
        for j,(alpha,beta,gamma) in enumerate(GARCH):
            persistence=alpha+beta+gamma*.5
            horizon_decay=np.power(persistence,np.arange(h)).mean()
            variance=np.nan
            for k,x in enumerate(arr[:-1]):
                base=total[k]
                if not numeric[k] or not np.isfinite(base):
                    continue
                if not np.isfinite(variance):
                    variance=base
                variance=(1-persistence)*base+(alpha+gamma*(x<0))*x*x+beta*variance
                pred[positions[k+1],j]=np.sqrt(252*(base+horizon_decay*(variance-base)))
    return pred


def qloss(y,p):
    v=np.maximum(.0001,(y/np.maximum(p,.004))**2)
    return v-np.log(v)-1


def pool_variance(t,prototypes):
    target=t.realized_vol.to_numpy()[:,None]
    loss=qloss(target,prototypes)
    origin=t.issue_ns.to_numpy();end=t.mature_ns.to_numpy()
    country=t.code.to_numpy();date=t.day.to_numpy()
    info={};receipts=[]
    for i in t.index[t.cohort.notna()]:
        cutoff=origin[i]
        local=(country=='india')&(end<cutoff)&(origin>cutoff-215*DAY)&np.isfinite(loss).all(axis=1)
        abroad=(country!='india')&(end<cutoff)&(origin>cutoff-215*DAY)&np.isfinite(loss).all(axis=1)
        f=pd.DataFrame(loss[abroad]).groupby(date[abroad]).mean().mean().to_numpy()
        s=loss[local].mean(axis=0)
        z=np.stack([s,f,.60*s+.40*f])
        # Continuous weights on registered GARCH parameter choices.
        w=np.exp(-24*(z-z.min(axis=1,keepdims=True)));w=w/w.sum(axis=1,keepdims=True)
        pred=np.sqrt(w@prototypes[i]**2)
        if not np.isfinite(pred).all():
            continue
        info[date[i]]=pred
        receipts.append(dict(day=date[i],horizon=int(t.horizon[i]),local_n=int(local.sum()),foreign_rows=int(abroad.sum()),
                      foreign_dates=len(set(date[abroad])),last_end_ns=int(end[local|abroad].max()),issue_ns=int(cutoff),
                      local_p=pred[0],foreign_p=pred[1],shrunk_p=pred[2],
                      local_weights=' '.join(map(str,w[0])),foreign_weights=' '.join(map(str,w[1])),shrunk_weights=' '.join(map(str,w[2]))))
    return info,receipts


def score_point(day,h,cohort,name,actual,p,event,prob,active,last,definition='V16 native realized volatility and expansion'):
    return dict(day=day,horizon=h,cohort=cohort,model=name,actual=actual,point=p,vol_mae=abs(actual-p),
                qlike=float(qloss(actual,p)),expand_brier=(prob-event)**2,p_expand=prob,actual_expand=event,active=active,
                last_mature_ns=last,cutoff='preauction_0855',target_definition=definition)


def provider_sensitivity():
    audit=csv('upstox-provider-comparison.csv').dropna(subset=['n_matched'])
    audit=audit[audit.same_type.eq('price-index candidate')]
    bad=audit[audit.close_within_006.div(audit.n_matched).lt(.10)].code.tolist()
    atlas=csv('analogue-law-atlas.csv')
    members=csv('analogue-law-members.csv.gz')
    paths=np.load(OUT/'analogue-observed-path-laws.npz')
    actual=csv('analogue-risk-cases.csv.gz')
    point=csv('india-protected-point-risk-cases.csv.gz')
    rows=[]
    for h in ORIGINAL:
        ag=atlas[atlas.horizon.eq(h)&atlas.model.eq('mixed_metric')]
        lookup=point[point.horizon.eq(h)&point.model.eq(POINT[h][0])].set_index('day')
        actual_h=actual[actual.horizon.eq(h)&actual.model.eq('mixed_metric')].set_index('day')
        observed=paths[f'p{h}']
        eligible_members=members[members.law.isin(ag.law)].groupby('law')
        for r in ag.itertuples(index=False):
            original=eligible_members.get_group(r.law).sort_values('order')
            for label in ('all_matched_sources','drop_low_agreement_sources'):
                m=original if label=='all_matched_sources' else original[~original.market.isin(bad)]
                if len(m)<12:
                    continue
                raw=observed[r.path_from+m.order.to_numpy()].astype(float)
                w=m.weight.div(m.groupby('episode').weight.transform('sum')).div(m.episode.nunique()).to_numpy()
                phase=np.arange(1,h+1)[None,:,None]/h
                vals=raw-float(w@raw[:,-1,3])*phase
                scale=np.clip(float(lookup.loc[r.day,'pred_vol'])/(w@path_variables(vals)['rv']),.45,2.5)
                target=actual_h.loc[r.day]
                y={k:target[k+'_actual'] for k in path_variables(vals)}
                score=risk_values(path_variables(vals*scale),w,y,r.causal_volatility,h)
                rows.append(dict(horizon=h,day=r.day,cohort=r.cohort,model=label,n_members=len(m),effective_members=1/(w@w),
                     excluded_sources=' '.join(bad) if label=='drop_low_agreement_sources' else '',range_crps=score['range_crps'],
                     drawdown_crps=score['drawdown_crps'],terminal_crps=score['terminal_crps']))
    write('india-risk-analogue-source-sensitivity.csv',pd.DataFrame(rows))


def run():
    raw=csv('protected-point-risk-cases.csv.gz',V20)
    benchmark=csv('protected-joint-benchmarks.csv',V20)
    reference={(5,'raw_iv','mae'):.037814,(5,'offshore_plus_domestic','mae'):.036469,
               (21,'GJR','mae'):.033179,(21,'GJR','qlike'):.199677,
               (5,'fixed_iv_rv','brier'):.152707,(21,'student_EGARCH','brier'):.172872}
    for (h,key,k),v in reference.items():
        assert abs(raw.loc[raw.horizon.eq(h)&raw.model.eq(key),k].mean()-v)<1.e-6
    assert abs(benchmark.loc[benchmark.horizon.eq(21)&benchmark.model.eq('V14_gjr_student'),'range_crps'].iloc[0]-.015422)<1.e-6
    write('india-protected-point-risk-cases.csv.gz',raw)
    write('india-protected-native-path-benchmarks.csv',benchmark)
    prior=csv('coherent-risk-path-cases.csv.gz',V20)
    prior=prior[prior.cutoff.eq('preauction_0855')].copy()
    write('india-protected-same-clock-path-cases.csv.gz',prior)
    feats=csv('international-feature-panel.csv.gz')
    transferred=csv('india-transfer-input-cases.csv.gz')
    atlas=csv('analogue-law-atlas.csv')
    members=csv('analogue-law-members.csv.gz')
    paths=np.load(OUT/'analogue-observed-path-laws.npz')
    originals=np.load(OUT/'local-observed-paths.npz')
    weights={i:g.weight.to_numpy(float) for i,g in members.groupby('law')}
    points=[];risks=[];fitted=[];paths_for_archive={};path_recipes=[]
    for h in ORIGINAL:
        t=target_block(feats,h)
        local=t[t.cohort.notna()].set_index('day').sort_index()
        preds=garch_book(t,h)
        var,fits=pool_variance(t,preds);fitted+=fits
        protected=raw[raw.horizon.eq(h)]
        points.extend(score_point(x.day,h,x.cohort,x.model,x.actual_vol,x.pred_vol,x.actual_expand,x.p,True,0)
                      for x in protected.itertuples(index=False))
        bt,bt2=(protected[protected.model.eq(k)].set_index('day').reindex(local.index) for k in POINT[h])
        np.testing.assert_allclose(bt.actual_vol,local.realized_vol,rtol=0,atol=.000001)
        trailing=csv(f'targets-{h}.csv',V14).set_index('day').reindex(bt.origin).trailing_at_origin.to_numpy(float)
        assert np.array_equal(bt.actual_vol.to_numpy()>1.25*trailing,bt.actual_expand.astype(bool).to_numpy())
        transfer=transferred[transferred.horizon.eq(h)].set_index(['day','model'])
        external=transfer.xs('loco_transfer',level='model').reindex(local.index)
        var_arr=np.array([var[day] for day in local.index])
        point=bt.pred_vol.to_numpy(float);event=bt.actual_expand.to_numpy(float)
        daily_rv=bt.actual_vol.to_numpy(float)
        p_ref=bt2.p.to_numpy(float)
        x=np.column_stack([np.log(np.maximum(external.rv_forecast,.015)/np.maximum(point,.015)),
              np.log(np.maximum(var_arr[:,2],.015)/np.maximum(point,.015)),external.expansion_p,local.global_vix,local.synchronization])
        result=np.column_stack([np.log(np.maximum(daily_rv,.012)/np.maximum(point,.015)),event-p_ref])
        aa=atlas[atlas.horizon.eq(h)].set_index(['day','model'])
        p=paths[f'p{h}']
        oh=originals[f'path_{h}']
        mature=local.mature_ns.to_numpy();issue=local.issue_ns.to_numpy();days=local.index.to_numpy()
        prospective=[]
        for i,day in enumerate(days):
            ix=np.flatnonzero((mature<issue[i])&(issue<issue[i]))[-140:]
            active=len(ix)>=45
            last=int(mature[ix].max()) if len(ix) else 0
            y=bt.loc[day]
            vi=var_arr[i]
            external_point=float(external.rv_forecast[day])
            external_prob=float(external.expansion_p[day])
            correction=np.zeros(2)
            if active:
                m=train(x[ix],result[ix],days[ix],tuple(range(x.shape[1])),1.3)
                correction=m.predict(x[i:i+1])[0]
            scale=float(np.exp(np.clip(.53*correction[0],-.20,.20))) if active else 1.
            adjusted_prob=float(np.clip(p_ref[i]+.60*correction[1],.015,.985)) if active else p_ref[i]
            this={
                'v22_garch_local':(vi[0],p_ref[i],True,0),'v22_garch_foreign':(vi[1],p_ref[i],True,0),
                'v22_garch_shrunk':(vi[2],p_ref[i],True,0),'v22_loco_risk':(external_point,external_prob,True,int(external.last_train_ns[day])),
                'v22_iv_gjr_shrink':(np.sqrt(.80*point[i]**2+.20*vi[2]**2),p_ref[i],True,0),
                'v22_iv_gjr_calibrated':(point[i]*scale,adjusted_prob,active,last)}
            for name,(pr,e,on,tim) in this.items():
                points.append(score_point(day,h,y.cohort,name,y.actual_vol,pr,y.actual_expand,e,on,tim))
            row=local.loc[day]
            actual={k:float(v[0]) for k,v in path_variables(oh[int(row.row):int(row.row)+1].astype(float)).items()}
            # Put both new and old risk laws on the same realized V14/V16 volatility units.
            assert abs(actual['rv']-float(y.actual_vol))<1.e-6
            phase=np.arange(1,h+1)[None,:,None]/h
            sel={'analogue_mix_unscaled':('mixed_metric',None,1.),'analogue_india_on_IV_GJR':('domestic_history',point[i],1.),
                 'analogue_global_on_IV_GJR':('mixed_metric',point[i],1.),'analogue_global_calibrated':('mixed_metric',point[i]*scale,1.),
                 'analogue_global_heavy_tail':('mixed_metric',point[i],1.12),
                 'analogue_global_shock_conditioned':('mixed_path' if row.synchronization>=.55 else 'mixed_nearest',point[i],1.),
                 'analogue_extreme_stress':('foreign_stress',None,1.)}
            for model,(key,target,exponent) in sel.items():
                rec=aa.loc[(day,key)]
                w=weights[int(rec.law)]
                m=p[int(rec.path_from):int(rec.path_to)].astype(float)
                gamma=0.;s=1.
                if target is not None:
                    gamma=float(w@m[:,-1,3])
                    m=m-gamma*phase
                    if exponent!=1.:
                        unit=max(.003,row.raw_daily_sigma*np.sqrt(h))
                        m=np.sign(m)*unit*(abs(m)/unit)**exponent
                    s=float(np.clip(target/(w@path_variables(m)['rv']),.45,2.5))
                    m=m*s
                high=m[:,:,1];low=m[:,:,2]
                assert (high>=np.maximum(m[:,:,0],m[:,:,3])-2.e-7).all() and (low<=np.minimum(m[:,:,0],m[:,:,3])+2.e-7).all()
                v=path_variables(m)
                stats=risk_values(v,w,actual,trailing[i]/np.sqrt(252),h)
                k0=len(prospective);prospective.extend(m.astype(np.float32))
                risks.append(dict(horizon=h,day=day,cohort=row.cohort,model=model,source_law=int(rec.law),n=len(w),active=True,
                     cutoff='preauction_0855',ess=rec.ess,last_mature_ns=max(int(rec.last_mature_ns),last if model.endswith('calibrated') else 0),
                     actual_rv=actual['rv'],actual_range=actual['range'],is_stress=bool(rec.is_stress),**stats))
                path_recipes.append(dict(horizon=h,day=day,model=model,source_law=int(rec.law),path_from=k0,path_to=len(prospective),
                        horizon_log_drift_removed=gamma,scale=s,signed_exponent=exponent,threshold_volatility=trailing[i]))
        paths_for_archive[f'p{h}']=np.array(prospective,np.float32)
        q=prior[prior.horizon.eq(h)&prior.model.eq('same_clock_IV')].set_index('day').reindex(local.index)
        np.testing.assert_allclose(q.actual_range,local.future_range,atol=1.e-6,rtol=0)
        print('Risk reference and analogues verified at',h,'sessions,',len(local),'NIFTY origins.',flush=True)
    write('india-risk-point-comparison-cases.csv.gz',pd.DataFrame(points))
    write('india-risk-path-comparison-cases.csv.gz',pd.DataFrame(risks))
    write('india-garch-pooling-receipts.csv.gz',pd.DataFrame(fitted))
    write('india-calibrated-risk-path-recipes.csv.gz',pd.DataFrame(path_recipes))
    np.savez_compressed(OUT/'india-calibrated-risk-ohlc-laws.npz',**paths_for_archive)
    provider_sensitivity()


if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='sensitivity':
        provider_sensitivity()
    else:
        run()
