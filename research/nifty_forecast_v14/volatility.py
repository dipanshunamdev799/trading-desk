"""Causal stochastic-volatility fits shared by both forecast horizons."""
from scipy.optimize import minimize
from scipy.signal import lfilter
from scipy.special import gammaln
from scipy.stats import norm, spearmanr

from .common import *
from .data import BASE, DOM, GLOBAL, INTRA

MINV = .018  # Percent-point squared variances during fitting.
MAXV = 70.
RIDGE_RISK = {
    'har': ('rv5','rv21','rv63','ewma_fast','ewma_slow'),
    'har_iv': ('rv5','rv21','rv63','ewma_fast','ewma_slow','atm','trade_iv_term','vix_change','vrp'),
    'intraday_har': ('rv5','rv21','rv63','atm','intra_gap21','overnight_share','jump_share_5','downshare_5',
                     'closing_share_5','profile_change','intra_sector_risk','intra_sync'),
    'component_risk': ('ewma_fast','ewma_slow','rv21','atm','term_slope','vix_level'),
}
PROC_SPEC={
    'garch_gauss': ('gjr','normal','none',300,False),
    'gjr_gauss': ('gjr','normal','none',300,True),
    'gjr_student': ('gjr','student','none',300,True),
    'gjr_skew': ('gjr','skew','none',300,True),
    'egarch_student': ('egarch','student','none',300,True),
    'gjr_ivx': ('gjr','student','iv',300,True),
    'gjr_vixx': ('gjr','student','vix',300,True),
    'gjr_t_short': ('gjr','student','none',145,True),
}


def robust_design(train,test,fields):
    """Train-only location/scale and exact-value duplicate detection."""
    fields=tuple(dict.fromkeys(fields))
    a=train.reindex(columns=fields).to_numpy(float)
    b=test.reindex(columns=fields).to_numpy(float)
    keep=[]
    seen=set()
    for j in range(a.shape[1]):
        col=a[:,j]
        if np.isfinite(col).sum()<15:
            continue
        key=np.nan_to_num(col,nan=1.e120).tobytes()
        if key not in seen:
            seen.add(key)
            keep.append(j)
    if not keep:
        return np.empty((len(a),0)),np.empty((len(b),0)),{'fields':[],'median':[],'mean':[],'scale':[]}
    a=a[:,keep];b=b[:,keep]
    median=np.nanmedian(a,axis=0)
    a=np.where(np.isfinite(a),a,median)
    b=np.where(np.isfinite(b),b,median)
    mean=a.mean(axis=0)
    scale=a.std(axis=0).clip(.000001)
    return ((a-mean)/scale).clip(-5,5),((b-mean)/scale).clip(-5,5),dict(
        fields=[fields[j] for j in keep],median=median.tolist(),mean=mean.tolist(),scale=scale.tolist())


def ridge(z,y,alpha):
    design=np.column_stack([np.ones(len(z)),z])
    reg=np.eye(design.shape[1])*alpha
    reg[0,0]=1e-8
    return np.linalg.solve(design.T@design+reg,design.T@y)


def design_apply(z,weights):
    return weights[0]+z@weights[1:]


def skew_constants(nu,skew):
    coefficient=np.exp(gammaln((nu+1)/2)-gammaln(nu/2))/np.sqrt(np.pi*(nu-2))
    a=4*skew*coefficient*(nu-2)/(nu-1)
    b=np.sqrt(1+3*skew**2-a*a)
    return coefficient,a,b


def innovations_logpdf(z,dist,nu,skew):
    if dist=='normal':
        return -.5*(z*z+np.log(2*np.pi))
    c,a,b=skew_constants(nu,skew)
    t=(b*z+a)/(1+skew*np.where(z<-a/b,-1.,1.))
    return np.log(b*c)-.5*(nu+1)*np.log1p(t*t/(nu-2))


def fitted_variables(z,spec):
    form,distribution,exog,_,asymmetric=spec
    if form=='egarch':
        # Level intercept is bounded around the conditional log-variance mean.
        mu,beta,alpha,leverage,nu=z
        return dict(form=form,distribution=distribution,mu=mu,beta=beta,alpha=alpha,leverage=leverage,nu=nu,skew=0.,exog=exog)
    w,p,q,asym,external,nu,skew=z
    # Count all leverage in the stability constraint. The long-run expectation is tighter.
    activations=np.exp([p,q,asym if asymmetric else -35.,external if exog!='none' else -35.,0.])
    a,b,g,xi=.995*activations[:4]/activations.sum()
    return dict(form=form,distribution=distribution,omega=np.exp(w),alpha=a,beta=b,gamma=g,xi=xi,
                nu=nu,skew=skew if distribution=='skew' else 0.,exog=exog)


