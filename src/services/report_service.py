from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
from src.dao.report_dao import ReportDAO

class ReportService:
    def __init__(self, dao: ReportDAO = None):
        self.dao = dao or ReportDAO()

    # Top N selling products by total quantity
    def top_selling_products(self, top_n: int = 5) -> List[Dict]:
        product_sales = defaultdict(int)

        # Sum quantities per prod_id across all orders
        for order in self.dao.get_all_orders():
            order_id = order.get("order_id")
            if order_id is None:
                continue
            items = self.dao.get_order_items(order_id)
            for item in items:
                pid = item.get("prod_id")
                qty = item.get("quantity") or item.get("qty") or 0
                if pid is None:
                    continue
                try:
                    product_sales[pid] += int(qty)
                except Exception:
                    # ignore malformed quantity values
                    continue

        # Sort by total qty desc and take top_n
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # Map product ids to names (if available)
        all_products = {p["prod_id"]: p for p in self.dao.get_all_products() if p.get("prod_id") is not None}
        result = []
        for pid, qty in sorted_products:
            prod = all_products.get(pid)
            result.append({
                "prod_id": pid,
                "product": prod.get("name") if prod else None,
                "quantity": qty
            })
        return result

    # Total revenue in the last month (calendar month before current)
    def total_revenue_last_month(self) -> float:
        today = datetime.utcnow()
        first_day_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_last_month = first_day_this_month - timedelta(seconds=1)
        first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total = 0.0
        for order in self.dao.get_all_orders():
            # Orders table uses `order_date` in your schema
            raw_date = order.get("order_date") or order.get("created_at") or order.get("order_date_iso")
            if not raw_date:
                continue
            order_date = self._parse_iso_datetime_safe(raw_date)
            if not order_date:
                continue
            # Compare in UTC
            if first_day_last_month <= order_date <= last_day_last_month:
                total_amount = order.get("total_amount") or 0
                try:
                    total += float(total_amount)
                except Exception:
                    continue
        return total

    # Total orders per customer (by cust_id)
    def total_orders_per_customer(self) -> List[Dict]:
        counts = defaultdict(int)
        for order in self.dao.get_all_orders():
            cust_id = order.get("cust_id") or order.get("customer_id")
            if cust_id is None:
                continue
            counts[cust_id] += 1
        return [{"cust_id": cid, "total_orders": c} for cid, c in counts.items()]

    # Customers with more than `min_orders` orders (default: more than 2)
    def frequent_customers(self, min_orders: int = 2) -> List[Dict]:
        # requirement: customers who placed more than 2 orders
        return [c for c in self.total_orders_per_customer() if c["total_orders"] > min_orders]

    # ---------- Helpers ----------
    def _parse_iso_datetime_safe(self, s):
        """
        Parse ISO datetime strings returned from Supabase.
        Supabase may return '2025-09-22T10:30:00Z' or without 'Z'.
        Return a timezone-naive UTC datetime on success, or None on failure.
        """
        if isinstance(s, datetime):
            return s
        if not isinstance(s, str):
            return None
        # remove trailing Z and fractional timezone if any, keep as UTC naive
        try:
            if s.endswith("Z"):
                s = s[:-1]
            # Some timestamps include +00:00 or other offsets -> remove offset for fromisoformat
            # If there is a '+' or '-' for offset after the time portion, split it off
            for sign in ("+", "-"):
                # find sign after date portion
                idx = s.find(sign, 10)  # offset signs appear after YYYY-MM-DDT...
                if idx != -1:
                    s = s[:idx]
                    break
            # fromisoformat can parse 'YYYY-MM-DDTHH:MM:SS' and 'YYYY-MM-DDTHH:MM:SS.ssssss'
            return datetime.fromisoformat(s)
        except Exception:
            return None
