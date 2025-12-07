# app/main_window.py
import tkinter as tk
from tkinter import ttk
from app.products_view import ProductsView
from app.sales_view import SalesView
from app.stats_ai_view import StatsAIView
from app.history_view import HistoryView # <--- Import mới

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Cửa Hàng Tiện Lợi (AI Powered)")
        self.geometry("950x650") # Tăng kích thước chút xíu cho đẹp

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Bán Hàng
        self.sales_tab = SalesView(self.notebook)
        self.notebook.add(self.sales_tab, text="🛒 Bán Hàng")

        # Tab 2: Kho Hàng
        self.products_tab = ProductsView(self.notebook)
        self.notebook.add(self.products_tab, text="📦 Kho & Sản phẩm")

        # Tab 3: Lịch sử (MỚI)
        self.history_tab = HistoryView(self.notebook)
        self.notebook.add(self.history_tab, text="📜 Lịch sử hóa đơn")

        # Tab 4: AI Assistant
        self.stats_tab = StatsAIView(self.notebook)
        self.notebook.add(self.stats_tab, text="🤖 AI Trợ Lý")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = self.notebook.select()
        # Refresh dữ liệu tùy theo tab được chọn
        if selected_tab == str(self.sales_tab):
            self.sales_tab.refresh_products()
        elif selected_tab == str(self.products_tab):
            self.products_tab.load_data()
        elif selected_tab == str(self.history_tab):
            self.history_tab.load_data() # Refresh lịch sử khi click vào