"""Retimed joint control, common-random-number convergence and barrier risk sets."""
import copy
from .common import *
from research.nifty_forecast_v16 import paths as v16
from research.nifty_forecast_v15.sequential import TICK, log_ticks, numpy_zip, RandomPanel, continuous, garch_paths


def outcome(legacy,w):
    i=legacy.pos[w['day']]
    ca=legacy.cash.to_numpy(float)
    h=w['horizon']
    return ca[i+1:i+h+1]/ca[i,3]


def recast(legacy):
    p=copy.copy(legacy)
    history=pd.read_csv(V16/'decision-features.csv.gz',low_memory=False)
    x=history[history.cutoff.eq('17:00')].set_index('day').reindex(legacy.y.origin)
    x.index=legacy.y.index
    g=pd.read_csv(OUT/'gift-decision-clock.csv',low_memory=False)
    pre=g[g.clock.eq('prior_close')].set_index('day').reindex(legacy.y.index)
    # Every retimed input is selected using its own historical 17:00 snapshot or GIFT quote clock.
    p.x=x
    p.dom=x[list(v16.FIT_COLS)].to_numpy(float)
    p.state=x[list(v16.STATE_COLS)].to_numpy(float)
    p.global_x=x[list((*v16.FIT_COLS,'eq6','us_asia','foreign_sd','vix_move'))].to_numpy(float)
    p.risk=x.atm.ffill().fillna(.12).to_numpy(float)
    p.gift=pre.return_1530.to_numpy(float)
    on=pd.to_datetime(pre.latest_available,utc=True,format='mixed')
    dc=pd.to_datetime(pre.decision,utc=True,format='mixed')
    assert on[on.notna()].le(dc[on.notna()]).all()
    assert pre.loc[on.notna(),'origin'].eq(legacy.y.origin[on.notna()]).all()
    return p


def compute_one(model,start,h,root,n):
    before=v16.PATH_N
    try:
        v16.PATH_N=n
        values,params,states=model.make(start,h,root)
    finally:
        v16.PATH_N=before
    return values,params


def cells(paths,actual,h):
    table=[]
    q=v16.output_scores(paths,actual,h,{},table)
    arr=pd.DataFrame(table)
    return q,arr


SCORECOLS=['brier','endpoint_crps','range_crps','range_coverage80','vol_mae','variance_qlike','energy','touch_brier','integrated_brier']


def pack(book,result,row):
    for item in row:
        book.append({**result,**item})


