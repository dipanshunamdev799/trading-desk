"""Conservative source clocks and five intraday decision experiments."""
import gzip

from .common import *
from .data import Daily
from .fitting import fit

SECTORS=('bank','financial','it','auto','broad','defensive','etf')
DOM=('cash5','cash21','breadth5','breadth21','finance','defensive','concentration','vix_level','atm')
OFF=('vix_us','vxn','fx_shock','oil_shock','us_breadth5')
FOREIGN={
    'spx':('^GSPC','America/New_York','16:00'),
    'dow':('^DJI','America/New_York','16:00'),
    'ftse':('^FTSE','Europe/London','16:35'),
    'dax':('^GDAXI','Europe/Berlin','17:40'),
    'nikkei':('^N225','Asia/Tokyo','15:35'),
    'hsi':('^HSI','Asia/Hong_Kong','16:15'),
}
CASH=('cash_gap','cash_move','cash_rv','cash_down_var','cash_intra_reversal','cash_extent')
GROUPS={
    'domestic_prior':DOM,
    'offshore_fresh':DOM+OFF+tuple(FOREIGN),
    'offshore_prior_only':DOM+OFF,
    'market_prefix':DOM+OFF+tuple(FOREIGN)+CASH,
    'sector_leadership':DOM+OFF+tuple(FOREIGN)+CASH+('leadership','sector_participation','sector_convergence','sector_synchronization'),
    'sector_etf':DOM+OFF+tuple(FOREIGN)+CASH+('leadership','sector_participation','sector_convergence','sector_synchronization',
                 'broad_relative','defensive_relative','etf_basis_return','etf_activity_20'),
    'sector_placebo':DOM+OFF+tuple(FOREIGN)+CASH+('leadership','sector_participation','sector_convergence','sector_synchronization',
                 'broad_relative','defensive_relative','etf_basis_return','etf_activity_20')
}


def candles(paths,step):
    bins={}; hashes=[]; conflicts=0
    for f in sorted(paths):
        r=json.loads(f.read_text(encoding='utf-8-sig'))
        assert r['status']=='success'
        hashes.append(dict(file=f.relative_to(ROOT).as_posix(),sha256=sha(f),bars=len(r['data']['candles'])))
        for ts,*a in r['data']['candles']:
            t=pd.Timestamp(ts).tz_convert('Asia/Kolkata')
            d=t.strftime('%Y-%m-%d')
            if not FIRST<=d<=FREEZE:
                continue
            z=bins.setdefault(d,{})
            if t in z and z[t]!=a:
                conflicts+=1
                continue
            z[t]=a
    result={}
    for day,values in bins.items():
        idx=sorted(values)
        a=pd.DataFrame([values[i] for i in idx],index=pd.DatetimeIndex(idx),columns=['open','high','low','close','vol','oi'])
        # Exclude premarket, auction and irregular-time bars independently of each day's observed addressable prefix.
        session_open=pd.Timestamp(day+'T09:15:00',tz='Asia/Kolkata')
        session_close=pd.Timestamp(day+'T15:30:00',tz='Asia/Kolkata')
        in_time=(a.index>=session_open)&(a.index<session_close)
        a=a.loc[in_time].copy()
        a['end']=(a.index+pd.Timedelta(minutes=step)).where(a.index+pd.Timedelta(minutes=step)<=session_close,session_close)
        result[day]=a
    return result,hashes,conflicts


def foreign():
    output={}; source={}
    for key,(ticker,zone,clock) in FOREIGN.items():
        p=V5/'sources'/f'g_{ticker}.json'
        j=json.loads(p.read_text(encoding='utf-8'))
        f=pd.DataFrame(j['rows']).sort_values('day').drop_duplicates('day').set_index('day')
        f=f.loc[FIRST:FREEZE]
        f=f.loc[pd.DatetimeIndex(f.index).day_of_week<5].copy()
        f['r']=np.log(f.close).diff()
        # Vendor midnight stamps are date labels. Use local cash closes plus a one-hour safety allowance.
        f['available']=[pd.Timestamp(f'{d}T{clock}:00',tz=zone).tz_convert('Asia/Kolkata')+pd.Timedelta(hours=1) for d in f.index]
        output[key]=f
        source[key]=dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),timezone=zone,assumed_local_close=clock,buffer_minutes=60,
                         reconstructable_end_of_day_marks=len(f))
    return output,source


