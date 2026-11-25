"""Chronological, date-weighted cross-market and cross-horizon transfer."""
import joblib
from sklearn.linear_model import Ridge
from .common import *
from .estimators import Distribution,diagnostics
from .experiments import common_indices,cohort_queries,score_law,buckets
from .features import cached
from research.nifty_forecast_v5.data import load


TASKS=[1,3,5,10,15,21]
CONFIG={
 'X_ONLY':('only','BASE5'),
 'X_POOL':('pooled','X_ONLY'),
 'X_SECTORS':('sectors','X_ONLY'),
 'X_ETFS':('etfs','X_ONLY'),
 'X_GLOBAL':('global','X_ONLY'),
 'X_ADJUST':('adjust','X_POOL'),
 'X_FACTORS':('factors','X_ONLY'),
 'X_ADAPT':('adapt','X_ONLY'),
 'X_MULTI':('multi','X_ONLY'),
 'X_MULTI_SHORT':('short','X_ONLY'),
 'X_SHIFT':('shift','X_ADAPT'),
 'X_RANDOM':('random','X_ADAPT'),
 'X_UNRELATED':('unrelated','X_ONLY'),
}


def panel(price):
    raw,_=load();idx=price.index
    quotes={'NIFTY':price}
    grouping={'NIFTY':'nifty'}
    selections={
      'broad':['idx_Nifty_100','idx_Nifty_500','idx_NIFTY_MIDCAP_100'],
      'sectors':['bank_nifty','nifty_it','nifty_auto','nifty_financial','nifty_fmcg','nifty_pharma','nifty_energy','nifty_metal'],
      'equities':['s_RELIANCE','s_HDFCBANK','s_INFY','s_ICICIBANK','s_TCS','s_SUNPHARMA','s_TATAMOTORS','s_AXISBANK'],
      'etfs':['niftybees'],
    }
    for family,names in selections.items():
        for name in names:
            if name in raw:quotes[name]=raw[name];grouping[name]=family
    extra=pd.read_csv(V9/'acquired-candles.csv')
    for name in ['bankbees','financial_etf','psu_etf','insurance_hdfc','insurance_sbi','private_bank']:
        quotes[name]=extra[extra.instrument.eq(name)].set_index('day')
        grouping[name]='equities' if 'insurance' in name or name=='private_bank' else 'etfs'
    availability=pd.read_csv(V8/'new-global-availability.csv')
    availability=availability[availability.assumed_available<=availability.decision]
    for ticker in ['NASDAQCOM','SP500','VIXCLS','DGS10','DEXINUS']:
        file=V8/f'sources/{ticker}.csv';a=availability[availability.series.eq(ticker)].set_index('origin')
        if not file.exists() or a.empty:continue
        source=pd.read_csv(file,index_col=0)[ticker];source=pd.to_numeric(source,errors='coerce')
        q=a.source_day.map(source).rename('close').to_frame()
        quotes[ticker]=q;grouping[ticker]='global' if ticker in ['NASDAQCOM','SP500'] else 'unrelated'
    close=pd.DataFrame({n:f.close.reindex(idx) for n,f in quotes.items()}).where(lambda z:z>0)
    lp=np.log(close);daily=lp.diff();rv=daily.rolling(21,min_periods=15).std().clip(lower=.001)
    dispersion=daily[list(n for n,g in grouping.items() if g=='sectors')].std(axis=1).rolling(5).mean()
    momentum=lp.diff(5);market=daily.NIFTY;beta=daily.rolling(63,min_periods=30).cov(market).div(market.rolling(63,min_periods=30).var().clip(lower=1e-8),axis=0).shift()
    adjustment=(daily-beta.mul(market,axis=0)).rolling(21,min_periods=15).sum()
    result=[];relative=(lp.bank_nifty-lp.NIFTY)
    for n in close:
        volume=quotes[n].get('volume',pd.Series(np.nan,index=quotes[n].index)).reindex(idx)
        turnover=(volume*close[n]).where(lambda a:a>0)
        activity=np.log(turnover/turnover.shift().rolling(21,min_periods=15).median())
        # Cash-index volume is normally absent. Training medians absorb missing activity.
        a=pd.DataFrame({'origin':idx,'instrument':n,'group':grouping[n],'mom5':momentum[n]/(rv[n]*np.sqrt(5)),
            'mom21':lp[n].diff(21)/(rv[n]*np.sqrt(21)),'vol21':np.log(rv[n]),'dispersion':dispersion/rv[n],
            'relative':adjustment[n]/(rv[n]*np.sqrt(21)),'activity':activity,'scale':rv[n]},index=idx)
        for h in TASKS:a[f'y{h}']=(lp[n].shift(-h)-lp[n])/(rv[n]*np.sqrt(h))
        a['risk_aux']=np.log((daily[n]**2).rolling(5).mean().shift(-5).clip(lower=1e-8).pow(.5)/rv[n])
        a['lead_aux']=(relative.shift(-5)-relative)/(rv[n]*np.sqrt(5))
        result.append(a.reset_index(drop=True))
    q=pd.concat(result,ignore_index=True).replace([np.inf,-np.inf],np.nan)
    assert not q.duplicated(['origin','instrument']).any()
    return q,grouping


