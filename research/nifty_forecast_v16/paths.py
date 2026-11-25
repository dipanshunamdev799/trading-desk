"""Generate coherent OHLC from predicted overnight and regular-session components."""
from .common import *
from .model import fit
from .session_models import load, prepare
from research.nifty_forecast_v15.scores import profile, positions_of_hit
from research.nifty_forecast_v15.sequential import TICK, log_ticks, numpy_zip

JOINT=('historical_iv','direct_domestic','direct_global','prev_momentum','prev_mean_reversion',
       'decomposed','decomposed_gift','session_state','multitask','fixed_mixture')
REFERENCES=('V14_constant_iv','V14_iv_scaled_blocks','V14_gjr_student','V14_gjr_iv','V14_trend_shrink','V14_trend_persistent','V15_iv_restart','V15_gjr_restart')
LEVELS=(.005,.01,.02,.03,.05)
STATE_COLS=('atm','rv21','finance','breadth5','foreign_sd','eq6','prior_gap','cash5')
FIT_COLS=('prior_return','prior_gap','rv21','cash5','cash21','breadth5','breadth21','finance','defensive','atm','iv_term')


def logs_to_path(a):
    prefix=np.column_stack((np.zeros(len(a)),np.cumsum(a[:,:-1,3],axis=1)))
    return a+prefix[:,:,None]


def reshape_local(base,gap,regular):
    # Retain each empirical high/low excursion relative to the initial and terminal marks for that session.
    high=np.maximum(base[:,:,0],base[:,:,3])
    low=np.minimum(base[:,:,0],base[:,:,3])
    c=gap+regular
    return np.stack((gap,np.maximum(gap,c)+np.maximum(base[:,:,1]-high,0.),
                     np.minimum(gap,c)+np.minimum(base[:,:,2]-low,0.),c),axis=-1)


def shift(local,change):
    ans=local.copy()
    g=ans[:,:,0]
    r=ans[:,:,3]-g+change
    return reshape_local(ans,g,r)


def select_analogue(past,current,draw):
    a=np.asarray(past,float)
    b=np.asarray(current,float)
    med=np.nanmedian(a,axis=0)
    z=np.where(np.isfinite(a),a,med)
    v=np.where(np.isfinite(b),b,med)
    std=z.std(axis=0).clip(.00001)
    dist=np.mean(np.square(((z-v)/std).clip(-5,5)),axis=1)
    w=np.exp(-.68*(dist-dist.min()))
    w=.8*w/w.sum()+.20/len(w)
    ids=np.searchsorted(np.cumsum(w),draw,side='right').clip(0,len(w)-1)
    return ids,float(1/(w@w))


def distance_crps(x,y):
    x=np.sort(x)
    return np.mean(np.abs(x-y))-np.dot(x,2*np.arange(len(x))-len(x)+1)/len(x)**2


