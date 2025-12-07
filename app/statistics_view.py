# app/statistics_view.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # <--- THÊM IMPORT NÀY
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from data.order_repo import OrderRepo

class StatisticsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.repo = OrderRepo()
        
        # Cấu hình grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.create_widgets()
        
        # Mặc định load tháng hiện tại
        now = datetime.now()
        self.cb_month.set(now.month)
        self.cb_year.set(now.year)
        self.load_data()

    def create_widgets(self):
        # 1. Header & Filter
        filter_frame = ttk.Frame(self, padding=10)
        filter_frame.grid(row=0, column=0, sticky="ew")
        
        ttk.Label(filter_frame, text="📅 Thống kê Tháng:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.cb_month = ttk.Combobox(filter_frame, values=list(range(1, 13)), width=5, state="readonly")
        self.cb_month.pack(side="left", padx=5)
        
        self.cb_year = ttk.Combobox(filter_frame, values=[2023, 2024, 2025, 2026], width=8, state="readonly")
        self.cb_year.pack(side="left", padx=5)
        
        ttk.Button(filter_frame, text="🔍 Xem báo cáo", command=self.load_data).pack(side="left", padx=10)

        # 2. KPI Cards
        kpi_frame = ttk.Frame(self, padding=10)
        kpi_frame.grid(row=1, column=0, sticky="ew")
        
        self.card_revenue = ttk.LabelFrame(kpi_frame, text="💰 Tổng Doanh Thu", padding=10)
        self.card_revenue.pack(side="left", fill="x", expand=True, padx=5)
        self.lbl_revenue = ttk.Label(self.card_revenue, text="0 VNĐ", font=("Arial", 18, "bold"), foreground="#27ae60")
        self.lbl_revenue.pack()

        self.card_orders = ttk.LabelFrame(kpi_frame, text="🛒 Tổng Đơn Hàng", padding=10)
        self.card_orders.pack(side="left", fill="x", expand=True, padx=5)
        self.lbl_orders = ttk.Label(self.card_orders, text="0", font=("Arial", 18, "bold"), foreground="#2980b9")
        self.lbl_orders.pack()

        # 3. Chart Area
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        self.chart_frame.columnconfigure(0, weight=2)
        self.chart_frame.columnconfigure(1, weight=1)
        self.chart_frame.rowconfigure(0, weight=1)

    def load_data(self):
        try:
            month = int(self.cb_month.get())
            year = int(self.cb_year.get())
        except:
            return

        # Xóa biểu đồ cũ
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Lấy dữ liệu
        daily_data, total_rev, total_orders = self.repo.get_stats_by_month(month, year)
        cat_data = self.repo.get_category_stats(month, year)

        # Cập nhật KPI
        self.lbl_revenue.config(text=f"{total_rev:,.0f} VNĐ")
        self.lbl_orders.config(text=f"{total_orders} đơn")

        # --- BIỂU ĐỒ 1: LINE CHART (CẢI TIẾN) ---
        fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        days = list(daily_data.keys())
        values = list(daily_data.values())
        
        ax1.plot(days, values, marker='o', linestyle='-', color='#e67e22', markersize=4)
        ax1.set_title(f"Doanh thu Tháng {month}/{year}", fontsize=10)
        ax1.set_ylabel("Doanh thu (VNĐ)")
        ax1.set_xlabel("Ngày")
        
        # === CẢI TIẾN TRỤC X: Hiển thị từng ngày một ===
        ax1.set_xticks(days) # Bắt buộc hiện tất cả các ngày có trong danh sách
        
        # === CẢI TIẾN TRỤC Y: Format số có dấu phẩy (250,000) ===
        # Dùng FuncFormatter để format lại số tiền cho dễ đọc
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
        
        ax1.grid(True, linestyle='--', alpha=0.5)
        
        canvas1 = FigureCanvasTkAgg(fig1, master=self.chart_frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5)

        # --- BIỂU ĐỒ 2: PIE CHART ---
        if cat_data:
            labels = [item["_id"] for item in cat_data]
            sizes = [item["total_revenue"] for item in cat_data]
            
            fig2, ax2 = plt.subplots(figsize=(4, 4), dpi=100)
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
            ax2.set_title("Tỷ trọng danh mục", fontsize=10)
            
            canvas2 = FigureCanvasTkAgg(fig2, master=self.chart_frame)
            canvas2.draw()
            canvas2.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=5)
        else:
            ttk.Label(self.chart_frame, text="Chưa có dữ liệu danh mục", foreground="gray").grid(row=0, column=1)