"""Date-balanced risk auxiliary model and10/15-session horizon diagnostics."""
import joblib
from scipy.stats import t
from .common import *
from .engine import fit,means,predict,mix,Distribution
from .experiments import datasets
from research.nifty_forecast_v5.data import load as sources
from research.nifty_forecast_v5.models import Scale
from research.nifty_forecast_v3.experiment import available,inner_split
from sklearn.linear_model import Ridge
def run():
    if (OUT/'monthly-plan.json').exists():raise FileExistsError('Monthly study exists')
    save('monthly-plan.json',{'registered_at':now(),'M_RISK_PANEL':'Native-sector date-balanced futureRMS/originRV log-ratio Ridge100, ratio clipped.5–2; shrunk monthly mean and Studentdf5 endpoint law mixed65/35 with historical. Not independent stock-date monthly outcomes.',
        'diagnostic_horizons':[10,15],'common_dates':'Same76 original monthly origins; primary5/21 unchanged',
        'diagnostic_models':['R_I03','H_DYNAMIC_CORE','A_STUDENT','J_EQUAL'],'monthly_independent_windows':4,
        'no_compounded_weekly_probabilities':True,'no_horizon_selection_for_primary':True})
    ds,_,_=datasets();price=pd.read_csv(OUT/'price.csv',index_col=0);deep=pd.read_csv(OUT/'deep-features.csv',index_col=0);labs={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [5,10,15,21]};data,_=sources();x=ds['native'];old=pd.read_csv(V5/'all-predictions.csv');query=old[(old.model=='I03_nosize')&(old.horizon==21)&(old.split=='outer_exposed')]
    table=[]
    for name,f in data.items():
        if not name.startswith('nifty_') or name=='nifty_spot':continue
        close=f.close.reindex(data['nifty_spot'].index);rr=close.pct_change(fill_method=None);rv=rr.rolling(21).std();lr=np.log(close).diff();future=np.sqrt(pd.concat([lr.shift(-i).pow(2) for i in range(1,22)],axis=1).mean(axis=1,skipna=False))
        a=pd.DataFrame({'own_rv':rv.reindex(x.index),'vix_daily':x.p_vix/100/np.sqrt(252),'momentum':close.pct_change(21).reindex(x.index),'sync':deep.q_sync,'correlation':deep.q_sector_correlation,'date':x.index,'asset':name,'target':np.log(future/rv).reindex(x.index)});table.append(a)
    panel=pd.concat(table,ignore_index=True);panel=panel[np.isfinite(panel[['own_rv','vix_daily','momentum','sync','correlation','target']]).all(axis=1)&panel.own_rv.gt(.001)];panel['target']=panel.target.clip(-np.log(3),np.log(3));panel.to_csv(OUT/'risk-panel.csv',index=False)
    columns=['own_rv','vix_daily','momentum','sync','correlation'];rows=[];ledger=[]
    for fold,g in query.groupby('fold'):
        cutoff=g.origin.min();ix=available(labs[21],cutoff);p=panel[panel.date.isin(ix)].copy();s=Scale().fit(p[columns]);weights=1/p.groupby('date').date.transform('size');risk=Ridge(alpha=100).fit(s.transform(p),p.target,sample_weight=weights)
        a=joblib.load(OUT/'models'/f'baseline-h21-{fold}-I03_nosize.joblib');mu=means(a['model'],x.loc[g.origin]);current=pd.DataFrame({'own_rv':x.loc[g.origin,'p_rv21'].to_numpy(),'vix_daily':x.loc[g.origin,'p_vix'].to_numpy()/100/np.sqrt(252),'momentum':x.loc[g.origin,'p_ret21'].to_numpy(),'sync':deep.loc[g.origin,'q_sync'].to_numpy(),'correlation':deep.loc[g.origin,'q_sector_correlation'].to_numpy()})
        ratio=np.clip(np.exp(risk.predict(s.transform(current))),.5,2);pool=a['model']['pool'];sigma=current.own_rv.to_numpy()*np.sqrt(21)*ratio
        for j,r in enumerate(g.itertuples()):
            location=.5*mu[j]+.5*pool.mean();atoms=np.maximum(location+sigma[j]*np.sqrt(3/5)*t.ppf((np.arange(401)+.5)/401,df=5),-.999999);d=Distribution(np.r_[atoms,pool],np.r_[np.full(len(atoms),.65/len(atoms)),np.full(len(pool),.35/len(pool))])
            rvpred=float(current.own_rv.iloc[j]*ratio[j]*np.sqrt(252));actual=float(labs[21].loc[r.origin,'volatility']);rr=(actual/max(rvpred,.001))**2
            rows.append({'horizon':21,'fold':fold,'model':'M_RISK_PANEL','origin':r.origin,'endpoint':r.endpoint,'regime':r.regime,'trend':r.trend,'global_risk':r.global_risk,'aux_predicted_rv_annual':rvpred,'aux_actual_rv_annual':actual,'aux_rv_mae':abs(rvpred-actual),'aux_qlike':float(rr-np.log(rr)-1),**d.score(r.realized_return)})
        path=OUT/'models'/f'h21-{fold}-M_RISK_PANEL.joblib';joblib.dump({'risk':risk,'scale':s,'mean_parent':a,'ratio_clip':[.5,2],'cutoff':cutoff},path,compress=3);ledger.append({'horizon':21,'fold':fold,'model':'M_RISK_PANEL','status':'ok','cutoff':cutoff,'last_endpoint':str(labs[21].loc[ix,'endpoint'].max()),'panel_rows':len(p),'panel_dates':p.date.nunique(),'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
    pd.DataFrame(rows).to_csv(OUT/'monthly-risk-predictions.csv',index=False)
    # Intermediate horizons: common dates, same causal fit machinery, no change to primary tasks.
    diagnostic=[]
    for h in [10,15]:
        for fold,g in query.groupby('fold'):
            cutoff=g.origin.min();ix=available(labs[h],cutoff);ii,vv=inner_split(labs[h],ix);fitted={}
            for name,xx,spec in [('R_I03',x,{'kind':'ridge'}),('H_DYNAMIC_CORE',ds['dynamic_core'],{'kind':'ridge'}),('A_STUDENT',x,{'kind':'ridge','law':'student'}),('R_L01',pd.read_csv(OUT/'liquidity-reference.csv',index_col=0),{'kind':'ridge'})]:
                inner=fit(spec,xx.loc[ii],labs[h],vv[0]);res=labs[h].loc[vv,'return'].to_numpy()-means(inner,xx.loc[vv]);model=fit(spec,xx.loc[ix],labs[h],cutoff);fitted[name]=predict(model,xx.loc[g.origin],res)
                path=OUT/'models'/f'intermediate-h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'cutoff':cutoff},path,compress=3);ledger.append({'horizon':h,'fold':fold,'model':name,'status':'ok','cutoff':cutoff,'last_endpoint':str(labs[h].loc[ix,'endpoint'].max()),'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
            baseline=Distribution(labs[h].loc[ix[-252:],'return'].to_numpy())
            for j,r in enumerate(g.itertuples()):
                yy=float(labs[h].loc[r.origin,'return']);base=baseline.score(yy)
                choices={name:ds[j] for name,ds in fitted.items() if name!='R_L01'};choices['J_EQUAL']=mix(fitted['R_I03'][j],fitted['R_L01'][j],.5)
                for name,d in choices.items():diagnostic.append({'horizon':h,'fold':fold,'model':name,'origin':r.origin,'endpoint':labs[h].loc[r.origin,'endpoint'],'baseline_brier':base['brier'],'baseline_crps':base['crps'],**d.score(yy)})
            print('Intermediate diagnostic',h,fold,flush=True)
    pd.DataFrame(diagnostic).to_csv(OUT/'intermediate-horizon-predictions.csv',index=False);save('monthly-ledger.json',ledger)
    print('Monthly risk and10/15-session diagnostics complete',flush=True)
if __name__=='__main__':run()
