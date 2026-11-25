"""Render an auditable research forecast directly from the retained case and law."""
import argparse
from .common import *
from .modeling import sample_law

TRACKS={
 'native':('native-mechanism-cases.csv.gz','native-mechanism-laws.npz','exact_v14'),
 'preauction':('architecture-cases.csv.gz','architecture-laws.npz','archived_same_clock'),
}
PICK={('native',5):'v18_corporate_native',('native',21):'v19_position_native',
      ('preauction',5):'E_sparse_horizon_inputs',('preauction',21):'E_sparse_horizon_inputs'}
QUANT=np.array([.05,.10,.25,.50,.75,.90,.95])

def metrics(a,w,ref):
    q=sample_law(a,w,QUANT)
    return dict(probability_up=float(w@(a>0)),expected_return=float(w@a),median_return=float(q[3]),
        expected_nifty_endpoint=float(ref*(1+w@a)),return_quantiles={str(k):float(v) for k,v in zip(QUANT,q)},
        index_quantiles={str(k):float(ref*(1+v)) for k,v in zip(QUANT,q)},
        interval_80=[float(q[1]),float(q[-2])],downside_2pct=float(w@(a<=-.02)),upside_2pct=float(w@(a>=.02)),
        downside_5pct=float(w@(a<=-.05)),upside_5pct=float(w@(a>=.05)))

def card(day,h,track,model=None):
    path,law_file,parent=TRACKS[track]
    d=csv(path)
    f=d[d.day.eq(day)&d.horizon.eq(h)].set_index('model')
    candidate=model or PICK[track,h]
    if f.empty or candidate not in f.index:
        raise ValueError(f'{day} has no archived {track} forecast for {h} sessions and {candidate}.')
    y=f.loc[candidate]
    z=f.loc[parent]
    previous=d[d.model.eq(candidate)&d.horizon.eq(h)&d.target_end.lt(day)]
    feature=csv('asof-features.csv.gz',usecols=['day','cutoff','decision','source_day','source_release','latest_available','surface_source_day','last_announcement','last_known_report','last_notice'])
    p=feature[feature.day.eq(day)&feature.cutoff.eq('preauction_0855')].iloc[0]
    ref=float(y.reference_close)
    def law(r,z):
        o=int(r.law)
        x,k=z['offsets'][o:o+2]
        a,w=z['atoms'][x:k],z['weights'][x:k]
        return a,w
    def history(q):
        if len(q)==0:return dict(n=0)
        s=q.brier.mean()
        return dict(n=len(q),brier=float(s),crps=float(q.crps.mean()),mean_probability=float(q.p.mean()),
                    actual_up=float(q.actual.gt(0).mean()),covered_80=float(q.covered.mean()))
    with np.load(OUT/law_file,allow_pickle=False) as a:
        atom,weight=law(y,a)
        cmp,w=law(z,a)
        snap={k:(None if pd.isna(v) else v) for k,v in p.items() if k not in ('cutoff','day')}
        return dict(research_classification='Retrospective frozen-vintage forecast',version='V20',origin=y.origin,decision_day=day,
           forecast_cutoff=y.cutoff,target_session=y.target_end,reference_index_close=ref,horizon=h,model_id=candidate,
           modeled_correction_active=bool(y.active),input_availability=snap,
           source_limit='Exchange EOD timing follows an assumed next-session guard. Full provisional daily FII/DII cash data and dated complete constituent weights are unresolved.',
           parent={'model':parent,**metrics(cmp,w,ref)},forecast=metrics(atom,weight,ref),
           available_historical_calibration=history(previous),law_archive=law_file,law_sha256=sha(OUT/law_file),
           parent_law_idx=int(z.law),forecast_law_idx=int(y.law),
           eligibility='This archived forecast shares its stated decision clock with the parent. Calibration uses only earlier fully matured cases.')

def run():
    p=argparse.ArgumentParser()
    p.add_argument('--day')
    p.add_argument('--horizon',type=int,choices=(5,21),default=5)
    p.add_argument('--clock',choices=tuple(TRACKS),default='native')
    p.add_argument('--model')
    a=p.parse_args()
    if a.day:
        print(json.dumps(card(a.day,a.horizon,a.clock,a.model),indent=2,default=str))
        return
    t=csv('architecture-cases.csv.gz',usecols=['day','horizon'])
    chosen=t[t.horizon.eq(21)].day.max()
    examples=[]
    for track in TRACKS:
        for h in HORIZONS:
            examples.append(card(chosen,h,track))
    save('experimental-forecast-examples.json',dict(cards=examples,policy='This entry point reconstructs stored cases with complete weighted terminal laws. Separately dated prospective references are indexed in the forward ledger.'))

if __name__=='__main__':
    run()

