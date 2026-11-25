"""Same-cutoff original weekly/monthly returns and immutable endpoint-law corrections."""
from .common import *
from .panel import EW,PRE_STOCK
from .gift import score
from research.nifty_forecast_v16.model import fit
from research.nifty_forecast_v14.path_score import summaries,log_brier

ORIGINAL_BASE=('prior_ret5','prior_ret21','rolling_rv5','trailing_vol','domestic_rotation_finance','domestic_rotation_defensive',
               'iv_prev','iv_skew','iv_term','vix_level','basis_previous','prior_future_curve',*EW)
STOCK_DAILY=('seed300_advance','seed300_dispersion','seed300_median','seed300_concentration','seed300_activity_relative',
             'basket_advance','basket_dispersion','allEQ_advance','allEQ_concentration')


def load_legacy():
    a={}
    with np.load(V14/'standalone-endpoint-laws.npz',allow_pickle=False) as x:
        keys=x['keys'];off=x['offsets'];v=x['atoms'];w=x['weights']
        for i,(h,origin,mod,tgt) in enumerate(keys):
            if (int(h)==5 and mod=='sign_shrinkage') or (int(h)==21 and mod=='domestic_location_gjr_scale'):
                a[(int(h),origin)]=(tgt,v[off[i]:off[i+1]],w[off[i]:off[i+1]])
    return a


def evaluate(a,w,y):
    x=summaries(np.asarray(a),np.array([y]),np.asarray(w))[0]
    cp=float(w@(a>0))
    br,ll=log_brier(cp,int(y>0))
    return dict(actual=y,p=cp,brier=br,crps=x['crps'],log_loss=ll,mean=x['predicted_mean'],median=x['predicted_median'],
         correct=int((cp>=.5)==(y>0)),mae=x['mae'],width=x['width80'],covered=x['coverage80'],interval_score=x['interval_score80'],
         quantile_loss=x['pinball'],squared_error=x['se'])


def family(x):
    d=pd.read_csv(OUT/'official-stock-breadth.csv').set_index('day').reindex(x.origin)
    d.index=x.index
    return x.join(d[['allEQ_advance','allEQ_concentration','seed300_advance','seed300_dispersion','seed300_median',
             'seed300_concentration','seed300_activity_relative','basket_advance','basket_dispersion']])


def chronology(frame,fields,y,ends,decision,kind='plain'):
    d=frame.index.to_numpy()
    a=frame.reindex(columns=fields).to_numpy(float)
    mu=np.full(len(frame),np.nan)
    for i in range(len(a)):
        t=np.flatnonzero((ends<decision[i])&(np.arange(len(d))<i)&np.isfinite(y))[-HIST:]
        if len(t)<MIN:continue
        if kind=='historical':
            mu[i]=float(np.median(y[t]))
        else:
            fit0=fit(a[t],y[t],150)
            mu[i]=np.clip(.65*fit0.values(a[i]),-.045,.045)
    return mu


def fit_multitask(x,y,decision,auxiliary=False):
    cols=ORIGINAL_BASE+STOCK_DAILY+('expected_gap','gift_proxy','eq6')
    u=x.reindex(columns=cols).to_numpy(float)
    tasks=['gap','initial_rth','original1','original3','original5','original21']
    if auxiliary:
        tasks+=['bank_relative','session_risk']
    yy=y[tasks].to_numpy(float)
    end=y.end_original21.fillna('9999-12-31').to_numpy()
    out=np.full_like(yy,np.nan)
    for i in range(len(x)):
        j=np.flatnonzero((end<decision[i])&(np.arange(len(x))<i)&np.isfinite(yy).all(axis=1))[-140:]
        if len(j)<53:continue
        a=yy[j]; med=np.median(a,axis=0); sd=a.std(axis=0).clip(.002)
        m=fit(u[j],(a-med)/sd,180.)
        U,S,V=np.linalg.svd(m.coefficient[1:],full_matrices=False)
        b=(U[:,:2]*S[:2])@V[:2]
        zz=u[i,m.active]
        zz=np.where(np.isfinite(zz),zz,m.median)
        w=((zz-m.center)/m.sd).clip(-5,5)
        out[i]=med+.6*sd*(m.coefficient[0]+w@b)
    return out


