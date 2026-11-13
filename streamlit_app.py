"""
Calculator Loop - Streamlit Application

A web-based multi-tool calculator built with Streamlit. It has five tabs:

- Basic: a keypad calculator for expressions, or two numbers and an
  operation, with a calculation history
- Financial: compound interest and loan/mortgage calculators with charts
- Converter: units (length, weight, temperature...) and live currency rates
- Plotter: graph one or two formulas of x and find where they cross
- Statistics: descriptive statistics for pasted numbers or an uploaded CSV

The whole interface is available in English and Portuguese (see i18n.py).

Author: Ana Condessa
"""

from __future__ import annotations

import html
import importlib
import os
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

import calculator
import currency
import i18n


def reload_if_changed(module) -> None:
    """
    Reload a helper module if its file changed after it was imported.

    Streamlit reruns this script on every interaction but keeps other modules
    in memory. After an update (e.g. a new deploy on Streamlit Cloud) the app
    could otherwise mix the new streamlit_app.py with old helper modules.
    """
    try:
        changed = getattr(module, "LOADED_MTIME", None) != os.path.getmtime(module.__file__)
    except OSError:
        return
    if changed:
        importlib.reload(module)


for _module in (i18n, calculator, currency):
    reload_if_changed(_module)

from calculator import (
    OPERATIONS,
    UNARY_OPERATIONS,
    UNITS,
    CalculationError,
    amortization_schedule,
    calculate,
    compound_interest_schedule,
    convert_units,
    evaluate_expression,
    find_crossings,
    format_expression,
    format_number,
    loan_payment,
    parse_numbers,
    sample_formula,
    summary_statistics,
)
from currency import (
    POPULAR_CURRENCIES,
    CurrencyError,
    convert_amount,
    get_currencies,
    get_latest_rate,
    get_rate_history,
    sort_currencies,
)
from i18n import (
    CURRENCY_NAMES_PT,
    LANGUAGES,
    format_date,
    localize_number,
    normalize_language,
    translate_error,
)
from i18n import t as translate

# Default "from" and "to" units shown for each converter category
DEFAULT_CONVERSIONS = {
    "Length": ("Kilometer", "Mile"),
    "Weight": ("Kilogram", "Pound"),
    "Volume": ("Liter", "Gallon (US)"),
    "Speed": ("Kilometers per hour", "Miles per hour"),
    "Data": ("Gigabyte", "Megabyte"),
    "Temperature": ("Celsius", "Fahrenheit"),
}

FORMULA_EXAMPLES = [
    "x^2 - 3*x + 2",
    "sin(x) * exp(-x/5)",
    "sqrt(abs(x))",
    "1 / x",
    "x^3 - 6*x",
    "log(x)",
]

COMPOUNDING_OPTIONS = {
    "Monthly": 12,
    "Quarterly": 4,
    "Semi-annually": 2,
    "Annually": 1,
    "Daily": 365,
}

HISTORY_PERIODS = {"1 month": 30, "3 months": 91, "1 year": 365, "5 years": 1826}

# Keypad layout: (label shown, text inserted, style group)
KEYPAD = [
    [("7", "7", "num"), ("8", "8", "num"), ("9", "9", "num"), ("÷", "÷", "op"), ("(", "(", "fn")],
    [("4", "4", "num"), ("5", "5", "num"), ("6", "6", "num"), ("×", "×", "op"), (")", ")", "fn")],
    [("1", "1", "num"), ("2", "2", "num"), ("3", "3", "num"), ("−", "-", "op"), ("^", "^", "fn")],
    [
        ("0", "0", "num"),
        (".", ".", "num"),
        ("π", "pi", "fn"),
        ("+", "+", "op"),
        ("√", "sqrt(", "fn"),
    ],
]