class Paths:
    def __init__(self):
        frame,self.y=load()
        self.x=prepare(self.y,frame[frame.cutoff.eq('08:55')].set_index('day').reindex(self.y.index))
        self.cash=matrix('cash-panel/cash.csv')
        self.days=self.cash.index.to_numpy()
        p=self.cash.to_numpy(float)
        self.local=np.log(p[1:]/p[:-1,3][:,None])
        self.pos={d:i for i,d in enumerate(self.y.index)}
        self.gap=self.local[:,0].copy()
        self.rth=self.local[:,3]-self.gap
        self.c=np.log(p[:,3])
        self.state=self.x[list(STATE_COLS)].to_numpy(float)
        self.dom=self.x[list(FIT_COLS)].to_numpy(float)
        self.global_x=self.x[list((*FIT_COLS,'eq6','us_asia','foreign_sd','vix_move'))].to_numpy(float)
        self.gift=self.x.gift_proxy.to_numpy(float)
        self.risk=self.x.atm.to_numpy().astype(float)
        self.volstates=read('daily-gjr-states.json',V15)

    def fit_tasks(self,i):
        last=i-20
        idx=np.arange(max(0,last-HIST),last)
        if len(idx)<51:return None
        cols=[self.gap[idx],self.rth[idx]]
        for k in [1,3,5,21]:
            cols.append(self.c[idx+k]-self.c[idx])
        v=np.mean(self.local[idx[:,None]+np.arange(21),3]**2,axis=1)
        vol=np.sqrt(v*252)
        cols.append(np.log(np.maximum(vol,.025)/np.maximum(self.risk[idx],.035)))
        y=np.column_stack(cols)
        med=np.median(y,axis=0)
        sd=y.std(axis=0).clip(.003)
        md=fit(self.global_x[idx],(y-med)/sd,150)
        # Estimate a shared low-rank map while preserving each response's native centering and scale.
        u,s,v=np.linalg.svd(md.coefficient[1:],full_matrices=False)
        b=(u[:,:2]*s[:2])@v[:2]
        current=self.global_x[i,md.active]
        current=np.where(np.isfinite(current),current,md.median)
        z=((current-md.center)/md.sd).clip(-5,5)
        val=med+sd*(md.coefficient[0]+z@b)*.70
        return val,dict(last_train_end=self.y.index[idx[-1]+20],rank=2,n=len(idx),task_scales=sd.tolist(),
                        coefficients=b.tolist(),intercept=md.coefficient[0].tolist(),task_centers=med.tolist(),feature_centers=md.center.tolist(),
                        feature_scales=md.sd.tolist(),feature_medians=md.median.tolist(),
                        columns=[[*FIT_COLS,'eq6','us_asia','foreign_sd','vix_move'][j] for j in md.active])

    def make(self,i,h,key):
        rng=np.random.default_rng(SEED+pd.Timestamp(key).toordinal()*47+h)
        hist=np.arange(max(0,i-h+1-HIST),i-h+1)
        assert len(hist)>=54 and hist[-1]+h-1<i
        target=self.c[hist+h]-self.c[hist]
        gf=fit(self.global_x[hist],self.gap[hist],110)
        rf=fit(self.dom[hist],self.rth[hist],110)
        remit=target-self.gap[hist]-self.rth[hist]
        remainder=fit(self.dom[hist],remit,140)
        df=fit(self.dom[hist],target,110)
        gl=fit(self.global_x[hist],target,125)
        loc_gap=float(np.clip(.70*gf.values(self.global_x[i]),-.021,.021))
        loc_rth=float(np.clip(.6*rf.values(self.dom[i]),-.014,.014))
        loc_rest=float(np.clip(.55*remainder.values(self.dom[i]),-.02,.02))
        gift=self.gift[i]
        cash_iv=float(np.clip(self.risk[i],.045,.65))
        if np.isfinite(gift):
            avail=hist[np.isfinite(self.gift[hist])]
            raw_tail=(self.gap[avail]-self.gift[avail])
            gmed=float(np.median(raw_tail)) if len(avail)>=35 else 0.
            location_g=float(np.clip(gift+.7*gmed,-.035,.035))
            tail_shrink=.50 if len(avail)<35 else float(np.clip(
                np.std(raw_tail)/max(.0005,np.std(self.gap[avail])),.28,.91))
        else:
            location_g=loc_gap
            tail_shrink=1.
        uniform=rng.random((PATH_N,3))
        idx0=np.minimum((uniform[:,0]*len(hist)).astype(int),len(hist)-1)
        idx,jess=select_analogue(self.state[hist],self.state[i],uniform[:,0])
        samples=hist[idx0]
        matched=hist[idx]
        pos=samples[:,None]+np.arange(h)
        pm=matched[:,None]+np.arange(h)
        hist_risk=np.maximum(.05,np.nan_to_num(self.risk[samples],nan=cash_iv))
        scaled=np.clip(cash_iv/hist_risk,.53,1.8)
        base=self.local[pos]*scaled[:,None,None]
        gd=self.local[pm].copy()
        risk_path=np.where(np.isfinite(self.risk[pm]),self.risk[pm],cash_iv)
        starting=np.maximum(risk_path[:,0],.045)
        # A drawn historical joint state path supplies risk and financial/global co-movements.
        # The current IV/GJR state, age, and signed simulated innovations set the scale after rebasing.
        root=float(self.volstates[key]['next_variance'])
        alpha=float(np.clip(self.volstates[key]['alpha'],0,.16))
        gamma=float(np.clip(self.volstates[key]['gamma'],0,.18))
        beta=float(np.clip(self.volstates[key]['beta'],.65,.95))
        omega=float(self.volstates[key]['omega'])
        dyn_scale=np.ones((len(gd),h))
        running=np.full(len(gd),max(.01,root))
        for j in range(h):
            fix=.45*np.sqrt(252*running)/100 + .55*cash_iv
            current_risk=.70*fix+.30*cash_iv*np.clip(risk_path[:,j]/starting,.6,1.7)
            dyn_scale[:,j]=np.clip(current_risk/np.maximum(.045,risk_path[:,j]),.5,1.8)
            simulated=100*gd[:,j,3]*dyn_scale[:,j]
            running=np.clip(omega+(alpha+gamma*(simulated<0))*simulated**2+beta*running,.01,65)
        gd*=dyn_scale[:,:,None]
        base_gap=base[:,:,0].copy()
        base_rth=base[:,:,3]-base_gap
        mean_g=float(np.median(base_gap[:,0]))
        mean_r=float(np.median(base_rth[:,0]))
        residual_g=base_gap[:,0]-mean_g
        rest_baseline=float(np.median(base[:,1:,3].sum(axis=1)))
        # Shift future regular-session increments relative to their empirical residuals.
        add=np.zeros(h)
        add[0]=loc_rth-mean_r
        add[1:]=(loc_rest-rest_baseline)/(h-1)
        g0=base_gap.copy()
        g0[:,0]=loc_gap+residual_g
        b0=reshape_local(base,g0,base_rth+add)
        g1=g0.copy()
        g1[:,0]=location_g+tail_shrink*residual_g
        gft=reshape_local(base,g1,base_rth+add)
        gg=gd[:,:,0].copy()
        gr=gd[:,:,3]-gg
        gg[:,0]=location_g+tail_shrink*(gg[:,0]-np.median(gg[:,0]))
        dyn_add=add.copy()
        dyn_add[0]=loc_rth-np.median(gr[:,0])
        dyn_add[1:]=(loc_rest-np.median(gd[:,1:,3].sum(axis=1)))/(h-1)
        local_state=reshape_local(gd,gg,gr+dyn_add)
        multitask_fit=self.fit_tasks(i)
        multi,tasks=multitask_fit if multitask_fit is not None else (None,None)
        if multi is None:
            mt=b0
        else:
            g2=base_gap.copy()
            add2=add.copy()
            loc=np.clip(multi[0],-.02,.02)
            rloc=np.clip(multi[1],-.012,.012)
            g2[:,0]=loc+residual_g
            add2[0]=rloc-mean_r
            loc_forward=multi[4] if h==5 else multi[5]
            add2[1:]=(np.clip(loc_forward-loc-rloc,-.02,.02)-rest_baseline)/(h-1)
            mt=reshape_local(base,g2,base_rth+add2)
        unconditional_center=np.median(base[:,:,3].sum(axis=1))
        direct=shift(base,(np.clip(.60*df.values(self.dom[i]),-.028,.028)-unconditional_center)/h)
        direct_all=shift(base,(np.clip(.60*gl.values(self.global_x[i]),-.028,.028)-unconditional_center)/h)
        mom=.23*float(np.clip(self.x.prior_return.iloc[i],-.025,.025))
        full={'historical_iv':base,'direct_domestic':direct,'direct_global':direct_all,
              'prev_momentum':shift(base,(mom-unconditional_center)/h),
              'prev_mean_reversion':shift(base,(-mom-unconditional_center)/h),
              'decomposed':b0,'decomposed_gift':gft,'session_state':local_state,'multitask':mt,
              'fixed_mixture':np.where((uniform[:,1]<1/3)[:,None,None],base,
                np.where((uniform[:,1]<2/3)[:,None,None],gft,direct))}
        assert set(full)==set(JOINT)
        projected=self.x[['atm','finance','vix_move','eq6']].to_numpy(float)[pm]
        project=np.nan_to_num(projected,nan=0.).astype('float32')
        params=dict(last_train_end=self.y.index[hist[-1]+h-1],train_n=len(hist),analogue_ess=jess,issue_iv=cash_iv,
                    gift_proxy=gift if np.isfinite(gift) else None,gift_gap_location=location_g,
                    conditional_gap=loc_gap,conditional_regular=loc_rth,conditional_remaining=loc_rest,
                    gap_fit=gf.receipt((*FIT_COLS,'eq6','us_asia','foreign_sd','vix_move')),
                    regular_fit=rf.receipt(FIT_COLS),remainder_fit=remainder.receipt(FIT_COLS),multitask=tasks)
        return {m:logs_to_path(v) for m,v in full.items()},params,project


