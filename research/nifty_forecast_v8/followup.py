"""Stress pre-registered early designs and V8 point leaders on observed history."""
from .common import *
from .experiments import frames, evaluate, spec


def run(wave):
    x,elig=frames();rotation=matrix('rotation.csv',OUT);states=matrix('state.csv',OUT);base=x['base']
    if wave=='coverage':
        small=base[['p_ret5','p_ret21','p_rv21','p_vix','p_trend','i_participation','i_dispersion','i_nifty_it_rel21']]
        x['early_small']=small
        x['early_rotation']=pd.concat([small,rotation[['r_bank_change','r_def_change']]],axis=1)
        cfg={
             'E_HIST':spec('early_small','self',law='history',hypothesis='Mature historical law on earlier exposed origins'),
             'E_SMALL':spec('early_small','E_HIST',alpha=150,hypothesis='Compact earlier-market parent'),
             'E_ROT':spec('early_rotation','E_SMALL',alpha=150,hypothesis='Earlier compact rotation treatment'),
             'E_SMALL_126':spec('early_small','E_SMALL',alpha=150,window=126,hypothesis='Fixed short-window compact parent'),
             'E_ROT_126':spec('early_rotation','E_SMALL_126',alpha=150,window=126,hypothesis='Fixed short-window compact rotation treatment'),
             'E_FULL_ROT':spec('both_changes','E_HIST',hypothesis='Full rotation on earlier eligible dates with unchanged maturity rules'),
        }
        for s in cfg.values():s.update(min_train=85,min_inner=40,residual_window=28)
        evaluate('coverage',cfg,x,elig,'early')
    elif wave=='intermediate':
        cfg={'K_HIST':spec('base','self',law='history'),'K_BASE':spec('base','K_HIST'),
             'K_ROT':spec('both_changes','K_BASE'),'K_STRUCTURE':spec('structure_change','K_ROT')}
        for s in cfg.values():s.update(horizons=[10,15],hypothesis='Diagnostic comparison on original 21-session query dates')
        evaluate('intermediate',cfg,x,elig,'diagnostic')
    elif wave=='smoothmatch':
        smooth=states.rolling(21).mean()
        price=x['m_price']
        x['smooth_strict_current']=pd.concat([price,smooth],axis=1)
        x['smooth_strict_lag']=pd.concat([price,smooth.shift(21)],axis=1)
        x['smooth_strict_lag5']=pd.concat([price,smooth.shift(5)],axis=1)
        elig['smooth_ready']=smooth.shift(21).notna().all(axis=1)&smooth.notna().all(axis=1)
        cfg={
            'MS_MATCH_PRICE':spec('m_price','M_HIST',hypothesis='Price parent on exact dates that have complete 21-lagged smoothed state'),
            'MS_MATCH_NOW':spec('smooth_strict_current','MS_MATCH_PRICE',hypothesis='Current smoothed state on the fully common availability cohort'),
            'MS_MATCH_LAG5':spec('smooth_strict_lag5','MS_MATCH_NOW',hypothesis='Five-session genuine delay on fully common dates'),
            'MS_MATCH_LAG21':spec('smooth_strict_lag','MS_MATCH_NOW',hypothesis='21-session genuine delay on fully common dates'),
            'MS_MATCH_ROLL':spec('smooth_strict_current','MS_MATCH_NOW',roll_group='w_',diagnostic=True,hypothesis='22-style monthly mechanism control, train-only roll by 21'),
        }
        for s in cfg.values():s.update(eligible='smooth_ready',horizons=[21])
        evaluate('smoothmatch',cfg,x,elig)
    elif wave=='stress':
        cfg={}
        strongest=[('W_RES','residual','R_RESIDUAL'),('W_STRUCT','structure_change','A_STRUCTURE_CHANGE'),('W_LEVEL','structure_level','A_STRUCTURE_LEVEL')]
        for prefix,frame,parent in strongest:
            for name,params in [('WINDOW',{'window':189}),('EMBARGO',{'embargo':3}),('PERTURB',{'perturb':True}),
                                ('ALPHA',{'alpha':150}),('TARGET_NULL',{'permute_target':True,'diagnostic':True})]:
                cfg[f'{prefix}_{name}']=spec(frame,parent,horizons=[5],**params,hypothesis=f'Adaptive {name.lower()} stress on preliminary V8 lead')
            cols=[c for c in x[frame] if c not in base.columns]
            x[frame+'_lag']=pd.concat([base,x[frame][cols].shift(5)],axis=1)
            cfg[f'{prefix}_LAG']=spec(frame+'_lag',parent,horizons=[5],hypothesis='Five-session genuine previous observations')
            r=x[frame];selected=cols+list(base.filter(regex='^i_nifty_(it|financial|auto)'))
            clones=r[selected].rename(columns=lambda c:'zz_stress_'+c);x[frame+'_clone']=pd.concat([r,clones],axis=1)
            cfg[f'{prefix}_DEDUP']=spec(frame,parent,dedup=True,horizons=[5],hypothesis='Canonical base before controlled copy')
            cfg[f'{prefix}_CLONE']=spec(frame+'_clone',f'{prefix}_DEDUP',dedup=True,horizons=[5],diagnostic=True,hypothesis='Copy rotation and three sector groups after canonicalization')
            revised=matrix('native-revision-1bp.csv',V7).reindex(columns=base.columns)
            x[frame+'_revised']=pd.concat([revised,r[cols]],axis=1)
            cfg[f'{prefix}_REVISION']=spec(frame+'_revised',parent,horizons=[5],hypothesis='One-basis-point native source revision with new inputs fixed')
        smooth=states.rolling(21).mean()
        price=x['m_price']
        x['smoothed_lag5']=pd.concat([price,smooth.shift(5)],axis=1)
        x['smoothed_lag21']=pd.concat([price,smooth.shift(21)],axis=1)
        x['smoothed_state_only']=smooth.assign(p_rv21=.01)
        for name,frame,extra in [('MS_LAG5','smoothed_lag5',{}),('MS_LAG21','smoothed_lag21',{}),('MS_STATE_ONLY','smoothed_state_only',{}),
                                 ('MS_ROLL','m_state_smooth',{'roll_group':'w_','diagnostic':True}),
                                 ('MS_PERMUTE','m_state_smooth',{'permute_target':True,'diagnostic':True}),
                                 ('MS_WINDOW','m_state_smooth',{'window':126}),('MS_EMBARGO','m_state_smooth',{'embargo':3})]:
            cfg[name]=spec(frame,'M_STATE_SMOOTH',horizons=[21],eligible='monthly',**extra,hypothesis='Adaptive falsification of smoothed monthly state result')
        evaluate('stress',cfg,x,elig)
    else:raise ValueError(wave)


if __name__=='__main__':
    import sys
    run(sys.argv[1])
