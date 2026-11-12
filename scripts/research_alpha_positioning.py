"""Project Alpha: fixed prior-session positioning ablations, no orders.

NSE EOD information is assumed published before the following session. This is
not an intraday OI tape or a recovered historical publication-time archive.
"""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import research_directional_lab as lab

OLD=ROOT/'artifacts'/'directional_research'
PHASE2=ROOT/'artifacts'/'directional_research_phase2'
OUT=ROOT/'artifacts'/'project_alpha'
SEED=20261109
FILTERS=['pcr_level_align','pcr_level_contrarian','pcr_change_align','volume_pcr_align','avoid_near_oi_wall','maxpain_direction_align']
FAMILIES=['ema_trend','donchian','pullback']
CONTRASTS=len(FILTERS)*len(FAMILIES)*2*2


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,default=str,allow_nan=False),encoding='utf-8')


def read_sources():
    retained=json.loads((PHASE2/'option-nse-retained-eod.json').read_text())
    archives={r['date']:r for r in retained};futures={};raw_audit=[];conflicts=[]
    for path in sorted((PHASE2/'option-nse-raw').glob('*.zip')):
        day=path.stem;digest=sha(path);chains={};futs=[]
        with zipfile.ZipFile(path) as z:
            names=[n for n in z.namelist() if n.lower().endswith('.csv')]
            assert len(names)==1 and z.getinfo(names[0]).file_size<150_000_000
            with io.TextIOWrapper(z.open(names[0]),encoding='utf-8-sig') as stream:
                for r in csv.DictReader(stream):
                    assert r['TradDt']==day
                    if r['TckrSymb']!='NIFTY':continue
                    expiry=r.get('FininstrmActlXpryDt') or r['XpryDt']
                    side=r['OptnTp']
                    if side in ['CE','PE']:
                        chain=chains.setdefault(expiry,{'expiry':expiry,'symbol':'NIFTY','contracts':[]})
                        chain['contracts'].append([r['FinInstrmId'],float(r['StrkPric']),side,float(r['OpnIntrst']),float(r['NewBrdLotQty']),float(r['ClsPric']),float(r['TtlTradgVol'])])
                    elif r.get('FinInstrmTp')=='IDF' or (not side and float(r.get('StrkPric') or 0)==0):
                        futs.append({'token':str(r['FinInstrmId']),'expiry':expiry,'close':float(r['ClsPric']),'open_interest_reported':float(r['OpnIntrst']),'volume':float(r['TtlTradgVol']),'lot':int(r['NewBrdLotQty'])})
        futures[day]=futs
        raw_audit.append({'date':day,'file':str(path.relative_to(ROOT)),'sha256':digest,'futures':len(futs)})
        if day in archives:
            if archives[day]['source_sha256']!=digest:conflicts.append(day)
        else:
            archives[day]={'date':day,'source_sha256':digest,'source_url':'https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'+day.replace('-','')+'_F_0000.csv.zip','chains':list(chains.values())}
    for day in conflicts:archives.pop(day,None)
    return archives,futures,raw_audit,conflicts


def chain_summary(chain,previous=None):
    rows=chain['contracts'];identities=[(str(r[0]),r[1],r[2]) for r in rows]
    assert len(identities)==len(set(identities))
    assert all(r[3]>=0 and r[4]>0 and r[6] is not None and r[6]>=0 for r in rows)
    calls=[r for r in rows if r[2]=='CE'];puts=[r for r in rows if r[2]=='PE']
    if not calls or not puts:return None
    assert len({r[4] for r in rows})==1, 'Within-expiry lot mismatch'
    call_oi=sum(r[3] for r in calls);put_oi=sum(r[3] for r in puts)
    cv=sum(r[6] for r in calls);pv=sum(r[6] for r in puts)
    strikes=np.array(sorted({r[1] for r in rows}));payout=np.zeros(len(strikes))
    # OI is summed once for each leg. Ratios are invariant to common within-expiry lot units.
    for r in calls:payout+=np.maximum(strikes-r[1],0)*r[3]
    for r in puts:payout+=np.maximum(r[1]-strikes,0)*r[3]
    result={'call_oi_reported':call_oi,'put_oi_reported':put_oi,'oi_pcr':put_oi/call_oi if call_oi>0 else None,
            'volume_pcr':pv/cv if cv>0 else None,'call_volume':cv,'put_volume':pv,
            'max_call_oi_strike':max(calls,key=lambda r:(r[3],-r[1]))[1],
            'max_put_oi_strike':max(puts,key=lambda r:(r[3],-r[1]))[1],
            'maxpain':float(strikes[np.argmin(payout)]),'common_pcr_log_change':None,'common_contract_count':0,
            'concentration_call':max(r[3] for r in calls)/call_oi if call_oi else None,
            'concentration_put':max(r[3] for r in puts)/put_oi if put_oi else None}
    if previous:
        prior={(str(r[0]),r[1],r[2]):r for r in previous['contracts']}
        current={key:r for key,r in zip(identities,rows)}
        common=set(current)&set(prior)
        # Exclude lot changes so apparent quantities are not roll/lot artifacts.
        common={k for k in common if current[k][4]==prior[k][4]}
        co=sum(current[k][3] for k in common if k[2]=='CE');po=sum(current[k][3] for k in common if k[2]=='PE')
        cp=sum(prior[k][3] for k in common if k[2]=='CE');pp=sum(prior[k][3] for k in common if k[2]=='PE')
        result['common_contract_count']=len(common)
        if min(co,po,cp,pp)>0:result['common_pcr_log_change']=float(np.log(po/co)-np.log(pp/cp))
    return result


