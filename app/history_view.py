# app/history_view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
from data.order_repo import OrderRepo
from core.invoice_generator import save_invoice_file

class HistoryView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.repo = OrderRepo()
        self.orders = []
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(toolbar, text="🔄 Làm mới", command=self.load_data).pack(side="left")
        
        # Nút chức năng bên phải
        ttk.Button(toolbar, text="Xuất file .txt", command=self.export_selected).pack(side="right", padx=5)
        ttk.Button(toolbar, text="👁️ Xem chi tiết", command=self.view_details).pack(side="right", padx=5)

        # Table
        columns = ("id", "date", "items_count", "total", "pay", "change")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("id", text="Mã Đơn")
        self.tree.heading("date", text="Ngày giờ")
        self.tree.heading("items_count", text="Số món")
        self.tree.heading("total", text="Tổng tiền")
        self.tree.heading("pay", text="Khách đưa")
        self.tree.heading("change", text="Tiền thừa")

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("date", width=140, anchor="center")
        self.tree.column("items_count", width=60, anchor="center")
        self.tree.column("total", width=100, anchor="e")
        self.tree.column("pay", width=100, anchor="e")
        self.tree.column("change", width=100, anchor="e")

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sự kiện: Nhấp đúp chuột trái
        self.tree.bind("<Double-1>", self.view_details)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.orders = self.repo.get_all_orders()
        for order in self.orders:
            # Format dữ liệu hiển thị
            oid = str(order["_id"])[-6:].upper()
            date = order["created_at"].strftime("%Y-%m-%d %H:%M")
            items_count = len(order["items"])
            total = "{:,}".format(int(order["total"]))
            pay = "{:,}".format(int(order.get("customer_pay", 0)))
            change = "{:,}".format(int(order.get("change", 0)))

            # Insert
            self.tree.insert("", tk.END, values=(oid, date, items_count, total, pay, change))

    def get_selected_order(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None

        item_values = self.tree.item(selected_item[0])['values']
        selected_oid_display = item_values[0] 
        
        for o in self.orders:
            if str(o["_id"])[-6:].upper() == str(selected_oid_display):
                return o
        return None

    def view_details(self, event=None):
        order = self.get_selected_order()
        if not order:
            if event is None: 
                messagebox.showwarning("Chú ý", "Vui lòng chọn một hóa đơn để xem!")
            return

        # 1. Tạo Popup
        popup = Toplevel(self)
        popup.title(f"Chi tiết đơn hàng #{str(order['_id'])[-6:].upper()}")
        popup.geometry("500x500") # Cao hơn chút để chứa đủ thông tin

        # 2. Header thông tin chung
        info_frame = ttk.LabelFrame(popup, text="Thông tin chung", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        date_str = order["created_at"].strftime("%d/%m/%Y %H:%M:%S")
        ttk.Label(info_frame, text=f"Mã hóa đơn: {str(order['_id'])}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Thời gian:   {date_str}").pack(anchor="w")

        # 3. Danh sách sản phẩm
        list_frame = ttk.LabelFrame(popup, text="Danh sách sản phẩm", padding=5)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("name", "qty", "price", "total")
        detail_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        detail_tree.heading("name", text="Tên SP")
        detail_tree.heading("qty", text="SL")
        detail_tree.heading("price", text="Đơn giá")
        detail_tree.heading("total", text="T.Tiền")

        detail_tree.column("name", width=200)
        detail_tree.column("qty", width=40, anchor="center")
        detail_tree.column("price", width=80, anchor="e")
        detail_tree.column("total", width=80, anchor="e")
        
        detail_tree.pack(fill="both", expand=True)

        # Fill dữ liệu
        for item in order["items"]:
            # Tính lại total_line nếu dữ liệu cũ chưa có
            line_total = item.get("total_line", item["qty"]*item["unit_price"])
            detail_tree.insert("", tk.END, values=(
                item["name"],
                item["qty"],
                "{:,}".format(item["unit_price"]),
                "{:,}".format(line_total)
            ))

        # 4. Footer Tổng kết tiền (PHẦN MỚI CẬP NHẬT)
        footer_frame = ttk.Frame(popup, padding=15)
        footer_frame.pack(fill="x", padx=10, pady=10)

        # Lấy dữ liệu tiền
        total_val = int(order["total"])
        pay_val = int(order.get("customer_pay", 0))
        change_val = int(order.get("change", 0))

        # Dùng Grid để căn chỉnh lề phải cho đẹp
        footer_frame.columnconfigure(0, weight=1) # Đẩy nội dung sang phải

        # Hàng 1: Tổng tiền
        ttk.Label(footer_frame, text="TỔNG CỘNG:", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="e", padx=5)
        ttk.Label(footer_frame, text=f"{total_val:,} VNĐ", font=("Arial", 11, "bold"), foreground="red").grid(row=0, column=2, sticky="e")

        # Hàng 2: Khách đưa
        ttk.Label(footer_frame, text="Khách đưa:").grid(row=1, column=1, sticky="e", padx=5)
        ttk.Label(footer_frame, text=f"{pay_val:,} VNĐ").grid(row=1, column=2, sticky="e")

        # Hàng 3: Tiền thừa
        ttk.Label(footer_frame, text="Tiền thừa:").grid(row=2, column=1, sticky="e", padx=5)
        ttk.Label(footer_frame, text=f"{change_val:,} VNĐ", font=("Arial", 10, "bold"), foreground="green").grid(row=2, column=2, sticky="e")

    def export_selected(self):
        order = self.get_selected_order()
        if not order:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một hóa đơn để xuất!")
            return
        
        oid_display = str(order["_id"])[-6:].upper()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile=f"Invoice_{oid_display}.txt"
        )
        if filepath:
            if save_invoice_file(order, filepath):
                messagebox.showinfo("Thành công", f"Đã xuất hóa đơn ra: {filepath}")