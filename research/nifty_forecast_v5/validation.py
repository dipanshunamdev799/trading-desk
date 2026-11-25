"""Explicit scope/schema/mature-label/availability contracts for subsequent fits."""
from .common import *
def validate_training(x,h,context):
    scope(x.index)
    allowed={r['name'] for r in read('feature-definitions.json')}
    p=OUT/'liquidity-features.csv'
    if p.exists():allowed.update('p_liq_'+c for c in pd.read_csv(p,nrows=0).columns[1:])
    p=OUT/'liquidity-proxy-features.csv'
    if p.exists():allowed.update('p_liq_CURRENT_BASKET_'+c for c in pd.read_csv(p,nrows=0).columns[1:])
    if set(x.columns)-allowed:raise ValueError('UNREGISTERED_FEATURE')
    if np.isinf(x.to_numpy(float)).any():raise ValueError('INVALID_FEATURE_INFINITY')
    if 'labels' in context and h in context['labels']:
        l=context['labels'][h].loc[x.index]
        if not (l.endpoint.notna()&(l.endpoint<context['cutoff'])&l['return'].notna()).all():raise ValueError('UNMATURED_LABEL_OR_NO_EMBARGO')
    for name,stamps in x.attrs.get('available_at',{}).items():
        if name not in x:continue
        for day,stamp in zip(x.index,stamps):
            decision=x.attrs.get('decision_times',{}).get(day,pd.Timestamp(day,tz='Asia/Kolkata')+pd.Timedelta(days=1,hours=9,minutes=10))
            if pd.Timestamp(stamp)>pd.Timestamp(decision):raise ValueError('FUTURE_AVAILABILITY_SENTINEL')
