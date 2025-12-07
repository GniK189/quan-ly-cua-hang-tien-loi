# app/products_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from data.product_repo import ProductRepo

class ProductsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.repo = ProductRepo()
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Form nhập liệu
        form_frame = ttk.LabelFrame(self, text="Thông tin sản phẩm")
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Tên SP:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = ttk.Entry(form_frame)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Giá nhập:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_import = ttk.Entry(form_frame)
        self.entry_import.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Giá bán:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_sell = ttk.Entry(form_frame)
        self.entry_sell.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Tồn kho:").grid(row=1, column=2, padx=5, pady=5)
        self.entry_stock = ttk.Entry(form_frame)
        self.entry_stock.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(form_frame, text="Thêm Sản Phẩm", command=self.add_product).grid(row=2, column=1, pady=10)
        ttk.Button(form_frame, text="Làm mới", command=self.load_data).grid(row=2, column=2, pady=10)

        # Bảng hiển thị
        columns = ("name", "import", "sell", "stock")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("name", text="Tên Sản Phẩm")
        self.tree.heading("import", text="Giá Nhập")
        self.tree.heading("sell", text="Giá Bán")
        self.tree.heading("stock", text="Tồn Kho")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    def add_product(self):
        try:
            data = {
                "name": self.entry_name.get(),
                "price_import": int(self.entry_import.get()),
                "price_sell": int(self.entry_sell.get()),
                "stock": int(self.entry_stock.get()),
                "min_stock": 10, # Mặc định
                "category": "General"
            }
            self.repo.add_product(data)
            messagebox.showinfo("Thành công", "Đã thêm sản phẩm!")
            self.load_data()
            # Clear inputs
            self.entry_name.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ cho giá và tồn kho")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in self.repo.get_all():
            self.tree.insert("", tk.END, values=(p["name"], p["price_import"], p["price_sell"], p["stock"]))