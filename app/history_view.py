# app/history_view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
from datetime import datetime
from data.order_repo import OrderRepo
from core.invoice_generator import save_invoice_file
# [THÊM] Import thư viện lịch
from tkcalendar import DateEntry 

class HistoryView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.repo = OrderRepo()
        self.orders = []
        self.create_widgets()
        # Load dữ liệu ngay khi khởi tạo
        self.load_data()

    def create_widgets(self):
        # --- 1. KHUNG TÌM KIẾM (FILTER FRAME) ---
        filter_frame = ttk.LabelFrame(self, text="🔍 Bộ lọc & Tìm kiếm", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Hàng 1: Tìm theo Mã đơn
        ttk.Label(filter_frame, text="Mã đơn:").pack(side="left", padx=(0, 5))
        self.entry_search_id = ttk.Entry(filter_frame, width=15, font=("Segoe UI", 10))
        self.entry_search_id.pack(side="left", padx=(0, 20))

        # --- [CẬP NHẬT] DÙNG DATEPICKER ---
        # Cấu hình chung cho DateEntry
        date_cfg = {
            "width": 12,
            "background": "darkblue",
            "foreground": "white",
            "borderwidth": 2,
            "date_pattern": "dd/mm/yyyy", # Quan trọng: Định dạng ngày Việt Nam
            "font": ("Segoe UI", 10)
        }

        # Từ ngày
        ttk.Label(filter_frame, text="Từ ngày:").pack(side="left", padx=(0, 5))
        self.entry_date_from = DateEntry(filter_frame, **date_cfg)
        self.entry_date_from.pack(side="left", padx=(0, 5))
        # Mặc định xóa ngày để hiện tất cả (DateEntry mặc định luôn có ngày, nên ta dùng biến flag hoặc logic riêng nếu muốn empty)
        # Tuy nhiên DateEntry không hỗ trợ giá trị rỗng tốt, nên ta cứ để mặc định là ngày hiện tại, 
        # nhưng logic load_data bên dưới sẽ xử lý. 
        # Để UX tốt nhất: Ta thêm Checkbox "Lọc theo ngày" hoặc mặc định load tất cả lúc đầu.
        # Ở đây tôi sẽ giữ nguyên DateEntry hiển thị ngày hôm nay, 
        # nhưng thêm nút "Xóa lọc ngày" để người dùng hiểu.

        # Đến ngày
        ttk.Label(filter_frame, text="Đến ngày:").pack(side="left", padx=(0, 5))
        self.entry_date_to = DateEntry(filter_frame, **date_cfg)
        self.entry_date_to.pack(side="left", padx=(0, 15))
        
        # Nút Tìm kiếm
        ttk.Button(filter_frame, text="🔎 Tìm kiếm", command=self.load_data).pack(side="left", padx=5)
        
        # Nút Tải lại (Reset)
        ttk.Button(filter_frame, text="🔄 Hiện tất cả (Bỏ lọc)", command=self.reset_filters).pack(side="left", padx=5)

        # --- 2. THANH CÔNG CỤ (ACTIONS) ---
        action_toolbar = ttk.Frame(self)
        action_toolbar.pack(fill="x", padx=10, pady=(5, 0))
        
        ttk.Button(action_toolbar, text="Xuất file .txt", command=self.export_selected).pack(side="right", padx=5)
        ttk.Button(action_toolbar, text="👁️ Xem chi tiết", command=self.view_details).pack(side="right", padx=5)

        # --- 3. BẢNG DỮ LIỆU ---
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
        
        self.tree.bind("<Double-1>", self.view_details)
        self.entry_search_id.bind("<Return>", lambda e: self.load_data())

    def load_data(self, use_date_filter=True):
        """
        use_date_filter=True: Lấy ngày từ DatePicker để lọc
        use_date_filter=False: Bỏ qua ngày (khi nhấn nút Reset)
        """
        keyword = self.entry_search_id.get()
        
        d_from = None
        d_to = None

        if use_date_filter:
            # DateEntry.get_date() trả về object datetime.date
            d_from = self.entry_date_from.get_date()
            d_to = self.entry_date_to.get_date()
            
            # Chuyển đổi về datetime full (đầu ngày và cuối ngày)
            d_from = datetime.combine(d_from, datetime.min.time())
            d_to = datetime.combine(d_to, datetime.max.time())

        # Xóa bảng cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Gọi Repo
        self.orders = self.repo.search_orders(keyword, d_from, d_to)
        
        # Hiển thị
        for order in self.orders:
            oid = str(order["_id"])[-6:].upper()
            date = order["created_at"].strftime("%d/%m/%Y %H:%M") 
            items_count = len(order["items"])
            total = "{:,}".format(int(order["total"]))
            pay = "{:,}".format(int(order.get("customer_pay", 0)))
            change = "{:,}".format(int(order.get("change", 0)))

            self.tree.insert("", tk.END, values=(oid, date, items_count, total, pay, change))

    def reset_filters(self):
        self.entry_search_id.delete(0, tk.END)
        # Khi reset, ta gọi load_data với tham số False để bỏ qua ngày tháng đang chọn
        self.load_data(use_date_filter=False)

    # --- CÁC HÀM XỬ LÝ KHÁC GIỮ NGUYÊN ---
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
            if event is None: messagebox.showwarning("Chú ý", "Vui lòng chọn một hóa đơn để xem!")
            return

        popup = Toplevel(self)
        popup.title(f"Chi tiết đơn hàng #{str(order['_id'])[-6:].upper()}")
        popup.geometry("500x500") 

        info_frame = ttk.LabelFrame(popup, text="Thông tin chung", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        date_str = order["created_at"].strftime("%d/%m/%Y %H:%M:%S")
        ttk.Label(info_frame, text=f"Mã hóa đơn: {str(order['_id'])}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Thời gian:   {date_str}").pack(anchor="w")

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

        for item in order["items"]:
            line_total = item.get("total_line", item["qty"]*item["unit_price"])
            detail_tree.insert("", tk.END, values=(item["name"], item["qty"], "{:,}".format(item["unit_price"]), "{:,}".format(line_total)))

        footer_frame = ttk.Frame(popup, padding=15)
        footer_frame.pack(fill="x", padx=10, pady=10)
        total_val = int(order["total"])
        pay_val = int(order.get("customer_pay", 0))
        change_val = int(order.get("change", 0))

        footer_frame.columnconfigure(0, weight=1) 
        ttk.Label(footer_frame, text="TỔNG CỘNG:", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="e", padx=5)
        ttk.Label(footer_frame, text=f"{total_val:,} VNĐ", font=("Arial", 11, "bold"), foreground="red").grid(row=0, column=2, sticky="e")
        ttk.Label(footer_frame, text="Khách đưa:").grid(row=1, column=1, sticky="e", padx=5)
        ttk.Label(footer_frame, text=f"{pay_val:,} VNĐ").grid(row=1, column=2, sticky="e")
        ttk.Label(footer_frame, text="Tiền thừa:").grid(row=2, column=1, sticky="e", padx=5)
        ttk.Label(footer_frame, text=f"{change_val:,} VNĐ", font=("Arial", 10, "bold"), foreground="green").grid(row=2, column=2, sticky="e")

    def export_selected(self):
        order = self.get_selected_order()
        if not order:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một hóa đơn để xuất!")
            return
        oid_display = str(order["_id"])[-6:].upper()
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile=f"Invoice_{oid_display}.txt")
        if filepath:
            if save_invoice_file(order, filepath):
                messagebox.showinfo("Thành công", f"Đã xuất hóa đơn ra: {filepath}")