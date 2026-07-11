# Banking Web Application — Implementation Plan

> **Status:** Complete  
> **Document type:** High-level architecture and planning only.

---

## 1. Solution Overview

### Objective
Build a lightweight, browser-based Banking Web Application that allows authenticated customers to view their account balance and perform basic fund transactions (deposit and withdrawal) through a clean, responsive UI.

### Scope

| In Scope | Out of Scope |
|---|---|
| Customer login / logout | Admin portal |
| Dashboard with account summary | Multi-currency support |
| View current balance | Transfers between accounts |
| Deposit funds | Scheduled / recurring transactions |
| Withdraw funds | Email / SMS notifications |
| Session management | Third-party payment integrations |

### Functional Requirements
1. A customer must be able to log in with a username and password.
2. After login, the customer lands on a **Dashboard** showing their name and current balance.
3. The customer can **deposit** a positive amount into their account.
4. The customer can **withdraw** a positive amount, provided sufficient funds exist.
5. The customer can **log out**, which terminates their session.
6. Unauthenticated users must be redirected to the login page.

### Non-Functional Requirements
| Category | Requirement |
|---|---|
| **Security** | Passwords stored as Werkzeug hashes; sessions server-side and signed. |
| **Usability** | Responsive Bootstrap 5 UI. |
| **Reliability** | Balance updates reflected immediately after every transaction. |
| **Simplicity** | No external queues, caches, or cloud services. |
| **Maintainability** | Clear separation between FRONTEND and BACKEND. |

---

## 2. High-Level Architecture

```
BROWSER (HTML + Bootstrap)
    |
    | HTTP form POST / GET
    v
BACKEND (Python Flask)
  Routes -> Auth -> Business Logic -> DB Access Layer
    |
    | SQL read/write
    v
DATABASE (SQLite — bank.db)
```

---

## 3. Component Design

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | HTML + Bootstrap 5 | Renders pages, collects input, displays results |
| Backend | Python Flask | Routes, session management, validation, DB access |
| Database | SQLite 3 | Persists customers, balances, transaction history |

---

## 4. Folder Structure

```
banking-app/
├── FRONTEND/templates/   Jinja2 HTML pages
├── FRONTEND/static/css/  Bootstrap overrides
├── BACKEND/app.py        Flask factory + routes
├── BACKEND/auth.py       Authentication module
├── BACKEND/transactions.py  Deposit/withdrawal logic
├── BACKEND/db.py         SQLite data access layer
├── BACKEND/models.py     Customer & Transaction dataclasses
├── tests/                51 pytest tests
└── requirements.txt
```

---

## 5. Module Breakdown

| Module | Responsibility |
|---|---|
| Authentication | verify_login, logout_user, login_required decorator |
| Dashboard | Query customer name + balance; render dashboard.html |
| Transactions | deposit_funds, withdraw_funds with atomic DB writes |
| DB Layer | All SQLite interaction; no other file imports sqlite3 |

---

## 6. Implementation Roadmap

| Phase | Status |
|---|---|
| 1 — Project Scaffolding | Complete |
| 2 — Database Setup | Complete |
| 3 — Authentication | Complete |
| 4 — Dashboard | Complete |
| 5 — Transactions | Complete |
| 6 — Integration & Testing | Complete (51/51 tests pass) |

---

*End of Implementation Plan*
