"""Refit V8 winners, matched controls, and older evidence using saved partitions."""
import joblib
from .common import *
from research.nifty_forecast_v8.experiments import frames
from research.nifty_forecast_v8.models import fit, location, predict, Distribution

WINNERS=['R_RESIDUAL','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','W_STRUCT_EMBARGO','G_ROT_ELASTIC']
OTHER=['E_HIST','E_FULL_ROT','E_SMALL_126','MS_WINDOW','M_STATE_SMOOTH','MS_ROLL','MS_MATCH_ROLL',
       'W_RES_WINDOW','W_STRUCT_WINDOW','A_ETF_ACTIVITY','A_INTRADAY','A_INTRADAY_BASE',
       'G_MATCH5','G_DIRECT5','G_MEDIATE5','G_CONDITIONAL5','G_MATCH21','G_DIRECT21','G_MEDIATE21','G_CONDITIONAL21']


def preserve():
    files=read('preservation.json',V8)['files'] | {str(Path(p)):v for p,v in read('delivery-manifest.json',V8)['files'].items()}
    path=V8/'delivery-manifest.json';files[str(path.relative_to(ROOT))]=sha(path)
    inputs=[ROOT/'NIFTY_V8_RESEARCH.md',*V8.glob('V8_*.md'),*V8.glob('*registry.json'),V8/'data-manifest.json',
            V8/'verification.json',V8/'all-predictions.csv',V8/'retained-endpoint-laws.jsonl',V8/'search-ledger.json']
    inputs+=sorted((ROOT/'research/nifty_forecast_v8').glob('*.py'))
    review=[{'file':str(p.relative_to(ROOT)),'bytes':len(p.read_text(encoding='utf-8').encode()),'sha256':sha(p)} for p in inputs]
    save('preservation.json',{'at':now(),'files':files,'review':review})


def replay_frames():
    x,_=frames();native=x['base'];q=matrix('rotation.csv',V8);state=matrix('state.csv',V8)
    small=native[['p_ret5','p_ret21','p_rv21','p_vix','p_trend','i_participation','i_dispersion','i_nifty_it_rel21']]
    x['early_small']=small
    x['smooth_strict_current']=pd.concat([x['m_price'],state.rolling(21).mean()],axis=1)
    g=matrix('global.csv',V8);g['asian_dispersion']=abs(g['g_^HSI_ret5']-g['g_^N225_ret5'])
    st=matrix('market-structure.csv',V7)
    from research.nifty_forecast_v8.global_research import LINKS
    cols=list(dict.fromkeys(c for group in LINKS.values() for c in group))
    for h in [5,21]:
        inc=matrix(f'global-intermediate-features-{h}.csv',V8)
        x[f'direct{h}']=pd.concat([x['both_changes'],g[cols]],axis=1)
        x[f'intermediate{h}']=pd.concat([x['both_changes'],inc],axis=1)
        x[f'intermediate_gate{h}']=pd.concat([x['both_changes'],inc,inc.mul((st.participation<.5).astype(float),axis=0).add_suffix('_weak')],axis=1)
    return x


def run():
    if (OUT/'reproduction.json').exists():raise FileExistsError('Use a fresh V9 folder')
    preserve()
    x=replay_frames();scores=['p','predicted_mean','predicted_median','brier','crps']
    prior=pd.read_csv(V8/'all-predictions.csv').set_index(['model','horizon','origin']).sort_index()
    reg=read('search-ledger.json',V8);ledger=[];rows=[]
    for f in reg['fold_attempts']:
        name=f.get('model');h=f['horizon']
        if f['status']!='ok' or name not in WINNERS+OTHER or (name in WINNERS and h!=5):continue
        path=V8/f['artifact'];assert sha(path)==f['sha256']
        obj=joblib.load(path);cfg=reg['configurations'][name];a=x[cfg['frame']];y=matrix(f'labels-{h}.csv')
        tr,ii,vv,q=(obj[k] for k in ['training','inner_dates','validation','queries'])
        outer=a.loc[tr].copy();inner=a.loc[ii].copy()
        if cfg.get('roll_group'):
            cols=[c for c in a if c.startswith(cfg['roll_group'])]
            outer[cols]=np.roll(outer[cols],21,axis=0);inner[cols]=np.roll(inner[cols],21,axis=0)
        yy=y.loc[tr,'return'].to_numpy();m=fit(cfg,outer,yy);m0=fit(cfg,inner,y.loc[ii,'return'].to_numpy())
        res=y.loc[vv,'return'].to_numpy()-location(m0,a.loc[vv]);risk=a.loc[vv,'p_rv21'].to_numpy()
        rot=a.loc[vv,'r_bank_change'].to_numpy() if 'r_bank_change' in a else np.zeros(len(vv))
        laws=[Distribution(yy[-252:])]*len(q) if cfg.get('law')=='history' else predict(m,a.loc[q],res,risk,rot)
        got=pd.DataFrame(d.score(y.loc[t,'return']) for t,d in zip(q,laws));want=prior.xs((name,h),level=[0,1]).loc[q,scores]
        np.testing.assert_allclose(got[scores],want,atol=1e-12,rtol=1e-12)
        err=float(abs(got[scores].to_numpy()-want.to_numpy()).max())
        ledger.append({'model':name,'fold':f['fold'],'horizon':h,'cohort':f.get('cohort'),'rows':len(q),'maximum_error':err,'artifact_hash':sha(path),'spec':cfg})
        rows.extend({'model':name,'horizon':h,'origin':d,'fold':f['fold'],**r} for d,r in zip(q,got.to_dict('records')))
    # Redirect the known V7 replay's writers into V9. The protected inputs retain their original paths.
    from research.nifty_forecast_v8 import reproduce as v8
    old=v8.save;old_out=v8.OUT
    v8.OUT=OUT/'legacy-replay';v8.OUT.mkdir(exist_ok=True)
    v8.preserve=lambda:None
    v8.save=lambda n,data:save('legacy-replay/'+n,data)
    v8.write=lambda n,data:write('legacy-replay/'+n,data)
    try:v8.run()
    finally:v8.OUT=old_out;v8.save=old
    write('replayed-v8-predictions.csv',pd.DataFrame(rows))
    save('reproduction.json',{'passed':True,'v8_rows':len(rows),'folds':ledger,'older_weekly_rows':read('legacy-replay/reproduction.json')['forecasts'],
         'max_abs_error':max(r['maximum_error'] for r in ledger),'expected_v8_winners':WINNERS})
    print('Reproduced',len(rows),'V8 rows and 644 older weekly reference rows',flush=True)


if __name__=='__main__':run()