CUSTOM_CSS = """
<style>
/* Gradient header */
.hero {
    background: linear-gradient(120deg, #7C3AED 0%, #6366F1 45%, #06B6D4 100%);
    border-radius: 1.25rem;
    padding: 1.6rem 1.8rem 1.4rem;
    margin-bottom: 1.2rem;
    color: #FFFFFF;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.25);
}
.hero h1 { color: #FFFFFF; margin: 0; padding: 0; font-size: 2.3rem; }
.hero p { color: rgba(255, 255, 255, 0.88); margin: 0.35rem 0 0; font-size: 1.02rem; }

/* Tabs: larger labels */
.stTabs [data-baseweb="tab"] p { font-size: 1.02rem; font-weight: 600; }

/* Metrics as coloured cards */
[data-testid="stMetric"] {
    background: rgba(124, 58, 237, 0.08);
    border: 1px solid rgba(124, 58, 237, 0.25);
    border-left: 6px solid #7C3AED;
    border-radius: 0.9rem;
    padding: 0.8rem 1rem;
}
[data-testid="stColumn"]:nth-of-type(2) [data-testid="stMetric"] {
    background: rgba(6, 182, 212, 0.08);
    border-color: rgba(6, 182, 212, 0.3);
    border-left-color: #06B6D4;
}
[data-testid="stColumn"]:nth-of-type(3) [data-testid="stMetric"],
[data-testid="stColumn"]:nth-of-type(4) [data-testid="stMetric"] {
    background: rgba(245, 158, 11, 0.08);
    border-color: rgba(245, 158, 11, 0.3);
    border-left-color: #F59E0B;
}

/* Calculator display */
.calc-display {
    background: linear-gradient(135deg, #1E1B4B, #312E81);
    border-radius: 1rem;
    padding: 0.9rem 1.2rem;
    margin: 0.3rem 0 0.8rem;
    text-align: right;
    font-family: "Source Code Pro", monospace;
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.35);
}
.calc-display .expr { color: #C4B5FD; font-size: 1rem; min-height: 1.4rem; word-break: break-all; }
.calc-display .result {
    color: #FFFFFF; font-size: 2.2rem; font-weight: 700; word-break: break-all;
}
.calc-display .result.error { color: #FCA5A5; font-size: 1.1rem; font-weight: 600; }

/* Keypad buttons */
[class*="st-key-key_"] button { min-height: 3rem; }
[class*="st-key-key_"] button p { font-size: 1.3rem; font-weight: 700; }
[class*="st-key-key_op_"] button {
    background: rgba(6, 182, 212, 0.15); border-color: rgba(6, 182, 212, 0.5);
}
[class*="st-key-key_fn_"] button {
    background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.5);
}
.st-key-key_clear button, .st-key-key_back button {
    background: rgba(236, 72, 153, 0.15); border-color: rgba(236, 72, 153, 0.5);
}

/* Currency result banner */
.fx-banner {
    background: linear-gradient(120deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15));
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 1rem;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
}
.fx-banner .big { font-size: 1.9rem; font-weight: 700; }
.fx-banner .small { opacity: 0.8; font-size: 0.92rem; }
</style>
"""


# ---------------------------------------------------------------------------
# Language helpers
# ---------------------------------------------------------------------------
def lang() -> str:
    """The language chosen by the visitor ("en" or "pt")."""
    return st.session_state.get("lang", "en")


def t(key: str, **params) -> str:
    """Text for ``key`` in the current language."""
    return translate(key, lang(), **params)


def num(value: float, decimals: int = 10) -> str:
    """Format a number for display (1,234.5 in English, 1.234,5 in Portuguese)."""
    return localize_number(format_number(value, decimals), lang())


def money(value: float) -> str:
    """Format an amount with two decimals in the current language."""
    return localize_number(f"{value:,.2f}", lang())


def error_text(error: Exception) -> str:
    return translate_error(error, lang())


def option_text(prefix: str):
    """Format function for translated options, fixed to the current language."""
    code = lang()
    return lambda option: translate(f"{prefix}{option}", code)


def show_error(error: Exception) -> None:
    st.error(t("error", message=error_text(error)))


def translated_selectbox(label, options, key, format_func, default=None, container=None):
    """
    A selectbox whose option names are translated.

    Streamlit keeps showing the old option name after the language changes,
    so each language gets its own widget (``key__en`` / ``key__pt``) and the
    chosen value is carried over in ``st.session_state[key]``.
    """
    container = container or st
    options = list(options)
    current = st.session_state.get(key)
    if current not in options:
        current = default if default in options else options[0]
    widget_key = f"{key}__{lang()}"
    start_key = f"{widget_key}__start"
    if widget_key in st.session_state and st.session_state[widget_key] not in options:
        reset_selectbox(key)
    # Streamlit treats a selectbox whose starting index changes as a new widget
    # (and resets it), so the starting index is fixed when the widget is created
    if widget_key not in st.session_state or start_key not in st.session_state:
        st.session_state[start_key] = options.index(current)
    index = min(st.session_state[start_key], len(options) - 1)
    value = container.selectbox(
        label, options, index=index, format_func=format_func, key=widget_key
    )
    st.session_state[key] = value
    return value


