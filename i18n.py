"""
English / Portuguese (Brazil) translations for Calculator Loop.

Every piece of text shown in the app lives in ``TEXT`` with one entry per
language. Error messages raised by ``calculator.py`` and ``currency.py`` are
translated from their English template in ``ERRORS``.
"""

from __future__ import annotations

LANGUAGES = {"en": "English", "pt": "Português"}
DEFAULT_LANGUAGE = "en"

TEXT: dict[str, dict[str, str]] = {
    # --- General -------------------------------------------------------------
    "language": {"en": "Language", "pt": "Idioma"},
    "subtitle": {
        "en": "Basic math, money, units &amp; currencies, graphs and statistics, all in one place.",
        "pt": "Contas, dinheiro, unidades e moedas, gráficos e estatística, tudo em um só lugar.",
    },
    "tab.basic": {"en": "🧮 Basic", "pt": "🧮 Básica"},
    "tab.financial": {"en": "💰 Financial", "pt": "💰 Financeira"},
    "tab.converter": {"en": "🔄 Converter", "pt": "🔄 Conversor"},
    "tab.plotter": {"en": "📈 Plotter", "pt": "📈 Gráficos"},
    "tab.statistics": {"en": "📊 Statistics", "pt": "📊 Estatística"},
    "error": {"en": "Error: {message}", "pt": "Erro: {message}"},
    "year": {"en": "Year", "pt": "Ano"},
    "year_by_year": {"en": "Year-by-year table", "pt": "Tabela ano a ano"},
    # --- Basic ---------------------------------------------------------------
    "mode": {"en": "Mode", "pt": "Modo"},
    "mode.keypad": {"en": "⌨️ Keypad & expressions", "pt": "⌨️ Teclado e expressões"},
    "mode.two_numbers": {"en": "🔢 Two numbers", "pt": "🔢 Dois números"},
    "expression": {"en": "Expression", "pt": "Expressão"},
    "expression.placeholder": {
        "en": "Type or use the keys, e.g. (3 + 4) × 2^3",
        "pt": "Digite ou use as teclas, ex.: (3 + 4) × 2^3",
    },
    "expression.help": {
        "en": "Press Enter or = to calculate. Supports + − × ÷ ^ %, brackets, "
        "pi, e and functions like sqrt(), sin(), log().",
        "pt": "Pressione Enter ou = para calcular. Aceita + − × ÷ ^ %, parênteses, "
        "pi, e e funções como sqrt(), sin(), log().",
    },
    "keypad.caption": {
        "en": "`%` is the remainder (10 % 3 = 1). Use a dot for decimals: 2.5",
        "pt": "`%` é o resto da divisão (10 % 3 = 1). Use vírgula para decimais: 2,5",
    },
    "operation": {"en": "Operation", "pt": "Operação"},
    "number": {"en": "Number", "pt": "Número"},
    "first_number": {"en": "First number", "pt": "Primeiro número"},
    "second_number": {"en": "Second number", "pt": "Segundo número"},
    "not_used": {"en": "Not used for this operation.", "pt": "Não é usado nesta operação."},
    "calculate": {"en": "Calculate", "pt": "Calcular"},
    "history": {"en": "🕘 History", "pt": "🕘 Histórico"},
    "history.empty": {
        "en": "Your calculations will appear here.",
        "pt": "Seus cálculos aparecerão aqui.",
    },
    "history.time": {"en": "Time", "pt": "Hora"},
    "history.expression": {"en": "Expression", "pt": "Expressão"},
    "history.result": {"en": "Result", "pt": "Resultado"},
    "history.clear": {"en": "Clear history", "pt": "Limpar histórico"},
    "history.download": {"en": "Download as CSV", "pt": "Baixar em CSV"},
    "history.filename": {"en": "calculator_history.csv", "pt": "historico_calculadora.csv"},
    "op.+": {"en": "Addition", "pt": "Adição"},
    "op.-": {"en": "Subtraction", "pt": "Subtração"},
    "op.×": {"en": "Multiplication", "pt": "Multiplicação"},
    "op.÷": {"en": "Division", "pt": "Divisão"},
    "op.^": {"en": "Power", "pt": "Potência"},
    "op.mod": {"en": "Modulo (remainder)", "pt": "Resto da divisão"},
    "op.% of": {"en": "Percentage (A% of B)", "pt": "Porcentagem (A% de B)"},
    "op.√": {"en": "Square root", "pt": "Raiz quadrada"},
    "percent_of": {"en": "{a}% of {b}", "pt": "{a}% de {b}"},
    # --- Financial -----------------------------------------------------------
    "calculator": {"en": "Calculator", "pt": "Calculadora"},
    "fin.compound": {"en": "📈 Compound interest", "pt": "📈 Juros compostos"},
    "fin.loan": {"en": "🏠 Loan / mortgage", "pt": "🏠 Empréstimo / financiamento"},
    "compound.title": {"en": "Compound interest", "pt": "Juros compostos"},
    "compound.intro": {
        "en": "See how an investment grows over time with regular contributions.",
        "pt": "Veja como um investimento cresce com o tempo com aportes mensais.",
    },
    "initial_amount": {"en": "Initial amount", "pt": "Valor inicial"},
    "monthly_contribution": {"en": "Monthly contribution", "pt": "Aporte mensal"},
    "annual_rate": {"en": "Annual interest rate (%)", "pt": "Taxa de juros anual (%)"},
    "years": {"en": "Years", "pt": "Anos"},
    "compounding": {"en": "Compounding frequency", "pt": "Frequência de capitalização"},
    "compounding.Monthly": {"en": "Monthly", "pt": "Mensal"},
    "compounding.Quarterly": {"en": "Quarterly", "pt": "Trimestral"},
    "compounding.Semi-annually": {"en": "Semi-annually", "pt": "Semestral"},
    "compounding.Annually": {"en": "Annually", "pt": "Anual"},
    "compounding.Daily": {"en": "Daily", "pt": "Diária"},
    "final_balance": {"en": "Final balance", "pt": "Saldo final"},
    "total_contributed": {"en": "Total contributed", "pt": "Total investido"},
    "interest_earned": {"en": "Interest earned", "pt": "Juros ganhos"},
    "col.Contributed": {"en": "Contributed", "pt": "Investido"},
    "col.Interest": {"en": "Interest", "pt": "Juros"},
    "col.Balance": {"en": "Balance", "pt": "Saldo"},
    "loan.title": {"en": "Loan / mortgage", "pt": "Empréstimo / financiamento"},
    "loan.intro": {
        "en": "Find the monthly payment and how much of it goes to interest.",
        "pt": "Descubra a parcela mensal e quanto dela vai para os juros.",
    },
    "loan_amount": {"en": "Loan amount", "pt": "Valor do empréstimo"},
    "loan_term": {"en": "Loan term (years)", "pt": "Prazo (anos)"},
    "monthly_payment": {"en": "Monthly payment", "pt": "Parcela mensal"},
    "total_paid": {"en": "Total paid", "pt": "Total pago"},
    "total_interest": {"en": "Total interest", "pt": "Total de juros"},
    "principal_vs_interest": {
        "en": "**Principal vs. interest paid each year**",
        "pt": "**Amortização vs. juros pagos por ano**",
    },
    "remaining_balance": {"en": "**Remaining balance**", "pt": "**Saldo devedor**"},
    "col.Principal paid": {"en": "Principal paid", "pt": "Amortização"},
    "col.Interest paid": {"en": "Interest paid", "pt": "Juros pagos"},
    "col.Remaining balance": {"en": "Remaining balance", "pt": "Saldo devedor"},
    # --- Converter -----------------------------------------------------------
    "convert": {"en": "Convert", "pt": "Converter"},
    "conv.units": {"en": "📏 Units", "pt": "📏 Unidades"},
    "conv.currency": {"en": "💱 Currency (live rates)", "pt": "💱 Moedas (cotação ao vivo)"},
    "units.title": {"en": "Unit converter", "pt": "Conversor de unidades"},
    "unit_type": {"en": "Type of unit", "pt": "Tipo de unidade"},
    "value": {"en": "Value", "pt": "Valor"},
    "from": {"en": "From", "pt": "De"},
    "to": {"en": "To", "pt": "Para"},
    "unit": {"en": "Unit", "pt": "Unidade"},
    "in_every_unit": {
        "en": "{value} {unit} in every {category} unit",
        "pt": "{value} {unit} em todas as unidades de {category}",
    },
    "category.Length": {"en": "Length", "pt": "Comprimento"},
    "category.Weight": {"en": "Weight", "pt": "Peso"},
    "category.Volume": {"en": "Volume", "pt": "Volume"},
    "category.Speed": {"en": "Speed", "pt": "Velocidade"},
    "category.Data": {"en": "Data", "pt": "Dados"},
    "category.Temperature": {"en": "Temperature", "pt": "Temperatura"},
    "unit.Millimeter": {"en": "Millimeter", "pt": "Milímetro"},
    "unit.Centimeter": {"en": "Centimeter", "pt": "Centímetro"},
    "unit.Meter": {"en": "Meter", "pt": "Metro"},
    "unit.Kilometer": {"en": "Kilometer", "pt": "Quilômetro"},
    "unit.Inch": {"en": "Inch", "pt": "Polegada"},
    "unit.Foot": {"en": "Foot", "pt": "Pé"},
    "unit.Yard": {"en": "Yard", "pt": "Jarda"},
    "unit.Mile": {"en": "Mile", "pt": "Milha"},
    "unit.Milligram": {"en": "Milligram", "pt": "Miligrama"},
    "unit.Gram": {"en": "Gram", "pt": "Grama"},
    "unit.Kilogram": {"en": "Kilogram", "pt": "Quilograma"},
    "unit.Tonne": {"en": "Tonne", "pt": "Tonelada"},
    "unit.Ounce": {"en": "Ounce", "pt": "Onça"},
    "unit.Pound": {"en": "Pound", "pt": "Libra"},
    "unit.Milliliter": {"en": "Milliliter", "pt": "Mililitro"},
    "unit.Liter": {"en": "Liter", "pt": "Litro"},
    "unit.Cubic meter": {"en": "Cubic meter", "pt": "Metro cúbico"},
    "unit.Teaspoon (US)": {"en": "Teaspoon (US)", "pt": "Colher de chá (EUA)"},
    "unit.Tablespoon (US)": {"en": "Tablespoon (US)", "pt": "Colher de sopa (EUA)"},
    "unit.Cup (US)": {"en": "Cup (US)", "pt": "Xícara (EUA)"},
    "unit.Gallon (US)": {"en": "Gallon (US)", "pt": "Galão (EUA)"},
    "unit.Meters per second": {"en": "Meters per second", "pt": "Metros por segundo"},
    "unit.Kilometers per hour": {"en": "Kilometers per hour", "pt": "Quilômetros por hora"},
    "unit.Miles per hour": {"en": "Miles per hour", "pt": "Milhas por hora"},
    "unit.Knot": {"en": "Knot", "pt": "Nó"},
    "unit.Byte": {"en": "Byte", "pt": "Byte"},
    "unit.Kilobyte": {"en": "Kilobyte", "pt": "Kilobyte"},
    "unit.Megabyte": {"en": "Megabyte", "pt": "Megabyte"},
    "unit.Gigabyte": {"en": "Gigabyte", "pt": "Gigabyte"},
    "unit.Terabyte": {"en": "Terabyte", "pt": "Terabyte"},
    "unit.Celsius": {"en": "Celsius", "pt": "Celsius"},
    "unit.Fahrenheit": {"en": "Fahrenheit", "pt": "Fahrenheit"},
    "unit.Kelvin": {"en": "Kelvin", "pt": "Kelvin"},
    "fx.title": {"en": "Currency converter", "pt": "Conversor de moedas"},
    "fx.common_only": {
        "en": "{message} Showing the most common currencies only.",
        "pt": "{message} Mostrando apenas as moedas mais comuns.",
    },
    "amount": {"en": "Amount", "pt": "Valor"},
    "swap": {"en": "Swap currencies", "pt": "Inverter moedas"},
    "fx.loading": {"en": "Loading the latest rate…", "pt": "Carregando a cotação mais recente…"},
    "fx.rate_from": {"en": "rate from {date}", "pt": "cotação de {date}"},
    "history_period": {"en": "History", "pt": "Histórico"},
    "period.1 month": {"en": "1 month", "pt": "1 mês"},
    "period.3 months": {"en": "3 months", "pt": "3 meses"},
    "period.1 year": {"en": "1 year", "pt": "1 ano"},
    "period.5 years": {"en": "5 years", "pt": "5 anos"},
    "fx.not_enough": {
        "en": "Not enough history available for this pair.",
        "pt": "Não há histórico suficiente para este par de moedas.",
    },
    "fx.rate_now": {"en": "Rate now", "pt": "Cotação atual"},
    "fx.change": {"en": "{change}% in {period}", "pt": "{change}% em {period}"},
    "lowest": {"en": "Lowest", "pt": "Mínima"},
    "highest": {"en": "Highest", "pt": "Máxima"},
    "date": {"en": "Date", "pt": "Data"},
    "rate": {"en": "Rate", "pt": "Cotação"},
    "fx.per": {"en": "{target} per 1 {base}", "pt": "{target} por 1 {base}"},
    "fx.source": {
        "en": "Rates: European Central Bank reference rates via frankfurter.dev, "
        "updated once per working day. For information only.",
        "pt": "Cotações: taxas de referência do Banco Central Europeu via frankfurter.dev, "
        "atualizadas uma vez por dia útil. Apenas para fins informativos.",
    },
    # --- Plotter -------------------------------------------------------------
    "plot.title": {"en": "Function plotter", "pt": "Gráfico de funções"},
    "plot.intro": {
        "en": "Type a formula using **x**. Supported: `+ - * / ^ %`, brackets, `pi`, `e`, "
        "and the functions `sin cos tan asin acos atan sqrt log log10 exp abs floor ceil`.",
        "pt": "Digite uma fórmula usando **x**. Aceita: `+ - * / ^ %`, parênteses, `pi`, `e` "
        "e as funções `sin cos tan asin acos atan sqrt log log10 exp abs floor ceil`. "
        "Use ponto para decimais nas fórmulas (2.5).",
    },
    "plot.example": {"en": "Start from an example", "pt": "Comece com um exemplo"},
    "plot.compare": {"en": "y₂ = (optional, to compare)", "pt": "y₂ = (opcional, para comparar)"},
    "plot.compare_placeholder": {"en": "e.g. 2*x + 1", "pt": "ex.: 2*x + 1"},
    "x_from": {"en": "x from", "pt": "x de"},
    "x_to": {"en": "x to", "pt": "x até"},
    "plot.gaps": {
        "en": "Gaps in a line are values of x where that function is undefined.",
        "pt": "Falhas em uma linha são valores de x onde a função não está definida.",
    },
    "plot.lowest": {"en": "Lowest y in range", "pt": "Menor y no intervalo"},
    "plot.highest": {"en": "Highest y in range", "pt": "Maior y no intervalo"},
    "plot.crossings": {"en": "Crossing points", "pt": "Pontos de cruzamento"},
    "plot.where": {"en": "Where the curves meet", "pt": "Onde as curvas se encontram"},
    "plot.no_cross": {"en": "They don't cross here", "pt": "Não se cruzam aqui"},
    "plot.more": {"en": " (+{count} more)", "pt": " (+{count} outros)"},
    # --- Statistics ----------------------------------------------------------
    "stats.title": {"en": "Descriptive statistics", "pt": "Estatística descritiva"},
    "data_source": {"en": "Data source", "pt": "Fonte dos dados"},
    "source.type": {"en": "✍️ Type or paste numbers", "pt": "✍️ Digitar ou colar números"},
    "source.csv": {"en": "📁 Upload CSV", "pt": "📁 Enviar CSV"},
    "stats.numbers": {
        "en": "Numbers (separated by commas, spaces or new lines)",
        "pt": "Números (separados por ponto e vírgula, espaços ou novas linhas)",
    },
    "stats.csv_file": {"en": "CSV file", "pt": "Arquivo CSV"},
    "stats.upload_hint": {
        "en": "Upload a CSV file to analyze one of its numeric columns.",
        "pt": "Envie um arquivo CSV para analisar uma das colunas numéricas.",
    },
    "stats.csv_error": {
        "en": "Could not read the CSV file: {message}",
        "pt": "Não foi possível ler o arquivo CSV: {message}",
    },
    "stats.no_numeric": {
        "en": "The file has no numeric columns.",
        "pt": "O arquivo não tem colunas numéricas.",
    },
    "stats.preview": {"en": "Preview data", "pt": "Pré-visualizar dados"},
    "stats.column": {"en": "Column to analyze", "pt": "Coluna para analisar"},
    "statistic": {"en": "Statistic", "pt": "Estatística"},
    "distribution": {"en": "**Distribution**", "pt": "**Distribuição**"},
    "bins": {"en": "Number of bins", "pt": "Número de faixas"},
    "range": {"en": "Range", "pt": "Faixa"},
    "count": {"en": "Count", "pt": "Quantidade"},
    "stat.Count": {"en": "Count", "pt": "Quantidade"},
    "stat.Sum": {"en": "Sum", "pt": "Soma"},
    "stat.Mean": {"en": "Mean", "pt": "Média"},
    "stat.Median": {"en": "Median", "pt": "Mediana"},
    "stat.Std. deviation": {"en": "Std. deviation", "pt": "Desvio padrão"},
    "stat.Std. deviation (sample)": {
        "en": "Std. deviation (sample)",
        "pt": "Desvio padrão (amostra)",
    },
    "stat.Std. deviation (population)": {
        "en": "Std. deviation (population)",
        "pt": "Desvio padrão (população)",
    },
    "stat.Min": {"en": "Min", "pt": "Mínimo"},
    "stat.Max": {"en": "Max", "pt": "Máximo"},
    "stat.Range": {"en": "Range", "pt": "Amplitude"},
    "stat.Q1 (25%)": {"en": "Q1 (25%)", "pt": "Q1 (25%)"},
    "stat.Q3 (75%)": {"en": "Q3 (75%)", "pt": "Q3 (75%)"},
    "stat.IQR": {"en": "IQR", "pt": "Intervalo interquartil"},
}

