"""Chronological transfer tests across firms, sectors and matched non-event controls."""
from .common import *
from research.nifty_forecast_v16.model import fit
from .events import interval_stats,FOCUS

PRICE=('prior_vol','prior_momentum','prior_beta','prior_liquidity','reaction_regular','reaction_gap','reaction_close','peer_reaction')
BUSINESS=('primary_text_sign','published_fundamental_surprise','earnings_growth','disagreement','explicit_uncertainty','n_release_cluster')

def make_arms(d):
    q=d.copy()
    price=q.reindex(columns=PRICE).to_numpy(float)
    typ=pd.get_dummies(q.family).reindex(columns=sorted(FOCUS),fill_value=0).astype(float)
    bus=q.reindex(columns=BUSINESS).to_numpy(float)
    rich=np.column_stack((price,bus,typ.to_numpy()))
    a=np.column_stack((price,np.nan_to_num(price)**2,np.sign(price)))
    res=np.random.default_rng(SEED+len(d))
    fake=typ.copy()
    months=q.day.str[:7]
    for month,ii in q.groupby(months).groups.items():
        ids=np.array(ii)
        past=np.flatnonzero(months.lt(month).to_numpy())[-300:]
        fake.iloc[ids]=(typ.iloc[res.choice(past,len(ids))].to_numpy() if len(past) else np.zeros((len(ids),len(typ.columns))))
    shuffle=np.column_stack((price,bus,fake.to_numpy()))
    old=q.groupby('symbol')[list(BUSINESS)].shift(1)
    oldtype=pd.concat([q.symbol,typ],axis=1).groupby('symbol').shift(1)
    delayed=np.column_stack((price,old.to_numpy(float),oldtype.to_numpy(float)))
    return price,rich,a,shuffle,delayed,tuple(ty for ty in typ.columns)

def train_price(x,y,current,penalty=145):
    m=fit(x,y,penalty)
    return m,m.values(current)

def main():
    x=csv('stock-event-pairs.csv.gz')
    ys=[];models=[]
    for h in (1,5,21):
        for stage in ('first_open','after_reaction'):
            d=x[x.horizon.eq(h)&x.stage.eq(stage)&x.beta_residual.notna()&x.matched_abnormal.notna()].sort_values(['day','symbol']).reset_index(drop=True)
            if d.empty:continue
            price,rich,equiv,shuffle,delayed,categories=make_arms(d)
            y=d.beta_residual.to_numpy(float)
            control=d.matched_non_event_return.to_numpy(float)-d.prior_beta.fillna(1).to_numpy()*d.nifty_return.to_numpy()
            dd=d.day.to_numpy()
            uu=d.target_end.to_numpy()
            sector=d.sector.to_numpy()
            firm=d.symbol.to_numpy()
            for day,ids0 in d.groupby('day',sort=True).groups.items():
                ids=np.asarray(ids0)
                tr=np.flatnonzero((uu<day)&(dd<day))[-1800:]
                if len(tr)<170 or len(set(dd[tr]))<35:continue
                price0,pc=train_price(price[tr],y[tr],price[ids])
                ev,mv=train_price(rich[tr],y[tr],rich[ids],170)
                _,reserve=train_price(equiv[tr],y[tr],equiv[ids],170)
                _,rand=train_price(shuffle[tr],y[tr],shuffle[ids],170)
                _,lag=train_price(delayed[tr],y[tr],delayed[ids],170)
                _,nn=train_price(price[tr],control[tr],price[ids],170)
                pred={'price_only':pc,'price_equivalent_complexity':reserve,'ordinary_pooled':mv,
                      'randomized_category':rand,'prior_issuer_event':lag,'matched_non_event_model':nn}
                strict=np.zeros(len(ids));partial=mv.copy();hierarchy=mv.copy()
                residual=y[tr]-ev.values(rich[tr])
                for k in np.unique(sector[ids]):
                    f=sector[tr]==k
                    here=np.flatnonzero(sector[ids]==k)
                    if f.sum()>=70:
                        _,s0=train_price(rich[tr][f],y[tr][f],rich[ids][here],185)
                        partial[here]=.55*s0+.45*mv[here]
                    hierarchy[here]+=np.clip(residual[f].sum()/(75+f.sum()),-.012,.012)
                for j,i in enumerate(ids):
                    mask=firm[tr]==firm[i]
                    # Firm-specific effect uses only the firm's earlier matured event episodes.
                    strict[j]=pc[j]+(y[tr][mask]-price0.values(price[tr][mask])).sum()/(35+mask.sum())
                    hierarchy[j]+=np.clip(residual[mask].sum()/(70+mask.sum()),-.012,.012)
                pred.update(company_only_adjustment=strict,sector_specific=partial,sector_issuer_partial_pool=hierarchy)
                models.append(dict(day=day,stage=stage,horizon=h,last_mature=max(uu[tr]),n=len(tr),
                                   **ev.receipt(PRICE+BUSINESS+categories)))
                for tag,values in pred.items():
                    for i,p in zip(ids,values):
                        a=float(y[i]);b=float(np.clip(p,-.10,.10))
                        ys.append(dict(day=day,stage=stage,horizon=h,model=tag,symbol=firm[i],sector=sector[i],
                         episode=d.episode.iloc[i],family=d.family.iloc[i],target_end=uu[i],last_mature=max(uu[tr]),pred=b,actual=a,
                         mae=abs(a-b),se=(a-b)**2,accuracy=int((a>0)==(b>0))))
            print('Transfer',h,stage,'complete',flush=True)
    z=pd.DataFrame(ys)
    assert z.last_mature.lt(z.day).all()
    write('stock-transfer-predictions.csv.gz',z)
    save('stock-transfer-fit-receipts.json',models)
    all_stats=[]
    for (h,k),g in z.groupby(['horizon','stage']):
        ref=g[g.model.eq('price_only')].set_index(['day','symbol','episode'])
        for m,f in g.groupby('model'):
            tmp=f.set_index(['day','symbol','episode']).join(ref[['mae','se']].rename(columns={'mae':'parent_mae','se':'parent_se'})).reset_index()
            tmp['paired_gain']=tmp.parent_mae-tmp.mae
            d=interval_stats(tmp,'paired_gain')
            all_stats.append(dict(horizon=h,stage=k,model=m,mae=tmp.mae.mean(),rmse=np.sqrt(tmp.se.mean()),accuracy=tmp.accuracy.mean(),
                                  rank_correlation=tmp[['pred','actual']].rank().corr().iloc[0,1],**d))
    write('event-transfer-comparison.csv',pd.DataFrame(all_stats))
    print('Event transfer predictions',len(z),flush=True)

if __name__=='__main__':
    main()