def reset_selectbox(key: str) -> None:
    """Forget the widgets behind a translated selectbox; they restart from its saved value."""
    for code in LANGUAGES:
        for suffix in ("", "__start"):
            st.session_state.pop(f"{key}__{code}{suffix}", None)


def _set_language() -> None:
    choice = st.session_state.get("lang_widget")
    if choice:
        st.session_state.lang = choice
    else:  # the visitor clicked the selected option again; keep the language
        st.session_state.lang_widget = st.session_state.lang


def init_language() -> None:
    """Pick the language from the link (?lang=pt), the browser, or English."""
    if "lang" not in st.session_state:
        st.session_state.lang = (
            normalize_language(st.query_params.get("lang"))
            or normalize_language(getattr(st.context, "locale", None))
            or "en"
        )
    st.session_state.setdefault("lang_widget", st.session_state.lang)
    # Keep the choice in the address bar so it survives a refresh and can be shared
    if st.query_params.get("lang") != st.session_state.lang:
        st.query_params["lang"] = st.session_state.lang


def main():
    """Render the Streamlit application."""
    st.set_page_config(page_title="Calculator Loop", page_icon="🎈")
    init_language()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    _, col_lang = st.columns([3, 2])
    col_lang.segmented_control(
        t("language"),
        list(LANGUAGES),
        format_func=lambda code: {"en": "🌐 English", "pt": "🌐 Português"}[code],
        key="lang_widget",
        on_change=_set_language,
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div class="hero"><h1>🎈 Calculator Loop</h1><p>{t("subtitle")}</p></div>',
        unsafe_allow_html=True,
    )

    st.session_state.setdefault("history", [])

    tab_keys = ["tab.basic", "tab.financial", "tab.converter", "tab.plotter", "tab.statistics"]
    labels = [t(key) for key in tab_keys]
    # Stay on the same tab when the language (and so the tab names) changes
    open_tab = st.session_state.get("main_tabs")
    if open_tab is not None and open_tab not in labels:
        for code in LANGUAGES:
            names = [translate(key, code) for key in tab_keys]
            if open_tab in names:
                st.session_state.main_tabs = labels[names.index(open_tab)]
                break
    basic_tab, financial_tab, converter_tab, plotter_tab, stats_tab = st.tabs(
        labels, key="main_tabs", on_change="rerun"
    )
    with basic_tab:
        render_basic_tab()
    with financial_tab:
        render_financial_tab()
    with converter_tab:
        render_converter_tab()
    with plotter_tab:
        render_plotter_tab()
    with stats_tab:
        render_statistics_tab()


# ---------------------------------------------------------------------------
# Basic calculator
# ---------------------------------------------------------------------------
def add_to_history(expression: str, result: float) -> None:
    """Record a successful calculation at the top of the history."""
    st.session_state.history.insert(
        0,
        {"Time": datetime.now().strftime("%H:%M:%S"), "Expression": expression, "Result": result},
    )


def render_basic_tab():
    """Keypad / two-number calculator with a calculation history."""
    mode = st.segmented_control(
        t("mode"),
        ["keypad", "two_numbers"],
        format_func=option_text("mode."),
        default="keypad",
        key="basic_mode",
    )
    if mode == "two_numbers":
        render_two_number_calculator()
    else:
        render_keypad_calculator()
    render_history()


# --- Keypad / expression mode ----------------------------------------------
def _press(text: str) -> None:
    st.session_state.expr = st.session_state.get("expr", "") + text


def _backspace() -> None:
    st.session_state.expr = st.session_state.get("expr", "")[:-1]


def _clear() -> None:
    st.session_state.expr = ""
    st.session_state.expr_output = None


def _evaluate() -> None:
    expression = st.session_state.get("expr", "").strip()
    if not expression:
        return
    # In Portuguese the comma is the decimal separator: 2,5 means 2.5. Our
    # functions take a single argument, so a comma is never needed otherwise.
    to_evaluate = expression.replace(",", ".") if lang() == "pt" else expression
    try:
        result = evaluate_expression(to_evaluate)
    except CalculationError as error:
        st.session_state.expr_output = {"expr": expression, "error": error}
        return
    st.session_state.expr_output = {"expr": expression, "result": result}
    add_to_history(expression, result)
    # Continue from the answer, like a pocket calculator
    st.session_state.expr = localize_number(format_number(result).replace(",", ""), lang())


