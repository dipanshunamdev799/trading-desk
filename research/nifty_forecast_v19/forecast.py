"""Chronological endpoint tests and same-origin attribution against protected laws."""
from dataclasses import dataclass
from itertools import combinations
from math import factorial

from .common import *
from .features import *
from research.nifty_forecast_v18 import forecast as prior
from research.nifty_forecast_v17 import weekly
from research.nifty_forecast_v17.gift import score

GROUPS={'delivery':DELIVERY[:8],'participant':POSITION,'transactions':DEALS[:6]}
CORP=prior.COUNT+prior.FUND
PRICE=('prior_ret5','prior_ret21','rolling_rv5','trailing_vol','iv_prev','iv_skew','iv_term','vix_level','basis_previous',
       'eq50_spread1','eq500_spread5','official_finance1','domestic_rotation_finance')
STANDALONE=('FII_index_futures_level','FII_index_futures_d1','FII_index_futures_d5',*INNOV,'del_sector_equal','del_high_frac','deal_size')
INT=('fund_delivery','earnings_positions','weak_fund_breadth','disclosure_concentration','financial_positions','scheduled_market_risk')
ACTIVITY=('del_volume_control','del_turnover_control','del_pricectl_advance','del_pricectl_dispersion')

@dataclass(frozen=True)
class Arm:
    name: str
    fields: tuple=()
    parent: str='clock_structural'
    method: str='shift'
    required: tuple=()

def subset_name(names):
    return 'clock_structural' if not names else ' + '.join(names)

SUBSETS=[q for i in range(4) for q in combinations(GROUPS,i)]
SUBSET_ARMS=[Arm(subset_name(q),tuple(k for block in q for k in GROUPS[block]),required=q) for q in SUBSETS if q]
EDITS=(
    Arm('residual_intercept',method='intercept'),
    Arm('price_only',PRICE,method='direct'),
    Arm('price_ordinary_oi',PRICE+FUTURES,parent='price_only',method='direct',required=('futures',)),
    Arm('price_ordinary_turnover',PRICE+ACTIVITY,parent='price_only',method='direct',required=('delivery',)),
    Arm('positions_direct',LEVEL+CHANGES,method='direct',required=('participant',)),
    Arm('price_plus_position_level',PRICE+FUTURES+LEVEL,parent='price_ordinary_oi',method='direct',required=('participant','futures')),
    Arm('price_plus_position_changes',PRICE+FUTURES+CHANGES,parent='price_ordinary_oi',method='direct',required=('participant','futures')),
    Arm('price_plus_innovation',PRICE+FUTURES+INNOV,parent='price_ordinary_oi',method='direct',required=('innovation','futures')),
    Arm('price_plus_disagreement',PRICE+FUTURES+CROWD,parent='price_ordinary_oi',method='direct',required=('participant','futures')),
    Arm('clock_with_oi_volume',FUTURES+ACTIVITY,required=('futures','delivery')),
    Arm('positions_beyond_oi',POSITION,parent='clock_with_oi_volume',method='shift',required=('participant','futures')),
    Arm('delivery_beyond_turnover',DELIVERY,parent='clock_with_oi_volume',method='shift',required=('delivery',)),
    Arm('deals_beyond_turnover',DEALS,parent='clock_with_oi_volume',method='shift',required=('transactions',)),
    Arm('innovation_augmentation',INNOV,required=('innovation',)),
    Arm('levels_only',LEVEL,required=('participant',)),
    Arm('changes_only',CHANGES,required=('participant',)),
    Arm('position_with_compact_factors',STANDALONE,required=('innovation','delivery','transactions')),
    Arm('corporate_position_additive',POSITION+DELIVERY+DEALS,'V18_corporate_same_clock',required=('participant','delivery','transactions')),
    Arm('corporate_position_interactions',POSITION[:7]+DELIVERY[:8]+INT,'V18_corporate_same_clock',required=('participant','delivery')),
    Arm('position_location_scale',CORE+INNOV,method='shape',required=('innovation','delivery','transactions')),
    Arm('structural_position_mixture',STANDALONE,method='mix',required=('innovation','delivery','transactions')),
    Arm('decomposition_position',POSITION+INNOV,'component_plus_residual',required=('innovation',)),
    Arm('participant_delay1',tuple(k+'_delay1' for k in POSITION),required=('participant_delay1',)),
    Arm('participant_delay5',tuple(k+'_delay5' for k in POSITION),required=('participant_delay5',)),
    Arm('participant_block_permuted',POSITION,method='permuted',required=('participant',)),
    Arm('delivery_25_window',('del_z25',*DELIVERY[1:4]),required=('delivery',)),
    Arm('delivery_liquidity_weight',('del_weight_liquid',*DELIVERY[1:4]),required=('delivery',)),
    Arm('delivery_without_top_15',('del_ex_heavy',*DELIVERY[1:4]),required=('delivery',)),
    Arm('delivery_ex_actions',('del_no_actions',*DELIVERY[1:4]),required=('delivery',)),
    Arm('delivery_random_half0',('del_half0',*DELIVERY[1:4]),required=('delivery',)),
    Arm('delivery_random_half1',('del_half1',*DELIVERY[1:4]),required=('delivery',)),
    Arm('deals_without_largest',('deal_without_largest',*DEALS[2:6]),required=('transactions',)),
    Arm('deals_all_reported_legs',('deal_naive_amount',*DEALS[2:6]),required=('transactions',)),
    Arm('deals_date_shift',tuple(k+'_delay5' for k in DEALS),required=('transactions_delay5',)),
)
NATIVE={'V14_exact':'V14_plus_positions','V14_event_overlay':'V18_plus_positions'}
NULL={'participant':POSITION,'delivery':DELIVERY[:8],'interactions':INT+POSITION[:5]}

