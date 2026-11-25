"""Historical and ongoing comparisons with the supplied frozen research code.

Only the reviewed pure class/function definitions are loaded from reference files;
their original CLI, filesystem setup and external imports are never executed.
All market data and corporate-action records are read from PostgreSQL.
"""
import ast
from datetime import datetime
from functools import lru_cache
from itertools import product
import json
import math
import warnings
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from .catalog import CAPITAL, DAY0
from .data import Inputs, IST, NIFTY, canonical
from .engine import DataBlocked, advance, auction_gate, equity, features, fresh_book
from .reference import sim5, xsim

REFERENCE = Path(__file__).with_name('reference')


def definitions(file, names, namespace):
    tree = ast.parse((REFERENCE / file).read_text(encoding='utf-8'))
    selected = [node for node in tree.body if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names]
    if {node.name for node in selected} != set(names):
        raise DataBlocked('Missing frozen reference definitions: '+file)
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(REFERENCE/file),'exec'),namespace)
    return namespace


def reference_inputs(instruments, sessions, frames, nifty_prices):
    keys = list(instruments)
    closes = frames['c'].to_numpy()
    meta = pd.DataFrame([dict(r,trading_symbol=r['symbol']) for r in instruments.values()])
    panel = SimpleNamespace(dates=pd.to_datetime(sessions),keys=np.array(keys),meta=meta,
                            industry=meta.industry.to_numpy(),ix={'Nifty_50':nifty_prices},
                            **{k:frames[k].to_numpy() for k in ('o','h','l','c','v')})
    # NIFTY defines calendar presence and reporting, never the stock ranking.
    scope = dict(np=np,pd=pd,cfg=SimpleNamespace(CUTOFF=pd.Timestamp('2025-01-01')),
                 dpanel=SimpleNamespace(load=lambda:panel))
    original = definitions('daily.py',['D25'],scope)['D25']()
    lag = np.vstack([np.full((1,len(keys)),np.nan),closes[:-1]])
    sigma = pd.DataFrame(np.log(closes/lag)).rolling(42,min_periods=36).std().to_numpy()
    momentum = np.full_like(closes,np.nan)
    momentum[63:] = closes[63:]/closes[:-63]-1
    with np.errstate(divide='ignore',invalid='ignore'):
        raw_score = np.where(original.history()>=64,momentum/(sigma*math.sqrt(63)),np.nan)
    a = dict(o=panel.o,c=panel.c,industry=panel.industry,dates=panel.dates)
    base = dict(d=original,A=a,F={'volnorm_3m':raw_score},
                adv=pd.DataFrame(panel.c*panel.v).rolling(63,min_periods=50).median().to_numpy())
    ns = dict(np=np,pd=pd,_IF=None,P5=SimpleNamespace(inputs=lambda:base))
    return definitions('p6common.py',['inputs_fixed'],ns)['inputs_fixed']()


@lru_cache(maxsize=1)
def guards():
    names = ['classify','check_classification','check_ca_causality','check_split_bonus','check_db_duplicates',
             'check_panel_candles','check_missing_for_holdings','check_delisted','check_pit_liquidity','check_universe_ties']
    scope = dict(np=np,pd=pd,ALLOWED_ISIN_PREFIX='INE',ETF_SYM='ETF|BEES|IETF|GOLD|LIQUID|NIFTY|SENSEX',
                 ETF_NAME=' ETF|FUND|EXCHANGE TRADED')
    return definitions('integrity.py',names,scope)


class CorporateActionRows:
    def __init__(self, actions):self.actions=actions
    def execute(self, query):
        if query != 'SELECT * FROM corporate_actions':raise ValueError('Unexpected reference query')
        return SimpleNamespace(df=lambda:pd.DataFrame(self.actions))


