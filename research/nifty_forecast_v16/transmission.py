"""Use the archived US sector ETFs as a dated cross-market transmission follow-up."""
from .common import *
from .data import DOM
from .model import fit, history
from .session_models import Engine, Spec, load, prepare

ETF_GROUPS={
 'it_gap':('XLK_market_spread','XLK','tech','fx'),
 'bank_gap':('XLF_market_spread','XLF','dgs10_change','vix_move'),
 'financial_gap':('XLF_market_spread','XLF','dgs10_change','vix_move'),
 'broad_gap':('RSP_market_spread','RSP','asia_mean','nikkei_partial','hsi_partial'),
 'energy_gap':('brent','wti','brent_intraday','XLF_market_spread'),
 'it_relative':('XLK_market_spread','XLK','fx'),
 'bank_relative':('XLF_market_spread','XLF','dgs10_change'),
 'session_risk':('risk_ETF','RSP_market_spread','vix_move','foreign_sd')
}


def primary():
    rows=[];validation=[]
    for symbol in ('RSP','SPY','XLF','XLK'):
        p=V11/'sources/nasdaq'/f'{symbol}.json'
        q=pd.DataFrame(read(p.name,p.parent)['data']['tradesTable']['rows'])
        d=pd.to_datetime(q.date,format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
        r=pd.to_numeric(q.close.str.replace('$','',regex=False).str.replace(',','',regex=False))
        assert d.between(FIRST,FREEZE).all() and not d.duplicated().any()
        rows.append(pd.Series(r.to_numpy(),name=symbol,index=d).sort_index())
        validation.append(dict(symbol=symbol,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),dates=len(d),
                  source='https://www.nasdaq.com/market-activity/etf/'+symbol.lower()+'/historical'))
    data=pd.concat(rows,axis=1).dropna().sort_index()
    diff=np.log(data).diff()
    for key in ['RSP','XLF','XLK']:
        diff[key+'_market_spread']=diff[key]-diff.SPY
    diff['risk_ETF']=diff.SPY.rolling(21).std()
    diff['published']=[(pd.Timestamp(d+'T16:00:00',tz='America/New_York')+pd.Timedelta(minutes=60)).tz_convert(IST) for d in diff.index]
    save('us-etf-source-receipt.json',dict(entries=validation,matched_sessions=len(diff),local_close='16:00 America/New_York',
        buffer_minutes=60,feed_basis='Raw close price, with exchange-traded spread and no historic publication receipts.'))
    return diff


def run():
    a,y=load()
    x=prepare(y,a[a.cutoff.eq('08:55')].set_index('day').reindex(y.index))
    et=primary()
    clock=pd.DatetimeIndex([stamp(d,'08:55') for d in x.index])
    ix=pd.DatetimeIndex(et.published).searchsorted(clock,side='right')-1
    avail=ix>=0
    chosen=et.iloc[ix.clip(0)].copy()
    date=chosen.index.to_numpy()
    chosen.index=x.index
    assert (chosen.published.iloc[np.flatnonzero(avail)]<=clock[avail]).all()
    ts=pd.DataFrame(dict(day=x.index,decision=clock.map(lambda z:z.isoformat()),
       US_local_session=np.where(avail,date,''),eligible=chosen.published.where(avail)))
    write('us-etf-information-clock.csv',ts)
    for c in et.columns.drop('published'):
        x[c]=chosen[c].where(avail)
        x['older_'+c]=x[c].shift(2)
    x['us_inr_proxy']=x.SPY+x.fx
    x['tech_vs_financial']=x.XLK-x.XLF
    x['indian_US_breadth_disagreement']=x.breadth5-x.RSP_market_spread
    e=Engine(x,y)
    made=[]
    days=y.index.to_numpy()
    for target,cols in ETF_GROUPS.items():
        for k in cols:
            if 'older_'+k not in x:
                x['older_'+k]=x[k].shift(2)
        specs=[Spec('domestic',DOM,control='historical',group='baseline'),Spec('historical',style='historical',control='domestic',group='baseline'),
               Spec('direct_foreign_ETF',DOM+cols,control='domestic',group='ETF_transmission'),
               Spec('ETF_only',cols,control='domestic',group='ETF_transmission'),
               Spec('delayed_foreign_ETF',DOM+tuple('older_'+k for k in cols),control='direct_foreign_ETF',group='ETF_transmission')]
        e.run('etf_transmission',target,specs)
        if target in ('bank_gap','it_gap','broad_gap','energy_gap'):
            yt=y[target].to_numpy(float)
            cols=tuple(cols)
            d=x.loc[:,list(cols)].to_numpy(float)
            maturity=y['label_'+target].fillna('9999-12-31').to_numpy()
            r=np.full(len(d),np.nan)
            for i in range(len(r)):
                past=history(days,maturity,yt,i)
                if len(past)>=54:r[i]=.75*fit(d[past],yt[past],85).values(d[i])
            x['ETF_intermediate_'+target]=r
            made.append('ETF_intermediate_'+target)
    e2=Engine(x,y)
    for target in ('gap','regular','one','five','twentyone'):
        m=[Spec('domestic',DOM,control='historical',group='baseline'),Spec('historical',style='historical',control='domestic',group='baseline'),
           Spec('additive_ETFs',DOM+('SPY','XLK_market_spread','XLF_market_spread','RSP_market_spread','us_inr_proxy'),control='domestic',group='ETF_direct'),
           Spec('foreign_sector_stack',DOM+tuple(made),control='additive_ETFs',group='ETF_stack'),
           Spec('ETF_disagreement',DOM+('SPY','tech_vs_financial','indian_US_breadth_disagreement','us_inr_proxy','us_asia','foreign_sd'),
                control='additive_ETFs',group='disagreement')]
        e2.run('ETF_NIFTY_link',target,m,y['cohort_'+target].to_numpy() if target in ('five','twentyone') else None)
    e.save('network-sectors')
    e2.save('network-nifty')

if __name__=='__main__':
    run()
