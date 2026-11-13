"""Unit tests for the calculation logic in calculator.py."""

import math

import pytest

from calculator import (
    CalculationError,
    amortization_schedule,
    calculate,
    compile_formula,
    compound_interest_schedule,
    convert_units,
    evaluate_formula,
    format_expression,
    format_number,
    loan_payment,
    parse_numbers,
    sample_formula,
    summary_statistics,
)


# --- Basic operations -------------------------------------------------------
@pytest.mark.parametrize(
    ("a", "b", "operation", "expected"),
    [
        (2, 3, "+", 5),
        (2, 3, "-", -1),
        (2, 3, "×", 6),
        (7, 2, "÷", 3.5),
        (2, 10, "^", 1024),
        (7, 3, "mod", 1),
        (20, 50, "% of", 10),
        (9, 0, "√", 3),
    ],
)
def test_calculate(a, b, operation, expected):
    assert calculate(a, b, operation) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("a", "b", "operation"),
    [
        (1, 0, "÷"),
        (1, 0, "mod"),
        (-4, 0, "√"),
        (-8, 0.5, "^"),
        (10, 1e6, "^"),
        (1, 1, "unknown"),
    ],
)
def test_calculate_errors(a, b, operation):
    with pytest.raises(CalculationError):
        calculate(a, b, operation)


def test_format_expression():
    assert format_expression(3, 4, "+") == "3 + 4"
    assert format_expression(20, 50, "% of") == "20% of 50"
    assert format_expression(9, 0, "√") == "√9"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1234567, "1,234,567"),
        (1234567.5, "1,234,567.5"),
        (0.1 + 0.2, "0.3"),
        (-2.0, "-2"),
        (math.inf, "inf"),
    ],
)
def test_format_number(value, expected):
    assert format_number(value) == expected


# --- Financial --------------------------------------------------------------
def test_compound_interest_matches_formula():
    rows = compound_interest_schedule(1000, 12, 1, compounds_per_year=12)
    assert rows[-1]["Balance"] == pytest.approx(1000 * (1 + 0.12 / 12) ** 12)


def test_compound_interest_with_contributions():
    rows = compound_interest_schedule(1000, 8, 10, 12, 100)
    assert len(rows) == 11
    assert rows[-1]["Contributed"] == pytest.approx(13_000)
    assert rows[-1]["Balance"] == pytest.approx(20_514.24, abs=0.01)


def test_compound_interest_zero_rate():
    rows = compound_interest_schedule(500, 0, 2, 12, 10)
    assert rows[-1]["Balance"] == pytest.approx(740)
    assert rows[-1]["Interest"] == pytest.approx(0)


def test_compound_interest_rejects_negative_values():
    with pytest.raises(CalculationError):
        compound_interest_schedule(-1, 5, 1)


def test_loan_payment():
    # Standard 30-year mortgage example
    assert loan_payment(200_000, 6, 30) == pytest.approx(1199.10, abs=0.01)
    assert loan_payment(1200, 0, 1) == pytest.approx(100)


def test_amortization_pays_off_loan():
    rows = amortization_schedule(200_000, 6, 30)
    assert len(rows) == 30
    assert rows[-1]["Remaining balance"] == pytest.approx(0, abs=1e-6)
    assert sum(r["Principal paid"] for r in rows) == pytest.approx(200_000)


@pytest.mark.parametrize(("principal", "rate", "years"), [(1000, 5, 0), (-1, 5, 1), (1000, -1, 1)])
def test_loan_errors(principal, rate, years):
    with pytest.raises(CalculationError):
        loan_payment(principal, rate, years)


# --- Unit conversion --------------------------------------------------------
@pytest.mark.parametrize(
    ("value", "category", "from_unit", "to_unit", "expected"),
    [
        (1, "Length", "Mile", "Kilometer", 1.609344),
        (12, "Length", "Inch", "Foot", 1),
        (1, "Weight", "Kilogram", "Pound", 2.20462262),
        (1, "Volume", "Gallon (US)", "Liter", 3.785411784),
        (100, "Speed", "Kilometers per hour", "Meters per second", 27.7777778),
        (1, "Data", "Gigabyte", "Megabyte", 1000),
        (100, "Temperature", "Celsius", "Fahrenheit", 212),
        (32, "Temperature", "Fahrenheit", "Kelvin", 273.15),
        (5, "Length", "Meter", "Meter", 5),
    ],
)
def test_convert_units(value, category, from_unit, to_unit, expected):
    assert convert_units(value, category, from_unit, to_unit) == pytest.approx(expected)


def test_convert_units_errors():
    with pytest.raises(CalculationError):
        convert_units(-300, "Temperature", "Celsius", "Kelvin")
    with pytest.raises(CalculationError):
        convert_units(1, "Length", "Meter", "Pound")
    with pytest.raises(CalculationError):
        convert_units(1, "Time", "Second", "Minute")


# --- Formulas ---------------------------------------------------------------
@pytest.mark.parametrize(
    ("formula", "x", "expected"),
    [
        ("x^2 - 3*x + 2", 3, 2),
        ("2*x + 1", -1, -1),
        ("sin(pi/2)", 0, 1),
        ("sqrt(x) + abs(-x)", 4, 6),
        ("e^x", 1, math.e),
        ("-x % 3", 1, 2),
    ],
)
def test_evaluate_formula(formula, x, expected):
    assert evaluate_formula(compile_formula(formula), x) == pytest.approx(expected)


@pytest.mark.parametrize(
    "formula",
    [
        "",
        "x +",
        '__import__("os").system("ls")',
        "open('file')",
        "x.real",
        "y * 2",
        "sin + 1",
        "sin(x, 2)",
        "[1, 2]",
        "lambda: 1",
    ],
)
def test_compile_formula_rejects_unsafe_or_invalid(formula):
    with pytest.raises(CalculationError):
        compile_formula(formula)


def test_sample_formula_marks_undefined_points():
    rows = sample_formula("sqrt(x)", -1, 1, points=3)
    assert [r["y"] for r in rows] == [None, 0, 1]


def test_sample_formula_handles_huge_powers_quickly():
    with pytest.raises(CalculationError):
        sample_formula("9^9^9 + x", 0, 1, points=2)


def test_sample_formula_range_error():
    with pytest.raises(CalculationError):
        sample_formula("x", 1, 1)


# --- Statistics -------------------------------------------------------------
def test_parse_numbers():
    assert parse_numbers("1, 2;3\n4  5.5") == [1, 2, 3, 4, 5.5]
    with pytest.raises(CalculationError):
        parse_numbers("1, two, 3")


def test_summary_statistics():
    stats = summary_statistics([2, 4, 4, 4, 5, 5, 7, 9])
    assert stats["Count"] == 8
    assert stats["Mean"] == pytest.approx(5)
    assert stats["Median"] == pytest.approx(4.5)
    assert stats["Std. deviation (population)"] == pytest.approx(2)
    assert stats["Range"] == 7


def test_summary_statistics_single_value_and_empty():
    assert summary_statistics([3])["Std. deviation (sample)"] == 0
    with pytest.raises(CalculationError):
        summary_statistics([])
