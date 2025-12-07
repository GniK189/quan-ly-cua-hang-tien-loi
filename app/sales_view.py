# app/sales_view.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
from datetime import datetime
import unicodedata
from data.product_repo import ProductRepo
from data.order_repo import OrderRepo
from core.invoice_generator import save_invoice_file

class SalesView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.product_repo = ProductRepo()
        self.order_repo = OrderRepo()
        
        self.cart = []            
        self.all_products = []    
        self.filtered_products = [] 
        
        # --- [QUAN TRỌNG] CẤU HÌNH FONT CHO DROPDOWN LISTBOX ---
        # Lệnh này sẽ áp dụng font chữ to cho tất cả các listbox xổ xuống của Combobox
        self.option_add('*TCombobox*Listbox.font', ("Segoe UI", 13)) 
        
        self.create_widgets()
        self.refresh_products()

    def create_widgets(self):
        # --- CẤU HÌNH STYLE ---
        style = ttk.Style()
        style.configure("Sales.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("Big.TEntry", font=("Segoe UI", 12), padding=5)
        style.configure("Big.TLabel", font=("Segoe UI", 11))

        # =========================================================
        # KHU VỰC 1: THANH CÔNG CỤ
        # =========================================================
        control_frame = ttk.LabelFrame(self, text="🎯 Tìm kiếm & Thêm hàng", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        # 1.1 Ô tìm kiếm
        ttk.Label(control_frame, text="🔍 Tìm nhanh:", style="Big.TLabel").pack(side="left", padx=(0, 5), anchor="center")
        
        self.entry_search = ttk.Entry(control_frame, width=25, font=("Segoe UI", 12))
        self.entry_search.pack(side="left", padx=(0, 20), ipady=3, anchor="center")
        self.entry_search.bind("<KeyRelease>", self.on_search_product)

        # 1.2 Combobox chọn sản phẩm
        ttk.Label(control_frame, text="📦 Sản phẩm:", style="Big.TLabel").pack(side="left", padx=(0, 5), anchor="center")
        
        # Font ở đây chỉ chỉnh text trong ô input, 
        # còn font danh sách xổ xuống đã được chỉnh ở __init__ bằng option_add
        self.cb_products = ttk.Combobox(control_frame, width=35, font=("Segoe UI", 12), state="readonly")
        self.cb_products.pack(side="left", padx=(0, 10), ipady=3, anchor="center")

        # 1.3 Số lượng
        ttk.Label(control_frame, text="SL:", style="Big.TLabel").pack(side="left", padx=(0, 5), anchor="center")
        self.spin_qty = ttk.Spinbox(control_frame, from_=1, to=100, width=5, font=("Segoe UI", 12))
        self.spin_qty.set(1)
        self.spin_qty.pack(side="left", padx=(0, 20), ipady=3, anchor="center")

        # 1.4 Nút Thêm
        btn_add = ttk.Button(control_frame, text="➕ THÊM VÀO GIỎ", style="Sales.TButton", command=self.add_to_cart)
        btn_add.pack(side="left", fill="y", anchor="center")

        # =========================================================
        # KHU VỰC 2: GIỎ HÀNG
        # =========================================================
        cart_toolbar = ttk.Frame(self)
        cart_toolbar.pack(fill="x", padx=10, pady=(10, 0))
        
        ttk.Label(cart_toolbar, text="🛒 Giỏ hàng hiện tại", font=("Segoe UI", 12, "bold", "underline")).pack(side="left")
        
        btn_delete = ttk.Button(cart_toolbar, text="🗑️ Xóa sản phẩm chọn", command=self.remove_from_cart)
        btn_delete.pack(side="right")

        self.tree = ttk.Treeview(self, columns=("name", "qty", "price", "total"), show="headings", height=10)
        self.tree.heading("name", text="Tên Sản Phẩm")
        self.tree.heading("qty", text="Số Lượng")
        self.tree.heading("price", text="Đơn Giá")
        self.tree.heading("total", text="Thành Tiền")

        self.tree.column("name", width=300)
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("price", width=120, anchor="e")
        self.tree.column("total", width=150, anchor="e")

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # =========================================================
        # KHU VỰC 3: THANH TOÁN (FOOTER)
        # =========================================================
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_total = ttk.Label(bottom_frame, text="Tổng cộng: 0 VNĐ", font=("Arial", 20, "bold"), foreground="#d35400")
        self.lbl_total.pack(side="left")

        btn_pay = ttk.Button(bottom_frame, text="💰 THANH TOÁN NGAY", style="Sales.TButton", command=self.open_payment_dialog)
        btn_pay.pack(side="right", ipadx=20) 

    # --- CÁC HÀM LOGIC GIỮ NGUYÊN ---
    def remove_accents(self, input_str):
        if not input_str: return ""
        s = input_str.replace("Đ", "D").replace("đ", "d")
        s = unicodedata.normalize('NFD', s)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        return s.lower()

    def refresh_products(self):
        self.all_products = list(self.product_repo.get_all())
        self.filtered_products = self.all_products
        self.update_combobox()

    def update_combobox(self):
        display_list = [f"{p['name']} (Kho: {p['stock']})" for p in self.filtered_products]
        self.cb_products['values'] = display_list
        if display_list:
            self.cb_products.current(0)
        else:
            self.cb_products.set('')

    def on_search_product(self, event):
        keyword = self.entry_search.get()
        keyword_norm = self.remove_accents(keyword)
        if not keyword:
            self.filtered_products = self.all_products
        else:
            self.filtered_products = []
            for p in self.all_products:
                name_norm = self.remove_accents(p["name"])
                if keyword_norm in name_norm:
                    self.filtered_products.append(p)
        self.update_combobox()

    def add_to_cart(self):
        idx = self.cb_products.current()
        if idx == -1: return
        product = self.filtered_products[idx]
        try:
            qty = int(self.spin_qty.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Lỗi", "Số lượng không hợp lệ")
            return
        current_in_cart = sum(item['qty'] for item in self.cart if item['product_id'] == product['_id'])
        if qty + current_in_cart > product['stock']:
            messagebox.showwarning("Hết hàng", f"Kho chỉ còn {product['stock']} (Giỏ đã có {current_in_cart})")
            return
        total_line = qty * product['price_sell']
        found = False
        for item in self.cart:
            if item["product_id"] == product["_id"]:
                item["qty"] += qty
                item["total_line"] += total_line
                found = True
                break
        if not found:
            self.cart.append({
                "product_id": product["_id"],
                "name": product["name"],
                "qty": qty,
                "unit_price": product["price_sell"],
                "total_line": total_line
            })
        self.update_cart_ui()
        self.spin_qty.set(1)

    def remove_from_cart(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn sản phẩm cần xóa trong danh sách!")
            return
        item_id = selected_item[0]
        index = self.tree.index(item_id)
        del self.cart[index]
        self.update_cart_ui()

    def update_cart_ui(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.grand_total = 0
        for item in self.cart:
            self.tree.insert("", tk.END, values=(item["name"], item["qty"], "{:,}".format(item["unit_price"]), "{:,}".format(item["total_line"])))
            self.grand_total += item["total_line"]
        self.lbl_total.config(text=f"Tổng cộng: {self.grand_total:,} VNĐ")

    def open_payment_dialog(self):
        if not self.cart:
            messagebox.showwarning("Trống", "Giỏ hàng đang trống!")
            return
        self.pay_window = Toplevel(self)
        self.pay_window.title("Xác nhận & Thanh toán")
        self.pay_window.geometry("500x600") 
        self.pay_window.grab_set() 
        list_frame = ttk.LabelFrame(self.pay_window, text="Chi tiết đơn hàng", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        columns = ("name", "qty", "total")
        detail_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        detail_tree.heading("name", text="Tên SP")
        detail_tree.heading("qty", text="SL")
        detail_tree.heading("total", text="Thành tiền")
        detail_tree.column("name", width=220)
        detail_tree.column("qty", width=50, anchor="center")
        detail_tree.column("total", width=100, anchor="e")
        detail_tree.pack(fill="both", expand=True)
        for item in self.cart:
            detail_tree.insert("", tk.END, values=(item["name"], item["qty"], "{:,}".format(item["total_line"])))
        interaction_frame = ttk.Frame(self.pay_window, padding=20)
        interaction_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(interaction_frame, text="Tổng tiền phải trả:", font=("Arial", 10)).pack(anchor="w")
        ttk.Label(interaction_frame, text=f"{self.grand_total:,} VNĐ", font=("Arial", 18, "bold"), foreground="red").pack(anchor="w", pady=(0, 15))
        ttk.Label(interaction_frame, text="Khách đưa:", font=("Arial", 10)).pack(anchor="w")
        self.var_customer_pay = tk.StringVar()
        self.var_customer_pay.trace("w", self.calculate_change) 
        entry_pay = ttk.Entry(interaction_frame, textvariable=self.var_customer_pay, font=("Arial", 12))
        entry_pay.pack(fill="x", pady=5)
        entry_pay.focus()
        self.lbl_change = ttk.Label(interaction_frame, text="Tiền thừa: 0 VNĐ", font=("Arial", 12, "bold"), foreground="green")
        self.lbl_change.pack(anchor="w", pady=10)
        btn_frame = ttk.Frame(interaction_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Hủy Bỏ", command=self.pay_window.destroy).pack(side="left", expand=True, fill="x", padx=5)
        self.btn_confirm = ttk.Button(btn_frame, text="XÁC NHẬN THANH TOÁN", command=self.confirm_checkout, state="disabled")
        self.btn_confirm.pack(side="right", expand=True, fill="x", padx=5)

    def calculate_change(self, *args):
        try:
            pay_str = self.var_customer_pay.get()
            if not pay_str:
                self.lbl_change.config(text="Tiền thừa: 0 VNĐ")
                self.btn_confirm.config(state="disabled")
                return
            clean_pay = pay_str.replace(",", "").replace(".", "")
            pay_amount = int(clean_pay)
            change = pay_amount - self.grand_total
            self.lbl_change.config(text=f"Tiền thừa: {change:,} VNĐ")
            if change >= 0:
                self.btn_confirm.config(state="normal")
            else:
                self.lbl_change.config(text=f"Thiếu: {abs(change):,} VNĐ")
                self.btn_confirm.config(state="disabled")
        except ValueError:
            pass

    def confirm_checkout(self):
        try:
            clean_pay = self.var_customer_pay.get().replace(",", "").replace(".", "")
            customer_pay = int(clean_pay)
            change = customer_pay - self.grand_total
            res = self.order_repo.create_order(self.cart, self.grand_total, customer_pay, change)
            order_id = res.inserted_id
            for item in self.cart:
                self.product_repo.update_stock(item["product_id"], item["qty"])
            self.pay_window.destroy()
            if messagebox.askyesno("Thành công", "Thanh toán thành công!\nBạn có muốn xuất hóa đơn ra file không?"):
                self.export_invoice_flow(order_id, customer_pay, change)
            self.cart = []
            self.update_cart_ui()
            self.refresh_products()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def export_invoice_flow(self, order_id, customer_pay, change):
        full_order_data = {
            "_id": order_id,
            "created_at": datetime.now(),
            "items": self.cart,
            "total": self.grand_total,
            "customer_pay": customer_pay,
            "change": change
        }
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile=f"Invoice_{str(order_id)[-6:].upper()}.txt")
        if filepath:
            if save_invoice_file(full_order_data, filepath):
                messagebox.showinfo("Thông báo", "Đã lưu hóa đơn!")