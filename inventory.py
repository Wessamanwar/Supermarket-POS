import tkinter as tk
from tkinter import messagebox, simpledialog
from models import Product


class InventoryManager:
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
        messagebox.showinfo(
            "Inventory", f"Inventory — {len(self.app.products)} products listed."
        )

    def search_product(self):
        q = simpledialog.askstring("Search", "Search by ID or Name:", parent=self.app)
        if not q or not q.strip():
            return
        q = q.strip()

        for p in self.app.products:
            if str(p.product_id) == q or p.name.lower() == q.lower():
                self.app.tabs.select(0)
                for row_id in self.app.inv_tree.get_children():
                    vals = self.app.inv_tree.item(row_id, "values")
                    if str(vals[0]) == str(p.product_id):
                        self.app.inv_tree.selection_set(row_id)
                        self.app.inv_tree.see(row_id)
                        break
                messagebox.showinfo(
                    "Found",
                    f"Found ➜ {p.name}\nPrice: ${p.price:.2f}\nStock: {p.stock}",
                )
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