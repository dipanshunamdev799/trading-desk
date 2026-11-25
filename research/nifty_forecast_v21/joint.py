"""Generate joint component laws and compare them with unchanged index anchors."""
from scipy.special import ndtr

from .common import *
from .reference import ANCHOR,DIRECTION
from .universe import SECTOR_NAMES
from research.nifty_forecast_v16.model import fit
from research.nifty_forecast_v17.weekly import evaluate
from research.nifty_forecast_v20.modeling import blend_laws,weighted_store,fit_slope

STOCK_SIMS=256
EXPERIMENTS=('date_only_ridge','date_only_no_position','pooled_market_factor','sector_direct_joint','stocks_to_sectors',
             'stock_history_joint','stock_pooled_joint','stock_conditional_joint','stock_independent','stock_gaussian_shrink',
             'stock_dynamic_factor','stock_heavy_factor','stock_factor_heads','stock_without_heavy5','stock_equal_weight',
             'proxy_randomized_aux','proxy_shifted_aux')
HYBRIDS=('anchor_bias','anchor_location','anchor_scale','anchor_asymmetry','anchor_aggregate_position','anchor_corporate_proxy',
         'anchor_fixed_joint_mixture')


def lagged_fit(x,y,t,i,penalty=145):
    m=fit(x[t],y[t],penalty)
    return np.asarray(m.values(x[i]))


def to_log(a):
    return np.log1p(np.clip(a,-.88,1.9))


def geo_draw(center,resid):
    return np.expm1(np.clip(center+resid,-2.1,1.05))


def weighted_mean(x,q):
    return np.nan_to_num(x,nan=0.)@q


def near_context(x,t,i):
    a=x[t];cur=x[i]
    valid=np.isfinite(a).sum(axis=0)>=18
    a=a[:,valid];cur=cur[valid]
    if not len(cur):
        return np.arange(len(t))
    center=np.nanmedian(a,axis=0)
    z=np.where(np.isfinite(a),a,center)
    c=np.where(np.isfinite(cur),cur,center)
    delta=np.clip((z-c)/np.maximum(.0001,np.std(z,axis=0)),-6,6)
    return np.argsort(np.mean(delta*delta,axis=1),kind='stable')[:max(45,int(.52*len(a)))]


def generator(draw,centers,tape,t,position,sector_tape,sector_location,beta,gamma,market,h,context,rng):
    """Construct historical row, factor, conditional and independent return scenarios."""
    valid=np.isfinite(tape).mean(axis=0)>.25
    stock_center=np.where(valid,np.nanmedian(tape,axis=0),0.)
    clean=np.nan_to_num(tape-stock_center, nan=0.)
    # Keep realized common return for missing historical quotes, with the missing mass audited separately.
    market_center=market-np.mean(market)
    clean=np.where(np.isfinite(tape),clean,market_center[:,None]*beta)
    clean-=np.mean(clean,axis=0)
    ix=rng.integers(len(clean),size=draw)
    cond=rng.choice(context,size=draw)
    history=geo_draw(centers['history'],clean[ix])
    joint=geo_draw(centers['pooled'],clean[ix])
    cond_joint=geo_draw(centers['pooled'],clean[cond])
    perm=np.argsort(rng.uniform(size=joint.shape),axis=0)
    independent=np.take_along_axis(joint,perm,axis=0)
    covariance=clean.T@clean/max(1,len(clean)-1)
    shrunk=.75*covariance+.25*np.diag(np.diag(covariance))+1.e-8*np.eye(len(beta))
    normal=rng.standard_normal(size=joint.shape)@np.linalg.cholesky(shrunk).T
    diagonal=geo_draw(centers['pooled'],normal)
    s=sector_tape-np.mean(sector_tape,axis=0)
    sector_relative=s-market_center[:,None]
    systematic=beta*market_center[:,None]+gamma*sector_relative[:,position]
    resid=clean-systematic
    sigma=np.std(resid,axis=0).clip(.002)
    vol_ratio=np.clip(np.std(market_center[context])/max(.001,np.std(market_center)),.65,1.45)
    idio=rng.standard_normal(joint.shape)*sigma
    innovation=systematic[cond]*vol_ratio+idio
    dynamic=geo_draw(centers['pooled'],innovation)
    heavy=geo_draw(centers['pooled'],innovation*np.sqrt(4/rng.chisquare(6,size=(draw,1))))
    factor=geo_draw(centers['factor'],innovation)
    sect=geo_draw(to_log(sector_location),s[ix])
    return dict(history=history,pooled=joint,conditional=cond_joint,independent=independent,gaussian=diagonal,
                dynamic=dynamic,heavy=heavy,factor=factor,sector=sect,draw_ix=ix,conditional_ix=cond)


