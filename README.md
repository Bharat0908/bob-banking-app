# SecureBank — Banking Web Application

A lightweight, full-stack banking web application built with **HTML + Bootstrap** (frontend) and **Python Flask + SQLite** (backend).

---

## Features

| Feature | Route |
|---|---|
| Customer Login | `/login` |
| Dashboard (balance summary) | `/dashboard` |
| Deposit Funds | `/deposit` |
| Withdraw Funds | `/withdraw` |
| Logout | `/logout` |

---

## Project Structure

```
banking-app/
├── FRONTEND/
│   ├── templates/          # Jinja2 HTML templates
│   └── static/css/         # Bootstrap overrides
├── BACKEND/
│   ├── app.py              # Flask application factory + all routes
│   ├── auth.py             # Login verification, session management
│   ├── transactions.py     # Deposit & withdrawal business logic
│   ├── db.py               # SQLite data access layer
│   └── models.py           # Customer & Transaction data classes
├── tests/
│   ├── conftest.py         # Pytest fixtures (isolated per-test DB)
│   ├── test_auth.py        # Unit tests — authentication logic
│   ├── test_transactions.py # Unit tests — deposit & withdrawal
│   └── test_routes.py      # Integration tests — all HTTP routes
├── requirements.txt
├── IMPLEMENTATION_PLAN.md
├── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
└── README.md
```

---

## Quick Start

### 1. Prerequisites

- Python 3.9 or later
- pip

### 2. Create and Activate a Virtual Environment

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
cd BACKEND
python app.py
```

The development server starts on **http://127.0.0.1:5000**.

> `bank.db` is created automatically in `BACKEND/` on the first run.

### 5. Demo Login

| Field | Value |
|---|---|
| Username | `demo` |
| Password | `password123` |

Starting balance: **$5,000.00**

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Expected: **51 tests passed**.

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `FLASK_SECRET_KEY` | `dev-secret-key-...` | Signs session cookies. **Change in production.** |
| `FLASK_TESTING` | _(unset)_ | Set to `1` by the test suite. |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, Bootstrap 5.3, Bootstrap Icons, Jinja2 |
| Backend | Python 3.9+, Flask 2.3+ |
| Database | SQLite 3 (built-in `sqlite3` module) |
| Testing | pytest, pytest-flask |