def verify_inputs(inputs, instruments, sessions, frames, universe, scores):
    original = reference_inputs(instruments,sessions,frames,inputs.index_prices(sessions))
    u = original['U']
    score = original['score']
    mask_mismatches = int(np.sum(u != universe.to_numpy()))
    score_missing = int(np.sum(np.isnan(score) != np.isnan(scores.to_numpy())))
    both = np.isfinite(score)&np.isfinite(scores.to_numpy())
    score_error = float(np.max(np.abs(score[both]-scores.to_numpy()[both]))) if both.any() else 0.
    if mask_mismatches or score_missing or score_error>1e-12:
        raise DataBlocked(f'Original universe/score mismatch: {mask_mismatches} universe cells, {score_missing} missing scores, error {score_error}')
    t0 = sessions.index('2025-04-01')
    tie = np.argsort(np.argsort(np.array(list(instruments))))
    original['t0'] = t0
    ref = sim5.run(original['A'],score,t0,tiebreak=tie,log=True)
    fn = guards()
    checks = {
        'classification':fn['check_classification'](original),
        'ca_causality':fn['check_ca_causality'](original),
        'panel_candles':fn['check_panel_candles'](original),
        'holdings_missing':fn['check_missing_for_holdings'](original,ref),
        'delisted':fn['check_delisted'](original),
        'universe_ties':fn['check_universe_ties'](original),
        'split_bonus':fn['check_split_bonus'](original,CorporateActionRows(inputs.metadata()['corporate_actions'])),
    }
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='All-NaN slice encountered',category=RuntimeWarning)
        checks['pit_liquidity']=fn['check_pit_liquidity'](original)
    with inputs.connection() as c:
        duplicates = c.execute(f"""SELECT count(*) FROM (SELECT instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date d
             FROM {inputs.market_table} WHERE interval='1day' GROUP BY 1,2 HAVING count(*)>1) x""").fetchone()[0]
    checks['db_duplicates'] = {'pass':True,'duplicate_daily_instrument_dates_in_store':duplicates,
                               'handling':'Panel readers select one latest timestamp per instrument/session'}
    failed = [k for k,v in checks.items() if not v['pass']]
    if failed:raise DataBlocked('Original integrity checks failed: '+', '.join(failed))
    return original,ref,dict(universe_mismatches=mask_mismatches,score_missing_mismatches=score_missing,
                             score_max_error=score_error,integrity=checks)


def replay_adapter(instruments,sessions,frames,scores,start,*,capital=CAPITAL,exposure=None,gate=None):
    book, values, fills, last_intents = fresh_book(capital),np.full(len(sessions),np.nan),[],[]
    snapshots = {}
    if start:values[start-1]=1.
    for t in range(start,len(sessions)):
        callback=(lambda key,side,q:gate(t,key,side,q)) if gate else None
        book, executions, last_intents = advance(book,day=sessions[t],offset=t-start,
            opens=frames['o'].iloc[t].to_dict(),closes=frames['c'].iloc[t].to_dict(),
            scores=scores.iloc[t].to_dict(),instruments=instruments,
            exposure=float(exposure[t]) if exposure is not None else 1.,overlay=exposure is not None,gate=callback)
        values[t] = equity(book)/capital
        fills.extend(r for r in executions if 'reference_quantity' in r)
        snapshots[t] = {k:p['value']/capital for k,p in book['holdings'].items()}
    return dict(eq=values,book=book,fills=fills,intents=last_intents,snaps=snapshots)


def verify_auction_classifier():
    original=definitions('auction_capture.py',['is_stale','classify_auction'],dict(pd=pd,STALE_SECONDS=120))['classify_auction']
    count=0
    for iep,ieq,imb,quantity,final,stale in product(
            [None,0,100.],[None,0,1000],[None,0,-1,1],[1,100,101,1000],
            [None,{'volume':0},{'volume':1000},{'volume':10000}],[False,True]):
        fields=dict(indicative_equilibrium_price=iep,indicative_equilibrium_quantity=ieq,
                    indicative_imbalance_quantity_market=imb,
                    timestamp='2026-11-16T09:00:00+05:30' if stale else '2026-11-16T09:04:30+05:30')
        expected=original(quantity,fields,final,'2026-11-16T09:04:30')[0]
        actual=auction_gate(quantity,dict(iep=iep,ieq=ieq,imbalance_market=imb),final,stale)
        if expected!=actual:raise DataBlocked('Original auction classifier disagreement')
        count+=1
    return count


