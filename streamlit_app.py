"""
Calculator Loop - Streamlit Application

A web-based multi-tool calculator built with Streamlit. It has five tabs:

- Basic: arithmetic with extra operations and a calculation history
- Financial: compound interest and loan/mortgage calculators with charts
- Converter: length, weight, volume, speed, data and temperature units
- Plotter: graph a formula of x, such as x^2 - 3*x + 2
- Statistics: descriptive statistics for pasted numbers or an uploaded CSV

Author: Ana Condessa
"""

from __future__ import annotations

from datetime import datetime

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
    format_expression,
    format_number,
    loan_payment,
    parse_numbers,
    sample_formula,
    summary_statistics,
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


def format_money(value: float) -> str:
    """Format a currency amount with thousands separators and two decimals."""
    return f"{value:,.2f}"


def main():
    """Render the Streamlit application."""
    st.set_page_config(page_title="Calculator Loop", page_icon="🎈")
    st.title("🎈 Calculator Loop")
    st.caption(
        "Basic math, financial planning, unit conversion, graphs and quick statistics in one place."
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    basic_tab, financial_tab, converter_tab, plotter_tab, stats_tab = st.tabs(
        ["🧮 Basic", "💰 Financial", "📏 Converter", "📈 Plotter", "📊 Statistics"]
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
def render_basic_tab():
    """Arithmetic calculator with a calculation history."""
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
            st.session_state.history.insert(
                0,
                {
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Expression": expression,
                    "Result": result,
                },
            )

    render_history()


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
    mode = st.radio("Calculator", ["Compound interest", "Loan / mortgage"], horizontal=True)
    if mode == "Compound interest":
        render_compound_interest()
    else:
        render_loan()


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
# Unit converter
# ---------------------------------------------------------------------------
def render_converter_tab():
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


# ---------------------------------------------------------------------------
# Function plotter
# ---------------------------------------------------------------------------
def render_plotter_tab():
    """Plot a formula of x over a chosen range."""
    st.subheader("Function plotter")
    st.write(
        "Type a formula using **x**. Supported: `+ - * / ^ %`, brackets, `pi`, `e`, "
        "and the functions `sin cos tan asin acos atan sqrt log log10 exp abs floor ceil`."
    )

    example = st.selectbox("Start from an example", FORMULA_EXAMPLES)
    formula = st.text_input("y =", value=example, key=f"formula_{example}")

    col_min, col_max = st.columns(2)
    x_min = col_min.number_input("x from", value=-10.0, step=1.0, format="%g")
    x_max = col_max.number_input("x to", value=10.0, step=1.0, format="%g")

    try:
        rows = sample_formula(formula, x_min, x_max)
    except CalculationError as error:
        st.error(f"Error: {error}")
        return

    points = pd.DataFrame(rows).set_index("x").rename(columns={"y": f"y = {formula}"})
    st.line_chart(points, x_label="x", y_label="y")

    defined = [row["y"] for row in rows if row["y"] is not None]
    if len(defined) < len(rows):
        st.caption("Gaps in the line are values of x where the function is undefined.")
    m_1, m_2 = st.columns(2)
    m_1.metric("Lowest y in range", format_number(min(defined), 4))
    m_2.metric("Highest y in range", format_number(max(defined), 4))


# ---------------------------------------------------------------------------
# Statistics calculator
# ---------------------------------------------------------------------------
def render_statistics_tab():
    """Descriptive statistics for pasted numbers or a CSV column."""
    st.subheader("Descriptive statistics")
    source = st.radio("Data source", ["Type or paste numbers", "Upload CSV"], horizontal=True)

    values = get_values(source)
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
    if source == "Type or paste numbers":
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
