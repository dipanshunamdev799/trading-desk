"""Exact feature effects, size-decomposition attribution, revisions and conditional IC."""
import joblib
from scipy.stats import rankdata
from .common import *
from .reproduce import frames
from .forensics import GROUPS
from research.nifty_forecast_v5.models import laws as old_laws
from research.nifty_forecast_v3.experiment import available
from .engine import Scale
def bh(p):
    p=np.asarray(p);order=np.argsort(p);q=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1];out=np.empty(len(p));out[order]=np.minimum(q,1);return out
def rankcorr(a,b):
    aa=rankdata(a);bb=rankdata(b)
    return float(np.corrcoef(aa,bb)[0,1]) if np.std(aa)>1e-10 and np.std(bb)>1e-10 else 0.
def run():
    x,price,labels,data,fr=frames();p=pd.read_csv(V5/'all-predictions.csv');p=p[p.split=='outer_exposed'];changes=[];coeff=[];conditional=[];directions=[]
    from sklearn.linear_model import Ridge
    for h in [5,21]:
        q=p[(p.horizon==h)&(p.model=='I03_nosize')];full=p[(p.horizon==h)&(p.model=='I00')].set_index('origin')
        for fold,g in q.groupby('fold'):
            a=joblib.load(V5/'models'/f'h{h}-{fold}-I03_nosize.joblib');model=a['model'];scale=model['scale'];xq=fr['I03_nosize'].loc[g.origin];before=g.p.to_numpy();idx=list(model['train_dates']);native=xq[scale.cols]
            for c,b in zip(scale.cols,model['estimator'].coef_):
                cq=xq.copy();cq[c]=scale.med[scale.cols.index(c)];ds=old_laws(model,cq,{},a['residual']);after=np.array([d.stats()['p_up'] for d in ds]);changes.append({'horizon':h,'fold':fold,'feature':c,'mean_abs_probability_change':float(np.mean(abs(after-before))),'max_abs_probability_change':float(np.max(abs(after-before))),
                    'note':'Exact query-date training-median replacement with fixed model; importance association, not causal effect'})
                coeff.append({'horizon':h,'fold':fold,'feature':c,'coefficient':float(b),'training_observed':int(fr['I03_nosize'].loc[idx,c].notna().sum())})
            # Conditional relationships are measured only in the first outer fold's development training.
            if fold=='2026-07':
                xx=fr['I03_nosize'].loc[idx,scale.cols];yy=labels[h].loc[idx,'return'].to_numpy();pricecols=[c for c in xx if c.startswith('p_')]
                for c in scale.cols:
                    controls=[n for n in pricecols if n!=c];s=Scale().fit(xx[controls]);z=s.transform(xx[controls]);target=xx[c].to_numpy();m=np.isfinite(target)
                    yc=yy-Ridge(alpha=10).fit(z,yy).predict(z);fc=target-Ridge(alpha=10).fit(z[m],target[m]).predict(z)
                    ar=fc[m];br=yc[m];ic=rankcorr(ar,br);rng=np.random.default_rng(SEED);n=len(ar);null=[rankcorr(ar,np.roll(br,int(j))) for j in rng.integers(2*h,n-2*h,200)];pv=(1+sum(abs(v)>=abs(ic) for v in null))/201
                    half=n//2;conditional.append({'horizon':h,'feature':c,'n':n,'price_conditioned_rank_ic':ic,'first_half_ic':rankcorr(ar[:half],br[:half]),'second_half_ic':rankcorr(ar[half:],br[half:]),'p_shift':pv,'interpretation':'Development-only regularized price residual association, not conditional independence or causation'})
        for name in ['I03_nosize','I00','L01','L02']:
            g=p[(p.horizon==h)&(p.model==name)];pred=g.p>=.5;y=g.outcome==1
            directions.append({'horizon':h,'model':name,'n':len(g),'predicted_up':int(pred.sum()),'actual_up':int(y.sum()),'true_up':int((pred&y).sum()),'false_up':int((pred&~y).sum()),'true_down':int((~pred&~y).sum()),'false_down':int((~pred&y).sum()),'mean_probability':float(g.p.mean()),'accuracy':float((pred==y).mean())})
    cc=pd.DataFrame(conditional);cc['bh_q']=bh(cc.p_shift);cc.to_csv(OUT/'conditional-feature-information.csv',index=False);pd.DataFrame(changes).to_csv(OUT/'exact-feature-effects.csv',index=False);pd.DataFrame(coeff).to_csv(OUT/'coefficient-stability.csv',index=False);save('direction-confusion.json',directions)
    # Actual old/new archive overlap, without inventing source revisions.
    old={}
    for path in (V3/'sources/upstox').glob('*.json'):
        d=json.loads(path.read_text())
        if d.get('ok') and d.get('rows'):old[d['instrument_key']]=pd.DataFrame(d['rows']).drop_duplicates('day').set_index('day')
    revisions=[]
    for name,meta in read('requested-universe.json',V5)['identities'].items():
        key=meta['key']
        if name not in data or key not in old:continue
        matched=data[name].index.intersection(old[key].index);delta=(data[name].loc[matched,'close'].astype(float)-old[key].loc[matched,'close'].astype(float)).abs()
        revisions.append({'identity':name,'family':meta['family'],'overlap_n':len(matched),'changed_closes':int(delta.gt(1e-8).sum()),'max_abs_close_difference':float(delta.max()) if len(delta) else None})
    save('actual-source-revision-audit.json',revisions)
    # A factorial decomposition clarifies what the original no-size operation changed.
    f=pd.read_csv(OUT/'forensic-predictions.csv');decomp=[]
    for h in [5,21]:
        for name in ['F_SIZE_COLS','F_SIZE_AGG','F_SMALL_ONLY','F_MID_ONLY','F_SIZE_ORTHO']:
            g=f[(f.horizon==h)&(f.model==name)].set_index('origin');baseline=p[(p.horizon==h)&(p.model=='I00')].set_index('origin').reindex(g.index);new=(g.p>=.5);oldp=(baseline.p>=.5);correct=(oldp==g.outcome);flip=new!=oldp
            decomp.append({'horizon':h,'variant':name,'n':len(g),'brier':float(g.brier.mean()),'crps':float(g.crps.mean()),'gain_vs_I00':float((baseline.brier-g.brier).mean()),'probability_change_mean_abs':float(abs(g.p-baseline.p).mean()),'flips':int(flip.sum()),'correct_to_wrong':int((flip&correct).sum()),'wrong_to_correct':int((flip&~correct).sum())})
    save('size-factorial-decomposition.json',decomp)
    save('forensic-audit-summary.json',{'conditional_tests':len(cc),'min_q':float(cc.bh_q.min()),'q_under_05':int((cc.bh_q<.05).sum()),
        'exact_effects_note':'New exact-feature-effects.csv uses training-median replacements. Earlier forensic influence CSV standardized-zero formula is a training-MEAN replacement proxy despite its legacy column label.',
        'source_revision_note':'Actual observed overlap is measured; synthetic1bp study is explicitly a sensitivity scenario, not a claim an exchange/vendor revised prices.'})
    print('Forensic influence/conditional/source/size audits complete',flush=True)
if __name__=='__main__':run()
