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
    assert any("Calculator Loop" in m.value for m in app.markdown)
    assert app.session_state.lang == "en"
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
    assert "Division by zero" in str(app.session_state.expr_output["error"])
    assert any("Division by zero" in m.value for m in app.markdown)

    press(app, "C")
    assert app.text_input(key="expr").value == ""


def test_two_number_mode(app):
    app.segmented_control(key="basic_mode").set_value("two_numbers").run()
    app.number_input(key="two_a").set_value(2)
    app.number_input(key="two_b").set_value(10)
    app.selectbox(key="two_op__en").set_value("^")
    next(b for b in app.button if b.label == "Calculate").click().run()
    assert not app.exception
    assert metric_values(app)["2 ^ 10"] == "1,024"


def test_financial_defaults(app):
    assert metric_values(app)["Final balance"] == "20,514.24"
    app.segmented_control(key="financial_mode").set_value("loan").run()
    assert not app.exception
    assert metric_values(app)["Monthly payment"] == "1,199.10"


def test_unit_converter(app):
    app.selectbox(key="unit_category__en").set_value("Temperature").run()
    app.number_input(key="unit_value").set_value(100).run()
    assert not app.exception
    assert metric_values(app)["100 Celsius ="] == "212 Fahrenheit"


def test_currency_converter(app):
    app.segmented_control(key="converter_mode").set_value("currency").run()
    assert not app.exception
    banner = next(m.value for m in app.markdown if 'class="fx-banner"' in m.value)
    assert "500.00 BRL" in banner  # 100 USD at the fake rate of 5
    assert metric_values(app)["Highest"] == "5"

    next(b for b in app.button if b.label == "⇄").click().run()
    assert app.session_state.fx_from == "BRL"
    assert app.session_state.fx_to == "USD"
    banner = next(m.value for m in app.markdown if 'class="fx-banner"' in m.value)
    assert "100.00 BRL" in banner


def test_currency_converter_when_service_is_down(app, monkeypatch):
    def broken(path, params=None):
        raise currency.CurrencyError("Could not load exchange rates right now.")

    monkeypatch.setattr(currency, "_get", broken)
    app.segmented_control(key="converter_mode").set_value("currency").run()
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
    app.text_input(key="formula_x^2 - 3*x + 2").set_value('__import__("os")').run()
    assert any("Unknown function" in e.value for e in app.error)


def test_statistics_defaults(app):
    assert metric_values(app)["Mean"] == "23.125"


# --- Portuguese -------------------------------------------------------------
def switch_to_portuguese(app):
    app.segmented_control(key="lang_widget").set_value("pt").run()
    assert not app.exception
    assert app.session_state.lang == "pt"


def test_language_switch_translates_everything(app):
    switch_to_portuguese(app)
    assert [tab.label for tab in app.tabs] == [
        "🧮 Básica",
        "💰 Financeira",
        "🔄 Conversor",
        "📈 Gráficos",
        "📊 Estatística",
    ]
    assert app.query_params["lang"] == "pt"
    values = metric_values(app)
    # Brazilian number format: dot for thousands, comma for decimals
    assert values["Saldo final"] == "20.514,24"
    assert values["Média"] == "23,125"

    app.segmented_control(key="lang_widget").set_value("en").run()
    assert metric_values(app)["Final balance"] == "20,514.24"


def test_switching_language_keeps_typed_values(app):
    app.number_input(key="invest_principal").set_value(5000).run()
    switch_to_portuguese(app)
    assert app.number_input(key="invest_principal").value == 5000


def test_link_with_lang_parameter_opens_in_portuguese():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.query_params["lang"] = "pt"
    at.run()
    assert not at.exception
    assert at.session_state.lang == "pt"
    assert at.tabs[0].label == "🧮 Básica"


def test_portuguese_keypad_uses_decimal_comma(app):
    switch_to_portuguese(app)
    assert any(b.label == "," for b in app.button)
    app.text_input(key="expr").input("2,5 × 4").run()
    assert app.session_state.expr_output["result"] == 10.0

    app.text_input(key="expr").input("1/0").run()
    assert any("Não é possível dividir por zero" in m.value for m in app.markdown)


def test_portuguese_loan_and_converter(app):
    switch_to_portuguese(app)
    app.segmented_control(key="financial_mode").set_value("loan").run()
    assert metric_values(app)["Parcela mensal"] == "1.199,10"

    app.selectbox(key="unit_category__pt").set_value("Temperature").run()
    app.number_input(key="unit_value").set_value(100).run()
    assert metric_values(app)["100 Celsius ="] == "212 Fahrenheit"
    app.selectbox(key="unit_category__pt").set_value("Length").run()
    assert metric_values(app)["100 Quilômetro ="] == "62,137119 Milha"


def test_portuguese_currency_converter(app):
    switch_to_portuguese(app)
    app.segmented_control(key="converter_mode").set_value("currency").run()
    banner = next(m.value for m in app.markdown if 'class="fx-banner"' in m.value)
    assert "500,00 BRL" in banner
    assert "cotação de 12/11/2026" in banner
    assert app.selectbox(key="fx_to__pt").format_func("BRL") == "BRL — Real brasileiro"


def test_portuguese_statistics_accepts_decimal_commas(app):
    switch_to_portuguese(app)
    app.text_area(key="stats_text_pt").input("1,5; 2,5; 3,5").run()
    assert metric_values(app)["Média"] == "2,5"


def test_dropdown_choice_survives_language_switch(app):
    app.selectbox(key="invest_compounding__en").set_value("Quarterly").run()
    switch_to_portuguese(app)
    box = app.selectbox(key="invest_compounding__pt")
    assert box.value == "Quarterly"
    assert box.format_func(box.value) == "Trimestral"


def test_app_reloads_helper_modules_left_over_from_an_older_version():
    """
    Reproduces a crash seen on Streamlit Cloud after a deploy: the new
    streamlit_app.py ran with the previous calculator.py still in memory, whose
    parse_numbers() did not accept decimal_comma yet.
    """
    import calculator

    def old_parse_numbers(text):  # the signature before the language switch
        raise AssertionError("the outdated module should have been reloaded")

    saved = dict(calculator.__dict__)
    try:
        calculator.parse_numbers = old_parse_numbers
        calculator.LOADED_MTIME = 0.0  # "imported from an older version of the file"

        at = AppTest.from_file(APP_PATH, default_timeout=30).run()
        assert not at.exception
        assert metric_values(at)["Mean"] == "23.125"
        assert calculator.parse_numbers is not old_parse_numbers
    finally:
        # Put the module back exactly as it was so other tests keep their classes
        calculator.__dict__.clear()
        calculator.__dict__.update(saved)
