"""Matched contrasts, calibration, chronological stress and search adjustment."""
from .common import *
from .models import Distribution
from research.nifty_forecast_v6.analyze import benchmark_frames
from research.nifty_forecast_v5.analyze import summary
from research.nifty_forecast_v3.experiment import nonoverlap, effective_n, available

BATCHES = ['compression','structure','distribution','advanced','liquidity','falsification','intermediate','global','integration','followup']
CONTROLS = ['V6_BRIER','V6_CRPS','V6_DEF_NORM','I03_nosize','I00','L01','V4_D02_student_shrunk','V4_D03_residual_shrunk','V4_M05_lgbm','V4_Z_neutral','E00','V6_MONTH_STATE','V6_MONTH_LAG1']
SCORES = ['brier','crps','mae']


def benchmarks():
    ref = benchmark_frames()
    out = {k:g.reset_index() for k,g in ref.items() if k[1] in CONTROLS}
    v6=pd.read_csv(V6/'all-predictions.csv')
    for actual,name in [('F_NO_DEFENSIVE','V6_BRIER'),('W2_NOAUTO_VOLUME','V6_CRPS'),('W2_DEF_NORM','V6_DEF_NORM'),
                        ('M_WEEKSTATE','V6_MONTH_STATE'),('M2_STATE_LAG1','V6_MONTH_LAG1')]:
        for h,g in v6[v6.model==actual].groupby('horizon'):out[h,name]=g.assign(model=name)
    return out


def intervals(contrasts,calendar,h,blocks):
    rng=np.random.default_rng(SEED+blocks);n=len(calendar)
    start=rng.integers(0,n,(2000,int(np.ceil(n/blocks))))
    ix=((start[:,:,None]+np.arange(blocks))%n).reshape(2000,-1)[:,:n]
    matrix=np.column_stack([d.reindex(calendar).to_numpy(float) for d in contrasts]);center=np.nanmean(matrix,axis=0)
    boot=np.column_stack([np.nanmean(matrix[:,j][ix],axis=1) for j in range(matrix.shape[1])])
    sd=np.maximum(np.nanstd(boot,axis=0),1e-12)
    k=np.nanquantile(np.nanmax(abs((boot-center)/sd),axis=1),.95)
    return center-k*sd,center+k*sd,np.nanquantile(boot,.025,axis=0),np.nanquantile(boot,.975,axis=0),float(k)


def metrics(h,name,g,status):
    g=g.sort_values('origin').copy()
    if 'bucket_y' not in g:g['bucket_y']=np.digitize(g.realized_return,[-.05,-.02,-.005,.005,.02,.05])
    s=summary(g)
    count=len(nonoverlap(g));ess=effective_n(g.realized_return,h)
    return {'horizon':h,'model':name,**s,'disjoint_n':count,'ESS':ess,'status':status}


def auxiliary():
    glob=pd.read_csv(OUT/'auxiliary-global-predictions.csv');glob=glob[glob.split=='outer_exposed'].dropna(subset=['actual'])
    state=pd.read_csv(OUT/'state-risk-predictions.csv');answers=[]
    for name,table in [('global',glob),('state',state)]:
        slices=[('all',table)]
        if name=='global':
            slices += [(f'{c}={v}',table[table[c]==v]) for c in ['high_correlation','high_volatility'] for v in [True,False]]
        for regime,t in slices:
            for (h,target,method),g in t.groupby(['horizon','target','method']):
                error=g.prediction-g.actual
                answers.append({'family':name,'regime':regime,'horizon':h,'target':target,'method':method,'n':len(g),
                                'mae':float(abs(error).mean()),'rmse':float(np.sqrt((error**2).mean())),
                                'actual_mean':float(g.actual.mean())})
    pd.DataFrame(answers).to_csv(OUT/'auxiliary-comparison.csv',index=False)


