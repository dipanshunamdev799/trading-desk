"""
upstox_ws_v3.py
Reusable async & background-threaded WebSocket client for Upstox Market Data Feed V3.
Automatically compiles the V3 Protobuf schema in memory (no external _pb2.py file needed)
and decodes binary ticks into clean Python dictionaries.
"""

import asyncio
import json
import logging
import ssl
import threading
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import websockets
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
from google.protobuf.json_format import MessageToDict
from google.protobuf import wrappers_pb2  # registers the official DoubleValue dependency

from upstox_analytics import UpstoxAnalyticsClient

logger = logging.getLogger("UpstoxMarketDataWSV3")


def _build_v3_feed_response_class():
    """
    Dynamically constructs the official Upstox MarketDataFeedV3 Protobuf schema
    in memory so no external `MarketDataFeedV3_pb2.py` file is required.
    """
    pool = descriptor_pool.Default()
    file_name = "upstox_market_data_feed_v3_dynamic.proto"

    try:
        file_desc = pool.FindFileByName(file_name)
        return message_factory.GetMessageClass(file_desc.message_types_by_name["FeedResponse"])
    except KeyError:
        pass

    fdp = descriptor_pb2.FileDescriptorProto()
    fdp.name = file_name
    fdp.package = "com.upstox.marketdatafeederv3udapi.rpc.proto"
    fdp.syntax = "proto3"
    fdp.dependency.append("google/protobuf/wrappers.proto")

    # Helper to add primitive fields
    def add_field(msg, name, number, field_type, label=descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL, type_name=None):
        f = msg.field.add()
        f.name = name
        f.number = number
        f.type = field_type
        f.label = label
        if type_name:
            f.type_name = type_name

    T_DOUBLE = descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE
    T_INT64 = descriptor_pb2.FieldDescriptorProto.TYPE_INT64
    T_INT32 = descriptor_pb2.FieldDescriptorProto.TYPE_INT32
    T_STRING = descriptor_pb2.FieldDescriptorProto.TYPE_STRING
    T_MSG = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    T_ENUM = descriptor_pb2.FieldDescriptorProto.TYPE_ENUM
    L_REP = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED

    # 1. LTPC
    ltpc = fdp.message_type.add(name="LTPC")
    add_field(ltpc, "ltp", 1, T_DOUBLE)
    add_field(ltpc, "ltt", 2, T_INT64)
    add_field(ltpc, "ltq", 3, T_INT64)
    add_field(ltpc, "cp", 4, T_DOUBLE)
    add_field(ltpc, "iep", 5, T_MSG, type_name=".google.protobuf.DoubleValue")

    # 2. Quote (Bid/Ask level)
    quote = fdp.message_type.add(name="Quote")
    add_field(quote, "bidQ", 1, T_INT64)
    add_field(quote, "bidP", 2, T_DOUBLE)
    add_field(quote, "askQ", 3, T_INT64)
    add_field(quote, "askP", 4, T_DOUBLE)

    # 3. MarketLevel
    m_level = fdp.message_type.add(name="MarketLevel")
    add_field(m_level, "bidAskQuote", 1, T_MSG, L_REP, "Quote")

    # 4. OHLC & MarketOHLC
    ohlc = fdp.message_type.add(name="OHLC")
    add_field(ohlc, "interval", 1, T_STRING)
    add_field(ohlc, "open", 2, T_DOUBLE)
    add_field(ohlc, "high", 3, T_DOUBLE)
    add_field(ohlc, "low", 4, T_DOUBLE)
    add_field(ohlc, "close", 5, T_DOUBLE)
    add_field(ohlc, "vol", 6, T_INT64)
    add_field(ohlc, "ts", 7, T_INT64)

    m_ohlc = fdp.message_type.add(name="MarketOHLC")
    add_field(m_ohlc, "ohlc", 1, T_MSG, L_REP, "OHLC")

    # 5. OptionGreeks
    greeks = fdp.message_type.add(name="OptionGreeks")
    add_field(greeks, "delta", 1, T_DOUBLE)
    add_field(greeks, "theta", 2, T_DOUBLE)
    add_field(greeks, "gamma", 3, T_DOUBLE)
    add_field(greeks, "vega", 4, T_DOUBLE)
    add_field(greeks, "rho", 5, T_DOUBLE)

    # 6. MarketFullFeed
    m_full = fdp.message_type.add(name="MarketFullFeed")
    add_field(m_full, "ltpc", 1, T_MSG, type_name="LTPC")
    add_field(m_full, "marketLevel", 2, T_MSG, type_name="MarketLevel")
    add_field(m_full, "optionGreeks", 3, T_MSG, type_name="OptionGreeks")
    add_field(m_full, "marketOHLC", 4, T_MSG, type_name="MarketOHLC")
    add_field(m_full, "atp", 5, T_DOUBLE)
    add_field(m_full, "vtt", 6, T_INT64)
    add_field(m_full, "oi", 7, T_DOUBLE)
    add_field(m_full, "iv", 8, T_DOUBLE)
    add_field(m_full, "tbq", 9, T_DOUBLE)
    add_field(m_full, "tsq", 10, T_DOUBLE)
    for name, number, field_type in [("iep", 11, T_DOUBLE), ("rp", 12, T_DOUBLE),
                                     ("ieq", 13, T_INT64), ("iiqTotal", 14, T_INT64),
                                     ("iiqM", 15, T_INT64), ("casEligible", 16, descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)]:
        add_field(m_full, name, number, field_type)

    # 7. IndexFullFeed
    i_full = fdp.message_type.add(name="IndexFullFeed")
    add_field(i_full, "ltpc", 1, T_MSG, type_name="LTPC")
    add_field(i_full, "marketOHLC", 2, T_MSG, type_name="MarketOHLC")

    # 8. FullFeed (oneof FullFeedUnion)
    full_feed = fdp.message_type.add(name="FullFeed")
    full_oneof = full_feed.oneof_decl.add(name="FullFeedUnion")
    f1 = full_feed.field.add(name="marketFF", number=1, type=T_MSG, type_name="MarketFullFeed")
    f1.oneof_index = 0
    f2 = full_feed.field.add(name="indexFF", number=2, type=T_MSG, type_name="IndexFullFeed")
    f2.oneof_index = 0

    # 9. FirstLevelWithGreeks (official `option_greeks` mode)
    fl_greeks = fdp.message_type.add(name="FirstLevelWithGreeks")
    add_field(fl_greeks, "ltpc", 1, T_MSG, type_name="LTPC")
    add_field(fl_greeks, "firstDepth", 2, T_MSG, type_name="Quote")
    add_field(fl_greeks, "optionGreeks", 3, T_MSG, type_name="OptionGreeks")
    add_field(fl_greeks, "vtt", 4, T_INT64)
    add_field(fl_greeks, "oi", 5, T_DOUBLE)
    add_field(fl_greeks, "iv", 6, T_DOUBLE)

    # 10. RequestMode Enum
    req_mode = fdp.enum_type.add(name="RequestMode")
    for idx, name in enumerate(["ltpc", "full_d5", "option_greeks", "full_d30"]):
        val = req_mode.value.add()
        val.name = name
        val.number = idx

    # 11. Feed (oneof FeedUnion + requestMode)
    feed = fdp.message_type.add(name="Feed")
    feed_oneof = feed.oneof_decl.add(name="FeedUnion")
    u1 = feed.field.add(name="ltpc", number=1, type=T_MSG, type_name="LTPC")
    u1.oneof_index = 0
    u2 = feed.field.add(name="fullFeed", number=2, type=T_MSG, type_name="FullFeed")
    u2.oneof_index = 0
    u3 = feed.field.add(name="firstLevelWithGreeks", number=3, type=T_MSG, type_name="FirstLevelWithGreeks")
    u3.oneof_index = 0
    add_field(feed, "requestMode", 4, T_ENUM, type_name="RequestMode")

    # 12. MarketStatus Enum & MarketInfo
    m_status = fdp.enum_type.add(name="MarketStatus")
    for idx, name in enumerate([
        "PRE_OPEN_START", "PRE_OPEN_END", "NORMAL_OPEN", "NORMAL_CLOSE", "CLOSING_START", "CLOSING_END"
    ]):
        val = m_status.value.add()
        val.name = name
        val.number = idx

    m_info = fdp.message_type.add(name="MarketInfo")
    seg_entry = m_info.nested_type.add(name="SegmentStatusEntry")
    seg_entry.options.map_entry = True
    add_field(seg_entry, "key", 1, T_STRING)
    add_field(seg_entry, "value", 2, T_ENUM, type_name="MarketStatus")
    add_field(m_info, "segmentStatus", 1, T_MSG, L_REP, "MarketInfo.SegmentStatusEntry")
    status_info = fdp.message_type.add(name="StatusInfo")
    add_field(status_info, "status", 1, T_STRING)
    add_field(status_info, "updatedTime", 2, T_INT64)
    for field_name, number in (("casMarketStatus", 2), ("preOpenSessionStatus", 3)):
        type_name = field_name[0].upper() + field_name[1:] + "Entry"
        status_entry = m_info.nested_type.add(name=type_name)
        status_entry.options.map_entry = True
        add_field(status_entry, "key", 1, T_STRING)
        add_field(status_entry, "value", 2, T_MSG, type_name="StatusInfo")
        add_field(m_info, field_name, number, T_MSG, L_REP, "MarketInfo." + type_name)

    # 13. Type Enum & FeedResponse Root Message
    resp_type = fdp.enum_type.add(name="Type")
    for idx, name in enumerate(["initial_feed", "live_feed", "market_info"]):
        val = resp_type.value.add()
        val.name = name
        val.number = idx

    feed_resp = fdp.message_type.add(name="FeedResponse")
    add_field(feed_resp, "type", 1, T_ENUM, type_name="Type")
    feeds_entry = feed_resp.nested_type.add(name="FeedsEntry")
    feeds_entry.options.map_entry = True
    add_field(feeds_entry, "key", 1, T_STRING)
    add_field(feeds_entry, "value", 2, T_MSG, type_name="Feed")
    add_field(feed_resp, "feeds", 2, T_MSG, L_REP, "FeedResponse.FeedsEntry")
    add_field(feed_resp, "currentTs", 3, T_INT64)
    add_field(feed_resp, "marketInfo", 4, T_MSG, type_name="MarketInfo")

    file_desc = pool.Add(fdp)
    return message_factory.GetMessageClass(file_desc.message_types_by_name["FeedResponse"])