def render_keypad_calculator():
    """Calculator with clickable keys; expressions can also be typed."""
    st.session_state.setdefault("expr", "")
    st.session_state.setdefault("expr_output", None)

    output = st.session_state.expr_output
    if output is None:
        expr_html, result_html = "&nbsp;", '<div class="result">0</div>'
    elif "error" in output:
        expr_html = html.escape(output["expr"])
        message = html.escape(error_text(output["error"]))
        result_html = f'<div class="result error">⚠️ {message}</div>'
    else:
        expr_html = html.escape(output["expr"]) + " ="
        result_html = f'<div class="result">{num(output["result"])}</div>'
    st.markdown(
        f'<div class="calc-display"><div class="expr">{expr_html}</div>{result_html}</div>',
        unsafe_allow_html=True,
    )

    st.text_input(
        t("expression"),
        key="expr",
        placeholder=t("expression.placeholder"),
        on_change=_evaluate,
        help=t("expression.help"),
    )

    decimal = "," if lang() == "pt" else "."
    for row_number, row in enumerate(KEYPAD):
        cols = st.columns(5)
        for col_number, (col, (label, text, group)) in enumerate(zip(cols, row, strict=True)):
            if label == ".":
                label = text = decimal
            col.button(
                label,
                key=f"key_{group}_{row_number}{col_number}",
                on_click=_press,
                args=(text,),
                width="stretch",
            )
    cols = st.columns(5)
    cols[0].button("C", key="key_clear", on_click=_clear, width="stretch")
    cols[1].button("⌫", key="key_back", on_click=_backspace, width="stretch")
    cols[2].button("%", key="key_op_mod", on_click=_press, args=("%",), width="stretch")
    cols[3].button("e", key="key_fn_e", on_click=_press, args=("e",), width="stretch")
    cols[4].button("=", key="key_equals", on_click=_evaluate, type="primary", width="stretch")
    st.caption(t("keypad.caption"))


# --- Two-number mode ---------------------------------------------------------
def two_number_expression(a: float, b: float, operation: str) -> str:
    if operation == "% of":
        return t("percent_of", a=num(a), b=num(b))
    return localize_number(format_expression(a, b, operation), lang())


def render_two_number_calculator():
    """Pick an operation and enter two numbers."""
    code = lang()
    operation = translated_selectbox(
        t("operation"),
        OPERATIONS,
        key="two_op",
        format_func=lambda op: f"{op}  —  {translate(f'op.{op}', code)}",
    )
    is_unary = operation in UNARY_OPERATIONS

    col_a, col_b = st.columns(2)
    number_1 = col_a.number_input(
        t("number") if is_unary else t("first_number"),
        value=0.0,
        step=1.0,
        format="%g",
        key="two_a",
    )
    number_2 = col_b.number_input(
        t("second_number"),
        value=0.0,
        step=1.0,
        format="%g",
        disabled=is_unary,
        help=t("not_used") if is_unary else None,
        key="two_b",
    )

    if st.button(t("calculate"), type="primary", key="two_calc"):
        expression = two_number_expression(number_1, number_2, operation)
        try:
            result = calculate(number_1, number_2, operation)
        except CalculationError as error:
            show_error(error)
        else:
            st.metric(label=expression, value=num(result))
            add_to_history(expression, result)


def render_history():
    """Show past calculations with clear and download options."""
    st.subheader(t("history"))
    history = st.session_state.history
    if not history:
        st.info(t("history.empty"))
        return

    history_df = pd.DataFrame(history).rename(
        columns={
            "Time": t("history.time"),
            "Expression": t("history.expression"),
            "Result": t("history.result"),
        }
    )
    # Show results in the app's language (the browser's own number format may differ);
    # the CSV download keeps the real numbers
    shown = history_df.copy()
    shown[t("history.result")] = [num(value) for value in shown[t("history.result")]]
    st.dataframe(
        shown,
        hide_index=True,
        width="stretch",
        column_config={t("history.result"): st.column_config.TextColumn(alignment="right")},
    )

    col_clear, col_download = st.columns(2)
    if col_clear.button(t("history.clear"), key="history_clear"):
        st.session_state.history = []
        st.rerun()
    # Portuguese spreadsheets expect ";" between columns and "," for decimals
    csv = (
        history_df.to_csv(index=False, sep=";", decimal=",")
        if lang() == "pt"
        else history_df.to_csv(index=False)
    )
    col_download.download_button(
        t("history.download"),
        data=csv.encode("utf-8-sig"),
        file_name=t("history.filename"),
        mime="text/csv",
        key="history_download",
    )


