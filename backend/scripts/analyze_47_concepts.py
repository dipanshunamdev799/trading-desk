"""Reproducible, causal NIFTY 47-concept research. Never places orders.

Run from project root: .venv/Scripts/python.exe backend/scripts/analyze_47_concepts.py
Use --fetch to refresh the frozen raw-data snapshot, otherwise replay it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT)]
from app.services import price_action as pa

OUT = ROOT / "artifacts" / "concept_research_2026-10-29"
REPORT = ROOT / "FINDINGS_47_CONCEPTS_1M_5M_LAST_7_DAYS.md"
ASOF = "2026-10-30T05:16:12+00:00"
PRIMARY_START, END = "2026-10-23", "2026-10-29"
SENS_START = "2026-10-21"
KEY = "NSE_INDEX|Nifty 50"
PROXIES = {"NIFTYBEES": "NSE_EQ|INF204KB14I2", "RELIANCE": "NSE_EQ|INE002A01018",
           "HDFCBANK": "NSE_EQ|INE040A01034", "ICICIBANK": "NSE_EQ|INE090A01021"}
RNG = np.random.default_rng(470105)


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, default=str, indent=2, allow_nan=False), encoding="utf-8")


def fetch_snapshot():
    from app.services.upstox_service import get_upstox
    client = get_upstox()
    snap = {"asof": ASOF, "primary_start": PRIMARY_START, "end": END, "proxies": {}, "retrieval": []}
    calls = [("index_1m", KEY, "minutes", 1, "2026-10-19"),
             ("index_5m_native", KEY, "minutes", 5, "2026-10-19"),
             ("daily", KEY, "days", 1, "2026-09-21")]
    calls += [(name, key, "minutes", 1, "2026-10-19") for name, key in PROXIES.items()]
    for name, key, unit, grain, first in calls:
        result = client.get_historical_candles_v3(key, unit, grain, END, first)
        rows = result.get("candles", [])
        if name in PROXIES:
            snap["proxies"][name] = rows
        else:
            snap[name] = rows
        snap["retrieval"].append({"name": name, "instrument_key": key, "source": result.get("_source"),
                                  "partial": result.get("_partial", False), "rows": len(rows)})
        print("snapshot", name, len(rows), flush=True)
    # Original in-progress session is diagnostic only; never used to fit/select signals.
    from sqlalchemy import create_engine, text
    from app.config import get_settings
    with create_engine(get_settings().database_url_sync).connect() as conn:
        snap["partial_oct30"] = [list(r) for r in conn.execute(text(
            "SELECT ts,open,high,low,close,volume,oi FROM candles WHERE instrument_key=:key "
            "AND interval='1minute' AND ts >= '2026-10-30T00:00:00+05:30' AND ts <= :cut ORDER BY ts"),
            {"key": KEY, "cut": ASOF})]
    dump("snapshot.json", snap)
    return json.loads((OUT / "snapshot.json").read_text(encoding="utf-8"))


def frame(rows):
    d = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume", "oi"])
    d["ts"] = pd.to_datetime(d.ts, utc=True).dt.tz_convert("Asia/Kolkata")
    for col in ["open", "high", "low", "close", "volume", "oi"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    return d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)


def regular(d):
    minute = d.ts.dt.hour * 60 + d.ts.dt.minute
    return d[(minute >= 555) & (minute < 930)].copy().reset_index(drop=True)


def aggregate(d):
    d = d.copy()
    d["bucket"] = d.ts.dt.floor("5min")
    a = d.groupby("bucket").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                close=("close", "last"), volume=("volume", "sum"), oi=("oi", "last"), n=("close", "size"))
    a = a[a.n == 5].drop(columns="n").reset_index().rename(columns={"bucket": "ts"})
    return a


def serialize(d):
    return [{**r, "ts": r["ts"].isoformat()} for r in d.to_dict("records")]


def deoverlap(d, horizon):
    """One position at a time, per session; entry is next candle open."""
    keep, last_exit = [], {}
    for idx, r in d.sort_values(["day", "bar"]).iterrows():
        if r.bar >= last_exit.get(r.day, -1):
            keep.append(idx)
            last_exit[r.day] = r.bar + horizon
    return d.loc[keep]


def wilson(wins, n):
    if not n:
        return [None, None]
    p, z = wins/n, 1.96
    den = 1+z*z/n
    mid = (p+z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [100*(mid-half), 100*(mid+half)]


def features(d, grain, daily, proxies):
    d = regular(d)
    d["day"] = d.ts.dt.strftime("%Y-%m-%d")
    d["bar"] = d.groupby("day").cumcount()
    tr = np.maximum(d.high-d.low, np.maximum((d.high-d.groupby("day").close.shift()).abs(),
                                           (d.low-d.groupby("day").close.shift()).abs()))
    tr = pd.Series(tr, index=d.index).fillna(d.high-d.low)
    # Auction freezes must not collapse next morning's ATR warm-up.
    continuous=d.ts.dt.hour*60+d.ts.dt.minute<915
    d["atr"] = tr.loc[continuous].rolling(14, min_periods=5).mean().shift(1).reindex(d.index).ffill()
    d["known_at"] = d.ts + pd.Timedelta(minutes=grain)
    # Signals/data above ASOF are excluded even during historical replay.
    d = d[d.known_at <= pd.Timestamp(ASOF)].reset_index(drop=True)
    pieces, all_events, studies, causal_checks = [], [], {}, []
    daily_rows = serialize(daily)
    for day, b in d.groupby("day", sort=True):
        b = b.copy()
        c, o, hi, lo, atr = b.close, b.open, b.high, b.low, b.atr.replace(0, np.nan)
        span = (hi-lo).replace(0, np.nan)
        b["p_ret1"] = c.diff()/atr
        b["p_ret3"] = c.diff(3)/atr
        b["p_ret6"] = c.diff(6)/atr
        e9, e21 = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
        b["p_ema_gap"] = (e9-e21)/atr
        b["p_close_ema"] = (c-e9)/atr
        b["p_ema_slope"] = e9.diff(3)/atr
        delta = c.diff()
        gain, loss = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean(), (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        b["p_rsi"] = gain/(gain+loss)
        b["p_body"] = (c-o)/span
        b["p_close_position"] = (c-lo)/span
        b["p_range_atr"] = (hi-lo)/atr
        b["p_atr_fraction"] = atr/c*10000
        b["p_prev20_high"] = (c-hi.shift().rolling(20, min_periods=1).max())/atr
        b["p_prev20_low"] = (c-lo.shift().rolling(20, min_periods=1).min())/atr
        b["p_day_high"] = (c-hi.shift().cummax())/atr
        b["p_day_low"] = (c-lo.shift().cummin())/atr
        b["p_compression"] = (hi.rolling(5, min_periods=5).max()-lo.rolling(5, min_periods=5).min())/atr
        b["p_from_open"] = (c-o.iloc[0])/atr
        b["p_round_distance"] = (c-(c/100).round()*100)/atr
        elapsed = (b.ts.dt.hour*60+b.ts.dt.minute-555)/360
        b["p_time_sin"], b["p_time_cos"] = np.sin(np.pi*elapsed), np.cos(np.pi*elapsed)
        previous = daily[daily.ts.dt.strftime("%Y-%m-%d") < day]
        b["p_pdh"] = (c-previous.high.iloc[-1])/atr if len(previous) else np.nan
        b["p_pdl"] = (c-previous.low.iloc[-1])/atr if len(previous) else np.nan
        b["p_open_gap"] = (o.iloc[0]-previous.close.iloc[-1])/atr if len(previous) else np.nan
        orb = b[b.ts.dt.hour*60+b.ts.dt.minute < 570]
        b["p_orb_high"] = np.where(b.known_at.dt.hour*60+b.known_at.dt.minute >= 570, (c-orb.high.max())/atr, np.nan)
        b["p_orb_low"] = np.where(b.known_at.dt.hour*60+b.known_at.dt.minute >= 570, (c-orb.low.min())/atr, np.nan)
        rows = serialize(b[["ts", "open", "high", "low", "close", "volume", "oi"]])
        study = pa.analyze(rows, f"{grain}minute", daily=daily_rows, session=day,
                           now=pd.Timestamp(ASOF).to_pydatetime(), orb_minutes=15, round_step=100)
        studies[day] = study
        pos = {ts: idx for idx, ts in zip(b.index, b.ts.map(lambda x:x.isoformat()))}
        for event in study["events"]:
            event = {**event, "day": day, "grain": grain, "row": pos[event["ts"]],
                     "bar": int(b.loc[pos[event["ts"]], "bar"])}
            all_events.append(event)
        # Each concept gets separate bullish, bearish and neutral recent-event channels.
        # 7,8,9,12 are continuous references, represented in p_* distances above.
        for concept in range(1, 48):
            for side, suffix in [(1, "up"), (-1, "down"), (0, "neutral")]:
                values = pd.Series(0., index=b.index)
                for event in study["events"]:
                    if event["concept"] == concept and event["side"] == side:
                        values.loc[pos[event["ts"]]] = 1.
                b[f"c{concept:02}_{suffix}"] = values.rolling(max(1, 5//grain), min_periods=1).max()
        # Verify event prefix invariance on real candles, at three times in each session.
        for count in sorted(set([min(30, len(rows)), len(rows)//2, max(1,len(rows)-20)])):
            prefix = pa.analyze(rows[:count], f"{grain}minute", daily=daily_rows, session=day,
                                now=pd.Timestamp(ASOF).to_pydatetime(), orb_minutes=15, round_step=100)
            wanted = [e for e in study["events"] if pd.Timestamp(e["known_at"]) <= b.known_at.iloc[count-1]]
            ok = prefix["events"] == wanted
            causal_checks.append({"day": day, "grain": grain, "prefix_bars": count, "pass": ok})
            assert ok, (day, grain, count)
        pieces.append(b)
    d = pd.concat(pieces, ignore_index=True)
    # Align trade-volume proxies by candle start, so all values are known at candle close.
    for name, raw in proxies.items():
        p = regular(raw) if grain == 1 else aggregate(regular(raw))
        p = p.set_index("ts")
        vols = d.ts.map(p.volume).astype(float)
        close = d.ts.map(p.close).astype(float)
        opn = d.ts.map(p.open).astype(float)
        d[f"rawvol_{name}"] = vols
        prior = vols.groupby(d.day).transform(lambda v: v.shift().rolling(max(3,20//grain), min_periods=3).median())
        rvol = vols/prior.replace(0,np.nan)
        d[f"v_{name}_rvol"] = np.log1p(rvol.clip(0,20))
        d[f"v_{name}_signed"] = np.sign(close-opn)*np.log1p(rvol.clip(0,20))
        d[f"v_{name}_return"] = close.groupby(d.day).pct_change()*10000
        d[f"v_{name}_missing"] = vols.isna().astype(float)
        # Intraday VWAP uses this traded proxy's own typical prices and volume.
        typical = d.ts.map((p.high+p.low+p.close)/3).astype(float)
        vwap = (typical*vols).groupby(d.day).cumsum()/vols.groupby(d.day).cumsum().replace(0,np.nan)
        d[f"v_{name}_vwap_gap"] = (close/vwap-1)*10000
    d["v_basket_rvol"] = d[[f"v_{n}_rvol" for n in PROXIES if n != "NIFTYBEES"]].mean(axis=1)
    for horizon in [5,15,30]:
        h = horizon//grain
        entry = d.groupby("day").open.shift(-1)
        exit_ = d.groupby("day").close.shift(-h)
        exit_time = d.groupby("day").known_at.shift(-h)
        d[f"ret_{horizon}"] = exit_-entry
        d[f"ret_all_{horizon}"] = exit_-entry
        d[f"entry_{horizon}"] = entry
        d[f"exit_time_{horizon}"] = exit_time
        # Avoid CAS price setting: every modeled holding window ends by 15:15 IST.
        valid = (exit_time.dt.hour*60+exit_time.dt.minute <= 915) & d.atr.gt(0)
        d.loc[~valid, f"ret_{horizon}"] = np.nan
        maxup, maxdown, barrier = [], [], []
        for i,r in d.iterrows():
            fut = d.iloc[i+1:i+h+1]
            if pd.isna(r[f"ret_{horizon}"]) or len(fut)!=h or (fut.day!=r.day).any():
                maxup.append(np.nan); maxdown.append(np.nan); barrier.append(np.nan); continue
            en = r[f"entry_{horizon}"]
            maxup.append(float(fut.high.max()-en)); maxdown.append(float(en-fut.low.min()))
            outcome = 0
            for _, q in fut.iterrows():
                up, down = q.high >= en+r.atr, q.low <= en-r.atr
                if up or down:
                    outcome = 2 if up and down else 1 if up else -1
                    break
            barrier.append(outcome)
        d[f"mfe_up_{horizon}"], d[f"mfe_down_{horizon}"] = maxup,maxdown
        d[f"barrier_{horizon}"] = barrier
    return d, pd.DataFrame(all_events), studies, causal_checks


def bh(pvals):
    pvals=np.asarray(pvals)
    order=np.argsort(pvals); ranked=pvals[order]
    adjusted=np.minimum.accumulate((ranked*len(ranked)/np.arange(1,len(ranked)+1))[::-1])[::-1]
    result=np.empty(len(pvals)); result[order]=np.minimum(1,adjusted)
    return result


def signal_stats(d, mask, sides, horizon=15, permutations=499):
    z=d.loc[mask & d[f"ret_{horizon}"].notna()].copy()
    z["direction"]=np.asarray(sides)[z.index]
    z=z[z.direction!=0]
    raw=len(z)
    z=deoverlap(z,horizon//int(d.attrs["grain"]))
    if not len(z): return {"n":0,"raw":raw}
    signed=z[f"ret_{horizon}"]*z.direction
    wins=int((signed>0).sum())
    # Side + same session + half-hour baseline controls drift and time of day.
    bucket=(d.ts.dt.hour*60+d.ts.dt.minute)//30
    pool=d[d[f"ret_{horizon}"].notna()].copy()
    pool["bucket"]=bucket.loc[pool.index]
    base=pool.groupby(["day","bucket"])[f"ret_{horizon}"].mean()
    expected=np.array([base.loc[(r.day,bucket.loc[i])]*r.direction for i,r in z.iterrows()])
    excess=signed.to_numpy()-expected
    daily=(z.assign(signed=signed,excess=excess).groupby("day").agg(n=("signed","size"),mean=("signed","mean"),excess=("excess","mean"))).reset_index().to_dict("records")
    # Circularly shift the forward-return series within each session, preserving autocorrelation.
    if permutations:
        null=np.zeros(permutations)
        for day,g in z.groupby("day"):
            full=pool[pool.day==day]
            vals=full[f"ret_{horizon}"].to_numpy()
            loc={ix:j for j,ix in enumerate(full.index)}
            locations=np.array([loc[ix] for ix in g.index])
            shifts=RNG.integers(0,len(vals),size=permutations)
            null += (vals[(locations[None,:]+shifts[:,None])%len(vals)]*g.direction.to_numpy()[None,:]).sum(axis=1)/len(z)
        p=float((1+(null>=signed.mean()).sum())/(permutations+1))
    else: p=None
    hit=z[f"barrier_{horizon}"]*z.direction
    return {"n":len(z),"raw":raw,"wins":wins,"win_pct":100*wins/len(z),"wilson":wilson(wins,len(z)),
            "mean":float(signed.mean()),"median":float(signed.median()),"mean_atr":float((signed/z.atr).mean()),
            "cost2":float(signed.mean()-2),"cost5":float(signed.mean()-5),"matched_mean":float(np.mean(expected)),
            "excess":float(excess.mean()),"days":len(daily),"positive_days":sum(x["mean"]>0 for x in daily),
            "daily":daily,"p":p,"tp_first_pct":float(100*(hit==1).mean()),
            "sl_first_pct":float(100*((hit==-1)|(np.abs(hit)==2)).mean()),
            "barrier_ambiguous":int((np.abs(hit)==2).sum())}


def concept_analysis(d,e,start=PRIMARY_START):
    selected=d.day.between(start,END)
    stats=[]
    for n in range(1,48):
        ev=e[e.concept==n]
        dirs=pd.Series(0.,index=d.index)
        # Opposing same-bar signals cancel; they cannot count as two opportunities.
        for row,g in ev.groupby("row"):
            dirs.loc[row]=np.sign(g.side.sum())
        item={"id":n,"label":pa.BY_ID[n]["label"],"events":int(ev.day.between(start,END).sum()),
              "bull":int(((ev.side==1)&ev.day.between(start,END)).sum()),
              "bear":int(((ev.side==-1)&ev.day.between(start,END)).sum()),
              "neutral":int(((ev.side==0)&ev.day.between(start,END)).sum())}
        for horizon in [5,15,30]:
            item[str(horizon)]=signal_stats(d,selected & dirs.ne(0),dirs.to_numpy(),horizon,
                                           permutations=499 if horizon==15 else 0)
        stats.append(item)
    valid=[x for x in stats if x["15"]["n"]>=5]
    if valid:
        for item,q in zip(valid,bh([x["15"]["p"] for x in valid])): item["q"]=float(q)
    return stats


def rule_masks(d,e):
    def recent(ids,minutes=5):
        sign=pd.Series(0.,index=d.index)
        for row,g in e[e.concept.isin(ids)].groupby("row"): sign.loc[row]=np.sign(g.side.sum())
        # Sum distinct event times; zero means conflict/no directional evidence.
        return sign.groupby(d.day).transform(lambda x: np.sign(x.rolling(max(1,minutes//d.attrs["grain"]),min_periods=1).sum()))
    momentum=np.sign(d.p_ema_gap).fillna(0)
    retest=recent([6,13,14],minutes=5)
    reversal=recent([11,15,20],minutes=5)
    displacement=recent([40,43,45,46],minutes=5)
    fvg=recent([44],minutes=5)
    confluence=recent([1,2,6,11,13,14,15,19,20,32,33,39,42],minutes=5)
    volume=d.v_NIFTYBEES_rvol>=np.log(2.5)  # rvol >= 1.5, using preceding rolling median.
    signedvol=np.sign(d.v_NIFTYBEES_signed)
    rules={
      "EMA9/21 trend":(momentum!=0,momentum),
      "3-bar continuation":(d.p_ret3.notna(),np.sign(d.p_ret3).fillna(0)),
      "3-bar fade":(d.p_ret3.notna(),-np.sign(d.p_ret3).fillna(0)),
      "Retest + EMA alignment":((retest!=0)&(retest==momentum),retest),
      "Retest against EMA":((retest!=0)&(retest==-momentum),retest),
      "Sweep/failed break/CHoCH + EMA alignment":((reversal!=0)&(reversal==momentum),reversal),
      "Displacement family + EMA alignment":((displacement!=0)&(displacement==momentum),displacement),
      "Displacement family fade":(displacement!=0,-displacement),
      "FVG + EMA alignment":((fvg!=0)&(fvg==momentum),fvg),
      "Structure/setup + EMA alignment":((confluence!=0)&(confluence==momentum),confluence),
      "Structure/setup + EMA + ETF RVOL>=1.5":((confluence!=0)&(confluence==momentum)&volume,confluence),
      "Structure/setup + EMA + signed ETF volume":((confluence!=0)&(confluence==momentum)&(signedvol==confluence)&volume,confluence),
      "EMA + signed ETF RVOL>=1.5":((momentum!=0)&(signedvol==momentum)&volume,momentum),
      "Compression break direction":((d.groupby("day").p_compression.shift()<=2)&(d.p_range_atr>=1.5),np.sign(d.p_ret1).fillna(0)),
    }
    if "m_ema_gap" in d:
        aligned=(momentum==np.sign(d.m_ema_gap))
        rules["1m setup + both EMA trends"] = ((confluence!=0)&(confluence==momentum)&aligned,confluence)
        rules["Both EMA trends + signed ETF RVOL>=1.5"] = ((momentum!=0)&aligned&volume&(signedvol==momentum),momentum)
    return rules


def fit_transform(train,test,cols):
    a=train[cols].to_numpy(float); b=test[cols].to_numpy(float)
    with np.errstate(all="ignore"):
        med=np.array([np.nanmedian(a[:,j]) if np.isfinite(a[:,j]).any() else 0 for j in range(a.shape[1])])
    a=np.where(np.isfinite(a),a,med); b=np.where(np.isfinite(b),b,med)
    mean=a.mean(0); sd=a.std(0); sd[sd<1e-6]=1
    return np.clip((a-mean)/sd,-8,8),np.clip((b-mean)/sd,-8,8)


def sigmoid(x): return 1/(1+np.exp(-np.clip(x,-25,25)))


def logistic(a,y,b,penalty=.20):
    x=np.column_stack([np.ones(len(a)),a]); xt=np.column_stack([np.ones(len(b)),b])
    w=np.zeros(x.shape[1]); w[0]=math.log((y.mean()+.001)/(1.001-y.mean()))
    reg=np.ones(len(w))*penalty;reg[0]=0
    for _ in range(25):
        p=sigmoid(x@w); curvature=np.maximum(p*(1-p),1e-5)
        grad=x.T@(p-y)/len(y)+reg*w
        hess=(x.T*curvature)@x/len(y)+np.diag(reg+1e-6)
        step=np.linalg.solve(hess,grad);w-=step
        if np.max(np.abs(step))<1e-6:break
    return sigmoid(xt@w),w[1:]


def stump_boost(a,y,b):
    # Deterministic additive logistic model: 60 depth-one trees, learning rate .08.
    n=len(y); minleaf=max(15,int(n*.05)); intercept=math.log((y.mean()+.001)/(1.001-y.mean()))
    pred=np.full(n,intercept); test=np.full(len(b),intercept); importance=np.zeros(a.shape[1])
    splits=[]
    for j in range(a.shape[1]):
        for threshold in np.unique(np.quantile(a[:,j],[.15,.3,.5,.7,.85])):
            mask=a[:,j]<=threshold
            if min(mask.sum(),(~mask).sum())>=minleaf: splits.append((j,threshold,mask))
    for _ in range(60):
        p=sigmoid(pred);res=y-p;h=p*(1-p);best=None
        for j,t,m in splits:
            l,r=res[m].sum(),res[~m].sum();hl,hr=h[m].sum()+5,h[~m].sum()+5
            gain=l*l/hl+r*r/hr
            if best is None or gain>best[0]:best=(gain,j,t,m,l/hl,r/hr)
        if best is None:break
        gain,j,t,m,l,r=best;pred+=.08*np.where(m,l,r);test+=.08*np.where(b[:,j]<=t,l,r);importance[j]+=gain
    return sigmoid(test),importance


def auc(y,p):
    if min(y.sum(),len(y)-y.sum())==0:return None
    rank=pd.Series(p).rank().to_numpy()
    return float((rank[y==1].sum()-y.sum()*(y.sum()+1)/2)/(y.sum()*(len(y)-y.sum())))


def classification_metrics(y,p):
    p=np.clip(p,.00001,.99999);pred=(p>=.5).astype(int)
    recalls=[(pred[y==v]==v).mean() for v in [0,1] if (y==v).any()]
    return {"n":len(y),"accuracy":float((pred==y).mean()),"balanced_accuracy":float(np.mean(recalls)),
            "auc":auc(y,p),"brier":float(np.mean((p-y)**2)),
            "logloss":float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))}


def model_analysis(d,start=PRIMARY_START):
    pcols=[c for c in d if c.startswith("p_")]
    ccols=[c for c in d if c.startswith("c") and len(c)>4 and c[1:3].isdigit()]
    vcols=[c for c in d if c.startswith("v_")]
    mcols=[c for c in d if c.startswith("m_")]
    configs=[("Logistic price",pcols,"logistic"),("Logistic concepts",ccols,"logistic"),
             ("Logistic price+concepts",pcols+ccols,"logistic"),
             ("Logistic price+volume",pcols+vcols,"logistic"),
             ("Logistic all",pcols+ccols+vcols,"logistic"),
             ("Boosted stumps all",pcols+ccols+vcols,"boost"),
             ("Ridge return all",pcols+ccols+vcols,"ridge")]
    if mcols:configs.append(("Logistic all+closed5m",pcols+ccols+vcols+mcols,"logistic"))
    selected=d[d.day.between(start,END)&d.ret_15.notna()&d.ret_15.ne(0)].copy()
    days=sorted(selected.day.unique()); results=[];predrows=[]
    for name,cols,kind in configs:
        folds=[];coeffs=[];all_test=[]
        for day in days[2:]:
            tr=selected[selected.day<day];te=selected[selected.day==day].copy()
            a,b=fit_transform(tr,te,cols);y=(tr.ret_15>0).to_numpy(float)
            if kind=="boost": prob,coef=stump_boost(a,y,b)
            elif kind=="ridge":
                target=(tr.ret_15/tr.atr).clip(-10,10).to_numpy(float)
                xa=np.column_stack([np.ones(len(a)),a]); xb=np.column_stack([np.ones(len(b)),b])
                reg=np.diag(np.r_[0,np.full(a.shape[1],.5)])
                coef_full=np.linalg.solve(xa.T@xa/len(a)+reg+np.eye(xa.shape[1])*1e-6,xa.T@target/len(a))
                prob=sigmoid(xb@coef_full);coef=coef_full[1:]
            else:prob,coef=logistic(a,y,b)
            te["prob"]=prob;te["model"]=name;te["direction"]=np.where(prob>=.5,1,-1)
            te["train_up"]=y.mean()
            met=classification_metrics((te.ret_15>0).to_numpy(int),prob)
            met.update(day=day,train_n=len(tr),train_sessions=int(tr.day.nunique()))
            folds.append(met);all_test.append(te);coeffs.append(dict(zip(cols,map(float,coef))))
        z=pd.concat(all_test)
        y=(z.ret_15>0).to_numpy(int);prob=z.prob.to_numpy()
        met=classification_metrics(y,prob)
        trades=deoverlap(z,15//d.attrs["grain"])
        confident=deoverlap(z[(z.prob>=.6)|(z.prob<=.4)],15//d.attrs["grain"])
        signed=trades.ret_15*trades.direction
        cs=confident.ret_15*confident.direction
        daily=trades.assign(pnl=signed).groupby("day").pnl.mean()
        met.update(name=name,features=len(cols),folds=folds,trade_n=len(trades),trade_win=float((signed>0).mean()),
                   mean_points=float(signed.mean()),net2=float(signed.mean()-2),net5=float(signed.mean()-5),
                   positive_days=int((daily>0).sum()),trade_days=len(daily),
                   confident_n=len(confident),confident_mean=float(cs.mean()) if len(cs) else None,
                   confident_win=float((cs>0).mean()) if len(cs) else None,
                   coefficients=sorted(coeffs[-1].items(),key=lambda x:abs(x[1]),reverse=True)[:15],
                   final_day=folds[-1])
        results.append(met)
        predrows.extend(z[["ts","day","bar","model","prob","ret_15","atr","train_up"]].to_dict("records"))
    # All baselines use identical dates/eligible rows to models, with no fitting on future labels.
    z=selected[selected.day.isin(days[2:])]
    baselines=[]
    for name,prob in [("Always up",np.ones(len(z))*.999),("Always down",np.ones(len(z))*.001),
                      ("EMA direction",np.where(z.p_ema_gap>=0,.7,.3)),
                      ("3-bar continuation",np.where(z.p_ret3>=0,.7,.3)),
                      ("3-bar fade",np.where(z.p_ret3>=0,.3,.7))]:
        met=classification_metrics((z.ret_15>0).to_numpy(int),prob)
        t=deoverlap(z,15//d.attrs["grain"]);directions=pd.Series(np.where(prob>=.5,1,-1),index=z.index)
        signed=t.ret_15*directions.loc[t.index]
        met.update(name=name,trade_n=len(t),mean_points=float(signed.mean()),net2=float(signed.mean()-2))
        baselines.append(met)
    dump(f"predictions_{d.attrs['grain']}m_{start}.json",predrows)
    return {"models":results,"baselines":baselines,"test_days":days[2:]}


def magnitude_analysis(d,e):
    eligible=d.day.between(PRIMARY_START,END)&d.ret_15.notna()
    target=d.ret_15.abs()/d.atr>=1
    conditions={"All eligible bars":eligible,"Prior 5-bar compression <=2 ATR":d.groupby("day").p_compression.shift()<=2,
                "Current range >=1.5 ATR":d.p_range_atr>=1.5,
                "ETF RVOL >=1.5":d.v_NIFTYBEES_rvol>=np.log(2.5),
                "ETF RVOL <1":d.v_NIFTYBEES_rvol<np.log(2),
                "EMA separation >=0.5 ATR":d.p_ema_gap.abs()>=.5}
    for n in [3,25,26,41]:conditions[f"Concept {n}: {pa.BY_ID[n]['label']}"]=d.index.isin(e.loc[e.concept==n,"row"])
    results=[]
    for label,mask in conditions.items():
        z=deoverlap(d.loc[eligible&mask],15//d.attrs["grain"])
        if len(z):results.append({"name":label,"n":len(z),"move1atr_pct":float(100*target.loc[z.index].mean()),
                                  "abs_mean":float(z.ret_15.abs().mean()),"abs_mean_atr":float((z.ret_15.abs()/z.atr).mean())})
    return results


def audit(snapshot,index,native,daily,proxy):
    agg=aggregate(index)
    common=agg.merge(native,on="ts",suffixes=("_agg","_native"))
    mismatches=[]
    for field in ["open","high","low","close"]:
        err=(common[field+"_agg"]-common[field+"_native"]).abs()
        mismatches.append({"field":field,"n":len(common),"above_0_011":int((err>.011).sum()),
                           "max_abs_error":float(err.max())})
    coverage=[]
    for day,b in regular(index).groupby(index.ts.dt.strftime("%Y-%m-%d")):
        if day<SENS_START:continue
        valid=((b.low<=b[["open","close"]].min(axis=1))&(b.high>=b[["open","close"]].max(axis=1))&
               (b.low<=b.high)&b[["open","high","low","close"]].gt(0).all(axis=1))
        continuous=b[b.ts.dt.hour*60+b.ts.dt.minute<915]
        auction=b[b.ts.dt.hour*60+b.ts.dt.minute>=915]
        coverage.append({"day":day,"bars1":len(b),"continuous1":len(continuous),
                         "bars5":int((agg.ts.dt.strftime("%Y-%m-%d")==day).sum()),
                         "native5":int((native.ts.dt.strftime("%Y-%m-%d")==day).sum()),
                         "invalid":int((~valid).sum()),"zero_range":int((b.high==b.low).sum()),
                         "flat_auction_bars":int((auction.high==auction.low).sum()),
                         "open":float(b.open.iloc[0]),"high":float(b.high.max()),"low":float(b.low.min()),
                         "continuous_last":float(continuous.close.iloc[-1]),"official_last":float(b.close.iloc[-1]),
                         "cts_change":float(continuous.close.iloc[-1]-b.open.iloc[0]),
                         "auction_change":float(b.close.iloc[-1]-continuous.close.iloc[-1])})
    prior=[]
    for day in [x["day"] for x in coverage]:
        q=daily[daily.ts.dt.strftime("%Y-%m-%d")<day].iloc[-1]
        intr=index[index.ts.dt.strftime("%Y-%m-%d")<day]
        last_intr=intr.ts.dt.strftime("%Y-%m-%d").max()
        prior.append({"day":day,"daily_reference":q.ts.strftime("%Y-%m-%d"),"latest_prior_intraday":last_intr,
                      "stale":q.ts.strftime("%Y-%m-%d")!=last_intr})
    volumes=[]
    for name,p in proxy.items():
        z=regular(p);z=z[z.ts.dt.strftime("%Y-%m-%d").between(PRIMARY_START,END)]
        volumes.append({"name":name,"bars":len(z),"positive":int(z.volume.gt(0).sum()),
                        "zero":int(z.volume.eq(0).sum()),"missing":int(z.volume.isna().sum())})
    return {"coverage":coverage,"5m_reconciliation":mismatches,"prior_daily":prior,"volume":volumes,
            "index_volume_positive":int(index.volume.gt(0).sum()),"partial_oct30_bars":len(snapshot.get("partial_oct30",[])),
            "retrieval":snapshot["retrieval"]}


def mdtable(headers,rows):
    clean=lambda s:str(s).replace("|","/").replace("\n"," ")
    return "| "+" | ".join(map(clean,headers))+" |\n| "+" | ".join(["---"]*len(headers))+" |\n"+"\n".join("| "+" | ".join(map(clean,r))+" |" for r in rows)+"\n"


def f(value,digits=2):return "—" if value is None or not np.isfinite(value) else f"{value:.{digits}f}"


def write_report(results,checks,snapshot_hash):
    au=results["audit"]
    text=["# NIFTY 50: all 47 concepts on 1-minute and 5-minute charts",
          "## Scope and main conclusion",
          "Research date: **29 October 2026, America/Los_Angeles**. Frozen decision cutoff: **30 October 2026, 05:16:12 UTC / 10:46:12 IST**. Instrument: `NSE_INDEX|Nifty 50`, the default instrument of this workspace’s 47-concept study.",
          "The main window is **23–29 October 2026 inclusive**, seven completed calendar dates, containing **five trading sessions: 23, 26, 27, 28 and 29 October**. The seven-session sensitivity window adds 21 and 22 October. The ongoing 30 October session is excluded: it is incomplete, in a different market date, and not a comparable full-day test. This definition avoids silently calling five sessions seven trading days.",
          "**Interpretation:** Results below test forward movement after a signal is observable. High event counts and a good fit to these few days do not establish a stable predictive edge. The strongest useful candidate must beat directional drift, survive later-day testing and still have positive movement after a stated cost assumption. All rules/model families are reported, including failures.",
          "## Data audit",
          mdtable(["Session IST","1m bars","5m derived / native","Open","15:15 value","Final value","Continuous change","Auction change"],
                  [[x["day"],x["bars1"],f"{x['bars5']} / {x['native5']}",f(x["open"]),f(x["continuous_last"]),f(x["official_last"]),f(x["cts_change"]),f(x["auction_change"])] for x in au["coverage"]]),
          "The source has 375 one-minute bars per full session (09:15–15:29), including the final auction-related interval. Main analysis uses **09:15–15:15**, and each forward holding period must finish by 15:15. The full 09:15–15:30 window is a sensitivity check. NSE’s schedule places CAS for eligible cash stocks from 15:15, with order matching following random order-entry closure. Index levels in that interval therefore need different interpretation from continuous price discovery. [NSE CAS schedule](https://www.nseindia.com/static/products-services/closing-auction-session).",
          "Five-minute candles are rebuilt from exactly five consecutive one-minute bars, aligned at 09:15. This gives the same underlying observations for both timeframes and does not treat them as independent datasets. Native five-minute candles were also retrieved and compared:",
          mdtable(["Field","Compared bars","Differences >0.011 points","Maximum difference"],[[x["field"],x["n"],x["above_0_011"],f(x["max_abs_error"],4)] for x in au["5m_reconciliation"]]),
          mdtable(["Session","Daily reference used by production study","Most recent prior intraday session","Reference stale?"],[[x["day"],x["daily_reference"],x["latest_prior_intraday"],x["stale"]] for x in au["prior_daily"]]),
          "The production study’s daily references are retained as supplied. No same-day/future daily high or low enters features. If a daily reference is older than the preceding intraday session, PDH/PDL-dependent results inherit that limitation. An alternate prior-session-extrema run below checks the effect; those extrema are research references, not a replacement for an official missing daily bar.",
          "### Volume availability",
          f"NIFTY index candles have **{au['index_volume_positive']} positive volume readings** in the fetched sample. Index zero volume is unavailable traded volume, not evidence that buying or selling stopped. Index VWAP/OBV/volume breakout claims would be invalid here.",
          mdtable(["Traded proxy","Main-window bars","Positive volume","Zero volume","Missing volume"],[[x["name"],x["bars"],x["positive"],x["zero"],x["missing"]] for x in au["volume"]]),
          "Volume inputs are **NIFTYBEES ETF volume**, plus separate RELIANCE, HDFCBANK and ICICIBANK volume/returns. The three-stock basket is an equal average of each stock’s normalized volume, not index volume or a complete breadth measure. NIFTYBEES identity is verified by its ISIN `INF204KB14I2`. [NSE instrument page](https://www.nseindia.com/get-quote/equity/NIFTYBEES/Nippon-India-ETF-Nifty-50-BeES).",
          "RVOL = current bar volume / median of the preceding 20 minutes’ bars (at least three previous bars). It is not time-of-day-normalized historical relative volume. Signed volume uses candle direction; it is not aggressor-side order flow. Proxy VWAP uses that proxy’s own typical price and volume. All proxies align by timestamp and become available only at their candle close.",
          "## Experimental design",
          "1. Recompute the existing `price_action.analyze` engine separately for every session and timeframe: default ORB 15 minutes, round-number step 100. Use events’ `known_at`, not a pivot’s original timestamp. Study parameters are unchanged.\n2. Enter at the **next candle open**, then measure its closing price after **5, 15 or 30 elapsed minutes**. No overnight labels; all main labels end by 15:15. Current trigger-candle movement is excluded from future return.\n3. Main table uses 15 minutes as a common horizon across timeframes. Directional accuracy is signed return >0; zero return is not a win. Return is index points, with a separate ATR normalization.\n4. Keep one observation per holding window per strategy/concept/session. Raw event counts are also shown. Signals sharing a candle are not independent trades; opposite directions on one candle cancel.\n5. Compare to same-side, same-session, same-half-hour mean forward movement, and to always-up/down and simple momentum/fade baselines. The matched baseline is retrospective diagnostic context, never a live feature.\n6. Fit models on prior sessions only. The first two primary sessions train the first fold; 27, 28 and 29 October are forward tests. Whole-session boundaries prevent training labels from overlapping a later test day. Imputation, means and scales come only from training data.\n7. Feature families: price/ATR, EMA9/21, RSI, compression, known level distances and time of day; recent bullish/bearish/neutral concept channels; traded-proxy volume, returns and VWAP; and, for 1m, the latest **fully closed** 5m context. Event memory is five minutes (five 1m bars or one 5m bar), not five bars on both charts.\n8. Fixed model settings: L2 logistic regression (mean-loss penalty 0.20); 60 boosted decision stumps, learning rate 0.08, minimum leaf max(15,5% training rows), leaf curvature penalty 5; ridge forward-return regression (penalty 0.50) with sigmoid-scaled score. No hyperparameter search. Ridge scores are ranking scores rather than calibrated probabilities.\n9. Subtract **2 and 5 index points per completed observation** as illustrative round-trip friction. These are sensitivity assumptions, not a broker fee model or an executable index fill. Futures/ETF basis and option Greeks are not modeled.\n10. Directional concept significance uses 499 within-session circular shifts of the return sequence; BH correction covers concepts with ≥5 independent 15m observations within each timeframe. Other horizons, rule variants and model comparisons are exploratory and are not covered by that correction.",
          f"**Causality verification:** {sum(c['pass'] for c in checks)}/{len(checks)} real-session prefix checks passed: adding later candles did not change earlier confirmed events. Production timing fixtures were also run separately. Technical ATR reference uses the preceding 14 continuous-session true ranges, with first-session bars warmed from earlier sessions, overnight gaps excluded from true range, and auction bars excluded from the warm-up. Production event ATR remains session-local and therefore has its own warm-up. Historical candles are assumed observable at their close; provider publication latency, revisions and live fill availability were not measured.",
          "**Uncertainty:** Independent observations within a session are still correlated. Wilson intervals below describe binomial sampling only and likely understate regime uncertainty. Five primary days cannot support a reliable long-run confidence interval, nor a strong claim about significance from hundreds of inspected alternatives."]
    for grain in [1,5]:
        r=results[str(grain)]
        text += [f"## {grain}-minute results", "### Complete 47-concept inventory",
                 "`Events` counts all detected directions and neutral annotations; `N15` removes conflicting directions, late/invalid labels and overlapping holding windows. Continuous references have no standalone directional event. Their distances are present in price features. A zero means no usable evidence under the current rule, not proof that the market concept does not exist.",
                 mdtable(["#","Concept","Events ↑/↓/0","N15","Win %","95% Wilson %","Mean pts","Matched excess pts","Mean 5m / 30m pts","q15"],
                         [[x["id"],x["label"],f"{x['bull']}/{x['bear']}/{x['neutral']}",x['15']['n'],f(x['15'].get('win_pct'),1),
                           "—" if not x['15']['n'] else "–".join(f(v,1) for v in x['15']['wilson']),f(x['15'].get('mean')),f(x['15'].get('excess')),
                           f"{f(x['5'].get('mean'))} / {f(x['30'].get('mean'))}",f(x.get('q'),3)] for x in r['concepts']]),
                 "### Candidate concepts with at least eight independent observations",
                 mdtable(["Concept","N15 / days","Win %","Mean / net2 / net5 pts","Matched excess","Positive days","TP-first / SL-first %"],
                         [[f"{x['id']}. {x['label']}",f"{x['15']['n']} / {x['15']['days']}",f(x['15']['win_pct'],1),
                           f"{f(x['15']['mean'])} / {f(x['15']['cost2'])} / {f(x['15']['cost5'])}",f(x['15']['excess']),
                           f"{x['15']['positive_days']}/{x['15']['days']}",f"{f(x['15']['tp_first_pct'],1)} / {f(x['15']['sl_first_pct'],1)}"]
                          for x in sorted([x for x in r['concepts'] if x['15']['n']>=8],key=lambda x:x['15']['excess'],reverse=True)[:10]]),
                 "TP/SL diagnostic: ±1 ATR from next-bar open, first hit within 15 minutes; an ambiguous candle hitting both is counted as an adverse hit. Neither-hit observations remain in the denominator. This is a path diagnostic, not a full stop/target P&L backtest.",
                 "### Fixed signal combinations and later-day check",
                 "Rules use recent five-minute signals and the current EMA sign. `Dev` is 23–28 October; 29 October is a separately shown final-day check. Rule results and rankings were inspected after the full experiment, so the final-day column is a temporal diagnostic, not an untouched lockbox for the entire research process.",
                 mdtable(["Rule","All N / win %","All mean / excess pts","Dev N / mean","29 Oct N / mean","7-session mean"],
                         [[x['name'],f"{x['all']['n']} / {f(x['all'].get('win_pct'),1)}",f"{f(x['all'].get('mean'))} / {f(x['all'].get('excess'))}",
                           f"{x['dev']['n']} / {f(x['dev'].get('mean'))}",f"{x['final']['n']} / {f(x['final'].get('mean'))}",f(x['sensitivity'].get('mean'))] for x in r['rules']]),
                 "### Predicting movement size, separately from direction",
                 mdtable(["Condition","N15 nonoverlap","P(abs net move ≥1 ATR) %","Mean abs pts","Mean abs ATR"],
                         [[x['name'],x['n'],f(x['move1atr_pct'],1),f(x['abs_mean']),f(x['abs_mean_atr'])] for x in r['magnitude']]),
                 "A large-move condition is not itself a bullish or bearish prediction. The target is the absolute terminal 15-minute move, not merely a wick that touched a barrier.",
                 "### Forward model comparisons",
                 f"All model rows below use forward test days **{', '.join(r['ml']['test_days'])}**. Directional metrics use every eligible nonzero-return bar and therefore have overlapping labels; point results use one position at a time. AUC measures ranking, Brier measures squared probability error (lower is better). Different models share the same observations.",
                 mdtable(["Model / baseline","Bar N","Accuracy %","Balanced %","AUC","Brier","Independent N","Mean / net2 / net5 pts"],
                         [[x['name'],x['n'],f(x['accuracy']*100,1),f(x['balanced_accuracy']*100,1),f(x.get('auc'),3),f(x['brier'],3),x['trade_n'],
                           f"{f(x['mean_points'])} / {f(x['net2'])} / {f(x.get('net5'))}"] for x in r['ml']['baselines']+r['ml']['models']]),
                 mdtable(["Model","Final 29 Oct accuracy % / AUC","Positive P&L days","Confidence ≥60% N / mean pts","Seven-session forward accuracy % / mean pts"],
                         [[x['name'],f"{f(x['final_day']['accuracy']*100,1)} / {f(x['final_day'].get('auc'),3)}",f"{x['positive_days']}/{x['trade_days']}",
                           f"{x['confident_n']} / {f(x['confident_mean'])}",
                           f"{f(next(y for y in r['ml_sensitivity']['models'] if y['name']==x['name'])['accuracy']*100,1)} / {f(next(y for y in r['ml_sensitivity']['models'] if y['name']==x['name'])['mean_points'])}"] for x in r['ml']['models']]),
                 "Confidence ≥60% is a fixed score filter; calibration is not established on five days. It is especially not a calibrated probability for ridge. Seven-session model comparisons test additional folds as well as supplying additional training data, so they are not an identical test sample.",
                 "### What changes with auction inclusion and reference choice",
                 mdtable(["Concept","Main N / mean","Through 15:30 N / mean","Prior-intraday-reference N / mean"],
                         [[f"{x['id']}. {x['label']}",f"{x['15']['n']} / {f(x['15'].get('mean'))}",
                           f"{r['auction'][x['id']-1]['15']['n']} / {f(r['auction'][x['id']-1]['15'].get('mean'))}",
                           f"{r['alternate_refs'][x['id']-1]['15']['n']} / {f(r['alternate_refs'][x['id']-1]['15'].get('mean'))}"]
                          for x in r['concepts'] if x['id'] in [6,11,13,14,15,20,39,42,44,46,47]]),
                 "Auction-inclusive figures are a contamination check, not the preferred estimate. Alternate-reference run uses the previous completed intraday session’s extrema and last value. All other settings are unchanged."]
    text += ["## Detection delays, duplicated information and practical interpretation",
             "- **HH/HL, LH/LL, equal highs/lows, support and resistance:** pivot labels confirm two bars late, i.e. 2 minutes on 1m and 10 minutes on 5m, on top of the pivot candle’s close. They describe structure already observed.\n- **BOS/CHoCH, ORB, displacement and FVG:** require a closed candle or completed three-bar pattern. A large trigger candle has already happened when the signal is available. A profitable continuation result must come from the following candles, as measured here.\n- **Break-and-retest/flip:** #6 is emitted alongside #13/#14 by the implementation. They are not independent votes. #40 is a swing-break subset of #46; #43/#45 often describe the same displacement and last opposite candle. #4/#5 duplicate the equal-pivot information in #10. Adding all these labels can manufacture apparent confluence without adding information.\n- **Neutral patterns:** #3, #25, #26 and compression within #41 do not provide a direction. Use their magnitude results or a separately specified breakout rule; assigning bullish/bearish meaning afterward is hindsight.\n- **Rare chart shapes:** double tops/bottoms, flags, triangles and head-and-shoulders patterns need enough independent instances on different days before ranking their reliability. No-match and low-N results should remain inconclusive.\n- **Levels #7/#8/#9/#12:** use distance, approach direction, rejection/acceptance and valid previous-session references. A horizontal line is not an entry signal.\n- **Multi-timeframe use:** 5m context must be fully closed before joining a 1m decision. The last unfinished 5m candle cannot be used. Both datasets describe the same underlying path; agreement is not independent confirmation.",
             "## Reproducibility and files",
             "The exact experimental outputs are saved alongside this report. The research script reads the project’s existing gateway and recomputes the existing concept engine; it changes no application signal rules and executes no trades.",
             "- Script: `backend/scripts/analyze_47_concepts.py`\n- Frozen inputs: `artifacts/concept_research_2026-10-29/snapshot.json`\n- Numerical results: `artifacts/concept_research_2026-10-29/results.json`\n- Event and feature exports: the `events_*m.csv` and `features_*m.csv` files in that directory\n- Per-bar forward model outputs: `predictions_*m_*.json`\n- Causality checks: `causality_checks.json`\n- Charts: `session_paths.png` and `model_comparison.png`",
             f"Snapshot SHA-256: `{snapshot_hash}`.",
             "Replay: `.venv\\Scripts\\python.exe backend/scripts/analyze_47_concepts.py`. To retrieve historical inputs again, append `--fetch`; provider revisions can change that new snapshot. Random seed is 470105. Models are implemented using NumPy so the analysis does not depend on an uninstalled ML package.",
             "### Source and method notes",
             "- The authoritative definitions for these particular 47 concepts are the local production catalog in `backend/app/services/price_action.py`, not generic names interpreted from textbooks. The rules are heuristic product definitions.\n- Candle timestamps denote **bar start**, not bar close. [Upstox historical candle specification](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).\n- Forward chronological validation avoids random-split leakage from correlated time-series observations. [scikit-learn time-series validation documentation](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-of-time-series-data). The implementation here uses whole sessions and custom NumPy estimators.\n- These results evaluate underlying index movement. They do not establish option profitability, fill quality or a deployable strategy. A longer untouched history and a forward paper-trading period are needed to distinguish a real edge from this week’s regime."]
    text.insert(5, findings_narrative(results))
    if "diagnostics" in results:
        insertion=text.index("## Detection delays, duplicated information and practical interpretation")
        extra=["## Candidate timing and fragility checks",
               "These checks focus on the most interesting observed concepts, selected after reviewing the main results. They help reject fragile interpretations; they do not create a new independent validation set.",
               mdtable(["Candidate","Immediate N / mean","One extra candle delay N / mean","Bull N / mean","Bear N / mean","Leave-one-day-out mean range"],
                       [[x['name'],f"{x['base']['n']} / {f(x['base'].get('mean'))}",f"{x['delay']['n']} / {f(x['delay'].get('mean'))}",
                         f"{x['bull']['n']} / {f(x['bull'].get('mean'))}",f"{x['bear']['n']} / {f(x['bear'].get('mean'))}",
                         f"{f(x['loo_min'])} to {f(x['loo_max'])}"] for x in results['diagnostics']['candidates']]),
               "The delay is one full chart candle (1 minute or 5 minutes), followed by the same 15-minute holding period. The delayed sample is resampled for overlap and can lose late-day events. Bull/bear columns independently reselect nonoverlapping observations within each side, so their counts do not partition the pooled sample. Leave-one-day-out recalculates the pooled mean from the existing nonoverlapping observations after dropping each day in turn; it is a fragility check, not a fresh strategy selection.",
               "### Holding the event cohort constant across forecast horizons",
               "The main 5/15/30-minute panels independently remove overlap for each horizon and can contain different events. To assess how a move develops, this table instead takes the 15-minute nonoverlapping sample and retains only events with all three valid forward labels. The 30-minute outcomes in this table can overlap; it is a descriptive path comparison, not an independent 30-minute trade backtest.",
               mdtable(["Candidate","Common N","5m mean pts","15m mean pts","30m mean pts"],
                       [[x['name'],x['common_path']['n'],f(x['common_path']['5']),f(x['common_path']['15']),f(x['common_path']['30'])] for x in results['diagnostics']['candidates']]),
               "### Time-matched volume effect on movement size",
               mdtable(["Chart / volume group","N","P(abs move ≥1 ATR) %","Same session/half-hour expected %","Excess pp"],
                       [[f"{x['grain']}m / {x['group']}",x['n'],f(x['actual'],1),f(x['matched'],1),f(x['actual']-x['matched'],1)] for x in results['diagnostics']['volume_magnitude']]),
               "ATR is specific to the chart timeframe, so a 1m ATR hurdle and a 5m ATR hurdle are not the same point move. Time matching is descriptive and still cannot identify a causal effect of ETF activity. RVOL and the underlying can both respond to the same price shock.",
               "### Concrete signal examples",
               "The best and worst independent 15-minute examples for selected candidates are shown together to expose the downside as well as the upside. They are deliberately selected extremes, not representative expected trades. All times are IST.",
               mdtable(["Candidate","Known at / next-open entry","Direction","Entry","5m / 15m / 30m signed pts"],
                       [[x['name'],f"{x['known_at']} / {x['entry_at']}",x['direction'],f(x['entry']),f"{f(x['r5'])} / {f(x['r15'])} / {f(x['r30'])}"] for x in results['diagnostics']['examples']])]
        extra += ["### Additional combinations of the candidate signals",
                  "These narrower combinations were added after identifying the candidates above, so they are **post-selection exploratory checks**. The final-day column is a temporal diagnostic. They are all reported to make it visible when apparent confirmation fails to help.",
                  mdtable(["Chart / rule","All N / mean pts","Matched excess pts","23–28 Oct N / mean","29 Oct N / mean"],
                          [[f"{grain}m / {x['name']}",f"{x['all']['n']} / {f(x['all'].get('mean'))}",f(x['all'].get('excess')),
                            f"{x['dev']['n']} / {f(x['dev'].get('mean'))}",f"{x['final']['n']} / {f(x['final'].get('mean'))}"]
                           for grain in [1,5] for x in results[str(grain)].get('additional_rules',[])])]
        text[insertion:insertion]=extra
    text.insert(text.index("## Reproducibility and files"),
                "## Exact rules for all 47 concepts\n\n"+mdtable(["#","Group","Concept","Production rule"],
                    [[x['id'],x['group'],x['label'],x['rule']] for x in pa.CATALOG]))
    text.insert(text.index("## Reproducibility and files"), research_next_steps(results))
    text.insert(text.index("## Data audit"),
                "![Session paths](artifacts/concept_research_2026-10-29/session_paths.png)\n\n![Forward model comparison](artifacts/concept_research_2026-10-29/model_comparison.png)")
    REPORT.write_text("\n\n".join(text)+"\n",encoding="utf-8")


def findings_narrative(results):
    a,b=results['1'],results['5']
    best1=max(a['ml']['models'],key=lambda x:x['mean_points'])
    best5=max(b['ml']['models'],key=lambda x:x['mean_points'])
    base1=next(x for x in a['ml']['baselines'] if x['name']=='Always up')
    base5=next(x for x in b['ml']['baselines'] if x['name']=='Always up')
    all1=next(x for x in a['ml']['models'] if x['name']=='Logistic all')
    multi=next(x for x in a['ml']['models'] if x['name']=='Logistic all+closed5m')
    m5={x['name']:x for x in b['magnitude']}
    ml_summary=(f"The strongest gross mean among the tested ML models is {f(best1['mean_points'])} points on 1m ({best1['name']}) and {f(best5['mean_points'])} on 5m ({best5['name']}). "
                +("All are negative under the illustrative 2-point friction." if max(best1['mean_points'],best5['mean_points'])<2 else "Any result above the illustrative 2-point friction still requires comparison against drift and later regimes."))
    rows=[]
    for grain,r,ids in [(1,a,[19,20,42,13]),(5,b,[47,33,39,46])]:
        for n in ids:
            x=r['concepts'][n-1];s=x['15'];sens=r['concepts_sensitivity'][n-1]['15']
            rows.append([f"{grain}m #{n} {x['label']}",s['n'],f(s.get('win_pct'),1),f(s.get('mean')),f(s.get('excess')),
                         f(sens.get('mean')),f(x.get('q'),3)])
    return "\n\n".join([
        "## Findings that matter",
        "**No robust predictor was established.** None of the eligible directional concepts reaches BH-adjusted q<0.05 on either chart. "+ml_summary+" More labels and more model complexity did not establish a dependable advantage on this small history.",
        mdtable(["Candidate / diagnostic","N15","Win %","Mean pts","Matched excess pts","7-session mean pts","q"],rows),
        "**1. The clearest 1m candidate is a confirmed trendline break (#19), with CHoCH (#20) a second research candidate.** #19 has 54 nonoverlapping observations, 68.5% directional wins, +7.80 points at 15 minutes and +7.23 versus the matched directional/time baseline. All five daily means are positive, and the seven-session mean remains +6.86. Its 5-minute future mean is only +1.59 points; its final-day mean is +4.38, which does not cover the 5-point cost assumption. These are research positives with q=0.453, not a validated edge.",
        "#20 CHoCH has +12.52 points at 15 minutes and +17.42 at 30 minutes, versus −2.52 points in the separately resampled 5-minute panel. Those panels use different events. **On the same 37-event cohort**, its forward means are **+0.92 at 5 minutes, +12.52 at 15, and +22.44 at 30**. That comparison supports a slower-reversal hypothesis; it does not imply a guaranteed initial loss or an immediately clean move. All five daily gross means are positive, but the final day is only +2.43 points and its matched excess is negative that day. Calling it an early entry without allowing adverse movement would overstate the evidence. CHoCH does not transfer to 5m here: that chart’s 15-minute result is −4.32 points from seven observations.",
        "**2. A positive raw return often describes the prevailing market drift.** On 1m, BOS (#42) averages +10.09 points and is positive on all five days, yet its matched excess is **−4.37 points**. The simple retest+EMA rule averages +8.10 points but has −3.99 matched excess. A label can be associated with a rising/falling market without selecting better moments within that market.",
        "**3. On 5m, zone mitigation/retest (#47) is worth further study, but its apparent edge is fragile.** It has 43 independent observations, 60.5% wins, +8.95 points and +6.04 matched excess; its seven-session mean falls to +5.19. The primary daily means are +33.48, −0.41, −11.99, +1.06 and +16.99 points. October 23 contributes more than the entire pooled gain, so the leave-one-day-out result matters. Pullback to resistance (#33) has an eye-catching 85.7% win rate, but only seven observations. That is too little to rank confidently above the larger samples.",
        "**4. Avoid automatically chasing displacement or counting FVG as continuation confirmation.** 1m displacement (#46) averages −1.68 points after confirmation; 5m displacement averages **−17.03** (11 observations), with a positive daily mean on only one day. Fading that 5m displacement reverses the full-sample result to +17.03, but the single final-day fade loses 7 points. This is a small-sample exhaustion hypothesis, not evidence for an automatic countertrend strategy. Standalone FVG is approximately flat on 1m (+0.30 points), and its 5m +3.95 points is −9.41 versus matched drift.",
        "**5. Extra volume confirmation did not improve direction.** On 1m, structure/setup+EMA averages +7.30 points; requiring ETF RVOL≥1.5 reduces that to +7.15, and also requiring signed ETF volume reduces it to +5.79. On 5m the same sequence is −2.07, −4.72 and −15.30 points. The logistic ablation also fails to show a reliable directional improvement from volume. "
        +f"RVOL may still help describe activity/movement size: 5m high-RVOL observations have a {f(m5['ETF RVOL >=1.5']['move1atr_pct'],1)}% chance of a terminal move ≥1 chart ATR versus {f(m5['All eligible bars']['move1atr_pct'],1)}% for the baseline and {f(m5['ETF RVOL <1']['move1atr_pct'],1)}% for low RVOL. See the time-matched table for the excess after controlling session and half-hour. This is an exploratory magnitude observation, not a direction signal.",
        "**6. Generic multi-timeframe agreement did not improve this sample’s simple setup rule.** The 1m setup+both-EMA-trends rule averages −0.96 points, versus +7.30 for setup+1m EMA alone. "
        +f"Adding closed-5m features changes the full logistic model’s mean forward movement from {f(all1['mean_points'])} to {f(multi['mean_points'])} points. A slower confirming chart can arrive after much of the opportunity; do not assume agreement must improve an early indicator.",
        "**7. Opening-range breakout looks impressive because of very few opportunities and a large day.** Its 15-minute means are +32.93 points on 1m (seven independent observations) and +34.75 on 5m (six). The 5m result includes a +132.80-point observation on October 26. Its matched excess is negative, and the final-day result is −2.20 points. There is no basis here for treating that high average as a stable opening edge.",
        "**8. ML did not establish a dependable forward improvement.** "
        +f"On October 27–29, always predicting up achieves {f(base1['accuracy']*100,1)}% bar accuracy on 1m and {f(base5['accuracy']*100,1)}% on 5m, with {f(base1['mean_points'])}/{f(base5['mean_points'])} gross points per nonoverlapping 15-minute interval. "
        +f"The best observed ML accuracy is {f(max(x['accuracy'] for x in a['ml']['models'])*100,1)}% on 1m and {f(max(x['accuracy'] for x in b['ml']['models'])*100,1)}% on 5m. "
        +"The seven-session sensitivity and a training-only expanding-prior probability baseline are also reported. AUC improvements without positive net movement do not establish a usable rule. Always-up itself is a hindsight benchmark for these dates, not a recommended strategy.",
        "**9. The most interesting narrow combination is 1m trendline break + same-side EMA9/21 alignment.** In the additional post-selection check, it produces 24 nonoverlapping observations, 70.8% wins and +11.26 gross points over 15 minutes, compared with +7.80 for the unfiltered concept. Matched excess is +3.52 points. The development mean is +12.64 (N=16), and October 29 is +8.51 (N=8). It is positive on only three of five days; its matched excess is lower than the unfiltered concept. This is a concrete candidate for a later frozen test, not proof the filter improves generalization. Requiring recent CHoCH as a second vote instead performs poorly. On 5m, zone revisit + EMA alignment increases the raw mean to +10.20 points (N=32), with +6.76 matched excess, but is likewise positive on only three days and heavily influenced by October 23. These extra rules are not covered by the concept q-values.",
        "**Practical answer:** prioritize testing 1m #19, including the narrow EMA-alignment variant, and track #20 separately as a slower-reversal candidate. Treat 5m #47 as a more fragile conditional zone reaction. Use candle-close confirmation and known levels, measure the subsequent 15–30 minute path, and record volume as context. This sample supports rejecting an all-47 composite or mandatory volume/5m-agreement filter more strongly than it supports a deployable entry system."
    ])


def research_next_steps(results):
    return "\n\n".join([
        "## A concrete next research specification",
        "The following is a proposed forward experiment derived from this report, not an additional backtest result or a trading recommendation:",
        "1. Track **1m #19 trendline break** and **1m #20 CHoCH** as separate triggers after their confirmation close. Freeze the #19 variant requiring EMA9>EMA21 for an upward break, or EMA9<EMA21 for a downward break, and compare it to the unfiltered #19. Do not add event counts together as confidence. Track **5m #47 first zone revisit**, with and without its own EMA alignment, separately. Record next-open prices and any adverse excursion before movement develops.\n2. Keep 5, 15 and 30-minute outcome columns, with 15 minutes as the predeclared primary horizon. #20’s weaker first five minutes is a reason to study timing and risk, not to hide the short-horizon result.\n3. Log ETF RVOL and 5m context without forcing those filters. Only adopt a filter if it improves a later untouched sample against the same timestamp/side baseline after realistic instrument costs.\n4. Freeze definitions and model settings before collecting a materially longer history, such as 60–120 complete trading sessions. Fit any further thresholds on earlier development dates, validate on following dates, and keep a final contiguous period untouched. Include both upward and downward regimes.\n5. Evaluate on the actual instrument to be traded: futures/ETF prices, spread, slippage and fees. Options need their own entry/exit premiums, expiry, Greeks and liquidity; index-point accuracy alone cannot establish option P&L.\n6. Continue to exclude the cash-index auction interval from the continuous-trading model. Model the auction separately only with appropriate auction data. Address the missing native 5m session on October 28 in the source pipeline; the research already reconstructs it from complete 1m candles.",
        "A reasonable promotion requirement is positive net performance against a same-side/time baseline on more than one later block of sessions, stable leave-day-out results, and a controlled false-discovery assessment for whatever final rule family is actually searched. This week alone does not meet that standard."
    ])


def enrich_results(datasets,events,results):
    diagnostics={"candidates":[],"examples":[],"volume_magnitude":[]}
    for grain,ids in [(1,[19,20,42,13]),(5,[47,33,39,46])]:
        d,e=datasets[grain],events[grain]
        # Proper training-only constant-probability baseline for Brier/log-loss.
        selected=d[d.day.between(PRIMARY_START,END)&d.ret_15.notna()&d.ret_15.ne(0)]
        testdays=results[str(grain)]['ml']['test_days']
        z=selected[selected.day.isin(testdays)]
        prob=np.array([(selected.loc[selected.day<day,'ret_15']>0).mean() for day in z.day])
        met=classification_metrics((z.ret_15>0).to_numpy(int),prob)
        t=deoverlap(z,15//grain);directions=pd.Series(np.where(prob>=.5,1,-1),index=z.index)
        signed=t.ret_15*directions.loc[t.index]
        met.update(name='Expanding prior up rate',trade_n=len(t),mean_points=float(signed.mean()),net2=float(signed.mean()-2),net5=float(signed.mean()-5))
        baselines=results[str(grain)]['ml']['baselines']
        baselines[:]=[x for x in baselines if x['name']!='Expanding prior up rate']+[met]
        # Narrow signal combinations. No learned thresholds or final-day fitting.
        def direction_for(n):
            signal=pd.Series(0.,index=d.index)
            for row,g in e[e.concept==n].groupby('row'):signal.loc[row]=np.sign(g.side.sum())
            return signal
        t19,t20,t47=direction_for(19),direction_for(20),direction_for(47)
        def memory(signal):
            # Same-direction evidence within the preceding five elapsed minutes.
            return signal.groupby(d.day).transform(lambda x:np.sign(x.rolling(max(1,5//grain),min_periods=1).sum()))
        trend=np.sign(d.p_ema_gap).fillna(0);vol=d.v_NIFTYBEES_rvol>=np.log(2.5)
        union=np.sign(t19+t20)
        extra_rules={
            'Trendline break OR CHoCH':(union.ne(0),union),
            'Trendline break + recent same-side CHoCH':(t19.ne(0)&t19.eq(memory(t20)),t19),
            'CHoCH + recent same-side trendline break':(t20.ne(0)&t20.eq(memory(t19)),t20),
            'Trendline break + EMA alignment':(t19.ne(0)&t19.eq(trend),t19),
            'CHoCH + EMA alignment':(t20.ne(0)&t20.eq(trend),t20),
            'Trendline break + ETF RVOL>=1.5':(t19.ne(0)&vol,t19),
            'CHoCH + ETF RVOL>=1.5':(t20.ne(0)&vol,t20),
            'Zone revisit + EMA alignment':(t47.ne(0)&t47.eq(trend),t47)}
        extra=[]
        for name,(mask,direction) in extra_rules.items():
            item={'name':name}
            for label,daymask in [('all',d.day.between(PRIMARY_START,END)),('dev',d.day.between(PRIMARY_START,'2026-10-28')),('final',d.day==END)]:
                item[label]=signal_stats(d,mask&daymask,direction.to_numpy(),permutations=0)
            extra.append(item)
        results[str(grain)]['additional_rules']=extra
        for n in ids:
            direction=pd.Series(0.,index=d.index)
            for row,g in e[e.concept==n].groupby('row'):direction.loc[row]=np.sign(g.side.sum())
            eligible=d.day.between(PRIMARY_START,END)
            delayed=direction.groupby(d.day).shift(1).fillna(0)
            base=signal_stats(d,eligible&direction.ne(0),direction.to_numpy(),permutations=0)
            loo=[]
            for day in sorted(d.loc[eligible,'day'].unique()):
                remaining=[x for x in base.get('daily',[]) if x['day']!=day]
                if remaining:loo.append(sum(x['mean']*x['n'] for x in remaining)/sum(x['n'] for x in remaining))
            name=f"{grain}m #{n} {pa.BY_ID[n]['label']}"
            cohort=d.loc[eligible&direction.ne(0)&d.ret_15.notna()].copy()
            cohort['direction']=direction.loc[cohort.index];cohort=deoverlap(cohort,15//grain)
            cohort=cohort[cohort.ret_5.notna()&cohort.ret_30.notna()]
            common_path={'n':len(cohort),**{str(h):float((cohort[f'ret_{h}']*cohort.direction).mean()) if len(cohort) else None for h in [5,15,30]}}
            diagnostics['candidates'].append({'name':name,'base':base,'common_path':common_path,
                'delay':signal_stats(d,eligible&delayed.ne(0),delayed.to_numpy(),permutations=0),
                'bull':signal_stats(d,eligible&direction.gt(0),direction.to_numpy(),permutations=0),
                'bear':signal_stats(d,eligible&direction.lt(0),direction.to_numpy(),permutations=0),
                'loo_min':min(loo) if loo else None,'loo_max':max(loo) if loo else None})
            if n in [19,20,47]:
                z=d.loc[eligible&direction.ne(0)&d.ret_15.notna()].copy()
                z['direction']=direction.loc[z.index];z=deoverlap(z,15//grain);z['signed']=z.ret_15*z.direction
                for ix in [z.signed.idxmax(),z.signed.idxmin()]:
                    r=z.loc[ix]
                    diagnostics['examples'].append({'name':name,'known_at':r.known_at.strftime('%m-%d %H:%M'),
                        'entry_at':r.known_at.strftime('%H:%M'),'direction':'up' if r.direction>0 else 'down',
                        'entry':float(r.entry_15),'r5':float(r.ret_5*r.direction) if pd.notna(r.ret_5) else None,
                        'r15':float(r.ret_15*r.direction),'r30':float(r.ret_30*r.direction) if pd.notna(r.ret_30) else None})
        valid=d.day.between(PRIMARY_START,END)&d.ret_15.notna()
        target=(d.ret_15.abs()/d.atr>=1).astype(float)
        bucket=(d.ts.dt.hour*60+d.ts.dt.minute)//30
        p=d.loc[valid].assign(target=target.loc[valid],bucket=bucket.loc[valid])
        expected=p.groupby(['day','bucket']).target.mean()
        for group,mask in [('RVOL >=1.5',d.v_NIFTYBEES_rvol>=np.log(2.5)),('RVOL <1',d.v_NIFTYBEES_rvol<np.log(2))]:
            z=deoverlap(d.loc[valid&mask],15//grain)
            matched=[expected.loc[(r.day,bucket.loc[ix])] for ix,r in z.iterrows()]
            diagnostics['volume_magnitude'].append({'grain':grain,'group':group,'n':len(z),
                'actual':float(100*target.loc[z.index].mean()),'matched':float(100*np.mean(matched))})
    results['diagnostics']=diagnostics


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--fetch",action="store_true");args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    snapshot=fetch_snapshot() if args.fetch or not (OUT/"snapshot.json").exists() else json.loads((OUT/"snapshot.json").read_text(encoding="utf-8"))
    idx=regular(frame(snapshot["index_1m"]));native=regular(frame(snapshot["index_5m_native"]));daily=frame(snapshot["daily"])
    proxy={name:frame(rows) for name,rows in snapshot["proxies"].items()}
    results={"asof":ASOF,"audit":audit(snapshot,idx,native,daily,proxy)}
    datasets={};events={};checks=[]
    for grain,raw in [(5,aggregate(idx)),(1,idx)]:
        d,e,studies,cc=features(raw,grain,daily,proxy);d.attrs["grain"]=grain
        datasets[grain]=d;events[grain]=e;checks+=cc
        dump(f"studies_{grain}m.json",studies)
        print("features",grain,len(d),"events",len(e),flush=True)
    # Latest CLOSED five-minute candle only: many 1m decisions share one context bar.
    left=datasets[1];right=datasets[5]
    mc=["p_ema_gap","p_ret3","p_compression","p_orb_high","p_orb_low","c20_up","c20_down","c42_up","c42_down"]
    right=right[["known_at"]+mc].rename(columns={c:"m_"+c.removeprefix("p_") for c in mc})
    left=pd.merge_asof(left.sort_values("known_at"),right.sort_values("known_at"),on="known_at",direction="backward",tolerance=pd.Timedelta(minutes=4))
    left.attrs["grain"]=1;datasets[1]=left
    # Build strictly prior-session alternative references, with no same-day projection.
    alt_daily=idx.groupby(idx.ts.dt.strftime("%Y-%m-%d")).agg(ts=("ts","first"),open=("open","first"),
                    high=("high","max"),low=("low","min"),close=("close","last"),volume=("volume","sum"),oi=("oi","last")).reset_index(drop=True)
    for grain in [1,5]:
        d,e=datasets[grain],events[grain]
        d.to_csv(OUT/f"features_{grain}m.csv",index=False);e.to_csv(OUT/f"events_{grain}m.csv",index=False)
        print("concepts",grain,flush=True)
        r={"concepts":concept_analysis(d,e),"concepts_sensitivity":concept_analysis(d,e,SENS_START)}
        r["rules"]=[]
        for name,(mask,direction) in rule_masks(d,e).items():
            sides=np.asarray(direction)
            row={"name":name}
            for label,extra in [("all",d.day.between(PRIMARY_START,END)),("dev",d.day.between(PRIMARY_START,"2026-10-28")),
                                ("final",d.day==END),("sensitivity",d.day.between(SENS_START,END))]:
                row[label]=signal_stats(d,mask&extra,sides,permutations=0)
            r["rules"].append(row)
        r["magnitude"]=magnitude_analysis(d,e)
        print("models",grain,flush=True)
        r["ml"]=model_analysis(d);r["ml_sensitivity"]=model_analysis(d,SENS_START)
        auction=d.copy();auction.attrs["grain"]=grain
        for h in [5,15,30]:auction[f"ret_{h}"]=auction[f"ret_all_{h}"]
        r["auction"]=concept_analysis(auction,e)
        # Recompute event history with alternate known references, then align rows to d.
        raw=idx if grain==1 else aggregate(idx)
        _,ee,_,_=features(raw,grain,alt_daily,proxy)
        r["alternate_refs"]=concept_analysis(d,ee)
        results[str(grain)]=r
        dump("results.json",results)
    enrich_results(datasets,events,results)
    dump("results.json",results)
    dump("causality_checks.json",checks)
    snapshot_hash=hashlib.sha256((OUT/"snapshot.json").read_bytes()).hexdigest()
    write_report(results,checks,snapshot_hash)
    plot_outputs(datasets,results)
    print("REPORT",REPORT,flush=True)


def plot_outputs(datasets,results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor":"white","axes.spines.top":False,"axes.spines.right":False})
    d=datasets[1];fig,ax=plt.subplots(figsize=(12,5))
    for day,b in d[d.day.between(PRIMARY_START,END)].groupby("day"):
        t=(b.ts.dt.hour*60+b.ts.dt.minute-555)
        ax.plot(t,b.close-b.open.iloc[0],label=day,linewidth=1.5)
    ax.axvspan(360,375,color="#ea9999",alpha=.3,label="Auction interval (excluded)")
    ax.axhline(0,color="#555",linewidth=.6);ax.set(xlabel="Minutes after 09:15 IST",ylabel="Index points from session open",title="NIFTY 50: primary five sessions and the auction interval")
    ax.legend(fontsize=8,ncol=2);fig.tight_layout();fig.savefig(OUT/"session_paths.png",dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(14,6))
    for ax,grain in zip(axes,[1,5]):
        rows=results[str(grain)]["ml"]["models"];names=[r["name"].replace("Logistic ","LR ") for r in rows]
        ax.barh(names,[r["mean_points"] for r in rows],color="#2e6e9e")
        ax.axvline(0,color="black",linewidth=.7);ax.axvline(2,color="#bd7823",linestyle="--",label="2-point friction")
        ax.set(title=f"{grain}m forward tests: Oct 27-29",xlabel="Mean 15-minute move per nonoverlapping prediction (points)")
        ax.invert_yaxis();ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(OUT/"model_comparison.png",dpi=150);plt.close(fig)


if __name__=="__main__":main()