def output_scores(paths,actual,h,meta,barrier_rows):
    res=profile(paths[None,...],np.empty((0,4)),h,1.)
    observed=profile(actual[None,None,...],np.empty((0,4)),h,1.)
    keys=['endpoint','vol','range','high','low','drawdown','rebound']
    vals={m:res[m][0] for m in keys}
    truth={m:float(observed[m][0,0]) for m in keys}
    metrics={}
    for k,x in vals.items():
        lo,mid,hi=np.quantile(x,[.1,.5,.9])
        o=truth[k]
        metrics.update({k+'_mean':x.mean(),k+'_median':mid,k+'_q10':lo,k+'_q90':hi,
                        k+'_crps':distance_crps(x,o),k+'_mae':abs(x.mean()-o),
                        k+'_coverage80':int(lo<=o<=hi),k+'_width80':hi-lo,
                        k+'_interval80':hi-lo+10*(max(lo-o,0)+max(o-hi,0))})
    p=float((vals['endpoint']>0).mean())
    y=truth['endpoint']>0
    units=np.array([.02,.03,.14,.032])*np.array([np.sqrt(h/5),np.sqrt(h/5),1,np.sqrt(h/5)])
    vals0=np.column_stack([vals[k] for k in ('endpoint','range','vol','drawdown')])/units
    actual0=np.array([truth[k] for k in ('endpoint','range','vol','drawdown')])/units
    e=np.linalg.norm(vals0-actual0,axis=1).mean()-.5*np.linalg.norm(vals0-np.roll(vals0,len(vals0)//2,axis=0),axis=1).mean()
    rr=(truth['vol']/max(.005,float(vals['vol'].mean())))**2
    touch=[]; integrated=[]
    for b in LEVELS:
        for side,cl in [('upper',1),('lower',2)]:
            w=1+b if side=='upper' else 1-b
            first=positions_of_hit(paths[:,:,cl],w,side=='upper')
            reality=int(positions_of_hit(actual[:,cl],w,side=='upper'))
            cdf=(first[:,None]<=np.arange(1,h+1)).mean(0)
            np.testing.assert_array_equal(cdf,np.maximum.accumulate(cdf))
            t=cdf[-1]
            assert t+1.e-12>=((paths[:,-1,3]>=w) if side=='upper' else (paths[:,-1,3]<=w)).mean()
            brier=(t-float(reality<=h))**2
            ib=((cdf-(np.arange(1,h+1)>=reality))**2).mean()
            survive=first>1
            post=float((first[survive]<=h).mean()) if survive.any() else np.nan
            extra={f'brier_by_{j}':(cdf[j-1]-(reality<=j))**2 for j in (1,3,5,10,21) if j<=h}
            barrier_rows.append(dict(**meta,barrier=b,side=side,p=t,actual_touch=int(reality<=h),touch_brier=brier,
                 integrated_brier=ib,actual_first=reality,event_time_log=-np.log(max(.0005,float((first==reality).mean()))),
                 p_first_session=float(cdf[0]),conditional_p_after_first=post,
                 conditional_brier=(post-(reality<=h))**2 if reality>1 else np.nan,**extra))
            touch.append(brier)
            integrated.append(ib)
    return dict(**meta,**metrics,actual_endpoint=truth['endpoint'],actual_vol=truth['vol'],actual_range=truth['range'],
                p_up=p,brier=(p-y)**2,log_loss=-np.log(max(.0005,p if y else 1-p)),accuracy=int((p>=.5)==y),
                energy=e,variance_qlike=rr-np.log(rr)-1,touch_brier=np.mean(touch),integrated_brier=np.mean(integrated))


def run():
    m=Paths()
    win=pd.read_csv(V15/'original-windows.csv')
    prior=read('joint-update-archive.json',V15)
    history_ref={(r['horizon'],r['origin']):r for r in prior['files']}
    records=[]; barrier_rows=[]; laws=[]
    model_states=[]
    arr=m.cash.to_numpy(float)
    for n,w in enumerate(win.itertuples(index=False)):
        i=m.pos[m.cash.index[m.cash.index.get_loc(w.origin)+1]]
        h=int(w.horizon)
        day=m.y.index[i]
        assert m.cash.index[i+h]==w.target and day>w.origin
        real=arr[i+1:i+h+1]/arr[i,3]
        simulated,meta,states=m.make(i,h,w.origin)
        ref=history_ref[h,w.origin]
        folder=OUT/'joint-paths'
        folder.mkdir(parents=True,exist_ok=True)
        outfile=folder/f'{h}-{w.origin}.npz'
        encoded={name:log_ticks(v) for name,v in simulated.items()}
        archive={**encoded,'simulated_analogue_states':states}
        for q in encoded.values():
            assert q.shape==(PATH_N,h,4) and (q[:,:,1]>=np.maximum(q[:,:,0],q[:,:,3])).all()
            assert (q[:,:,2]<=np.minimum(q[:,:,0],q[:,:,3])).all()
        numpy_zip(outfile,archive)
        laws.append(dict(origin=w.origin,day=day,horizon=h,target=w.target,decision=stamp(day,'08:55').isoformat(),
                         reference_close=float(arr[i,3]),gift_eligible=bool(meta['gift_proxy'] is not None),
                         file=outfile.relative_to(OUT).as_posix(),sha256=sha(outfile),
                         original_v14=ref['frozen_file'],v14_sha256=ref['frozen_sha256'],
                         original_v15=ref['file'],v15_sha256=ref['sha256']))
        model_states.append(dict(origin=w.origin,day=day,horizon=h,target=w.target,**meta))
        candidates={name:np.exp(values*TICK) for name,values in encoded.items()}
        with np.load(V14/ref['frozen_file'],allow_pickle=False) as z:
            for tag in ['constant_iv','iv_scaled_blocks','gjr_student','gjr_iv','trend_shrink','trend_persistent']:
                candidates['V14_'+tag]=np.exp(z[tag][:,:h]*TICK)
        with np.load(V15/ref['file'],allow_pickle=False) as z:
            for tag in ['iv_restart','gjr_restart']:
                candidates['V15_'+tag]=np.exp(z['k00_'+tag]*TICK)
        for name,x in candidates.items():
            row=dict(origin=w.origin,forecast_day=day,horizon=h,cohort=w.cohort,target=w.target,model=name,
                     gift_eligible=int(meta['gift_proxy'] is not None),literal_calendar=w.literal_calendar)
            records.append(output_scores(x,real,h,row,barrier_rows))
        if (n+1)%100==0:
            print('Paths replayed',n+1,'/',len(win),flush=True)
    f=pd.DataFrame(records)
    a=pd.DataFrame(barrier_rows)
    write('path-scores.csv.gz',f)
    write('path-passage-scores.csv.gz',a)
    save('path-fit-ledger.json',model_states)
    save('path-archive.json',dict(n_paths=PATH_N,joint_models=JOINT,protected_joint_models=REFERENCES,
        order='Open, high, low, close as log ticks relative original close',log_tick=TICK,
        state_columns=['ATM IV','financial relative performance','foreign VIX change','simple global factor'],files=laws))
    print('Scored',len(f),'coherent path laws across',len(win),'fixed targets',flush=True)

if __name__=='__main__':
    run()
