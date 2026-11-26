"""Apply foreign priors and empirical path laws on the original NIFTY dates."""
from .common import *
from .learning import FIELDS,OWN,DAY,train,selected,law,target_array,target_block,eligible,date_country_permute
from .reference import NATIVE_ANCHORS
from .analogues import weighted_quantile
from research.nifty_forecast_v17.weekly import evaluate
from research.nifty_forecast_v20.modeling import direction_weights,blend_laws,weighted_store

DOMESTIC=('reaction_mean','domestic_rotation_finance','eq500_spread5','FII_index_futures_d21',
          'index_futures_detail_hhi_z','iv_prev','trailing_vol','allEQ_advance','weight_top5',
          'effective_expected_contributors','expected_index_contribution','expected_contribution_dispersion')
OFFSHORE=('gift_proxy','expected_gap')
TRANSFER=('loco_transfer','loro_transfer','local_history','local_own_only','local_ridge','pooled_with_context',
          'partial_country','factor_only','global_factor_only','factor_and_innovation','dominant_excluded',
          'country_shuffle','date_block_null','delayed_transfer','low_rank_shared','mechanism_momentum_reversal',
          'mechanism_drawdown_recovery','mechanism_volatility_clustering','mechanism_synchronization_relative','mechanism_breadth_leadership')


def load_laws(root,name):
    z=np.load(root/name)
    return z['atoms'],z['weights'],z['offsets']


def from_book(book,i):
    a,w,e=book
    return a[e[i]:e[i+1]],w[e[i]:e[i+1]]


def domestic_inputs(h):
    cols=['day','cutoff','decision',*DOMESTIC[:8],*OFFSHORE]
    d=csv('asof-features.csv.gz',V20,usecols=cols)
    d=d[d.cutoff.eq('preauction_0855')].set_index('day')
    assert (pd.to_datetime(d.decision,utc=True).dt.tz_convert(IST).dt.strftime('%H:%M')=='08:55').all()
    w=csv('concentration-cases.csv',V21,usecols=['day','horizon','decision','weight_top5','effective_expected_contributors'])
    w=w[w.horizon.eq(h)].set_index('day')
    assert (pd.to_datetime(w.decision,utc=True).dt.tz_convert(IST).dt.strftime('%H:%M')=='08:55').all()
    p=csv('constituent-contribution-cases.csv.gz',V21,usecols=['day','horizon','symbol','return_contribution'])
    p=p[p.horizon.eq(h)].groupby('day').return_contribution.agg(['sum','std'])
    p.columns=DOMESTIC[-2:]
    return d.join(w[list(DOMESTIC[8:10])]).join(p).drop(columns=['decision','cutoff'])


def empirical(center,dist,scale):
    a=np.expm1(np.clip((center+dist)*scale,-1.75,1.4))
    return a,np.full(len(a),1/len(a))