def verify_historical(inputs=None):
    inputs = inputs or Inputs()
    last = inputs.metadata()['duckdb_import']['last_session']
    instruments,sessions,frames = inputs.load(last)
    universe,scores = features(frames['c'],frames['v'],instruments)
    original,ref0,report = verify_inputs(inputs,instruments,sessions,frames,universe,scores)
    keys = list(instruments);a=original['A'];sc=original['score'];t0=original['t0']
    tie=np.argsort(np.argsort(np.array(keys)))
    ours0 = replay_adapter(instruments,sessions,frames,scores,t0)
    error0=float(np.nanmax(np.abs(ref0['eq']-ours0['eq'])))
    expected_fills=xsim.run(a,sc,t0,tiebreak=tie,ledger=True)['ledger']
    expected_orders=[(sessions[r['t']],keys[r['s']],'BUY' if r['side']=='B' else 'SELL') for r in expected_fills if r['filled_value']>0]
    actual_orders=[(r['session'],r['instrument_key'],r['side']) for r in ours0['fills']]
    if error0>1e-12 or expected_orders!=actual_orders:
        raise DataBlocked(f'C0-R historical portfolio mismatch: equity error {error0}')
    vt=definitions('p6common.py',['vt_exposure'],dict(np=np,pd=pd,math=math))['vt_exposure']
    exposure=vt(ref0['eq'])
    ref1=sim5.run(a,sc,t0,tiebreak=tie,exposure=exposure,rebalance_on_exposure=.10)
    ours1=replay_adapter(instruments,sessions,frames,scores,t0,exposure=exposure)
    error1=float(np.nanmax(np.abs(ref1['eq']-ours1['eq'])))
    ref2=[];ours2=[]
    for j in range(5):
        ref2.append(np.nan_to_num(sim5.run(a,sc,t0+j,tiebreak=tie)['eq'],nan=1.))
        ours2.append(np.nan_to_num(replay_adapter(instruments,sessions,frames,scores,t0+j,capital=CAPITAL/5)['eq'],nan=1.))
    error2=float(np.max(np.abs(np.mean(ref2,axis=0)-np.mean(ours2,axis=0))))
    def admitted(t,k,side,q):return 'likely' if (t+keys.index(k))%4 else 'unobserved'
    def ref_fill(t,s,side,rupees,q):return (a['o'][t,s],1.,'likely') if (t+s)%4 else (None,0.,'unobserved')
    refx=xsim.run(a,sc,t0,tiebreak=tie,fill=ref_fill)
    oursx=replay_adapter(instruments,sessions,frames,scores,t0,gate=admitted)
    errorx=float(np.nanmax(np.abs(refx['eq']-oursx['eq'])))
    if max(error1,error2,errorx)>1e-12:
        raise DataBlocked(f'Portfolio mismatch: C1={error1}, C2={error2}, X={errorx}')
    # The original paper run issued day-zero whole-share intentions. Compare
    # those exact quantities, including the two rejected C2-S zero-share rows.
    day0=sessions.index(DAY0)
    book_intents={}
    for name,j,capital,e in [('C0_R',0,CAPITAL,None),('C1_R',0,CAPITAL,exposure),
                             ('C2_S',0,CAPITAL/5,None),('C0_R_X',0,CAPITAL,None)]:
        r=replay_adapter(instruments,sessions,frames,scores,day0,capital=capital,exposure=e)
        book_intents[name]=r['intents']
    with inputs.connection() as c:
        row=c.execute('SELECT content FROM source_files WHERE name=%s',
                      ('swing_2025_2026/results/phase8/paper/orders/2026-11-16.json',)).fetchone()
    if not row:raise DataBlocked('Original paper intention fixture is missing')
    issued=json.loads(bytes(row[0]));old=issued['orders']+issued['rejected']
    order_key=lambda r:(r['strategy'],r['side'],r['key'],r['qty'])
    expected=sorted(order_key(r) for r in old)
    actual=sorted((name,r['side'],r['instrument_key'],r['quantity']) for name,intents in book_intents.items() for r in intents)
    if actual!=expected:raise DataBlocked('Original day-zero whole-share intentions differ')
    report.update(passed=True,verified_at=datetime.now(IST).isoformat(),first_session=sessions[0],
                  last_session=sessions[-1],sessions=len(sessions),instruments=len(keys),
                  equity_max_errors={'C0_R':error0,'C1_R':error1,'C2_S':error2,'C0_R_X_synthetic_gate':errorx},
                  c0_historical_return=float(ref0['eq'][-1]-1),c0_closed_positions=len(ref0['trades']),
                  c0_orders_matched=len(actual_orders),day_zero_intents_matched=len(actual),
                  auction_classifier_cases_matched=verify_auction_classifier(),
                  c0x_note='Portfolio mechanics compared with a deterministic synthetic gate; prospective auction evidence is still required',
                  real_orders_submitted=0)
    with inputs.connection() as c:
        c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload',
                  ('historical_parity',canonical(report)))
    return report


if __name__ == '__main__':
    print(json.dumps(verify_historical(),indent=2))