def add_int(f):
    f=f.copy()
    f['fund_delivery']=f.fund_growth_breadth*f.del_rising_frac
    f['earnings_positions']=f.fund_surprise*f.FII_index_futures_d5
    f['weak_fund_breadth']=f.fund_profit_breadth*f.cash_breadth_change
    f['disclosure_concentration']=f.lexical_direction*f.del_flow_concentration
    f['financial_positions']=f.fund_financial*f.FII_stock_futures_d5
    f['scheduled_market_risk']=np.log1p(f.earnings_notice_count)*f.iv_prev
    return f

def matrix(f,fields):
    return f.reindex(columns=list(dict.fromkeys(fields))).to_numpy(float)

def matured(when,end,y,i,decision=None,n=140):
    at=when[i] if decision is None else decision[i]
    return np.flatnonzero((np.arange(len(y))<i)&(end<at)&np.isfinite(y))[-n:]

def shift(x,r,i,t,cap,method='shift',random_order=None):
    t=t[np.isfinite(r[t])]
    if len(t)<38:
        return 0.,None,t
    if method=='intercept':
        return float(np.clip(.58*np.mean(r[t]),-cap,cap)),None,t
    ix=t if random_order is None else t[random_order]
    m=fit(x[ix],r[t],175)
    return float(np.clip(.58*m.values(x[i]),-cap,cap)),m,t

def shuffled_blocks(n,seed):
    pieces=[np.arange(i,min(i+21,n)) for i in range(0,n,21)]
    rng=np.random.default_rng(seed)
    return np.concatenate([pieces[i] for i in rng.permutation(len(pieces))])

def book_panel(clock,h,p):
    f,y=prior.build_clock(clock,h)
    now_=p[p.cutoff.eq(clock)].set_index('day')
    f=f.join(now_.drop(columns=['origin','cutoff','decision']),how='left',validate='1:1')
    g=add_int(f)
    return g,y

def coverage(f):
    return {'futures':f.ordinary_oi.notna().to_numpy(),'participant':f.FII_index_futures_level.notna().to_numpy(),
            'innovation':f.innovation_5.notna().to_numpy(),'delivery':f.del_intensity.notna().to_numpy(),
            'transactions':f.deal_n.notna().to_numpy(),'participant_delay1':f.FII_index_futures_level_delay1.notna().to_numpy(),
            'participant_delay5':f.FII_index_futures_level_delay5.notna().to_numpy(),
            'transactions_delay5':f.deal_n_delay5.notna().to_numpy()}

def blend(a,b):
    return np.r_[a[::2],b[1::2]]

