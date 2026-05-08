import datetime
import json
import os
import sqlite3
from dataclasses import dataclass, field
from typing import Optional
import httpx


# ── Domain models ────────────────────────────────────────────────────

@dataclass
class OrderItem:
    product_id: str
    name: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order:
    order_id: str
    customer_email: str
    items: list[OrderItem] = field(default_factory=list)
    discount_pct: float = 0.0
    created_at: Optional[datetime.datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def total(self) -> float:
        return self.subtotal * (1 - self.discount_pct / 100)


# ── Validation ───────────────────────────────────────────────────────

def validate_order(order: Order) -> list[str]:
    """Returns a list of validation errors. Empty list = valid."""
    errors = []
    if not order.order_id or not order.order_id.strip():
        errors.append("order_id is required")
    if not order.customer_email or "@" not in order.customer_email:
        errors.append("customer_email is invalid")
    if not order.items:
        errors.append("order must contain at least one item")
    for item in order.items:
        if item.quantity <= 0:
            errors.append(f"item {item.product_id}: quantity must be positive")
        if item.unit_price < 0:
            errors.append(f"item {item.product_id}: unit_price cannot be negative")
    if not (0 <= order.discount_pct <= 100):
        errors.append("discount_pct must be between 0 and 100")
    return errors


# ── Database layer ───────────────────────────────────────────────────

def get_db_connection(db_path: str = "orders.db") -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def save_order(order: Order, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Saves order to DB. Returns True on success."""
    _conn = conn or get_db_connection()
    try:
        cursor = _conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO orders (order_id, customer_email, total, created_at) VALUES (?, ?, ?, ?)",
            (order.order_id, order.customer_email, order.total, order.created_at.isoformat()),
        )
        _conn.commit()
        return True
    except Exception:
        return False
    finally:
        if conn is None:
            _conn.close()


def load_order(order_id: str, conn: Optional[sqlite3.Connection] = None) -> Optional[dict]:
    _conn = conn or get_db_connection()
    try:
        cursor = _conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        if row:
            return {"order_id": row[0], "customer_email": row[1], "total": row[2], "created_at": row[3]}
        return None
    finally:
        if conn is None:
            _conn.close()


# ── Payment client ───────────────────────────────────────────────────

PAYMENT_API_URL = os.getenv("PAYMENT_API_URL", "https://api.payments.example.com")


def charge_customer(order: Order, card_token: str) -> dict:
    """Calls external payment API. Returns response dict."""
    payload = {
        "amount": round(order.total * 100),  # pence/cents
        "currency": "GBP",
        "card_token": card_token,
        "reference": order.order_id,
        "customer": order.customer_email,
    }
    response = httpx.post(
        f"{PAYMENT_API_URL}/v1/charge",
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


# ── Async notification ───────────────────────────────────────────────

NOTIFICATION_URL = os.getenv("NOTIFICATION_URL", "https://notify.example.com")


async def notify_customer(order: Order, message: str, client: Optional[httpx.AsyncClient] = None) -> bool:
    """Sends async notification. Returns True on success."""
    _client = client or httpx.AsyncClient()
    try:
        response = await _client.post(
            f"{NOTIFICATION_URL}/send",
            json={"to": order.customer_email, "body": message, "ref": order.order_id},
        )
        return response.status_code == 200
    except httpx.HTTPError:
        return False
    finally:
        if client is None:
            await _client.aclose()


# ── Main orchestration ───────────────────────────────────────────────

def process_order(order: Order, card_token: str, conn: Optional[sqlite3.Connection] = None) -> dict:
    """
    Full order processing pipeline:
    1. Validate
    2. Save to DB
    3. Charge payment
    Returns status dict.
    """
    errors = validate_order(order)
    if errors:
        return {"status": "invalid", "errors": errors}

    saved = save_order(order, conn)
    if not saved:
        return {"status": "error", "message": "Failed to save order"}

    try:
        payment = charge_customer(order, card_token)
        return {"status": "ok", "payment_id": payment.get("id"), "total": order.total}
    except httpx.HTTPStatusError as e:
        return {"status": "payment_failed", "message": str(e)}
    except httpx.TimeoutException:
        return {"status": "payment_timeout"}
