"""Audit cross-version matching and separate early versus later path skill."""
from .common import *
from .model import quantify
from .evidence import pairs, bands


def run():
    v=pd.read_csv(OUT/'v15-replayed-gap-forecasts.csv.gz',low_memory=False)
    old=v[v.cutoff.eq('09:10')&v.delay.eq(60)&v.target_name.eq('immediate_open')].copy()
    rows=[]
    with np.load(OUT/'v15-replayed-gap-laws.npz',allow_pickle=False) as z:
        kk=z['keys']
        pp=z['atoms']
        for r in old.itertuples(index=False):
            idx=np.flatnonzero((kk[:,0]==r.day)&(kk[:,1]==r.target_name)&(kk[:,2]==r.model))[0]
            q=quantify(pp[idx,:int(kk[idx,3])],r.actual,True)
            q.update(brier=r.brier,log_loss=r.log_loss,p_up=r.p)
            rows.append(dict(day=r.day,cohort=r.cohort,model='V15_'+r.model,**q))
    old=pd.DataFrame(rows)
    all_v=[]
    for clk in ('0830','0845','0855','0910'):
        now=pd.read_csv(OUT/f'opening-{clk}-scores.csv.gz',low_memory=False)
        now=now[now.model.isin(['gift_raw','gift_calibrated','asia_partial','single_US','equal_six','six_cash','domestic'])]
        a=pd.concat([now[list(old.columns)],old],ignore_index=True)
        a['cutoff']=clk[:2]+':'+clk[2:]
        all_v.append(a)
    q=pd.concat(all_v,ignore_index=True)
    write('v15-v16-gap-common-units.csv.gz',q)
    def side(group,z):
        return [(m,k) for m in z.model.unique() if not m.startswith('V15_') for k in ['V15_offshore_fresh','V15_offshore_prior_only']]
    out=pairs(q,['cutoff'],['brier','crps','mae','log_loss'],side)
    write('v15-v16-opening-matched.csv',out)
    t=pd.read_csv(OUT/'path-passage-scores.csv.gz')
    cols=['touch_brier','integrated_brier','conditional_brier','brier_by_1','brier_by_3','brier_by_5','brier_by_10','brier_by_21']
    order=[]
    for (h,m),a in t.groupby(['horizon','model']):
        o=dict(horizon=h,model=m,risk_set_rows=len(a),still_unhit_at_day1=int(a.conditional_brier.notna().sum()))
        for col in cols:
            o[col]=a[col].mean()
        order.append(o)
    write('passage-by-session.csv',pd.DataFrame(order))
    w=t.groupby(['horizon','origin','cohort','model'],as_index=False)[cols].mean()
    def match(group,x):
        control='V14_trend_shrink' if group['horizon']==5 else 'V14_trend_persistent'
        return [(m,r) for m in ('decomposed_gift','session_state','fixed_mixture') for r in (control,'V15_iv_restart','decomposed')]
    ordinary=[c for c in cols if c!='conditional_brier']
    dd=pairs(w,['horizon'],ordinary,match,'origin')
    # Zero predicted survivor mass is undefined in a conditioned law. Align barrier and side before averaging.
    exact=[]; support=[]
    for h,z in t.groupby('horizon'):
        order=sorted(z.origin.unique())
        gains=[]; rows=[]
        for current,base in match({'horizon':h},z):
            keys=['origin','barrier','side']
            a=z[z.model.eq(current)].set_index(keys)
            b=z[z.model.eq(base)].set_index(keys)
            a,b=a.align(b,axis=0,join='inner')
            survived=a.actual_first.gt(1)
            select=survived & a.conditional_brier.notna() & b.conditional_brier.notna()
            support.append(dict(horizon=h,candidate=current,control=base,actual_survivors=int(survived.sum()),
                                matching_sides=int(select.sum()),unsupported_candidate=int((survived & a.conditional_brier.isna()).sum()),
                                unsupported_parent=int((survived & b.conditional_brier.isna()).sum())))
            a,b=a[select],b[select]
            e=(b.conditional_brier-a.conditional_brier).groupby(level=0).mean()
            gains.append(e.reindex(order).to_numpy())
            cohort=a.cohort.groupby(level=0).first()
            rows.append(dict(horizon=h,candidate=current,control=base,metric='conditional_brier',n=len(e),
                candidate_loss=a.conditional_brier.groupby(level=0).mean().mean(),
                control_loss=b.conditional_brier.groupby(level=0).mean().mean(),gain=e.mean(),
                early_gain=e[cohort.eq('early')].mean(),later_gain=e[cohort.eq('later')].mean()))
        qs=bands(np.column_stack(gains),['conditional_brier']*len(rows))
        for i,row in enumerate(rows):
            row.update({c:v[i] for c,v in qs.items()})
        exact.extend(rows)
    write('passage-age-matched.csv',pd.concat([dd,pd.DataFrame(exact)],ignore_index=True))
    write('passage-conditional-support.csv',pd.DataFrame(support))
    s=pd.read_csv(OUT/'path-scores.csv.gz')
    g=s[s.gift_eligible.eq(1)]
    gg=pairs(g,['horizon'],['brier','endpoint_crps','range_crps','touch_brier','integrated_brier'],
        lambda key,z:[(m,ref) for m in ['decomposed_gift','session_state','fixed_mixture'] for ref in ['decomposed','V15_iv_restart']],'origin')
    write('path-gift-common-support.csv',gg)
    print('Paired old and new gap laws in identical arithmetic return units',flush=True)

if __name__=='__main__':
    run()
