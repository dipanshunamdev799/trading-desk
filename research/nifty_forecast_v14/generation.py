"""Generate common 21-session OHLC laws, with 5-session prefix forecasts."""
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from scipy.special import ndtr, stdtrit

from .common import *
from .data import DOM, INTRA
from .volatility import MINV, MAXV, design_apply, ridge, robust_design, skew_constants

TICK = .00001


def random_panel(day,n=N,steps=STEPS):
    """All candidates consume the same shocks and bridge per origin."""
    seed=SEED+pd.Timestamp(day).toordinal()*37
    rng=np.random.default_rng(seed)
    maker=lambda :rng.standard_normal((n,21)).astype('float32')
    z,gap,latent=maker(),maker(),maker()
    u=rng.random((n,21,4),dtype='float32')
    b=rng.standard_normal((n,21,steps)).astype('float32')
    fraction=np.arange(1,steps+1,dtype='float32')/steps
    bridge=(b.cumsum(axis=2)-b.sum(axis=2)[:,:,None]*fraction)/np.sqrt(np.float32(steps))
    return dict(z=z,u=u,gap=gap,eta=latent,bridge=bridge,frac=fraction,seed=seed)


def student(z,nu,skew=0.):
    p=ndtr(z).astype(float)
    if not skew:
        return stdtrit(nu,p.clip(1.e-7,1-1.e-7))*np.sqrt((nu-2)/nu)
    c,a,b=skew_constants(nu,skew)
    limit=(1-skew)/2
    left=p<limit
    arg=np.where(left,p/(1-skew),.5+(p-limit)/(1+skew))
    t=stdtrit(nu,arg.clip(1.e-7,1-1.e-7))*np.sqrt((nu-2)/nu)
    return (t*np.where(left,1-skew,1+skew)-a)/b


def normalized_pool(values, minimum=20):
    x=np.asarray(values)
    x=x[np.isfinite(x)]
    if len(x)<minimum:
        raise ValueError('Insufficient previously observed innovations')
    x=np.clip(x,np.quantile(x,.004),np.quantile(x,.996))
    return (x-x.mean())/max(x.std(),.0001)


def pool_sample(pool,u):
    return pool[np.minimum((u*len(pool)).astype(int),len(pool)-1)]


def jump_parameters(prior,k,omit=False,shift=False,horizon=21):
    subset=prior.iloc[-210:]
    if omit:
        top=subset.daily_log_return.abs().idxmax()
        index=subset.index.get_loc(top)
        mask=abs(np.arange(len(subset))-index)>7
        subset=subset.iloc[mask]
    flag=subset[f'jump_flag_{k}'].eq(True)
    usable=subset[f'jump_flag_{k}'].notna()
    size=np.sqrt(subset[f'positive_excess_{k}'].loc[flag])*np.sqrt(252)/subset.rv21.loc[flag].clip(.045)
    size=size.dropna().clip(.15,2.8)
    pc=(flag.sum()+1.2)/(usable.sum()+14)
    levels=subset[f'jump_share_{k}']
    current=levels.iloc[:-21].tail(5) if shift else levels.tail(5)
    p=np.clip(pc*(1+.45*(current.mean()-.18)) if current.notna().any() else pc,.035,.19)
    tau2=(np.square(size).sum()+8*.9**2)/(len(size)+8)
    return dict(prob=float(p),sd=float(np.sqrt(tau2)),sample=int(usable.sum()),number=int(flag.sum()),
                history_first=subset.index[0],history_last=subset.index[-1],in_sample_scale=float(np.sqrt(tau2)))


def collapse_daily(bridges,gaps,returns,intraday_sd,jumps,jump_at,fraction):
    # The bridge is conditional on the known continuous component of the close.
    # A discrete jump is added only from its sampled regular-session step onward.
    smooth=returns-gaps-jumps
    low=np.minimum(gaps,returns)
    high=np.maximum(gaps,returns)
    # Vectorize across simulated paths and intraday cells one session at a time.
    for k in range(21):
        regular=intraday_sd[:,k,None]*bridges[:,k,:]+smooth[:,k,None]*fraction
        if np.any(jumps[:,k]):
            regular+=jumps[:,k,None]*(np.arange(len(fraction))>=jump_at[:,k,None])
        high[:,k]=np.maximum(high[:,k],gaps[:,k]+regular.max(axis=1))
        low[:,k]=np.minimum(low[:,k],gaps[:,k]+regular.min(axis=1))
    prior=np.column_stack([np.zeros(len(returns)),returns[:,:-1].cumsum(axis=1)])
    return np.stack([prior+gaps,prior+high,prior+low,prior+returns],axis=2)


