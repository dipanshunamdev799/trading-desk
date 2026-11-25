"""Positioning-conditioned volatility distributions and joint OHLC path stress tests."""
from .common import *
from .features import FUTURES,POSITION,CROWD,DELIVERY,DEALS,INNOV
from .forecast import matrix,book_panel,matured
from research.nifty_forecast_v18.risk import scalar_score
from research.nifty_forecast_v16 import paths as predecessor
from research.nifty_forecast_v17.paths import outcome
from research.nifty_forecast_v15.sequential import TICK,log_ticks,numpy_zip
from research.nifty_forecast_v16.model import fit

PRICE=('iv_prev','iv_skew','iv_term','vix_level','trailing_vol','rolling_rv5','prior_ret5','cash_breadth_change',*FUTURES)
ARMS={
    'price_and_oi':PRICE,
    'crowding_on_price':PRICE+CROWD,
    'delivery_on_price':PRICE+DELIVERY[:9],
    'deals_on_price':PRICE+DEALS[:6],
    'innovation_on_price':PRICE+INNOV,
    'combined_positioning_risk':PRICE+CROWD+POSITION[:8]+DELIVERY[:9]+DEALS[:4],
    'combined_delay1':PRICE+tuple(k+'_delay1' for k in CROWD+POSITION[:8]+DELIVERY[:9]+DEALS[:4]),
    'combined_delay5':PRICE+tuple(k+'_delay5' for k in CROWD+POSITION[:8]+DELIVERY[:9]+DEALS[:4]),
}
PROTECTED={
    'protected_GJR','protected_student_EGARCH','protected_raw_iv','protected_offshore_plus_domestic',
    'protected_fixed_iv_rv','protected_V14_IV_GJR','raw_atm_point_same_clock','price_volatility','price_volatility_transition',
    'fundamental_risk','scheduled_then_fundamental','non_price_risk','protected_postopen_cash_risk',
    'protected_postopen_after_open_iv','protected_postopen_after_open_RV','protected_postopen_after_open_GJR',
}
Q=(np.arange(128)+.5)/128

def bound(p):
    return float(np.clip(p,.0005,.9995))

def scaled_fit(x,err,t,i):
    u=t[np.isfinite(err[t])]
    if len(u)<44 or not np.isfinite(x[i]).any():
        return 1.,None,u
    m=fit(x[u],err[u],185)
    return float(np.exp(np.clip(.55*m.values(x[i]),-.23,.23))),m,u

def path_score(info,tag,parent,a,real,fields,barriers):
    values=np.exp(a.astype(float)*TICK)
    book=[]
    z=predecessor.output_scores(values,real,info['horizon'],{},book)
    for row in book:
        barriers.append(info|dict(model=tag,parent=parent)|row)
    fields.append(info|dict(model=tag,parent=parent)|z)

