"""Native mechanisms and their evolution, no stock-membership proxies."""
import warnings
from .common import *
from .reproduce import frames
from research.nifty_forecast_v3.features import labels_for

def deep_features(data,index):
    requested=index;index=data['nifty_spot'].index
    c=data['nifty_spot'].close.reindex(index);r=c.pct_change(fill_method=None);rv=r.rolling(21).std().clip(lower=.001)
    native=['bank_nifty','nifty_financial','nifty_it','nifty_auto','nifty_metal','nifty_pharma','nifty_fmcg','nifty_energy','idx_Nifty_500'];out=pd.DataFrame(index=index)
    rr={n:data[n].close.reindex(index) for n in native}
    # Registered scales, not a Cartesian product of every indicator and interaction.
    for n in native:
        for h in [1,2,3,5,10,20]:out[f'n_{n}_rel{h}']=(rr[n].pct_change(h,fill_method=None)-c.pct_change(h,fill_method=None))/(rv*np.sqrt(h))
        out[f'n_{n}_rv_ratio']=rr[n].pct_change(fill_method=None).rolling(21).std()/rv
        out[f'n_{n}_drawdown']=rr[n]/rr[n].rolling(21).max()-c/c.rolling(21).max()
    sectors=pd.concat([rr[n].pct_change(fill_method=None) for n in native if n!='idx_Nifty_500'],axis=1);sectors.columns=[n for n in native if n!='idx_Nifty_500']
    out['q_sync']=sectors.gt(0).sum(axis=1)/sectors.notna().sum(axis=1).replace(0,np.nan)
    # Mean correlation from the off-diagonal of the trailing21 sector matrix.
    correlations=[]
    for i in range(len(index)):
        a=sectors.iloc[max(0,i-20):i+1].dropna()
        corr=a.corr().to_numpy();mask=~np.eye(len(corr),dtype=bool)
        correlations.append(float(corr[mask].mean()) if len(a)>=15 and np.isfinite(corr[mask]).all() else np.nan)
    out['q_sector_correlation']=correlations;out['q_corr_jump']=out.q_sector_correlation.diff(5)
    out['q_bank_deceleration']=out.n_bank_nifty_rel3-out.n_bank_nifty_rel10
    out['q_financial_it_rotation']=out.n_nifty_it_rel5-out.n_nifty_financial_rel5
    out['q_broad_deterioration']=out.n_idx_Nifty_500_rel3-out.n_idx_Nifty_500_rel20
    out['q_defensive_rotation']=(out.n_nifty_pharma_rel5+out.n_nifty_fmcg_rel5-out.n_nifty_auto_rel5-out.n_nifty_metal_rel5)/2
    cyc=pd.concat([rr[n].pct_change(5,fill_method=None) for n in ['bank_nifty','nifty_auto','nifty_metal','nifty_energy']],axis=1)
    out['q_cyclical_weakness']=cyc.lt(0).mean(axis=1)
    out['q_dispersion_change']=sectors.rolling(5).sum().std(axis=1).diff(3)
    out['q_banks_warning']=out.n_bank_nifty_rel5.clip(upper=0)*(c.pct_change(5)>0)
    out['q_index_breadth_divergence']=c.pct_change(5)-sectors.rolling(5).sum().mean(axis=1)
    for col in ['q_sync','q_sector_correlation','q_bank_deceleration','q_financial_it_rotation','q_broad_deterioration','q_defensive_rotation']:
        out[col+'_d1']=out[col].diff();out[col+'_d2']=out[col].diff().diff()
        out[col+'_slope5']=(out[col]-out[col].shift(5))/5
    out['q_trend_persistence']=(c.pct_change()>0).rolling(20).mean();out['q_risk_persistence']=(r.abs()>r.abs().shift().rolling(21).median()).rolling(20).mean()
    out['q_defensive_persistence']=out.q_defensive_rotation.gt(0).rolling(20).mean()
    # Transition probability is a causal empirical hazard of observed states, not a latent regime oracle.
    state=(out.q_sync>.5).astype(float);out['q_transition_rate']=state.diff().abs().rolling(63,min_periods=30).mean()
    return out.replace([np.inf,-np.inf],np.nan).reindex(requested)

DYNAMIC_CORE=['q_bank_deceleration','q_broad_deterioration','q_defensive_rotation','q_corr_jump','q_sync_d1','q_sector_correlation_slope5','q_financial_it_rotation_d2','q_cyclical_weakness']
def run():
    x,price,labels,data,f=frames();native=f['I03_nosize'][[c for c in f['I03_nosize'] if c.startswith(('p_','i_'))]]
    with warnings.catch_warnings():warnings.simplefilter('ignore',pd.errors.PerformanceWarning);deep=deep_features(data,x.index)
    native.to_csv(OUT/'native-reference.csv');deep.to_csv(OUT/'deep-features.csv');price.to_csv(OUT/'price.csv')
    x[[c for c in x if c.startswith(('g_','x_'))]].to_csv(OUT/'global-reference.csv')
    for h in [1,3,5,10,15,21]:labels_for(price,h).to_csv(OUT/f'labels-{h}.csv')
    f['L01'][[c for c in f['L01'] if c.startswith(('p_','i_'))]].to_csv(OUT/'liquidity-reference.csv')
    save('feature-definitions.json',[{'feature':c,'family':'native' if c in native else 'dynamic' if c.startswith('q_') else 'multiscale_native','missing_fraction':float((native[c] if c in native else deep[c]).isna().mean()),'scope':'2025–2026; forward-only transforms; no constituent proxies'} for c in list(native)+list(deep)])
    dataset_files=['native-reference.csv','deep-features.csv','liquidity-reference.csv','global-reference.csv','price.csv']+[f'labels-{h}.csv' for h in [1,3,5,10,15,21]]
    save('dataset-manifest.json',{'created_at':now(),'rows':len(native),'first':native.index[0],'last':native.index[-1],'native_features':len(native.columns),'deep_features':len(deep.columns),'files':{name:sha(OUT/name) for name in dataset_files}})
    print('Native/deep matrices',native.shape,deep.shape,flush=True)
if __name__=='__main__':run()