def dynamic_paths(name,panel,origin_state,context):
    z=panel['z']
    if name in {'gjr_student','gjr_skew'}:
        model=origin_state[name]
        z=student(z,model['nu'],model['skew'])
    elif name=='historical_innov':
        z=pool_sample(context['r_pool'],panel['u'][:,:,0])
    elif name in {'separate_gap','jump_diffusion','jump_1m','jump_shift','jump_no_episode'}:
        z=student(z,9.)
    n=len(z)
    gap=np.empty((n,21),dtype='float32')
    returns=np.empty_like(gap)
    intraday=np.empty_like(gap)
    jump=np.zeros_like(gap)
    u=panel['u']
    index=np.minimum((u[:,:,2]*len(panel['frac'])).astype(int),len(panel['frac'])-1)
    is_gjr=name in {'gjr_gauss','gjr_iv','gjr_student','gjr_skew','historical_innov','separate_gap',
                    'jump_diffusion','jump_1m','jump_shift','jump_no_episode','trend_persistent'}
    gmodel=origin_state['gjr_ivx'] if name in {'gjr_iv','separate_gap','jump_diffusion','jump_1m',
                                               'jump_shift','jump_no_episode','trend_persistent'} else origin_state.get(name,origin_state['gjr_gauss'])
    market=np.asarray(origin_state['market_anchors']['term_curve'])
    if is_gjr:
        start=gmodel['next_variance']
        if name in {'gjr_iv','separate_gap','jump_diffusion','jump_1m','jump_shift','jump_no_episode','trend_persistent'}:
            start=.70*market[0]+.30*start
        v=np.full(n,start)
    else:
        var=context['ivdaily']**2*10000
        if name=='calibrated_iv':
            var*=context['calibration']**2
        if name=='widened_gauss':
            var*=1.18**2
        v=np.full(n,var)
    latent=name=='latent_sv'
    state=name=='regime_state'
    if latent:
        lv=origin_state['latent_iv']
        log_v=lv['current_center']+np.sqrt(lv['current_var'])*panel['eta'][:,0]
    if state:
        mark=origin_state['two_state']
        state_id=(u[:,0,2]<mark['prob_high'][0]).astype(int)
        sign_id=np.full(n,context['last_sign'],dtype=int)
    prev=np.full(n,context['last_return'])
    g_share=context['gap_share'] if name in {'separate_gap','jump_diffusion','jump_1m','jump_shift','jump_no_episode'} else .28**2
    j=context['jumps'].get(name)
    if j is not None:
        # Reserve the mass of expected discontinuous squared variation within total variance.
        continuous_variance=1-j['prob']*j['sd']**2
    else:
        continuous_variance=1.
    assert continuous_variance>.35
    for k in range(21):
        if latent:
            v=np.exp(log_v)
        if state:
            v=np.asarray(mark['states'])[state_id]
        sd=np.sqrt(np.clip(v,MINV,MAXV))/100.
        if g_share==.28**2:
            gz=panel['gap'][:,k]
        else:
            gz=pool_sample(context['gap_pool'],u[:,k,3])
        gap[:,k]=sd*np.sqrt(g_share)*gz
        intraday[:,k]=sd*np.sqrt((1-g_share)*continuous_variance)
        if j is not None:
            # Independent symmetric sign and magnitude keep zero expected drift.
            shock_z=panel['eta'][:,k]
            jump[:,k]=sd*np.sqrt(1-g_share)*j['sd']*shock_z*(u[:,k,1]<j['prob'])
        if name=='trend_persistent':
            drift=np.clip(context['trend']*.83**k+context['ar1']*prev,-.00155,.00155)
        elif name=='trend_shrink':
            drift=context['trend']*.90**k
        elif name=='simple_drift':
            drift=context['simple_drift']
        elif state:
            continuation=np.asarray(mark['sign_transition'])[sign_id,1]
            drift=.12*sd*(2*continuation-1)
        else:
            drift=0.
        r=gap[:,k]+intraday[:,k]*z[:,k]+jump[:,k]+drift
        returns[:,k]=r
        prev=r
        if is_gjr:
            innovations=(r-drift)*100
            market_risk=market[min(k+1,20)]
            v=gmodel['omega']+(gmodel['alpha']+gmodel['gamma']*(innovations<0))*innovations**2+gmodel['beta']*v+gmodel['xi']*market_risk
        if latent and k<20:
            log_v=lv['mu']+lv['rho']*(log_v-lv['mu'])+np.sqrt(lv['eta_var'])*panel['eta'][:,k+1]+lv['leverage']*np.minimum(0,r/sd)
            log_v=np.clip(log_v,-4.,3.9)
        if state and k<20:
            state_id=(u[:,k+1,2]<np.asarray(mark['transition'])[state_id,1]).astype(int)
            sign_id=(r>0).astype(int)
    return collapse_daily(panel['bridge'],gap,returns,intraday,jump,index,panel['frac'])