def component_horizon(p,forecast,sample,h,ref,sector_weights):
    days=p['days'];end=p[f'end{h}'];cohort=p[f'cohort{h}'];market=p[f'index{h}'];states=p['market_features']
    fields=list(p['market_fields']);features=list(p['fields']);sect=p[f'sector_target{h}']
    daily=sample.set_index('day').reindex(days)
    basis=np.expm1(np.log1p(daily['nifty50_monthly_drift_lag5']).rolling(h).sum().shift(1-h)).to_numpy(float)
    basis=market-basis
    group_idx=np.array([SECTOR_NAMES.index(k) for k in SECTORS])
    seci=pd.Index(SECTOR_NAMES)
    sector_horiz=sect[:,group_idx]
    y=p[f'target{h}'][:,:,0]
    eligible=p['eligible'];weights=p['weights'];bt=p['beta'];gm=p['sector_beta'];groups=p['sector']
    out={};recipes=[];concentration=[];sector_evidence=[];market_rows=[];draws=[];stocks=[];tracked=[]
    mode=list(forecast['models']);mu=forecast[f'mean{h}']
    get=lambda name:mu[mode.index(name),:,:,0]
    stock_abs=get('pooled');stock_hist=get('history');stock_null=get('random_aux_labels');stock_lag=get('shifted_company')
    can=np.isfinite(stock_abs).any(axis=1)
    pooled_scalar=np.divide(np.where(eligible,np.nan_to_num(stock_abs),0.).sum(axis=1),eligible.sum(axis=1).clip(1))
    pooled_scalar[~can]=np.nan
    all_store=[]
    close=ref[(ref.horizon==h)&ref.model.eq(ANCHOR[h])].set_index('day')
    for i in np.flatnonzero(cohort!=''):
        d=days[i]
        ok=(end<d)&(np.arange(len(days))<i)&np.isfinite(market)&np.isfinite(sector_horiz).all(axis=1)
        t=np.flatnonzero(ok)[-140:]
        assert len(t)>=45 and np.isfinite(weights[i]).all() and float(weights[i].sum())>.99
        adequate=t[can[t]]
        q_full=weights[i]
        pos=np.flatnonzero(q_full>0)
        q=q_full[pos]
        r_market=market[t]
        w_sector=sector_weights[i]
        assert np.isfinite(w_sector).all() and np.isclose(w_sector.sum(),1)
        beta=np.nan_to_num(bt[i,pos],nan=1.)
        gamma=np.nan_to_num(gm[i,pos])
        reg_pos=[fields.index(k) for k in ('position_level','position_change21','position_concentration')]
        control_fields=[j for j in range(states.shape[1]) if j not in reg_pos]
        no_pos=float(lagged_fit(states[:,control_fields],market,t,i,155))
        direct=float(lagged_fit(states,market,t,i,155))
        s0=lagged_fit(states,sector_horiz,t,i,155)
        sector_location=lagged_fit(states,sect,t,i,155)
        aux=np.column_stack([states[:,control_fields],pooled_scalar]);pool_factor=direct
        if len(adequate)>=45 and np.isfinite(pooled_scalar[i]):
            pool_factor=float(lagged_fit(aux,market,adequate,i,155))
        cp=np.nan_to_num(stock_abs[i,pos],nan=direct)
        ch=np.nan_to_num(stock_hist[i,pos],nan=np.median(r_market))
        cf=mu[mode.index('factor_residual'),i,pos,7].astype(float)
        cf=np.nan_to_num(cf)+beta*pool_factor+gamma*(sector_location[groups[i,pos]]-pool_factor)
        means=dict(pooled=to_log(cp),history=to_log(ch),factor=to_log(cf))
        tape=to_log(y[t][:,pos]);fit_values=to_log(stock_abs[t][:,pos])
        fallback=np.nanmedian(tape,axis=0)
        fallback=np.nan_to_num(fallback,nan=np.mean(to_log(r_market)))
        e=tape-np.where(np.isfinite(fit_values),fit_values,fallback)
        context=near_context(states[:,[fields.index('trailvol'),fields.index('shared_iv'),fields.index('market_sync')]],t,i)
        rng=np.random.default_rng(SEED+1009*h+13*i)
        gen=generator(1024,means,e,t,groups[i,pos],to_log(sect[t]),sector_location,beta,gamma,to_log(r_market),h,context,rng)
        a,b=gen['draw_ix'],gen['conditional_ix']
        historical_basis=np.clip(np.nan_to_num(basis[t]),-.017,.017)
        track_mean=float(np.mean(historical_basis))
        market_atoms=to_log(r_market)-np.mean(to_log(r_market))
        market_dist=lambda loc:geo_draw(to_log(loc),market_atoms[a])
        joint=gen['pooled'];sq=joint@q
        k=rng.permutation(len(pos))
        equal=joint.mean(axis=1)
        route=np.argsort(q)[:-5]
        rest=w_sector.copy()
        sector_sims=gen['sector'][:,group_idx]
        stock_sector=[]
        stock_sector_members=[]
        for n,kname in enumerate(SECTORS):
            g=(groups[i]==seci.get_loc(kname))&eligible[i]&np.isfinite(stock_abs[i])
            if g.sum()<4:
                stock_sector.append(s0[n]);stock_sector_members.append(int(g.sum()));continue
            stock_sector.append(float(np.mean(stock_abs[i,g])));stock_sector_members.append(int(g.sum()))
        sector_joint=sector_sims@rest
        delta=np.asarray(stock_sector)-s0
        stock_sector_joint=np.clip(sector_sims+.65*delta,-.88,1.9)@rest
        gen_baseline=joint@q
        null_repair=np.nan_to_num(stock_null[i,pos],nan=direct)@q-cp@q
        lag_repair=np.nan_to_num(stock_lag[i,pos],nan=direct)@q-cp@q
        laws={
            'date_only_ridge':market_dist(direct),'date_only_no_position':market_dist(no_pos),
            'pooled_market_factor':market_dist(pool_factor),'sector_direct_joint':sector_joint,
            'stocks_to_sectors':stock_sector_joint,'stock_history_joint':gen['history']@q+historical_basis[a],
            'stock_pooled_joint':sq+historical_basis[a],'stock_conditional_joint':gen['conditional']@q+historical_basis[b],
            'stock_independent':gen['independent']@q+historical_basis[a],
            'stock_gaussian_shrink':gen['gaussian']@q+track_mean,'stock_dynamic_factor':gen['dynamic']@q+historical_basis[b],
            'stock_heavy_factor':gen['heavy']@q+historical_basis[b],'stock_factor_heads':gen['factor']@q+historical_basis[b],
            'stock_without_heavy5':joint[:,route]@(q[route]/q[route].sum()),'stock_equal_weight':equal,
            'proxy_randomized_aux':gen_baseline+historical_basis[a]+null_repair,
            'proxy_shifted_aux':gen_baseline+historical_basis[a]+lag_repair,
        }
        x=close.loc[d];actual=float(market[i])
        assert abs(float(x.actual)-actual)<2.e-10 and x.target_end==end[i]
        accepted=np.isfinite(y[i,pos]);realized=q*np.nan_to_num(y[i,pos])
        expected=q*joint[:STOCK_SIMS].mean(axis=0)
        effective=lambda a:float(np.sum(np.abs(a))**2/max(1.e-12,np.sum(a*a)))
        share=np.var(joint[:STOCK_SIMS]@q)/max(1.e-10,np.var(joint[:STOCK_SIMS],axis=0)@q)
        evidence=dict(day=d,horizon=h,cohort=cohort[i],actual=actual,decision=d+'T08:55:00+05:30',
            target_end=end[i],last_mature=end[t[-1]],constituents=len(pos),prior_month_available=True,
            model_equities=int(np.isfinite(stock_abs[i,eligible[i]]).sum()),realized_weight_covered=float(q[accepted].sum()),
            weight_top5=np.sort(q)[-5:].sum(),weight_hhi=float(q@q),effective_weights=1/(q@q),
            effective_expected_contributors=effective(expected),effective_realized_contributors=effective(realized),
            predicted_asset_dispersion=float(np.std(cp)),realized_asset_dispersion=float(np.nanstd(y[i,pos])),
            stock_signal_before_aggregation=float(np.mean(np.abs(cp))),net_stock_signal=float(np.abs(cp@q)),
            forecast_common_variance_ratio=share,prior_synchronization=states[i,fields.index('market_sync')],
            prior_breadth=states[i,fields.index('advance')],prior_iv=states[i,fields.index('shared_iv')],
            sector_dispersion=float(np.std(s0)))
        concentration.append(evidence)
        market_rows.extend(dict(day=d,horizon=h,cohort=cohort[i],model=v,actual=actual,prediction=float(laws[v][:256].mean()),
                                **{'market_crps':evaluate(laws[v][:256],np.full(256,1/256.),actual)['crps']})
                           for v in ('date_only_ridge','date_only_no_position','pooled_market_factor'))
        variance=float(np.var(sq[:256],ddof=0))
        cov=np.mean((joint[:256]-joint[:256].mean(axis=0))*(sq[:256,None]-sq[:256].mean()),axis=0)
        b0=sector_joint[:256]
        for j,gname in enumerate(SECTORS):
            g=groups[i,pos]==seci.get_loc(gname)
            u=sector_sims[:256,j];sector_actual=float(sector_horiz[i,j])
            u2=np.clip(u+.65*delta[j],-.88,1.9)
            vdir=evaluate(u,np.full(256,1/256.),sector_actual)
            vstock=evaluate(u2,np.full(256,1/256.),sector_actual)
            a_sector=y[i,pos][g];q_group=q[g]
            sector_evidence.append(dict(day=d,horizon=h,cohort=cohort[i],sector=gname,realized_sector=sector_actual,
                  relative_realized=sector_actual-actual,expected_sector=float(u.mean()),expected_relative=float((u-b0).mean()),
                  probability_outperformance=float((u>b0).mean()),conditional_volatility=float(np.std(u)),
                  statistical_sector_weight=rest[j],sector_mixture_contribution=float(u.mean()*rest[j]),
                  constituent_weight=float(q_group.sum()),constituent_return_contribution=float(expected[g].sum()),
                  observed_return_contribution=float(q_group@np.nan_to_num(a_sector)),
                  constituent_risk_share=float((q_group@cov[g])/max(1.e-9,variance)),stock_model_members=stock_sector_members[j],
                  direct_brier=vdir['brier'],direct_crps=vdir['crps'],direct_mae=vdir['mae'],
                  stock_brier=vstock['brier'],stock_crps=vstock['crps'],stock_mae=vstock['mae']))
        for j,s in enumerate(pos):
            stocks.append(dict(day=d,horizon=h,cohort=cohort[i],symbol=p['symbols'][s],sector=SECTOR_NAMES[groups[i,s]],
                 guarded_weight=q[j],expected=float(joint[:256,j].mean()),return_contribution=expected[j],
                 realized=float(y[i,s]),realized_contribution=realized[j] if accepted[j] else np.nan,variance_contribution=float(q[j]*cov[j])))
        for siz in (128,256,1024):
            pred=laws['stock_pooled_joint'][:siz]
            draws.append(dict(day=d,horizon=h,cohort=cohort[i],draws=siz,mean=float(pred.mean()),p_up=float((pred>0).mean()),
                q10=float(np.quantile(pred,.10)),q90=float(np.quantile(pred,.90)),std=float(pred.std())))
        recipe=dict(day=d,horizon=h,last_mature=end[t[-1]],n_train=len(t),training_dates=','.join(days[t]),
                    tracking_basis_mean=track_mean,conditional_dates=len(context),available_prediction=bool(can[i]),
                    valid_weight_in_current_features=float(q[np.isfinite(stock_abs[i,pos])].sum()),row=len(all_store))
        recipes.append(recipe)
        out[d]={k:np.ascontiguousarray(v[:STOCK_SIMS]) for k,v in laws.items()}
        tracked.append([cp@q,sector_location[group_idx]@rest,pool_factor, cp@q-pool_factor,np.std(cp),
                        np.std(sq[:256]),q@p['stock_features'][i,pos,features.index('event_reaction')].astype(float) if np.isfinite(p['stock_features'][i,pos,features.index('event_reaction')]).all() else
                        float(q@np.nan_to_num(p['stock_features'][i,pos,features.index('event_reaction')])),float(q@np.nan_to_num(y[i,pos]))])
        all_store.append((pos,q,joint[:256],historical_basis[a[:256]],sector_sims[:256]))
    return (out,pd.DataFrame(recipes),pd.DataFrame(concentration),pd.DataFrame(sector_evidence),pd.DataFrame(market_rows),
            pd.DataFrame(draws),pd.DataFrame(stocks),np.asarray(tracked),all_store)


