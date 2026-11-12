if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('compression_breakout','Compression breakout','Prior six-bar span below 3 ATR followed by a 1 ATR body breakout.',6,'trend','afternoon',{'prior_range_atr': 3, 'body_atr': 1})

def signals(f):
    compressed=(f.high6-f.low6)/f.atr<3
    return eligible(f,direction(compressed&(f.close>f.high6)&(f.body>1),compressed&(f.close<f.low6)&(f.body<-1)),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
