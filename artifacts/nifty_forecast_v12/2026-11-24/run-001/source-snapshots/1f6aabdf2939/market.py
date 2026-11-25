"""Walk-forward physical forecast mapping, market-scale heads and falsification controls."""
from dataclasses import dataclass
import warnings

import joblib
from scipy.special import expit,logit
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression,Ridge
from .common import *
from .features import DOM,ETF,FUT,GLOB,INTRA,OPT_CORE,REAL,SCHEDULE,SHOCK,XJOINT
from research.nifty_forecast_v9.run_models import cohort_queries,score_law
from research.nifty_forecast_v10.targets import buckets
from research.nifty_forecast_v8.models import canonical

MAIN='J11_EXCLUDE_B_ROT'
ALTERNATE='O_NATIVE_PHASE0'
NEUTRAL='NEUTRAL'
HISTORY='HISTORY'
MAX_ABS_LAW=.88


def spec(kind,group=(),parent='V12_STAT',**extra):
    return {'kind':kind,'columns':list(group),'parent':parent,**extra}


def registered():
    hist=spec('stat',parent='HISTORY',base=HISTORY)
    main={
      'V12_STAT':spec('stat',parent=MAIN), 'V12_NATIVE_STAT':spec('stat',parent=ALTERNATE,base=ALTERNATE),
      'V12_HIST':hist, 'V12_NEUTRAL':spec('stat',parent=NEUTRAL,base=NEUTRAL),
      'V12_RV_PATH':spec('raw_rv',parent='V12_STAT'),
      'V12_RV_SCALE':spec('scale',REAL),
      'V12_STRADDLE_SCALE':spec('scale',REAL+['straddle_horizon_scaled'],'V12_RV_SCALE',option=True),
      'V12_IV_LEVEL':spec('scale',REAL+['iv_nearest'],'V12_RV_SCALE',option=True),
      'V12_IV_SCALE':spec('scale',REAL+OPT_CORE,'V12_IV_LEVEL',option=True),
      'V12_IV_NATIVE':spec('scale',REAL+OPT_CORE,'V12_NATIVE_RV',option=True,base=ALTERNATE),
      'V12_NATIVE_RV':spec('scale',REAL,'V12_NATIVE_STAT',base=ALTERNATE),
      'V12_IV_NEUTRAL':spec('scale',REAL+OPT_CORE,'V12_NEUTRAL_RV',option=True,base=NEUTRAL),
      'V12_NEUTRAL_RV':spec('scale',REAL,'V12_NEUTRAL',base=NEUTRAL),
      'V12_IV_ASYMMETRY':spec('asym',REAL+OPT_CORE+['iv_curvature'],'V12_IV_SCALE',option=True),
      'V12_FUTURES_SCALE':spec('scale',REAL+OPT_CORE+FUT,'V12_IV_SCALE',option=True),
      'V12_GLOBAL_SCALE':spec('scale',REAL+OPT_CORE+GLOB,'V12_IV_SCALE',option=True),
      'V12_INTRA_SCALE':spec('scale',REAL+OPT_CORE+INTRA,'V12_IV_SCALE',option=True,eligible=['intra_sector_risk']),
      'V12_ETF_SCALE':spec('scale',REAL+OPT_CORE+ETF,'V12_IV_SCALE',option=True),
      'V12_SURFACE_TAIL_SCALE':spec('scale',REAL+OPT_CORE+['density_forward_skew','density_external_mass','density_priced_down5'],
                                   'V12_IV_SCALE',option=True,density=True),
      'V12_DOM_LOCATION':spec('loc',DOM), 'V12_FUTURES_LOCATION':spec('loc',DOM+FUT,'V12_DOM_LOCATION'),
      'V12_JOINT_LOCATION':spec('loc',DOM+FUT+OPT_CORE+XJOINT,'V12_FUTURES_LOCATION',option=True),
      'V12_DOM_IV':spec('joint',REAL+OPT_CORE,'V12_IV_SCALE',option=True,location=DOM),
      'V12_JOINT_IV':spec('joint',REAL+OPT_CORE+XJOINT,'V12_DOM_IV',option=True,location=DOM+FUT+XJOINT),
      'V12_EVENT_RV':spec('scale',REAL+SCHEDULE+SHOCK,'V12_RV_SCALE',event=True),
      'V12_EVENT_HISTORY':spec('event_history',parent='V12_HIST',base=HISTORY,event=True),
      'V12_EVENT_IV':spec('scale',REAL+OPT_CORE+SCHEDULE+SHOCK,'V12_EVENT_RV',event=True,option=True),
      'V12_EVENT_IV_INCREMENT':spec('scale',REAL+OPT_CORE+SCHEDULE+SHOCK,'V12_IV_SCALE',event=True,option=True),
      'V12_DIVERGENCE':spec('disagreement',(),MAIN,option=True,density=True),
    }
    for name,setting in [('LAG2','LAG2'),('LAG5','LAG5'),('SAME_CLOSE','SAME_CLOSE'),('LIQUID','LIQUID'),
              ('SETTLEMENT','SETTLEMENT'),('BRACKET','BRACKET'),('LONGER','LONGER'),('FUTURE_FORWARD','FUTURE_FORWARD'),
              ('RATE_ZERO','RATE_ZERO'),('RATE_HIGH','RATE_HIGH')]:
        fields=REAL+OPT_CORE
        if name=='BRACKET':fields=REAL+['iv_bracket','iv_term','iv_change','iv_skew']
        main[f'V12_IV_{name}']=spec('scale',fields,'V12_IV_SCALE',option=True,version=setting,
                                    diagnostic=name in ['LAG2','LAG5','SAME_CLOSE','RATE_ZERO','RATE_HIGH'])
    for mode in ['roll21','roll42','permuted','noise']:
        columns=REAL+[f'noise_{i}' for i in range(5)] if mode=='noise' else REAL+OPT_CORE
        main['V12_CONTROL_'+mode.upper()]=spec('scale',columns,'V12_IV_SCALE',option=True,perturb=mode,diagnostic=True)
    q={
      'Q12_RAW':spec('q_raw',parent=MAIN,diagnostic=True,density=True),
      'Q12_NATURALLY_ALIGNED':spec('q_raw',parent=MAIN,version='NATURAL',diagnostic=True,density=True),
      'Q12_BLACK_ATM':spec('q_black',parent='Q12_RAW',diagnostic=True,density=True),
      'Q12_FIXED_UNCALIBRATED_MIX':spec('q_mix_raw',parent=MAIN,diagnostic=True,density=True),
      'P12_Q_LOCATION':spec('q_loc',parent='Q12_RAW',density=True),
      'P12_Q_SCALE':spec('q_scale',parent='P12_Q_LOCATION',density=True),
      'P12_Q_TILT':spec('q_tilt',parent='P12_Q_SCALE',density=True),
      'P12_Q_PHYSICAL_MIX':spec('q_mix',parent=MAIN,density=True),
      'P12_Q_HIST_FALLBACK':spec('q_fallback',parent='P12_Q_PHYSICAL_MIX',density=True),
    }
    for v in ['LIQUID','SETTLEMENT','SMOOTH','TRUNCATED','LONGER','LAG2','LAG5','FUTURE_FORWARD']:
        q[f'Q12_{v}']=spec('q_raw',parent='Q12_RAW',version=v,density=True,diagnostic=True)
        if v in ['LIQUID','SETTLEMENT','SMOOTH','TRUNCATED','LONGER']:
            q[f'P12_Q_{v}']=spec('q_mix',parent='P12_Q_PHYSICAL_MIX',version=v,density=True)
    return main,q


