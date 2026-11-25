"""Fresh experimental endpoint forecasts using authenticated18Nov official closes."""
import re,zipfile,joblib,warnings
from .common import *
from .data import load
from .features import build,completion
from .models import fit,mean_prediction,laws
from .expansion import variant
from research.nifty_forecast_v3.features import labels_for
from research.nifty_forecast_v3.experiment import available,inner_split

def run():
    if (OUT/'experimental-forecasts.json').exists():raise FileExistsError('Issued forecasts are immutable')
    save('forecast-selection.json',{'selected_at':now(),'status':'POSTSELECTED EXPLORATORY; no independent validation',
        'weekly_distribution':'L01, lowest exposed CRPS among usable V5 systems','weekly_direction_alternative':'I03_nosize, best exposed Brier; retain its own full law',
        'monthly_default':'E00 simple historical law; higher complexity failed calibration','monthly_research_alternative':'I01_legacy best V5 exposed CRPS, but severe undercoverage',
        'reference_strategy':'Official NSE18Nov index OHLC + cash ETF OHLC/volume, independently crosschecked with official FO underlying. No fake broker candle or overwritten history.'})
    data,_=load();identities=read('requested-universe.json')['identities'];index=pd.read_csv(OUT/'latest-sources/index18.csv')
    if set(index['Index Date'])!={'18-11-2026'}:raise ValueError('NSE_INDEX_DATE_MISMATCH')
    norm=lambda s:re.sub('[^a-z0-9]','',s.lower().replace('index',''))
    aliases={'niftyfinservice':'niftyfinancialservices','niftyconsumption':'niftyindiaconsumption','niftyinfra':'niftyinfrastructure','niftyinfralog':'niftyindiainfrastructurelogistics'}
    native={norm(r['Index Name']):r for r in index.to_dict('records')};matches=[]
    for name,meta in identities.items():
        if meta['family']!='domestic':continue
        key=norm(meta['key'].split('|')[-1]);key=aliases.get(key,key)
        if key not in native:raise ValueError('UNMATCHED_NATIVE_INDEX: '+name)
        r=native[key];row={'open':float(r['Open Index Value']),'high':float(r['High Index Value']),'low':float(r['Low Index Value']),'close':float(r['Closing Index Value']),'volume':0,'oi':0,'ts':'2026-11-18T00:00:00+05:30'}
        if not row['low']<=min(row['open'],row['close'])<=max(row['open'],row['close'])<=row['high']:raise ValueError('INVALID_NSE_OHLC')
        data[name].loc['2026-11-18']=pd.Series(row);matches.append({'identity':name,'official_index_name':r['Index Name'],'classification':'Official index OHLC; published constituent turnover is NOT treated as traded index volume'})
    z=zipfile.ZipFile(OUT/'latest-sources/cash18.zip');cash=pd.read_csv(z.open(z.namelist()[0]));cash=cash[cash.SctySrs=='EQ']
    if set(cash.TradDt)!={'2026-11-18'}:raise ValueError('NSE_CASH_DATE_MISMATCH')
    byisin={r['ISIN']:r for r in cash.to_dict('records')};etfs={}
    for meta in read('liquidity-acquisition.json'):
        if meta['ok']:etfs[meta['symbol']]=pd.read_csv(OUT/'liquidity'/f"{meta['symbol']}.csv",index_col=0)
    for name,meta in identities.items():
        if meta['family'] not in ['stock_proxy','etf']:continue
        isin=meta['key'].split('|')[-1]
        if isin not in byisin:continue
        r=byisin[isin];data[name].loc['2026-11-18']=pd.Series({'open':r['OpnPric'],'high':r['HghPric'],'low':r['LwPric'],'close':r['ClsPric'],'volume':r['TtlTradgVol'],'oi':0,'ts':'2026-11-18T00:00:00+05:30'})
    for symbol in etfs:
        r=cash[cash.TckrSymb==symbol].iloc[0];etfs[symbol].loc['2026-11-18']=pd.Series({'open':r.OpnPric,'high':r.HghPric,'low':r.LwPric,'close':r.ClsPric,'volume':r.TtlTradgVol})
    etfs['NIFTYBEES']=data['niftybees']
    with warnings.catch_warnings():warnings.simplefilter('ignore',pd.errors.PerformanceWarning);x,price,alignment=build(data)
    reference=float(price.close.iloc[-1]);official=read('fo/2026-11-18.json');underlying=float(next(r['UndrlygPric'] for r in official['rows'] if float(r.get('UndrlygPric') or 0)>0))
    if price.index[-1]!='2026-11-18' or abs(reference-underlying)>1e-6:raise ValueError('REFERENCE_FO_CROSSCHECK_FAILED')
    # Historical features used for research must not be overwritten or retrospectively revised.
    original=pd.read_csv(OUT/'features.csv',index_col=0);np.testing.assert_allclose(x.reindex(original.index).to_numpy(),original.to_numpy(),equal_nan=True,atol=1e-10,rtol=1e-10)
    dest=OUT/'latest-inputs';dest.mkdir(exist_ok=True);x.to_csv(dest/'features.csv');price.to_csv(dest/'price.csv');alignment.to_csv(dest/'global-availability.csv',index=False)
    liquid=pd.DataFrame(index=x.index)
    for name,f in etfs.items():
        f=f.reindex(x.index);liquid[name+'_ret5']=f.close.pct_change(5,fill_method=None);liquid[name+'_rv21']=f.close.pct_change(fill_method=None).rolling(21).std();liquid[name+'_volume']=f.volume/f.volume.shift().rolling(21).median()
    liquid=liquid.replace([np.inf,-np.inf],np.nan);liquid.to_csv(dest/'liquidity-features.csv')
    labels={h:labels_for(price,h) for h in [1,3,5,21]}
    for h,f in labels.items():f.to_csv(dest/f'labels-{h}.csv')
    from research.nifty_forecast.horizons import future_sessions
    calendar=read('horizon-calendar-v1.json',ROOT/'artifacts/nifty_forecast/2026-11-17');future=future_sessions('2026-11-18',calendar,21);scope(future)
    forecasts={};models=read('metrics.json');ctx={'labels':labels,'cutoff':'2026-11-18'}
    for h,names in [(5,['L01','I03_nosize']),(21,['E00','I01_legacy'])]:
        ix=available(labels[h],'2026-11-18');ii,vv=inner_split(labels[h],ix)
        for name in names:
            xx=pd.concat([x,liquid.add_prefix('p_liq_')],axis=1) if name=='L01' else variant(name,x,data) if name in ['I03_nosize','I01_legacy'] else x
            base='I00' if name!='E00' else 'E00';inner=fit(base,xx.loc[ii],labels[h].loc[ii,'return'].to_numpy(),h,ctx);res=labels[h].loc[vv,'return'].to_numpy()-mean_prediction(inner,xx.loc[vv],ctx)
            fitted=fit(base,xx.loc[ix],labels[h].loc[ix,'return'].to_numpy(),h,ctx);law=laws(fitted,xx.loc[['2026-11-18']],ctx,res)[0]
            artifact=dest/f'h{h}-{name}.joblib';joblib.dump({'model':fitted,'residual':res,'training_dates':list(ix),'last_training_endpoint':labels[h].loc[ix,'endpoint'].max()},artifact,compress=3)
            historical=next(r for r in models if r['horizon']==h and r['model']==name)
            forecasts[f'h{h}-{name}']={'horizon':h,'model':name,'endpoint':future[h-1],'target_sessions':future[:h],'statistics':law.stats(reference),'atoms':law.a.tolist(),'weights':law.w.tolist(),
                'historical_exposed_performance':historical,'last_training_endpoint':str(labels[h].loc[ix,'endpoint'].max()),'training_origin_count':len(ix),'model_path':str(artifact.relative_to(ROOT)),'model_sha256':sha(artifact),
                'status':'EXPERIMENTAL / UNCALIBRATED / NOT INDEPENDENTLY VALIDATED'}
    issued=now();latest_alignment=alignment[alignment.origin=='2026-11-18']
    if any(pd.Timestamp(r['available_assumption'])>pd.Timestamp(issued) for r in latest_alignment.to_dict('records')):raise ValueError('FUTURE_GLOBAL_CLOSE_AT_ISSUE')
    save('latest-inputs/native-identity-mapping.json',matches)
    save('experimental-forecasts.json',{'issued_at':issued,'reference_session':'2026-11-18','reference_close':reference,'reference_source':'Official NSE index18Nov CSV independently corroborated by NSE FO18Nov underlying',
        'first_target_session':future[0],'before_first_target_session':pd.Timestamp(issued).date()<pd.Timestamp(future[0]).date(),
        'source_acquisition':read('latest-sources/acquisition.json'),'source_age_limitations':'Global inputs use conservative completion/receipt assumptions; vendor histories revised. No unfinished US18Nov close used.',
        'training_rule':'Distinct V5 latest-as-of refit using matured endpoints strictly before reference; not a change to V4 monthly-refit prospective protocol',
        'historical_feature_prefix_unchanged':True,'forecasts':forecasts,'source_code_hashes':{p.name:sha(p) for p in SRC.glob('*.py')},
        'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in list(dest.glob('*'))+list((OUT/'latest-sources').glob('*')) if p.is_file()},
        'independent_validation':False,'production_status':'NO DEPLOYMENT','outcomes':'UNRESOLVED; no watcher installed','v4_ledger_modified':False})
    print('Frozen fresh experimental laws',issued,'reference',reference,'first_target',future[0],flush=True)
if __name__=='__main__':run()
