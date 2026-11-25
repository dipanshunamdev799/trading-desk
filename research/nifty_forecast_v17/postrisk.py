"""Forecast only the unknown suffix of joint session paths after the cash open."""
from .common import *
from .panel import SURPRISE,LIQ
from .paths import cells,SCORECOLS
from research.nifty_forecast_v15.sessions import candles
from research.nifty_forecast_v15.sequential import TICK,log_ticks,numpy_zip
from research.nifty_forecast_v16.model import fit,logistic_offset,predict_probability

PRICE=('known_move','known_rth','gap_seen','prefix_range','prefix_rv','iv_prev','trailing_vol')
ADDITIONS={
  'opening_surprise':SURPRISE,
  'participation':('stock_dispersion','stock_sync','stock_above_open','native_dispersion','financial_lead','bank_sector_surprise'),
  'liquidity_disagreement':LIQ+('etf_tracking_vs_past','cash_vs_gift_repricing','basis_previous_z'),
  'option_surface':('iv_skew','iv_term','iv_curvature','OI_pc_prior','vix_level'),
}


def neighbors(state,current,u):
    present=np.isfinite(current)&(np.isfinite(state).sum(axis=0)>=20)
    if not present.any():
        return np.floor(u*len(state)).astype(int),float(len(state))
    state=state[:,present]
    current=current[present]
    middle=np.nanmedian(state,axis=0)
    state=np.where(np.isfinite(state),state,middle)
    std=state.std(axis=0).clip(.000001)
    distance=np.square(((state-current)/std).clip(-5,5)).mean(axis=1)
    w=np.exp(-.70*(distance-distance.min()))
    w=.72*w/w.sum()+.28/len(w)
    return np.searchsorted(w.cumsum(),u,side='right').clip(0,len(w)-1),float(1/(w@w))


def local(mark,p,refs,loc,h,first,suffix,active):
    rv_now=max(.04,refs[loc])
    ratio=np.clip(rv_now/np.maximum(.04,refs[active]),.55,1.70)
    shape=ratio[:,None]
    initial=suffix[active]*shape
    previous=p[loc-1,3]
    m=np.log(mark/previous)
    first_close=m+initial[:,2]
    day0=np.column_stack((np.full(len(active),first[0]),np.maximum(first[1],m+initial[:,0]),
                          np.minimum(first[2],m+initial[:,1]),first_close))
    blocks=np.log(p[active[:,None]+np.arange(1,h)]/p[active[:,None]+np.arange(h-1),3,None])
    blocks*=ratio[:,None,None]
    origin=np.column_stack((first_close,first_close[:,None]+np.cumsum(blocks[:,:-1,3],axis=1)))
    steps=blocks+origin[:,:,None]
    return np.concatenate((day0[:,None,:],steps),axis=1)


