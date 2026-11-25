"""Compare the annualized risk heads with prior mature, matching V11 risk forecasts."""
from .common import *
from research.nifty_forecast_v8.analyze import intervals
from research.nifty_forecast_v9.run_models import cohort_queries


def run():
    m=pd.read_csv(OUT/'market-predictions.csv',low_memory=False)
    p=pd.read_csv(V11/'all-predictions.csv',low_memory=False)
    p=p[p.path_risk_abs_error.notna()].rename(columns={'path_risk_abs_error':'path_volatility_mae'})
    m=m[m.path_volatility_mae.notna()]
    targets=sorted(m.model.unique())
    refs=sorted(p.model.unique())
    save('legacy-risk-plan.json',{'registered_at':now(),'candidates':targets,'references':refs,
         'disclosure':'Supplemental registered after V12 fits. Includes all stored V11 and V12 risk heads, before computing these cross-version matched gains.'})
    contrasts=[];vectors={}
    for h in [5,21]:
        for c in ['early','later','combined']:
            a=m[m.horizon.eq(h)&(True if c=='combined' else m.cohort.eq(c))]
            b=p[p.horizon.eq(h)&(True if c=='combined' else p.cohort.eq(c))]
            family=[]
            for n,z in a.groupby('model'):
                vv=z.set_index('origin')
                for control,t in b.groupby('model'):
                    bb=t.set_index('origin')
                    common=vv.index.intersection(bb.index).sort_values()
                    aa=vv.loc[common];f=bb.loc[common]
                    if len(aa)<20:continue
                    np.testing.assert_array_equal(aa.endpoint,f.endpoint)
                    np.testing.assert_allclose(aa.realized_path_volatility,f.path_risk_realized,atol=1e-12,rtol=0)
                    gain=f.path_volatility_mae-aa.path_volatility_mae
                    row={'horizon':h,'cohort':c,'model':n,'baseline':control,'n':len(gain),
                         'market_mae':aa.path_volatility_mae.mean(),'V11_mae':f.path_volatility_mae.mean(),'gain':gain.mean()}
                    contrasts.append(row)
                    if h==5 and len(gain)>=35:family.append((row,gain))
            if h==5 and family:
                calendar=cohort_queries(5).query("split==@c").origin.tolist() if c!='combined' else cohort_queries(5).origin.tolist()
                lo,hi,a,b,k=intervals([v for _,v in family],calendar,10)
                for j,(row,_) in enumerate(family):row.update(low10=lo[j],high10=hi[j])
                vectors[c]={'cells':len(family),'critical10':k}
    result=pd.DataFrame(contrasts)
    write('legacy-risk-comparisons.csv',result)
    save('legacy-risk-uncertainty.json',vectors)
    print('Matched',len(result),'V11/V12 annualized risk comparisons',flush=True)


if __name__=='__main__':run()
