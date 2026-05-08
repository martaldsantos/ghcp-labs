"""
SOLUTION — Part 1: Mocking HTTP & DB
=====================================
All 5 code paths of process_order() covered.
"""

import sqlite3
from unittest.mock import patch, MagicMock
import httpx
from order_processor import Order, OrderItem, process_order


def make_test_order(**overrides):
    defaults = dict(
        order_id="ORD-001",
        customer_email="test@example.com",
        items=[OrderItem("PROD-1", "Widget", 2, 10.00)],
    )
    defaults.update(overrides)
    return Order(**defaults)


def setup_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE orders "
        "(order_id TEXT PRIMARY KEY, customer_email TEXT, total REAL, created_at TEXT)"
    )
    return conn


class TestProcessOrder:

    # Path 1: invalid order
    def test_invalid_order_returns_errors(self):
        order = make_test_order(items=[])
        result = process_order(order, "tok_xxx")
        assert result["status"] == "invalid"
        assert "errors" in result
        assert any("at least one item" in e for e in result["errors"])

    # Path 2: DB save failure (no table → INSERT fails)
    @patch("order_processor.httpx.post")
    def test_db_save_failure(self, mock_post):
        order = make_test_order()
        empty_conn = sqlite3.connect(":memory:")  # no table created
        result = process_order(order, "tok_xxx", conn=empty_conn)
        assert result["status"] == "error"
        assert "Failed to save order" in result["message"]
        empty_conn.close()

    # Path 3: successful payment
    @patch("order_processor.httpx.post")
    def test_successful_payment(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "PAY-123"}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        order = make_test_order()
        conn = setup_db()
        result = process_order(order, "tok_xxx", conn=conn)

        assert result["status"] == "ok"
        assert result["payment_id"] == "PAY-123"
        assert result["total"] == 20.00
        conn.close()

    # Path 4: payment HTTP error (402)
    @patch("order_processor.httpx.post")
    def test_payment_http_error(self, mock_post):
        mock_resp = MagicMock()
        mock_request = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "402 Payment Required", request=mock_request, response=mock_resp
        )
        mock_post.return_value = mock_resp

        order = make_test_order()
        conn = setup_db()
        result = process_order(order, "tok_xxx", conn=conn)

        assert result["status"] == "payment_failed"
        assert "402" in result["message"]
        conn.close()

    # Path 5: payment timeout
    @patch("order_processor.httpx.post")
    def test_payment_timeout(self, mock_post):
        mock_post.side_effect = httpx.TimeoutException("timed out")

        order = make_test_order()
        conn = setup_db()
        result = process_order(order, "tok_xxx", conn=conn)

        assert result["status"] == "payment_timeout"
        conn.close()
