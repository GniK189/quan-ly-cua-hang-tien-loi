# core/invoice_generator.py
import os

def generate_invoice_content(order):
    """
    Tạo nội dung text cho hóa đơn từ dữ liệu order.
    """
    # Lấy thông tin cơ bản
    order_id = str(order.get("_id"))[-6:].upper() # Lấy 6 ký tự cuối của ID
    date_str = order.get("created_at").strftime("%Y-%m-%d %H:%M:%S")
    customer_pay = order.get("customer_pay", 0)
    change = order.get("change", 0)
    total = order.get("total", 0)

    # Header
    lines = [
        "================================",
        "      CỬA HÀNG TIỆN LỢI",
        "================================",
        f"Mã đơn: #{order_id}",
        f"Ngày:   {date_str}",
        "--------------------------------",
        f"{'Tên SP':<20} {'SL':<3} {'T.Tiền':>10}"
    ]

    # Items
    for item in order["items"]:
        name = item["name"][:18] # Cắt tên nếu quá dài
        qty = item["qty"]
        subtotal = "{:,}".format(int(item.get("total_line", item["qty"] * item["unit_price"])))
        lines.append(f"{name:<20} x{qty:<2} {subtotal:>10}")

    # Footer
    lines.extend([
        "--------------------------------",
        f"{'TỔNG CỘNG:':<20} {total:>10,}",
        f"{'KHÁCH ĐƯA:':<20} {customer_pay:>10,}",
        f"{'TIỀN THỪA:':<20} {change:>10,}",
        "================================",
        "      CẢM ƠN QUÝ KHÁCH!",
        "================================"
    ])

    return "\n".join(lines)

def save_invoice_file(order, filepath):
    """Ghi nội dung hóa đơn ra file"""
    content = generate_invoice_content(order)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Lỗi ghi file: {e}")
        return False