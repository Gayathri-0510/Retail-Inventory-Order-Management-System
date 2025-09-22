# src/services/product_service.py
from typing import List, Dict, Optional
from src.dao.product_dao import ProductDAO

class ProductError(Exception):
    pass

class ProductService:
    def __init__(self, dao: Optional[ProductDAO] = None):
        self.dao = dao or ProductDAO()

    # CREATE
    def add_product(
        self,
        name: str,
        sku: str,
        price: float,
        stock: int = 0,
        category: str | None = None
    ) -> Dict:
        """
        Validate and insert a new product.
        Raises ProductError on validation failure.
        """
        if price <= 0:
            raise ProductError("Price must be greater than 0")
        existing = self.dao.get_product_by_sku(sku)
        if existing:
            raise ProductError(f"SKU already exists: {sku}")
        return self.dao.create_product(name, sku, price, stock, category)

    # READ
    def get_product_by_id(self, prod_id: int) -> Dict:
        p = self.dao.get_product_by_id(prod_id)
        if not p:
            raise ProductError(f"Product not found with id: {prod_id}")
        return p

    def get_product_by_sku(self, sku: str) -> Dict:
        p = self.dao.get_product_by_sku(sku)
        if not p:
            raise ProductError(f"Product not found with SKU: {sku}")
        return p

    def list_products(self, limit: int = 100, category: str | None = None) -> List[Dict]:
        return self.dao.list_products(limit=limit, category=category)

    # UPDATE
    def update_product(self, prod_id: int, fields: Dict) -> Dict:
        if not fields:
            raise ProductError("No fields provided for update")
        p = self.dao.get_product_by_id(prod_id)
        if not p:
            raise ProductError(f"Product not found with id: {prod_id}")
        return self.dao.update_product(prod_id, fields)

    def restock_product(self, prod_id: int, delta: int) -> Dict:
        if delta <= 0:
            raise ProductError("Delta must be positive")
        p = self.dao.get_product_by_id(prod_id)
        if not p:
            raise ProductError("Product not found")
        new_stock = (p.get("stock") or 0) + delta
        return self.dao.update_product(prod_id, {"stock": new_stock})

    # DELETE
    def delete_product(self, prod_id: int) -> Dict:
        p = self.dao.get_product_by_id(prod_id)
        if not p:
            raise ProductError(f"Product not found with id: {prod_id}")
        return self.dao.delete_product(prod_id)

    # CUSTOM
    def get_low_stock(self, threshold: int = 5) -> List[Dict]:
        all_products = self.dao.list_products(limit=1000)
        return [p for p in all_products if (p.get("stock") or 0) <= threshold]
