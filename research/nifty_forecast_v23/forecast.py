"""Walk-forward V23 distribution construction on frozen comparable experts."""
from collections import Counter, defaultdict

from .common import *
from .geometry import load_bank
from .laws import Law,mix,transport,metrics,logshape,piece,store,invariant_test,GRID,expit,logit
from .reference import PARENTS
from research.nifty_forecast_v20.modeling import block_counts

F=('prior_ret5','prior_ret21','trailing_vol','iv_prev','iv_skew','iv_term','domestic_rotation_finance',
   'eq500_spread5','allEQ_advance','reaction_mean','count9','FII_index_futures_d21','index_futures_detail_hhi_z',
   'gift_proxy','expected_gap','foreign_sd','vix_level')
MEMORY=120
MIN=36
POINT={5:'raw_iv',21:'GJR'}


def past_rows(mature,decision,at,limit=MEMORY):
    return np.flatnonzero((mature<at)&(decision<at))[-limit:]


def asof_features(index,clock):
    b=csv('asof-features.csv.gz',root_for(20),usecols=['day','cutoff','decision',*F])
    supported='preauction_0855' if clock=='native_0910' else clock
    b=b[b.cutoff.eq(supported)].set_index('day').reindex(index)
    assert not b.index.has_duplicates
    return b[list(F)].to_numpy(float)


def standardize(x,point):
    present=np.isfinite(x)
    enough=present.sum(axis=0)>8
    mean=np.where(enough,np.nanmedian(x,axis=0),0.)
    q=np.nanquantile(x,[.25,.75],axis=0)
    sd=np.where(enough,np.maximum(1e-6,(q[1]-q[0])/1.349),1.)
    z=np.where(present&(enough[None,:]),(x-mean)/sd,0.).clip(-4,4)
    v=np.clip(np.where(np.isfinite(point)&enough,(point-mean)/sd,0.),-4,4)
    return np.column_stack([np.ones(len(z)),z]),np.r_[1.,v]


def ridge(x,y,w,penalty,prior=None):
    w=w/w.sum()
    p=np.ones(x.shape[1])*penalty;p[0]=1.e-6
    b=np.zeros(x.shape[1]) if prior is None else prior
    return np.linalg.solve((x*w[:,None]).T@x+np.diag(p),(x*w[:,None]).T@y+p*b)


def family_base(families):
    c=Counter(families)
    p=np.array([1/c[z] for z in families])
    return p/p.sum()


def exact_unique(signatures):
    representatives=[]
    already=set()
    for k,s in enumerate(signatures):
        if s not in already:
            representatives.append(k)
            already.add(s)
    return np.array(representatives)


def component_laws(experts,base,donor,risk,history_shape,h):
    original_loc,original_scale,original_skew=logshape(base)
    model_location,_,model_skew=logshape(donor)
    weak_location=original_loc+.40*np.clip(model_location-original_loc,-.030,.030)
    scale=float(np.clip(.65+.35*risk/max(original_scale,.0008),.72,1.36)) if np.isfinite(risk) else 1.
    skew=float(np.clip(.65*(model_skew-original_skew),-.23,.23))
    identified={
        'component_location_only':base.transform(weak_location),
        'component_iv_gjr_scale_only':base.transform(scale=scale),
        'component_asymmetry_only':base.transform(asymmetry=skew),
        'component_sign_only':base.reweight_sign(.75*base.positive()+.25*donor.positive()),
    }
    tail=history_shape.quantiles(np.r_[np.linspace(.012,.125,16),np.linspace(.875,.988,16)])
    typical=logshape(history_shape)
    x=np.log1p(tail)
    x=x-x.mean()
    tail_shape=Law.build(np.expm1(original_loc+original_scale*x/max(typical[1],.001)))
    identified['component_tail_only']=mix([base,tail_shape],[.90,.10])
    same_shape=history_shape.transform(location=original_loc,scale=original_scale/max(typical[1],.001))
    identified['component_historical_shape_only']=same_shape
    joint=base.transform(weak_location,scale,skew)
    identified['component_coherent_joint']=mix([joint,tail_shape],[.90,.10])
    return identified


