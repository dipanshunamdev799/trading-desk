"""Causal-feature sentinel, date perturbations and bounded representative null search."""
from .common import *
from .engine import inputs,frame_for,dates,distributions,cohort_queries,target_store,spec


def run():
    x,_,states,price,broad,pos,loss=inputs()
    cases={
      'recent':spec('rotation',budget=85),
      'spread':spec('rotation',budget=85,selection='spread'),
      'blocks':spec('rotation',budget=85,selection='random_blocks'),
      'learned':spec('rotation',budget=85,selection='usefulness'),
      'breadth':spec('rotation',plus=['BREADTH']),
      'overlap':spec('rotation',plus=['BREADTH'],overlap='blockmean'),
    }
    save('falsification-registry.json',{'registered':now(),'designs':cases,'null_draws':12,'resampling_draws':10,
         'dates':'First query from three earlier and three later distinct monthly refit folds per horizon.',
         'selection':'Compete all six methods under each null draw. Re-select historical dates with jittered history block merits and seeded random blocks.'})
    diagnostics=[];null=[];changes=[];weights=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv');t=target_store(h,y,price,broad)
        q=cohort_queries(h)
        groups=[g.iloc[0] for k,g in q.groupby(['split','fold'],sort=False)]
        earlier=[r for r in groups if r.split=='early'];later=[r for r in groups if r.split=='later']
        assessed=[earlier[i] for i in np.linspace(0,len(earlier)-1,3,dtype=int)]+later[-3:]
        for r in assessed:
            cut=r.origin;c=r.split;real=r.realized_return
            unrestricted=pd.Series(True,index=pos.index)
            baseline=dates(y,{},states,cut,unrestricted,pos,h,loss,SEED)
            hist=baseline[3][-252:];from .engine import Distribution
            benchmark=Distribution(y.loc[hist,'return'].to_numpy()).score(real)
            for name,s in cases.items():
                frame=frame_for(s,x)
                for draw in range(-1,12):
                    seed=SEED+max(0,draw)*11
                    alt=loss.copy()
                    if draw>=0 and name=='learned':
                        rng=np.random.default_rng(seed);older=alt.endpoint.lt(cut)&alt.horizon.eq(h)
                        z=alt.loc[older,'gain'].to_numpy(copy=True);alt.loc[older,'gain']=rng.permutation(z)
                    plan=dates(y,s,states,cut,unrestricted,pos,h,alt,seed)
                    ds,o,_=distributions(s,frame,y,t,pos,states,h,cut,plan,[cut],seed,permute=draw>=0)
                    a=ds[0].score(real)
                    null.append({'horizon':h,'cohort':c,'origin':cut,'design':name,'draw':draw,
                                 'brier_gain':benchmark['brier']-a['brier'],'crps_gain':benchmark['crps']-a['crps']})
                if name=='breadth':
                    s={**s,'kind':'elastic','rep':'cluster_elastic'}
                    plan=dates(y,s,states,cut,unrestricted,pos,h,loss,SEED)
                    original=distributions(s,frame,y,t,pos,states,h,cut,plan,[cut])[0][0]
                    alt=frame.assign(zz_alias=3+9*frame.b5_50,zz_alias_two=7+frame.b21_500)
                    yy=y.copy();tt=t.copy();updated=frame.copy()
                    future=y.endpoint.ge(cut)|y.endpoint.isna()
                    yy.loc[future,'return']=.5;tt.loc[future,'raw']=-.42;updated.loc[updated.index>cut]*=-13
                    for kind,source,y1,t1 in [('affine_alias',alt[alt.columns[::-1]],y,t),('future_sentinel',updated,yy,tt)]:
                        a=distributions(s,source,y1,t1,pos,states,h,cut,plan,[cut])[0][0]
                        np.testing.assert_allclose(a.a,original.a,atol=1e-10,rtol=1e-10)
                        np.testing.assert_allclose(a.w,original.w,atol=1e-10,rtol=1e-10)
                        diagnostics.append({'test':kind,'cohort':c,'horizon':h,'origin':cut,'max_atom_delta':np.max(abs(a.a-original.a))})
            for draw in range(10):
                law=[]
                for name,s in [('base',spec(selection='random_blocks',budget=85)),('breadth',spec(selection='random_blocks',budget=85,plus=['BREADTH'])),
                               ('long',spec(persistent='blocks',episode_count=2))]:
                    frame=frame_for(s,x);seed=SEED+draw*47
                    plan=dates(y,s,states,cut,unrestricted,pos,h,loss,seed)
                    if name=='long':
                        fit_dates,inner_dates,vv,pool,ic=plan
                        from research.nifty_forecast_v10.estimators import choose
                        tr=choose(fit_dates,int(.80*len(fit_dates)),'random_blocks',states,cut,seed)
                        ii=choose(inner_dates,int(.80*len(inner_dates)),'random_blocks',states,ic,seed+1)
                        plan=(tr,ii,vv,pool,ic)
                    ds,obj,_=distributions(s,frame,y,t,pos,states,h,cut,plan,[cut],seed)
                    d=ds[0];score=d.score(real);law.append(d)
                    changes.append({'horizon':h,'cohort':c,'query':cut,'draw':draw,'expert':name,'train':len(plan[0]),
                        'p':score['p'],'mean':score['predicted_mean'],'width80':score['width80'],'q10':float(d.quantile(.10)),
                        'brier':score['brier'],'crps':score['crps'],'selected':'|'.join(plan[0])})
                    m=obj['outer'];beta=(m['basis']@m['beta'][1:])[:,0]
                    weights.extend({'horizon':h,'query':cut,'draw':draw,'expert':name,'feature':n,'coefficient':b} for n,b in zip(m['scale'].cols,beta))
                a=Distribution(np.concatenate([d.a for d in law]),np.concatenate([d.w/3 for d in law]))
                s=a.score(real)
                changes.append({'horizon':h,'cohort':c,'query':cut,'draw':draw,'expert':'complete_law_mix','p':s['p'],'mean':s['predicted_mean'],
                                'width80':s['width80'],'q10':float(a.quantile(.1)),'brier':s['brier'],'crps':s['crps']})
    a=pd.DataFrame(null);selected=[]
    for (h,c,j),g in a.groupby(['horizon','cohort','draw']):
        m=g.groupby('design')[['brier_gain','crps_gain']].mean()
        for k in m:selected.append({'horizon':h,'cohort':c,'draw':j,'metric':k,'selected':m[k].idxmax(),'best_gain':m[k].max(),'origins':g.origin.nunique()})
    write('null-origins.csv',a);write('null-selected.csv',pd.DataFrame(selected))
    write('invariance-and-sentinel.csv',pd.DataFrame(diagnostics))
    write('block-perturbation.csv',pd.DataFrame(changes));write('block-perturbation-coefficients.csv',pd.DataFrame(weights))
    print(len(diagnostics),'invariance/sentinel checks;',len(a),'null evaluation points',flush=True)


if __name__=='__main__':run()
