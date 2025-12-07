# app/statistics_view.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data.order_repo import OrderRepo

class StatisticsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.repo = OrderRepo()
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # 1. Tiêu đề tổng quan
        self.lbl_summary = ttk.Label(self, text="Tổng quan doanh thu", font=("Arial", 14, "bold"))
        self.lbl_summary.pack(pady=10)

        # 2. Khu vực Biểu đồ (Trên)
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 3. Khu vực Top sản phẩm (Dưới)
        lbl_top = ttk.Label(self, text="🏆 Top 5 Sản phẩm bán chạy nhất", font=("Arial", 12, "bold"), foreground="#d35400")
        lbl_top.pack(pady=(10, 5))

        columns = ("name", "qty", "revenue")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.tree.heading("name", text="Tên Sản Phẩm")
        self.tree.heading("qty", text="Đã bán")
        self.tree.heading("revenue", text="Doanh thu")
        
        self.tree.column("name", width=250)
        self.tree.column("qty", width=100, anchor="center")
        self.tree.column("revenue", width=150, anchor="e")
        
        self.tree.pack(fill="x", padx=20, pady=5)
        
        # Nút làm mới
        ttk.Button(self, text="🔄 Cập nhật số liệu", command=self.load_data).pack(pady=10)

    def load_data(self):
        # --- A. Vẽ Biểu đồ Doanh thu ---
        # Xóa biểu đồ cũ nếu có
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Lấy dữ liệu
        revenue_data = self.repo.get_revenue_last_7_days()
        days = list(revenue_data.keys())
        amounts = list(revenue_data.values())

        # Tạo Figure Matplotlib
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
        # Vẽ cột
        bars = ax.bar(days, amounts, color='#4CAF50', width=0.5)
        
        ax.set_title("Doanh thu 7 ngày gần nhất (VNĐ)", fontsize=10)
        ax.set_ylabel("Doanh thu", fontsize=8)
        ax.tick_params(axis='x', labelsize=8)
        ax.tick_params(axis='y', labelsize=8)

        # Hiển thị số tiền trên đầu cột
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=8)

        # Nhúng vào Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # --- B. Load Top Sản phẩm ---
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        top_products = self.repo.get_top_selling_products()
        for p in top_products:
            self.tree.insert("", tk.END, values=(
                p["_id"],
                p["total_qty"],
                "{:,}".format(p["total_revenue"])
            ))