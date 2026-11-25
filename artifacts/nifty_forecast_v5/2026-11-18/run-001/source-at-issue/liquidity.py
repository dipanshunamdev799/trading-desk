"""Information-led expansion: ETF activity and wider-stock volume, separately versioned."""
import gzip,json,joblib,requests,sys
from urllib.parse import quote
from .common import *
from .models import fit,laws,mean_prediction,query_own
from .data import load
from research.nifty_forecast_v3.experiment import available,inner_split
def run():
    if (OUT/'stage4-registry.json').exists():raise FileExistsError('Liquidity expansion already registered')
    save('stage4-registry.json',{'registered_at':now(),'rationale':'Volume/ETF information was acquired but not represented in earlier V5 regression families; add actual INR gold/silver and foreign-equity ETF proxies, not invented commodity spot or IV.',
        'models':{'L00':{'base':'P00','hypothesis':'ETF activity incremental to price'},'L01':{'base':'I00','hypothesis':'ETF activity incremental to native internals'},'L02':{'base':'C00','hypothesis':'ETF activity incremental to global/Indian state'},'L03':{'base':'C00','hypothesis':'Additional wider-stock volume participation; survivorship-exposed','research_only':True}},
        'requested_symbols':['GOLDBEES','SILVERBEES','MON100','HNGSNGBEES'],'features':'ETF ret5,rv21,volume/prior21median and NIFTYBEES; basket median volume ratio/active advance/volume dispersion',
        'no_tuning':True,'status':'Registered exploratory expansion after stages1/2; additional multiplicity, not new validation','source_sha256':sha(Path(__file__))})
    master=json.loads(gzip.decompress((OUT/'metadata/NSE.json.gz').read_bytes()));lookup={r.get('trading_symbol'):r for r in master if r.get('segment')=='NSE_EQ'}
    sys.path[:0]=[str(ROOT/'backend')]
    from app.config import get_settings
    token=get_settings().upstox_analytics_token;acquisition=[];extra={}
    for name in ['GOLDBEES','SILVERBEES','MON100','HNGSNGBEES']:
        if name not in lookup:acquisition.append({'symbol':name,'ok':False,'reason':'Not in current master'});continue
        key=lookup[name]['instrument_key'];url='https://api.upstox.com/v3/historical-candle/'+quote(key,safe='')+'/days/1/'+END+'/'+START;sent=now()
        try:
            r=requests.get(url,headers={'Authorization':'Bearer '+token},timeout=20);r.raise_for_status();rows=[]
            for a in r.json().get('data',{}).get('candles',[]):
                day=pd.Timestamp(a[0]).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d')
                if START<=day<=END:rows.append({'day':day,**dict(zip(['open','high','low','close','volume'],a[1:6]))})
            f=pd.DataFrame(rows).drop_duplicates('day').set_index('day').sort_index();valid=(f[['open','high','low','close']]>0).all(axis=1)&f.high.ge(f[['open','low','close']].max(axis=1))&f.low.le(f[['open','high','close']].min(axis=1));f=f[valid];extra[name]=f
            path=OUT/'liquidity'/f'{name}.csv';path.parent.mkdir(exist_ok=True);f.to_csv(path);acquisition.append({'symbol':name,'ok':True,'key':key,'url':url,'sent':sent,'received':now(),'server_date':r.headers.get('Date'),'rows':len(f),'sha256':sha(path),'classification':'INR-traded ETF proxy; not foreign index/commodity spot; raw price adjustment vintage limited'})
        except Exception as e:acquisition.append({'symbol':name,'ok':False,'error':type(e).__name__,'sent':sent,'received':now()})
    save('liquidity-acquisition.json',acquisition)
    data,_=load();extra['NIFTYBEES']=data['niftybees'];x=pd.read_csv(OUT/'features.csv',index_col=0);price=pd.read_csv(OUT/'price.csv',index_col=0);new=pd.DataFrame(index=x.index)
    for name,f in extra.items():
        f=f.reindex(x.index);new[name+'_ret5']=f.close.pct_change(5,fill_method=None);new[name+'_rv21']=f.close.pct_change(fill_method=None).rolling(21).std();new[name+'_volume']=f.volume/f.volume.shift().rolling(21).median()
    vv=pd.concat({n:f.volume for n,f in data.items() if n.startswith('s_')},axis=1).reindex(x.index);cc=pd.concat({n:f.close for n,f in data.items() if n.startswith('s_')},axis=1).reindex(x.index)
    ratios=vv/vv.shift().rolling(21).median();proxy=pd.DataFrame({'median_activity':ratios.median(axis=1),'volume_dispersion':ratios.std(axis=1),'active_advance':((cc.pct_change(fill_method=None)>0)&(ratios>1)).sum(axis=1)/ratios.notna().sum(axis=1)},index=x.index)
    new=new.replace([np.inf,-np.inf],np.nan);new.to_csv(OUT/'liquidity-features.csv');proxy.to_csv(OUT/'liquidity-proxy-features.csv')
    labs={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [1,3,5,21]};ctx={'own':query_own(x,price),'labels':labs};old=pd.read_csv(V3/'predictions.csv');records=[];fits=[];live={}
    for h in [5,21]:
        query=old[(old.horizon==h)&(old.model=='B00_empirical')&(old.split=='outer_exposed')];folds={n:list(g.origin) for n,g in query.groupby('fold')};folds['LIVE_ASOF']=[x.index[-1]]
        for fold,days in folds.items():
            cutoff=days[0];ix=available(labs[h],cutoff);ii,vv=inner_split(labs[h],ix);ctx['cutoff']=cutoff
            for name,base in [('L00','P00'),('L01','I00'),('L02','C00'),('L03','C00')]:
                additions=pd.concat([new,proxy.add_prefix('CURRENT_BASKET_')],axis=1) if name=='L03' else new;xx=pd.concat([x,additions.add_prefix('p_liq_')],axis=1)
                try:
                    inner=fit(base,xx.loc[ii],labs[h].loc[ii,'return'].to_numpy(),h,ctx);res=labs[h].loc[vv,'return'].to_numpy()-mean_prediction(inner,xx.loc[vv],ctx);model=fit(base,xx.loc[ix],labs[h].loc[ix,'return'].to_numpy(),h,ctx);pred=laws(model,xx.loc[days],ctx,res)
                    path=OUT/'models'/f'h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'variant':name,'cutoff':cutoff},path,compress=3)
                    fits.append({'id':f'V5-H{h}-{fold}-{name}','horizon':h,'fold':fold,'model':name,'stage':4,'status':'ok','last_training_endpoint':str(labs[h].loc[ix,'endpoint'].max()),'first_query':cutoff,'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
                    if fold=='LIVE_ASOF':live.setdefault(str(h),{})[name]={'statistics':pred[0].stats(float(price.close.iloc[-1])),'atoms':pred[0].a.tolist(),'weights':pred[0].w.tolist()};continue
                    for day,law in zip(days,pred):r=query.set_index('origin').loc[day];records.append({'horizon':h,'stage':4,'fold':fold,'model':name,'origin':day,'endpoint':r.endpoint,'split':'outer_exposed','regime':r.regime,'trend':r.trend_regime,'global_risk':('riskoff' if x.loc[day,'x_global_mean']<0 else 'riskon'),'participation':('broad' if x.loc[day,'i_participation']>.5 else 'narrow'),'expiry':('near' if x.loc[day,'d_option_dte']<=2 else 'far'),**law.score(labs[h].loc[day,'return'])})
                except Exception as e:fits.append({'model':name,'horizon':h,'fold':fold,'stage':4,'status':'failed','error':type(e).__name__+':'+str(e)[:180]})
            print('Liquidity expansion',h,fold,flush=True)
    pd.DataFrame(records).to_csv(OUT/'predictions-stage4.csv',index=False);save('fits-stage4.json',fits);save('live-stage4.json',live)
if __name__=='__main__':run()
