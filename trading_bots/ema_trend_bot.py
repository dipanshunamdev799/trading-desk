if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('ema_trend','EMA trend','EMA12/26 separation over 0.5 ATR in an afternoon trend.',1,'trend','afternoon',{'fast': 12, 'slow': 26, 'gap_atr': 0.5})

def signals(f):
    diff=(f.ema12-f.ema26)/f.atr
    return eligible(f,direction(diff>.5,diff<-.5),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
