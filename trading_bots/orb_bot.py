if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('orb','Opening range breakout','15-minute opening range with 0.25 ATR buffer and EMA alignment.',7,'ema_aligned','afternoon',{'range_minutes': 15, 'buffer_atr': 0.25})

def signals(f):
    return eligible(f,direction(f.close>f.orb_high15+.25*f.atr,f.close<f.orb_low15-.25*f.atr),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