def run():
    registry={};ledgers=[];parts=[]
    for b in BATCHES:
        plans=read(f'{b}-registry.json');g=pd.read_csv(OUT/f'{b}-predictions.csv');parts.append(g.assign(batch=b))
        registry.update({n:{'batch':b,**s} for n,s in plans['configurations'].items()})
        if b!='integration':ledgers.extend(read(f'{b}-ledger.json'))
    allp=pd.concat(parts,ignore_index=True);allp.to_csv(OUT/'all-predictions.csv',index=False)
    assert not allp.duplicated(['horizon','model','origin']).any()
    save('experiment-registry.json',{'configurations':registry,'fit_attempts':ledgers,'auxiliary_fits':read('auxiliary-ledger.json'),
         'integration_fits':read('integration-ledger.json'),
         'superseded_attempts':{'first_global_integration':'V5 I03 only had outer rows. 27 downstream fits failed minimum history. Archive preserved. Corrected with frozen V3 B00 development origins.',
                                 'integration_attribution':'Corrected origin source needed V5 trend and volatility metadata join. Initial unsuccessful registry preserved separately.'},
         'stopping_rule':'Bounded initial batches plus 15 weekly follow-up configurations motivated by V7 exposed ranking. No extensive hyperparameter expansion.'})
    pd.DataFrame(ledgers).to_csv(OUT/'fit-ledger.csv',index=False)
    ref=benchmarks();seen={};outs=[];pairs=[];lossseries=[];increments=[];stress=[];regimes=[];month_lag=[]
    for (h,name),g in ref.items():
        outs.append(metrics(h,name,g,'frozen reference'))
    for (h,name),g in allp.groupby(['horizon','model']):
        s=registry[name];status='diagnostic' if s.get('diagnostic') or h in [10,15] else 'research-exposed'
        if name.startswith('M_STATE'):status='monthly state falsification'
        r=metrics(h,name,g,status);r.update(batch=s['batch'],parent=s['parent'],feature_family=s.get('frame','parent return laws'),
               architecture=s.get('kind','mixture' if name.startswith('J_') else 'ridge'),representation=s.get('rep','raw'),
               law=s.get('law','empirical'),leakage_status='retrospective source receipts unavailable' if name!='L_STOCK_PROXY' else 'current basket selection exposure')
        outs.append(r);seen[h,name]=g
    for (h,name),g in seen.items():
        g=g.set_index('origin').sort_index();parent=registry[name]['parent'];p=seen.get((h,parent),ref.get((h,parent)))
        if p is not None:
            same=g.index.intersection(p.origin);b=p.set_index('origin').loc[same]
            for score in SCORES:increments.append({'horizon':h,'model':name,'parent':parent,'metric':score,'n':len(same),'gain':float((b[score]-g.loc[same,score]).mean())})
        if h in [10,15]:
            label=matrix(f'labels-{h}.csv')
            for fold,z in g.groupby('fold'):
                dates=available(label,z.index.min());d=Distribution(label.loc[dates[-252:],'return'].to_numpy())
                for origin,row in z.iterrows():
                    b=d.score(row.realized_return)
                    month_lag.append({'horizon':h,'model':name,'origin':origin,'brier_gain':b['brier']-row.brier,
                                      'crps_gain':b['crps']-row.crps,'hist_crps':b['crps']})
            continue
        for (bh,base),bf in ref.items():
            if bh!=h:continue
            same=g.index.intersection(bf.origin);b=bf.set_index('origin').loc[same];z=g.loc[same]
            assert np.array_equal(z.endpoint,b.endpoint)
            np.testing.assert_allclose(z.realized_return,b.realized_return,atol=1e-12)
            for score in SCORES:
                delta=b[score]-z[score]
                pairs.append({'horizon':h,'model':name,'baseline':base,'metric':score,'n':len(same),'gain':float(delta.mean())})
                lossseries.append(delta)
                if base not in ['V6_BRIER','V6_CRPS','V6_MONTH_STATE'] or score not in ['brier','crps']:continue
                for fold in sorted(z.fold.unique()):
                    clean=delta[z.fold!=fold]
                    stress.append({'horizon':h,'model':name,'baseline':base,'metric':score,'test':'omit_fold','parameter':fold,'n':len(clean),'gain':float(clean.mean())})
                for k in [1,3,5,10]:
                    clean=delta.sort_values().iloc[:-k]
                    stress.append({'horizon':h,'model':name,'baseline':base,'metric':score,'test':'omit_largest_gains','parameter':k,'n':len(clean),'gain':float(clean.mean())})
                for phase in range(5):
                    chosen=nonoverlap(z.reset_index().iloc[phase:]).origin
                    stress.append({'horizon':h,'model':name,'baseline':base,'metric':score,'test':'disjoint_phase','parameter':phase,'n':len(chosen),'gain':float(delta.loc[chosen].mean())})
        for field in ['regime','trend','global_risk']:
            for state,z in g.reset_index().groupby(field):
                refcase=ref[h,'V6_BRIER'].set_index('origin').reindex(z.origin)
                regimes.append({'horizon':h,'model':name,'regime_type':field,'state':state,'n':len(z),'disjoint':len(nonoverlap(z)),
                                'brier':float(z.brier.mean()),'crps':float(z.crps.mean()),'coverage80':float(z.coverage80.mean()),
                                'nominal_width80':float(z.width80.mean()),'brier_gain_vs_V6':float(refcase.brier.mean()-z.brier.mean())})
    weekly_ids=[i for i,r in enumerate(pairs) if r['horizon']==5];weekly_calendar=sorted(ref[5,'V6_BRIER'].origin)
    tuple_set=[lossseries[i] for i in weekly_ids];criticals={}
    for block in [5,10,15]:
        a,b,c,d,critical=intervals(tuple_set,weekly_calendar,5,block);criticals[block]=critical
        for j,i in enumerate(weekly_ids):
            pairs[i][f'adjusted95_block{block}']=[float(a[j]),float(b[j])]
            if block==10:pairs[i]['unadjusted95_block10']=[float(c[j]),float(d[j])]
    for r in pairs:
        r['inference']='approximate shared-block simultaneous intervals' if r['horizon']==5 else 'withheld, only four disjoint monthly windows'
    save('benchmark-contrasts.json',pairs);pd.DataFrame(pairs).to_csv(OUT/'benchmark-contrasts.csv',index=False)
    save('uncertainty.json',{'weekly_family_contrasts':len(weekly_ids),'reps':2000,'critical_values':criticals,
          'method':'Common circular blocks on original origin calendar, max absolute standardized bootstrap deviation. Candidate and diagnostic contrasts included. Monthly intervals withheld.'})
    pd.DataFrame(increments).to_csv(OUT/'parent-increments.csv',index=False)
    pd.DataFrame(stress).to_csv(OUT/'stability-stress.csv',index=False)
    pd.DataFrame(regimes).to_csv(OUT/'regime-calibration.csv',index=False)
    pd.DataFrame(month_lag).to_csv(OUT/'intermediate-normalized.csv',index=False)
    save('metrics.json',outs)
    flat=pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,(dict,list))} for r in outs])
    flat.sort_values(['horizon','brier']).to_csv(OUT/'direction-leaderboard.csv',index=False)
    flat.sort_values(['horizon','crps']).to_csv(OUT/'distribution-leaderboard.csv',index=False)
    auxiliary()
    print('Scored',len(allp),'rows;',len(seen),'system/horizon cells;',len(pairs),'matched comparisons',flush=True)


if __name__=='__main__':
    run()
