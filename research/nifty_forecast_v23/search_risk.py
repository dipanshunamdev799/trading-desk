"""Recover archived search exposure and refit bounded falsification families."""
from collections import Counter
import re

from .common import *
from .forecast import past_rows,asof_features,standardize,ridge,F,MIN
from .geometry import load_bank


def records(data):
    for field in ('hypotheses','models','experiments','families','designs','mechanisms'):
        a=data.get(field)
        if isinstance(a,dict):
            return [(k,v) for k,v in a.items()]
        if isinstance(a,list):
            return [(str(v.get('name',v.get('id',i))) if isinstance(v,dict) else str(v),v) for i,v in enumerate(a)]
    return []


def registry():
    family=csv('master-model-family-registry.csv')
    cov=csv('master-archive-coverage.csv').set_index('version')
    ever=[];studies=[];leaders=[];timeline=[]
    for v in range(1,23):
        root=root_for(v)
        if v<=2:
            root=ROOT/'artifacts/nifty_forecast/2026-11-17'
        reports=sorted(root.glob(f'NIFTY_V{v}_RESEARCH.md'))
        if (ROOT/f'NIFTY_V{v}_RESEARCH.md').is_file():
            reports.append(ROOT/f'NIFTY_V{v}_RESEARCH.md')
        if v<=2:
            reports=[ROOT/('NIFTY_FORECAST_2026-11-17.md' if v==1 else 'NIFTY_WEEK_MONTH_2026-11-17.md')]
        counts=Counter()
        for f in sorted(root.glob('*.json')):
            if 'registry' not in f.name and 'registration' not in f.name:
                continue
            a=read(f.name,root)
            if not isinstance(a,dict):
                continue
            for label,value in records(a):
                counts[f.name]+=1
                ever.append(dict(version=v,registry=f.relative_to(ROOT).as_posix(),name=label,
                     record=json.dumps(value,ensure_ascii=False,default=str),file_sha256=sha(f)))
        for f in sorted(root.glob('*.csv')):
            if not re.search('leaderboard|comparison|headline-results|failur|episode',f.name) or f.stat().st_size>900000:
                continue
            g=pd.read_csv(f,low_memory=False)
            metric=next((k for k in ('brier','crps','endpoint_crps','range_crps','mae','qlike','log_loss') if k in g),None)
            mod=next((k for k in ('model','candidate','method','configuration') if k in g),None)
            if metric and mod:
                g=g.assign(val=pd.to_numeric(g[metric],errors='coerce')).dropna(subset=['val'])
                keys=[k for k in ('horizon','cohort','scope','cutoff','track','target') if k in g]
                pick=g.sort_values('val').groupby(keys,dropna=False).head(1) if keys else g.nsmallest(1,'val')
                for r in pick.itertuples(index=False):
                    leaders.append(dict(version=v,source=f.relative_to(ROOT).as_posix(),metric=metric,model=getattr(r,mod),
                                     score=r.val,context=' | '.join(f'{key}={getattr(r,key)}' for key in keys)))
            if 'episode' in f.name:
                for k in ('day','omitted','episode','start','end','date'):
                    if k not in g:
                        continue
                    found=Counter(y[:7] for x in g[k].astype(str) for y in re.findall(r'202[56]-[0-9]{2}-[0-9]{2}', x))
                    for month,n in found.items():
                        timeline.append(dict(version=v,month=month,source=f.relative_to(ROOT).as_posix(),mentions=n,kind='archived episode diagnostic'))
        f0=family[family.version.eq(v)]
        studies.append(dict(version=v,files_in_catalog=int(cov.loc[v,'inventoried_files']),records_in_registry=sum(counts.values()),
              registry_files=len(counts),unique_version_model_ids=len(f0),known_law_ids=int((f0.law_pointers>0).sum()),
              date_case_rows=int(cov.loc[v,'case_rows']),law_linked_rows=int(cov.loc[v,'archived_law_links']),
              has_main_report=bool(reports),primary_sources=' | '.join(p.relative_to(ROOT).as_posix() for p in reports)))
    o=csv('india-episode-omission.csv.gz',V22)
    for val,n in o[o.type.str.startswith('largest')].omitted.value_counts().items():
        for month in set(t[:7] for t in re.findall(r'202[56]-[0-9]{2}-[0-9]{2}',val)):
            timeline.append(dict(version=22,month=month,source='V22 india-episode-omission.csv.gz',mentions=n,kind='largest-block diagnostic'))
    write('cumulative-version-coverage.csv',pd.DataFrame(studies))
    write('cumulative-recovered-registrations.csv.gz',pd.DataFrame(ever))
    write('cumulative-reported-leaders.csv.gz',pd.DataFrame(leaders))
    write('cumulative-historical-episode-exposure.csv.gz',pd.DataFrame(timeline))
    records_with_link=int((family.law_pointers>0).sum())
    summary=dict(versions=22,observed_version_model_ids=len(family),ids_with_a_law_pointer=records_with_link,
              share_of_observed_ids_with_case_law_pointer=records_with_link/len(family),
              registered_records_discovered=len(ever),registry_bearing_versions=sum(s['registry_files']>0 for s in studies),
              indexed_leader_rows=len(leaders),true_search_denominator='unknown; some variants and discretionary choices have no retained receipt',
              coverage_denominator='Recovered IDs are neither mechanism count nor all historical trials. Archived names can represent duplicate fits and repeated exposures.')
    save('cumulative-search-coverage.json',summary)


