"""Small adaptive follow-up on the first V7 weekly leads."""
from .common import *
from .experiments import all_frames, evaluate, spec


def run():
    frames,eligible=all_frames()
    low=frames['nodef'];native=frames['native']
    rotation=frames['rotation'];rot=rotation.drop(columns=low.columns)
    daily=frames['daily'];daily_extra=daily.drop(columns=low.columns)
    frames['rotation_domestic']=pd.concat([low,rot[['financial_spread','defensive_dispersion']]],axis=1)
    frames['rotation_other']=pd.concat([low,rot[['global_relative_change','etf_activity_change']]],axis=1)
    frames['rotation_lag']=pd.concat([low,rot.shift(5)],axis=1)
    frames['rotation_lag_global']=rotation.assign(global_relative_change=rot.global_relative_change.shift(1))
    frames['rotation_revision']=pd.concat([frames['revision'][low.columns],rot],axis=1)
    frames['day_parts']=pd.concat([low,daily_extra[['l_overnight5','l_openclose5','l_range5']]],axis=1)
    frames['day_etf']=pd.concat([low,daily_extra[['l_etf_average','l_etf_delta5']]],axis=1)
    frames['daily_lag']=pd.concat([low,daily_extra.shift(5)],axis=1)
    configs={
        'T_ROT_DOMESTIC':spec('C_NO_DEF','rotation_domestic',hypothesis='Domestic rotation alone'),
        'T_ROT_OTHER':spec('C_NO_DEF','rotation_other',hypothesis='Global-relative and ETF activity change alone'),
        'T_ROT_LAG5':spec('S_ROTATION','rotation_lag',diagnostic=True,hypothesis='Five-session lag placebo for new inputs'),
        'T_ROT_FOREIGN_LAG':spec('S_ROTATION','rotation_lag_global',hypothesis='One extra session of staleness on the foreign-relative term'),
        'T_ROT_REV':spec('S_ROTATION','rotation_revision',hypothesis='Synthetic one-basis-point perturbation of native sources, rotation inputs fixed'),
        'T_ROT_WINDOW':spec('S_ROTATION','rotation',window=189,hypothesis='Fixed latest 189 fit observations'),
        'T_ROT_EMBARGO':spec('S_ROTATION','rotation',embargo=3,hypothesis='Earlier fully matured label cutoff'),
        'T_DAY_OC':spec('C_NO_DEF','day_parts',hypothesis='Opening/closing split without ETF terms'),
        'T_DAY_ETF':spec('C_NO_DEF','day_etf',hypothesis='Two ETF activity summaries without the open-close split'),
        'T_DAY_LAG':spec('L_DAILY','daily_lag',diagnostic=True,hypothesis='Lagged daily liquidity block'),
        'T_DAY_WINDOW':spec('L_DAILY','daily',window=189,hypothesis='Fixed latest 189 fit observations'),
        'T_DAY_STUDENT':spec('L_DAILY','daily',law='student',hypothesis='Same location, Student residual law'),
        'T_RAW_ELASTIC':spec('C_ELASTIC',kind='elastic',hypothesis='Isolate cluster scaling from cross-model penalty change'),
        'T_ELASTIC_WINDOW':spec('C_ELASTIC',rep='cluster_balance',kind='elastic',window=189,hypothesis='Fixed latest 189 fit observations'),
        'T_ELASTIC_EMBARGO':spec('C_ELASTIC',rep='cluster_balance',kind='elastic',embargo=3,hypothesis='Earlier label cutoff sensitivity'),
    }
    for cfg in configs.values():cfg.update(horizons=[5],selection='Adaptive test prompted by V7 exposed S_ROTATION, L_DAILY and C_ELASTIC point scores')
    evaluate('followup',configs,frames,eligible)


if __name__=='__main__':
    run()
