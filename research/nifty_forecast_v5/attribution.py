"""Cross old/new feature systems with old/new laws; no new fitted estimator."""
import joblib
from .common import *
from research.nifty_forecast_v3.models import predict as old_predict
from research.nifty_forecast_v4.distributions import Distribution
from .models import mean_prediction
def run():
    if (OUT/'attribution-registry.json').exists():raise FileExistsError('Attribution study exists')
    save('attribution-registry.json',{'registered_at':now(),'reason':'Do not attribute improvement from coherent-law construction to newly acquired indices/global sources. Cross feature systems and law construction with cached unchanged estimators.',
        'models':{'AT00_old_newlaw':'Exact old V3/V4 price+sector mean model/residuals with V5 .65conditional/.35unconditional law',
            'AT01_new_oldlaw':'Exact V5 I00 mean/residuals with V4 D03 .5mean+.5base location and raw residual law'},
        'reference_cells':['V4_D03_residual_shrunk (old/old)','I00 (new/new)'],'new_model_fits':0,'status':'Postdiscovery attribution; all exposed, not independent confirmation'})
    oldx=pd.read_csv(V3/'features.csv',index_col=0);x=pd.read_csv(OUT/'features.csv',index_col=0);old=pd.read_csv(V3/'predictions.csv');records=[];ledger=[]
    for h in [5,21]:
        query=old[(old.horizon==h)&(old.model=='B00_empirical')&(old.split=='outer_exposed')]
        for fold,g in query.groupby('fold'):
            original=joblib.load(V3/'models'/f'h{h}-{fold}-A00_sector.joblib');new=joblib.load(OUT/'models'/f'h{h}-{fold}-I00.joblib')
            pp=old_predict(original['model'],oldx.loc[g.origin],original['residuals']);mu_new=mean_prediction(new['model'],x.loc[g.origin],{})
            pool_old=original['model']['y'][-252:];pool_new=new['model']['pool']
            for j,r in enumerate(g.itertuples()):
                laws={'AT00_old_newlaw':Distribution(np.r_[np.maximum(pp[j]['mean']+original['residuals'],-.999999),pool_old],np.r_[np.full(len(original['residuals']),.65/len(original['residuals'])),np.full(len(pool_old),.35/len(pool_old))]),
                    'AT01_new_oldlaw':Distribution(np.maximum(.5*mu_new[j]+.5*pool_new.mean()+new['residual'],-.999999))}
                for name,law in laws.items():records.append({'horizon':h,'stage':5,'fold':fold,'model':name,'origin':r.origin,'endpoint':r.endpoint,'split':'outer_exposed','regime':r.regime,'trend':r.trend_regime,'global_risk':('riskoff' if x.loc[r.origin,'x_global_mean']<0 else 'riskon'),'participation':('broad' if x.loc[r.origin,'i_participation']>.5 else 'narrow'),'expiry':('near' if x.loc[r.origin,'d_option_dte']<=2 else 'far'),**law.score(r.realized_return)})
            for name in ['AT00_old_newlaw','AT01_new_oldlaw']:
                path=OUT/'models'/f'h{h}-{fold}-{name}.joblib';joblib.dump({'old_source':str(V3/'models'/f'h{h}-{fold}-A00_sector.joblib'),'new_source':str(OUT/'models'/f'h{h}-{fold}-I00.joblib'),'rule':name,'fitted_new_estimator':False},path)
                ledger.append({'id':f'V5-H{h}-{fold}-{name}','horizon':h,'fold':fold,'model':name,'stage':5,'status':'ok','cached_estimator_evaluation':True,'first_query':g.origin.min(),'last_training_endpoint':str(pd.read_csv(OUT/f'labels-{h}.csv',index_col=0).loc[new['model']['train_dates'],'endpoint'].max()),'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
    pd.DataFrame(records).to_csv(OUT/'predictions-stage5.csv',index=False);save('fits-stage5.json',ledger);print('Completed2x2 feature/law attribution without new estimator fitting',flush=True)
if __name__=='__main__':run()
