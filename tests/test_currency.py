"""Tests for currency.py with the network replaced by fake responses."""

import pytest
import requests

import currency


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"HTTP {self.status}")

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


@pytest.fixture
def fake_api(monkeypatch):
    """Replace requests.get and record the URLs that were requested."""
    calls = []

    def install(payload, status=200):
        def fake_get(url, params=None, timeout=None):
            calls.append((url, params))
            return FakeResponse(payload, status)

        monkeypatch.setattr(currency.requests, "get", fake_get)
        return calls

    return install


def test_get_latest_rate(fake_api):
    calls = fake_api({"amount": 1.0, "base": "USD", "date": "2026-11-12", "rates": {"BRL": 5.31}})
    assert currency.get_latest_rate("USD", "BRL") == (5.31, "2026-11-12")
    assert calls[0] == (f"{currency.API_URL}/latest", {"base": "USD", "symbols": "BRL"})


def test_same_currency_needs_no_request(fake_api):
    calls = fake_api({})
    assert currency.get_latest_rate("EUR", "EUR")[0] == 1.0
    assert currency.get_rate_history("EUR", "EUR", 30) == []
    assert calls == []


def test_get_rate_history_is_sorted(fake_api):
    fake_api(
        {
            "base": "USD",
            "rates": {
                "2026-11-03": {"BRL": 5.2},
                "2026-11-01": {"BRL": 5.0},
                "2026-11-02": {"BRL": 5.1},
            },
        }
    )
    history = currency.get_rate_history("USD", "BRL", 30)
    assert [row["Date"] for row in history] == ["2026-11-01", "2026-11-02", "2026-11-03"]
    assert [row["Rate"] for row in history] == [5.0, 5.1, 5.2]


def test_get_currencies(fake_api):
    fake_api({"BRL": "Brazilian Real", "USD": "United States Dollar"})
    assert currency.get_currencies()["BRL"] == "Brazilian Real"


@pytest.mark.parametrize(
    ("payload", "status"),
    [
        ({}, 404),  # HTTP error
        (ValueError("not JSON"), 200),  # invalid JSON
        ({"date": "2026-11-12", "rates": {}}, 200),  # currency missing
    ],
)
def test_latest_rate_errors(fake_api, payload, status):
    fake_api(payload, status)
    with pytest.raises(currency.CurrencyError):
        currency.get_latest_rate("USD", "XYZ")


def test_network_failure(monkeypatch):
    def offline(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(currency.requests, "get", offline)
    with pytest.raises(currency.CurrencyError):
        currency.get_currencies()


def test_sort_currencies_puts_popular_first():
    assert currency.sort_currencies(["ZAR", "USD", "AUD", "BRL", "SEK"]) == [
        "BRL",
        "USD",
        "AUD",
        "SEK",
        "ZAR",
    ]


def test_convert_amount():
    assert currency.convert_amount(100, 5.31) == pytest.approx(531)
