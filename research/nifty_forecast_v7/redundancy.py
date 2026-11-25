"""Training-only correlation maps and factor stability diagnostics."""
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from scipy.linalg import subspace_angles
from sklearn.linear_model import Ridge
from research.nifty_forecast_v5.models import Scale
from .common import *
from .models import clusters
from .reproduce import references


def spectrum(a):
    eigen, basis = np.linalg.eigh(np.cov(a,rowvar=False,bias=True))
    v = np.maximum(eigen,0)
    p = v/max(v.sum(),1e-12)
    return basis[:,-6:], float(np.exp(-np.sum(p*np.log(np.maximum(p,1e-12))))),float(p[-1])


def run():
    native,_,defensive = references()
    cols = [c for c in native if c.startswith('i_') and c.endswith(('_rel5','_rel21'))]
    rows, maps, loadings, stability = [], [], [], []
    previous = None
    for r in read('compression-ledger.json'):
        if r['model']!='C_RAW' or r['status']!='ok':continue
        art=joblib.load(OUT/r['artifact'])
        dates=art['training']
        x=native.loc[dates];a=Scale().fit(x[cols]).transform(x[cols]);control=Scale().fit(x.filter(regex='^p_')).transform(x.filter(regex='^p_'))
        residual=a-Ridge(alpha=100).fit(control,a).predict(control)
        groups, cor, tree=clusters(a);_, conditional,_=clusters(residual)
        for group in groups:
            maps.append({'horizon':r['horizon'],'fold':r['fold'],'cutoff':r['cutoff'],'members':[cols[i] for i in group]})
        for i,name in enumerate(cols):
            for j in range(i+1,len(cols)):
                rows.append({'horizon':r['horizon'],'fold':r['fold'],'a':name,'b':cols[j],'corr':cor[i,j],'price_residual_corr':conditional[i,j],
                             'same_lookback':name.split('_')[-1]==cols[j].split('_')[-1],
                             'identical_standardized_series':bool(np.allclose(a[:,i],a[:,j],atol=1e-12,rtol=0))})
        all_basis,rank,top = spectrum(a);recent,rrank,rtop = spectrum(a[-126:]);early,erank,etop=spectrum(a[:126])
        _,crank,_ = spectrum(residual)
        angles=np.degrees(subspace_angles(early,recent))
        sets={tuple(sorted((int(i),int(j)))) for group in groups for i in group for j in group if i<j}
        drift=None if previous is None or r['horizon']!=previous[0] else len(sets & previous[1])/max(1,len(sets | previous[1]))
        previous=r['horizon'],sets
        stability.append({'horizon':r['horizon'],'fold':r['fold'],'training_n':len(dates),'clusters':len(groups),'effective_rank':rank,
                          'residual_rank':crank,'first_share':top,'early_rank':erank,'recent_rank':rrank,'early_first_share':etop,
                          'recent_first_share':rtop,'early_recent_top_factor_abs_cosine':abs(float(early[:,-1]@recent[:,-1])),
                          'early_recent_max_principal_angle_deg':max(angles),'prior_fold_cluster_pair_jaccard':drift})
        for label,mat in [('full',all_basis),('recent126',recent),('first126',early)]:
            for comp,vec in enumerate(mat.T[::-1],1):
                anchor=int(abs(vec).argmax());vec=vec*np.sign(vec[anchor])
                for feature,loading in zip(cols,vec):loadings.append({'horizon':r['horizon'],'fold':r['fold'],'window':label,'feature':feature,'component':comp,'loading':loading})
        if r['horizon']==5 and r['fold']=='2026-07':
            fig,(ax,heat)=plt.subplots(1,2,figsize=(15,9),gridspec_kw={'width_ratios':[1.3,1]})
            labels=[c.removeprefix('i_').replace('idx_','') for c in cols]
            ordered=dendrogram(tree,orientation='left',labels=labels,leaf_font_size=8,color_threshold=.25,ax=ax)
            order=ordered['leaves'];im=heat.imshow(cor[np.ix_(order,order)],vmin=-1,vmax=1,cmap='RdBu_r',origin='lower')
            heat.set_title('Training correlation in dendrogram order');heat.set_xlabel('Relative-return features');heat.set_ylabel('Relative-return features')
            fig.colorbar(im,ax=heat,shrink=.6,label='Pearson correlation');ax.set_xlabel('Average linkage distance 1 − |correlation|')
            fig.suptitle('Native index redundancy at the first weekly evaluation cutoff',fontweight='bold')
            fig.tight_layout();fig.savefig(OUT/'feature-cluster-map.png',dpi=145);plt.close(fig)
    pd.DataFrame(rows).to_csv(OUT/'feature-correlations.csv',index=False)
    pd.DataFrame(stability).to_csv(OUT/'factor-stability.csv',index=False)
    pd.DataFrame(loadings).to_csv(OUT/'factor-loadings.csv',index=False)
    save('cluster-definitions.json',maps)
    sector=[]
    cutoff='2026-06-30'
    for filename in ['sector-returns.csv','sector-momentum5.csv','sector-volatility5.csv']:
        f=matrix(filename,OUT).loc[:cutoff].iloc[:-1]
        for a in f:
            for b in f:
                if a<b:sector.append({'matrix':filename,'a':a,'b':b,'corr':f[a].corr(f[b]),'last_date':f.index[-1]})
    pd.DataFrame(sector).to_csv(OUT/'sector-correlation-map.csv',index=False)
    print('Training feature map with',len(rows),'pair records and',len(loadings),'loadings',flush=True)


if __name__=='__main__':
    run()
