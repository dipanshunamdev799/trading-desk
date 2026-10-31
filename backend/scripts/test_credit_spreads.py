"""Strategy gates and real PostgreSQL transactions in a disposable isolated schema."""
import copy
import json
import os
import sys
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from sqlalchemy import create_engine, text
from app.config import get_settings
from app.services.credit_spreads import (AccountSettings, CloseRequest, CreditSpreads, Ticket,
                                         evaluate, executable, exit_reason)
from app.services.market_store import IST

AT = datetime(2026, 10, 28, 11, 0, tzinfo=IST)
EXPIRY = "2026-11-10"
ACCOUNT = {"capital": 1000000, "fee_per_leg": 25, "slippage": .05, "auto_exit": True}
HOURLY = {"trend": "bearish", "closed_at": AT.replace(hour=10, minute=15).isoformat()}


def ticket(**changes):
    return Ticket(**{"request_id": uuid.uuid4().hex, "strategy": "BEAR_CALL", "expiry": EXPIRY,
        "short_strike": 25400, "long_strike": 25500, "lots": 1, "level": 25200,
        "trend_confirmed": True, "candle_confirmed": True, "event_clear": True,
        "entry_reason": "Hourly resistance rejection and closed 15-minute breakdown", **changes})


def market():
    return {"expiry": EXPIRY, "spot": 25000, "session": {"active": True}, "options_session": {"active": True},
        "quote_at": AT.isoformat(), "error": None, "options": [
        {"key": "NSE_FO|TEST_SHORT", "type": "CE", "strike": 25400, "lot_size": 65,
         "bid": 60, "ask": 61, "bid_qty": 10000, "ask_qty": 10000, "delta": .2, "iv": 15, "greeks_at": AT.isoformat()},
        {"key": "NSE_FO|TEST_LONG", "type": "CE", "strike": 25500, "lot_size": 65,
         "bid": 35, "ask": 36, "bid_qty": 10000, "ask_qty": 10000, "delta": .1, "iv": 16, "greeks_at": AT.isoformat()}]}


