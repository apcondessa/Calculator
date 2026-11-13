# 🎈 Calculator Loop – Streamlit Application

[![CI](https://github.com/apcondessa/Calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/apcondessa/Calculator/actions/workflows/ci.yml)

<!-- After deploying, replace YOUR-APP-URL below and uncomment this line:
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR-APP-URL)
-->

An interactive **multi-tool calculator** built with **Python** and **Streamlit**: basic math with a calculation history, financial planning, unit conversion, a function plotter and quick descriptive statistics, all in one web app.

The project started as a terminal calculator and grew into a small, tested web application with the calculation logic kept separate from the user interface.

![Basic tab with calculation history](docs/screenshots/basic.png)

---

## ✨ Features

The app is organized into five tabs.

### 🧮 Basic
- Operations: addition (+), subtraction (-), multiplication (×), division (÷), power (^), modulo (mod), percentage (A% of B) and square root (√)
- Clear error messages for invalid operations (division by zero, square root of a negative number, overflow…)
- **Calculation history** with a *Clear history* button and *Download as CSV*

### 💰 Financial
- **Compound interest:** initial amount, monthly contributions, annual rate, years and compounding frequency, with a stacked chart of contributions vs. interest
- **Loan / mortgage:** monthly payment, total paid and total interest, with a principal-vs-interest chart and the remaining balance over time
- Year-by-year tables for both

### 📏 Converter
- Length, weight, volume, speed, data size and temperature
- Shows the value converted to every unit of the chosen type

### 📈 Plotter
- Type a formula of `x` (e.g. `x^2 - 3*x + 2` or `sin(x) * exp(-x/5)`) and see its graph over any range
- Supports `+ - * / ^ %`, brackets, `pi`, `e` and common math functions (`sin`, `cos`, `sqrt`, `log`, `exp`, `abs`…)
- Formulas are parsed safely: only math is allowed, so no arbitrary code can run

### 📊 Statistics
- Type/paste a list of numbers or upload a CSV and pick a numeric column
- Count, sum, mean, median, standard deviation, min, max, range, quartiles and IQR
- Histogram with an adjustable number of bins

---

## 📸 Screenshots

| Financial – compound interest | Financial – loan |
| --- | --- |
| ![Compound interest](docs/screenshots/financial.png) | ![Loan calculator](docs/screenshots/loan.png) |

| Converter | Plotter | Statistics |
| --- | --- | --- |
| ![Unit converter](docs/screenshots/converter.png) | ![Function plotter](docs/screenshots/plotter.png) | ![Statistics](docs/screenshots/statistics.png) |

---

## 🧰 Tech Stack

- **Python 3**
- **Streamlit** – web interface and charts
- **pandas** – tables, CSV handling and statistics
- **pytest** – automated tests
- **ruff** – linting and formatting
- **GitHub Actions** – runs the linter and tests on every push and pull request

### Project structure

```
├── streamlit_app.py          # User interface (tabs, inputs, charts)
├── calculator.py             # Calculation logic, independent from the UI
├── tests/
│   ├── test_calculator.py    # Unit tests for the calculation logic
│   └── test_app.py           # Runs the app headlessly and checks each tab
├── docs/screenshots/         # Images used in this README
├── requirements.txt          # Packages needed to run the app
├── requirements-dev.txt      # Extra packages for testing and linting
└── .github/workflows/ci.yml  # Continuous integration
```

---

## 📦 Requirements

- Python 3.10 or higher
- pip (Python package manager)

---

## 🚀 How to Run

1. **Clone the repository**

   ```bash
   git clone https://github.com/apcondessa/Calculator.git
   cd Calculator
   ```

2. **(Optional) Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the app**

   ```bash
   streamlit run streamlit_app.py
   ```

5. Open the URL shown in the terminal (usually <http://localhost:8501>) in your browser.

---

## 🧪 Running the Tests

Install the development dependencies, then run the linter and the tests:

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

The same checks run automatically on GitHub for every push and pull request (see the **CI** badge at the top).

---

## ☁️ Deploying to Streamlit Community Cloud

The app can be published for free so anyone can use it in the browser:

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Choose the repository `apcondessa/Calculator`, branch `main`, and main file `streamlit_app.py`.
4. Click **Deploy**. Every new push to `main` updates the live app automatically.

---

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).