def law_fit(arm,x,e,y,i,tr,parent,h,order=None):
    cap=.009 if h==5 else .014
    if arm.method=='direct':
        m=fit(x[tr],y[tr],150)
        hist=y[tr]
        a=np.quantile(hist,(np.arange(len(parent))+.5)/len(parent))
        loc=.67*m.values(x[i])+.33*np.median(hist)
        return a-np.median(a)+np.clip(loc,-.042,.042),m,tr,0.,1.,None
    delta,m,u=shift(x,e,i,tr,cap,arm.method,order)
    scale=1.; sm=None
    law=parent+delta
    if arm.method=='shape' and len(u)>=38:
        ref=max(.0035,np.median(abs(e[u])))
        sm=fit(x[u],np.log(np.maximum(abs(e[u]),.0005)/ref),240)
        scale=np.exp(np.clip(.36*sm.values(x[i]),-.22,.22))
        asym=np.clip(.28*delta/ref,-.09,.09)
        base=parent-np.median(parent)
        law=np.median(parent)+delta+base*scale*np.where(base>0,1+asym,1-asym)
    if arm.method=='mix':
        law=blend(parent,law)
    return law,m,u,delta,scale,sm

def filtered(x,i,mask):
    return x[mask[x]] if mask[i] else x[:0]

