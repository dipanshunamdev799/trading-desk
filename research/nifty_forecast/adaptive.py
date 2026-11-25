"""Learn input coefficients and blend weights from prior prediction errors."""
from __future__ import annotations
import argparse
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from .engine import (BASE,ROOT,Scale,check_manifest,load_panel,make_features,
                     sigmoid,digest,write_json,block_interval)

MIN_TRAIN=252
MIN_SHADOW_TRAIN=63
MIN_META=126
METHODS=['neutral','rolling_frequency','equal_groups','adaptive_groups','calibrated_adaptive']


def imbalance(buy,sell):
    if buy is None or sell is None or not np.isfinite([buy,sell]).all() or buy<0 or sell<0 or buy+sell<=0:
        return np.nan
    return (buy-sell)/(buy+sell)


def institutional_features(folder,inputs,decision_days):
    check_manifest(folder)
    merged={};revisions=0
    files=list(folder.glob('fii-*.json'))+list(folder.glob('dii-*.json'))
    files += [inputs/'fii-history.json',inputs/'dii-history.json']
    for path in sorted(files,key=lambda p:json.loads(p.read_text()).get('acquired_at','')):
        doc=json.loads(path.read_text())
        if not doc.get('ok'):continue
        provider='fii' if path.name.startswith('fii') else 'dii'
        for segment,rows in doc['payload'].items():
            for row in rows:
                stamp=pd.Timestamp(row['time_stamp'],unit='ms',tz='UTC').tz_convert('Asia/Kolkata')
                day=stamp.strftime('%Y-%m-%d')
                key=(provider,segment,day)
                if key in merged and merged[key]!=row:revisions+=1
                merged[key]=row
    series={}
    for (provider,segment,day),row in merged.items():
        if segment=='NSE_EQ|CASH':
            series.setdefault(provider+'_cash_imbalance',{})[day]=imbalance(row.get('buy_amount'),row.get('sell_amount'))
        elif provider=='fii' and segment=='NSE_FO|INDEX_FUTURES':
            series.setdefault('fii_futures_position_imbalance',{})[day]=imbalance(row.get('total_long_contracts'),row.get('total_short_contracts'))
            series.setdefault('fii_futures_trade_imbalance',{})[day]=imbalance(row.get('buy_contracts'),row.get('sell_contracts'))
        elif provider=='fii' and segment=='NSE_FO|INDEX_OPTIONS':
            values=[row.get(k) for k in ['total_call_long_contracts','total_put_short_contracts','total_put_long_contracts','total_call_short_contracts']]
            if all(v is not None and np.isfinite(v) and v>=0 for v in values):
                series.setdefault('fii_option_position_imbalance',{})[day]=imbalance(values[0]+values[1],values[2]+values[3])
    observed=pd.DataFrame(series).sort_index()
    # Reindex to the Indian decision calendar: no backward fill from future data.
    panel=observed.reindex(decision_days).reset_index(drop=True)
    for name in ['fii_cash_imbalance','dii_cash_imbalance']:
        panel[name+'_mean5']=panel[name].rolling(5,min_periods=5).mean()
    panel['fii_futures_position_change']=panel.fii_futures_position_imbalance.diff()
    panel['fii_option_position_change']=panel.fii_option_position_imbalance.diff()
    audit={'first':str(observed.index.min()),'last':str(observed.index.max()),
        'observed_sessions':len(observed),'duplicate_revisions':revisions,
        'columns':list(panel.columns),'finite_counts':panel.notna().sum().to_dict(),
        'unit_basis':'Common-scale-invariant ratios, not INR crore amounts',
        'availability_assumption':'Session EOD institutional report available by next 00:30 IST; publication clock not reconstructed'}
    return panel,audit


