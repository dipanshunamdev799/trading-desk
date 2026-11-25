"""Matured prequential loss targets, forecast reliability and coherent mixtures."""
from scipy.spatial.distance import cdist
from sklearn.covariance import LedoitWolf
from sklearn.linear_model import Ridge
from .common import *
from .models import Distribution, Scale
from .run_models import cohort_queries, score_law, inputs

EXPERTS=['P_NATIVE','P_ROT','P_STRUCTURE','P_CLUSTER','P_LIQ','P_REVERT','P_HIST']


def mixture(distributions,weights):
    return Distribution(np.concatenate([d.a for d in distributions]),np.concatenate([d.w*w for d,w in zip(distributions,weights)]))


def summarize_reliability(x, query, hist, previous, r, situations):
    train=x.loc[hist];scale=Scale().fit(train);a=scale.transform(train);z=scale.transform(x.loc[[query]])
    lc=LedoitWolf().fit(a);u=z[0]-lc.location_;mahal=float(np.sqrt(u@lc.precision_@u))
    nearest=np.sort(cdist(z,a,'euclidean')[0])[:min(8,len(a))].mean();cov_change=np.linalg.norm(np.cov(a[-42:].T)-np.cov(a.T),ord='fro')/len(scale.cols)
    ridge_cov=np.linalg.inv(a.T@a+100*np.eye(a.shape[1]));sample_error=float(np.std(previous[-42:])) if len(previous)>=12 else .02
    parameter_uncertainty=float(sample_error*np.sqrt(z[0]@ridge_cov@z[0]+1/len(a)))
    p=np.clip(r[1]['p_up'],1e-10,1-1e-10);entropy=-(p*np.log(p)+(1-p)*np.log(1-p))
    return {'mahalanobis':mahal,'analogue_distance':float(nearest),'covariance_change':float(cov_change),
            'parameter_uncertainty':parameter_uncertainty,'entropy':float(entropy),'expert_p_disagreement':float(np.std([s['p_up'] for s in r])),
            'expert_mean_disagreement':float(np.std([s['mean_return'] for s in r])),
            'endpoint_width80':r[1]['quantiles']['q90']-r[1]['quantiles']['q10'],
            'recent_brier':situations[0],'recent_crps':situations[1],'recent_gain':situations[2]}


