"""Test gap survival, direction continuation and retracement from known cash prefixes."""
from .common import *
from .data import DOM
from .model import logistic_offset, predict_probability

PREDICTORS=DOM+('gap_visible','gap_scaled','abs_gap_scaled','cash_prefix','cash_prefix_rv','open_bank_lead','open_breadth',
                'open_dispersion','open_defensive','gap_broad','gap_finance','eq6','cross_sign','gift_proxy','foreign_after_gap')
SEGMENTS=(('09:25',1),('10:20',12))


def clipped_log(p,y):
    return -np.log(np.clip(p if y else 1-p,.0005,.9995))


def combine_survival(obs,gap,cur):
    mag=np.log(np.maximum(abs(gap),.0003))
    med=max(np.nanmedian(abs(mag-np.nanmedian(mag))),.2)
    w=np.exp(-np.minimum(abs(mag-np.log(max(abs(cur),.0003)))/med,10))
    w*=np.where(np.sign(gap)==np.sign(cur),1.,.60)
    w=.65*w/w.sum()+.35/len(w)
    values=np.bincount(obs.astype(int),weights=w,minlength=77)
    return values,(1/(w@w))


def run():
    x=pd.read_csv(OUT/'decision-features.csv.gz')
    y=matrix('session-targets.csv')
    evt=pd.read_csv(OUT/'gap-fill-events.csv')
    rows=[]; timing=[]; cdf=[]; observed=[]
    for clk,k in SEGMENTS:
        f=x[x.cutoff.eq(clk)].set_index('day').reindex(y.index)
        a=f.reindex(columns=PREDICTORS).to_numpy(float)
        days=y.index.to_numpy()
        status=f.gap_visible.notna().to_numpy()
        known=(np.sign(f.gap_visible.to_numpy())==np.sign(y.gap.to_numpy())) & status
        c=y.one
        valid=y.cash_regular_grid.eq(1).to_numpy()
        expected=y.cohort.notna().to_numpy()
        # Keep distinct binary outcomes. A close may sustain the prior close-to-open gap while retracing part of it.
        after='regular_after_bar' if k==1 else 'remaining'
        targets={
          'remaining_same_gap_direction':np.sign(y[after])*np.sign(y.gap),
          'open_to_close_continuation':np.sign(y.regular)*np.sign(y.gap),
          'close_beyond_previous_close_in_gap_direction':np.sign(c)*np.sign(y.gap),
          'next_regular_day_same_direction':np.sign(y.next_next_close)*np.sign(y.gap)}
        for task,v in targets.items():
            vv=np.asarray(v)
            clock_label_extra=int(task=='next_regular_day_same_direction')
            for i in np.flatnonzero(valid & known & expected & np.isfinite(vv)):
                eligible=(np.arange(len(y))<i-clock_label_extra)&known&valid&np.isfinite(vv)
                ix=np.flatnonzero(eligible)[-160:]
                if len(ix)<50:continue
                h=(vv[ix]>0).astype(int)
                g=(vv[i]>0)
                prior=(h.sum()+1)/(len(h)+2)
                big=np.abs(f.gap_visible.iloc[ix].to_numpy())
                cur=abs(f.gap_visible.iloc[i])
                # The magnitude threshold comes from the fit’s existing sample.
                high=(cur>=np.quantile(big,.75))
                bucket=(big>=np.quantile(big,.75))==high
                same_sign=np.sign(f.gap_visible.iloc[i])==np.sign(f.gap_visible.iloc[ix].to_numpy())
                group=h[bucket & same_sign]
                cond=(group.sum()+.8+3*prior)/(len(group)+4.6)
                pars=logistic_offset(a[ix],h,prior,105)
                full=float(predict_probability(pars,a[i],prior,.85))
                pars=logistic_offset(a[ix,:len(DOM)+5],h,prior,105)
                loc=float(predict_probability(pars,a[i,:len(DOM)+5],prior,.85))
                for model,p in [('history',prior),('gap_sign_size',cond),('cash_prefix_only',loc),('sector_offshore_full',full),
                                ('continuation_rule',.67),('reversal_rule',.33)]:
                    rows.append(dict(day=days[i],cutoff=clk,target=task,cohort=y.cohort.iloc[i],model=model,actual=int(g),p=p,
                                     brier=(p-g)**2,log_loss=clipped_log(p,g),high_gap=int(high),positive_gap=int(y.gap.iloc[i]>0),
                                     last_training_end=days[ix[-1]+clock_label_extra],training=len(ix)))
        for threshold,z in evt.groupby('touch_fraction'):
            hits=z.set_index('day').first_hit.reindex(days).to_numpy()
            open_risk=(hits>k)&known&valid
            for i in np.flatnonzero(expected&open_risk):
                ix=np.flatnonzero((np.arange(len(y))<i)&open_risk)[-160:]
                if len(ix)<42:continue
                past=hits[ix].astype(int)
                now=hits[i]
                raw=np.bincount(past,minlength=77).astype(float)/len(past)
                cond,ess=combine_survival(past,f.gap_visible.iloc[ix].to_numpy(),f.gap_visible.iloc[i])
                h=(past<76).astype(int)
                base=(h.sum()+.75)/(len(h)+1.50)
                args=logistic_offset(a[ix],h,base,105)
                q=float(predict_probability(args,a[i],base,.75))
                blend=cond.copy()
                if cond[k+1:76].sum()>0:
                    blend[k+1:76]*=q/cond[k+1:76].sum()
                    blend[76]=1-q
                for name,v in [('survivor_history',raw),('gap_matched_survival',cond),('calibrated_survival',blend)]:
                    assert abs(v.sum()-1)<1.e-8 and v[:k+1].sum()==0.
                    p_hit=float(v[k+1:76].sum())
                    curve=np.cumsum(v)[k+1:76]
                    bs=np.mean((curve-(np.arange(k+1,76)>=now))**2)
                    if p_hit>0:
                        conditional=float(v[k+1:76]@np.arange(k+1,76)/p_hit)
                    else:
                        conditional=np.nan
                    ae=5*abs(conditional-now) if now<76 else np.nan
                    timing.append(dict(day=days[i],cutoff=clk,threshold=threshold,model=name,cohort=y.cohort.iloc[i],actual_touch=int(now<76),p_hit=p_hit,
                        brier=(p_hit-(now<76))**2,integrated_brier=bs,time_log_loss=clipped_log(float(v[int(now)]),True),
                        expected_bar_if_hit=conditional,actual_bar=now,conditional_abs_minutes=ae,matched_hist_n=len(ix),
                        analogue_ess=ess if name!='survivor_history' else len(ix),last_training_end=days[ix[-1]]))
                    cdf.append(v.astype('float32'))
                observed.append(dict(day=days[i],cutoff=clk,threshold=threshold,risk_n=len(ix),already_resolved=int((hits[:i]<=k).sum())))
    r=pd.DataFrame(rows)
    pp=pd.DataFrame(timing)
    assert r.last_training_end.lt(r.day).all() and pp.last_training_end.lt(pp.day).all()
    write('session-continuation-scores.csv.gz',r)
    write('first-touch-fill-scores.csv.gz',pp)
    np.savez_compressed(OUT/'gap-fill-time-laws.npz',prob=np.stack(cdf),index_units=np.array('0 opening, 1–75 bar index, 76 right-censored'))
    write('gap-fill-training-risks.csv',pd.DataFrame(observed))
    q=r.groupby(['cutoff','target','model'],as_index=False).agg(n=('day','size'),actual=('actual','mean'),p=('p','mean'),brier=('brier','mean'),log_loss=('log_loss','mean'))
    write('continuation-leaderboard.csv',q)
    tw=pp.groupby(['cutoff','threshold','model'],as_index=False).agg(n=('day','size'),actual_fill=('actual_touch','mean'),forecast_fill=('p_hit','mean'),
                         brier=('brier','mean'),integrated_brier=('integrated_brier','mean'),log_loss=('time_log_loss','mean'),
                         conditional_abs_minutes=('conditional_abs_minutes','mean'),median_ess=('analogue_ess','median'))
    write('gap-fill-leaderboard.csv',tw)
    save('absorption-receipt.json',dict(n_continuation=len(r),n_survival=len(pp),abs_bar_units=5,
                note='Only clocks where the reported barrier remained untouched enter the corresponding loss. Day 76 is right censored.'))
    print(len(r),'directional absorption scores and',len(pp),'survivor scores',flush=True)

if __name__=='__main__':
    run()