def filter_garch(r,market,m,init):
    if m['form']=='gjr':
        u=m['omega']+(m['alpha']+m['gamma']*(r<0))*r*r+m['xi']*market
        all_v=np.r_[init,lfilter([1.],[1.,-m['beta']],u,zi=[m['beta']*init])[0]]
        return np.maximum(all_v,MINV)
    mu,beta,alpha,lever=(m[k] for k in ('mu','beta','alpha','leverage'))
    _,a,b=skew_constants(m['nu'],0.)
    expected_abs=4*np.exp(gammaln((m['nu']+1)/2)-gammaln(m['nu']/2))/np.sqrt(np.pi*(m['nu']-2))*(m['nu']-2)/(m['nu']-1)/2
    z=np.empty(len(r)+1)
    z[0]=np.log(init)
    for i,e in enumerate(r):
        standardized=max(-8.,min(8.,e*np.exp(-.5*z[i])))
        z[i+1]=max(-5.,min(5.,(1-beta)*mu+beta*z[i]+alpha*(abs(standardized)-expected_abs)+lever*standardized))
    return np.exp(z)


def fit_garch(r,market,spec):
    form,dist,exog,_,asym=spec
    init=max(float(np.mean(r[:25]**2)),.06)
    if form=='egarch':
        guess=[float(np.log(np.mean(r*r))),.92,.15,-.05,8.]
        bounds=[(-4.,3.),(.12,.987),(.012,.55),(-.38,.24),(5.5,22.)]
    else:
        guess=[-3.6, .15,2.7,-.35 if asym else -15.,-2.,8.,0.]
        bounds=[(-8.,1.),(-5.,3.),(-1.,5.),(-5.,3.) if asym else (-15.,-15.),
                (-5.,2.) if exog!='none' else (-15.,-15.),(5.5,22.) if dist!='normal' else (8.,8.),
                (-.27,.27) if dist=='skew' else (0.,0.)]
    def objective(z):
        p=fitted_variables(z,spec)
        v=filter_garch(r,market,p,init)[:-1]
        ll=innovations_logpdf(r/np.sqrt(v),p['distribution'],p['nu'],p['skew'])-.5*np.log(v)
        shrink=.002*(p.get('leverage',0.)/.2)**2+.014*p['skew']**2
        return float(-ll[12:].mean()+shrink)
    f=minimize(objective,guess,bounds=bounds,method='L-BFGS-B',options={'maxiter':64,'ftol':1.e-9})
    result=fitted_variables(f.x,spec)
    result.update(initial=init,ok=bool(f.success),objective=float(f.fun),raw_parameters=f.x.tolist(),optimizer_message=str(f.message))
    return result


def forecast_variance(p,market):
    if p['form']=='egarch':
        return np.exp(p['mu']+p['beta']**np.arange(21)*(np.log(p['next_variance'])-p['mu']))
    a,b,g,xi=(p[k] for k in ('alpha','beta','gamma','xi'))
    vm=p['next_variance']
    sequence=[]
    for lev in market:
        sequence.append(vm)
        vm=p['omega']+(a+b+.5*g)*vm+xi*lev
    return np.asarray(sequence)


def kfilter(obs,scale,r,z,start=None):
    mu,rho,q,lean,measurement=z
    if start is None:
        last=mu
        variance=.6
    else:
        last,variance=start
    loss=0.
    for val,s,e in zip(obs,scale,r):
        obs_noise=s*measurement
        error=val-last
        total=variance+obs_noise
        loss+=.5*(np.log(total)+error*error/total)
        gain=variance/total
        after=last+gain*error
        aftervar=(1-gain)*variance
        leverage=lean*np.clip(e/np.exp(.5*after),-4,0)
        last=(1-rho)*mu+rho*after+leverage
        variance=rho**2*aftervar+q
    return float(loss/len(obs)),float(last),float(variance)


