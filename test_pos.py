import unittest
from models import Product, OrderItem, SaleRecord


class TestSupermarketPOS(unittest.TestCase):
    def test_product_creation(self):
        p = Product("Test Milk", "Dairy", 10.0, 50)
        self.assertEqual(p.name, "Test Milk")
        self.assertEqual(p.price, 10.0)
        self.assertEqual(p.stock, 50)

    def test_order_item_subtotal(self):
        p = Product("Test Bread", "Bakery", 2.5, 20)
        item = OrderItem(p, 4)
        self.assertEqual(item.sub_total(), 10.0)

    def test_sale_record(self):
        sr = SaleRecord(5, 45.50)
        self.assertEqual(sr.items_sold, 5)
        self.assertEqual(sr.revenue, 45.50)


if __name__ == "__main__":
    unittest.main()