@dataclass
class TrainScale:
    columns:list

    def fit(self,x):
        a=x[self.columns].replace([np.inf,-np.inf],np.nan)
        self.med=a.median().fillna(0.)
        self.sd=a.std().fillna(1.).clip(lower=1e-7)
        z=((a.fillna(self.med)-self.med)/self.sd).to_numpy()
        ids,self.aliases=canonical(self.columns,np.c_[z.T,a.notna().to_numpy().T])
        if not len(ids):raise ValueError('Missing features')
        self.columns=[self.columns[j] for j in ids]
        self.med=self.med.loc[self.columns]
        self.sd=self.sd.loc[self.columns]
        return self

    def transform(self,x):
        z=x[self.columns].replace([np.inf,-np.inf],np.nan).fillna(self.med)
        return ((z-self.med)/self.sd).clip(-6,6).to_numpy(float)


def forecast_width(d):
    mu=d.w@d.a
    return max(float(np.sqrt(d.w@((d.a-mu)**2))),.003)


def resize(d,center,scale,asymmetry=0.):
    a=d.a-(d.w@d.a)
    if asymmetry:
        a=a*np.where(a<0,np.exp(-asymmetry),np.exp(asymmetry))
        a-=d.w@a
    a=np.maximum(center+a*scale,-MAX_ABS_LAW)
    return Distribution(a,d.w)


