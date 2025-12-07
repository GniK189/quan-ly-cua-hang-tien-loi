# app/main_window.py
import tkinter as tk
from tkinter import ttk
from app.products_view import ProductsView
from app.sales_view import SalesView
from app.stats_ai_view import StatsAIView
from app.history_view import HistoryView
from app.statistics_view import StatisticsView 

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Cửa Hàng Tiện Lợi (AI Powered)")
        
        # 1. Tăng kích thước cửa sổ chính
        self.state('zoomed')
        
        # 2. Cấu hình Style chung cho toàn bộ App (To và Rõ hơn)
        self.setup_styles()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Bán Hàng
        self.sales_tab = SalesView(self.notebook)
        self.notebook.add(self.sales_tab, text="🛒 Bán Hàng")

        # Tab 2: Kho Hàng
        self.products_tab = ProductsView(self.notebook)
        self.notebook.add(self.products_tab, text="📦 Kho & Sản phẩm")

        # Tab 3: Lịch sử
        self.history_tab = HistoryView(self.notebook)
        self.notebook.add(self.history_tab, text="📜 Lịch sử hóa đơn")
        
        # Tab 4: Thống kê
        self.stats_view_tab = StatisticsView(self.notebook)
        self.notebook.add(self.stats_view_tab, text="📊 Thống kê doanh thu")

        # Tab 5: AI Assistant
        self.stats_tab = StatsAIView(self.notebook)
        self.notebook.add(self.stats_tab, text="🤖 AI Trợ Lý")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') # Dùng theme 'clam' để dễ tùy chỉnh màu sắc

        # Font chữ mặc định cho tất cả widget
        default_font = ("Segoe UI", 12)
        bold_font = ("Segoe UI", 12, "bold")
        
        # Cấu hình chung
        style.configure(".", font=default_font)
        
        # Cấu hình Tab (Notebook)
        style.configure("TNotebook.Tab", font=("Segoe UI", 13, "bold"), padding=[15, 5])
        
        # Cấu hình Treeview (Bảng dữ liệu)
        style.configure("Treeview", 
                        font=("Segoe UI", 11), 
                        rowheight=30) # Tăng chiều cao hàng cho thoáng
        
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 12, "bold"), 
                        background="#e1e1e1")
        
        # Cấu hình Button
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=5)
        
        # Cấu hình LabelFrame
        style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"), foreground="#333")

    def on_tab_change(self, event):
        selected_tab = self.notebook.select()
        if selected_tab == str(self.sales_tab):
            self.sales_tab.refresh_products()
        elif selected_tab == str(self.products_tab):
            self.products_tab.load_data()
        elif selected_tab == str(self.history_tab):
            self.history_tab.load_data()
        elif selected_tab == str(self.stats_view_tab):
            self.stats_view_tab.load_data()