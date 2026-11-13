"""
Pure calculation logic for Calculator Loop.

Kept separate from the Streamlit UI so the math can be reused and tested
on its own.
"""

from __future__ import annotations

import ast
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
    """
    Raised when an operation cannot be performed (e.g. division by zero).

    The message is kept as a template plus values, so the app can show it in
    another language; ``str(error)`` gives the English text.
    """

    def __init__(self, template: str, **params):
        self.template = template
        self.params = params
        super().__init__(template.format(**params))


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
            result = a**b
        except (OverflowError, ZeroDivisionError) as exc:
            raise CalculationError("Cannot compute {a} ^ {b}.", a=a, b=b) from exc
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
    raise CalculationError("Unknown operation: {operation}", operation=operation)


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


def parse_numbers(text: str, decimal_comma: bool = False) -> list[float]:
    """
    Parse numbers separated by commas, semicolons, spaces or new lines.

    With ``decimal_comma=True`` (Portuguese style) the comma is the decimal
    separator, so numbers are separated by semicolons, spaces or new lines.
    """
    if decimal_comma:
        tokens = [token.replace(",", ".") for token in text.replace(";", " ").split()]
    else:
        tokens = text.replace(";", " ").replace(",", " ").split()
    numbers = []
    for token in tokens:
        try:
            numbers.append(float(token))
        except ValueError as exc:
            raise CalculationError("'{token}' is not a valid number.", token=token) from exc
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


# ---------------------------------------------------------------------------
# Loans
# ---------------------------------------------------------------------------
def loan_payment(principal: float, annual_rate_pct: float, years: int) -> float:
    """Return the fixed monthly payment for an amortizing loan."""
    if principal < 0 or years <= 0:
        raise CalculationError("Loan amount must not be negative and years must be positive.")
    if annual_rate_pct < 0:
        raise CalculationError("Interest rate must not be negative.")
    months = years * 12
    monthly_rate = annual_rate_pct / 100 / 12
    if monthly_rate == 0:
        return principal / months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def amortization_schedule(principal: float, annual_rate_pct: float, years: int) -> list[dict]:
    """Return one row per year with the principal and interest paid and the balance left."""
    payment = loan_payment(principal, annual_rate_pct, years)
    monthly_rate = annual_rate_pct / 100 / 12
    balance = principal
    rows = []
    for year in range(1, years + 1):
        principal_paid = interest_paid = 0.0
        for _ in range(12):
            interest = balance * monthly_rate
            interest_paid += interest
            principal_paid += payment - interest
            balance -= payment - interest
        rows.append(
            {
                "Year": year,
                "Principal paid": principal_paid,
                "Interest paid": interest_paid,
                "Remaining balance": max(balance, 0.0),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------------------------
# Each unit's factor converts it to the category's base unit
UNITS = {
    "Length": {
        "Millimeter": 0.001,
        "Centimeter": 0.01,
        "Meter": 1.0,
        "Kilometer": 1000.0,
        "Inch": 0.0254,
        "Foot": 0.3048,
        "Yard": 0.9144,
        "Mile": 1609.344,
    },
    "Weight": {
        "Milligram": 0.001,
        "Gram": 1.0,
        "Kilogram": 1000.0,
        "Tonne": 1_000_000.0,
        "Ounce": 28.349523125,
        "Pound": 453.59237,
    },
    "Volume": {
        "Milliliter": 0.001,
        "Liter": 1.0,
        "Cubic meter": 1000.0,
        "Teaspoon (US)": 0.00492892159375,
        "Tablespoon (US)": 0.01478676478125,
        "Cup (US)": 0.2365882365,
        "Gallon (US)": 3.785411784,
    },
    "Speed": {
        "Meters per second": 1.0,
        "Kilometers per hour": 1 / 3.6,
        "Miles per hour": 0.44704,
        "Knot": 1852 / 3600,
    },
    "Data": {
        "Byte": 1.0,
        "Kilobyte": 1e3,
        "Megabyte": 1e6,
        "Gigabyte": 1e9,
        "Terabyte": 1e12,
    },
    "Temperature": {"Celsius": None, "Fahrenheit": None, "Kelvin": None},
}


def _to_celsius(value: float, unit: str) -> float:
    if unit == "Celsius":
        return value
    if unit == "Fahrenheit":
        return (value - 32) * 5 / 9
    if unit == "Kelvin":
        return value - 273.15
    raise CalculationError("Unknown temperature unit: {unit}", unit=unit)


def _from_celsius(value: float, unit: str) -> float:
    if unit == "Celsius":
        return value
    if unit == "Fahrenheit":
        return value * 9 / 5 + 32
    if unit == "Kelvin":
        return value + 273.15
    raise CalculationError("Unknown temperature unit: {unit}", unit=unit)


def convert_units(value: float, category: str, from_unit: str, to_unit: str) -> float:
    """Convert ``value`` between two units of the same category."""
    if category not in UNITS:
        raise CalculationError("Unknown category: {category}", category=category)
    units = UNITS[category]
    if from_unit not in units or to_unit not in units:
        raise CalculationError("Unknown unit for {category}.", category=category)
    if category == "Temperature":
        celsius = _to_celsius(value, from_unit)
        if celsius < -273.15:
            raise CalculationError("Temperature cannot be below absolute zero.")
        return _from_celsius(celsius, to_unit)
    return value * units[from_unit] / units[to_unit]


# ---------------------------------------------------------------------------
# Safe formula evaluation (used by the function plotter)
# ---------------------------------------------------------------------------
_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
}
_CONSTANTS = {"pi": math.pi, "e": math.e}
_BIN_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a**b,
    ast.Mod: lambda a, b: a % b,
}
_UNARY_OPS = {ast.UAdd: lambda a: a, ast.USub: lambda a: -a}


