# Expense Tracker

A simple Python expense tracker with a clean browser UI, built by two people using Git.
Add expenses, filter by date or category, export CSV reports, and visualize spending with a donut chart, a bar chart, and a monthly trend chart.

## Features

- **Add & Validate Expenses**: Record expenses with date, amount (whole number or up to 1 decimal place), category, and optional notes
- **One-Click Delete**: Remove any expense row directly from the web table with confirmation
- **Flexible Time Filtering**: Switch between **All** records, **Today** shortcut, a specific **Date** picker, or **Month** dropdown
- **Category & Keyword Search**: Filter records, summary cards, and charts by category or keyword in notes
- **CSV Export**: Download currently filtered expenses as a UTF-8 CSV file (`Export CSV`)
- **Interactive Charts**: View spending via **Donut chart** (category share), **Bar chart** (amount per category), and **Monthly trend** (total per month), with full Chinese font support
- **Plain CSV Storage**: All records are persisted locally in `expenses.csv`

## Project structure

| File | Purpose | Owner |
| :--- | :--- | :--- |
| `expense_input.py` | Validate, store, and delete expenses in `expenses.csv` (CLI supported) | hsisophia |
| `expense_app.py` | Web UI, time/category/keyword filters, and CSV export (standard library only) | hsisophia & sunyuen526 |
| `expense_chart.py` | Donut and bar charts by category with Chinese font and 1-decimal support | sunyuen526 |
| `expense_trend.py` | Monthly spending trend bar chart | hsisophia |
| `sample_expenses.csv` | Bundled sample dataset for testing | - |
| `requirements.txt` | Python dependencies (`matplotlib`) | sunyuen526 |

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt