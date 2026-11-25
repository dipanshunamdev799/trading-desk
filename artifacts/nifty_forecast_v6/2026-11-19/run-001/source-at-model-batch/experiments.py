"""Controlled mechanism, architecture and coherent integration batches."""
import warnings,joblib
from .common import *
from .engine import fit,means,predict,mix,cross_abs,Distribution
from .features import DYNAMIC_CORE
from research.nifty_forecast_v3.experiment import available,inner_split

SMALL=['p_ret5','p_ret21','p_rv21','p_vix','i_participation','i_dispersion','i_bank_nifty_rel5','i_nifty_it_rel21']
SPECS={
 'C_SMALL':{'kind':'ridge','features':'small','hypothesis':'Compact static parent'},
 'H_MULTISCALE':{'kind':'ridge','features':'multiscale','hypothesis':'Selected normalized cross-index divergences beyond native reference'},
 'H_DYNAMIC':{'kind':'ridge','features':'dynamic_full','hypothesis':'Eight state-evolution variables add information'},
 'H_DYNAMIC_CORE':{'kind':'ridge','features':'dynamic_core','hypothesis':'Small evolution system instead of large static states'},
 'H_WARNINGS':{'kind':'ridge','features':'warning','hypothesis':'Banks/cyclicals weaken while headline rises'},
 'H_CORRELATION':{'kind':'ridge','features':'correlation','hypothesis':'Sector synchronization/correlation breakdown'},
 'H_ROTATION':{'kind':'ridge','features':'rotation','hypothesis':'Defensive/IT-financial/broad rotation'},
 'Q_ETF_NOSIZE':{'kind':'ridge','features':'etf_full','hypothesis':'Cross I03 native block with all L01 ETF inputs'},
 'Q_ETF_VOLUME':{'kind':'ridge','features':'etf_volume','hypothesis':'ETF activity separate from cross-asset price exposure'},
 'Q_ETF_PRICE':{'kind':'ridge','features':'etf_price','hypothesis':'ETF return/variation separate from activity'},
 'A_ELASTIC':{'kind':'elastic','features':'native','hypothesis':'Sparse conditional return estimator'},
 'A_HUBER':{'kind':'huber','features':'native','hypothesis':'Robust loss reduces influential return shocks'},
 'A_BAYES':{'kind':'bayes','features':'native','law':'bayes','hypothesis':'Regularized Bayesian predictive normal atoms'},
 'A_FOREST':{'kind':'forest','features':'native','hypothesis':'Native-state empirical forest law'},
 'A_LGBM_QUANT':{'kind':'lgbm_quantile','features':'native','hypothesis':'Native shallow boosting with direct quantiles'},
 'A_QUANTILE':{'kind':'quantile','features':'native','hypothesis':'Regularized linear quantile law'},
 'A_GAM':{'kind':'spline','features':'small','hypothesis':'Low-dimensional additive nonlinear response'},
 'A_STUDENT':{'kind':'ridge','features':'native','law':'student','hypothesis':'Regularized heavy-tailed conditional law'},
 'R_VOL':{'kind':'experts','features':'native','gate':'volatility','hypothesis':'Shrunk high/low-volatility experts'},
 'R_TREND':{'kind':'experts','features':'native','gate':'trend','hypothesis':'Shrunk trend/sideways experts'},
 'G_MATCHED':{'kind':'ridge','features':'matched_small','hypothesis':'Same mature training dates as mediator models'},
 'G_DIRECT':{'kind':'ridge','features':'global_direct','hypothesis':'Sparse raw globals beyond date-matched domestic control'},
 'G_MEDIATED':{'kind':'ridge','features':'mediated','hypothesis':'Honest global-sector correction forecasts beyond domestic control'},
 'M_WEEKSTATE':{'kind':'ridge','features':'weekly_states','only_horizon':21,'hypothesis':'Past issued weekly-state evolution predicts month, no probability compounding'},
 'M_PERSIST':{'kind':'ridge','features':'persistent','only_horizon':21,'hypothesis':'Slow persistent observed regimes, low-dimensional monthly law'}}
