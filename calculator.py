"""
Pure calculation logic for Calculator Loop.

Kept separate from the Streamlit UI so the math can be reused and tested
on its own.
"""

from __future__ import annotations

import math
from statistics import mean, median, pstdev, stdev

# Operations that use both numbers
BINARY_OPERATIONS = {
    "+": "Addition",
    "-": "Subtraction",
    "×": "Multiplication",
    "÷": "Division",
    "^": "Power",
    "mod": "Modulo (remainder)",
    "% of": "Percentage (A% of B)",
}

# Operations that use only the first number
UNARY_OPERATIONS = {
    "√": "Square root",
}

OPERATIONS = {**BINARY_OPERATIONS, **UNARY_OPERATIONS}


class CalculationError(ValueError):
    """Raised when an operation cannot be performed (e.g. division by zero)."""


def calculate(a: float, b: float, operation: str) -> float:
    """Apply ``operation`` to ``a`` and ``b`` and return the result."""
    if operation == "+":
        return a + b
    if operation == "-":
        return a - b
    if operation == "×":
        return a * b
    if operation == "÷":
        if b == 0:
            raise CalculationError("Division by zero is not allowed.")
        return a / b
    if operation == "^":
        try:
            result = a ** b
        except (OverflowError, ZeroDivisionError) as exc:
            raise CalculationError(f"Cannot compute {a} ^ {b}.") from exc
        if isinstance(result, complex):
            raise CalculationError(
                "A negative number raised to a fractional power has no real result."
            )
        return result
    if operation == "mod":
        if b == 0:
            raise CalculationError("Modulo by zero is not allowed.")
        return a % b
    if operation == "% of":
        return a / 100 * b
    if operation == "√":
        if a < 0:
            raise CalculationError("Cannot take the square root of a negative number.")
        return math.sqrt(a)
    raise CalculationError(f"Unknown operation: {operation}")


def format_expression(a: float, b: float, operation: str) -> str:
    """Return a human-readable expression such as ``'3 + 4'``."""
    if operation in UNARY_OPERATIONS:
        return f"√{format_number(a)}"
    if operation == "% of":
        return f"{format_number(a)}% of {format_number(b)}"
    return f"{format_number(a)} {operation} {format_number(b)}"


def format_number(value: float, decimals: int = 10) -> str:
    """Format a number without trailing zeros, using thousands separators."""
    if math.isinf(value) or math.isnan(value):
        return str(value)
    rounded = round(value, decimals)
    if rounded == int(rounded) and abs(rounded) < 1e15:
        return f"{int(rounded):,}"
    return f"{rounded:,.{decimals}f}".rstrip("0").rstrip(".")


def compound_interest_schedule(
    principal: float,
    annual_rate_pct: float,
    years: int,
    compounds_per_year: int = 12,
    monthly_contribution: float = 0.0,
) -> list[dict]:
    """
    Simulate an investment month by month and return one row per year.

    Each row contains the year, the total contributed so far (principal plus
    contributions), the interest earned so far and the ending balance.
    """
    if years < 0 or principal < 0 or monthly_contribution < 0:
        raise CalculationError("Principal, years and contributions must not be negative.")
    if compounds_per_year <= 0:
        raise CalculationError("Compounding frequency must be positive.")

    # Effective monthly rate equivalent to the chosen compounding frequency
    annual = annual_rate_pct / 100
    monthly_rate = (1 + annual / compounds_per_year) ** (compounds_per_year / 12) - 1

    balance = principal
    contributed = principal
    rows = [{"Year": 0, "Contributed": principal, "Interest": 0.0, "Balance": principal}]
    for year in range(1, years + 1):
        for _ in range(12):
            balance = balance * (1 + monthly_rate) + monthly_contribution
            contributed += monthly_contribution
        rows.append(
            {
                "Year": year,
                "Contributed": contributed,
                "Interest": balance - contributed,
                "Balance": balance,
            }
        )
    return rows


def parse_numbers(text: str) -> list[float]:
    """Parse numbers separated by commas, semicolons, spaces or new lines."""
    tokens = text.replace(";", " ").replace(",", " ").split()
    numbers = []
    for token in tokens:
        try:
            numbers.append(float(token))
        except ValueError as exc:
            raise CalculationError(f"'{token}' is not a valid number.") from exc
    return numbers


def summary_statistics(values: list[float]) -> dict[str, float]:
    """Return common descriptive statistics for a list of numbers."""
    if not values:
        raise CalculationError("Enter at least one number.")
    ordered = sorted(values)
    return {
        "Count": len(values),
        "Sum": sum(values),
        "Mean": mean(values),
        "Median": median(values),
        "Std. deviation (sample)": stdev(values) if len(values) > 1 else 0.0,
        "Std. deviation (population)": pstdev(values),
        "Min": ordered[0],
        "Max": ordered[-1],
        "Range": ordered[-1] - ordered[0],
    }
