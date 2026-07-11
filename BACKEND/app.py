"""
app.py — Flask application entry point.
Registers all routes, initialises the database on first run,
configures template/static folder paths, and registers error handlers.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "FRONTEND")


def create_app(secret_key: str = None):
    """Create and configure the Flask application."""
    flask_app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static"),
    )

    flask_app.secret_key = secret_key or os.environ.get(
        "FLASK_SECRET_KEY", "dev-secret-key-change-in-production-32chars"
    )

    from db import init_db, seed_test_customer, close_db

    with flask_app.app_context():
        init_db()
        seed_test_customer()

    @flask_app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    from auth import login_required, verify_login, logout_user
    from transactions import deposit_funds, withdraw_funds
    from db import get_customer_by_id

    @flask_app.route("/")
    def index():
        if session.get("customer_id"):
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @flask_app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("customer_id"):
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if not username:
                flash("Username is required.", "danger")
                return render_template("login.html")
            if not password:
                flash("Password is required.", "danger")
                return render_template("login.html")
            result = verify_login(username, password)
            if result["success"]:
                session.clear()
                session["customer_id"] = result["customer"].id
                flash(f"Welcome back, {result['customer'].full_name}!", "success")
                return redirect(url_for("dashboard"))
            flash(result["message"], "danger")
            return render_template("login.html")
        return render_template("login.html")

    @flask_app.route("/logout")
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @flask_app.route("/dashboard")
    @login_required
    def dashboard():
        customer = get_customer_by_id(session["customer_id"])
        if not customer:
            session.clear()
            flash("Session expired. Please log in again.", "danger")
            return redirect(url_for("login"))
        return render_template("dashboard.html", customer=customer)

    @flask_app.route("/deposit", methods=["GET", "POST"])
    @login_required
    def deposit():
        if request.method == "POST":
            amount_str = request.form.get("amount", "").strip()
            try:
                amount = float(amount_str)
            except (ValueError, TypeError):
                flash("Please enter a valid numeric amount.", "danger")
                return render_template("deposit.html")
            result = deposit_funds(session["customer_id"], amount)
            if result["success"]:
                flash(f"Deposit successful! New balance: ${result['new_balance']:,.2f}", "success")
                return redirect(url_for("dashboard"))
            flash(result["message"], "danger")
            return render_template("deposit.html")
        return render_template("deposit.html")

    @flask_app.route("/withdraw", methods=["GET", "POST"])
    @login_required
    def withdraw():
        customer = get_customer_by_id(session["customer_id"])
        if request.method == "POST":
            amount_str = request.form.get("amount", "").strip()
            if not amount_str:
                flash("Amount is required.", "danger")
                return render_template("withdraw.html", customer=customer)
            try:
                amount = float(amount_str)
            except (ValueError, TypeError):
                flash("Please enter a valid numeric amount.", "danger")
                return render_template("withdraw.html", customer=customer)
            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                return render_template("withdraw.html", customer=customer)
            if amount > customer.balance:
                flash("Insufficient funds.", "danger")
                return render_template("withdraw.html", customer=customer)
            result = withdraw_funds(session["customer_id"], amount)
            if result["success"]:
                flash(f"Withdrawal successful! New balance: ${result['new_balance']:,.2f}", "success")
                return redirect(url_for("dashboard"))
            flash(result["message"], "danger")
            return render_template("withdraw.html", customer=customer)
        return render_template("withdraw.html", customer=customer)

    @flask_app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @flask_app.errorhandler(500)
    def internal_error(e):
        flask_app.logger.error(f"Server error: {e}")
        return render_template("500.html"), 500

    return flask_app


if not os.environ.get("FLASK_TESTING"):
    app = create_app()

if __name__ == "__main__":
    _app = create_app()
    _app.run(debug=True)
