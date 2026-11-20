import json
import os
from datetime import datetime


class Product:
    _counter = 1

    def __init__(
        self,
        name: str,
        category: str,
        price: float,
        stock: int,
        product_id: int | None = None,
    ):
        if price < 0 or stock < 0:
            raise ValueError("Price and stock cannot be negative.")
        if product_id is not None:
            self.product_id = product_id
            if product_id >= Product._counter:
                Product._counter = product_id + 1
        else:
            self.product_id = Product._counter
            Product._counter += 1

        self.name = name
        self.category = category
        self.price = float(price)
        self.stock = int(stock)

    def is_low_stock(self, threshold: int = 5) -> bool:
        return self.stock < threshold

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        return cls(
            name=data["name"],
            category=data["category"],
            price=data["price"],
            stock=data["stock"],
            product_id=data["product_id"],
        )


class OrderItem:
    def __init__(self, product: Product, qty: int):
        if qty <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.product = product
        self.qty = qty

    def sub_total(self) -> float:
        return round(self.product.price * self.qty, 2)


class SaleRecord:
    def __init__(
        self,
        items_sold: int,
        revenue: float,
        date: str | None = None,
        time: str | None = None,
    ):
        now = datetime.now()
        self.date = date or now.strftime("%Y-%m-%d")
        self.time = time or now.strftime("%H:%M:%S")
        self.items_sold = int(items_sold)
        self.revenue = round(float(revenue), 2)

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "time": self.time,
            "items_sold": self.items_sold,
            "revenue": self.revenue,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SaleRecord":
        return cls(
            items_sold=data["items_sold"],
            revenue=data["revenue"],
            date=data.get("date"),
            time=data.get("time"),
        )


class DataStorage:
    DEFAULT_FILE = "pos_data.json"

    @staticmethod
    def save_state(
        products: list[Product],
        sales_log: list[SaleRecord],
        total_revenue: float,
        total_sold: int,
        filepath: str = DEFAULT_FILE,
    ) -> None:
        payload = {
            "total_revenue": round(total_revenue, 2),
            "total_sold": total_sold,
            "products": [p.to_dict() for p in products],
            "sales_log": [s.to_dict() for s in sales_log],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

    @staticmethod
    def load_state(filepath: str = DEFAULT_FILE) -> dict | None:
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        Product._counter = 1
        products = [Product.from_dict(p) for p in data.get("products", [])]
        sales_log = [SaleRecord.from_dict(s) for s in data.get("sales_log", [])]
        return {
            "products": products,
            "sales_log": sales_log,
            "total_revenue": data.get("total_revenue", 0.0),
            "total_sold": data.get("total_sold", 0),
        }