if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('failed_breakout','Failed breakout','Rejects a 20-bar range break and closes back inside.',2,'range','all',{'lookback': 20})

def signals(f):
    return eligible(f,direction((f.low<f.low20)&(f.close>f.low20)&(f.close>f.open),(f.high>f.high20)&(f.close<f.high20)&(f.close<f.open)),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
