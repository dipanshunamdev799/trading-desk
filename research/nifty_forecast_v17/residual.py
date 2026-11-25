"""Chronological residual learning against explicit same-cutoff parents."""
from dataclasses import dataclass
from .common import *
from .panel import PX,RV,EW,NATIVE,STOCK,STANDARD,FIN,LIQ,SURPRISE,CROSS,OPTIONS,NEWS,GLOBAL,ALTS
from .gift import score
from research.nifty_forecast_v16.model import fit, logistic_offset, predict_probability

BASE=tuple(dict.fromkeys(PX+RV+EW+NATIVE+('domestic_rotation_finance','domestic_rotation_defensive')))
RISK_TARGETS=('remaining_vol','remaining_range','abs_regular')
BIN_TARGETS=('touch_up','touch_down')
RETURN_TARGETS=('r15','r30','r60','regular_residual','next_session','remaining_3','remaining_5','remaining_10','remaining_21')

@dataclass
class Arm:
    name:str
    features:tuple=()
    kind:str='residual'
    parent:str='frozen_parent_residual_history'
    category:str='core'

def prior_idx(dates,ends,y,i,key=None,limit=HIST):
    use=(ends<dates[i])&(np.arange(len(dates))<i)&np.isfinite(y)
    if key is not None:use&=key
    return np.flatnonzero(use)[-limit:]

def standardize_raw_features(x,z,days):
    """Predict each candidate feature on a strictly earlier copy of the parent's state."""
    b=np.full(x.shape,np.nan)
    for i in range(len(x)):
        t=np.flatnonzero(days<days[i])[-90:]
        if len(t)<30:
            continue
        xx=x[t].copy()
        enough=np.isfinite(xx).sum(axis=0)>=14
        if not enough.any():continue
        sub=xx[:,enough]
        med=np.nanmedian(sub,axis=0)
        yes=np.where(np.isfinite(sub),sub,med)
        f=fit(z[t],yes,70)
        out=x[i,enough]-f.values(z[i])
        b[i,enough]=out
    return b


def setups(clock,target):
    a=[Arm('neutral',(),kind='neutral',parent='native_control',category='parent'),
       Arm('historical',(),kind='history',parent='native_control',category='parent'),
       Arm('price_only',PX,kind='base',parent='native_control',category='parent'),
       Arm('vol_only',RV,kind='base',parent='native_control',category='parent'),
       Arm('price_vol',tuple(dict.fromkeys(PX+RV)),kind='base',parent='native_control',category='parent'),
       Arm('official_ew',tuple(dict.fromkeys(PX+RV+EW)),kind='base',parent='price_vol',category='official_equal_weight'),
       Arm('native_control',BASE,kind='base',parent='price_vol',category='native_sector'),
       Arm('frozen_parent_residual_history',BASE,kind='base_error',parent='native_control',category='parent'),
       Arm('gap_size_only',('gap_seen',),kind='base',parent='price_only',category='opening_surprise')]
    if target in BIN_TARGETS:
        return [q for q in a if q.name in ('historical','price_vol','native_control')]+[
                Arm('dispersion_touch',STOCK+LIQ,parent='native_control',category='stock_liquidity',kind='binary'),
                Arm('surprise_touch',SURPRISE,parent='native_control',category='opening_surprise',kind='binary'),
                Arm('etf_touch',CROSS,parent='native_control',category='cross_instrument',kind='binary')]
    controls=[Arm('surprise_direct',SURPRISE,'direct',parent='native_control',category='opening_surprise'),
              Arm('surprise_residual',SURPRISE,category='opening_surprise'),
              Arm('stock_direct',STOCK,'direct',parent='native_control',category='stock_breadth'),
              Arm('stock_residual',STOCK,category='stock_breadth'),
              Arm('stock_neutralized',STANDARD,category='sector_adjusted_stock'),
              Arm('financial_residual',FIN,category='financial_participation'),
              Arm('liquidity_residual',LIQ,category='volume_liquidity'),
              Arm('cross_instrument_residual',CROSS,category='cross_instrument'),
              Arm('IV_residual',OPTIONS[1:],category='option_surface'),
              Arm('official_EW_residual',EW,category='official_equal_weight')]
    if clock in ('09:25','10:20') and (target in ('r30','regular_residual','remaining_vol','remaining_range','remaining_5','remaining_21')):
        controls.extend([
          Arm('previous_foreign_residual',GLOBAL,category='international'),
          Arm('announcements_residual',NEWS,category='announcements'),
          Arm('stock_orthogonal',STOCK,'orthogonal',category='stock_breadth'),
          Arm('surprise_orthogonal',SURPRISE,'orthogonal',category='opening_surprise'),
          Arm('stock_delay1',STOCK,'delay',category='stock_falsification'),
          Arm('stock_clock_delay',tuple('earlier_'+z for z in STOCK),'residual',category='stock_falsification'),
          Arm('stock_block_shuffle',STOCK,'shuffle',category='stock_falsification'),
          Arm('residual_label_shuffle',STOCK,'label_mix',category='stock_falsification'),
          Arm('stock_without_heavy',ALTS[4:6],category='stock_falsification'),
          Arm('stock_random_subset1',ALTS[:2],category='stock_falsification'),
          Arm('stock_random_subset2',ALTS[2:4],category='stock_falsification'),
          Arm('action_screen_stock',ALTS[6:],category='stock_falsification'),
          Arm('proxy_open_surprise',('proxy_surprise_z','pred_gap_std'),'residual',category='opening_surprise'),
          Arm('surprise_delayed',SURPRISE,'delay',category='surprise_falsification'),
          Arm('joint_stock_native',STOCK+STANDARD+FIN+LIQ,'direct',parent='native_control',category='stock_breadth'),
          Arm('participation_term',('surprise_x_breadth','surprise_x_finance','open_surprise_z','stock_above_open','financial_lead'),
              'residual',category='opening_surprise'),
          Arm('training_month_removed',STOCK,'trim',category='stock_falsification')])
    return a+controls


