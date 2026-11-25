"""New market sessions score only targets that have subsequently matured."""
from .common import *
from .run_models import run as evaluate, spec
from research.nifty_forecast_v3.features import labels_for


def run():
    raw=pd.read_csv(OUT/'acquired-candles.csv');new=raw[(raw.instrument=='nifty_spot')&(raw.day>'2026-11-17')].set_index('day').sort_index()
    officially={r['origin']:r for r in read('acquisition.json')['official_crosscheck'] if r['status']=='verified'}
    corrections=[]
    for d,meta in officially.items():
        if abs(meta['delta'])>.01:
            corrections.append({'date':d,'upstox':new.loc[d,'close'],'official':meta['official_close']})
            new.loc[d,'close']=meta['official_close']
    frozen=matrix('price.csv');price=pd.concat([frozen,new.reindex(columns=frozen.columns)]).sort_index()
    prepared={};counts={}
    for h in [5,21]:
        y=labels_for(price,h);old=matrix(f'labels-{h}.csv')
        subset=old.endpoint.notna();np.testing.assert_allclose(y.loc[old.index[subset],'return'],old.loc[subset,'return'],atol=1e-12)
        np.testing.assert_array_equal(y.loc[old.index[subset],'endpoint'],old.loc[subset,'endpoint'])
        relevant=y.loc[old.index[~subset]].dropna(subset=['return','endpoint'])
        q=pd.DataFrame({'origin':relevant.index,'endpoint':relevant.endpoint.to_numpy(),'realized_return':relevant['return'].to_numpy(),
                        'fold':relevant.index.str[:7],'split':'refresh','regime':'UNCLASSIFIED','trend':'UNCLASSIFIED','global_risk':'UNCLASSIFIED'})
        prepared[h]=(y,q,price.close);counts[h]={'new_resolved_prior_origins':len(q),'origin_dates':list(q.origin),'endpoints':list(q.endpoint)}
        write(f'extended-labels-{h}.csv',y,index=True)
    write('extended-price.csv',price,index=True)
    save('extended-coverage.json',{'counts':counts,'new_2026_sessions':list(new.index),'official_overrides':corrections,
         'meaning':'Historical origins from frozen features whose endpoints became resolved using the separate refreshed vintage. No post-Nov17 feature-origin target mature after only four sessions.'})
    cfg={'E9_HIST':spec('small','P_HIST',law='history'),'E9_ROT':spec('residual','E9_HIST'),'E9_STRUCT':spec('structure_change','E9_HIST'),'E9_COMPACT':spec('small_resid','E9_HIST')}
    evaluate('extended',cfg,custom=prepared)


if __name__=='__main__':run()