def precclose_log_steps(paths):
    c=np.column_stack([np.ones(len(paths)),paths[:,:-1,3]])
    return np.log(paths/c[:,:,None]).astype('float32')


def features_for_path(day,x,y5,y21,daily,bracket,ori):
    idx=daily.index.get_loc(day)
    f=x.loc[day]
    history=daily.iloc[:idx+1]
    old=history.iloc[-210:]
    poolr=normalized_pool(old.daily_log_return/history.rv21.shift().reindex(old.index).clip(.03))
    poolg=normalized_pool(old.gap/history.rv21.shift().reindex(old.index).clip(.03))
    t=mature(y5,day,160)
    ref=y5.iloc[t]
    px=x.reindex(ref.index)
    z,bb,transform=robust_design(px,f.to_frame().T,DOM)
    anchor=px.atm.fillna(px.rv21).to_numpy().clip(.03)
    beta=ridge(z,np.log1p(ref.endpoint_return.to_numpy())/(anchor*np.sqrt(5/252.)),225.)
    drift=float(np.clip(design_apply(bb,beta)[0]*f.atm*np.sqrt(5/252.)/5*.45,-.0012,.0012))
    returns=old.daily_log_return.dropna().to_numpy()
    ar=float(.40*np.clip(np.dot(returns[1:],returns[:-1])/(np.dot(returns[:-1],returns[:-1])+1.e-9),-.32,.32))
    avg=float(np.clip(.30*np.mean(returns[-63:]),-.00055,.00055))
    gap_share=float(np.clip(bracket if np.isfinite(bracket) else f.overnight_share,.035,.53))
    history_iv=np.where(px.atm.notna(),px.atm,px.rv21)
    correction=float(np.clip(np.median(ref.volatility/history_iv),.76,1.27))
    jumps={nm:jump_parameters(history,1 if nm=='jump_1m' else 5,omit=nm=='jump_no_episode',shift=nm=='jump_shift')
           for nm in ['jump_diffusion','jump_1m','jump_shift','jump_no_episode']}
    context=dict(r_pool=poolr,gap_pool=poolg,trend=drift,ar1=ar,simple_drift=avg,last_sign=int(returns[-1]>0),
                 last_return=float(returns[-1]),ivdaily=float(f.atm/np.sqrt(252)),gap_share=gap_share,
                 calibration=correction,jumps=jumps)
    receipt=dict(origin=day,prior_fit_origins=ref.index.tolist(),last_mature=ref.endpoint.max(),
                 causal_surface_day=f.option_day,configured_steps=STEPS,trend=float(drift),
                 normalization=transform,coefficients=beta.tolist(),empirical_ar=float(ar),gap_share=gap_share,
                 r_innovations=int(len(poolr)),gap_innovations=int(len(poolg)),jumps=jumps,calibration=correction)
    return context,receipt


def conditional_weights(t,query,columns):
    a,b,_=robust_design(t,query,columns)
    if not a.shape[1]:
        return np.full(len(a),1/len(a))
    v=np.exp(-.55*np.mean(np.minimum((a-b)**2,16),axis=1))
    return .42/len(v)+.58*v/v.sum()


