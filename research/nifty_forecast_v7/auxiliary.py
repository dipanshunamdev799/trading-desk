"""Matched tests of targeted global links and state-change risk forecasts."""
from sklearn.linear_model import Ridge
from research.nifty_forecast_v5.models import Scale
from .common import *
from .experiments import all_frames, evaluate, spec
from research.nifty_forecast_v6.common import V3
from research.nifty_forecast_v3.experiment import available


LINKS = {
    'it': ['g_IXIX_ret1','g_IXIX_ret5'],
    'energy': ['g_BZUSD_ret5','g_USDINR_ret5','x_oil_fx'],
    'synchrony': ['x_global_vol','x_global_dispersion'],
    'breadth': ['g_^HSI_ret5','g_^N225_ret5','asia_dispersion'],
    'magnitude': ['x_global_vol','x_global_dispersion'],
    'volatility': ['x_global_vol','x_global_dispersion'],
    'large_move': ['x_global_dispersion','x_global_mean'],
}


def forecasts(base,extra,dates,query,y):
    x=pd.concat([base,extra],axis=1)
    scale=Scale().fit(x.loc[dates]);model=Ridge(alpha=100).fit(scale.transform(x.loc[dates]),y.loc[dates])
    return model.predict(scale.transform(x.loc[query]))


def run():
    frames,eligible=all_frames();x=frames['native'];index=x.index;struct=matrix('market-structure.csv',OUT)
    save('auxiliary-plan.json',{'registered_at':now(),'links':LINKS,'fixed_gates':'high-correlation state >.60, high volatility threshold based on median training p_rv21',
          'protocol':'First fit own-state vs targeted global inputs for each intermediate. Downstream receives reconstructed incremental forecasts. Dynamics vs identical levels separately tested for magnitude, volatility and large moves.',
          'target_definition':'IT and energy future relative 5/21-session changes. Breadth/correlation at horizon endpoint. Magnitude |endpoint return|. Volatility annualized RMS of realized path. Large move |endpoint return| exceeds 2% weekly or 4% monthly.'})
    globe=matrix('global-reference.csv');globe['asia_dispersion']=abs(globe['g_^HSI_ret5']-globe['g_^N225_ret5'])
    base=x[['p_ret5','p_ret21','p_rv21','p_vix']]
    momentum=matrix('sector-momentum5.csv',OUT);sec=matrix('sector-returns.csv',OUT)
    skill=[];ledgers=[];preq_store=[];intermediate_data={}
    old=pd.read_csv(V3/'predictions.csv');old=old[old.model=='B00_empirical']
    for h in [5,21]:
        label=matrix(f'labels-{h}.csv');queries=old[(old.horizon==h)&(old.split.isin(['outer_exposed','development_exposed']))]
        targets={'it': (1+sec.nifty_it).rolling(h).apply(np.prod,raw=True).shift(-h)-1-label['return'],
                 'energy':(1+sec.nifty_energy).rolling(h).apply(np.prod,raw=True).shift(-h)-1-label['return'],
                 'synchrony':struct.mean_corr.shift(-h), 'breadth':struct.participation.shift(-h),
                 'magnitude':label.absolute_return,'volatility':label.volatility,
                 'large_move':label.absolute_return.gt(.02 if h==5 else .04).astype(float).where(label['return'].notna())}
        optional={'it':momentum[['nifty_it']], 'energy':momentum[['nifty_energy']],
                  'synchrony':struct[['mean_corr','corr_dispersion','rv_sync']], 'breadth':struct[['participation','leader_persistence','breadth_relative']],
                  'magnitude':struct[['mean_corr','lambda_share','rv_sync','participation']],
                  'volatility':struct[['mean_corr','lambda_share','rv_sync','participation']],
                  'large_move':struct[['mean_corr','lambda_share','rv_sync','participation']]}
        increment=pd.DataFrame(index=index)
        for fold,group in queries.groupby('fold'):
            cutoff=group.origin.min();dates=available(label,cutoff)
            for target,y in targets.items():
                train=dates[y.loc[dates].notna()]; q=group.origin
                if len(train)<70:continue
                own=pd.concat([base,optional[target].reindex(index)],axis=1)
                global_input=globe[LINKS[target]]
                plain=forecasts(own,pd.DataFrame(index=index),train,q,y)
                plus=forecasts(own,global_input,train,q,y)
                for campaign, values in [('BASE',plain),('GLOBAL',plus)]:
                    for r,pred in zip(group.itertuples(),values):
                        preq_store.append({'horizon':h,'fold':fold,'origin':r.origin,'endpoint':r.endpoint,'split':r.split,'target':target,'method':campaign,'prediction':pred,
                                           'actual':y.loc[r.origin],'high_correlation':bool(struct.loc[r.origin,'mean_corr']>.60),
                                           'high_volatility':bool(base.loc[r.origin,'p_rv21']>base.loc[train,'p_rv21'].median())})
                if target in ['it','energy','synchrony','breadth']:
                    increment.loc[q,f'{target}_increment']=plus-plain
                if target in ['magnitude','volatility','large_move'] and (group.split=='outer_exposed').all():
                    columns=list(optional[target]);delta=struct[[c+'_change5' for c in columns]]
                    dynamic=forecasts(own,delta,train,q,y)
                    for campaign,values in [('LEVEL',plain),('CHANGE',dynamic)]:
                        for r,pred in zip(group.itertuples(),values):
                            if target=='large_move':pred=np.clip(pred,0,1)
                            skill.append({'horizon':h,'fold':fold,'origin':r.origin,'target':target,'method':campaign,
                                          'actual':y.loc[r.origin],'prediction':pred})
                ledgers.append({'horizon':h,'fold':fold,'target':target,'cutoff':cutoff,'last_endpoint':label.loc[train,'endpoint'].max(),'n':len(train)})
        intermediate_data[h]=increment
        increment.to_csv(OUT/f'global-intermediate-{h}.csv')
    pd.DataFrame(preq_store).to_csv(OUT/'auxiliary-global-predictions.csv',index=False)
    pd.DataFrame(skill).to_csv(OUT/'state-risk-predictions.csv',index=False)
    save('auxiliary-ledger.json',ledgers)
    print('Evaluated intermediate targets on',len(preq_store),'historical prediction rows',flush=True)
    # Same origin and availability controls for fixed sparse direct and intermediate inputs.
    direct=['g_IXIX_ret5','g_BZUSD_ret5','g_USDINR_ret5','x_global_vol','asia_dispersion']
    specs={}
    for h,inc in intermediate_data.items():
        matched=f'global{h}';own=frames['nodef']
        eligible[matched]=inc.notna().all(axis=1)
        frames[f'{matched}_direct']=pd.concat([own,globe[direct]],axis=1)
        conditional=inc.assign(corr_it=inc.it_increment*(struct.mean_corr>.60),corr_vol=inc.synchrony_increment*(struct.mean_corr>.60))
        frames[f'{matched}_mediated']=pd.concat([own,conditional],axis=1)
        for name,frame,parent in [(f'G_BASE{h}','nodef','C_NO_DEF'),(f'G_DIRECT{h}',f'{matched}_direct',f'G_BASE{h}'),
                                  (f'G_INTERMEDIATE{h}',f'{matched}_mediated',f'G_BASE{h}')]:
            specs[name]=spec(parent,frame,eligible=matched,horizons=[h],hypothesis='Compare targeted cross-market information on the exact intermediate-eligible cohorts')
    evaluate('global',specs,frames,eligible)


if __name__=='__main__':
    run()
