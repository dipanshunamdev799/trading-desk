"""Coherent fixed-endpoint scoring and eligible event-time risk sets."""
import csv
import gzip

from .common import *
from .data import Daily
from research.nifty_forecast_v14.generation import TICK

Q=np.array([.05,.10,.25,.5,.75,.90,.95])
QCOL=['q05','q10','q25','q50','q75','q90','q95']
EPS=.0005


def losses(a,actual):
    """Every row is an equal-weight predictive law, with a common target."""
    n=a.shape[1]
    ranked=np.sort(a,axis=1)
    qs=ranked[:,np.ceil(n*Q).astype(int)-1]
    rank=(np.arange(n)*2+1-n)/(n*n)
    return (a.mean(axis=1),qs,np.mean(abs(a-actual),axis=1)-ranked@rank,
            np.maximum(Q[None,:]*(actual-qs),(Q[None,:]-1)*(actual-qs)).mean(axis=1))


def p_loss(p,actual):
    p=np.asarray(p)
    b=(p-actual)**2
    l=-np.log(np.clip(p if actual else 1-p,EPS,1))
    return b,l


def positions_of_hit(matrix,boundary,upper):
    mark=matrix>=boundary if upper else matrix<=boundary
    return np.where(mark.any(axis=-1),mark.argmax(axis=-1)+1,matrix.shape[-1]+1)


def profile(paths,known,h,anchor):
    """Separate original-window and still-uncertain outcomes."""
    # Suffix is expressed relative to the unchanged original anchor.
    volume=paths[:,:, :,3]
    m,n,r=volume.shape
    previous=np.concatenate([np.full((m,n,1),anchor),volume[:,:,:-1]],axis=2)
    rr=np.log(volume/previous)
    ss=np.sum(rr*rr,axis=2)
    future_high=paths[:,:,:,1].max(axis=2)
    future_low=paths[:,:,:,2].min(axis=2)
    if len(known):
        hi=known[:,1].max();lo=known[:,2].min()
        oldret=np.diff(np.log(np.r_[1.,known[:,3]]))
        old_var=oldret@oldret
        closes=np.concatenate([np.broadcast_to(np.r_[1.,known[:,3]],(m,n,len(known)+1)),volume],axis=2)
    else:
        hi=0.;lo=np.inf;old_var=0.
        closes=np.concatenate([np.ones((m,n,1)),volume],axis=2)
    high=np.maximum(hi,future_high)
    low=np.minimum(lo,future_low)
    full_range=high-low
    rem_range=(future_high-future_low)/anchor
    drawdown=(closes/np.maximum.accumulate(closes,axis=2)-1.).min(axis=2)
    rebound=(closes/np.minimum.accumulate(closes,axis=2)-1.).max(axis=2)
    return dict(endpoint=volume[:,:,-1]-1.,remaining_return=volume[:,:,-1]/anchor-1.,
        vol=np.sqrt(252*(ss+old_var)/h),remaining_vol=np.sqrt(252*ss/r),
        range=full_range,remaining_range=rem_range,high=high-1.,low=low-1.,drawdown=drawdown,rebound=rebound)


def opening_code(p,u,d,k,h):
    same=(u==d)&(u<=h)
    op=np.take_along_axis(p[:,:,:,0],np.minimum(u-1,h-1)[:,:,None],axis=2)[:,:,0]
    up=(u<d)|(same&(op>=1+k))
    down=(d<u)|(same&(op<=1-k))
    return np.where(up,0,np.where(down,1,np.where(same,2,3)))


class Stream:
    def __init__(self,path,fields):
        self.handle=gzip.open(path,'wt',encoding='utf-8',compresslevel=2,newline='')
        self.writer=csv.DictWriter(self.handle,fieldnames=fields)
        self.writer.writeheader()
        self.n=0

    def write(self,rows):
        self.writer.writerows(rows)
        self.n+=len(rows)

    def __enter__(self):
        return self

    def __exit__(self,*unused):
        self.handle.close()


