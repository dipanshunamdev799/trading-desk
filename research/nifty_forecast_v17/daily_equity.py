"""Point-in-time exchange-wide daily participation and liquid-share controls."""
from .common import *


def stats(r,w):
    y=np.asarray(r,float)
    v=np.asarray(w,float)
    good=np.isfinite(y)&np.isfinite(v)&(v>0)
    y=y[good]; v=v[good]
    if not len(y):
        return dict(n=0,advance=np.nan,median=np.nan,equal=np.nan,dispersion=np.nan,turnover=np.nan,concentration=np.nan)
    z=v/v.sum()
    return dict(n=len(y),advance=float((y>0).mean()),median=float(np.median(y)),equal=float(y.mean()),dispersion=float(y.std()),
                turnover=float(v.sum()),concentration=float(z@z))


def run():
    file=OUT/'official-equity-daily.csv.gz'
    w=pd.read_csv(file,usecols=['day','stock','isin','open','close','previous_close','turnover','volume'],low_memory=False)
    p=w[w.day.isin(SEEDS)]
    tr=p.groupby('stock',as_index=False).agg(five_seed_count=('day','nunique'),mean_turnover=('turnover','mean'))
    tr=tr[tr.five_seed_count.ge(4)].sort_values(['mean_turnover','stock'],ascending=[False,True]).head(300)
    tr['seed_anchor']=SEEDS[-1]
    write('stock-daily-top300-policy.csv',tr)
    names=set(tr.stock)
    claims=set(pd.read_csv(OUT/'historical-stock-basket.csv').stock)
    w=w[w.close.gt(0)&w.open.gt(0)&w.previous_close.gt(0)&w.turnover.gt(0)].copy()
    w['actual_close_return']=np.log(w.close/w.previous_close)
    w['regular']=np.log(w.close/w.open)
    # Exchange reference close may be explicitly reset for corporate actions.
    # The EOD measurement excludes numerical outliers outside +/-24% without backfilling their returns.
    w.loc[w.actual_close_return.abs().gt(.24),'actual_close_return']=np.nan
    rows=[]
    for d,c in w.groupby('day',sort=True):
        row=dict(day=d)
        for mark,v in [('allEQ',c),('seed300',c[c.stock.isin(names)]),('basket',c[c.stock.isin(claims)])]:
            z=stats(v.actual_close_return,v.turnover)
            row.update({f'{mark}_{k}':v for k,v in z.items()})
            row[f'{mark}_intraday_advance']=float((v.regular>0).mean())
        rows.append(row)
    x=pd.DataFrame(rows).sort_values('day')
    for mark in ['allEQ','seed300','basket']:
        x[mark+'_activity_relative']=np.log(x[mark+'_turnover']/x[mark+'_turnover'].shift().rolling(20,min_periods=12).median())
    write('official-stock-breadth.csv',x)
    save('daily-stock-policy.json',dict(rule='All dated liquid EQ securities present on their actual reporting date; alternate fixed top 300 turnover cohort from the January seed. Requirements and threshold use no later target returns.',
          daily_rows=len(x),frozen_policy_date=SEEDS[-1],count_seed_cohort=len(tr),market_report=sha(file)))
    print('Built official all-EQ and fixed top-300 breadth over',len(x),'dates',flush=True)
if __name__=='__main__':
    run()
