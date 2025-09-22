from src.config import get_supabase
from src.services.product_service import ProductService

class OrderDAO:
    """DAO for Orders table."""
    def __init__(self):
        self._sb = get_supabase()
        self.product_service = ProductService()

    # CREATE
    def create_order(self, cust_id: int, items: list[dict], total_amount: float):
        # Insert order
        order_payload = {
            "cust_id": cust_id,
            "status": "PLACED",
            "total_amount": total_amount
        }
        resp = self._sb.table("orders").insert(order_payload).execute()
        if not resp.data:
            raise Exception(f"Order creation failed: {resp.data}")
        order_id = resp.data[0]["order_id"]

        # Insert order_items with price
        for item in items:
            product = self.product_service.get_product_by_id(item["prod_id"])
            resp_item = self._sb.table("order_items").insert({
                "order_id": order_id,
                "prod_id": item["prod_id"],
                "quantity": item["quantity"],
                "price": product["price"]
            }).execute()
            if not resp_item.data:
                raise Exception(f"Failed to insert order item: {item}")

        return order_id

    # READ
    def get_order(self, order_id: int):
        """Fetch order along with its items."""
        order_resp = self._sb.table("orders").select("*").eq("order_id", order_id).execute()
        if not order_resp.data:
            return None
        order = order_resp.data[0]

        items_resp = self._sb.table("order_items").select("*").eq("order_id", order_id).execute()
        order["items"] = items_resp.data or []
        return order

    def list_orders(self, cust_id: int):
        resp = self._sb.table("orders").select("*").eq("cust_id", cust_id).execute()
        return resp.data or []

    # UPDATE
    def update_order_status(self, order_id: int, status: str):
        resp = self._sb.table("orders").update({"status": status}).eq("order_id", order_id).execute()
        if not resp.data:
            raise Exception(f"Failed to update order status: {resp.data}")
        return resp.data[0]