IDENT=['horizon','origin','target','asof','checkpoint','remaining','cohort','model','literal_calendar']
CONT=['endpoint','remaining_return','vol','remaining_vol','range','remaining_range','high','low','drawdown','rebound']
ENDCOLS=['p_up','p_remaining_up','brier','log_loss','remaining_brier','remaining_log_loss','vol_qlike','remaining_vol_qlike',
         'joint_energy','expand25','expand50','contract20','range_extreme_p','vol_transition_p']
COLS=IDENT+CONT+[f'{key}_{metric}' for key in CONT for metric in
                     ['mean','q10','q50','q90','crps','mae','pinball','cov50','cov80','width80','is80']]+ENDCOLS
BARCOLS=IDENT+['barrier','threshold','side','actual','p','observed_rel_time','expected_time_given_hit',
               'brier','log_loss','integrated_brier','passage_log_loss','opposite_after_hit','baseline_alive']
ORDCOLS=IDENT+['barrier','threshold','known_upper','known_lower','known_order','score_order',
              'actual_order','p_upper_first','p_lower_first','p_same_candle','p_neither','order_brier',
              'score_additional','no_additional_actual','no_additional_p','no_additional_brier']

def metadata(rec,model):
    return {**{k:getattr(rec,k) for k in IDENT if k!='model'},'model':model}