# Initialize the Protobuf message class once at import time
FeedResponseProto = _build_v3_feed_response_class()


class UpstoxMarketDataWSV3:
    """
    Reusable Upstox Market Data Feed V3 WebSocket Client.
    Supports modes: 'ltpc', 'option_greeks', 'full', and 'full_d30'.
    """

    VALID_MODES = {"ltpc", "option_greeks", "full", "full_d30"}

    def __init__(
        self,
        client: UpstoxAnalyticsClient,
        on_ticks: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_market_info: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_connect: Optional[Callable[["UpstoxMarketDataWSV3"], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_close: Optional[Callable[[Optional[int], Optional[str]], None]] = None,
        auto_reconnect: bool = True,
        max_reconnect_delay: int = 30,
    ):
        """
        :param client: Initialized `UpstoxAnalyticsClient` instance.
        :param on_ticks: Callback receiving decoded `initial_feed` and `live_feed` dicts.
        :param on_market_info: Optional callback receiving `market_info` segment status updates.
        :param on_connect: Callback invoked immediately after WebSocket connects.
        :param on_error: Callback invoked on exceptions.
        :param on_close: Callback invoked when connection closes.
        :param auto_reconnect: Automatically obtain a fresh one-time WSS URL and re-subscribe on drop.
        """
        self.client = client
        self.on_ticks = on_ticks
        self.on_market_info = on_market_info
        self.on_connect = on_connect
        self.on_error = on_error
        self.on_close = on_close
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_delay = max_reconnect_delay

        # Track active subscriptions by mode so auto-reconnect restores state automatically
        self._subscriptions: Dict[str, Set[str]] = {mode: set() for mode in self.VALID_MODES}
        self._subscription_lock = threading.RLock()
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # =========================================================================
    # PROTOBUF DECODER
    # =========================================================================

    @staticmethod
    def decode_protobuf(binary_data: bytes) -> Dict[str, Any]:
        """Decode raw binary Protobuf frame from Upstox V3 into a Python dict."""
        msg = FeedResponseProto()
        msg.ParseFromString(binary_data)
        # Proto3 scalar zeros (including Gamma and OI) are actual values, not gaps.
        return MessageToDict(msg, preserving_proto_field_name=False, always_print_fields_with_no_presence=True)

    # =========================================================================
    # SUBSCRIPTION & MODE CONTROL (Thread-Safe & Async-Safe)
    # =========================================================================

    def _validate_mode(self, mode: str) -> None:
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Choose from {self.VALID_MODES}.")

    async def _send_control_frame(self, method: str, mode: str, instrument_keys: List[str]) -> None:
        """
        Upstox V3 requires control messages ('sub', 'unsub', 'change_mode')
        to be UTF-8 encoded and transmitted as BINARY WebSocket frames.
        """
        if not instrument_keys or not self._ws:
            return

        payload = {
            "guid": uuid.uuid4().hex[:20],
            "method": method,
            "data": {
                "mode": mode,
                "instrumentKeys": list(instrument_keys),
            },
        }
        binary_frame = json.dumps(payload).encode("utf-8")
        await self._ws.send(binary_frame)

    def subscribe(self, instrument_keys: List[str], mode: str = "ltpc") -> None:
        """Subscribe in an official V3 mode; the legacy option_chain alias is accepted."""
        mode = "option_greeks" if mode == "option_chain" else mode  # old local alias
        self._validate_mode(mode)
        # Remove from any previous mode set and add to the target mode
        with self._subscription_lock:
            for m in self.VALID_MODES:
                self._subscriptions[m].difference_update(instrument_keys)
            self._subscriptions[mode].update(instrument_keys)

        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(
                self._send_control_frame("sub", mode, instrument_keys), self._loop
            )

    def unsubscribe(self, instrument_keys: List[str], mode: str = "ltpc") -> None:
        """Unsubscribe instrument_keys."""
        mode = "option_greeks" if mode == "option_chain" else mode
        self._validate_mode(mode)
        with self._subscription_lock:
            for m in self.VALID_MODES:
                self._subscriptions[m].difference_update(instrument_keys)

        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(
                self._send_control_frame("unsub", mode, instrument_keys), self._loop
            )

    def change_mode(self, instrument_keys: List[str], new_mode: str) -> None:
        """Switch the feed mode for already subscribed instruments."""
        new_mode = "option_greeks" if new_mode == "option_chain" else new_mode
        self._validate_mode(new_mode)
        with self._subscription_lock:
            for m in self.VALID_MODES:
                self._subscriptions[m].difference_update(instrument_keys)
            self._subscriptions[new_mode].update(instrument_keys)

        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(
                self._send_control_frame("change_mode", new_mode, instrument_keys), self._loop
            )

    # =========================================================================
    # CORE ASYNC STREAM LOOP
    # =========================================================================

    async def _restore_subscriptions(self) -> None:
        """Re-send all active subscriptions upon connection or reconnection."""
        with self._subscription_lock:
            subscriptions = [(mode, list(keys)) for mode, keys in self._subscriptions.items()]
        for mode, keys in subscriptions:
            if keys:
                await self._send_control_frame("sub", mode, list(keys))

    async def run_async(self) -> None:
        """Main async loop with exponential backoff reconnection and fresh WSS URL authorization."""
        self._loop = asyncio.get_running_loop()
        ssl_context = ssl.create_default_context()
        attempt = 0

        while not self._stop_event.is_set():
            try:
                # Every connection attempt requires a fresh one-time authorized WSS URL
                wss_url = self.client.get_market_data_feed_ws_url_v3()
                if self._stop_event.is_set():
                    break
                async with websockets.connect(
                    wss_url,
                    ssl=ssl_context,
                    ping_interval=20,
                    ping_timeout=10,
                    max_size=None,
                ) as ws:
                    self._ws = ws
                    attempt = 0
                    logger.info("Connected to Upstox Market Data Feed V3.")

                    if self.on_connect:
                        self.on_connect(self)

                    await self._restore_subscriptions()

                    async for raw_msg in ws:
                        if self._stop_event.is_set():
                            break
                        if isinstance(raw_msg, bytes):
                            decoded = self.decode_protobuf(raw_msg)
                            msg_type = decoded.get("type")

                            if msg_type == "market_info" and self.on_market_info:
                                self.on_market_info(decoded)
                            elif self.on_ticks:
                                self.on_ticks(decoded)

            except websockets.ConnectionClosed as closed_err:
                self._ws = None
                if self.on_close:
                    self.on_close(closed_err.code, closed_err.reason)
                if not self.auto_reconnect or self._stop_event.is_set():
                    break
            except Exception as exc:
                self._ws = None
                if self.on_error:
                    self.on_error(exc)
                if not self.auto_reconnect or self._stop_event.is_set():
                    break

            finally:
                self._ws = None
                if self.on_close:
                    self.on_close(None, None)

            attempt += 1
            delay = min(2 ** attempt, self.max_reconnect_delay)
            logger.warning(f"Reconnecting to Upstox V3 WebSocket in {delay}s...")
            for _ in range(delay * 4):
                if self._stop_event.is_set():
                    return
                await asyncio.sleep(.25)

    # =========================================================================
    # BACKGROUND THREAD RUNNERS (For Synchronous Scripts)
    # =========================================================================

    def start_background(self) -> None:
        """Start the WebSocket stream in a non-blocking background daemon thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=lambda: asyncio.run(self.run_async()),
            name="UpstoxWSV3Thread",
            daemon=True,
        )
        self._thread.start()

    @property
    def is_running(self):
        return bool(self._thread and self._thread.is_alive())

    def stop(self) -> None:
        """Gracefully close the WebSocket stream."""
        self._stop_event.set()
        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop)
