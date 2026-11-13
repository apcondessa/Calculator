"""
Calculator Loop - Streamlit Application

A web-based multi-tool calculator built with Streamlit. It has five tabs:

- Basic: a keypad calculator for expressions, or two numbers and an
  operation, with a calculation history
- Financial: compound interest and loan/mortgage calculators with charts
- Converter: units (length, weight, temperature...) and live currency rates
- Plotter: graph one or two formulas of x and find where they cross
- Statistics: descriptive statistics for pasted numbers or an uploaded CSV

Author: Ana Condessa
"""

from __future__ import annotations

import html
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

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


def format_money(value: float) -> str:
    """Format a currency amount with thousands separators and two decimals."""
    return f"{value:,.2f}"


def main():
    """Render the Streamlit application."""
    st.set_page_config(page_title="Calculator Loop", page_icon="🎈")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="hero"><h1>🎈 Calculator Loop</h1>'
        "<p>Basic math, money, units &amp; currencies, graphs and statistics, all in one place."
        "</p></div>",
        unsafe_allow_html=True,
    )

    st.session_state.setdefault("history", [])

    basic_tab, financial_tab, converter_tab, plotter_tab, stats_tab = st.tabs(
        ["🧮 Basic", "💰 Financial", "🔄 Converter", "📈 Plotter", "📊 Statistics"]
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
        "Mode",
        ["⌨️ Keypad & expressions", "🔢 Two numbers"],
        default="⌨️ Keypad & expressions",
        key="basic_mode",
    )
    if mode == "🔢 Two numbers":
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
    try:
        result = evaluate_expression(expression)
    except CalculationError as error:
        st.session_state.expr_output = {"expr": expression, "error": str(error)}
        return
    st.session_state.expr_output = {"expr": expression, "result": result}
    add_to_history(expression, result)
    # Continue from the answer, like a pocket calculator
    st.session_state.expr = format_number(result).replace(",", "")


def render_keypad_calculator():
    """Calculator with clickable keys; expressions can also be typed."""
    st.session_state.setdefault("expr", "")
    st.session_state.setdefault("expr_output", None)

    output = st.session_state.expr_output
    if output is None:
        expr_html, result_html = "&nbsp;", '<div class="result">0</div>'
    elif "error" in output:
        expr_html = html.escape(output["expr"])
        result_html = f'<div class="result error">⚠️ {html.escape(output["error"])}</div>'
    else:
        expr_html = html.escape(output["expr"]) + " ="
        result_html = f'<div class="result">{format_number(output["result"])}</div>'
    st.markdown(
        f'<div class="calc-display"><div class="expr">{expr_html}</div>{result_html}</div>',
        unsafe_allow_html=True,
    )

    st.text_input(
        "Expression",
        key="expr",
        placeholder="Type or use the keys, e.g. (3 + 4) × 2^3",
        on_change=_evaluate,
        help="Press Enter or = to calculate. Supports + − × ÷ ^ %, brackets, "
        "pi, e and functions like sqrt(), sin(), log().",
    )

    for row_number, row in enumerate(KEYPAD):
        cols = st.columns(5)
        for col_number, (col, (label, text, group)) in enumerate(zip(cols, row, strict=True)):
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
    st.caption("`%` is the remainder (10 % 3 = 1). Use a dot for decimals: 2.5")


# --- Two-number mode ---------------------------------------------------------
def render_two_number_calculator():
    """Pick an operation and enter two numbers."""
    operation = st.selectbox(
        "Operation",
        options=list(OPERATIONS),
        format_func=lambda op: f"{op}  —  {OPERATIONS[op]}",
    )
    is_unary = operation in UNARY_OPERATIONS

    col_a, col_b = st.columns(2)
    number_1 = col_a.number_input(
        "Number" if is_unary else "First number", value=0.0, step=1.0, format="%g"
    )
    number_2 = col_b.number_input(
        "Second number",
        value=0.0,
        step=1.0,
        format="%g",
        disabled=is_unary,
        help="Not used for this operation." if is_unary else None,
    )

    if st.button("Calculate", type="primary"):
        expression = format_expression(number_1, number_2, operation)
        try:
            result = calculate(number_1, number_2, operation)
        except CalculationError as error:
            st.error(f"Error: {error}")
        else:
            st.metric(label=expression, value=format_number(result))
            add_to_history(expression, result)


