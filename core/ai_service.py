# core/ai_service.py
import google.generativeai as genai
from config import GEMINI_API_KEY
from data.product_repo import ProductRepo
from data.order_repo import OrderRepo
import json
import math  # Thêm thư viện math
from datetime import datetime

genai.configure(api_key=GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.product_repo = ProductRepo()
        self.order_repo = OrderRepo()

    def get_restock_suggestions(self):
        # 1. Thu thập dữ liệu
        products = self.product_repo.get_all()
        orders = self.order_repo.get_recent_orders(days=7)
        
        today = datetime.now()
        weekday_str = today.strftime("%A") 
        date_str = today.strftime("%d/%m/%Y")

        # 2. Tính toán thống kê
        product_stats = {} 
        
        for p in products:
            profit = p.get("price_sell", 0) - p.get("price_import", 0)
            product_stats[str(p["_id"])] = {
                "name": p["name"],
                "stock": p["stock"],
                "profit_per_unit": profit, 
                "total_sold": 0
            }

        for order in orders:
            for item in order["items"]:
                pid = str(item["product_id"])
                if pid in product_stats:
                    product_stats[pid]["total_sold"] += item["qty"]

        # Chuẩn bị dữ liệu gửi AI
        ai_input_data = []
        for pid, stat in product_stats.items():
            avg_daily_sales = round(stat["total_sold"] / 7, 2)
            
            # --- CẢI TIẾN LOGIC DỰ BÁO ---
            if avg_daily_sales > 0:
                raw_days = stat["stock"] / avg_daily_sales
                # Nếu < 1 ngày -> Gán bằng 0 để AI hiểu là khẩn cấp
                # Nếu > 1 ngày -> Làm tròn lên (ví dụ 1.2 ngày -> 2 ngày cho an toàn)
                if raw_days < 1:
                    days_left = 0 
                else:
                    days_left = math.ceil(raw_days)
            else:
                days_left = 999 

            # Chỉ gửi món cần thiết
            if days_left <= 3 or stat["stock"] < 10 or avg_daily_sales > 2:
                ai_input_data.append({
                    "product": stat["name"],
                    "stock": stat["stock"],
                    "avg_sales": avg_daily_sales,
                    "profit": stat["profit_per_unit"],
                    "days_until_empty": days_left # Giờ đây sẽ là số nguyên: 0, 1, 2...
                })

        if not ai_input_data:
            return "Cửa hàng đang hoạt động ổn định, chưa có mặt hàng nào cần nhập gấp."

        # 3. Gửi Prompt (Đã chỉnh sửa để AI nói chuyện tự nhiên hơn)
        prompt = f"""
        Bạn là Trợ lý Quản lý kho hàng (Business AI).
        Hôm nay là: {weekday_str}, ngày {date_str}.
        
        Hãy phân tích dữ liệu JSON dưới đây để gợi ý nhập hàng.
        
        QUY TẮC QUAN TRỌNG VỀ NGÔN NGỮ:
        1. Trường "days_until_empty" = 0 nghĩa là **"Sẽ hết hàng ngay trong hôm nay"** (Dùng ngôn ngữ cảnh báo khẩn cấp).
        2. Trường "days_until_empty" từ 1-3: Nghĩa là "Chỉ còn đủ bán khoảng X ngày".
        3. Không bao giờ dùng các cụm từ máy móc như "0.0 ngày" hay "days_until_empty". Hãy nói như người thật.
        
        Tiêu chí ưu tiên:
        - Lợi nhuận cao (profit lớn) + Bán chạy => Ưu tiên số 1.
        - Hàng sắp hết (days_until_empty thấp) => Ưu tiên số 2.
        
        Output (Định dạng Markdown):
        # 🚨 Cảnh báo khẩn cấp (Nếu có món days=0)
        - [Tên món]: Lý do ngắn gọn (VD: Tốc độ bán quá nhanh, kho sắp cạn).
        
        # 📦 Đề xuất nhập hàng
        - [Tên món] (Còn đủ bán ... ngày): Nên nhập thêm [Số lượng].
        
        # 💡 Mẹo kinh doanh hôm nay
        (Một câu lời khuyên dựa trên thứ trong tuần).

        Dữ liệu:
        {json.dumps(ai_input_data, ensure_ascii=False)}
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Lỗi kết nối AI: {str(e)}"