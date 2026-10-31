"""
upstox_analytics.py
Complete, production-ready client library for the Upstox Analytics Token.
Covers all 65 V2 & V3 Open Access and Static-IP Read-Only endpoints.
"""

import os
import gzip
import json
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class UpstoxAPIError(Exception):
    """Custom exception raised on non-2xx responses from Upstox API."""
    def __init__(self, status_code: int, message: str, response_data: Any = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"HTTP {status_code}: {message}")


class UpstoxAnalyticsClient:
    BASE_URL = "https://api.upstox.com"
    BOD_INSTRUMENTS_URL = "https://assets.upstox.com/market-quote/instruments/exchange/{exchange}.json.gz"

    def __init__(
        self,
        analytics_token: Optional[str] = None,
        timeout: int = 15,
        max_retries: int = 3,
        unwrap_data: bool = True,
        allow_missing_token: bool = False,
    ):
        """
        :param analytics_token: Upstox Analytics Token (or set UPSTOX_ANALYTICS_TOKEN env var).
        :param timeout: HTTP request timeout in seconds.
        :param max_retries: Automatic retries on HTTP 429 and 5xx errors.
        :param unwrap_data: If True, returns payload["data"] directly when present.
        """
        self.token = analytics_token or os.getenv("UPSTOX_ANALYTICS_TOKEN")
        if not self.token and not allow_missing_token:
            raise ValueError(
                "Upstox Analytics Token is required. Pass `analytics_token` or set `UPSTOX_ANALYTICS_TOKEN`."
            )

        self.timeout = timeout
        self.unwrap_data = unwrap_data

        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        })

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    @staticmethod
    def _encode_key(key: str) -> str:
        """URL-encode instrument keys (e.g., 'NSE_EQ|INE002A01018' -> 'NSE_EQ%7CINE002A01018')."""
        return urllib.parse.quote(key, safe="")

    @staticmethod
    def _format_keys(keys: Union[str, List[str]], max_limit: int = 500) -> str:
        """Convert a single key or list of keys into a comma-separated string."""
        if isinstance(keys, list):
            if len(keys) > max_limit:
                raise ValueError(f"Maximum of {max_limit} instrument_keys allowed per batch request.")
            return ",".join(keys)
        return keys

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, Any]]]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Centralized HTTP dispatcher supporting both dict and repeated-key list params."""
        if not self.token:
            raise RuntimeError("UPSTOX_ANALYTICS_TOKEN is required for an API cache miss; retained database data remains readable.")
        url = f"{self.BASE_URL}{endpoint}"

        if isinstance(params, dict):
            clean_params = {}
            for k, v in params.items():
                if v is not None:
                    clean_params[k] = str(v).lower() if isinstance(v, bool) else v
            params = clean_params

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json_body,
            headers=extra_headers,
            timeout=self.timeout,
        )

        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if not response.ok:
            err_msg = payload.get("errors", payload) if isinstance(payload, dict) else payload
            raise UpstoxAPIError(response.status_code, str(err_msg), payload)

        if self.unwrap_data and isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload

    # =========================================================================
    # 1. INSTRUMENTS & SEARCH (Open Access)
    # =========================================================================

    def search_instruments(
        self,
        query: str,
        exchanges: Optional[str] = None,
        segments: Optional[str] = None,
        instrument_types: Optional[str] = None,
        expiry: Optional[str] = None,
        atm_offset: Optional[int] = None,
        page_number: int = 1,
        records: int = 20,
    ) -> Any:
        """GET /v2/instruments/search — Dynamic instrument lookup with F&O filters."""
        params = {
            "query": query,
            "exchanges": exchanges,
            "segments": segments,
            "instrument_types": instrument_types,
            "expiry": expiry,
            "atm_offset": atm_offset,
            "page_number": page_number,
            "records": records,
        }
        return self._request("GET", "/v2/instruments/search", params=params)

    def download_bod_instruments(self, exchange: str = "complete") -> List[Dict[str, Any]]:
        """
        Download and decompress daily Beginning-of-Day (BOD) Instrument Master JSON.
        :param exchange: 'complete', 'NSE', 'BSE', 'MCX', 'suspended', 'MTF', or 'global'
        """
        url = self.BOD_INSTRUMENTS_URL.format(exchange=exchange)
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return json.loads(gzip.decompress(resp.content).decode("utf-8"))

    # =========================================================================
    # 2. HISTORICAL & INTRADAY CANDLES — V3 & V2 (Open Access)
    # =========================================================================

    def get_historical_candles_v3(
        self,
        instrument_key: str,
        unit: str,
        interval: Union[int, str],
        to_date: str,
        from_date: Optional[str] = None,
    ) -> Any:
        """
        GET /v3/historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}
        :param unit: 'minutes' (1-300), 'hours' (1-5), 'days' (1), 'weeks' (1), 'months' (1)
        """
        key_enc = self._encode_key(instrument_key)
        if from_date:
            endpoint = f"/v3/historical-candle/{key_enc}/{unit}/{interval}/{to_date}/{from_date}"
        else:
            endpoint = f"/v3/historical-candle/{key_enc}/{unit}/{interval}/{to_date}"
        return self._request("GET", endpoint)

    def get_intraday_candles_v3(
        self,
        instrument_key: str,
        unit: str = "minutes",
        interval: Union[int, str] = 1,
    ) -> Any:
        """GET /v3/historical-candle/intraday/{instrument_key}/{unit}/{interval}"""
        key_enc = self._encode_key(instrument_key)
        return self._request("GET", f"/v3/historical-candle/intraday/{key_enc}/{unit}/{interval}")

    def get_historical_candles_v2(
        self,
        instrument_key: str,
        interval: str,
        to_date: str,
        from_date: Optional[str] = None,
    ) -> Any:
        """
        GET /v2/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}
        :param interval: '1minute', '30minute', 'day', 'week', 'month'
        """
        key_enc = self._encode_key(instrument_key)
        if from_date:
            endpoint = f"/v2/historical-candle/{key_enc}/{interval}/{to_date}/{from_date}"
        else:
            endpoint = f"/v2/historical-candle/{key_enc}/{interval}/{to_date}"
        return self._request("GET", endpoint)

    def get_intraday_candles_v2(self, instrument_key: str, interval: str = "1minute") -> Any:
        """GET /v2/historical-candle/intraday/{instrument_key}/{interval}"""
        key_enc = self._encode_key(instrument_key)
        return self._request("GET", f"/v2/historical-candle/intraday/{key_enc}/{interval}")

    # =========================================================================
    # 3. EXPIRED INSTRUMENTS & BACKTESTING V2 (Open Access — Upstox Plus)
    # =========================================================================

    def get_expired_expiries(self, underlying_instrument_key: str) -> List[str]:
        """GET /v2/expired-instruments/expiries"""
        return self._request(
            "GET",
            "/v2/expired-instruments/expiries",
            params={"instrument_key": underlying_instrument_key},
        )

    def get_expired_option_contracts(
        self, underlying_instrument_key: str, expiry_date: str
    ) -> List[Dict[str, Any]]:
        """GET /v2/expired-instruments/option/contract"""
        return self._request(
            "GET",
            "/v2/expired-instruments/option/contract",
            params={"instrument_key": underlying_instrument_key, "expiry_date": expiry_date},
        )

    def get_expired_future_contracts(
        self, underlying_instrument_key: str, expiry_date: str
    ) -> List[Dict[str, Any]]:
        """GET /v2/expired-instruments/future/contract"""
        return self._request(
            "GET",
            "/v2/expired-instruments/future/contract",
            params={"instrument_key": underlying_instrument_key, "expiry_date": expiry_date},
        )

    def get_expired_historical_candles(
        self,
        expired_instrument_key: str,
        interval: str,
        to_date: str,
        from_date: str,
    ) -> Any:
        """
        GET /v2/expired-instruments/historical-candle/{expired_instrument_key}/{interval}/{to_date}/{from_date}
        :param interval: '1minute', '3minute', '5minute', '15minute', '30minute', 'day'
        """
        key_enc = self._encode_key(expired_instrument_key)
        endpoint = f"/v2/expired-instruments/historical-candle/{key_enc}/{interval}/{to_date}/{from_date}"
        return self._request("GET", endpoint)

    # =========================================================================
    # 4. MARKET QUOTES SNAPSHOTS — V3 & V2 (Open Access — Up to 500 keys)
    # =========================================================================

    def get_full_market_quotes_v3(self, instrument_keys: Union[str, List[str]]) -> Dict[str, Any]:
        """GET /v3/market-quote/quotes"""
        return self._request(
            "GET",
            "/v3/market-quote/quotes",
            params={"instrument_key": self._format_keys(instrument_keys)},
        )

    def get_ohlc_quotes_v3(
        self, instrument_keys: Union[str, List[str]], interval: str = "1d"
    ) -> Dict[str, Any]:
        """GET /v3/market-quote/ohlc — interval: '1d', 'I1' (1m), 'I30' (30m)."""
        return self._request(
            "GET",
            "/v3/market-quote/ohlc",
            params={"instrument_key": self._format_keys(instrument_keys), "interval": interval},
        )

    def get_ltp_quotes_v3(self, instrument_keys: Union[str, List[str]]) -> Dict[str, Any]:
        """GET /v3/market-quote/ltp — Includes last_price, ltq, volume, cp."""
        return self._request(
            "GET",
            "/v3/market-quote/ltp",
            params={"instrument_key": self._format_keys(instrument_keys)},
        )

    def get_option_greeks_v3(self, instrument_keys: Union[str, List[str]]) -> Dict[str, Any]:
        """GET /v3/market-quote/option-greek"""
        return self._request(
            "GET",
            "/v3/market-quote/option-greek",
            params={"instrument_key": self._format_keys(instrument_keys)},
        )

    def get_full_market_quotes_v2(self, instrument_keys: Union[str, List[str]]) -> Dict[str, Any]:
        """GET /v2/market-quote/quotes (Legacy V2)"""
        return self._request(
            "GET",
            "/v2/market-quote/quotes",
            params={"instrument_key": self._format_keys(instrument_keys)},
        )

    def get_ohlc_quotes_v2(
        self, instrument_keys: Union[str, List[str]], interval: str = "1d"
    ) -> Dict[str, Any]:
        """GET /v2/market-quote/ohlc (Legacy V2)"""
        return self._request(
            "GET",
            "/v2/market-quote/ohlc",
            params={"instrument_key": self._format_keys(instrument_keys), "interval": interval},
        )

    def get_ltp_quotes_v2(self, instrument_keys: Union[str, List[str]]) -> Dict[str, Any]:
        """GET /v2/market-quote/ltp (Legacy V2)"""
        return self._request(
            "GET",
            "/v2/market-quote/ltp",
            params={"instrument_key": self._format_keys(instrument_keys)},
        )

    # =========================================================================
    # 5. OPTION CHAIN & ACTIVE DERIVATIVE CONTRACTS V2 (Open Access)
    # =========================================================================

    def get_option_contracts(
        self, instrument_key: str, expiry_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """GET /v2/option/contract"""
        return self._request(
            "GET",
            "/v2/option/contract",
            params={"instrument_key": instrument_key, "expiry_date": expiry_date},
        )

    def get_option_chain(self, instrument_key: str, expiry_date: str) -> List[Dict[str, Any]]:
        """GET /v2/option/chain"""
        return self._request(
            "GET",
            "/v2/option/chain",
            params={"instrument_key": instrument_key, "expiry_date": expiry_date},
        )

    # =========================================================================
    # 6. MARKET INFORMATION, SMARTLISTS, FII/DII & OI ANALYTICS V2 (Open Access)
    # =========================================================================

    def get_options_smartlist(
        self,
        asset_type: str = "INDEX",
        category: str = "MOST_ACTIVE",
        page_number: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        GET /v2/market/smartlist/options
        :param asset_type: 'INDEX', 'STOCK', or 'COMMODITY'
        :param category: 'TOP_TRADED', 'MOST_ACTIVE', 'OI_GAINERS', 'OI_LOSERS',
                         'PRICE_GAINERS', 'PRICE_LOSERS', 'IV_GAINERS', 'IV_LOSERS',
                         'UNDER_5000', 'UNDER_10000'
        """
        params = {
            "asset_type": asset_type,
            "category": category,
            "page_number": page_number,
            "page_size": page_size,
        }
        return self._request("GET", "/v2/market/smartlist/options", params=params)

    def get_futures_smartlist(
        self,
        asset_type: str = "INDEX",
        category: str = "MOST_ACTIVE",
        page_number: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        GET /v2/market/smartlist/futures
        :param asset_type: 'INDEX', 'STOCK', or 'COMMODITY'
        :param category: 'TOP_TRADED', 'MOST_ACTIVE', 'OI_GAINERS', 'OI_LOSERS',
                         'PRICE_GAINERS', 'PRICE_LOSERS', 'PREMIUM', 'DISCOUNT'
        """
        params = {
            "asset_type": asset_type,
            "category": category,
            "page_number": page_number,
            "page_size": page_size,
        }
        return self._request("GET", "/v2/market/smartlist/futures", params=params)

    def get_mtf_smartlist(self, page_number: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """GET /v2/market/smartlist/mtf — Ranked MTF stocks with effective mtf_price & margin_saved."""
        return self._request(
            "GET",
            "/v2/market/smartlist/mtf",
            params={"page_number": page_number, "page_size": page_size},
        )

    def get_fii_data(
        self,
        data_types: Union[str, List[str]] = "NSE_EQ|CASH",
        interval: str = "1D",
        from_date: Optional[str] = None,
    ) -> Any:
        """
        GET /v2/market/fii — Foreign Institutional Investor activity.
        :param data_types: One or list of: 'NSE_FO|INDEX_FUTURES', 'NSE_FO|STOCK_FUTURES',
                           'NSE_FO|INDEX_OPTIONS', 'NSE_FO|STOCK_OPTIONS', 'NSE_EQ|CASH'
        :param interval: '1D' (daily) or '1M' (monthly)
        :param from_date: Optional 'YYYY-MM-DD'
        """
        if isinstance(data_types, str):
            data_types = [data_types]
        query_tuples: List[Tuple[str, Any]] = [("data_type", dt) for dt in data_types]
        query_tuples.append(("interval", interval))
        if from_date:
            query_tuples.append(("from", from_date))
        return self._request("GET", "/v2/market/fii", params=query_tuples)

    def get_dii_data(
        self, interval: str = "1D", from_date: Optional[str] = None
    ) -> Any:
        """
        GET /v2/market/dii — Domestic Institutional Investor activity (NSE Cash).
        :param interval: '1D' (daily) or '1M' (monthly)
        """
        params = {"data_type": "NSE_EQ|CASH", "interval": interval, "from": from_date}
        return self._request("GET", "/v2/market/dii", params=params)

    def get_oi_data(
        self,
        instrument_key: str,
        expiry: str,
        date: str,
        bucket_interval: Optional[int] = None,
    ) -> Any:
        """
        GET /v2/market/oi — Open Interest strike breakdown for an underlying.
        :param expiry: 'YYYY-MM-DD' or keyword ('current_week', 'next_week', 'current_month', etc.)
        :param date: 'YYYY-MM-DD'
        """
        params = {
            "instrument_key": instrument_key,
            "expiry": expiry,
            "date": date,
            "bucket_interval": bucket_interval,
        }
        return self._request("GET", "/v2/market/oi", params=params)

    def get_change_in_oi(
        self,
        instrument_key: str,
        expiry: str,
        date: str,
        bucket_interval: Optional[int] = None,
    ) -> Any:
        """
        GET /v2/market/change-in-oi — Change in Open Interest across strikes.
        :param expiry: 'YYYY-MM-DD' or keyword ('current_week', 'next_week', 'current_month', etc.)
        """
        params = {
            "instrument_key": instrument_key,
            "expiry": expiry,
            "date": date,
            "bucket_interval": bucket_interval,
        }
        return self._request("GET", "/v2/market/change-in-oi", params=params)

    def get_max_pain(
        self,
        instrument_key: str,
        expiry: str = "current_week",
        date: Optional[str] = None,
        bucket_interval: int = 60,
    ) -> Dict[str, Any]:
        """
        GET /v2/market/max-pain — Max Pain strike level & intraday interval insights.
        """
        params = {
            "instrument_key": instrument_key,
            "expiry": expiry,
            "date": date,
            "bucket_interval": bucket_interval,
        }
        return self._request("GET", "/v2/market/max-pain", params=params)

    def get_pcr(
        self,
        instrument_key: str,
        expiry: str = "current_week",
        date: Optional[str] = None,
        bucket_interval: int = 60,
    ) -> Dict[str, Any]:
        """
        GET /v2/market/pcr — Put-Call Ratio (PCR) & intraday interval insights.
        """
        params = {
            "instrument_key": instrument_key,
            "expiry": expiry,
            "date": date,
            "bucket_interval": bucket_interval,
        }
        return self._request("GET", "/v2/market/pcr", params=params)

    def get_market_holidays(self, date: Optional[str] = None) -> Any:
        """GET /v2/market/holidays/{date}"""
        endpoint = f"/v2/market/holidays/{date}" if date else "/v2/market/holidays"
        return self._request("GET", endpoint)

    def get_market_timings(self, date: str) -> Any:
        """GET /v2/market/timings/{date}"""
        return self._request("GET", f"/v2/market/timings/{date}")

    def get_market_status(self, exchange: str = "NSE") -> Dict[str, Any]:
        """GET /v2/market/status/{exchange}"""
        return self._request("GET", f"/v2/market/status/{exchange}")

    # =========================================================================
    # 7. COMPANY FUNDAMENTALS SUITE V2 (Open Access — Query by ISIN)
    # =========================================================================

    def get_company_profile(self, isin: str) -> Dict[str, Any]:
        """GET /v2/fundamentals/{isin}/profile"""
        return self._request("GET", f"/v2/fundamentals/{isin}/profile")

    def get_balance_sheet(
        self, isin: str, statement_type: str = "consolidated", full_statement: bool = True
    ) -> Dict[str, Any]:
        """GET /v2/fundamentals/{isin}/balance-sheet"""
        return self._request(
            "GET",
            f"/v2/fundamentals/{isin}/balance-sheet",
            params={"type": statement_type, "fs": full_statement},
        )

    def get_cash_flow(
        self, isin: str, statement_type: str = "consolidated", full_statement: bool = True
    ) -> Dict[str, Any]:
        """GET /v2/fundamentals/{isin}/cash-flow"""
        return self._request(
            "GET",
            f"/v2/fundamentals/{isin}/cash-flow",
            params={"type": statement_type, "fs": full_statement},
        )

    def get_income_statement(
        self,
        isin: str,
        statement_type: str = "consolidated",
        time_period: str = "yearly",
        full_statement: bool = True,
    ) -> Dict[str, Any]:
        """GET /v2/fundamentals/{isin}/income-statement"""
        return self._request(
            "GET",
            f"/v2/fundamentals/{isin}/income-statement",
            params={"type": statement_type, "time_period": time_period, "fs": full_statement},
        )

    def get_share_holdings(self, isin: str) -> List[Dict[str, Any]]:
        """GET /v2/fundamentals/{isin}/share-holdings"""
        return self._request("GET", f"/v2/fundamentals/{isin}/share-holdings")

    def get_key_ratios(self, isin: str) -> List[Dict[str, Any]]:
        """GET /v2/fundamentals/{isin}/key-ratios"""
        return self._request("GET", f"/v2/fundamentals/{isin}/key-ratios")

    def get_corporate_actions(self, isin: str) -> List[Dict[str, Any]]:
        """GET /v2/fundamentals/{isin}/corporate-actions"""
        return self._request("GET", f"/v2/fundamentals/{isin}/corporate-actions")

    def get_competitors(self, isin: str) -> List[Dict[str, Any]]:
        """GET /v2/fundamentals/{isin}/competitors"""
        return self._request("GET", f"/v2/fundamentals/{isin}/competitors")

    # =========================================================================
    # 8. NEWS & PUBLIC IPO DATASETS V2 (Open Access)
    # =========================================================================

    def get_news(
        self,
        category: str = "instrument_keys",
        instrument_keys: Optional[Union[str, List[str]]] = None,
        page_number: int = 1,
        page_size: int = 20,
    ) -> Any:
        """GET /v2/news — category: 'instrument_keys' (max 30 keys), 'holdings', or 'positions'."""
        params: Dict[str, Any] = {
            "category": category,
            "page_number": page_number,
            "page_size": page_size,
        }
        if instrument_keys:
            params["instrument_keys"] = self._format_keys(instrument_keys, max_limit=30)
        return self._request("GET", "/v2/news", params=params)

    def get_ipos(
        self,
        status: str = "open",
        issue_type: Optional[str] = None,
        page_number: int = 1,
        records: int = 30,
    ) -> Any:
        """GET /v2/ipos — status: 'upcoming', 'open', 'closed', 'listed'; issue_type: 'regular', 'sme'."""
        params = {
            "status": status,
            "issue_type": issue_type,
            "page_number": page_number,
            "records": records,
        }
        return self._request("GET", "/v2/ipos", params=params)

    def get_ipo_details(self, ipo_id: str) -> Dict[str, Any]:
        """GET /v2/ipos/{id}"""
        return self._request("GET", f"/v2/ipos/{ipo_id}")

    # =========================================================================
    # 9. CHARGES & MARGIN CALCULATORS V2 (Open Access)
    # =========================================================================

    def get_brokerage_charges(
        self,
        instrument_token: str,
        quantity: int,
        product: str,
        transaction_type: str,
        price: float,
    ) -> Dict[str, Any]:
        """GET /v2/charges/brokerage"""
        params = {
            "instrument_token": instrument_token,
            "quantity": quantity,
            "product": product,
            "transaction_type": transaction_type,
            "price": price,
        }
        return self._request("GET", "/v2/charges/brokerage", params=params)

    def calculate_margin(self, instruments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """POST /v2/charges/margin (Up to 20 instruments per call)."""
        return self._request("POST", "/v2/charges/margin", json_body={"instruments": instruments})

    # =========================================================================
    # 10. WEBSOCKET STREAM AUTHORIZATION — V3 & V2 (Open Access)
    # =========================================================================

    def get_market_data_feed_ws_url_v3(self) -> str:
        """GET /v3/feed/market-data-feed/authorize"""
        res = self._request("GET", "/v3/feed/market-data-feed/authorize")
        return res.get("authorized_redirect_uri", res)

    def get_market_data_feed_ws_url_v2(self) -> str:
        """GET /v2/feed/market-data-feed/authorize (Legacy V2 fallback)"""
        res = self._request("GET", "/v2/feed/market-data-feed/authorize")
        return res.get("authorized_redirect_uri", res)

    def get_portfolio_stream_feed_ws_url(
        self, update_types: Optional[str] = "order,gtt_order,position,holding"
    ) -> str:
        """
        GET /v2/feed/portfolio-stream-feed/authorize
        :param update_types: Comma-separated combination of 'order', 'gtt_order', 'position', 'holding'
        """
        res = self._request(
            "GET",
            "/v2/feed/portfolio-stream-feed/authorize",
            params={"update_types": update_types},
        )
        return res.get("authorized_redirect_uri", res)

    # =========================================================================
    # 11. USER, FUNDS (V2/V3), KILL SWITCH & STATIC IP (Requires Whitelisted Static IP)
    # =========================================================================

    def get_user_profile(self) -> Dict[str, Any]:
        """GET /v2/user/profile"""
        return self._request("GET", "/v2/user/profile")

    def get_funds_and_margin_v3(self) -> Dict[str, Any]:
        """
        GET /v3/user/get-funds-and-margin
        Unified breakdown of cash_available_to_trade, pledge_available_to_trade, and unsettled profit.
        """
        return self._request(
            "GET",
            "/v3/user/get-funds-and-margin",
            extra_headers={"Api-Version": "3.0"},
        )

    def get_funds_and_margin_v2(self, segment: Optional[str] = None) -> Dict[str, Any]:
        """GET /v2/user/get-funds-and-margin — segment: 'SEC' or 'COM'."""
        return self._request("GET", "/v2/user/get-funds-and-margin", params={"segment": segment})

    def get_kill_switch_status(self) -> List[Dict[str, Any]]:
        """GET /v2/user/kill-switch — Segment-wise ACTIVE/INACTIVE and kill_switch_enabled status."""
        return self._request("GET", "/v2/user/kill-switch")

    def get_static_ips(self) -> Dict[str, Any]:
        """GET /v2/user/ip — Registered primary and secondary static IPs for the account."""
        return self._request("GET", "/v2/user/ip")

    # =========================================================================
    # 12. PAYMENTS — PAY-INS & PAYOUTS (Requires Whitelisted Static IP)
    # =========================================================================

    def get_payins(self) -> List[Dict[str, Any]]:
        """GET /v2/user/payments/payin — Last 20 fund deposit transactions."""
        return self._request("GET", "/v2/user/payments/payin")

    def get_payouts(self) -> List[Dict[str, Any]]:
        """GET /v2/user/payments/payout — Last 20 fund withdrawal transactions & ETAs."""
        return self._request("GET", "/v2/user/payments/payout")

    def get_payout_modes(self) -> Any:
        """GET /v2/user/payments/payout-modes — NEFT/IMPS eligibility and withdrawal limits."""
        return self._request("GET", "/v2/user/payments/payout-modes")

    # =========================================================================
    # 13. PORTFOLIO — HOLDINGS, POSITIONS & MTF (Requires Whitelisted Static IP)
    # =========================================================================

    def get_long_term_holdings(self) -> List[Dict[str, Any]]:
        """GET /v2/portfolio/long-term-holdings"""
        return self._request("GET", "/v2/portfolio/long-term-holdings")

    def get_positions(self) -> List[Dict[str, Any]]:
        """GET /v2/portfolio/short-term-positions"""
        return self._request("GET", "/v2/portfolio/short-term-positions")

    def get_mtf_positions(self) -> List[Dict[str, Any]]:
        """GET /v3/portfolio/mtf-positions — Margin Trade Funding positions."""
        return self._request("GET", "/v3/portfolio/mtf-positions")

    # =========================================================================
    # 14. MUTUAL FUNDS SUITE V2 (Requires Whitelisted Static IP)
    # =========================================================================

    def get_mf_holdings(self) -> List[Dict[str, Any]]:
        """GET /v2/mf/holdings — Mutual fund portfolio holdings, NAV, folio, and P&L."""
        return self._request("GET", "/v2/mf/holdings")

    def get_mf_orders(
        self,
        page_number: int = 1,
        records: int = 10,
        status: str = "ALL",
        transaction_type: str = "ALL",
    ) -> List[Dict[str, Any]]:
        """GET /v2/mf/orders — Paginated Mutual Fund order book."""
        params = {
            "page_number": page_number,
            "records": records,
            "status": status,
            "transaction_type": transaction_type,
        }
        return self._request("GET", "/v2/mf/orders", params=params)

    def get_mf_order_details(self, order_id: str) -> Dict[str, Any]:
        """GET /v2/mf/orders/{order_id} — Single Mutual Fund order details."""
        return self._request("GET", f"/v2/mf/orders/{order_id}")

    def get_mf_sips(self, page_number: int = 1, records: int = 10) -> List[Dict[str, Any]]:
        """GET /v2/mf/sips — Paginated Mutual Fund SIP registrations (max records=30)."""
        return self._request(
            "GET",
            "/v2/mf/sips",
            params={"page_number": page_number, "records": records},
        )

    # =========================================================================
    # 15. ORDERS, TRADES, GTT & IPO ORDERS (Requires Whitelisted Static IP)
    # =========================================================================

    def get_order_book(self) -> List[Dict[str, Any]]:
        """GET /v2/order/retrieve-all — Full order book for the current trading day."""
        return self._request("GET", "/v2/order/retrieve-all")

    def get_order_details(
        self, order_id: Optional[str] = None, tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """GET /v2/order/details — Latest status of a specific order by order_id or tag."""
        if not order_id and not tag:
            raise ValueError("At least one of `order_id` or `tag` is required.")
        return self._request("GET", "/v2/order/details", params={"order_id": order_id, "tag": tag})

    def get_order_history(
        self, order_id: Optional[str] = None, tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """GET /v2/order/history — Progression stages of an order by order_id or tag."""
        if not order_id and not tag:
            raise ValueError("At least one of `order_id` or `tag` is required.")
        return self._request("GET", "/v2/order/history", params={"order_id": order_id, "tag": tag})

    def get_trade_book(self) -> List[Dict[str, Any]]:
        """GET /v2/order/trades/get-trades-for-day — All executed trades for today."""
        return self._request("GET", "/v2/order/trades/get-trades-for-day")

    def get_trades_by_order(self, order_id: str) -> List[Dict[str, Any]]:
        """GET /v2/order/trades — Executed fills for a specific order_id."""
        return self._request("GET", "/v2/order/trades", params={"order_id": order_id})

    def get_historical_trades(
        self,
        segment: str,
        start_date: str,
        end_date: str,
        page_number: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        GET /v2/charges/historical-trades — Historical trade fills across a date range.
        :param segment: 'EQ', 'FO', 'COM', 'CD', 'MF'
        :param start_date: 'YYYY-MM-DD'
        :param end_date: 'YYYY-MM-DD'
        """
        params = {
            "segment": segment,
            "start_date": start_date,
            "end_date": end_date,
            "page_number": page_number,
            "page_size": page_size,
        }
        return self._request("GET", "/v2/charges/historical-trades", params=params)

    def get_gtt_order_details(self, gtt_order_id: Optional[str] = None) -> Any:
        """GET /v3/order/gtt — Fetch active GTT order(s) and ENTRY/TARGET/STOPLOSS rules."""
        return self._request("GET", "/v3/order/gtt", params={"gtt_order_id": gtt_order_id})

    def get_ipo_orders(self, page_number: int = 1, records: int = 10) -> Any:
        """GET /v2/ipos/orders — Paginated list of user IPO applications."""
        return self._request(
            "GET",
            "/v2/ipos/orders",
            params={"page_number": page_number, "records": records},
        )

    def get_ipo_order_details(self, order_id: str) -> Dict[str, Any]:
        """GET /v2/ipos/orders/{order_id} — Single IPO application & UPI mandate status."""
        return self._request("GET", f"/v2/ipos/orders/{order_id}")

    # =========================================================================
    # 16. TRADE PROFIT & LOSS (P&L) SUITE V2 (Requires Whitelisted Static IP)
    # =========================================================================

    def get_trade_pnl_metadata(
        self,
        segment: str,
        financial_year: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        GET /v2/trade/profit-loss/metadata
        :param segment: 'EQ', 'FO', 'COM', 'CD'
        :param financial_year: Concatenated 4-digit FY (e.g., '2526' for FY 2025-2026)
        :param from_date: Optional 'dd-mm-yyyy'
        :param to_date: Optional 'dd-mm-yyyy'
        """
        params = {
            "segment": segment,
            "financial_year": financial_year,
            "from_date": from_date,
            "to_date": to_date,
        }
        return self._request("GET", "/v2/trade/profit-loss/metadata", params=params)

    def get_trade_pnl_report(
        self,
        segment: str,
        financial_year: str,
        page_number: int = 1,
        page_size: int = 100,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        GET /v2/trade/profit-loss/data — Paginated trade-wise realized P&L report.
        :param from_date: Optional 'dd-mm-yyyy'
        :param to_date: Optional 'dd-mm-yyyy'
        """
        params = {
            "segment": segment,
            "financial_year": financial_year,
            "page_number": page_number,
            "page_size": page_size,
            "from_date": from_date,
            "to_date": to_date,
        }
        return self._request("GET", "/v2/trade/profit-loss/data", params=params)

    def get_trade_pnl_charges(
        self,
        segment: str,
        financial_year: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        GET /v2/trade/profit-loss/charges — Statutory taxes & brokerage breakdown for P&L.
        """
        params = {
            "segment": segment,
            "financial_year": financial_year,
            "from_date": from_date,
            "to_date": to_date,
        }
        return self._request("GET", "/v2/trade/profit-loss/charges", params=params)

    # =========================================================================
    # DATAFRAME HELPER
    # =========================================================================

    @staticmethod
    def candles_to_df(candle_response: Any):
        """Convert any V2/V3 historical or intraday candle response into a sorted Pandas DataFrame."""
        import pandas as pd

        candles = (
            candle_response.get("candles", [])
            if isinstance(candle_response, dict)
            else candle_response
        )
        df = pd.DataFrame(
            candles,
            columns=["timestamp", "open", "high", "low", "close", "volume", "oi"],
        )
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp").reset_index(drop=True)
        return df
