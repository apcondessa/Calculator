# 🎈 Calculator Loop – Streamlit Application

A simple and interactive **web-based calculator** built with **Python** and **Streamlit**, designed to perform basic arithmetic operations through a clean and user-friendly interface.

This project demonstrates the correct adaptation of a terminal-based calculator into a Streamlit application, following best practices for reactive web apps.

---

## 📋 Overview

The Calculator Loop app allows users to input two numbers, select an arithmetic operation, and instantly view the result. It handles common edge cases, such as division by zero, and provides immediate visual feedback.

---

## ✨ Features

The app is organized into three tabs:

### 🧮 Basic
- Operations: addition (+), subtraction (-), multiplication (×), division (÷), power (^), modulo (mod), percentage (A% of B) and square root (√)
- Clear error messages for invalid operations (division by zero, square root of a negative number, overflow…)
- **Calculation history** with a *Clear history* button and *Download as CSV*

### 💰 Financial
- Compound interest calculator with an initial amount, monthly contributions, annual rate, years and compounding frequency
- Final balance, total contributed and interest earned
- Stacked bar chart of contributions vs. interest, plus a year-by-year table

### 📊 Statistics
- Type/paste a list of numbers or upload a CSV and pick a numeric column
- Count, sum, mean, median, standard deviation, min, max, range, quartiles and IQR
- Histogram with an adjustable number of bins

---

## 🧰 Tech Stack

- **Python 3**
- **Streamlit**
- **pandas**

### Project structure

- `streamlit_app.py` – the user interface (tabs, inputs, charts)
- `calculator.py` – the calculation logic, independent from the UI

---

## 📦 Requirements

- Python 3.8 or higher
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

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).
