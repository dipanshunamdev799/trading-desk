"""Authenticate matched Nasdaq ETF histories and conservative IST availability."""
from urllib.parse import quote
import requests
from .common import *

TICKERS=['RSP','SPY','XLF','XLK']


def run():
    path=OUT/'sources/nasdaq';path.mkdir(parents=True,exist_ok=True)
    cols={};evidence=[]
    for ticker in TICKERS:
        name=f'{ticker}.json';url=f'https://api.nasdaq.com/api/quote/{quote(ticker)}/historical'
        if not (path/name).exists():
            r=requests.get(url,params={'assetclass':'etf','fromdate':'2025-01-01','todate':'2026-11-17','limit':600},
                           headers={'User-Agent':'Mozilla/5.0','Accept':'application/json','Referer':'https://www.nasdaq.com/'},timeout=10)
            r.raise_for_status();save(f'sources/nasdaq/{name}',r.json())
        a=read(name,path)['data'];f=pd.DataFrame(a['tradesTable']['rows'])
        d=pd.to_datetime(f.date,format='%m/%d/%Y')
        for c in ['open','close','high','low']:f[c]=pd.to_numeric(f[c].str.replace('$','',regex=False).str.replace(',','',regex=False))
        check=f.close.gt(0)&f.high.ge(f[['open','close','low']].max(axis=1))&f.low.le(f[['open','close','high']].min(axis=1))
        assert not d.duplicated().any() and d.dt.year.isin([2025,2026]).all() and d.max()<=pd.Timestamp('2026-11-17')
        cols[ticker]=pd.Series(f.close[check].to_numpy(),index=d[check]).sort_index()
        evidence.append({'ticker':ticker,'valid':int(check.sum()),'rejected':int((~check).sum()),'first':str(d.min().date()),'last':str(d.max().date()),
                         'sha256':sha(path/name),'source':f'https://www.nasdaq.com/market-activity/etf/{ticker.lower()}/historical'})
    d=pd.DataFrame(cols).dropna()
    p=np.log(d);ret=p.diff()
    q=pd.DataFrame({'us_breadth5':p.RSP.diff(5)-p.SPY.diff(5),'us_breadth21':p.RSP.diff(21)-p.SPY.diff(21),
                    'us_sector5':p.XLF.diff(5)-p.XLK.diff(5),'us_cap5':p.SPY.diff(5),'us_cap21':p.SPY.diff(21),
                    'us_risk':ret.SPY.rolling(21).std()})
    q['source_us_session']=q.index.strftime('%Y-%m-%d')
    ref=matrix('matrices/BREADTH.csv',OUT);cut=pd.DataFrame({'origin':pd.to_datetime(ref.index)})
    aligned=pd.merge_asof(cut,q.reset_index(names='us_observation'),left_on='origin',right_on='us_observation',allow_exact_matches=False)
    assert (aligned.us_observation<aligned.origin).all()
    aligned['origin']=aligned.origin.dt.strftime('%Y-%m-%d');aligned=aligned.set_index('origin')
    write('international-availability.csv',aligned[['source_us_session']],index=True)
    aligned=aligned.drop(columns=['source_us_session','us_observation'])
    aligned['us_india_breadth_gap']=ref.b5_500-aligned.us_breadth5
    d={'US_CAP':['us_cap5','us_cap21','us_risk','us_sector5'],'US_EQ':['us_breadth5','us_breadth21'],'US_DIVERGE':['us_india_breadth_gap']}
    defs=read('feature-definitions.json')
    for n,columns in d.items():
        m=aligned[columns]
        write(f'matrices/{n}.csv',m,index=True)
        defs[n]={'columns':columns,'hash':sha(OUT/f'matrices/{n}.csv'),'complete_rows':int(m.notna().all(axis=1).sum())}
    save('feature-definitions.json',defs)
    save('global-breadth-audit.json',{'series':evidence,'common_US_sessions':len(q),'matched_Indian_origins':len(aligned),
         'availability':'For each Indian 15:30 close, select the most recent US date strictly earlier than the Indian origin date.',
         'methodology':'RSP/SPY are traded equal-weight/cap-weight fund proxies. XLF/XLK are financial/technology funds. Use exchange closes, not a total-return reconstruction.',
         'source_limit':'Historical data downloaded now. Previous-session restriction is conservative for US equity closes. Raw dividend and split adjustments are not independently reconstructed.'})
    from .engine import run as estimate
    estimate('international')


if __name__=='__main__':run()