def regime_null():
    all_x=csv('v23-return-cases.csv.gz')
    experts,_=load_bank()
    out=[]
    spec=[['prior_ret5','trailing_vol','iv_prev'],['reaction_mean','count9','allEQ_advance','domestic_rotation_finance'],
          ['FII_index_futures_d21','index_futures_detail_hhi_z','prior_ret21'],['gift_proxy','expected_gap','vix_level','foreign_sd']]
    for h in HORIZONS:
        f=all_x[all_x.horizon.eq(h)&all_x.clock.eq('native_0910')]
        p=f[f.model.eq('protected_direction')].set_index('day').sort_index()
        dates=p.index.to_numpy()
        x=asof_features(dates,'native_0910')
        yy=p.actual.gt(0).to_numpy()
        eps=yy-p.p.to_numpy()
        prob=p.p.to_numpy()
        loss=(prob-yy)**2
        choice=p.issue_ns.to_numpy();mature=p.mature_ns.to_numpy()
        ixs=[past_rows(mature,choice,int(d)) for d in choice]
        on=np.array([len(a)>=MIN for a in ixs])
        n=len(p)
        e=experts[experts.horizon.eq(h)&experts.clock.eq('native_0910')]
        e=e.pivot(index='day',columns='expert',values='p').reindex(p.index).to_numpy()
        cand=f.pivot(index='day',columns='model',values='p').reindex(p.index)
        for scenario in ('observed','blocked_residuals','persistent_random_features','random_fixed_expert_weights'):
            reps=1 if scenario=='observed' else 39
            for j in range(reps):
                rng=np.random.default_rng(SEED+h+235*j+19*len(scenario))
                arms={}
                if scenario=='random_fixed_expert_weights':
                    for k in range(8):
                        w=rng.dirichlet(np.full(e.shape[1],.70))
                        arms[f'prior_mix_{k}']=.72*prob+.28*(e@w)
                else:
                    for k,fields in enumerate(spec):
                        a=x[:,[F.index(t) for t in fields]].copy()
                        if scenario=='persistent_random_features':
                            a=rng.standard_normal(a.shape)
                            for i in range(1,len(a)):
                                a[i]=.75*a[i-1]+.6614*a[i]
                        v=prob.copy()
                        for i in np.flatnonzero(on):
                            t=ixs[i]
                            y=eps[t]
                            if scenario=='blocked_residuals':
                                blocks=np.array_split(np.arange(len(t)),max(3,len(t)//8))
                                order=np.concatenate([blocks[b] for b in rng.permutation(len(blocks))])
                                y=y[order]
                            tr,point=standardize(a[t],a[i])
                            fitted=ridge(tr,y,np.ones(len(t)),1.7)
                            v[i]=np.clip(prob[i]+.52*point@fitted,.02,.98)
                        arms[f'chronological_residual_{k}']=v
                    if scenario=='observed':
                        for chosen in ('equal_families','agg_loss_mean','agg_loss_robust','component_coherent_joint'):
                            arms[chosen]=cand[chosen].to_numpy()
                    else:
                        # Include bounded null weights in each refit family, with matched total variant count.
                        for k in range(4):
                            w=rng.dirichlet(np.full(e.shape[1],.70))
                            arms[f'fixed_control_mix_{k}']=.72*prob+.28*(e@w)
                gains={name:float((loss[on]-(a[on]-yy[on])**2).mean()) for name,a in arms.items()}
                win=max(gains,key=gains.get)
                for k,v in gains.items():
                    out.append(dict(horizon=h,experiment=scenario,replicate=j,model=k,selected=k==win,n_active=int(on.sum()),mean_brier_gain=v))
    f=pd.DataFrame(out)
    write('bounded-refit-reselection-cases.csv.gz',f)
    active=f[f.selected]
    obs=active[active.experiment.eq('observed')].set_index('horizon')
    rows=[]
    for (h,exp),g in active[active.experiment.ne('observed')].groupby(['horizon','experiment']):
        p=obs.loc[h]
        r=g.mean_brier_gain
        rows.append(dict(horizon=h,experiment=exp,n_draws=len(r),observed_model=p.model,n_active=int(p.n_active),observed_gain=p.mean_brier_gain,
                         null_median=r.median(),null_p95=r.quantile(.95),fraction_positive=float(r.gt(0).mean()),
                         tail_fraction=(1+int(r.ge(p.mean_brier_gain).sum()))/(1+len(r))))
    write('bounded-refit-reselection-summary.csv',pd.DataFrame(rows))
    save('bounded-refit-reselection-method.json',dict(horizons=HORIZONS,refitted_draws=39,primary_loss='Brier',arms_reselected=8,
       weight_control='Fixed random weights on existing honest expert probability forecasts. The averaged probability is the sign mass of an actual linear pool.',
       blocked_control='Only completely matured labels shuffled in training blocks. Test features preserved.',
       scope='Representative refit and selection exercise, no estimate of full V1–V23 adaptive search bias.'))


if __name__=='__main__':
    registry()
    regime_null()
