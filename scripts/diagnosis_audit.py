"""Independent diagnostic evidence; never changes original research artifacts."""
from pathlib import Path
import sys,json,re,sqlite3,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.swing_discovery import signals as S
from research.swing_discovery.engine import simulate,fee_coeff
OLD=ROOT/'artifacts/swing_discovery';OUT=ROOT/'artifacts/swing_diagnosis';OUT.mkdir(exist_ok=True)

def save(name,x):
    (OUT/name).write_text(json.dumps(x,indent=2,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else str(v)),encoding='utf-8')

def load_panel():
    idx=json.loads((OLD/'panel-index.json').read_text())
    with np.load(OLD/'daily-panel.npz') as a:
        p={k:a[k].copy() for k in ['unit_factor','split_factor','dividend','eligible','liquidity_volume','liquidity_turnover']}
        p['actual']={k:a['actual_'+k].copy() for k in ['open','high','low','close','volume']}
        p['neutral']={k:a['neutral_'+k].copy() for k in p['actual']}
        p['nifty']=a['niftyclose'].copy()
    p.update(symbols=idx['symbols'],dates=pd.DatetimeIndex(pd.to_datetime(idx['dates'],utc=True)).tz_convert('Asia/Kolkata'),sector=idx['sector'])
    p['median_volume20']=p['liquidity_volume'];p['liquidity_value']=p['liquidity_turnover']
    return p

def dividend_corrections():
    audit=json.loads((OLD/'data-audit.json').read_text());rows=[]
    for symbol,s in audit['stock_audits'].items():
        for e in s.get('events',[]):
            amounts=re.findall(r'(?:Rs\.?|Re\.?)\s*(\d+(?:\.\d+)?)',e['subject'],re.I)
            if e['kind']=='dividend' and len(amounts)>1:
                rows.append(dict(symbol=symbol,date=e['date'],eligible=s['eligible'],old=e['dividend'],corrected=sum(map(float,amounts)),delta=sum(map(float,amounts))-e['dividend'],subject=e['subject']))
    df=pd.DataFrame(rows);df.to_csv(OUT/'audit-dividend-corrections.csv',index=False)
    return df

def journal_impact(panel,corrections):
    # Fixed original trade paths: quantity at ex date includes intervening splits.
    # This is an attribution, not a resimulation of changed cash/sizing/targets.
    research=corrections[corrections.eligible & corrections.date.ge('2024-11-11')]
    bysym={s:g for s,g in research.groupby('symbol')};pos={s:i for i,s in enumerate(panel['symbols'])}
    days=panel['dates'].strftime('%Y-%m-%d');di={d:i for i,d in enumerate(days)}
    records=[];trade_deltas=[]
    for path in sorted((OLD/'finalist_journals').glob('*-trades.csv')):
        if not ('-all_eligible_stocks-final-' in path.name or '-all_eligible_stocks-two_year-' in path.name):continue
        t=pd.read_csv(path);stage='two_year' if '-two_year-' in path.name else 'final';ident=path.name.split('-all_eligible_stocks')[0]
        en=t.entry_day.str[:10];ex=t.exit_day.str[:10];same=en.eq(ex)
        # Delivery -> non-delivery statutory cost difference. Broker cap not
        # included, so this is conservative with respect to that extra saving.
        saving=np.where(same, t.entry_fill*t.entry_quantity*(.001+.00012)+t.exit*t.quantity*(.001-.00025),0.)
        delta=np.zeros(len(t));events=0
        for sym,g in t.groupby('symbol'):
            if sym not in bysym:continue
            for event in bysym[sym].itertuples():
                held=g.index[(en.loc[g.index]<event.date)&(ex.loc[g.index]>=event.date)]
                for j in held:
                    start=di[en[j]];end=di[event.date];q=t.loc[j,'entry_quantity']*np.prod(panel['split_factor'][pos[sym],start+1:end+1])
                    delta[j]+=q*event.delta;events+=1
        for j in np.flatnonzero((delta!=0)|(saving!=0)):
            trade_deltas.append(dict(id=ident,stage=stage,symbol=t.loc[j,'symbol'],entry_day=t.loc[j,'entry_day'],exit_day=t.loc[j,'exit_day'],entry_fill=t.loc[j,'entry_fill'],entry_quantity=int(t.loc[j,'entry_quantity']),missing_dividend=delta[j],same_day_statutory_refund=saving[j]))
        records.append(dict(id=ident,stage=stage,trades=len(t),same_day_trades=int(same.sum()),same_day_pct=float(same.mean()*100),
            same_day_statutory_overcharge=float(saving.sum()),missing_dividend_cash=float(delta.sum()),held_missing_dividend_events=events,
            original_net_pnl=float(t.net_pnl.sum()),fixed_path_corrected_net_pnl=float(t.net_pnl.sum()+saving.sum()+delta.sum()),
            original_mean_sleeve_return_pct=float(t.net_pnl.sum()/470/1e6*100),
            fixed_path_corrected_mean_sleeve_return_pct=float((t.net_pnl.sum()+saving.sum()+delta.sum())/470/1e6*100)))
    df=pd.DataFrame(records);df.to_csv(OUT/'audit-fixed-path-corrections.csv',index=False)
    pd.DataFrame(trade_deltas).to_csv(OUT/'audit-trade-deltas.csv',index=False)
    return df

