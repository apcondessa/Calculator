"""Checks that every text in the app is translated consistently."""

import ast
import string
from pathlib import Path

import pytest

import calculator
import currency
from i18n import (
    ERRORS_PT,
    LANGUAGES,
    TEXT,
    format_date,
    localize_number,
    normalize_language,
    t,
    translate_error,
)

ROOT = Path(__file__).resolve().parent.parent


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def error_templates() -> set[str]:
    """Every message template passed to CalculationError / CurrencyError."""
    templates = set()
    for filename in ["calculator.py", "currency.py"]:
        tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and getattr(node.func, "id", "") in {"CalculationError", "CurrencyError"}
                and node.args
            ):
                assert isinstance(node.args[0], ast.Constant), (
                    f"{filename}:{node.lineno}: use a plain template string, not an f-string"
                )
                templates.add(node.args[0].value)
    return templates


@pytest.mark.parametrize("key", sorted(TEXT))
def test_every_text_has_all_languages_and_same_placeholders(key):
    entry = TEXT[key]
    assert set(entry) == set(LANGUAGES), f"{key} is missing a language"
    assert placeholders(entry["en"]) == placeholders(entry["pt"]), key


def test_every_error_message_has_a_portuguese_translation():
    missing = error_templates() - set(ERRORS_PT)
    assert not missing, f"Add these to ERRORS_PT in i18n.py: {missing}"


@pytest.mark.parametrize("template", sorted(ERRORS_PT))
def test_error_translations_keep_placeholders(template):
    assert placeholders(template) == placeholders(ERRORS_PT[template])


def test_every_unit_and_category_is_translated():
    for category, units in calculator.UNITS.items():
        assert f"category.{category}" in TEXT
        for unit in units:
            assert f"unit.{unit}" in TEXT


def test_translate_error():
    with pytest.raises(calculator.CalculationError) as info:
        calculator.calculate(1, 0, "÷")
    assert translate_error(info.value, "en") == "Division by zero is not allowed."
    assert translate_error(info.value, "pt") == "Não é possível dividir por zero."

    error = currency.CurrencyError(
        "No exchange rate available for {base} → {target}.", base="USD", target="XYZ"
    )
    assert translate_error(error, "pt") == "Não há cotação disponível para USD → XYZ."


def test_t_falls_back_safely():
    assert t("calculate", "pt") == "Calcular"
    assert t("calculate", "fr") == "Calculate"  # unknown language → English
    assert t("no.such.key", "pt") == "no.such.key"
    assert t("fx.rate_from", "pt", date="12/11/2026") == "cotação de 12/11/2026"


@pytest.mark.parametrize(
    ("value", "expected"),
    [("pt", "pt"), ("pt-BR", "pt"), ("PT_br", "pt"), ("en-US", "en"), ("fr", None), (None, None)],
)
def test_normalize_language(value, expected):
    assert normalize_language(value) == expected


def test_localize_number_and_date():
    assert localize_number("1,234,567.89", "pt") == "1.234.567,89"
    assert localize_number("1,234,567.89", "en") == "1,234,567.89"
    assert format_date("2026-11-12", "pt") == "12/11/2026"
    assert format_date("2026-11-12", "en") == "2026-11-12"


def test_parse_numbers_with_decimal_comma():
    assert calculator.parse_numbers("1,5; 2,5\n3", decimal_comma=True) == [1.5, 2.5, 3]
