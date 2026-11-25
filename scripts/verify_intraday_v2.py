"""Independent arithmetic/ledger audit of saved results, not model reruns."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import json
import numpy as np
import pandas as pd
from research.intraday_momentum import data as base
from research.intraday_momentum_v2.data import OUT
from scripts.run_intraday_momentum_v2 import hashes


def independent_fee(side,price,q):
    value=price*q;broker=min(20,.001*value);exchange=.0000307*value;sebi=.000001*value
    return dict(brokerage=broker,exchange_ipft=exchange,sebi=sebi,gst=.18*(broker+exchange+sebi),
        stt=.00025*value if side=='SELL' else 0,stamp=.00003*value if side=='BUY' else 0,dp=0)


def main():
    report=json.loads((OUT/'report.json').read_text());assert hashes()==report['manifest']['code'],'Code changed'
    assert base.sha(OUT/'jobs-plan.json')==report['manifest']['plan_sha256']
    assert base.sha(OUT/'acquisition-manifest.json')==report['manifest']['acquisition_sha256']
    trades=pd.read_csv(OUT/'trades.csv');daily=pd.read_csv(OUT/'daily-equity.csv');errors=[];maxdelta=0.
    def close(a,b,label):
        nonlocal maxdelta
        delta=abs(float(a)-float(b));maxdelta=max(maxdelta,delta)
        if delta>max(.00001,abs(float(b))*1e-10):errors.append(dict(check=label,a=float(a),b=float(b)))
    for row in trades.to_dict('records'):
        side=1 if row['side']=='LONG' else -1;q=int(row['quantity']);assert q>0 and q==row['quantity']
        ef=json.loads(row['entry_fee_components']);xf=json.loads(row['exit_fee_components']);enter='BUY' if side==1 else 'SELL';exit='SELL' if side==1 else 'BUY'
        for name,observed,typ,p in [('entry',ef,enter,row['entry_price']),('exit',xf,exit,row['exit_price'])]:
            expected=independent_fee(typ,p,q)
            for key,value in expected.items():close(observed[key],value,name+' '+key)
            close(observed['total'],sum(expected.values()),name+' total')
        close(row['gross_pnl'],side*(row['exit_price']-row['entry_price'])*q,'gross')
        close(row['net_pnl'],row['gross_pnl']-ef['total']-xf['total'],'net')
        close(row['gross_before_slippage'],side*(row['raw_exit_price']-row['raw_entry_price'])*q,'rawgross')
        close(row['slippage_rupees'],(abs(row['entry_price']-row['raw_entry_price'])+abs(row['exit_price']-row['raw_exit_price']))*q,'slippage')
        assert row['entry_price']*q+ef['total']<=row['equity_before']+.0001
        assert str(row['session']).startswith(('2025','2026'))
        assert row['decision_bar_participation']<=.01+1e-9
    counts={}
    for name,days in daily.groupby('strategy'):
        ts=trades.loc[trades.strategy.eq(name)].sort_values('entry_at');days=days.sort_values('session');counts[name]=len(ts)
        assert ts.groupby('session').size().max()<=3 if len(ts) else True
        assert (ts.groupby(['session','instrument_key']).size()<=1).all()
        for a,b in zip(ts.to_dict('records'),ts.to_dict('records')[1:]):
            assert pd.Timestamp(b['entry_at'])>=pd.Timestamp(a['capital_released_at'])
            close(b['equity_before'],a['equity_after'],'successive cash')
        for row in days.to_dict('records'):
            close(row['pnl'],ts.loc[ts.session.eq(row['session']),'net_pnl'].sum(),'day pnl')
        close(days.iloc[-1].equity,1e6+ts.net_pnl.sum(),'terminal')
        for m in [m for m in report['metrics'] if m['strategy']==name]:
            first,last=report['manifest']['periods'][m['period']];part=ts.loc[ts.session.between(first,last)];d=days.loc[days.session.between(first,last)]
            assert m['trades']==len(part);close(m['net_pnl'],part.net_pnl.sum(),'summarynet')
            close(m['fees'],part.fees.sum(),'summaryfees');close(m['total_return'],np.prod(1+d.return_fraction)-1,'summaryreturn')
            if len(part):close(m['mean_net_bps_per_trade'],(part.net_pnl/(part.entry_price*part.quantity)*1e4).mean(),'summarybps')
            positive=part.loc[part.net_pnl>0,'net_pnl'].sum();negative=-part.loc[part.net_pnl<0,'net_pnl'].sum()
            if negative:close(m['profit_factor'],positive/negative,'PF')
    for f in ('stress','capacity-and-latency'):
        csv=pd.read_csv(OUT/(f+'.csv'));assert len(csv)==len(report['stress' if f=='stress' else 'additional_selected_stress'])
    result=dict(status='PASS' if not errors else 'FAIL',portfolios=len(counts),ledger_rows=len(trades),summary_rows=len(report['metrics']),
        stress_rows=len(report['stress']),capacity_latency_rows=len(report['additional_selected_stress']),max_numeric_delta=maxdelta,errors=errors,
        observed_2025_2026_only=True,code_source_hashes_match=True,real_orders_submitted=0,
        limitation='Base ledgers independently recomputed. Stress CSV/report rows checked for completeness; stress individual ledgers not retained/re-audited.')
    base.dump(OUT/'independent-audit.json',result);print(json.dumps(result,indent=2));assert not errors


if __name__=='__main__':main()