# ---------------------------------------------------------------------------
# Financial calculator
# ---------------------------------------------------------------------------
def render_financial_tab():
    """Switch between the investment and loan calculators."""
    mode = st.segmented_control(
        t("calculator"),
        ["compound", "loan"],
        format_func=option_text("fin."),
        default="compound",
        key="financial_mode",
    )
    if mode == "loan":
        render_loan()
    else:
        render_compound_interest()


def translated_table(rows: list[dict]) -> pd.DataFrame:
    """Year-indexed table with column names in the current language."""
    table = pd.DataFrame(rows).set_index("Year")
    table.index.name = t("year")
    return table.rename(columns={column: t(f"col.{column}") for column in table.columns})


def styled_money_table(table: pd.DataFrame):
    return table.style.format(money)


def render_compound_interest():
    """Compound interest calculator with a growth chart."""
    st.subheader(t("compound.title"))
    st.write(t("compound.intro"))

    col_1, col_2 = st.columns(2)
    principal = col_1.number_input(
        t("initial_amount"), min_value=0.0, value=1000.0, step=100.0, key="invest_principal"
    )
    monthly_contribution = col_2.number_input(
        t("monthly_contribution"), min_value=0.0, value=100.0, step=10.0, key="invest_monthly"
    )
    annual_rate = col_1.number_input(
        t("annual_rate"), min_value=-100.0, value=8.0, step=0.5, key="invest_rate"
    )
    years = col_2.slider(t("years"), min_value=1, max_value=50, value=10, key="invest_years")
    compounding = translated_selectbox(
        t("compounding"),
        COMPOUNDING_OPTIONS,
        key="invest_compounding",
        format_func=option_text("compounding."),
    )

    try:
        rows = compound_interest_schedule(
            principal,
            annual_rate,
            years,
            COMPOUNDING_OPTIONS[compounding],
            monthly_contribution,
        )
    except CalculationError as error:
        show_error(error)
        return

    final = rows[-1]
    m_1, m_2, m_3 = st.columns(3)
    m_1.metric(t("final_balance"), money(final["Balance"]))
    m_2.metric(t("total_contributed"), money(final["Contributed"]))
    m_3.metric(t("interest_earned"), money(final["Interest"]))

    schedule = translated_table(rows)
    st.bar_chart(schedule[[t("col.Contributed"), t("col.Interest")]], stack=True)

    with st.expander(t("year_by_year")):
        st.dataframe(styled_money_table(schedule), width="stretch")


def render_loan():
    """Loan / mortgage calculator with an amortization chart."""
    st.subheader(t("loan.title"))
    st.write(t("loan.intro"))

    col_1, col_2 = st.columns(2)
    principal = col_1.number_input(
        t("loan_amount"), min_value=0.0, value=200_000.0, step=1000.0, key="loan_principal"
    )
    annual_rate = col_2.number_input(
        t("annual_rate"), min_value=0.0, value=6.0, step=0.25, key="loan_rate"
    )
    years = st.slider(t("loan_term"), min_value=1, max_value=40, value=30, key="loan_years")

    try:
        payment = loan_payment(principal, annual_rate, years)
        rows = amortization_schedule(principal, annual_rate, years)
    except CalculationError as error:
        show_error(error)
        return

    total_paid = payment * years * 12
    m_1, m_2, m_3 = st.columns(3)
    m_1.metric(t("monthly_payment"), money(payment))
    m_2.metric(t("total_paid"), money(total_paid))
    m_3.metric(t("total_interest"), money(total_paid - principal))

    schedule = translated_table(rows)
    st.write(t("principal_vs_interest"))
    st.bar_chart(schedule[[t("col.Principal paid"), t("col.Interest paid")]], stack=True)
    st.write(t("remaining_balance"))
    st.area_chart(schedule[t("col.Remaining balance")])

    with st.expander(t("year_by_year")):
        st.dataframe(styled_money_table(schedule), width="stretch")


