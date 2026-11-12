if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('donchian','Donchian breakout','Six-bar breakout with an afternoon trend filter.',4,'trend','afternoon',{'lookback': 6, 'buffer_atr': 0})

def signals(f):
    return eligible(f,direction(f.close>f.high6,f.close<f.low6),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
