"""Finite new mechanisms; all endpoint outputs are coherent weighted laws."""
from .common import *
from sklearn.linear_model import Ridge
from sklearn.decomposition import PCA
from sklearn.preprocessing import SplineTransformer
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics.pairwise import cosine_distances,manhattan_distances
from research.nifty_forecast_v4.distributions import Distribution

SPECS={
 'E00':('empirical','price','Unconditional return law'),
 'P00':('ridge','price','Price-only coherent control'),
 'G00':('ridge','global','Global-only predictive information'),
 'I00':('ridge','indian','Native broad/sector internal structure'),
 'C00':('ridge','combined','Global increment beyond Indian prices/sectors'),
 'F00':('pca','combined','Five static train-only joint factors'),
 'F01':('rolling_pca','combined','Causal rolling126 loading adaptation'),
 'N00':('spline','core','Low-complexity additive nonlinear response'),
 'N01':('forest','combined','Shallow randomized conditional return law'),
 'N02':('kernel','core','Regularized smooth joint-state interaction'),
 'R00':('regime','core','Global-risk x domestic-volatility conditional law'),
 'A00':('cosine','joint_derivatives','Angular state analogue with shrinkage'),
 'A01':('manhattan','joint_derivatives','Robust L1 state analogue with shrinkage'),
 'S00':('ridge','sequence','Cross-market evolution beyond static state'),
 'T00':('sector_transfer','core','Date-grouped shared sector-to-NIFTY mapping'),
 'T01':('stock_transfer','core','Wider equity transfer, survivorship-exposed'),
 'M00':('multitask','core','Normalized shared1/3/5/21-session tasks'),
 'D00':('ridge','derivatives','Price x positioning x expiry risk'),
 'D01':('ridge','joint_derivatives','Derivative increment beyond global/Indian state'),
 'BR00':('ridge','proxy','Wider current-stock participation proxy')}
CORE=['p_ret1','p_ret5','p_ret21','p_rv21','p_vix','i_participation','i_dispersion','i_defensive_cyclical','x_global_mean','x_global_dispersion','x_india_relative','x_oil_fx','x_tech_it','d_oi_pcr','d_price_oi','d_position_expiry']
def cols(x,mode):
    prefixes={'price':('p_',),'global':('g_','b_'),'indian':('p_','i_'),'combined':('p_','i_','g_','b_','x_'),
      'derivatives':('p_','d_'),'joint_derivatives':('p_','i_','g_','b_','x_','d_'),
      'sequence':('p_','i_','g_','b_','x_','l_'),'proxy':('p_','i_','g_','b_','x_','s_')}
    return [c for c in CORE if c in x] if mode=='core' else [c for c in x if c.startswith(prefixes[mode])]

class Scale:
    def fit(self,x):
        self.cols=[c for c in x if x[c].notna().sum()>=30]
        a=x[self.cols].to_numpy(float);self.med=np.nanmedian(a,axis=0);a=np.where(np.isfinite(a),a,self.med)
        self.mu=a.mean(axis=0);self.sd=a.std(axis=0);self.sd[self.sd<1e-8]=1;return self
    def transform(self,x):
        a=x[self.cols].to_numpy(float);return np.clip((np.where(np.isfinite(a),a,self.med)-self.mu)/self.sd,-5,5)

def own_features(c):
    r=c.pct_change(fill_method=None);rv=r.rolling(21).std()
    return pd.DataFrame({'own_ret1':r,'own_ret5':c.pct_change(5,fill_method=None),'own_ret21':c.pct_change(21,fill_method=None),'own_rv21':rv,'own_trend':c/c.ewm(span=21,adjust=False).mean()-1})

def panel(data,x,stock=False):
    names=[k for k in data if (k.startswith('s_') if stock else k.startswith('nifty_') and k not in ['nifty_spot'])]
    names=[n for n in names if n!='india_vix'];rows=[]
    for name in names:
        c=data[name].close.reindex(x.index).astype(float);f=own_features(c);f['date']=x.index;f['asset']=name
        f['global_state']=x.x_global_mean.to_numpy();f['participation']=x.i_participation.to_numpy()
        for h in [1,3,5,21]:f[f'y{h}']=c.shift(-h)/c-1
        rows.append(f)
    return pd.concat(rows,ignore_index=True)

def transfer_fit(table,dates,h):
    f=table[table.date.isin(dates)].copy();names=[c for c in f if c.startswith('own_')]+['global_state','participation']
    f=f[np.isfinite(f[names+[f'y{h}']]).all(axis=1)&f.own_rv21.gt(.001)&f[f'y{h}'].abs().lt(.5)]
    if len(f)<80:raise ValueError('INSUFFICIENT_DATE_GROUPED_PANEL')
    scale=Scale().fit(f[names]);a=scale.transform(f);target=f[f'y{h}']/(f.own_rv21*np.sqrt(h));weights=1/f.groupby('date').date.transform('size')
    estimator=Ridge(alpha=100).fit(a,target,sample_weight=weights.to_numpy())
    return {'scale':scale,'estimator':estimator,'names':names,'panel_rows':len(f),'panel_dates':f.date.nunique(),'last_panel_date':f.date.max()}