JOINT=['J_EQUAL','J_BRIER','J_CRPS','J_COMBINED','J_SIGN']
def datasets():
    native=pd.read_csv(OUT/'native-reference.csv',index_col=0);deep=pd.read_csv(OUT/'deep-features.csv',index_col=0);liq=pd.read_csv(OUT/'liquidity-reference.csv',index_col=0);glob=pd.read_csv(OUT/'global-reference.csv',index_col=0);med=pd.read_csv(OUT/'mediator-features.csv',index_col=0);state=pd.read_csv(OUT/'state-features.csv',index_col=0)
    selected=[f'n_{n}_{field}' for n in ['bank_nifty','nifty_financial','nifty_it','idx_Nifty_500'] for field in ['rel1','rel3','rel10','rel20','rv_ratio']]
    etf=[c for c in liq if c.startswith('p_liq_')]
    d={'native':native,'small':native[SMALL],'multiscale':pd.concat([native,deep[selected]],axis=1),
        'dynamic_full':pd.concat([native,deep[DYNAMIC_CORE]],axis=1),'dynamic_core':pd.concat([native[SMALL[:4]],deep[DYNAMIC_CORE]],axis=1),
        'warning':pd.concat([native,deep[['q_banks_warning','q_cyclical_weakness','q_index_breadth_divergence']]],axis=1),
        'correlation':pd.concat([native,deep[['q_sector_correlation','q_corr_jump','q_sector_correlation_slope5']]],axis=1),
        'rotation':pd.concat([native,deep[['q_defensive_rotation','q_financial_it_rotation','q_broad_deterioration']]],axis=1),
        'persistent':pd.concat([native[SMALL[:4]],deep[['q_trend_persistence','q_risk_persistence','q_defensive_persistence','q_transition_rate']]],axis=1)}
    for name,columns in [('etf_full',etf),('etf_volume',[c for c in etf if c.endswith('_volume')]),('etf_price',[c for c in etf if not c.endswith('_volume')])]:d[name]=pd.concat([native,liq[columns]],axis=1)
    for h in [5,21]:
        available_med=[f'med{h}_{target}_increment' for target in ['IT','ENERGY','BANKREL','MAGNITUDE']]+[f'med{h}_weak_breadth_shock']
        d[f'mediated_{h}']=pd.concat([native[SMALL],med[available_med]],axis=1)
        direct=['g_IXIX_ret1','g_IXIX_ret5','g_BZUSD_ret5','g_USDINR_ret5','x_oil_fx','x_global_mean','x_global_vol']
        d[f'global_direct_{h}']=pd.concat([native[SMALL],glob[direct]],axis=1)
    d['weekly_states']=pd.concat([native[SMALL[:4]],state],axis=1)
    return d,med,state
def quadratic_minimum(fn,lower=.1,upper=.9):
    a,b,c=fn(0.),fn(1.),fn(.5);quadratic=2*(a+b-2*c);linear=b-a-quadratic
    return float(np.clip(-linear/(2*quadratic),lower,upper)) if quadratic>1e-12 else .5
