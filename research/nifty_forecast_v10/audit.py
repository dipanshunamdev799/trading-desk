"""Exact legacy invariance, immutable-input hashing and frozen forecast rescoring."""
from .common import *
from research.nifty_forecast_v3.features import labels_for
from research.nifty_forecast_v6.common import V4


def protected():
    old=read('preservation.json')['files'];bad=[]
    for rel,expected in old.items():
        p=ROOT/rel
        if not p.is_file() or sha(p)!=expected:bad.append(rel)
    save('protected-hash-check.json',{'checked_at':now(),'files_checked':len(old),'changed_or_missing':bad,'pass':not bad})
    assert not bad,bad[:10]
    print('Protected files checked',len(old),flush=True)


def exact_copies():
    from research.nifty_forecast_v8 import invariance
    invariance.save=lambda n,d:save('duplicate-replay/'+n,d)
    invariance.write=lambda n,d:write('duplicate-replay/'+n,d)
    invariance.run()
    invariance.run(sector_alias=True)
    for batch in ['invariance','sector-alias']:
        a=pd.read_csv(V8/f'{batch}-effects.csv');b=pd.read_csv(OUT/f'duplicate-replay/{batch}-effects.csv')
        pd.testing.assert_frame_equal(a,b,atol=1e-12,rtol=1e-12)


def refresh():
    folder=OUT/'refresh';receipt=read('acquisition.json',folder)
    raw=pd.read_csv(folder/'acquired-candles.csv')
    recent=raw[(raw.instrument=='nifty_spot')&(raw.day>'2026-11-17')].set_index('day').sort_index()
    official={r['origin']:r for r in receipt['official_crosscheck'] if r['status']=='verified'}
    assert set(recent.index)==set(official)
    frozen=matrix('price.csv');retro=pd.read_csv(V9/'extended-predictions.csv');override=[]
    for d,r in official.items():
        if abs(r['delta'])>.01:
            override.append({'date':d,'upstox':float(recent.loc[d,'close']),'official':r['official_close']})
            recent.loc[d,'close']=r['official_close']
    price=pd.concat([frozen,recent.reindex(columns=frozen.columns)]).sort_index()
    comparison=[];counts={}
    for h in [5,21]:
        fresh=labels_for(price,h);old=matrix(f'labels-{h}.csv');past=old.endpoint.notna()
        np.testing.assert_allclose(fresh.loc[old.index[past],'return'],old.loc[past,'return'],atol=1e-12)
        archived=retro[retro.horizon.eq(h)].copy()
        actual=fresh.loc[archived.origin]
        np.testing.assert_array_equal(actual.endpoint,archived.endpoint)
        np.testing.assert_allclose(actual['return'],archived.realized_return,atol=1e-12)
        y=(actual['return'].to_numpy()>0).astype(int)
        np.testing.assert_allclose((archived.p-y)**2,archived.brier,atol=1e-12)
        archived['refreshed_close']=price.loc[archived.endpoint,'close'].to_numpy()
        archived['verified_return']=actual['return'].to_numpy()
        archived['issued_live']=False
        comparison.append(archived)
        counts[h]={'matured_frozen_origins':archived.origin.nunique(),'checked_archived_rows':len(archived),'dates':sorted(archived.endpoint.unique())}
    ledger=V4/'prospective-ledger.jsonl';issued=[]
    for event in map(json.loads,ledger.read_text(encoding='utf-8').splitlines()):
        if event['kind']!='FORECAST':continue
        p=event['payload']
        for h,f in p['forecasts'].items():
            d=f['expected_endpoint']
            issued.append({'origin':f['reference'],'horizon':int(h),'expected_endpoint':d,'mature_as_of_refresh':d in price.index,
               'cohort':p['cohort'],'forecast_id':event['hash'],'ledger_sha256':sha(ledger)})
    assert all(not s['mature_as_of_refresh'] for s in issued)
    old_sessions=read('extended-coverage.json',V9)['new_2026_sessions']
    save('refresh/refresh-audit.json',{'observed_through':price.index[-1],'post_frozen_dates':list(recent.index),'official_overrides':override,
          'additional_since_v9':sorted(set(recent.index)-set(old_sessions)),'historical_reconstruction':counts,'known_previous_issued_forecasts':issued,
          'realized_endpoint_scoring':'Revalidated actual endpoints, returns and Brier of each immutable V9 historical reconstruction. The prior future issue remains pending.'})
    write('refresh/frozen-forecast-rescore.csv',pd.concat(comparison,ignore_index=True))


def covariance():
    from .experiments import cfg,run
    config={}
    for n in [85,126,None]:
        for rule in ['plain','gls_empirical']:
            code=n or 'MAX';config[f'EC_{code}_{rule.upper()}']=cfg(parent=f'EC_{code}_PLAIN' if rule!='plain' else f'O{code}_PLAIN',
                  budget=n,overlap=rule,hypothesis='Training-only residual lag covariance shrunk toward analytical overlap and independent noise')
    run('covariance',config)


if __name__=='__main__':
    import sys
    {'protected':protected,'copies':exact_copies,'refresh':refresh,'covariance':covariance}[sys.argv[1]]()