def risk_model_rows(rec,y,m,old,point,names):
    out=[]
    data={k:np.concatenate([old[k],m[k]],axis=0) for k in CONT if not k.startswith('remaining')}
    full={k:losses(v,point[k]) for k,v in data.items()}
    # Frozen distribution is expressed in the same current-price units by an exact price ratio transformation.
    for k in ('remaining_return','remaining_vol','remaining_range'):
        a=m[k]
        if k=='remaining_return':
            frozen=(1+old['endpoint'])/rec.realized_price_ratio-1
        else:
            frozen=old[k]
        full[k]=losses(np.concatenate([frozen,a]),point[k])
        data[k]=np.concatenate([frozen,a])
    p=(data['endpoint']>0).mean(axis=1);pr=(data['remaining_return']>0).mean(axis=1)
    b,l=p_loss(p,point['endpoint']>0);br,lr=p_loss(pr,point['remaining_return']>0)
    a=np.stack([data[k] for k in ('endpoint','range','vol','drawdown')],axis=-1)
    # Fixed dimension units; common half-sample permutation for the energy pair term.
    units=np.array([.02,.03,.14,.032])*np.array([np.sqrt(rec.horizon/5.),np.sqrt(rec.horizon/5.),1.,np.sqrt(rec.horizon/5.)])
    z=a/units
    observed=np.array([point[k] for k in ('endpoint','range','vol','drawdown')])/units
    energy=np.linalg.norm(z-observed,axis=-1).mean(axis=-1)-.5*np.linalg.norm(z-np.roll(z,z.shape[1]//2,axis=1),axis=-1).mean(axis=-1)
    for j,n in enumerate(names):
        row=metadata(rec,n)
        row.update({k:point[k] for k in CONT})
        for key,score in full.items():
            mu,q,c,pb=score
            lo,mid,hi=q[j,1],q[j,3],q[j,5]
            a=point[key]
            row.update({key+'_mean':mu[j],key+'_q10':lo,key+'_q50':mid,key+'_q90':hi,key+'_crps':c[j],
                key+'_mae':abs(mu[j]-a),key+'_pinball':pb[j],key+'_cov50':int(q[j,2]<=a<=q[j,4]),
                key+'_cov80':int(lo<=a<=hi),key+'_width80':hi-lo,
                key+'_is80':hi-lo+10*(max(0.,lo-a)+max(0.,a-hi))})
        v=(point['vol']/max(.006,row['vol_mean']))**2
        rem=(point['remaining_vol']/max(.006,row['remaining_vol_mean']))**2
        # Zero-remaining-volatility paths supply an endpoint control, not a variance forecast.
        row.update(p_up=p[j],p_remaining_up=pr[j],brier=b[j],log_loss=l[j],remaining_brier=br[j],remaining_log_loss=lr[j],
            vol_qlike=float(v-np.log(v)-1) if n!='zero_remaining' and v>0 else None,
            remaining_vol_qlike=float(rem-np.log(rem)-1) if n!='zero_remaining' and rem>0 else None,
            joint_energy=energy[j],expand25=float(np.mean(data['vol'][j]>=1.25*y.trailing_at_origin)),
            expand50=float(np.mean(data['vol'][j]>=1.50*y.trailing_at_origin)),
            contract20=float(np.mean(data['vol'][j]<=.80*y.trailing_at_origin)),
            range_extreme_p=float(np.mean(data['range'][j]>=y.range_threshold)),
            vol_transition_p=float(np.mean(data['vol'][j]>=y.high_threshold)))
        out.append(row)
    return out


def score_passage(rec,past,actual,future,prior,names,iv0):
    """Emit survival forecasts only where the indicated side remains at risk."""
    k,h,r=rec.checkpoint,rec.horizon,rec.remaining
    c=np.arange(1,r+1)
    thresholds=[(str(i),b) for i,b in enumerate(BARRIERS)]
    thresholds.extend([(f'iv{n}',n*iv0*np.sqrt(h/252.)) for n in (.5,1.,1.5,2.)])
    ts=[];orders=[];excluded=0
    for label,b in thresholds:
        pos={};truth={};past_known={};prior_indices={};past_times={}
        for side in ('upper','lower'):
            col=1 if side=='upper' else 2
            level=1+b if side=='upper' else 1-b
            truth[side]=int(positions_of_hit(actual[:,col],level,side=='upper'))
            past_times[side]=int(positions_of_hit(past[:,col],level,side=='upper')) if k else 1
            past_known[side]=past_times[side]<=k
            pos[side]=positions_of_hit(future[:,:,:,col],level,side=='upper')
            prior_indices[side]=positions_of_hit(prior[:,:,col],level,side=='upper')
        known_order=-1
        if any(past_known.values()):
            a,b0=past_times['upper'],past_times['lower']
            known_order=0 if a<b0 else 1 if b0<a else 0 if past[a-1,0]>=1+b else 1 if past[a-1,0]<=1-b else 2
        for side in ('upper','lower'):
            if past_known[side]:
                excluded+=1
                continue
            opp='lower' if side=='upper' else 'upper'
            actual_time=truth[side]-k
            yes=int(actual_time<=r)
            fc=pos[side]
            alive=prior_indices[side]>k
            frozen_f=prior_indices[side][alive]-k
            fpt=[frozen_f,*list(fc)]
            vec=np.stack([(v[:,None]<=c).mean(axis=0) if len(v) else np.full(r,np.nan) for v in fpt])
            for j,name in enumerate(names):
                if len(fpt[j])==0:
                    continue
                px=float(vec[j,-1])
                probability_day=float(np.mean(fpt[j]==actual_time))
                conditional=float(np.mean(fpt[j][fpt[j]<=r])) if px>0 else None
                br,ls=p_loss(px,yes)
                loss_int=float(np.mean((vec[j]-(c>=actual_time))**2))
                ts.append(dict(**metadata(rec,name),barrier=label,threshold=b,side=side,actual=yes,p=px,
                    observed_rel_time=actual_time,expected_time_given_hit=conditional,brier=float(br),log_loss=float(ls),
                    integrated_brier=loss_int,passage_log_loss=float(-np.log(max(EPS,probability_day))),
                    opposite_after_hit=int(past_known[opp]),baseline_alive=int(alive.sum()) if name=='frozen' else None))
            # Monotonicity and endpoint-vs-touch coherence for every updated law.
            assert np.all(np.diff(vec[1:],axis=-1)>=-1.e-12)
            probability_endpoint=(future[:,:,-1,3]>=1+b).mean(axis=1) if side=='upper' else (future[:,:,-1,3]<=1-b).mean(axis=1)
            assert np.all(vec[1:,-1]+1.e-12>=probability_endpoint)
        u=np.where(past_known['upper'],past_times['upper'],k+pos['upper'])
        d=np.where(past_known['lower'],past_times['lower'],k+pos['lower'])
        if known_order<0:
            a=opening_code(future,pos['upper'],pos['lower'],b,r)
        else:
            a=np.full(u.shape,known_order)
        actual_order=0 if truth['upper']<truth['lower'] else 1 if truth['lower']<truth['upper'] else 3 if truth['upper']>h else (
            0 if actual[truth['upper']-1,0]>=1+b else 1 if actual[truth['upper']-1,0]<=1-b else 2)
        score_additional=not all(past_known.values())
        none=(u>h) if past_known['lower'] else (d>h) if past_known['upper'] else ((u>h)&(d>h))
        actual_none=int((past_known['upper'] or truth['upper']>h) and (past_known['lower'] or truth['lower']>h))
        hit=np.stack([(a==j).mean(axis=1) for j in range(4)],axis=1)
        no=none.mean(axis=1) if score_additional else np.ones(len(future))
        for i,n in enumerate(names[1:]):
            orders.append(dict(**metadata(rec,n),barrier=label,threshold=b,known_upper=int(past_known['upper']),
                known_lower=int(past_known['lower']),known_order=known_order,score_order=int(known_order<0),
                actual_order=actual_order,p_upper_first=hit[i,0],p_lower_first=hit[i,1],p_same_candle=hit[i,2],p_neither=hit[i,3],
                order_brier=float(np.square(hit[i]-np.eye(4)[actual_order]).sum()) if known_order<0 else None,
                score_additional=int(score_additional),no_additional_actual=actual_none,no_additional_p=no[i],
                no_additional_brier=(no[i]-actual_none)**2 if score_additional else None))
    return ts,orders,excluded


def compute():
    d=Daily.load()
    iv=matrix('remaining-tenor-availability.csv').reset_index().set_index(['asof','remaining'])
    version=read('joint-update-archive.json')
    price=d.prices.to_numpy()
    date_cols=pd.read_csv(OUT/'update-calendar.csv',low_memory=False)
    lookup=dict(tuple(date_cols.groupby(['horizon','origin'])))
    thresholds={h:matrix(f'thresholds-{h}.csv',V14) for h in HORIZONS}
    models=version['models']
    counts_excluded=0; frozen_n=2048
    sub=np.arange(N)*(frozen_n//N)+frozen_n//N//2
    with Stream(OUT/'sequential-scores.csv.gz',COLS) as point_out, Stream(OUT/'sequential-passage.csv.gz',BARCOLS) as event_out, Stream(OUT/'sequential-order.csv.gz',ORDCOLS) as order_out:
        for j,unit in enumerate(version['files'],1):
            h,origin=unit['horizon'],unit['origin']
            ii=d.positions[origin]
            actual=price[ii+1:ii+h+1]/price[ii,3]
            frame=lookup[h,origin]
            y=d.labels[h].loc[origin].copy()
            y['range_threshold']=thresholds[h].at[origin,'range90']
            y['high_threshold']=thresholds[h].at[origin,'high_risk']
            iv0=iv.at[(origin,h),'iv']
            with np.load(V14/unit['frozen_file'],allow_pickle=False) as z:
                prior=np.exp(TICK*z[unit['frozen_model']][:,:h])
            assert len(prior)==frozen_n
            # Full exact frozen endpoint law and full-window quantities are scored at each checkpoint.
            original=profile(prior[None,...],np.empty((0,4)),h,1.)
            with np.load(OUT/unit['file'],allow_pickle=False) as z:
                for row in frame.sort_values('checkpoint').itertuples(index=False):
                    k=row.checkpoint
                    anchor=row.realized_price_ratio
                    suffix=np.stack([z[f'k{k:02}_{n}'] for n in models[1:]])
                    future=np.exp(TICK*suffix)*anchor
                    prefix=actual[:k]
                    true=profile(actual[None,None,k:],prefix,h,anchor)
                    true={key:float(val[0,0]) for key,val in true.items()}
                    p=profile(future,prefix,h,anchor)
                    ref=prior[:,k-1,3] if k else np.ones(len(prior))
                    frozen_part=profile(prior[None,:,k:]/ref[None,:,None,None],np.empty((0,4)),row.remaining,1.)
                    # No-conversion control uses issued OHLC. Known extreme floors apply only to actual updates.
                    old={**original,'remaining_range':frozen_part['remaining_range'],'remaining_vol':frozen_part['remaining_vol']}
                    # Use equal length for vectorized scores; overwrite the frozen row with exact V14-A atoms below.
                    thin={key:val[:,sub] for key,val in old.items()}
                    table=risk_model_rows(row,y,p,thin,true,models)
                    a=table[0]
                    for key in CONT:
                        if key=='remaining_return':
                            data=(1+old['endpoint'])/anchor-1
                        else:
                            data=old[key]
                        pred,qs,crps,pb=losses(data,true[key])
                        lo,mid,hi=qs[0,1],qs[0,3],qs[0,5]
                        y0=true[key]
                        for m,v in {'mean':pred[0],'q10':lo,'q50':mid,'q90':hi,'crps':crps[0],'mae':abs(pred[0]-y0),
                                    'pinball':pb[0],'cov50':int(qs[0,2]<=y0<=qs[0,4]),'cov80':int(lo<=y0<=hi),
                                    'width80':hi-lo,'is80':hi-lo+10*(max(0,lo-y0)+max(0,y0-hi))}.items():
                            a[key+'_'+m]=v
                    for kind,prob,actual_,score_name,log_name in (
                        ('p_up',float((old['endpoint']>0).mean()),true['endpoint']>0,'brier','log_loss'),
                        ('p_remaining_up',float(((1+old['endpoint'])/anchor>1).mean()),true['remaining_return']>0,'remaining_brier','remaining_log_loss')):
                        a[kind]=prob
                        a[score_name],a[log_name]=[float(x) for x in p_loss(prob,actual_)]
                    for field in ['vol','remaining_vol']:
                        value=(true[field]/max(.006,a[field+'_mean']))**2
                        a[field+'_qlike']=value-np.log(value)-1 if value>0 else None
                    for field,hit in [('expand25',old['vol']>=1.25*y.trailing_at_origin),
                             ('expand50',old['vol']>=1.50*y.trailing_at_origin),('contract20',old['vol']<=.80*y.trailing_at_origin),
                             ('range_extreme_p',old['range']>=y.range_threshold),('vol_transition_p',old['vol']>=y.high_threshold)]:
                        a[field]=float(hit.mean())
                    if k:
                        assert np.all(p['range']>=row.range_floor-2.e-11)
                        assert np.all(p['high']>=row.known_high-2.e-11) and np.all(p['low']<=row.known_low+2.e-11)
                    point_out.write(table)
                    ev,orders,excluded=score_passage(row,prefix,actual,future,prior,models,iv0)
                    counts_excluded+=excluded
                    event_out.write(ev)
                    order_out.write(orders)
            if j%60==0:
                print('Scored',j,'/',len(version['files']),'fixed windows',flush=True)
        save('sequential-score-counts.json',dict(scores=point_out.n,passage=event_out.n,ordering=order_out.n,
             resolved_side_checkpoints_excluded=counts_excluded,date_windows=len(version['files']),
             uncertainty='Future touch probabilities evaluated only for side-specific survivors. Order modeled only while unresolved.'))
        print('Scored',point_out.n,'law rows and',event_out.n,'eligible passage rows',flush=True)


if __name__=='__main__':
    compute()
