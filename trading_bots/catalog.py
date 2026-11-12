import importlib

IDS=('ema_trend','failed_breakout','pullback','donchian','momentum','compression_breakout','orb','ema_reversion','gap_follow','gap_fade','rsi_reversion')


def strategy(bot_id):
    if bot_id not in IDS:raise ValueError('Unknown trading bot')
    return importlib.import_module('trading_bots.'+bot_id+'_bot')


def definitions():return [strategy(key).DEFINITION.json() for key in IDS]