def learned_weight(rows,cutoff,criterion):
    by={}
    for r in rows:
        if r['endpoint']<cutoff:by.setdefault(r['origin'],{})[r['model']]=r
    origins=sorted(d for d,v in by.items() if len(v)==2)[-42:];prepared=[]
    for day in origins:
        a=by[day]['I03_nosize'];b=by[day]['L01'];la=Distribution(a['atoms'],a['weights']);lb=Distribution(b['atoms'],b['weights']);y=a['realized_return']
        aa=float(la.w@abs(la.a-y));ab=float(lb.w@abs(lb.a-y));ba=cross_abs(la,la);bb=cross_abs(lb,lb);bc=cross_abs(la,lb)
        prepared.append((aa,ab,ba,bb,bc,la.stats()['p_up'],lb.stats()['p_up'],int(y>0),a['classifier_p']))
    if len(prepared)<20:return .5,origins,{'fallback':'too few honest prior forecasts'}
    p=np.array(prepared,float)
    def objective(w):
        crps=np.mean(w*p[:,0]+(1-w)*p[:,1]-.5*(w*w*p[:,2]+(1-w)**2*p[:,3]+2*w*(1-w)*p[:,4]));brier=np.mean((w*p[:,5]+(1-w)*p[:,6]-p[:,7])**2)
        return float(brier+.05*(w-.5)**2) if criterion=='J_BRIER' else float(crps+.002*(w-.5)**2) if criterion=='J_CRPS' else float(crps/.015+brier/.25+.25*(w-.5)**2)
    weight=quadratic_minimum(objective)
    return weight,origins,{'objective_at_half':objective(.5),'objective_at_weight':objective(weight),'latest_training_endpoint':max(by[d]['I03_nosize']['endpoint'] for d in origins)}
