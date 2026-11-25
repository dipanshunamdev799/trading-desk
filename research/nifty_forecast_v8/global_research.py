"""Target-specific foreign inputs and past-only intermediate forecasts."""
from sklearn.linear_model import Ridge
from .common import *
from .experiments import evaluate, frames, queries, spec
from .models import Scale
from research.nifty_forecast_v3.experiment import available

LINKS={'technology':['NASDAQCOM'],'volatility':['VIXCLS','x_global_vol'],
       'oil_currency':['g_BZUSD_ret5','g_USDINR_ret5','x_oil_fx'],'rates':['DGS10'],
       'asia':['asian_dispersion','g_^HSI_ret5','g_^N225_ret5']}


def run():
    inputs,eligibility=frames();base=inputs['both_changes'];rot=matrix('rotation.csv',OUT)
    glob=matrix('global.csv',OUT);glob['asian_dispersion']=abs(glob['g_^HSI_ret5']-glob['g_^N225_ret5'])
    links={name:cols for name,cols in LINKS.items() if all(c in glob for c in cols)}
    save('global-intermediate-plan.json',{'registered_at':now(),'links':links,'requested':LINKS,
         'targets':'IT relative to NIFTY, future synchrony, defensive-minus-cyclical return, Financial Services relative return, endpoint sector participation.',
         'development':'V3 frozen development origins plus primary. Fit each targeted Ridge model on matured labels only.'})
    close=matrix('sector-returns.csv',V7).reindex(base.index);st=matrix('market-structure.csv',V7)
    rows=[];ledger=[];specs={}
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv')
        panels=(1+close).rolling(h).apply(np.prod,raw=True).shift(-h)-1
        targets={'technology':panels.nifty_it-y['return'],'volatility':st.mean_corr.shift(-h),
                 'oil_currency':panels[['nifty_fmcg','nifty_pharma']].mean(axis=1)-panels[['nifty_auto','nifty_metal','nifty_energy']].mean(axis=1),
                 'rates':panels.nifty_financial-y['return'],'asia':st.participation.shift(-h)}
        state={'technology':base[['i_nifty_it_rel5','i_nifty_it_rel21']], 'volatility':st[['mean_corr','rv_sync']],
               'oil_currency':rot[['r_def','r_def_change']],'rates':rot[['m_financial','r_bank_change']],
               'asia':st[['participation','leader_persistence']]}
        q=pd.concat([queries(h,'early').assign(split='early'),queries(h,'primary').assign(split='primary')],ignore_index=True)
        inc=pd.DataFrame(index=base.index)
        for (split,fold),g in q.groupby(['split','fold']):
            cutoff=g.origin.min();dates=available(y,cutoff)
            for target,cols in links.items():
                label=targets[target];train=dates[label.reindex(dates).notna()];x=pd.concat([base[['p_ret5','p_ret21','p_rv21','p_vix']],state[target]],axis=1)
                if len(train)<70:
                    ledger.append({'horizon':h,'split':split,'fold':fold,'target':target,'status':'unestimated','n':len(train)});continue
                if label.reindex(g.origin).isna().any():g0=g[label.reindex(g.origin).notna().to_numpy()]
                else:g0=g
                preds=[]
                for method,features in [('own',x),('foreign',pd.concat([x,glob[cols]],axis=1))]:
                    scale=Scale().fit(features.loc[train]);model=Ridge(alpha=100).fit(scale.transform(features.loc[train]),label.loc[train])
                    vals=model.predict(scale.transform(features.loc[g0.origin]));preds.append(vals)
                    for r,forecast in zip(g0.itertuples(),vals):
                        rows.append({'horizon':h,'fold':fold,'split':split,'origin':r.origin,'target':target,'method':method,'prediction':forecast,
                                     'realized':label.loc[r.origin],'error':abs(label.loc[r.origin]-forecast),
                                     'high_vol':bool(x.loc[r.origin,'p_rv21']>x.loc[train,'p_rv21'].median()),
                                     'weak_participation':bool(st.loc[r.origin,'participation']<.5)})
                inc.loc[g0.origin,target+'_correction']=preds[1]-preds[0]
                ledger.append({'horizon':h,'split':split,'fold':fold,'target':target,'status':'ok','cutoff':cutoff,
                               'last_endpoint':y.loc[train,'endpoint'].max(),'n':len(train)})
        eligible=f'foreign{h}';eligibility[eligible]=inc.notna().all(axis=1)
        direct=list(dict.fromkeys(c for cols in links.values() for c in cols))
        inputs[f'direct{h}']=pd.concat([base,glob[direct]],axis=1)
        inputs[f'intermediate{h}']=pd.concat([base,inc],axis=1)
        inputs[f'intermediate_gate{h}']=pd.concat([base,inc,inc.mul((st.participation<.5).astype(float),axis=0).add_suffix('_weak')],axis=1)
        inc.to_csv(OUT/f'global-intermediate-features-{h}.csv')
        for name,frame,parent in [('G_MATCH','both_changes','B_ROT'),('G_DIRECT','direct'+str(h),'G_MATCH'),
                                  ('G_MEDIATE','intermediate'+str(h),'G_MATCH'),('G_CONDITIONAL','intermediate_gate'+str(h),'G_MEDIATE')]:
            specs[name+str(h)]=spec(frame,parent+str(h) if parent.startswith('G_') else parent,horizons=[h],eligible=eligible,
                                    hypothesis='Matched origins for narrowly specified direct or intermediate foreign contributions')
    write('global-intermediate-predictions.csv',pd.DataFrame(rows));save('global-intermediate-ledger.json',ledger)
    evaluate('global',specs,inputs,eligibility)


if __name__=='__main__':run()
