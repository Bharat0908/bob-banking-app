"""
models.py — Plain Python data classes for domain entities.
These classes hold data only; they do not talk to the database directly.
"""

from dataclasses import dataclass


@dataclass
class Customer:
    """Represents a bank customer account."""
    id: int
    username: str
    password_hash: str
    full_name: str
    balance: float

    def formatted_balance(self) -> str:
        return f"${self.balance:,.2f}"


@dataclass
class Transaction:
    """Represents a single deposit or withdrawal transaction."""
    id: int
    customer_id: int
    transaction_type: str
    amount: float
    balance_after: float
    created_at: str

    def formatted_amount(self) -> str:
        return f"${self.amount:,.2f}"

    def formatted_balance_after(self) -> str:
        return f"${self.balance_after:,.2f}"