def endpoint():
    p=csv('asof-positioning-features.csv.gz')
    prior_case=csv('original-event-forecasts.csv.gz',V18).set_index(['horizon','cutoff','day','model'])
    old=np.load(V18/'original-event-laws.npz',allow_pickle=False)['atoms'].astype(float)
    native=csv('v18-native-exact-replay.csv').set_index(['horizon','day','model'])
    nat=np.load(OUT/'v18-native-replayed-laws.npz',allow_pickle=False)
    atoms0,weights0,off=nat['atoms'],nat['weights'],nat['offsets']
    seen_arms=tuple(SUBSET_ARMS)+EDITS
    atoms=[];rows=[];wrows=[];watoms=[];wweights=[];shap=[];null=[]
    law_rows=[]
    exact={'clock_structural':'clock_structural','component_plus_residual':'component_plus_residual','neutral':'neutral','historical':'historical',
           'stock_direct':'stock_direct','stock_residual':'stock_residual','low_rank_sector_risk':'low_rank_sector_risk',
           'V18_corporate_same_clock':'fundamental_augmentation','V18_nonprice_same_clock':'additional_nonprice',
           'V18_repricing_same_clock':'expectation_repricing'}
    for clock in CLOCKS:
        for h in HORIZONS:
            f,y=book_panel(clock,h,p)
            decision=f.decision.str[:10].to_numpy()
            ds=f.index.to_numpy()
            end=y[f'end_original{h}'].fillna('9999-12-31').to_numpy()
            origin=y.origin.to_numpy()
            labels=y[f'original{h}'].to_numpy(float)
            cohort=y[f'cohort_{h}']
            use=np.flatnonzero(cohort.notna())
            assert len(use)==EXPECTED[h]
            masks=coverage(f)
            live={a.name:np.logical_and.reduce([masks[k] for k in a.required]) if a.required else np.ones(len(f),bool) for a in seen_arms}
            xs={a.name:matrix(f,a.fields) for a in seen_arms}
            xn={name:matrix(f,fields) for name,fields in NULL.items()}
            nx=matrix(f,POSITION+INNOV)
            center=weekly.chronology(f,weekly.ORIGINAL_BASE,labels,end,decision)
            e={k:labels-center.copy() for k in exact}
            for k in ('V18_corporate_same_clock','component_plus_residual'):
                for i in use:
                    v=prior_case.loc[(h,clock,ds[i],exact[k])]
                    e[k][i]=labels[i]-float(old[int(v.law)].mean())
            native_err={name:np.full(len(f),np.nan) for name in NATIVE}
            if clock=='preauction_0855':
                for name in NATIVE:
                    for i in use:
                        item=native.loc[h,ds[i],name]
                        native_err[name][i]=labels[i]-np.log1p(item['mean'])
            for i in use:
                args=dict(day=ds[i],origin=origin[i],target_end=end[i],cohort=cohort.iloc[i],cutoff=clock,horizon=h,
                          decision=f.decision.iloc[i],source_day=f.source_day.iloc[i],source_release=f.source_release.iloc[i],
                          expiry_guard=int(pd.notna(f.days_to_expiry.iloc[i]) and f.days_to_expiry.iloc[i]>3 and f.roll_event.iloc[i]==0))
                tr=matured(ds,end,labels,i,decision)
                seen={};price_error=dict(e)
                for name,arc in exact.items():
                    row=prior_case.loc[(h,clock,ds[i],arc)]
                    a=old[int(row.law)].copy()
                    atoms.append(a.astype(np.float32))
                    v=score(a,labels[i])
                    if name=='neutral':
                        v.update(p=.5,brier=.25,log_loss=np.log(2),correct=int(labels[i]>0))
                    seen[name]=(a,v)
                    rows.append(args|dict(model=name,parent=name,active=1,last_mature=row.last_mature,n_train=0,law=len(atoms)-1,**v))
                for a in seen_arms:
                    if a.parent not in seen and a.parent!='clock_with_oi_volume':
                        raise AssertionError(a)
                    parent_key=a.parent if a.parent in seen else 'clock_structural'
                    parent,se=seen[parent_key]
                    train=filtered(tr,i,live[a.name])
                    er=e.get(parent_key,e['clock_structural'])
                    # Evaluate overlays over the ordinary-OI/turnover reference after the reference is built.
                    assert a.parent==parent_key
                    if parent_key=='clock_with_oi_volume':
                        er=price_error[parent_key]
                    m=None;sm=None;scale=1.;dv=0.
                    is_active=len(train)>=38 and np.isfinite(xs[a.name][i]).any() or a.method=='intercept' and len(train)>=38
                    if is_active:
                        pool=train if a.method=='direct' else train[np.isfinite(er[train])]
                        is_active=len(pool)>=38
                    if is_active:
                        ro=shuffled_blocks(len(pool),SEED+71) if a.method=='permuted' else None
                        law,m,pool,dv,scale,sm=law_fit(a,xs[a.name],er,labels,i,pool,parent,h,ro)
                        latest=max(end[pool])
                    else:
                        law=parent
                        pool=tr[:0]
                        latest=max(end[tr])
                    v=score(law,labels[i]) if is_active else se.copy()
                    seen[a.name]=(law,v)
                    if a.name=='clock_with_oi_volume':
                        # Populate one prediction for each evaluated origin, retained for its later matured descendants.
                        if a.name not in e:e[a.name]=np.full(len(f),np.nan)
                        e[a.name][i]=labels[i]-float(np.mean(law))
                        price_error[a.name]=e[a.name]
                    atoms.append(law.astype(np.float32))
                    rows.append(args|dict(model=a.name,parent=a.parent,active=int(is_active),last_mature=latest,n_train=len(pool),
                                          law=len(atoms)-1,shift=dv,scale=scale,**v))
                    if m is not None:
                        law_rows.append(dict(law=len(atoms)-1,n=len(pool),end=latest,training_dates=ds[pool].tolist(),
                                             scale_fit=sm.receipt(list(dict.fromkeys(a.fields))) if sm is not None else None,
                                             **m.receipt(list(dict.fromkeys(a.fields)))))
                for family in GROUPS:
                    marg={}
                    for k in ('brier','crps'):
                        marg[k]=0.
                        for subset in SUBSETS:
                            if family in subset:continue
                            after=tuple(n for n in GROUPS if n in subset or n==family)
                            w=factorial(len(subset))*factorial(2-len(subset))/6
                            marg[k]+=w*(seen[subset_name(subset)][1][k]-seen[subset_name(after)][1][k])
                    shap.append(args|dict(block=family,**marg))
                if clock=='preauction_0855':
                    q=seen['clock_structural']
                    for seed in range(23):
                        for name,x in xn.items():
                            t=tr[np.isfinite(e['clock_structural'][tr])]
                            rd=(seed+3)*7
                            perm=np.roll(np.arange(len(t)),rd) if seed%2==0 else shuffled_blocks(len(t),SEED+seed)
                            delta,_,_=shift(x,e['clock_structural'],i,t,.009 if h==5 else .014,random_order=perm)
                            v=score(q[0]+delta,labels[i])
                            null.append(dict(horizon=h,day=ds[i],cohort=cohort.iloc[i],seed=seed,arm=name,
                                             brier_gain=q[1]['brier']-v['brier'],crps_gain=q[1]['crps']-v['crps']))
                    for name,new in NATIVE.items():
                        item=native.loc[h,ds[i],name]
                        k=int(item.law_index)
                        aa=atoms0[off[k]:off[k+1]]
                        ww=weights0[off[k]:off[k+1]]
                        d=native_err[name]
                        t=filtered(tr,i,masks['innovation'])
                        delta,m,u=shift(nx,d,i,t,.009 if h==5 else .012)
                        for label,arr,n_train in [(name,aa,0),(new,(1+aa)*np.exp(delta)-1,len(u) if m is not None else 0)]:
                            watoms.append(arr); wweights.append(ww)
                            wrows.append(args|dict(model=label,parent=name,cutoff='native_v14_guard',position_features_frozen='08:55',
                                        active=int(label==name or m is not None),last_mature=max(end[u]) if m is not None else None,
                                        n_train=n_train,shift=delta if label==new else 0.,law=len(watoms)-1,
                                        **weekly.evaluate(arr,ww,np.expm1(labels[i]))))
            print('Completed original endpoint tests',clock,h,len(use),flush=True)
    write('endpoint-cases.csv.gz',pd.DataFrame(rows))
    write('native-residual-cases.csv.gz',pd.DataFrame(wrows))
    write('v19-block-shapley.csv.gz',pd.DataFrame(shap))
    write('refit-null-cases.csv.gz',pd.DataFrame(null))
    np.savez_compressed(OUT/'endpoint-laws.npz',log_return_atoms=np.stack(atoms))
    np.savez_compressed(OUT/'native-residual-laws.npz',atoms=np.concatenate(watoms),weights=np.concatenate(wweights),
                        offsets=np.r_[0,np.cumsum([len(a) for a in watoms])])
    with gzip.open(OUT/'endpoint-fit-receipts.ndjson.gz','wt',encoding='utf8') as w:
        for row in law_rows:
            w.write(json.dumps(row,default=str,allow_nan=False)+'\n')
    save('endpoint-config.json',dict(source_clocks=CLOCKS,arms=[a.__dict__ for a in seen_arms],
          archive_references=exact,null=tuple(NULL),native_models=NATIVE,shrinkage=.58,penalty=175,
          n_train=[38,140],return_units='The endpoint atom arrays store log returns. Scores are arithmetic returns. Native laws store arithmetic returns and their exact weights.',
          intended_cohorts=EXPECTED,case_models=len(rows),weighted_native_case_models=len(wrows),fit_receipts=len(law_rows)))