def training_weights(loss,iq,weights,regime,rng,h):
    # Weighted risk across individual expert CRPS values is a conservative objective for a linear law pool.
    ref=np.median(loss,axis=1)
    residual=(loss-ref[:,None])/max(.002,np.median(ref))
    raw=residual.mean(axis=0)
    robust=np.clip(residual,-.8,.8).mean(axis=0)
    distances=np.mean(np.abs(iq[:,:,None,:]-iq[:,None,:,:]),axis=(0,3))
    degree=np.exp(-distances/max(.0004,.25*np.median(distances))).sum(axis=1)
    red=weights/np.sqrt(degree);red=red/red.sum()
    low=regime<=0;high=regime>0
    group=[robust] if min(low.sum(),high.sum())<18 else [residual[low].mean(axis=0),residual[high].mean(axis=0)]
    pessimistic=np.max(group,axis=0)
    def merge(obj,factor=3.4):
        a=weights*np.exp(-factor*(obj-obj.min()))
        return .60*weights+.40*a/a.sum()
    scales=block_counts(len(residual),min(21,max(h,5)),32,rng)
    loss_draw=(scales@residual)/len(residual)
    soft=np.exp(-3.4*(loss_draw-loss_draw.min(axis=1,keepdims=True)))*weights
    mean_prob=soft/soft.sum(axis=1,keepdims=True)
    # Bounded pseudo-posterior, conditional on date-block loss draws and a fixed family prior.
    post=np.array([rng.dirichlet(45*p+.15) for p in mean_prob])
    post=.65*weights+.35*post
    return {'agg_redundancy':red,'agg_loss_mean':merge(raw),'agg_loss_robust':merge(robust),
            'agg_minimax_env':merge(pessimistic),'agg_bayesian':post.mean(axis=0)},post