def risk():
    panel=csv('asof-positioning-features.csv.gz')
    archive=read('retimed-path-archive.json',V17)
    paths={(r['horizon'],r['origin']):r for r in archive['files']}
    oldpaths=predecessor.Paths()
    old=csv('event-volatility-predictions.csv.gz',V18).set_index(['horizon','cutoff','day','model'])
    stored=np.load(V18/'event-volatility-laws.npz',allow_pickle=False)['atoms']
    previous=csv('retimed-path-scores.csv.gz',V17)
    parent_barriers=csv('retimed-passage-scores.csv.gz',V17)
    risk_cases=[];risk_atoms=[];risk_fits=[];out_paths=[];barriers=[];files=[]
    for clock in CLOCKS:
        for h in HORIZONS:
            f,y=book_panel(clock,h,panel)
            t0=csv(f'targets-{h}.csv',V14).set_index('day').reindex(f.origin)
            t0.index=f.index
            ds=f.index.to_numpy();dec=f.decision.str[:10].to_numpy()
            origins=y.origin.to_numpy(); end=y['end_original'+str(h)].fillna('9999-12-31').to_numpy()
            cohort=y['cohort_'+str(h)]
            actual=t0.volatility.to_numpy(float)
            trailing=t0.trailing_at_origin.to_numpy(float)
            event=t0.event_expand.to_numpy(float)
            vol_base=f.iv_prev.fillna(f.trailing_vol).fillna(.13).clip(.04,.55).to_numpy(float)
            errors=np.log(np.maximum(actual,.014)/vol_base)
            x={k:matrix(f,fields) for k,fields in ARMS.items()}
            live={
                'crowding_on_price':f.index_futures_detail_hhi_z.notna(),
                'delivery_on_price':f.del_intensity.notna(),
                'deals_on_price':f.deal_n.notna(),
                'innovation_on_price':f.innovation_5.notna(),
                'combined_positioning_risk':f.index_futures_detail_hhi_z.notna()&f.del_intensity.notna()&f.deal_n.notna(),
                'combined_delay1':f.index_futures_detail_hhi_z_delay1.notna()&f.del_intensity_delay1.notna(),
                'combined_delay5':f.index_futures_detail_hhi_z_delay5.notna()&f.del_intensity_delay5.notna(),
                'price_and_oi':f.iv_prev.notna()|f.trailing_vol.notna(),
            }
            for i in np.flatnonzero(cohort.notna()):
                tr=matured(ds,end,actual,i,dec)
                a=old.loc[(h,clock,ds[i],'risk_calibrated_iv')]
                ctl=stored[int(a.law)].astype(float)
                latest=max(end[tr])
                assert abs(a.actual-actual[i])<1.e-10
                high=np.quantile(actual[tr],.80)
                contraction=.8*trailing[i]; expansion=1.25*trailing[i]
                high_entry=trailing[i]<high
                assert int(actual[i]>=expansion)==event[i] or abs(actual[i]-expansion)<1.e-10
                common=dict(day=ds[i],origin=origins[i],horizon=h,cutoff=clock,cohort=cohort.iloc[i],target_end=end[i],
                         decision=f.decision.iloc[i],source_day=f.source_day.iloc[i],source_release=f.source_release.iloc[i],
                         high_entry=int(high_entry),prior_rv=trailing[i],
                         expiry_guard=int(pd.notna(f.days_to_expiry.iloc[i]) and f.days_to_expiry.iloc[i]>3 and f.roll_event.iloc[i]==0))
                ctl_mult,_,_=scaled_fit(x['price_and_oi'],errors,tr,i)
                factors={}
                for m in ('risk_calibrated_iv',*ARMS):
                    fitrow=None
                    if m=='risk_calibrated_iv':
                        multiplier=1.; u=tr; active=True
                    else:
                        j=live[m].to_numpy(bool)
                        multiplier,fitrow,u=scaled_fit(x[m],errors,tr[j[tr]&j[i]],i)
                        active=fitrow is not None
                        if not active:multiplier=ctl_mult
                    factors[m]=multiplier
                    arr=ctl*multiplier
                    risk_atoms.append(arr.astype(np.float32))
                    prob=bound(np.mean(arr>=expansion))
                    pc=bound(np.mean(arr<=contraction))
                    ph=bound(np.mean(arr>=high))
                    truth_c=int(actual[i]<=contraction); truth_h=int(actual[i]>=high)
                    risk_cases.append(common|dict(model=m,parent='risk_calibrated_iv' if m in ('risk_calibrated_iv','price_and_oi') else 'price_and_oi',
                        active=int(active),n_train=len(u),last_mature=max(end[u]) if len(u) else latest,scale=multiplier,
                        law=len(risk_atoms)-1,expansion_threshold=expansion,contraction_threshold=contraction,high_threshold=high,
                        p_contraction=pc,p_high=ph,actual_contraction=truth_c,actual_high=truth_h,
                        contraction_brier=(pc-truth_c)**2,high_entry_brier=(ph-truth_h)**2 if high_entry else np.nan,
                        **scalar_score(arr,actual[i],prob,int(event[i]))))
                    if fitrow is not None:
                        risk_fits.append(common|dict(model=m,scale=multiplier,last_mature=max(end[u]),n_train=len(u),
                                                      **fitrow.receipt(list(dict.fromkeys(ARMS[m])))))
                q=paths[h,origins[i]]
                real=outcome(oldpaths,q)
                assert len(real)==h
                with np.load(V17/q['file'],allow_pickle=False) as z:
                    m0={n:z[clock+'_'+n].copy() for n in ('same_clock_IV','same_clock_GJR')}
                if clock=='preauction_0855':
                    with np.load(V16/q['v16_reference'],allow_pickle=False) as z:
                        m0['same_clock_GIFT_first']=z['decomposed_gift'].copy()
                path_factor=np.clip(factors['combined_positioning_risk']/ctl_mult,.85,1.18)
                modified={}
                for j,parent in [('position_on_IV','same_clock_IV'),('position_on_GJR','same_clock_GJR')]:
                    a=m0[parent]
                    modified[j]=log_ticks(a.astype(float)*TICK*path_factor)
                out=(OUT/'joint-laws'/f'{clock}-{h}-{origins[i]}.npz')
                out.parent.mkdir(parents=True,exist_ok=True)
                for tag,arr in (m0|modified).items():
                    assert arr.shape==(256,h,4)
                    assert (arr[:,:,1]>=np.maximum(arr[:,:,0],arr[:,:,3])).all()
                    assert (arr[:,:,2]<=np.minimum(arr[:,:,0],arr[:,:,3])).all()
                    b={'position_on_IV':'same_clock_IV','position_on_GJR':'same_clock_GJR'}.get(tag,tag)
                    path_score(common|dict(path_factor=path_factor if tag in modified else 1.),tag,b,arr,real,out_paths,barriers)
                numpy_zip(out,modified)
                files.append(common|dict(file=out.relative_to(OUT).as_posix(),sha256=sha(out),parent_file=q['file'],
                    parent_sha256=q['sha256'],factor=float(path_factor),atom_count=256,tick=TICK))
            print('Positioning volatility and paths',clock,h,flush=True)
    d=old.reset_index()
    r=d[d.model.isin(PROTECTED)&d.cutoff.isin(CLOCKS)].copy()
    r['active']=1
    r['law']=-1
    write('risk-cases.csv.gz',pd.concat([pd.DataFrame(risk_cases),r],ignore_index=True))
    write('joint-path-cases.csv.gz',pd.DataFrame(out_paths))
    write('barrier-cases.csv.gz',pd.DataFrame(barriers))
    np.savez_compressed(OUT/'volatility-laws.npz',annualized_volatility_atoms=np.stack(risk_atoms))
    save('joint-law-receipts.json',dict(files=files,ticks=TICK,shape='scenario x cash session x open/high/low/close log ticks',
        archived_parent_paths='Use V17 hashes at their matching original decision clock. GIFT-first 08:55 reads exact V16 decomposed_gift.'))
    with gzip.open(OUT/'risk-fits.ndjson.gz','wt',encoding='utf8') as g:
        for row in risk_fits:g.write(json.dumps(row,allow_nan=False,default=str)+'\n')
    # Confirm archived point and barrier controls agree on their common scored target.
    observed=pd.DataFrame(out_paths)
    k=['day','horizon','cutoff','model']
    z=observed[observed.model.isin(['same_clock_GJR','same_clock_IV'])].merge(previous,on=k,suffixes=('','_arch'),validate='1:1')
    terms=['endpoint_crps','range_crps','brier','touch_brier','integrated_brier']
    err=max(z[p].sub(z[p+'_arch']).abs().max() for p in terms)
    assert len(z)==2*2*sum(EXPECTED.values()) and err<1.e-9,(len(z),err)
    save('risk-replay-receipt.json',dict(cases=len(z),max_error=err,parent_barriers=len(parent_barriers),
          training_guard='Latest earlier mature labels only, trailing at original cash cut. Path transformation scales all log OHLC legs together around reference close.',
          models=ARMS,law_cases=len(risk_cases),path_files=len(files)))

