"""Exact fixed-variance controls to isolate elapsed time and the realized anchor."""
from scipy.special import ndtr

from .common import *


def lognormal_score(y,mu,sigma):
    """CRPS for a lognormal terminal price ratio, invariant to subtracting one."""
    z=(np.log(y)-mu)/sigma
    mean=np.exp(mu+.5*sigma*sigma)
    first=y*(2*ndtr(z)-1)+mean*(1-2*ndtr(z-sigma))
    dispersion=mean*(2*ndtr(sigma/np.sqrt(2))-1)
    return first-dispersion


def run():
    cal=pd.read_csv(OUT/'update-calendar.csv')
    iv=pd.read_csv(OUT/'remaining-tenor-availability.csv').set_index(['asof','remaining']).iv
    a=np.array([iv.loc[x,h] for x,h in zip(cal.origin,cal.horizon)])
    b=np.array([iv.loc[x,r] for x,r in zip(cal['asof'],cal.remaining)])
    root=cal.target_close/cal.origin_reference
    anchor=cal.realized_price_ratio
    sigma=a*np.sqrt(cal.horizon/252.)
    shrunk=a*np.sqrt(cal.remaining/252.)
    current=b*np.sqrt(cal.remaining/252.)
    identify=cal[['horizon','origin','target','asof','checkpoint','cohort','remaining','literal_calendar']]
    out=[]
    for name,mu,r in [
            ('same_law_no_updates',np.zeros(len(cal)),sigma),
            ('same_law_shorter_only',np.zeros(len(cal)),shrunk),
            ('same_law_price_and_shorter',np.log(anchor),shrunk),
            ('same_law_with_fresh_IV',np.log(anchor),current)]:
        # Label source is used only after the four forecast parameters are defined.
        p=ndtr(mu/r)
        truth=root.gt(1)
        br=(p-truth)**2
        loss=-np.log(np.clip(np.where(truth,p,1-p),.0005,1.))
        z=identify.assign(model=name,p=p,brier=br,log_loss=loss,crps=lognormal_score(root,mu,r),
                  remaining_p=ndtr((mu-np.log(anchor))/r),remaining_crps=lognormal_score(root/anchor,mu-np.log(anchor),r))
        z['remaining_brier']=(z.remaining_p-(root>anchor))**2
        out.append(z)
    s=pd.concat(out,ignore_index=True)
    assert s.crps.ge(-1.e-12).all()
    write('mechanical-same-law-scores.csv.gz',s)
    write('mechanical-same-law-evidence.csv',s.groupby(['horizon','checkpoint','model'],as_index=False).agg(
         n=('origin','nunique'),brier=('brier','mean'),log_loss=('log_loss','mean'),crps=('crps','mean'),
         remaining_crps=('remaining_crps','mean'),remaining_brier=('remaining_brier','mean')))


if __name__=='__main__':
    run()
