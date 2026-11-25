"""Nested calibration and joint proper-score frontier for coherent laws."""
from itertools import product
from .common import *
from .experiments import frames, queries, cutoff_dates, row
from .models import fit, location, predict, Distribution, mix, cross_abs


def tilt(law,odds,spread=1.):
    m=law.stats()['mean_return'];atoms=np.maximum(m+spread*(law.a-m),-.999999)
    return Distribution(atoms,law.w*np.exp(odds*(atoms>0)))


def pairs_table(rows):
    t=[]
    for _,a,b,y in rows:
        t.append((a.w@abs(a.a-y),b.w@abs(b.a-y),cross_abs(a,a),cross_abs(b,b),cross_abs(a,b),a.stats()['p_up'],b.stats()['p_up'],y>0))
    return np.asarray(t).T


def loss(vals,w):
    ea,eb,aa,bb,ab,pa,pb,y=vals
    brier=np.mean((w*pa+(1-w)*pb-y)**2)
    crps=np.mean(w*ea+(1-w)*eb-.5*(w*w*aa+(1-w)**2*bb+2*w*(1-w)*ab))
    return float(brier),float(crps)


def train(prior):
    if len(prior)<36:return .5,0.,1.,{'enabled':False,'reason':'fewer than 36 resolved historical forecasts'}
    check=prior[-18:]
    gate_start=check[0][0].origin
    early=[z for z in prior[:-18] if z[0].endpoint<gate_start]
    if len(early)<18:return .5,0.,1.,{'enabled':False,'reason':'fewer than 18 purged observations before chronological gate'}
    a=pairs_table(early);b=pairs_table(check)
    # Low-cardinality objective and weights. Choose preference on a later historical validation segment.
    preferences=[.25,.5,.75];weights=np.linspace(.1,.9,17);candidates=[]
    for preference in preferences:
        def objective(w):
            p,c=loss(a,w);return preference*p/.25+(1-preference)*c/.02+.2*(w-.5)**2
        w=float(min(weights,key=objective));pp,cc=loss(b,w);candidates.append((pp/.25+cc/.02,w,preference,pp,cc))
    chosen=min(candidates);bb,bc=loss(b,.5)
    w=chosen[1] if chosen[0]<bb/.25+bc/.02 else .5
    control=[(mix(x,y,w),r) for _,x,y,r in early]
    def scores(data,o,s):
        values=[tilt(d,o,s).score(r) for d,r in data]
        return np.mean([v['brier'] for v in values]),np.mean([v['crps'] for v in values]),np.mean([v['coverage80'] for v in values])
    def calibration_loss(z):
        p,c,_=scores(control,*z);return p/.25+c/.02+.15*z[0]**2+.2*(z[1]-1)**2
    odds,spread=min(product([-.25,0.,.25],[.9,1.,1.1]),key=calibration_loss)
    test=[(mix(a,b,w),y) for _,a,b,y in check];old=scores(test,0.,1.);new=scores(test,odds,spread)
    enabled=bool((odds!=0 or spread!=1) and new[0]/.25+new[1]/.02<old[0]/.25+old[1]/.02 and abs(new[2]-.8)<=abs(old[2]-.8)+1e-12)
    return w,odds if enabled else 0.,spread if enabled else 1.,{'enabled':enabled,'preference':chosen[2],
         'selected_candidate_weight':chosen[1],'mixture_gate_enabled':bool(w!=.5),'proposed_tilt':odds,'proposed_spread':spread,
         'raw_gate_scores':[float(z) for z in old],'adjusted_gate_scores':[float(z) for z in new],'n_early':len(early),'n_gate':18,
         'gate_first_origin':gate_start,'calibration_fit_last_endpoint':max(z[0].endpoint for z in early)}


def run():
    models={'J_EQUAL':{'parent':'B_ROT'},'J_LEARNED':{'parent':'J_EQUAL'},'J_ADJUSTED':{'parent':'J_LEARNED'}}
    curve={f'J_GRID{i}':{'parent':'J_EQUAL','diagnostic':True,'weight':i/4} for i in range(5)}
    save('integration-registry.json',{'registered_at':now(),'cohort':'primary','configurations':models|curve,'seed':SEED,
          'weights':'Recent 84 strictly matured reconstructed outcomes. Earliest subset, purged so its endpoints precede the first gate origin, fits candidate blend and tilt. Last 18 form chronological gate. Prior gate improvement and no coverage deterioration required for adjustment.',
          'parents':['Ridge100 + rotation','cluster-balanced Elastic Net native'],'fixed_grid':'0, .25, .5, .75, 1 for reporting, diagnostic only'})
    x,_=frames();price=matrix('price.csv').close;rows=[];ledger=[];cache=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv');history=[]
        q=pd.concat([queries(h,'early').assign(split='early'),queries(h,'primary').assign(split='primary')],ignore_index=True)
        for (split,fold),g in q.groupby(['split','fold']):
            cutoff=g.origin.min()
            try:tr,ii,vv,tc,ic=cutoff_dates(y,x['base'].index,cutoff,{'min_train':85,'min_inner':35},None)
            except ValueError as exc:
                ledger.append({'horizon':h,'fold':fold,'split':split,'status':'unestimated','reason':str(exc)});continue
            predictions=[]
            for inp,cfg in [(x['both_changes'],{}),(x['native'],{'rep':'cluster','dedup':True,'kind':'elastic'})]:
                m=fit(cfg,inp.loc[tr],y.loc[tr,'return'].to_numpy());m0=fit(cfg,inp.loc[ii],y.loc[ii,'return'].to_numpy())
                res=y.loc[vv,'return'].to_numpy()-location(m0,inp.loc[vv])
                predictions.append(predict(m,inp.loc[g.origin],res,inp.loc[vv,'p_rv21'].to_numpy(),np.zeros(len(vv))))
            earlier=[z for z in history if z[0].endpoint<cutoff][-84:];w,odds,spread,gate=train(earlier)
            ledger.append({'horizon':h,'fold':fold,'split':split,'status':'ok','cutoff':cutoff,'train_cutoff':tc,'inner_cutoff':ic,
                           'last_endpoint':y.loc[tr,'endpoint'].max(),'inner_last_endpoint':y.loc[ii,'endpoint'].max(),
                           'historical_origins':[{'origin':r.origin,'endpoint':r.endpoint} for r,_,_,_ in earlier],
                           'weight':w,'tilt':odds,'spread':spread,**gate})
            for r,a,b in zip(g.itertuples(),*predictions):
                history.append((r,a,b,r.realized_return));cache.append({'horizon':h,'origin':r.origin,'endpoint':r.endpoint,
                     'split':split,'rotation_atoms':a.a.tolist(),'rotation_weights':a.w.tolist(),'elastic_atoms':b.a.tolist(),'elastic_weights':b.w.tolist()})
                if split=='early':continue
                learned=mix(a,b,w)
                choices={'J_EQUAL':mix(a,b,.5),'J_LEARNED':learned,'J_ADJUSTED':tilt(learned,odds,spread)}
                choices.update({name:mix(a,b,c['weight']) for name,c in curve.items()})
                for name,d in choices.items():rows.append(row(h,fold,name,r,d,float(price.loc[r.origin]),'primary'))
    write('integration-predictions.csv',pd.DataFrame(rows));save('integration-ledger.json',ledger)
    (OUT/'integration-parent-laws.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in cache),encoding='utf-8')
    print('Coherent joint forecasts',len(rows),flush=True)


if __name__=='__main__':run()
