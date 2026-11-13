"""Smoke tests that run the Streamlit app headlessly and use each tab."""

from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import currency

APP_PATH = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")


@pytest.fixture(autouse=True)
def fake_exchange_rates(monkeypatch):
    """Never call the real exchange-rate API from tests."""

    def fake_get(path, params=None):
        if path == "currencies":
            return {"USD": "United States Dollar", "BRL": "Brazilian Real", "EUR": "Euro"}
        if path == "latest":
            return {"date": "2026-11-12", "rates": {params["symbols"]: 5.0}}
        return {
            "rates": {
                "2026-10-01": {params["symbols"]: 4.0},
                "2026-11-12": {params["symbols"]: 5.0},
            }
        }

    monkeypatch.setattr(currency, "_get", fake_get)
    st.cache_data.clear()  # don't reuse rates cached by another test


@pytest.fixture
def app():
    at = AppTest.from_file(APP_PATH, default_timeout=30).run()
    assert not at.exception
    return at


def metric_values(at):
    return {m.label: m.value for m in at.metric}


def test_app_renders_all_tabs(app):
    assert "Calculator Loop" in app.markdown[1].value
    assert [tab.label for tab in app.tabs] == [
        "🧮 Basic",
        "💰 Financial",
        "🔄 Converter",
        "📈 Plotter",
        "📊 Statistics",
    ]


def press(app, *keys):
    """Click keypad buttons by their label."""
    for key in keys:
        button = next(b for b in app.button if b.label == key)
        button.click().run()
        assert not app.exception


def test_keypad_builds_and_evaluates_expression(app):
    press(app, "(", "3", "+", "4", ")", "×", "2", "^", "3", "=")
    assert app.session_state.expr_output == {"expr": "(3+4)×2^3", "result": 56.0}
    assert app.session_state.history[0]["Result"] == 56.0
    # The answer stays on the display so you can keep calculating
    assert app.text_input(key="expr").value == "56"


def test_typed_expression_and_errors(app):
    app.text_input(key="expr").input("sqrt(16) + 10 % 3").run()
    assert app.session_state.expr_output["result"] == 5.0

    app.text_input(key="expr").input("1/0").run()
    assert "Division by zero" in app.session_state.expr_output["error"]

    press(app, "C")
    assert app.text_input(key="expr").value == ""


def test_two_number_mode(app):
    app.segmented_control(key="basic_mode").set_value("🔢 Two numbers").run()
    basic = app.tabs[0]
    basic.number_input[0].set_value(2)
    basic.number_input[1].set_value(10)
    basic.selectbox[0].set_value("^")
    next(b for b in app.button if b.label == "Calculate").click().run()
    assert not app.exception
    assert metric_values(app)["2 ^ 10"] == "1,024"


def test_financial_defaults(app):
    assert metric_values(app)["Final balance"] == "20,514.24"
    app.segmented_control(key="financial_mode").set_value("🏠 Loan / mortgage").run()
    assert not app.exception
    assert metric_values(app)["Monthly payment"] == "1,199.10"


def test_unit_converter(app):
    converter = app.tabs[2]
    converter.selectbox[0].set_value("Temperature").run()
    app.tabs[2].number_input[0].set_value(100).run()
    assert not app.exception
    assert metric_values(app)["100 Celsius ="] == "212 Fahrenheit"


def test_currency_converter(app):
    app.segmented_control(key="converter_mode").set_value("💱 Currency (live rates)").run()
    assert not app.exception
    banner = next(m.value for m in app.markdown if 'class="fx-banner"' in m.value)
    assert "500.00 BRL" in banner  # 100 USD at the fake rate of 5
    assert metric_values(app)["Highest"] == "5"

    next(b for b in app.button if b.label == "⇄").click().run()
    assert app.selectbox(key="fx_from").value == "BRL"
    assert app.selectbox(key="fx_to").value == "USD"


def test_currency_converter_when_service_is_down(app, monkeypatch):
    def broken(path, params=None):
        raise currency.CurrencyError("Could not load exchange rates right now.")

    monkeypatch.setattr(currency, "_get", broken)
    app.segmented_control(key="converter_mode").set_value("💱 Currency (live rates)").run()
    assert not app.exception
    assert any("Could not load exchange rates" in e.value for e in app.error)


def test_plotter_compares_two_formulas(app):
    app.text_input(key="formula_2").input("x + 2").run()
    assert not app.exception
    # x^2 - 3x + 2 = x + 2  →  x = 0 and x = 4
    values = metric_values(app)
    assert values["Crossing points"] == "2"
    assert values["Where the curves meet"] == "x ≈ 0, x ≈ 4"


def test_plotter_rejects_unsafe_formula(app):
    plotter = app.tabs[3]
    plotter.text_input[0].set_value('__import__("os")').run()
    assert any("Unknown function" in e.value for e in app.error)


def test_statistics_defaults(app):
    assert metric_values(app)["Mean"] == "23.125"