def sparse_screen():
    conn=sqlite3.connect(f'file:{(OLD/"research.sqlite3").as_posix()}?mode=ro',uri=True)
    df=pd.read_sql_query("SELECT r.id,r.stage,SUM(s.n_trades>0) active_stocks,SUM(s.total_return_pct>0) positive_stocks,COUNT(*) stocks FROM runs r JOIN stock_metrics s ON s.key=r.key WHERE r.stage IN ('development','validation') GROUP BY r.key",conn)
    r=pd.read_sql_query("SELECT id,stage,summary FROM runs WHERE stage IN ('development','validation')",conn)
    x=pd.DataFrame([{**{'id':z.id,'stage':z.stage},**json.loads(z.summary)} for z in r.itertuples()])
    df=df.merge(x[['id','stage','total_return_pct','expectancy_r','n_trades']],on=['id','stage'])
    df['breadth_mathematically_impossible']=df.active_stocks<np.ceil(df.stocks/2)
    df['active_positive_pct']=100*df.positive_stocks/df.active_stocks.replace(0,np.nan)
    df.to_csv(OUT/'audit-sparse-screen.csv',index=False);conn.close()
    return {stage:dict(rules=len(g),sparse_breadth_impossible=int(g.breadth_mathematically_impossible.sum()),profitable_rules=int(g.total_return_pct.gt(0).sum()),profitable_but_breadth_impossible=int((g.total_return_pct.gt(0)&g.breadth_mathematically_impossible).sum()),median_active_stocks=float(g.active_stocks.median())) for stage,g in df.groupby('stage')}

def reference_ema(x,n,alpha=None):
    out=np.full(len(x),np.nan);state=None;window=[];a=2/(n+1) if alpha is None else alpha
    for t,v in enumerate(x):
        if not np.isfinite(v):state=None;window=[];continue
        if state is None:
            window.append(v)
            if len(window)==n:state=float(np.mean(window));out[t]=state
        else:state=(1-a)*state+a*v;out[t]=state
    return out

