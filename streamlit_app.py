"""
Calculator Loop - Streamlit Application

A web-based multi-tool calculator built with Streamlit. It has three tabs:

- Basic: arithmetic with extra operations and a calculation history
- Financial: compound interest with monthly contributions and a growth chart
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
    CalculationError,
    calculate,
    compound_interest_schedule,
    format_expression,
    format_number,
    parse_numbers,
    summary_statistics,
)

COMPOUNDING_OPTIONS = {
    "Monthly": 12,
    "Quarterly": 4,
    "Semi-annually": 2,
    "Annually": 1,
    "Daily": 365,
}


def main():
    """Render the Streamlit application."""
    st.set_page_config(page_title="Calculator Loop", page_icon="🎈")
    st.title("🎈 Calculator Loop")
    st.caption("Basic math, financial planning and quick statistics in one place.")

    if "history" not in st.session_state:
        st.session_state.history = []

    basic_tab, financial_tab, stats_tab = st.tabs(
        ["🧮 Basic", "💰 Financial", "📊 Statistics"]
    )
    with basic_tab:
        render_basic_tab()
    with financial_tab:
        render_financial_tab()
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
    st.dataframe(history_df, hide_index=True, width="stretch")

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
    """Compound interest calculator with a growth chart."""
    st.subheader("Compound interest")
    st.write("See how an investment grows over time with regular contributions.")

    col_1, col_2 = st.columns(2)
    principal = col_1.number_input(
        "Initial amount", min_value=0.0, value=1000.0, step=100.0
    )
    monthly_contribution = col_2.number_input(
        "Monthly contribution", min_value=0.0, value=100.0, step=10.0
    )
    annual_rate = col_1.number_input(
        "Annual interest rate (%)", min_value=-100.0, value=8.0, step=0.5
    )
    years = col_2.slider("Years", min_value=1, max_value=50, value=10)
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
    m_1.metric("Final balance", format_number(final["Balance"], 2))
    m_2.metric("Total contributed", format_number(final["Contributed"], 2))
    m_3.metric("Interest earned", format_number(final["Interest"], 2))

    schedule = pd.DataFrame(rows).set_index("Year")
    st.bar_chart(schedule[["Contributed", "Interest"]], stack=True)

    with st.expander("Year-by-year table"):
        st.dataframe(
            schedule.style.format("{:,.2f}"), width="stretch"
        )


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
    for col, key in zip(cols, ["Count", "Mean", "Median", "Std. deviation (sample)"]):
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
            {"Statistic": stats_table.keys(),
             "Value": [format_number(v, 4) for v in stats_table.values()]}
        ),
        hide_index=True,
        width="stretch",
    )

    if len(values) > 1:
        st.write("**Distribution**")
        bins = st.slider("Number of bins", 3, 30, max(3, min(10, len(set(values)))))
        histogram = pd.cut(series, bins=bins).value_counts(sort=False)
        histogram.index = [f"{interval.left:,.2f} – {interval.right:,.2f}" for interval in histogram.index]
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
