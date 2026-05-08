"""
Lab 3 — Debugging, Troubleshooting & Documentation
====================================================
A buggy inventory management system. Participants use Copilot to find
and fix bugs, then generate documentation.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


# ── Models ───────────────────────────────────────────────────────────

class Product:
    def __init__(self, sku: str, name: str, price: float, stock: int = 0):
        self.sku = sku
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"Product({self.sku!r}, {self.name!r}, price={self.price}, stock={self.stock})"


class Inventory:
    def __init__(self):
        self._products: dict[str, Product] = {}
        self._transactions: list[dict] = []

    def add_product(self, product: Product) -> None:
        self._products[product.sku] = product
        logger.info(f"Added product {product.sku}")

    def get_product(self, sku: str) -> Optional[Product]:
        return self._products.get(sku)

    def restock(self, sku: str, quantity: int) -> bool:
        """Add stock. Returns True on success."""
        product = self.get_product(sku)
        if product is None:
            return False
        product.stock += quantity
        self._record_transaction(sku, "restock", quantity)
        return True

    def sell(self, sku: str, quantity: int) -> dict:
        """
        Process a sale. Returns dict with status and details.
        """
        product = self.get_product(sku)
        if product is None:
            return {"status": "error", "message": f"Product {sku} not found"}

        if product.stock < quantity:
            return {"status": "error", "message": "Insufficient stock"}

        product.stock -= quantity
        total = product.price * quantity
        self._record_transaction(sku, "sale", quantity)

        return {"status": "ok", "total": total, "remaining_stock": product.stock}

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        """Returns products with stock below threshold."""
        return [p for p in self._products.values() if p.stock < threshold]

    def get_total_value(self) -> float:
        """Calculate total inventory value (price × stock for each product)."""
        total = 0
        for product in self._products.values():
            total += product.price * product.stock
        return total

    def bulk_update_prices(self, adjustment_pct: float) -> int:
        """
        Adjust all prices by a percentage. Returns count of updated products.
        Example: adjustment_pct=10 increases prices by 10%.
        """
        count = 0
        for product in self._products.values():
            product.price = product.price * (1 + adjustment_pct / 100)
            count += 1
        return count

    def export_report(self) -> str:
        """Export inventory as JSON report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_products": len(self._products),
            "total_value": self.get_total_value(),
            "products": [],
        }
        for product in self._products.values():
            report["products"].append({
                "sku": product.sku,
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                "value": product.price * product.stock,
            })
        return json.dumps(report, indent=2)

    def _record_transaction(self, sku: str, txn_type: str, quantity: int) -> None:
        self._transactions.append({
            "sku": sku,
            "type": txn_type,
            "quantity": quantity,
            "timestamp": datetime.now().isoformat(),
        })

    def get_transactions(self, sku: Optional[str] = None, since: Optional[datetime] = None) -> list[dict]:
        """Filter transactions by SKU and/or date."""
        results = self._transactions
        if sku:
            results = [t for t in results if t["sku"] == sku]
        if since:
            results = [t for t in results if datetime.fromisoformat(t["timestamp"]) > since]
        return results