# ---------------------------------------------------------------------------
# Converter (units and currency)
# ---------------------------------------------------------------------------
def render_converter_tab():
    """Switch between the unit and currency converters."""
    mode = st.segmented_control(
        t("convert"),
        ["units", "currency"],
        format_func=option_text("conv."),
        default="units",
        key="converter_mode",
    )
    if mode == "currency":
        render_currency_converter()
    else:
        render_unit_converter()


def render_unit_converter():
    """Convert a value between units of the same kind."""
    st.subheader(t("units.title"))
    category = translated_selectbox(
        t("unit_type"),
        UNITS,
        key="unit_category",
        format_func=option_text("category."),
    )
    unit_names = list(UNITS[category])

    language = lang()

    def unit_label(unit: str) -> str:
        return translate(f"unit.{unit}", language)

    col_value, col_from, col_to = st.columns([2, 3, 3])
    value = col_value.number_input(t("value"), value=1.0, format="%g", key="unit_value")
    default_from, default_to = DEFAULT_CONVERSIONS.get(category, (unit_names[0], unit_names[-1]))
    from_unit = translated_selectbox(
        t("from"),
        unit_names,
        key=f"from_{category}",
        format_func=unit_label,
        default=default_from,
        container=col_from,
    )
    to_unit = translated_selectbox(
        t("to"),
        unit_names,
        key=f"to_{category}",
        format_func=unit_label,
        default=default_to,
        container=col_to,
    )

    try:
        result = convert_units(value, category, from_unit, to_unit)
    except CalculationError as error:
        show_error(error)
        return

    st.metric(f"{num(value)} {unit_label(from_unit)} =", f"{num(result, 6)} {unit_label(to_unit)}")

    expander_title = t(
        "in_every_unit",
        value=num(value),
        unit=unit_label(from_unit),
        category=t(f"category.{category}").lower(),
    )
    with st.expander(expander_title):
        table = pd.DataFrame(
            {
                t("unit"): [unit_label(unit) for unit in unit_names],
                t("value"): [
                    num(convert_units(value, category, from_unit, unit), 6) for unit in unit_names
                ],
            }
        )
        st.dataframe(table, hide_index=True, width="stretch")


# Exchange rates are cached so the free API is called at most once per hour
@st.cache_data(ttl=3600, show_spinner=False)
def cached_currencies() -> dict[str, str]:
    return get_currencies()


@st.cache_data(ttl=3600, show_spinner=False)
def cached_latest_rate(base: str, target: str) -> tuple[float, str]:
    return get_latest_rate(base, target)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_rate_history(base: str, target: str, days: int) -> list[dict]:
    return get_rate_history(base, target, days)


def _swap_currencies() -> None:
    st.session_state.fx_from, st.session_state.fx_to = (
        st.session_state.fx_to,
        st.session_state.fx_from,
    )
    reset_selectbox("fx_from")
    reset_selectbox("fx_to")