def priced_normal(row):
    scale=float(row.iv_target_total_sd)
    drift=float(row.option_forward_basis)*.65
    z=norm.ppf((np.arange(199)+.5)/199)
    return Distribution(np.expm1(drift-.5*scale*scale+scale*z))


def fold_risk(s,x,t,q,y,h):
    own=x.loc[t]
    test=x.loc[q]
    columns=s['columns']
    scale=TrainScale(columns).fit(own)
    past=scale.transform(own)
    ahead=scale.transform(test)
    if s.get('perturb') in ['roll21','roll42','permuted']:
        selected=[i for i,n in enumerate(scale.columns) if n not in REAL]
        if s['perturb'].startswith('roll'):
            past[:,selected]=np.roll(past[:,selected],int(s['perturb'][4:]),axis=0)
        else:
            chunks=np.array_split(past[:,selected],max(2,len(past)//15))
            rng=np.random.default_rng(SEED+h)
            past[:,selected]=np.concatenate([chunks[i] for i in rng.permutation(len(chunks))])
    rvol=x.loc[t,'rv21'].clip(lower=.02).to_numpy()
    train_r=y.loc[t,'return'].to_numpy()
    annual=np.log(y.loc[t,'volatility'].clip(lower=.015))
    signed=np.clip(train_r/(rvol*np.sqrt(h/252)),-3,3)
    # Calibrate log terminal magnitude against an ex-ante scale. Realized path risk has its own head.
    magnitude=np.log(np.maximum(abs(train_r)/np.sqrt(h/252),.012))
    skew_target=np.clip(signed**3,-6,6)
    output=np.column_stack([annual,magnitude,skew_target])
    model=Ridge(alpha=180).fit(past,output)
    fitted=model.predict(ahead)
    p0=np.exp(.80*fitted[:,0]+.20*float(annual.mean()))
    endscale=np.exp(.77*fitted[:,1]+.23*float(magnitude.mean()))
    # Geometric abs error is not directly the standard deviation. Calibrate
    # the realized-to-model factor on mature historical returns with a floor.
    errscale=np.exp(model.predict(past)[:,1])
    ratio=np.clip((abs(train_r)/np.sqrt(h/252))/np.maximum(errscale,.01),0,5)
    correction=max(.9,float(np.sqrt(np.mean(ratio**2))))
    terminal_std=endscale*correction*np.sqrt(h/252)
    asym=np.clip((fitted[:,2]-np.mean(skew_target))*.07,-.14,.14)
    return p0,terminal_std,asym,{'risk_model':model,'risk_scale':scale,'terminal_correction':correction}


def fit_location(cols,x,t,q,y):
    scale=TrainScale(cols).fit(x.loc[t])
    reg=Ridge(alpha=250).fit(scale.transform(x.loc[t]),y.loc[t,'return'])
    mu=np.clip(reg.predict(scale.transform(x.loc[q])),-.075,.075)
    return mu,{'location_model':reg,'location_scale':scale}


def prices_data(d,stat):
    mu=float(d.w@d.a);sig=forecast_width(d)
    direction=float(d.w[d.a>0].sum())
    return {'priced_positive_mass':direction,'priced_mean':mu,'priced_std':sig,'priced_q10':float(d.quantile(.10)),
         'priced_q90':float(d.quantile(.90)),'priced_abs':float(d.w@abs(d.a)),
         'priced_left5':float(d.w[d.a<-.05].sum()),
         'stat_positive':float(stat.w[stat.a>0].sum()),'stat_mean':float(stat.w@stat.a),'stat_std':forecast_width(stat),
         'stat_q10':float(stat.quantile(.1)),'stat_q90':float(stat.quantile(.9)),'stat_abs':float(stat.w@abs(stat.a)),
         'stat_left5':float(stat.w[stat.a<-.05].sum())}


def difference(stats):
    return pd.DataFrame({f'gap_{x}':stats[k]-stats[j] for x,k,j in [
       ('p','priced_positive_mass','stat_positive'),('mean','priced_mean','stat_mean'),('width','priced_std','stat_std'),
       ('q10','priced_q10','stat_q10'),('q90','priced_q90','stat_q90'),('abs','priced_abs','stat_abs'),
       ('tail5','priced_left5','stat_left5')]},index=stats.index)


def price_calibration(raw,t,y):
    p=np.array([raw[d].w[raw[d].a>0].sum() for d in t])
    width=np.array([forecast_width(raw[d]) for d in t])
    r=y.loc[t,'return'].to_numpy()
    k=np.clip(np.sqrt(np.mean(np.clip((r-np.mean(r))/width,-5,5)**2)),.70,1.50)
    target=r>0
    model=None
    if min(target.sum(),(~target).sum())>=8:
        model=LogisticRegression(C=.10,max_iter=500).fit(logit(np.clip(p,.015,.985))[:,None],target)
    return k,model


def recenter_probability(d,p):
    pos=d.a>0
    a=d.w[pos].sum()
    if min(a,1-a)<1e-8:return d
    w=d.w*np.where(pos,p/a,(1-p)/(1-a))
    return Distribution(d.a,w)


def transform_market(s,x,tr,query,y,h,stat,qs,disagree,prior,cutoff):
    code=s['kind'];result=[];risk=None;fitobj={}
    if code=='stat':return stat,None,fitobj
    if code=='raw_rv':return stat,x.loc[query,'rv21'].to_numpy(float),fitobj
    if code=='event_history':
        flags=x[SCHEDULE].gt(.5)
        for k in SHOCK:flags[k]=x[k].gt(x.loc[tr,k].quantile(.80))
        populations={}
        for k in flags:
            match=tr[flags.loc[tr,k].to_numpy()]
            if len(match)>=12:populations[k]=Distribution(y.loc[match[-126:],'return'])
        for day,law in zip(query,stat):
            matched=[populations[k] for k in populations if flags.at[day,k]]
            result.append(mixture([law,mixture(matched)],[.65,.35]) if matched else law)
        return result,None,{'eligible_event_counts':{k:int(flags.loc[tr,k].sum()) for k in flags}}
    if code=='q_raw':return [qs[d] for d in query],None,fitobj
    if code=='q_black':return [priced_normal(x.loc[d]) for d in query],None,fitobj
    if code=='q_mix_raw':return [mixture([d,qs[k]],[.8,.2]) for d,k in zip(stat,query)],None,fitobj
    if code.startswith('q_'):
        k,tilt=price_calibration(qs,tr,y)
        fitobj={'width_multiplier':k,'probability_calibrator':tilt}
        for day,d in zip(query,stat):
            q=qs[day];center=float(d.w@d.a)
            if code=='q_loc':result.append(resize(q,center,1.));continue
            physical=resize(q,center,k)
            if code!='q_scale' and tilt is not None:
                prob=float(tilt.predict_proba([[logit(np.clip(q.w[q.a>0].sum(),.015,.985))]])[0,1])
                p_stat=float(d.w[d.a>0].sum())
                physical=recenter_probability(physical,.55*prob+.45*p_stat)
            out=physical if code in ['q_scale','q_tilt'] else mixture([d,physical],[.75,.25])
            if code=='q_fallback':out=mixture([out,Distribution(prior)],[.75,.25])
            result.append(out)
        return result,None,fitobj
    if code=='disagreement':
        past=disagree.index.intersection(tr)
        if len(past)<24:return stat,None,{'fallback':'less than 24 earlier matured archived disagreements'}
        g=difference(disagree)
        scale=TrainScale(list(g)).fit(g.loc[past])
        target=y.loc[past,'return']-disagree.loc[past,'stat_mean']
        ridge=Ridge(alpha=250).fit(scale.transform(g.loc[past]),target)
        shifts=np.clip(.30*ridge.predict(scale.transform(g.loc[query])),-.007,.007)
        return [resize(d,float(d.w@d.a)+v,1.) for d,v in zip(stat,shifts)],None,{'disagreement_model':ridge,'scale':scale,'paired_train':list(past)}
    risk=None;width=None;asym=None;shifts=np.zeros(len(query))
    if code in ['scale','joint','asym']:
        risk,width,asym,fitobj=fold_risk(s,x,tr,query,y,h)
    if code in ['loc','joint']:
        shifts,params=fit_location(s.get('location',s['columns']),x,tr,query,y)
        fitobj.update(params)
    for j,d in enumerate(stat):
        mu=float(d.w@d.a)
        target=mu if code not in ['loc','joint'] else mu+np.clip(.35*(shifts[j]-mu),-.012,.012)
        ratio=1. if width is None else float(np.clip((width[j]/forecast_width(d))**.55,.72,1.45))
        skew=float(asym[j]) if code=='asym' else 0.
        result.append(resize(d,target,ratio,skew))
    return result,risk,fitobj


def separate_masks(s,x,qs):
    mask=pd.Series(True,index=x.index)
    if s.get('option'):mask &= x.surface_available & x.iv_nearest.notna()
    if s.get('density'):mask &= x.index.isin(qs)
    if s.get('eligible'):mask &= x[s['eligible']].notna().all(axis=1)
    if s.get('version')=='BRACKET':mask &= x.iv_bracket.notna()
    return mask


def common_history(y,first,x,train_mask):
    mature=y.index[y.endpoint.notna()&y.endpoint.lt(first)&y['return'].notna()]
    eligible=mature[train_mask.reindex(mature).fillna(False).to_numpy()]
    return eligible,mature


def meta_record(h,cohort,fold,model,chosen):
    return {'horizon':h,'cohort':cohort,'fold':fold,'model':model,'cutoff':chosen}


def run(batch):
    main,q=registered()
    cfg={'market':main,'priced':q}[batch]
    save(f'{batch}-registry.json',{'registered_at':now(),'models':cfg,'implementation':sha(SRC/'market.py'),
          'strict_maturity':'Train endpoints < first monthly refit origin. Fit scalers, variance heads, downside mapping and thresholds inside that fit.',
          'default_prior':'V11 J11_EXCLUDE_B_ROT. Raw priced laws and merged raw diagnostics are explicitly labelled Q.'})
    price=matrix('price.csv')
    stat=original_laws({MAIN,ALTERNATE,NEUTRAL,HISTORY})
    qlaw={(int(h),v,k):a for (h,v,k,_),a in bundle_entries(OUT/'laws/aligned-Q.npz')}
    align=pd.read_csv(OUT/'horizon-alignment.csv')
    saved=[];keys=[];laws=[];attempt=[];diagnostics=[];event_flags=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv')
        reference=cohort_queries(h)
        versions=sorted({s.get('version','TRADE') for s in cfg.values()}|{'TRADE'})
        x={k:matrix(f'features/{h}-{k}.csv',OUT) for k in versions}
        qs={k:{day:d for (hh,v,day),d in qlaw.items() if hh==h and k==v} for k in versions}
        timing=align[(align.horizon.eq(h))&align.version.eq('TRADE')].set_index('origin')
        disagreement=pd.DataFrame([{'origin':d,**prices_data(qs['TRADE'][d],stat[h,MAIN,d])}
                           for d in reference.origin if d in qs['TRADE'] and (h,MAIN,d) in stat]).set_index('origin')
        for (cohort,fold),g in reference.groupby(['split','fold'],sort=False):
            first=g.origin.min()
            ss=x['TRADE']
            clean=pd.Series(True,index=ss.index)
            eligible,mature=common_history(y,first,ss,clean)
            assert len(eligible)>=70
            base_cut=np.quantile(y.loc[mature[-252:],'return'],[.1,.3,.5,.7,.9])
            past=y.loc[mature[-252:],'return'].to_numpy()
            cuts={name:float(ss.loc[mature,name].quantile(.80)) for name in SHOCK}
            for r in g.itertuples():
                d=r.origin;feature=ss.loc[d]
                meta={'origin':d,'endpoint':r.endpoint,'horizon':h,'cohort':cohort,'fold':fold}
                for name in SCHEDULE:event_flags.append({**meta,'event':name,'active':bool(feature[name]>.5),'threshold':.5})
                for name in SHOCK:event_flags.append({**meta,'event':name,'active':bool(feature[name]>cuts[name]),'threshold':cuts[name]})
                if d in disagreement.index:
                    a=disagreement.loc[d].to_dict()
                    a.update(realized_return=r.realized_return,realized_abs=abs(r.realized_return),realized_vol=float(y.loc[d,'volatility']),
                             priced_expiry=timing.at[d,'expiry'],priced_source_day=timing.at[d,'option_source_day'],
                             quoted_iv=timing.at[d,'iv_nearest'],implied_move=timing.at[d,'straddle_horizon_scaled'],
                             skew=timing.at[d,'iv_skew'],term=timing.at[d,'iv_term'])
                    diagnostics.append({**meta,**a})
            for name,s in cfg.items():
                item=meta_record(h,cohort,fold,name,first)
                version=s.get('version','TRADE')
                a=x[version]
                raw=qs[version]
                mask=separate_masks(s,a,raw)
                t,_=common_history(y,first,a,mask)
                group=g[mask.loc[g.origin].to_numpy()]
                if version=='NATURAL':
                    # Ex-post evaluation restriction. It is never supplied as a predictor or used to choose a strike.
                    e=align[(align.horizon.eq(h))&align.version.eq(version)].set_index('origin')
                    group=group[e.loc[group.origin,'natural_realized'].eq(True).to_numpy()]
                query=list(group.origin)
                if not query:
                    attempt.append({**item,'status':'unestimated','reason':'No valid option/price observations in fold'});continue
                training_needed=s['kind'] not in ['stat','q_raw','q_black','q_mix_raw','raw_rv']
                if training_needed and len(t)<42:
                    attempt.append({**item,'status':'unestimated','reason':'Fewer than 42 prior mature eligible outcomes'});continue
                base=s.get('base',MAIN)
                base_laws=[stat[h,base,d] for d in query]
                try:
                    d,risk,fitobj=transform_market(s,a,t,query,y,h,base_laws,raw,disagreement,past,first)
                    ref=f'models/{batch}/{h}-{cohort}-{fold}-{name}.joblib'
                    path=OUT/ref;path.parent.mkdir(parents=True,exist_ok=True)
                    assert not len(t) or y.loc[t,'endpoint'].max()<first
                    joblib.dump({'fit':fitobj,'training':list(t),'pool':list(mature[-252:]),'query':query,'specification':s},path,compress=2)
                    for j,(r,law) in enumerate(zip(group.itertuples(),d)):
                        score={**score_law(h,fold,name,r,law,float(price.close.loc[r.origin]),cohort),**buckets(law,r.realized_return,base_cut)}
                        score['absolute_return_error']=abs(float(law.w@abs(law.a))-abs(r.realized_return))
                        if risk is not None:
                            score['forecast_path_volatility']=risk[j]
                            score['realized_path_volatility']=y.at[r.origin,'volatility']
                            score['path_volatility_mae']=abs(risk[j]-score['realized_path_volatility'])
                        saved.append(score);keys.append((h,name,r.origin,r.endpoint));laws.append(law)
                    item.update(status='ok',training=len(t),training_last_endpoint=y.loc[t,'endpoint'].max() if len(t) else None,
                                quotes=len(group),file=ref,sha256=sha(path),version=version)
                except (KeyError,ValueError,np.linalg.LinAlgError) as error:
                    item.update(status='unestimated',reason=str(error))
                attempt.append(item)
        print(batch,h,'sessions;',len(saved),'predictions',flush=True)
    write(f'{batch}-predictions.csv',pd.DataFrame(saved))
    save(f'{batch}-ledger.json',attempt)
    save(f'{batch}-laws.json',pack_bundle(f'laws/{batch}.npz',keys,laws))
    if batch=='market':
        write('expectations-vs-statistics.csv',pd.DataFrame(diagnostics))
        write('event-origin-states.csv',pd.DataFrame(event_flags))


if __name__=='__main__':
    import sys
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',category=RuntimeWarning)
        run(sys.argv[1])