def fit_kalman(obs,scale,r):
    guess=(float(np.median(obs)),.90,.038,-.10,1.)
    bounds=[(-4.,2.5),(.6,.986),(.003,.19),(-.24,.06),(.60,2.2)]
    def objective(z):
        return kfilter(obs,scale,r,z)[0]+.01*(z[3]/.18)**2
    result=minimize(objective,guess,bounds=bounds,method='L-BFGS-B',options={'maxiter':42})
    return result.x,bool(result.success)


def markov_filter(returns,vars_,transition,smooth=False):
    normed=np.zeros((len(returns),2))
    pdf=np.exp(-.5*np.square(returns[:,None])/vars_)/np.sqrt(vars_)
    a=np.array([.75,.25])
    scales=np.empty(len(a) if len(returns)==0 else len(returns))
    for i,z in enumerate(pdf):
        un=(a@transition)*z
        scales[i]=un.sum()
        a=un/max(scales[i],1e-250)
        normed[i]=a
    if not smooth:
        return normed[-1]
    b=np.ones((len(returns),2))
    for i in range(len(returns)-2,-1,-1):
        b[i]=transition@(pdf[i+1]*b[i+1])/max(scales[i+1],1e-250)
    state=normed*b
    state/=state.sum(axis=1,keepdims=True)
    xi=normed[:-1,:,None]*transition[None,:,:]*(pdf[1:]*b[1:])[:,None,:]
    xi/=xi.sum(axis=(1,2),keepdims=True).clip(1e-250)
    return state,xi.sum(axis=0)


def fit_two_state(r):
    v=max(np.mean(r*r),.07)
    vals=np.array([.48*v,1.9*v])
    trans=np.array([[.93,.07],[.14,.86]])
    for _ in range(15):
        prob,count=markov_filter(r,vals,trans,smooth=True)
        vals=(prob.T@(r*r)+7*np.array([.52*v,1.75*v]))/(prob.sum(axis=0)+7)
        vals=np.maximum(vals,.025)
        smooth_count=count+np.array([[13,2],[3,11]])
        trans=smooth_count/smooth_count.sum(axis=1,keepdims=True)
        order=np.argsort(vals)
        vals,trans=vals[order],trans[np.ix_(order,order)]
    return vals,trans


def rs_mode(r,asof_mature,close_risk):
    p=float(np.count_nonzero(r<0)/len(r))
    sign=np.asarray(r>0,int)
    trans=np.ones((2,2))*10
    np.add.at(trans,(sign[:-1],sign[1:]),1)
    trans/=trans.sum(axis=1,keepdims=True)
    return trans.tolist(),p


def process_inputs():
    d=matrix('daily-process-features.csv').copy()
    x=matrix('features-5.csv')
    y=matrix('features-21.csv')
    iv=x.atm.reindex(d.index)
    slow=y.atm.reindex(d.index)
    vix=x.vix_level.reindex(d.index).div(100)
    # Use an explicit fallback before the historical surface becomes available.
    market=pd.DataFrame({'none':np.zeros(len(d)),'iv':iv,'vix':vix,'slow':slow},index=d.index)
    for k in ['iv','vix','slow']:
        market[k]=market[k].fillna(d.rv21).fillna(.16).pow(2)*10000/252.
    # The density likelihood sees each market signal at least one return prior.
    f=market.shift().fillna(.95)
    r=d.daily_log_return.fillna(0.).mul(100)
    proxy=(d.raw_variance_5+d.gap.pow(2))*10000
    obs=np.log(proxy.clip(.015)).fillna(np.log((r*r).clip(.025))+.85)
    weights=pd.Series(np.where(proxy.notna(),.70,3.5),index=d.index)
    return d,market,f,r,obs,weights


