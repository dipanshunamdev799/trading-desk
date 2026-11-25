"""Replay the protected V19 laws and audit when their inputs became available."""
from collections import defaultdict
from .common import *
from research.nifty_forecast_v19 import forecast as v19
from research.nifty_forecast_v19.evidence import disjoint
from research.nifty_forecast_v18 import forecast as v18
from research.nifty_forecast_v17.weekly import evaluate,load_legacy

METRICS=('p','brier','crps','mean','median','log_loss')

def protect():
    m=read('manifest.json',V19)
    for root,key in [(V19,'files'),(ROOT,'source_files')]:
        for row in m[key]:
            assert sha(root/row['file'])==row['sha256'],row['file']
    names=[(V19/'NIFTY_V19_RESEARCH.md'),*sorted(V19.glob('V19_*.md')),*(ROOT/x['file'] for x in m['source_files'])]
    assert len(list(V19.glob('V19_*.md')))==18
    docs=[]
    for p in names:
        body=p.read_text(encoding='utf-8-sig')
        docs.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),lines=len(body.splitlines()),
                         headings=[s.strip('# ').strip() for s in body.splitlines() if s.startswith('#')][:18]))
    save('predecessor-inventory.json',dict(v19_manifest=sha(V19/'manifest.json'),artifacts=len(m['files']),
        source_files=len(m['source_files']),chain=read('predecessor-protection.json',V19),documents=docs))
    print('Verified all',len(m['files']),'V19 artifacts and inherited code hashes',flush=True)

def archive(name):
    f=np.load(V19/name,allow_pickle=False)
    return f['atoms'],f['weights'],f['offsets']

def use(book,i):
    a,w,o=book
    return a[o[i]:o[i+1]],w[o[i]:o[i+1]]

def metric_diff(target,observed):
    return max(abs(observed[k]-target[k]) for k in METRICS)