def block_paths(name,day,x,t,observed_steps,panel):
    f=x.loc[[day]]
    prior=x.loc[t]
    if name=='trend_blocks':
        w=conditional_weights(prior,f,DOM+('cash5','cash21','sign_streak','vrp'))
    elif name=='intraday_blocks':
        w=conditional_weights(prior,f,INTRA+('rv21','atm'))
    else:
        w=np.full(len(t),1/len(t))
    draws=np.searchsorted(np.cumsum(w),np.minimum(panel['u'][:,0,3],.99999997),side='right').clip(0,len(t)-1)
    ref=prior.atm.fillna(prior.rv21).to_numpy()
    scale=np.clip(f.atm.iloc[0]/ref,.45,2.1)[draws]
    steps=observed_steps[draws]*scale[:,None,None]
    prior_close=np.column_stack([np.zeros(len(steps)),steps[:,:-1,3].cumsum(axis=1)])
    return steps+prior_close[:,:,None]


def log_ticks(logs):
    arr=np.rint(logs/TICK)
    if np.max(abs(arr))>=np.iinfo(np.int16).max:
        return arr.astype('int32')
    return arr.astype('int16')


def log_decode(ticks):
    return ticks.astype('float64')*TICK


def range_from_ticks(a,h):
    return np.exp(TICK*a[:,:h,1].max(axis=1))-np.exp(TICK*a[:,:h,2].min(axis=1))


