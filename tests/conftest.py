"""
conftest.py — Shared pytest fixtures.

Sets FLASK_TESTING=1 before any import so the module-level app = create_app()
in app.py is skipped. Each test gets its own isolated SQLite DB via tmp_path.
"""

import os
import sys

os.environ["FLASK_TESTING"] = "1"

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BACKEND"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pytest


@pytest.fixture
def app(tmp_path, monkeypatch):
    import db as db_module
    from app import create_app
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test_bank.db"))
    flask_app = create_app(secret_key="test-secret-key-32-characters-ok")
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    client.post("/login", data={"username": "demo", "password": "password123"})
    return client
