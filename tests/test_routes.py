"""
test_routes.py — Integration tests for all Flask routes.
"""

import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))


class TestLoginPage:
    def test_login_page_returns_200(self, client):
        assert client.get("/login").status_code == 200
    def test_login_page_contains_form(self, client):
        r = client.get("/login")
        assert b"username" in r.data and b"password" in r.data
    def test_logged_in_user_redirected_away_from_login(self, auth_client):
        r = auth_client.get("/login", follow_redirects=False)
        assert r.status_code == 302 and "/dashboard" in r.headers["Location"]


class TestLoginPost:
    def test_valid_login_redirects_to_dashboard(self, client):
        r = client.post("/login", data={"username": "demo", "password": "password123"}, follow_redirects=False)
        assert r.status_code == 302 and "/dashboard" in r.headers["Location"]
    def test_invalid_password_stays_on_login(self, client):
        r = client.post("/login", data={"username": "demo", "password": "wrong"}, follow_redirects=True)
        assert b"Invalid username or password" in r.data
    def test_nonexistent_user_stays_on_login(self, client):
        r = client.post("/login", data={"username": "nobody", "password": "pass"}, follow_redirects=True)
        assert b"Invalid username or password" in r.data
    def test_empty_username_shows_error(self, client):
        r = client.post("/login", data={"username": "", "password": "pass"}, follow_redirects=True)
        assert b"required" in r.data.lower()
    def test_empty_password_shows_error(self, client):
        r = client.post("/login", data={"username": "demo", "password": ""}, follow_redirects=True)
        assert b"required" in r.data.lower()


class TestDashboard:
    def test_unauthenticated_redirects_to_login(self, client):
        r = client.get("/dashboard", follow_redirects=False)
        assert r.status_code == 302 and "/login" in r.headers["Location"]
    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/dashboard").status_code == 200
    def test_dashboard_shows_customer_name(self, auth_client):
        assert b"Alex Johnson" in auth_client.get("/dashboard").data
    def test_dashboard_shows_balance(self, auth_client):
        assert b"5,000.00" in auth_client.get("/dashboard").data


class TestDeposit:
    def test_deposit_page_requires_login(self, client):
        r = client.get("/deposit", follow_redirects=False)
        assert r.status_code == 302 and "/login" in r.headers["Location"]
    def test_deposit_page_loads_for_authenticated(self, auth_client):
        assert auth_client.get("/deposit").status_code == 200
    def test_valid_deposit_redirects_to_dashboard(self, auth_client):
        r = auth_client.post("/deposit", data={"amount": "100"}, follow_redirects=False)
        assert r.status_code == 302 and "/dashboard" in r.headers["Location"]
    def test_valid_deposit_updates_balance_on_dashboard(self, auth_client):
        auth_client.post("/deposit", data={"amount": "500"})
        assert b"5,500.00" in auth_client.get("/dashboard").data
    def test_deposit_zero_shows_error(self, auth_client):
        r = auth_client.post("/deposit", data={"amount": "0"}, follow_redirects=True)
        assert b"greater than zero" in r.data.lower()
    def test_deposit_negative_shows_error(self, auth_client):
        r = auth_client.post("/deposit", data={"amount": "-50"}, follow_redirects=True)
        assert b"greater than zero" in r.data.lower()
    def test_deposit_non_numeric_shows_error(self, auth_client):
        r = auth_client.post("/deposit", data={"amount": "abc"}, follow_redirects=True)
        assert b"valid" in r.data.lower()


class TestWithdraw:
    def test_withdraw_page_requires_login(self, client):
        r = client.get("/withdraw", follow_redirects=False)
        assert r.status_code == 302 and "/login" in r.headers["Location"]
    def test_withdraw_page_loads_for_authenticated(self, auth_client):
        assert auth_client.get("/withdraw").status_code == 200
    def test_withdraw_page_shows_balance(self, auth_client):
        assert b"5,000.00" in auth_client.get("/withdraw").data
    def test_valid_withdrawal_redirects_to_dashboard(self, auth_client):
        r = auth_client.post("/withdraw", data={"amount": "100"}, follow_redirects=False)
        assert r.status_code == 302 and "/dashboard" in r.headers["Location"]
    def test_valid_withdrawal_updates_balance(self, auth_client):
        auth_client.post("/withdraw", data={"amount": "1000"})
        assert b"4,000.00" in auth_client.get("/dashboard").data
    def test_overdraft_shows_error(self, auth_client):
        r = auth_client.post("/withdraw", data={"amount": "99999"}, follow_redirects=True)
        assert b"insufficient" in r.data.lower()
    def test_withdraw_zero_shows_error(self, auth_client):
        r = auth_client.post("/withdraw", data={"amount": "0"}, follow_redirects=True)
        assert b"greater than zero" in r.data.lower()
    def test_withdraw_non_numeric_shows_error(self, auth_client):
        r = auth_client.post("/withdraw", data={"amount": "hello"}, follow_redirects=True)
        assert b"valid" in r.data.lower()


class TestLogout:
    def test_logout_redirects_to_login(self, auth_client):
        r = auth_client.get("/logout", follow_redirects=False)
        assert r.status_code == 302 and "/login" in r.headers["Location"]
    def test_after_logout_dashboard_is_inaccessible(self, auth_client):
        auth_client.get("/logout")
        r = auth_client.get("/dashboard", follow_redirects=False)
        assert r.status_code == 302 and "/login" in r.headers["Location"]


class TestRoot:
    def test_unauthenticated_root_redirects_to_login(self, client):
        r = client.get("/", follow_redirects=False)
        assert r.status_code == 302 and "/login" in r.headers["Location"]
    def test_authenticated_root_redirects_to_dashboard(self, auth_client):
        r = auth_client.get("/", follow_redirects=False)
        assert r.status_code == 302 and "/dashboard" in r.headers["Location"]
