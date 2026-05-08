"""
Part 1 — Mocking HTTP & DB (10 min)
====================================
Goal: Test all 5 code paths in process_order() by mocking the payment
API (httpx.post) and using an in-memory SQLite database.

Code paths to cover:
  1. Invalid order         → {"status": "invalid", "errors": [...]}
  2. DB save failure       → {"status": "error", ...}
  3. Payment succeeds      → {"status": "ok", ...}
  4. Payment HTTP error    → {"status": "payment_failed", ...}
  5. Payment timeout       → {"status": "payment_timeout"}

Hints (try on your own first!):
  - Patch at the import location: @patch("order_processor.httpx.post")
  - For raise_for_status on 402: mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("402", request=..., response=...)
  - For timeout: mock_post.side_effect = httpx.TimeoutException("timed out")
"""

import pytest
import sqlite3
from unittest.mock import patch, MagicMock
import httpx
from order_processor import Order, OrderItem, process_order


# ── Helpers ──────────────────────────────────────────────────────────

def make_test_order(**overrides):
    """Create a valid Order. Pass keyword args to override defaults."""
    defaults = dict(
        order_id="ORD-001",
        customer_email="test@example.com",
        items=[OrderItem("PROD-1", "Widget", 2, 10.00)],
    )
    defaults.update(overrides)
    return Order(**defaults)


def setup_db():
    """Return an in-memory SQLite connection with the orders table."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE orders "
        "(order_id TEXT PRIMARY KEY, customer_email TEXT, total REAL, created_at TEXT)"
    )
    return conn


# ── Tests — fill in each method ──────────────────────────────────────

class TestProcessOrder:

    # Path 1: invalid order
    def test_invalid_order_returns_errors(self):
        # TODO: Create an order with no items and call process_order.
        #       Assert status == "invalid" and "errors" key is present.
        pytest.skip("TODO: implement this test")

    # Path 2: DB save failure
    @patch("order_processor.httpx.post")
    def test_db_save_failure(self, mock_post):
        # TODO: Pass a connection that has NO orders table so the INSERT fails.
        #       Assert status == "error".
        pytest.skip("TODO: implement this test")

    # Path 3: successful payment
    @patch("order_processor.httpx.post")
    def test_successful_payment(self, mock_post):
        # TODO: Make mock_post return a response whose .json() is {"id": "PAY-123"}.
        #       Don't forget .raise_for_status should do nothing (default mock).
        #       Assert status == "ok" and payment_id == "PAY-123".
        pytest.skip("TODO: implement this test")

    # Path 4: payment HTTP error (e.g. 402 Payment Required)
    @patch("order_processor.httpx.post")
    def test_payment_http_error(self, mock_post):
        # TODO: Make .raise_for_status() raise httpx.HTTPStatusError("402", request=..., response=...).
        #       Assert status == "payment_failed".
        pytest.skip("TODO: implement this test")

    # Path 5: payment timeout
    @patch("order_processor.httpx.post")
    def test_payment_timeout(self, mock_post):
        # TODO: Set mock_post.side_effect = httpx.TimeoutException("timed out")
        #       Assert status == "payment_timeout".
        pytest.skip("TODO: implement this test")