def take(panel,day,cutoff,min_bars):
    a=panel.get(day)
    if a is None:
        return None
    a=a.loc[a.end<=cutoff]
    if len(a)<min_bars or a.index[0].strftime('%H:%M')!='09:15':
        return None
    return a


def snapshots(d):
    p,hh,conf=candles((V13/'sources/upstox').glob('nifty-5m-*'),5)
    sets={}; hashes={'nifty':hh}; conflicts={'nifty':conf}
    for name in SECTORS:
        root=(V10/'sources/intraday') if name in SECTORS[:4] else OUT/'sources/market-intraday'
        sets[name],hashes[name],conflicts[name]=candles(root.glob(f'{name}-*'),25)
    external,external_receipt=foreign()
    win=matrix('original-windows.csv').reset_index().set_index(['horizon','origin'])
    pre_x=d.features.reindex(columns=(*DOM,*OFF))
    px=d.prices
    out=[]; receipts=[]; closure=[]
    # Cohort includes additional warmup rows for fitting. Model scores explicitly select evaluation cohorts.
    for i,day in enumerate(d.sessions):
        if i==0:
            continue
        prev=d.sessions[i-1]
        old_close=px.close.iloc[i-1]
        close=px.close.iloc[i]
        eod=take(p,day,pd.Timestamp(day+'T16:55:00',tz='Asia/Kolkata'),75)
        if eod is not None:
            closure.append(dict(day=day,intraday_close=eod.close.iloc[-1],official_close=close,
                                gap_points=float(eod.close.iloc[-1]-close),bars=len(eod)))
        for stage,clock in CLOCKS.items():
            cutoff=pd.Timestamp(day+'T'+clock+':00',tz='Asia/Kolkata')
            padded=cutoff-pd.Timedelta(minutes=5)
            done=stage=='completed'
            before=stage=='pre_open'
            a=take(p,day,padded,{'pre_open':1,'opening':9,'midday':38,'near_close':70,'completed':75}[stage]) if not before else None
            if not (before or done) and a is None:
                continue
            on=prev if not done else day
            x=pre_x.loc[on].to_dict()
            r=dict(day=day,stage=stage,decision=cutoff.isoformat(),observation_day=on,last_cash_bar_end=None,
                   option_source=d.features.at[on,'option_day'],cutoff_bar=padded.isoformat())
            for column,f in external.items():
                eligible=f[f.available.le(cutoff)]
                x[column]=float(eligible.r.iloc[-1]) if len(eligible) else np.nan
                r['foreign_'+column]=eligible.available.iloc[-1].isoformat() if len(eligible) else None
                r['foreign_'+column+'_date']=eligible.index[-1] if len(eligible) else None
            if a is not None:
                r['last_cash_bar_end']=a.end.iloc[-1].isoformat()
                op=a.open.iloc[0]
                spot=close if done else a.close.iloc[-1]
                prefix=np.diff(np.log(np.r_[op,a.close.to_numpy()]))
                x.update(cash_gap=np.log(op/old_close),cash_move=np.log(spot/old_close),
                         cash_rv=np.sqrt(prefix@prefix),cash_down_var=np.minimum(prefix,0)@np.minimum(prefix,0),
                         cash_intra_reversal=np.log(spot/a.close.iloc[max(0,len(a)//2-1)]),
                         cash_extent=(a.high.max()-a.low.min())/old_close)
            else:
                spot=close if done else old_close
            sectors={nm:take(q,day,padded,{'pre_open':1,'opening':1,'midday':7,'near_close':14,'completed':15}[stage])
                   for nm,q in sets.items()} if not before else {}
            sr={}; vectors=[]
            for nm,b in sectors.items():
                if b is None:
                    continue
                r[nm+'_bar_end']=b.end.iloc[-1].isoformat()
                # Compare instruments against the identical latest endpoint available for their common bar clock.
                last_cash=a[a.end.le(b.end.iloc[-1])] if a is not None else None
                if last_cash is None or not len(last_cash):
                    continue
                ivret=np.log(b.close.iloc[-1]/b.open.iloc[0])
                cr=np.log(last_cash.close.iloc[-1]/a.open.iloc[0])
                sr[nm]=ivret-cr
                if nm in SECTORS[:4]:
                    vectors.append(np.diff(np.log(np.r_[b.open.iloc[0],b.close])))
                if nm=='etf':
                    # Compare only the same number of already-completed bars from previous sessions.
                    prior=[sets[nm][z].vol.iloc[:len(b)].sum() for z in d.sessions[max(1,i-20):i]
                           if z in sets[nm] and len(sets[nm][z])>=len(b)]
                    x['etf_activity_20']=np.log((1+b.vol.sum())/(1+np.median(prior))) if len(prior)>=8 else np.nan
            fl=['bank','financial','it','auto']
            if all(z in sr for z in fl):
                x['leadership']=float(np.mean([sr['bank'],sr['financial']])-np.mean([sr['it'],sr['auto']]))
                x['sector_participation']=float(np.mean([v.sum()>0 for v in vectors]))
                x['sector_convergence']=float(np.std([sr[z] for z in fl]))
                m=min(map(len,vectors))
                tol=np.array([z[:m] for z in vectors])
                x['sector_synchronization']=float(np.abs(np.sign(tol).mean(axis=0)).mean())
            for name,nm in [('broad_relative','broad'),('defensive_relative','defensive'),('etf_basis_return','etf')]:
                x[name]=sr.get(nm,np.nan)
            r['old_domestic_source']=on
            r['sector_ready']=int(all(nm in sr for nm in fl))
            r['added_source_ready']=int(r['sector_ready'] and all(nm in sr for nm in ('broad','defensive','etf')))
            assert all(pd.Timestamp(t)<=cutoff for field,t in r.items() if (field.endswith('_bar_end') or field in {'foreign_'+f for f in FOREIGN}) and t)
            assert pd.isna(r['option_source']) or r['option_source']<on
            receipts.append(r)
            targets=[]
            if not done:
                targets.append(('same_session',day,close,spot,prev))
            if before:
                targets.append(('immediate_open',day,px.open.iloc[i],old_close,prev))
            if i+1<len(px):
                nextday=d.sessions[i+1]
                targets.extend([('next_open_gap',nextday,px.open.iloc[i+1],close,on),
                                ('next_close',nextday,px.close.iloc[i+1],spot,on)])
            for kind,h in [('weekly_endpoint',5),('monthly_endpoint',21)]:
                if i-1+h<len(d.sessions):
                    target=d.sessions[i-1+h]
                    targets.append((kind,target,px.close.iloc[i-1+h],spot,prev))
            for name,end,price,ref,original in targets:
                h=5 if name=='weekly_endpoint' else 21 if name=='monthly_endpoint' else None
                cohort=(win.at[(h,original),'cohort'] if (h,original) in win.index else '') if h else (
                        'early' if '2025-11-03'<=day<='2026-05-08' else 'later' if day>'2026-05-08' else '')
                origref=old_close if h else ref
                out.append(dict(day=day,stage=stage,target_name=name,target=end,origin=original,reference=ref,cohort=cohort,
                           target_log=np.log(price/ref),target_total_log=np.log(price/origref),known=np.log(ref/origref),eval_sectors=r['sector_ready'],
                           eval_new=r['added_source_ready'],**x))
    write('session-feature-receipts.csv',pd.DataFrame(receipts))
    write('session-cash-reconciliation.csv',pd.DataFrame(closure))
    save('session-source-audit.json',dict(candle_files=hashes,candle_conflicts=conflicts,global_files=external_receipt,
        source_rule='Authentic historical candles, reconstruction diagnostic. Use end plus 5 minutes. Every foreign close uses its local calendar and DST plus one hour; FX, oil, global-vol use earlier audited V14 day labels. No intraday options or official intraday equal-weight.',
        receipt_rows=len(receipts)))
    return pd.DataFrame(out)


def empirical_crps(a,y):
    a=np.sort(a)
    n=len(a)
    return float(np.abs(a-y).mean()-a@(2*np.arange(n)-n+1)/n**2)


def main():
    d=Daily.load()
    features=snapshots(d)
    rows=[]; log=[]
    for (stage,target),g in features.groupby(['stage','target_name'],sort=False):
        g=g.sort_values('day').reset_index(drop=True)
        X=g.reindex(columns=list(dict.fromkeys(sum(GROUPS.values(),()))))
        y=g.target_log.to_numpy()
        cols=np.array(X.columns)
        data=X.to_numpy()
        for i,case in g[g.cohort.ne('')].iterrows():
            train=np.flatnonzero(g.target.lt(case.day).to_numpy() & (np.arange(len(g))<i))[-160:]
            if len(train)<54:
                continue
            cutoffs=g.target.iloc[train]
            assert cutoffs.max()<case.day
            offset=float(case.known)
            resid=y[train]
            laws={'price_zero':resid-np.median(resid),'unconditional':resid}
            for name,c in GROUPS.items():
                if name in {'market_prefix','sector_leadership','sector_etf','sector_placebo'} and stage=='pre_open':
                    continue
                if name=='sector_leadership' and case.eval_sectors!=1:
                    continue
                if name in {'sector_etf','sector_placebo'} and case.eval_new!=1:
                    continue
                use=np.array([np.flatnonzero(cols==n)[0] for n in c])
                a=data[train[:,None],use]; vec=data[i,use]
                mask=np.isin(np.array(c),GROUPS['sector_etf'][len(GROUPS['market_prefix']):])
                rng=np.random.default_rng(SEED+i) if name=='sector_placebo' else None
                md=fit(a,resid,125 if name.startswith('sector') else 95,rng,mask)
                loc=.70*float(md.values(vec))
                # Retain the same centered residual law across candidates to isolate location.
                laws[name]=loc+(resid-np.median(resid))
                log.append(dict(stage=stage,target=target,day=case.day,train_n=len(train),last_mature=cutoffs.max(),model=name,
                                **md.receipt(c)))
            for n,a in laws.items():
                threshold= -offset
                p=(np.count_nonzero(a>threshold)+.5)/(len(a)+1)
                v=y[i]+offset>0
                br=(p-v)**2
                ll=-np.log(p if v else 1-p)
                lo,med,hi=np.quantile(a,[.1,.5,.9])+offset
                rows.append(dict(day=case.day,cutoff=stage,target_name=target,target=case.target,origin=case.origin,
                    cohort=case.cohort,model=n,case_sector=case.eval_sectors,case_new=case.eval_new,n_train=len(train),last_mature=cutoffs.max(),
                    actual=case.target_total_log,p=p,median=med,lower=lo,upper=hi,brier=br,log_loss=ll,
                    crps=empirical_crps(a+offset,case.target_total_log),mae=abs(med-case.target_total_log),covered=int(lo<=case.target_total_log<=hi)))
    out=pd.DataFrame(rows)
    assert out.last_mature.lt(out.day).all() and out.day.le(out.target).all()
    write('session-forecasts.csv.gz',out)
    with gzip.open(OUT/'session-fit-ledger.json.gz','wt',encoding='utf-8',compresslevel=4) as f:
        json.dump(log,f,allow_nan=False,separators=(',',':'))
    refs={'domestic_prior':'price_zero','offshore_fresh':'offshore_prior_only','offshore_prior_only':'domestic_prior',
          'market_prefix':'offshore_fresh','sector_leadership':'market_prefix','sector_etf':'sector_leadership',
          'sector_placebo':'sector_leadership','unconditional':'price_zero'}
    table=[]
    for (stage,target),g in out.groupby(['cutoff','target_name']):
        for model,parent in refs.items():
            x=g[g.model.eq(model)].merge(g[g.model.eq(parent)],on='day',suffixes=('', '_base'))
            if x.empty:
                continue
            row=dict(checkpoint=stage,target=target,model=model,parent=parent,n=len(x),positive_rate=(x.actual>0).mean())
            for m in ('brier','log_loss','crps','mae','covered'):
                row.update({m:x[m].mean(),m+'_base':x[m+'_base'].mean(),m+'_delta':(x[m]-x[m+'_base']).mean()})
            table.append(row)
    write('session-evidence.csv',pd.DataFrame(table))
    print('Scored',len(rows),'timestamped session forecasts',flush=True)


if __name__=='__main__':
    main()
