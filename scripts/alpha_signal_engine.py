"""Read-only Project Alpha diagnostic engine. No live strategy passed validation."""
import argparse,hashlib,json,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'backend'),str(ROOT/'scripts')]
import research_directional_lab as lab
CONFIG=ROOT/'artifacts'/'project_alpha'/'alpha-config.json'


def _evaluate_rules(candles,at,market_status='UNKNOWN',config=None):
    cfg=config or json.loads(CONFIG.read_text());at=pd.Timestamp(at)
    if at.tzinfo is None:raise ValueError('Timezone-aware decision timestamp required')
    at=at.tz_convert('Asia/Kolkata')
    result={'at':at.isoformat(),'configuration_version':cfg['version'],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'deployment':'RESEARCH ONLY','action':'NO TRADE',
        'candidate_action':None,'regime':'unknown','selected_rule':None,'selected_contract':None,'entry_price':None,'planned_stop':None,
        'lots':0,'maximum_planned_risk_rupees':None,'reasons':['historical_and_forward_acceptance_not_passed'],'broker_order_sent':False}
    try:d=pd.DataFrame(candles)
    except (ValueError,TypeError):result['reasons'].append('malformed_candles');return result
    if d.empty:result['reasons'].append('no_completed_candles');return result
    if not {'ts','open','high','low','close'}.issubset(d):result['reasons'].append('malformed_candles');return result
    d['ts']=pd.to_datetime(d.ts,utc=True,errors='coerce').dt.tz_convert('Asia/Kolkata')
    for c in ['open','high','low','close']:d[c]=pd.to_numeric(d[c],errors='coerce')
    if d.ts.isna().any():result['reasons'].append('invalid_candle_timestamp');return result
    d=d[d.ts+pd.Timedelta(minutes=5)<=at].sort_values('ts',kind='stable').copy()
    if d.empty:result['reasons'].append('no_completed_candles');return result
    if (d.groupby('ts')[['open','high','low','close']].nunique(dropna=False)>1).any().any():result['reasons'].append('conflicting_duplicate_candles');return result
    if ((d.ts.dt.minute%5!=0)|(d.ts.dt.second!=0)|(d.ts.dt.microsecond!=0)).any():result['reasons'].append('misaligned_candle_clock');return result
    d=d.drop_duplicates('ts')
    d=d[(d.ts.dt.hour*60+d.ts.dt.minute>=555)&(d.ts.dt.hour*60+d.ts.dt.minute<910)].copy();d['day']=d.ts.dt.strftime('%Y-%m-%d')
    if d.empty:result['reasons'].append('no_regular_research_bars');return result
    day=at.strftime('%Y-%m-%d')
    complete=[session for session,g in d.groupby('day') if session==day or list(g.ts.dt.hour*60+g.ts.dt.minute)==list(range(555,910,5))]
    d=d[d.day.isin(complete)]
    if d.empty:result['reasons'].append('no_complete_context_sessions');return result
    f=lab.features(d.reset_index(drop=True));r=f.iloc[-1];day=at.strftime('%Y-%m-%d')
    if r.day!=day or not 0<=(at-r.known_at).total_seconds()<=60:result['reasons'].append('stale_signal_bar')
    if at>r.known_at+pd.Timedelta(seconds=2):result['reasons'].append('missed_entry_decision_deadline')
    if at+pd.Timedelta(minutes=60)>at.replace(hour=15,minute=10,second=0,microsecond=0):result['reasons'].append('actual_exit_after_research_cutoff')
    today=f[f.day==day]
    if not today.empty and (today.ts.iloc[0].hour*60+today.ts.iloc[0].minute!=555 or not today.ts.diff().dropna().eq(pd.Timedelta(minutes=5)).all()):result['reasons'].append('missing_session_candles')
    if not (np.isfinite(f[['open','high','low','close']]).all().all() and (f.low>0).all() and (f.high>=f[['open','low','close']].max(axis=1)).all() and (f.low<=f[['open','high','close']].min(axis=1)).all()):result['reasons'].append('invalid_price_data')
    if market_status!='NORMAL_OPEN':result['reasons'].append('market_not_normal_open')
    clock=at.strftime('%H:%M')
    if not '13:05'<=clock<='14:10':result['reasons'].append('outside_entry_window')
    if pd.isna(r.efficiency) or pd.isna(r.atr) or r.atr<=0:result['reasons'].append('indicator_warmup_missing');return result
    trend=bool(r.efficiency>=.35 and abs(r.trend)>=.5)
    result['regime']='uptrend' if trend and r.trend>0 else 'downtrend' if trend else 'range' if r.efficiency<.25 else 'transition'
    result['features']={key:float(r[key]) for key in ['atr','efficiency','trend','ema9','ema12','ema21','ema26']}
    side=0;chosen=None
    if trend:
        gap=(r.ema12-r.ema26)/r.atr
        if abs(gap)>.5:side=1 if gap>0 else -1;chosen=cfg['research_profiles'][0]['rule']
        elif r.close>r.high20 or r.close<r.low20:side=1 if r.close>r.high20 else -1;chosen=cfg['research_profiles'][1]['rule']
        elif r.ema9>r.ema21 and r.low<=r.ema9+.75*r.atr and r.close>r.ema9 and r.close>r.open:side=1;chosen=cfg['research_profiles'][2]['rule']
        elif r.ema9<r.ema21 and r.high>=r.ema9-.75*r.atr and r.close<r.ema9 and r.close<r.open:side=-1;chosen=cfg['research_profiles'][2]['rule']
    if side:
        result['selected_rule']=chosen
        if result['reasons']==['historical_and_forward_acceptance_not_passed']:
            result['candidate_action']='BUY CE' if side==1 else 'BUY PE'
    else:result['reasons'].append('no_frozen_candidate_setup')
    # Candles may show a research candidate; a failed acceptance gate always wins.
    return result