# Portuguese versions of the English error templates in calculator.py / currency.py
ERRORS_PT: dict[str, str] = {
    "Division by zero is not allowed.": "Não é possível dividir por zero.",
    "Cannot compute {a} ^ {b}.": "Não é possível calcular {a} ^ {b}.",
    "A negative number raised to a fractional power has no real result.": (
        "Um número negativo elevado a uma potência fracionária não tem resultado real."
    ),
    "Modulo by zero is not allowed.": "Não é possível calcular o resto da divisão por zero.",
    "Cannot take the square root of a negative number.": (
        "Não existe raiz quadrada (real) de número negativo."
    ),
    "Unknown operation: {operation}": "Operação desconhecida: {operation}",
    "Principal, years and contributions must not be negative.": (
        "Valor inicial, anos e aportes não podem ser negativos."
    ),
    "Compounding frequency must be positive.": "A frequência de capitalização deve ser positiva.",
    "'{token}' is not a valid number.": "'{token}' não é um número válido.",
    "Enter at least one number.": "Digite pelo menos um número.",
    "Loan amount must not be negative and years must be positive.": (
        "O valor do empréstimo não pode ser negativo e o prazo deve ser positivo."
    ),
    "Interest rate must not be negative.": "A taxa de juros não pode ser negativa.",
    "Unknown temperature unit: {unit}": "Unidade de temperatura desconhecida: {unit}",
    "Unknown category: {category}": "Categoria desconhecida: {category}",
    "Unknown unit for {category}.": "Unidade desconhecida para {category}.",
    "Temperature cannot be below absolute zero.": (
        "A temperatura não pode ser menor que o zero absoluto."
    ),
    "Enter a formula.": "Digite uma fórmula.",
    "The formula is not valid.": "A fórmula não é válida.",
    "{name}() takes exactly one argument.": "{name}() aceita exatamente um valor.",
    "Unknown function '{name}'.": "Função desconhecida: '{name}'.",
    "Use {name}(...) with brackets.": "Use {name}(...) com parênteses.",
    "Unknown name '{name}'. Use x as the variable.": (
        "Nome desconhecido: '{name}'. Use x como variável."
    ),
    "Unknown name '{name}'. Only numbers are allowed here.": (
        "Nome desconhecido: '{name}'. Aqui só são permitidos números."
    ),
    "Use a dot for decimals (2.5), not a comma (2,5).": (
        "Nas fórmulas, use ponto para decimais (2.5), não vírgula (2,5)."
    ),
    "The formula contains something that is not allowed.": (
        "A fórmula contém algo que não é permitido."
    ),
    "Unsupported formula.": "Fórmula não suportada.",
    "The result is too large to calculate.": "O resultado é grande demais para calcular.",
    "The expression has no real result (e.g. sqrt(-1)).": (
        "A expressão não tem resultado real (ex.: sqrt(-1))."
    ),
    "The start of the range must be less than the end.": (
        "O início do intervalo deve ser menor que o fim."
    ),
    "The function is undefined over the whole range.": (
        "A função não está definida em nenhum ponto do intervalo."
    ),
    "Could not load exchange rates right now. Please try again in a moment.": (
        "Não foi possível carregar as cotações agora. Tente novamente em instantes."
    ),
    "The exchange-rate service returned an unexpected answer.": (
        "O serviço de cotações retornou uma resposta inesperada."
    ),
    "The exchange-rate service returned no currencies.": (
        "O serviço de cotações não retornou nenhuma moeda."
    ),
    "No exchange rate available for {base} → {target}.": (
        "Não há cotação disponível para {base} → {target}."
    ),
    "The rate history could not be read.": "Não foi possível ler o histórico de cotações.",
}


