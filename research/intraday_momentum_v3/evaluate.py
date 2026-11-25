"""Prespecified future-only assessment. Missing evidence cannot qualify."""
from collections import Counter
import gzip,json,math
import numpy as np
from .common import OUT,dump,sha,now
from .features import timestamp
from .model import load,panel


def day_bound(values,seed=301):
    """Resample whole observed days, preserving within-day dependence."""
    a=np.asarray(values,float)
    if len(a)<30:return None
    rng=np.random.default_rng(seed);means=np.array([rng.choice(a,len(a),replace=True).mean() for _ in range(10000)])
    return dict(mean=float(a.mean()),lower_one_sided_98_75=float(np.quantile(means,.0125)),
                upper_percentile_98_75=float(np.quantile(means,.9875)),days=len(a),bootstrap_samples=10000)


def events():
    for p in sorted((OUT/'runs').glob('*/derived-events.jsonl.gz')):
        manifest=json.loads((p.parent/'manifest.json').read_text())
        if manifest.get('protocol_sha256')!=sha(OUT/'protocol-frozen.json'):continue
        with gzip.open(p,'rt',encoding='utf-8') as stream:
            for line in stream:yield json.loads(line)


def assess():
    ready=json.loads((OUT/'forward-readiness.json').read_text());m=load()
    days=sorted({r['session'] for r in ready['sessions'] if r['transport']=='ws' and r['quality_pass']})
    result=dict(checked_at=now().isoformat(),status='FORWARD_DATA_REQUIRED',quality_sessions=len(days),
        models_available=bool(m),profitability_demonstrated=False,primary_claims=4,scheduling_enabled=False,real_orders=0)
    if not m or len(days)<60:
        result['reason']='Need60 fresh quality sessions, first20 training and at least40 subsequent evaluation sessions; scope ends2026-12-31.'
        dump(OUT/'evaluation-status.json',result);return result
    data=panel();targets=data[~data.is_control] if len(data) else data
    if len(targets)<1000 or targets.session.nunique()<50:
        result.update(reason='Need1000 within-stock embargoed targets across50 days; events across stocks are not independent',target_episodes=len(targets));dump(OUT/'evaluation-status.json',result);return result
    calibration_path=OUT/'execution-calibration.json';lock_path=OUT/'execution-calibration-freeze.json'
    if not calibration_path.exists() or not lock_path.exists() or json.loads(lock_path.read_text()).get('sha256')!=sha(calibration_path):
        result['reason']='Frozen training-only quote-cost calibration is required';dump(OUT/'evaluation-status.json',result);return result
    calibration=json.loads(calibration_path.read_text())
    if calibration.get('model_sha256')!=sha(OUT/'frozen-forward-model.json'):
        raise RuntimeError('Calibration/model identity mismatch')
    uncertainty=calibration['uncertainty_bps'];edge=max(5,2*uncertainty);evaluation=[d for d in days if d>m['training_end']][:40]
    if len(evaluation)<40:
        result['reason']='Fewer than40 post-training quality sessions';dump(OUT/'evaluation-status.json',result);return result
    candidates={};outcomes={};costs={};ledger=[];marks=[];unresolved=[]
    for r in events():
        if r['kind']=='candidate':candidates[r['episode_id']]=r
        elif r['kind']=='diagnostic_entry_cost':costs[r['episode_id']]=r
        elif r['kind']=='observed_outcome' and r.get('horizon_seconds')==900 and r.get('status')=='OBSERVED':outcomes[r['episode_id']]=r
        elif r['kind']=='shadow_ledger':
            if r['status']=='HYPOTHETICAL_CLOSED':ledger.append(r)
            elif r['status']=='HYPOTHETICAL_MARK':marks.append(r)
            elif 'UNRESOLVED' in r['status'] or 'UNPRICED' in r['status']:unresolved.append(r)
    metrics={};missing=Counter();included=set(targets.episode_id)
    for family in ('H3-A','H3-B','H3-C'):
        rows=[]
        for ident,c in candidates.items():
            day=timestamp(c['at']).astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date().isoformat()
            if c['family']!=family or ident not in included or day not in evaluation:continue
            p=c.get('paired_model_predictions') or {};cost=(costs.get(ident,{}).get('cost') or {});out=outcomes.get(ident,{}).get('net_quote_markout') or {}
            if set(p)!=set(('P','PV','PVD')) or cost.get('status')!='QUOTED_BOUND_ONLY' or out.get('status')!='QUOTED_BOUND_ONLY':missing[family]+=1;continue
            base=c['volume_confirmation'] and p['PV']+cost['net_bps']>edge
            enhanced=c['volume_confirmation'] and c['depth_confirmation'] and p['PVD']+cost['net_bps']>edge
            rows.append(dict(day=day,net=out['net_bps'],side=c['side'],increment=(int(enhanced)-int(base))*out['net_bps'],
                selected=enhanced,pv_selected=base,extra_5bps_net=out['net_bps']-8))
        daily=[sum(r['increment'] for r in rows if r['day']==d)/max(1,sum(r['day']==d for r in rows)) for d in evaluation]
        bound=day_bound(daily);mean=float(np.mean([r['increment'] for r in rows])) if rows else None
        selected=[r for r in rows if r['selected']]
        metrics[family]=dict(common_events=len(rows),missing_or_unfilled=missing[family],selected=len(selected),
            mean_increment_bps=mean,day_cluster_bound=bound,long_events=sum(r['side']==1 for r in rows),short_events=sum(r['side']==-1 for r in rows),
            selected_mean_net_bps=float(np.mean([r['net'] for r in selected])) if selected else None,
            selected_5bps_side_stress_mean=float(np.mean([r['extra_5bps_net'] for r in selected])) if selected else None,
            qualified=bool(len(rows)>=100 and len({r['day'] for r in rows})>=30 and bound and bound['lower_one_sided_98_75']>0 and mean>edge))
    def day_of(r):return timestamp(r['at']).astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date().isoformat()
    trades=[r for r in ledger if day_of(r) in evaluation];returns=[sum(r['net_pnl'] for r in trades if day_of(r)==d)/1e6 for d in evaluation]
    pnl=np.array([r['net_pnl'] for r in trades]);profit=float(pnl[pnl>0].sum());loss=float(-pnl[pnl<0].sum());pf=profit/loss if loss else None
    equity=np.r_[1.,1+np.cumsum(returns)];eod_dd=float(np.min(equity/np.maximum.accumulate(equity)-1));bound=day_bound(returns)
    concentration=float(np.sort(pnl[pnl>0])[-5:].sum()/profit) if profit else None
    worst=min(returns);intraday=min((r['max_intraday_drawdown'] for r in marks if day_of(r) in evaluation),default=None)
    uncertain=[r for r in unresolved if 'at' in r and day_of(r) in evaluation]
    portfolio=dict(closed_trades=len(trades),active_days=len({day_of(r) for r in trades}),profit_factor=pf,funded_return=float(equity[-1]-1),
        worst_day=worst,max_eod_drawdown=eod_dd,max_intraday_drawdown=intraday,top5_positive_pnl_concentration=concentration,
        day_cluster_bound=bound,unpriced_or_unresolved_events=len(uncertain),entry_cap_violations=max(Counter(day_of(r) for r in trades).values(),default=0)>3)
    portfolio['qualified']=bool(len(trades)>=75 and portfolio['active_days']>=30 and pf is not None and pf>=1.2 and bound and bound['lower_one_sided_98_75']>0
        and worst>=-.02 and eod_dd>=-.15 and intraday is not None and intraday>=-.15 and concentration is not None and concentration<=.5 and not uncertain and not portfolio['entry_cap_violations'])
    result.update(status='ASSESSMENT_COMPLETE',evaluation_sessions=evaluation,family_metrics=metrics,shared_portfolio=portfolio,
        profitability_demonstrated=portfolio['qualified'] and all(x['qualified'] for x in metrics.values()),
        interpretation='Prespecified quote-bound research assessment; no broker fills or real trading approval. H3-C reversal and avoided continuation are opposite signed outcomes; no independent extra hypothesis.')
    dump(OUT/'evaluation-status.json',result);return result


if __name__=='__main__':print(json.dumps(assess(),indent=2))