COLS=['mom5','mom21','vol21','dispersion','relative','activity']


def transform(frame,med,scale):
    return ((frame[COLS].fillna(med)-med)/scale).clip(-7,7).to_numpy()


def regression(A,y,alpha=100,w=None):
    return Ridge(alpha=alpha).fit(A,y,sample_weight=w)


def trained(tab,dates,h,mode,seed):
    col=f'y{h}'
    a=tab[tab.origin.isin(dates)&tab[col].notna()].copy()
    own=a[a.instrument.eq('NIFTY')].sort_values('origin')
    group={'only':['nifty'],'sectors':['nifty','sectors'],'etfs':['nifty','etfs'],
           'global':['nifty','global'],'unrelated':['nifty','unrelated']}.get(mode,['nifty','broad','sectors','etfs','equities','global'])
    a=a[a.group.isin(group)].sort_values(['instrument','origin'])
    # Later exchange labels are given a further two eligible Indian-session buffers.
    a=a[~(a.group.isin(['global','unrelated'])&a.origin.isin(dates[-2:]))].copy()
    if len(own)<38 or (mode in ['global','unrelated'] and len(a)<=len(own)):raise ValueError('Insufficient mature rows')
    med=own[COLS].median().fillna(0);scale=own[COLS].std().fillna(1).clip(lower=1e-6)
    z=transform(own,med,scale);v=transform(a,med,scale)
    weights=(1/a.groupby('origin').origin.transform('size')).to_numpy()
    names=sorted(a.instrument.unique());projection=np.eye(z.shape[1]);adjustments=False
    if mode in ['multi','short']:
        aux=[f'y{k}' for k in (TASKS if mode=='multi' else [1,3,5])]+['risk_aux','lead_aux']
        common=own[aux].notna().all(axis=1)
        raw=own.loc[common,aux];target=(raw-raw.mean())/raw.std().clip(lower=.01)
        shared=regression(z[common],target,alpha=150)
        _,_,basis=np.linalg.svd(shared.coef_,full_matrices=False)
        projection=basis[:2].T
        fit=regression(z@projection,own[col])
    elif mode in ['adapt','random','shift','factors']:
        rng=np.random.default_rng(seed)
        if mode in ['random','shift']:
            for _,g in a[~a.instrument.eq('NIFTY')].groupby('instrument',sort=True):
                vals=g[col].to_numpy()
                if mode=='shift':perturbed=np.roll(vals,min(42,max(1,len(vals)//3)))
                else:
                    blocks=np.array_split(vals,max(1,len(vals)//10))
                    perturbed=np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
                a.loc[g.index,col]=perturbed
        pooled=regression(v,a[col],w=weights)
        if mode=='factors':
            # Spread-weighted supervised factor plus strongest orthogonal panel direction.
            _,_,vectors=np.linalg.svd(np.vstack([pooled.coef_*4,v*np.sqrt(weights[:,None])/np.sqrt(len(dates))]),full_matrices=False)
            projection=vectors[:2].T
            fit=regression(z@projection,own[col])
        else:
            fit=regression(z,own[col]-pooled.predict(z),alpha=350)
            fit.coef_+=pooled.coef_;fit.intercept_+=pooled.intercept_
    elif mode=='adjust':
        adjustment=pd.get_dummies(pd.Categorical(a.instrument,categories=names),dtype=float).to_numpy()*.7
        fit=regression(np.c_[v,adjustment],a[col],w=weights);adjustments=True
    else:fit=regression(v,a[col],w=weights)
    return {'fit':fit,'med':med,'scale':scale,'projection':projection,'instruments':names,'adjustments':adjustments,
            'panel_rows':len(a),'panel_origin_count':a.origin.nunique(),'nifty_rows':len(own),'latest_panel_origin':a.origin.max(),
            'instrument_counts':a.instrument.value_counts().to_dict(),'fit_dates':a.groupby('instrument').origin.apply(list).to_dict()}


def forecast(m,own):
    d=transform(own,m['med'],m['scale'])@m['projection']
    if m['adjustments']:
        adjust=np.zeros((len(d),len(m['instruments'])));adjust[:,m['instruments'].index('NIFTY')]=.7;d=np.c_[d,adjust]
    return m['fit'].predict(d)


def run():
    assert read('reproduction.json')['passed']
    path=OUT/'transfer-registry.json'
    if path.exists():raise FileExistsError(path)
    config={n:{'mode':mode,'parent':parent,'diagnostic':mode in ['random','shift','unrelated'],'horizons':[5,21],
               'hypothesis':'Instrument-normalized panel Ridge and NIFTY endpoint recalibration'} for n,(mode,parent) in CONFIG.items()}
    save(path.name,{'registered_at':now(),'seed':SEED,'configurations':config,'code_hash':sha(SRC/'transfer.py'),
       'maturity':'Entire training date group uses 21-session purge. Foreign auxiliary late cutoff excludes two more eligible rows.'})
    price=matrix('price.csv');tab,groups=panel(price);own=tab[tab.instrument.eq('NIFTY')].set_index('origin')
    write('transfer-panel.csv',tab)
    if not any(g=='global' for g in groups.values()):raise ValueError('Chronologically mapped global price series absent')
    save('transfer-panel-audit.json',{'groups':groups,'tasks':TASKS+['risk_aux','lead_aux'],'features':COLS,'panel_rows':len(tab),
          'equity_selection':'Fixed liquid named series from frozen inventory. Current instrument availability and survivorship do not establish historical index membership.'})
    _,_,state=cached();monthly=matrix('labels-21.csv');pos=pd.Series(np.arange(len(price)),index=price.index)
    rows=[];logs=[];laws=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv');mask=own[['scale',f'y{h}']].notna().all(axis=1)
        for (c,f),q in cohort_queries(h).groupby(['split','fold'],sort=False):
            anchor=q.origin.min()
            for name,(mode,parent) in CONFIG.items():
                log={'model':name,'horizon':h,'cohort':c,'fold':f,'cutoff':anchor}
                try:
                    tr,ii,vv,ic,pool=common_indices(monthly,anchor,{},state,mask)
                    assert (monthly.loc[tr,'endpoint']<anchor).all() and (monthly.loc[ii,'endpoint']<ic).all()
                    m=trained(tab,tr,h,mode,SEED);m0=trained(tab,ii,h,mode,SEED+1)
                    err=own.loc[vv,f'y{h}'].to_numpy()-forecast(m0,own.loc[vv])
                    past=y.loc[pool[-252:],'return'].to_numpy();cuts=np.quantile(past,[.1,.3,.5,.7,.9])
                    mu=forecast(m,own.loc[q.origin]);scales=own.loc[q.origin,'scale'].to_numpy()*np.sqrt(h)
                    rel=f'models/transfer-{h}-{c}-{f}-{name}.joblib'
                    joblib.dump({'model':m,'inner_model':m0,'training':list(tr),'inner':list(ii),'validation':list(vv),'query':list(q.origin),'residuals':err},OUT/rel,compress=3)
                    for r,point,scale in zip(q.itertuples(),mu,scales):
                        atoms=np.expm1(np.clip((point+err)*scale,-8,3))
                        law=Distribution(np.r_[atoms,past],np.r_[np.full(len(atoms),.65/len(atoms)),np.full(len(past),.35/len(past))])
                        rows.append({**score_law(h,f,name,r,law,float(price.close.loc[r.origin]),c),**buckets(law,r.realized_return,cuts)})
                        if name in ['X_ONLY','X_ADAPT','X_MULTI']:laws.append({'model':name,'horizon':h,'cohort':c,'origin':r.origin,'endpoint':r.endpoint,'atoms':law.a.tolist(),'weights':law.w.tolist()})
                    log.update(status='ok',query_count=len(q),training=len(tr),inner_fit=len(ii),valid=len(vv),inner_cutoff=ic,artifact=rel,
                               sha256=sha(OUT/rel),latest_endpoint=monthly.loc[tr,'endpoint'].max(),inner_latest_endpoint=monthly.loc[ii,'endpoint'].max(),
                               training_metrics={**diagnostics(pos.loc[tr].to_numpy(),h,np.ones(len(tr))),
                                  'panel_rows':m['panel_rows'],'panel_origin_count':m['panel_origin_count'],'parameters':int(m['fit'].coef_.size)})
                except (ValueError,KeyError) as exc:log.update(status='unestimated',reason=str(exc))
                logs.append(log)
        print('transfer',h,len(rows),'predictions',sum(a['status']!='ok' for a in logs),'unestimated',flush=True)
    save('transfer-ledger.json',logs);write('transfer-predictions.csv',pd.DataFrame(rows))
    (OUT/'transfer-laws.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in laws),encoding='utf-8')


if __name__=='__main__':run()
