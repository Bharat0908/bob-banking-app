"""
transactions.py — Business logic for deposits and withdrawals.
Never touches templates or sessions — only takes numbers and returns result dicts.
All DB writes are wrapped in a single atomic transaction.
"""

from db import get_db, get_customer_by_id, update_balance, record_transaction


def deposit_funds(customer_id: int, amount) -> dict:
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return {"success": False, "message": "Please enter a valid numeric amount."}
    if amount <= 0:
        return {"success": False, "message": "Deposit amount must be greater than zero."}
    customer = get_customer_by_id(customer_id)
    if customer is None:
        return {"success": False, "message": "Customer account not found."}
    new_balance = round(customer.balance + amount, 2)
    db = get_db()
    try:
        db.execute("BEGIN")
        update_balance(customer_id, new_balance, db)
        record_transaction(customer_id, "deposit", amount, new_balance, db)
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        return {"success": False, "message": "A database error occurred. Please try again."}
    return {"success": True, "new_balance": new_balance}


def withdraw_funds(customer_id: int, amount) -> dict:
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return {"success": False, "message": "Please enter a valid numeric amount."}
    if amount <= 0:
        return {"success": False, "message": "Withdrawal amount must be greater than zero."}
    customer = get_customer_by_id(customer_id)
    if customer is None:
        return {"success": False, "message": "Customer account not found."}
    if amount > customer.balance:
        return {"success": False, "message": f"Insufficient funds. Your current balance is ${customer.balance:,.2f}."}
    new_balance = round(customer.balance - amount, 2)
    db = get_db()
    try:
        db.execute("BEGIN")
        update_balance(customer_id, new_balance, db)
        record_transaction(customer_id, "withdrawal", amount, new_balance, db)
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        return {"success": False, "message": "A database error occurred. Please try again."}
    return {"success": True, "new_balance": new_balance}