def feature_groups(columns):
    groups={k:[] for k in ['trend','short_term_price','candles_gaps','volatility',
        'banks_financials','other_sectors','participation','global_equities','oil_currency',
        'gift_nifty','institutional_cash','fii_positioning']}
    for name in columns:
        if name.startswith(('fii_cash_','dii_cash_')):group='institutional_cash'
        elif name.startswith('fii_'):group='fii_positioning'
        elif name.startswith('lagged_global_gift_nifty_'):group='gift_nifty'
        elif name.startswith(('lagged_global_brent_','lagged_global_usdinr_')):group='oil_currency'
        elif name.startswith('lagged_global_'):group='global_equities'
        elif name.startswith(('bank_nifty_','nifty_financial_','nifty_psu_bank_')):group='banks_financials'
        elif name.startswith(('nifty_500_','sector_')):group='participation'
        elif name.startswith('nifty_'):group='other_sectors'
        elif name in ['realized_vol20','vol_ratio5_20','atr_pct'] or name.startswith('vix_'):group='volatility'
        elif name in ['daily_range','body','close_location','previous_gap']:group='candles_gaps'
        elif name in ['return1_risk_scaled','rsi14']:group='short_term_price'
        elif name.startswith(('return','ema')):group='trend'
        else:raise ValueError(f'Unassigned feature {name}')
        groups[group].append(name)
    flattened=[v for cols in groups.values() for v in cols]
    if len(flattened)!=len(set(flattened)) or set(flattened)!=set(columns):
        raise AssertionError('Groups must partition raw features exactly once')
    return groups


def recency_weights(n,half_life):
    w=np.exp2((np.arange(n)-(n-1))/half_life)
    return w/w.sum()


def weighted_logistic(a,y,penalty=25):
    design=np.column_stack([np.ones(len(a)),a])
    w=recency_weights(len(a),252)*len(a)
    beta=np.zeros(design.shape[1]);reg=np.eye(design.shape[1])*penalty;reg[0,0]=1e-6
    for _ in range(35):
        p=sigmoid(design@beta)
        h=(design.T*(w*p*(1-p)))@design+reg
        step=np.linalg.solve(h,design.T@(w*(p-y))+reg@beta)
        beta-=step
        if np.max(np.abs(step))<1e-7:break
    return beta


def project_simplex(v):
    u=np.sort(v)[::-1];c=np.cumsum(u)-1
    rho=np.flatnonzero(u-c/np.arange(1,len(u)+1)>0)[-1]
    return np.maximum(v-c[rho]/(rho+1),0)


def learn_blend(predictions,y,penalty=.005):
    """Convex weighted-Brier stack; all supplied labels must already be resolved."""
    if not np.isfinite(predictions).all() or not np.isfinite(y).all():
        raise ValueError('Meta learner requires finite, resolved history')
    d=predictions-.5;a=recency_weights(len(y),126)
    prior=np.zeros(d.shape[1]);prior[0]=1
    q=(d.T*a)@d+penalty*np.eye(d.shape[1])
    b=d.T@(a*(y-.5))+penalty*prior
    step=1/(2*np.linalg.eigvalsh(q).max())
    w=prior.copy();z=w.copy();momentum=1.
    for _ in range(400):
        next_w=project_simplex(z-step*2*(q@z-b))
        if np.max(np.abs(next_w-w))<1e-9:
            w=next_w;break
        next_momentum=(1+np.sqrt(1+4*momentum**2))/2
        z=next_w+(momentum-1)/next_momentum*(next_w-w)
        w=next_w;momentum=next_momentum
    return w


def fit_calibrator(p,y):
    logits=np.log(np.clip(p,.05,.95)/(1-np.clip(p,.05,.95)))
    a=np.column_stack([np.ones(len(p)),logits])
    weights=recency_weights(len(p),126)*len(p)
    prior=np.array([0.,1.]);beta=prior.copy();penalty=10.
    lipschitz=np.linalg.eigvalsh((a.T*(weights*.25))@a+penalty*np.eye(2)).max()
    for _ in range(250):
        gradient=a.T@(weights*(sigmoid(a@beta)-y))+penalty*(beta-prior)
        next_beta=beta-gradient/lipschitz
        next_beta[1]=np.clip(next_beta[1],0,3)
        if np.max(np.abs(next_beta-beta))<1e-9:
            beta=next_beta;break
        beta=next_beta
    return beta


