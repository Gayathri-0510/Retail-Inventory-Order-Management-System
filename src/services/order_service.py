from src.dao.order_dao import OrderDAO
from src.services.product_service import ProductService, ProductError

class OrderError(Exception):
    pass

class OrderService:
    def __init__(self):
        self.dao = OrderDAO()
        self.product_service = ProductService()

    # CREATE
    def create_order(self, cust_id: int, items: list[dict]):
        total_amount = 0
        # Validate products and calculate total
        for item in items:
            product = self.product_service.get_product_by_id(item["prod_id"])
            if product["stock"] < item["quantity"]:
                raise OrderError(f"Not enough stock for product {product['name']}")
            total_amount += product["price"] * item["quantity"]

        # Deduct stock
        for item in items:
            product = self.product_service.get_product_by_id(item["prod_id"])
            new_stock = product["stock"] - item["quantity"]
            self.product_service.update_product(
                prod_id=item["prod_id"],
                fields={"stock": new_stock}
            )

        order_id = self.dao.create_order(cust_id, items, total_amount)
        return self.get_order_details(order_id)

    # READ
    def get_order_details(self, order_id: int):
        order = self.dao.get_order(order_id)
        if not order:
            raise OrderError(f"Order {order_id} not found")
        return order

    def list_orders(self, cust_id: int):
        return self.dao.list_orders(cust_id)

    # CANCEL
    def cancel_order(self, order_id: int):
        order = self.get_order_details(order_id)
        if order["status"] != "PLACED":
            raise OrderError("Only orders with status 'PLACED' can be cancelled")
        # Restore stock
        for item in order["items"]:
            product = self.product_service.get_product_by_id(item["prod_id"])
            self.product_service.update_product(
                prod_id=item["prod_id"],
                fields={"stock": product["stock"] + item["quantity"]}
            )
        return self.dao.update_order_status(order_id, "CANCELLED")

    # COMPLETE
    def complete_order(self, order_id: int):
        order = self.get_order_details(order_id)
        if order["status"] != "PLACED":
            raise OrderError("Only orders with status 'PLACED' can be completed")
        return self.dao.update_order_status(order_id, "COMPLETED")
