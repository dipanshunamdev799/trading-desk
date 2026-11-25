"""Fair comparisons, complete search multiplicity, conditions and stability."""
from .common import *
from .models import SPECS
from .expansion import VARIANTS
from research.nifty_forecast_v3.experiment import nonoverlap,effective_n,paired_ci
from research.nifty_forecast_v4.distributions import summarize as distribution_summary
RESEARCH_ONLY={'T01','BR00','L03'}
def summary(g):
    r=distribution_summary(g);pred=g.p>=.5;y=g.outcome
    r['balanced_accuracy']=float(np.mean([np.mean(pred[y==v]==v) for v in [0,1] if (y==v).any()]));r['mean_return']=float(g.realized_return.mean())
    bins=[]
    for lo,hi in [(0,.35),(.35,.45),(.45,.55),(.55,.65),(.65,1.00001)]:
        f=g[(g.p>=lo)&(g.p<hi)]
        if len(f):bins.append({'lo':lo,'hi':min(hi,1),'n':len(f),'predicted':float(f.p.mean()),'observed':float(f.outcome.mean())})
    r['calibration_bins']=bins;r['ece']=float(sum(z['n']*abs(z['predicted']-z['observed']) for z in bins)/len(g));return r
def simultaneous(matrix,h):
    n,k=matrix.shape
    if n<8*h:return [None]*k
    rng=np.random.default_rng(SEED);block=2*h;starts=rng.integers(0,n-block+1,(2000,int(np.ceil(n/block))))
    ids=(starts[:,:,None]+np.arange(block)).reshape(2000,-1)[:,:n];center=matrix.mean(axis=0);boot=matrix[ids].mean(axis=1);sd=boot.std(axis=0);sd[sd<1e-12]=1e-12
    critical=np.quantile(np.max(abs((boot-center)/sd),axis=1),.95);return [[float(m-critical*s),float(m+critical*s)] for m,s in zip(center,sd)]
def load_predictions():
    return pd.concat([pd.read_csv(p) for p in sorted(OUT.glob('predictions-stage*.csv'))],ignore_index=True)
