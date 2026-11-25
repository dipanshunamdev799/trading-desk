"""Five registered conditions with training-only exact-condition baselines."""
from .common import *
from .analyze import load_predictions,summary
from research.nifty_forecast_v3.experiment import available,nonoverlap,paired_ci
from research.nifty_forecast_v4.distributions import Distribution
def masks(x,training):
    high=x.p_rv21>x.loc[training,'p_rv21'].median();riskoff=x.x_global_mean<0;narrow=x.i_participation<=.5
    return {'global_weak_narrow':riskoff&narrow,'global_weak_broad':riskoff&~narrow,
        'highvol_nearexpiry':high&(x.d_option_dte<=2),
        'concentrated_rally':(x.i_concentration>x.loc[training,'i_concentration'].median())&(x.p_ret21>x.p_rv21*np.sqrt(21)),
        'oil_fx_up_highvol':(x.g_BZUSD_ret5>0)&(x.g_USDINR_ret5>0)&high}
def run():
    save('conditional-plan.json',{'registered_at':now(),'conditions':['global_weak_narrow','global_weak_broad','highvol_nearexpiry','concentrated_rally','oil_fx_up_highvol'],
        'thresholds':'Training median volatility/concentration; breadth .5; positive oil/FX; near expiry<=2calendar days; trend>RV21*sqrt21',
        'baseline':'Exact same causal condition, historical conditional return atoms plus30 unconditional pseudoobservations',
        'complexity_limit':'No additional progressively narrower conditions','multiplicity':'32models x5conditions x2horizons inspected; intervals descriptive/unadjusted and cannot qualify conditional edge'})
    x=pd.read_csv(OUT/'features.csv',index_col=0);f=load_predictions();outer=f[f.split=='outer_exposed'];records=[];training_counts=[]
    for h in [5,21]:
        labs=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0);queries=outer[(outer.horizon==h)&(outer.model=='E00')]
        for fold,g in queries.groupby('fold'):
            ix=available(labs,g.origin.min());mm=masks(x,ix);ypool=labs.loc[ix[-252:],'return'].to_numpy()
            for condition,mask in mm.items():
                selected=ix[mask.reindex(ix).fillna(False).to_numpy()];ys=labs.loc[selected,'return'].to_numpy();atoms=np.r_[ys,ypool];w=np.r_[np.ones(len(ys)),np.full(len(ypool),30/len(ypool))];law=Distribution(atoms,w)
                training_counts.append({'horizon':h,'fold':fold,'condition':condition,'training_total':len(ix),'training_conditional':len(selected),'training_conditional_disjoint':len(nonoverlap(pd.DataFrame({'origin':selected,'endpoint':labs.loc[selected,'endpoint'].to_numpy()})))})
                for day in g.origin:
                    if bool(mask.loc[day]):records.append({'horizon':h,'fold':fold,'condition':condition,'origin':day,'endpoint':labs.loc[day,'endpoint'],**law.score(labs.loc[day,'return'])})
    base=pd.DataFrame(records);base.to_csv(OUT/'condition-baseline-predictions.csv',index=False);save('conditional-training-counts.json',training_counts);results=[]
    for (h,condition),b in base.groupby(['horizon','condition']):
        for name,g in outer[outer.horizon==h].groupby('model'):
            sub=g.set_index('origin').reindex(b.origin).reset_index();delta=b.brier.to_numpy()-sub.brier.to_numpy()
            results.append({'horizon':int(h),'condition':condition,'model':name,'n':len(sub),'coverage':len(sub)/len(g),'disjoint_n':len(nonoverlap(sub)),
                'metrics':summary(sub),'exact_condition_baseline':summary(b),'brier_improvement':float(delta.mean()),'crps_improvement':float((b.crps.to_numpy()-sub.crps.to_numpy()).mean()),'unadjusted_paired95':paired_ci(delta,int(h)),'status':'EXPLORATORY_ONLY; no conditional qualification from these subgroup scores'})
    save('conditional-hypotheses.json',results);print('Exact-condition comparisons',len(results),flush=True)
if __name__=='__main__':run()