def numpy_zip(file, arrays):
    with ZipFile(file,'w',compression=ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for name,a in arrays.items():
            with z.open(name+'.npy','w',force_zip64=True) as f:
                np.lib.format.write_array(f,np.ascontiguousarray(a),allow_pickle=False)


def coherent_calibration(ticks,training,day,panel):
    n=len(ticks)
    weight=np.ones(n)
    miss=[]; historical_tails=[]
    receipt=[]
    for h in HORIZONS:
        rows=[r for r in training[h] if r['endpoint']<day][-126:]
        assert not rows or max(r['endpoint'] for r in rows)<day
        observed=np.asarray([r['pit'] for r in rows])
        r=range_from_ticks(ticks,h)
        ordered=np.argsort(r,kind='stable')
        p0=np.empty(len(r))
        p0[ordered]=(np.arange(len(r))+.5)/len(r)
        if len(rows)>=24:
            bins=np.minimum((observed*5).astype(int),4)
            count=np.bincount(bins,minlength=5)
            fit=(count+12)/(count.sum()+60)*5
            # Both horizons contribute to the same path weights.
            weight*=np.sqrt(fit[np.minimum((p0*5).astype(int),4)].clip(.65,1.50))
            miss.extend(observed.tolist())
            historical_tails.extend([k['upper_ratio'] for k in rows])
        receipt.append(dict(horizon=h,n=len(rows),last=max((r['endpoint'] for r in rows),default=None),
                            range_upper_exceed=float(np.mean(observed>.90)) if len(rows) else None))
    weight/=weight.sum()
    # Widen a learned tail fraction while maintaining every path's OHLC and both prefixes.
    if len(miss)>=24:
        miss=np.array(miss)
        up=float(np.clip(.09+max(0,np.mean(miss>.9)-.10)*.55,.09,.30))
        low=float(np.clip(.075+max(0,np.mean(miss<.1)-.10)*.45,.075,.24))
        strength=float(np.clip(np.quantile(historical_tails,.85),1.13,1.55))
    else:
        up,low,strength=.13,.09,1.25
    src=panel['u'][:,0,2]
    scale=np.where(src<low,.78,np.where(src>1-up,strength,1.))
    widened=log_ticks(log_decode(ticks)*scale[:,None,None])
    return weight,widened,receipt,dict(upper_mix=up,lower_mix=low,upper_scale=strength)


def make():
    paths_dir=OUT/'joint-paths'
    paths_dir.mkdir(parents=True,exist_ok=True)
    daily=matrix('daily-process-features.csv')
    x=matrix('features-5.csv')
    y={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    origin_state=read('process-states.json')
    gap=pd.read_csv(OUT/'gap-channel-forecasts.csv')
    by_day=gap[gap.horizon.eq(5)&gap.model.eq('offshore_gap')].set_index('origin').conditional_share
    gap=gap[gap.horizon.eq(21)&gap.model.eq('offshore_gap')].set_index('origin').conditional_share
    gap=by_day.combine_first(gap)
    with np.load(OUT/'observed-21.npz',allow_pickle=False) as z:
        steps=precclose_log_steps(z['paths'])
        path_ix=pd.Index(z['origins'])
    assert np.array_equal(path_ix,y[21].index)
    training={h:[] for h in HORIZONS}
    receipts=[]
    models=[n for n in PATH_MODELS if n not in ('joint_pit','joint_tail_width','path_mixture')]
    joint_prefix_checks=0
    for i,day in enumerate(sorted(origin_state)):
        state=origin_state[day]
        panel=random_panel(day)
        context,receipt=features_for_path(day,x,y[5],y[21],daily,gap.get(day,np.nan),state)
        receipt['seed']=panel['seed']
        t=y[21].index[mature(y[21],day,210)]
        receipt.update(block_training=t.tolist(),block_last_mature=y[21].loc[t,'endpoint'].max())
        lookup=path_ix.get_indexer(t)
        encoded={}
        for name in models:
            if name.endswith('_blocks'):
                p=block_paths(name,day,x,t,steps[lookup],panel)
            else:
                p=dynamic_paths(name,panel,state,context)
            assert np.isfinite(p).all()
            a=log_ticks(p)
            assert np.all(a[:,:,1]>=np.maximum(a[:,:,0],a[:,:,3]))
            assert np.all(a[:,:,2]<=np.minimum(a[:,:,0],a[:,:,3]))
            encoded[name]=a
        selector=panel['u'][:,0,3]
        mixed=encoded['constant_iv'].astype('int32')
        for lo,hi,name in [(.30,.60,'gjr_iv'),(.60,.80,'jump_diffusion'),(.80,1.01,'iv_scaled_blocks')]:
            mask=(selector>=lo)&(selector<hi)
            mixed[mask]=encoded[name][mask]
        mixed=log_ticks(log_decode(mixed))
        weights,widened,cal,ws=coherent_calibration(mixed,training,day,panel)
        encoded['path_mixture']=mixed
        encoded['joint_tail_width']=widened
        encoded['joint_pit_weights']=weights
        receipt['calibration_history']=cal
        receipt['width_fit']=ws
        for h in HORIZONS:
            if day not in y[h].index or pd.isna(y[h].at[day,'cohort']):
                continue
            realized=y[h].at[day,'range']
            r=range_from_ticks(mixed,h)
            # PIT contributions are recorded now and can enter a later fit only after maturity.
            training[h].append(dict(origin=day,endpoint=y[h].at[day,'endpoint'],pit=float(np.mean(r<=realized)),
                upper_ratio=float(realized/np.quantile(r,.90)),horizon=h))
        file=paths_dir/(day+'.npz')
        numpy_zip(file,encoded)
        receipt['file']='joint-paths/'+file.name
        receipt['sha256']=sha(file)
        receipt['samples']=N
        receipts.append(receipt)
        if day in y[5].index and day in y[21].index and pd.notna(y[5].at[day,'cohort']) and pd.notna(y[21].at[day,'cohort']):
            joint_prefix_checks+=len(PATH_MODELS)
        if (i+1)%40==0:
            print('Archived joint simulations',i+1,'/',len(origin_state),flush=True)
    save('joint-path-ledger.json',dict(days=len(receipts),models=PATH_MODELS,tick=TICK,
        reference='log price relative to frozen cash origin. Column order open, high, low, close.',
        prefix='Each origin has one 21-session law. The weekly forecast uses first five sessions and the same path weights.',
        path_mixture={'constant_iv':.30,'gjr_iv':.30,'jump_diffusion':.20,'iv_scaled_blocks':.20},
        raw_recipe='joint_pit uses path_mixture atoms with the archived joint_pit_weights; all other arrays are equally weighted.',
        common_origins_family_checks=joint_prefix_checks,rows=receipts))
    write('joint-rolling-calibration.csv',pd.DataFrame(training[5]+training[21]))
    print('Completed',len(receipts),'joint path origins across',len(PATH_MODELS),'mechanisms',flush=True)


if __name__=='__main__':
    make()
