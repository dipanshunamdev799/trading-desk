"""Registered exposure-aware follow-ups and model sensitivity diagnostics."""
from .common import *
from .experiments import cfg,run,common_indices,cohort_queries,fit_laws,cached,target_store,load


def curves():
    models={}
    for n in [85,126,189,252,300,None]:
        suffix=n or 'MAX';control=f'LC_PLAIN_{suffix}';common={'budget':n,'common_target':True}
        models[control]=cfg(parent='BASE10',**common,hypothesis='Equivalent 10-input, recent maturity-budget control')
        for code,s in [('SPREAD',{'selection':'spread'}),('BLOCK',{'overlap':'blockmean'}),('STUDENT',{'target':'vol','law':'student'})]:
            models[f'LC_{code}_{suffix}']=cfg(parent=control,**common,**s,
                 hypothesis='Adaptive V10 follow-up to fixed-row and both-cohort comparisons. No point-based cutoff tuning.')
    run('finalcurve',models)


def information():
    models={
      'N_RISK_MATCHED':cfg(parent='T_VOL_RISK',target='vol',law='risk',common_target=True,
         hypothesis='Corrected symmetric mature volatility mask after initial invalid-distribution failures'),
      'N_GLOBAL_RISK_MATCHED':cfg('global','N_RISK_MATCHED',target='vol',law='risk',common_target=True,
         hypothesis='Conservative global states on identical complete target dates'),
    }
    for frame,code in [('persistent','PERSIST'),('distributed','DISTRIBUTED')]:
        for roll in [5,21,42,'blocks']:
            parent='S_'+code
            models[f'M_{code}_PLACEBO_{str(roll).upper()}']=cfg(frame,parent,horizons=[21],rotate=roll,diagnostic=True,
               alpha=180 if code=='DISTRIBUTED' else 125,hypothesis='Train-only circular state shift or chronological block-order permutation')
    run('informationlaws',models)


def laws_equal(a,b):
    np.testing.assert_allclose(a.a,b.a,atol=2e-10,rtol=2e-10)
    np.testing.assert_allclose(a.w,b.w,atol=2e-10,rtol=2e-10)