def run():
    if (OUT/'model-registry.json').exists():raise FileExistsError('Model batch already registered')
    save('model-registry.json',{'registered_at':now(),'specifications':SPECS,'joint_laws':JOINT,'parameters':'Fixed Ridge100; ElasticNet.001/.5; Huber10/1.35; RF64/depth3/minleaf30; LGBM80/depth2/leaves4/minleaf40/.04/L2=10; GAM3knots/degree2; quantilealpha.005; Studentdf5; conditional.65/unconditional.35',
        'mixtures':'Only prior honestly issued prequential laws, endpoint<current cutoff,last42; weights constrained .1–.9; penalties Brier.05,CRPS.002,joint.25; equal-mixture benchmark',
        'sign_tilt':'Shrink toward native logisticC.1 using beta learned from honest prior Brier with penalty.05, bounded0–.75; reweight actual return atoms, not invent magnitudes',
        'monthly_context':'Four disjoint windows; monthly-specific systems are not forced onto weekly',
        'matched_training':'Direct/mediated/date-matched control share dates where intermediate forecast exists; no backfilled fitted sector outcomes',
        'source_hashes':{p.name:sha(p) for p in SRC.glob('*.py')},'exposure':'All retrospective dates exposed; no independently validated claim'})
    ds,med,state=datasets();old=pd.read_csv(V5/'all-predictions.csv');old=old[(old.split=='outer_exposed')&(old.model=='I03_nosize')];labels={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [5,21]}
    cached=[json.loads(line) for line in (OUT/'prequential-laws.jsonl').read_text().splitlines()];clf=joblib.load(OUT/'prequential-classifiers.joblib');records=[];ledger=[];weights=[]
    for h in [5,21]:
        for fold,g in old[old.horizon==h].groupby('fold'):
            cutoff=g.origin.min();ix=available(labels[h],cutoff);ii,vv=inner_split(labels[h],ix)
            for name,spec in SPECS.items():
                if spec.get('only_horizon',h)!=h:continue
                key=spec['features'];x=ds[f'{key}_{h}'] if key in ['mediated','global_direct'] else ds['small'] if key=='matched_small' else ds[key]
                trainix=ix;innerix=ii
                if key in ['mediated','global_direct','matched_small']:
                    present=med[f'med{h}_IT_increment'].notna();trainix=ix[present.loc[ix].to_numpy()];innerix=ii[present.loc[ii].to_numpy()]
                if key=='weekly_states':
                    present=state.w_I03_nosize_p.notna();trainix=ix[present.loc[ix].to_numpy()];innerix=ii[present.loc[ii].to_numpy()]
                try:
                    if len(trainix)<80 or len(innerix)<60:raise ValueError('Insufficient honest intermediate-state history')
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always');inner=fit(spec,x.loc[innerix],labels[h],vv[0]);res=labels[h].loc[vv,'return'].to_numpy()-means(inner,x.loc[vv]);model=fit(spec,x.loc[trainix],labels[h],cutoff);pred=predict(model,x.loc[g.origin],res)
                    path=OUT/'models'/f'h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'inner_fit':list(innerix),'inner_validation':list(vv),'cutoff':cutoff},path,compress=3)
                    ledger.append({'horizon':h,'fold':fold,'model':name,'status':'ok','training_n':len(trainix),'inner_n':len(innerix),'last_endpoint':str(labels[h].loc[trainix,'endpoint'].max()),'cutoff':cutoff,'inner_last_endpoint':str(labels[h].loc[innerix,'endpoint'].max()),'inner_first':vv[0],'warnings':list({str(w.message)[:150] for w in caught}),'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
                    for row,d in zip(g.itertuples(),pred):
                        stats=d.stats();score=d.score(row.realized_return)
                        records.append({'horizon':h,'fold':fold,'model':name,'origin':row.origin,'endpoint':row.endpoint,'regime':row.regime,'trend':row.trend,'global_risk':row.global_risk,'expected_absolute_return':stats['expected_absolute_return'],'magnitude_mae':abs(stats['expected_absolute_return']-abs(row.realized_return)),
                            'endpoint_below2':float(d.w[d.a<-.02].sum()),'endpoint_below5':float(d.w[d.a<-.05].sum()),**score})
                except Exception as e:ledger.append({'horizon':h,'fold':fold,'model':name,'status':'failed','reason':type(e).__name__+':'+str(e)[:180]})
            # Every mixture uses the same two complete endpoint laws, without selecting test weights.
            rows=[r for r in cached if r['horizon']==h];by={(r['model'],r['origin']):r for r in rows}
            for name in JOINT:
                w=.5;training=[];details={}
                if name in ['J_BRIER','J_CRPS','J_COMBINED']:w,training,details=learned_weight(rows,cutoff,name)
                beta=0.
                if name=='J_SIGN':
                    history=[r for r in rows if r['model']=='I03_nosize' and r['endpoint']<cutoff][-42:];training=[r['origin'] for r in history]
                    p=np.array([r['p'] for r in history]);pc=np.array([r['classifier_p'] for r in history]);y=np.array([r['realized_return']>0 for r in history]);delta=pc-p
                    beta=float(np.clip(np.mean(delta*(y-p))/(np.mean(delta**2)+.05),0,.75));details={'latest_training_endpoint':max(r['endpoint'] for r in history)}
                weights.append({'horizon':h,'fold':fold,'model':name,'cutoff':cutoff,'I03_weight':w,'sign_beta':beta,'training_forecast_origins':training,**details})
                for row in g.itertuples():
                    aa=by[('I03_nosize',row.origin)];bb=by[('L01',row.origin)];a=Distribution(aa['atoms'],aa['weights']);b=Distribution(bb['atoms'],bb['weights'])
                    if name=='J_SIGN':
                        raw=a.stats()['p_up'];prob=(1-beta)*raw+beta*aa['classifier_p'];tilt=np.where(a.a>0,prob/max(raw,1e-9),(1-prob)/max(1-raw,1e-9));d=Distribution(a.a,a.w*tilt)
                    else:d=mix(a,b,w)
                    st=d.stats();records.append({'horizon':h,'fold':fold,'model':name,'origin':row.origin,'endpoint':row.endpoint,'regime':row.regime,'trend':row.trend,'global_risk':row.global_risk,'expected_absolute_return':st['expected_absolute_return'],'magnitude_mae':abs(st['expected_absolute_return']-abs(row.realized_return)),
                        'endpoint_below2':float(d.w[d.a<-.02].sum()),'endpoint_below5':float(d.w[d.a<-.05].sum()),**d.score(row.realized_return)})
            print('V6 registered models',h,fold,'failures',sum(r['status']=='failed' for r in ledger),flush=True)
    pd.DataFrame(records).to_csv(OUT/'model-predictions.csv',index=False);save('model-ledger.json',ledger);save('mixture-weight-ledger.json',weights)
    print('Mechanism/architecture/integration batch complete',len(records),'records',flush=True)
if __name__=='__main__':run()