class RuleTests(unittest.TestCase):
    def preview(self, t=None, m=None, account=None, opened=None, hourly=None, at=AT):
        return evaluate(t or ticket(), m or market(), account or ACCOUNT, opened or [], hourly or HOURLY, at)

    def test_valid_bear_call_exact_math(self):
        p = self.preview()
        self.assertTrue(p["eligible"], p["checks"])
        self.assertEqual(p["credit"], 23.9)
        self.assertAlmostEqual(p["max_profit"], 1553.5)
        self.assertAlmostEqual(p["max_loss"], 4946.5)
        self.assertAlmostEqual(p["risk_reserved"], 5046.5)
        self.assertAlmostEqual(p["target_debit"], 11.95)
        self.assertAlmostEqual(p["stop_debit"], 47.8)

    def test_bull_put_uses_signed_delta_and_correct_hedge_direction(self):
        m = market()
        for leg in m["options"]:
            leg["type"] = "PE"
            leg["strike"] = 24600 if leg["strike"] == 25400 else 24500
            leg["delta"] *= -1
        result = self.preview(ticket(strategy="BULL_PUT", short_strike=24600, long_strike=24500, level=24800), m,
                              hourly={**HOURLY, "trend": "bullish"})
        self.assertTrue(result["eligible"], result["checks"])

    def test_no_zero_ltp_or_one_leg_fill_fallback(self):
        for field, value in (("bid", None), ("ask", 0), ("bid_qty", 1), ("ask", 50)):
            m = market()
            m["options"][0][field] = value
            self.assertFalse(self.preview(m=m)["eligible"])
        self.assertIsNone(executable(None, market()["options"][1], 65))

    def test_stale_closed_unknown_or_future_quotes_block(self):
        for age in (-1, 66, 86400):
            m = market(); m["quote_at"] = (AT - timedelta(seconds=age)).isoformat()
            self.assertFalse(self.preview(m=m)["eligible"])
        for field in ("session", "options_session"):
            m = market(); m[field] = {"active": False}
            self.assertFalse(self.preview(m=m)["eligible"])

    def test_stale_greek_and_hourly_confirmation_block(self):
        m = market(); m["options"][0]["greeks_at"] = (AT - timedelta(minutes=2)).isoformat()
        self.assertFalse(self.preview(m=m)["eligible"])
        self.assertFalse(self.preview(hourly={**HOURLY, "closed_at": (AT-timedelta(days=1)).isoformat()})["eligible"])
        self.assertFalse(self.preview(hourly={**HOURLY, "trend": "bullish"})["eligible"])

    def test_one_lot_above_risk_budget_is_rejected(self):
        p = self.preview(account={**ACCOUNT, "capital": 100000})
        self.assertFalse(next(c["passed"] for c in p["checks"] if c["code"] == "position_risk"))

    def test_portfolio_risk_and_no_averaging(self):
        opened = [{"status": "OPEN", "strategy": "BULL_PUT", "risk_reserved": 16000}]
        p = self.preview(opened=opened)
        self.assertFalse(next(c["passed"] for c in p["checks"] if c["code"] == "portfolio"))
        opened[0]["strategy"] = "BEAR_CALL"
        self.assertFalse(next(c["passed"] for c in self.preview(opened=opened)["checks"] if c["code"] == "averaging"))

    def test_windows_and_rules_cannot_be_overridden(self):
        for changes in ({"lots": 10}, {"long_strike": 25300}, {"long_strike": 25800},
                        {"trend_confirmed": False}, {"candle_confirmed": False}, {"event_clear": False},
                        {"expiry": "2026-11-03"}, {"level": 25600}):
            self.assertFalse(self.preview(ticket(**changes))["eligible"], changes)
        for at in (AT.replace(hour=9), AT.replace(hour=14, minute=31), AT+timedelta(days=2)):
            self.assertFalse(self.preview(at=at)["eligible"])

    def test_credit_filter_and_missing_lot(self):
        m = market(); m["options"][1]["ask"] = 50
        self.assertFalse(self.preview(m=m)["eligible"])
        m = market(); m["options"][1]["lot_size"] = None
        self.assertFalse(self.preview(m=m)["eligible"])

    def test_exit_priorities_and_gap_price(self):
        trade = {"expiry": EXPIRY, "stop_debit": 48, "target_debit": 12}
        self.assertEqual(exit_reason(trade, 70, AT), "STOP_LOSS")
        self.assertEqual(exit_reason(trade, 8, AT), "PROFIT_TARGET")
        self.assertIsNone(exit_reason(trade, 20, AT))
        self.assertEqual(exit_reason({**trade, "expiry": "2026-10-30"}, 20, AT), "TIME_EXIT")
        m = market(); m["options"][0]["ask"] = 100
        self.assertEqual(executable(*m["options"], 65, True, .05)["net"], 65.1)

    def test_calendar_closes_before_weekend_two_dte_deadline(self):
        service = CreditSpreads(SimpleNamespace(), SimpleNamespace(get_market_timings=lambda day: []))
        friday = datetime(2026, 10, 30, 11, tzinfo=IST)
        self.assertTrue(service.last_session_before_exit("2026-11-03", friday))
        monday_open = [{"exchange": "NFO", "start_time": "2026-11-02T09:15:00+05:30", "end_time": "2026-11-02T15:30:00+05:30"}]
        service = CreditSpreads(SimpleNamespace(), SimpleNamespace(get_market_timings=lambda day: monday_open if day == "2026-11-02" else []))
        self.assertFalse(service.last_session_before_exit("2026-11-04", friday))

    def test_unknown_near_expiry_calendar_uses_conservative_early_exit(self):
        service = CreditSpreads(SimpleNamespace(), SimpleNamespace())
        self.assertTrue(service.last_session_before_exit("2026-11-02", AT))
        self.assertFalse(service.last_session_before_exit(EXPIRY, AT))


