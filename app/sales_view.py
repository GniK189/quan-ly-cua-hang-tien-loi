# app/sales_view.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
from datetime import datetime
from data.product_repo import ProductRepo
from data.order_repo import OrderRepo
from core.invoice_generator import save_invoice_file

class SalesView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.product_repo = ProductRepo()
        self.order_repo = OrderRepo()
        self.cart = [] 
        self.create_widgets()

    def create_widgets(self):
        # --- Phần chọn hàng ---
        select_frame = ttk.LabelFrame(self, text="Chọn hàng")
        select_frame.pack(fill="x", padx=10, pady=5)

        self.cb_products = ttk.Combobox(select_frame, width=30)
        self.cb_products.pack(side="left", padx=5, pady=5)
        
        self.spin_qty = ttk.Spinbox(select_frame, from_=1, to=100, width=5)
        self.spin_qty.set(1)
        self.spin_qty.pack(side="left", padx=5)

        ttk.Button(select_frame, text="Thêm vào giỏ", command=self.add_to_cart).pack(side="left", padx=5)

        # --- Giỏ hàng (Màn hình chính) ---
        self.tree = ttk.Treeview(self, columns=("name", "qty", "price", "total"), show="headings")
        self.tree.heading("name", text="Tên SP")
        self.tree.heading("qty", text="SL")
        self.tree.heading("price", text="Đơn giá")
        self.tree.heading("total", text="Thành tiền")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Footer ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        # TĂNG SIZE FONT TẠI ĐÂY (size 18)
        self.lbl_total = ttk.Label(bottom_frame, text="Tổng cộng: 0 VNĐ", font=("Arial", 18, "bold"), foreground="#d35400")
        self.lbl_total.pack(side="left")

        # TĂNG PADDING CHO NÚT THANH TOÁN
        btn_pay = ttk.Button(bottom_frame, text="THANH TOÁN", command=self.open_payment_dialog)
        btn_pay.pack(side="right", ipady=5, ipadx=10) # ipady làm nút cao hơn
        
        self.refresh_products()

    def refresh_products(self):
        self.products = list(self.product_repo.get_all())
        product_names = [f"{p['name']} (Kho: {p['stock']})" for p in self.products]
        self.cb_products['values'] = product_names

    def add_to_cart(self):
        idx = self.cb_products.current()
        if idx == -1: return
        
        product = self.products[idx]
        qty = int(self.spin_qty.get())
        
        # Check tồn kho
        current_in_cart = sum(item['qty'] for item in self.cart if item['product_id'] == product['_id'])
        if qty + current_in_cart > product['stock']:
            messagebox.showwarning("Cảnh báo", f"Kho chỉ còn {product['stock']} (Giỏ hàng đã có {current_in_cart})")
            return

        total_line = qty * product['price_sell']
        self.cart.append({
            "product_id": product["_id"],
            "name": product["name"],
            "qty": qty,
            "unit_price": product["price_sell"],
            "total_line": total_line
        })
        self.update_cart_ui()

    def update_cart_ui(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.grand_total = 0
        for item in self.cart:
            self.tree.insert("", tk.END, values=(item["name"], item["qty"], "{:,}".format(item["unit_price"]), "{:,}".format(item["total_line"])))
            self.grand_total += item["total_line"]
        
        self.lbl_total.config(text=f"Tổng cộng: {self.grand_total:,} VNĐ")

    # ==========================================
    # LOGIC THANH TOÁN (CẬP NHẬT GIAO DIỆN)
    # ==========================================
    def open_payment_dialog(self):
        if not self.cart:
            messagebox.showwarning("Trống", "Giỏ hàng đang trống!")
            return

        # 1. Tạo Popup (Tăng kích thước để chứa bảng)
        self.pay_window = Toplevel(self)
        self.pay_window.title("Xác nhận & Thanh toán")
        self.pay_window.geometry("500x600") 
        self.pay_window.grab_set() 

        # 2. PHẦN TRÊN: Danh sách sản phẩm (Hóa đơn tạm)
        list_frame = ttk.LabelFrame(self.pay_window, text="Chi tiết đơn hàng", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Bảng chi tiết nhỏ trong popup
        columns = ("name", "qty", "total")
        detail_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        detail_tree.heading("name", text="Tên SP")
        detail_tree.heading("qty", text="SL")
        detail_tree.heading("total", text="Thành tiền")

        detail_tree.column("name", width=220)
        detail_tree.column("qty", width=50, anchor="center")
        detail_tree.column("total", width=100, anchor="e")
        detail_tree.pack(fill="both", expand=True)

        # Đổ dữ liệu từ giỏ hàng vào bảng popup
        for item in self.cart:
            detail_tree.insert("", tk.END, values=(
                item["name"], 
                item["qty"], 
                "{:,}".format(item["total_line"])
            ))

        # 3. PHẦN DƯỚI: Nhập tiền thanh toán
        interaction_frame = ttk.Frame(self.pay_window, padding=20)
        interaction_frame.pack(fill="x", padx=10, pady=5)

        # Tổng tiền
        ttk.Label(interaction_frame, text="Tổng tiền phải trả:", font=("Arial", 10)).pack(anchor="w")
        ttk.Label(interaction_frame, text=f"{self.grand_total:,} VNĐ", font=("Arial", 18, "bold"), foreground="red").pack(anchor="w", pady=(0, 15))

        # Nhập khách đưa
        ttk.Label(interaction_frame, text="Khách đưa:", font=("Arial", 10)).pack(anchor="w")
        self.var_customer_pay = tk.StringVar()
        self.var_customer_pay.trace("w", self.calculate_change) 
        
        entry_pay = ttk.Entry(interaction_frame, textvariable=self.var_customer_pay, font=("Arial", 12))
        entry_pay.pack(fill="x", pady=5)
        entry_pay.focus()

        # Tiền thừa
        self.lbl_change = ttk.Label(interaction_frame, text="Tiền thừa: 0 VNĐ", font=("Arial", 12, "bold"), foreground="green")
        self.lbl_change.pack(anchor="w", pady=10)

        # Nút bấm
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

            pay_amount = int(pay_str)
            change = pay_amount - self.grand_total

            self.lbl_change.config(text=f"Tiền thừa: {change:,} VNĐ")
            
            if change >= 0:
                self.btn_confirm.config(state="normal")
            else:
                self.lbl_change.config(text=f"Thiếu: {abs(change):,} VNĐ")
                self.btn_confirm.config(state="disabled")
        except ValueError:
            self.lbl_change.config(text="Lỗi: Vui lòng nhập số")
            self.btn_confirm.config(state="disabled")

    def confirm_checkout(self):
        try:
            customer_pay = int(self.var_customer_pay.get())
            change = customer_pay - self.grand_total
            
            # 1. Lưu Order
            res = self.order_repo.create_order(self.cart, self.grand_total, customer_pay, change)
            order_id = res.inserted_id

            # 2. Trừ tồn kho
            for item in self.cart:
                self.product_repo.update_stock(item["product_id"], item["qty"])

            # Đóng popup
            self.pay_window.destroy()

            # 3. Hỏi in hóa đơn
            if messagebox.askyesno("Thành công", "Thanh toán thành công!\nBạn có muốn xuất hóa đơn ra file không?"):
                self.export_invoice_flow(order_id, customer_pay, change)

            # 4. Reset
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

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile=f"Invoice_{str(order_id)[-6:].upper()}.txt"
        )
        
        if filepath:
            if save_invoice_file(full_order_data, filepath):
                messagebox.showinfo("Thông báo", "Đã lưu hóa đơn!")