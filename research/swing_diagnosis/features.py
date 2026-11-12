"""Retrospective causal-feature and failure diagnostics, without retuning entries.

All prior discovery files are read-only inputs. Frozen finalists and dates have
already been selected/researched: causal timestamps do not restore a clean OOS.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from research.swing_discovery.signals import smooth

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'artifacts/swing_discovery'
OUT=ROOT/'artifacts/swing_diagnosis'
BOUNDARIES=['2024-11-10','2025-02-10','2025-05-10','2025-08-10','2025-11-10','2026-02-10','2026-05-10','2026-08-10','2026-11-10']
FEATURES=['atr_pct','volatility60','efficiency60','relative_strength60','liquidity20','volume_consistency60','gap_frequency60','return_autocorrelation60','nifty_correlation60','sector_peer_momentum60','trend_strength60','directional_persistence60','support_rejection60']

def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,default=str,allow_nan=False),encoding='utf-8')

def roll(a,w,kind='mean'):
    f=pd.DataFrame(a.T).rolling(w,min_periods=w)
    return getattr(f,kind)().to_numpy().T

def shift(a,n=1):
    return np.concatenate([np.full((a.shape[0],n),np.nan),a[:,:-n]],axis=1)

def bh(p):
    p=np.asarray(p,float);out=np.ones(len(p));order=np.argsort(p);rank=np.arange(1,len(p)+1)
    out[order]=np.minimum.accumulate((p[order]*len(p)/rank)[::-1])[::-1]
    return np.minimum(out,1)

def bootstrap(values,seed=7341,draws=3000,block=10):
    """Paired common-calendar resampling; no trade independence assumption."""
    values=np.asarray(values,float);n=len(values)
    if not n:return dict(delta=0.,lo=0.,hi=0.,p=1.)
    rng=np.random.default_rng(seed);batches=[]
    for _ in range(0,draws,100):
        starts=rng.integers(0,n,size=(min(100,draws-_),int(np.ceil(n/block))))
        ix=((starts[:,:,None]+np.arange(block))%n).reshape(len(starts),-1)[:,:n]
        batches.append(values[ix].sum(axis=1))
    sums=np.concatenate(batches);centered=sums-values.sum()
    return dict(delta=float(values.sum()),lo=float(np.quantile(sums,.025)),hi=float(np.quantile(sums,.975)),p=float((1+(np.abs(centered)>=abs(values.sum())).sum())/(draws+1)))

def regime_uncertainty(sub,allg,calendar):
    sums=[];counts=[]
    for g in [sub,allg]:
        grouped=g.groupby('signal_day').net_r.agg(['sum','count']).reindex(calendar,fill_value=0)
        sums.append(grouped['sum'].to_numpy());counts.append(grouped['count'].to_numpy())
    if not len(sub):return dict(selected_r_lo=None,selected_r_hi=None,delta_r_lo=None,delta_r_hi=None)
    rng=np.random.default_rng(7341);n=len(calendar);means=[[],[]]
    for start in range(0,3000,100):
        blocks=rng.integers(0,n,size=(100,int(np.ceil(n/10))))
        ix=((blocks[:,:,None]+np.arange(10))%n).reshape(100,-1)[:,:n]
        for j in range(2):
            den=counts[j][ix].sum(axis=1);num=sums[j][ix].sum(axis=1)
            means[j].append(np.divide(num,den,out=np.full(100,np.nan),where=den>0))
    a,b=[np.concatenate(x) for x in means];valid=np.isfinite(a)&np.isfinite(b);a,b=a[valid],b[valid]
    return dict(selected_r_lo=float(np.quantile(a,.025)),selected_r_hi=float(np.quantile(a,.975)),delta_r_lo=float(np.quantile(a-b,.025)),delta_r_hi=float(np.quantile(a-b,.975)))

def load():
    idx=json.loads((OLD/'panel-index.json').read_text());p=dict(np.load(OLD/'daily-panel.npz'))
    dates=pd.DatetimeIndex(pd.to_datetime(idx['dates'],utc=True)).tz_convert('Asia/Kolkata').tz_localize(None)
    protocol=json.loads((OLD/'protocol.json').read_text());frozen=json.loads((OLD/'frozen-finalists.json').read_text())['finalists']
    return idx,p,dates,protocol,frozen

def feature_panel(idx,p):
    c,o,h,l,v=[p['neutral_'+k] for k in ['close','open','high','low','volume']]
    prev=shift(c);r=c/prev-1;market=p['niftyclose'];mr=pd.Series(market).pct_change().to_numpy()
    atr=smooth(np.fmax(h-l,np.fmax(abs(h-prev),abs(l-prev))),14,1/14)
    volatility=roll(r,60,'std');ret60=c/shift(c,60)-1
    travel=roll(abs(c-prev),60)*60
    efficiency=abs(c-shift(c,60))/travel
    volume_cv=roll(v,60,'std')/roll(v,60)
    gap=abs(o/prev-1)>.01;gap[~np.isfinite(prev)]=False
    auto=np.full_like(c,np.nan);corr=np.full_like(c,np.nan)
    for i in range(len(c)):
        s=pd.Series(r[i]);auto[i]=s.rolling(60,min_periods=60).corr(s.shift(1));corr[i]=s.rolling(60,min_periods=60).corr(pd.Series(mr))
    sector=np.full_like(c,np.nan)
    for name in set(idx['sector']):
        ids=np.flatnonzero(np.array(idx['sector'])==name)
        if len(ids)<2:continue
        a=ret60[ids];count=np.isfinite(a).sum(axis=0);total=np.nansum(a,axis=0)
        sector[ids]=np.divide(total-a,count-np.isfinite(a),out=np.full_like(a,np.nan),where=count-np.isfinite(a)>0)
    support=shift(roll(l,20,'min'))
    reject=(l<=support+.5*atr)&(c>support)&(c>o)
    feature=dict(atr_pct=atr/c,volatility60=volatility,efficiency60=efficiency,
      relative_strength60=ret60-(market/np.concatenate([np.full(60,np.nan),market[:-60]])-1),
      liquidity20=p['liquidity_turnover'],volume_consistency60=-volume_cv,gap_frequency60=roll(gap.astype(float),60),
      return_autocorrelation60=auto,nifty_correlation60=corr,sector_peer_momentum60=sector,
      trend_strength60=ret60/(volatility*np.sqrt(60)),directional_persistence60=roll((np.sign(r)==np.sign(shift(r))).astype(float),60),
      support_rejection60=roll(reject.astype(float),60))
    # Regimes are known only at each completed signal-day close.
    m=market[None,:]
    vol20=pd.Series(mr).rolling(20).std().to_numpy();vol60=pd.Series(mr).rolling(60).std().to_numpy()
    priorvol=pd.Series(vol20).rolling(252).median().shift(1).to_numpy()
    mret20=m[0]/shift(m,20)[0]-1;mret60=m[0]/shift(m,60)[0]-1
    normalized=mret60/(vol60*np.sqrt(60))
    trend=np.where(abs(normalized)<.5,'sideways',np.where(normalized>=1,'strong_bull',np.where(normalized>0,'weak_bull',np.where(normalized<=-1,'strong_bear','weak_bear'))))
    regimes=dict(trend=trend,volatility=np.where(vol20>priorvol,'high','low'),
      expansion=np.where(vol20/vol60>1.2,'expansion',np.where(vol20/vol60<.8,'contraction','stable')))
    return feature,regimes

def load_trades(idx,p,dates,frozen,corrected=False):
    symbols={s:i for i,s in enumerate(idx['symbols'])};daymap={d.strftime('%Y-%m-%d'):i for i,d in enumerate(dates)}
    rows=[]
    for record in frozen:
        path=(OUT/'audit_corrected_journals'/f"{record['id']}-two_year-trades.csv.gz") if corrected else (OLD/'finalist_journals'/f"{record['id']}-all_eligible_stocks-two_year-trades.csv")
        t=pd.read_csv(path)
        t['id']=record['id'];t['family']=record['family'];t['entry_type']=record['family'];t['exit_policy']=record['config'].get('exit','fixed')
        for key in ['signal_day','entry_day','exit_day']:t[key]=pd.to_datetime(t[key],utc=True).dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        rows.append(t)
    t=pd.concat(rows,ignore_index=True);t['s']=t.symbol.map(symbols);t['e']=t.entry_day.dt.strftime('%Y-%m-%d').map(daymap);t['x']=t.exit_day.dt.strftime('%Y-%m-%d').map(daymap);t['d']=t.signal_day.dt.strftime('%Y-%m-%d').map(daymap)
    s=t.s.to_numpy(int);e=t.e.to_numpy(int);x=t.x.to_numpy(int)
    t['sector']=np.array(idx['sector'])[s];t['gross_r']=t.gross_pnl/t.initial_cash_risk;t['fee_r']=t.fees/t.initial_cash_risk
    for horizon in [1,5,10,20]:
        future=e+horizon-1;valid=future<len(dates);result=np.full(len(t),np.nan)
        result[valid]=p['neutral_close'][s[valid],future[valid]]/(t.entry_fill.to_numpy()[valid]/p['unit_factor'][s[valid],e[valid]])-1
        t[f'entry_forward_close{horizon}_pct']=result*100
    mfe=np.full(len(t),np.nan);mae=mfe.copy()
    for j,(si,ei,xi,entry,risk,q) in enumerate(zip(s,e,x,t.entry_fill,t.initial_cash_risk,t.entry_quantity)):
        if xi<=ei:continue
        unit=p['unit_factor'][si,ei];price=entry/unit
        mfe[j]=(np.nanmax(p['neutral_high'][si,ei:xi])-price)*unit*q/risk
        mae[j]=(np.nanmin(p['neutral_low'][si,ei:xi])-price)*unit*q/risk
    t['pre_exit_bar_mfe_r']=mfe;t['pre_exit_bar_mae_r']=mae
    t['block']=pd.cut(t.entry_day,pd.to_datetime(BOUNDARIES),right=False,labels=False).astype(int)
    t['stage']=np.where(t.block<4,'development',np.where(t.block<6,'validation','final'))
    t['year']=t.entry_day.dt.year;t['month']=t.entry_day.dt.strftime('%Y-%m');t['holding_bucket']=pd.cut(t.holding_hours,[-1,24,72,168,336,np.inf],labels=['<=24h','1-3d','3-7d','7-14d','>14d']).astype(str)
    return t

def summaries(t,regimes):
    for dimension,label in regimes.items():t['regime_'+dimension]=label[t.d.to_numpy(int)]
    output=[]
    t['win']=t.net_pnl.gt(0).astype(float)*100
    for dimension in ['year','month','sector','symbol','holding_bucket','entry_type','exit_policy','reason','regime_trend','regime_volatility','regime_expansion']:
        keys=['family','stage',dimension]
        g=t.groupby(keys,dropna=False).agg(n_trades=('net_r','size'),stocks=('symbol','nunique'),
          net_pnl=('net_pnl','sum'),gross_pnl=('gross_pnl','sum'),fees=('fees','sum'),net_r=('net_r','mean'),gross_r=('gross_r','mean'),fee_r=('fee_r','mean'),
          win_pct=('win','mean'),mean_hold_hours=('holding_hours','mean'),mfe_r=('pre_exit_bar_mfe_r','mean'),mae_r=('pre_exit_bar_mae_r','mean'),
          forward5_pct=('entry_forward_close5_pct','mean'),forward10_pct=('entry_forward_close10_pct','mean'),forward20_pct=('entry_forward_close20_pct','mean')).reset_index()
        g=g.rename(columns={dimension:'value'});g['dimension']=dimension;output.append(g)
    pd.concat(output,ignore_index=True).to_csv(OUT/'breakdown-all-dimensions.csv',index=False)
    aggregate=t.groupby(['family','stage']).agg(n_trades=('net_r','size'),net_pnl=('net_pnl','sum'),gross_pnl=('gross_pnl','sum'),fees=('fees','sum'),net_r=('net_r','mean'),gross_r=('gross_r','mean'),fee_r=('fee_r','mean'),win_pct=('net_pnl',lambda x:100*x.gt(0).mean()),mean_hold_hours=('holding_hours','mean'),mfe_r=('pre_exit_bar_mfe_r','mean'),mae_r=('pre_exit_bar_mae_r','mean'),forward5_pct=('entry_forward_close5_pct','mean'),forward10_pct=('entry_forward_close10_pct','mean'),forward20_pct=('entry_forward_close20_pct','mean')).reset_index()
    aggregate.to_csv(OUT/'breakdown-family-cost-excursions.csv',index=False)
    t.to_csv(OUT/'breakdown-trade-diagnostics.csv',index=False)
    return aggregate

def characteristics(idx,p,dates,protocol,feature,t):
    eligible=np.flatnonzero(p['eligible']);symbols=np.array(idx['symbols']);development=set(protocol['development_stocks']);reserved=set(protocol['reserved_stocks'])
    cells=[]
    for b,boundary in enumerate(BOUNDARIES[:-1]):
        d=np.flatnonzero(dates<pd.Timestamp(boundary))[-1]
        for s in eligible:
            cells.append(dict(symbol=symbols[s],block=b,snapshot_day=str(dates[d].date()),pool='development375' if symbols[s] in development else 'reserved95',
              stage='development' if b<4 else ('validation' if b<6 else 'final'),**{name:float(a[s,d]) for name,a in feature.items()}))
    cells=pd.DataFrame(cells)
    for name in FEATURES:
        cells[name+'_bin']='missing'
        for b,g in cells.groupby('block'):
            values=g[name];finite=np.isfinite(values)
            # Cross-sectional terciles defined at the snapshot, ties retained.
            lo,hi=values[finite].quantile([1/3,2/3])
            label=np.where(values<=lo,'low',np.where(values>=hi,'high','middle')).astype(object);label[~finite]='missing'
            cells.loc[g.index,name+'_bin']=label
    outcome=t.groupby(['symbol','block']).agg(future_net_pnl=('net_pnl','sum'),future_gross_pnl=('gross_pnl','sum'),n_trades=('net_r','size'),mean_net_r=('net_r','mean'))
    cells=cells.merge(outcome,on=['symbol','block'],how='left');cells[['future_net_pnl','future_gross_pnl','n_trades']]=cells[['future_net_pnl','future_gross_pnl','n_trades']].fillna(0)
    cells['future_pnl_pct_initial_per_rule']=cells.future_net_pnl/48/1e6*100
    cells.to_csv(OUT/'characteristics-stock-quarter-cells.csv',index=False)
    labels=cells.set_index(['symbol','block'])[[x+'_bin' for x in FEATURES]]
    joined=t.merge(labels,left_on=['symbol','block'],right_index=True,how='left');joined['pool']=np.where(joined.symbol.isin(development),'development375','reserved95')
    # Training labels ending after the fit date cannot enter orientation fitting.
    orientation={};training=joined[(joined.stage=='development')&(joined.pool=='development375')&(joined.exit_day<pd.Timestamp(BOUNDARIES[4]))]
    detail=[]
    for name in FEATURES:
        bincol=name+'_bin';g=cells[(cells.stage=='development')&(cells.pool=='development375')]
        totals=training.groupby(bincol).net_pnl.sum();den=g.groupby(bincol).size()
        delta=(totals.get('high',0)/den.get('high',1)-totals.get('low',0)/den.get('low',1))/48/1e6*100
        orientation[name]='high' if delta>=0 else 'low'
        for (stage,pool),base in cells.groupby(['stage','pool']):
            trades=joined[(joined.stage==stage)&(joined.pool==pool)]
            if stage=='development':trades=trades[trades.exit_day<pd.Timestamp(BOUNDARIES[4])]
            b0=0 if stage=='development' else (4 if stage=='validation' else 6);b1=b0+(4 if stage=='development' else 2)
            calendar=dates[(dates>=pd.Timestamp(BOUNDARIES[b0]))&(dates<pd.Timestamp(BOUNDARIES[b1]))]
            mean_daily={}
            for binname in ['high','low']:
                group=trades[trades[bincol]==binname].copy();counts=base[base[bincol]==binname].groupby('block').size()
                group['weighted']=group.net_pnl/group.block.map(counts)/48/1e6*100
                mean_daily[binname]=group.groupby('entry_day').weighted.sum().reindex(calendar,fill_value=0)
                detail.append(dict(feature=name,orientation=orientation[name],stage=stage,pool=pool,bin=binname,stock_quarters=int(counts.sum()),n_trades=len(group),
                  cumulative_quarter_pnl_pct_initial=float(group.weighted.sum()),mean_net_r=float(group.net_r.mean()) if len(group) else None))
            sign=1 if orientation[name]=='high' else -1
            result=bootstrap((mean_daily['high']-mean_daily['low']).to_numpy()*sign)
            detail.append(dict(feature=name,orientation=orientation[name],stage=stage,pool=pool,bin='selected_minus_opposite',**result))
    detail=pd.DataFrame(detail)
    detail['bh_q']=np.nan
    for (stage,pool),g in detail[detail.bin=='selected_minus_opposite'].groupby(['stage','pool']):detail.loc[g.index,'bh_q']=bh(g.p)
    detail.to_csv(OUT/'characteristics-forward-validation.csv',index=False)
    save('characteristics-frozen-orientations.json',orientation)
    return detail

def regime_gate(t,protocol,dates):
    """Fixed family-group analysis; selected trade subsets, not cash simulations."""
    development=set(protocol['development_stocks']);t=t.copy()
    t['broad_family']=np.where(t.family.str.startswith(('macd_','ppo_')),'MACD_PPO',np.where(t.family.str.startswith(('ema_','kama_')),'EMA_KAMA',np.where(t.family.str.startswith('hybrid_'),'hybrid','support_resistance')))
    t['pool']=np.where(t.symbol.isin(development),'development375','reserved95');result=[];selected={}
    for broad,allg in t.groupby('broad_family'):
        for dim in ['trend','volatility','expansion']:
            col='regime_'+dim;train=allg[(allg.stage=='development')&(allg.pool=='development375')&(allg.exit_day<pd.Timestamp(BOUNDARIES[4]))]
            scores=train.groupby(col).net_r.agg(['mean','count']);allowed=scores[scores['count']>=100]
            if allowed.empty:continue
            chosen=allowed['mean'].idxmax();selected[broad+'|'+dim]=str(chosen)
            for (stage,pool),g in allg.groupby(['stage','pool']):
                if stage=='development':g=g[g.exit_day<pd.Timestamp(BOUNDARIES[4])]
                sub=g[g[col]==chosen];other=g[g[col]!=chosen]
                b0=0 if stage=='development' else (4 if stage=='validation' else 6);b1=b0+(4 if stage=='development' else 2)
                first_signal_session=dates[dates<pd.Timestamp(BOUNDARIES[b0])][-1]
                calendar=dates[(dates>=first_signal_session)&(dates<pd.Timestamp(BOUNDARIES[b1]))]
                uncertainty=regime_uncertainty(sub,g,calendar)
                months=sub.groupby(sub.signal_day.dt.to_period('M')).size()
                result.append(dict(broad_family=broad,dimension=dim,chosen_regime=chosen,stage=stage,pool=pool,n_selected=len(sub),n_other=len(other),
                  selected_signal_days=sub.signal_day.nunique(),selected_months=len(months),largest_month_trade_fraction=months.max()/len(sub) if len(sub) else None,
                  selected_net_r=sub.net_r.mean(),other_net_r=other.net_r.mean(),universal_net_r=g.net_r.mean(),selected_pnl=sub.net_pnl.sum(),universal_pnl=g.net_pnl.sum(),**uncertainty))
    pd.DataFrame(result).to_csv(OUT/'regime-development-gates.csv',index=False);save('regime-frozen-gates.json',selected)

def main(corrected=False):
    OUT.mkdir(parents=True,exist_ok=True)
    design=dict(feature_names=FEATURES,boundaries=BOUNDARIES,training='First four quarters; original375 companies only; labels must exit before2025-11-10. Choose high or low only once per descriptor using cumulative quarterly PNL advantage.',
      binning='Cross-sectional terciles using only snapshot strictly before quarter start; no thresholds optimized; ties retained. Snapshot universe inherits original complete-data eligibility bias.',
      outcomes='Trades entered in following quarter from original frozen48 two-year journals. Aggregate net PNL across48 /48 /initial1m per stock. This is attributed PNL per initial capital, not a newly simulated quarter return. Zero-trade stock-quarter cells included.',
      uncertainty='3000 common-calendar circular10session-block draws of high-minus-low daily entry-attributed PNL, preserving same-date stock/family dependence. BH correction across13 descriptors separately within stage/pool; small number of quarters, chosen feature signs and frozen-family selection remain limitations.',
      contamination='All dates and48 finalists previously researched/selected. Causal descriptors plus later outcomes test retrospective transfer only, not untouched OOS or independent proof.',
      regime='Trend abs60return/(vol60*sqrt60)<.5 sideways; >=1 strongbull;0..1 weakbull; <=-1 strongbear; remainder weakbear. Vol20 > prior252median high. Vol20/vol60 >1.2 expansion, <.8 contraction. One development-selected regime per broadfamily/dimension, no new entry/exit simulation.',
      mfe='Price excursions use bars from entry through day before exit only, avoiding unknowable exit-day intrabar ordering; not a realized alternative execution. Forward close returns exclude dividends/costs and use1/5/10/20session closes from entry.',
      not_included=['true sector-index relative strength (selected sector TRI acquired separately; this frozen diagnostic uses sector peers)','delivery volume','volume-at-price','untouched temporal holdout','short trades'],
      journal_basis='Corrected48 exact two-year execution replay: multi-component dividends and same-daystatutory fees corrected; no rule changes.' if corrected else 'Original48 two-year trade paths, prior to identified dividend/fee corrections; sensitivity reference only.')
    save('features-design.json',design)
    idx,p,dates,protocol,frozen=load();feature,regimes=feature_panel(idx,p);print('Historical features complete',flush=True)
    t=load_trades(idx,p,dates,frozen,corrected=corrected);print('Loaded trade diagnostics',len(t),flush=True)
    aggregate=summaries(t,regimes);print('Breakdowns complete',flush=True)
    detail=characteristics(idx,p,dates,protocol,feature,t);regime_gate(t,protocol,dates)
    overall=t.groupby('stage').agg(n_trades=('net_r','size'),net_pnl=('net_pnl','sum'),gross_pnl=('gross_pnl','sum'),fees=('fees','sum'),net_r=('net_r','mean'),gross_r=('gross_r','mean'),fee_r=('fee_r','mean')).reset_index()
    overall.to_csv(OUT/'breakdown-overall-costs.csv',index=False)
    findings=dict(trades=len(t),families=t.family.nunique(),journal_basis=design['journal_basis'],overall=overall.to_dict('records'),
      feature_validation=detail[(detail.stage!='development')&(detail.bin=='selected_minus_opposite')][['feature','orientation','stage','pool','delta','lo','hi','p','bh_q']].to_dict('records'),
      limitations=design['contamination'],files=['breakdown-all-dimensions.csv','breakdown-family-cost-excursions.csv','breakdown-trade-diagnostics.csv','characteristics-stock-quarter-cells.csv','characteristics-forward-validation.csv','regime-development-gates.csv'])
    save('features-findings.json',findings)
    print(json.dumps({'trades':len(t),'families':t.family.nunique(),'feature_tests':len(detail),'files':findings['files']}))

if __name__=='__main__':main()