def after_open():
    b=csv('asof-positioning-features.csv.gz')
    rows=[];all_atoms=[]
    for clock in POST:
        p=b[b.cutoff.eq(clock)].set_index('day')
        name='residual-'+clock.replace(':','')
        d=csv(name+'-scores.csv.gz',V17)
        atoms=np.load(V17/(name+'-laws.npz'),allow_pickle=False)['atoms']
        xs=matrix(p,POSITION[:9]+INNOV+DELIVERY[:5])
        for target in ('remaining_5','remaining_21','r30','regular_residual'):
            v=d[d.model.eq('frozen_parent_residual_history')&d.target.eq(target)].set_index('day').reindex(p.index)
            y=np.log1p(v.actual.to_numpy(float))
            ds=p.index.to_numpy(); end=v.target_end.fillna('9999-12-31').to_numpy()
            e=np.full(len(y),np.nan)
            for i in np.flatnonzero(v.law.notna()):
                e[i]=y[i]-atoms[int(v.law.iloc[i])].mean()
            for i in np.flatnonzero(np.isfinite(e)):
                t=matured(ds,end,e,i)
                cap=.009
                a=atoms[int(v.law.iloc[i])]
                dv,m,u=shift(xs,e,i,t,cap)
                for model,law in [('V17_same_clock',a),('V19_position_residual',a+dv)]:
                    all_atoms.append(law.astype(np.float32))
                    rows.append(dict(day=ds[i],target_end=end[i],origin=v.origin.iloc[i],cutoff=clock,
                         target=target,cohort=v.cohort.iloc[i],model=model,parent='V17_same_clock',law=len(all_atoms)-1,
                         active=int(model=='V17_same_clock' or m is not None),last_mature=max(end[u]) if len(u) else None,
                         source_release=p.source_release.iloc[i],**score(law,y[i])))
    write('postopen-cases.csv.gz',pd.DataFrame(rows))
    lengths=np.array([len(a) for a in all_atoms])
    np.savez_compressed(OUT/'postopen-endpoint-laws.npz',atoms=np.concatenate(all_atoms),offsets=np.r_[0,lengths.cumsum()])

if __name__=='__main__':
    endpoint()
    after_open()

