"""Read-only current integration coverage; do not materialize repeated snapshots as labels."""
import sys
from .common import *
def run():
    sys.path[:0]=[str(ROOT/'backend')]
    from app.config import get_settings
    from sqlalchemy import create_engine,text
    eng=create_engine(get_settings().database_url_sync,connect_args={'connect_timeout':8});out={}
    queries={'schema':"SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,column_name",
      'methods':"SELECT method,count(*) n,min(fetched_at) first,max(fetched_at) last FROM market_datasets GROUP BY method",
      'historical_identities':"SELECT DISTINCT method,parameters->>'instrument_key' instrument_key FROM market_datasets WHERE method LIKE '%historical%' LIMIT 1000"}
    for n,q in queries.items():
        try:
            with eng.connect() as c:c.execute(text('SET statement_timeout=10000'));out[n]=[dict(r) for r in c.execute(text(q)).mappings()]
        except Exception as e:out[n]={'error':type(e).__name__}
    eng.dispose();save('database-audit.json',out);print('Read-only database inventory complete',flush=True)
if __name__=='__main__':run()