def run():
    f=pd.read_csv(OUT/'intraday-feature-panel.csv.gz',low_memory=False)
    cash=matrix('cash-panel/cash.csv',V16)
    original=matrix('original-target-panel.csv')
    n,_,_=candles((V13/'sources/upstox').glob('nifty-5m-*'),5)
    px=cash.to_numpy(float)
    target_rows=[];passage=[];draws=[];risk_rows=[];risk_laws=[];fit_rows=[]
    folder=OUT/'postopen-paths';folder.mkdir(exist_ok=True)
    for clock in ('09:25','10:20'):
        x=f[f.cutoff.eq(clock)].set_index('day').reindex(cash.index)
        refs=x.iv_prev.ffill().fillna(.12).to_numpy(float)
        support=x.index.to_numpy()
        paths_by_day=np.full((len(cash),3),np.nan)
        known={}
        for i,d in enumerate(cash.index):
            b=n.get(d)
            if i==0 or b is None or pd.isna(x.at[d,'feature_last_bar']):
                continue
            minute=pd.Timestamp(x.at[d,'feature_last_bar'])
            fit_before=b[b.end.le(minute)]
            following=b[b.index>=minute]
            if fit_before.empty or following.empty or following.index[0]!=minute:
                continue
            mark=float(fit_before.close.iloc[-1]);last=float(b.close.iloc[-1])
            paths_by_day[i]=np.log(np.array([following.high.max(),following.low.min(),last])/mark)
            # Historical and current conditioning marks are the same point in the day.
            known[i]=(mark,np.log(np.array([cash.open.iloc[i],fit_before.high.max(),fit_before.low.min()])/px[i-1,3]),minute.isoformat())
        core=x.reindex(columns=PRICE).to_numpy(float)
        combo=x.reindex(columns=PRICE+('stock_dispersion','stock_sync','stock_above_open','relative_volume','abs_surprise_z','etf_tracking_vs_past','financial_lead')).to_numpy(float)
        extra={tag:x.reindex(columns=fields).to_numpy(float) for tag,fields in ADDITIONS.items()}
        extra_core={tag:np.column_stack((core,w)) for tag,w in extra.items()}
        for h in HORIZONS:
            c='cohort_'+str(h)
            lookup=matrix(f'targets-{h}.csv',V14)
            prior_days=pd.Index(['']+list(cash.index[:-1]))
            ivs=lookup.reindex(prior_days)
            actual=ivs.volatility.to_numpy(float)
            rv0=ivs.trailing_at_origin.to_numpy(float)
            threshold=1.25*rv0
            event=(actual>=threshold).astype(float)
            gap=x.gap_seen.to_numpy(float)
            prefix=x.prefix_rv.to_numpy(float)
            parent=np.sqrt(np.maximum(.002,(refs**2+.40*252/h*(gap**2+prefix**2-refs**2/252*.32))))
            adr=np.log(np.maximum(actual,.012)/parent)
            for i in sorted(known):
                d=support[i];ori=support[i-1]
                if i+h-1>=len(px) or d not in original.index or not isinstance(original.at[d,c],str):
                    continue
                co=original.at[d,c];end=support[i+h-1]
                train=np.arange(max(1,i-h+1-HIST),i-h+1)
                train=train[np.isfinite(paths_by_day[train]).all(axis=1)]
                if len(train)<MIN:
                    continue
                rng=np.random.default_rng(SEED+pd.Timestamp(d).toordinal()*41+h)
                rand=rng.random(256)
                real=px[i:i+h]/px[i-1,3]
                mark,known0,t=known[i]
                meta=dict(day=d,origin=ori,target=end,cutoff=clock,horizon=h,cohort=co,known_through=t,last_mature=support[train[-1]+h-1])
                stored={}
                for m,v in [('cash_IV',core),('cash_IV_stock',combo)]:
                    ix,ess=neighbors(v[train],v[i],rand)
                    ar=local(mark,px,refs,i,h,known0,paths_by_day,train[ix])
                    tick=log_ticks(ar)
                    assert np.all(tick[:,:,1]>=np.maximum(tick[:,:,0],tick[:,:,3]))
                    assert np.all(tick[:,:,2]<=np.minimum(tick[:,:,0],tick[:,:,3]))
                    b,e=cells(np.exp(tick*TICK),real,h)
                    target_rows.append(dict(**meta,model=m,ess=ess,**{k:b[k] for k in SCORECOLS}))
                    for a in e.to_dict('records'):
                        level=a['barrier'];side=a['side']
                        already=(np.expm1(known0[1])>=level if side=='upper' else np.expm1(known0[2])<=-level)
                        passage.append(dict(**meta,model=m,known_touch=int(already),**a))
                    stored[m]=tick
                file=folder/f'{clock.replace(":","")}-{h}-{ori}.npz';numpy_zip(file,stored)
                draws.append(dict(**meta,file=file.relative_to(OUT).as_posix(),sha256=sha(file),training_origins=support[train].tolist()))
                tr=train[np.isfinite(adr[train])]
                if len(tr)<MIN or not np.isfinite(parent[i]) or not np.isfinite(actual[i]):
                    continue
                by_lev=float((event[tr].sum()+.75)/(len(tr)+1.5))
                maps={'cash_risk':(np.log(parent[i]),None), 'raw_IV':(np.log(refs[i]),None)}
                for tag,g in ADDITIONS.items():
                    w=extra[tag]
                    fit0=fit(w[tr],adr[tr],155.)
                    mu=np.log(parent[i])+float(np.clip(.48*fit0.values(w[i]),-.28,.28))
                    ex=logistic_offset(extra_core[tag][tr],event[tr],by_lev,170.)
                    prob=predict_probability(ex,extra_core[tag][i],by_lev,.48)
                    maps[tag]=(mu,float(prob))
                    fit_rows.append(dict(**meta,model=tag,**fit0.receipt(g)))
                null=logistic_offset(core[tr],event[tr],by_lev,170.)
                shape=np.quantile(adr[tr]-np.median(adr[tr]),Q)
                for name,(mu,pro) in maps.items():
                    ar=np.exp(shape+mu)
                    mean=float(np.mean(ar));q10,q90=np.quantile(ar,[.1,.9]);ratio=actual[i]**2/mean**2
                    if name=='cash_risk':pro=float(predict_probability(null,core[i],by_lev,.48))
                    if pro is None:pro=float((ar>=threshold[i]).mean())
                    one=float(event[i]);qu=np.quantile(ar,[.1,.25,.5,.75,.9]);dt=actual[i]-qu
                    curve=np.arange(len(ar))*2-len(ar)+1
                    ix=len(risk_laws);risk_laws.append(ar.astype('float32'))
                    risk_rows.append(dict(**meta,law=ix,model=name,actual=actual[i],mean=mean,median=float(np.median(ar)),expansion=one,
                        p=pro,brier=(pro-one)**2,log_loss=-np.log(np.clip(pro if one else 1-pro,.0005,1.)),mae=abs(mean-actual[i]),
                        sq_error=(mean-actual[i])**2,qlike=ratio-np.log(ratio)-1,crps=np.abs(ar-actual[i]).mean()-curve@ar/len(ar)**2,
                        covered=float(q10<=actual[i]<=q90),width=q90-q10,quantile_loss=np.maximum(np.array([.1,.25,.5,.75,.9])*dt,np.array([-.9,-.75,-.5,-.25,-.1])*dt).mean()))
        print('Completed stock-conditioned paths at',clock,flush=True)
    write('postopen-path-scores.csv.gz',pd.DataFrame(target_rows))
    write('postopen-passage-scores.csv.gz',pd.DataFrame(passage))
    write('postopen-volatility-scores.csv.gz',pd.DataFrame(risk_rows))
    save('postopen-path-archive.json',dict(tick=TICK,scenarios=256,rows=draws))
    save('postopen-volatility-fits.json',fit_rows)
    np.savez_compressed(OUT/'postopen-volatility-laws.npz',atoms=np.stack(risk_laws))


if __name__=='__main__':
    run()