def compile_formula(formula: str, allow_x: bool = True) -> ast.Expression:
    """
    Parse a formula such as ``"x^2 - 3*x + 2"`` and check that it only uses
    numbers, ``x``, arithmetic, the constants ``pi``/``e`` and the allowed
    math functions. Never uses ``eval``, so arbitrary code cannot run.

    With ``allow_x=False`` the variable ``x`` is rejected, which is used for
    plain expressions such as ``"(3 + 4) * 2^3"``.
    """
    if not formula.strip():
        raise CalculationError("Enter a formula.")
    # Accept the symbols people type on calculators as well as Python operators
    normalized = formula.replace("^", "**").replace("×", "*").replace("÷", "/")
    try:
        tree = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:
        raise CalculationError("The formula is not valid.") from exc

    # Function names are only valid as the target of a call, e.g. sin(x)
    call_targets = {id(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expression, ast.Load, ast.BinOp, ast.UnaryOp)):
            continue
        if isinstance(node, tuple(_BIN_OPS) + tuple(_UNARY_OPS)):
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            continue
        if isinstance(node, ast.Name) and ((node.id == "x" and allow_x) or node.id in _CONSTANTS):
            continue
        if isinstance(node, ast.Name) and node.id in _FUNCTIONS and id(node) in call_targets:
            continue  # validated as part of the Call below
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCTIONS
            and len(node.args) == 1
            and not node.keywords
        ):
            continue
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _FUNCTIONS:
                raise CalculationError("{name}() takes exactly one argument.", name=node.func.id)
            raise CalculationError("Unknown function '{name}'.", name=node.func.id)
        if isinstance(node, ast.Name):
            if node.id in _FUNCTIONS:
                raise CalculationError("Use {name}(...) with brackets.", name=node.id)
            if allow_x:
                raise CalculationError(
                    "Unknown name '{name}'. Use x as the variable.", name=node.id
                )
            raise CalculationError(
                "Unknown name '{name}'. Only numbers are allowed here.", name=node.id
            )
        if isinstance(node, ast.Tuple):
            raise CalculationError("Use a dot for decimals (2.5), not a comma (2,5).")
        raise CalculationError("The formula contains something that is not allowed.")
    return tree


