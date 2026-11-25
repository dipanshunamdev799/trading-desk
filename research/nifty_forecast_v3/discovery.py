"""Development-only information screening; never select on outer outcomes."""
import json
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import ElasticNet,LogisticRegression
from .audit import OUT,save
from .experiment import available
from .models import SEED,Preprocess

def bh(p):
    p=np.asarray(p);order=np.argsort(p);ranked=p[order]*len(p)/np.arange(1,len(p)+1)
    adjusted=np.minimum.accumulate(ranked[::-1])[::-1];out=np.empty(len(p));out[order]=np.minimum(1,adjusted);return out

def main():
    x=pd.read_csv(OUT/'features.csv',index_col=0);allrows=[];univariate=[];stability=[];mi=[]
    for h in [5,21]:
        labels=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0)
        dev=labels.index[labels.endpoint.notna()&(labels.endpoint<'2026-07-01')]
        rng=np.random.default_rng(SEED);group_rows=[]
        for name in x.columns:
            valid=dev[x.loc[dev,name].notna()]
            if len(valid)<60:continue
            a=x.loc[valid,name].to_numpy();y=labels.loc[valid,'return'].to_numpy()
            ra=rankdata(a);ry=rankdata(y)
            if np.std(ra)<1e-10:continue
            observed=float(np.corrcoef(ra,ry)[0,1]);null=[]
            for shift in rng.integers(2*h,max(2*h+1,len(y)-2*h),200):null.append(np.corrcoef(ra,np.roll(ry,shift))[0,1])
            half=len(a)//2
            first=float(spearmanr(a[:half],y[:half]).statistic) if np.std(a[:half])>0 else None
            second=float(spearmanr(a[half:],y[half:]).statistic) if np.std(a[half:])>0 else None
            group_rows.append({'horizon':h,'feature':name,'family':name.split('_')[0],'n':len(valid),
                'rank_ic':observed,'first_half_ic':first,'second_half_ic':second,
                'block_shift_p':float((1+np.sum(np.abs(null)>=abs(observed)))/201),
                'research_only':name.startswith('proxy_')})
        q=bh([r['block_shift_p'] for r in group_rows])
        for r,value in zip(group_rows,q):r['bh_q']=float(value)
        allrows.extend(group_rows)
        # Monthly univariate forecasts, evaluated exclusively in development.
        monthly={}
        for day in dev:
            if len(available(labels,day))>=100:monthly.setdefault(day[:7],[]).append(day)
        for month,query in monthly.items():
            train_idx=available(labels,query[0]);y=(labels.loc[train_idx,'return']>0).to_numpy()
            if len(np.unique(y))<2:continue
            for name in x:
                if x.loc[train_idx,name].notna().sum()<60:continue
                pre=Preprocess().fit(x.loc[train_idx],[name]);a=pre.transform(x.loc[train_idx]);b=pre.transform(x.loc[query])
                clf=LogisticRegression(C=.1,max_iter=1000).fit(a,y);p=clf.predict_proba(b)[:,1]
                actual=(labels.loc[query,'return']>0).to_numpy();base=(y.sum()+1)/(len(y)+2)
                univariate.append({'horizon':h,'month':month,'feature':name,'n':len(query),
                    'brier_sum':float(np.sum((p-actual)**2)),'baseline_brier_sum':float(np.sum((base-actual)**2)),
                    'coefficient':float(clf.coef_[0,0]),'last_train_endpoint':labels.loc[train_idx,'endpoint'].max()})
        representatives=[c for c in ['price_ret21','price_rv21','risk_vix','sector_participation','sector_dispersion',
            'fo_oi_pcr','fo_fut_basis','etf_relative_volume','intraday_efficiency','global_sp500_ret5',
            'institution_fii_futures_position_imbalance','proxy_above_ema21'] if x.loc[dev,c].notna().sum()>=60]
        pre=Preprocess().fit(x.loc[dev],representatives);a=pre.transform(x.loc[dev]);y=labels.loc[dev,'return'].to_numpy()
        observed=mutual_info_regression(a,y,random_state=SEED);null=[]
        for shift in rng.integers(2*h,len(y)-2*h,20):null.append(mutual_info_regression(a,np.roll(y,shift),random_state=SEED))
        for name,value,null_mean in zip(pre.columns,observed,np.mean(null,axis=0)):
            mi.append({'horizon':h,'feature':name,'mi':float(value),'shift_null_mean':float(null_mean),
                'interpretation':'Development diagnostic, no independent significance claim'})
        # Temporal block stability of L1 coefficients, development labels only.
        cols=[c for c in x if not c.startswith(('proxy_','sequence_','interaction_'))]
        pre=Preprocess().fit(x.loc[dev],cols);a=pre.transform(x.loc[dev]);coeff=[]
        for _ in range(30):
            starts=rng.integers(0,len(dev)-2*h+1,int(np.ceil(len(dev)/(2*h))))
            ix=(starts[:,None]+np.arange(2*h)).ravel()[:len(dev)]
            fit=ElasticNet(alpha=.001,l1_ratio=.5,max_iter=10000).fit(a[ix],y[ix]);coeff.append(fit.coef_)
        coeff=np.array(coeff)
        for j,name in enumerate(pre.columns):
            stability.append({'horizon':h,'feature':name,'selected_fraction':float(np.mean(abs(coeff[:,j])>1e-8)),
                'positive_fraction':float(np.mean(coeff[:,j]>1e-8)),'negative_fraction':float(np.mean(coeff[:,j]<-1e-8))})
    pd.DataFrame(allrows).to_csv(OUT/'development-feature-information.csv',index=False)
    pd.DataFrame(univariate).to_csv(OUT/'development-univariate-oos.csv',index=False)
    pd.DataFrame(stability).to_csv(OUT/'development-stability-selection.csv',index=False)
    save('development-mutual-information.json',mi)
    print('Development-only information audit:',len(allrows),'feature/horizon rows;',len(univariate),'univariate folds',flush=True)
if __name__=='__main__':main()