def add_filters(t):
    side=t.direction.to_numpy();pcr=t.oi_pcr.to_numpy();delta=t.common_pcr_log_change.to_numpy();vpcr=t.volume_pcr.to_numpy()
    wall=np.where(side>0,t.max_call_oi_strike-t.signal_spot,t.signal_spot-t.max_put_oi_strike)
    return {'baseline':np.ones(len(t),bool),
        'pcr_level_align':np.isfinite(pcr)&(side*(pcr-1)>0),
        'pcr_level_contrarian':np.isfinite(pcr)&(side*(pcr-1)<0),
        'pcr_change_align':np.isfinite(delta)&(side*delta>0),
        'volume_pcr_align':np.isfinite(vpcr)&(side*(vpcr-1)>0),
        'avoid_near_oi_wall':np.isfinite(wall)&np.isfinite(t.signal_atr.to_numpy())&~((wall>0)&(wall<=t.signal_atr.to_numpy())),
        'maxpain_direction_align':side*(t.maxpain.to_numpy()-t.signal_spot.to_numpy())>0}


def stats(t):
    if t.empty:return {'n':0,'gross_mean':None,'net2_mean':None,'net5_mean':None,'win_pct':None,'sessions':0}
    return {'n':len(t),'gross_mean':float(t.gross_index_points.mean()),'net2_mean':float(t.net2_index_points.mean()),
            'net5_mean':float(t.net5_index_points.mean()),'win_pct':float(t.gross_index_points.gt(0).mean()*100),'sessions':int(t.session.nunique())}


