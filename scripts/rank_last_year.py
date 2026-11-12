"""Descriptive latest-year rankings; no selection or deployment validation."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import research_directional_lab as lab
OUT=ROOT/'artifacts'/'last_year_ranking';OUT.mkdir(exist_ok=True)
START,END='2025-11-09','2026-11-08'


def metrics(p):
    p=np.asarray(p);net=p-5;eq=np.r_[0,net.cumsum()]
    return {'trades':len(p),'gross_mean':float(p.mean()),'net5_mean':float(net.mean()),'net5_total':float(net.sum()),
        'net5_win_pct':float((net>0).mean()*100),'net5_profit_factor':float(net[net>0].sum()/-net[net<0].sum()) if (net<0).any() else None,
        'net5_max_drawdown_points':float((np.maximum.accumulate(eq)-eq).max())}


def interval(trades,days):
    rng=np.random.default_rng(20261110);counts=trades.groupby('day').size().reindex(days,fill_value=0).to_numpy()
    sums=trades.groupby('day').net.sum().reindex(days,fill_value=0).to_numpy();n=len(days)
    starts=rng.integers(0,n,(3000,int(np.ceil(n/5)),1));idx=((starts+np.arange(5))%n).reshape(3000,-1)[:,:n]
    den=counts[idx].sum(axis=1);good=den>0
    return np.quantile(sums[idx].sum(axis=1)[good]/den[good],[.025,.975]).tolist()


def main():
    d,audit=lab.load_data();f=lab.features(d);f=f[f.day.between(START,END)].reset_index(drop=True);days=sorted(f.day.unique())
    configs=lab.configurations(f);rows=[]
    for name,family,params,filter_name,window,hold,signal in configs:
        t=lab.trade_rows(f,signal,hold)
        if not len(t):continue
        rows.append({'strategy':name,'family':family,'params':params,'filter':filter_name,'window':window,'hold_minutes':hold,**metrics(t[:,3])})
    table=pd.DataFrame(rows);table.to_csv(OUT/'all-configurations.csv',index=False)
    eligible=table[table.trades>=50].sort_values(['net5_total','strategy'],ascending=[False,True])
    leaders=eligible.drop_duplicates('family').copy()
    byname={c[0]:c for c in configs};export=[];result=[]
    for r in leaders.to_dict('records'):
        t=lab.trade_rows(f,byname[r['strategy']][-1],r['hold_minutes'])
        marks=pd.DataFrame({'day':f.day.iloc[t[:,0].astype(int)].to_numpy(),'net':t[:,3]-5})
        r['net5_conditional_ci95']=interval(marks,days);result.append(r)
        for i,j,side,pnl in t:
            i,j=int(i),int(j)
            export.append({'strategy':r['strategy'],'session':f.day.iloc[i],'entry_at':str(f.ts.iloc[i+1]),'exit_at':str(f.known_at.iloc[j]),'side':int(side),'entry':float(f.open.iloc[i+1]),'exit':float(f.close.iloc[j]),'gross_points':pnl,'net5_points':pnl-5})
    pd.DataFrame(result).to_csv(OUT/'family-leaders.csv',index=False);pd.DataFrame(export).to_csv(OUT/'family-leader-trades.csv',index=False)
    prior=pd.read_csv(ROOT/'artifacts'/'directional_research'/'lab-selected-trades.csv');prior=prior[prior.session.between(START,END)]
    frozen=[]
    for name,g in prior.groupby('strategy'):
        frozen.append({'strategy':name,**metrics(g.gross_index_points)})
    frozen=sorted(frozen,key=lambda r:-r['net5_total']);pd.DataFrame(frozen).to_csv(OUT/'previously-selected-finalists.csv',index=False)
    premium_path=ROOT/'artifacts'/'directional_research_phase2'/'option-premium-trades.csv'
    p=pd.read_csv(premium_path);p=p[(p.status=='premium_proxy_observed')&p.entry_date.between('2025-10-24','2026-10-23')]
    premiums=[]
    from research_option_premiums import bootstrap
    for (strategy,bucket,strike),g in p.groupby(['strategy','expiry_bucket','strike_rule']):
        net=g.illustrative_net_rupees_per_lot
        premiums.append({'strategy':strategy,'expiry_bucket':bucket,'strike':strike,'trades':len(g),'net_mean_rupees_per_lot':float(net.mean()),
            'net_total_rupees_unit_lot':float(net.sum()),'net_win_pct':float((net>0).mean()*100),'severe_mean_rupees_per_lot':float(g.severe_net_rupees_per_lot.mean()),
            'net_conditional_ci95':bootstrap(g,'illustrative_net_rupees_per_lot')})
    premiums.sort(key=lambda r:-r['net_total_rupees_unit_lot']);pd.DataFrame(premiums).to_csv(OUT/'option-premium-ranking.csv',index=False)
    summary={'requested_index_window':[START,END],'actual_complete_index_sessions':len(days),'first_index_session':days[0],'last_index_session':days[-1],
        'ranking':'Retrospective cumulative signed index points after5illustrativepoints/trade; >=50trades; one highest-total configuration per family. NOT out-of-sample selection or option PnL.',
        'grid_configurations':len(configs),'eligible_configurations':len(eligible),'family_leaders':result,'previously_selected':frozen,
        'premium_window':['2025-10-24','2026-10-23'],'premium_note':'Daily-signal exactoption firsttradeopen/officialclose proxies; not the same intraday rulebook. All policy groups disclosed; overlapping/duplicate policies not pooled.',
        'premium_groups':premiums,'input_hashes':{**audit['input_hashes'],'option-premium-trades.csv':hashlib.sha256(premium_path.read_bytes()).hexdigest()},
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'sessions':len(days),'grid':len(configs),'eligible':len(eligible),'family_leaders':result[:5],'previously_selected':frozen[:5],'premium_best':premiums[:2]},indent=2))


if __name__=='__main__':main()
