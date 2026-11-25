"""Finite endpoint distributions: every statistic uses the same weighted atoms."""
import numpy as np
from scipy.stats import t
from .common import *
from research.nifty_forecast_v3.models import train,predict,SPECS

BUCKETS=np.array([-.05,-.02,-.005,.005,.02,.05])
class Distribution:
    def __init__(self,atoms,weights=None):
        a=np.asarray(atoms,float);w=np.ones(len(a)) if weights is None else np.asarray(weights,float)
        if not len(a) or not np.isfinite(a).all() or (a<=-1).any() or not np.isfinite(w).all() or (w<0).any() or w.sum()<=0:raise ValueError('INVALID_DISTRIBUTION')
        order=np.argsort(a);self.a=a[order];self.w=w[order]/w.sum()
    def quantile(self,q):return self.a[np.minimum(np.searchsorted(np.cumsum(self.w),q,side='left'),len(self.a)-1)]
    def stats(self,reference=1.):
        a,w=self.a,self.w;p=float(w[a>0].sum());mean=float(w@a);q=self.quantile(np.array([.05,.1,.25,.5,.75,.9,.95]))
        buckets=np.bincount(np.digitize(a,BUCKETS),weights=w,minlength=7)
        return {'p_up':p,'p_nonpositive':1-p,'mean_return':mean,'median_return':float(q[3]),
            'quantiles':dict(zip(['q05','q10','q25','q50','q75','q90','q95'],map(float,q))),
            'buckets':buckets.tolist(),'expected_endpoint':reference*(1+mean),'median_endpoint':reference*(1+float(q[3])),
            'interval50':(reference*(1+q[[2,4]])).tolist(),'interval80':(reference*(1+q[[1,5]])).tolist(),
            'expected_absolute_return':float(w@abs(a)),'endpoint_return_std':float(np.sqrt(w@((a-mean)**2))),
            'path_breach_probability':None,'future_realized_volatility':None,
            'path_note':'UNAVAILABLE: endpoint-only law does not identify paths or future realized volatility'}
    def score(self,y):
        s=self.stats();p=s['p_up'];yc=int(y>0);pc=float(np.clip(p,1e-6,1-1e-6))
        q=self.quantile(np.array([.1,.25,.5,.75,.9]));levels=np.array([.1,.25,.5,.75,.9]);truth=np.zeros(7);truth[np.digitize(y,BUCKETS)]=1
        crps=float(self.w@abs(self.a-y)-np.sum(self.w*self.a*(2*np.cumsum(self.w)-self.w-1)))
        return {'p':p,'outcome':yc,'realized_return':float(y),'predicted_mean':s['mean_return'],'predicted_median':s['median_return'],
            'brier':(p-yc)**2,'log_loss':-yc*np.log(pc)-(1-yc)*np.log(1-pc),'mae':abs(s['mean_return']-y),
            'squared_error':(s['mean_return']-y)**2,'median_mae':abs(s['median_return']-y),'crps':crps,
            'pinball':float(np.mean(np.maximum(levels*(y-q),(levels-1)*(y-q)))),
            'bucket_brier':float(np.sum((np.array(s['buckets'])-truth)**2)),
            'coverage50':int(q[1]<=y<=q[3]),'coverage80':int(q[0]<=y<=q[4]),'width50':float(q[3]-q[1]),'width80':float(q[4]-q[0]),
            **{f'bucket{i}_p':v for i,v in enumerate(s['buckets'])},'bucket_y':int(np.digitize(y,BUCKETS))}

def prepare(x,labels,training,innerfit,innerval):
    full=train(SPECS['A00_sector'],x.loc[training],labels.loc[training])
    inner=train(SPECS['A00_sector'],x.loc[innerfit],labels.loc[innerfit])
    residual=labels.loc[innerval,'return'].to_numpy()-np.array([p['mean'] for p in predict(inner,x.loc[innerval])])
    pool=labels.loc[training[-252:],'return'].to_numpy()
    return {'full':full,'residual':residual,'pool':pool,'trainx':x.loc[training[-252:]],'rv_median':float(x.loc[training[-252:],'price_rv21'].median())}

def forecast(context,row,h):
    y=context['pool'];n=len(y);x=context['trainx'];res=context['residual']
    mask=(x.price_ret21.gt(0).to_numpy()==bool(row.price_ret21>0))&(x.price_rv21.gt(context['rv_median']).to_numpy()==bool(row.price_rv21>context['rv_median']))
    weights=np.full(n,30/n)+mask.astype(float)
    mu=.5*predict(context['full'],row.to_frame().T)[0]['mean']+.5*float(y.mean())
    scale=max(float(np.sqrt(np.mean(res**2))),.005*np.sqrt(h/5))*np.sqrt(3/5)
    atoms=mu+scale*t.ppf((np.arange(501)+.5)/501,df=5)
    return {'D00_empirical':Distribution(y),'D01_regime_shrunk':Distribution(y,weights),
        'D02_student_shrunk':Distribution(np.maximum(atoms,-.999999)),
        'D03_residual_shrunk':Distribution(np.maximum(mu+res,-.999999))}

def summarize(g):
    result={'n':len(g),'accuracy':float(((g.p>=.5)==g.outcome).mean()),'rmse':float(np.sqrt(g.squared_error.mean()))}
    for c in ['brier','log_loss','mae','median_mae','crps','pinball','bucket_brier','coverage50','coverage80','width50','width80']:result[c]=float(g[c].mean())
    result['bucket_calibration']=[{'bucket':i,'predicted':float(g[f'bucket{i}_p'].mean()),'observed':float((g.bucket_y==i).mean())} for i in range(7)]
    return result

def run():
    if (OUT/'distribution-predictions.csv').exists():raise FileExistsError('Do not overwrite a completed study')
    read('registry.json');x,labels,v3=load();records=[];fits=[]
    from research.nifty_forecast_v3.experiment import available,inner_split,nonoverlap
    # Identical prequential origins and monthly boundaries, including development.
    for h in [5,21]:
        origins=v3[(v3.horizon==h)&(v3.model=='B00_empirical')]
        for fold,g in origins.groupby('fold'):
            training=available(labels[h],g.origin.min());innerfit,innerval=inner_split(labels[h],training)
            context=prepare(x,labels[h],training,innerfit,innerval)
            fits.append({'horizon':h,'fold':fold,'last_training_endpoint':str(labels[h].loc[training,'endpoint'].max()),'query_first':g.origin.min(),'inner_first':innerval[0],'inner_fit_last_endpoint':str(labels[h].loc[innerfit,'endpoint'].max()),'residual_count':len(context['residual'])})
            for r in g.itertuples():
                for name,d in forecast(context,x.loc[r.origin],h).items():
                    records.append({'horizon':h,'fold':fold,'origin':r.origin,'endpoint':r.endpoint,'split':r.split,'model':name,**d.score(r.realized_return)})
            print('Coherent distributions',h,fold,flush=True)
    frame=pd.DataFrame(records);frame.to_csv(OUT/'distribution-predictions.csv',index=False)
    metrics=[]
    for (h,split,name),g in frame.groupby(['horizon','split','model']):metrics.append({'horizon':int(h),'split':split,'model':name,**summarize(g),'disjoint':summarize(nonoverlap(g))})
    save('distribution-metrics.json',metrics);save('distribution-fit-ledger.json',fits)
    print('Saved coherent endpoint records',len(frame),flush=True)
if __name__=='__main__':run()
