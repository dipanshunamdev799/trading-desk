"""Registered two-stage discovery, identical V3/V4 origin dates, purged residuals."""
import argparse,joblib
from .common import *
from .models import *
from .data import load as load_sources
from research.nifty_forecast_v3.experiment import available,inner_split,nonoverlap,effective_n
from research.nifty_forecast_v4.distributions import summarize

STAGE1=['E00','P00','G00','I00','C00','F00','T00','T01','BR00']
def register():
    if (OUT/'registry.json').exists():raise FileExistsError('Registry exists')
    save('registry.json',{'registered_at':now(),'scope':[START,END],'exposure':'All historical observations research-exposed',
        'specifications':{n:{'kind':s[0],'features':s[1],'hypothesis':s[2],'research_only':n in ['T01','BR00']} for n,s in SPECS.items()},
        'stage1':STAGE1,'stage2':[n for n in SPECS if n not in STAGE1],
        'parameters':{'ridge_alpha':100,'kernel_alpha':10,'kernel_gamma':'1/d','PCA_components':5,'rolling_PCA_window':126,
            'spline_knots':3,'spline_degree':2,'forest_trees':64,'forest_depth':3,'forest_minleaf':30,'forest_maxfeatures':.7,'analog_k':40,
            'conditional_unconditional_mixture':[.65,.35],'regime_unconditional_pseudocount':50,'seed':SEED},
        'validation':'Exact V3 prequential origins, monthly refit, min126 mature labels and80 inner fit, last42 purged residual origins; endpoints strictly before refit origin',
        'primary_comparisons':'All primary metrics matched92 weekly/76monthly V3 outer origins; V5 latest source vintage explicitly different',
        'selection':'Historical outer leaderboard is descriptive postselection. No independent claims. No automated hyperparameter tuning.',
        'stage2_rule':'Execute registered mechanisms even if stage1 inconclusive; no unregistered expansion. Later expansions need separate prospective registry before scores.',
        'source_hashes':{p.name:sha(p) for p in SRC.glob('*.py')},'dataset_manifest_sha256':sha(OUT/'dataset-manifest.json')})

def run(stage):
    reg=read('registry.json');names=reg['stage1' if stage==1 else 'stage2'];dest=OUT/f'predictions-stage{stage}.csv'
    if dest.exists():raise FileExistsError('Completed stage is immutable')
    x=pd.read_csv(OUT/'features.csv',index_col=0);price=pd.read_csv(OUT/'price.csv',index_col=0);labs={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [1,3,5,21]}
    data,_=load_sources();ctx={'sector_panel':panel(data,x),'stock_panel':panel(data,x,True),'own':query_own(x,price),'labels':labs}
    if stage==1:
        ctx['sector_panel'].to_csv(OUT/'sector-panel.csv',index=False);ctx['stock_panel'].to_csv(OUT/'stock-panel.csv',index=False)
    old=pd.read_csv(V3/'predictions.csv');records=[];fits=[];live={}
    (OUT/'models').mkdir(exist_ok=True)
    for h in [5,21]:
        queries=old[(old.horizon==h)&(old.model=='B00_empirical')]
        folds={fold:list(g.origin) for fold,g in queries.groupby('fold')};folds['LIVE_ASOF']=[x.index[-1]]
        for fold,days in folds.items():
            cutoff=days[0];ix=available(labs[h],cutoff);ii,vv=inner_split(labs[h],ix);ctx['cutoff']=cutoff
            for name in names:
                try:
                    inner=fit(name,x.loc[ii],labs[h].loc[ii,'return'].to_numpy(),h,ctx)
                    residual=labs[h].loc[vv,'return'].to_numpy()-mean_prediction(inner,x.loc[vv],ctx)
                    model=fit(name,x.loc[ix],labs[h].loc[ix,'return'].to_numpy(),h,ctx);predictions=laws(model,x.loc[days],ctx,residual)
                    path=OUT/'models'/f'h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':residual,'inner_fit_dates':list(ii),'inner_validation_dates':list(vv),'cutoff':cutoff},path,compress=3)
                    fits.append({'id':f'V5-H{h}-{fold}-{name}','stage':stage,'horizon':h,'fold':fold,'model':name,'status':'ok','training_n':len(ix),'inner_n':len(ii),
                        'last_training_endpoint':str(labs[h].loc[ix,'endpoint'].max()),'first_query':cutoff,'last_inner_endpoint':str(labs[h].loc[ii,'endpoint'].max()),'inner_first':vv[0],
                        'artifact':str(path.relative_to(ROOT)),'sha256':sha(path),'panel_rows':model.get('transfer',{}).get('panel_rows'),'panel_dates':model.get('transfer',{}).get('panel_dates')})
                    if fold=='LIVE_ASOF':live.setdefault(str(h),{})[name]={'statistics':predictions[0].stats(float(price.close.iloc[-1])),'atoms':predictions[0].a.tolist(),'weights':predictions[0].w.tolist()};continue
                    orig=queries.set_index('origin')
                    for day,law in zip(days,predictions):
                        row=orig.loc[day];score=law.score(float(labs[h].loc[day,'return']))
                        records.append({'horizon':h,'stage':stage,'fold':fold,'model':name,'origin':day,'endpoint':row.endpoint,'split':row.split,
                            'regime':'high_vol' if x.loc[day,'p_rv21']>x.loc[ix,'p_rv21'].median() else 'low_vol',
                            'trend':'trend' if abs(x.loc[day,'p_ret21'])>x.loc[day,'p_rv21']*np.sqrt(21) else 'sideways',
                            'global_risk':'riskoff' if x.loc[day,'x_global_mean']<0 else 'riskon',
                            'participation':'broad' if x.loc[day,'i_participation']>.5 else 'narrow',
                            'expiry':'near' if x.loc[day,'d_option_dte']<=2 else 'far',**score})
                except Exception as exc:
                    fits.append({'id':f'V5-H{h}-{fold}-{name}','horizon':h,'fold':fold,'model':name,'stage':stage,'status':'failed','error':type(exc).__name__+': '+str(exc)[:220]})
            print('Stage',stage,'horizon',h,'fold',fold,'failed',sum(r['status']=='failed' for r in fits),flush=True)
    pd.DataFrame(records).to_csv(dest,index=False);save(f'fits-stage{stage}.json',fits);save(f'live-stage{stage}.json',live)
    print('Stage complete',stage,'records',len(records),'failures',sum(r['status']=='failed' for r in fits),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','stage1','stage2']);a=p.parse_args()
    if a.action=='register':register()
    else:run(int(a.action[-1]))