def expert_predictions(x,labels,groups,target):
    raw=x.to_numpy(float);returns=labels[target].to_numpy(float)
    y=(returns>0).astype(float);known=np.isfinite(returns)
    pred=np.full((len(x),len(groups)),np.nan);n_train=np.zeros_like(pred,dtype=int)
    fits=[];names=list(groups)
    eligible=np.arange(len(x))>=504
    months=labels.target_day.str[:7]
    blocks=[np.flatnonzero((months==m).to_numpy()&eligible) for m in months[eligible].unique()]
    # The current call gets a fresh fit using all now-resolved labels. Earlier
    # historical predictions remain monthly-frozen as specified.
    blocks=[block[block<len(x)-1] for block in blocks]
    blocks=[b for b in blocks if len(b)]+[np.array([len(x)-1])]
    for block in blocks:
        first=int(block[0]);history=np.flatnonzero(known&(np.arange(len(x))<first))[-1260:]
        if len(history) and labels.target_day.iloc[history[-1]]>labels.decision_day.iloc[first]:
            raise AssertionError('Unresolved label used in expert fitting')
        for g,name in enumerate(names):
            cols=[x.columns.get_loc(k) for k in groups[name]]
            observed=np.isfinite(raw[history][:,cols]).mean(axis=1)>=.5
            train=history[observed];minimum=63 if name in ['institutional_cash','fii_positioning'] else 252
            n_train[block,g]=len(train)
            if len(train)<minimum:continue
            scaler=Scale().fit(raw[train][:,cols])
            beta=weighted_logistic(scaler.transform(raw[train][:,cols]),y[train])
            usable=np.isfinite(raw[block][:,cols]).mean(axis=1)>=.5
            selected=block[usable]
            if len(selected):
                scaled=scaler.transform(raw[selected][:,cols])
                pred[selected,g]=np.clip(sigmoid(np.column_stack([np.ones(len(selected)),scaled])@beta),.05,.95)
            fits.append({'target':target,'group':name,'fit_for_target':labels.target_day.iloc[first],
                'last_training_target':labels.target_day.iloc[train[-1]],'training_n':len(train),
                'first_training_target':labels.target_day.iloc[train[0]],
                'columns':groups[name],'intercept':float(beta[0]),
                'coefficients':beta[1:].tolist(),'mean':scaler.mean.tolist(),
                'std':scaler.std.tolist(),'median':scaler.median.tolist(),
                'current_fit':first==len(x)-1})
    return pred,n_train,fits


