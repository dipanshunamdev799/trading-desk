"""Paired session deltas and cross-vintage endpoint comparisons."""
from .common import *
from .evidence import paired_intervals


def sessions():
    s=pd.read_csv(OUT/'session-forecasts.csv.gz')
    p=pd.read_csv(OUT/'session-evidence.csv',usecols=['checkpoint','target','model','parent'])
    rows=[]
    for stage,task in p[['checkpoint','target']].drop_duplicates().itertuples(index=False):
        take=s[s.cutoff.eq(stage)&s.target_name.eq(task)]
        idx=pd.Index(take.day.unique()).sort_values()
        sub=p[p.checkpoint.eq(stage)&p.target.eq(task)]
        info=[]; gains=[]
        for x in sub.itertuples(index=False):
            a=take[take.model.eq(x.model)].set_index('day')
            b=take[take.model.eq(x.parent)].set_index('day')
            a,b=a.align(b,join='inner',axis=0)
            if len(a)<35:
                continue
            for m in ('crps','brier','log_loss'):
                v=b[m]-a[m]
                gains.append(v.reindex(idx).to_numpy())
                c=dict(checkpoint=stage,target=task,model=x.model,parent=x.parent,metric=m,n=len(a),
                       distinct_targets=a.target.nunique(),gain=v.mean(),score=a[m].mean(),parent_score=b[m].mean())
                for f in ('early','later'):
                    z=v[a.cohort.eq(f)]
                    c[f+'_n']=len(z)
                    c[f+'_gain']=z.mean()
                info.append(c)
        if info:
            q=paired_intervals(np.column_stack(gains),5,np.array([x['metric'] for x in info]))
            for i,x in enumerate(info):
                x.update({k:v[i] for k,v in q.items()})
            rows.extend(info)
    write('session-dependence-evidence.csv',pd.DataFrame(rows))


def cross_vintages():
    a=pd.read_csv(OUT/'sequential-scores.csv.gz',usecols=['horizon','origin','checkpoint','model','p_up','brier','log_loss',
        'endpoint_crps','endpoint_pinball','endpoint_mae','endpoint_cov50','endpoint_cov80','endpoint_width80','endpoint'])
    a=a[a.checkpoint.eq(0)].drop(columns='checkpoint')
    ref=pd.read_csv(OUT/'earlier-endpoint-references.csv.gz')
    ref=ref.rename(columns={'p':'p_up','actual':'endpoint','crps':'endpoint_crps','pinball':'endpoint_pinball','mae':'endpoint_mae',
                            'coverage50':'endpoint_cov50','coverage80':'endpoint_cov80','width80':'endpoint_width80'})
    old=pd.read_csv(V14/'path-marginals.csv.gz',usecols=['horizon','origin','model','target','actual','p_up','brier','crps',
        'log_loss','pinball','mae','coverage50','coverage80','width80'])
    old=old[old.horizon.eq(21)&old.model.eq('regime_state')&old.target.eq('endpoint_return')].copy()
    old['model']='V14_regime_state_joint'
    old=old.rename(columns={'actual':'endpoint','crps':'endpoint_crps','pinball':'endpoint_pinball','mae':'endpoint_mae',
                           'coverage50':'endpoint_cov50','coverage80':'endpoint_cov80','width80':'endpoint_width80'})
    ref=pd.concat([ref,old],ignore_index=True)
    ref=ref[[n for n in a.columns if n in ref]]
    ref=ref.sort_values(['horizon','origin','model']).drop_duplicates(['horizon','origin','model'])
    a['version']='V15 joint laws'
    ref['version']='Protected reference systems'
    aligned=pd.concat([a,ref],ignore_index=True)
    r=a[a.model.eq('iv_restart')][['horizon','origin','brier','endpoint_crps','log_loss']]
    z=aligned.merge(r,on=['horizon','origin'],validate='many_to_one',suffixes=('','_raw_iv'))
    z['truth']=z.endpoint.gt(0).astype(int)
    z['correct']=(z.p_up.ge(.5)==z.truth).astype(int)
    z['tp']=z.correct.where(z.truth.eq(1))
    z['tn']=z.correct.where(z.truth.eq(0))
    for n in ('brier','endpoint_crps','log_loss'):
        z['gain_'+n]=z[n+'_raw_iv']-z[n]
    fields=list(z.select_dtypes(include='number').columns.difference(['horizon','truth','tp','tn','endpoint']))
    u=z.groupby(['horizon','version','model'],as_index=False).agg(origins=('origin','nunique'),
        tpr=('tp','mean'),tnr=('tn','mean'),**{n:(n,'mean') for n in fields})
    u['balanced_accuracy']=(u.tpr+u.tnr)/2
    write('cross-vintage-endpoint-leaderboard.csv',u)
    comparisons=[]
    for h in HORIZONS:
        pool=z[z.horizon.eq(h)]
        for mm in ('brier','endpoint_crps','log_loss'):
            w=pool.pivot(index='origin',columns='model',values='gain_'+mm).sort_index()
            good=w.count().ge(35)
            w=w.loc[:,good]
            dat=paired_intervals(w.to_numpy(),h)
            for i,name in enumerate(w.columns):
                comparisons.append(dict(horizon=h,metric=mm,model=name,n=w[name].count(),gain=w[name].mean(),
                                        **{k:v[i] for k,v in dat.items()}))
    write('cross-vintage-matched-uncertainty.csv',pd.DataFrame(comparisons))


if __name__=='__main__':
    sessions()
    cross_vintages()
