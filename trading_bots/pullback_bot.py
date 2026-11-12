if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('pullback','EMA pullback','EMA9/21 pullback within 0.75 ATR, same-direction candle.',3,'ema_aligned','afternoon',{'slow': 21, 'tolerance_atr': 0.75})

def signals(f):
    return eligible(f,direction((f.ema9>f.ema21)&(f.low<=f.ema9+.75*f.atr)&(f.close>f.ema9)&(f.close>f.open),(f.ema9<f.ema21)&(f.high>=f.ema9-.75*f.atr)&(f.close<f.ema9)&(f.close<f.open)),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