def perturb():
    frames,_,state=cached();price=matrix('price.csv');raw,_=load();broad=raw['idx_Nifty_500'].close
    pos=pd.Series(np.arange(len(price)),index=price.index);rows=[];effects=[];null=[];selection=[]
    specs={'compact':cfg(), 'block':cfg(overlap='blockmean'), 'balanced':cfg(weight='balance'),
           'structural':cfg('native_rot',rep='groups'),'elastic':cfg('native_rot',rep='cluster_elastic',kind='elastic'),
           'small_spread':cfg(selection='spread',budget=85)}
    held=[0,3,5,8,11,13]
    save('diagnostic-protocol.json',{'registered_at':now(),'seed':SEED,'code_sha256':sha(SRC/'followup.py'),
         'null_draws':16,'null_origins':'First query of each selected earlier/later monthly fold group, at both horizons',
         'selected_fold_positions_early':held,'null_specs':specs,'perturbation_draws':12,
         'perturbation_modes':['small_blocks','small_individual','expanding_drop20'],'blocks_nominal_sessions':5})
    for h in [5,21]:
        base=matrix(f'labels-{h}.csv');store=target_store(h,base,price,broad)
        cohorts=cohort_queries(h)
        folds=[g.iloc[:1] for (c,f),g in cohorts.groupby(['split','fold'],sort=False)]
        picked=[folds[k] for k in held if k<len(folds)-5]+folds[-5:]
        for g in picked:
            d=g.origin.iloc[0];c=g.split.iloc[0];q=g.origin;real=float(g.realized_return.iloc[0])
            base_plan=common_indices(base,d,{},state);tr,ii,vv,ic,pool=base_plan;seed=SEED+int(d.replace('-',''))
            reference=fit_laws(cfg(law='history'),frames['ten'],base,store,state,pos,h,d,tr,ii,vv,q,pool)[3][0].score(real)
            if c=='later':
                for mode in ['small_blocks','small_individual','expanding_drop20']:
                    for rep in range(12):
                        rng=np.random.default_rng(seed+rep)
                        draw=lambda ix,budget:ix[np.sort(rng.choice(len(ix),size=budget,replace=False))]
                        if mode=='small_individual':ta,ia=draw(tr,85),draw(ii,min(85,len(ii)))
                        else:
                            budget=85 if mode=='small_blocks' else int(.8*len(tr))
                            smaller=min(85,len(ii)) if mode=='small_blocks' else int(.8*len(ii))
                            from .estimators import choose
                            ta=choose(tr,budget,'random_blocks',state,d,seed+rep)
                            ia=choose(ii,smaller,'random_blocks',state,ic,seed+rep+100)
                        m,_,_,ds,_,_=fit_laws(cfg(),frames['ten'],base,store,state,pos,h,d,ta,ia,vv,q,pool)
                        score=ds[0].score(real)
                        rows.append({'origin':d,'horizon':h,'mode':mode,'rep':rep,'n':len(ta),'inner':len(ia),
                            'p':score['p'],'mean':score['predicted_mean'],'brier':score['brier'],'crps':score['crps'],
                            'training_dates':'|'.join(ta),'inner_dates':'|'.join(ia),
                            **{f'beta_{k}':val for k,val in zip(m['scale'].cols,(m['basis']@m['beta'][1:])[:,0])}})
                x=frames['native_rot'];names=[n for n in x if 'nifty_fmcg' in n or 'nifty_pharma' in n][:5]
                extra=x.assign(**{f'zz_v10_{j}_{n}':3+7*x[n] for n in names for j in range(3)})
                for model in ['structural','elastic']:
                    spec=specs[model];active=fit_laws(spec,x,base,store,state,pos,h,d,tr,ii,vv,q,pool)[3][0]
                    for case,a in [('affine_copies',extra),('reordered',extra[extra.columns[::-1]])]:
                        other=fit_laws(spec,a,base,store,state,pos,h,d,tr,ii,vv,q,pool)[3][0]
                        laws_equal(active,other);effects.append({'horizon':h,'origin':d,'model':model,'test':case,
                           'max_atom_error':float(abs(active.a-other.a).max()),'max_weight_error':float(abs(active.w-other.w).max())})
                    cutoff_for_data=base.endpoint.isna()|base.endpoint.ge(d);xp=x.copy();xp.loc[xp.index>d]*=-3891.
                    yp=base.copy();yp.loc[cutoff_for_data,'return']=.78
                    changed=store.copy();changed.loc[cutoff_for_data,'raw']=.78
                    other=fit_laws(spec,xp,yp,changed,state,pos,h,d,tr,ii,vv,q,pool)[3][0]
                    laws_equal(active,other);effects.append({'horizon':h,'origin':d,'model':model,'test':'future_labels_and_features_sentinel',
                           'max_atom_error':float(abs(active.a-other.a).max()),'max_weight_error':float(abs(active.w-other.w).max())})
            for name,s in specs.items():
                x=frames[s['frame']];train,inner,valid,_,past=common_indices(base,d,s,state)
                for rep in range(-1,16):
                    store0=store.copy()
                    if rep>=0:
                        rng=np.random.default_rng(seed+rep)
                        for dates in [train,inner]:
                            # Fit-label blocks are permuted separately for outer and inner models.
                            # The inner fit receives its own copy, while validation and history stay genuine.
                            blocks=np.array_split(store.loc[dates,'raw'].to_numpy(),max(2,len(dates)//h))
                            raw_permuted=np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
                            if dates is train:store0.loc[dates,'raw']=raw_permuted
                            else:
                                from .estimators import fit,location
                                from .targets import paired_laws
                                m=fit(s,x.loc[train],store0.loc[train,'raw'],pos.loc[train].to_numpy(),h,state,d)
                                inn=fit(s,x.loc[inner],raw_permuted,pos.loc[inner].to_numpy(),h,state,valid[0])
                                resid=store.loc[valid,'raw'].to_numpy()[:,None]-location(inn,x.loc[valid])
                                law=paired_laws({},'raw',store,q,location(m,x.loc[q]),resid,base.loc[past[-252:],'return'].to_numpy())[0]
                    else:law=fit_laws(s,x,base,store,state,pos,h,d,train,inner,valid,q,past)[3][0]
                    score=law.score(real)
                    null.append({'horizon':h,'cohort':c,'origin':d,'model':name,'draw':rep,
                         'brier_gain':reference['brier']-score['brier'],'crps_gain':reference['crps']-score['crps']})
        print('Diagnostics',h,len(null),len(effects),flush=True)
    a=pd.DataFrame(null)
    for (h,c,j),g in a.groupby(['horizon','cohort','draw']):
        means=g.groupby('model')[['brier_gain','crps_gain']].mean()
        for m in means:
            selection.append({'horizon':h,'cohort':c,'draw':j,'metric':m,'selected_model':means[m].idxmax(),'best_gain':means[m].max(),'origins':g.origin.nunique()})
    write('bounded-null-origins.csv',a);write('bounded-null-selection.csv',pd.DataFrame(selection))
    write('training-perturbations.csv',pd.DataFrame(rows));write('invariance-sentinel.csv',pd.DataFrame(effects))


if __name__=='__main__':
    import sys
    {'curves':curves,'information':information,'perturb':perturb}[sys.argv[1]]()
