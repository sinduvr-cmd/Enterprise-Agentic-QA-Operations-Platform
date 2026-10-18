"""
Pytest configuration and test client fixtures.
Uses an in-memory SQLite database isolated per test session.
"""
import pytest
import os
from fastapi.testclient import TestClient

# Ensure test configuration environment
os.environ["DATABASE_URL"] = "sqlite:///./test_qa_ops.db"
os.environ["DEMO_MODE"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-12345"

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal, init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create tables and seed data
    init_db()
    yield
    # Teardown test db
    if os.path.exists("./test_qa_ops.db"):
        try:
            os.remove("./test_qa_ops.db")
        except Exception:
            pass


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
