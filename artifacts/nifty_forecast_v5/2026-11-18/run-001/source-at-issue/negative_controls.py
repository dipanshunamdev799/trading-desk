"""Two fixed training-label shuffles for the strongest first-stage mechanism."""
from .common import *
from .models import fit,mean_prediction,laws
from research.nifty_forecast_v3.experiment import available,inner_split
def run():
    save('null-plan.json',{'registered_at':now(),'model':'I00','seeds':[301,907],'mechanism':'Shuffle only matured training labels; inner residual null labels shuffled separately; score actual future outcomes. Descriptive diagnostic, no selection.'})
    x=pd.read_csv(OUT/'features.csv',index_col=0);old=pd.read_csv(V3/'predictions.csv');records=[]
    for h in [5,21]:
        labs=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0);queries=old[(old.horizon==h)&(old.model=='B00_empirical')&(old.split=='outer_exposed')]
        for seed in [301,907]:
            rng=np.random.default_rng(seed)
            for fold,g in queries.groupby('fold'):
                ix=available(labs,g.origin.min());ii,vv=inner_split(labs,ix);ctx={'cutoff':g.origin.min(),'labels':{h:labs}}
                yi=rng.permutation(labs.loc[ii,'return'].to_numpy());inner=fit('I00',x.loc[ii],yi,h,ctx);res=rng.permutation(labs.loc[vv,'return'].to_numpy())-mean_prediction(inner,x.loc[vv],ctx)
                model=fit('I00',x.loc[ix],rng.permutation(labs.loc[ix,'return'].to_numpy()),h,ctx);pred=laws(model,x.loc[g.origin],ctx,res)
                for row,law in zip(g.itertuples(),pred):records.append({'horizon':h,'seed':seed,'fold':fold,'origin':row.origin,**law.score(row.realized_return)})
    frame=pd.DataFrame(records);frame.to_csv(OUT/'negative-control-predictions.csv',index=False)
    save('negative-controls.json',[{'horizon':int(h),'seed':int(s),'n':len(g),'brier':float(g.brier.mean()),'crps':float(g.crps.mean()),'accuracy':float(((g.p>=.5)==g.outcome).mean())} for (h,s),g in frame.groupby(['horizon','seed'])]);print('Negative controls complete',flush=True)
if __name__=='__main__':run()