def processes():
    register()
    daily,market,lagged,r,obs,measurement=process_inputs()
    y={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    q=sorted(set.union(*[set(m.index[m.cohort.notna()]) for m in y.values()]))
    caches={}
    fits=[]
    states={}
    forecasts=[]
    for day in q:
        i=daily.index.get_loc(day)
        month=day[:7]
        signal=market.loc[day]
        steps=np.arange(21)
        anchor=signal['slow']+(signal['iv']-signal['slow'])*np.exp(-steps/4.)
        vix=np.full(21,signal['vix'])
        daily_state={}
        for name,spec in PROC_SPEC.items():
            form,err,kind,cap,_=spec
            fit_key=(month,name)
            if fit_key not in caches:
                lo=max(1,i-cap+1)
                p=fit_garch(r.iloc[lo:i+1].to_numpy(),lagged[kind].iloc[lo:i+1].to_numpy(),spec)
                caches[fit_key]=(lo,p)
                fits.append(dict(origin=day,fit_first=daily.index[lo],fit_last=day,method=name,parameters=p))
            lo,defaults=caches[fit_key]
            p=defaults.copy()
            p['next_variance']=float(filter_garch(r.iloc[lo:i+1].to_numpy(),
                        lagged[kind].iloc[lo:i+1].to_numpy(),p,p['initial'])[-1])
            # At origin the future innovation is unknown. Use the visible market anchor.
            if kind!='none':
                p['next_variance']+=p['xi']*(signal[kind]-lagged.at[day,kind])
            p['next_variance']=float(np.clip(p['next_variance'],MINV,MAXV))
            p['variance_curve']=forecast_variance(p,anchor if kind=='iv' else vix if kind=='vix' else np.zeros(21)).tolist()
            daily_state[name]=p
        p=daily_state['gjr_student'].copy()
        p.update(gamma=p['gamma']*.45,beta=p['beta']*.99,nu=12.)
        p['variance_curve']=forecast_variance(p,np.zeros(21)).tolist()
        daily_state['gjr_t_perturbed']=p
        ep=daily_state['gjr_student']
        curve=np.asarray(ep['variance_curve'])
        w=.80*np.exp(-steps/6.)
        daily_state['blend_gjr_iv']={'variance_curve':(w*anchor+(1-w)*curve).tolist()}
        lo=max(1,i-260)
        if (month,'state') not in caches:
            x=r.iloc[lo:i+1].to_numpy()
            z,opt=fit_kalman(obs.iloc[lo:i+1].to_numpy(),measurement.iloc[lo:i+1].to_numpy(),x)
            mv,pt=fit_two_state(x)
            caches[month,'state']=(lo,z,mv,pt)
            fits.extend([dict(origin=day,fit_first=daily.index[lo],fit_last=day,method='latent_kalman',
                             parameters=dict(vector=z.tolist(),optimizer_success=opt)),
                         dict(origin=day,fit_first=daily.index[lo],fit_last=day,method='two_state',
                              parameters=dict(states=mv.tolist(),transition=pt.tolist()))])
        lo,z,mv,pt=caches[month,'state']
        r0=r.iloc[lo:i+1].to_numpy()
        _,center,var=kfilter(obs.iloc[lo:i+1].to_numpy(),measurement.iloc[lo:i+1].to_numpy(),r0,z)
        mu,rho,sigma,leverage,_=z
        latent_mean=mu+rho**steps*(center-mu)
        latent_var=rho**(2*steps)*var+sigma*(1-rho**(2*steps))/(1-rho*rho)
        for name,log_center in [('latent_kalman',latent_mean),('latent_iv',latent_mean+.58*rho**steps*(np.log(anchor[0])-center))]:
            daily_state[name]=dict(mu=float(mu),rho=float(rho),eta_var=float(sigma),leverage=float(leverage),
                current_center=float(log_center[0]),current_var=float(var),variance_curve=np.exp(log_center+.5*latent_var).clip(MINV,MAXV).tolist())
        state=markov_filter(r0,mv,pt)
        var=[]
        prob=[]
        for j in steps:
            state=state@pt
            var.append(float(state@mv))
            prob.append(float(state[1]))
        sign,pneg=rs_mode(r0,None,None)
        daily_state['two_state']=dict(states=mv.tolist(),transition=pt.tolist(),prob_high=prob,
            sign_transition=sign,p_negative=pneg,variance_curve=var)
        daily_state['market_anchors']=dict(near=float(signal['iv']),far=float(signal['slow']),term_curve=anchor.tolist(),
              vix=float(signal['vix']),risk_steady=float(daily.rv21.at[day]),risk_current=float(daily.rv5.at[day]))
        states[day]=daily_state
        for h in HORIZONS:
            if day not in y[h].index or pd.isna(y[h].at[day,'cohort']):
                continue
            for name,p in daily_state.items():
                if 'variance_curve' in p:
                    forecasts.append(dict(horizon=h,origin=day,model=name,prediction=float(np.sqrt(np.mean(p['variance_curve'][:h])*252)/100),
                                          variance_first=float(p['variance_curve'][0])*252/10000,
                                          variance_last=float(p['variance_curve'][h-1])*252/10000))
    write('process-risk-predictions.csv',pd.DataFrame(forecasts))
    save('process-fits.json',fits)
    save('process-states.json',states)
    print(f'Estimated {len(fits)} stochastic-process refits and {len(forecasts)} horizon risk forecasts',flush=True)


def point_models():
    rows,ledger,mechanism=[],[],[]
    for h in HORIZONS:
        x=matrix(f'features-{h}.csv').copy()
        y=matrix(f'targets-{h}.csv')
        q=y[y.cohort.notna()]
        x['historical_iv_balance']=x.atm-x.rv21
        for day,r in q.iterrows():
            t=mature(y,day,180)
            a=x.loc[[day]]
            tr=x.reindex(y.index).iloc[t]
            cut=y.iloc[t]
            hist=tr.atm.to_numpy()
            outcomes=cut.volatility.to_numpy()
            adjust=float(np.clip(np.nanmedian(outcomes/hist),.76,1.27))
            for name,cols in RIDGE_RISK.items():
                z,b,note=robust_design(tr,a,cols)
                anchor=tr.atm.fillna(tr.rv21).to_numpy() if name.endswith('iv') or name=='intraday_har' else tr.rv21.to_numpy()
                current=float(a.atm.iloc[0]) if name.endswith('iv') or name=='intraday_har' else float(a.rv21.iloc[0])
                fitted=ridge(z,np.log(outcomes/anchor.clip(.025)),170.)
                estimate=float(np.exp(design_apply(b,fitted)[0])*current)
                rows.append(dict(horizon=h,origin=day,model=name,prediction=estimate))
                ledger.append(dict(horizon=h,origin=day,model=name,n=len(t),last_mature=cut.endpoint.max(),
                              coefficients=fitted.tolist(),transform=note))
            for name,cols in [('overnight_decomposition',('overnight_rv21','rth_rv21','rv21','atm','firsthour_share_5','closing_share_5')),
                              ('offshore_gap',('overnight_rv21','rth_rv21','rv21','atm',*GLOBAL))]:
                z,b,note=robust_design(tr,a,cols)
                denom=tr[['overnight_rv21','rth_rv21']].to_numpy().clip(.02)
                target=cut[['overnight_sd','regular_sd']].to_numpy().clip(.012)
                coef=ridge(z,np.log(target/denom),240.)
                current=a[['overnight_rv21','rth_rv21']].to_numpy().clip(.02)
                g,regular=(np.exp(design_apply(b,coef))*current)[0]
                cov=np.median(outcomes**2-cut.overnight_sd.to_numpy()**2-cut.regular_sd.to_numpy()**2)
                prediction=float(np.sqrt(max(g*g+regular*regular+.5*cov,.0008)))
                rows.append(dict(horizon=h,origin=day,model=name,prediction=prediction))
                mechanism.append(dict(horizon=h,origin=day,model=name,forecast_overnight=g,forecast_intraday=regular,
                    actual_overnight=r.overnight_sd,actual_intraday=r.regular_sd,conditional_share=g*g/(g*g+regular*regular)))
                ledger.append(dict(horizon=h,origin=day,model=name,n=len(t),last_mature=cut.endpoint.max(),
                              coefficients=coef.tolist(),transform=note,training_covariance=float(cov)))
            for model,val in {'raw_iv':a.atm.iloc[0],'v14_iv_calibrated':a.atm.iloc[0]*adjust,'realized_rms':a.trailing.iloc[0],
                              'rv_gap_lagged':a.rv_decomposition.iloc[0]}.items():
                rows.append(dict(horizon=h,origin=day,model=model,prediction=float(val)))
    write('point-risk-models.csv',pd.DataFrame(rows))
    write('gap-channel-forecasts.csv',pd.DataFrame(mechanism))
    save('risk-fit-ledger.json',ledger)
    print(f'Estimated {len(ledger)} causal volatility regression heads',flush=True)


if __name__=='__main__':
    import sys
    {'process':processes,'point':point_models}[sys.argv[1]]()
