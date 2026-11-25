"""Freeze late-issued, explicitly unvalidated multi-target as-of scenarios."""
import json,platform,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import joblib
import pandas as pd
import scipy,sklearn,lightgbm
from .audit import OUT,ROOT,OLD,save,sha
from research.nifty_forecast.horizons import future_sessions

def main():
    destination=OUT/'09_FINAL_FORECASTS.json'
    if destination.exists():raise FileExistsError('Final forecast already frozen')
    live=json.loads((OUT/'current-model-record.json').read_text());metrics=json.loads((OUT/'metrics.json').read_text())
    issued=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
    price=pd.read_csv(OUT/'price.csv',index_col=0);reference=float(price.close.iloc[-1]);reference_day=price.index[-1]
    calendar=json.loads((OLD/'horizon-calendar-v1.json').read_text());future=future_sessions(reference_day,calendar,21)
    outputs={};contributions={}
    for h in [5,21]:
        a=live[str(h)];selected=a['selectors'];preds={target:a['forecasts'][name][0] for target,name in selected.items()}
        samples=np.asarray(preds['distribution']['samples']);quant=np.quantile(samples,[.1,.25,.5,.75,.9])
        buckets=np.bincount(np.digitize(samples,[-.05,-.02,-.005,.005,.02,.05]),minlength=7)/len(samples)
        direction=preds['direction']['p'];mean=preds['return']['mean'];vol=preds['volatility']['vol']
        historical={target:next(r for r in metrics if r['horizon']==h and r['model']=='S_'+target and r['split']=='outer_exposed') for target in selected}
        fixed={target:next(r for r in metrics if r['horizon']==h and r['model']==model and r['split']=='outer_exposed') for target,model in selected.items()}
        statuses={name:'NOT VALIDATED' for name in ['probabilities','expected_return','median_return','endpoint_price','intervals','volatility','tail_risk','contributing_signals']}
        outputs['week' if h==5 else 'month']={
            'horizon_trading_sessions':h,'expected_endpoint_date':future[h-1],
            'positive_return_probability':direction,'nonpositive_return_probability':1-direction,
            'probability_status':'RAW MODEL ESTIMATE; NOT HISTORICALLY CALIBRATED OR INDEPENDENTLY VALIDATED',
            'expected_return_regression':mean,'median_return_distribution':float(quant[2]),
            'expected_endpoint_price':reference*(1+mean),'median_endpoint_price':reference*(1+quant[2]),
            'central50_endpoint_interval':[reference*(1+quant[1]),reference*(1+quant[3])],
            'central80_endpoint_interval':[reference*(1+quant[0]),reference*(1+quant[4])],
            'annualized_volatility_point':vol,'sqrt_time_horizon_move_proxy':float(vol*np.sqrt(h/252)),
            'expected_absolute_move_distribution':float(np.mean(abs(samples))),
            'path_breach_below_minus2_probability':preds['tail']['tail02'],
            'path_breach_below_minus5_probability':preds['tail']['tail05'],
            'return_bucket_probabilities':dict(zip(['below_-5pct','-5_to_-2pct','-2_to_-0.5pct','-0.5_to_+0.5pct','+0.5_to_+2pct','+2_to_+5pct','above_+5pct'],map(float,buckets))),
            'scenarios':{'bearish':'Endpoint below -0.5% reference return','neutral':'Endpoint between -0.5% and +0.5%','bullish':'Endpoint above +0.5%'},
            'scenario_probabilities_from_distribution':{'bearish':float(buckets[:3].sum()),'neutral':float(buckets[3]),'bullish':float(buckets[4:].sum())},
            'selected_models':selected,'selectors_use_only_purged_inner_validation':True,
            'specific_selector_policy_oos':historical,'specific_current_selected_model_oos_exploratory':fixed,
            'effective_evaluation':{'origins':historical['direction']['n'],'nonoverlapping':historical['direction']['nonoverlapping_n'],
                'outcome_acf_ess':historical['direction']['outcome_autocorrelation_ess'],'independence_guaranteed':False},
            'cross_target_consistency':{'classifier_p_up':direction,'distribution_p_up':float(np.mean(samples>0)),
                'distribution_mean':float(samples.mean()),'direct_return_mean':mean,
                'note':'Independent target selectors do not define a jointly calibrated distribution; discrepancies are not hidden'},
            'validation_status':statuses,'future_market_regime':'NOT VALIDATED: only causal origin-regime conditioning was tested',
            'main_contributing_signals':'Training associations in model-contributions.json; no family has independently demonstrated incremental predictive importance',
            'outcome':{'endpoint_close':None,'reference_close_revision':None,'return':None,'scored_at':None}}
        assoc=[]
        for target,name in selected.items():
            artifact=joblib.load(a['metadata'][name]['model_path']);model=artifact['model']
            if 'pre' not in model:continue
            estimator=model.get('direction_model') if target=='direction' else model.get('mean_model')
            cols=[model['pre'].columns[j] for j in model['pre'].keep]
            if hasattr(estimator,'feature_importance'):values=estimator.feature_importance(importance_type='gain');kind='training gain, not causal/test importance'
            elif hasattr(estimator,'coef_'):values=np.ravel(estimator.coef_);kind='signed standardized training coefficient, not causal'
            else:continue
            assoc.append({'target':target,'model':name,'kind':kind,'features':sorted([{'feature':c,'value':float(v)} for c,v in zip(cols,values)],key=lambda r:abs(r['value']),reverse=True)})
        contributions[str(h)]=assoc
    acquisition=[]
    for p in (OUT/'sources/upstox').glob('*.json'):acquisition.append(json.loads(p.read_text())['acquired_at'])
    for p in (OUT/'sources/fo').glob('*.json'):acquisition.append(json.loads(p.read_text())['acquired_at'])
    call={'version':'NIFTY_FORECAST_V3_RUN001','issued_at':issued,
        'status':'LATE_ISSUED_ASOF_RECONSTRUCTION — NOT A FRESH PREMARKET FORECAST',
        'genuinely_fresh_forward_confirmation':False,
        'reference_close':reference,'reference_session':reference_day,
        'reference_source_timestamp':str(price.ts.iloc[-1]),'reference_source':'Upstox daily candle, corroborated by official NSE FO underlying on all465 dates',
        'information_cutoff':{'last_completed_indian_session':reference_day,
            'intended_historical_decision_clock':'00:30 IST on following trading session',
            'actual_source_acquisition_last':max(acquisition),
            'intraday_17nov_used':False,'publication_clock_reconstruction':'ASSUMED, NOT VALIDATED',
            'timing_note':'Issued after17Nov open, with only16Nov-completed-session inputs. Horizon includes the already-started17Nov session; no fresh premarket validation claim.'},
        'scope':{'start':'2025-01-01','end':'2026-11-16','pre2025_warmup':False},
        'qualified_predictive_edge':'NONE DEMONSTRATED','qualified_trading_utility':'NOT QUALIFIED; no trading strategy optimized',
        'forecasts':outputs,'registry_sha256':sha(OUT/'registry-config.json'),'dataset_manifest_sha256':sha(OUT/'dataset-manifest.json'),
        'fitted_source_archive':str(OUT/'source-at-first-fit'),
        'verification_sha256':sha(OUT/'verification.json'),
        'libraries':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
            'scipy':scipy.__version__,'scikit_learn':sklearn.__version__,'lightgbm':lightgbm.__version__},
        'limitations':['All historical evaluation dates are research-exposed',
            'No model/target improvement survives the simultaneous weekly uncertainty family; monthly sample too small',
            'Direct distributions under-cover; nominal intervals are not coverage guarantees',
            'Current-membership basket is research-only and excluded from primary selectors',
            'FO/institutional historical publication clocks and vendor revision vintages are not archived',
            'Next valid premarket freeze requires a not-yet-started origin and all necessary newly completed inputs']}
    save('model-contributions.json',contributions);save(destination.name,call)
    save('guard-amendment.json',{'change':'Input schema/time guards, explicit contract-ID exclusion, intraday invalid-day rejection and corrected progress label',
        'why':'Negative-control hardening, no parameter or model selection change',
        'trained_data_affected':False,'proof':'15 checks pass, including exact feature rebuild and representative ridge/boosted prediction reproduction',
        'original_code_preserved':str(OUT/'source-at-first-fit'),
        'current_code_hashes':{p.name:sha(p) for p in Path(__file__).parent.glob('*.py')}})
    print(json.dumps({'saved':str(destination),'status':call['status'],'forecasts':{k:{'up':v['positive_return_probability'],'mean':v['expected_return_regression'],'endpoint':v['expected_endpoint_date']} for k,v in outputs.items()}}),flush=True)
if __name__=='__main__':main()
