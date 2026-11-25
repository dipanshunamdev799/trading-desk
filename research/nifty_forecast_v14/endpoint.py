"""Endpoint attribution experiments and separate rolling interval adjustments."""
from scipy.stats import t as student_t

from .common import *
from .data import DOM
from .path_score import INNER, Q_NAMES, summaries, log_brier
from .signals import fit_logistic
from .volatility import ridge, robust_design, design_apply


def center_scale(a,w,mu,sd):
    center=w@a
    variance=w@np.square(a-center)
    return mu+(a-center)*(sd/max(np.sqrt(variance),1.e-7))


def mix_samples(positive,negative,probability):
    a=np.r_[positive,negative]
    w=np.r_[np.full(len(positive),probability/len(positive)),
            np.full(len(negative),(1-probability)/len(negative))]
    return a,w


def analysis():
    pred=pd.read_csv(OUT/'process-risk-predictions.csv')
    by={(h,model):g.set_index('origin').prediction for (h,model),g in pred.groupby(['horizon','model'])}
    with np.load(V13/'prior-endpoint-quantiles.npz',allow_pickle=False) as ar:
        keys=ar['keys']; v=ar['values']; means=ar['means']; sigmas=ar['sd']
    old={(int(h),n,d):(a,m,sd) for (h,n,d),a,m,sd in zip(keys,v,means,sigmas)
         if n in ('NEUTRAL','PH_NATIVE_PHASE_MIXTURE','J12_GROUP_BALANCED','V12_STAT')}
    phases=[]
    components=[]
    ledger=[]
    law_keys=[]
    law_atoms=[]
    law_weights=[]
    for h in HORIZONS:
        x=matrix(f'features-{h}.csv').copy()
        y=matrix(f'targets-{h}.csv')
        x['rotation_risk']=x.finance*x.vrp
        x['breadth_expansion']=x.breadth5*x.atm1
        x['breadth_iv']=x.breadth21*x.atm
        q=y[y.cohort.notna()]
        for day,row in q.iterrows():
            t=mature(y,day,178)
            hist=y.iloc[t]
            d=x.loc[[day]]
            past=x.reindex(y.index).iloc[t]
            fields=DOM+('rotation_risk','breadth_expansion','breadth_iv','atm','vrp','iv_skew','term_slope')
            z,test,descr=robust_design(past,d,fields)
            h0=float(d.atm.iloc[0]*np.sqrt(h/252.))
            s0=past.atm.fillna(past.rv21).to_numpy().clip(.026)*np.sqrt(h/252.)
            response=hist.endpoint_return.to_numpy()
            normalized=response/s0
            rfit=ridge(z,normalized,250.)
            target_mu=float(np.clip(design_apply(test,rfit)[0]*h0,-.032,.032))
            direction,record=fit_logistic(z,np.asarray(response>0,float),28.)
            raw_p=float(1/(1+np.exp(-design_apply(test,direction)[0])))
            inv=by[h,'gjr_student'].at[day]*np.sqrt(h/252.)
            inv_hybrid=by[h,'blend_gjr_iv'].at[day]*np.sqrt(h/252.)
            pos=np.maximum(normalized[normalized>0]*inv_hybrid,.00001)
            neg=np.minimum(normalized[normalized<=0]*inv_hybrid,-.00001)

            parent='PH_NATIVE_PHASE_MIXTURE' if h==5 else 'NEUTRAL'
            group='J12_GROUP_BALANCED' if h==5 else 'NEUTRAL'
            a,mu,sigma=old[h,parent,day]
            b,mu_b,sigma_b=old[h,group,day]
            w=np.full(len(a),1/len(a))
            # Risk-informed V13 references set the location before shape substitutions.
            iv_reference=mu+(a-mu)*np.clip(h0/sigma,.60,1.55)
            aw=center_scale(iv_reference,w,mu,np.sqrt(w@np.square(iv_reference-mu)))
            width=float(np.sqrt(w@(aw-mu)**2))
            xb=aw-mu
            sigma_m=float(np.clip(inv/sigma,.60,1.55)*sigma)
            hybrid_m=float(np.clip(inv_hybrid/sigma_b,.60,1.55)*sigma_b)
            shift=.28*(target_mu-mu) if h==5 else .19*(target_mu-mu)
            curve=np.arange(.5,512.5)/512.
            tail=student_t.ppf(curve,6)*np.sqrt(4/6)
            ta=np.r_[xb/width,tail]
            tw=np.r_[np.full(len(a),.85/len(a)),np.full(len(tail),.15/len(tail))]
            raw_skew=float(d.iv_skew.iloc[0]) if np.isfinite(d.iv_skew.iloc[0]) else 0.
            skewed=xb*(1+np.clip(-raw_skew,-.12,.12)*np.sign(xb))
            prob=float(w@(aw>0))
            shrink=.70*prob+.15
            shrunk=mix_samples(aw[aw>0],aw[aw<=0],shrink) if 0.<prob<1. else (aw,w)
            signed=mix_samples(pos,neg,.55*prob+.45*raw_p) if len(pos) and len(neg) else (aw,w)
            fixed={
                'gjr_dispersion_only':(center_scale(xb,w,mu,sigma_m),w),
                'hybrid_gjr_group':(center_scale(b,w,mu_b,hybrid_m),w),
                'domestic_location_only':(aw+shift,w),
                'domestic_location_gjr_scale':(center_scale(xb,w,mu+shift,sigma_m),w),
                'skew_only':(center_scale(skewed,w,mu,width),w),
                'sign_shrinkage':shrunk,
                'student_tail_only':(center_scale(ta,tw,mu,width),tw),
                'sign_magnitude_hybrid':signed,
            }
            for name,(atoms,weight) in fixed.items():
                law_keys.append((h,day,name,row.endpoint))
                law_atoms.append(atoms)
                law_weights.append(weight)
                result=summaries(atoms,np.array([row.endpoint_return]),weight)[0]
                p=float(weight@(atoms>0))
                br,ls=log_brier(p,int(row.endpoint_return>0))
                onset=dict(horizon=h,origin=day,cohort=row.cohort,model=name,target='endpoint_return',actual=row.endpoint_return)
                phases.append(dict(**onset,**result,p_up=p,brier=br,log_loss=ls))
                components.append(dict(**onset,reference_p=prob,p=p,reference_mean=mu,mean=weight@atoms,
                              reference_width=width,width=np.sqrt(weight@np.square(atoms-weight@atoms)),
                              lower_tail_mass=float(weight@(atoms<-.025)),upper_tail_mass=float(weight@(atoms>.025))))
            ledger.append(dict(horizon=h,origin=day,model='endpoint_attribution',last_mature=hist.endpoint.max(),
                 train_origins=hist.index.tolist(),features=descr,coef_location=rfit.tolist(),coef_direction=direction.tolist(),
                 parent=parent,group=group,direction_fit=record,gjr_stdev=inv,hybrid_stdev=inv_hybrid,
                 iv_horizon_stdev=h0,original_mean=float(mu),original_std=float(sigma),location_shift=shift))
    write('endpoint-attribution.csv',pd.DataFrame(phases))
    write('endpoint-components.csv',pd.DataFrame(components))
    offsets=np.r_[0,np.cumsum([len(a) for a in law_atoms],dtype=np.int64)]
    np.savez_compressed(OUT/'standalone-endpoint-laws.npz',keys=np.asarray(law_keys,dtype=str),
                        offsets=offsets,atoms=np.concatenate(law_atoms),weights=np.concatenate(law_weights))
    save('endpoint-fits.json',ledger)
    print('Preserved',len(phases),'standalone endpoint attribution forecasts',flush=True)