def query_own(x,price):
    own=own_features(price.close).reindex(x.index);own['global_state']=x.x_global_mean;own['participation']=x.i_participation
    return own

def fit(name,x,y,h,context):
    kind,mode,_=SPECS[name];scope(x.index)
    if not np.isfinite(y).all():raise ValueError('UNMATURED_LABEL')
    model={'name':name,'kind':kind,'pool':np.asarray(y)[-252:],'y':np.asarray(y),'train_dates':list(x.index),'h':h,
        'rv_median':float(x.p_rv21.median()),'global_sign':x.x_global_mean.gt(0).to_numpy(),'risk_state':x.p_rv21.to_numpy()}
    if kind=='empirical':return model
    if kind in ['sector_transfer','stock_transfer']:
        model['transfer']=transfer_fit(context['stock_panel' if kind=='stock_transfer' else 'sector_panel'],x.index,h);return model
    names=cols(x,mode);scale=Scale().fit(x[names]);a=scale.transform(x);model['scale']=scale
    if kind in ['pca','rolling_pca']:
        transform=PCA(n_components=min(5,a.shape[1],len(a)),svd_solver='full').fit(a[-126:] if kind=='rolling_pca' else a)
        model['transform']=transform;a=transform.transform(a)
    if kind=='spline':
        transform=SplineTransformer(n_knots=3,degree=2,include_bias=False).fit(a);model['transform']=transform;a=transform.transform(a)
    if kind in ['cosine','manhattan']:model['z']=a;return model
    if kind=='regime':return model
    if kind=='forest':
        estimator=ExtraTreesRegressor(n_estimators=64,max_depth=3,min_samples_leaf=30,max_features=.7,random_state=SEED,n_jobs=1).fit(a,y)
        model['estimator']=estimator;model['train_leaves']=estimator.apply(a);return model
    if kind=='multitask':
        aa=[];yy=[];ww=[];dates=x.index
        for hh in [1,3,5,21]:
            labs=context['labels'][hh];valid=dates[(labs.loc[dates,'endpoint'].notna())&(labs.loc[dates,'endpoint']<context['cutoff'])]
            aa.append(np.column_stack([scale.transform(x.loc[valid]),np.full(len(valid),np.log(hh))]));yy.extend(labs.loc[valid,'return']/np.sqrt(hh));ww.extend([.25]*len(valid))
        model['estimator']=Ridge(alpha=100).fit(np.vstack(aa),yy,sample_weight=ww);return model
    model['estimator']=(KernelRidge(alpha=10,kernel='rbf',gamma=1/max(1,a.shape[1])) if kind=='kernel' else Ridge(alpha=100)).fit(a,y)
    return model

def mean_prediction(model,x,context):
    kind=model['kind'];h=model['h']
    if kind=='empirical':return np.full(len(x),model['pool'].mean())
    if kind in ['sector_transfer','stock_transfer']:
        f=context['own'].loc[x.index];m=model['transfer'];return m['estimator'].predict(m['scale'].transform(f[m['names']]))*f.own_rv21.to_numpy()*np.sqrt(h)
    a=model['scale'].transform(x)
    if 'transform' in model:a=model['transform'].transform(a)
    if kind=='multitask':return model['estimator'].predict(np.column_stack([a,np.full(len(a),np.log(h))]))*np.sqrt(h)
    if kind in ['cosine','manhattan','regime']:return np.full(len(x),model['pool'].mean())
    return model['estimator'].predict(a)

def laws(model,x,context,residuals=None):
    pool=model['pool'];kind=model['kind'];out=[]
    if kind in ['cosine','manhattan','forest']:a=model['scale'].transform(x)
    mu=mean_prediction(model,x,context) if kind not in ['cosine','manhattan','forest','regime'] else None
    for j,(_,row) in enumerate(x.iterrows()):
        if kind=='empirical':law=Distribution(pool)
        elif kind=='regime':
            mask=(model['global_sign']==bool(row.x_global_mean>0))&((model['risk_state']>model['rv_median'])==bool(row.p_rv21>model['rv_median']))
            w=np.ones(len(model['y']))*50/len(model['y'])+mask;law=Distribution(model['y'],w)
        elif kind in ['cosine','manhattan']:
            distance=(cosine_distances(a[j:j+1],model['z'])[0] if kind=='cosine' else manhattan_distances(a[j:j+1],model['z'])[0]/model['z'].shape[1]);ix=np.argsort(distance)[:40]
            w=np.ones(len(model['y']))*.35/len(model['y']);near=1/(distance[ix]+.25);w[ix]+=.65*near/near.sum();law=Distribution(model['y'],w)
        elif kind=='forest':
            leaves=model['estimator'].apply(a[j:j+1])[0];matches=model['train_leaves']==leaves
            w=(matches/np.maximum(1,matches.sum(axis=0))).mean(axis=1);w=.65*w+.35/len(w);law=Distribution(model['y'],w)
        else:
            r=np.asarray(residuals) if residuals is not None and len(residuals)>=20 else model['y']-model['y'].mean()
            atoms=np.r_[np.maximum(mu[j]+r,-.999999),pool];weights=np.r_[np.full(len(r),.65/len(r)),np.full(len(pool),.35/len(pool))];law=Distribution(atoms,weights)
        out.append(law)
    return out
