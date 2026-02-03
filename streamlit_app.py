import streamlit as st

st.title("🎈Calculator Loomp")
"""
Calculator Loop - Streamlit Application

A simple web-based calculator built with Streamlit that performs basic arithmetic operations (addition, subtraction, multiplication, and division) using an interactive user interface.

Author: Ana Condessa
"""

import streamlit as st


def main():
    """Main function that renders the Streamlit application."""

    # Page title and description
    st.title("🎈 Calculator Loop")
    st.write(
        "Enter two numbers, select an operation, and click **Calculate** "
        "to view the result."
    )

    # Numeric inputs
    number_1 = st.number_input(
        "First number",
        value=0.0,
        step=1.0
    )
    number_2 = st.number_input(
        "Second number",
        value=0.0,
        step=1.0
    )

    # Operation selector
    operation = st.selectbox(
        "Select an operation",
        options=["+", "-", "*", "/"]
    )

    # Calculate button
    if st.button("Calculate"):
        calculate(number_1, number_2, operation)


def calculate(number_1: float, number_2: float, operation: str):
    """
    Performs the selected arithmetic operation and displays the result.

    Args:
        number_1 (float): First number
        number_2 (float): Second number
        operation (str): Arithmetic operator
    """

    if operation == "+":
        result = number_1 + number_2
        st.success(f"Result: {result}")

    elif operation == "-":
        result = number_1 - number_2
        st.success(f"Result: {result}")

    elif operation == "*":
        result = number_1 * number_2
        st.success(f"Result: {result}")

    elif operation == "/":
        if number_2 == 0:
            st.error("Error: Division by zero is not allowed.")
        else:
            result = number_1 / number_2
            st.success(f"Result: {result}")


if __name__ == "__main__":
    main()
