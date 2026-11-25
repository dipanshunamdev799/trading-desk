"""Rebuild exact reference laws before new models are fitted."""
import joblib
from .common import *
from research.nifty_forecast_v7.experiments import all_frames
from research.nifty_forecast_v7.models import fit, location, laws
from research.nifty_forecast_v7.analyze import benchmarks
from research.nifty_forecast_v3.experiment import available, inner_split

V7_NAMES = ['T_ROT_DOMESTIC','T_ROT_EMBARGO','T_ROT_LAG5','T_DAY_ETF','T_ELASTIC_EMBARGO']


def sources():
    earlier = read('preservation.json',V7)['files']
    v7 = read('delivery-manifest.json',V7)['delivered']
    files = earlier | {str(Path(p)):v for p,v in v7.items()}
    manifest=V7/'delivery-manifest.json'
    files[str(manifest.relative_to(ROOT))]=sha(manifest)
    review=[]
    paths=[ROOT/'NIFTY_V7_RESEARCH.md', *V7.glob('V7_*.md'), *V7.glob('*registry.json'),
           *V7.glob('*verification.json'), V7/'cluster-definitions.json',
           V7/'all-predictions.csv', V7/'complete-comparison.csv']
    paths += list((ROOT/'research/nifty_forecast_v7').glob('*.py'))
    for p in paths:
        text=p.read_text(encoding='utf-8')
        review.append({'file':str(p.relative_to(ROOT)),'lines':len(text.splitlines()),'sha256':sha(p)})
    save('preservation.json', {'recorded_at':now(),'files':files,'review':review})


def run():
    if (OUT/'reproduction.json').exists():raise FileExistsError('Use a fresh V8 directory')
    sources()
    from research.nifty_forecast_v6 import reproduce as legacy
    legacy.save=lambda name,data:save('legacy-'+name,data)
    legacy.run()
    frames,_=all_frames()
    low=frames['nodef'];rot=frames['rotation'].drop(columns=low.columns);daily=frames['daily']
    frames['rotation_domestic']=pd.concat([low,rot[['financial_spread','defensive_dispersion']]],axis=1)
    frames['rotation_lag']=pd.concat([low,rot.shift(5)],axis=1)
    frames['day_etf']=pd.concat([low,daily[['l_etf_average','l_etf_delta5']]],axis=1)
    frozen=benchmarks()
    v7=pd.read_csv(V7/'all-predictions.csv');specs=read('followup-registry.json',V7)['configurations']
    y=matrix('labels-5.csv');price=matrix('price.csv').close
    results=[];manifest=[];records=[];coeff=[];paired=[]
    for name in V7_NAMES+['V6_BRIER','V6_CRPS']:
        control=frozen[5,name] if name.startswith('V6') else v7[(v7.horizon==5)&(v7.model==name)]
        for fold,g in control.groupby('fold'):
            cutoff=g.origin.min()
            if name.startswith('V6'):
                config={'frame':'nodef' if name=='V6_BRIER' else 'noauto_volume'}
                tr=available(y,cutoff);ii,vv=inner_split(y,tr);q=g.origin.tolist()
            else:
                config=specs[name];obj=joblib.load(V7/'models'/f'{name}-5-{fold}.joblib')
                tr,ii,vv,q=(obj[k] for k in ['training','inner','validation','query'])
            x=frames[config['frame']];g=g.set_index('origin').loc[q]
            inner=fit(config,x.loc[ii],y.loc[ii,'return'].to_numpy())
            model=fit(config,x.loc[tr],y.loc[tr,'return'].to_numpy())
            residual=y.loc[vv,'return'].to_numpy()-location(inner,x.loc[vv])
            forecast=laws(model,x.loc[q],residual,x.loc[vv,'p_rv21'].to_numpy())
            error=0.;prior=frozen[5,'V6_BRIER'].set_index('origin')
            scaler=model['scale'];weights=model['transform']@model['estimator'].coef_
            for j,c in enumerate(scaler.cols):
                coeff.append({'model':name,'fold':fold,'feature':c,'coefficient':weights[j],'median':scaler.med[j],
                              'mean':scaler.mu[j],'sd':scaler.sd[j],'intercept':model['estimator'].intercept_})
            for d,law in zip(q,forecast):
                row=g.loc[d];score=law.score(row.realized_return)
                error=max(error,max(abs(score[c]-row[c]) for c in ['p','predicted_mean','predicted_median','brier','crps']))
                records.append({'model':name,'fold':fold,'origin':d,'endpoint':row.endpoint,'atoms':law.a.tolist(),'weights':law.w.tolist()})
                outcome=bool(row.outcome);correct=bool((score['p']>=.5)==outcome)
                paired.append({'model':name,'fold':fold,'origin':d,'endpoint':row.endpoint,'regime':row.regime,
                               'outcome':outcome,'correct':correct,'p':score['p'],'brier_gain_vs_v6':prior.loc[d,'brier']-score['brier'],
                               'crps_gain_vs_v6':prior.loc[d,'crps']-score['crps']})
                results.append({'model':name,'fold':fold,'horizon':5,'origin':d,'endpoint':row.endpoint,
                               **score,**law.stats(float(price.loc[d]))['quantiles']})
            assert error<1e-12,(name,fold,error)
            manifest.append({'model':name,'fold':fold,'decision_anchor':cutoff,'configuration':config,'columns':list(x),
                             'training':list(tr),'inner':list(ii),'validation':list(vv),'max_abs_error':error})
    write('reproduced-predictions.csv',pd.DataFrame(results));write('winner-origin-diagnosis.csv',pd.DataFrame(paired));write('winner-coefficients.csv',pd.DataFrame(coeff))
    (OUT/'reproduced-endpoint-laws.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records),encoding='utf-8')
    save('reproduction.json',{'passed':True,'forecasts':len(results),'folds':manifest,'max_error':max(r['max_abs_error'] for r in manifest)})
    print('Reproduced',len(results),'weekly benchmarks',flush=True)


if __name__=='__main__':run()
