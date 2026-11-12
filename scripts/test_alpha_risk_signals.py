"""Meaningful fail-closed and risk-headroom regression checks; fixtures are not trades."""
import json,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from alpha_signal_engine import evaluate
from research_alpha_metrics import simulate


def main():
    rows=json.loads((ROOT/'artifacts'/'directional_research'/'nifty-upstox-5minute.json').read_text())
    at='2026-11-06T13:05:00+05:30';checks=[]
    assert evaluate([],at)['action']=='NO TRADE';checks.append('empty source abstains')
    assert evaluate([{'bad':1}],at)['action']=='NO TRADE';checks.append('malformed source abstains')
    base=evaluate(rows,at,'NORMAL_OPEN');assert base['action']=='NO TRADE' and base['candidate_action']=='BUY CE';checks.append('research candidate cannot override unpassed acceptance')
    prefix=[r for r in rows if pd.Timestamp(r['ts'])+pd.Timedelta(minutes=5)<=pd.Timestamp(at)]
    assert evaluate(prefix,at,'NORMAL_OPEN')==base;checks.append('future candles do not affect current decision')
    assert evaluate(rows,'2026-11-06T14:10:30+05:30','NORMAL_OPEN')['candidate_action'] is None;checks.append('late entry cannot breach15:10exit')
    bad={**prefix[-1],'close':float(prefix[-1]['close'])+.01}
    assert 'conflicting_duplicate_candles' in evaluate(prefix+[bad],at,'NORMAL_OPEN')['reasons'];checks.append('conflicting revision rejected')
    assert evaluate(rows,at,'CLOSED')['candidate_action'] is None;checks.append('closed market suppresses candidate')
    assert evaluate(rows,'2026-11-07T13:05:00+05:30','NORMAL_OPEN')['candidate_action'] is None;checks.append('stale prior session suppresses candidate')
    fixture=pd.DataFrame([{'entry_at':f'2026-11-06T{h}:00:00+05:30','exit_at':f'2026-11-06T{h}:30:00+05:30','premium_entry':100,'lot':65,'planned_stop_loss_rupees':500,'severe_net_rupees_per_lot':-900} for h in ['10','11','12']])
    taken,skips=simulate(fixture,250000,.005)
    assert len(taken)==2 and sum(r['net'] for r in taken)==-1800;checks.append('remaining daily planned risk prevents third entry')
    taken,skips=simulate(fixture,100000,.0025)
    assert not taken and skips['minimum_lot_exceeds_risk_or_cash']==3;checks.append('minimum lot above risk budget abstains')
    f=fixture.iloc[:1].copy();f['premium_entry']=100000/65;f['planned_stop_loss_rupees']=1
    taken,_=simulate(f,100000,.005);assert not taken;checks.append('cash must fund premium and full reserved fee allowance')
    result={'passed':len(checks),'checks':checks,'synthetic_risk_fixtures_only':True}
    (ROOT/'artifacts'/'project_alpha'/'risk-signal-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))


if __name__=='__main__':main()
