"""Registered paired walk-forward experiments for both endpoint horizons."""
import joblib
from sklearn.linear_model import Ridge
from .common import *
from research.nifty_forecast_v10.features import cached
from research.nifty_forecast_v10.estimators import Distribution,choose,fit,location,diagnostics
from research.nifty_forecast_v10.targets import target_store,transformed,paired_laws,sign_magnitude,buckets
from research.nifty_forecast_v10.experiments import eligible_target
from research.nifty_forecast_v9.run_models import cohort_queries,score_law
from research.nifty_forecast_v3.experiment import available
from research.nifty_forecast_v5.data import load
from research.nifty_forecast_v8.models import Scale,canonical


def spec(frame='rotation',parent='B_ROT',**kw):
    return {'frame':frame,'parent':parent,**kw}


BREADTH={
 'B_ROT':spec(parent='BASE_ROTATION'),
 'B_NATIVE':spec('native','BASE_NATIVE'),
 'B_TEN':spec('ten','BASE10'),
 'B_SPARSE':spec('native_rot','S_ELASTIC',kind='elastic',rep='cluster_elastic'),
 'B_STUD':spec('ten','T_VOL_STUDENT',target='vol',law='student',target_mask=True),
 'B_ROT_EQ':spec(plus=['BREADTH']),
 'B_NATIVE_EQ':spec('native','B_NATIVE',plus=['BREADTH']),
 'B_TEN_EQ':spec('ten','B_TEN',plus=['BREADTH']),
 'B_SPARSE_EQ':spec('native_rot','B_SPARSE',kind='elastic',rep='cluster_elastic',plus=['BREADTH']),
 'B_STUD_EQ':spec('ten','B_STUD',target='vol',law='student',target_mask=True,plus=['BREADTH']),
 'B_EQUAL_ONLY':spec(plus=['EQUAL']),
 'B_CAP_ONLY':spec(plus=['CAP']),
 'B_PAIR100':spec(plus=['PAIR100']),
 'B_CHANGE':spec(plus=['CHANGE']),
 'B_PERSIST':spec(plus=['PERSIST']),
 'B_FIN_INTERACT':spec(plus=['BREADTH','INTERACT'],parent='B_ROT_EQ'),
 'B_EQ_MOMO_DROP':spec(parent='B_MOMO_DROP',plus=['BREADTH'],drop_mom=True),
 'B_MOMO_DROP':spec(drop_mom=True,diagnostic=True),
 'B_SIZE_RISK':spec(plus=['CONTROL']),
 'B_EQ_SIZE_RISK':spec(plus=['RESID'],residual=True,parent='B_SIZE_RISK'),
 'B_EQ_CLOSE':spec(plus=['SAME_CLOSE'],diagnostic=True),
 'B_EQ_LAG5':spec(plus=['LAG5'],diagnostic=True),
 'B_EQ_SHIFT21':spec(plus=['BREADTH'],shift=21,diagnostic=True),
 'B_EQ_SHIFT42':spec(plus=['BREADTH'],shift=42,diagnostic=True),
 'B_EQ_PERM':spec(plus=['BREADTH'],shift='blocks',diagnostic=True),
 'B_STYLE':spec(plus=['FACTOR'],mask='FACTOR'),
 'B_STYLE_PARENT':spec(mask='FACTOR'),
 'L_CONC':spec(plus=['CONC']),
 'L_EQ_CONC':spec(plus=['BREADTH','CONC'],parent='B_ROT_EQ'),
 'L_BASIC':spec('STATE','B_TEN'),
 'L_CHANGE':spec('STATE_CHANGE','L_BASIC'),
 'L_PERSIST':spec('STATE_PERSIST','L_BASIC'),
 'L_NO_FIN':spec('L_NO_FIN','L_BASIC',diagnostic=True),
}
BREADTH['B_STYLE']['parent']='B_STYLE_PARENT'

MEMORY={}
for budget in [85,126,189,252,300,None]:
    suffix=budget or 'MAX'
    baseline=f'M_RECENT_{suffix}'
    for rule in ['recent','earliest','spread','balance_vol','balance_rotation','blocks','random_blocks','diverse','usefulness']:
        name=f'M_{rule.upper()}_{suffix}'
        MEMORY[name]=spec('rotation',parent='B_ROT' if rule=='recent' else baseline,budget=budget,selection=rule,
                          diagnostic=rule=='random_blocks')
