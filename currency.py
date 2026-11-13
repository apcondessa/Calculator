"""
Live exchange rates for Calculator Loop.

Rates come from the free Frankfurter API (https://frankfurter.dev), which
publishes the European Central Bank reference rates once per working day.
No API key is needed.
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import requests

# Lets the app detect that this file changed since it was imported (see streamlit_app.py)
LOADED_MTIME = os.path.getmtime(__file__)

API_URL = "https://api.frankfurter.dev/v1"
TIMEOUT_SECONDS = 10

# Shown first in the currency lists
POPULAR_CURRENCIES = ["BRL", "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"]


class CurrencyError(RuntimeError):
    """Raised when exchange rates cannot be loaded (message kept as a template)."""

    def __init__(self, template: str, **params):
        self.template = template
        self.params = params
        super().__init__(template.format(**params))


def _get(path: str, params: dict | None = None) -> dict:
    """Call the Frankfurter API and return the JSON response."""
    try:
        response = requests.get(f"{API_URL}/{path}", params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise CurrencyError(
            "Could not load exchange rates right now. Please try again in a moment."
        ) from exc
    except ValueError as exc:  # invalid JSON
        raise CurrencyError("The exchange-rate service returned an unexpected answer.") from exc


def get_currencies() -> dict[str, str]:
    """Return available currencies as ``{"USD": "United States Dollar", ...}``."""
    data = _get("currencies")
    if not isinstance(data, dict) or not data:
        raise CurrencyError("The exchange-rate service returned no currencies.")
    return data


def sort_currencies(codes: list[str]) -> list[str]:
    """Put popular currencies first, then the rest alphabetically."""
    popular = [code for code in POPULAR_CURRENCIES if code in codes]
    others = sorted(code for code in codes if code not in POPULAR_CURRENCIES)
    return popular + others


def get_latest_rate(base: str, target: str) -> tuple[float, str]:
    """Return ``(rate, date)``: how much one unit of ``base`` is worth in ``target``."""
    if base == target:
        return 1.0, date.today().isoformat()
    data = _get("latest", {"base": base, "symbols": target})
    try:
        return float(data["rates"][target]), data["date"]
    except (KeyError, TypeError, ValueError) as exc:
        raise CurrencyError(
            "No exchange rate available for {base} → {target}.", base=base, target=target
        ) from exc


def get_rate_history(base: str, target: str, days: int) -> list[dict]:
    """
    Return the daily rate over the last ``days`` days as
    ``[{"Date": "2026-01-02", "Rate": 5.31}, ...]`` (working days only).
    """
    if base == target:
        return []
    start = (date.today() - timedelta(days=days)).isoformat()
    data = _get(f"{start}..", {"base": base, "symbols": target})
    try:
        rates = data["rates"]
        return [
            {"Date": day, "Rate": float(values[target])}
            for day, values in sorted(rates.items())
            if target in values
        ]
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise CurrencyError("The rate history could not be read.") from exc


def convert_amount(amount: float, rate: float) -> float:
    """Convert ``amount`` using ``rate`` (units of target per unit of base)."""
    return amount * rate
