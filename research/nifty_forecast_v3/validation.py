"""Input-boundary enforcement shared by all future model fits."""
import json
import numpy as np
import pandas as pd
from .audit import OUT

def validate_frame(frame):
    if any(str(day)<'2025-01-01' for day in frame.index):raise ValueError('PRE_2025_INPUT_REJECTED')
    definitions=json.loads((OUT/'feature-definitions.json').read_text())
    allowed={r['feature'] for r in definitions}
    unknown=set(frame.columns)-allowed
    if unknown:raise ValueError('UNREGISTERED_FEATURE_REJECTED: '+','.join(sorted(unknown)))
    for column,available_at in frame.attrs.get('available_at',{}).items():
        if column not in frame:continue
        stamps=available_at.reindex(frame.index) if hasattr(available_at,'reindex') else available_at
        clocks=frame.attrs.get('decision_times',{})
        if any(pd.Timestamp(stamp)>pd.Timestamp(clocks.get(origin,pd.Timestamp(origin)+pd.Timedelta(days=1,minutes=30)))
               for stamp,origin in zip(stamps,frame.index)):
            raise ValueError('LOOKAHEAD_SENTINEL_REJECTED: '+column)
    numeric=frame.to_numpy(float)
    if np.isinf(numeric).any():raise ValueError('NONFINITE_FEATURE_REJECTED')