class AdapterTests(unittest.TestCase):
    def service(self, snapshot=None):
        rows = [{"expiry": EXPIRY, "underlying_key": "NSE_INDEX|Nifty 50", "underlying_spot_price": 25000,
                 "strike_price": 25400, "call_options": {"instrument_key": "NSE_FO|S", "market_data": {
                     "bid_price": 60, "ask_price": 61, "bid_qty": 130, "ask_qty": 195}, "option_greeks": {"delta": .2, "iv": 15}}}]
        contracts = [{"expiry": EXPIRY, "instrument_key": "NSE_FO|S", "strike_price": 25400, "instrument_type": "CE", "lot_size": 65}]
        gateway = SimpleNamespace(get_option_contracts=lambda key: contracts,
            get_option_chain=lambda key, expiry: rows, get_market_session=lambda key: {"active": True},
            get_current_option_chain_snapshot=lambda key, expiry: snapshot or {"observed_at": AT.isoformat()})
        return CreditSpreads(SimpleNamespace(), gateway), rows, contracts

    @patch("app.services.credit_spreads.now", return_value=AT)
    def test_contract_master_and_rest_seed_determine_price_identity_and_time(self, _):
        seed = (AT-timedelta(seconds=50)).isoformat()
        service, _, _ = self.service({"transport": "websocket", "observed_at": AT.isoformat(), "rest_seed_at": seed})
        result = service.market(EXPIRY)
        self.assertEqual(result["quote_at"], seed)
        self.assertEqual(result["options"][0]["lot_size"], 65)
        self.assertEqual(result["options"][0]["bid_qty"], 130)

    @patch("app.services.credit_spreads.now", return_value=AT)
    def test_unrelated_stream_updates_cannot_certify_bid_ask_without_seed(self, _):
        service, _, _ = self.service({"transport": "websocket", "observed_at": AT.isoformat()})
        self.assertIsNone(service.market(EXPIRY)["quote_at"])

    @patch("app.services.credit_spreads.now", return_value=AT)
    def test_mismatched_underlying_expiry_or_strike_is_not_substituted(self, _):
        for changes in ({"underlying_key": "NSE_INDEX|Other"}, {"expiry": "2026-11-03"}, {"strike_price": 25000}):
            service, rows, _ = self.service()
            rows[0].update(changes)
            self.assertEqual(service.market(EXPIRY)["options"], [])

    @patch("app.services.credit_spreads.now", return_value=AT)
    def test_chart_ema_ignores_current_unfinished_hour(self, _):
        rows = []
        for i in range(30):
            at = AT - timedelta(days=5) + timedelta(hours=i)
            rows.append([at.isoformat(), 100, 101, 99, 100, 10])
        rows.append([AT.replace(hour=10, minute=15).isoformat(), 100, 1000, 99, 1000, 10])
        gateway = SimpleNamespace(get_historical_candles_v3=lambda *args: {"candles": rows})
        result = CreditSpreads(SimpleNamespace(), gateway).chart()
        self.assertEqual(result["ema_value"], 100)


