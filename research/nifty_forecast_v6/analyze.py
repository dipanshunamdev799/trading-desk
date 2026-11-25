"""Strong matched controls, search-wide uncertainty, Pareto tables and fixed confidence."""
from .common import *
from research.nifty_forecast_v3.experiment import nonoverlap,effective_n
from research.nifty_forecast_v5.analyze import summary

def predictions():
    names=['forensic-predictions.csv','model-predictions.csv','monthly-risk-predictions.csv','monthly-followup-predictions.csv','weekly-followup-predictions.csv']
    return pd.concat([pd.read_csv(OUT/n) for n in names],ignore_index=True)
def benchmark_frames():
    p5=pd.read_csv(V5/'all-predictions.csv');p5=p5[p5.split=='outer_exposed'];p4=pd.read_csv(V4/'distribution-predictions.csv');p4=p4[p4.split=='outer_exposed'];p3=pd.read_csv(V3/'predictions.csv');p3=p3[p3.split=='outer_exposed'];out={}
    for h in [5,21]:
        for name in ['I03_nosize','I00','L01','I01_legacy','I02_newindices','L02','E00']:
            out[(h,name)]=p5[(p5.horizon==h)&(p5.model==name)].set_index('origin')
        for name in ['D02_student_shrunk','D03_residual_shrunk']:
            out[(h,'V4_'+name)]=p4[(p4.horizon==h)&(p4.model==name)].set_index('origin')
        for name in ['M05_lgbm','Z_neutral']:
            out[(h,'V4_'+name)]=p3[(p3.horizon==h)&(p3.model==name)].set_index('origin')
    return out
def simultaneous(contrasts,origins,h):
    if len(origins)<8*h:return [None]*len(contrasts)
    rng=np.random.default_rng(SEED);n=len(origins);block=2*h;starts=rng.integers(0,n-block+1,(2000,int(np.ceil(n/block))));ids=(starts[:,:,None]+np.arange(block)).reshape(2000,-1)[:,:n]
    matrix=np.column_stack([v.reindex(origins).to_numpy(float) for v in contrasts]);center=np.nanmean(matrix,axis=0)
    boot=np.column_stack([np.nanmean(matrix[:,j][ids],axis=1) for j in range(matrix.shape[1])]);sd=np.nanstd(boot,axis=0);sd[sd<1e-12]=1e-12
    critical=np.nanquantile(np.nanmax(abs((boot-center)/sd),axis=1),.95)
    return [[float(m-critical*s),float(m+critical*s)] for m,s in zip(center,sd)]
