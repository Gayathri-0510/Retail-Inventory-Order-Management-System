
from typing import Optional, Dict
from src.config import get_supabase

class PaymentDAO:
    """Data Access Object (DAO) for Payments table."""

    def __init__(self):
        self._sb = get_supabase()

    # CREATE
    def create_payment(self, order_id: int, amount: float) -> Optional[Dict]:
        """Insert a pending payment record."""
        payload = {
            "order_id": order_id,
            "amount": amount,
            "status": "PENDING",
            "method": None
        }
        self._sb.table("payments").insert(payload).execute()
        resp = self._sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    # READ
    def get_payment_by_order(self, order_id: int) -> Optional[Dict]:
        resp = self._sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    # UPDATE
    def update_payment(self, order_id: int, fields: Dict) -> Optional[Dict]:
        self._sb.table("payments").update(fields).eq("order_id", order_id).execute()
        resp = self._sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    # DELETE (optional)
    def delete_payment(self, order_id: int) -> Optional[Dict]:
        resp_before = self._sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        row = resp_before.data[0] if resp_before.data else None
        self._sb.table("payments").delete().eq("order_id", order_id).execute()
        return row
