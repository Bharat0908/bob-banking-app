"""
test_auth.py — Unit tests for verify_login().
"""

import sys, os, pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

from werkzeug.security import generate_password_hash
from models import Customer


def _make_customer(password="password123"):
    return Customer(id=1, username="demo",
                    password_hash=generate_password_hash(password),
                    full_name="Alex Johnson", balance=5000.0)


class TestVerifyLogin:

    def test_correct_credentials_return_success(self):
        from auth import verify_login
        with patch("auth.get_customer_by_username", return_value=_make_customer()):
            result = verify_login("demo", "password123")
        assert result["success"] is True
        assert result["customer"].username == "demo"

    def test_wrong_password_returns_failure(self):
        from auth import verify_login
        with patch("auth.get_customer_by_username", return_value=_make_customer()):
            result = verify_login("demo", "wrongpassword")
        assert result["success"] is False
        assert "invalid" in result["message"].lower()

    def test_nonexistent_username_returns_failure(self):
        from auth import verify_login
        with patch("auth.get_customer_by_username", return_value=None):
            result = verify_login("nobody", "password123")
        assert result["success"] is False
        assert "invalid" in result["message"].lower()

    def test_failure_message_is_same_regardless_of_cause(self):
        from auth import verify_login
        with patch("auth.get_customer_by_username", return_value=None):
            result_a = verify_login("nobody", "anything")
        with patch("auth.get_customer_by_username", return_value=_make_customer()):
            result_b = verify_login("demo", "wrongpassword")
        assert result_a["message"] == result_b["message"]

    def test_empty_username_is_handled(self):
        from auth import verify_login
        with patch("auth.get_customer_by_username", return_value=None):
            assert verify_login("", "password123")["success"] is False

    def test_empty_password_is_handled(self):
        from auth import verify_login
        with patch("auth.get_customer_by_username", return_value=_make_customer()):
            assert verify_login("demo", "")["success"] is False
