"""
test_transactions.py — Unit tests for deposit_funds() and withdraw_funds().
"""

import sys, os, pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

from models import Customer


def _make_customer(balance=5000.0):
    return Customer(id=1, username="demo", password_hash="hashed",
                    full_name="Alex Johnson", balance=balance)

def _mock_db(): return MagicMock()


class TestDepositFunds:

    def _run(self, customer, amount):
        from transactions import deposit_funds
        with patch("transactions.get_customer_by_id", return_value=customer), \
             patch("transactions.get_db", return_value=_mock_db()), \
             patch("transactions.update_balance"), \
             patch("transactions.record_transaction"):
            return deposit_funds(customer.id if customer else 1, amount)

    def test_valid_deposit_returns_success(self):
        assert self._run(_make_customer(5000.0), 200.0) == {"success": True, "new_balance": 5200.0}

    def test_deposit_zero_returns_failure(self):
        r = self._run(_make_customer(), 0)
        assert not r["success"] and "greater than zero" in r["message"].lower()

    def test_deposit_negative_returns_failure(self):
        r = self._run(_make_customer(), -50)
        assert not r["success"] and "greater than zero" in r["message"].lower()

    def test_deposit_non_numeric_returns_failure(self):
        r = self._run(_make_customer(), "abc")
        assert not r["success"] and "valid" in r["message"].lower()

    def test_deposit_empty_string_returns_failure(self):
        assert not self._run(_make_customer(), "")["success"]

    def test_deposit_precise_decimal(self):
        r = self._run(_make_customer(100.0), 0.01)
        assert r["success"] and r["new_balance"] == 100.01

    def test_deposit_rounds_to_two_decimals(self):
        r = self._run(_make_customer(0.1), 0.2)
        assert r["success"] and r["new_balance"] == round(0.1 + 0.2, 2)


class TestWithdrawFunds:

    def _run(self, customer, amount):
        from transactions import withdraw_funds
        with patch("transactions.get_customer_by_id", return_value=customer), \
             patch("transactions.get_db", return_value=_mock_db()), \
             patch("transactions.update_balance"), \
             patch("transactions.record_transaction"):
            return withdraw_funds(customer.id if customer else 1, amount)

    def test_valid_withdrawal_returns_success(self):
        assert self._run(_make_customer(5000.0), 100.0) == {"success": True, "new_balance": 4900.0}

    def test_withdraw_full_balance_returns_success(self):
        assert self._run(_make_customer(500.0), 500.0) == {"success": True, "new_balance": 0.0}

    def test_overdraft_returns_failure(self):
        r = self._run(_make_customer(100.0), 200.0)
        assert not r["success"] and "insufficient" in r["message"].lower()

    def test_withdraw_zero_returns_failure(self):
        r = self._run(_make_customer(), 0)
        assert not r["success"] and "greater than zero" in r["message"].lower()

    def test_withdraw_negative_returns_failure(self):
        r = self._run(_make_customer(), -10)
        assert not r["success"] and "greater than zero" in r["message"].lower()

    def test_withdraw_non_numeric_returns_failure(self):
        r = self._run(_make_customer(), "xyz")
        assert not r["success"] and "valid" in r["message"].lower()

    def test_withdraw_penny_over_balance_fails(self):
        r = self._run(_make_customer(99.99), 100.0)
        assert not r["success"] and "insufficient" in r["message"].lower()
