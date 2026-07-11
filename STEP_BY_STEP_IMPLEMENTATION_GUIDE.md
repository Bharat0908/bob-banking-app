# Banking Web Application — Step-by-Step Implementation Guide

> **Reference:** [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)  
> **Style:** Plain-English instructions and logic. No complete source code.

---

## Table of Contents
1. [Environment Setup](#1-environment-setup)
2. [Backend Implementation](#2-backend-implementation)
3. [Frontend Implementation](#3-frontend-implementation)
4. [Integration Steps](#4-integration-steps)
5. [Validation Rules](#5-validation-rules)
6. [Testing](#6-testing)
7. [Deployment](#7-deployment)

---

## 1. Environment Setup

### 1.1 Prerequisites
- Python 3.9 or later
- pip

### 1.2 Project Folder Structure
```
banking-app/
├── FRONTEND/templates/
├── FRONTEND/static/css/
├── BACKEND/
└── requirements.txt
```

### 1.3 Virtual Environment
1. Create: `python -m venv venv`
2. Activate (Windows CMD): `venv\Scripts\activate.bat`
3. Activate (macOS/Linux): `source venv/bin/activate`

### 1.4 Dependencies
Add to `requirements.txt`:
- `Flask` — web framework
- `Werkzeug` — password hashing
- `pytest`, `pytest-flask` — testing

Install: `pip install -r requirements.txt`

### 1.5 Verify Flask
Create a minimal `app.py` with a single `/` route returning "Flask is running". Navigate to `http://127.0.0.1:5000` to confirm.

---

## 2. Backend Implementation

### 2.1 db.py — Database Layer
- Open/create `bank.db` using `sqlite3.connect(DB_PATH)`
- Store connection on Flask's `g` object for request lifetime
- `init_db()` — CREATE TABLE IF NOT EXISTS for customers and transactions
- `seed_test_customer()` — insert demo account with hashed password if absent
- Helper functions: `get_customer_by_username`, `get_customer_by_id`, `update_balance`, `record_transaction`
- `@app.teardown_appcontext` closes the connection at end of each request

### 2.2 models.py — Data Classes
- `Customer` dataclass: id, username, password_hash, full_name, balance
- `Transaction` dataclass: id, customer_id, transaction_type, amount, balance_after, created_at
- Include `formatted_balance()` helper for currency display

### 2.3 auth.py — Authentication
- `verify_login(username, password)` — look up customer, check hash with `check_password_hash`
- Same error message for unknown username and wrong password (no information leakage)
- `logout_user()` — calls `session.clear()`
- `login_required` decorator — checks `session.get('customer_id')`, redirects to `/login` if absent

### 2.4 transactions.py — Business Logic
- `deposit_funds(customer_id, amount)` — validate > 0, compute new balance, atomic BEGIN/COMMIT
- `withdraw_funds(customer_id, amount)` — validate > 0, check sufficient funds, atomic BEGIN/COMMIT
- Both functions read balance fresh from DB before computing; never trust cached values

### 2.5 app.py — Routes
| Route | Method | Action |
|---|---|---|
| `/` | GET | Redirect to dashboard or login |
| `/login` | GET | Render login form |
| `/login` | POST | Verify credentials, create session, redirect |
| `/logout` | GET | Clear session, redirect to login |
| `/dashboard` | GET | Show name + balance |
| `/deposit` | GET/POST | Show/process deposit form |
| `/withdraw` | GET/POST | Show/process withdrawal form |

Always use POST → Redirect → GET after successful form submissions.

### 2.6 Session Management
- Set `app.secret_key` from `FLASK_SECRET_KEY` env variable
- Store only `customer_id` in session — never balance or password hash
- `session.clear()` on logout

### 2.7 Error Handling
- `@app.errorhandler(404)` — renders 404.html
- `@app.errorhandler(500)` — renders 500.html, logs the error
- Wrap DB writes in try/except; ROLLBACK on failure, flash a user-friendly message

---

## 3. Frontend Implementation

### 3.1 base.html
- Bootstrap 5 CDN link + Bootstrap Icons CDN
- Navbar with app name; show Logout button when `session.customer_id` is set
- Flash message loop using `get_flashed_messages(with_categories=true)`
- `{% block content %}` for page-specific HTML

### 3.2 login.html
- Centred Bootstrap card with username + password inputs
- Form POSTs to `{{ url_for('login') }}`
- Demo credentials hint card below the form

### 3.3 dashboard.html
- Balance card showing `{{ customer.formatted_balance() }}`
- Quick-action buttons: Deposit (success), Withdraw (warning), Logout (outline)

### 3.4 deposit.html
- Dollar input-group with `min=0.01 step=0.01`
- Back arrow + Cancel link to dashboard

### 3.5 withdraw.html
- Same structure as deposit; shows available balance hint above form
- `max` attribute set to `{{ customer.balance }}`

### 3.6 Bootstrap Layout
Use: `container`, `row/col-md-*`, `card/card-body`, `btn btn-*`, `alert alert-*`, `form-control`, `input-group`

---

## 4. Integration Steps

### 4.1 Flask Template/Static Paths
Pass `template_folder` and `static_folder` to the Flask constructor pointing at `FRONTEND/templates` and `FRONTEND/static` using `os.path` relative to `app.py`.

### 4.2 Form-to-Route Wiring
HTML `<form method="post" action="{{ url_for('deposit') }}">` — the `name` attribute on each `<input>` must match `request.form.get("name")` in the route handler.

### 4.3 Flask to SQLite
- `db.py` opens a connection per request via Flask's `g` object
- `@app.teardown_appcontext` closes it automatically
- All other modules call `db.py` helpers — no direct `sqlite3` imports elsewhere

### 4.4 Template Variables
| Key | Type | Pages |
|---|---|---|
| `customer` | Customer | dashboard, withdraw, navbar |
| Flash messages | via `flash()` | all pages |

---

## 5. Validation Rules

### Login
| Field | Rule | Message |
|---|---|---|
| username | not empty | "Username is required." |
| password | not empty | "Password is required." |
| credentials | hash match | "Invalid username or password." |

### Deposit
| Rule | Message |
|---|---|
| Numeric value | "Please enter a valid numeric amount." |
| amount > 0 | "Deposit amount must be greater than zero." |

### Withdrawal
| Rule | Message |
|---|---|
| Numeric value | "Please enter a valid numeric amount." |
| amount > 0 | "Withdrawal amount must be greater than zero." |
| amount <= balance | "Insufficient funds. Your current balance is $X." |

---

## 6. Testing

### 6.1 Unit Tests (test_auth.py, test_transactions.py)
- Patch `get_customer_by_username` / `get_customer_by_id` with mock objects
- Test all success and failure paths
- Confirm failure messages are identical for username-not-found and wrong-password

### 6.2 Integration Tests (test_routes.py)
- Use Flask test client against an isolated `tmp_path` SQLite database
- Cover every route, both GET and POST, including all error conditions
- Verify PRG pattern: successful POST returns 302 to `/dashboard`

### 6.3 Manual Checklist
- [ ] Unauthenticated access to /dashboard redirects to /login
- [ ] Wrong password shows generic error (no field hint)
- [ ] Deposit updates balance on dashboard
- [ ] Withdrawal over balance shows Insufficient funds
- [ ] Logout prevents back-button access
- [ ] Responsive on narrow viewport

---

## 7. Deployment

### 7.1 Run Locally
```bash
cd BACKEND
python app.py
# → http://127.0.0.1:5000
```

### 7.2 Production Checklist
| Concern | Action |
|---|---|
| WSGI server | `gunicorn --workers 2 --bind 0.0.0.0:8000 "app:app"` |
| Debug mode | Set `FLASK_DEBUG=0` |
| Secret key | Load from `FLASK_SECRET_KEY` env variable |
| HTTPS | nginx reverse proxy with TLS |
| Static files | Serve `FRONTEND/static/` directly via nginx |

---

*End of Step-by-Step Implementation Guide*