def fit_adaptations(f,h):
    x=f[list(FIELDS)].to_numpy(float)
    y=target_array(h,f)
    codes=f.code.to_numpy();day=f.day.to_numpy();is_india=codes=='india';issue=f.issue_ns.to_numpy()
    actual=f.mature_ns.to_numpy()
    own=selected(OWN)
    result={};receipts=[];prior_cache={}
    for i in f.index[f.cohort.notna()]:
        cut=int(issue[i]);block=(cut//DAY-20089)//10
        fit_cut=int((block*10+20089)*DAY)
        ix=np.flatnonzero(is_india&np.isfinite(y[:,0])&(actual<cut)&(issue<cut))
        if block not in prior_cache:
            foreign=eligible(f,fit_cut)&~is_india
            sy=y[foreign];dy=day[foreign]
            shuffled=date_country_permute(sy,dy,np.random.default_rng(SEED+h+block))
            international=train(x[foreign],sy,dy,own)
            random=train(x[foreign],shuffled,dy,own)
            prior_cache[block]=(international,random,int(actual[foreign].max()),int(foreign.sum()))
        shared,random,last_foreign,n_foreign=prior_cache[block]
        members={}
        for n in (60,120):
            recent=ix[-n:]
            if len(recent)<n:
                continue
            older=ix[max(0,len(ix)-n-120):len(ix)-n]
            historical=train(x[older],y[older],day[older],own,1.65) if len(older)>=45 else None
            dist=law(y[recent,0]);scale=f.raw_daily_sigma[i]*np.sqrt(h)
            for name,penalty,prior,last_ext in (
                    ('zero_centered',1.65,None,0),('ordinary_ridge',.40,None,0),('strong_zero',4.,None,0),
                    ('historical_prior',1.65,historical,0),('foreign_prior',1.65,shared,last_foreign),
                    ('foreign_strong',4.,shared,last_foreign),('foreign_random',1.65,random,last_foreign)):
                m=train(x[recent],y[recent],day[recent],own,penalty,prior)
                center=np.clip(m.predict(x[i:i+1])[0,0],-2,2)
                key=f'{name}_{n}'
                members[key]=(empirical(center,dist,scale),int(max(last_ext,actual[recent].max())))
                receipts.append(dict(day=day[i],horizon=h,model=key,train_n=len(recent),domestic_first=day[recent[0]],
                             domestic_last=day[recent[-1]],last_local_mature_ns=int(actual[recent].max()),foreign_last_mature_ns=last_ext,
                             usable_historical_prior=len(older)>=45,n_historical=len(older),penalty=penalty,
                             foreign_rows=n_foreign if last_ext else 0,prior_fit_cut_ns=fit_cut if last_ext else 0,issue_ns=cut))
        result[day[i]]=members
    return result,pd.DataFrame(receipts)


def ridge_prediction(x,y,d,prior=1.25):
    mod=train(x,y[:,None],d,tuple(range(x.shape[1])),prior)
    return mod


def residual_variants(parent,info,feature,sigma,ix,day,values):
    a,w=parent
    pp=float(w@(a>0))
    out={}
    if len(ix)<45:
        return out
    truth,mean,abs_err,law_scale,pred_p=info.T
    norm_err=(truth-mean)/np.maximum(sigma,1.e-4)
    norm_abs=np.log(np.clip(abs_err/np.maximum(law_scale,.001),.15,5.))
    p_err=(truth>0)-pred_p
    log_a=np.log1p(a)
    ma=float(w@log_a)
    residual=log_a-ma
    xdom,xext,xdirect=feature
    date=day[ix]
    obs=values['ix']
    def fit_measure(data,y,penalty=1.25):
        m=ridge_prediction(data[ix],y[ix],date,penalty)
        return float(m.predict(data[obs:obs+1])[0,0])
    bias=float(np.median(norm_err[ix]))
    for name,data in (('offshore_only',xdirect),('domestic_only',xdom),('international_only',xext),
                      ('combined',np.column_stack([xdom,xext])),('beyond_gift',np.column_stack([xdom,xext,xdirect]))):
        loc=np.clip(fit_measure(data,norm_err)-.45*bias,-.85,.85)*sigma[obs]*.50
        out['location_'+name]=(np.expm1(log_a+loc),w)
        if name=='beyond_gift':
            scale=float(np.clip(np.exp(.26*(fit_measure(data,norm_abs)-np.median(norm_abs[ix]))),.72,1.33))
            out['scale_only']=(np.expm1(ma+residual*scale),w)
            sign=float(np.clip(pp+.46*fit_measure(data,p_err),.03,.97))
            out['sign_only']=(a,direction_weights(a,w,sign))
            asym=float(np.clip(.28*fit_measure(data,norm_err),-.26,.26))
            skew=residual*np.where(residual>=0,1+asym,1-asym)
            out['asymmetry_only']=(np.expm1(ma+skew-(w@skew)),w)
            robust=np.clip(fit_measure(data,np.clip(norm_err,-1.5,1.5),2.),-.65,.65)
            out['robust_location']=(np.expm1(log_a+.48*sigma[obs]*robust),w)
    out['bias_only']=(np.expm1(log_a+np.clip(.45*sigma[obs]*bias,-.025,.025)),w)
    return out


def compare():
    old=csv('protected-india-return-cases.csv.gz')
    protected=load_laws(OUT,'protected-india-return-laws.npz')
    states=csv('international-feature-panel.csv.gz')
    transfer=csv('india-transfer-input-cases.csv.gz')
    atlas=csv('analogue-law-atlas.csv')
    members=csv('analogue-law-members.csv.gz')
    member_laws={i:(a.mapped_terminal.to_numpy(float),a.weight.to_numpy(float)) for i,a in members.groupby('law')}
    new=[];book=[];fits=[];residual_receipts=[]
    for h in ORIGINAL:
        t=target_block(states,h)
        adapt,r=fit_adaptations(t,h);fits.append(r)
        d=t[t.cohort.notna()].set_index('day').sort_index()
        prospects=transfer[transfer.horizon.eq(h)].set_index(['day','model'])
        abroad=np.load(OUT/f'market-forecast-atoms-{h}.npz')['s']
        a=atlas[atlas.horizon.eq(h)&~atlas.is_stress].set_index(['day','model'])
        inputs=domestic_inputs(h).reindex(d.index)
        d0=inputs[list(DOMESTIC)].to_numpy(float)
        off=inputs[list(OFFSHORE)].to_numpy(float)
        ext_cols=('global5','relative5','cross_dispersion','synchronization','global_vix','local_innovation5')
        ext=d[list(ext_cols)].to_numpy(float)
        p_ext=prospects.p.unstack().reindex(d.index)
        v_ext=prospects.rv_forecast.unstack().reindex(d.index)
        ext=np.column_stack([ext,p_ext['loco_transfer'],p_ext['loro_transfer'],v_ext['loco_transfer']])
        sigma=d.raw_daily_sigma.to_numpy()*np.sqrt(h)
        decision=d.issue_ns.to_numpy('int64');mature=d.mature_ns.to_numpy('int64')
        days=d.index.to_numpy()
        for clock in ('preauction_0855','native_0910'):
            ck=old[old.horizon.eq(h)&old.cutoff.eq(clock)]
            anchor=(NATIVE_ANCHORS[h][0] if clock=='native_0910' else 'archived_same_clock')
            secondary=('omit_latest_21_training_origins' if h==5 else 'v19_position_native') if clock=='native_0910' else 'archived_joint_GJR'
            refs={k:s.set_index('day').reindex(d.index) for k,s in ck.groupby('model')}
            base=refs[anchor]
            if clock=='native_0910':
                cutoff=utc_int(pd.DatetimeIndex([stamp(day,'09:10') for day in days]))
            else:
                cutoff=decision
            infos={}
            for k in (anchor,secondary):
                p=refs[k]
                rq=[weighted_quantile(*from_book(protected,int(v)),[.10,.90]) for v in p.law]
                u=np.array(rq)
                infos[k]=np.column_stack([p.actual,p['mean'],p.mae,(u[:,1]-u[:,0])/2.5631,p.p])
            for i,(day,row) in enumerate(d.iterrows()):
                truth=float(base.actual[day]);cp=int(cutoff[i])
                assert abs(truth-row.ret)<2.e-10
                ref_amt=(float(base.reference_close[day]))
                complete={}
                for k,b in refs.items():
                    complete[k]=(from_book(protected,int(b.law[day])),True,0,0,'protected')
                key=prospects.loc[day] if day in prospects.index.get_level_values(0) else None
                for name in TRANSFER:
                    if key is None or name not in key.index:
                        continue
                    v=key.loc[name]
                    trans=empirical(v.center_normalized,abroad[int(v.law)],v.horizon_scale)
                    complete['direct_'+name]=(trans,True,int(v.last_train_ns),0,'international_direct')
                for name,(atoms,last) in adapt[day].items():
                    complete['adapt_'+name]=(atoms,True,last,0,'india_adaptation')
                for name,v in a.loc[day].iterrows():
                    if name=='foreign_stress':
                        continue
                    complete['analogue_'+name]=(member_laws[int(v.law)],True,int(v.last_mature_ns),int(v.members),'market_analogues')
                ix=np.flatnonzero((mature<decision[i])&(decision<decision[i]))[-140:]
                for parent in (anchor,secondary):
                    inherited=complete[parent][0]
                    prefix='parent_' if parent==anchor else 'secondary_'
                    adjustments=residual_variants(inherited,infos[parent],(d0,ext,off),sigma,ix,days,dict(ix=i))
                    last=int(mature[ix].max()) if len(ix) else 0
                    residual_receipts.append(dict(horizon=h,day=day,cutoff=clock,parent=parent,n=len(ix),last_mature_ns=last,
                                                  issue_ns=cp,first_train=days[ix[0]] if len(ix) else None,offshore_input_known=bool(np.isfinite(off[i]).any())))
                    names=('location_offshore_only','location_domestic_only','location_international_only','location_combined',
                           'location_beyond_gift','scale_only','sign_only','asymmetry_only','robust_location','bias_only')
                    for method in names:
                        available=method in adjustments
                        complete[prefix+method]=(adjustments.get(method,inherited),available,last,len(ix),'parent_attribution')
                    for ally,tag,pct in (('analogue_mixed_nearest','mixture_analogues',.25),('analogue_domestic_history','historical_shrinkage',.25),
                                         ('direct_loco_transfer','mixture_transfer',.25),('analogue_foreign_nearest','mixture_foreign_tail',.12)):
                        if ally not in complete:
                            continue
                        atoms,active,timed,n,_=complete[ally]
                        if tag=='mixture_foreign_tail':
                            l,w=atoms
                            z=np.log1p(l);ret=weighted_quantile(z,w,[.1,.90])
                            take=(z<=ret[0])|(z>=ret[1])
                            z=z[take];w=w[take]/w[take].sum()
                            a0,w0=inherited
                            # Move the tail law to the parent location before mixing.
                            atoms=(np.expm1(z-w@z+w0@np.log1p(a0)),w)
                        joint=blend_laws(*inherited,*atoms,pct)
                        complete[prefix+tag]=(joint,active,timed,n,'valid_law_mixture')
                for name,(law0,active,last,n,kind) in complete.items():
                    atoms,w=law0
                    w=np.asarray(w,float);w=w/w.sum()
                    assert np.isfinite(atoms).all() and last<cp
                    quant=weighted_quantile(atoms,w,[.01,.05,.10,.25,.5,.75,.90,.95,.99])
                    v=evaluate(atoms,w,truth)
                    down=.02 if h==5 else .05
                    new.append(dict(horizon=h,day=day,origin=base.origin[day],target_end=base.target_end[day],cutoff=clock,cohort=base.cohort[day],
                            model=name,active=bool(active),kind=kind,law=len(book),reference_close=ref_amt,issue_ns=cp,last_mature_ns=last,n_training=n,
                            expected_index=ref_amt*(1+v['mean']),p_tail_up=float(w@(atoms>down)),p_tail_down=float(w@(atoms<-down)),
                            tail_up_brier=(w@(atoms>down)-(truth>down))**2,tail_down_brier=(w@(atoms<-down)-(truth<-down))**2,
                            **{f'q{k}':float(x) for k,x in zip((1,5,10,25,50,75,90,95,99),quant)},**v))
                    book.append((atoms,w))
        print('Complete NIFTY distributions for',h,'sessions',sum(k['horizon']==h for k in new),'cases',flush=True)
    write('india-forecast-cases.csv.gz',pd.DataFrame(new))
    write('india-adaptation-fit-receipts.csv.gz',pd.concat(fits,ignore_index=True))
    write('india-residual-fit-receipts.csv.gz',pd.DataFrame(residual_receipts))
    weighted_store(OUT/'india-forecast-laws.npz',book)


if __name__=='__main__':
    compare()
