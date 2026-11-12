if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('ema_reversion','EMA mean reversion','Fades distance beyond 2 ATR from EMA21 in a morning range.',8,'range','morning',{'distance_atr': 2})

def signals(f):
    return eligible(f,direction(f.distance<-2,f.distance>2),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
