"""Registered follow-up: stress the new native-index lead, not a free search."""
import joblib
from .common import *
from .data import load
from .models import fit,mean_prediction,laws,panel,query_own
from research.nifty_forecast_v3.experiment import available,inner_split
VARIANTS={
 'I01_legacy':('I00','Old native sector block and recomputed old-sector participation only'),
 'I02_newindices':('I00','New native broad/size/style indices only plus recomputed participation'),
 'I03_nosize':('I00','Remove midcap/smallcap and recompute internals'),
 'I04_delay':('I00','Lag all Indian internal features one extra session'),
 'I05_rolling126':('I00','Rolling126 training with causal rolling inner model'),
 'I06_forest':('N01','Same shallow forest on Indian-only inputs'),
 'C01_delayglobal':('C00','Extra-session global/relationship lag clock sensitivity'),
 'D02_rawonly':('D01','Joint state with raw derivative block, removing five engineered derivative transforms')}
def variant(name,x,data):
    xx=x.copy()
    native=[k for k in data if not k.startswith(('g_','s_')) and k not in ['nifty_spot','india_vix','niftybees']]
    if name in ['I01_legacy','I02_newindices','I03_nosize']:
        keep=[k for k in native if (not k.startswith('idx_') if name=='I01_legacy' else k.startswith('idx_') if name=='I02_newindices' else not any(t in k.lower() for t in ['midcap','smallcap']))]
        xx=xx.drop(columns=[c for c in xx if c.startswith('i_') and any(c.startswith('i_'+k+'_') for k in native if k not in keep)])
        sr=pd.concat([data[k].close.reindex(x.index).pct_change(5,fill_method=None) for k in keep],axis=1)
        xx['i_participation']=sr.gt(0).sum(axis=1)/sr.notna().sum(axis=1).replace(0,np.nan);xx['i_dispersion']=sr.std(axis=1)
        xx['i_acceleration']=xx.i_participation.diff(5);xx['i_concentration']=sr.abs().max(axis=1)/sr.abs().sum(axis=1).replace(0,np.nan)
        xx['i_leadership_persistence']=sr.rank(axis=1).corrwith(sr.shift(5).rank(axis=1),axis=1)
        if name=='I02_newindices':xx=xx.drop(columns=['i_defensive_cyclical'],errors='ignore')
    elif name=='I04_delay':
        columns=[c for c in xx if c.startswith('i_')];xx[columns]=xx[columns].shift(1)
    elif name=='I06_forest':xx=xx[[c for c in xx if c.startswith(('p_','i_'))]]
    elif name=='C01_delayglobal':
        columns=[c for c in xx if c.startswith(('g_','x_','b_'))];xx[columns]=xx[columns].shift(1)
    elif name=='D02_rawonly':xx=xx.drop(columns=['d_price_oi','d_concentration_risk','d_position_expiry','d_basis_z','d_oi_z'])
    return xx
def run():
    if (OUT/'stage3-registry.json').exists():raise FileExistsError('Expansion already registered')
    save('stage3-registry.json',{'registered_at':now(),'reason':'Stage1 Indian native-index I00 .18610 Brier/.01022 CRPS led global-only and joint; Stage2 derivatives, factors, transfers did not improve it. Follow-up isolates information and stresses timing/window. No hyperparameter tuning.',
        'variants':VARIANTS,'retrospective_only':True,'robust_candidate_gate':'Improve Brier+CRPS vs empirical/price controls; positive all leave-month/phase effects; acceptable50/80coverage; no timing/window reversal; simultaneous interval lower>0. Still research-exposed, never independently validated.',
        'source_hashes':{p.name:sha(p) for p in SRC.glob('*.py')},'after_stage1_hash':sha(OUT/'predictions-stage1.csv'),'after_stage2_hash':sha(OUT/'predictions-stage2.csv')})
    x=pd.read_csv(OUT/'features.csv',index_col=0);price=pd.read_csv(OUT/'price.csv',index_col=0);labs={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [1,3,5,21]};data,_=load()
    ctx={'sector_panel':panel(data,x),'stock_panel':panel(data,x,True),'own':query_own(x,price),'labels':labs};old=pd.read_csv(V3/'predictions.csv');records=[];fits=[];live={}
    for h in [5,21]:
        query=old[(old.horizon==h)&(old.model=='B00_empirical')];query=query[query.split=='outer_exposed'];folds={f:list(g.origin) for f,g in query.groupby('fold')};folds['LIVE_ASOF']=[x.index[-1]]
        for fold,days in folds.items():
            cutoff=days[0];ix=available(labs[h],cutoff);ii,vv=inner_split(labs[h],ix);ctx['cutoff']=cutoff
            for name,(base,hypothesis) in VARIANTS.items():
                xx=variant(name,x,data);trainix=ix[-126:] if name=='I05_rolling126' else ix;innerix=ii[-126:] if name=='I05_rolling126' else ii
                try:
                    inner=fit(base,xx.loc[innerix],labs[h].loc[innerix,'return'].to_numpy(),h,ctx);res=labs[h].loc[vv,'return'].to_numpy()-mean_prediction(inner,xx.loc[vv],ctx)
                    model=fit(base,xx.loc[trainix],labs[h].loc[trainix,'return'].to_numpy(),h,ctx);pred=laws(model,xx.loc[days],ctx,res)
                    path=OUT/'models'/f'h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'variant':name,'cutoff':cutoff,'train_dates':list(trainix)},path,compress=3)
                    fits.append({'id':f'V5-H{h}-{fold}-{name}','horizon':h,'fold':fold,'model':name,'stage':3,'status':'ok','training_n':len(trainix),'last_training_endpoint':str(labs[h].loc[trainix,'endpoint'].max()),'first_query':cutoff,'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
                    if fold=='LIVE_ASOF':live.setdefault(str(h),{})[name]={'statistics':pred[0].stats(float(price.close.iloc[-1])),'atoms':pred[0].a.tolist(),'weights':pred[0].w.tolist()};continue
                    for day,law in zip(days,pred):
                        r=query.set_index('origin').loc[day]
                        records.append({'horizon':h,'stage':3,'fold':fold,'model':name,'origin':day,'endpoint':r.endpoint,'split':'outer_exposed','regime':r.regime,'trend':r.trend_regime,'global_risk':('riskoff' if x.loc[day,'x_global_mean']<0 else 'riskon'),'participation':('broad' if x.loc[day,'i_participation']>.5 else 'narrow'),'expiry':('near' if x.loc[day,'d_option_dte']<=2 else 'far'),**law.score(labs[h].loc[day,'return'])})
                except Exception as e:fits.append({'model':name,'horizon':h,'fold':fold,'stage':3,'status':'failed','error':type(e).__name__+':'+str(e)[:180]})
            print('Registered expansion',h,fold,'failures',sum(r['status']=='failed' for r in fits),flush=True)
    pd.DataFrame(records).to_csv(OUT/'predictions-stage3.csv',index=False);save('fits-stage3.json',fits);save('live-stage3.json',live)
if __name__=='__main__':run()