class Engine:
    def __init__(self,f,y,cutoff):
        self.f=f.sort_index()
        self.y=y.reindex(self.f.index)
        self.dates=self.f.index.to_numpy()
        self.clock=cutoff
        self.atoms=[];self.fits=[];self.rows=[];self.visibility=[]
        self.matrix={}

    def array(self,cols):
        if cols not in self.matrix:
            self.matrix[cols]=self.f.reindex(columns=list(cols)).to_numpy(float)
        return self.matrix[cols]

    def base_history(self,y,end,features,scalar=False):
        sample=self.array(features)
        pred=np.full(len(y),np.nan)
        sp=np.full(len(y),np.nan)
        for i in range(len(y)):
            train=prior_idx(self.dates,end,y,i)
            if len(train)<MIN:continue
            lhs=y[train]
            mod=fit(sample[train],lhs,140)
            fitted=mod.values(sample[i])
            mid=np.median(lhs)
            dev=max(.00025,float(np.std(lhs)))
            pred[i]=float(np.clip(.65*fitted+.35*mid,mid-1.75*dev,mid+1.75*dev))
            if scalar:pred[i]=max(0,pred[i])
            sp[i]=dev
        return pred,sp

    def binary(self,k,end,y,arms):
        C=self.y.cohort.fillna('').to_numpy()
        for arm in arms:
            var=self.array(BASE if arm.kind=='binary' else arm.features)
            if arm.kind=='binary':
                b=self.array(arm.features)
                var=np.column_stack((var,b))
            for i in np.flatnonzero((C!='')&np.isfinite(y)):
                t=prior_idx(self.dates,end,y,i)
                if len(t)<MIN:continue
                h=y[t]
                base=(h.sum()+.75)/(len(h)+1.5)
                fit_row=None
                if var.shape[1]:
                    fit_row=logistic_offset(var[t],h,base,140.)
                    p=float(predict_probability(fit_row,var[i],base,.68))
                else:p=float(base)
                s=dict(actual=y[i],p=p,brier=(p-y[i])**2,log_loss=-np.log(p if y[i] else 1-p),correct=int((p>=.5)==y[i]),
                    crps=(p-y[i])**2,mean=p,median=float(p>=.5),sq_error=(p-y[i])**2,abs_error=abs(y[i]-.5),width=np.nan,
                    interval_score=np.nan,covered=np.nan,qlike=np.nan,rank_error=np.nan,quantile_loss=np.nan)
                self.append(k,arm,s,np.where(Q>1-p,1.,0.),i,t,end,None)
                if fit_row is not None and arm.kind=='binary':
                    self.fits.append(dict(law=self.rows[-1]['law'],logistic_parameters=fit_row[1].tolist(),
                                      **fit_row[0].receipt((*BASE,*arm.features))))

    def append(self,k,arm,s,law,i,t,end,fit_row=None,cols=None):
        nn=len(self.atoms)
        day=self.dates[i]
        self.rows.append(dict(law=nn,day=day,origin=self.y.origin.iloc[i],cutoff=self.clock,target=k,category=arm.category,
                          model=arm.name,baseline=arm.parent,cohort=self.y.cohort.iloc[i],target_end=end[i],
                          last_mature=max(end[t].tolist()),n_train=len(t),**s))
        self.atoms.append(law.astype('float32'))
        if fit_row is not None:
            self.fits.append(dict(law=nn,**fit_row.receipt(cols)))

    def run(self,k):
        y=self.y[k].to_numpy(float)
        ends=np.asarray(self.y['end_'+k].fillna('9999-12-31')).astype(str)
        scalar=k in RISK_TARGETS
        arms=setups(self.clock,k)
        if k in BIN_TARGETS:
            return self.binary(k,ends,y,arms)
        baseline,vol=self.base_history(y,ends,BASE,scalar)
        residual=y-baseline
        c=self.y.cohort.fillna('').to_numpy()
        aud=[]
        for i in np.flatnonzero(np.isfinite(baseline)&np.isfinite(y)):
            train=prior_idx(self.dates,ends,y,i)
            aud.append(dict(day=self.dates[i],cutoff=self.clock,target=k,target_end=ends[i],baseline_expected=baseline[i],
                            target_scale=vol[i],realized=y[i],residual=residual[i],latest_matured=max(ends[train].tolist())))
        self.visibility.extend(aud)
        for arm in arms:
            fs=arm.features
            v=self.array(fs)
            predictor=np.ones(len(y),bool)
            is_base=arm.kind in ('base','neutral','history')
            if arm.kind=='delay':
                v=pd.DataFrame(v).shift(1).to_numpy(float)
            if arm.kind=='orthogonal':
                v=standardize_raw_features(v,self.array(BASE),self.dates)
            if not is_base and arm.kind!='base_error':
                predictor=np.isfinite(v).any(axis=1)
                if arm.category in {'opening_surprise','surprise_falsification'}:
                    predictor&=np.isfinite(self.f.open_surprise_z.to_numpy())
                if arm.category.startswith('stock') or arm.category in ('financial_participation','volume_liquidity','sector_adjusted_stock'):
                    predictor&=(self.f.stock_n.to_numpy()>=14)
            if arm.kind=='direct':
                fs=tuple(dict.fromkeys((*BASE,*fs)))
                v=self.array(fs)
            for i in np.flatnonzero((c!='')&np.isfinite(y)&predictor):
                tr=prior_idx(self.dates,ends,y,i)
                if len(tr)<MIN:continue
                centered=y[tr]-np.median(y[tr])
                fit_row=None
                if is_base:
                    if arm.kind=='neutral':
                        law=np.quantile(np.r_[-abs(y[tr]),abs(y[tr])],Q) if not scalar else np.quantile(y[tr],Q)
                    elif arm.kind=='history':
                        law=np.quantile(y[tr],Q)
                    elif arm.name=='native_control':
                        law=baseline[i]+np.quantile(centered,Q)
                    else:
                        fit_row=fit(v[tr],y[tr],140)
                        law=(.65*fit_row.values(v[i])+.35*np.median(y[tr]))+np.quantile(centered,Q)
                elif arm.kind=='direct':
                    fit_row=fit(v[tr],y[tr],145)
                    law=.70*fit_row.values(v[i])+.30*np.median(y[tr])+np.quantile(centered,Q)
                else:
                    tt=prior_idx(self.dates,ends,residual,i,predictor&np.isfinite(vol),limit=140)
                    if len(tt)<38 or not np.isfinite(baseline[i]):continue
                    tr=tt
                    r=residual[tt]
                    u=r/np.maximum(vol[tt],.00025)
                    common=prior_idx(self.dates,ends,residual,i,np.isfinite(vol),limit=140)
                    u_common=residual[common]/np.maximum(vol[common],.00025)
                    shape=np.quantile(u_common-np.median(u_common),Q)*vol[i]
                    loc=0.
                    if arm.kind!='base_error':
                        aa=v[tt]
                        yy=u.copy()
                        rng=None; m=None
                        if arm.kind=='trim':
                            remove=self.dates[tt[len(tt)//2]][:7]
                            t2=~np.char.startswith(self.dates[tt].astype(str),remove)
                            aa=aa[t2];yy=yy[t2]
                        if arm.kind=='shuffle':
                            rng=np.random.default_rng(SEED+i)
                            m=np.ones(len(fs),bool)
                        if arm.kind=='label_mix':
                            g=np.random.default_rng(SEED+7*i)
                            fx=np.array_split(np.arange(len(yy)),max(2,len(yy)//9))
                            yy=yy[np.concatenate([fx[j] for j in g.permutation(len(fx))])]
                        fit_row=fit(aa,yy,170.,rng,m)
                        loc=float(np.clip(.50*fit_row.values(v[i]),-.65,.65)*vol[i])
                    law=baseline[i]+loc+shape
                if scalar:
                    law=np.maximum(law,.00001)
                v0=score(law,y[i],arithmetic=not scalar)
                if scalar:
                    ratio=(y[i]/max(float(law.mean()),1.e-5))**2
                    v0['qlike']=ratio-np.log(max(ratio,1.e-8))-1
                    for cs in ('brier','log_loss','correct'):v0[cs]=np.nan
                else:
                    v0['qlike']=np.nan
                    if arm.kind=='neutral':
                        v0.update(p=.50,brier=.25,log_loss=np.log(2),correct=int(y[i]>0))
                self.append(k,arm,v0,law,i,tr,ends,fit_row,fs)

    def save(self,name):
        d=pd.DataFrame(self.rows)
        assert d.last_mature.lt(d.day).all()
        assert not d.duplicated(['day','cutoff','target','model']).any()
        write(name+'-scores.csv.gz',d)
        write(name+'-baseline-residual-ledger.csv.gz',pd.DataFrame(self.visibility))
        np.savez_compressed(OUT/(name+'-laws.npz'),atoms=np.stack(self.atoms),units='Log return, absolute log risk, or Bernoulli depending on target')
        with gzip.open(OUT/(name+'-fit-receipt.ndjson.gz'),'wt',encoding='utf-8',compresslevel=3) as z:
            for row in self.fits:
                z.write(json.dumps(row,allow_nan=False,separators=(',',':'))+'\n')
        print(name,len(d),'distributions',flush=True)

def run():
    f=pd.read_csv(OUT/'intraday-feature-panel.csv.gz',low_memory=False)
    y=pd.read_csv(OUT/'intraday-target-panel.csv.gz',low_memory=False)
    previous=f.groupby('day')[list(STOCK)].shift(1).add_prefix('earlier_')
    f=f.join(previous)
    for clock in SESSION_CLOCKS:
        a=f[f.cutoff.eq(clock)].set_index('day')
        t=y[y.cutoff.eq(clock)].set_index('day')
        e=Engine(a,t,clock)
        target=['r15','r30','r60','regular_residual','next_session','remaining_3','remaining_5','remaining_10','remaining_21',
                'remaining_range','remaining_vol','abs_regular','touch_up','touch_down'] if clock in ('09:25','10:20') else [
                'r30','regular_residual','remaining_vol','remaining_range']
        if clock=='15:00':
            target=['r15','regular_residual','remaining_vol','remaining_range']
        for k in target:
            if k in t and t[k].notna().sum()>=90:
                e.run(k)
        e.save('residual-'+clock.replace(':',''))

if __name__=='__main__':
    run()
