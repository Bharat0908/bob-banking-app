"""
auth.py — Authentication logic.
Handles credential verification, session creation, logout,
and the login_required decorator that protects all secured routes.
"""

import functools
from flask import session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from db import get_customer_by_username


def verify_login(username: str, password: str) -> dict:
    """
    Verify a username/password pair against the database.
    The failure message is the same for both cases — no information leakage.
    """
    customer = get_customer_by_username(username)
    if customer is None:
        return {"success": False, "message": "Invalid username or password."}
    if not check_password_hash(customer.password_hash, password):
        return {"success": False, "message": "Invalid username or password."}
    return {"success": True, "customer": customer}


def logout_user():
    """Destroy the server-side session entirely."""
    session.clear()


def login_required(view_func):
    """Decorator that guards a Flask route behind an active session."""
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("customer_id"):
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped
