"""Stable serialization of training-only market feature scale and aliases."""
from dataclasses import dataclass
from .common import np
from research.nifty_forecast_v8.models import canonical


@dataclass
class TrainScale:
    columns:list

    def fit(self,x):
        a=x[self.columns].replace([np.inf,-np.inf],np.nan)
        self.med=a.median().fillna(0.)
        self.sd=a.std().fillna(1.).clip(lower=1e-7)
        z=((a.fillna(self.med)-self.med)/self.sd).to_numpy()
        ids,self.aliases=canonical(self.columns,np.c_[z.T,a.notna().to_numpy().T])
        if not len(ids):raise ValueError('Missing features')
        self.columns=[self.columns[j] for j in ids]
        self.med=self.med.loc[self.columns]
        self.sd=self.sd.loc[self.columns]
        return self

    def transform(self,x):
        z=x[self.columns].replace([np.inf,-np.inf],np.nan).fillna(self.med)
        return ((z-self.med)/self.sd).clip(-6,6).to_numpy(float)
