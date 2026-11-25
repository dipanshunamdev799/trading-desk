"""Repair only the documented unused-global-metadata error in Indian-only forest."""
import joblib
from .common import *
from .models import *
from .data import load
from .expansion import variant
from research.nifty_forecast_v3.experiment import available,inner_split
def run():
    if (OUT/'predictions-stage3-repair.csv').exists():raise FileExistsError('Repair already frozen')
    save('repair-registration.json',{'registered_at':now(),'candidate':'I06_forest','reason':'Original fit read x_global_mean into unused model metadata even when all global inputs intentionally absent. Use zero metadata only in that case; no forest feature/target/parameter change.',
        'old_models_sha256':sha(OUT/'source-at-first-fit/models.py'),'new_models_sha256':sha(SRC/'models.py'),'original_failures_preserved':True,'no_new_hypothesis':True})
    x=pd.read_csv(OUT/'features.csv',index_col=0);price=pd.read_csv(OUT/'price.csv',index_col=0);labs={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [1,3,5,21]};data,_=load();xx=variant('I06_forest',x,data);ctx={'own':query_own(x,price),'labels':labs};old=pd.read_csv(V3/'predictions.csv');records=[];fits=[];live={}
    for h in [5,21]:
        query=old[(old.horizon==h)&(old.model=='B00_empirical')&(old.split=='outer_exposed')];folds={n:list(g.origin) for n,g in query.groupby('fold')};folds['LIVE_ASOF']=[x.index[-1]]
        for fold,days in folds.items():
            cutoff=days[0];ix=available(labs[h],cutoff);ii,vv=inner_split(labs[h],ix);ctx['cutoff']=cutoff;name='I06_forest'
            inner=fit('N01',xx.loc[ii],labs[h].loc[ii,'return'].to_numpy(),h,ctx);res=labs[h].loc[vv,'return'].to_numpy()-mean_prediction(inner,xx.loc[vv],ctx);model=fit('N01',xx.loc[ix],labs[h].loc[ix,'return'].to_numpy(),h,ctx);pred=laws(model,xx.loc[days],ctx,res)
            path=OUT/'models'/f'h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'variant':name,'cutoff':cutoff},path,compress=3)
            fits.append({'id':f'V5-H{h}-{fold}-{name}-REPAIR','horizon':h,'fold':fold,'model':name,'stage':'3-repair','status':'ok','last_training_endpoint':str(labs[h].loc[ix,'endpoint'].max()),'first_query':cutoff,'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
            if fold=='LIVE_ASOF':live.setdefault(str(h),{})[name]={'statistics':pred[0].stats(float(price.close.iloc[-1])),'atoms':pred[0].a.tolist(),'weights':pred[0].w.tolist()};continue
            for day,law in zip(days,pred):r=query.set_index('origin').loc[day];records.append({'horizon':h,'stage':3,'fold':fold,'model':name,'origin':day,'endpoint':r.endpoint,'split':'outer_exposed','regime':r.regime,'trend':r.trend_regime,'global_risk':('riskoff' if x.loc[day,'x_global_mean']<0 else 'riskon'),'participation':('broad' if x.loc[day,'i_participation']>.5 else 'narrow'),'expiry':('near' if x.loc[day,'d_option_dte']<=2 else 'far'),**law.score(labs[h].loc[day,'return'])})
    pd.DataFrame(records).to_csv(OUT/'predictions-stage3-repair.csv',index=False);save('fits-stage3-repair.json',fits);save('live-stage3-repair.json',live);print('Repaired same I06 candidate',len(fits),'fits',flush=True)
if __name__=='__main__':run()
