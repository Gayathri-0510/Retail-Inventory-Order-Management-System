from typing import Optional, List, Dict
from src.config import get_supabase

class CustomerDAO:
    """Data Access Object for Customers table."""

    def __init__(self):
        self._sb = get_supabase()

    # CREATE
    def create_customer(self, name: str, email: str, phone: str, city: str) -> Optional[Dict]:
        payload = {"name": name, "email": email, "phone": phone, "city": city}
        self._sb.table("customers").insert(payload).execute()
        resp = self._sb.table("customers").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None

    # READ
    def get_customer_by_id(self, cust_id: int) -> Optional[Dict]:
        resp = self._sb.table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        resp = self._sb.table("customers").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None

    def list_customers(self, limit: int = 100, city: str | None = None) -> List[Dict]:
        q = self._sb.table("customers").select("*").order("cust_id", desc=False).limit(limit)
        if city:
            q = q.eq("city", city)
        resp = q.execute()
        return resp.data or []

    # UPDATE
    def update_customer(self, cust_id: int, fields: Dict) -> Optional[Dict]:
        self._sb.table("customers").update(fields).eq("cust_id", cust_id).execute()
        resp = self._sb.table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    # DELETE
    def delete_customer(self, cust_id: int) -> Optional[Dict]:
        resp_before = self._sb.table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
        row = resp_before.data[0] if resp_before.data else None
        self._sb.table("customers").delete().eq("cust_id", cust_id).execute()
        return row
