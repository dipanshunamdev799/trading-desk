"""Read-only Tapetide endpoint library, backed by the published REST API.

The personal token is accepted directly by REST. Unlike the MCP bridge this
does not need OAuth exchange, MCP sessions, or size-truncated text responses.
"""
from __future__ import annotations

import copy
import json
import os
import threading
import time
from pathlib import Path
from urllib.parse import quote

import requests


ENDPOINTS = json.loads(Path(__file__).with_name("tapetide_endpoints.json").read_text())["endpoints"]


class TapetideAPIError(Exception):
    def __init__(self, status_code: int, message: str = "Tapetide request failed"):
        self.status_code = status_code
        # Never include response bodies, request headers or tokens in errors.
        super().__init__(f"{message} (HTTP {status_code})")


class TapetideClient:
    BASE_URL = "https://api.tapetide.com"

    def __init__(self, token: str | None = None, timeout: float = 15, requests_per_second: float = 2):
        self._token = token or os.getenv("TAPETIDE_TOKEN", "")
        self.timeout = timeout
        self.spacing = 1 / max(0.1, requests_per_second)
        self._lock = threading.Lock()
        self._next_request = 0.0
        self._local = threading.local()

    @property
    def configured(self) -> bool:
        return bool(self._token)

    @staticmethod
    def catalog() -> dict:
        return copy.deepcopy(ENDPOINTS)

    def call(self, endpoint: str, **parameters) -> dict:
        if endpoint not in ENDPOINTS:
            raise ValueError(f"Unknown read-only Tapetide dataset: {endpoint}")
        definition = ENDPOINTS[endpoint]
        allowed = {p["name"] for p in definition["parameters"]}
        if set(parameters) - allowed:
            raise ValueError(f"Unknown parameters for {endpoint}: {sorted(set(parameters) - allowed)}")
        for p in definition["parameters"]:
            if p["required"] and parameters.get(p["name"]) in (None, ""):
                raise ValueError(f"{endpoint} requires {p['name']}")
            value, schema = parameters.get(p["name"]), p["schema"]
            if value is None:
                continue
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if "minimum" in schema and value < schema["minimum"] or "maximum" in schema and value > schema["maximum"]:
                    raise ValueError(f"{endpoint}: {p['name']} is outside the documented range")
            if "enum" in schema and value not in schema["enum"]:
                raise ValueError(f"{endpoint}: invalid {p['name']}")
        if not self.configured:
            raise TapetideAPIError(401, "TAPETIDE_TOKEN is not configured")
        path, query = definition["path"], {}
        for p in definition["parameters"]:
            value = parameters.get(p["name"])
            if value is None:
                continue
            if p["in"] == "path":
                path = path.replace("{" + p["name"] + "}", quote(str(value), safe=""))
            else:
                query[p["name"]] = (",".join(map(str, value)) if isinstance(value, (list, tuple)) else
                                     str(value).lower() if isinstance(value, bool) else value)
        with self._lock:
            delay = self._next_request - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            self._next_request = time.monotonic() + self.spacing
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session()
        try:
            response = self._local.session.get(self.BASE_URL + path, params=query,
                headers={"Authorization": f"Bearer {self._token}", "Accept": "application/json"},
                timeout=(min(5, self.timeout), self.timeout), allow_redirects=False)
        except requests.RequestException:
            raise TapetideAPIError(503, "Tapetide transport unavailable") from None
        if not 200 <= response.status_code < 300:
            raise TapetideAPIError(response.status_code)
        try:
            payload = response.json()
        except ValueError:
            raise TapetideAPIError(502, "Tapetide returned invalid JSON") from None
        if not isinstance(payload, dict) or "data" not in payload or payload.get("error"):
            raise TapetideAPIError(502, "Tapetide returned an invalid dataset")
        return payload
