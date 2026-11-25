"""Isolate endpoint-distribution mechanisms and compare probabilistic tails."""
from scipy.special import ndtr

from .common import *
from .data import Daily
from .scores import p_loss, losses
from .sequential import Simulator, RandomPanel, continuous, TICK
from .fitting import RevisionDesign, fit
from .evidence import paired_intervals

END_MODELS=('common_raw_iv','location_at_raw_iv','fitted_risk_without_drift','location_plus_risk',
            'risk_matched_asymmetry','empirical_sign_magnitude','state_risk_only','tail_t6_mixture','episode_tails','analogue_asymmetry')
MARGIN_MODELS=('raw_probability','domestic_probability','sign_shrink_half','historical_prior_mix','bounded_domestic_probability')


def decomposition():
    daily=Daily.load()
    led=read('joint-update-archive.json')
    rec=read('joint-update-receipts.json')
    stats={(x['horizon'],x['origin'],x['checkpoint']):x for x in rec}
    by=dict(tuple(pd.read_csv(OUT/'update-calendar.csv').groupby(['horizon','origin'])))
    tails=[]; out=[]; attribution=[]
    for v in led['files']:
        h,day=v['horizon'],v['origin']
        y=daily.labels[h].loc[day]
        actual=float(y.endpoint_return)
        stop=y.endpoint
        with np.load(OUT/v['file'],allow_pickle=False) as z:
            for row in by[h,day].itertuples(index=False):
                k=row.checkpoint
                if k not in CHECKPOINTS[h]:
                    continue
                s=stats[h,day,k]
                r=row.remaining
                readlaw=lambda name:z[f'k{k:02}_{name}'][:,-1,3].astype(float)*TICK
                iv=readlaw('iv_restart')
                dmu,dsig=s['estimated_models']['domestic']
                df=readlaw('domestic')
                empirical=readlaw('historical')
                a=np.clip(row.realized_price_ratio,.75,1.35)
                assert a==row.realized_price_ratio
                af=readlaw('analogue')
                center=df.mean()
                asym=(af-af.mean())*df.std()/max(.000001,af.std())+center
                forecasts={
                    'common_raw_iv':iv,'location_at_raw_iv':iv+dmu,
                    'fitted_risk_without_drift':iv*dsig/s['raw_iv'],'location_plus_risk':df,
                    'risk_matched_asymmetry':asym,'empirical_sign_magnitude':readlaw('sign_magnitude'),
                    'state_risk_only':readlaw('gjr_restart'),'tail_t6_mixture':readlaw('heavy_tail'),
                    'episode_tails':readlaw('episode_tail'),'analogue_asymmetry':af,
                }
                vectors=np.stack(list(forecasts.values()))
                full_prices=a*np.exp(vectors)-1
                mu,quant,crps,pin=losses(full_prices,actual)
                p=(full_prices>0).mean(axis=1)
                b,ll=p_loss(p,actual>0)
                for j,m in enumerate(forecasts):
                    values=full_prices[j]
                    summary=dict(horizon=h,origin=day,target=stop,asof=row.asof,cohort=row.cohort,checkpoint=k,model=m,
                                 actual=actual,p=p[j],brier=b[j],log_loss=ll[j],crps=crps[j],pinball=pin[j],expected=mu[j],
                                 q10=quant[j,1],q50=quant[j,3],q90=quant[j,5])
                    out.append(summary)
                    if k:
                        continue
                    fixed=.03 if h==5 else .05
                    rel=1.5*y.horizon_sd_at_origin
                    thresholds={'up_fixed':values>=fixed,'down_fixed':values<=-fixed,
                                'up_relative':values>=rel,'down_relative':values<=-rel}
                    outcomes={'up_fixed':actual>=fixed,'down_fixed':actual<=-fixed,'up_relative':actual>=rel,'down_relative':actual<=-rel}
                    for event,hit in thresholds.items():
                        q=float(hit.mean())
                        br,ls=p_loss(q,outcomes[event])
                        tails.append(dict(horizon=h,origin=day,target=stop,cohort=row.cohort,model=m,event=event,actual=int(outcomes[event]),
                                          p=q,brier=float(br),log_loss=float(ls),threshold=fixed if event.endswith('fixed') else rel))
                prior_p=float((a*np.exp(empirical)>1).mean())
                for name,pred in zip(MARGIN_MODELS,[float(p[0]),float(p[3]),.50*float(p[3])+.50*float(p[0]),
                           .82*float(p[3])+.18*prior_p,.96*float(p[3])+.04*.50]):
                    br,ls=p_loss(pred,actual>0)
                    attribution.append(dict(horizon=h,origin=day,target=stop,cohort=row.cohort,checkpoint=k,model=name,probability=pred,
                                            brier=float(br),log_loss=float(ls),actual=int(actual>0)))
    out=pd.DataFrame(out)
    attr=pd.DataFrame(attribution)
    tails=pd.DataFrame(tails)
    write('endpoint-mechanism-scores.csv.gz',out)
    write('endpoint-probability-mechanism-scores.csv.gz',attr)
    write('endpoint-tail-scores.csv.gz',tails)
    for name,v,cols in [('endpoint-mechanism-evidence',out,['checkpoint']),('endpoint-probability-mechanism-evidence',attr,['checkpoint']),
                        ('endpoint-tail-evidence',tails,['event'])]:
        g=v.groupby(['horizon','model',*cols],as_index=False)
        wanted=['brier','log_loss','crps','actual','p','probability','pinball']
        s=g.agg(n=('origin','nunique'),**{m:(m,'mean') for m in wanted if m in v.columns})
        write(name+'.csv',s)


