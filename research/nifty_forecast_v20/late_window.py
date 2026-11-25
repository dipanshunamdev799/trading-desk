"""Anchor the post-week positioning check to archived same-clock GJR paths."""
from .common import *
from .joint import outcome_series,paths_index
from .modeling import block_intervals,disjoint,fit_slope,timed,variant_matrix
from .panel import GROUPS,POSITION,cash,dedup
from research.nifty_forecast_v15.sequential import TICK
from research.nifty_forecast_v17.weekly import evaluate

PARENT='archived_GJR_component'

def path_components(panel,targets,book):
    log_cells=np.full((len(panel),2,256),np.nan)
    ids=np.flatnonzero(targets.cohort_21.notna())
    clock=panel.cutoff.iloc[0]
    for i in ids:
        record=book[21,targets.origin.iloc[i]]
        with np.load(V17/record['file'],allow_pickle=False) as z:
            ticks=z[clock+'_same_clock_GJR'][:,[4,20],3].astype(float)*TICK
        log_cells[i,0]=ticks[:,0]
        log_cells[i,1]=ticks[:,1]-ticks[:,0]
        np.testing.assert_allclose(log_cells[i].sum(axis=0),ticks[:,1],rtol=0,atol=1.e-12)
    return ids,log_cells

def test_clock(panel,y,calendar,book,law_shift):
    cutoff=panel.decision.str[:10].to_numpy(dtype='U10')
    ids,logs=path_components(panel,y,book)
    fields=GROUPS['participant_futures']
    position=variant_matrix(panel,fields,calendar)
    persistent=variant_matrix(panel,dedup(POSITION['persistence']+POSITION['concentration']),calendar)
    corporate=variant_matrix(panel,GROUPS['corporate_announcements'],calendar)
    entries={PARENT:None,'bias_only':None,'participant_now':position['fresh'],
             'participant_smoothed':position['smooth5'],'participant_lag5':position['lag5'],
             'participant_persistent':persistent['fresh'],'corporate_now':corporate['fresh']}
    w=np.full(logs.shape[-1],1/logs.shape[-1])
    summary=[]; rows=[]
    for j,(a,b) in enumerate(((0,5),(5,21))):
        r,end=outcome_series(y,f'{a}_{b}')
        parent=logs[:,j]
        err=r-parent.mean(axis=1)
        d=[]
        for i in ids:
            k=len(law_shift)
            law_shift.append(parent[i])
            t=timed(end,cutoff,i,err)
            cap=.009*np.sqrt((b-a)/5)
            base=dict(cutoff=panel.cutoff.iloc[i],day=panel.index[i],origin=y.origin.iloc[i],start_offset=a,end_offset=b,
                      first_target=y[f'start_{a}_{b}'].iloc[i],target_end=end[i],cohort=y.cohort_21.iloc[i],law=k)
            for name,x in entries.items():
                ok=name==PARENT
                shift=0.
                use=t
                if name=='bias_only' and len(t)>=45:
                    ok=True
                    shift=.65*np.mean(err[t])
                if x is not None:
                    m=np.isfinite(x).any(axis=1)
                    use=t[m[t]]
                    if m[i] and len(use)>=45:
                        shift,fit=fit_slope(x[use],err[use],x[i])
                        ok=bool(len(fit.active))
                        shift=.65*shift if ok else 0.
                shift=float(np.clip(shift,-cap,cap))
                out=evaluate(np.expm1(parent[i]+shift),w,np.expm1(r[i]))
                d.append(base|dict(model=name,active=ok,correction=shift,n_train=len(use),
                         last_mature=max(end[use]) if len(use) else None,**out))
        rows+=d
        m=pd.DataFrame(d)
        ref=m[m.model.eq(PARENT)].set_index('day')
        for score in ('brier','crps'):
            stacks=[];group=[]
            for name,g in m.groupby('model'):
                q=g.set_index('day').reindex(ref.index)
                gain=ref[score]-q[score]
                ok=q.active
                t=q.loc[ok].reset_index().rename(columns={'day':'origin_day','first_target':'day'})
                stacks.append(gain.where(ok).to_numpy())
                group.append(dict(cutoff=q.cutoff.iloc[0],start_offset=a,end_offset=b,model=name,metric=score,n=len(q),
                         matched=int(ok.sum()),disjoint=disjoint(t),parent=ref.loc[ok,score].mean(),matched_loss=q.loc[ok,score].mean(),
                         matched_gain=gain[ok].mean(),full_parent=ref[score].mean(),full_loss=q[score].mean(),
                         earlier_gain=gain[ok&q.cohort.eq('early')].mean(),later_gain=gain[ok&q.cohort.eq('later')].mean()))
            bands=block_intervals(np.column_stack(stacks),21,1000,SEED+20*j+(score=='crps')).add_prefix('interval_')
            summary.append(pd.concat([pd.DataFrame(group),bands],axis=1))
    return rows,pd.concat(summary,ignore_index=True)

def run():
    f=csv('asof-features.csv.gz').set_index('day')
    y=csv('multi-horizon-targets.csv').set_index('day')
    calendar=cash().index
    book=paths_index()
    laws=[];rows=[];scores=[]
    for clock in CLOCKS:
        p=f[f.cutoff.eq(clock)]
        d,s=test_clock(p,y.reindex(p.index),calendar,book,laws)
        rows+=d
        scores.append(s)
    write('strong-parent-component-cases.csv.gz',pd.DataFrame(rows))
    write('strong-parent-component-comparisons.csv',pd.concat(scores,ignore_index=True))
    np.savez_compressed(OUT/'strong-parent-component-laws.npz',log_parent_atoms=np.stack(laws))
    save('strong-parent-component-config.json',dict(clocks=CLOCKS,components=[(0,5),(5,21)],parent=PARENT,
         parent_file='V17 retimed OHLC archive, same-clock GJR column',train='45 to 140 fully matured component errors',
         shift='0.65 times slope only, capped at 0.009 × sqrt(component sessions / 5), plus a separate pure bias control',
         controls='No shift, bias, 5-session participant lag and corporate comparison. Fallback preserves unchanged path component.',
         importance='Follow-up with a path-calibrated parent and same 217 origins for each piece, examining post-first-week placement.',
         law='Add correction to indexed equal-weight log atoms and apply expm1. From the matched 256 inherited GJR paths.'))
    print('Scored GJR-anchored first-week and 6–21 returns for',len(rows),'cases',flush=True)

if __name__=='__main__':
    run()
