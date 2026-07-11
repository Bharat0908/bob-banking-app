"""
db.py — Database access layer.
All SQLite interaction is centralised here.
No other file imports sqlite3 directly.
"""

import sqlite3
import os
from datetime import datetime, timezone
from flask import g
from models import Customer, Transaction

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bank.db")


def get_db() -> sqlite3.Connection:
    """Return the per-request database connection (stored on Flask's g object)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they do not already exist. Safe to call on every startup."""
    db = _open_direct()
    try:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS customers (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                full_name     TEXT    NOT NULL,
                balance       REAL    NOT NULL DEFAULT 0.0
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id      INTEGER NOT NULL,
                transaction_type TEXT    NOT NULL CHECK(transaction_type IN ('deposit','withdrawal')),
                amount           REAL    NOT NULL,
                balance_after    REAL    NOT NULL,
                created_at       TEXT    NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
        """)
        db.commit()
    finally:
        db.close()


def seed_test_customer():
    """Insert a demo customer if one does not already exist."""
    from werkzeug.security import generate_password_hash
    db = _open_direct()
    try:
        if db.execute("SELECT id FROM customers WHERE username = ?", ("demo",)).fetchone() is None:
            db.execute(
                "INSERT INTO customers (username, password_hash, full_name, balance) VALUES (?, ?, ?, ?)",
                ("demo", generate_password_hash("password123"), "Alex Johnson", 5000.00),
            )
            db.commit()
    finally:
        db.close()


def get_customer_by_username(username: str):
    db = get_db()
    row = db.execute(
        "SELECT id, username, password_hash, full_name, balance FROM customers WHERE username = ?",
        (username,),
    ).fetchone()
    return _row_to_customer(row)


def get_customer_by_id(customer_id: int):
    db = get_db()
    row = db.execute(
        "SELECT id, username, password_hash, full_name, balance FROM customers WHERE id = ?",
        (customer_id,),
    ).fetchone()
    return _row_to_customer(row)


def update_balance(customer_id: int, new_balance: float, db: sqlite3.Connection):
    db.execute("UPDATE customers SET balance = ? WHERE id = ?", (new_balance, customer_id))


def record_transaction(customer_id, transaction_type, amount, balance_after, db):
    db.execute(
        "INSERT INTO transactions (customer_id, transaction_type, amount, balance_after, created_at) VALUES (?, ?, ?, ?, ?)",
        (customer_id, transaction_type, amount, balance_after, datetime.now(timezone.utc).isoformat()),
    )


def get_transactions_for_customer(customer_id: int):
    db = get_db()
    rows = db.execute(
        "SELECT id, customer_id, transaction_type, amount, balance_after, created_at FROM transactions WHERE customer_id = ? ORDER BY id DESC",
        (customer_id,),
    ).fetchall()
    return [_row_to_transaction(r) for r in rows]


def _open_direct() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _row_to_customer(row):
    if row is None:
        return None
    return Customer(id=row["id"], username=row["username"], password_hash=row["password_hash"],
                    full_name=row["full_name"], balance=row["balance"])


def _row_to_transaction(row):
    if row is None:
        return None
    return Transaction(id=row["id"], customer_id=row["customer_id"],
                       transaction_type=row["transaction_type"], amount=row["amount"],
                       balance_after=row["balance_after"], created_at=row["created_at"])
