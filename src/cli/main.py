import argparse
from src.services.product_service import ProductService, ProductError
from src.services.customer_service import CustomerService, CustomerError
from src.services.order_service import OrderService, OrderError
from src.services.payment_service import PaymentService, PaymentError
from src.services.report_service import ReportService

class RetailCLI:
    def __init__(self):
        self.product_service = ProductService()
        self.customer_service = CustomerService()
        self.order_service = OrderService()
        self.payment_service = PaymentService(self.order_service)
        self.report_service = ReportService()

    def run(self):
        parser = argparse.ArgumentParser(description="Retail CLI")
        subparsers = parser.add_subparsers(dest="cmd")

        # ------------------- Product -------------------
        product_parser = subparsers.add_parser("product", help="Product operations")
        product_sub = product_parser.add_subparsers(dest="action")

        add_product_parser = product_sub.add_parser("add")
        add_product_parser.add_argument("--name", required=True)
        add_product_parser.add_argument("--sku", required=True)
        add_product_parser.add_argument("--price", type=float, required=True)
        add_product_parser.add_argument("--stock", type=int, default=0)
        add_product_parser.add_argument("--category")

        list_product_parser = product_sub.add_parser("list")
        list_product_parser.add_argument("--category")

        add_product_parser.set_defaults(func=self.product_add)
        list_product_parser.set_defaults(func=self.product_list)

        # ------------------- Customer -------------------
        customer_parser = subparsers.add_parser("customer", help="Customer operations")
        customer_sub = customer_parser.add_subparsers(dest="action")

        add_customer_parser = customer_sub.add_parser("add")
        add_customer_parser.add_argument("--name", required=True)
        add_customer_parser.add_argument("--email", required=True)
        add_customer_parser.add_argument("--phone", required=True)
        add_customer_parser.add_argument("--city", required=True)

        list_customer_parser = customer_sub.add_parser("list")
        list_customer_parser.add_argument("--city")

        add_customer_parser.set_defaults(func=self.customer_add)
        list_customer_parser.set_defaults(func=self.customer_list)

        # ------------------- Order -------------------
        order_parser = subparsers.add_parser("order", help="Order operations")
        order_sub = order_parser.add_subparsers(dest="action")

        create_order_parser = order_sub.add_parser("create")
        create_order_parser.add_argument("--customer_id", type=int, required=True)
        create_order_parser.add_argument("--items", nargs="+", required=True, help="prod_id:quantity")

        list_order_parser = order_sub.add_parser("list")
        list_order_parser.add_argument("--customer_id", type=int, required=True)

        show_order_parser = order_sub.add_parser("show")
        show_order_parser.add_argument("--order_id", type=int, required=True)

        cancel_order_parser = order_sub.add_parser("cancel")
        cancel_order_parser.add_argument("--order_id", type=int, required=True)

        complete_order_parser = order_sub.add_parser("complete")
        complete_order_parser.add_argument("--order_id", type=int, required=True)

        create_order_parser.set_defaults(func=self.order_create)
        list_order_parser.set_defaults(func=self.order_list)
        show_order_parser.set_defaults(func=self.order_show)
        cancel_order_parser.set_defaults(func=self.order_cancel)
        complete_order_parser.set_defaults(func=self.order_complete)

        # ------------------- Payment -------------------
        payment_parser = subparsers.add_parser("payment", help="Payment operations")
        payment_sub = payment_parser.add_subparsers(dest="action")

        create_payment_parser = payment_sub.add_parser("create")
        create_payment_parser.add_argument("--order_id", type=int, required=True)
        create_payment_parser.add_argument("--amount", type=float, required=True)

        process_payment_parser = payment_sub.add_parser("process")
        process_payment_parser.add_argument("--order_id", type=int, required=True)
        process_payment_parser.add_argument("--method", required=True)

        refund_payment_parser = payment_sub.add_parser("refund")
        refund_payment_parser.add_argument("--order_id", type=int, required=True)

        create_payment_parser.set_defaults(func=self.payment_create)
        process_payment_parser.set_defaults(func=self.payment_process)
        refund_payment_parser.set_defaults(func=self.payment_refund)

        # ------------------- Report -------------------
        report_parser = subparsers.add_parser("report", help="Reporting commands")
        report_sub = report_parser.add_subparsers(dest="action")

        top_products_parser = report_sub.add_parser("top_products")
        top_products_parser.add_argument("--top_n", type=int, default=5)

        revenue_parser = report_sub.add_parser("total_revenue_last_month")
        orders_parser = report_sub.add_parser("total_orders_per_customer")
        frequent_parser = report_sub.add_parser("frequent_customers")
        frequent_parser.add_argument("--min_orders", type=int, default=2)

        top_products_parser.set_defaults(func=self.report_run)
        revenue_parser.set_defaults(func=self.report_run)
        orders_parser.set_defaults(func=self.report_run)
        frequent_parser.set_defaults(func=self.report_run)

        args = parser.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()

    # ------------------- Product Handlers -------------------
    def product_add(self, args):
        try:
            product = self.product_service.add_product(
                args.name, args.sku, args.price, args.stock, args.category
            )
            print("Product added:", product)
        except ProductError as e:
            print("Error:", e)

    def product_list(self, args):
        products = self.product_service.list_products(category=args.category)
        print(products)

    # ------------------- Customer Handlers -------------------
    def customer_add(self, args):
        try:
            customer = self.customer_service.add_customer(
                args.name, args.email, args.phone, args.city
            )
            print("Customer added:", customer)
        except CustomerError as e:
            print("Error:", e)

    def customer_list(self, args):
        customers = self.customer_service.list_customers(city=args.city)
        print(customers)

    # ------------------- Order Handlers -------------------
    def order_create(self, args):
        try:
            items = [{"prod_id": int(x.split(":")[0]), "quantity": int(x.split(":")[1])} for x in args.items]
            order = self.order_service.create_order(args.customer_id, items)
            print(f"Order created successfully! Order ID: {order['order_id']}")
        except OrderError as e:
            print("Error:", e)

    def order_list(self, args):
        orders = self.order_service.list_orders(args.customer_id)
        print(orders)

    def order_show(self, args):
        try:
            order = self.order_service.get_order_details(args.order_id)
            print(order)
        except OrderError as e:
            print("Error:", e)

    def order_cancel(self, args):
        try:
            order = self.order_service.cancel_order(args.order_id)
            print("Order cancelled:", order)
        except OrderError as e:
            print("Error:", e)

    def order_complete(self, args):
        try:
            order = self.order_service.complete_order(args.order_id)
            print("Order completed:", order)
        except OrderError as e:
            print("Error:", e)

    # ------------------- Payment Handlers -------------------
    def payment_create(self, args):
        try:
            payment = self.payment_service.create_payment(args.order_id, args.amount)
            print("Payment created:", payment)
        except PaymentError as e:
            print("Error:", e)

    def payment_process(self, args):
        try:
            payment = self.payment_service.process_payment(args.order_id, args.method)
            print("Payment processed:", payment)
        except PaymentError as e:
            print("Error:", e)

    def payment_refund(self, args):
        try:
            payment = self.payment_service.refund_payment(args.order_id)
            print("Payment refunded:", payment)
        except PaymentError as e:
            print("Error:", e)

    # ------------------- Report Handlers -------------------
    def report_run(self, args):
        if args.action == "top_products":
            result = self.report_service.top_selling_products(args.top_n)
        elif args.action == "total_revenue_last_month":
            result = self.report_service.total_revenue_last_month()
        elif args.action == "total_orders_per_customer":
            result = self.report_service.total_orders_per_customer()
        elif args.action == "frequent_customers":
            result = self.report_service.frequent_customers(args.min_orders)
        else:
            print("Invalid report action")
            return
        print(result)


def main():
    cli = RetailCLI()
    cli.run()


if __name__ == "__main__":
    main()
