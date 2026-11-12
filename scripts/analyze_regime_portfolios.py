from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.regime_opportunities.framework import OUT,PERIODS,save
from research.regime_opportunities.forward import bh,events,weights
from research.ema_validation.engine import prepare,fee_coeff

def contrasts(paths,columns,tests):
    x=np.column_stack(paths);returns=x/np.vstack([np.full((1,len(paths)),1e6),x[:-1]])-1;n=len(x);rng=np.random.default_rng(64391);draw=[]
    for _ in range(30):
        starts=rng.integers(0,n,(100,int(np.ceil(n/20))));ix=((starts[:,:,None]+np.arange(20))%n).reshape(100,-1)[:,:n];draw.append(100*(np.prod(1+returns[ix],axis=1)-1))
    draw=np.vstack(draw);value=100*(x[-1]/1e6-1);rows=[]
    for name,coef in tests.items():
        c=np.asarray(coef);z=draw@c;point=value@c;rows.append(dict(test=name,effect_pct=point,ci95_low_pct=np.quantile(z,.025),ci95_high_pct=np.quantile(z,.975),block20_two_sided_p=(1+int((abs(z-point)>=abs(point)).sum()))/(1+len(z))))
    return rows

def benchmark(q,cols,util,series):
    value=1e6;held=0.;path=[];turn=0.;fees=0.;dates=q['p']['dates'];previous_weights=np.r_[0.,util[:-1]]
    for j,t in enumerate(cols):
        target=value*previous_weights[j];delta=target-held;rate,fixed=fee_coeff(dates[t],delta>0,True);rate+=.0005
        if delta>0:target=min(target,held+max(0,value-held-fixed)/(1+rate))
        delta=target-held;notional=abs(delta);charge=notional*rate+fixed if notional>1e-8 else 0.;cash=value-target-charge
        ret=series.loc[str(dates[t].date())]/series.loc[str(dates[t-1].date())]-1
        held=target*(1+ret);value=cash+held;path.append(value);fees+=charge;turn+=notional
        assert cash>=-1e-6
    if held>0:
        rate,fixed=fee_coeff(dates[cols[-1]],False,True);charge=held*(rate+.0005)+fixed;path[-1]-=charge;fees+=charge;turn+=held
    return np.asarray(path),turn/1e6,fees

