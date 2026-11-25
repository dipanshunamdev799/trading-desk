"""Re-execute the exact V8 duplication diagnostics in a V9 directory."""
from .common import OUT, save, write
from research.nifty_forecast_v8 import invariance


def run():
    invariance.save=lambda n,obj:save('duplicate-replay/'+n,obj)
    invariance.write=lambda n,obj:write('duplicate-replay/'+n,obj)
    invariance.run()
    invariance.run(sector_alias=True)


if __name__=='__main__':run()
