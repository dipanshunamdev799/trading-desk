"""Small fixed model batch; direct targets and native return distributions."""
from __future__ import annotations
import warnings
import numpy as np
import lightgbm as lgb
from sklearn.linear_model import Ridge,ElasticNet,LogisticRegression

SEED=20261117
SPECS=[
 ('B00_empirical','empirical','price',{}),('B01_ewma','ewma','price',{}),
 ('B02_rv_scaled','rv_scaled','price',{}),('B03_vix_scaled','vix_scaled','price',{}),
 ('B04_momentum','momentum','price',{}),('B05_reversion','reversion','price',{}),('B06_regime','regime','price',{}),
 ('M00_ridge_price','ridge','price',{'alpha':100}),('M01_ridge_full','ridge','full',{'alpha':100}),
 ('M02_elastic001','elastic','full',{'alpha':.001}),('M03_elastic01','elastic','full',{'alpha':.01}),
 ('M04_corr_ridge','ridge','pruned',{'alpha':100}),('M05_lgbm','lgbm','full',{}),
 ('M06_analog30','analogue','full',{}),('M07_sequence','ridge','sequence',{'alpha':100}),
 ('A00_sector','ridge','sector',{'alpha':100}),('A01_nofo','ridge','nofo',{'alpha':100}),
 ('A02_proxy','ridge','proxy',{'alpha':100}),('A03_interact','ridge','interaction',{'alpha':100})]
SPECS={name:{'id':name,'kind':kind,'features':features,'parameters':p,'research_only':features=='proxy'} for name,kind,features,p in SPECS}
QUANTILES=np.array([.05,.1,.25,.5,.75,.9,.95])
PROBS=(np.arange(201)+.5)/201

def columns(x,spec):
    ordinary=[c for c in x if not c.startswith(('proxy_','sequence_','interaction_'))]
    mode=spec['features']
    if mode=='price':return [c for c in x if c.startswith('price_')]
    if mode=='sector':return [c for c in x if c.startswith(('price_','sector_'))]
    if mode=='nofo':return [c for c in ordinary if not c.startswith(('fo_','institution_'))]
    if mode=='sequence':return [c for c in x if c.startswith(('price_','sequence_'))]
    if mode=='proxy':return ordinary+[c for c in x if c.startswith('proxy_')]
    if mode=='interaction':return ordinary+[c for c in x if c.startswith('interaction_')]
    return ordinary

class Preprocess:
    def fit(self,x,columns_,prune=False):
        self.columns=[c for c in columns_ if x[c].notna().sum()>=30]
        a=x[self.columns].to_numpy(float)
        self.median=np.array([np.median(c[np.isfinite(c)]) if np.isfinite(c).any() else 0 for c in a.T])
        filled=np.where(np.isfinite(a),a,self.median);self.mean=filled.mean(axis=0);self.std=filled.std(axis=0)
        self.std[self.std<1e-8]=1
        self.keep=np.arange(len(self.columns))
        if prune and len(self.keep):
            z=(filled-self.mean)/self.std
            with np.errstate(divide='ignore',invalid='ignore'):corr=np.nan_to_num(np.corrcoef(z,rowvar=False))
            selected=[]
            for j in range(len(self.columns)):
                if not selected or np.max(np.abs(corr[j,selected]))<.9:selected.append(j)
            self.keep=np.array(selected,dtype=int)
        return self
    def transform(self,x):
        a=x[self.columns].to_numpy(float);missing=~np.isfinite(a)
        z=np.clip((np.where(missing,self.median,a)-self.mean)/self.std,-5,5)
        # No missingness-date indicators: avoid learning provider launch dates.
        return z[:,self.keep]

def empirical_sample(values,weights=None):
    v=np.asarray(values,float);order=np.argsort(v);v=v[order]
    w=np.ones(len(v)) if weights is None else np.asarray(weights)[order]
    cum=np.cumsum(w)/np.sum(w)
    return v[np.minimum(np.searchsorted(cum,PROBS),len(v)-1)]

def fit_classifier(a,y,elastic=False):
    if len(np.unique(y))<2:return float((y.sum()+1)/(len(y)+2))
    model=LogisticRegression(C=.1,solver='saga' if elastic else 'lbfgs',l1_ratio=.5 if elastic else 0,
        max_iter=3000,random_state=SEED)
    model.fit(a,y.astype(int));return model

def classifier_predict(model,a):
    return np.full(len(a),model) if isinstance(model,float) else model.predict_proba(a)[:,1]

def tree(a,y,objective='regression',alpha=None):
    params={'objective':objective,'verbosity':-1,'num_leaves':4,'max_depth':2,'min_data_in_leaf':40,
        'learning_rate':.04,'lambda_l2':10.,'num_threads':1,'deterministic':True,'force_col_wise':True,'seed':SEED}
    if alpha is not None:params['alpha']=alpha
    return lgb.train(params,lgb.Dataset(a,label=y),num_boost_round=80)