def sequential_blend(pred,n_train,labels,target,start=504):
    """Predict at i, then expose y[i] only to later decisions."""
    returns=labels[target].to_numpy(float);known=np.isfinite(returns)
    y=(returns>0).astype(float);ng=pred.shape[1]
    allocation=np.zeros((len(pred),ng+1));allocation[:,0]=1
    rows=[];raw_stack=np.full(len(pred),np.nan)
    for i in range(start,len(pred)):
        history=np.flatnonzero(known&(np.arange(len(pred))<i)&(np.arange(len(pred))>=start))[-504:]
        available=np.isfinite(pred[i])
        evidence=np.sum(np.isfinite(pred[history]),axis=0) if len(history) else np.zeros(ng)
        active=available&(evidence>=126)&(n_train[i]>=252)
        active_indices=np.flatnonzero(active)
        if len(history)>=126 and len(active_indices):
            p_history=pred[history][:,active_indices]
            # Use common chronological support; never assign a new expert past
            # predictions it had not actually made.
            common=np.isfinite(p_history).all(axis=1)
            meta_idx=history[common]
            if len(meta_idx)>=126:
                matrix=np.column_stack([np.full(len(meta_idx),.5),p_history[common]])
                weights=learn_blend(matrix,y[meta_idx])
                allocation[i,0]=weights[0];allocation[i,active_indices+1]=weights[1:]
            else:meta_idx=np.array([],dtype=int)
        else:meta_idx=np.array([],dtype=int)
        query=np.where(available,pred[i],.5)
        raw=float(allocation[i]@np.r_[.5,query]);raw_stack[i]=raw
        calib_idx=np.flatnonzero(known&(np.arange(len(pred))<i)&np.isfinite(raw_stack))[-252:]
        beta=fit_calibrator(raw_stack[calib_idx],y[calib_idx]) if len(calib_idx)>=126 else np.array([0.,1.])
        logit=np.log(np.clip(raw,.05,.95)/(1-np.clip(raw,.05,.95)))
        calibrated=float(np.clip(sigmoid(beta[0]+beta[1]*logit),.05,.95))
        prior=np.flatnonzero(known&(np.arange(len(pred))<i))[-1260:]
        row={'i':i,'decision_day':labels.decision_day.iloc[i],'target_day':labels.target_day.iloc[i],
            'outcome':int(y[i]) if known[i] else np.nan,'return':float(returns[i]) if known[i] else np.nan,
            'neutral':.5,'rolling_frequency':float((y[prior].sum()+1)/(len(prior)+2)),
            'equal_groups':float(query[active].mean()) if active.any() else .5,
            'adaptive_groups':raw,'calibrated_adaptive':calibrated,
            'meta_training_n':len(meta_idx),'meta_last_target':labels.target_day.iloc[meta_idx[-1]] if len(meta_idx) else None,
            'calibration_training_n':len(calib_idx),'calibration_last_target':labels.target_day.iloc[calib_idx[-1]] if len(calib_idx) else None,
            'calibration_intercept':float(beta[0]),'calibration_slope':float(beta[1]),
            'active_experts':int(active.sum())}
        rows.append(row)
    return pd.DataFrame(rows),allocation


