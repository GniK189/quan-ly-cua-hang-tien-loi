# seed_data.py
import random
from datetime import datetime, timedelta
from data.db import db_instance

# 1. Kết nối Database
db = db_instance.db
products_col = db["products"]
orders_col = db["orders"]

def clean_db():
    """Xóa sạch dữ liệu cũ"""
    print("🧹 Đang dọn dẹp dữ liệu cũ...")
    products_col.delete_many({})
    orders_col.delete_many({})
    print("✅ Đã xóa sạch collection 'products' và 'orders'")

def create_products():
    """Tạo danh sách 40+ sản phẩm chuẩn cửa hàng tiện lợi Việt Nam"""
    print("📦 Đang tạo kho hàng mẫu xịn xò...")

    # Danh mục sản phẩm thực tế
    raw_data = [
        # --- NHÓM MÌ ĂN LIỀN ---
        {"name": "Mì Hảo Hảo Tôm Chua Cay", "cat": "Mì ăn liền", "imp": 3500, "sell": 4500, "stock": 15}, # Sắp hết
        {"name": "Mì Hảo Hảo Sườn Heo", "cat": "Mì ăn liền", "imp": 3500, "sell": 4500, "stock": 40},
        {"name": "Mì Omachi Xốt Bò Hầm", "cat": "Mì ăn liền", "imp": 6500, "sell": 8000, "stock": 30},
        {"name": "Mì Trộn Indomie", "cat": "Mì ăn liền", "imp": 5000, "sell": 7000, "stock": 25},
        {"name": "Mì Ly Modern Lẩu Thái", "cat": "Mì ăn liền", "imp": 7000, "sell": 10000, "stock": 20},
        {"name": "Phở Bò Gói Vifon", "cat": "Mì ăn liền", "imp": 6000, "sell": 8000, "stock": 35},

        # --- NHÓM NƯỚC GIẢI KHÁT ---
        {"name": "Sting Dâu (330ml)", "cat": "Nước giải khát", "imp": 8000, "sell": 12000, "stock": 10}, # Hot & Sắp hết
        {"name": "Coca Cola Lon 330ml", "cat": "Nước giải khát", "imp": 8500, "sell": 12000, "stock": 50},
        {"name": "Pepsi Lon 330ml", "cat": "Nước giải khát", "imp": 8500, "sell": 12000, "stock": 45},
        {"name": "Nước Tăng Lực Redbull", "cat": "Nước giải khát", "imp": 10000, "sell": 15000, "stock": 20},
        {"name": "Trà Xanh C2 (Chai)", "cat": "Nước giải khát", "imp": 6000, "sell": 9000, "stock": 30},
        {"name": "Nước Suối Aquafina 500ml", "cat": "Nước giải khát", "imp": 4000, "sell": 6000, "stock": 12}, # Sắp hết
        {"name": "Cafe Lon Highlands", "cat": "Nước giải khát", "imp": 12000, "sell": 18000, "stock": 25},
        {"name": "Sữa Tươi Vinamilk Có Đường", "cat": "Sữa & Chế phẩm", "imp": 7000, "sell": 9000, "stock": 40},
        {"name": "Sữa Chua Uống Probi", "cat": "Sữa & Chế phẩm", "imp": 5000, "sell": 7000, "stock": 30},

        # --- NHÓM BIA & CỒN ---
        {"name": "Bia Tiger Lon", "cat": "Bia & Cồn", "imp": 16000, "sell": 20000, "stock": 100},
        {"name": "Bia Heineken Silver", "cat": "Bia & Cồn", "imp": 19000, "sell": 24000, "stock": 80},
        {"name": "Bia Sài Gòn Lager", "cat": "Bia & Cồn", "imp": 12000, "sell": 15000, "stock": 60},

        # --- NHÓM ĂN VẶT ---
        {"name": "Snack Oishi Tôm Cay", "cat": "Ăn vặt", "imp": 5000, "sell": 8000, "stock": 20},
        {"name": "Snack Lay's Khoai Tây", "cat": "Ăn vặt", "imp": 12000, "sell": 18000, "stock": 15},
        {"name": "Bánh ChocoPie (Hộp 2 cái)", "cat": "Ăn vặt", "imp": 10000, "sell": 15000, "stock": 25},
        {"name": "Bánh Quy Oreo", "cat": "Ăn vặt", "imp": 12000, "sell": 17000, "stock": 30},
        {"name": "Kẹo Singum Cool Air", "cat": "Ăn vặt", "imp": 5000, "sell": 8000, "stock": 50},
        {"name": "Xúc Xích Vissan (Gói)", "cat": "Ăn vặt", "imp": 15000, "sell": 22000, "stock": 18},
        {"name": "Bánh Mì Tươi Kinh Đô", "cat": "Ăn vặt", "imp": 8000, "sell": 12000, "stock": 10}, # Hạn ngắn

        # --- NHÓM CÁ NHÂN & GIA DỤNG ---
        {"name": "Khẩu Trang Y Tế (Hộp 10c)", "cat": "Y tế & CN", "imp": 15000, "sell": 25000, "stock": 50},
        {"name": "Bàn Chải Đánh Răng Colgate", "cat": "Y tế & CN", "imp": 20000, "sell": 30000, "stock": 20},
        {"name": "Kem Đánh Răng PS", "cat": "Y tế & CN", "imp": 25000, "sell": 38000, "stock": 25},
        {"name": "Khăn Giấy Ướt", "cat": "Y tế & CN", "imp": 10000, "sell": 15000, "stock": 30},
        {"name": "Bật Lửa BIC", "cat": "Gia dụng", "imp": 8000, "sell": 12000, "stock": 40},
        {"name": "Pin AA Con Ó (Cặp)", "cat": "Gia dụng", "imp": 5000, "sell": 8000, "stock": 30},
        {"name": "Dao Cạo Râu Gillette", "cat": "Y tế & CN", "imp": 18000, "sell": 28000, "stock": 15},
        
        # --- VĂN PHÒNG PHẨM ---
        {"name": "Bút Bi Thiên Long", "cat": "VPP", "imp": 3000, "sell": 5000, "stock": 100},
        {"name": "Băng Keo Trong", "cat": "VPP", "imp": 8000, "sell": 12000, "stock": 20},
    ]

    inserted_products = []
    for item in raw_data:
        # Tự động set min_stock = 20% tồn kho ban đầu hoặc min 10
        min_stock = max(10, int(item["stock"] * 0.2))
        
        product = {
            "name": item["name"],
            "category": item["cat"],
            "price_import": item["imp"],
            "price_sell": item["sell"],
            "stock": item["stock"],
            "min_stock": min_stock
        }
        res = products_col.insert_one(product)
        product["_id"] = res.inserted_id
        inserted_products.append(product)
        
    print(f"✅ Đã thêm {len(inserted_products)} sản phẩm đa dạng.")
    return inserted_products

