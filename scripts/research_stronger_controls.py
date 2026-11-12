"""Phase-two controls for the three frozen NIFTY research candidates.

No broker access. All returns are index points, not option-premium P&L.
Optional --extra adds older five-minute history; --label preserves each panel.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import research_directional_lab as lab

OUT = ROOT/'artifacts'/'directional_research_phase2'
SEED = 20261109
FIXED = [('ema_trend','12_26_gap0.5'), ('donchian','lookback20_buffer0'), ('pullback','ema21_tolerance0.75')]


def save(prefix, name, value):
    (OUT/f'{prefix}-{name}.json').write_text(json.dumps(value,indent=2,default=str,allow_nan=False),encoding='utf-8')


def load(extra):
    d,audit=lab.load_data()
    if extra:
        p=Path(extra); newer=lab.frame(p)
        newer['day']=newer.ts.dt.strftime('%Y-%m-%d')
        # Existing frozen source takes precedence on overlaps, which must agree.
        overlap=d.merge(newer,on='ts',suffixes=('_old','_extra'))
        deviations={c:float((overlap[c+'_old']-overlap[c+'_extra']).abs().max()) if len(overlap) else 0 for c in ['open','high','low','close']}
        assert all(v<.011 for v in deviations.values()),deviations
        all_rows=pd.concat([newer,d]).sort_values('ts',kind='stable').drop_duplicates('ts',keep='last')
        minute=all_rows.ts.dt.hour*60+all_rows.ts.dt.minute
        all_rows=all_rows[(minute>=555)&(minute<910)].copy()
        good=[];excluded=[]
        for day,g in all_rows.groupby('day'):
            valid=np.isfinite(g[['open','high','low','close']]).all().all() and (g.low>0).all() and (g.high>=g[['open','close','low']].max(axis=1)).all() and (g.low<=g[['open','close','high']].min(axis=1)).all()
            if list(g.ts.dt.hour*60+g.ts.dt.minute)==list(range(555,910,5)) and valid:good.append(day)
            else:excluded.append(day)
        d=all_rows[all_rows.day.isin(good)].reset_index(drop=True)
        audit['extra']={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'overlap_deviations':deviations,'excluded':excluded}
    return d,audit


def signal(f, side, filter_name='trend', window='afternoon'):
    mask=(f.efficiency>=.35)&(f.trend.abs()>=.5) if filter_name=='trend' else np.ones(len(f),bool)
    window_mask=(f.minute>=780) if window=='afternoon' else ((f.minute>=570)&(f.minute<660))
    return np.where(mask & window_mask & f.atr.gt(0),side,0).astype(np.int8)


def replay(f, side, horizon=60, delay=0, label=''):
    h=horizon//5; rows=[];last=-1
    for i in np.flatnonzero(side):
        j=i+h+delay; entry_i=i+1+delay
        if i<last or j>=len(f) or f.day.iloc[i]!=f.day.iloc[j] or f.minute.iloc[j]+5>910:continue
        entry=float(f.open.iloc[entry_i]);exit=float(f.close.iloc[j]);direction=int(side[i]);change=exit-entry
        momentum=int(np.sign(f.ret6.iloc[i])) if np.isfinite(f.ret6.iloc[i]) else 0
        rows.append({'strategy':label,'session':f.day.iloc[i],'signal_i':int(i),'entry_i':int(entry_i),'exit_i':int(j),
            'signal_at':str(f.known_at.iloc[i]),'entry_at':str(f.ts.iloc[entry_i]),'exit_at':str(f.known_at.iloc[j]),
            'direction':direction,'entry':entry,'exit':exit,'gross':direction*change,'net2':direction*change-2,'net5':direction*change-5,
            'matched_long_net2':change-2,'matched_short_net2':-change-2,'matched_momentum_net2':momentum*change-2*int(momentum!=0),
            'excess_long':(direction-1)*change,'excess_momentum':(direction-momentum)*change-2*int(momentum==0),'hold_minutes':horizon,'delay_bars':delay})
        last=j
    return pd.DataFrame(rows)


def stats(t):
    if not len(t):return {'n':0}
    return {'n':len(t),**{k:float(t[k].mean()) for k in ['gross','net2','net5','matched_long_net2','matched_short_net2','matched_momentum_net2','excess_long','excess_momentum']},
            'win_pct':float(t.gross.gt(0).mean()*100),'sessions':int(t.session.nunique())}


def bootstrap(t, days, seed=SEED):
    count=t.groupby('session').size().reindex(days,fill_value=0).to_numpy()
    sums=t.groupby('session')[['net2','excess_long','excess_momentum']].sum().reindex(days,fill_value=0).to_numpy()
    rng=np.random.default_rng(seed);n=len(days);block=min(5,n)
    idx=((rng.integers(0,n,(6000,int(np.ceil(n/block)),1))+np.arange(block))%n).reshape(6000,-1)[:,:n]
    den=count[idx].sum(axis=1);good=den>0
    draws=sums[idx].sum(axis=1)[good]/den[good,None]
    # Three strategies x two confirmatory contrasts, conditional on fixed set.
    simultaneous_alpha=.05/6
    result={}
    for i,key in enumerate(['net2','excess_long','excess_momentum']):
        result[key+'_ci95']=np.quantile(draws[:,i],[.025,.975]).tolist()
        if key in ['net2','excess_momentum']:
            result[key+'_bonferroni6_ci']=np.quantile(draws[:,i],[simultaneous_alpha/2,1-simultaneous_alpha/2]).tolist()
    return result


def randomization(t, days):
    # One flip per whole session preserves within-session signal clustering.
    values=t.groupby('session').gross.sum().reindex(days,fill_value=0).to_numpy()
    observed=float(t.gross.mean());rng=np.random.default_rng(SEED)
    draws=rng.choice([-1,1],size=(20000,len(days)))@values/len(t)
    p=float((1+(np.abs(draws)>=abs(observed)).sum())/(len(draws)+1))
    return {'session_sign_flip_two_sided_p':p,'randomized_gross_mean_ci95':np.quantile(draws,[.025,.975]).tolist(),
            'gross_mean_observed':observed,'draws':len(draws),'null':'Conditional on observed trade times/magnitudes: session-wide random direction orientation. Not an incremental-factor p-value.'}


def verify(t, f):
    checked=0
    for strategy,g in t.groupby('strategy'):
        previous_exit=None
        for r in g.sort_values('entry_i').itertuples():
            assert pd.Timestamp(r.entry_at)-pd.Timestamp(r.signal_at)==pd.Timedelta(minutes=5*r.delay_bars)
            assert pd.Timestamp(r.exit_at)-pd.Timestamp(r.entry_at)==pd.Timedelta(minutes=r.hold_minutes)
            assert f.day.iloc[r.entry_i]==r.session==f.day.iloc[r.exit_i]
            assert f.open.iloc[r.entry_i]==r.entry and f.close.iloc[r.exit_i]==r.exit
            assert np.isclose(r.gross,r.direction*(r.exit-r.entry))
            if previous_exit is not None:assert pd.Timestamp(r.entry_at)>=previous_exit
            previous_exit=pd.Timestamp(r.exit_at);checked+=6
    return checked


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--extra');parser.add_argument('--label',default='original');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);prefix='control-'+args.label
    raw,audit=load(args.extra);f=lab.features(raw);days=np.array(sorted(f.day.unique()))
    fixed_holdout_start='2026-06-29';final_days=days[days>=fixed_holdout_start]
    rules={(family,param):s for family,param,s in lab.rules(f)}
    frozen={name:signal(f,rules[(name,param)]) for name,param in FIXED}
    # Deterministic priority; the router is fixed before computing its returns.
    router=np.zeros(len(f),dtype=np.int8)
    for name,_ in FIXED:router=np.where(router!=0,router,frozen[name])
    save(prefix,'preregister',{'fixed_rules':FIXED,'router_priority':[x[0] for x in FIXED],'router_hold_minutes':60,'router_one_position':True,
        'historical_final_period':{'first':fixed_holdout_start,'last':str(final_days[-1]),'sessions':len(final_days)},
        'status':'Retrospective phase-two hypotheses motivated by phase-one observed results; not independent/prospective confirmation.',
        'contrasts':['net2 positive','excess versus same-time 30-minute momentum positive'],
        'multiplicity':'Six Bonferroni intervals: 3 candidates x 2 contrasts. Conditional fixed-set coverage, NOT correction of phase-one 3600-configuration selection.',
        'randomization':'20000 session-level sign flips; two-sided diagnostic, not market-stationarity guarantee.',
        'ablations':'Same parameters, none/trend filters, morning/afternoon windows,15/30/60 holds. Exploratory; no new selection.',
        'walkforward':'Monthly choose one of fixed3 using preceding120complete sessions, requiring>=30trades and positive net5; otherwise abstain.',
        'source_audit':audit,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'feature_dependency_sha256':hashlib.sha256(Path(lab.__file__).read_bytes()).hexdigest()})
    complete={};export=[];checks=0;primary=[];robust=[];latency=[];subgroups=[];signs=[];monthly=[]
    for name,_ in FIXED+[('fixed_router','')]:
        s=router if name=='fixed_router' else frozen[name]
        t=replay(f,s,label=name);complete[name]=t;export.append(t);checks+=verify(t,f)
        final=t[t.session>=fixed_holdout_start]
        result={'strategy':name,**stats(final),**bootstrap(final,final_days),**randomization(final,final_days)}
        result['passes_conditional6_gate']=bool(len(final)>=30 and result['net5']>0 and result['net2_bonferroni6_ci'][0]>0 and result['excess_momentum_bonferroni6_ci'][0]>0) if name!='fixed_router' else None
        primary.append(result)
        grouped=final.groupby('session').net2.sum()
        bestday=grouped.idxmax()
        robust.append({'strategy':name,'full':stats(final),'drop_best_5_trades':stats(final.drop(final.nlargest(5,'gross').index)),
                       'drop_best_day':stats(final[final.session!=bestday]),'best_day':bestday,
                       'positive_active_day_pct':float(grouped.gt(0).mean()*100),'positive_all_final_day_pct':float(grouped.reindex(final_days,fill_value=0).gt(0).mean()*100)})
        lagged=replay(f,s,delay=1,label=name+'_delay1');checks+=verify(lagged,f)
        latency.append({'strategy':name,**stats(lagged[lagged.session>=fixed_holdout_start])})
        for period,selected in [('year',t.session.str[:4]),('quarter',pd.to_datetime(t.session).dt.to_period('Q').astype(str)),('side',t.direction.map({1:'call_direction',-1:'put_direction'}))]:
            for label,g in t.groupby(selected):subgroups.append({'strategy':name,'period':period,'label':str(label),'scope':'all_history' if period!='side' else 'historical_final','stats':stats(g if period!='side' else g[g.session>=fixed_holdout_start])})
        for month,g in final.groupby(final.session.str[:7]):monthly.append({'strategy':name,'month':month,**stats(g)})
    # Each ablation's returns are disclosed. No rule is chosen from this table.
    ablations=[]
    for name,param in FIXED:
        for filter_name in ['none','trend']:
            for window in ['morning','afternoon']:
                for horizon in [15,30,60]:
                    t=replay(f,signal(f,rules[(name,param)],filter_name,window),horizon=horizon,label=name)
                    ablations.append({'strategy':name,'filter':filter_name,'window':window,'hold':horizon,**stats(t[t.session>=fixed_holdout_start])})
    momentum=np.where((f.minute>=570)&f.ret6.notna(),np.sign(f.ret6.fillna(0)),0)
    t=replay(f,momentum,label='simple_momentum30m');base=stats(t[t.session>=fixed_holdout_start])
    # Monthly policy uses only completed preceding sessions. Trading begins in final period.
    walk=[];walkchoices=[]
    for month in sorted(set(pd.Series(final_days).str[:7])):
        month_days=days[pd.Series(days).str.startswith(month).to_numpy()];first=month_days[0]
        past=days[days<first][-120:]
        scores=[]
        for name,_ in FIXED:
            q=complete[name][complete[name].session.isin(past)];m=stats(q)
            if m.get('n',0)>=30 and m['net5']>0:scores.append((m['net5'],name,m['n']))
        chosen=sorted(scores,key=lambda x:(-x[0],x[1]))[0] if scores else None
        walkchoices.append({'month':month,'training_first':str(past[0]) if len(past) else None,'training_last':str(past[-1]) if len(past) else None,'eligible_scores':scores,'chosen':chosen[1] if chosen else None})
        if chosen:
            q=complete[chosen[1]];walk.append(q[(q.session>=fixed_holdout_start)&q.session.str.startswith(month)])
    walked=pd.concat(walk,ignore_index=True) if walk else pd.DataFrame(columns=complete['ema_trend'].columns)
    walk_result={**stats(walked),**bootstrap(walked,final_days)} if len(walked) else stats(walked)
    # Reconcile against phase-one persisted finalists exactly for the original input.
    phase1=pd.read_csv(ROOT/'artifacts'/'directional_research'/'lab-selected-trades.csv')
    if not args.extra:
        for name,param in FIXED:
            expected=phase1[phase1.strategy.str.startswith(name+'|'+param+'|trend|afternoon|h60')].reset_index(drop=True)
            actual=complete[name].reset_index(drop=True)
            assert len(actual)==len(expected)
            assert np.allclose(actual.gross,expected.gross_index_points)
            assert (pd.to_datetime(actual.entry_at)==pd.to_datetime(expected.entry_at)).all()
            checks+=3
    for cut in [81,len(f)//2+17,len(f)-9]:
        pf=lab.features(raw.iloc[:cut]);cols=[c for c in pf if c not in ['source','volume','oi']]
        pd.testing.assert_frame_equal(pf[cols],f.iloc[:cut][cols],check_dtype=False);checks+=1
    backward=[]
    if args.extra:
        older=days[days<'2025-01-01']
        for name,t in complete.items():
            prior=t[t.session<'2025-01-01']
            backward.append({'strategy':name,**stats(prior),**bootstrap(prior,older),**randomization(prior,older)})
    summary={'coverage':{'first':str(days[0]),'last':str(days[-1]),'sessions':len(days)},'final_days':{'first':str(final_days[0]),'last':str(final_days[-1]),'sessions':len(final_days)},
        'primary':primary,'latency':latency,'robustness':robust,'momentum_baseline':base,'monthly_walkforward':walk_result,'verification_assertions':checks,'backward_2022_2024':backward,
        'limitations':['All market-direction index points; executable option-premium outcome unknown.','Phase-two candidate set was motivated by phase-one results; conditional six-contrast intervals do not correct original search.','Year/quarter tables include development history and are descriptive. Final-only months and sides are separately reported.','The hypothetical matched-time controls share trigger times; this isolates side choice, not entry opportunity selection.','One-bar delay changes eligible entries/next signals and sample. It is an execution sensitivity, not a paired attribution.','No stop, target, sizing, quote spread or actual tax model.','Rolling monthly policy is specified now on already studied history and remains exploratory.']}
    save(prefix,'summary',summary);save(prefix,'monthly-choices',walkchoices);save(prefix,'subgroups',subgroups)
    pd.concat(export,ignore_index=True).to_csv(OUT/f'{prefix}-trades.csv',index=False)
    pd.DataFrame(ablations).to_csv(OUT/f'{prefix}-ablations.csv',index=False)
    pd.DataFrame(monthly).to_csv(OUT/f'{prefix}-final-months.csv',index=False)
    walked.to_csv(OUT/f'{prefix}-walkforward-trades.csv',index=False)
    lines=['# Stronger controls for frozen intraday candidates','',f"{len(days)} complete research sessions, {days[0]} through {days[-1]}. Historical final period {final_days[0]}–{final_days[-1]} ({len(final_days)} sessions). All numbers are index points per trade, not option returns.",'',
        'The rules were chosen from phase-one observations. These are retrospective diagnostics. The six-contrast Bonferroni intervals cover net2 and matched-momentum excess for the fixed three-rule set, conditional on that set. They do not correct the original strategy search. The router is an additional exploratory portfolio, outside those six comparisons.',
        '', '|Rule|N|Gross|Net2|Net5|Matched long net2|Matched momentum net2|Excess over momentum|Net2 conditional six-test interval|Excess conditional six-test interval|',
        '|---|---:|---:|---:|---:|---:|---:|---:|---|---|']
    for r in primary:
        ci=r['net2_bonferroni6_ci'];ex=r['excess_momentum_bonferroni6_ci']
        lines.append(f"|{r['strategy']}|{r['n']}|{r['gross']:.2f}|{r['net2']:.2f}|{r['net5']:.2f}|{r['matched_long_net2']:.2f}|{r['matched_momentum_net2']:.2f}|{r['excess_momentum']:.2f}|{ci[0]:.2f}, {ci[1]:.2f}|{ex[0]:.2f}, {ex[1]:.2f}|")
    lines+=['','Same-time controls use the identical entry/exit prices with long, short or preceding-30-minute momentum direction. They isolate direction choice at those times. The all-opportunity momentum baseline (60m hold) had '+str(base['n'])+f" trades, net2 mean {base['net2']:.2f}.",'',
        '|Rule|Session sign-flip two-sided p|One-bar-delay N|One-bar-delay net2|Drop best five net2|Drop best day net2|', '|---|---:|---:|---:|---:|---:|']
    for r,l,z in zip(primary,latency,robust):lines.append(f"|{r['strategy']}|{r['session_sign_flip_two_sided_p']:.4f}|{l['n']}|{l['net2']:.2f}|{z['drop_best_5_trades']['net2']:.2f}|{z['drop_best_day']['net2']:.2f}|")
    if backward:
        lines+=['','## Earlier-history replication (2022–2024)',
            'Frozen rules motivated by the2025–2026 study are replayed on earlier history without refitting. This is backward replication, not a future holdout. Separate year/quarter rows disclose changing regimes.',
            '', '|Rule|N|Gross|Net2|Excess over same-time momentum|Net2 conditional six-test interval|Excess conditional six-test interval|', '|---|---:|---:|---:|---:|---|---|']
        for r in backward:
            ci=r['net2_bonferroni6_ci'];ex=r['excess_momentum_bonferroni6_ci']
            lines.append(f"|{r['strategy']}|{r['n']}|{r['gross']:.2f}|{r['net2']:.2f}|{r['excess_momentum']:.2f}|{ci[0]:.2f}, {ci[1]:.2f}|{ex[0]:.2f}, {ex[1]:.2f}|")
    lines+=['','Sign flips randomize a whole session together to retain within-day clustering. Their p-values are conditional directional-null diagnostics, not proof that the market is stationary or an option premium would profit.',
        '', '## Router and chronological adaptation', 'The fixed router gives EMA priority over Donchian, then pullback when signals coincide. It holds one position for60minutes; no new entry before exit. Only the predefined afternoon trend state is eligible. It does not add the individual strategy profits.',
        '',f"The monthly past-only selector chooses among fixed three rules using the preceding120 completed sessions, requiring30 trades and positive mean after5 points; otherwise it abstains. Final result: N={walk_result.get('n',0)}, net2={walk_result.get('net2',0):.2f}. This is a new retrospective policy, not a prospective test.",
        '', '## Full diagnostics', 'All36 ablations, all-history year/quarter diagnostics, final-period side/month breakdowns, exact trade ledger and monthly selection decisions are exported. No candidate is promoted from those tables. Removing a profitable outlier is a stress test, not a reason to exclude the original trade from the official result.',
        '',f"Verification: {checks} exact timing, source-price, holding-period, nonoverlap, signed-PnL, phase-one reconciliation and feature-prefix assertions passed. Data hashes and script version are in the preregistration.",
        '', 'Future rules must be frozen and tested on new market data, with actual option contracts and executable premium prices before profitability claims.']
    (OUT/f'{prefix}-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'label':args.label,'sessions':len(days),'finalists':[{k:r[k] for k in ['strategy','n','net2','excess_momentum','passes_conditional6_gate']} for r in primary],'walkforward':walk_result,'assertions':checks},default=str))


if __name__=='__main__':main()
