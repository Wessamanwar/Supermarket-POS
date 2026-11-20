import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from models import OrderItem, SaleRecord


class SalesManager:
    def __init__(self, app):
        self.app = app

    def add_to_cart(self):
        id_str = simpledialog.askstring(
            "Add to Cart", "Enter Product ID:", parent=self.app
        )
        if id_str is None:
            return
        qty_str = simpledialog.askstring(
            "Add to Cart", "Enter Quantity:", parent=self.app
        )
        if qty_str is None:
            return

        try:
            pid = int(id_str.strip())
            qty = int(qty_str.strip())
            if qty <= 0:
                raise ValueError

            for p in self.app.products:
                if p.product_id == pid:
                    if qty > p.stock:
                        messagebox.showwarning(
                            "Stock", f"❌ Not enough stock! Available: {p.stock}"
                        )
                        return
                    p.stock -= qty
                    for item in self.app.cart:
                        if item.product.product_id == pid:
                            item.qty += qty
                            self.app.refresh_all()
                            return
                    self.app.cart.append(OrderItem(p, qty))
                    self.app.refresh_all()
                    messagebox.showinfo("Added", f"✅ {p.name} x{qty} added to cart.")
                    return
            messagebox.showerror("Error", "❌ Product ID not found.")
        except ValueError:
            messagebox.showerror("Error", "❌ Invalid input. Enter valid numbers.")

    def remove_from_cart(self):
        if not self.app.cart:
            messagebox.showinfo("Cart", "Cart is already empty.")
            return

        id_str = simpledialog.askstring(
            "Remove", "Enter Product ID to remove:", parent=self.app
        )
        if id_str is None:
            return

        try:
            pid = int(id_str.strip())
            for i, item in enumerate(self.app.cart):
                if item.product.product_id == pid:
                    item.product.stock += item.qty
                    self.app.cart.pop(i)
                    self.app.refresh_all()
                    return
            messagebox.showwarning("Cart", "❌ Item not found in cart.")
        except ValueError:
            messagebox.showerror("Error", "❌ Invalid ID entered.")

    def show_cart(self):
        self.app.refresh_cart_table()
        self.app.tabs.select(1)

    def checkout(self):
        if not self.app.cart:
            messagebox.showwarning("Checkout", "❌ Cart is empty!")
            return

        now = datetime.now()
        sub = 0.0
        batch_items = 0

        lines = [
            "╔══════════════════════════════════════╗",
            "║       CARREFOUR SUPERMARKET          ║",
            "║           Official Receipt           ║",
            "╠══════════════════════════════════════╣",
            f"║  Date : {now.strftime('%Y-%m-%d'):<28} ║",
            f"║  Time : {now.strftime('%H:%M:%S'):<28} ║",
            "╠══════════════════════════════════════╣",
            f" {'Item':<14} {'Price':>7}  {'Qty':>4}  {'Total':>9}",
            "──────────────────────────────────────",
        ]

        for item in self.app.cart:
            item_total = item.sub_total()
            sub += item_total
            batch_items += item.qty
            self.app.total_sold += item.qty
            lines.append(
                f" {item.product.name:<14} ${item.product.price:>6.2f}  x{item.qty:<3}  ${item_total:>8.2f}"
            )

        discount = sub * (self.app.discount_percent / 100.0)
        after_discount = sub - discount
        tax = after_discount * 0.10
        total = after_discount + tax
        self.app.total_revenue += total

        self.app.sales_log.append(SaleRecord(batch_items, total))

        lines.extend(
            [
                "──────────────────────────────────────",
                f" Subtotal:                    ${sub:>8.2f}",
                f" Discount ({self.app.discount_percent:.0f}%):              -${discount:>7.2f}",
                f" Tax (10%):                    ${tax:>8.2f}",
                "══════════════════════════════════════",
                f" TOTAL:                       ${total:>8.2f}",
                "╚══════════════════════════════════════╝",
            ]
        )

        self.app._set_receipt_text("\n".join(lines))
        self.app.cart.clear()
        self.app.discount_percent = 0.0
        self.app.refresh_all()
        self.app.tabs.select(2)
        messagebox.showinfo("Checkout", "✅ Checkout complete!")

    def set_discount(self):
        inp = simpledialog.askstring(
            "Discount", "Enter Discount % (0 – 100):", parent=self.app
        )
        if inp is None:
            return
        try:
            d = float(inp.strip())
            if d < 0 or d > 100:
                messagebox.showerror("Error", "❌ Discount must be between 0 and 100!")
                return
            self.app.discount_percent = d
            self.app.refresh_cart_table()
            messagebox.showinfo("Discount", f"🏷 Discount set to {d}%")
        except ValueError:
            messagebox.showerror("Error", "❌ Invalid value.")

    def show_report(self):
        report_txt = (
            "╔══════════════════════════════╗\n"
            "║      DAILY SALES REPORT      ║\n"
            "╠══════════════════════════════╣\n"
            f"║  Revenue : ${self.app.total_revenue:<17.2f}║\n"
            f"║  Items   : {str(self.app.total_sold) + ' items':<18}║\n"
            "╚══════════════════════════════╝"
        )
        messagebox.showinfo("Daily Sales Report", report_txt)

    def track_daily_sales(self):
        dlg = tk.Toplevel(self.app)
        dlg.title("📈 Daily Sales Tracker")
        dlg.geometry("520x400")
        dlg.configure(bg=self.app.BG_MID)

        cols = ("#", "Time", "Items Sold", "Revenue ($)")
        tree = self.app._create_table(dlg, cols)
        for idx, sr in enumerate(self.app.sales_log, start=1):
            tree.insert(
                "", tk.END, values=(idx, sr.time, sr.items_sold, f"{sr.revenue:.2f}")
            )

        self.app._make_button(dlg, "✖ Close", dlg.destroy).pack(pady=8)