def main():
    broad=pd.read_csv(OUT/'portfolio-results.csv');actual=broad[broad.seed.eq(0)];null=broad[broad.seed.ne(0)];rows=[]
    for (regime,style,stage),g in actual.groupby(['regime','style','stage']):
        own=g.iloc[0];other=null[(null.regime==regime)&(null['style']==style)&(null.stage==stage)];base=actual[(actual.regime=='universal')&(actual['style']==style)&(actual.stage==stage)].iloc[0]
        if len(other):
            u=null[(null.regime=='universal')&(null['style']==style)&(null.stage==stage)].set_index('seed');v=other.set_index('seed');common=v.index.intersection(u.index);delta=v.loc[common,'total_return_pct']-u.loc[common,'total_return_pct'];obs=own.total_return_pct-base.total_return_pct
            mean=other.total_return_pct.mean();p=(1+int(other.total_return_pct.ge(own.total_return_pct).sum()))/(len(other)+1);ip=(1+int(delta.ge(obs).sum()))/(len(delta)+1)
        else:mean=own.total_return_pct;p=1.;ip=1.
        rows.append(dict(regime=regime,style=style,stage=stage,return_pct=own.total_return_pct,drawdown_pct=own.max_drawdown_pct,sharpe=own.sharpe,trades=own.n_trades,exposure_pct=own.exposure_pct,turnover_multiple=own.turnover_multiple,
          matched_random_mean_pct=mean,entry_advantage_pct=own.total_return_pct-mean,randomization_p=p,gate_vs_universal_pct=own.total_return_pct-base.total_return_pct,gate_interaction_p=ip,null_seeds=len(other),holding_reference=style=='buyhold10'))
    a=pd.DataFrame(rows);a['entry_BH_q']=1.;a['interaction_BH_q']=1.
    for stage,g in a[(~a.holding_reference)&a.regime.ne('universal')].groupby('stage'):
        a.loc[g.index,'entry_BH_q']=bh(g.randomization_p);a.loc[g.index,'interaction_BH_q']=bh(g.gate_interaction_p)
    a.to_csv(OUT/'portfolio-comparison.csv',index=False)
    short=json.loads((OUT/'frozen-combinations.json').read_text())['combinations'];extended=pd.read_csv(OUT/'shortlist-results.csv');stress_null=pd.read_csv(OUT/'stress-random-results.csv');u=pd.read_csv(OUT/'universal-extended-results.csv');ci=[];summary=[];benchrows=[];episode=[];q=prepare()
    markettri=pd.read_csv(OUT/'official-TRI.csv',index_col=0);markettri.index=pd.DatetimeIndex(pd.to_datetime(markettri.index,utc=True)).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d')
    with np.load(OUT/'portfolio-inputs.npz') as inp:masks={name:inp['mask_'+name] for name in [x['regime'] for x in short]}
    for record in short:
        regime=record['regime'];style=record['style']
        for stage in PERIODS:
            g=extended[(extended.regime==regime)&(extended['style']==style)&(extended.stage==stage)&extended.scenario.eq('baseline')];own=g[g.seed.eq(0)].iloc[0];control=g[g.seed.ne(0)].set_index('seed');ug=u[(u['style']==style)&u.stage.eq(stage)];uo=ug[ug.seed.eq(0)].iloc[0];ur=ug[ug.seed.ne(0)].set_index('seed');seeds=control.index.intersection(ur.index)
            with np.load(OUT/'portfolio_jobs'/f'{regime}-{style}-{stage}-extended.npz') as p:
                paths=[p['0_equity'].copy(),np.mean([p[f'{s}_equity'] for s in seeds],axis=0)];cols=p['0_cols'].copy();util=p['0_utilization'].copy();tr=p['0_trades'].copy()
            with np.load(OUT/'portfolio_jobs'/f'universal-{style}-{stage}-extended.npz') as p:paths+=[p['0_equity'].copy(),np.mean([p[f'{s}_equity'] for s in seeds],axis=0)]
            tests={'absolute_return':[1,0,0,0],'entry_vs_random':[1,-1,0,0],'gate_vs_universal':[1,0,-1,0],'gate_entry_interaction':[1,-1,-1,1]}
            for row in contrasts(paths,None,tests):ci.append(dict(regime=regime,style=style,stage=stage,**row))
            delta=control.loc[seeds,'total_return_pct']-ur.loc[seeds,'total_return_pct'];interaction=(own.total_return_pct-uo.total_return_pct)
            stress=extended[(extended.regime==regime)&(extended['style']==style)&(extended.stage==stage)&extended.scenario.eq('double_fees10bps')].iloc[0]
            sn=stress_null[(stress_null.regime==regime)&(stress_null['style']==style)&stress_null.stage.eq(stage)]
            localmask=masks[regime][cols];ev=events(localmask);summary.append(dict(regime=regime,style=style,stage=stage,training_eligible=record['eligible'],return_pct=own.total_return_pct,stress_return_pct=stress.total_return_pct,stress_random_mean_pct=sn.total_return_pct.mean(),stress_null_seeds=len(sn),drawdown_pct=own.max_drawdown_pct,
              trades=own.n_trades,exposure_pct=own.exposure_pct,turnover_multiple=own.turnover_multiple,random_mean_pct=control.total_return_pct.mean(),entry_advantage_pct=own.total_return_pct-control.total_return_pct.mean(),
              random_p=(1+int(control.total_return_pct.ge(own.total_return_pct).sum()))/(1+len(control)),gate_interaction_p=(1+int(delta.ge(interaction).sum()))/(1+len(delta)),null_seeds=len(control),pooled_events=len(ev)))
            for index in ['Nifty 50','Nifty 500']:
                nav,turn,fees=benchmark(q,cols,util,markettri[index]);effect=contrasts([paths[0],nav],None,{'strategy_minus_matched_index':[1,-1]})[0]
                benchrows.append(dict(regime=regime,style=style,stage=stage,benchmark=index,benchmark_return_pct=100*(nav[-1]/1e6-1),benchmark_turnover=turn,benchmark_fees=fees,**effect))
            for e,ix in enumerate(ev):
                oncols=cols[ix];selected=np.isin(tr[:,1].astype(int),oncols);trade=tr[selected];episode.append(dict(regime=regime,style=style,stage=stage,event=e,start=str(q['p']['dates'][oncols[0]].date()),end=str(q['p']['dates'][oncols[-1]].date()),on_sessions=len(ix),trades=len(trade),net_pnl=trade[:,8].sum(),stocks=len(np.unique(trade[:,0]))))
    s=pd.DataFrame(summary);s['final_selection_BH_q']=1.;s['interaction_selection_BH_q']=1.
    for stage,g in s.groupby('stage'):
        s.loc[g.index,'final_selection_BH_q']=bh(g.random_p);s.loc[g.index,'interaction_selection_BH_q']=bh(g.gate_interaction_p)
    s.to_csv(OUT/'shortlist-comparison.csv',index=False);c=pd.DataFrame(ci);c['BH_q']=1.
    for _,g in c.groupby('stage'):c.loc[g.index,'BH_q']=bh(g.block20_two_sided_p)
    c.to_csv(OUT/'shortlist-confidence.csv',index=False);pd.DataFrame(benchrows).to_csv(OUT/'shortlist-exposure-benchmarks.csv',index=False);pd.DataFrame(episode).to_csv(OUT/'shortlist-event-PnL.csv',index=False)
    save('portfolio-inference-scope.json',dict(broad='64commonseeds perprotectivecell, opportunitycounts matched percompleteddate, notexactrealizedexposure. BH185nonuniversalregime/entrytestsperstage, interactionseparatefamily. Holdingbenchmarkhasdegeneratenull.',
      shortlisted='1000fixedcommonseeds fortraining-onlychosenentriesandtheiruniversalcomparators; nofinalreselection.20sessioncommoncalendarblock3000draws; intervalsconditionalonfixedpaths, noresimulatedcashwithinbootstrap. Tradecountnotindependenteventcount.',
      benchmark='Prior-closeknownutilizationtarget, cashcapped, modeledgenericdeliveryfeesand5bps, officialTRIclose-to-close. Notexactnext-openETFexecution/beta or priceimpact. No cashinterest.',
      risk='Buyhold10/fullbuyhold use sameATRreferencequantitybutnoprotectivestop/target, soactualriskdiffers. Fiveprotectiveentrystylesandtheirnullsshareallrisk/exitrules.'))
    print('PORTFOLIO_ANALYSIS_COMPLETE',len(a),len(s),flush=True)

if __name__=='__main__':main()