def postopen():
    z=csv('protected-v17-postopen-risk.csv.gz',V18)
    p=csv('asof-positioning-features.csv.gz')
    rows=[]
    atoms=[]
    for (h,c),r in z[z.model.eq('cash_risk')].groupby(['horizon','cutoff']):
        a=r.sort_values('day').merge(p[p.cutoff.eq(c)],on=['day','origin','cutoff'],validate='1:1')
        ds=a.day.to_numpy();en=a.target.to_numpy();y=a.actual.to_numpy(float)
        mean=a['mean'].to_numpy(float)
        event=a.expansion.to_numpy(float);prob=a.p.to_numpy(float)
        ese=np.log(np.maximum(y,.014)/np.maximum(mean,.027))
        xx=matrix(a,POSITION+DELIVERY[:7]+INNOV)
        for i in range(len(a)):
            t=matured(ds,en,y,i)
            if len(t)<44:continue
            factor,m,u=scaled_fit(xx,ese,t,i)
            b=fit(xx[t],event[t]-prob[t],195)
            pc=bound(prob[i]+.45*b.values(xx[i]))
            residual=ese[t]-np.mean(ese[t])
            shape=np.exp(np.quantile(residual,Q))
            parent=shape/shape.mean()*mean[i]
            # Exact point/event forecast is preserved; the companion law shares its point center and uses a fitted prior error shape.
            for mod,mult,pr in [('V17_cash_risk',1.,bound(prob[i])),('V19_position_postopen',factor,pc)]:
                q=parent*mult
                atoms.append(q.astype(np.float32))
                rows.append(dict(day=ds[i],horizon=h,cutoff=c,origin=a.origin.iloc[i],target_end=en[i],cohort=a.cohort.iloc[i],
                    model=mod,parent='V17_cash_risk',law=len(atoms)-1,active=1,last_mature=max(en[t]),
                    source_release=a.source_release.iloc[i],**scalar_score(q,y[i],pr,int(event[i]))))
    write('postopen-risk-cases.csv.gz',pd.DataFrame(rows))
    np.savez_compressed(OUT/'postopen-risk-laws.npz',annualized_volatility_atoms=np.stack(atoms))

if __name__=='__main__':
    risk()
    postopen()

