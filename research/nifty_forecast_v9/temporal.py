"""Quantify design, sample-size and date effects without causal attribution."""
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
from .common import *
from research.nifty_forecast_v3.experiment import nonoverlap


def run():
    p=pd.read_csv(OUT/'learning-predictions.csv');mine=pd.read_csv(OUT/'base-predictions.csv');r=read('learning-ledger.json')
    rows=[];match_rows=[]
    for cohort,q in p.groupby('cohort'):
        histories=q[q.model=='L_HIST_MAX'].set_index('origin')
        for model,g in q.groupby('model'):
            g=g.set_index('origin').sort_index();d=histories.loc[g.index]
            a=[v for v in r if v['status']=='ok' and v['model']==model and v['cohort']==cohort]
            rows.append({'cohort':cohort,'model':model,'n':len(g),'first':g.index[0],'last':g.index[-1],
                         'training_min':min(z['train_n'] for z in a),'training_max':max(z['train_n'] for z in a),
                         'inner_min':min(z['inner_n'] for z in a),'inner_max':max(z['inner_n'] for z in a),
                         'brier':g.brier.mean(),'crps':g.crps.mean(),'matched_history_brier':d.brier.mean(),
                         'matched_history_crps':d.crps.mean(),'brier_gain':(d.brier-g.brier).mean(),'crps_gain':(d.crps-g.crps).mean()})
        for root in ['ROT','RES','SMALL','HIST']:
            models=[f'L_{root}_{n}' for n in [85,126,189,252,300,'MAX']]
            availability={s:set(q[q.model==s].origin) for s in models}
            for allowed in [85,126,189,252,300]:
                list_=models[:[85,126,189,252,300].index(allowed)+1]+[models[-1]]
                dates=set.intersection(*(availability[s] for s in list_))
                if not dates:continue
                filtered=q[q.model.isin(list_)&q.origin.isin(dates)]
                for name,g in filtered.groupby('model'):
                    match_rows.append({'cohort':cohort,'family':root,'largest_eligible_length':allowed,
                      'model':name,'n':len(g),'disjoint':len(nonoverlap(g)),'brier':g.brier.mean(),'crps':g.crps.mean()})
    write('learning-curves.csv',pd.DataFrame(rows));write('learning-common-dates.csv',pd.DataFrame(match_rows))
    table=pd.DataFrame(rows).set_index(['cohort','model']);components=[]
    for metric in ['brier','crps']:
        e85=table.loc['early','L_ROT_85'][metric];l85=table.loc['later','L_ROT_85'][metric]
        emax=table.loc['early','L_ROT_MAX'][metric];lmax=table.loc['later','L_ROT_MAX'][metric]
        components.append({'loss':metric,'observed_earlier_minus_later':emax-lmax,
          'early_expanding_minus_85':emax-e85,'equal_85_date_regime_component':e85-l85,'later_85_minus_expanding':l85-lmax,
          'historical_baseline_gap':table.loc['early','L_HIST_MAX'][metric]-table.loc['later','L_HIST_MAX'][metric]})
    write('gap-decomposition.csv',pd.DataFrame(components))
    # Retrospective matching on concurrent observed conditions using only early normalization.
    condition=matrix('state-context.csv',OUT)
    cols=['s_trend','s_vol','s_breadth','s_bank','s_defensive','s_sector_dispersion','s_liquidity','s_cross_corr','s_acf','s_global_vol']
    cut=p[p.model=='L_ROT_85'];e=cut[cut.cohort=='early'].sort_values('origin');l=cut[cut.cohort=='later'].sort_values('origin')
    a=condition.loc[e.origin,cols];b=condition.loc[l.origin,cols];med=a.median();sd=a.std().clip(lower=1e-8)
    z=(a.fillna(med)-med)/sd;w=(b.fillna(med)-med)/sd
    distances=cdist(w,z)/np.sqrt(len(cols));i,j=linear_sum_assignment(distances)
    hist=p[p.model=='L_HIST_MAX'].set_index('origin');pairs=[]
    for later,earlier in zip(i,j):
        v,u=l.iloc[later],e.iloc[earlier];d=distances[later,earlier]
        pairs.append({'early':u.origin,'later':v.origin,'normalized_distance':d,'within_caliper':d<=1,
                     'early_brier':u.brier,'later_brier':v.brier,'early_crps':u.crps,'later_crps':v.crps,
                     'early_relative_brier':u.brier-hist.loc[u.origin,'brier'],'later_relative_brier':v.brier-hist.loc[v.origin,'brier']})
    write('market-state-matches.csv',pd.DataFrame(pairs))
    profile=[]
    for k in cols+['s_sync','s_concentration','s_trend_consistency']:
        for g in [e,l]:
            s=condition.loc[g.origin,k];profile.append({'cohort':g.cohort.iloc[0],'feature':k,'n':int(s.notna().sum()),'mean':s.mean(),'std':s.std()})
    write('cohort-market-profile.csv',pd.DataFrame(profile))
    # Prequential rolling skill and dated retrospective CUSUM. Online measures never take future fit errors.
    model=mine[(mine.model=='P_ROT')&(mine.horizon==5)].sort_values('origin').set_index('origin');baseline=mine[(mine.model=='P_HIST')&(mine.horizon==5)].set_index('origin')
    difference=model.brier-baseline.brier.reindex(model.index);cascade=(difference-difference.mean()).cumsum();breakpoint=cascade.abs().idxmax()
    audit=[]
    for d,m in model.iterrows():
        mature=difference[model.endpoint<d];old=mature.iloc[-63:-21];now_=mature.iloc[-21:]
        alarm=None if len(old)<20 else float((now_.mean()-old.mean())/max(old.std(),.01))
        errors=(model.predicted_mean-model.realized_return).reindex(mature.index).iloc[-42:];ctx0=condition.loc[errors.index,'s_bank']
        audit.append({'origin':d,'endpoint':m.endpoint,'cohort':m.cohort,'loss_delta':difference.loc[d],
                      'retrospective_cusum':cascade.loc[d],'n_mature':len(mature),'online_loss_alarm':alarm,
                      'rolling_matured_bank_error_corr':errors.corr(ctx0) if len(errors)>=10 else None,
                      'last_resolved_endpoint':model.loc[mature.index,'endpoint'].max() if len(mature) else None})
    write('online-and-retrospective-breaks.csv',pd.DataFrame(audit))
    save('temporal-diagnostics.json',{'retrospective_max_abs_CUSUM':breakpoint,'observed_max_cusum':float(cascade.abs().max()),
          'causal_alarm_rule':'Compare last 21 resolved losses with previous up to 42. Alarm only after endpoints preceding origin. Diagnostic, no ex-post break is a gate input.',
          'pairing':'One-to-one retrospective minimum-distance matching between later and earlier states. Normalized using earlier observations. No causal attribution.',
          'gap_algebra':'early expanding minus early fixed + early fixed minus later fixed + later fixed minus later expanding. Date effect conflates regime and unmeasured differences.'})
    print('Completed matched learning curves, date/regime profiles and error-break diagnostics',flush=True)


if __name__=='__main__':run()
