"""One shared, session-aware Upstox feed for market readers and browser updates."""
from __future__ import annotations

import copy
import logging
import json
import queue
import threading
import time
import uuid
from collections import deque
from datetime import timedelta

from .market_session import MarketSessions, timestamp
from .market_store import IST, now
from .market_stream_store import MarketStreamStore

LOG = logging.getLogger(__name__)


def feed_data(feed):
    full = feed.get("fullFeed") or feed.get("ff") or {}
    return full.get("marketFF") or full.get("indexFF") or feed.get("firstLevelWithGreeks") or feed


class MarketStream:
    def __init__(self, gateway, settings, ws_factory=None):
        self.gateway, self.settings = gateway, settings
        self.repo = MarketStreamStore(gateway.store)
        self.sessions = MarketSessions(gateway)
        self.ws_factory = ws_factory
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.queue = queue.Queue(maxsize=10000)
        self.leases, self.owners, self.chains, self.ticks = {}, {}, {}, {}
        self.ws, self.thread, self.writer = None, None, None
        self.connected, self.generation = False, ""
        self.last_error, self.last_frame_at = None, None
        self.active_keys = set()
        self.revision, self.events = 0, deque(maxlen=1000)
        self.archived_minutes = {}

    def start(self):
        if not self.settings.market_stream_enabled or self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.writer = threading.Thread(target=self._write_loop, name="market-feed-writer", daemon=True)
        self.thread = threading.Thread(target=self._control_loop, name="market-feed-control", daemon=True)
        self.writer.start()
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.ws:
            self.ws.stop()
        for thread in (self.thread, self.writer):
            if thread and thread is not threading.current_thread():
                thread.join(timeout=5)

    @staticmethod
    def owner(key):
        if key.startswith("NSE_"):
            return "NSE_INDEX|Nifty 50"
        if key.startswith("BSE_"):
            return "BSE_INDEX|SENSEX"
        return key

    def watch(self, keys, owner=None, renew_group=False):
        with self.lock:
            until = time.monotonic() + 600
            if renew_group:
                groups = set(keys)
                for key, parent in self.owners.items():
                    if parent in groups:
                        self.leases[key] = until
            for key in keys:
                if key not in self.leases and len(self.leases) >= self.settings.market_stream_max_instruments:
                    self.last_error = "Subscription limit reached; additional instruments use REST."
                    continue
                self.leases[key] = until
                self.owners[key] = owner or self.owners.get(key) or self.owner(key)

    def seed_chain(self, underlying, expiry, rows, metadata):
        if not isinstance(rows, list) or not rows:
            return
        if any(not isinstance(row, dict) or row.get("expiry", expiry) != expiry or row.get("underlying_key", underlying) != underlying for row in rows):
            raise ValueError("Option chain expiry or underlying does not match the request")
        keys = [underlying] + [row[side]["instrument_key"] for row in rows for side in ("call_options", "put_options")
                              if isinstance(row.get(side), dict) and row[side].get("instrument_key")]
        self.watch(keys, owner=underlying)
        with self.lock:
            self.chains[(underlying, expiry)] = (copy.deepcopy(rows), dict(metadata))

    def _on_connect(self, _):
        with self.lock:
            self.connected, self.generation = True, uuid.uuid4().hex
            self.ticks.clear()
            self.last_frame_at = None
            self.last_error = None

    def _on_close(self, *_):
        with self.lock:
            self.connected = False

    def _on_error(self, error):
        with self.lock:
            self.connected = False
            # Provider exceptions can include one-time authorized URLs. Never expose them.
            self.last_error = f"Live feed unavailable ({type(error).__name__}); using REST fallback."

    def _on_market_info(self, frame):
        self.sessions.update_segments((frame.get("marketInfo") or {}).get("segmentStatus") or {})

    def _on_ticks(self, frame):
        if not isinstance(frame.get("feeds"), dict):
            return
        try:
            json.dumps(frame, allow_nan=False)
            frame = {**frame, "_connection_generation": self.generation}
            self.queue.put((frame, now()), timeout=2)
        except (queue.Full, ValueError, TypeError):
            self._on_error(BufferError())
            if self.ws:
                self.ws.stop()

    def _apply(self, frame, received):
        at = timestamp(frame.get("currentTs"))
        if at is None or at > received + timedelta(seconds=5):
            return  # Still archived, but undated/future frames cannot become live values.
        changed = set()
        with self.lock:
            if frame.get("_connection_generation", self.generation) != self.generation:
                return
            for key, feed in frame.get("feeds", {}).items():
                values = feed_data(feed)
                previous = self.ticks.get(key)
                if previous and previous["at"] > at:
                    continue
                item = previous or {"fields": {}, "times": {}, "generation": self.generation}
                for field in ("ltpc", "optionGreeks", "marketOHLC", "oi", "iv", "vtt", "atp", "marketLevel"):
                    if field in values:
                        item["fields"][field] = copy.deepcopy(values[field])
                        item["times"][field] = at
                item.update(at=at, received=received, generation=self.generation)
                self.ticks[key] = item
                changed.update((key, self.owners.get(key, key)))
            self.last_frame_at = at.isoformat()
            self.revision += 1
            self.events.append((self.revision, sorted(changed)))

    def _write_loop(self):
        pending = []
        while not self.stop_event.is_set() or not self.queue.empty() or pending:
            if not pending:
                try:
                    pending.append(self.queue.get(timeout=.25))
                except queue.Empty:
                    continue
                while len(pending) < 1000:
                    try:
                        pending.append(self.queue.get_nowait())
                    except queue.Empty:
                        break
            try:
                self.repo.ticks(pending)
                for frame, received in pending:
                    self._apply(frame, received)
                    self.queue.task_done()
                pending = []
            except Exception as exc:
                self._on_error(exc)
                if self.ws:
                    self.ws.stop()
                if self.stop_event.wait(1):
                    LOG.error("Market-feed storage failed during shutdown; uncommitted updates were not published")
                    break

    def _control_loop(self):
        while not self.stop_event.is_set():
            try:
                self.maintain()
            except Exception as exc:
                self._on_error(exc)
            self.stop_event.wait(5)

    def maintain(self):
        with self.lock:
            expired = [key for key, until in self.leases.items() if until < time.monotonic()]
            for key in expired:
                self.leases.pop(key, None)
                self.owners.pop(key, None)
                self.ticks.pop(key, None)
            for identity in list(self.chains):
                if identity[0] not in self.leases:
                    self.chains.pop(identity, None)
                    self.archived_minutes.pop(identity, None)
            owners = dict(self.owners)
        contexts = {owner: self.sessions.context(owner) for owner in set(owners.values())}
        active = {key for key, owner in owners.items() if contexts[owner]["active"]}
        if not active:
            if self.ws:
                self.ws.stop()
                self.ws = None
            with self.lock:
                self.connected = False
                self.active_keys.clear()
            return
        if self.ws is not None and not self.ws.is_running:
            self.ws = None
        if self.ws is None:
            if self.ws_factory is None:
                from upstox_ws_v3 import UpstoxMarketDataWSV3
                factory = UpstoxMarketDataWSV3
            else:
                factory = self.ws_factory
            gateway = self.gateway
            class Authorization:
                def get_market_data_feed_ws_url_v3(self):
                    return gateway._remote_call("get_market_data_feed_ws_url_v3")
            self.ws = factory(Authorization(), on_ticks=self._on_ticks, on_market_info=self._on_market_info,
                              on_connect=self._on_connect, on_close=self._on_close, on_error=self._on_error)
            self.ws.subscribe(sorted(active), mode="full")
            self.active_keys = active
            self.ws.start_background()
        else:
            added, removed = active - self.active_keys, self.active_keys - active
            if added:
                self.ws.subscribe(sorted(added), mode="full")
            if removed:
                self.ws.unsubscribe(sorted(removed), mode="full")
            self.active_keys = active
        for underlying, expiry in list(self.chains):
            if underlying not in contexts or not contexts[underlying]["active"]:
                continue
            minute = now().replace(second=0, microsecond=0)
            if self.archived_minutes.get((underlying, expiry)) == minute:
                continue
            captured = self.chain(underlying, expiry)
            if captured and captured[1].get("transport") == "websocket":
                self.repo.chain(underlying, expiry, captured[0], captured[1])
                self.archived_minutes[(underlying, expiry)] = minute

    def fresh(self, item, field):
        at = item["times"].get(field)
        return self.connected and item.get("generation") == self.generation and at is not None and \
            at.astimezone(IST).date() == now().astimezone(IST).date() and 0 <= (now() - at).total_seconds() <= self.settings.market_stream_stale_seconds

    def chain(self, underlying, expiry):
        with self.lock:
            seeded = self.chains.get((underlying, expiry))
            if not seeded:
                return None
            rows, provenance = copy.deepcopy(seeded)
            latest, received, greek_at, oi_at, live_legs, live_oi_legs = None, None, None, None, 0, 0
            volume_at, live_volume_legs = None, 0
            for row in rows:
                for side in ("call_options", "put_options"):
                    option = row.get(side) or {}
                    item = self.ticks.get(option.get("instrument_key"))
                    option["_provenance"] = {"greeks_source": "rest", "greeks_at": provenance.get("observed_at"),
                                             "iv_source": "rest", "iv_at": provenance.get("observed_at")}
                    if not item or option.get("instrument_key") not in self.active_keys:
                        continue
                    fields = item["fields"]
                    md = option.setdefault("market_data", {})
                    if self.fresh(item, "ltpc"):
                        md["ltp"] = fields["ltpc"].get("ltp")
                    for field, target in (("oi", "oi"), ("vtt", "volume"), ("atp", "average_price")):
                        if self.fresh(item, field):
                            md[target] = fields[field]
                            if field == "oi":
                                live_oi_legs += 1
                                oi_at = max(oi_at, item["times"]["oi"]) if oi_at else item["times"]["oi"]
                            elif field == "vtt":
                                live_volume_legs += 1
                                volume_at = max(volume_at, item["times"]["vtt"]) if volume_at else item["times"]["vtt"]
                    if self.fresh(item, "optionGreeks"):
                        option.setdefault("option_greeks", {}).update(fields["optionGreeks"])
                        option["_provenance"].update(greeks_source="websocket", greeks_at=item["times"]["optionGreeks"].isoformat())
                        greek_at = max(greek_at, item["times"]["optionGreeks"]) if greek_at else item["times"]["optionGreeks"]
                        live_legs += 1
                    if self.fresh(item, "iv"):
                        # Feed V3 IV is a fraction; option-chain IV is a percentage.
                        option.setdefault("option_greeks", {})["iv"] = float(fields["iv"]) * 100
                        option["_provenance"].update(iv_source="websocket", iv_at=item["times"]["iv"].isoformat())
                    if any(self.fresh(item, field) for field in ("ltpc", "oi", "vtt", "optionGreeks", "iv")):
                        latest = max(latest, item["at"]) if latest else item["at"]
                        received = max(received, item["received"]) if received else item["received"]
                spot = self.ticks.get(underlying)
                if spot and self.fresh(spot, "ltpc"):
                    row["underlying_spot_price"] = spot["fields"]["ltpc"].get("ltp")
                    provenance.update(spot_source="websocket", spot_reported_at=spot["times"]["ltpc"].isoformat())
            if latest:
                provenance.update(transport="websocket", reported_at=latest.isoformat(), observed_at=received.isoformat(),
                                  session_date=latest.astimezone(IST).date().isoformat(), live_legs=live_legs, live_oi_legs=live_oi_legs,
                                  greeks_reported_at=greek_at.isoformat() if greek_at else None,
                                  oi_reported_at=oi_at.isoformat() if oi_at else None)
                provenance.update(live_volume_legs=live_volume_legs,
                                  volume_reported_at=volume_at.isoformat() if volume_at else None)
            return rows, provenance

    def quotes(self, keys):
        self.watch(keys)
        result = {}
        with self.lock:
            for key in keys:
                item = self.ticks.get(key)
                if key not in self.active_keys or not item or not self.fresh(item, "ltpc"):
                    continue
                ltpc = item["fields"]["ltpc"]
                ltp, cp = ltpc.get("ltp"), ltpc.get("cp")
                entry = {"instrument_token": key, "last_price": ltp, "last_trade_time": ltpc.get("ltt"),
                         "timestamp": item["at"].isoformat(), "cp": cp, "close_price": cp,
                         "net_change": ltp - cp if ltp is not None and cp is not None else None,
                         "_transport": "websocket", "_observed_at": item["received"].isoformat()}
                for field, target in (("oi", "oi"), ("vtt", "volume"), ("atp", "average_price")):
                    if self.fresh(item, field):
                        entry[target] = item["fields"][field]
                if self.fresh(item, "marketOHLC"):
                    bars = item["fields"]["marketOHLC"].get("ohlc", [])
                    daily = next((row for row in bars if row.get("interval") == "1d"), {})
                    entry["ohlc"] = {**daily, "close": cp}
                    entry["_live_candles"] = bars
                if self.fresh(item, "optionGreeks"):
                    entry["option_greeks"] = item["fields"]["optionGreeks"]
                if self.fresh(item, "iv"):
                    entry["iv"] = item["fields"]["iv"]
                result[key] = entry
        return result

    def updates(self, since=0):
        with self.lock:
            keys = sorted({key for revision, keys in self.events if revision > since for key in keys})
            return {"type": "market_update", "revision": self.revision, "instrument_keys": keys, "status": self.status()}

    def status(self):
        with self.lock:
            frame_at = timestamp(self.last_frame_at)
            fresh = bool(self.connected and frame_at and 0 <= (now() - frame_at).total_seconds() <= self.settings.market_stream_stale_seconds)
            return {"enabled": self.settings.market_stream_enabled, "connected": self.connected,
                    "active_instruments": len(self.active_keys), "watched_instruments": len(self.leases),
                    "last_frame_at": self.last_frame_at, "error": self.last_error,
                    "fresh": fresh, "mode": "websocket" if fresh else "rest", "queued_frames": self.queue.qsize()}