def run():
    f=pd.read_csv(OUT/'original-feature-panel.csv.gz',low_memory=False)
    y=matrix('original-target-panel.csv')
    y=y.join(matrix('session-targets.csv',V16)[['bank_relative','session_risk']])
    v16=pd.read_csv(V16/'original-endpoint-scores.csv.gz')
    old=load_legacy()
    combos=[]
    data=[];atoms=[];rid=[];audit=[]
    for clock in ('previous_1700','preauction_0855'):
        x=family(f[f.cutoff.eq(clock)].set_index('day').reindex(y.index))
        day=x.index.to_numpy()
        decision=x.decision.str[:10].to_numpy()
        multi=fit_multitask(x,y,decision)
        multi_risk=fit_multitask(x,y,decision,auxiliary=True)
        assert np.all(decision<=day)
        if clock=='previous_1700':
            assert x.reindex(columns=['gift_proxy','eq6','us_mean','asia_mean']).isna().all().all()
        for h in HORIZONS:
            target='original'+str(h)
            actual=y[target].to_numpy()
            until=y['end_'+target].fillna('9999-12-31').to_numpy()
            cohort=y[f'cohort_{h}'].fillna('').to_numpy()
            idx=np.flatnonzero(cohort!='')
            assert len(idx)==EXPECTED[h]
            v14_y=matrix(f'targets-{h}.csv',V14).endpoint_return
            b=x.reindex(columns=PRE_STOCK+STOCK_DAILY).to_numpy(float)
            loc=chronology(x,ORIGINAL_BASE,actual,until,decision)
            loc_hist=chronology(x,(),actual,until,decision,'historical')
            loc_stock=chronology(x,ORIGINAL_BASE+PRE_STOCK+STOCK_DAILY,actual,until,decision)
            phase1=chronology(x,ORIGINAL_BASE+('expected_gap',),y.gap.to_numpy(),y.end_gap.to_numpy(),decision)
            phase2=chronology(x,ORIGINAL_BASE+PRE_STOCK,y.initial_rth.to_numpy(),y.end_initial_rth.to_numpy(),decision)
            offset=actual-y.gap.to_numpy()-y.initial_rth.to_numpy()
            phase3=chronology(x,ORIGINAL_BASE+STOCK_DAILY,offset,until,decision)
            q_gift=x.expected_gap.to_numpy(float)
            e0=actual-loc
            exact_mean=np.full(len(day),np.nan)
            for i in idx:
                tgt,xx,ww=old[h,y.origin.iloc[i]]
                assert tgt==until[i]
                exact_mean[i]=np.log1p(float(ww@xx))
            e_old=actual-exact_mean
            for i in idx:
                when=decision[i];sym=y.origin.iloc[i];yt=float(np.expm1(actual[i]))
                np.testing.assert_allclose(yt,v14_y.loc[sym],atol=3.e-14,rtol=0)
                valid=(until<when)&(np.arange(len(day))<i)&np.isfinite(actual)
                ii=np.flatnonzero(valid)[-HIST:]
                assert len(ii)>=MIN
                known=actual[ii]
                sig=float(x.iv_prev.iloc[i]*np.sqrt(h/252))
                spread=np.nanstd(known)
                base_r=np.quantile(known-np.median(known),Q)
                if np.isfinite(sig) and spread>0:
                    base_r*=np.clip(sig/spread,.55,1.65)
                u0=np.quantile(np.r_[abs(known),-abs(known)],Q)
                p1=float(q_gift[i]) if np.isfinite(q_gift[i]) else phase1[i]
                m=(p1+phase2[i]+phase3[i])
                laws={'neutral':u0,'historical':loc_hist[i]+base_r,'clock_structural':loc[i]+base_r,
                      'stock_direct':loc_stock[i]+base_r,'component_plus_residual':m+base_r,
                      'low_rank_tasks':(multi[i,4] if h==5 else multi[i,5])+base_r,
                      'low_rank_sector_risk':(multi_risk[i,4] if h==5 else multi_risk[i,5])+base_r}
                for name,v in list(laws.items()):
                    if not np.isfinite(v).all():
                        laws[name]=laws['clock_structural']
                j=np.flatnonzero(valid&np.isfinite(e0))[-125:]
                dv=0.
                if len(j)>=44:
                    rd=fit(b[j],e0[j],185.)
                    dv=float(np.clip(.52*rd.values(b[i]),-.009,.009))
                    rid.append(dict(day=day[i],horizon=h,mode='structural_oos_residual',fit_cut=clock,
                                    latest=max(until[j]),**rd.receipt(PRE_STOCK+STOCK_DAILY)))
                laws['stock_residual']=laws['clock_structural']+dv
                laws['fixed_structural_mixture']=np.r_[laws['clock_structural'][::3],laws['component_plus_residual'][1::3],
                    laws['stock_residual'][2::3]]
                for tag,law in laws.items():
                    s=score(law,actual[i])
                    if tag=='neutral':
                        s.update(p=.5,brier=.25,log_loss=np.log(2),correct=int(yt>0))
                    where=len(atoms);atoms.append(law.astype('float32'))
                    data.append(dict(day=day[i],origin=sym,target_date=until[i],horizon=h,cutoff=clock,model=tag,
                        cohort=cohort[i],last_mature=max(until[ii]),law=where,adapted=int(tag=='stock_residual' and len(j)>=44),**s))
                if clock=='preauction_0855':
                    # Exact benchmarks are always retained with their documented native clock. The corrected overlay
                    # is a separately labeled prior-law experiment once the source's inputs are available.
                    tgt,aa,ww=old[h,sym]
                    j0=np.flatnonzero(valid&np.isfinite(e_old))[-120:]
                    dv0=0.0
                    if len(j0)>=38:
                        o=fit(b[j0],e_old[j0],200.)
                        dv0=float(np.clip(.55*o.values(b[i]),-.008,.008))
                        rid.append(dict(day=day[i],horizon=h,mode='protected_law_residual_overlay',fit_cut='after_prior_guard',
                                        latest=max(until[j0]),**o.receipt(PRE_STOCK+STOCK_DAILY)))
                    s=evaluate((1+aa)*np.exp(dv0)-1,ww,yt)
                    s['abs_error']=abs(s['actual']-s['median'])
                    s['sq_error']=s['squared_error']
                    combos.append(dict(day=day[i],origin=sym,horizon=h,cutoff='after_prior_guard',model='V14_stock_overlay',
                        law_shift=dv0,adapted=int(len(j0)>=38),time_assumption='Protected V14 input availability retains 09:10 guard',
                        last_mature=max(until[j0]) if len(j0) else None,cohort=cohort[i],target_date=until[i],**s))
                audit.append(dict(day=day[i],decision=x.decision.iloc[i],horizon=h,clock=clock,origin=sym,target=until[i],
                                  prev_gift=(float(q_gift[i]) if np.isfinite(q_gift[i]) else None),
                                  gap_input_kind='known previous-day GIFT move' if clock=='previous_1700' else 'known current early GIFT forecast',
                                  max_label_end=max(until[ii]),maturity_guard_day=when))
    old_id=['V14_sign_shrinkage','V14_domestic_GJR','V15_gjr_restart','V16_decomposed_gift','session_state','decomposed_gift',
            'neutral','matured_historical']
    keep=v16[v16.model.isin(old_id)].copy()
    keep['cutoff']='native_archived'
    keep['day']=keep.origin.map(y.reset_index().set_index('origin').day)
    keep=keep.rename(columns={'target':'target_date','actual_endpoint':'actual','p_up':'p','endpoint_crps':'crps','endpoint_mae':'abs_error',
             'endpoint_coverage80':'covered','endpoint_width80':'width'})
    keep['correct']=((keep.p>=.5)==(keep.actual>0)).astype(int)
    df=pd.DataFrame(data)
    assert df.last_mature.lt(df.day).all()
    write('original-clock-forecasts.csv.gz',df)
    write('protected-original-scores.csv.gz',keep)
    write('protected-law-residual-overlays.csv.gz',pd.DataFrame(combos))
    write('original-cutoff-audit.csv',pd.DataFrame(audit))
    save('original-fits.json',rid)
    np.savez_compressed(OUT/'original-clock-laws.npz',atoms=np.stack(atoms),axis='log-return')
    print('Original fixed objectives:',len(df),'same-cutoff forecasts and',len(combos),'protected-law overlays',flush=True)

if __name__=='__main__':
    run()
