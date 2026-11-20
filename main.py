import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import Product, OrderItem, SaleRecord
from inventory import InventoryManager
from sales import SalesManager


class SupermarketPOS(tk.Tk):
    BG_DEEP = "#F5F0FC"
    BG_MID = "#E5D9F8"
    BG_LIGHT = "#B48DE8"
    PURPLE = "#6D28D9"
    PURPLE_DARK = "#5B21B6"
    PURPLE_HOVER = "#8B5CF6"
    CREAM = "#FAF7FF"
    MUTED = "#4C1D95"

    def __init__(self):
        super().__init__()
        self.title("Carrefour POS — Point of Sale System")
        self.state("zoomed")
        self.minsize(960, 640)
        self.configure(bg=self.BG_DEEP)

        # System State
        self.products: list[Product] = []
        self.cart: list[OrderItem] = []
        self.sales_log: list[SaleRecord] = []
        self.total_revenue = 0.0
        self.total_sold = 0
        self.discount_percent = 0.0

        # Managers
        self.inventory_mgr = InventoryManager(self)
        self.sales_mgr = SalesManager(self)

        self._setup_styles()
        self._load_default_products()
        self._build_header()
        self._build_button_bar()
        self._build_tabs()
        self._start_clock()

        self.refresh_all()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=self.BG_DEEP, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=self.BG_MID,
            foreground=self.PURPLE_DARK,
            font=("Georgia", 11, "bold"),
            padding=[14, 6],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.PURPLE)],
            foreground=[("selected", self.CREAM)],
        )
        style.configure(
            "Treeview",
            background=self.CREAM,
            fieldbackground=self.CREAM,
            foreground="#1F1135",
            rowheight=28,
            font=("Consolas", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=self.BG_MID,
            foreground=self.PURPLE_DARK,
            font=("Georgia", 10, "bold"),
        )

    def _load_default_products(self):
        defaults = [
            ("Milk 1L", "Dairy", 2.50, 80),
            ("Bread Loaf", "Bakery", 1.80, 100),
            ("Orange Juice", "Beverages", 3.20, 60),
            ("Chicken 1kg", "Meat", 7.50, 40),
            ("Rice 2kg", "Grains", 4.90, 75),
            ("Eggs x12", "Dairy", 3.00, 50),
            ("Olive Oil", "Condiments", 8.75, 35),
            ("Chips 150g", "Snacks", 1.50, 120),
            ("Shampoo 400ml", "Hygiene", 5.30, 45),
            ("Mineral Water", "Beverages", 0.90, 200),
        ]
        for item in defaults:
            self.products.append(Product(*item))

    def _build_header(self):
        header = tk.Frame(self, bg=self.BG_LIGHT, height=62, padx=18, pady=8)
        header.pack(fill=tk.X, side=tk.TOP)

        logo_frame = tk.Frame(header, bg=self.BG_LIGHT)
        logo_frame.pack(side=tk.LEFT)

        tk.Label(
            logo_frame,
            text="🛒 CARREFOUR",
            bg=self.BG_LIGHT,
            fg=self.CREAM,
            font=("Georgia", 20, "bold"),
        ).pack(side=tk.LEFT)
        tk.Label(
            logo_frame,
            text="  Point of Sale System",
            bg=self.BG_LIGHT,
            fg=self.MUTED,
            font=("Georgia", 11, "italic"),
        ).pack(side=tk.LEFT, pady=(6, 0))

        stats_frame = tk.Frame(header, bg=self.BG_LIGHT)
        stats_frame.pack(side=tk.RIGHT, pady=6)

        self.rev_var = tk.StringVar(value="Revenue: $0.00")
        self.sold_var = tk.StringVar(value="Sold: 0 items")
        self.prod_var = tk.StringVar(value="Products: 10")
        self.cart_var = tk.StringVar(value="Cart: 0 items")
        self.time_var = tk.StringVar(value="--:--:--")

        stat_vars = [
            self.rev_var,
            self.sold_var,
            self.prod_var,
            self.cart_var,
            self.time_var,
        ]
        for idx, var in enumerate(stat_vars):
            tk.Label(
                stats_frame,
                textvariable=var,
                bg=self.BG_LIGHT,
                fg=self.CREAM,
                font=("Consolas", 10, "bold"),
            ).pack(side=tk.LEFT, padx=6)
            if idx < len(stat_vars) - 1:
                tk.Label(
                    stats_frame, text="│", bg=self.BG_LIGHT, fg=self.MUTED
                ).pack(side=tk.LEFT)

    def _start_clock(self):
        self.time_var.set(datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._start_clock)

    def _build_button_bar(self):
        bar = tk.Frame(self, bg=self.BG_MID, pady=6)
        bar.pack(fill=tk.X, side=tk.BOTTOM)

        row1 = tk.Frame(bar, bg=self.BG_MID)
        row1.pack(pady=3)
        row2 = tk.Frame(bar, bg=self.BG_MID)
        row2.pack(pady=3)

        buttons_r1 = [
            ("➕ Add Item", self.inventory_mgr.add_product),
            ("📦 Inventory", self.inventory_mgr.show_inventory),
            ("🔍 Search", self.inventory_mgr.search_product),
            ("🛒 Add to Cart", self.sales_mgr.add_to_cart),
            ("✖ Remove", self.sales_mgr.remove_from_cart),
            ("🛍 View Cart", self.sales_mgr.show_cart),
        ]
        buttons_r2 = [
            ("💳 Checkout", self.sales_mgr.checkout),
            ("📥 Restock", self.inventory_mgr.restock),
            ("📊 Report", self.sales_mgr.show_report),
            ("🏷 Discount", self.sales_mgr.set_discount),
            ("📈 Daily Sales", self.sales_mgr.track_daily_sales),
            ("🚪 Exit", self.exit_with_summary),
        ]

        for text, cmd in buttons_r1:
            self._make_button(row1, text, cmd).pack(side=tk.LEFT, padx=5)
        for text, cmd in buttons_r2:
            self._make_button(row2, text, cmd).pack(side=tk.LEFT, padx=5)

    def _make_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.PURPLE,
            fg=self.CREAM,
            activebackground=self.PURPLE_HOVER,
            activeforeground=self.CREAM,
            font=("Georgia", 10, "bold"),
            width=14,
            height=1,
            pady=4,
            relief=tk.FLAT,
            cursor="hand2",
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=self.PURPLE_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.PURPLE))
        return btn

    def _build_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 4))

        inv_tab = tk.Frame(self.tabs, bg=self.BG_DEEP, padx=10, pady=10)
        self.tabs.add(inv_tab, text="📦  Inventory")
        inv_cols = ("ID", "Name", "Category", "Price ($)", "Stock")
        self.inv_tree = self._create_table(inv_tab, inv_cols)

        cart_tab = tk.Frame(self.tabs, bg=self.BG_DEEP, padx=10, pady=10)
        self.tabs.add(cart_tab, text="🛒  Cart")
        cart_cols = ("ID", "Name", "Price ($)", "Qty", "Subtotal ($)")
        self.cart_tree = self._create_table(cart_tab, cart_cols)

        footer = tk.Frame(cart_tab, bg=self.BG_MID, pady=8, padx=14)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.discount_info_var = tk.StringVar(
            value="Subtotal: $0.00  |  Discount: 0%  |  Est. Total: $0.00"
        )
        tk.Label(
            footer,
            textvariable=self.discount_info_var,
            bg=self.BG_MID,
            fg=self.MUTED,
            font=("Consolas", 11, "bold"),
        ).pack(side=tk.RIGHT)

        rec_tab = tk.Frame(self.tabs, bg=self.BG_DEEP, padx=10, pady=10)
        self.tabs.add(rec_tab, text="🧾  Receipt")
        self.receipt_text = tk.Text(
            rec_tab,
            bg=self.CREAM,
            fg=self.PURPLE_DARK,
            font=("Consolas", 11),
            padx=16,
            pady=16,
            state=tk.DISABLED,
        )
        self.receipt_text.pack(fill=tk.BOTH, expand=True)
        self._set_receipt_text(
            "\n\n\n         No receipt yet.\n         Complete a checkout to see it here."
        )

    def _create_table(self, parent, columns):
        frame = tk.Frame(parent, bg=self.BG_DEEP)
        frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=140)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def exit_with_summary(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()

    def _set_receipt_text(self, text: str):
        self.receipt_text.config(state=tk.NORMAL)
        self.receipt_text.delete("1.0", tk.END)
        self.receipt_text.insert(tk.END, text)
        self.receipt_text.config(state=tk.DISABLED)

    def refresh_all(self):
        self.refresh_inventory_table()
        self.refresh_cart_table()
        self.update_dashboard()

    def refresh_inventory_table(self):
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
        for p in self.products:
            self.inv_tree.insert(
                "",
                tk.END,
                values=(p.product_id, p.name, p.category, f"{p.price:.2f}", p.stock),
            )

    def refresh_cart_table(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        sub = 0.0
        for item in self.cart:
            sub += item.sub_total()
            self.cart_tree.insert(
                "",
                tk.END,
                values=(
                    item.product.product_id,
                    item.product.name,
                    f"{item.product.price:.2f}",
                    item.qty,
                    f"{item.sub_total():.2f}",
                ),
            )
        est_total = (sub * (1 - self.discount_percent / 100.0)) * 1.10
        self.discount_info_var.set(
            f"Subtotal: ${sub:.2f}  |  Discount: {self.discount_percent:.0f}%  |  Est. Total: ${est_total:.2f}"
        )
        self.cart_var.set(f"Cart: {len(self.cart)} items")

    def update_dashboard(self):
        self.rev_var.set(f"Revenue: ${self.total_revenue:.2f}")
        self.sold_var.set(f"Sold: {self.total_sold} items")
        self.prod_var.set(f"Products: {len(self.products)}")


if __name__ == "__main__":
    app = SupermarketPOS()
    app.mainloop()