def render_currency_converter():
    """Convert money using the latest European Central Bank rates."""
    st.subheader(t("fx.title"))

    try:
        names = cached_currencies()
    except CurrencyError as error:
        st.warning(t("fx.common_only", message=error_text(error)))
        names = {code: code for code in POPULAR_CURRENCIES}
    codes = sort_currencies(list(names))

    language = lang()

    def label(code: str) -> str:
        name = CURRENCY_NAMES_PT.get(code) if language == "pt" else None
        name = name or names.get(code, code)
        return f"{code} — {name}" if name != code else code

    col_amount, col_from, col_swap, col_to = st.columns([2, 3, 1, 3], vertical_alignment="bottom")
    amount = col_amount.number_input(
        t("amount"), min_value=0.0, value=100.0, step=10.0, key="fx_amount"
    )
    base = translated_selectbox(
        t("from"), codes, key="fx_from", format_func=label, default="USD", container=col_from
    )
    col_swap.button("⇄", on_click=_swap_currencies, help=t("swap"), width="stretch", key="fx_swap")
    target = translated_selectbox(
        t("to"), codes, key="fx_to", format_func=label, default="BRL", container=col_to
    )

    try:
        with st.spinner(t("fx.loading")):
            rate, rate_date = cached_latest_rate(base, target)
    except CurrencyError as error:
        st.error(error_text(error))
        return

    converted = convert_amount(amount, rate)
    inverse = num(1 / rate, 4) if rate else "—"
    st.markdown(
        f'<div class="fx-banner"><div class="small">{money(amount)} {base} =</div>'
        f'<div class="big">{money(converted)} {target}</div>'
        f'<div class="small">1 {base} = {num(rate, 4)} {target} · '
        f"1 {target} = {inverse} {base} · "
        f"{t('fx.rate_from', date=format_date(rate_date, lang()))}</div></div>",
        unsafe_allow_html=True,
    )

    if base == target:
        return

    period = st.segmented_control(
        t("history_period"),
        list(HISTORY_PERIODS),
        format_func=option_text("period."),
        default="3 months",
        key="fx_period",
    )
    period = period or "3 months"
    try:
        history = cached_rate_history(base, target, HISTORY_PERIODS[period])
    except CurrencyError as error:
        st.info(error_text(error))
        return
    if len(history) < 2:
        st.info(t("fx.not_enough"))
        return

    first, last = history[0]["Rate"], history[-1]["Rate"]
    rates = [row["Rate"] for row in history]
    change = localize_number(f"{(last - first) / first * 100:+.2f}", lang())
    m_1, m_2, m_3 = st.columns(3)
    m_1.metric(
        t("fx.rate_now"),
        num(last, 4),
        delta=t("fx.change", change=change, period=t(f"period.{period}")),
    )
    m_2.metric(t("lowest"), num(min(rates), 4))
    m_3.metric(t("highest"), num(max(rates), 4))

    chart_data = pd.DataFrame(history)
    chart_data["Date"] = pd.to_datetime(chart_data["Date"])
    date_format = "%d/%m/%y" if lang() == "pt" else "%b %d"
    chart = (
        alt.Chart(chart_data)
        .mark_line(strokeWidth=3, interpolate="monotone", point=alt.OverlayMarkDef(size=12))
        .encode(
            x=alt.X("Date:T", title=None, axis=alt.Axis(format=date_format)),
            # Zoom in on the actual range instead of starting at zero
            y=alt.Y(
                "Rate:Q",
                title=t("fx.per", target=target, base=base),
                scale=alt.Scale(zero=False),
            ),
            tooltip=[
                alt.Tooltip("Date:T", title=t("date"), format="%d/%m/%Y"),
                alt.Tooltip("Rate:Q", title=t("rate"), format=",.4f"),
            ],
        )
    )
    st.altair_chart(chart, width="stretch")
    st.caption(t("fx.source"))


# ---------------------------------------------------------------------------
# Function plotter
# ---------------------------------------------------------------------------
def render_plotter_tab():
    """Plot one or two formulas of x over a chosen range."""
    st.subheader(t("plot.title"))
    st.write(t("plot.intro"))

    example = st.selectbox(t("plot.example"), FORMULA_EXAMPLES, key="plot_example")
    col_1, col_2 = st.columns(2)
    formula = col_1.text_input("y₁ =", value=example, key=f"formula_{example}")
    compare = col_2.text_input(
        t("plot.compare"),
        value="",
        placeholder=t("plot.compare_placeholder"),
        key="formula_2",
    )

    col_min, col_max = st.columns(2)
    x_min = col_min.number_input(t("x_from"), value=-10.0, step=1.0, format="%g", key="x_min")
    x_max = col_max.number_input(t("x_to"), value=10.0, step=1.0, format="%g", key="x_max")

    try:
        rows = sample_formula(formula, x_min, x_max)
    except CalculationError as error:
        st.error(f"y₁: {error_text(error)}")
        return

    second_rows = None
    if compare.strip():
        try:
            second_rows = sample_formula(compare, x_min, x_max)
        except CalculationError as error:
            st.error(f"y₂: {error_text(error)}")

    points = pd.DataFrame(rows).set_index("x").rename(columns={"y": f"y₁ = {formula}"})
    if second_rows is not None:
        points[f"y₂ = {compare}"] = [row["y"] for row in second_rows]
    st.line_chart(points, x_label="x", y_label="y")

    if any(row["y"] is None for row in rows) or (
        second_rows and any(row["y"] is None for row in second_rows)
    ):
        st.caption(t("plot.gaps"))

    defined = [row["y"] for row in rows if row["y"] is not None]
    if second_rows is None:
        m_1, m_2 = st.columns(2)
        m_1.metric(t("plot.lowest"), num(min(defined), 4))
        m_2.metric(t("plot.highest"), num(max(defined), 4))
        return

    crossings = find_crossings(rows, second_rows)
    m_1, m_2 = st.columns(2)
    m_1.metric(t("plot.crossings"), len(crossings))
    if crossings:
        shown = ", " if lang() == "en" else "; "
        shown = shown.join(f"x ≈ {num(x, 3)}" for x in crossings[:6])
        more = t("plot.more", count=len(crossings) - 6) if len(crossings) > 6 else ""
        m_2.metric(t("plot.where"), shown + more)
    else:
        m_2.metric(t("plot.where"), t("plot.no_cross"))


