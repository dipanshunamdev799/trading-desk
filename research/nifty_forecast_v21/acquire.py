"""Retrieve dated official reports and only the missing NSE cash archives."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from zipfile import ZipFile, is_zipfile

import requests

from .common import *

ARCHIVES = 'https://nsearchives.nseindia.com/content/cm/'
INDEX = 'https://niftyindices.com/'
MARKET_PAGE = INDEX + 'reports/monthly-reports'
WEIGHT = 'Market_Capitalisation_Weightage_Beta_for_NIFTY_50_And_NIFTY_Next_50/'
FAMILY = 'Indices_-_Market_Capitalisation_and_Weightage/'
AGENT = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
NOTICES = {
    '2025-06-13':'https://nsearchives.nseindia.com/content/circulars/FAOP68547.pdf',
    '2025-10-07':INDEX+'Press_Release/ind_prs07102025.pdf',
    '2025-11-13':INDEX+'Press_Release/ind_prs13112025.pdf',
}


def is_good(content, kind):
    return is_zipfile(BytesIO(content)) if kind == 'zip' else content.startswith(b'%PDF-')


def fetch(job):
    family, day, urls, file, kind = job
    p = OUT / file
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and is_good(p.read_bytes(), kind):
        return dict(family=family, day=day, file=file, url=urls[0], sha256=sha(p), bytes=p.stat().st_size, status='retained')
    attempts = []
    for url in urls:
        sent = now()
        try:
            ret = requests.get(url, headers=AGENT, timeout=(8, 16))
            actual = is_good(ret.content, kind)
            attempts.append(dict(url=url, code=ret.status_code, sent=sent, received=now(), server_date=ret.headers.get('Date'), valid=actual))
            if ret.ok and actual:
                p.write_bytes(ret.content)
                result = dict(family=family, day=day, file=file, url=ret.url, sha256=sha(p), bytes=p.stat().st_size,
                              status='accepted', attempts=attempts)
                if kind == 'zip':
                    with ZipFile(BytesIO(ret.content)) as archive:
                        result['members'] = archive.namelist()
                return result
        except requests.RequestException as exc:
            attempts.append(dict(url=url, sent=sent, error=type(exc).__name__))
    return dict(family=family, day=day, status='unavailable', attempts=attempts)


def run():
    register()
    raw = V17 / 'sources/cash-eod'
    days = cash().index
    known = []
    jobs = []
    for day in days:
        p = raw / f'{day}.zip'
        name = f"BhavCopy_NSE_CM_0_0_0_{day.replace('-', '')}_F_0000.csv.zip"
        url = ARCHIVES + name
        if p.exists():
            known.append(dict(family='cash', day=day, file=p.relative_to(ROOT).as_posix(), base='repository',
                              sha256=sha(p), bytes=p.stat().st_size, status='inherited', url=url))
        else:
            jobs.append(('cash',day,[url,url.replace('nsearchives.', 'archives.')],f'sources/cash/{day}.zip','zip'))
    for date in pd.date_range('2025-01-01', '2026-10-31', freq='ME'):
        day = date.strftime('%Y-%m-%d')
        file = f"mcwb_{date.strftime('%b%y').lower()}.zip"
        wide = f"indices_data{date.strftime('%b%Y')}.zip"
        a, b = INDEX + WEIGHT + file, INDEX + FAMILY + wide
        jobs.extend([
            ('nifty50_weights',day,[a,a.replace('://','://www.')],f'sources/weights/{day}.zip','zip'),
            ('index_families',day,[b,b.replace('://','://www.')],f'sources/index-families/{day}.zip','zip'),
        ])
    for day,url in NOTICES.items():
        jobs.append(('dated_actions',day,[url],f'sources/actions/{day}.pdf','pdf'))
    old = {(r['family'],r['day']):r for r in read('source-receipt.json')['records']} if (OUT/'source-receipt.json').is_file() else {}
    def retain(job):
        family,day,_,file,_ = job
        previous=old.get((family,day))
        if previous and (OUT/file).is_file() and previous.get('sha256')==sha(OUT/file):
            return previous
        return fetch(job)
    with ThreadPoolExecutor(max_workers=7) as pool:
        rows = list(pool.map(retain,jobs))
    save('source-receipt.json',dict(retrieved=now(),start=FIRST,end=FREEZE,scope='Historical; appended cash and monthly files only',
        monthly_index=MARKET_PAGE,methodology=INDEX+'Methodology/Method_NIFTY_Equity_Indices.pdf', records=known+rows))
    for family in ('cash','nifty50_weights','index_families'):
        good=[r for r in known+rows if r['family']==family and 'file' in r]
        print(family,len(good),'available files',flush=True)
        if family!='cash' and good:
            print('Examples:',[(r['day'], r.get('members',[])[:6]) for r in good[:2]],flush=True)


if __name__ == '__main__':
    run()
