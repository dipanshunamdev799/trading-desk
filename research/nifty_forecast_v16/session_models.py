"""Advanced opening-gap models, timing decay, pre/post-absorption and network channels."""
from dataclasses import dataclass

from .common import *
from .data import DOM, CLOSE6, GLOBAL, MORNING, SETS, US, EU, ASIA
from .model import Q, fit, history, law, quantify

FRESH=(DOM+('eq6',))
POST=DOM+('gap_visible','cash_first_bar','cash_prefix','cash_prefix_rv','cash_first_hour')
BREADTH=POST+('open_breadth','open_bank_lead','open_tech_lead','open_dispersion','open_defensive','etf_relative','etf_volume')
ASIA_FRESH=('nikkei_partial','hsi_partial')
ADVANCED=DOM+SETS['global_extended']
NETWORK={
    'it_gap':('tech','tech_lead','fx','spx','fx_intraday'),
    'bank_gap':('spx','dow','tech_lead','dgs10_change','vix_move','fx'),
    'energy_gap':('brent','wti','brent_intraday','spx','oil_diverge'),
    'broad_gap':('nikkei','hsi','nikkei_partial','hsi_partial','cross_sign'),
    'bank_relative':('dow','tech_lead','vix_move','dgs10_change','spx'),
    'it_relative':('tech','tech_lead','fx','fx_intraday'),
    'energy_relative':('brent','wti','oil_diverge','brent_intraday'),
    'session_risk':('vix_move','vix_us','foreign_sd','cross_sign','fx_intraday','brent_intraday'),
}
NLINEAR=('eq6_signed_square','vix_abs_equity','us_asia_product','risk_absolute','oil_abs','triple_sign')
DTARGETS=('gap','regular','firsthour','remaining','one','next_gap','next_next_close','two','three','five','ten','twentyone')
PORTIONS=('us','europe','asia')

@dataclass
class Spec:
    name: str
    cols: tuple=()
    style: str='ridge'
    required: str|None=None
    control: str='domestic'
    group: str='candidate'
    penalty: float=95


