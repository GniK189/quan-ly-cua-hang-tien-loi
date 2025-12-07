# app/products_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from data.product_repo import ProductRepo

class ProductsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.repo = ProductRepo()
        self.selected_product_id = None
        self.products_map = [] 
        self.current_stock_db = 0 
        
        # Cấu hình Style cho nút bấm to đẹp
        self.setup_styles()
        
        self.create_widgets()
        self.load_data()

    def setup_styles(self):
        style = ttk.Style()
        # Tạo style mới cho nút bấm lớn
        style.configure("Big.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        # Style cho Label và Entry
        style.configure("Form.TLabel", font=("Segoe UI", 11))
        style.configure("Form.TEntry", font=("Segoe UI", 11))

    def create_widgets(self):
        # Font chữ chung
        form_font = ("Segoe UI", 11)
        
        # --- Form nhập liệu (To và Rộng rãi hơn) ---
        form_frame = ttk.LabelFrame(self, text="📝 Thông tin chi tiết", padding=15)
        form_frame.pack(fill="x", padx=15, pady=10)
        
        # Cấu hình cột để giãn đều đẹp mắt
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Hàng 0: Tên SP (Trải dài)
        ttk.Label(form_frame, text="Tên Sản Phẩm:", style="Form.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.entry_name = ttk.Entry(form_frame, font=form_font)
        # ipady=4 giúp ô nhập cao hơn, dễ nhìn hơn
        self.entry_name.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=8, ipady=4)

        # Hàng 1: Giá cả
        ttk.Label(form_frame, text="Giá Nhập (VNĐ):", style="Form.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.entry_import = ttk.Entry(form_frame, font=form_font)
        self.entry_import.grid(row=1, column=1, sticky="ew", padx=5, pady=8, ipady=4)

        ttk.Label(form_frame, text="Giá Bán (VNĐ):", style="Form.TLabel").grid(row=1, column=2, sticky="w", padx=5, pady=8)
        self.entry_sell = ttk.Entry(form_frame, font=form_font)
        self.entry_sell.grid(row=1, column=3, sticky="ew", padx=5, pady=8, ipady=4)

        # --- Hàng 2: QUẢN LÝ KHO (Ẩn/Hiện linh hoạt) ---
        
        # A. Widget cho chế độ THÊM MỚI
        self.lbl_init_stock = ttk.Label(form_frame, text="Tồn Kho Ban Đầu:", style="Form.TLabel")
        self.entry_init_stock = ttk.Entry(form_frame, font=form_font)
        
        # Grid vị trí mặc định
        self.lbl_init_stock.grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.entry_init_stock.grid(row=2, column=1, sticky="w", padx=5, pady=8, ipady=4, ipadx=10)

        # B. Widget cho chế độ SỬA (Current + Add Stock)
        self.lbl_current_stock = ttk.Label(form_frame, text="Tồn Hiện Tại:", style="Form.TLabel")
        self.var_current_stock = tk.StringVar(value="0")
        self.entry_current_stock = ttk.Entry(form_frame, textvariable=self.var_current_stock, state="disabled", font=form_font, width=12)

        self.lbl_add_stock = ttk.Label(form_frame, text="Nhập Thêm (+):", foreground="#2980b9", font=("Segoe UI", 11, "bold"))
        self.entry_add_stock = ttk.Spinbox(form_frame, from_=-1000, to=1000, font=form_font, width=12)
        
        # Frame nhỏ chứa Hint để layout gọn hơn
        self.hint_frame = ttk.Frame(form_frame)
        self.lbl_hint = ttk.Label(self.hint_frame, text="(Nhập âm để trừ)", font=("Segoe UI", 9, "italic"), foreground="gray")
        self.lbl_hint.pack(side="left")

        # --- KHU VỰC NÚT BẤM (To hơn) ---
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=20)

        self.btn_add = ttk.Button(btn_frame, text="➕ Thêm Mới", style="Big.TButton", command=self.add_product)
        self.btn_add.pack(side="left", padx=10)

        self.btn_update = ttk.Button(btn_frame, text="💾 Lưu Thay Đổi", style="Big.TButton", command=self.update_product)
        self.btn_update.pack(side="left", padx=10)

        self.btn_delete = ttk.Button(btn_frame, text="❌ Xóa", style="Big.TButton", command=self.delete_product)
        self.btn_delete.pack(side="left", padx=10)

        ttk.Button(btn_frame, text="Mặc định / Hủy", style="Big.TButton", command=self.clear_form).pack(side="left", padx=10)

        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")

        # --- Bảng hiển thị (Giữ nguyên logic cũ) ---
        columns = ("name", "import", "sell", "stock")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("name", text="Tên Sản Phẩm")
        self.tree.heading("import", text="Giá Nhập")
        self.tree.heading("sell", text="Giá Bán")
        self.tree.heading("stock", text="Tồn Kho")
        
        self.tree.column("name", width=250) # Tên dài hơn chút
        self.tree.column("import", width=100, anchor="e")
        self.tree.column("sell", width=100, anchor="e")
        self.tree.column("stock", width=80, anchor="center")
        
        # Tăng chiều cao dòng trong bảng
        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

    def switch_mode(self, mode="add"):
        """Hàm điều khiển ẩn/hiện widget với layout mới"""
        if mode == "add":
            # Ẩn nhóm Sửa
            self.lbl_current_stock.grid_remove()
            self.entry_current_stock.grid_remove()
            self.lbl_add_stock.grid_remove()
            self.entry_add_stock.grid_remove()
            self.hint_frame.grid_remove()
            
            # Hiện nhóm Thêm Mới (Đúng vị trí grid)
            self.lbl_init_stock.grid(row=2, column=0, sticky="w", padx=5, pady=8)
            self.entry_init_stock.grid(row=2, column=1, sticky="w", padx=5, pady=8, ipady=4, ipadx=10)
            
        elif mode == "edit":
            # Ẩn nhóm Thêm Mới
            self.lbl_init_stock.grid_remove()
            self.entry_init_stock.grid_remove()
            
            # Hiện nhóm Sửa
            self.lbl_current_stock.grid(row=2, column=0, sticky="w", padx=5, pady=8)
            self.entry_current_stock.grid(row=2, column=1, sticky="w", padx=5, pady=8, ipady=4)
            
            self.lbl_add_stock.grid(row=2, column=2, sticky="w", padx=5, pady=8)
            # Spinbox nằm cạnh label
            self.entry_add_stock.grid(row=2, column=3, sticky="w", padx=5, pady=8, ipady=4)
            # Hint nằm cùng ô với Spinbox nhưng lệch sang phải (hoặc dùng frame nếu muốn)
            # Ở đây tôi đặt hint_frame đè lên hoặc grid sang cột khác. 
            # Tốt nhất là dùng grid_forget trước rồi grid lại.
            self.hint_frame.grid(row=2, column=3, sticky="e", padx=20, pady=8)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.products_map = []
        for p in self.repo.get_all():
            self.products_map.append(p)
            self.tree.insert("", tk.END, values=(
                p["name"], 
                "{:,}".format(p["price_import"]), 
                "{:,}".format(p["price_sell"]), 
                p["stock"]
            ))

    def on_item_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items: return
            
        item_id = selected_items[0]
        index = self.tree.index(item_id)
        product = self.products_map[index]
        self.selected_product_id = product["_id"]
        self.current_stock_db = int(product["stock"])

        # Fill dữ liệu
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, product["name"])
        self.entry_import.delete(0, tk.END)
        self.entry_import.insert(0, str(product["price_import"]))
        self.entry_sell.delete(0, tk.END)
        self.entry_sell.insert(0, str(product["price_sell"]))
        
        # Chuyển chế độ
        self.switch_mode("edit")
        
        self.var_current_stock.set(str(self.current_stock_db))
        self.entry_add_stock.set(0)

        self.btn_add.config(state="disabled")
        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_import.delete(0, tk.END)
        self.entry_sell.delete(0, tk.END)
        self.entry_init_stock.delete(0, tk.END)
        
        self.current_stock_db = 0
        self.var_current_stock.set("0")
        self.entry_add_stock.set(0)
        
        self.selected_product_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
            
        self.switch_mode("add")

        self.btn_add.config(state="normal")
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")
        
        self.load_data()

    def get_form_data(self, is_update=False):
        try:
            name = self.entry_name.get()
            if not name:
                messagebox.showerror("Lỗi", "Tên sản phẩm trống")
                return None
            
            p_import = int(self.entry_import.get().replace(",", ""))
            p_sell = int(self.entry_sell.get().replace(",", ""))
            
            if is_update:
                added_qty = int(self.entry_add_stock.get())
                final_stock = self.current_stock_db + added_qty
            else:
                init_val = self.entry_init_stock.get()
                final_stock = int(init_val) if init_val else 0

            return {
                "name": name,
                "price_import": p_import,
                "price_sell": p_sell,
                "stock": final_stock,
                "min_stock": 10,
                "category": "General"
            }
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ")
            return None

    def add_product(self):
        data = self.get_form_data(is_update=False)
        if data:
            self.repo.add_product(data)
            messagebox.showinfo("Thành công", "Đã thêm sản phẩm mới!")
            self.clear_form()

    def update_product(self):
        if not self.selected_product_id: return
        data = self.get_form_data(is_update=True)
        if data:
            self.repo.update_product_info(self.selected_product_id, data)
            messagebox.showinfo("Thành công", "Đã cập nhật!")
            self.clear_form()

    def delete_product(self):
        if not self.selected_product_id: return
        if messagebox.askyesno("Xác nhận", "Xóa sản phẩm này?"):
            self.repo.delete_product(self.selected_product_id)
            messagebox.showinfo("Đã xóa", "Sản phẩm đã bị xóa.")
            self.clear_form()