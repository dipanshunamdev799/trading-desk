"""Registered weekly defensive/volume combinations and monthly falsification."""
import joblib
from .common import *
from .engine import fit,means,predict
from .forensics import GROUPS
from .experiments import SMALL
from research.nifty_forecast_v3.experiment import available,inner_split
def run():
    if (OUT/'followup-registry.json').exists():raise FileExistsError('Follow-up already exists')
    save('followup-registry.json',{'registered_at':now(),'weekly_motivation':'Forensic removal of influential defensive columns improved exposed Brier; test fixed group compression/normalization and combinations with actual ETF volume, not arbitrary coefficient tuning.',
        'systems':{'W2_NODEF_VOLUME':'I03 minus defensive column family plus5ETF volume ratios','W2_NOAUTO_VOLUME':'I03 minus training-selected auto21 feature plus5ETF volumes','W2_DEF_PC':'Train-only whitened1PC of six defensive columns, retain other native features','W2_DEF_NORM':'Scale standardized defensive group by1/sqrt(group_size), fixed Ridge100'},
        'monthly_nulls':{'state_block_shifts':[5,21,42],'target_block_shifts':[21,42,63]},'nulls_not_candidates':True,'status':'Newly registered exposed-data follow-up; no independent confirmation'})
    native=pd.read_csv(OUT/'native-reference.csv',index_col=0);liq=pd.read_csv(OUT/'liquidity-reference.csv',index_col=0);vol=liq[[c for c in liq if c.endswith('_volume')]];labels={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [5,21]};old=pd.read_csv(V5/'all-predictions.csv');query=old[(old.horizon==5)&(old.model=='I03_nosize')&(old.split=='outer_exposed')]
    frames={'W2_NODEF_VOLUME':pd.concat([native.drop(columns=[c for c in native if GROUPS['DEFENSIVE'](c)]),vol],axis=1),
        'W2_NOAUTO_VOLUME':pd.concat([native.drop(columns=['i_nifty_auto_rel21']),vol],axis=1),'W2_DEF_PC':native,'W2_DEF_NORM':native}
    records=[];ledger=[]
    for fold,g in query.groupby('fold'):
        cutoff=g.origin.min();ix=available(labels[5],cutoff);ii,vv=inner_split(labels[5],ix)
        for name,x in frames.items():
            spec={'kind':'ridge','defensive_pc':name=='W2_DEF_PC','defensive_norm':name=='W2_DEF_NORM'};inner=fit(spec,x.loc[ii],labels[5],vv[0]);res=labels[5].loc[vv,'return'].to_numpy()-means(inner,x.loc[vv]);model=fit(spec,x.loc[ix],labels[5],cutoff);ds=predict(model,x.loc[g.origin],res)
            path=OUT/'models'/f'h5-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'inner_fit':list(ii),'inner_validation':list(vv),'cutoff':cutoff},path,compress=3);ledger.append({'horizon':5,'fold':fold,'model':name,'status':'ok','last_endpoint':str(labels[5].loc[ix,'endpoint'].max()),'cutoff':cutoff,'inner_last_endpoint':str(labels[5].loc[ii,'endpoint'].max()),'inner_first':vv[0],'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
            for r,d in zip(g.itertuples(),ds):records.append({'horizon':5,'fold':fold,'model':name,'origin':r.origin,'endpoint':r.endpoint,'regime':r.regime,'trend':r.trend,'global_risk':r.global_risk,**d.score(r.realized_return)})
        print('Weekly defensive/volume follow-up',fold,flush=True)
    pd.DataFrame(records).to_csv(OUT/'weekly-followup-predictions.csv',index=False);save('weekly-followup-ledger.json',ledger)
    state=pd.read_csv(OUT/'state-features.csv',index_col=0);x=pd.concat([native[SMALL[:4]],state],axis=1);q=old[(old.horizon==21)&(old.model=='I03_nosize')&(old.split=='outer_exposed')];null=[]
    for fold,g in q.groupby('fold'):
        cutoff=g.origin.min();ix=available(labels[21],cutoff);ii,vv=inner_split(labels[21],ix);mask=state.w_I03_nosize_p.notna();ix=ix[mask.loc[ix].to_numpy()];ii=ii[mask.loc[ii].to_numpy()]
        for kind,shifts in [('STATE',[5,21,42]),('TARGET',[21,42,63])]:
            for shift in shifts:
                xi=x.loc[ii].copy();xf=x.loc[ix].copy();li=labels[21].copy();lf=labels[21].copy()
                if kind=='STATE':
                    columns=list(state);xi[columns]=np.roll(xi[columns].to_numpy(),shift,axis=0);xf[columns]=np.roll(xf[columns].to_numpy(),shift,axis=0);yv=li.loc[vv,'return'].to_numpy()
                else:li.loc[ii,'return']=np.roll(li.loc[ii,'return'].to_numpy(),shift);lf.loc[ix,'return']=np.roll(lf.loc[ix,'return'].to_numpy(),shift);yv=np.roll(labels[21].loc[vv,'return'].to_numpy(),shift)
                inner=fit({'kind':'ridge'},xi,li,vv[0]);res=yv-means(inner,x.loc[vv]);model=fit({'kind':'ridge'},xf,lf,cutoff);ds=predict(model,x.loc[g.origin],res)
                for r,d in zip(g.itertuples(),ds):null.append({'horizon':21,'fold':fold,'origin':r.origin,'model':'DIAGNOSTIC_'+kind,'shift':shift,**d.score(r.realized_return)})
    pd.DataFrame(null).to_csv(OUT/'monthly-expanded-nulls.csv',index=False);print('Monthly block-preserving falsification complete',flush=True)
if __name__=='__main__':run()
