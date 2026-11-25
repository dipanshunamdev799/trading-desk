from pathlib import Path
import hashlib

SPECS = Path(__file__).with_name('specs')
START = '2025-01-01'
DAY0 = '2026-11-13'
END = '2026-12-31'
CAPITAL = 1_000_000.0
COST = .00225

CATALOG = {
    'C0_R': dict(name='C0-R', title='Volatility-adjusted momentum',
                 description='20-stock portfolio, reviewed every five sessions. Retain holdings inside the top 40.',
                 fingerprint='b7e95c049fc97184', books=1),
    'C1_R': dict(name='C1-R', title='Momentum with volatility targeting',
                 description='C0-R selection with a 15% annual volatility target and a 10-point exposure adjustment band.',
                 fingerprint='973ea8e007246aba', books=1),
    'C2_S': dict(name='C2-S', title='Five staggered momentum books',
                 description='Five independent ₹2 lakh books, each holding up to 20 stocks on a different rebalance phase.',
                 fingerprint='a5a369d9565d8938', books=5),
    'C0_R_X': dict(name='C0-R-X', title='Momentum with auction evidence',
                   description='C0-R mechanics; simulated fills require prospective auction evidence classified as likely.',
                   fingerprint='3d1228a7750225ed', books=1),
}


def definition(bot_id):
    if bot_id not in CATALOG:
        raise ValueError('Unknown investment bot')
    item = CATALOG[bot_id]
    document = SPECS / (item['name'] + '.md')
    return dict(id=bot_id, **item, category='investment', mode='paper', capital=CAPITAL,
                day0=DAY0, window_end=END, source_config_version='124623e3a4b1db81',
                implementation='specification-adapter-v1',
                verification='Historical parity pending: original daily panel and metadata are required',
                specification_sha256=hashlib.sha256(document.read_bytes()).hexdigest(),
                parameters=dict(universe=300, momentum_sessions=63, volatility_sessions=42,
                                holdings_per_book=20, retain_below_rank=40, industry_cap=6,
                                rebalance_sessions=5, cost_per_side=COST))