def residuals(x,day,mature,active,i,base,actual,sigma,h,rng):
    hist=active
    train,test=standardize(x[hist],x[i])
    n=len(hist)
    y=(np.log1p(actual[hist])-np.log1p(base[hist]))/sigma[hist]
    w=np.ones(n)
    b=ridge(train,y,w,1.6)
    model={'residual_ordinary_ridge':b}
    huber=b
    for _ in range(4):
        err=y-train@huber
        s=max(.30,np.median(np.abs(err-np.median(err)))*1.4826)
        huber=ridge(train,y,np.minimum(1.,1.345*s/np.maximum(1e-7,abs(err))),1.6)
    model['residual_huber']=huber
    # Every environment is computed from origin-known state with a fit-only cutpoint.
    labels=np.sign(train[:,F.index('trailing_vol')+1]) + 2*np.sign(train[:,F.index('index_futures_detail_hhi_z')+1])
    _,lab,count=np.unique(labels,return_inverse=True,return_counts=True)
    clean=(count[lab]>=12)
    env=np.where(clean,.5+.5*n/(len(count)*count[lab]),1.)
    model['residual_environment_balanced']=ridge(train,y,env,1.6)
    m=max(18,n//2)
    prior=ridge(train[:m],y[:m],np.ones(m),3.)
    model['residual_hierarchical']=ridge(train,y,w,1.6,prior=.50*prior)
    res=(y-train@b)**2
    vals=np.array([res[lab==k].mean() if count[k]>=18 else -np.inf for k in range(len(count))])
    pessimistic=1.+.60*(lab==int(np.argmax(vals))) if np.isfinite(vals).any() else w
    model['residual_worst_environment']=ridge(train,y,pessimistic,1.6)
    perm=np.array_split(np.arange(n),max(3,n//min(h,9)))
    order=np.concatenate([perm[j] for j in rng.permutation(len(perm))])
    model['residual_block_permuted']=ridge(train,y[order],w,1.6)
    result={k:(test@v,v) for k,v in model.items()}
    _,delayed=standardize(x[hist],x[max(0,i-5)])
    result['residual_delayed_5']=(delayed@b,b)
    return result,float(np.sqrt(np.mean(test[1:]**2)))


def calibrate(base,pp,truth,ranks):
    yy=(truth>0).astype(float)
    x=logit(np.clip(pp,.025,.975));a=np.c_[np.ones(len(x)),x]
    v=np.array([0.,1.])
    pen=np.diag([.10,.32])
    for _ in range(5):
        z=expit(a@v)
        derivative=z*(1-z)
        right=a.T@(yy-z)/len(x)-pen@(v-np.array([0.,1.]))
        v+=np.linalg.solve((a*derivative[:,None]).T@a/len(x)+pen,right)
    p=float(expit(v[0]+v[1]*logit(np.clip(base.positive(),.025,.975))))
    r=.65*GRID+.35*np.quantile(np.clip(ranks,.005,.995),GRID)
    return base.reweight_sign(.70*base.positive()+.30*p),Law.build(base.quantiles(r)),v


def get_historical(h):
    t=csv('international-target-panel.csv.gz',V22,usecols=['code','day','horizon','ret','mature_ns'])
    t=t[t.code.eq('india')&t.horizon.eq(h)&t.ret.notna()].sort_values('day')
    return t.ret.to_numpy(),t.mature_ns.to_numpy()


def experiment():
    invariant_test()
    q,raw=load_bank()
    anchors=csv('india-protected-point-risk-cases.csv.gz',V22)
    density=csv('analogue-law-atlas.csv',V22)
    density=density[density.model.eq('mixed_metric')].set_index(['horizon','day']).ess
    records=[];booking=[];provenance=[];components=[];coefs=[];disagree=[]
    for (h,clock),t in q.groupby(['horizon','clock']):
        # Archived design selection is fixed by the registry and remains retrospective.
        metadata=t[['expert','family']].drop_duplicates().sort_values('expert')
        core=metadata.expert.to_list()
        distribution={x:g.set_index('day').sort_index() for x,g in t.groupby('expert')}
        date=np.array(sorted(set.intersection(*(set(z.index) for z in distribution.values()))))
        n=len(date)
        if clock!='previous_1700':
            assert n==sum(COHORTS[h][:2])
        direction_anchor,dist_anchor=PARENTS[h,clock]
        base=distribution[dist_anchor].reindex(date)
        ref=distribution[direction_anchor].reindex(date)
        donor_tag = ('V22/v18_corporate_native' if h==5 else 'V22/smooth5') if clock=='native_0910' else (
            'V19/V18_repricing_same_clock' if h==5 else 'V19/price_plus_position_changes')
        families=metadata.family.to_numpy()
        timeline=base.issue_ns.to_numpy(np.int64)
        mature=base.mature_ns.to_numpy(np.int64)
        truth=base.actual.to_numpy(float)
        parent_mid=base['median'].to_numpy(float)
        ns=base.log_scale.to_numpy().clip(.003)
        loss=np.column_stack([distribution[k].reindex(date).crps for k in core])
        pmat=np.column_stack([distribution[k].reindex(date).p for k in core])
        medmat=np.column_stack([distribution[k].reindex(date)['mean'] for k in core])
        wmat=np.stack([distribution[k].reindex(date)[['q10','q50','q90']].to_numpy() for k in core],axis=1)
        hashes=np.column_stack([distribution[k].reindex(date).law_hash for k in core])
        positions=np.column_stack([distribution[k].reindex(date).law for k in core])
        x=asof_features(date,clock)
        point=anchors[anchors.horizon.eq(h)&anchors.model.eq(POINT[h])].set_index('day').pred_vol.reindex(date).to_numpy()
        if clock=='previous_1700':
            point=x[:,F.index('iv_prev')] if h==5 else x[:,F.index('trailing_vol')]
        try:
            breadth=density.loc[h].reindex(date).to_numpy()
        except KeyError:
            breadth=np.full(n,np.nan)
        historic,known=get_historical(h)
        fallback_counts=0
        rng0=np.random.default_rng(SEED+143*h+len(clock))
        random_prior0=rng0.dirichlet(np.repeat(.85,len(core)))
        pit_hist=np.empty(n)
        for i,day in enumerate(date):
            rng=np.random.default_rng(SEED+171*i+11*h+len(clock))
            ts=int(timeline[i])
            prior=past_rows(mature,timeline,ts)
            refs=[piece(raw,k) for k in positions[i]]
            par=refs[core.index(dist_anchor)]
            ds=refs[core.index(direction_anchor)]
            pit_hist[i]=par.cdf(truth[i],False)+rng.random()*(par.cdf(truth[i])-par.cdf(truth[i],False))
            hist=historic[known<ts][-140:]
            assert len(hist)>=45
            simple=Law.build(hist)
            sym=np.quantile(np.abs(hist),(np.arange(64)+.5)/64)
            neutral=Law.build(np.r_[-sym[::-1],sym])
            current_ref=refs[core.index(donor_tag)] if donor_tag in core else refs[core.index(direction_anchor)]
            path_tag='V22/analogue_domestic_history'
            shape=refs[core.index(path_tag)] if path_tag in core else simple
            livepoint=point[i]*np.sqrt(h/252)
            signed=pmat[i];mu=medmat[i]
            check=np.vstack([hashes[prior],hashes[i:i+1]])
            use=exact_unique([tuple(z) for z in check.T])
            models=[refs[k] for k in use]
            fr=family_base(families[use])
            pn=pmat[i,use]
            best_family=Counter(families[use])
            empirical_mean=float(fr@mu[use])
            between=float(fr@np.square(mu[use]-empirical_mean))
            within=float(fr@np.array([j.moments()[1] for j in models]))
            score_cards={'protected_direction':(ds,True,'benchmark'),'protected_distribution':(par,True,'benchmark'),
                         'equal_models':(mix(models),True,'aggregation'),'equal_families':(mix(models,fr),True,'aggregation'),
                         'quantile_family_pool':(transport(models,fr),True,'aggregation'),
                         'fixed_zero_weight':(par,True,'control'),'history_only':(simple,True,'baseline'),
                         'fixed_20pct_history':(mix([par,simple],[.80,.20]),True,'baseline'),
                         'fixed_20pct_neutral':(mix([par,neutral],[.80,.20]),True,'baseline'),
                         'fixed_neutral_sign':(par.reweight_sign(.80*par.positive()+.10),True,'calibration'),
                         'randomized_fixed_weights':(mix(models,random_prior0[use]/random_prior0[use].sum()),True,'control')}
            legal=bool(len(prior)>=MIN)
            ew_low=ew_high=float(fr@pn)
            rr=np.nan;param_std=np.nan;stability=np.nan
            if legal:
                var=x[prior,F.index('trailing_vol')]
                cal_env=np.nan_to_num(var-np.nanmedian(var))
                w,p=training_weights(loss[np.ix_(prior,use)],wmat[prior][:,use],fr,cal_env,rng,h)
                ew_low,ew_high=np.quantile(p@pn,[.1,.9])
                param_std=float((p@pn).std(ddof=1))
                # Compare the same ridge system with a few strictly earlier fits omitting disjoint blocks.
                for key,ix in [('early_half',prior[:max(30,len(prior)//2)]),('late_half',prior[-max(30,len(prior)//2):])]:
                    xx,vv=standardize(x[ix],x[i])
                    yy=(np.log1p(truth[ix])-np.log1p(parent_mid[ix]))/ns[ix]
                    v=ridge(xx,yy,np.ones(len(ix)),1.6)
                    components.append(dict(horizon=h,clock=clock,day=day,fit=key,term=float(vv@v),n=len(ix),last_ns=int(mature[ix].max())))
                stability=abs(components[-1]['term']-components[-2]['term'])
                fn,rr=residuals(x,date,mature,prior,i,parent_mid,truth,ns,h,rng)
                for name,(value,v) in fn.items():
                    gap=float(np.clip(.50*ns[i]*value,-.017,.017))
                    score_cards[name]=(par.transform(location=np.log1p(par.quantiles(.5))+gap),True,'stability')
                    coefs.append(dict(horizon=h,clock=clock,day=day,model=name,target='normalized earlier return error',
                                      intercept=v[0],**dict(zip(F,v[1:],strict=True))))
                sign,pit,v=calibrate(par,base.p.to_numpy()[prior],truth[prior],pit_hist[prior])
                score_cards['calibration_sign_fit']=(sign,True,'calibration')
                score_cards['calibration_pit_fit']=(pit,True,'calibration')
                coefs.append(dict(horizon=h,clock=clock,day=day,model='calibration_sign_fit',target='sign',intercept=v[0],probability_slope=v[1]))
            else:
                fallback_counts+=1
                w={key:fr for key in ('agg_redundancy','agg_loss_mean','agg_loss_robust','agg_minimax_env','agg_bayesian')}
                for a in ('residual_ordinary_ridge','residual_huber','residual_environment_balanced','residual_hierarchical',
                          'residual_worst_environment','residual_block_permuted','residual_delayed_5','calibration_sign_fit','calibration_pit_fit'):
                    score_cards[a]=(par,False,'calibration' if a.startswith('calibr') else 'stability')
            for spec,ww in w.items():
                score_cards[spec]=(mix(models,ww),legal,'aggregation')
                for j,v in enumerate(ww):
                    provenance.append(dict(horizon=h,clock=clock,day=day,method=spec,expert=core[use[j]],family=families[use[j]],weight=v,
                        fit_n=len(prior),last_mature_ns=int(mature[prior].max()) if len(prior) else 0,issue_ns=ts))
            candidates=component_laws(models,par,current_ref,livepoint,shape,h)
            score_cards.update({name:(item,bool(np.isfinite(livepoint)) if name.endswith('scale_only') else True,'component') for name,item in candidates.items()})
            # Conservative share increases with estimation instability, capped before evaluation.
            if legal:
                share=float(np.clip(.12+.24*stability+(.18 if param_std>.018 else 0.),.12,.32))
                combined=mix([par,score_cards['agg_bayesian'][0],neutral],[1-share,.70*share,.30*share])
            else:
                combined=par
            score_cards['uncertainty_guarded_mixture']=(combined,legal,'uncertainty')
            score_cards['complementary_residual_component']=(mix([candidates['component_coherent_joint'],score_cards['residual_huber'][0]],[.65,.35]),legal,'component')
            for k,(law,active,kind) in score_cards.items():
                vals=metrics(law,truth[i],h,float(.35+(i%13)/40))
                records.append(dict(horizon=h,clock=clock,day=day,target=base.target.loc[day],reference=base.reference.loc[day],cohort=base.cohort.loc[day],
                      model=k,kind=kind,active=bool(active),fit_n=len(prior),issue_ns=ts,mature_ns=int(mature[i]),
                      last_mature_ns=int(mature[prior].max()) if len(prior) else 0,law=len(booking),
                      matched_direction_parent=direction_anchor,matched_distribution_parent=dist_anchor,
                      expected_index=base.reference.loc[day]*(1+vals['mean']),
                      calibration_parent=par.positive(),**vals))
                booking.append(law)
            disagree.append(dict(horizon=h,clock=clock,day=day,mature_ns=int(mature[i]),issue_ns=ts,estimation_n=len(prior),
                  future_abs_error=abs(truth[i]-base['mean'].iloc[i]),conditional_mean_disagreement=np.sqrt(between),
                  within_expert_outcome_var=within,between_expert_mean_var=between,pooled_total_var=within+between,
                  ordinary_prob_spread=np.std(signed),family_prob_spread=np.sqrt(fr@np.square(pn-fr@pn)),probability_parameter_se=param_std,
                  probability_weight_model_p10=ew_low,probability_weight_model_p90=ew_high,feature_distance=rr,training_period_shift=stability,
                  implied_volatility=point[i] if h==5 else x[i,F.index('iv_prev')],observed_trailing_vol=x[i,F.index('trailing_vol')],
                  positioning_concentration=x[i,F.index('index_futures_detail_hhi_z')],analogue_effective_n=breadth[i] if clock!='previous_1700' else np.nan,
                  breadth=x[i,F.index('allEQ_advance')],recent_trend=x[i,F.index('prior_ret5')],earnings_activity=x[i,F.index('count9')],
                  global_environment=x[i,F.index('foreign_sd')],snapshot_probability=par.positive(),family_count=len(best_family),
                  conditional_loss_brier=base.brier.iloc[i],conditional_loss_crps=base.crps.iloc[i],tail_miss=int(base.tail_miss.iloc[i]),
                  eligible_experts=len(use),unfiltered_experts=len(core),cohort=base.cohort.iloc[i]))
        print(h,clock,n,'exact matched origins,',len(core),'experts and',fallback_counts,'training warm-up fallbacks',flush=True)
    write('v23-return-cases.csv.gz',pd.DataFrame(records))
    write('ensemble-date-weights.csv.gz',pd.DataFrame(provenance))
    write('model-uncertainty-cases.csv.gz',pd.DataFrame(disagree))
    write('return-residual-coefficient-history.csv.gz',pd.DataFrame(coefs))
    write('training-period-stability-receipts.csv.gz',pd.DataFrame(components))
    store('v23-return-laws.npz',booking)


if __name__=='__main__':
    experiment()
