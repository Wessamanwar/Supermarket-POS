from datetime import datetime


class Product:
    _counter = 1

    def __init__(self, name: str, category: str, price: float, stock: int):
        self.product_id = Product._counter
        Product._counter += 1
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock


class OrderItem:
    def __init__(self, product: Product, qty: int):
        self.product = product
        self.qty = qty

    def sub_total(self) -> float:
        return self.product.price * self.qty


class SaleRecord:
    def __init__(self, items_sold: int, revenue: float):
        now = datetime.now()
        self.date = now.strftime("%Y-%m-%d")
        self.time = now.strftime("%H:%M:%S")
        self.items_sold = items_sold
        self.revenue = revenue