from typing import List, Dict
from src.config import get_supabase
from collections import defaultdict

class ReportDAO:
    """DAO for reporting queries."""

    def __init__(self):
        self._sb = get_supabase()

    def get_all_orders(self) -> List[Dict]:
        # Returns raw orders rows (contains at least order_id, cust_id, order_date, status, total_amount)
        resp = self._sb.table("orders").select("*").execute()
        return resp.data or []

    def get_order_items(self, order_id: int) -> List[Dict]:
        # Returns items rows (contains at least item_id, order_id, prod_id, quantity, price)
        resp = self._sb.table("order_items").select("*").eq("order_id", order_id).execute()
        return resp.data or []

    def get_all_products(self) -> List[Dict]:
        resp = self._sb.table("products").select("*").execute()
        return resp.data or []

    def get_all_customers(self) -> List[Dict]:
        resp = self._sb.table("customers").select("*").execute()
        return resp.data or []