def refit_null():
    sim=Simulator()
    reps=32
    # Refitting and reselection share a matched sparse grid. Use the unmodified input as the paired observed fit.
    out=[]; summaries=[]
    for h in HORIZONS:
        offset=2 if h==5 else 10
        cal=sim.calendar[sim.calendar.horizon.eq(h) & sim.calendar.checkpoint.isin([0,offset])]
        unique=cal.origin.unique()
        chosen=unique[np.linspace(0,len(unique)-1,19,dtype=int)]
        cohorts=cal[cal.origin.isin(chosen)]
        score=np.full((reps+1,len(chosen),4),np.nan)
        for w in cohorts.itertuples(index=False):
            index=sim.d.positions[w.asof]
            y0=sim.d.prices.at[w.target,'close']/sim.d.prices.at[w.origin,'close']-1
            current=w.realized_price_ratio
            n=w.remaining
            iv=sim.fits.iv[index,n-1]
            panel=RandomPanel.create(w.asof)
            baseline=np.exp(continuous(panel,n,iv)[:,-1,3])*current-1
            brier0=float(p_loss((baseline>0).mean(),y0>0)[0])
            for col,model in enumerate(['domestic','full']):
                design,names,which=sim.fits.columns(w.checkpoint,n,model)
                tm=np.arange(max(w.checkpoint,index-n-HIST),index-n)
                assert tm[-1]+n<index
                rhs=sim.fits.responses[n][tm,0]
                block=np.zeros(design.shape[1],bool)
                for group,s in which.items():
                    block[s]=True
                column=col+(2 if w.checkpoint else 0)
                for draw in range(reps+1):
                    rng=np.random.default_rng(SEED+h*1000+index*3+draw*7777) if draw else None
                    cur=.60*fit(design[tm],rhs,225,rng,block).values(design[index])
                    lu=iv*np.sqrt(n/252.)
                    p=float(ndtr((np.log(current)+np.clip(cur,-.65,.65)*lu)/lu))
                    g=brier0-float(p_loss(p,y0>0)[0])
                    score[draw,np.flatnonzero(chosen==w.origin)[0],column]=g
                    out.append(dict(horizon=h,origin=w.origin,asof=w.asof,checkpoint=w.checkpoint,model=model,replicate=draw,
                                    gain=g,matched_control=brier0,fit_mode='observed' if not draw else 'block-shuffled training revisions'))
        ave=np.nanmean(score,axis=1)
        stat=np.max(ave,axis=1)
        pvalue=(1+(stat[1:]>=stat[0]).sum())/(reps+1)
        summaries.append(dict(horizon=h,origins=len(chosen),refitted_draws=reps,candidate_slots=4,
                         selected_observed=float(stat[0]),null_max_mean=float(stat[1:].mean()),
                         null_max_q95=float(np.quantile(stat[1:],.95)),monte_carlo_tail=float(pvalue)))
    write('refit-reselection-null.csv.gz',pd.DataFrame(out))
    write('refit-reselection-evidence.csv',pd.DataFrame(summaries))


def auxiliary():
    specs=[
        ('volatility-transition-scores.csv.gz',['horizon','event'],'iv_raw','brier','expansion'),
        ('volatility-level-scores.csv',['horizon'],'iv_raw','mae','volatility'),
        ('causal-error-scores.csv.gz',['horizon','variable','task'],'matured_frequency','brier','warnings'),
        ('endpoint-tail-scores.csv.gz',['horizon','event'],'common_raw_iv','brier','tails'),
        ('endpoint-mechanism-scores.csv.gz',['horizon','checkpoint'],'common_raw_iv','crps','endpoint mechanisms'),
        ('endpoint-probability-mechanism-scores.csv.gz',['horizon','checkpoint'],'raw_probability','brier','probability shrinkage'),
    ]
    out=[]
    for file,cols,base,metric,category in specs:
        a=pd.read_csv(OUT/file,low_memory=False)
        for group,z in a.groupby(cols):
            if not isinstance(group,tuple):
                group=(group,)
            pivot=z.pivot(index='origin',columns='model',values=metric).sort_index()
            if base not in pivot.columns:
                continue
            compare=pivot.apply(lambda col:pivot[base]-col).drop(columns=[base]).dropna(axis=1,how='all')
            if compare.empty: continue
            h=group[0]
            block=paired_intervals(compare.to_numpy(),h)
            for j,name in enumerate(compare):
                c=pivot[name]; b=pivot[base]
                take=compare[name].notna()
                out.append(dict(category=category,**dict(zip(cols,group)),model=name,control=base,metric=metric,n=int(take.sum()),
                   candidate_loss=c[take].mean(),reference_loss=b[take].mean(),gain=compare[name].mean(),**{k:v[j] for k,v in block.items()}))
    write('secondary-paired-evidence.csv',pd.DataFrame(out))


if __name__=='__main__':
    decomposition()
    refit_null()
    print('Isolated endpoint mechanisms and refit the directional null',flush=True)