def evaluate_formula(tree: ast.Expression, x: float) -> float:
    """Evaluate a formula from :func:`compile_formula` at a given ``x``."""

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            # Floats overflow quickly instead of building gigantic integers
            return float(node.value)
        if isinstance(node, ast.Name):
            return x if node.id == "x" else _CONSTANTS[node.id]
        if isinstance(node, ast.BinOp):
            return _BIN_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return _UNARY_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Call):
            return _FUNCTIONS[node.func.id](_eval(node.args[0]))
        raise CalculationError("Unsupported formula.")

    result = _eval(tree)
    if isinstance(result, complex):
        raise ValueError("complex result")
    return float(result)


def evaluate_expression(expression: str) -> float:
    """
    Evaluate a plain math expression such as ``"(3 + 4) * 2^3"`` or
    ``"sqrt(16) + 10 % 3"`` safely and return the result.
    """
    tree = compile_formula(expression, allow_x=False)
    try:
        result = evaluate_formula(tree, 0.0)
    except ZeroDivisionError as exc:
        raise CalculationError("Division by zero is not allowed.") from exc
    except OverflowError as exc:
        raise CalculationError("The result is too large to calculate.") from exc
    except ValueError as exc:
        raise CalculationError("The expression has no real result (e.g. sqrt(-1)).") from exc
    if math.isinf(result) or math.isnan(result):
        raise CalculationError("The result is too large to calculate.")
    return result


def sample_formula(formula: str, x_min: float, x_max: float, points: int = 400) -> list[dict]:
    """
    Evaluate ``formula`` at evenly spaced points between ``x_min`` and ``x_max``.

    Points where the function is undefined (e.g. ``sqrt(-1)`` or ``1/0``) are
    returned with ``y`` set to ``None`` so charts show a gap.
    """
    if x_min >= x_max:
        raise CalculationError("The start of the range must be less than the end.")
    tree = compile_formula(formula)
    step = (x_max - x_min) / (points - 1)
    rows = []
    for i in range(points):
        x = x_min + i * step
        try:
            y = evaluate_formula(tree, x)
            if math.isinf(y) or math.isnan(y) or abs(y) > 1e12:
                y = None
        except (ValueError, ZeroDivisionError, OverflowError):
            y = None
        rows.append({"x": x, "y": y})
    if all(row["y"] is None for row in rows):
        raise CalculationError("The function is undefined over the whole range.")
    return rows


def find_crossings(first: list[dict], second: list[dict]) -> list[float]:
    """
    Return the approximate x values where two sampled curves cross.

    Both lists must come from :func:`sample_formula` with the same range and
    number of points. Points where either curve is undefined are skipped.
    """
    crossings: list[float] = []
    defined = [p["y"] for p in first + second if p["y"] is not None]
    if not defined:
        return crossings
    # A sign change with a jump this large is a discontinuity (like 1/x at 0),
    # not a real crossing
    max_jump = 0.1 * ((max(defined) - min(defined)) or 1.0)
    previous = None  # (x, difference) of the last point where both are defined
    for a, b in zip(first, second, strict=True):
        if a["y"] is None or b["y"] is None:
            previous = None
            continue
        x, diff = a["x"], a["y"] - b["y"]
        if diff == 0:
            if not crossings or abs(crossings[-1] - x) > 1e-9:
                crossings.append(x)
        elif (
            previous is not None
            and previous[1] != 0
            and (previous[1] < 0) != (diff < 0)
            and abs(diff - previous[1]) <= max_jump
        ):
            # Linear interpolation between the two samples
            x0, d0 = previous
            crossings.append(x0 + (x - x0) * d0 / (d0 - diff))
        previous = (x, diff)
    return crossings