def intervals(base,filtered,days):
    if filtered.empty:return {'net2_ci95':[None,None],'delta_ci95':[None,None],'net2_conditional72_ci':[None,None],'delta_conditional72_ci':[None,None]}
    n=len(days);block=min(5,n);rng=np.random.default_rng(SEED)
    idx=((rng.integers(0,n,(20000,int(np.ceil(n/block)),1))+np.arange(block))%n).reshape(20000,-1)[:,:n]
    def totals(t):return t.groupby('session').size().reindex(days,fill_value=0).to_numpy(),t.groupby('session').net2_index_points.sum().reindex(days,fill_value=0).to_numpy()
    bc,bp=totals(base);fc,fp=totals(filtered);bn=bc[idx].sum(axis=1);fn=fc[idx].sum(axis=1);good=(bn>0)&(fn>0)
    bm=bp[idx].sum(axis=1)[good]/bn[good];fm=fp[idx].sum(axis=1)[good]/fn[good]
    alpha=.05/CONTRASTS
    return {'net2_ci95':np.quantile(fm,[.025,.975]).tolist(),'delta_ci95':np.quantile(fm-bm,[.025,.975]).tolist(),
            'net2_conditional72_ci':np.quantile(fm,[alpha/2,1-alpha/2]).tolist(),'delta_conditional72_ci':np.quantile(fm-bm,[alpha/2,1-alpha/2]).tolist()}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=PHASE2/'option-nse-retained-eod.json';ledger_source=OLD/'lab-selected-trades.csv'
    dump('positioning-preregister.json',{'hypothesis_id':'ALPHA-OI-001','created_research_date':'2026-11-09',
        'hypothesis':'Prior-completed-session positioning may improve frozen price-rule opportunity selection. Report both trend and contrarian PCR orientation.',
        'mechanism':'Inventory/hedging constraints and disagreement can condition next-session movement; OI does not identify trader direction or guarantee support/resistance.',
        'falsification':'No repeatable incremental net index expectancy versus identical covered price-only opportunities; unstable expiry/regime transfer or wide uncertainty rejects promotion.',
        'parameters':{'families':FAMILIES,'expiry_buckets':['nearest_nonexpiry_day','month_end_proxy'],'filters':FILTERS,
                      'pcr_neutral':1,'oi_wall_distance':'one signal-time ATR','maxpain':'same-side distance to exact prior-chain payout minimum'},
        'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [source,ledger_source,OLD/'nifty-upstox-1day.json',OLD/'nifty-upstox-5minute.json']},
        'script_sha256':sha(Path(__file__)),'feature_dependency_sha256':sha(Path(lab.__file__)),'availability':'Use exactly previous observed NIFTY daily session only. EOD publication before next session is assumed; archived release times absent. No same-day or stale chain carry.',
        'pcr_change':'Same expiry, matched identical token/strike/type/lot across the immediately preceding two archived NIFTY sessions, never cross-expiry rolling change.',
        'volume_pcr':'Sum reported put volume / call volume, distinct from OI PCR; neither reveals whether options were bought or written.',
        'selection':'No new strategy/filter winner; all outcomes disclosed. Fixed opportunity subsets keep phase-one entries/exits. Index units only.',
        'multiplicity':f'{CONTRASTS} fixed conditional contrasts:3families x2expirybuckets x6filters x(net2,improvement). 20000 pairedfive-sessionblock bootstrap; approximate Bonferroni intervals, not correction of earlier strategy search.',
        'futures':'Prior daily same-contract price/OI classifications only where existing raw archives support consecutive observations; no fabricated continuous intraday futures.'})
    dump('positioning-option-protocol.json',{'experiment_id':'ALPHA-OI-OPTION-001','created_research_date':'2026-11-09',
        'status':'Retrospective diagnostic extension; aggregate positive five-session premium results were previously inspected, not independent validation.',
        'rules':'Apply exactly the same six prior-session positioning masks to all available recent62 option-candle proxies; no parameter/contract tuning.',
        'baseline':'Identical available premium-policy opportunities; report allfiltersandmissinggroups. No confidence/profitability claim onfive sessions.',
        'premium_source_sha256':sha(PHASE2/'option-intraday-trades.csv')})
    archives,futures,raw_audit,conflicts=read_sources();dates=sorted(archives)
    daily=pd.DataFrame(json.loads((OLD/'nifty-upstox-1day.json').read_text()));daily['day']=daily.ts.str[:10];dailydays=sorted(daily.day)
    previous={day:(dailydays[i-1] if i else None) for i,day in enumerate(dailydays)}
    d,audit=lab.load_data();f=lab.features(d)
    sourcefeatures={t.isoformat():{'spot':float(c),'atr':float(a),'efficiency':float(e) if np.isfinite(e) else None,'trend':float(tr)} for t,c,a,e,tr in zip(f.known_at,f.close,f.atr,f.efficiency,f.trend) if np.isfinite(a)}
    t=pd.read_csv(ledger_source);t=t[t.strategy.str.split('|').str[0].isin(FAMILIES)].copy();t['family']=t.strategy.str.split('|').str[0]
    rows=[];rejections=[];checks=0
    for r in t.to_dict('records'):
        day=r['session'];prior=previous.get(day)
        if prior not in archives:
            rejections.append({'strategy':r['strategy'],'session':day,'signal_at':r['signal_at'],'reason':'immediately_prior_NIFTY_session_archive_unavailable','required_date':prior});continue
        prior2=previous.get(prior);chains={c['expiry']:c for c in archives[prior]['chains']};expiries=sorted(e for e in chains if e>day)
        if not expiries:continue
        months={}
        for e in chains:months[e[:7]]=max(e,months.get(e[:7],e))
        monthly=sorted(e for e in months.values() if e>day)
        feat=sourcefeatures[pd.Timestamp(r['signal_at']).isoformat()]
        for bucket,expiry in [('nearest_nonexpiry_day',expiries[0]),('month_end_proxy',monthly[0] if monthly else None)]:
            if expiry is None:continue
            chain=chains[expiry];previouschain=next((c for c in archives.get(prior2,{}).get('chains',[]) if c['expiry']==expiry),None)
            info=chain_summary(chain,previouschain)
            if info is None:continue
            row={**r,**info,'expiry_bucket':bucket,'selected_expiry':expiry,'prior_session':prior,'prior_prior_session':prior2,
                 'prior_archive_sha256':archives[prior]['source_sha256'],'signal_spot':feat['spot'],'signal_atr':feat['atr'],
                 'expiry_session':day in chains,'dte_calendar_days':(pd.Timestamp(expiry)-pd.Timestamp(day)).days}
            row['futures_same_contract_price_change']=None;row['futures_same_contract_oi_change']=None;row['futures_prior_basis_points']=None
            futs=[v for v in futures.get(prior,[]) if v['expiry']>day]
            if futs:
                selected=min(futs,key=lambda v:v['expiry']);old=next((v for v in futures.get(prior2,[]) if v['token']==selected['token'] and v['expiry']==selected['expiry'] and v['lot']==selected['lot'] and v['volume']>0 and v['close']>0),None)
                prior_close=float(daily.loc[daily.day==prior,'close'].iloc[0]);row['futures_prior_basis_points']=selected['close']-prior_close
                if old and selected['volume']>0 and selected['close']>0:
                    row['futures_same_contract_price_change']=selected['close']-old['close'];row['futures_same_contract_oi_change']=selected['open_interest_reported']-old['open_interest_reported']
            assert prior<day<expiry;checks+=1
            assert not previouschain or previouschain['expiry']==expiry;checks+=1
            assert np.isclose(row['gross_index_points'],row['direction']*(row['exit']-row['entry']));checks+=1
            rows.append(row)
    panel=pd.DataFrame(rows);panel.to_csv(OUT/'positioning-trade-panel.csv',index=False)
    pd.DataFrame(rejections).to_csv(OUT/'positioning-rejections.csv',index=False)
    summary=[];kept_rows=[];final_days=sorted(day for day in d.day.unique() if day>='2026-06-29' and previous.get(day) in archives)
    for (family,bucket,part),base in panel.groupby(['family','expiry_bucket','split']):
        base=base.copy();masks=add_filters(base)
        for name,mask in masks.items():
            kept=base[mask].copy();r={'family':family,'expiry_bucket':bucket,'split':part,'filter':name,'baseline_n':len(base),**stats(kept)}
            r['improvement_net2_mean']=r['net2_mean']-base.net2_index_points.mean() if len(kept) else None
            if part=='holdout':r.update(intervals(base,kept,final_days))
            r['conditional_gate']=bool(part=='holdout' and name!='baseline' and r['n']>=30 and r.get('net2_conditional72_ci',[None])[0] is not None and r['net2_conditional72_ci'][0]>0 and r['delta_conditional72_ci'][0]>0)
            summary.append(r)
            for record in kept.to_dict('records'):kept_rows.append({'filter':name,**record})
    for r in summary:
        for field in ['net2_ci95','delta_ci95','net2_conditional72_ci','delta_conditional72_ci']:
            if field in r:
                low,high=r.pop(field);r[field+'_low']=low;r[field+'_high']=high
    results=pd.DataFrame(summary);results.to_csv(OUT/'positioning-ablations.csv',index=False)
    # Expiry/time diagnostics do not classify final-day behavior using future price information.
    subgroup=[]
    base=panel[(panel.expiry_bucket=='nearest_nonexpiry_day')&(panel.split=='holdout')]
    for key in ['expiry_session','direction']:
        for (family,value),g in base.groupby(['family',key]):subgroup.append({'family':family,'dimension':key,'value':str(value),**stats(g)})
    base=base.copy();base['entry_hour']=pd.to_datetime(base.entry_at).dt.hour
    for (family,hour),g in base.groupby(['family','entry_hour']):subgroup.append({'family':family,'dimension':'entry_hour','value':str(hour),**stats(g)})
    # Futures confirmation is explicitly exploratory and has its own covered baseline.
    future_results=[]
    futures_base=base.dropna(subset=['futures_same_contract_price_change','futures_same_contract_oi_change'])
    for family,g in futures_base.groupby('family'):
        confirmed=g[(g.direction*g.futures_same_contract_price_change>0)&(g.futures_same_contract_oi_change>0)]
        future_results.append({'family':family,'baseline':stats(g),'prior_price_and_OI_buildup_alignment':stats(confirmed)})
    option=pd.read_csv(PHASE2/'option-intraday-trades.csv');option=option[option.status=='observed_candle_proxy'].copy()
    keys=['strategy','signal_at','expiry_bucket']
    feature_columns=keys+['family','direction','oi_pcr','common_pcr_log_change','volume_pcr','max_call_oi_strike','max_put_oi_strike','signal_spot','signal_atr','maxpain','prior_session']
    # Source signals share direction; discard only the duplicate direction field before validated join.
    joined=option.drop(columns='direction').merge(panel[feature_columns],on=keys,how='left',validate='many_to_one')
    option_results=[];option_ledger=[]
    for (family,bucket,strike),g in joined.groupby(['family','expiry_bucket','strike_rule']):
        g=g.copy();masks=add_filters(g)
        for name,mask in masks.items():
            chosen=g[mask]
            option_results.append({'family':family,'expiry_bucket':bucket,'strike_rule':strike,'filter':name,
                'n':len(chosen),'baseline_n':len(g),'sessions':int(chosen.session.nunique()),
                'gross_mean_rupees_per_lot':float(chosen.gross_rupees_per_lot.mean()) if len(chosen) else None,
                'illustrative_net_mean_rupees_per_lot':float(chosen.illustrative_net_rupees_per_lot.mean()) if len(chosen) else None,
                'severe_net_mean_rupees_per_lot':float(chosen.severe_net_rupees_per_lot.mean()) if len(chosen) else None,
                'delta_illustrative_net_mean':float(chosen.illustrative_net_rupees_per_lot.mean()-g.illustrative_net_rupees_per_lot.mean()) if len(chosen) else None})
            for record in chosen.to_dict('records'):option_ledger.append({'positioning_filter':name,**record})
    pd.DataFrame(option_results).to_csv(OUT/'positioning-option-ablations.csv',index=False)
    pd.DataFrame(option_ledger).to_csv(OUT/'positioning-option-trades.csv',index=False)
    # Source-availability invariance: removing tomorrow's archives does not change the selected prior chain.
    for day in sorted(t.session.unique())[::40]:
        prior=previous.get(day)
        if prior in archives:
            prefix={k:v for k,v in archives.items() if k<day}
            assert prior in prefix and prior<day
            assert chain_summary(archives[prior]['chains'][0])==chain_summary(prefix[prior]['chains'][0])
            checks+=1
    # A newly listed contract must affect level PCR but not matched-contract change.
    prior={'contracts':[['1',100,'CE',100,65,1,1],['2',100,'PE',100,65,1,1]]}
    current={'contracts':[['1',100,'CE',200,65,1,1],['2',100,'PE',100,65,1,1]]}
    with_new={'contracts':current['contracts']+[['3',110,'PE',1e9,65,1,1]]}
    a=chain_summary(current,prior);b=chain_summary(with_new,prior)
    assert np.isclose(a['common_pcr_log_change'],-np.log(2)) and np.isclose(a['common_pcr_log_change'],b['common_pcr_log_change'])
    assert a['oi_pcr']!=b['oi_pcr'];checks+=2
    report={'frozen_signal_trades':len(t),'covered_signal_trades':len(panel)//2,'feature_policy_rows':len(panel),
            'rejected_signal_trades':len(rejections),'retained_archive_days':255,'all_archive_days':len(archives),'archive_first':dates[0],'archive_last':dates[-1],
            'raw_zip_days':len(raw_audit),'conflicting_source_days':conflicts,'final_covered_sessions':len(final_days),
            'assertions_passed':checks,'conditional_gate_passes':int(results.conditional_gate.sum()),
            'final_results':results[results.split=='holdout'].replace({np.nan:None}).to_dict('records'),
            'subgroups':subgroup,'futures_diagnostic':future_results,'raw_archives':raw_audit,
            'recent_option_diagnostic':{'source_policy_rows':len(option),'joined_feature_rows':int(joined.prior_session.notna().sum()),'results':option_results}}
    dump('positioning-summary.json',report)
    dump('positioning-source-audit.json',{'archives':[{k:v for k,v in r.items() if k!='chains'} for _,r in sorted(archives.items())],
                                       'raw_archives':raw_audit,'source_conflicts_excluded':conflicts,'input_nifty_audit':audit,'source_code_sha256':sha(Path(__file__))})
    lines=['# Project Alpha: previous-session positioning research','',
        f"{len(t)} frozen intraday signal trades; {len(panel)//2} have exactly the prior NIFTY session's dated archive, yielding {len(panel)} expiry-policy feature rows. {len(rejections)} signals lack that prior archive and remain explicit rejections. Sources span {dates[0]}–{dates[-1]} across {len(archives)} archived sessions.",
        '', 'This adds a valid EOD positioning experiment; it does not reconstruct intraday historical OI updates. Each decision uses only the immediately preceding NIFTY session, never current-session closing OI or a stale older chain. The source file was retrieved later; publication before the next open is assumed and historical release timestamps were not independently archived.',
        '', 'Frozen phase-one entries/exits are retained. The baseline is the same covered price-only opportunity set. All returns are underlying index points after2/5 illustrative points, not option-premium expectancy. Filtered-minus-baseline differences compare subsets and are observational, not causal treatment estimates.',
        '', 'Nearest future expiry and month-end listed-expiry proxy are fixed from the prior dated universe. Same-expiry common-contract PCR change matches token, strike, side and lot across the preceding two NIFTY sessions. OI is counted once per leg; ratios do not require guessing trade direction. Volume PCR is separately calculated and cannot identify whether puts were bought or written. OI walls/maxpain are hypotheses, never guaranteed support, resistance or attraction.',
        '', '|Family|Expiry bucket|Filter|Final N|Baseline N|Net2 points|Net2 ordinary95%interval|Change vs covered baseline|Change ordinary95%interval|',
        '|---|---|---|---:|---:|---:|---|---:|---|']
    for r in report['final_results']:
        if not r['n']:continue
        ci=[r['net2_ci95_low'],r['net2_ci95_high']];delta=[r['delta_ci95_low'],r['delta_ci95_high']]
        lines.append(f"|{r['family']}|{r['expiry_bucket']}|{r['filter']}|{r['n']}|{r['baseline_n']}|{r['net2_mean']:.2f}|{ci[0]:.2f} to {ci[1]:.2f}|{r['improvement_net2_mean']:.2f}|{delta[0]:.2f} to {delta[1]:.2f}|")
    lines+=['',f"Conditional gate passes: {report['conditional_gate_passes']}. Gate requires>=30final trades, positive lower net2 interval and positive lower improvement interval after approximate Bonferroni correction across72fixed contrasts. These intervals remain conditional on previously selected rules and do not correct phase-one strategy search. 20,000pairedfive-sessionblock draws are a Monte Carlo approximation, especially in extreme tails. No strategy is promoted.",
        '', 'The full CSV also discloses development/validation outcomes, ordinary and72-contrast intervals, and every rejection. Same expiry-policy selections can duplicate opportunities. Expiry-day, side and entry-hour breakdowns are descriptive, not additional selection criteria.',
        '', '## Futures boundary',
        'Existing raw NSE ZIPs also supply dated NIFTY futures close/OI. Where both immediately prior sessions contain the same token/expiry/lot, an exploratory prior-day price-and-OI buildup condition is reported on its own covered baseline. Close-to-close price/basis values are asynchronous EOD proxies. No continuous intraday futures or futures order-book data was manufactured.',
        '', '|Family|Futures-covered final N|Covered baseline net2|Confirmed N|Confirmed net2|','|---|---:|---:|---:|---:|']
    for r in future_results:
        a=r['baseline'];b=r['prior_price_and_OI_buildup_alignment'];lines.append(f"|{r['family']}|{a['n']}|{a['net2_mean']:.2f}|{b['n']}|{b['net2_mean'] if b['net2_mean'] is not None else 'NA'}|")
    lines+=['','## Actual recent premium diagnostic',
        f"The same fixed prior-session filters were joined to {len(option)} accepted recent intraday option-policy proxies; {int(joined.prior_session.notna().sum())} had positioning features. All84 family/expiry/strike/filter cells are disclosed in positioning-option-ablations.csv and accepted feature-filtered rows in positioning-option-trades.csv.",
        'This is a retrospective diagnostic on the previously inspected2–6November week. It is not a new holdout. Four-to-seven baseline trades per policy, often fewer after filtering, cannot establish positioning-dependent option expectancy. Premium proxy and cost limitations from the phase-two intraday study remain. No winner or confidence claim is made from these tiny cells.']
    lines+=['',f"{checks} source/date/identity/PnL checks passed. All input hashes and source dates are in positioning-source-audit.json and positioning-preregister.json. Prior-data features can be reconstructed, but observed-at publication precision remains weaker than a contemporaneously captured intraday chain.",
        '', '[NSE official derivatives reports](https://www.nseindia.com/all-reports-derivatives) provide dated EOD data; [NSE option-chain page](https://www.nseindia.com/option-chain) describes the current chain display. These are different data products.']
    (OUT/'positioning-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['covered_signal_trades','feature_policy_rows','all_archive_days','conditional_gate_passes','assertions_passed']}))


if __name__=='__main__':main()