# ---------------------------------------------------------------------------
# Statistics calculator
# ---------------------------------------------------------------------------
def render_statistics_tab():
    """Descriptive statistics for pasted numbers or a CSV column."""
    st.subheader(t("stats.title"))
    source = st.segmented_control(
        t("data_source"),
        ["type", "csv"],
        format_func=option_text("source."),
        default="type",
        key="stats_source",
    )

    values = get_values(source or "type")
    if values is None:
        return

    try:
        stats = summary_statistics(values)
    except CalculationError as error:
        st.warning(error_text(error))
        return

    cols = st.columns(4)
    for col, key in zip(cols, ["Count", "Mean", "Median", "Std. deviation (sample)"], strict=True):
        label = "Std. deviation" if key == "Std. deviation (sample)" else key
        col.metric(t(f"stat.{label}"), num(stats[key], 4))

    series = pd.Series(values, name="Value")
    quartiles = series.quantile([0.25, 0.5, 0.75])
    stats_table = {
        **stats,
        "Q1 (25%)": quartiles[0.25],
        "Q3 (75%)": quartiles[0.75],
        "IQR": quartiles[0.75] - quartiles[0.25],
    }
    st.dataframe(
        pd.DataFrame(
            {
                t("statistic"): [t(f"stat.{key}") for key in stats_table],
                t("value"): [num(v, 4) for v in stats_table.values()],
            }
        ),
        hide_index=True,
        width="stretch",
    )

    if len(values) > 1:
        st.write(t("distribution"))
        bins = st.slider(t("bins"), 3, 30, max(3, min(10, len(set(values)))), key="stats_bins")
        histogram = pd.cut(series, bins=bins).value_counts(sort=False)
        histogram.index = [
            f"{localize_number(f'{interval.left:,.2f}', lang())} – "
            f"{localize_number(f'{interval.right:,.2f}', lang())}"
            for interval in histogram.index
        ]
        st.bar_chart(histogram, x_label=t("range"), y_label=t("count"))


DECIMAL_COMMA = r"^-?\d{1,3}(\.\d{3})*(,\d+)?$|^-?\d+(,\d+)?$"


def convert_decimal_comma_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Turn text columns like "1.234,56" (Brazilian format) into numbers."""
    for column in data.select_dtypes(exclude="number").columns:
        values = data[column].dropna().astype(str).str.strip()
        if len(values) and values.str.match(DECIMAL_COMMA).all():
            data[column] = pd.to_numeric(
                data[column].astype(str).str.replace(".", "", regex=False).str.replace(",", "."),
                errors="coerce",
            )
    return data


def get_values(source: str) -> list[float] | None:
    """Collect numbers from the chosen data source, or ``None`` if not ready."""
    if source != "csv":
        portuguese = lang() == "pt"
        text = st.text_area(
            t("stats.numbers"),
            value=(
                "12; 15; 18; 22; 22; 25; 30; 41" if portuguese else "12, 15, 18, 22, 22, 25, 30, 41"
            ),
            key=f"stats_text_{lang()}",
        )
        try:
            return parse_numbers(text, decimal_comma=portuguese)
        except CalculationError as error:
            show_error(error)
            return None

    uploaded = st.file_uploader(t("stats.csv_file"), type="csv", key="stats_csv")
    if uploaded is None:
        st.info(t("stats.upload_hint"))
        return None
    try:
        data = pd.read_csv(uploaded, sep=None, engine="python")
    except Exception as error:  # pandas raises several different error types
        st.error(t("stats.csv_error", message=error))
        return None

    data = convert_decimal_comma_columns(data)
    numeric_columns = data.select_dtypes("number").columns.tolist()
    if not numeric_columns:
        st.error(t("stats.no_numeric"))
        return None

    with st.expander(t("stats.preview")):
        st.dataframe(data.head(20), width="stretch")
    column = st.selectbox(t("stats.column"), numeric_columns, key="stats_column")
    return data[column].dropna().tolist()


if __name__ == "__main__":
    main()