def prepare(y,x):
    b=x.copy()
    b['eq6_signed_square']=np.clip(b.eq6,-.04,.04)*abs(b.eq6)
    b['vix_abs_equity']=abs(b.eq6)*b.vix_move
    b['us_asia_product']=b.us_mean*b.asia_mean
    b['risk_absolute']=abs(b.vix_move)
    b['oil_abs']=abs(b.oil_diverge)
    b['triple_sign']=np.sign(b.us_mean)+np.sign(b.europe_mean)+np.sign(b.asia_mean)
    for lag in [1,2,5,17]:
        for k in ['eq6','us_mean','europe_mean','asia_mean']:
            b[f'{k}_lag{lag}']=b[k].shift(lag)
    b['eq6_smooth']=b.eq6.rolling(3,min_periods=3).mean()
    b['gift_one_lag']=b.gift_proxy.shift(1)
    rng=np.random.default_rng(SEED+int(b.cutoff.iloc[0].replace(':','')))
    for name in CLOSE6:
        b['noise_'+name]=rng.standard_normal(len(b))*0.008
    b['gap_sign']=np.sign(b.gap_visible)
    b['gap_abs']=abs(b.gap_visible)
    b['fit_block']=[pd.Timestamp(d).toordinal()//5 for d in b.index]
    return b


def network_predictions(z,labels):
    data=z.copy()
    vars0=[]
    issu=labels.index.to_numpy()
    for target,fs in list(NETWORK.items())[:4]:
        y=labels[target].to_numpy(float)
        end=np.asarray(labels['label_'+target].fillna('9999-12-31')).astype(str)
        a=data.reindex(columns=fs).to_numpy(float)
        result=np.full(len(y),np.nan)
        for i in range(len(y)):
            train=history(issu,end,y,i)
            if len(train)>=54:
                f=fit(a[train],y[train],80)
                result[i]=.70*f.values(a[i])
        name='learned_'+target
        data[name]=result
        vars0.append(name)
    return data,tuple(vars0)


def opening_specs(extended=True):
    simple=[Spec('neutral',style='neutral',control='historical',group='baseline'),
            Spec('historical',style='historical',control='neutral',group='baseline'),
            Spec('prior_return',SETS['prior_return'],control='historical',group='baseline'),
            Spec('domestic',DOM,control='historical',group='baseline'),
            Spec('V15_style_parent',SETS['offshore_prior'],control='domestic',group='baseline'),
            Spec('single_US',SETS['us_single'],control='historical',group='baseline'),
            Spec('equal_six',SETS['global_equal'],control='domestic',group='baseline'),
            Spec('domestic_equal',FRESH,control='domestic',group='factors'),
            Spec('six_cash',DOM+CLOSE6,control='domestic_equal',group='factors'),
            Spec('gift_raw',('gift_proxy',),style='gift_raw',required='gift_proxy',control='equal_six',group='gift'),
            Spec('gift_calibrated',('gift_proxy',),style='gift_calibrated',required='gift_proxy',control='gift_raw',group='gift'),
            Spec('gift_roll_screened',('gift_proxy',),style='gift_raw',required='gift_no_roll',control='gift_raw',group='gift'),
            Spec('gift_delay10',('gift_delay_minutes_10',),style='gift_raw',required='gift_delay_minutes_10',control='gift_raw',group='gift'),
            Spec('gift_delay25',('gift_delay_minutes_25',),style='gift_raw',required='gift_delay_minutes_25',control='gift_raw',group='gift'),
            Spec('gift_daily_lag',('gift_day',),control='equal_six',group='gift'),
            Spec('gift_plus_global',('gift_proxy',*CLOSE6,*ASIA_FRESH),style='gift_plus',required='gift_proxy',control='gift_calibrated',group='gift'),
            Spec('gift_disagreement',('gift_proxy','cash_vs_gift','foreign_sd','us_asia','tech_lead'),style='gift_plus',required='gift_proxy',control='gift_calibrated',group='gift'),
            Spec('asia_partial',FRESH+ASIA_FRESH,control='domestic_equal',group='factors')]
    if not extended:
        return simple
    more=[Spec('rich_global_ridge',ADVANCED,control='six_cash',group='factors',penalty=130),
          Spec('student_location_scale',FRESH+SETS['global_only'],style='student',control='domestic_equal',group='distribution'),
          Spec('sign_magnitude',ADVANCED,style='logistic_magnitude',control='domestic_equal',group='distribution'),
          Spec('cluster_balanced',DOM+CLOSE6,style='cluster',control='six_cash',group='factors'),
          Spec('shallow_interactions',FRESH+SETS['global_only']+NLINEAR,control='domestic_equal',group='factors',penalty=160),
          Spec('disagreement',FRESH+tuple(k for k in SETS['disagreement'] if k!='cash_vs_gift'),control='domestic_equal',group='disagreement'),
          Spec('shuffled_foreign',DOM+CLOSE6,style='permuted',control='six_cash',group='placebo'),
          Spec('noisy_foreign',DOM+tuple('noise_'+k for k in CLOSE6),control='six_cash',group='placebo')]
    more += [Spec('without_'+k,DOM+tuple(j for j in CLOSE6 if j!=k),control='six_cash',group='deletion') for k in CLOSE6]
    return simple+more


def decay_specs(post=False):
    dom=POST if post else DOM
    parent='cash_prefix' if post else 'domestic'
    out=[Spec(parent,dom,control='historical',group='baseline'),Spec('historical',style='historical',control=parent,group='baseline'),
         Spec('eq_fresh',dom+('eq6',),control=parent,group='decay'),
         Spec('rich_fresh',dom+SETS['global_extended'],control='eq_fresh',group='decay'),
         Spec('disagreement',dom+('eq6',)+tuple(k for k in SETS['disagreement'] if k!='cash_vs_gift'),control='eq_fresh',group='disagreement'),
         Spec('gift_conditional',dom+('gift_proxy',),required='gift_proxy',control=parent,group='gift')]
    out.extend(Spec('eq_lag'+str(l),dom+(f'eq6_lag{l}',),control='eq_fresh',group='decay') for l in (1,2,5,17))
    out.append(Spec('eq_smooth',dom+('eq6_smooth',),control='eq_fresh',group='decay'))
    for name in PORTIONS:
        out.extend([Spec(name+'_fresh',dom+(name+'_mean',),control=parent,group='decay'),
                    Spec(name+'_stale',dom+(name+'_mean_lag2',),control=name+'_fresh',group='decay')])
    if post:
        out.extend([Spec('breadth_after_open',BREADTH,control=parent,group='absorption'),
                    Spec('gap_breadth_interaction',BREADTH+('gap_finance','gap_broad','gap_scaled'),control='breadth_after_open',group='absorption'),
                    Spec('continuation_rule',('gap_visible',),style='continuation',required='gap_visible',control=parent,group='absorption'),
                    Spec('reversal_rule',('gap_visible',),style='reversal',required='gap_visible',control=parent,group='absorption'),
                    Spec('foreign_after_gap',BREADTH+('foreign_after_gap','eq6','us_asia'),control='breadth_after_open',group='absorption')])
    return out


class Engine:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.days=x.index.to_numpy()
        self.laws=[]
        self.rows=[]
        self.params=[]
        self.zcols={}

    def run(self,track,target,specs,cohort=None,need_open=False):
        y=self.y[target].to_numpy(float)
        dates=np.asarray(self.y['label_'+target].fillna('9999-12-31')).astype(str)
        assert len(y)==len(self.days)
        cohort=self.y.cohort.to_numpy() if cohort is None else cohort
        f=lambda k:self.x[k].to_numpy(float)
        clock=self.x.cutoff.iloc[0]
        for m in specs:
            need=m.required
            if need=='gift_no_roll':
                mask=np.isfinite(f('gift_proxy'))&self.x.gift_roll_guard.eq(0).to_numpy()
            elif need:
                mask=np.isfinite(f(need))
            else:
                mask=np.ones(len(y),bool)
            if need_open:
                mask=mask & np.isfinite(f('gap_visible'))
            a=self.x.reindex(columns=m.cols).to_numpy(float)
            for i in np.flatnonzero((cohort!='')&np.isfinite(y)&mask):
                t=history(self.days,dates,y,i,mask)
                if len(t)<54:
                    continue
                h=y[t]
                features=a[i]
                fit_obj=None
                if m.style=='neutral':
                    ab=np.quantile(np.abs(h),(np.arange(80)+.5)/80)
                    atoms=np.r_[ab,-ab]
                elif m.style=='historical':
                    atoms=np.quantile(h,Q)
                elif m.style in {'continuation','reversal'}:
                    direction=1 if m.style=='continuation' else -1
                    atoms=.22*features[0]*direction+np.quantile(h-np.median(h),Q)
                elif m.style.startswith('gift_'):
                    g=a[t,0]
                    residual=h-g
                    gate=.85 if m.style=='gift_calibrated' else 0.
                    bias=gate*np.median(residual)
                    residual0=residual-np.median(residual)
                    if m.style=='gift_plus':
                        fit_obj=fit(a[t,1:],residual,135)
                        bias=.60*fit_obj.values(features[1:])
                    atoms=features[0]+bias+np.quantile(residual0,Q)
                else:
                    perm=np.isin(m.cols,CLOSE6) if m.style=='permuted' else None
                    rng=np.random.default_rng(SEED+i) if perm is not None else None
                    atoms,fit_obj=law(a[t],features,h,m.style,m.penalty,rng,perm,f('fit_block')[t].astype(int))
                if target=='session_risk':
                    atoms=np.maximum(atoms,0.)
                assert np.isfinite(atoms).all()
                s=quantify(atoms,y[i],target!='session_risk')
                if m.style=='neutral' and target!='session_risk':
                    # Exactly symmetric probability includes half of the possible tied mass at zero.
                    s.update(p_up=.5,brier=.25,log_loss=np.log(2),correct=int(y[i]>0))
                key=len(self.laws)
                self.laws.append(atoms.astype('float32'))
                self.rows.append(dict(law=key,day=self.days[i],exercise=track,cutoff=clock,cohort=cohort[i],model=m.name,
                                      baseline=m.control,target=target,target_date=dates[i],origin=self.y.origin.iloc[i],n_train=len(t),
                                      last_training_end=max(dates[t].tolist()),segment=self.y.regular_weekday.iloc[i],
                                      roll_guard=self.x.gift_roll_guard.iloc[i],family=m.group,**s))
                if fit_obj is not None:
                    n0=tuple(m.cols[1:] if m.style=='gift_plus' else m.cols)
                    self.params.append(dict(law=key,**fit_obj.receipt(n0)))

    def save(self,label):
        rows=pd.DataFrame(self.rows)
        assert (rows.last_training_end<rows.day).all()
        assert not rows.duplicated(['exercise','cutoff','day','target','model']).any()
        write(label+'-scores.csv.gz',rows)
        np.savez_compressed(OUT/(label+'-laws.npz'),atoms=np.stack(self.laws),probabilities=np.full(len(Q),1/len(Q)),
                            units=np.array('Log price ratio before scoring. session_risk is realized log intraday volatility.'))
        with gzip.open(OUT/(label+'-fits.ndjson.gz'),'wt',compresslevel=3,encoding='utf-8') as out:
            for m in self.params:
                out.write(json.dumps(m,allow_nan=False,separators=(',',':'))+'\n')
        print(label,':',len(rows),'forecast distributions',flush=True)


def load():
    a=pd.read_csv(OUT/'decision-features.csv.gz',low_memory=False)
    y=matrix('session-targets.csv').fillna({'cohort':'','cohort_five':'','cohort_twentyone':''})
    return a,y


def run(track):
    a,y=load()
    frames=[]
    for cut in (CLOCKS[:4] if track=='opening' else ('08:55','09:25','10:20','17:00')):
        x=a[a.cutoff.eq(cut)].set_index('day').reindex(y.index)
        b=prepare(y,x)
        e=Engine(b,y)
        if track=='opening':
            e.run('opening_gap','gap',opening_specs(cut in ('08:55','09:10')))
        if track=='decay':
            if cut=='17:00':
                e.run('after_close','next_gap',decay_specs(False))
                e.run('after_close','next_next_close',decay_specs(False))
            elif cut=='08:55':
                b,nets=network_predictions(b,y)
                e=Engine(b,y)
                for yd in DTARGETS:
                    cc=y['cohort_'+yd].to_numpy() if yd in ('five','twentyone') else None
                    specs=decay_specs(False)
                    if yd in ('gap','one','three','five','twentyone'):
                        specs+=[Spec('network_stack',DOM+nets,control='rich_fresh',group='network')]
                    e.run('pre_session_decay',yd,specs,cc)
                for k,fs in NETWORK.items():
                    for f0 in fs:
                        b['stale_'+f0]=b[f0].shift(2)
                    specs=[Spec('domestic',DOM,control='historical',group='baseline'),Spec('historical',style='historical',control='domestic',group='baseline'),
                           Spec('targeted_block',DOM+fs,control='domestic',group='network'),
                           Spec('global_only',fs,control='domestic',group='network'),
                           Spec('targeted_stale',DOM+tuple('stale_'+z for z in fs),control='targeted_block',group='network')]
                    e.run('sector_network',k,specs)
            else:
                ts=['regular_after_bar','firsthour_residual','next_gap','three','five'] if cut=='09:25' else ['remaining','next_gap','three','five']
                for yd in ts:
                    cohort=y.cohort_five.to_numpy() if yd=='five' else None
                    e.run('after_absorption',yd,decay_specs(True),cohort,need_open=True)
        e.save(track+'-'+cut.replace(':',''))


if __name__=='__main__':
    import sys
    run(sys.argv[1])
