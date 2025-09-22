from typing import Dict, Optional
from src.dao.payment_dao import PaymentDAO
from src.services.order_service import OrderService, OrderError

class PaymentError(Exception):
    pass

class PaymentService:
    def __init__(self, dao: Optional[PaymentDAO] = None, order_service: Optional[OrderService] = None):
        self.dao = dao or PaymentDAO()
        self.order_service = order_service or OrderService()

    # CREATE
    def create_payment(self, order_id: int, amount: float) -> Dict:
        if amount <= 0:
            raise PaymentError("Payment amount must be greater than 0")
        return self.dao.create_payment(order_id, amount)

    # READ
    def get_payment(self, order_id: int) -> Dict:
        payment = self.dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentError(f"No payment record found for order {order_id}")
        return payment

    # PROCESS PAYMENT
    def process_payment(self, order_id: int, method: str) -> Dict:
        payment = self.get_payment(order_id)
        if payment["status"] != "PENDING":
            raise PaymentError(f"Cannot process payment with status {payment['status']}")
        updated_payment = self.dao.update_payment(order_id, {"status": "PAID", "method": method})
        self.order_service.complete_order(order_id)
        return updated_payment

    # REFUND
    def refund_payment(self, order_id: int) -> Dict:
        payment = self.get_payment(order_id)
        if payment["status"] != "PAID":
            raise PaymentError(f"Cannot refund payment with status {payment['status']}")
        return self.dao.update_payment(order_id, {"status": "REFUNDED"})

