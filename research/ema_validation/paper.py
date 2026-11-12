"""Append-only local paper ledger. Consumes verified completed bars, no broker API."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from research.ema_validation.engine import ROOT,OUT,prepare,orders,simulate,cache_correlations,fee_coeff,save
from research.swing_discovery.signals import build_features,generate
from research.swing_diagnosis.common import clean

START='2026-11-12'
CODE=[ROOT/'research/ema_validation/paper.py',ROOT/'research/ema_validation/engine.py',ROOT/'research/swing_discovery/signals.py']

def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in CODE}

def init(base=None):
    base=Path(base or OUT/'paper');base.mkdir(exist_ok=True,parents=True)
    file=base/'frozen.json'
    if file.exists():
        frozen=json.loads(file.read_text());assert frozen['source_hashes']==hashes(),'Frozen code changed';return frozen
    study=json.loads((OUT/'freeze.json').read_text())
    frozen=dict(created_utc=datetime.now(timezone.utc).isoformat(),client_start_date=START,initial_cash=1e6,configuration=study['config'],source_hashes=hashes(),
      study_freeze_sha256=hashlib.sha256((OUT/'freeze.json').read_bytes()).hexdigest(),
      inputs=study['inputs'],first_signal_policy='First completed decision close on/after12Nov2026, earliestfollowing observedopen. No prestart positions or retrospective performance.',
      paper_execution='Hypothetical next daily open with frozen adverse slippage/fees; cannot certify quotes or broker fills. Previous signal must have been received before entry-session09:15IST.',
      feed='Verified actual-unit unadjustedOHLC and sharevolume, complete frozen470company universe, NIFTYclose, explicit corporateaction factors/dividends. Missing/ambiguousdata failclosed; no orderrouting.')
    file.write_text(json.dumps(clean(frozen),indent=2));(base/'inputs').mkdir(exist_ok=True)
    (base/'state.json').write_text(json.dumps(dict(status='awaiting_verified_completed_bars',cash=1e6,equity=1e6,positions=[],trades=0,first_signal_date=START),indent=2))
    (base/'events.jsonl').write_text(json.dumps({'event':'initialized','utc':frozen['created_utc'],'equity':1e6})+'\n')
    return frozen

def validate_payload(payload,symbols,now=None):
    now=pd.Timestamp(now or datetime.now(timezone.utc));now=now.tz_localize('UTC') if now.tzinfo is None else now.tz_convert('UTC')
    day=pd.Timestamp(payload['date']);close=(day+pd.Timedelta(hours=15,minutes=30)).tz_localize('Asia/Kolkata')
    if close>now:raise ValueError('Session has not completed; no unfinished candles')
    if payload.get('price_basis')!='actual_unadjusted' or not payload.get('corporate_actions_verified') or not payload.get('source') or not payload.get('calendar_source') or not payload.get('previous_session_date'):
        raise ValueError('Verified actual-price basis, action review and source required')
    if set(payload['bars'])!=set(symbols):raise ValueError('Require complete frozen eligible-stock bars')
    for symbol,row in payload['bars'].items():
        x=[float(row[k]) for k in ['open','high','low','close','volume','split_factor','dividend']]
        o,h,l,c,v,f,d=x
        if not np.isfinite(x).all() or min(o,h,l,c)<=0 or h<max(o,l,c) or l>min(o,h,c) or v<0 or f<=0 or d<0:raise ValueError('Invalid bar/action '+symbol)
        if abs(f-round(f))>1e-9:raise ValueError('Fractional/ambiguous corporate action requires a separately approved model')
    if not np.isfinite(payload['nifty_close']) or payload['nifty_close']<=0:raise ValueError('Invalid NIFTY completedclose')

def rebuild(q,payloads):
    p=q['p'];p={**p,'actual':{k:v.copy() for k,v in p['actual'].items()},'neutral':{k:v.copy() for k,v in p['neutral'].items()}}
    eligible=np.flatnonzero(p['eligible']);index={s:i for i,s in enumerate(p['symbols'])}
    for payload in payloads:
        day=pd.Timestamp(payload['date'],tz=p['dates'].tz)
        if day<=p['dates'][-1]:raise ValueError('Input must strictly append observed sessions')
        factors=np.ones(len(index));divs=np.zeros(len(index));new={k:np.full(len(index),np.nan) for k in p['actual']}
        for symbol,row in payload['bars'].items():
            s=index[symbol];factors[s]=row['split_factor'];divs[s]=row['dividend']
            for k in new:new[k][s]=row[k]
        unit=p['unit_factor'][:,-1]/factors
        # Frozen liquidity hypothesis uses neutral-share volume; feed supplies realsharevolume.
        new['volume']*=unit
        for k in p['actual']:
            p['actual'][k]=np.column_stack([p['actual'][k],new[k]])
            z=new[k] if k=='volume' else new[k]/unit
            p['neutral'][k]=np.column_stack([p['neutral'][k],z])
        for k,v in [('unit_factor',unit),('split_factor',factors),('dividend',divs)]:p[k]=np.column_stack([p[k],v])
        p['dates']=p['dates'].append(pd.DatetimeIndex([day]));p['niftyclose']=np.r_[p['niftyclose'],payload['nifty_close']]
    p['nifty']=p['niftyclose']
    median=lambda v:pd.DataFrame(v.T).rolling(20,min_periods=20).median().shift(1).to_numpy().T
    p['liquidity_volume']=median(p['actual']['volume'])/p['unit_factor'];p['liquidity_turnover']=median(p['neutral']['close']*p['actual']['volume'])
    f=build_features(p);sig=generate(p,q['cfg'],f);c=p['neutral']['close'];r=c/np.roll(c,1,axis=1)-1;r[:,0]=np.nan
    ratio=pd.Series(p['niftyclose']).pct_change();gate=(ratio.rolling(20).std()/ratio.rolling(60).std()>1.2).to_numpy();rank=[]
    for t in range(len(p['dates'])):
        score=c[:,max(0,t-1)]/c[:,max(0,t-61)]-1
        rank.append(np.asarray(sorted(range(len(c)),key=lambda s:(-score[s] if np.isfinite(score[s]) else np.inf,p['symbols'][s]))))
    q={**q,'p':p,'sig':sig,'returns':r,'gate':gate,'ranks':rank,'fee':[fee_coeff(d,True,False) for d in p['dates']],
      'sellfee':[fee_coeff(d,False,True) for d in p['dates']],'corr':{},'cols':np.flatnonzero(p['dates']>=pd.Timestamp(START,tz=p['dates'].tz))}
    return q

def record(input_path,base=None):
    base=Path(base or OUT/'paper');frozen=init(base);raw=Path(input_path).read_bytes();payload=json.loads(raw);q=prepare();p=q['p']
    for name,expected in frozen['inputs'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError('Frozen historical input changed: '+name)
    symbols=[s for s,ok in zip(p['symbols'],p['eligible']) if ok];validate_payload(payload,symbols)
    target=base/'inputs'/(payload['date']+'.json')
    if target.exists():
        if target.read_bytes()!=raw:raise ValueError('Append-only snapshot cannot be revised')
        return json.loads((base/'state.json').read_text())
    old=sorted((base/'inputs').glob('*.json'));past=[json.loads(x.read_text()) for x in old]
    if past and payload['date']<=past[-1]['date']:raise ValueError('Date must append ledger')
    previous=past[-1]['date'] if past else str(p['dates'][-1].date())
    if payload['previous_session_date']!=previous:raise ValueError('Missing observed-session bridge; feed each actual session in order')
    # Executions may only follow a decision actually recorded before that opening.
    receipts=[json.loads(x) for x in (base/'events.jsonl').read_text().splitlines()]
    if payload['date']>=START and past and past[-1]['date']>=START:
        received=[x for x in receipts if x.get('event')=='completed_bar'][-1]['utc']
        if pd.Timestamp(received)>=pd.Timestamp(payload['date']+' 09:15',tz='Asia/Kolkata'):
            raise ValueError('Prior decision was not recorded before current open; cannot backfill prospective trades')
    # A verified feed must bridge every actual session since the frozenNov9panel.
    q=rebuild(q,past+[payload]);cache_correlations(q)
    state=dict(status='warmup_bridge_only',cash=1e6,equity=1e6,positions=[],trades=0,last_completed_date=payload['date'])
    result=None
    if len(q['cols']):
        end=str((q['p']['dates'][-1]+pd.Timedelta(days=1)).date());entry=q['sig']['entry']&q['gate'][None,:]&q['p']['eligible'][:,None]
        result=simulate(q,orders(q,entry),START,end,force_end=False)
        pending=[q['p']['symbols'][s] for s in np.flatnonzero(entry[:,-1])]
        state=dict(status='recording_hypothetical_daily_execution',last_completed_date=payload['date'],cash=result['cash'][-1],equity=result['equity'][-1],
          positions=[dict(symbol=q['p']['symbols'][s],**z) for s,z in result['open_positions'].items()],closed_trades=len(result['trades']),
          pending_next_open_candidates=pending,gate_active=bool(q['gate'][-1]),configuration_sha256=hashlib.sha256((base/'frozen.json').read_bytes()).hexdigest())
    # Save immutable receipt before publishing mutable latest-view state.
    target.write_bytes(raw);utc=datetime.now(timezone.utc).isoformat()
    with (base/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'event':'completed_bar','date':payload['date'],'utc':utc,'sha256':hashlib.sha256(raw).hexdigest()})+'\n')
    (base/'state.json').write_text(json.dumps(clean(state),indent=2))
    if result is not None:
        np.savez_compressed(base/(payload['date']+'-paper-path.npz'),**{k:result[k] for k in ['equity','cash','utilization','positions','trades','cols']})
    return clean(state)

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['init','record','status']);parser.add_argument('--input');args=parser.parse_args()
    if args.action=='init':init();print('Frozen paper ledger initialized; awaiting verified completed bars.')
    elif args.action=='record':print(json.dumps(record(args.input),indent=2))
    else:
        init();print((OUT/'paper/state.json').read_text())

if __name__=='__main__':main()
