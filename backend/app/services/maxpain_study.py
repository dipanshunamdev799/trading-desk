"""Reproducible, fixed-target expiry-convergence research from official EOD OI.

This is an observational study, not an options strategy/P&L backtest. Each target
is known from a completed earlier session; evaluation starts at the next open.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import statistics
import threading
import time
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

from .upstox_service import get_upstox
from .market_store import IST, market_day, now
import nifty_max_pain as nmp

UNIVERSE = [
    ("NIFTY", "Nifty 50", "NSE_INDEX|Nifty 50"),
    ("BANKNIFTY", "Bank Nifty", "NSE_INDEX|Nifty Bank"),
    ("FINNIFTY", "Fin Nifty", "NSE_INDEX|Nifty Fin Service"),
    ("MIDCPNIFTY", "Midcap Select", "NSE_INDEX|NIFTY MID SELECT"),
    ("RELIANCE", "Reliance", "NSE_EQ|INE002A01018"),
    ("HDFCBANK", "HDFC Bank", "NSE_EQ|INE040A01034"),
    ("ICICIBANK", "ICICI Bank", "NSE_EQ|INE090A01021"),
    ("TCS", "TCS", "NSE_EQ|INE467B01029"),
    ("INFY", "Infosys", "NSE_EQ|INE009A01021"),
    ("SBIN", "SBI", "NSE_EQ|INE062A01020"),
]
HORIZONS = (1, 3, 5)
VERSION = "expiry-convergence-v2"
SOURCE = "https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{day}_F_0000.csv.zip"


def finite(value, *, positive=False):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) and (result > 0 if positive else result >= 0) else None
    except (ValueError, TypeError):
        return None


def parse_bhavcopy(content: bytes, day: str) -> dict:
    """Preserve all selected option legs, including real zero OI, in compact rows.

    Each row: token, strike, CE/PE, OI units, lot size, close, volume.
    Never infer missing OI or use a different file's trading date.
    """
    symbols = {row[0] for row in UNIVERSE}
    chains, spots = {}, defaultdict(set)
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(names) != 1 or archive.getinfo(names[0]).file_size > 150_000_000:
            raise ValueError("Unexpected NSE archive layout")
        with io.TextIOWrapper(archive.open(names[0]), encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            required = {"TradDt", "TckrSymb", "XpryDt", "StrkPric", "OptnTp", "OpnIntrst", "FinInstrmId", "UndrlygPric", "NewBrdLotQty"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("NSE bhavcopy schema changed")
            count = 0
            for row in reader:
                if row["TradDt"] != day:
                    raise ValueError("NSE file contains a different trading date")
                symbol, side = row["TckrSymb"], row["OptnTp"]
                if symbol not in symbols or side not in ("CE", "PE"):
                    continue
                expiry = row.get("FininstrmActlXpryDt") or row["XpryDt"]
                if date.fromisoformat(expiry).isoformat() < day:
                    raise ValueError("NSE file contains an expired live contract")
                strike = finite(row["StrkPric"], positive=True)
                oi, lot = finite(row["OpnIntrst"]), finite(row["NewBrdLotQty"], positive=True)
                if strike is None or oi is None or lot is None:
                    raise ValueError("A selected option leg has missing/invalid strike, OI or lot size")
                spot = finite(row["UndrlygPric"], positive=True)
                if spot is not None:
                    spots[symbol].add(spot)
                chain = chains.setdefault((symbol, expiry), {"symbol": symbol, "expiry": expiry, "contracts": []})
                chain["contracts"].append([row["FinInstrmId"], strike, side, oi, lot,
                    finite(row.get("ClsPric")), finite(row.get("TtlTradgVol"))])
                count += 1
    if not count:
        raise ValueError("No selected option contracts in the NSE file")
    return {"date": day, "source_url": SOURCE.format(day=day.replace("-", "")),
            "sha256": hashlib.sha256(content).hexdigest(), "leg_count": count,
            "spots": {symbol: sorted(values) for symbol, values in spots.items()},
            "chains": list(chains.values()), "row_columns": ["token", "strike", "side", "oi_units", "lot_size", "close", "volume"]}


class DailyArchive:
    def __init__(self, gateway):
        self.gateway = gateway
        self.lock, self.next_request = threading.Lock(), 0.

    def read(self, day):
        def fetch():
            with self.lock:
                delay = self.next_request - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                self.next_request = time.monotonic() + .5
            response = requests.get(SOURCE.format(day=day.replace("-", "")),
                headers={"User-Agent": "Mozilla/5.0 MaxPainResearch/1.0"}, timeout=(5, 35))
            response.raise_for_status()
            return parse_bhavcopy(response.content, day)
        # Completed historic files are immutable. Re-runs use cache/DB, not NSE.
        for attempt in range(3):
            try:
                return self.gateway.store.read("research_nse_fo_eod", {"date": day, "universe": [x[0] for x in UNIVERSE], "version": 1}, fetch)
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    raise
                if attempt == 2:
                    raise
            except (requests.RequestException, ValueError, zipfile.BadZipFile):
                if attempt == 2:
                    raise
            time.sleep(attempt + 1)


def candles_by_day(payload):
    if payload.get("_partial"):
        raise ValueError("Incomplete underlying candle coverage")
    result = {}
    for row in payload.get("candles") or []:
        day = str(row[0])[:10]
        values = [finite(value, positive=True) for value in row[1:5]]
        if len(values) != 4 or any(value is None for value in values):
            raise ValueError("Invalid underlying OHLC")
        opened, high, low, close = values
        if low > min(opened, close) or high < max(opened, close) or high < low:
            raise ValueError("Inconsistent underlying OHLC")
        if day in result:
            raise ValueError("Duplicate underlying candle date")
        result[day] = {"open": opened, "high": high, "low": low, "close": close}
    return result


def chain_target(chain, *, allow_unpaired=False):
    pairs, identities = {}, set()
    for token, strike, side, oi, lot, *_ in chain["contracts"]:
        identity = (strike, side)
        if identity in identities:
            raise ValueError("duplicate_strike_side")
        identities.add(identity)
        pairs.setdefault(strike, {})[side] = oi
    unpaired = {strike for strike, row in pairs.items() if set(row) != {"CE", "PE"}}
    if not pairs or (unpaired and not allow_unpaired):
        raise ValueError("missing_strike_side")
    strikes = sorted(pairs)
    if sum(sum(pair.values()) for pair in pairs.values()) <= 0:
        raise ValueError("zero_oi")
    # A published contract contributes once, only on its own side. No absent
    # counterpart contract is introduced in the sensitivity calculation.
    legs = chain["contracts"]
    result = nmp.compute_max_pain([row[1] for row in legs],
        [row[3] if row[2] == "CE" else 0 for row in legs],
        [row[3] if row[2] == "PE" else 0 for row in legs], oi_in_units=True)
    total = sum(row[3] for row in legs)
    return {"target": result.strike, "tied_strikes": sorted(set(result.tied_strikes)),
            "strikes": len(strikes), "call_oi": sum(row[3] for row in legs if row[2] == "CE"),
            "put_oi": sum(row[3] for row in legs if row[2] == "PE"),
            "unpaired_strikes": len(unpaired), "unpaired_oi_pct": sum(row[3] for row in legs if row[1] in unpaired) / total * 100,
            "strict_eligible": not unpaired}


def contract_adjusted(before, after):
    mapping = {row[0]: (row[1], row[4]) for row in before["contracts"]}
    return any(token in mapping and mapping[token] != (strike, lot)
               for token, strike, _, _, lot, *_ in after["contracts"])


def observation(symbol, label, key, expiry, snapshot_day, entry_day, horizon, target, candles):
    entered, exited = candles[entry_day]["open"], candles[expiry]["close"]
    initial = abs(entered - target["target"])
    final = abs(exited - target["target"])
    mirror = 2 * entered - target["target"]
    tolerance = max(1e-8, entered * 1e-10)
    comparable = initial > tolerance
    path = [bar for day, bar in candles.items() if entry_day <= day <= expiry]
    return {"symbol": symbol, "label": label, "instrument_key": key, "expiry": expiry,
        "snapshot_date": snapshot_day, "entry_date": entry_day, "horizon": horizon,
        **target, "entry_open": entered, "expiry_close": exited,
        "start_gap": initial, "end_gap": final, "start_gap_pct": initial / entered * 100,
        "end_gap_pct": final / entered * 100, "gap_reduction_pct_points": (initial - final) / entered * 100,
        "closer": (final < initial - tolerance) if comparable else None,
        "unchanged": (abs(final - initial) <= tolerance) if comparable else None,
        "moved_toward": ((exited - entered) * (target["target"] - entered) > tolerance) if comparable else None,
        "mirror_target": mirror, "mirror_closer": (abs(exited - mirror) < initial - tolerance) if comparable else None,
        "range_reached_target": any(bar["low"] <= target["target"] <= bar["high"] for bar in path),
        "near": initial / entered <= .01, "entry_month": entry_day[:7]}


def summarize(rows):
    comparable = [row for row in rows if row["closer"] is not None]
    n = len(comparable)
    rate = lambda field: sum(bool(row[field]) for row in comparable) / n * 100 if n else None
    return {"n": n, "already_at_target": len(rows) - n,
        "expiry_dates": len({row["expiry"] for row in comparable}),
        "closer_rate": rate("closer"), "mirror_rate": rate("mirror_closer"),
        "moved_toward_rate": rate("moved_toward"),
        "range_reached_rate": sum(row["range_reached_target"] for row in rows) / len(rows) * 100 if rows else None,
        "median_gap_reduction_pct_points": statistics.median(row["gap_reduction_pct_points"] for row in comparable) if n else None,
        "mean_start_gap_pct": statistics.mean(row["start_gap_pct"] for row in comparable) if n else None,
        "mean_end_gap_pct": statistics.mean(row["end_gap_pct"] for row in comparable) if n else None,
        "difference_vs_mirror": (rate("closer") - rate("mirror_closer")) if n else None}


def bootstrap(rows, repeats=2000, seed=7341):
    """Expiry-date cluster bootstrap: chains expiring together share market risk."""
    import numpy as np
    groups = defaultdict(list)
    for row in rows:
        if row["closer"] is not None:
            groups[row["expiry"]].append(row)
    if len(groups) < 10:
        return None
    blocks = list(groups.values())
    counts = np.array([len(block) for block in blocks])
    wins = np.array([sum(row["closer"] for row in block) for block in blocks])
    mirrors = np.array([sum(row["mirror_closer"] for row in block) for block in blocks])
    indexes = np.random.default_rng(seed).integers(0, len(blocks), size=(repeats, len(blocks)))
    denominator = counts[indexes].sum(axis=1)
    rates = wins[indexes].sum(axis=1) / denominator * 100
    differences = (wins - mirrors)[indexes].sum(axis=1) / denominator * 100
    return {"method": "Expiry-date cluster bootstrap", "repeats": repeats, "seed": seed,
        "rate_low": float(np.quantile(rates, .025)), "rate_high": float(np.quantile(rates, .975)),
        "difference_low": float(np.quantile(differences, .025)), "difference_high": float(np.quantile(differences, .975))}


def analyze(daily, candles, start, end):
    index = {(day, chain["symbol"], chain["expiry"]): chain
             for day, payload in daily.items() for chain in payload["chains"]}
    observations, exclusions, coverage, groups = [], [], [], []
    for symbol, label, key in UNIVERSE:
        bars = candles.get(symbol, {})
        sessions = sorted(bars)
        expiries = sorted({expiry for _, asset, expiry in index if asset == symbol and start <= expiry <= end})
        for expiry in expiries:
            for horizon in HORIZONS:
                base = {"symbol": symbol, "label": label, "expiry": expiry, "horizon": horizon}
                if expiry not in sessions:
                    exclusions.append({**base, "reason": "missing_expiry_candle"}); continue
                position = sessions.index(expiry)
                if position < horizon:
                    exclusions.append({**base, "reason": "missing_lookback_sessions"}); continue
                snapshot_day, entry_day = sessions[position - horizon], sessions[position - horizon + 1]
                base.update(snapshot_date=snapshot_day, entry_date=entry_day)
                if entry_day < start:
                    exclusions.append({**base, "reason": "entry_before_window"}); continue
                selected_days = sessions[position - horizon:position + 1]
                if any(day not in daily for day in selected_days):
                    exclusions.append({**base, "reason": "missing_nse_file"}); continue
                chain = index.get((snapshot_day, symbol, expiry))
                if not chain:
                    exclusions.append({**base, "reason": "missing_chain_snapshot"}); continue
                # Cross-source price agreement prevents adjusted/raw price mixtures.
                disagreement = False
                for day in selected_days:
                    prices = daily[day].get("spots", {}).get(symbol, [])
                    if not prices or any(abs(price - bars[day]["close"]) > max(.02, bars[day]["close"] * .0002) for price in prices):
                        disagreement = True; break
                if disagreement:
                    exclusions.append({**base, "reason": "underlying_close_not_corroborated"}); continue
                if any(contract_adjusted(chain, index[(day, symbol, expiry)]) for day in selected_days[1:]
                       if (day, symbol, expiry) in index):
                    exclusions.append({**base, "reason": "contract_strike_or_lot_adjustment"}); continue
                try:
                    target = chain_target(chain, allow_unpaired=True)
                except ValueError as exc:
                    exclusions.append({**base, "reason": str(exc)}); continue
                observations.append(observation(symbol, label, key, expiry, snapshot_day, entry_day, horizon, target, bars))
                if not target["strict_eligible"]:
                    exclusions.append({**base, "reason": "unpaired_strikes_strict_only"})
        coverage.append({"symbol": symbol, "label": label, "expiries_identified": len(expiries),
            "price_sessions": sum(start <= day <= end for day in sessions)})
    for horizon in HORIZONS:
      for coverage_mode in ("strict", "published"):
        eligible_rows = [row for row in observations if row["horizon"] == horizon and (coverage_mode == "published" or row["strict_eligible"])]
        for proximity in ("near", "all"):
            subset = [row for row in eligible_rows if proximity == "all" or row["near"]]
            per_asset = [{"symbol": symbol, "label": label,
                **summarize([row for row in subset if row["symbol"] == symbol])} for symbol, label, _ in UNIVERSE]
            months = sorted({row["entry_month"] for row in observations})
            eligible = len(eligible_rows)
            excluded = [row for row in exclusions if row["horizon"] == horizon and row["reason"] != "entry_before_window"
                        and (coverage_mode == "strict" or row["reason"] != "unpaired_strikes_strict_only")]
            groups.append({"horizon": horizon, "proximity": proximity, "coverage_mode": coverage_mode, "summary": summarize(subset),
                "confidence": bootstrap(subset), "by_asset": per_asset,
                "by_month": [{"month": month, **summarize([row for row in subset if row["entry_month"] == month])} for month in months],
                "data_coverage": {"eligible": eligible, "excluded": len(excluded),
                    "coverage_pct": eligible / (eligible + len(excluded)) * 100 if eligible + len(excluded) else None}})
    return {"observations": observations, "exclusions": exclusions, "coverage": coverage, "groups": groups,
            "exclusion_reasons": dict(Counter(row["reason"] for row in exclusions))}


def run_study(output_dir, progress_path=None):
    gateway = get_upstox()
    end = market_day() - timedelta(days=1)
    start = end - timedelta(days=364)
    warmup = start - timedelta(days=14)
    prices, price_sources, errors = {}, {}, []
    print(f"Study window {start} through {end}; warmup {warmup}", flush=True)
    for symbol, _, key in UNIVERSE:
        try:
            raw = gateway.get_historical_candles_v3(key, "days", 1, end.isoformat(), warmup.isoformat())
            prices[symbol] = candles_by_day(raw)
            price_sources[symbol] = {"instrument_key": key, "sessions": len(prices[symbol]), "source": raw.get("_provider", "upstox"),
                "first": min(prices[symbol]) if prices[symbol] else None, "last": max(prices[symbol]) if prices[symbol] else None}
            print(f"Prices {symbol}: {len(prices[symbol])} sessions", flush=True)
        except Exception as exc:
            prices[symbol] = {}
            errors.append({"symbol": symbol, "stage": "prices", "error": type(exc).__name__})
    sessions = sorted({day for bars in prices.values() for day in bars if warmup.isoformat() <= day <= end.isoformat()})
    if not sessions:
        raise ValueError("No underlying price history was available")
    archive = DailyArchive(gateway)
    daily = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(archive.read, day): day for day in sessions}
        for completed, job in enumerate(as_completed(jobs), 1):
            day = jobs[job]
            try:
                daily[day] = job.result()
            except Exception as exc:
                errors.append({"day": day, "stage": "NSE daily archive", "error": type(exc).__name__})
            if completed % 10 == 0 or completed == len(sessions):
                status = {"completed": completed, "total": len(sessions), "files_available": len(daily), "errors": len(errors)}
                print(json.dumps(status), flush=True)
                if progress_path:
                    Path(progress_path).write_text(json.dumps(status), encoding="utf-8")
    print("Analyzing frozen targets and bootstrapping by expiry date", flush=True)
    study = analyze(daily, prices, start.isoformat(), end.isoformat())
    primary = next(group for group in study["groups"] if group["horizon"] == 1 and group["proximity"] == "near")
    study.update(version=VERSION, generated_at=now().isoformat(), start_date=start.isoformat(), end_date=end.isoformat(),
        primary={"horizon": 1, "proximity": "near", "near_pct": 1, "coverage_mode": "strict"},
        universe=[{"symbol": symbol, "label": label, "instrument_key": key} for symbol, label, key in UNIVERSE],
        file_coverage={"expected_sessions": len(sessions), "available_files": len(daily),
            "first_file": min(daily) if daily else None, "last_file": max(daily) if daily else None},
        price_sources=price_sources, errors=errors,
        source_files=[{"date": day, "url": payload["source_url"], "sha256": payload["sha256"], "leg_count": payload["leg_count"]} for day, payload in sorted(daily.items())],
        methodology=[
            "Primary: snapshot T−1 end-of-day OI, expiry-day open to expiry close; near means initial spot within 1% of the frozen target.",
            "Secondary: snapshots T−3 and T−5 trading sessions, evaluated from the next session's open to expiry close. Horizons are not pooled.",
            "Targets use the same intrinsic-payout formula as the app. Ties select the lowest minimizing strike, without using future prices.",
            "Closer means the absolute expiry-close distance to the frozen target is smaller than the entry-open distance. A move toward it that overshoots can still finish farther away.",
            "Mirror control is an opposite-side target at the same initial distance from spot; it is a descriptive comparison, not proof of causality.",
            "95% intervals resample entire expiry dates, keeping chains that expire together in the same block; 2,000 samples, fixed seed 7341.",
            "Only official listed expiry dates from NSE files are used. No weekly/monthly expiry calendar is invented.",
            "Primary strict mode requires a published call and put at every included strike. The all-published sensitivity mode sums only actual published contracts, allows unmatched strikes, and makes no assertion about absent contracts. It is not verified complete-market OI.",
            "NSE underlying reference closes must agree with daily price closes within max(0.02, 2 basis points). Invalid/missing inputs and observable strike/lot adjustments are excluded and counted.",
            "Selected current instruments form a fixed research universe, not the complete historical F&O universe. Common market moves, survivorship, remaining corporate-action risk and source revisions limit inference.",
            "This measures spot convergence, not an executable option strategy. Official underlying close is an expiry proxy; fees, slippage, option premiums, margin and official settlement differences are not modeled.",
        ])
    summary = primary["summary"]
    report = {"slug": "max-pain-convergence-1y", "name": "Max Pain convergence · last 1 year",
        "strategy": "Frozen EOD Max Pain → expiry convergence", "instrument_key": "10 NSE option underlyings",
        "interval": "EOD → expiry", "start_date": start.isoformat(), "end_date": end.isoformat(),
        "metrics": {"kind": "max_pain_convergence", "observations": summary["n"], "convergence_rate": summary["closer_rate"],
                    "mirror_rate": summary["mirror_rate"], "horizon": 1, "near_pct": 1},
        "research": study, "equity": [], "trades": []}
    # The complete research run also survives outside the filesystem in Timescale.
    params = {"date": end.isoformat(), "start": start.isoformat(), "version": VERSION, "universe": [row[0] for row in UNIVERSE]}
    gateway.store.read("research_maxpain_convergence", params, lambda: report, force=True)
    path = Path(output_dir) / "max-pain-convergence-1y.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)
    print(json.dumps({"report": str(path), "primary": summary, "file_coverage": study["file_coverage"], "errors": errors}), flush=True)
    return report