def replay():
    u=csv('asof-positioning-features.csv.gz',V19)
    cmp=csv('native-residual-cases.csv.gz',V19).set_index(['horizon','day','model'])
    checks=csv('native-mechanism-cases.csv.gz',V19).set_index(['horizon','day','model'])
    v19books=archive('native-residual-laws.npz')
    mech=archive('native-mechanism-laws.npz')
    native=load_legacy()
    assert '09:10' in read('registration.json',V14)['reference']
    out=[];vintages=[];null=defaultdict(list);err=[]
    for h in HORIZONS:
        f,y=v19.book_panel('preauction_0855',h,u)
        earlier,_=v19.book_panel('previous_1700',h,u)
        day=f.index.to_numpy()
        issue=f.decision.str[:10].to_numpy()
        end=y[f'end_original{h}'].fillna('9999-12-31').to_numpy()
        r=y[f'original{h}'].to_numpy(float)
        keep=np.flatnonzero(y[f'cohort_{h}'].notna())
        parent={'V14_exact':np.full(len(f),np.nan),'V14_event_overlay':np.full(len(f),np.nan)}
        x=v19.matrix(f,v19.POSITION+v19.INNOV)
        lag={k:v19.matrix(f,[p+f'_delay{k}' for p in v19.POSITION+v19.INNOV]) for k in (1,5)}
        corp=v19.matrix(f,v18.FUND+v18.COUNT)
        cover=v19.coverage(f)['innovation']
        opt=csv(f'features-{h}.csv',V14,usecols=['day','option_day']).set_index('day')
        for i in keep:
            ori=y.origin.iloc[i]
            tgt,a,w=native[h,ori]
            assert tgt==end[i]
            parent['V14_exact'][i]=r[i]-np.log1p(w@a)
        for i in keep:
            info=f.decision.iloc[i]
            actual_issue=f'{day[i]}T09:10:00+05:30'
            available=f.source_release.iloc[i]
            raw_day=f.source_day.iloc[i]
            assert available<=info<actual_issue and raw_day==y.origin.iloc[i]
            assert opt.at[raw_day,'option_day']<raw_day
            for entry in ('last_announcement','last_known_report','last_known_reaction'):
                t=f[entry].iloc[i]
                assert pd.isna(t) or t<=info[:19].replace('T',' ')
            assert earlier.source_release.iloc[i]<=earlier.decision.iloc[i]
            vintages.append(dict(horizon=h,day=day[i],origin=raw_day,outcome_end=end[i],parent_decision=actual_issue,
                input_snapshot=info,participant_guard=available,previous_evening=earlier.decision.iloc[i],
                previous_evening_latest_source_day=earlier.source_day.iloc[i],option_day=opt.at[raw_day,'option_day'],
                last_announcement=f.last_announcement.iloc[i],last_financial=f.last_known_report.iloc[i],
                last_reaction=f.last_known_reaction.iloc[i]))
            tr=v19.matured(day,end,r,i,issue)
            assert len(tr)>38 and (end[tr]<issue[i]).all()
            ts=v19.filtered(tr,i,cover)
            _,a,w=native[h,raw_day]
            d18,fit18,_=v18.fit_shift(corp,parent['V14_exact'],i,tr,limit=.012)
            a18=(1+a)*np.exp(d18)-1
            parent['V14_event_overlay'][i]=r[i]-np.log1p(w@a18)
            cap=.009 if h==5 else .012
            delta,model,past=v19.shift(x,parent['V14_exact'],i,ts,cap)
            delta18,model18,_=v19.shift(x,parent['V14_event_overlay'],i,ts,cap)
            b0,_,_=v19.shift(x,parent['V14_exact'],i,ts,cap,'intercept')
            named={'V14_exact':(a,0.,1),'V14_event_overlay':(a18,d18,int(fit18 is not None)),
                'V14_plus_positions':((1+a)*np.exp(delta)-1,delta,int(model is not None)),
                'V18_plus_positions':((1+a18)*np.exp(delta18)-1,delta18,int(model18 is not None))}
            meta=dict(horizon=h,day=day[i],origin=raw_day,target_end=end[i],cohort=y[f'cohort_{h}'].iloc[i],cutoff=NATIVE,
                      decision=actual_issue,feature_clock=info,fit_last_mature=max(end[past]) if len(past) else None)
            actual=np.expm1(r[i])
            for name,(law,d,active) in named.items():
                z=cmp.loc[h,day[i],name]
                atoms,weights=use(v19books,int(z.law))
                np.testing.assert_allclose(law,atoms,atol=1e-10,rtol=0)
                np.testing.assert_array_equal(w,weights)
                val=evaluate(law,w,actual)
                err.append(metric_diff(z,val))
                out.append(meta|dict(track='parent_replay',model=name,shift=d,active=active,**val))
            extra={'V14_exact':0.,'V14_plus_positions':delta,'V14_bias_only':b0,
                   'V14_position_increment_without_bias':float(np.clip(delta-b0,-cap,cap))}
            for k,g in lag.items():
                live=ts[np.isfinite(g[ts]).any(axis=1)] if np.isfinite(g[i]).any() else ts[:0]
                extra[f'positions_delay{k}'],_,_=v19.shift(g,parent['V14_exact'],i,live,cap)
            for name,d in extra.items():
                z=checks.loc[h,day[i],name]
                law=(1+a)*np.exp(d)-1
                val=evaluate(law,w,actual)
                err.append(metric_diff(z,val))
                atoms,weights=use(mech,int(z.law))
                np.testing.assert_allclose(law,atoms,atol=1e-10,rtol=0)
                np.testing.assert_array_equal(w,weights)
                out.append(meta|dict(track='mechanism_replay',model=name,shift=d,active=int(z.active),**val))
            if model is None:
                assert delta==0. and delta18==0.
                continue
            q=evaluate((1+a)*np.exp(b0)-1,w,actual)
            groups={'levels':np.arange(3),'changes':np.arange(3,10),'crowding':np.arange(10,len(v19.POSITION)),
                    'innovation':np.arange(len(v19.POSITION),x.shape[1])}
            for g,cols in groups.items():
                a0=x[:,cols]
                dv,_,_=v19.shift(a0,parent['V14_exact'],i,past,cap)
                solid=evaluate((1+a)*np.exp(dv)-1,w,actual)
                null[h,'actual',g].append([q[k]-solid[k] for k in ('brier','crps')])
                for s in range(23):
                    order=np.roll(np.arange(len(past)),(s+3)*7) if s%2==0 else v19.shuffled_blocks(len(past),191125+s)
                    dv,_,_=v19.shift(a0,parent['V14_exact'],i,past,cap,random_order=order)
                    v=evaluate((1+a)*np.exp(dv)-1,w,actual)
                    null[h,s,g].append([q[k]-v[k] for k in ('brier','crps')])
        print('Reproduced V19 native timing, arms and nulls on',len(keep),h,'session origins',flush=True)
    z=pd.DataFrame(out)
    write('native-audit-cases.csv.gz',z)
    write('native-source-clock-audit.csv',pd.DataFrame(vintages))
    a=[]
    for (track,h,m),g in z.groupby(['track','horizon','model']):
        for k,q in [('all',g),('active',g[g.active.eq(1)]),('earlier',g[g.cohort.eq('early')]),('later',g[g.cohort.eq('later')])]:
            a.append(dict(track=track,horizon=h,model=m,scope=k,n=len(q),disjoint=disjoint(q),active=int(q.active.sum()),
                          **{v:q[v].mean() for v in ('brier','crps','log_loss')}))
    write('native-audit-summary.csv',pd.DataFrame(a))
    b=[]
    for h in HORIZONS:
        real=np.max([np.mean(v,axis=0) for (a,s,g),v in null.items() if a==h and s=='actual'],axis=0)
        sim=np.stack([np.max([np.mean(v,axis=0) for (a,k,g),v in null.items() if a==h and k==s],axis=0) for s in range(23)])
        for j,metric in enumerate(('brier','crps')):
            b.append(dict(horizon=h,metric=metric,best_observed_increment=real[j],rotation_median=np.median(sim[:,j]),
                rotation_95=np.quantile(sim[:,j],.95),exceedances=int((sim[:,j]>=real[j]).sum()),runs=len(sim)))
    b=pd.DataFrame(b)
    old=csv('native-refit-null-summary.csv',V19)
    np.testing.assert_allclose(b.select_dtypes('number'),old.select_dtypes('number'),rtol=0,atol=1e-8)
    write('native-audit-null-replay.csv',b)
    deletion=[]
    n=z[z.track.eq('mechanism_replay')]
    for h in HORIZONS:
        d=n[n.horizon.eq(h)].pivot(index=['day','target_end','cohort'],columns='model',values=['brier','crps','active']).sort_index()
        live=d['active']['V14_plus_positions'].eq(1)
        for field in ('brier','crps'):
            x=d[field]['V14_exact']-d[field]['V14_plus_positions']
            q=x[live]
            b=q.groupby(np.arange(len(q))//21).agg(['sum','count'])
            s=(q.sum()-b['sum'])/(len(q)-b['count'])
            j=int(s.argmin())
            deletion.append(dict(horizon=h,metric=field,early=x[x.index.get_level_values('cohort')=='early'].mean(),
                later=x[x.index.get_level_values('cohort')=='later'].mean(),n=len(q),combined=x.mean(),active_gain=q.mean(),
                remaining_gain=s.iloc[j],removed_start=q.index[j*21][0],removed_end=q.index[min(len(q)-1,j*21+20)][0]))
    write('native-audit-cohort-and-omission.csv',pd.DataFrame(deletion))
    assert max(err)<1e-8
    save('timing-audit-receipt.json',dict(replayed_cases=len(z),actual_native_origins=len(vintages),checked_scalar_error=max(err),
        native_parent_decision='09:10 IST following cash session from V14 registered source',
        archived_decision_field='V19 decision field stores the overlay snapshot, 08:55 IST. This field alone does not specify issuance of the combined native law.',
        eligible='All 482 participant availability times were at or before 08:55 and therefore before 09:10, using the inherited 08:15 next-session publication allowance.',
        caveat='Historical per-file first publication timestamps are unavailable. The V20 preceding-evening and extra lag tests measure sensitivity. Native cohorts and laws remain separated from the rebuilt 08:55 forecasts.',
        archived_options='All matched V14 option days strictly precede the cash reference day. V18 corporate sources and price reaction receipts precede their 08:55 snapshot.'))

if __name__=='__main__':
    import sys
    {'protect':protect,'replay':replay}[sys.argv[1]]()