def run():
    f=load_predictions();f.to_csv(OUT/'all-predictions.csv',index=False);outer=f[f.split=='outer_exposed'];metrics=[];stability=[];conditions=[];contrasts=[]
    old=pd.read_csv(V3/'predictions.csv');old=old[old.split=='outer_exposed'];v4=pd.read_csv(V4/'distribution-predictions.csv');v4=v4[v4.split=='outer_exposed']
    legacy=[]
    for h in [5,21]:
        for name in ['M05_lgbm','A00_sector','Z_neutral','Z_reversion','B00_empirical']:
            g=old[(old.horizon==h)&(old.model==name)].copy();g['bucket_y']=np.digitize(g.realized_return,[-.05,-.02,-.005,.005,.02,.05]);r=summary(g);legacy.append({'horizon':h,'model':'V4_FROZEN_'+name,**r,'origin_status':'REPRODUCED_OLD_VINTAGE'})
        for name in ['D00_empirical','D02_student_shrunk','D03_residual_shrunk']:
            g=v4[(v4.horizon==h)&(v4.model==name)];legacy.append({'horizon':h,'model':'V4_'+name,**summary(g),'origin_status':'REPRODUCED_EXPOSED'})
        g=outer[outer.horizon==h];pivot={metric:g.pivot(index='origin',columns='model',values=metric).sort_index() for metric in ['brier','crps','mae','pinball','bucket_brier']}
        descriptors=[];delta_vectors=[]
        for metric,p in pivot.items():
            prior=v4[v4.horizon==h].pivot(index='origin',columns='model',values=metric).reindex(p.index)
            strongest=min(prior,key=lambda n:prior[n].mean())
            for n in p:
                for baseline,basevalues in [('E00',p.E00),('V4_'+strongest,prior[strongest])]:
                    delta=basevalues-p[n];descriptors.append({'horizon':h,'model':n,'metric':metric,'baseline':baseline,'prior_baseline_outer_selected':baseline!='E00'});delta_vectors.append(delta.to_numpy())
        direction=pivot['brier']
        for n in direction:
            for control in ['Z_neutral','Z_reversion']:
                basevalues=old[(old.horizon==h)&(old.model==control)].set_index('origin').brier.reindex(direction.index)
                descriptors.append({'horizon':h,'model':n,'metric':'brier','baseline':'V4_FROZEN_'+control});delta_vectors.append((basevalues-direction[n]).to_numpy())
        for a,b,hyp in [('C00','I00','Global increment beyond native internals'),('I00','P00','Native internals beyond index price'),('D01','C00','Derivatives beyond joint state'),('S00','C00','Structured evolution beyond state'),('L01','I00','ETF activity beyond internals'),('L02','C00','ETF activity beyond joint'),('BR00','C00','Current-basket participation proxy'),('L03','L02','Current-basket volume participation'),('I00','I01_legacy','New indices beyond legacy sectors'),('I00','I03_nosize','Mid/small-size index contribution')]:
            for metric,p in pivot.items():
                descriptors.append({'horizon':h,'model':a,'metric':metric,'baseline':b,'incremental_hypothesis':hyp});delta_vectors.append((p[b]-p[a]).to_numpy())
        matrix=np.column_stack(delta_vectors);ci=simultaneous(matrix,h)
        for d,delta,c in zip(descriptors,delta_vectors,ci):contrasts.append({**d,'n':len(delta),'mean_improvement':float(delta.mean()),'paired95':paired_ci(delta,h),'simultaneous95':c,'family_contrasts':len(descriptors),'status':'RESEARCH_EXPOSED'})
        for name,gg in g.groupby('model'):
            gg=gg.sort_values('origin');disjoint=nonoverlap(gg);base=g[g.model=='E00'].set_index('origin')
            metrics.append({'horizon':int(h),'model':name,**summary(gg),'disjoint':summary(disjoint),'effective_n_return_acf':effective_n(gg.realized_return,h),'research_only':name in RESEARCH_ONLY})
            for metric in ['brier','crps']:
                delta=base[metric].reindex(gg.origin).to_numpy()-gg[metric].to_numpy()
                for month in sorted(gg.fold.unique()):
                    m=gg.fold!=month;stability.append({'horizon':int(h),'model':name,'metric':metric,'test':'leave_month_out','excluded':month,'n':int(m.sum()),'mean_improvement_E00':float(delta[m].mean())})
                for phase in range(min(h,5)):
                    subset=nonoverlap(gg.iloc[phase:]);dd=base[metric].reindex(subset.origin).to_numpy()-subset[metric].to_numpy();stability.append({'horizon':int(h),'model':name,'metric':metric,'test':'nonoverlap_phase','phase':phase,'n':len(dd),'mean_improvement_E00':float(dd.mean())})
                for k in [1,3,5,10]:stability.append({'horizon':int(h),'model':name,'metric':metric,'test':'remove_best_origins','removed':k,'mean_improvement_E00':float(np.sort(delta)[:-k].mean()),'overlap_note':'Origins are not independent weeks/months'})
            # Prespecified broad slices; never progressively narrow to find a winner.
            for var in ['fold','regime','trend','global_risk','participation','expiry']:
                for value,sub in gg.groupby(var):
                    b=g[g.model=='R00'].set_index('origin').reindex(sub.origin);d=(b.brier.to_numpy()-sub.brier.to_numpy())
                    conditions.append({'horizon':int(h),'model':name,'variable':var,'value':str(value),'coverage':len(sub)/len(gg),'n':len(sub),'disjoint_n':len(nonoverlap(sub)),
                        'metrics':summary(sub),'regime_baseline':'R00','brier_improvement_vs_regime_baseline':float(d.mean()),'paired95':paired_ci(d,h),'selection':'DESCRIPTIVE_ONLY, inspected across all models/slices; no conditional validation'})
            confident=gg[abs(gg.p-.5)>=.15];b=g[g.model=='R00'].set_index('origin').reindex(confident.origin)
            if len(confident):conditions.append({'horizon':int(h),'model':name,'variable':'fixed_confidence','value':'abs(p-.5)>=.15','coverage':len(confident)/len(gg),'n':len(confident),'disjoint_n':len(nonoverlap(confident)),'metrics':summary(confident),'regime_baseline':'R00','brier_improvement_vs_regime_baseline':float((b.brier.to_numpy()-confident.brier.to_numpy()).mean()),'selection':'Fixed threshold, not tuned to test outcomes'})
    save('metrics.json',metrics);save('legacy-matched-controls.json',legacy);save('uncertainty.json',contrasts);save('stability.json',stability);save('conditional-signals.json',conditions)
    fits=[]
    for p in sorted(OUT.glob('fits-stage*.json')):fits.extend(read(p.name))
    pd.DataFrame(fits).to_csv(OUT/'experiment-registry.csv',index=False);save('experiment-registry.json',fits)
    # Searchable hypothesis ranking: multiple metrics and stability, not peak accuracy.
    rankings=[]
    for r in metrics:
        h=r['horizon'];n=r['model'];base=next(v for v in metrics if v['horizon']==h and v['model']=='E00')
        leave=[s for s in stability if s['horizon']==h and s['model']==n and s['test']=='leave_month_out' and s['metric']=='crps'];fraction=float(np.mean([s['mean_improvement_E00']>0 for s in leave]))
        gain_b=(base['brier']-r['brier'])/base['brier'];gain_c=(base['crps']-r['crps'])/base['crps'];gap=abs(r['coverage80']-.8)+abs(r['coverage50']-.5)
        score=.4*gain_c+.3*gain_b+.2*fraction-.1*gap-(.1 if n in RESEARCH_ONLY else 0)
        sig=[u for u in contrasts if u['horizon']==h and u['model']==n and u['metric']=='crps' and u['baseline']=='E00'];lower=sig[0]['simultaneous95'] if sig else None
        status='EXPLORATORY LEAD' if gain_c>0 and gain_b>0 else 'INCONCLUSIVE'
        if n in ['G00','T00','T01','M00','N02'] and gain_c<0 and gain_b<0:status='REJECTED'
        if status=='EXPLORATORY LEAD' and h==5 and lower and lower[0]>0 and fraction==1 and gap<=.2:status='ROBUST RETROSPECTIVE CANDIDATE'
        rankings.append({'horizon':h,'model':n,'status':status,'ranking_score':score,'relative_crps_gain':gain_c,'relative_brier_gain':gain_b,'leave_month_crps_positive_fraction':fraction,
            'coverage_gap_sum':gap,'research_only':n in RESEARCH_ONLY,'simultaneous_crps95':lower,'independently_validated':False,'recommended_next':'Frozen fresh comparison; do not retune on this outer set' if status=='EXPLORATORY LEAD' else 'No additional same-data sweep; investigate documented failure/data limit'})
    ranking=pd.DataFrame(rankings).sort_values(['horizon','ranking_score'],ascending=[True,False]);ranking.to_csv(OUT/'signal-ranking.csv',index=False);save('signal-ranking.json',ranking.to_dict('records'))
    print('Analyzed',len(metrics),'model/horizon rows,',len(contrasts),'contrasts; registered attempts',len(fits),flush=True)
if __name__=='__main__':run()
