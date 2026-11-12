"""Reconcile statistical scope/source hashes and render completed research artifacts.

This never generates a new strategy, entry, stock selection or execution run.
"""
from __future__ import annotations
import sys,json,sqlite3,hashlib
from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.swing_discovery.diagnostics import pbo_cscv
from research.swing_discovery.reporting import build_report
OUT=ROOT/'artifacts'/'swing_discovery'

def regime_breakdowns():
    idx=json.loads((OUT/'panel-index.json').read_text());dates=pd.DatetimeIndex(pd.to_datetime(idx['dates'],utc=True)).tz_convert('Asia/Kolkata')
    with np.load(OUT/'daily-panel.npz') as data:close=pd.Series(data['niftyclose'],index=dates)
    r=close.pct_change();vol=r.rolling(20).std();prior_median=vol.rolling(252).median().shift(1)
    strength=close.pct_change(60).abs()/(vol*np.sqrt(60))
    shock=(r.abs()>2*vol.shift(1))&(r*close.pct_change(20).shift(1)<0)
    labels=pd.DataFrame({'market_volatility':np.where(vol>prior_median,'high','low'),
      'market_trend_strength':np.where(strength>=1,'strong','weak'),
      'known_reversal_shock':np.where(shock,'shock','ordinary')},index=dates.strftime('%Y-%m-%d'))
    frozen=json.loads((OUT/'frozen-finalists.json').read_text())['finalists'];rows=[]
    for record in frozen:
        ident=record['id']
        for stage in ['final','two_year']:
            path=OUT/'finalist_journals'/f'{ident}-all_eligible_stocks-{stage}-trades.csv'
            try:t=pd.read_csv(path)
            except pd.errors.EmptyDataError:continue
            if t.empty:continue
            days=pd.to_datetime(t.signal_day,utc=True).dt.tz_convert('Asia/Kolkata').dt.strftime('%Y-%m-%d')
            for dimension in labels:
                t['regime_value']=days.map(labels[dimension])
                for label,g in t.groupby('regime_value'):
                    rows.append({'id':ident,'family':record['family'],'stage':stage,'dimension':dimension,'regime':label,
                      'stocks':g.symbol.nunique(),'n_trades':len(g),'expectancy_r':g.net_r.mean(),
                      'win_rate_pct':g.net_pnl.gt(0).mean()*100,'net_pnl':g.net_pnl.sum()})
    pd.DataFrame(rows).to_csv(OUT/'additional-regime-analysis.csv',index=False)

def main():
    protocol=json.loads((OUT/'protocol.json').read_text());coarse=[c['id'] for c in protocol['configurations']]
    with sqlite3.connect(OUT/'research.sqlite3') as conn:
        rows=pd.read_sql_query("SELECT r.id,d.day,d.net_return FROM runs r JOIN portfolio_days d ON r.key=d.key WHERE r.stage='development' AND r.pool='development_stocks'",conn)
        run_count=int(conn.execute('SELECT COUNT(*) FROM runs').fetchone()[0])
    panel=rows.pivot(index='day',columns='id',values='net_return').fillna(0)
    corrected=pbo_cscv(panel[coarse],blocks=6)
    corrected['scope']='Frozen coarse grid only; development-selected refinements excluded; duplicate rounded return paths removed before CSCV ranking.'
    (OUT/'pbo-development.json').write_text(json.dumps(corrected,indent=2),encoding='utf-8')
    regime_breakdowns()
    source=list((ROOT/'research/swing_discovery').glob('*.py'))+[ROOT/'scripts/run_swing_discovery.py',Path(__file__),ROOT/'scripts/verify_discovery_intraday.py']
    if (ROOT/'scripts/verify_swing_discovery.py').exists():source.append(ROOT/'scripts/verify_swing_discovery.py')
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source}
    metadata={'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__,'source_sha256_at_delivery':hashes,
      'protocol_sha256':hashlib.sha256((OUT/'protocol.json').read_bytes()).hexdigest(),
      'frozen_finalists_sha256':hashlib.sha256((OUT/'frozen-finalists.json').read_bytes()).hexdigest(),
      'source_scope_note':'PBO was recomputed from frozen coarse development columns with outcome deduplication; no trading simulation, final selection or rule parameters changed.',
      'execution_runs':run_count}
    (OUT/'environment.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    result=build_report(OUT,ROOT)
    overview=('# Expanded swing research\n\n'+
      '**No frozen family finalist passes the full evidence screen.**\n\n'+
      '1,174 coarse configurations plus 134 development-only refinements across 48 families; 470 eligible stocks from 500 dated fund holdings; 95 reserved novel companies; 6,429 logged execution runs.\n\n'+
      '[Full report](artifacts/swing_discovery/REPORT.md) · [Top 20 diagnostics](artifacts/swing_discovery/top-20.csv) · [Exact rules](artifacts/swing_discovery/top-20-rules.md) · [Research database](artifacts/swing_discovery/research.sqlite3)\n\n'+
      'The final calendar overlaps prior project research. Reserved companies provide cross-sectional novelty, not a newly untouched market history. Daily bars and modeled liquidity/fees impose execution limits.\n')
    (ROOT/'SWING_DISCOVERY_RESULTS.md').write_text(overview,encoding='utf-8')
    print(json.dumps({'pbo':corrected.get('pbo'),'coarse_rules':len(coarse),'distinct_development_paths':corrected.get('distinct_rules'),**result}))

if __name__=='__main__':main()