def render_history():
    """Show past calculations with clear and download options."""
    st.subheader("🕘 History")
    history = st.session_state.history
    if not history:
        st.info("Your calculations will appear here.")
        return

    history_df = pd.DataFrame(history)
    st.dataframe(
        history_df,
        hide_index=True,
        width="stretch",
        column_config={"Result": st.column_config.NumberColumn(format="localized")},
    )

    col_clear, col_download = st.columns(2)
    if col_clear.button("Clear history"):
        st.session_state.history = []
        st.rerun()
    col_download.download_button(
        "Download as CSV",
        data=history_df.to_csv(index=False).encode("utf-8"),
        file_name="calculator_history.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# Financial calculator
# ---------------------------------------------------------------------------
def render_financial_tab():
    """Switch between the investment and loan calculators."""
    mode = st.segmented_control(
        "Calculator",
        ["📈 Compound interest", "🏠 Loan / mortgage"],
        default="📈 Compound interest",
        key="financial_mode",
    )
    if mode == "🏠 Loan / mortgage":
        render_loan()
    else:
        render_compound_interest()


def render_compound_interest():
    """Compound interest calculator with a growth chart."""
    st.subheader("Compound interest")
    st.write("See how an investment grows over time with regular contributions.")

    col_1, col_2 = st.columns(2)
    principal = col_1.number_input("Initial amount", min_value=0.0, value=1000.0, step=100.0)
    monthly_contribution = col_2.number_input(
        "Monthly contribution", min_value=0.0, value=100.0, step=10.0
    )
    annual_rate = col_1.number_input(
        "Annual interest rate (%)", min_value=-100.0, value=8.0, step=0.5
    )
    years = col_2.slider("Years", min_value=1, max_value=50, value=10, key="invest_years")
    compounding = st.selectbox("Compounding frequency", list(COMPOUNDING_OPTIONS))

    try:
        rows = compound_interest_schedule(
            principal,
            annual_rate,
            years,
            COMPOUNDING_OPTIONS[compounding],
            monthly_contribution,
        )
    except CalculationError as error:
        st.error(f"Error: {error}")
        return

    final = rows[-1]
    m_1, m_2, m_3 = st.columns(3)
    m_1.metric("Final balance", format_money(final["Balance"]))
    m_2.metric("Total contributed", format_money(final["Contributed"]))
    m_3.metric("Interest earned", format_money(final["Interest"]))

    schedule = pd.DataFrame(rows).set_index("Year")
    st.bar_chart(schedule[["Contributed", "Interest"]], stack=True)

    with st.expander("Year-by-year table"):
        st.dataframe(schedule.style.format("{:,.2f}"), width="stretch")


def render_loan():
    """Loan / mortgage calculator with an amortization chart."""
    st.subheader("Loan / mortgage")
    st.write("Find the monthly payment and how much of it goes to interest.")

    col_1, col_2 = st.columns(2)
    principal = col_1.number_input("Loan amount", min_value=0.0, value=200_000.0, step=1000.0)
    annual_rate = col_2.number_input(
        "Annual interest rate (%)", min_value=0.0, value=6.0, step=0.25, key="loan_rate"
    )
    years = st.slider("Loan term (years)", min_value=1, max_value=40, value=30, key="loan_years")

    try:
        payment = loan_payment(principal, annual_rate, years)
        rows = amortization_schedule(principal, annual_rate, years)
    except CalculationError as error:
        st.error(f"Error: {error}")
        return

    total_paid = payment * years * 12
    m_1, m_2, m_3 = st.columns(3)
    m_1.metric("Monthly payment", format_money(payment))
    m_2.metric("Total paid", format_money(total_paid))
    m_3.metric("Total interest", format_money(total_paid - principal))

    schedule = pd.DataFrame(rows).set_index("Year")
    st.write("**Principal vs. interest paid each year**")
    st.bar_chart(schedule[["Principal paid", "Interest paid"]], stack=True)
    st.write("**Remaining balance**")
    st.area_chart(schedule["Remaining balance"])

    with st.expander("Year-by-year table"):
        st.dataframe(schedule.style.format("{:,.2f}"), width="stretch")


# ---------------------------------------------------------------------------
# Converter (units and currency)
# ---------------------------------------------------------------------------
def render_converter_tab():
    """Switch between the unit and currency converters."""
    mode = st.segmented_control(
        "Convert",
        ["📏 Units", "💱 Currency (live rates)"],
        default="📏 Units",
        key="converter_mode",
    )
    if mode == "💱 Currency (live rates)":
        render_currency_converter()
    else:
        render_unit_converter()


def render_unit_converter():
    """Convert a value between units of the same kind."""
    st.subheader("Unit converter")
    category = st.selectbox("Type of unit", list(UNITS))
    unit_names = list(UNITS[category])

    col_value, col_from, col_to = st.columns([2, 3, 3])
    value = col_value.number_input("Value", value=1.0, format="%g")
    default_from, default_to = DEFAULT_CONVERSIONS.get(category, (unit_names[0], unit_names[-1]))
    from_unit = col_from.selectbox(
        "From", unit_names, index=unit_names.index(default_from), key=f"from_{category}"
    )
    to_unit = col_to.selectbox(
        "To", unit_names, index=unit_names.index(default_to), key=f"to_{category}"
    )

    try:
        result = convert_units(value, category, from_unit, to_unit)
    except CalculationError as error:
        st.error(f"Error: {error}")
        return

    st.metric(
        f"{format_number(value)} {from_unit} =",
        f"{format_number(result, 6)} {to_unit}",
    )

    with st.expander(f"{format_number(value)} {from_unit} in every {category.lower()} unit"):
        table = pd.DataFrame(
            {
                "Unit": unit_names,
                "Value": [
                    format_number(convert_units(value, category, from_unit, unit), 6)
                    for unit in unit_names
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


def render_currency_converter():
    """Convert money using the latest European Central Bank rates."""
    st.subheader("Currency converter")

    try:
        names = cached_currencies()
    except CurrencyError as error:
        st.warning(f"{error} Showing the most common currencies only.")
        names = {code: code for code in POPULAR_CURRENCIES}
    codes = sort_currencies(list(names))
    st.session_state.setdefault("fx_from", "USD" if "USD" in codes else codes[0])
    st.session_state.setdefault("fx_to", "BRL" if "BRL" in codes else codes[-1])

    def label(code: str) -> str:
        return f"{code} — {names[code]}" if names.get(code, code) != code else code

    col_amount, col_from, col_swap, col_to = st.columns([2, 3, 1, 3], vertical_alignment="bottom")
    amount = col_amount.number_input("Amount", min_value=0.0, value=100.0, step=10.0)
    base = col_from.selectbox("From", codes, format_func=label, key="fx_from")
    col_swap.button("⇄", on_click=_swap_currencies, help="Swap currencies", width="stretch")
    target = col_to.selectbox("To", codes, format_func=label, key="fx_to")

    try:
        with st.spinner("Loading the latest rate…"):
            rate, rate_date = cached_latest_rate(base, target)
    except CurrencyError as error:
        st.error(str(error))
        return

    converted = convert_amount(amount, rate)
    st.markdown(
        f'<div class="fx-banner"><div class="small">{format_money(amount)} {base} =</div>'
        f'<div class="big">{format_money(converted)} {target}</div>'
        f'<div class="small">1 {base} = {format_number(rate, 4)} {target} · '
        f"1 {target} = {format_number(1 / rate, 4) if rate else '—'} {base} · "
        f"rate from {rate_date}</div></div>",
        unsafe_allow_html=True,
    )

    if base == target:
        return

    period = st.segmented_control(
        "History", list(HISTORY_PERIODS), default="3 months", key="fx_period"
    )
    try:
        history = cached_rate_history(base, target, HISTORY_PERIODS[period or "3 months"])
    except CurrencyError as error:
        st.info(str(error))
        return
    if len(history) < 2:
        st.info("Not enough history available for this pair.")
        return

    first, last = history[0]["Rate"], history[-1]["Rate"]
    rates = [row["Rate"] for row in history]
    m_1, m_2, m_3 = st.columns(3)
    m_1.metric(
        "Rate now",
        format_number(last, 4),
        delta=f"{(last - first) / first * 100:+.2f}% in {period}",
    )
    m_2.metric("Lowest", format_number(min(rates), 4))
    m_3.metric("Highest", format_number(max(rates), 4))

    chart_data = pd.DataFrame(history)
    chart_data["Date"] = pd.to_datetime(chart_data["Date"])
    chart = (
        alt.Chart(chart_data)
        .mark_line(strokeWidth=3, interpolate="monotone", point=alt.OverlayMarkDef(size=12))
        .encode(
            x=alt.X("Date:T", title=None),
            # Zoom in on the actual range instead of starting at zero
            y=alt.Y("Rate:Q", title=f"{target} per 1 {base}", scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip("Date:T"), alt.Tooltip("Rate:Q", format=",.4f")],
        )
    )
    st.altair_chart(chart, width="stretch")
    st.caption(
        "Rates: European Central Bank reference rates via frankfurter.dev, "
        "updated once per working day. For information only."
    )


# ---------------------------------------------------------------------------
# Function plotter
# ---------------------------------------------------------------------------
def render_plotter_tab():
    """Plot one or two formulas of x over a chosen range."""
    st.subheader("Function plotter")
    st.write(
        "Type a formula using **x**. Supported: `+ - * / ^ %`, brackets, `pi`, `e`, "
        "and the functions `sin cos tan asin acos atan sqrt log log10 exp abs floor ceil`."
    )

    example = st.selectbox("Start from an example", FORMULA_EXAMPLES)
    col_1, col_2 = st.columns(2)
    formula = col_1.text_input("y₁ =", value=example, key=f"formula_{example}")
    compare = col_2.text_input(
        "y₂ = (optional, to compare)", value="", placeholder="e.g. 2*x + 1", key="formula_2"
    )

    col_min, col_max = st.columns(2)
    x_min = col_min.number_input("x from", value=-10.0, step=1.0, format="%g")
    x_max = col_max.number_input("x to", value=10.0, step=1.0, format="%g")

    try:
        rows = sample_formula(formula, x_min, x_max)
    except CalculationError as error:
        st.error(f"y₁: {error}")
        return

    second_rows = None
    if compare.strip():
        try:
            second_rows = sample_formula(compare, x_min, x_max)
        except CalculationError as error:
            st.error(f"y₂: {error}")

    points = pd.DataFrame(rows).set_index("x").rename(columns={"y": f"y₁ = {formula}"})
    if second_rows is not None:
        points[f"y₂ = {compare}"] = [row["y"] for row in second_rows]
    st.line_chart(points, x_label="x", y_label="y")

    if any(row["y"] is None for row in rows) or (
        second_rows and any(row["y"] is None for row in second_rows)
    ):
        st.caption("Gaps in a line are values of x where that function is undefined.")

    defined = [row["y"] for row in rows if row["y"] is not None]
    if second_rows is None:
        m_1, m_2 = st.columns(2)
        m_1.metric("Lowest y in range", format_number(min(defined), 4))
        m_2.metric("Highest y in range", format_number(max(defined), 4))
        return

    crossings = find_crossings(rows, second_rows)
    m_1, m_2 = st.columns(2)
    m_1.metric("Crossing points", len(crossings))
    if crossings:
        shown = ", ".join(f"x ≈ {format_number(x, 3)}" for x in crossings[:6])
        more = f" (+{len(crossings) - 6} more)" if len(crossings) > 6 else ""
        m_2.metric("Where the curves meet", shown + more)
    else:
        m_2.metric("Where the curves meet", "They don't cross here")


# ---------------------------------------------------------------------------
# Statistics calculator
# ---------------------------------------------------------------------------
def render_statistics_tab():
    """Descriptive statistics for pasted numbers or a CSV column."""
    st.subheader("Descriptive statistics")
    source = st.segmented_control(
        "Data source",
        ["✍️ Type or paste numbers", "📁 Upload CSV"],
        default="✍️ Type or paste numbers",
        key="stats_source",
    )

    values = get_values(source or "✍️ Type or paste numbers")
    if values is None:
        return

    try:
        stats = summary_statistics(values)
    except CalculationError as error:
        st.warning(error)
        return

    cols = st.columns(4)
    for col, key in zip(cols, ["Count", "Mean", "Median", "Std. deviation (sample)"], strict=True):
        col.metric(key.replace(" (sample)", ""), format_number(stats[key], 4))

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
                "Statistic": stats_table.keys(),
                "Value": [format_number(v, 4) for v in stats_table.values()],
            }
        ),
        hide_index=True,
        width="stretch",
    )

    if len(values) > 1:
        st.write("**Distribution**")
        bins = st.slider("Number of bins", 3, 30, max(3, min(10, len(set(values)))))
        histogram = pd.cut(series, bins=bins).value_counts(sort=False)
        histogram.index = [
            f"{interval.left:,.2f} – {interval.right:,.2f}" for interval in histogram.index
        ]
        st.bar_chart(histogram, x_label="Range", y_label="Count")


def get_values(source: str) -> list[float] | None:
    """Collect numbers from the chosen data source, or ``None`` if not ready."""
    if source != "📁 Upload CSV":
        text = st.text_area(
            "Numbers (separated by commas, spaces or new lines)",
            value="12, 15, 18, 22, 22, 25, 30, 41",
        )
        try:
            return parse_numbers(text)
        except CalculationError as error:
            st.error(f"Error: {error}")
            return None

    uploaded = st.file_uploader("CSV file", type="csv")
    if uploaded is None:
        st.info("Upload a CSV file to analyze one of its numeric columns.")
        return None
    try:
        data = pd.read_csv(uploaded)
    except Exception as error:  # pandas raises several different error types
        st.error(f"Could not read the CSV file: {error}")
        return None

    numeric_columns = data.select_dtypes("number").columns.tolist()
    if not numeric_columns:
        st.error("The file has no numeric columns.")
        return None

    with st.expander("Preview data"):
        st.dataframe(data.head(20), width="stretch")
    column = st.selectbox("Column to analyze", numeric_columns)
    return data[column].dropna().tolist()


if __name__ == "__main__":
    main()