def interval_calibration():
    # Re-use marginal predictions and embargo outcomes by endpoint.
    results=[]; ledger=[]
    margins=pd.read_csv(OUT/'path-marginals.csv.gz',low_memory=False)
    selected=margins[margins.model.isin(['constant_iv','path_mixture','iv_scaled_blocks','jump_diffusion'])&
                    margins.target.isin(['range','endpoint_return','high','low','volatility'])]
    groups={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    methods=['rolling_cqr','asymmetric_residual','state_residual','calendar_block_cqr']
    for (h,name,k),frame in selected.groupby(['horizon','model','target']):
        outcome=groups[h]
        s=frame.sort_values('origin').set_index('origin')
        end=s.index.map(outcome.endpoint)
        iv=outcome.horizon_sd_at_origin.reindex(s.index)
        vol=outcome.trailing_at_origin.reindex(s.index)
        order=np.arange(len(s))
        # Dimensionless scores account for the width of each issued interval.
        for i,(day,row) in enumerate(s.iterrows()):
            eligible=np.flatnonzero(end<day)[-126:]
            ready=len(eligible)>=24
            valid=eligible[-84:] if len(eligible)>84 else eligible
            for level,(lo,hi) in INNER.items():
                coverage=int(level)/100
                alpha=1-coverage
                lower,upper=row[Q_NAMES[lo]],row[Q_NAMES[hi]]
                width=max(upper-lower,1.e-6)
                if len(valid):
                    past=s.iloc[valid]
                    w0=(past[Q_NAMES[hi]]-past[Q_NAMES[lo]]).clip(1.e-6)
                    residual_l=(past[Q_NAMES[lo]]-past.actual)/w0
                    residual_u=(past.actual-past[Q_NAMES[hi]])/w0
                    joint=np.maximum(residual_l,residual_u)
                for method in methods:
                    lf=rf=0.
                    used=valid
                    if ready:
                        p=min(1.,np.ceil((len(valid)+1)*coverage)/len(valid))
                        if method=='rolling_cqr':
                            lf=rf=float(np.clip(np.quantile(joint,p,method='higher'),-.15,.60))
                        elif method=='asymmetric_residual':
                            lf,rf=[float(np.clip(np.quantile(v,1-alpha/2,method='higher'),-.17,.65))
                                   for v in [residual_l,residual_u]]
                        elif method=='state_residual':
                            distance=np.abs(np.log(vol.iloc[valid]/vol.iloc[i]))
                            ii=np.argsort(distance.to_numpy())[:max(24,len(valid)//2)]
                            used=valid[ii]
                            lf,rf=[float(np.clip(np.quantile(v.iloc[ii],1-alpha/2,method='higher'),-.17,.65))
                                   for v in [residual_l,residual_u]]
                        else:
                            block=order[valid]//h
                            block_score=pd.Series(joint.to_numpy()).groupby(block).max()
                            lf=rf=float(np.clip(np.quantile(block_score,p,method='higher')*.55,-.14,.62))
                    left=lower-lf*width;right=upper+rf*width
                    if k=='range':
                        left=max(0.,left)
                    assert right>=left
                    actual=float(row.actual)
                    score=right-left+2/alpha*(max(0.,left-actual)+max(0.,actual-right))
                    z=dict(horizon=h,origin=day,cohort=row.cohort,model=name,target=k,method=method,central=level,
                           lower=left,upper=right,coverage=int(left<=actual<=right),width=right-left,interval_score=score,
                           lower_miss=int(actual<left),upper_miss=int(actual>right),fitted=bool(ready),train_n=len(used),
                           baseline_coverage=row['coverage'+level],baseline_width=row['width'+level],
                           baseline_interval_score=row['interval_score'+level],max_calibration_endpoint=max(end[used]) if len(used) else None)
                    if z['max_calibration_endpoint'] is not None:
                        assert z['max_calibration_endpoint']<day
                    results.append(z)
    write('standalone-calibrated-intervals.csv.gz',pd.DataFrame(results))
    print('Scored',len(results),'separate matured-residual interval adjustments',flush=True)


if __name__=='__main__':
    import sys
    {'endpoint':analysis,'intervals':interval_calibration}[sys.argv[1]]()