def generate_payment_info(total):
    """Giả lập tiền khách đưa thông minh"""
    denominations = [10000, 20000, 50000, 100000, 200000, 500000]
    
    # 30% trả vừa đủ (QR Code hoặc tiền lẻ)
    if random.random() < 0.3:
        return total
    
    # Tìm mệnh giá lớn hơn tổng tiền
    possible_pays = [d for d in denominations if d >= total]
    if not possible_pays: 
        return total + 50000 # Trường hợp hiếm
    
    return random.choice(possible_pays)

def create_fake_history(products):
    """Tạo lịch sử bán hàng giả lập thông minh (Smart Seeding)"""
    print("🛒 Đang tạo lịch sử giao dịch giả lập (7 ngày)...")
    
    orders_to_insert = []
    
    # Phân loại sản phẩm để tạo xu hướng mua
    drinks = [p for p in products if p["category"] == "Nước giải khát"]
    noodles = [p for p in products if p["category"] == "Mì ăn liền"]
    beers = [p for p in products if p["category"] == "Bia & Cồn"]
    snacks = [p for p in products if p["category"] == "Ăn vặt"]
    others = [p for p in products if p["category"] not in ["Nước giải khát", "Mì ăn liền", "Bia & Cồn", "Ăn vặt"]]

    # Món HOT (AI sẽ phát hiện bán chạy)
    hot_items = [p for p in products if "Sting" in p["name"] or "Hảo Hảo" in p["name"] or "Tiger" in p["name"]]

    for i in range(7): # 7 ngày qua
        curr_date = datetime.now() - timedelta(days=i)
        is_weekend = curr_date.weekday() >= 5 # T7, CN
        
        # Số lượng đơn hàng: Cuối tuần đông hơn
        num_orders = random.randint(15, 25) if is_weekend else random.randint(8, 15)
        
        for _ in range(num_orders):
            # --- LOGIC GIỜ CAO ĐIỂM ---
            rand_val = random.random()
            if rand_val < 0.4: # 40% đơn rơi vào trưa (11-13h)
                hour = random.randint(11, 13)
            elif rand_val < 0.8: # 40% đơn rơi vào tối (17-20h)
                hour = random.randint(17, 20)
            else: # 20% rải rác
                hour = random.randint(7, 22)
            
            minute = random.randint(0, 59)
            order_date = curr_date.replace(hour=hour, minute=minute)

            items = []
            total_money = 0
            
            # --- LOGIC COMBO MUA HÀNG ---
            # Mỗi khách mua từ 1-5 món
            num_items = random.randint(1, 5)
            
            # Khách hay mua kèm Mì + Nước hoặc Bia + Snack
            combo_type = random.choice(["lunch", "party", "random"])
            
            selected_products = []
            if combo_type == "lunch": # Mì + Nước
                selected_products.extend(random.sample(noodles, k=min(len(noodles), 1)))
                selected_products.extend(random.sample(drinks, k=min(len(drinks), 1)))
            elif combo_type == "party": # Bia + Snack
                selected_products.extend(random.sample(beers, k=min(len(beers), 1)))
                selected_products.extend(random.sample(snacks, k=min(len(snacks), 2)))
            else: # Random, ưu tiên món HOT
                if random.random() < 0.5:
                    selected_products.extend(random.sample(hot_items, k=1))
                selected_products.extend(random.sample(products, k=random.randint(1, 3)))

            # Loại bỏ trùng lặp và giới hạn số lượng item trong 1 đơn
            selected_products = list({v['_id']:v for v in selected_products}.values())[:num_items]

            for prod in selected_products:
                qty = random.randint(1, 3)
                if "Bia" in prod["name"]: qty = random.randint(2, 6) # Mua bia mua nhiều
                if "Hảo Hảo" in prod["name"]: qty = random.randint(2, 5)

                line_total = prod["price_sell"] * qty
                total_money += line_total
                
                items.append({
                    "product_id": prod["_id"],
                    "name": prod["name"],
                    "qty": qty,
                    "unit_price": prod["price_sell"],
                    "total_line": line_total
                })
            
            if not items: continue

            # Thanh toán
            customer_pay = generate_payment_info(total_money)
            change = customer_pay - total_money

            order = {
                "created_at": order_date,
                "items": items,
                "total": total_money,
                "customer_pay": customer_pay,
                "change": change
            }
            orders_to_insert.append(order)

    if orders_to_insert:
        orders_to_insert.sort(key=lambda x: x["created_at"])
        orders_col.insert_many(orders_to_insert)
        print(f"✅ Đã tạo {len(orders_to_insert)} đơn hàng giả lập (Có Logic Giờ cao điểm & Combo).")
    
if __name__ == "__main__":
    try:
        clean_db()
        created_prods = create_products()
        create_fake_history(created_prods)
        print("\n🎉 XONG! Dữ liệu mẫu 'xịn' đã sẵn sàng.")
        print("👉 Hãy chạy lại 'python main.py' để trải nghiệm.")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")