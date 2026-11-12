if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('gap_follow','Gap continuation','Follows a gap beyond 3 ATR during high volatility.',9,'high_vol','all',{'gap_atr': 3, 'prior_close': 'previous_complete_research_session_15:10'})

def signals(f):
    active=(f.gap.abs()>3)&(f.minute<660)
    return eligible(f,direction(active&(f.gap>0),active&(f.gap<0)),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
