# app/products_view.py
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from data.product_repo import ProductRepo

class ProductsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.repo = ProductRepo()
        self.products_map = [] 
        self.selected_product_id = None
        self.current_stock_db = 0 
        
        self.setup_styles()
        self.create_layout()
        self.load_data()

    def setup_styles(self):
        style = ttk.Style()
        # Style cho nút bấm trên thanh công cụ
        style.configure("Toolbar.TButton", font=("Segoe UI", 10, "bold"), padding=6)

    def create_layout(self):
        # --- 1. THANH CÔNG CỤ (TOOLBAR) ---
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill="x")

        # Nút Thêm Mới
        self.btn_add = ttk.Button(toolbar, text="➕ Thêm Sản Phẩm", style="Toolbar.TButton", command=self.open_add_dialog)
        self.btn_add.pack(side="left", padx=5)

        # Nút Sửa
        self.btn_edit = ttk.Button(toolbar, text="✏️ Sửa", style="Toolbar.TButton", command=self.open_edit_dialog)
        self.btn_edit.pack(side="left", padx=5)

        # Nút Xóa
        self.btn_delete = ttk.Button(toolbar, text="❌ Xóa", style="Toolbar.TButton", command=self.delete_product)
        self.btn_delete.pack(side="left", padx=5)

        # Nút Làm mới / Hủy chọn
        ttk.Button(toolbar, text="🔄 Làm mới / Hủy chọn", command=self.refresh_view).pack(side="right", padx=5)

        # Set trạng thái ban đầu (Chưa chọn gì -> Add sáng, Edit/Delete tắt)
        self.toggle_buttons(has_selection=False)

        # --- 2. BẢNG DỮ LIỆU (TREEVIEW) ---
        columns = ("name", "import", "sell", "stock", "profit")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("name", text="Tên Sản Phẩm")
        self.tree.heading("import", text="Giá Nhập")
        self.tree.heading("sell", text="Giá Bán")
        self.tree.heading("stock", text="Tồn Kho")
        self.tree.heading("profit", text="Lợi Nhuận/SP")
        
        self.tree.column("name", width=300)
        self.tree.column("import", width=120, anchor="e")
        self.tree.column("sell", width=120, anchor="e")
        self.tree.column("stock", width=100, anchor="center")
        self.tree.column("profit", width=120, anchor="e")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bắt sự kiện chọn dòng
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

    def toggle_buttons(self, has_selection):
        """Hàm điều khiển trạng thái nút bấm"""
        if has_selection:
            # Khi ĐANG chọn sản phẩm: Không cho thêm, cho phép Sửa/Xóa
            self.btn_add.config(state="disabled")
            self.btn_edit.config(state="normal")
            self.btn_delete.config(state="normal")
        else:
            # Khi KHÔNG chọn sản phẩm: Cho phép thêm, khóa Sửa/Xóa
            self.btn_add.config(state="normal")
            self.btn_edit.config(state="disabled")
            self.btn_delete.config(state="disabled")

    def load_data(self):
        # Xóa dữ liệu cũ trên bảng
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.products_map = []
        products = self.repo.get_all()
        
        for p in products:
            self.products_map.append(p)
            profit = int(p.get("price_sell", 0)) - int(p.get("price_import", 0))
            self.tree.insert("", tk.END, values=(
                p["name"], 
                "{:,}".format(p["price_import"]), 
                "{:,}".format(p["price_sell"]), 
                p["stock"],
                "{:,}".format(profit)
            ))

    def on_item_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items: 
            self.toggle_buttons(has_selection=False)
            return
            
        # Lấy ID sản phẩm đang chọn
        item_id = selected_items[0]
        index = self.tree.index(item_id)
        product = self.products_map[index]
        
        self.selected_product_id = product["_id"]
        self.current_stock_db = int(product["stock"])
        
        # Bật chế độ "Đã chọn"
        self.toggle_buttons(has_selection=True)

    def refresh_view(self):
        """Tải lại dữ liệu và hủy chọn"""
        self.selected_product_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        self.toggle_buttons(has_selection=False)
        self.load_data()

    # ========================================================
    #               LOGIC MODAL (HỘP THOẠI)
    # ========================================================

    def create_modal_form(self, title, is_edit=False, product_data=None):
        """Hàm helper để tạo giao diện popup chung cho Thêm và Sửa"""
        modal = Toplevel(self)
        modal.title(title)
        modal.geometry("450x400")
        modal.grab_set() # Chặn tương tác màn hình chính
        
        # Frame chứa form
        form = ttk.Frame(modal, padding=20)
        form.pack(fill="both", expand=True)
        
        font_label = ("Segoe UI", 10)
        font_entry = ("Segoe UI", 11)

        # 1. Tên sản phẩm
        ttk.Label(form, text="Tên sản phẩm:", font=font_label).pack(anchor="w", pady=(0, 5))
        entry_name = ttk.Entry(form, font=font_entry)
        entry_name.pack(fill="x", pady=(0, 15), ipady=3)
        if is_edit and product_data:
            entry_name.insert(0, product_data["name"])

        # 2. Frame giá (Grid 2 cột)
        price_frame = ttk.Frame(form)
        price_frame.pack(fill="x", pady=(0, 15))

        # Giá nhập
        ttk.Label(price_frame, text="Giá nhập (VNĐ):", font=font_label).grid(row=0, column=0, sticky="w")
        entry_import = ttk.Entry(price_frame, font=font_entry, width=15)
        entry_import.grid(row=1, column=0, sticky="w", padx=(0, 10), ipady=3)
        if is_edit and product_data:
            entry_import.insert(0, str(product_data["price_import"]))

        # Giá bán
        ttk.Label(price_frame, text="Giá bán (VNĐ):", font=font_label).grid(row=0, column=1, sticky="w")
        entry_sell = ttk.Entry(price_frame, font=font_entry, width=15)
        entry_sell.grid(row=1, column=1, sticky="w", ipady=3)
        if is_edit and product_data:
            entry_sell.insert(0, str(product_data["price_sell"]))

        # 3. Tồn kho
        stock_frame = ttk.LabelFrame(form, text="Quản lý kho", padding=10)
        stock_frame.pack(fill="x", pady=(0, 20))
        
        entry_stock_change = None # Biến để lưu entry nhập số lượng

        if not is_edit:
            # --- Form THÊM MỚI ---
            ttk.Label(stock_frame, text="Tồn kho ban đầu:", font=font_label).pack(anchor="w")
            entry_stock_change = ttk.Entry(stock_frame, font=font_entry)
            entry_stock_change.pack(fill="x", ipady=3)
            entry_stock_change.insert(0, "0")
        else:
            # --- Form CHỈNH SỬA ---
            current = product_data["stock"]
            ttk.Label(stock_frame, text=f"Tồn hiện tại: {current}", font=("Segoe UI", 10, "bold"), foreground="blue").pack(anchor="w")
            
            ttk.Label(stock_frame, text="Nhập thêm (+):", font=font_label).pack(anchor="w", pady=(5,0))
            entry_stock_change = ttk.Spinbox(stock_frame, from_=-1000, to=1000, font=font_entry)
            entry_stock_change.pack(fill="x", ipady=3)
            entry_stock_change.set(0)
            ttk.Label(stock_frame, text="(Nhập số âm để trừ kho)", font=("Segoe UI", 8, "italic"), foreground="gray").pack(anchor="w")

        # Nút Lưu
        btn_save = ttk.Button(form, text="💾 LƯU DỮ LIỆU", style="Toolbar.TButton")
        btn_save.pack(fill="x", pady=10, ipady=5)
        
        return modal, entry_name, entry_import, entry_sell, entry_stock_change, btn_save

    def open_add_dialog(self):
        modal, e_name, e_imp, e_sell, e_stock, btn_save = self.create_modal_form("Thêm Sản Phẩm Mới", is_edit=False)
        
        def save_action():
            try:
                name = e_name.get()
                if not name:
                    messagebox.showerror("Lỗi", "Tên sản phẩm không được trống", parent=modal)
                    return
                
                p_import = int(e_imp.get().replace(",", ""))
                p_sell = int(e_sell.get().replace(",", ""))
                stock = int(e_stock.get())

                data = {
                    "name": name,
                    "price_import": p_import,
                    "price_sell": p_sell,
                    "stock": stock,
                    "min_stock": 10,
                    "category": "General"
                }
                self.repo.add_product(data)
                messagebox.showinfo("Thành công", "Đã thêm sản phẩm!", parent=modal)
                modal.destroy()
                self.refresh_view()
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ", parent=modal)

        btn_save.config(command=save_action)

    def open_edit_dialog(self):
        if not self.selected_product_id: return
        
        # Lấy data hiện tại để fill vào form
        idx = self.tree.index(self.tree.selection()[0])
        current_data = self.products_map[idx]
        
        modal, e_name, e_imp, e_sell, e_stock, btn_save = self.create_modal_form("Sửa Sản Phẩm", is_edit=True, product_data=current_data)

        def update_action():
            try:
                name = e_name.get()
                p_import = int(e_imp.get().replace(",", ""))
                p_sell = int(e_sell.get().replace(",", ""))
                added_stock = int(e_stock.get())
                
                final_stock = self.current_stock_db + added_stock

                data = {
                    "name": name,
                    "price_import": p_import,
                    "price_sell": p_sell,
                    "stock": final_stock,
                    "category": "General" # Giữ nguyên hoặc mở rộng sau
                }
                self.repo.update_product_info(self.selected_product_id, data)
                messagebox.showinfo("Thành công", "Cập nhật thành công!", parent=modal)
                modal.destroy()
                self.refresh_view()
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ", parent=modal)

        btn_save.config(command=update_action)

    def delete_product(self):
        if not self.selected_product_id: return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sản phẩm này không?"):
            self.repo.delete_product(self.selected_product_id)
            messagebox.showinfo("Đã xóa", "Sản phẩm đã bị xóa.")
            self.refresh_view()