def train(spec,x,labels):
    kind=spec['kind']
    if kind in ['empirical','ewma','rv_scaled','vix_scaled','momentum','reversion','regime']:
        x=x.tail(252);labels=labels.loc[x.index]
    y=labels['return'].to_numpy(float);rv=labels.volatility.to_numpy(float)
    model={'spec':spec,'y':y,'vol':rv,'tail02':labels.path_loss.lt(-.02).to_numpy(float),
        'tail05':labels.path_loss.lt(-.05).to_numpy(float),'x':x.copy(),
        'risk_median':float(x.price_rv21.median()),'rv_origin':x.price_rv21.to_numpy(float)}
    if kind in ['empirical','ewma','rv_scaled','vix_scaled','momentum','reversion','regime']:return model
    pre=Preprocess().fit(x,columns(x,spec),spec['features']=='pruned');a=pre.transform(x);model['pre']=pre
    if kind=='analogue':model['z']=a;return model
    if kind=='lgbm':
        model['mean_model']=tree(a,y);model['quantile_models']=[tree(a,y,'quantile',q) for q in QUANTILES]
        model['direction_model']=tree(a,(y>0).astype(float),'binary') if len(np.unique(y>0))>1 else float(np.mean(y>0))
        model['vol_model']=tree(a,rv)
        for key in ['tail02','tail05']:
            target=model[key];model[key+'_model']=tree(a,target,'binary') if len(np.unique(target))>1 else float(np.mean(target))
    else:
        model['mean_model']=(ElasticNet(alpha=spec['parameters']['alpha'],l1_ratio=.5,max_iter=10000,random_state=SEED)
                             if kind=='elastic' else Ridge(alpha=spec['parameters']['alpha'])).fit(a,y)
        model['direction_model']=fit_classifier(a,(y>0).astype(float),kind=='elastic')
        model['vol_model']=Ridge(alpha=100).fit(a,rv)
        for key in ['tail02','tail05']:model[key+'_model']=fit_classifier(a,model[key])
    return model

def predict(model,x,residuals=None):
    spec=model['spec'];kind=spec['kind'];y=model['y'];n=len(y);output=[]
    a=model['pre'].transform(x) if 'pre' in model else None
    if kind not in ['empirical','ewma','rv_scaled','vix_scaled','momentum','reversion','regime','analogue']:
        means=model['mean_model'].predict(a)
        p=(model['direction_model'].predict(a) if kind=='lgbm' and not isinstance(model['direction_model'],float)
           else classifier_predict(model['direction_model'],a))
        volatility=np.maximum(.02,model['vol_model'].predict(a))
        tails={key:(model[key+'_model'].predict(a) if kind=='lgbm' and not isinstance(model[key+'_model'],float)
                     else classifier_predict(model[key+'_model'],a)) for key in ['tail02','tail05']}
        if kind=='lgbm':qraw=np.column_stack([m.predict(a) for m in model['quantile_models']])
    for j,(_,row) in enumerate(x.iterrows()):
        weights=np.ones(n)
        if kind=='ewma':weights=np.exp2((np.arange(n)-(n-1))/63)
        if kind in ['momentum','reversion','regime']:
            trainx=model['x']
            if kind=='momentum':mask=(trainx.price_ret21>0).to_numpy()==(row.price_ret21>0)
            elif kind=='reversion':mask=(trainx.price_ret5>0).to_numpy()!=(row.price_ret5>0)
            else:mask=((trainx.price_ret21>0).to_numpy()==(row.price_ret21>0))&((trainx.price_rv21>model['risk_median']).to_numpy()==(row.price_rv21>model['risk_median']))
            weights=np.ones(n)*30/n
            if mask.any():weights+=mask.astype(float)
        if kind=='analogue':
            distance=np.mean((model['z']-a[j])**2,axis=1);nearest=np.argsort(distance)[:30]
            weights=np.ones(n)*30/n;extra=1/(np.sqrt(distance[nearest])+.25);extra*=30/extra.sum();weights[nearest]+=extra
        weights/=weights.sum()
        if kind in ['empirical','ewma','momentum','reversion','regime','analogue']:
            sample=empirical_sample(y,weights);mean=float(np.dot(weights,y));prob=float(np.dot(weights,y>0))
            vol=float(np.dot(weights,model['vol']));tail02=float(np.dot(weights,model['tail02']));tail05=float(np.dot(weights,model['tail05']));crossings=0
        elif kind in ['rv_scaled','vix_scaled']:
            scale=(row.price_rv21 if kind=='rv_scaled' else row.risk_vix/100/np.sqrt(252))/np.maximum(.001,model['rv_origin'])
            scaled=y*np.clip(scale,.5,2);sample=empirical_sample(scaled)
            mean=float(scaled.mean());prob=float(np.mean(scaled>0));vol=float(row.price_rv21*np.sqrt(252) if kind=='rv_scaled' else row.risk_vix/100)
            tail02=float(np.mean(model['tail02']));tail05=float(np.mean(model['tail05']));crossings=0
        else:
            mean=float(means[j]);prob=float(p[j]);vol=float(volatility[j]);tail02=float(tails['tail02'][j]);tail05=float(tails['tail05'][j])
            if kind=='lgbm':
                quant=qraw[j];crossings=int(np.sum(np.diff(quant)<0));quant=np.sort(quant)
                sample=np.interp(PROBS,QUANTILES,quant)
                # Explicit extrapolation beyond directly fitted 5/95 percentiles.
                sample[PROBS<.05]=quant[0]+(PROBS[PROBS<.05]-.05)*(quant[1]-quant[0])/.05
                sample[PROBS>.95]=quant[-1]+(PROBS[PROBS>.95]-.95)*(quant[-1]-quant[-2])/.05
            else:
                # Residuals come from an earlier purged inner validation fit.
                pool=np.asarray(residuals) if residuals is not None and len(residuals)>=20 else y-y.mean()
                sample=mean+empirical_sample(pool);crossings=0
        output.append({'p':float(np.clip(prob,.02,.98)),'mean':mean,'vol':max(.001,vol),
            'tail02':float(np.clip(tail02,.001,.999)),'tail05':float(np.clip(tail05,.001,.999)),
            'samples':sample,'crossings':crossings})
    return output