def endpoint_forecasts(h,book,result,refs,features):
    lawmap,recipes,*_=result
    proxy=result[-2]
    data=[];laws=[]
    # The last column of proxy is the realized constituent return and never enters a design.
    proxy=proxy[:,:-1]
    original=refs[refs.horizon.eq(h)]
    for clock in ('preauction_0855','native_0910'):
        reference=ANCHOR[h] if clock=='native_0910' else ('archived_same_clock' if h==5 else 'archived_joint_GJR')
        r=original[original.cutoff.eq(clock)&original.model.eq(reference)].set_index('day').reindex(recipes.day)
        assert r.target_end.notna().all()
        mv=features.reindex(r.index)[['position_level','position_change21','position_concentration']].to_numpy(float)
        end=r.target_end.to_numpy(dtype='U10');err=(r.actual-r['mean']).to_numpy(float)
        dates=r.index.to_numpy(dtype='U10')
        for i,day in enumerate(dates):
            row=r.iloc[i]
            a,w=book[h,clock,reference,day]
            actual=float(row.actual)
            t=np.flatnonzero((end<day)&(np.arange(len(dates))<i))[-140:]
            can=len(t)>=45
            shock=lambda x,yy,limit:float(np.clip(.55*fit_slope(x[t],yy[t],x[i],150)[0],-limit,limit)) if can else 0.
            d=lawmap[day]
            bank={k:(v,np.full(len(v),1./len(v)),True,recipes.iloc[i].last_mature) for k,v in d.items()}
            for model,m in original[original.cutoff.eq(clock)&original.day.eq(day)].set_index('model').iterrows():
                v,n=book[h,clock,model,day]
                bank[model]=(v,n,bool(m.active),None)
            m=float(w@a)
            bias=float(np.clip(.45*np.mean(err[t]),-.013,.013)) if can else 0.
            loc=shock(proxy,err,.013)
            sc=np.exp(shock(proxy,np.log(np.maximum(.003,np.abs(err))),.20))
            asym=shock(proxy,np.sign(err),.15)
            pos=shock(mv,err,.012)
            corp=shock(proxy[:,[-1]],err,.008)
            def bound(v):
                return np.clip(v,-.88,1.9)
            mix,mx=blend_laws(a,w,d['stock_pooled_joint'],np.full(STOCK_SIMS,1/STOCK_SIMS),.25)
            extras={'anchor_bias':(bound(a+bias),w),'anchor_location':(bound(a+loc),w),
                    'anchor_scale':(bound(m+sc*(a-m)),w),'anchor_asymmetry':(bound(m+(a-m)*(1+asym*np.sign(a-m))),w),
                    'anchor_aggregate_position':(bound(a+pos),w),'anchor_corporate_proxy':(bound(a+corp),w),
                    'anchor_fixed_joint_mixture':(mix,mx)}
            for model,(a0,w0) in extras.items():
                bank[model]=(a0,w0,can or model.endswith('mixture'),end[t[-1]] if can else None)
            for name,(a0,w0,active,mature) in bank.items():
                sc0=evaluate(a0,w0,actual);ref_close=float(row.reference_close)
                residual_fit=name in HYBRIDS and name!='anchor_fixed_joint_mixture'
                data.append(dict(day=day,origin=row.origin,horizon=h,cutoff=clock,cohort=row.cohort,model=name,
                        anchor=reference,target_end=row.target_end,active=active,last_mature=mature,ensemble_example=bool(name in HYBRIDS),
                        n_residual_train=len(t) if residual_fit else 0,law=len(laws),reference_close=ref_close,
                        endpoint_expected=ref_close*(1+sc0['mean']),p_down_2=float(w0@(a0<-.02)),p_up_2=float(w0@(a0>.02)),**sc0))
                laws.append((a0,w0))
    return data,laws