for rule in ['recent','spread']:
    for k in [1,2,3]:
        MEMORY[f'M_OMIT_{rule.upper()}{k}']=spec('rotation',f'M_{rule.upper()}_85',budget=85,selection=rule,omit=k,diagnostic=True)
for n,kw in {
    'P_SHORT':{'budget':85},'P_RECENT_SHRINK':{'persistent':'residual'},'P_RECENT_FREE':{'persistent':'free'},
    'P_LONG_SHORT':{'persistent':'mean'},'P_BLOCK_EXPERTS':{'persistent':'blocks'},'P_HIER':{'persistent':'hierarchical'},
    'P_BREADTH_PERSIST':{'persistent':'residual','plus':['BREADTH','PERSIST'],'parent':'B_ROT_EQ'},
}.items():MEMORY[n]=spec(**kw)

OVERLAP={}
for frame,code,parent in [('ten','COMPACT','B_TEN'),('rotation','ROT','B_ROT'),('native','NATIVE','B_NATIVE')]:
    for kind in ['plain','phase0','phase1','staggered','overlap_weight','gls','gls_empirical','blockmean']:
        OVERLAP[f'O_{code}_{kind.upper()}']=spec(frame,parent,overlap=kind)
for kind in ['plain','blockmean','staggered','gls','overlap_weight']:
    for rule in ['recent','spread']:
        OVERLAP[f'O85_{rule.upper()}_{kind.upper()}']=spec('rotation','M_'+rule.upper()+'_85',budget=85,selection=rule,overlap=kind)
for rule in ['disjoint_recent','disjoint_spread']:
    OVERLAP[f'O_{rule.upper()}']=spec('rotation','B_ROT',selection=rule,budget=14)

REPAIR={f'O_COMPACT_{rule.upper()}':spec('rotation','B_ROT',selection=rule,budget=14,small_disjoint=True)
        for rule in ['disjoint_recent','disjoint_spread']}

DISTRIBUTION={}
for code,frame,plus in [('ROT','rotation',[]),('EQ','rotation',['BREADTH']),('NATIVE','native',[])]:
    parent=f'D_{code}_RAW'
    for method,changes in [
      ('RAW',{}),('VOL',{'target':'vol'}),('STUDENT',{'target':'vol','law':'student'}),
      ('SIGNMAG',{'target':'signmag'}),('ASYM',{'target':'vol','extra':'asym'}),
      ('TAIL',{'target':'vol','extra':'tail'}),('SCALE',{'target':'vol','extra':'scale'}),
      ('SHARED',{'target':'split','shared_rank':1}),
    ]:
        DISTRIBUTION[f'D_{code}_{method}']=spec(frame,parent if method!='RAW' else 'B_ROT',plus=plus,target_mask=True,**changes)
for n,key in [('DERIV_RISK','DERIV'),('INTRA','INTRADAY'),('GLOBAL_RISK','GLOBAL'),('ETF','ETF')]:
    parent=f'D_{n}_PARENT'
    options={'target':'vol','extra':'scale','mask':key,'target_mask':True}
    DISTRIBUTION[parent]=spec(parent='D_ROT_SCALE',**options)
    DISTRIBUTION['D_'+n]=spec(parent=parent,plus=[key],scale_only=key in ['DERIV','GLOBAL'],**options)
DISTRIBUTION['D_INTRA_TIMING']=spec(parent='D_INTRA_PARENT',plus=['INTRADAY'],target='vol',extra='scale',mask='INTRADAY',target_mask=True,shift=5,diagnostic=True)

INTERNATIONAL={
 'I_CAP_PARENT':spec(parent='B_ROT_EQ',plus=['BREADTH','US_CAP']),
 'I_EQ':spec(parent='I_CAP_PARENT',plus=['BREADTH','US_CAP','US_EQ']),
 'I_DIVERGE':spec(parent='I_CAP_PARENT',plus=['BREADTH','US_CAP','US_DIVERGE']),
 'I_RISK_PARENT':spec(parent='D_EQ_SCALE',target='vol',extra='scale',target_mask=True,plus=['BREADTH','US_CAP']),
 'I_RISK_EQ':spec(parent='I_RISK_PARENT',target='vol',extra='scale',target_mask=True,plus=['BREADTH','US_CAP','US_EQ']),
}