def numerical_and_causal_checks(panel):
    # Independent scalar seeded recursion, explicit OHLC TR and strict pivot loop.
    p={**panel};ids=np.flatnonzero(panel['eligible'])[:6]
    for k in ['actual','neutral']:p[k]={a:v[ids].copy() for a,v in panel[k].items()}
    for k in ['unit_factor','split_factor','dividend']:p[k]=panel[k][ids]
    p['symbols']=[panel['symbols'][i] for i in ids];p['sector']=[panel['sector'][i] for i in ids]
    f=S.build_features(p);c=p['neutral']['close'];h=p['neutral']['high'];l=p['neutral']['low'];errors={}
    for n in [9,12,20,26,50,200]:
        ref=np.stack([reference_ema(x,n) for x in c]);a=S._ema(f,n)
        errors['ema_'+str(n)]=float(np.nanmax(abs(ref-a)))
    tr=np.stack([np.nanmax(np.stack([h[i]-l[i],abs(h[i]-np.r_[np.nan,c[i,:-1]]),abs(l[i]-np.r_[np.nan,c[i,:-1]])]),axis=0) for i in range(len(ids))])
    ref=np.stack([reference_ema(x,14,1/14) for x in tr]);errors['atr14']=float(np.nanmax(abs(ref-f['atr'])))
    delta=c-np.concatenate([np.full((len(c),1),np.nan),c[:,:-1]],axis=1)
    up=np.stack([reference_ema(np.maximum(x,0),14,1/14) for x in delta])
    down=np.stack([reference_ema(np.maximum(-x,0),14,1/14) for x in delta])
    rs=np.divide(up,down,out=np.full_like(up,np.inf),where=down>0)
    rsi=np.where(np.isfinite(up),np.where((up==0)&(down==0),50.,100-100/(1+rs)),np.nan)
    errors['rsi14']=float(np.nanmax(abs(rsi-f['rsi'])))
    rise=h-np.concatenate([np.full((len(c),1),np.nan),h[:,:-1]],axis=1)
    fall=np.concatenate([np.full((len(c),1),np.nan),l[:,:-1]],axis=1)-l
    plus=np.stack([reference_ema(x,14,1/14) for x in np.where((rise>fall)&(rise>0),rise,0)])
    minus=np.stack([reference_ema(x,14,1/14) for x in np.where((fall>rise)&(fall>0),fall,0)])
    dx=np.divide(100*abs(plus-minus),plus+minus,out=np.zeros_like(c),where=(plus+minus)>0);dx[~np.isfinite(plus+minus)]=np.nan
    adx=np.stack([reference_ema(x,14,1/14) for x in dx]);errors['adx14']=float(np.nanmax(abs(adx-f['adx'])))
    fast=np.stack([reference_ema(x,12) for x in c]);slow=np.stack([reference_ema(x,26) for x in c]);macd=fast-slow
    line,sig,hist=S._osc(f,12,26,9);errors['macd_line']=float(np.nanmax(abs(line-macd)));errors['macd_signal']=float(np.nanmax(abs(sig-np.stack([reference_ema(x,9) for x in macd]))))
    cut=len(p['dates'])-113;short={**p,'dates':p['dates'][:cut],'nifty':p['nifty'][:cut]}
    for k in ['actual','neutral']:short[k]={a:v[:,:cut].copy() for a,v in p[k].items()}
    for k in ['unit_factor','split_factor','dividend']:short[k]=p[k][:,:cut].copy()
    sf=S.build_features(short);representatives={}
    for cfg in S.catalog():representatives.setdefault(cfg['family'],cfg)
    causal=[]
    for cfg in representatives.values():
        a=S.generate(p,cfg,f);b=S.generate(short,cfg,sf)
        causal.append(dict(family=cfg['family'],all_arrays_prefix_equal=all(np.allclose(a[k][:,:cut],b[k],equal_nan=True) for k in a)))
    from research.swing_discovery.structure import build_structure
    s=build_structure(p,pivot=2,atr=f['atr']);ref=np.zeros(c.shape,bool)
    for i in range(len(ids)):
        for t in range(4,c.shape[1]):
            at=t-2;v=l[i,at];neighbors=np.r_[l[i,at-2:at],l[i,at+1:at+3]]
            ref[i,t]=np.isfinite(v) and np.all(v<neighbors)
    return dict(independent_numeric_max_abs_errors=errors,independent_pivot_release_equal=bool(np.array_equal(ref,s['pivot_low_event'])),real_panel_prefix_checks=causal,all_48_families_prefix_invariant=all(x['all_arrays_prefix_equal'] for x in causal),stocks=p['symbols'],prefix_end=str(short['dates'][-1]))

def main():
    panel=load_panel();corrections=dividend_corrections()
    impacts=journal_impact(panel,corrections)
    evidence=dict(sparse_screen=sparse_screen(),indicators_and_causality=numerical_and_causal_checks(panel),
        dividend_parser=dict(all_history_affected_events=len(corrections),research_eligible_affected_events=int((corrections.eligible&corrections.date.ge('2024-11-11')).sum()),research_eligible_affected_stocks=int(corrections.loc[corrections.eligible&corrections.date.ge('2024-11-11'),'symbol'].nunique())),
        fixed_path_scope='Final all-stock and two-year all-stock journals only. Periods overlap. Corrections keep entries, quantities, targets and exits fixed; they are not an executable rerun or revised strategy validation.',
        original_source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'research/swing_discovery').glob('*.py')})
    evidence['fixed_path_summary']={stage:dict(rules=len(g),original_positive=int(g.original_net_pnl.gt(0).sum()),corrected_positive=int(g.fixed_path_corrected_net_pnl.gt(0).sum()),same_day_trade_count=int(g.same_day_trades.sum()),total_trade_count=int(g.trades.sum()),tax_difference=float(g.same_day_statutory_overcharge.sum()),missing_dividends=float(g.missing_dividend_cash.sum())) for stage,g in impacts.groupby('stage')}
    save('audit-evidence.json',evidence);print(json.dumps(evidence,indent=2,default=str))

if __name__=='__main__':main()
