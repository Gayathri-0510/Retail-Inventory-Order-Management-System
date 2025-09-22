from typing import List, Dict, Optional
from src.dao.customer_dao import CustomerDAO

class CustomerError(Exception):
    pass

class CustomerService:
    def __init__(self, dao: Optional[CustomerDAO] = None):
        self.dao = dao or CustomerDAO()

    # CREATE
    def add_customer(self, name: str, email: str, phone: str, city: str) -> Dict:
        if self.dao.get_customer_by_email(email):
            raise CustomerError(f"Email already exists: {email}")
        return self.dao.create_customer(name, email, phone, city)

    # READ
    def get_customer_by_id(self, cust_id: int) -> Dict:
        c = self.dao.get_customer_by_id(cust_id)
        if not c:
            raise CustomerError(f"Customer not found with id: {cust_id}")
        return c

    def get_customer_by_email(self, email: str) -> Dict:
        c = self.dao.get_customer_by_email(email)
        if not c:
            raise CustomerError(f"Customer not found with email: {email}")
        return c

    def list_customers(self, city: str | None = None, limit: int = 100) -> List[Dict]:
        return self.dao.list_customers(limit=limit, city=city)

    # UPDATE
    def update_customer(self, cust_id: int, phone: str | None = None, city: str | None = None) -> Dict:
        fields = {}
        if phone:
            fields["phone"] = phone
        if city:
            fields["city"] = city
        if not fields:
            raise CustomerError("No fields to update")
        return self.dao.update_customer(cust_id, fields)

    # DELETE
    def delete_customer(self, cust_id: int, has_orders_func) -> Dict:
        c = self.dao.get_customer_by_id(cust_id)
        if not c:
            raise CustomerError(f"Customer not found with id: {cust_id}")
        if has_orders_func(cust_id):
            raise CustomerError("Cannot delete customer with existing orders")
        return self.dao.delete_customer(cust_id)

    # SEARCH
    def search_customers(self, email: str | None = None, city: str | None = None) -> List[Dict]:
        results = []
        if email:
            c = self.dao.get_customer_by_email(email)
            if c:
                results.append(c)
        if city:
            city_customers = self.dao.list_customers(city=city)
            results.extend([c for c in city_customers if c not in results])
        return results