def run():
    save('analysis-plan.json',{'registered_at':now(),'primary_scores':['brier','crps','mae'],'strong_controls':['I03_nosize','I00','L01','V4_D02_student_shrunk','V4_D03_residual_shrunk','V4_M05_lgbm','V4_Z_neutral','E00'],
        'uncertainty':'Shared chronological2H block bootstrap,2000 reps; standardized max across all models/scores/controls per horizon; monthly require8H origins; variable missing cohorts reindex common calendar and retain structural missingness',
        'ranking':'Separate Brier andCRPS sorted/Pareto systems; NO custom composite ranking score',
        'confidence_thresholds':[.55,.65,.75],'confidence_other_rules':'Source-model agreement; interval80width<.8*training historical width; fixed before score inspection; matched baselines and coverage mandatory',
        'status':'Exposed research only; monthly null comparison is mandatory before claiming mechanism'})
    f=predictions();f.to_csv(OUT/'all-predictions.csv',index=False);bench=benchmark_frames();metrics=[];comparisons=[];stability=[];regimes=[];confidence=[];rolling=[];allpairs=[]
    controls=['I03_nosize','I00','L01','V4_D02_student_shrunk','V4_D03_residual_shrunk','V4_M05_lgbm','V4_Z_neutral','E00']
    for h in [5,21]:
        g=f[f.horizon==h];origins=bench[(h,'I03_nosize')].index.sort_values();descriptors=[];deltas=[]
        for name,sub in g.groupby('model'):
            sub=sub.sort_values('origin');r=summary(sub);r.update({'horizon':h,'model':name,'disjoint':summary(nonoverlap(sub)),'effective_n_return_acf':effective_n(sub.realized_return,h)})
            if 'magnitude_mae' in sub and sub.magnitude_mae.notna().any():r['magnitude_mae']=float(sub.magnitude_mae.mean())
            metrics.append(r);indexed=sub.set_index('origin')
            for base in controls:
                b=bench[(h,base)].reindex(sub.origin)
                for metric in ['brier','crps','mae']:
                    delta=b[metric]-indexed[metric];descriptors.append({'horizon':h,'model':name,'baseline':base,'metric':metric,'n':len(delta),'mean_improvement':float(delta.mean())});deltas.append(delta)
            # Month exclusions and independent-return windows against the two actual V5 leads.
            for metric,base in [('brier','I03_nosize'),('crps','L01')]:
                b=bench[(h,base)].reindex(sub.origin);delta=b[metric].to_numpy()-sub[metric].to_numpy()
                for month in sorted(sub.fold.unique()):
                    mask=sub.fold!=month;stability.append({'horizon':h,'model':name,'metric':metric,'baseline':base,'test':'leave_month_out','excluded':month,'n':int(mask.sum()),'gain':float(delta[mask].mean())})
                for offset in range(5):
                    s=nonoverlap(sub.iloc[offset:]);dd=bench[(h,base)][metric].reindex(s.origin).to_numpy()-s[metric].to_numpy();stability.append({'horizon':h,'model':name,'metric':metric,'baseline':base,'test':'disjoint_phase','phase':offset,'n':len(s),'gain':float(dd.mean())})
                for k in [1,3,5,10]:stability.append({'horizon':h,'model':name,'metric':metric,'baseline':base,'test':'remove_best_overlapping_origins','removed':k,'gain':float(np.sort(delta)[:-k].mean())})
            for variable in ['regime','trend','global_risk']:
                for value,ss in sub.groupby(variable):
                    b=bench[(h,'I03_nosize')].reindex(ss.origin);regimes.append({'horizon':h,'model':name,'variable':variable,'value':str(value),'coverage':len(ss)/len(sub),'metrics':summary(ss),'disjoint_n':len(nonoverlap(ss)),'gain_brier_vs_I03':float((b.brier.to_numpy()-ss.brier.to_numpy()).mean())})
            p0=bench[(h,'I03_nosize')].p.reindex(sub.origin).to_numpy();p1=bench[(h,'L01')].p.reindex(sub.origin).to_numpy();rules={}
            for threshold in [.55,.65,.75]:
                rules[f'bull_ge_{threshold}']=sub.p.to_numpy()>=threshold;rules[f'bear_le_{1-threshold:.2f}']=sub.p.to_numpy()<=1-threshold
                rules[f'either_conf_{threshold}']=(sub.p.to_numpy()>=threshold)|(sub.p.to_numpy()<=1-threshold)
            rules['agree_I03_L01']=(p0>=.5)==(p1>=.5);historical_width=bench[(h,'E00')].width80.reindex(sub.origin).to_numpy();rules['narrow80_vs_historical']=sub.width80.to_numpy()<.8*historical_width
            for rule,mask in rules.items():
                selected=sub[mask]
                if len(selected):
                    b=bench[(h,'I03_nosize')].reindex(selected.origin);c=bench[(h,'L01')].reindex(selected.origin);confidence.append({'horizon':h,'model':name,'rule':rule,'n':len(selected),'coverage':len(selected)/len(sub),'disjoint_n':len(nonoverlap(selected)),'metrics':summary(selected),
                        'I03_matched_brier':float(b.brier.mean()),'I03_matched_accuracy':float(((b.p>=.5)==b.outcome).mean()),'L01_matched_crps':float(c.crps.mean()),'uncertainty':'Conditional subgroups descriptive; no narrow independently justified interval'})
            for window in [20]:
                for j in range(window-1,len(sub)):
                    z=sub.iloc[j-window+1:j+1];rolling.append({'horizon':h,'model':name,'last_origin':z.origin.iloc[-1],'window_overlapping_origins':window,'brier':float(z.brier.mean()),'crps':float(z.crps.mean())})
        intervals=simultaneous(deltas,origins,h)
        for d,ci in zip(descriptors,intervals):comparisons.append({**d,'simultaneous95':ci,'family_contrasts':len(descriptors),'status':'EXPOSED / not independent confirmation'})
    save('metrics.json',metrics);save('strong-benchmark-comparisons.json',comparisons);save('stability.json',stability);save('regime-slices.json',regimes);save('confidence-slices.json',confidence);pd.DataFrame(rolling).to_csv(OUT/'rolling-performance.csv',index=False)
    # Explicit immediate-parent effects separate from whole-system ranks.
    parent={'H_MULTISCALE':'I03_nosize','H_DYNAMIC':'I03_nosize','H_DYNAMIC_CORE':'C_SMALL','H_WARNINGS':'I03_nosize','H_CORRELATION':'I03_nosize','H_ROTATION':'I03_nosize',
        'Q_ETF_NOSIZE':'I03_nosize','Q_ETF_VOLUME':'I03_nosize','Q_ETF_PRICE':'I03_nosize','G_DIRECT':'G_MATCHED','G_MEDIATED':'G_MATCHED','M_WEEKSTATE':'M2_WINDOW_SMALL','M2_LEVELS':'M2_WINDOW_SMALL','M2_SLOPES':'M2_WINDOW_SMALL','M2_STATE_LAG1':'M_WEEKSTATE',
        'W2_NODEF_VOLUME':'F_NO_DEFENSIVE','W2_NOAUTO_VOLUME':'F_DROP_TOP3','W2_DEF_PC':'I03_nosize','W2_DEF_NORM':'I03_nosize'}
    for h in [5,21]:
        for name,base in parent.items():
            a=f[(f.horizon==h)&(f.model==name)].set_index('origin')
            if a.empty:continue
            b=f[(f.horizon==h)&(f.model==base)].set_index('origin') if (f[(f.horizon==h)].model==base).any() else bench[(h,base)];b=b.reindex(a.index)
            for metric in ['brier','crps','mae']:allpairs.append({'horizon':h,'model':name,'parent':base,'metric':metric,'n':len(a),'gain':float((b[metric]-a[metric]).mean()),'status':'Exploratory matched parent comparison; inspect search-wide strong-control intervals separately'})
    save('incremental-hypotheses.json',allpairs)
    ledgers=[]
    for name in ['forensic-ledger.json','model-ledger.json','monthly-ledger.json','monthly-followup-ledger.json','weekly-followup-ledger.json']:ledgers.extend(read(name))
    save('experiment-registry.json',ledgers);pd.DataFrame(ledgers).to_csv(OUT/'experiment-registry.csv',index=False)
    # Proper-score leaderboards/Pareto table instead of an arbitrary weighted score.
    rows=[]
    for r in metrics:
        h=r['horizon'];c=[s for s in comparisons if s['horizon']==h and s['model']==r['model'] and ((s['metric']=='brier' and s['baseline']=='I03_nosize') or (s['metric']=='crps' and s['baseline']=='L01'))]
        matched_b=bench[(h,'I03_nosize')].reindex(f[(f.horizon==h)&(f.model==r['model'])].origin);bb=float(matched_b.brier.mean());cc=float(bench[(h,'L01')].reindex(matched_b.index).crps.mean())
        status='EXPLORATORY LEAD' if r['brier']<bb or r['crps']<cc else 'INCONCLUSIVE'
        if h==21 and r['model'].startswith(('M_WEEKSTATE','M2_')):status='INCONCLUSIVE / monthly block-null mechanism not passed'
        row={'horizon':h,'model':r['model'],'n':r['n'],'disjoint':r['disjoint']['n'],'ESS':r['effective_n_return_acf'],'brier':r['brier'],'log_loss':r['log_loss'],'accuracy':r['accuracy'],'balanced_accuracy':r['balanced_accuracy'],'crps':r['crps'],'mae':r['mae'],'rmse':r['rmse'],'coverage50':r['coverage50'],'coverage80':r['coverage80'],'width80':r['width80'],'status':status,'independently_validated':False}
        rows.append(row)
    frame=pd.DataFrame(rows);frame.sort_values(['horizon','brier']).to_csv(OUT/'direction-leaderboard.csv',index=False);frame.sort_values(['horizon','crps']).to_csv(OUT/'distribution-leaderboard.csv',index=False)
    save('leaderboards.json',rows)
    # Horizon diagnostics normalize against each horizon's own historical distribution.
    hd=pd.read_csv(OUT/'intermediate-horizon-predictions.csv');hr=[]
    for (h,name),sub in hd.groupby(['horizon','model']):hr.append({'horizon':int(h),'model':name,**summary(sub),'disjoint_n':len(nonoverlap(sub)),'relative_crps_gain':float((sub.baseline_crps.mean()-sub.crps.mean())/sub.baseline_crps.mean()),'normalized_brier_gain':float(sub.baseline_brier.mean()-sub.brier.mean()),'intervals':'NOT ESTIMATED: too few dependent common-date outcomes'})
    save('intermediate-horizon-metrics.json',hr)
    for file in ['block-null-predictions.csv','monthly-expanded-nulls.csv']:
        df=pd.read_csv(OUT/file);keys=['horizon','block_shift_multiple'] if 'block_shift_multiple' in df else ['model','shift'];save(file.replace('.csv','-metrics.json'),[{**dict(zip(keys,key if isinstance(key,tuple) else (key,))),**summary(sub)} for key,sub in df.groupby(keys)])
    print('Analyzed',len(metrics),'system/horizon rows;',len(comparisons),'strong benchmark contrasts',flush=True)
if __name__=='__main__':run()
