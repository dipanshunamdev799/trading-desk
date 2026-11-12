if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('momentum','Morning momentum','Three-bar movement beyond 0.5 ATR in normal volatility.',5,'normal_vol','morning',{'lookback': 3, 'threshold_atr': 0.5})

def signals(f):
    return eligible(f,direction(f.ret3>.5,f.ret3<-.5),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
