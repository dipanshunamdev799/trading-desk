if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from trading_bots.common.strategy import Definition, direction, eligible

DEFINITION=Definition('rsi_reversion','RSI mean reversion','RSI below 40/above 60 and price below/above EMA21 in a morning range.',11,'range','morning',{'rsi': 40, 'distance_atr': 0})

def signals(f):
    return eligible(f,direction((f.rsi<40)&(f.distance<0),(f.rsi>60)&(f.distance>0)),DEFINITION)

if __name__ == "__main__":
    from trading_bots.common.worker import run_cli
    run_cli(DEFINITION.id)