@unittest.skipUnless(os.environ.get("RUN_MARKET_DB_TESTS") == "1", "Opt in to isolated PostgreSQL tests")
class DatabaseLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = "test_credit_spreads_" + uuid.uuid4().hex
        url = get_settings().database_url_sync
        cls.admin = create_engine(url)
        with cls.admin.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{cls.schema}"'))
        cls.engine = create_engine(url, connect_args={"options": f"-csearch_path={cls.schema}"})
        with cls.engine.begin() as conn:
            conn.exec_driver_sql((ROOT / "backend/sql/006_credit_spreads.sql").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        with cls.admin.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{cls.schema}" CASCADE'))
        cls.admin.dispose()

    def setUp(self):
        with self.engine.begin() as conn:
            conn.execute(text("TRUNCATE credit_spread_marks,credit_spread_orders,credit_spread_trades"))
            conn.execute(text("UPDATE credit_spread_account SET settings=CAST(:s AS jsonb),monitor_at=NULL,monitor_error=NULL"), {"s": json.dumps(ACCOUNT)})
        self.service = CreditSpreads(SimpleNamespace(engine=self.engine), SimpleNamespace())
        self.m = market()
        self.service.market = lambda expiry=None: copy.deepcopy(self.m)
        self.service.chart = lambda interval="1hour": HOURLY
        self.clock = patch("app.services.credit_spreads.now", return_value=AT)
        self.clock.start(); self.addCleanup(self.clock.stop)

    def test_entry_is_atomic_and_idempotent_across_restart(self):
        t = ticket()
        first = self.service.enter(t)
        self.assertEqual(first["status"], "FILLED")
        self.assertEqual([l["side"] for l in first["legs"]], ["SELL", "BUY"])
        self.assertEqual(self.service.enter(t)["id"], first["id"])
        restarted = CreditSpreads(SimpleNamespace(engine=self.engine), SimpleNamespace())
        self.assertEqual(restarted.dashboard()["summary"]["open_count"], 1)
        self.assertEqual(len(restarted.dashboard()["orders"]), 1)
        with self.assertRaises(ValueError):
            self.service.settings(AccountSettings(**{**ACCOUNT, "capital": 2000000}))

    def test_profit_exit_records_four_legs_fees_and_journal(self):
        self.service.enter(ticket())
        self.service.monitor()
        self.m["options"][0].update(bid=39, ask=40)
        self.m["quote_at"] = (AT+timedelta(seconds=10)).isoformat()
        with patch("app.services.credit_spreads.now", return_value=AT+timedelta(seconds=10)):
            self.service.monitor(); self.service.monitor()
        desk = self.service.dashboard()
        trade = desk["trades"][0]
        self.assertEqual(trade["status"], "CLOSED")
        self.assertEqual(trade["exit_reason"], "PROFIT_TARGET")
        self.assertAlmostEqual(trade["net_pnl"], (23.9-5.1)*65-100)
        self.assertEqual(len(desk["orders"]), 2)
        self.assertEqual(sum(len(o["legs"]) for o in desk["orders"]), 4)
        self.assertEqual(desk["summary"]["fees"], 100)
        self.assertEqual(desk["summary"]["closed_count"], 1)
        self.assertEqual(len(self.service.marks(trade["id"])), 2)
        self.assertIn("PROFIT_TARGET", self.service.export("trades"))

    def test_stop_fills_beyond_trigger_after_gap(self):
        self.service.enter(ticket())
        self.m["options"][0].update(bid=99, ask=100)
        self.service.monitor()
        t = self.service.dashboard()["trades"][0]
        self.assertEqual(t["exit_reason"], "STOP_LOSS")
        self.assertEqual(t["exit_debit"], 65.1)
        self.assertLess(t["net_pnl"], -23.9*65)

    def test_queued_technical_exit_survives_unavailable_quotes(self):
        order = self.service.enter(ticket())
        self.m["options_session"]["active"] = False
        result = self.service.close(order["trade_id"], CloseRequest(reason="TECHNICAL_INVALIDATION", notes="Failed hourly retest"))
        self.assertEqual(result["status"], "OPEN")
        self.assertIsNotNone(result["exit_requested"])
        self.m["options_session"]["active"] = True
        self.service.monitor()
        self.service.close(order["trade_id"], CloseRequest())
        desk = self.service.dashboard()
        self.assertEqual(desk["trades"][0]["exit_reason"], "TECHNICAL_INVALIDATION")
        self.assertEqual(len(desk["orders"]), 3)

    def test_rejected_order_never_creates_a_position(self):
        order = self.service.enter(ticket(lots=100))
        self.assertEqual(order["status"], "REJECTED")
        self.assertEqual(order["legs"], [])
        self.assertEqual(self.service.dashboard()["summary"]["open_count"], 0)

    def test_order_failure_rolls_back_position_in_same_transaction(self):
        with patch.object(self.service, "_order", side_effect=RuntimeError("Simulated storage failure")):
            with self.assertRaises(RuntimeError):
                self.service.enter(ticket())
        desk = self.service.dashboard()
        self.assertEqual(desk["trades"], [])
        self.assertEqual(desk["orders"], [])

    def test_time_exit_is_recorded_at_actual_executable_debit(self):
        self.service.enter(ticket())
        due = AT + timedelta(days=11)
        self.m["quote_at"] = due.isoformat()
        with patch("app.services.credit_spreads.now", return_value=due):
            self.service.monitor()
        trade = self.service.dashboard()["trades"][0]
        self.assertEqual(trade["exit_reason"], "TIME_EXIT")
        self.assertEqual(trade["exit_debit"], 26.1)

    def test_concurrent_requests_cannot_average_or_double_fill(self):
        t = ticket()
        with ThreadPoolExecutor(2) as pool:
            orders = list(pool.map(self.service.enter, [t, t]))
        self.assertEqual(orders[0]["id"], orders[1]["id"])
        self.assertEqual(self.service.enter(ticket())["status"], "REJECTED")
        self.assertEqual(self.service.dashboard()["summary"]["open_count"], 1)

    def test_auto_exit_can_be_disabled_but_manual_exit_still_works(self):
        self.service.settings(AccountSettings(**{**ACCOUNT, "auto_exit": False}))
        order = self.service.enter(ticket())
        self.m["options"][0].update(bid=39, ask=40)
        self.service.monitor()
        self.assertEqual(self.service.dashboard()["trades"][0]["status"], "OPEN")
        self.assertEqual(self.service.close(order["trade_id"], CloseRequest())["status"], "CLOSED")

    def test_settings_and_csv_text_preserve_trade_history(self):
        order = self.service.enter(ticket(entry_reason="=untrusted spreadsheet text"))
        self.service.close(order["trade_id"], CloseRequest())
        self.service.settings(AccountSettings(**{**ACCOUNT, "capital": 1500000, "fee_per_leg": 100}))
        self.assertEqual(self.service.dashboard()["trades"][0]["entry_fees"], 50)
        self.assertIn("'=untrusted spreadsheet text", self.service.export("trades"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
