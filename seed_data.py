# seed_data.py
import random
from datetime import datetime, timedelta
from data.db import db_instance

# 1. Kết nối Database
db = db_instance.db
products_col = db["products"]
orders_col = db["orders"]

def clean_db():
    """Xóa sạch dữ liệu cũ để tránh trùng lặp"""
    print("🧹 Đang dọn dẹp dữ liệu cũ...")
    products_col.delete_many({})
    orders_col.delete_many({})
    print("✅ Đã xóa sạch collection 'products' và 'orders'")

def create_products():
    """Tạo sản phẩm mẫu"""
    print("📦 Đang tạo sản phẩm mẫu...")
    
    # Danh sách sản phẩm
    # Logic test AI: 
    # - Món HOT (Hảo Hảo, Sting): Sẽ mua nhiều -> Stock giảm sâu -> AI báo nhập.
    # - Món CHẬM (Bàn chải): Ít mua -> Stock còn nguyên -> AI không báo.
    sample_products = [
        {"name": "Mì Hảo Hảo Tôm Chua Cay", "category": "Mì gói", "price_import": 3200, "price_sell": 4500, "stock": 10, "min_stock": 20},
        {"name": "Sting Dâu (330ml)", "category": "Nước giải khát", "price_import": 8000, "price_sell": 12000, "stock": 8, "min_stock": 24},
        {"name": "Bánh Snack Lay's Vị Tảo", "category": "Ăn vặt", "price_import": 10000, "price_sell": 16000, "stock": 5, "min_stock": 10},
        {"name": "Nước Suối Aquafina", "category": "Nước giải khát", "price_import": 4000, "price_sell": 6000, "stock": 20, "min_stock": 10},
        {"name": "Cafe Lon Highlands", "category": "Nước giải khát", "price_import": 12000, "price_sell": 18000, "stock": 25, "min_stock": 10},
        {"name": "Bàn Chải Đánh Răng", "category": "Gia dụng", "price_import": 15000, "price_sell": 25000, "stock": 50, "min_stock": 5},
        {"name": "Khẩu Trang Y Tế (Hộp)", "category": "Y tế", "price_import": 25000, "price_sell": 40000, "stock": 100, "min_stock": 10},
        {"name": "Bật lửa BIC", "category": "Gia dụng", "price_import": 8000, "price_sell": 12000, "stock": 30, "min_stock": 5},
    ]
    
    inserted_products = []
    for p in sample_products:
        res = products_col.insert_one(p)
        p["_id"] = res.inserted_id
        inserted_products.append(p)
        
    print(f"✅ Đã thêm {len(inserted_products)} sản phẩm.")
    return inserted_products

def generate_payment_info(total):
    """Giả lập tiền khách đưa hợp lý"""
    # Các mệnh giá tiền phổ biến
    denominations = [10000, 20000, 50000, 100000, 200000, 500000]
    
    # Logic: Khách thường đưa số tiền >= tổng, và làm tròn lên mệnh giá gần nhất
    # Hoặc đôi khi đưa vừa đủ
    if random.random() < 0.3: # 30% trả đúng tiền lẻ
        return total
    
    # Tìm mệnh giá lớn hơn tổng tiền
    possible_pays = [d for d in denominations if d >= total]
    if not possible_pays: 
        # Nếu tổng lớn quá (trên 500k), giả sử đưa dư 1 chút
        return total + 50000
    
    # Chọn một mệnh giá ngẫu nhiên để trả (ví dụ hết 12k, có thể đưa 20k hoặc 50k)
    pay = random.choice(possible_pays)
    
    # Đôi khi khách đưa thêm tiền lẻ để thối chẵn (Logic phức tạp bỏ qua, lấy cơ bản)
    return pay

def create_fake_history(products):
    """Tạo đơn hàng giả trong 7 ngày qua có đầy đủ thông tin thanh toán"""
    print("🛒 Đang tạo lịch sử bán hàng giả lập (7 ngày qua)...")
    
    orders_to_insert = []
    
    hot_products = [p for p in products if p["stock"] < 15] 
    normal_products = [p for p in products if p["stock"] >= 15]

    for i in range(7):
        # Ngày hiện tại lùi về i ngày
        # Set giờ ngẫu nhiên trong ngày làm việc (7h sáng - 22h tối)
        base_date = datetime.now() - timedelta(days=i)
        
        # Random số lượng đơn mỗi ngày (5-12 đơn)
        num_orders = random.randint(5, 12)
        
        for _ in range(num_orders):
            # Chỉnh giờ ngẫu nhiên cho mỗi đơn
            hour = random.randint(7, 22)
            minute = random.randint(0, 59)
            order_date = base_date.replace(hour=hour, minute=minute)

            items = []
            total_money = 0
            
            # Mỗi đơn mua 1-4 món
            num_items = random.randint(1, 4)
            
            for _ in range(num_items):
                # Tỉ lệ mua hàng HOT cao hơn để test AI
                if random.random() < 0.7:
                    prod = random.choice(hot_products)
                    qty = random.randint(2, 6) 
                else:
                    prod = random.choice(normal_products)
                    qty = random.randint(1, 2)

                line_total = prod["price_sell"] * qty
                total_money += line_total
                
                items.append({
                    "product_id": prod["_id"],
                    "name": prod["name"],
                    "qty": qty,
                    "unit_price": prod["price_sell"],
                    "total_line": line_total # Thêm trường này cho đồng bộ code mới
                })
            
            # --- LOGIC MỚI: Tính tiền khách đưa và tiền thừa ---
            customer_pay = generate_payment_info(total_money)
            change = customer_pay - total_money

            order = {
                "created_at": order_date,
                "items": items,
                "total": total_money,
                "customer_pay": customer_pay, # Trường mới
                "change": change              # Trường mới
            }
            orders_to_insert.append(order)

    if orders_to_insert:
        # Sort lại theo thời gian cho giống thật trước khi insert
        orders_to_insert.sort(key=lambda x: x["created_at"])
        orders_col.insert_many(orders_to_insert)
        print(f"✅ Đã tạo {len(orders_to_insert)} đơn hàng giả lập với đầy đủ thông tin thanh toán.")
    
if __name__ == "__main__":
    try:
        clean_db()
        created_prods = create_products()
        create_fake_history(created_prods)
        print("\n🎉 XONG! Dữ liệu mẫu đã sẵn sàng.")
        print("👉 Hãy chạy 'python main.py' để kiểm tra tab Lịch sử và AI.")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        print("💡 Gợi ý: Kiểm tra file config.py xem đã đúng user/pass chưa.")