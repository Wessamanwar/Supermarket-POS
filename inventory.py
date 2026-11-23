import tkinter as tk
from tkinter import messagebox, simpledialog
from models import Product


class InventoryManager:
    LOW_STOCK_THRESHOLD = 5

    def __init__(self, app):
        self.app = app

    def add_product(self):
        dlg = tk.Toplevel(self.app)
        dlg.title("Add New Product")
        dlg.geometry("360x280")
        dlg.configure(bg=self.app.BG_MID)
        dlg.transient(self.app)
        dlg.grab_set()

        fields = {}
        for idx, label in enumerate(["Name:", "Category:", "Price ($):", "Stock:"]):
            tk.Label(
                dlg,
                text=label,
                bg=self.app.BG_MID,
                fg=self.app.MUTED,
                font=("Georgia", 10, "bold"),
            ).grid(row=idx, column=0, padx=16, pady=10, sticky="w")
            entry = tk.Entry(dlg, font=("Consolas", 11), width=22)
            entry.grid(row=idx, column=1, padx=10, pady=10)
            fields[label] = entry

        def save():
            try:
                nm = fields["Name:"].get().strip()
                ct = fields["Category:"].get().strip()
                if not nm or not ct:
                    raise ValueError("Empty fields")
                pr = float(fields["Price ($):"].get().strip())
                st = int(fields["Stock:"].get().strip())
                if pr <= 0 or st < 0:
                    raise ValueError("Invalid range")

                self.app.products.append(Product(nm, ct, pr, st))
                self.app.refresh_all()
                dlg.destroy()
                messagebox.showinfo("Success", f"✅ Added: {nm}")
            except ValueError:
                messagebox.showerror("Error", "❌ Please enter valid data!", parent=dlg)

        self.app._make_button(dlg, "✔ Add Product", save).grid(
            row=4, column=0, columnspan=2, pady=14
        )

    def show_inventory(self):
        self.app.refresh_inventory_table()
        self.app.tabs.select(0)
        low_items = self.get_low_stock_items()
        msg = f"Inventory — {len(self.app.products)} products listed."
        if low_items:
            names = ", ".join(f"{p.name} ({p.stock})" for p in low_items)
            msg += f"\n\n⚠️ Low Stock Alert (< {self.LOW_STOCK_THRESHOLD}):\n{names}"
        messagebox.showinfo("Inventory", msg)

    def search_product(self):
        q = simpledialog.askstring(
            "Search", "Search by ID, Name, or Category:", parent=self.app
        )
        if not q or not q.strip():
            return
        q_lower = q.strip().lower()

        matches = [
            p
            for p in self.app.products
            if str(p.product_id) == q_lower
            or q_lower in p.name.lower()
            or q_lower in p.category.lower()
        ]

        if matches:
            self.app.tabs.select(0)
            matched_ids = {str(p.product_id) for p in matches}
            selected_rows = []
            for row_id in self.app.inv_tree.get_children():
                vals = self.app.inv_tree.item(row_id, "values")
                if str(vals[0]) in matched_ids:
                    selected_rows.append(row_id)
            if selected_rows:
                self.app.inv_tree.selection_set(selected_rows)
                self.app.inv_tree.see(selected_rows[0])

            details = "\n".join(
                f"• #{p.product_id} {p.name} [{p.category}] — ${p.price:.2f} (Stock: {p.stock})"
                for p in matches
            )
            messagebox.showinfo(f"Found ({len(matches)})", details)
            return

        messagebox.showwarning("Not Found", f"❌ Not found: {q}")

    def restock(self):
        id_str = simpledialog.askstring(
            "Restock", "Enter Product ID to restock:", parent=self.app
        )
        if id_str is None:
            return
        qty_str = simpledialog.askstring(
            "Restock", "Enter quantity to add:", parent=self.app
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
                    p.stock += qty
                    self.app.refresh_all()
                    messagebox.showinfo("Restocked", f"✅ Restocked: {p.name}")
                    return
            messagebox.showerror("Error", "❌ Product ID not found.")
        except ValueError:
            messagebox.showerror("Error", "❌ Invalid input.")

    def update_price(self):
        id_str = simpledialog.askstring(
            "Update Price", "Enter Product ID to update price:", parent=self.app
        )
        if id_str is None:
            return
        price_str = simpledialog.askstring(
            "Update Price", "Enter new price ($):", parent=self.app
        )
        if price_str is None:
            return

        try:
            pid = int(id_str.strip())
            new_price = float(price_str.strip())
            if new_price <= 0:
                raise ValueError
            for p in self.app.products:
                if p.product_id == pid:
                    old_price = p.price
                    p.price = new_price
                    self.app.refresh_all()
                    messagebox.showinfo(
                        "Price Updated",
                        f"✅ {p.name}: ${old_price:.2f} ➜ ${new_price:.2f}",
                    )
                    return
            messagebox.showerror("Error", "❌ Product ID not found.")
        except ValueError:
            messagebox.showerror("Error", "❌ Invalid price or Product ID.")

    def delete_product(self):
        id_str = simpledialog.askstring(
            "Delete Product", "Enter Product ID to delete:", parent=self.app
        )
        if id_str is None:
            return

        try:
            pid = int(id_str.strip())
            for p in self.app.products:
                if p.product_id == pid:
                    if messagebox.askyesno(
                        "Confirm Delete",
                        f"Are you sure you want to delete '{p.name}'?",
                        parent=self.app,
                    ):
                        self.app.products.remove(p)
                        self.app.refresh_all()
                        messagebox.showinfo("Deleted", f"🗑️ Deleted: {p.name}")
                    return
            messagebox.showerror("Error", "❌ Product ID not found.")
        except ValueError:
            messagebox.showerror("Error", "❌ Invalid Product ID.")

    def get_low_stock_items(self) -> list[Product]:
        return [
            p for p in self.app.products if p.stock < self.LOW_STOCK_THRESHOLD
        ]
