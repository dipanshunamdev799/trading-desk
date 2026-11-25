"""Development-only cross-market lead/lag and noncausal information diagnostics."""
from scipy.stats import rankdata
from .common import *
from .data import load

def bh(p):
    p=np.asarray(p);o=np.argsort(p);ranked=p[o]*len(p)/np.arange(1,len(p)+1);q=np.minimum.accumulate(ranked[::-1])[::-1];out=np.empty(len(p));out[o]=np.minimum(q,1);return out
def run():
    x=pd.read_csv(OUT/'features.csv',index_col=0);data,_=load();records=[]
    names=[c for c in x if c.startswith(('g_','x_','b_'))]
    save('lead-lag-plan.json',{'registered_at':now(),'features':names,'lags':[0,1,3,5],'targets':['NIFTY5','NIFTY21','IT5','IT21'],'development_endpoint_cutoff':'2026-07-01','null':'200 circular shifts with separation>=2H; BH across all tests; no causation claim','no_test_selection':True})
    for h in [5,21]:
        labs=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0);ix=labs.index[labs.endpoint.notna()&(labs.endpoint<'2026-07-01')]
        for target in ['NIFTY','IT']:
            y=labs['return'] if target=='NIFTY' else data['nifty_it'].close.reindex(x.index).shift(-h)/data['nifty_it'].close.reindex(x.index)-1
            for name in names:
                for lag in [0,1,3,5]:
                    xx=x[name].shift(lag).reindex(ix);yy=y.reindex(ix);m=xx.notna()&yy.notna();a=xx[m].to_numpy();b=yy[m].to_numpy();n=len(a)
                    if n<100 or np.std(a)<1e-10:continue
                    ar=rankdata(a);br=rankdata(b);ar=(ar-ar.mean())/ar.std();br=(br-br.mean())/br.std();ic=float(ar@br/n)
                    rng=np.random.default_rng(SEED);shifts=rng.integers(2*h,n-2*h,200);null=np.array([ar@np.roll(br,int(s))/n for s in shifts]);p=float((1+np.sum(abs(null)>=abs(ic)))/201)
                    half=n//2
                    corr=lambda u,v:float(np.corrcoef(rankdata(u),rankdata(v))[0,1])
                    records.append({'horizon':h,'target':target,'feature':name,'lag':lag,'n':n,'rank_ic':ic,'first_half_ic':corr(a[:half],b[:half]),'second_half_ic':corr(a[half:],b[half:]),'p_shift':p,'causation':False})
    frame=pd.DataFrame(records);frame['bh_q']=bh(frame.p_shift);frame.to_csv(OUT/'global-lead-lag-discovery.csv',index=False)
    # Rolling correlations and factor relationships already causal features; no significance from visual similarity.
    save('discovery-summary.json',{'tests':len(frame),'min_bh_q':float(frame.bh_q.min()),'q_under_05':int((frame.bh_q<.05).sum()),'top':frame.sort_values('bh_q').head(20).to_dict('records')})
    print('Global-to-NIFTY/IT lead-lag tests',len(frame),'minq',frame.bh_q.min(),flush=True)
if __name__=='__main__':run()