def run():
    configs={
       'J9_EQUAL':{'parent':'P_HIST','hypothesis':'Equal coherent blend across seven distinct experts'},
       'J9_STATIC':{'parent':'J9_EQUAL','hypothesis':'Fixed 50/50 blend of equal experts and empirical history'},
       'J9_PERFORMANCE':{'parent':'J9_EQUAL','hypothesis':'Recent resolved loss weighting, shrunk 60% to equal'},
       'J9_DOMESTIC_GATE':{'parent':'J9_EQUAL','hypothesis':'Regularized domestic predictability ranking with shrinkage'},
       'J9_GLOBAL_GATE':{'parent':'J9_DOMESTIC_GATE','hypothesis':'Same gate with conservative global state inputs'},
       'J9_OOD':{'parent':'J9_EQUAL','hypothesis':'In unfamiliar states reduce expert weights toward the empirical history law'},
       'J9_REGIME':{'parent':'J9_EQUAL','hypothesis':'Select pooled past expert weights by current volatility regime'},
       'J9_REL_SHRINK':{'parent':'J9_STATIC','hypothesis':'Shrink toward history when conditional gain forecast is weak'},
    }
    save('reliability-registry.json',{'at':now(),'configuration':configs,'experts':EXPERTS,
         'targets':['loss difference versus history','Brier','CRPS','correct sign','central interval coverage','realized volatility'],
         'strict_maturity':'Expert prediction belongs to past origin. Its loss can enter gate only once outcome endpoint is strictly before fit origin. Recent diagnostics use the same test.',
         'gate':'Last 126 matured prequential rows, min 35. Ridge50, Equal/learned weight .60/.40; Brier/.25 + CRPS/.02.'})
    base=pd.read_csv(OUT/'base-predictions.csv');cash=matrix('price.csv').close;context=matrix('state-context.csv',OUT)
    global_=matrix('global-context.csv',OUT);frames,_=inputs();small=frames['small_resid'];frozen=[]
    with (OUT/'expert-laws.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            if r['model'] in EXPERTS:frozen.append(r)
    laws={(r['horizon'],r['origin'],r['model']):Distribution(r['atoms'],r['weights']) for r in frozen}
    out=[];reliability=[];decisions=[];ledger=[];target_rows=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv');q=cohort_queries(h);score=base[base.horizon==h].set_index(['origin','model']).sort_index()
        m_data={};tests=[]
        for r in q.itertuples():
            d=r.origin;ready=q[q.endpoint<d].origin.tolist();recent=ready[-21:]
            prior=score.xs('P_ROT',level='model').reindex(recent);control=score.xs('P_HIST',level='model').reindex(recent)
            stats_values=[laws[h,d,n].stats() for n in EXPERTS]
            mature=small.index[small.index<d][-126:];mature=mature[-126:]
            mean=lambda s,default:float(s.mean()) if len(s) else default
            recent_res=(prior.predicted_mean-prior.realized_return).dropna().to_numpy()
            diagnostic=summarize_reliability(small,d,mature,recent_res,stats_values,(mean(prior.brier,.25),mean(prior.crps,.02),mean(control.brier-prior.brier,0)))
            if recent:assert q.set_index('origin').loc[recent,'endpoint'].max()<d
            context_row={**context.loc[d].to_dict(),**diagnostic}
            m_data[d]=context_row
            tests.append({'horizon':h,'cohort':r.split,'origin':d,'endpoint':r.endpoint,'recent_mature_n':len(recent),
                          'last_recent_mature_endpoint':q[q.origin.isin(recent)].endpoint.max() if recent else None,**diagnostic})
        dom=pd.DataFrame.from_dict(m_data,orient='index');plus=dom.join(global_.reindex(dom.index));date_rows=q.set_index('origin');
        write(f'reliability-features-{h}.csv',plus,index=True)
        def resp(dates):
            bs=score.loc[(dates,EXPERTS),'brier'].unstack('model').reindex(index=dates,columns=EXPERTS)
            cs=score.loc[(dates,EXPERTS),'crps'].unstack('model').reindex(index=dates,columns=EXPERTS)
            objective=(bs.sub(bs['P_HIST'],axis=0)/.25+cs.sub(cs['P_HIST'],axis=0)/.02)
            return objective
        def soft(values):
            values=np.asarray(values,dtype=float);weight=np.exp(-2*(values-values.min()));w=weight/weight.sum()
            return .60/len(w)+.40*w
        for (cohort,fold),chunk in q.groupby(['split','fold'],sort=False):
            cutoff=chunk.origin.min();train=q[q.endpoint<cutoff].origin.tolist()[-126:]
            fits={};targets=None
            if len(train)>=35:
                targets=resp(train)
                for k,z in [('dom',dom),('global',plus)]:
                    sc=Scale().fit(z.loc[train]);within=sc.transform(z.loc[train]);mod=Ridge(alpha=50).fit(within,targets)
                    risk_targets=y.loc[train,'volatility'].to_numpy()
                    risk=Ridge(alpha=50).fit(within,risk_targets)
                    fits[k]=(sc,mod,risk)
                sc=fits['dom'][0];a=sc.transform(dom.loc[train]);r=score.xs('P_ROT',level='model').loc[train]
                risk_y=np.column_stack([r.brier,r.crps,(r.p.ge(.5)==r.outcome).astype(float),r.coverage80]);self_assess=Ridge(alpha=50).fit(a,risk_y)
                cutoff_gain=float(np.quantile(-fits['dom'][1].predict(a)[:,1],.60))
                distance_cut=np.quantile(dom.loc[train,'mahalanobis'],.75)
            ledger.append({'horizon':h,'cohort':cohort,'fold':fold,'cutoff':cutoff,'fit_n':len(train),'status':'ok',
                           'last_gate_endpoint':date_rows.loc[train,'endpoint'].max() if train else None,'training_origins':train,
                           'used_gate':len(train)>=35})
            for r in chunk.itertuples():
                d=r.origin;actual=y.loc[d];ds=[laws[h,d,n] for n in EXPERTS];equal=np.full(len(ds),1/len(ds));historic=np.zeros(len(ds));historic[-1]=1
                current_mature=q[q.endpoint<d].origin.tolist()[-42:];recent=resp(current_mature) if current_mature else None
                perf=soft(np.average(recent,weights=np.exp(np.linspace(-1,0,len(recent))),axis=0)) if recent is not None and len(recent)>=12 else equal
                weights={'J9_EQUAL':equal,'J9_STATIC':.5*equal+.5*historic,'J9_PERFORMANCE':perf}
                raw_pred=None;risks={};assessment=[None]*4;select=False;mahal_cut=None
                if fits:
                    for k,z in [('dom',dom),('global',plus)]:
                        sc,mod,rm=fits[k];dmat=sc.transform(z.loc[[d]]);prediction=mod.predict(dmat)[0]
                        weights['J9_DOMESTIC_GATE' if k=='dom' else 'J9_GLOBAL_GATE']=soft(prediction)
                        risks[k]=float(max(0.,rm.predict(dmat)[0]))
                        if k=='dom':raw_pred=prediction;assessment=self_assess.predict(dmat)[0].tolist()
                    select=bool(-raw_pred[1]>cutoff_gain);mahal_cut=float(distance_cut)
                    ood=dom.loc[d,'mahalanobis']>distance_cut
                    weights['J9_OOD']=(.4*equal+.6*historic) if ood else equal
                    hi=context.loc[d,'s_vol']>context.loc[train,'s_vol'].median();vol=context.loc[train,'s_vol'];mask=(vol>vol.median())==hi
                    weights['J9_REGIME']=soft(targets.loc[mask.index[mask]].mean()) if mask.sum()>=15 else equal
                    confidence=.65 if raw_pred[1]<0 else .20
                    weights['J9_REL_SHRINK']=confidence*equal+(1-confidence)*historic
                else:
                    for name in ['J9_DOMESTIC_GATE','J9_GLOBAL_GATE','J9_OOD','J9_REGIME']:weights[name]=equal
                    weights['J9_REL_SHRINK']=.5*equal+.5*historic
                for name,w in weights.items():
                    law=mixture(ds,w);out.append(score_law(h,fold,name,r,law,float(cash.loc[d]),cohort))
                    decisions.append({'model':name,'horizon':h,'origin':d,'cohort':cohort,**dict(zip(EXPERTS,w))})
                base_row=score.loc[(d,'P_ROT')];history_row=score.loc[(d,'P_HIST')]
                target_rows.append({'horizon':h,'origin':d,'endpoint':r.endpoint,'cohort':cohort,'fold':fold,'gate_available':bool(fits),
                                    'selected':select,'predicted_brier':assessment[0],'predicted_crps':assessment[1],
                                    'predicted_correctness':assessment[2],'predicted_interval_coverage':assessment[3],
                                    'actual_brier':base_row.brier,'actual_crps':base_row.crps,'actual_correct':int((base_row.p>=.5)==base_row.outcome),
                                    'actual_coverage80':int(base_row.coverage80),'history_brier':history_row.brier,'history_crps':history_row.crps,
                                    'realized_vol':actual.volatility,'predicted_dom_vol':risks.get('dom'),'predicted_global_vol':risks.get('global'),
                                    'predicted_gain':float(-raw_pred[1]) if raw_pred is not None else None,
                                    'ood_threshold':mahal_cut,**m_data[d]})
        reliability.extend(tests)
    write('reliability-predictions.csv',pd.DataFrame(out));write('reliability-diagnostics.csv',pd.DataFrame(reliability));write('reliability-targets.csv',pd.DataFrame(target_rows))
    write('expert-weights.csv',pd.DataFrame(decisions));save('reliability-ledger.json',ledger)
    print('Built',len(out),'coherent adaptive forecast laws and',len(target_rows),'reliability assessments',flush=True)


if __name__=='__main__':run()
