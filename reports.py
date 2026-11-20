import csv
from datetime import datetime
from models import OrderItem, SaleRecord


class ReportGenerator:
    def __init__(self, app):
        self.app = app
        self.last_receipt = ""

    def build_receipt(
        self,
        cart: list[OrderItem],
        sub: float,
        discount_percent: float,
        discount_amount: float,
        tax: float,
        total: float,
        payment_method: str,
        cash_paid: float,
        change: float,
    ) -> str:
        now = datetime.now()
        lines = [
            "╔══════════════════════════════════════╗",
            "║       CARREFOUR SUPERMARKET          ║",
            "║           Official Receipt           ║",
            "╠══════════════════════════════════════╣",
            f"║  Date    : {now.strftime('%Y-%m-%d'):<25} ║",
            f"║  Time    : {now.strftime('%H:%M:%S'):<25} ║",
            f"║  Payment : {payment_method:<25} ║",
            "╠══════════════════════════════════════╣",
            f" {'Item':<14} {'Price':>7}  {'Qty':>4}  {'Total':>9}",
            "──────────────────────────────────────",
        ]

        for item in cart:
            lines.append(
                f" {item.product.name:<14} ${item.product.price:>6.2f}  x{item.qty:<3}  ${item.sub_total():>8.2f}"
            )

        lines.extend(
            [
                "──────────────────────────────────────",
                f" Subtotal:                    ${sub:>8.2f}",
                f" Discount ({discount_percent:.0f}%):              -${discount_amount:>7.2f}",
                f" Tax (10%):                    ${tax:>8.2f}",
                "══════════════════════════════════════",
                f" TOTAL:                       ${total:>8.2f}",
                f" Paid ({payment_method}):                 ${cash_paid:>8.2f}",
                f" Change:                      ${change:>8.2f}",
                "╚══════════════════════════════════════╝",
            ]
        )

        self.last_receipt = "\n".join(lines)
        return self.last_receipt

    def save_receipt_txt(self, filepath: str = "last_receipt.txt") -> None:
        if not self.last_receipt:
            return
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.last_receipt)

    def format_daily_summary(
        self, sales_log: list[SaleRecord], total_revenue: float, total_sold: int
    ) -> str:
        avg_sale = total_revenue / len(sales_log) if sales_log else 0.0
        return (
            "╔══════════════════════════════╗\n"
            "║      DAILY SALES REPORT      ║\n"
            "╠══════════════════════════════╣\n"
            f"║  Orders  : {len(sales_log):<18}║\n"
            f"║  Revenue : ${total_revenue:<17.2f}║\n"
            f"║  Items   : {str(total_sold) + ' items':<18}║\n"
            f"║  Avg/Ord : ${avg_sale:<17.2f}║\n"
            "╚══════════════════════════════╝"
        )

    def export_sales_csv(self, filepath: str = "sales_report.csv") -> int:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Order #", "Date", "Time", "Items Sold", "Revenue ($)"])
            for idx, sr in enumerate(self.app.sales_log, start=1):
                writer.writerow(
                    [idx, sr.date, sr.time, sr.items_sold, f"{sr.revenue:.2f}"]
                )
        return len(self.app.sales_log)
