# core/ai_service.py
import google.generativeai as genai
from config import GEMINI_API_KEY
from data.product_repo import ProductRepo
from data.order_repo import OrderRepo
import json

genai.configure(api_key=GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash') # Dùng bản Flash cho nhanh
        self.product_repo = ProductRepo()
        self.order_repo = OrderRepo()

    def get_restock_suggestions(self):
        # 1. Thu thập dữ liệu
        products = self.product_repo.get_all()
        orders = self.order_repo.get_recent_orders(days=7)

        # 2. Tính toán thống kê (Logic thuần Python)
        product_stats = {} # {product_id: {name, total_sold}}
        
        for p in products:
            product_stats[str(p["_id"])] = {
                "name": p["name"],
                "stock": p["stock"],
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
            avg_per_day = round(stat["total_sold"] / 7, 1)
            
            # Chỉ gửi những món có bán được hoặc sắp hết hàng để tiết kiệm token
            if avg_per_day > 0 or stat["stock"] < 10:
                ai_input_data.append({
                    "product": stat["name"],
                    "stock_current": stat["stock"],
                    "avg_sales_per_day": avg_per_day,
                })

        if not ai_input_data:
            return "Dữ liệu bán hàng chưa đủ để phân tích."

        # 3. Gửi Prompt cho Gemini
        prompt = f"""
        Bạn là trợ lý quản lý kho hàng (Smart Reorder Assistant). 
        Dựa vào dữ liệu JSON dưới đây (tồn kho và bán trung bình ngày trong 7 ngày qua), hãy đưa ra lời khuyên nhập hàng ngắn gọn, thân thiện bằng tiếng Việt.
        
        Quy tắc:
        - Chỉ tập trung vào hàng sắp hết hoặc bán chạy.
        - Đề xuất số lượng cụ thể nên nhập (ước lượng cho 5-7 ngày tới).
        - Format kết quả dạng danh sách gạch đầu dòng dễ đọc.

        Dữ liệu:
        {json.dumps(ai_input_data, ensure_ascii=False)}
        """

        response = self.model.generate_content(prompt)
        return response.text