def run():
    with np.load(OUT/'component-panel.npz',allow_pickle=False) as r:
        p=dict(r.items())
    with np.load(OUT/'equity-forecast-laws.npz',allow_pickle=False) as r:
        f=dict(r.items())
    x=csv('protected-return-cases.csv.gz')
    with np.load(OUT/'protected-return-laws.npz',allow_pickle=False) as laws:
        atom,w,o=laws['atoms'],laws['weights'],laws['offsets']
    book={(r.horizon,r.cutoff,r.model,r.day):(atom[o[r.law]:o[r.law+1]],w[o[r.law]:o[r.law+1]]) for r in x.itertuples(index=False)}
    states=csv('market-state-features.csv').set_index('day')
    sample=csv('daily-index-reconstruction.csv')
    weights=np.load(OUT/'tracking-factors.npz',allow_pickle=False)['sector_weights']
    results={h:component_horizon(p,f,sample,h,x,weights) for h in HORIZONS}
    whole=[];distribution=[]
    for h,v in results.items():
        d,q=endpoint_forecasts(h,book,v,x,states)
        for row in d:
            row['law']+=len(distribution)
        whole+=d
        distribution+=q
    write('index-forecast-cases.csv.gz',pd.DataFrame(whole))
    weighted_store(OUT/'index-forecast-laws.npz',distribution)
    names=['joint-fit-receipts.csv','concentration-cases.csv','sector-contribution-cases.csv.gz','market-factor-cases.csv',
           'monte-carlo-convergence-cases.csv','constituent-contribution-cases.csv.gz']
    for j,name in enumerate(names,start=1):
        write(name,pd.concat([v[j] for v in results.values()],ignore_index=True))
    full=[b for h in HORIZONS for b in results[h][-1]]
    k=max(len(x[0]) for x in full)
    stock=np.zeros((len(full),STOCK_SIMS,k),dtype=np.float32)
    basis=[];indices=np.full((len(full),k),-1);coeff=np.zeros_like(indices,dtype=float);sector=[]
    for i,(a,q,m,b,z) in enumerate(full):
        n=len(a); indices[i,:n]=a; coeff[i,:n]=q;stock[i,:,:n]=m;basis.append(b);sector.append(z)
    np.savez_compressed(OUT/'joint-simultaneous-laws.npz',stock_returns=stock,sector_returns=np.stack(sector),basis=np.stack(basis),
                       asset_indices=indices,asset_weights=coeff,asset_symbols=p['symbols'],cases=np.array([len(results[h][-1]) for h in HORIZONS]))
    save('joint-forecast-config.json',dict(secondary_clocks=['08:55 IST','09:10 IST with pre-auction inputs and native anchor'],
          scenarios=STOCK_SIMS, convergence=[128,256,1024],models=EXPERIMENTS,hybrids=HYBRIDS,
          history='Matured return vectors, subtract chronological stock forecasts where available. Paired basis residual of dated index reconstruction.',
          dependence='Joint empirical rows, prior-risk-conditional rows, 25% diagonal Gaussian shrinkage, market/sector factor with dynamic scale and Student-t tail variant, exact marginal permutations.',
          return_algebra='Starting weights aggregate terminal simple cash returns, implicit buy-and-hold drift, plus observed-basis error if enabled. No realized future holdings used.',
          archive='Case row order is five-session origins followed by 21-session origins. Primary equity law includes all holdings in each joint scenario and its paired basis atom.',
          anchor_fit='Only earlier realized forecast errors can fit shifts, scale, asymmetry, aggregate positioning or corporate conditional corrections. Baselines retain exact laws.'))
    print('Measured',len(whole),'matched index forecast laws and',len(full),'simultaneous constituent forecasts',flush=True)


if __name__=='__main__':
    run()