def evaluate(candles,at,market_status='UNKNOWN',config=None,market_snapshot=None,scoring_evidence=None):
    """Attach holistic assessments while retaining frozen execution gates.

    Historical diagnostics must supply their own as-of market snapshot; a
    current dashboard is never substituted for missing historical inputs.
    """
    result=_evaluate_rules(candles,at,market_status,config)
    from app.services.strategy_evaluation import evaluate_market
    assessment=evaluate_market(candles,market_snapshot or {},at,
        session_phase='open' if market_status=='NORMAL_OPEN' else 'unknown',evidence=scoring_evidence)
    assessment.pop('generated_at',None)
    result['strategy_assessment']=assessment
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--candles',type=Path);p.add_argument('--at');p.add_argument('--live',action='store_true');p.add_argument('--output',type=Path)
    p.add_argument('--market-snapshot',type=Path,help='Historically available NIFTY dashboard snapshot; never join current context into a past decision')
    p.add_argument('--weight-evidence',type=Path,help='Dated chronological incremental-validation artifact')
    a=p.parse_args()
    status='UNKNOWN'
    snapshot=json.loads(a.market_snapshot.read_text(encoding='utf-8')) if a.market_snapshot else {}
    weight_evidence=json.loads(a.weight_evidence.read_text(encoding='utf-8')) if a.weight_evidence else None
    if a.live:
        from app.config import get_settings
        from upstox_analytics import UpstoxAnalyticsClient
        now=datetime.now(timezone.utc);local=now.astimezone(timezone(timedelta(hours=5,minutes=30)))
        client=UpstoxAnalyticsClient(get_settings().upstox_analytics_token,timeout=15,max_retries=0)
        try:
            candles=client.get_historical_candles_v3('NSE_INDEX|Nifty 50','minutes',5,local.date().isoformat(),(local.date()-timedelta(days=27)).isoformat())['candles']
            candles=[dict(zip(['ts','open','high','low','close','volume','oi'],row)) for row in candles]
            status=client.get_market_status('NSE').get('status','UNKNOWN');at=now
        except Exception as exc:
            result={'action':'NO TRADE','deployment':'RESEARCH ONLY','reasons':['provider_unavailable',type(exc).__name__],'broker_order_sent':False}
            if a.output:a.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
            print(json.dumps(result));return
    else:
        path=a.candles or ROOT/'artifacts'/'directional_research'/'nifty-upstox-5minute.json';candles=json.loads(path.read_text())
        at=a.at or '2026-11-06T13:05:00+05:30'
    if a.live and not a.market_snapshot:
        from app.services.nifty_service import get_nifty_service
        from app.services.strategy_evaluation import load_weight_evidence
        try:snapshot=get_nifty_service().dashboard(auto_refresh=False)
        except Exception:snapshot={'sections':[],'source_errors':[{'source':'NIFTY context','error':'Context unavailable at live decision'}]}
        if not a.weight_evidence:weight_evidence,_=load_weight_evidence()
        at=datetime.now(timezone.utc)
    result=evaluate(candles,at,status,market_snapshot=snapshot,scoring_evidence=weight_evidence)
    result['input_sha256']=hashlib.sha256(json.dumps(candles,sort_keys=True).encode()).hexdigest()
    result['market_snapshot_sha256']=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
    if a.output:
        a.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
        if a.live:a.output.with_suffix('.inputs.json').write_text(json.dumps({'at':str(at),'market_status':status,'candles':candles,'market_snapshot':snapshot,'scoring_evidence':weight_evidence}),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
