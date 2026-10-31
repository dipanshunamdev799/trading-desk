"""NIFTY credit-spread paper broker. No broker order API is used.

Both legs, their simulated fills and the journal commit together. The account
row serializes risk checks across entries, closes and settings changes.
"""
from __future__ import annotations

import copy
import csv
import io
import json
import math
import threading
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text

from .market_store import IST, now
from .market_session import timestamp
from .upstox_service import get_upstox, get_market_store, _normalize_candles

KEY = "NSE_INDEX|Nifty 50"


class Ticket(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    request_id: str = Field(min_length=8, max_length=100)
    strategy: Literal["BEAR_CALL", "BULL_PUT"]
    expiry: date
    short_strike: float = Field(gt=0)
    long_strike: float = Field(gt=0)
    lots: int = Field(ge=1, le=1000, strict=True)
    level: float = Field(gt=0)
    trend_confirmed: bool = False
    candle_confirmed: bool = False
    event_clear: bool = False
    entry_reason: str = Field(min_length=5, max_length=2000)


class AccountSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    capital: float = Field(ge=1000, le=1e10)
    fee_per_leg: float = Field(ge=0, le=10000)
    slippage: float = Field(ge=0, le=100)
    auto_exit: bool = True


class CloseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: Literal["MANUAL", "TECHNICAL_INVALIDATION"] = "MANUAL"
    notes: str = Field(default="", max_length=2000)


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def fresh(value, at, seconds=65):
    parsed = timestamp(value)
    return bool(parsed and 0 <= (at - parsed).total_seconds() <= seconds)


def executable(short, long, qty, closing=False, slippage=0):
    """Conservative top-of-book, all-or-none fills; never substitute LTP."""
    if not short or not long:
        return None
    for leg in (short, long):
        bid, ask = number(leg.get("bid")), number(leg.get("ask"))
        if bid is None or ask is None or bid <= 0 or ask <= 0 or bid > ask:
            return None
    sfield, lfield = ("ask", "bid") if closing else ("bid", "ask")
    if any((number(leg.get(field + "_qty")) or 0) < qty for leg, field in ((short, sfield), (long, lfield))):
        return None
    sell = (long if closing else short)["bid"] - slippage
    buy = (short if closing else long)["ask"] + slippage
    if sell < 0:
        return None
    net = buy - sell if closing else sell - buy
    if closing and net < 0:
        return None
    return {"net": round(net, 4), "short_fill": round(buy if closing else sell, 4),
            "long_fill": round(sell if closing else buy, 4)}


def evaluate(ticket, market, account, opened, hourly, at):
    side = "CE" if ticket.strategy == "BEAR_CALL" else "PE"
    legs = market.get("options", [])
    short = next((leg for leg in legs if leg["type"] == side and leg["strike"] == ticket.short_strike), None)
    long = next((leg for leg in legs if leg["type"] == side and leg["strike"] == ticket.long_strike), None)
    lot = short.get("lot_size") if short else None
    lot = int(lot) if lot and number(lot) and float(lot).is_integer() and lot > 0 else None
    qty = ticket.lots * lot if lot else 0
    width = abs(ticket.long_strike - ticket.short_strike)
    fill = executable(short, long, qty, slippage=account["slippage"]) if qty else None
    credit = fill["net"] if fill else None
    maximum_loss = (width - credit) * qty if credit is not None else None
    estimated_fees = account["fee_per_leg"] * 4
    # Brokerage is per leg order, not per lot. Entry costs plus an estimated exit.
    risk = maximum_loss + estimated_fees if maximum_loss is not None else None
    equity = account["capital"] + sum(t.get("net_pnl", 0) for t in opened if t["status"] == "CLOSED")
    active = [t for t in opened if t["status"] == "OPEN"]
    open_risk = sum(t["risk_reserved"] for t in active)
    local = at.astimezone(IST)
    dte = (ticket.expiry - local.date()).days
    bearish = ticket.strategy == "BEAR_CALL"
    trend = hourly.get("trend")
    last_closed = timestamp(hourly.get("closed_at"))
    trend_current = bool(last_closed and last_closed.astimezone(IST).date() == local.date()
                         and 0 <= (at - last_closed).total_seconds() <= 7200)
    checks = []
    def check(code, label, passed, detail):
        checks.append({"code": code, "label": label, "passed": bool(passed), "detail": detail})
    check("trend", "1-hour structure and 20 EMA agree", ticket.trend_confirmed and trend_current and
          trend == ("bearish" if bearish else "bullish"),
          f"Closed hourly bar: {trend or 'unavailable'}. Confirm structure or level rejection/retest.")
    check("candle", "15-minute confirmation candle has closed", ticket.candle_confirmed,
          "Manually confirm a completed breakdown/rejection or breakout/support candle.")
    spot = market.get("spot")
    beyond = bool(spot and (ticket.short_strike > ticket.level > spot if bearish else ticket.short_strike < ticket.level < spot))
    check("level", "OTM short strike is beyond resistance / support", beyond, f"Selected level {ticket.level:,.2f}; spot {spot or 'unavailable'}.")
    delta = number(short.get("delta")) if short else None
    check("delta", "Short absolute delta is 0.15–0.25", delta is not None and .15 <= abs(delta) <= .25 and
          short is not None and fresh(short.get("greeks_at"), at),
          f"Provider delta: {delta if delta is not None else 'unavailable'}.")
    check("dte", "Expiry is 7–21 calendar days away", 7 <= dte <= 21, f"{dte} calendar days to expiry.")
    check("credit", "Credit is at least 15% of width", credit is not None and 0 < credit < width and credit >= .15 * width,
          f"Executable credit {credit if credit is not None else 'unavailable'}; minimum {width * .15:.2f} pts.")
    check("position_risk", "Maximum loss fits 1% of capital", risk is not None and risk <= equity * .01,
          f"Risk including estimated costs: {risk if risk is not None else 'unavailable'}; limit ₹{equity * .01:,.2f}.")
    check("event", "No imminent major event / unacceptable gap risk", ticket.event_clear,
          "Manual event-calendar review; no automated event feed is connected.")
    check("exits", "50% target and 2× credit stop recorded", credit is not None and credit > 0,
          "Closing debit target = 0.5× credit; stop = 2× credit; time exit by 2 DTE.")
    check("portfolio", "Combined theoretical open risk fits 2%", risk is not None and open_risk + risk <= equity * .02,
          f"Existing reserved risk ₹{open_risk:,.2f}; portfolio limit ₹{equity * .02:,.2f}.")
    check("window", "Monday–Thursday, 10:00–14:30 IST", local.weekday() <= 3 and (10, 0) <= (local.hour, local.minute) <= (14, 30),
          local.strftime("%a %d %b %Y %H:%M IST"))
    check("market", "Verified open options session and recent depth", market.get("session", {}).get("active") and
          market.get("options_session", {}).get("active") and fresh(market.get("quote_at"), at),
          f"Bid/ask capture: {market.get('quote_at') or 'unavailable'}; no closed-market fills.")
    check("structure", "Same expiry, actual lot size, 100–300 pt hedge", short and long and lot and
          long.get("lot_size") == lot and 100 <= width <= 300 and
          (ticket.long_strike > ticket.short_strike if bearish else ticket.long_strike < ticket.short_strike),
          f"{side}; width {width:g}; contract lot size {lot or 'unavailable'}.")
    check("liquidity", "Both legs have usable bid/ask and sufficient depth", fill is not None,
          f"Requires {qty} units at top of book on each leg, with configured slippage.")
    check("averaging", "No averaging into an existing same-direction spread", not any(t["strategy"] == ticket.strategy for t in active),
          "One open spread per direction; same-direction positions are correlated.")
    return {"eligible": all(c["passed"] for c in checks), "checks": checks, "short": short, "long": long,
            "lot_size": lot, "qty": qty, "width": width, "credit": credit, "fill": fill, "dte": dte,
            "max_profit": credit * qty if credit is not None else None, "max_loss": maximum_loss,
            "risk_reserved": risk, "round_trip_fees": estimated_fees,
            "target_debit": credit * .5 if credit is not None else None,
            "stop_debit": credit * 2 if credit is not None else None,
            "quote_at": market.get("quote_at"), "hourly": hourly}


def exit_reason(trade, debit, at):
    if trade.get("exit_requested"):
        return trade["exit_requested"]["reason"]
    if (date.fromisoformat(trade["expiry"]) - at.astimezone(IST).date()).days <= 2:
        return "TIME_EXIT"
    if debit >= trade["stop_debit"]:
        return "STOP_LOSS"
    if debit <= trade["target_debit"]:
        return "PROFIT_TARGET"
    return None


class CreditSpreads:
    def __init__(self, store=None, gateway=None):
        self.store = store or get_market_store()
        self.gateway = gateway or get_upstox()
        self.cache = {}
        self.cache_lock = threading.RLock()
        self.load_locks = {}

    def cached(self, key, ttl, loader):
        with self.cache_lock:
            loader_lock = self.load_locks.setdefault(key, threading.Lock())
        # Chart history retrieval must not hold up the exit monitor's depth read.
        with loader_lock:
            hit = self.cache.get(key)
            if hit and time.monotonic() - hit[0] < ttl:
                return copy.deepcopy(hit[1])
            value = loader()
            self.cache[key] = (time.monotonic(), value)
            return copy.deepcopy(value)

    def chart(self, interval="1hour"):
        if interval not in ("1day", "1hour", "15minute"):
            raise ValueError("Choose Daily, 1 hour or 15 minutes")
        def load():
            unit, grain, days = {"1day": ("days", 1, 200), "1hour": ("hours", 1, 35), "15minute": ("minutes", 15, 10)}[interval]
            at = now()
            raw = self.gateway.get_historical_candles_v3(KEY, unit, grain,
                at.astimezone(IST).date().isoformat(), (at.astimezone(IST).date() - timedelta(days=days)).isoformat())
            candles = _normalize_candles(raw)
            duration = {"1day": 86400, "1hour": 3600, "15minute": 900}[interval]
            ema, points, closed = None, [], []
            for candle in candles:
                t = timestamp(candle["ts"])
                if not t:
                    continue
                # The final exchange hour ends at 15:30 even for a 15:15 bar.
                end = min(t + timedelta(seconds=duration), t.astimezone(IST).replace(hour=15, minute=30, second=0))
                is_closed = end <= at if interval != "1day" else t.astimezone(IST).date() < at.astimezone(IST).date() or end <= at
                if is_closed:
                    ema = candle["close"] if ema is None else candle["close"] * 2/21 + ema * 19/21
                    closed.append({**candle, "ema": ema, "closed_at": end.isoformat()})
                    if len(closed) >= 20:
                        points.append({"ts": candle["ts"], "value": ema})
            latest = closed[-1] if len(closed) >= 20 else None
            return {"interval": interval, "candles": candles[-150:], "ema": points[-150:],
                    "trend": ("bullish" if latest["close"] > latest["ema"] else "bearish" if latest["close"] < latest["ema"] else "neutral") if latest else None,
                    "closed_at": latest["closed_at"] if latest else None,
                    "ema_value": latest["ema"] if latest else None,
                    "checked_at": at.isoformat(), "source": "Stored / Upstox candles; EMA uses completed bars"}
        return self.cached(("chart", interval), 60, load)

    def market(self, expiry=None):
        def load():
            at = now()
            result = {"options": [], "expiries": [], "spot": None, "quote_at": None, "session": {}, "options_session": {},
                      "checked_at": at.isoformat(), "error": None, "expiry": expiry, "source": "Upstox REST bid/ask depth"}
            try:
                contracts = self.gateway.get_option_contracts(KEY)
                expiries = sorted({str(c["expiry"])[:10] for c in contracts if c.get("expiry") and str(c["expiry"])[:10] >= at.astimezone(IST).date().isoformat()})
                result["expiries"] = [{"date": e, "dte": (date.fromisoformat(e) - at.astimezone(IST).date()).days} for e in expiries]
                selected = expiry or next((e["date"] for e in result["expiries"] if 7 <= e["dte"] <= 21), None)
                result["expiry"] = selected
                result["session"] = self.gateway.get_market_session(KEY)
                if not selected:
                    result["error"] = "No listed expiry in the 7–21 DTE entry window."
                    return result
                if selected not in expiries:
                    raise ValueError("Expiry is not present in the retained contract master")
                chain = self.gateway.get_option_chain(KEY, selected)
                snapshot = self.gateway.get_current_option_chain_snapshot(KEY, selected) or {}
                # Streaming merges LTP/Greeks but not depth. Certify bid/ask using
                # the REST seed time, never the newer unrelated stream timestamp.
                result["quote_at"] = (snapshot.get("rest_seed_at") if snapshot.get("transport") == "websocket"
                                      else snapshot.get("rest_seed_at") or snapshot.get("observed_at"))
                master = {c["instrument_key"]: c for c in contracts if c.get("instrument_key") and str(c.get("expiry"))[:10] == selected}
                for row in chain:
                    if str(row.get("expiry"))[:10] != selected or row.get("underlying_key") != KEY:
                        continue
                    result["spot"] = number(row.get("underlying_spot_price")) or result["spot"]
                    for name, side in (("call_options", "CE"), ("put_options", "PE")):
                        leg = row.get(name) or {}
                        contract = master.get(leg.get("instrument_key"))
                        if not contract or contract.get("instrument_type") != side or number(contract.get("strike_price")) != number(row.get("strike_price")):
                            continue
                        md, greek = leg.get("market_data") or {}, leg.get("option_greeks") or {}
                        result["options"].append({"key": leg["instrument_key"], "type": side,
                            "strike": number(row.get("strike_price")), "lot_size": number(contract.get("lot_size")),
                            **{field: number(md.get(source)) for field, source in (("bid", "bid_price"), ("ask", "ask_price"),
                                ("bid_qty", "bid_qty"), ("ask_qty", "ask_qty"), ("ltp", "ltp"))},
                            "delta": number(greek.get("delta")), "iv": number(greek.get("iv")),
                            "greeks_at": (leg.get("_provenance") or {}).get("greeks_at") or result["quote_at"]})
                if result["options"]:
                    result["options_session"] = self.gateway.get_market_session(result["options"][0]["key"])
            except Exception as exc:
                result["error"] = f"Market data unavailable ({type(exc).__name__}); fills are blocked."
                result["options"] = []
            return result
        return self.cached(("market", expiry), 10, load)

    def _account(self, conn, lock=False):
        return dict(conn.execute(text("SELECT settings FROM credit_spread_account WHERE id=1" + (" FOR UPDATE" if lock else ""))).scalar_one())

    def _trades(self, conn):
        return [dict(row) for row in conn.execute(text("SELECT payload FROM credit_spread_trades ORDER BY created_at")).scalars()]

    def _save_trade(self, conn, trade):
        conn.execute(text("UPDATE credit_spread_trades SET status=:status,payload=CAST(:payload AS jsonb) WHERE id=:id"),
                     {"id": trade["id"], "status": trade["status"], "payload": json.dumps(trade)})

    def _order(self, conn, order):
        conn.execute(text("INSERT INTO credit_spread_orders(id,request_id,trade_id,payload) VALUES(:id,:request_id,:trade_id,CAST(:payload AS jsonb))"),
                     {"id": order["id"], "request_id": order["request_id"], "trade_id": order.get("trade_id"), "payload": json.dumps(order)})

    def preview(self, ticket):
        market = self.market(ticket.expiry.isoformat())
        try:
            hourly = self.chart()
        except Exception:
            hourly = {}
        with self.store.engine.connect() as conn:
            return evaluate(ticket, market, self._account(conn), self._trades(conn), hourly, now())

    def enter(self, ticket):
        with self.store.engine.connect() as conn:
            previous = conn.execute(text("SELECT payload FROM credit_spread_orders WHERE request_id=:id"), {"id": ticket.request_id}).scalar()
            if previous:
                return previous
        market = self.market(ticket.expiry.isoformat())
        try:
            hourly = self.chart()
        except Exception:
            hourly = {}
        with self.store.engine.begin() as conn:
            settings = self._account(conn, True)
            previous = conn.execute(text("SELECT payload FROM credit_spread_orders WHERE request_id=:id"), {"id": ticket.request_id}).scalar()
            if previous:
                return previous
            at = now()
            preview = evaluate(ticket, market, settings, self._trades(conn), hourly, at)
            order = {"id": uuid.uuid4().hex, "request_id": ticket.request_id, "created_at": at.isoformat(),
                     "action": "ENTRY", "status": "FILLED" if preview["eligible"] else "REJECTED",
                     "ticket": ticket.model_dump(mode="json"), "checks": preview["checks"], "legs": [], "paper": True}
            if preview["eligible"]:
                trade_id = uuid.uuid4().hex
                trade = {**ticket.model_dump(mode="json"), **{k: preview[k] for k in
                    ("short", "long", "lot_size", "qty", "width", "credit", "dte", "max_profit", "max_loss", "risk_reserved", "target_debit", "stop_debit", "quote_at")},
                    "id": trade_id, "status": "OPEN", "created_at": at.isoformat(), "entry_checks": preview["checks"],
                    "entry_hourly": hourly, "entry_iv": preview["short"]["iv"], "entry_delta": preview["short"]["delta"],
                    "entry_fees": settings["fee_per_leg"] * 2, "fee_per_leg": settings["fee_per_leg"], "slippage": settings["slippage"],
                    "last_debit": None, "unrealized_pnl": None, "net_pnl": 0, "mae": 0, "mfe": 0, "exit_requested": None}
                # Retain only the entry indicator summary, not duplicate chart history.
                trade["entry_hourly"] = {k: hourly.get(k) for k in ("trend", "ema_value", "closed_at")}
                conn.execute(text("INSERT INTO credit_spread_trades(id,request_id,status,payload) VALUES(:id,:request_id,'OPEN',CAST(:payload AS jsonb))"),
                             {"id": trade_id, "request_id": ticket.request_id, "payload": json.dumps(trade)})
                order.update(trade_id=trade_id, net_price=preview["credit"], fees=trade["entry_fees"], quote_at=market["quote_at"],
                    legs=[{"key": preview["short"]["key"], "side": "SELL", "qty": preview["qty"], "price": preview["fill"]["short_fill"]},
                          {"key": preview["long"]["key"], "side": "BUY", "qty": preview["qty"], "price": preview["fill"]["long_fill"]}])
            self._order(conn, order)
            return order

    def settings(self, value):
        with self.store.engine.begin() as conn:
            self._account(conn, True)
            trades = self._trades(conn)
            if any(t["status"] == "OPEN" for t in trades):
                raise ValueError("Close open spreads before changing capital or execution assumptions.")
            conn.execute(text("UPDATE credit_spread_account SET settings=CAST(:value AS jsonb) WHERE id=1"), {"value": value.model_dump_json()})
        return value.model_dump()

    def close(self, trade_id, request):
        with self.store.engine.begin() as conn:
            self._account(conn, True)
            trade = conn.execute(text("SELECT payload FROM credit_spread_trades WHERE id=:id"), {"id": trade_id}).scalar()
            if trade is None:
                raise ValueError("Spread was not found")
            if trade["status"] == "CLOSED" or trade.get("exit_requested"):
                return trade
            trade["exit_requested"] = {"reason": request.reason, "notes": request.notes, "at": now().isoformat()}
            self._save_trade(conn, trade)
            self._order(conn, {"id": uuid.uuid4().hex, "request_id": "request-close-" + trade_id,
                "trade_id": trade_id, "created_at": now().isoformat(), "action": "EXIT_REQUEST", "status": "QUEUED",
                "reason": request.reason, "notes": request.notes, "legs": [], "paper": True})
        # Monitor retries queued exits even after a restart or browser closure.
        self.monitor()
        with self.store.engine.connect() as conn:
            return conn.execute(text("SELECT payload FROM credit_spread_trades WHERE id=:id"), {"id": trade_id}).scalar_one()

    def monitor(self):
        with self.store.engine.connect() as conn:
            opened = [t for t in self._trades(conn) if t["status"] == "OPEN"]
        errors = []
        markets = {e: self.market(e) for e in {t["expiry"] for t in opened}}
        with self.store.engine.begin() as conn:
            settings = self._account(conn, True)
            at = now()
            for trade in self._trades(conn):
                if trade["status"] != "OPEN":
                    continue
                market = markets.get(trade["expiry"])
                if not market:
                    continue
                indexed = {leg["key"]: leg for leg in market["options"]}
                fill = executable(indexed.get(trade["short"]["key"]), indexed.get(trade["long"]["key"]),
                                  trade["qty"], True, trade["slippage"])
                usable = bool(fill and market.get("session", {}).get("active") and
                              market.get("options_session", {}).get("active") and fresh(market.get("quote_at"), at))
                trade["mark_fresh"] = usable
                trade["last_checked_at"] = at.isoformat()
                if not usable:
                    trade["mark_error"] = market.get("error") or "Waiting for an open session and usable bid/ask depth."
                    errors.append(trade["mark_error"])
                    self._save_trade(conn, trade)
                    continue
                debit = fill["net"]
                pnl = round((trade["credit"] - debit) * trade["qty"] - trade["entry_fees"] - trade["fee_per_leg"] * 2, 2)
                trade.update(last_debit=debit, mark_at=market["quote_at"], unrealized_pnl=pnl, mark_error=None,
                             mae=max(trade["mae"], -pnl, 0), mfe=max(trade["mfe"], pnl, 0))
                conn.execute(text("INSERT INTO credit_spread_marks(trade_id,quote_at,payload) VALUES(:id,:at,CAST(:value AS jsonb)) ON CONFLICT DO NOTHING"),
                             {"id": trade["id"], "at": market["quote_at"], "value": json.dumps({"ts": market["quote_at"], "debit": debit, "pnl": pnl})})
                reason = exit_reason(trade, debit, at) if settings["auto_exit"] or trade.get("exit_requested") else None
                if not reason and settings["auto_exit"] and self.last_session_before_exit(trade["expiry"], at):
                    reason = "TIME_EXIT"
                if reason:
                    trade.update(status="CLOSED", closed_at=at.isoformat(), exit_debit=debit, exit_reason=reason,
                                 exit_fees=trade["fee_per_leg"] * 2, net_pnl=pnl, unrealized_pnl=0,
                                 gross_pnl=round((trade["credit"] - debit) * trade["qty"], 2), return_on_risk=pnl / trade["risk_reserved"])
                    self._order(conn, {"id": uuid.uuid4().hex, "request_id": "close-" + trade["id"], "trade_id": trade["id"],
                        "created_at": at.isoformat(), "action": "EXIT", "status": "FILLED", "net_price": debit,
                        "reason": reason, "fees": trade["exit_fees"], "quote_at": market["quote_at"], "paper": True,
                        "legs": [{"key": trade["short"]["key"], "side": "BUY", "qty": trade["qty"], "price": fill["short_fill"]},
                                 {"key": trade["long"]["key"], "side": "SELL", "qty": trade["qty"], "price": fill["long_fill"]}]})
                self._save_trade(conn, trade)
            conn.execute(text("UPDATE credit_spread_account SET monitor_at=:at,monitor_error=:error WHERE id=1"),
                         {"at": at, "error": "; ".join(sorted(set(errors))) or None})

    def last_session_before_exit(self, expiry, at):
        """Exit before a closed 2-DTE day rather than waiting until 1 DTE.

        Exchange calendars, including special sessions, take precedence over a
        weekday assumption. If the near-expiry calendar cannot be verified,
        conservatively exit early at the next executable observation.
        """
        local_day = at.astimezone(IST).date()
        deadline = date.fromisoformat(expiry) - timedelta(days=2)
        days = (deadline - local_day).days
        if days <= 0:
            return True
        if days > 3:
            return False
        def load():
            for offset in range(1, days + 1):
                day = (local_day + timedelta(days=offset)).isoformat()
                rows = self.gateway.get_market_timings(day)
                if not isinstance(rows, list):
                    return True
                if any(row.get("exchange") == "NFO" and timestamp(row.get("start_time")) and
                       timestamp(row.get("end_time")) for row in rows):
                    return False
            return True
        try:
            return self.cached(("exit-calendar", expiry, local_day.isoformat()), 3600, load)
        except Exception:
            return True

    def dashboard(self):
        at = now()
        with self.store.engine.connect() as conn:
            settings = self._account(conn)
            status = conn.execute(text("SELECT monitor_at,monitor_error FROM credit_spread_account WHERE id=1")).mappings().one()
            trades = self._trades(conn)
            orders = list(conn.execute(text("SELECT payload FROM credit_spread_orders ORDER BY created_at DESC LIMIT 500")).scalars())
        for trade in trades:
            trade["mark_fresh"] = bool(trade.get("mark_fresh") and fresh(trade.get("mark_at"), at))
        closed = sorted((t for t in trades if t["status"] == "CLOSED"), key=lambda t: t["closed_at"])
        opened = [t for t in trades if t["status"] == "OPEN"]
        realized = round(sum(t["net_pnl"] for t in closed), 2)
        unrealized = sum(t["unrealized_pnl"] or 0 for t in opened)
        # An entry without a usable closing mark has unknown account MTM.
        known = all(t["unrealized_pnl"] is not None for t in opened)
        equity, high, drawdown, curve = settings["capital"], settings["capital"], 0, []
        if closed:
            curve.append({"ts": min(t["created_at"] for t in closed), "equity": equity, "drawdown": 0})
        for trade in closed:
            equity += trade["net_pnl"]
            high = max(high, equity)
            dd = high - equity
            drawdown = max(drawdown, dd)
            curve.append({"ts": trade["closed_at"], "equity": round(equity, 2), "drawdown": round(dd, 2)})
        wins = [t for t in closed if t["net_pnl"] > 0]
        losses = [t for t in closed if t["net_pnl"] < 0]
        return {"settings": settings, "monitor": {"at": status["monitor_at"].isoformat() if status["monitor_at"] else None,
                "error": status["monitor_error"]}, "trades": list(reversed(trades)), "orders": orders,
                "marks": [], "equity_curve": curve,
                "summary": {"realized_pnl": realized, "unrealized_pnl": round(unrealized, 2) if known else None,
                    "equity": round(settings["capital"] + realized + unrealized, 2) if known else None,
                    "open_count": len(opened), "closed_count": len(closed), "open_risk": sum(t["risk_reserved"] for t in opened),
                    "risk_limit": (settings["capital"] + realized) * .02, "win_rate": len(wins) / len(closed) * 100 if closed else None,
                    "expectancy": realized / len(closed) if closed else None, "max_drawdown": round(drawdown, 2),
                    "return_on_risk": realized / sum(t["risk_reserved"] for t in closed) * 100 if closed else None,
                    "profit_factor": sum(t["net_pnl"] for t in wins) / -sum(t["net_pnl"] for t in losses) if losses else None,
                    "fees": sum(t["entry_fees"] + t.get("exit_fees", 0) for t in trades),
                    "marks_stale": any(not t["mark_fresh"] for t in opened)}, "checked_at": at.isoformat()}

    def marks(self, trade_id):
        # A growing journal must not resend every historical mark on each account
        # poll. The selected chart loads its own recent observations; all raw
        # observations remain in PostgreSQL without an automatic retention limit.
        with self.store.engine.connect() as conn:
            rows = conn.execute(text("SELECT payload FROM credit_spread_marks WHERE trade_id=:id ORDER BY quote_at DESC LIMIT 3000"),
                                {"id": trade_id}).scalars().all()
        return [{"trade_id": trade_id, **row} for row in reversed(rows)]

    def export(self, kind):
        dashboard = self.dashboard()
        if kind == "orders":
            with self.store.engine.connect() as conn:
                rows = list(conn.execute(text("SELECT payload FROM credit_spread_orders ORDER BY created_at DESC")).scalars())
        else:
            rows = dashboard["trades"]
        keys = (["id", "trade_id", "created_at", "action", "status", "net_price", "fees", "reason", "quote_at", "legs", "checks"] if kind == "orders" else
                ["id", "strategy", "status", "created_at", "closed_at", "expiry", "short_strike", "long_strike", "lots", "lot_size", "qty", "entry_delta", "entry_iv", "dte", "width", "credit", "max_loss", "risk_reserved", "target_debit", "stop_debit", "exit_debit", "gross_pnl", "net_pnl", "entry_fees", "exit_fees", "mae", "mfe", "return_on_risk", "entry_reason", "exit_reason", "exit_requested"])
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            values = {k: json.dumps(row[k]) if isinstance(row.get(k), (dict, list)) else row.get(k, "") for k in keys}
            # Spreadsheet formula injection protection for free-text journal fields.
            writer.writerow({k: "'" + v if isinstance(v, str) and v.startswith(("=", "+", "-", "@")) else v for k, v in values.items()})
        return output.getvalue()


@lru_cache
def get_credit_spreads():
    return CreditSpreads()