def run():
    archive=read('path-archive.json',V16)
    base=v16.Paths()
    retime=recast(base)
    comparisons=[]; barriers=[]; density=[]; blobs=[]; receipts=[]
    outdir=OUT/'timed-paths'
    outdir.mkdir(exist_ok=True)
    keep=['decomposed','decomposed_gift','session_state']
    sample={(h,ls[i]['origin']) for h in HORIZONS for ls in [[r for r in archive['files'] if r['horizon']==h]]
            for i in np.linspace(0,len(ls)-1,32,dtype=int)}
    for j,w in enumerate(archive['files'],1):
        h=w['horizon']; ori=w['origin']; day=w['day']
        real=outcome(base,w)
        pos=base.pos[day]
        target=w['target']
        co=base.y.loc[day,'cohort_five' if h==5 else 'cohort_twentyone']
        snap,fit=compute_one(retime,pos,h,ori,256)
        with np.load(V16/w['file'],allow_pickle=False) as z:
            prior={k:z[k].copy() for k in keep}
        file=outdir/f'{h}-{ori}.npz'
        stored={}
        for tm,m,book in [('previous_1700',retime,snap),('preauction_0855',base,None)]:
            mu=float(np.clip(m.risk[pos],.045,.65))
            rp=RandomPanel.create(ori)
            controls={'same_clock_IV':continuous(rp,h,mu),'same_clock_GJR':garch_paths(rp,h,m.volstates[ori])}
            raw={**{tag:log_ticks(book[tag]) if book is not None else prior[tag] for tag in keep},
                 **{tag:log_ticks(a) for tag,a in controls.items()}}
            for tag,current in raw.items():
                score,b=cells(np.exp(current*TICK),real,h)
                exact=dict(horizon=h,origin=ori,day=day,cutoff=tm,cohort=co,target=target,model=tag,n=256,
                         gift_eligible=int(np.isfinite(m.gift[pos])),**{k:score[k] for k in SCORECOLS})
                comparisons.append(exact)
                pack(barriers,exact|{'cohort':co},b.to_dict('records'))
                if tm=='previous_1700' or tag in controls:
                    stored[tm+'_'+tag]=current
        for name in stored:
            ar=stored[name];assert ar.shape==(256,h,4)
            assert (ar[:,:,1]>=np.maximum(ar[:,:,0],ar[:,:,3])).all() and (ar[:,:,2]<=np.minimum(ar[:,:,0],ar[:,:,3])).all()
        numpy_zip(file,stored)
        blobs.append(dict(origin=ori,horizon=h,day=day,target=target,file=file.relative_to(OUT).as_posix(),sha256=sha(file),
             v16_reference=w['file'],v16_sha256=w['sha256']))
        if (h,ori) in sample:
            for n in PATH_COUNTS:
                active,nt=compute_one(base,pos,h,ori,n)
                for tag in ('decomposed_gift','session_state'):
                    qq=log_ticks(active[tag])
                    if n==256:
                        assert np.array_equal(qq,prior[tag]),(ori,h,tag)
                    b,events=cells(np.exp(qq*TICK),real,h)
                    density.append(dict(horizon=h,origin=ori,day=day,cohort=co,model=tag,paths=n,
                       **{s:b[s] for s in SCORECOLS},day_one_Brier=float(events.brier_by_1.mean()),
                       survivor_Brier=float(events.conditional_brier.mean()),survivor_sides=int(events.conditional_brier.notna().sum())))
                    fpath=OUT/'convergence-laws'/str(n)/f'{h}-{ori}-{tag}.npz'
                    fpath.parent.mkdir(parents=True,exist_ok=True)
                    np.savez_compressed(fpath,ohlc_log_ticks=qq)
                    receipts.append(dict(horizon=h,origin=ori,model=tag,n=n,file=fpath.relative_to(OUT).as_posix(),sha256=sha(fpath),
                                   last_fit_end=nt['last_train_end'],nested_stream=True))
        if j%120==0:
            print('Retimed path windows',j,'/',len(archive['files']),flush=True)
    z=pd.DataFrame(comparisons)
    n=pd.DataFrame(density)
    write('retimed-path-scores.csv.gz',z)
    write('retimed-passage-scores.csv.gz',pd.DataFrame(barriers))
    write('path-convergence-scores.csv',n)
    save('retimed-path-archive.json',dict(ticks=TICK,paths=256,files=blobs,protected_v16_before_auction='Exact maps and archive hashes retained. V16 265-origin lead GIFT result was a next-morning 08:55 comparison, not a previous-close simulation.',
         baseline_metadata='Reconstructed both clocks via V16 method, also restarted IV and GJR from each cutoff eligible risk state. Exact V14 native forecasts are shown separately.'))
    save('path-convergence-archive.json',dict(counts=PATH_COUNTS,seed='V16 preserved paired seed and shared leading uniform draws',files=receipts))
    b=n.pivot(index=['horizon','origin','model'],columns='paths',values=SCORECOLS+['day_one_Brier','survivor_Brier'])
    v=[]
    for (h,mod),g in b.groupby(level=[0,2]):
        for k in SCORECOLS+['day_one_Brier','survivor_Brier']:
            for n0 in [256,2048,8192]:
                a0=g[k,n0]
                d0=a0-g[k,8192]
                v.append(dict(horizon=h,model=mod,metric=k,paths=n0,origins=len(g),average=a0.mean(),signed_delta_8192=d0.mean(),
                              median_abs_MC_delta=d0.abs().median(),rms_MC_delta=np.sqrt((d0**2).mean())))
    write('path-convergence-summary.csv',pd.DataFrame(v))
    print('Scored',len(z),'same-time path laws and',len(density),'nested convergence laws',flush=True)

if __name__=='__main__':
    run()