def inputs():
    x,masks,state=cached()
    for name in read('feature-definitions.json'):
        x[name]=matrix(f'matrices/{name}.csv',OUT)
    x['L_NO_FIN']=x['STATE'].drop(columns='s_bank')
    price=matrix('price.csv');raw,_=load();broad=raw['idx_Nifty_500'].close
    pos=pd.Series(np.arange(len(price)),index=price.index)
    old=pd.read_csv(V10/'base-predictions.csv')
    a=old[old.model.eq('BASE10')].set_index(['horizon','origin'])
    hist=old[old.model.eq('HISTORY')].set_index(['horizon','origin'])
    loss=(hist.brier-a.brier).rename('gain').reset_index().merge(a.endpoint.reset_index(),on=['horizon','origin'])
    return x,masks,state,price,broad,pos,loss


def select(dates,s,states,anchor,pos,h,loss,seed):
    rule=s.get('selection','recent');budget=s.get('budget')
    if 'omit' in s:
        months=pd.Index(dates.str[:7]).unique().sort_values(ascending=False)
        dates=dates[dates.str[:7]!=months[s['omit']-1]]
    if rule.startswith('disjoint'):
        keep=[];prior=-h
        for d in dates:
            if pos.loc[d]-prior>=h:keep.append(d);prior=pos.loc[d]
        dates=pd.Index(keep)
        n=min(budget,len(dates))
        return choose(dates,n,'spread' if rule.endswith('spread') else 'recent',states,anchor,seed)
    if budget is None or len(dates)<=budget:return dates
    if rule=='usefulness':
        z=loss[loss.endpoint.lt(anchor)&loss.horizon.eq(h)].copy()
        performance=z.groupby(z.origin.str[:7]).gain.agg(['sum','size'])
        shrink=performance['sum']/(12+performance['size'])
        # Keep half the historical coverage and fill the rest with prior-exposed episodes.
        cover=choose(dates,budget//2,'spread',states,anchor,seed);remain=dates.difference(cover)
        merit=pd.Series(remain.str[:7],index=remain).map(shrink).fillna(0)
        remainder=[]
        by_month={m:list(g.index) for m,g in merit.groupby(merit.index.str[:7])}
        ordering=sorted(by_month,key=lambda m:(-float(shrink.get(m,0)),m))
        while len(remainder)<budget-len(cover):
            for m in ordering:
                if by_month[m]:remainder.append(by_month[m].pop(len(by_month[m])//2))
                if len(remainder)==budget-len(cover):break
        return cover.union(pd.Index(remainder)).sort_values()
    if rule=='diverse':
        z=states.loc[dates,['s_vol','s_trend','s_bank']].copy()
        z=z.fillna(z.median()).fillna(0)
        z=z.apply(lambda a:a.rank(pct=True).gt(.5).astype(int))
        bins=z.s_vol+2*z.s_trend+4*z.s_bank
        groups=[bins[bins==g].index.tolist() for g in sorted(bins.unique())]
        orders=[list(np.array(a)[np.argsort(np.random.default_rng(seed+j).random(len(a)))]) for j,a in enumerate(groups)]
        chosen=[]
        while len(chosen)<budget:
            for a in orders:
                if a:chosen.append(a.pop())
                if len(chosen)==budget:break
        return pd.Index(sorted(chosen))
    return choose(dates,budget,rule,states,anchor,seed)


def dates(y,s,state,anchor,mask,pos,h,loss,seed):
    pool=available(y,anchor)
    pool=pool[mask.reindex(pool).fillna(False).to_numpy()]
    need=85 if s.get('selection','').startswith('disjoint') else max(85,s.get('budget') or 0)
    if len(pool)<need:raise ValueError('Insufficient mature outer budget')
    valid=pool[-28:];ic=valid[0];history=pool[y.loc[pool,'endpoint']<ic]
    if len(history)<38:raise ValueError('Insufficient purged inner budget')
    inner={**s}
    if inner.get('budget') and not inner.get('selection','').startswith('disjoint'):
        inner['budget']=min(inner['budget'],len(history))
    tr=select(pool,s,state,anchor,pos,h,loss,seed)
    ii=select(history,inner,state,ic,pos,h,loss,seed+1)
    if not s.get('selection','').startswith('disjoint') and len(tr)<need:raise ValueError('Budget unavailable after deletion')
    if min(len(ii),len(tr))<3:raise ValueError('Insufficient effective fit')
    assert y.loc[tr,'endpoint'].max()<anchor and y.loc[ii,'endpoint'].max()<ic and y.loc[valid,'endpoint'].max()<anchor
    return tr,ii,valid,pool,ic


def frame_for(s,x):
    base=x[s['frame']].copy()
    if s.get('drop_mom'):
        base=base[[c for c in base if not any(a in c for a in ['p_ret','trend','rel5','rel21','return','momentum'])]]
    for n in s.get('plus',[]):base=base.join(x[n],rsuffix='_added')
    return base


def causal_x(s,x,tr,q,fit_input,seed):
    a=x.loc[tr].copy();b=x.loc[q].copy();fitted={}
    if s.get('residual'):
        columns=[c for c in a if c.startswith(('b5_','b21_'))]
        controls=['size','small','rel_risk','rel_level_risk','p_ret5','p_ret21']
        med=a[controls].median().fillna(0)
        scale=a[controls].std().clip(lower=1e-5).fillna(1)
        ex=((a[controls].fillna(med)-med)/scale).clip(-8,8)
        eq=((b[controls].fillna(med)-med)/scale).clip(-8,8)
        for c in columns:
            ok=a[c].notna()
            model=Ridge(alpha=35).fit(ex.loc[ok],a.loc[ok,c])
            a[c]-=model.predict(ex);b[c]-=model.predict(eq)
            fitted[c]=(model,med,scale)
    if 'shift' in s:
        cols=[c for c in a if c.startswith(('b5_','b21_','v11_'))]
        if isinstance(s['shift'],int):a[cols]=np.roll(a[cols].to_numpy(),s['shift'],axis=0)
        else:
            pieces=np.array_split(a[cols].to_numpy(),max(2,len(a)//21));rng=np.random.default_rng(seed)
            a[cols]=np.concatenate([pieces[j] for j in rng.permutation(len(pieces))])
    return a,b,fitted


def location_fit(s,a,b,y,p,h,state,anchor):
    if s.get('small_disjoint'):
        # A disjoint sample at 21 sessions has fewer rows than the usual robust
        # scale requires. Register a compact equivalent rule for both selectors.
        chosen=a[['p_ret5','p_ret21','p_rv21','i_participation','r_bank_residual','r_def_residual']]
        z=chosen.replace([np.inf,-np.inf],np.nan)
        z=z.loc[:,z.notna().sum().ge(3)&z.std().gt(1e-10)]
        if z.shape[1]==0:raise ValueError('No estimable inputs at disjoint budget')
        scaler=Scale();scaler.cols=list(z);scaler.med=z.median().to_numpy()
        filled=z.fillna(z.median()).to_numpy()
        scaler.mu=filled.mean(axis=0);scaler.sd=filled.std(axis=0).clip(min=1e-8)
        raw=(filled-scaler.mu)/scaler.sd
        ids,aliases=canonical(scaler.cols,np.c_[raw.T,z.notna().to_numpy().T])
        basis=np.eye(z.shape[1])[:,ids]
        r=Ridge(alpha=30).fit(scaler.transform(a)@basis,y)
        beta=np.vstack([np.asarray(r.intercept_).reshape(1,-1),np.atleast_2d(r.coef_).T])
        meta=diagnostics(p.loc[a.index].to_numpy(),h,np.ones(len(a)))
        meta.update(aliases=aliases,parameters=beta.size,df=float(beta.size))
        model={'scale':scaler,'basis':basis,'beta':beta,'metadata':meta}
        return model,location(model,b)
    model=fit(s,a,y,p.loc[a.index].to_numpy(),h,state,anchor)
    prediction=location(model,b)
    conf=s.get('persistent')
    if not conf:return model,prediction
    recent=a.iloc[-85:];ys=np.asarray(y)[-len(recent):]
    if conf=='blocks':
        experts=[];pred=[]
        for indices in np.array_split(np.arange(len(a)),s.get('episode_count',3)):
            part=a.iloc[indices];agent=fit(s,part,np.asarray(y)[indices],p.loc[part.index].to_numpy(),h,state,anchor)
            experts.append(agent);pred.append(location(agent,b))
        model['supplement']=experts
        model['metadata']['expert_location_variance']=float(np.mean(np.var(pred,axis=0)))
        return model,.5*prediction+.5*np.mean(pred,axis=0)
    if conf in ['residual','hierarchical']:
        residual=ys-location(model,recent)
        options={**s,'alpha':650 if conf=='residual' else 325}
        extension=fit(options,recent,residual,p.loc[recent.index].to_numpy(),h,state,anchor)
        increment=location(extension,b)-extension['beta'][0] if conf=='hierarchical' else location(extension,b)
        result=prediction+.5*increment
    else:
        extension=fit(s,recent,ys,p.loc[recent.index].to_numpy(),h,state,anchor)
        result=location(extension,b) if conf=='free' else .65*prediction+.35*location(extension,b)
    model['supplement']=extension
    model['metadata']['expert_location_variance']=float(np.mean((prediction-result)**2))
    return model,result


def distributions(s,frame,y,store,p,state,h,anchor,plan,query,seed=SEED,permute=False):
    tr,ii,vv,pool,ic=plan
    target=s.get('target','raw')
    outer,ctx=transformed(store,target,tr);inner,ictx=transformed(store,target,ii)
    a,b,outer_res=causal_x(s,frame,tr,query,True,seed)
    c,d,inner_res=causal_x(s,frame,ii,vv,True,seed+1)
    targets=lambda values,idx:values[store.index.get_indexer(idx)]
    ya,yi=targets(outer,tr),targets(inner,ii)
    if permute:
        rng=np.random.default_rng(seed)
        def perm(values):
            blocks=np.array_split(values,max(2,len(values)//h))
            return np.concatenate([blocks[j] for j in rng.permutation(len(blocks))])
        ya,yi=perm(ya),perm(yi)
    loc_a=a;loc_b=b;loc_c=c;loc_d=d
    if s.get('scale_only'):
        cols=[k for k in a if k not in s['_scale_cols']]
        loc_a,loc_b,loc_c,loc_d=(g[cols] for g in [a,b,c,d])
    m,point=location_fit(s,loc_a,loc_b,ya,p,h,state,anchor)
    m0,valid_point=location_fit(s,loc_c,loc_d,yi,p,h,state,ic)
    residual=targets(inner,vv)-valid_point
    past=y.loc[pool[-252:],'return'].to_numpy()
    method=s.get('extra')
    risk_forecast=None;scale_model=None
    if method=='scale':
        # Model the conditional endpoint magnitude separately from location.
        scale_targets=np.log(np.maximum(abs(y.loc[tr,'return'].to_numpy())/store.loc[tr,'vol_scale'],.10))
        rv_target=np.log(y.loc[tr,'volatility'].clip(lower=.015))
        unit_state=a.replace([np.inf,-np.inf],np.nan)
        med=unit_state.median().fillna(0);std=unit_state.std().fillna(1).clip(lower=1e-5)
        design=((unit_state.fillna(med)-med)/std).clip(-5,5)
        test=((b.fillna(med)-med)/std).clip(-5,5)
        scale_model=Ridge(alpha=325).fit(design,np.c_[scale_targets,rv_target])
        pred=scale_model.predict(test)
        factor=np.clip(np.exp(.65*(pred[:,0]-scale_targets.mean())),.65,1.5)
        risk_forecast=np.exp(.70*pred[:,1]+.30*rv_target.mean())
        from research.nifty_forecast_v10.targets import inverse
        laws=[]
        for j,k in enumerate(query):
            atoms=inverse(point[j]+residual*factor[j],store.loc[k],target,ctx)
            laws.append(Distribution(np.r_[atoms,past],np.r_[np.full(len(atoms),.65/len(atoms)),np.full(len(past),.35/len(past))]))
    elif target=='signmag':laws=sign_magnitude(m,frame,y,tr,query)
    elif method=='asym':
        from scipy.stats import t
        from research.nifty_forecast_v10.targets import inverse
        e=residual[:,0];std=np.sqrt(np.mean(e**2));lo=np.sqrt(np.mean(np.minimum(e,0)**2)*2);hi=np.sqrt(np.mean(np.maximum(e,0)**2)*2)
        lo=np.sqrt(.6*std**2+.4*lo**2);hi=np.sqrt(.6*std**2+.4*hi**2)
        q=t.ppf((np.arange(301)+.5)/301,5)*np.sqrt(3/5)
        atom=q*np.where(q<0,lo,hi);laws=[]
        for j,k in enumerate(query):
            r=inverse(point[j]+atom[:,None],store.loc[k],target,ctx)
            laws.append(Distribution(np.r_[r,past],np.r_[np.full(len(r),.65/len(r)),np.full(len(past),.35/len(past))]))
    else:
        laws=paired_laws(ctx,target,store,query,point,residual,past,s.get('law','empirical'))
        if method=='tail':
            tail=past[past<=np.quantile(past,.10)]
            laws=[Distribution(np.r_[law.a,tail],np.r_[law.w*.94,np.full(len(tail),.06/len(tail))]) for law in laws]
    return laws,{'outer':m,'inner':m0,'residuals':residual,'outer_residualizers':outer_res,'inner_residualizers':inner_res,
                 'scale_model':scale_model,'context':ctx},risk_forecast


def run(batch):
    models={'breadth':BREADTH,'memory':MEMORY,'overlap':OVERLAP,'distribution':DISTRIBUTION,'disjoint':REPAIR,'international':INTERNATIONAL}[batch]
    if (OUT/f'{batch}-registry.json').exists():raise FileExistsError(batch)
    save(f'{batch}-registry.json',{'registered':now(),'models':models,'seed':SEED,'source':sha(SRC/'engine.py')})
    frames,masks,state,price,broad,pos,loss=inputs()
    path=OUT/'models';path.mkdir(exist_ok=True)
    ratings=[];folds=[];laws=[];weights=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv');t=target_store(h,y,price,broad)
        for (cohort,fold),g in cohort_queries(h).groupby(['split','fold'],sort=False):
            k=g.origin.min()
            for name,s in models.items():
                item={'model':name,'horizon':h,'cohort':cohort,'fold':fold,'cutoff':k}
                try:
                    x=frame_for(s,frames);mask=pd.Series(True,index=x.index)
                    if s.get('target_mask'):mask &= eligible_target(t)
                    if 'mask' in s:mask &= frames[s['mask']].notna().any(axis=1)
                    q=g[mask.loc[g.origin].to_numpy()]
                    if q.empty:raise ValueError('No eligible queries')
                    settings={**s,'_scale_cols':list(frames[s['plus'][0]]) if s.get('scale_only') else []}
                    plan=dates(y,s,state,k,mask,pos,h,loss,SEED);tr,ii,vv,pool,ic=plan
                    ds,obj,rv=distributions(settings,x,y,t,pos,state,h,k,plan,q.origin)
                    rel=f'models/{batch}-{h}-{cohort}-{fold}-{name}.joblib'
                    joblib.dump({**obj,'train':list(tr),'inner_dates':list(ii),'validation':list(vv),'query':list(q.origin),'pool':list(pool[-252:])},OUT/rel,compress=2)
                    point=q.origin.tolist();cuts=np.quantile(y.loc[pool[-252:],'return'],[.1,.3,.5,.7,.9])
                    for j,(row,d) in enumerate(zip(q.itertuples(),ds)):
                        score={**score_law(h,fold,name,row,d,float(price.close.loc[row.origin]),cohort),**buckets(d,row.realized_return,cuts)}
                        score['abs_return_error']=abs(score['expected_abs']-abs(row.realized_return))
                        if rv is not None:
                            score['path_risk_estimate']=rv[j];score['path_risk_realized']=y.loc[row.origin,'volatility']
                            score['path_risk_abs_error']=abs(rv[j]-score['path_risk_realized'])
                        ratings.append(score)
                        if name in ['B_ROT','B_ROT_EQ','B_SPARSE','B_SPARSE_EQ','B_STUD','B_STUD_EQ','B_NATIVE_EQ','L_EQ_CONC','D_ROT_STUDENT','D_EQ_STUDENT','D_EQ_SIGNMAG','D_EQ_TAIL','D_DERIV_RISK','D_ETF','P_LONG_SHORT','M_SPREAD_85','O_ROT_BLOCKMEAN']:
                            laws.append({'model':name,'horizon':h,'cohort':cohort,'origin':row.origin,'endpoint':row.endpoint,
                                         'atoms':d.a.tolist(),'weights':d.w.tolist()})
                    m=obj['outer'];beta=(m['basis']@m['beta'][1:])[:,0]
                    weights.extend({**item,'feature':field,'coefficient':v} for field,v in zip(m['scale'].cols,beta))
                    item.update(status='ok',training=len(tr),inner=len(ii),valid=len(vv),inner_cutoff=ic,training_endpoint=y.loc[tr,'endpoint'].max(),
                        inner_endpoint=y.loc[ii,'endpoint'].max(),queries=len(q),file=rel,sha256=sha(OUT/rel),support=m['metadata'])
                except (ValueError,KeyError,IndexError,np.linalg.LinAlgError) as e:item.update(status='unestimated',reason=str(e))
                folds.append(item)
        print(batch,h,len(ratings),'predictions;',sum(f['status']!='ok' for f in folds),'unestimated folds',flush=True)
    write(f'{batch}-predictions.csv',pd.DataFrame(ratings));save(f'{batch}-ledger.json',folds)
    write(f'{batch}-coefficients.csv',pd.DataFrame(weights));cache(f'{batch}-laws.jsonl',laws)


if __name__=='__main__':
    import sys
    run(sys.argv[1])
