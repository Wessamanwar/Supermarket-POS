import tkinter as tk
from tkinter import messagebox, simpledialog
import math

from models import OrderItem, SaleRecord


class SalesManager:
    def __init__(self, app):
        self.app = app

    def add_to_cart(self):
        id_str = simpledialog.askstring(
            "Add to Cart",
            "Enter Product ID:",
            parent=self.app
        )

        if id_str is None:
            return

        qty_str = simpledialog.askstring(
            "Add to Cart",
            "Enter Quantity:",
            parent=self.app
        )

        if qty_str is None:
            return

        try:
            pid = int(id_str.strip())
            qty = int(qty_str.strip())

            if pid <= 0 or qty <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter valid positive numbers."
            )
            return

        for product in self.app.products:

            if product.product_id == pid:

                if qty > product.stock:
                    messagebox.showwarning(
                        "Stock",
                        f"Not enough stock!\nAvailable: {product.stock}"
                    )
                    return

                product.stock -= qty

                for item in self.app.cart:

                    if item.product.product_id == pid:
                        item.qty += qty
                        self.app.refresh_all()

                        messagebox.showinfo(
                            "Added",
                            f"{product.name} quantity updated."
                        )
                        return

                self.app.cart.append(
                    OrderItem(product, qty)
                )

                self.app.refresh_all()

                messagebox.showinfo(
                    "Added",
                    f"{product.name} x{qty} added to cart."
                )
                return

        messagebox.showerror(
            "Error",
            "Product ID not found."
        )

    def remove_from_cart(self):
        if not self.app.cart:
            messagebox.showinfo(
                "Cart",
                "Cart is already empty."
            )
            return

        id_str = simpledialog.askstring(
            "Remove",
            "Enter Product ID to remove:",
            parent=self.app
        )

        if id_str is None:
            return

        try:
            pid = int(id_str.strip())

            if pid <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter a valid Product ID."
            )
            return

        for index, item in enumerate(self.app.cart):

            if item.product.product_id == pid:

                item.product.stock += item.qty

                self.app.cart.pop(index)

                self.app.refresh_all()

                messagebox.showinfo(
                    "Cart",
                    "Item removed and stock restored."
                )
                return

        messagebox.showwarning(
            "Cart",
            "Item not found in cart."
        )

    def clear_cart(self):
        if not self.app.cart:
            messagebox.showinfo(
                "Cart",
                "Cart is already empty."
            )
            return

        confirm = messagebox.askyesno(
            "Clear Cart",
            "Return all cart items back to stock?"
        )

        if not confirm:
            return

        for item in self.app.cart:
            item.product.stock += item.qty

        self.app.cart.clear()
        self.app.discount_percent = 0.0

        self.app.refresh_all()

        messagebox.showinfo(
            "Cleared",
            "Cart cleared and stock restored."
        )

    def show_cart(self):
        self.app.refresh_cart_table()
        self.app.tabs.select(1)

    def checkout(self):
        if not self.app.cart:
            messagebox.showwarning(
                "Checkout",
                "Cart is empty!"
            )
            return

        payment_method = simpledialog.askstring(
            "Payment Method",
            "Enter Payment Method (Cash / Card):",
            initialvalue="Cash",
            parent=self.app
        )

        if payment_method is None:
            return

        payment_method = payment_method.strip().capitalize()

        if payment_method not in ("Cash", "Card"):
            messagebox.showerror(
                "Error",
                "Payment method must be Cash or Card."
            )
            return

        # Calculate subtotal
        sub = sum(
            item.sub_total()
            for item in self.app.cart
        )

        batch_items = sum(
            item.qty
            for item in self.app.cart
        )

        # Validate discount
        discount_percent = self.app.discount_percent

        if (
            not math.isfinite(discount_percent)
            or discount_percent < 0
            or discount_percent > 100
        ):
            messagebox.showerror(
                "Error",
                "Invalid discount percentage."
            )
            return

        discount = sub * (discount_percent / 100.0)

        after_discount = sub - discount

        tax = after_discount * 0.10

        total = round(after_discount + tax, 2)

        cash_paid = total
        change = 0.0

        # Cash payment
        if payment_method == "Cash":

            paid_str = simpledialog.askstring(
                "Cash Payment",
                f"Total is ${total:.2f}.\n"
                "Enter cash tendered ($):",
                parent=self.app
            )

            if paid_str is None:
                return

            try:
                cash_paid = float(paid_str.strip())

                if not math.isfinite(cash_paid):
                    raise ValueError

                if cash_paid < total:
                    messagebox.showerror(
                        "Insufficient Cash",
                        "Cash is less than the total!"
                    )
                    return

                change = round(cash_paid - total, 2)

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Please enter a valid cash amount."
                )
                return

        # Update sales information
        self.app.total_sold += batch_items

        self.app.total_revenue = round(
            self.app.total_revenue + total,
            2
        )

        self.app.sales_log.append(
            SaleRecord(batch_items, total)
        )

        # Create receipt
        receipt_txt = self.app.report_mgr.build_receipt(
            cart=self.app.cart,
            sub=sub,
            discount_percent=discount_percent,
            discount_amount=discount,
            tax=tax,
            total=total,
            payment_method=payment_method,
            cash_paid=cash_paid,
            change=change
        )

        self.app._set_receipt_text(receipt_txt)

        self.app.report_mgr.save_receipt_txt()

        # Clear cart after successful checkout
        self.app.cart.clear()

        self.app.discount_percent = 0.0

        self.app.refresh_all()

        self.app.tabs.select(2)

        messagebox.showinfo(
            "Checkout",
            f"Checkout complete!\nChange: ${change:.2f}"
        )

    def set_discount(self):
        inp = simpledialog.askstring(
            "Discount",
            "Enter Discount % (0 - 100):",
            parent=self.app
        )

        if inp is None:
            return

        try:
            discount = float(inp.strip())

            if not math.isfinite(discount):
                raise ValueError

            if discount < 0 or discount > 100:
                messagebox.showerror(
                    "Error",
                    "Discount must be between 0 and 100!"
                )
                return

            self.app.discount_percent = discount

            self.app.refresh_cart_table()

            messagebox.showinfo(
                "Discount",
                f"Discount set to {discount}%"
            )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter a valid discount value."
            )

    def show_report(self):
        report_txt = self.app.report_mgr.format_daily_summary(
            self.app.sales_log,
            self.app.total_revenue,
            self.app.total_sold
        )

        messagebox.showinfo(
            "Daily Sales Report",
            report_txt
        )

    def track_daily_sales(self):
        dlg = tk.Toplevel(self.app)

        dlg.title("Daily Sales Tracker")
        dlg.geometry("520x400")
        dlg.configure(bg=self.app.BG_MID)

        cols = (
            "#",
            "Time",
            "Items Sold",
            "Revenue ($)"
        )

        tree = self.app._create_table(dlg, cols)

        for idx, sale in enumerate(
            self.app.sales_log,
            start=1
        ):
            tree.insert(
                "",
                tk.END,
                values=(
                    idx,
                    sale.time,
                    sale.items_sold,
                    f"{sale.revenue:.2f}"
                )
            )

        self.app._make_button(
            dlg,
            "Close",
            dlg.destroy
        ).pack(pady=8)
