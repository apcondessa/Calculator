"""Smoke tests that run the Streamlit app headlessly and use each tab."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")


@pytest.fixture
def app():
    at = AppTest.from_file(APP_PATH, default_timeout=30).run()
    assert not at.exception
    return at


def metric_values(at):
    return {m.label: m.value for m in at.metric}


def test_app_renders_all_tabs(app):
    assert app.title[0].value == "🎈 Calculator Loop"
    assert [tab.label for tab in app.tabs] == [
        "🧮 Basic",
        "💰 Financial",
        "📏 Converter",
        "📈 Plotter",
        "📊 Statistics",
    ]


def test_basic_calculation_is_added_to_history(app):
    basic = app.tabs[0]
    basic.number_input[0].set_value(2)
    basic.number_input[1].set_value(10)
    basic.selectbox[0].set_value("^")
    basic.button[0].click().run()
    assert not app.exception
    assert metric_values(app)["2 ^ 10"] == "1,024"
    assert len(app.tabs[0].dataframe[0].value) == 1


def test_basic_division_by_zero_shows_error(app):
    basic = app.tabs[0]
    basic.number_input[0].set_value(5)
    basic.selectbox[0].set_value("÷")
    basic.button[0].click().run()
    assert any("Division by zero" in e.value for e in app.error)


def test_financial_defaults(app):
    values = metric_values(app)
    assert values["Final balance"] == "20,514.24"

    app.tabs[1].radio[0].set_value("Loan / mortgage").run()
    assert not app.exception
    assert metric_values(app)["Monthly payment"] == "1,199.10"


def test_converter(app):
    converter = app.tabs[2]
    converter.selectbox[0].set_value("Temperature").run()
    converter = app.tabs[2]
    converter.number_input[0].set_value(100).run()
    assert not app.exception
    assert metric_values(app)["100 Celsius ="] == "212 Fahrenheit"


def test_plotter_rejects_unsafe_formula(app):
    plotter = app.tabs[3]
    plotter.text_input[0].set_value('__import__("os")').run()
    assert any("Unknown function" in e.value for e in app.error)


def test_statistics_defaults(app):
    assert metric_values(app)["Mean"] == "23.125"