def normalize_language(value: str | None) -> str | None:
    """Turn ``"pt"``, ``"pt-BR"``, ``"en_US"``… into a supported code, or ``None``."""
    if not value:
        return None
    code = value.strip().lower()[:2]
    return code if code in LANGUAGES else None


def t(key: str, lang: str, **params) -> str:
    """Return the text for ``key`` in ``lang`` (falls back to English, then the key)."""
    entry = TEXT.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry[DEFAULT_LANGUAGE]
    return text.format(**params) if params else text


def translate_error(error: Exception, lang: str) -> str:
    """Translate an error raised with a message template (see calculator.py)."""
    template = getattr(error, "template", None)
    if lang == "pt" and template in ERRORS_PT:
        return ERRORS_PT[template].format(**getattr(error, "params", {}))
    return str(error)


def localize_number(text: str, lang: str) -> str:
    """
    Convert a number formatted the English way (``1,234.5``) to the Brazilian
    way (``1.234,5``) when the language is Portuguese.
    """
    if lang != "pt":
        return text
    return text.translate(str.maketrans({",": ".", ".": ","}))


# Portuguese names for the most common currencies (others keep the API's English name)
CURRENCY_NAMES_PT = {
    "BRL": "Real brasileiro",
    "USD": "Dólar americano",
    "EUR": "Euro",
    "GBP": "Libra esterlina",
    "JPY": "Iene japonês",
    "CAD": "Dólar canadense",
    "AUD": "Dólar australiano",
    "CHF": "Franco suíço",
    "CNY": "Yuan chinês",
}


def format_date(iso_date: str, lang: str) -> str:
    """Show ``2026-11-12`` as ``12/11/2026`` in Portuguese."""
    if lang == "pt" and len(iso_date) == 10:
        year, month, day = iso_date.split("-")
        return f"{day}/{month}/{year}"
    return iso_date