def metrics(frame):
    y=frame.outcome.to_numpy(float);p_base=frame.neutral.to_numpy(float)
    results={}
    for name in METHODS:
        p=frame[name].to_numpy(float);loss=(p-y)**2
        results[name]={'n':len(y),'accuracy':float(((p>=.5)==y).mean()),
            'brier':float(loss.mean()),'log_loss':float((-y*np.log(p)-(1-y)*np.log(1-p)).mean()),
            'brier_improvement_vs_neutral':float(np.mean((p_base-y)**2-loss)),
            'paired_improvement_ci95':block_interval((p_base-y)**2-loss),
            'first_half_brier':float(loss[:len(y)//2].mean()),'second_half_brier':float(loss[len(y)//2:].mean()),
            'latest126_brier':float(loss[-126:].mean()),'latest126_accuracy':float(((p[-126:]>=.5)==y[-126:]).mean())}
    calibration={}
    for name in ['equal_groups','adaptive_groups','calibrated_adaptive']:
        p=frame[name].to_numpy();bins=[]
        for lo,hi in zip([0,.4,.45,.5,.55,.6],[.4,.45,.5,.55,.6,1.0001]):
            mask=(p>=lo)&(p<hi)
            if mask.any():bins.append({'lower':lo,'upper':min(hi,1),'n':int(mask.sum()),
                'predicted':float(p[mask].mean()),'observed_up':float(y[mask].mean())})
        calibration[name]=bins
    return {'period':[frame.target_day.iloc[0],frame.target_day.iloc[-1]],'up_frequency':float(y.mean()),
            'methods':results,'calibration':calibration}


def weight_explanations(x,labels,groups,pred,n_train,fits,allocation,target):
    latest_fits={r['group']:r for r in fits if r['current_fit']}
    feature_rows=[];group_rows=[];last=len(x)-1
    y=(labels[target].to_numpy(float)>0).astype(float)
    for j,(name,cols) in enumerate(groups.items()):
        evidence=np.flatnonzero(np.isfinite(pred[:,j])&labels[target].notna().to_numpy())
        recent=evidence[-252:];fit=latest_fits.get(name)
        weight=float(allocation[-1,j+1])
        reason='eligible' if len(evidence)>=126 and n_train[-1,j]>=252 and np.isfinite(pred[-1,j]) else \
               'insufficient_out_of_sample_history' if len(evidence)<126 else \
               'insufficient_training_history' if n_train[-1,j]<252 else 'current_inputs_unavailable'
        group_rows.append({'target':target,'group':name,'weight':weight,
            'expert_up_probability':float(pred[-1,j]) if np.isfinite(pred[-1,j]) else None,
            'latest_training_n':int(n_train[-1,j]),'out_of_sample_n':len(evidence),
            'recent_oos_n':len(recent),'recent_oos_brier':float(np.mean((pred[recent,j]-y[recent])**2)) if len(recent) else None,
            'status':reason,'current_logit':float(np.log(pred[-1,j]/(1-pred[-1,j]))) if np.isfinite(pred[-1,j]) else None})
        if fit:
            raw=x.loc[last,cols].to_numpy(float);median=np.array(fit['median'])
            missing=~np.isfinite(raw)
            z=np.clip((np.where(missing,median,raw)-fit['mean'])/fit['std'],-5,5)
            beta=np.array(fit['coefficients'])
            for k,feature in enumerate(cols):
                feature_rows.append({'target':target,'group':name,'feature':feature,
                    'group_weight':weight,'raw_value':float(raw[k]) if np.isfinite(raw[k]) else None,
                    'standardized_value':float(z[k]),'signed_logistic_coefficient':float(beta[k]),
                    'current_group_log_odds_contribution':float(beta[k]*z[k]),
                    'missingness_coefficient':float(beta[len(cols)+k]),
                    'currently_missing':bool(missing[k]),'training_n':fit['training_n']})
    group_rows.insert(0,{'target':target,'group':'neutral','weight':float(allocation[-1,0]),
        'expert_up_probability':.5,'latest_training_n':0,'out_of_sample_n':last-504,
        'recent_oos_n':252,'recent_oos_brier':.25,'status':'uncertainty_anchor','current_logit':0.})
    return group_rows,feature_rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=BASE/'adaptive-v1')
    parser.add_argument('--institutional',type=Path,default=BASE/'institutional-v1')
    parser.add_argument('--inputs',type=Path,default=BASE/'inputs-v2')
    parser.add_argument('--supplement',type=Path,default=BASE/'supplement-v1')
    parser.add_argument('--reference-run',type=Path,default=BASE/'run-v3')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    reference=args.reference_run/'forecast.json'
    old=json.loads(reference.read_text());old_hash=digest(reference)
    bars,globals_,audit,provisional,retained,fresh=load_panel(args.inputs,args.supplement,old['target_date'])
    x,labels,_=make_features(bars,globals_,old['target_date'])
    institution,institution_audit=institutional_features(args.institutional,args.inputs,labels.decision_day.tolist())
    x=pd.concat([x,institution],axis=1);groups=feature_groups(x.columns)
    x.to_csv(args.out/'feature-panel.csv',index=False);labels.to_csv(args.out/'labels.csv',index=False)
    write_json(args.out/'data-audit.json',{'institutional':institution_audit,'groups':groups,
        'raw_feature_count':len(x.columns),'provisional_bars':provisional,'original_price_audit':audit})
    results={};forecast={};all_group=[];all_feature=[]
    for target in ['close_return','intraday_return']:
        print('Fitting chronological experts:',target,flush=True)
        pred,n_train,fits=expert_predictions(x,labels,groups,target)
        print('Learning daily weights and calibration:',target,flush=True)
        replay,allocations=sequential_blend(pred,n_train,labels,target)
        names=['neutral']+list(groups)
        weights=pd.DataFrame(allocations,columns=names)
        weights=pd.concat([labels[['decision_day','target_day']],weights],axis=1)
        weights.to_csv(args.out/f'daily-weights-{target}.csv',index=False)
        pd.concat([labels[['decision_day','target_day']],pd.DataFrame(pred,columns=list(groups))],axis=1).to_csv(args.out/f'expert-predictions-{target}.csv',index=False)
        pd.DataFrame(n_train,columns=list(groups)).to_csv(args.out/f'expert-training-counts-{target}.csv',index=False)
        write_json(args.out/f'expert-fits-{target}.json',fits)
        replay.to_csv(args.out/f'prequential-{target}.csv',index=False)
        evaluation=replay[replay.outcome.notna()].tail(504).copy()
        evaluation.to_csv(args.out/f'evaluation-{target}.csv',index=False)
        results[target]={'all504':metrics(evaluation),
                         'published503':metrics(evaluation[evaluation.target_day<'2026-11-16'])}
        group_rows,feature_rows=weight_explanations(x,labels,groups,pred,n_train,fits,allocations,target)
        all_group.extend(group_rows);all_feature.extend(feature_rows)
        today=replay.iloc[-1]
        forecast[target]={**old['forecasts'][target],
            'up_probability':{k:float(today[k]) for k in METHODS},
            'primary_model':'calibrated_adaptive','calibration_intercept':float(today.calibration_intercept),
            'calibration_slope':float(today.calibration_slope),
            'meta_training_n':int(today.meta_training_n),'calibration_training_n':int(today.calibration_training_n),
            'group_weights':{r['group']:r['weight'] for r in group_rows}}
        # Keep compatibility with the existing immutable outcome scorer.
        forecast[target]['up_probability']['ensemble']=float(today.calibrated_adaptive)
        print(target,'current',forecast[target]['up_probability'],flush=True)
    pd.DataFrame(all_group).to_csv(args.out/'group-weights.csv',index=False)
    pd.DataFrame(all_feature).to_csv(args.out/'input-coefficients.csv',index=False)
    write_json(args.out/'validation.json',results)
    inventory=json.loads((args.reference_run/'factor-inventory.json').read_text())
    write_json(args.out/'catalog-eligibility.json',{'catalog_count':len(inventory),
        'note':'Direct model features are listed separately; unrepresented concepts have no fitted weight',
        'excluded_examples':{'options_pcr_iv_max_pain':'No sufficiently long timestamped historical panel',
            'macro_policy_news':'No usable archived numeric release/vintage panel',
            'institutional_short_history':'Experts scored in shadow until training and OOS minima are met'},
        'inventory':inventory})
    final={**old,'experiment':'NIFTY historical-error-weighted inputs v2',
        'issued_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'primary_model':'calibrated_adaptive',
        'original_forecast_sha256':old_hash,'original_forecast_path':str(reference),
        'input_manifests':{**old['input_manifests'],str(args.institutional/'manifest.json'):digest(args.institutional/'manifest.json')},
        'source_code_hashes':{p.name:digest(p) for p in [Path(__file__),Path(__file__).with_name('ADAPTIVE_PROTOCOL.md'),Path(__file__).with_name('engine.py')]},
        'features':list(x.columns),'forecasts':forecast,
        'limits':old['limits']+['Historical evaluation period previously inspected; exploratory, not a fresh confirmatory test',
            'Institutional availability inferred from session EOD, not a reconstructed publication timestamp',
            'Group allocation is a fitted probability-blend weight, not a causal feature importance']}
    write_json(args.out/'forecast.json',final)
    write_json(args.out/'artifact-manifest.json',{'created_at':final['issued_at'],
        'files':{p.name:digest(p) for p in sorted(args.out.glob('*')) if p.is_file()}})
    if digest(reference)!=old_hash:raise AssertionError('Original forecast changed')
    print(json.dumps({'out':str(args.out),'raw_features':len(x.columns),'groups':len(groups),
        'institutional_audit':institution_audit,
        'validation':{k:v['all504']['methods'] for k,v in results.items()}},indent=2),flush=True)


if __name__=='__main__':main()
