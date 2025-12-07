from data.db import db_instance
from datetime import datetime, timedelta
import pymongo
import calendar

class OrderRepo:
    def __init__(self):
        self.collection = db_instance.get_collection("orders")

    def create_order(self, items, total, customer_pay, change):
        order = {
            "created_at": datetime.now(),
            "items": items,
            "total": total,
            "customer_pay": customer_pay,
            "change": change
        }
        return self.collection.insert_one(order)

    def get_recent_orders(self, days=7):
        start_date = datetime.now() - timedelta(days=days)
        return list(self.collection.find({"created_at": {"$gte": start_date}}))

    def get_all_orders(self):
        return list(self.collection.find().sort("created_at", pymongo.DESCENDING))
    
    def search_orders(self, keyword=None, date_from=None, date_to=None):
        """
        Tìm kiếm đơn hàng theo từ khóa (Mã đơn) và khoảng thời gian
        """
        query_filter = {}

        # 1. Lọc theo ngày (Date Range)
        if date_from or date_to:
            query_filter["created_at"] = {}
            if date_from:
                # Bắt đầu từ 00:00:00 của ngày đó
                query_filter["created_at"]["$gte"] = date_from
            if date_to:
                # Kết thúc lúc 23:59:59 của ngày đó
                query_filter["created_at"]["$lte"] = date_to

        # Lấy dữ liệu từ DB (Sắp xếp mới nhất trước)
        cursor = self.collection.find(query_filter).sort("created_at", pymongo.DESCENDING)
        results = list(cursor)

        # 2. Lọc theo từ khóa (ID) - Xử lý phía Python cho linh hoạt với ObjectId
        if keyword:
            keyword = keyword.strip().upper()
            filtered_results = []
            for order in results:
                # Lấy 6 ký tự cuối của ID để so sánh (giống hiển thị trên UI)
                short_id = str(order["_id"])[-6:].upper()
                full_id = str(order["_id"]).upper()
                
                # Tìm tương đối: Khớp mã ngắn hoặc mã dài
                if keyword in short_id or keyword in full_id:
                    filtered_results.append(order)
            return filtered_results
        
        return results
    
    def get_revenue_last_7_days(self):
        """Tính doanh thu 7 ngày gần nhất (trả về dictionary {ngày: doanh_thu})"""
        start_date = datetime.now() - timedelta(days=6)
        # Reset về 0h00 để so sánh ngày
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%d/%m", "date": "$created_at"}
                    },
                    "daily_total": {"$sum": "$total"}
                }
            },
            {"$sort": {"_id": 1}} # Sắp xếp theo ngày tăng dần
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        # Chuyển đổi list thành dict để dễ vẽ biểu đồ
        data = {item["_id"]: item["daily_total"] for item in result}
        
        # Đảm bảo đủ 7 ngày (ngày nào không bán được thì revenue = 0)
        final_data = {}
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            date_str = date.strftime("%d/%m")
            final_data[date_str] = data.get(date_str, 0)
            
        return final_data

    def get_top_selling_products(self, limit=5):
        """Lấy top sản phẩm bán chạy nhất"""
        pipeline = [
            {"$unwind": "$items"}, # Tách mảng items ra từng dòng riêng
            {
                "$group": {
                    "_id": "$items.name",
                    "total_qty": {"$sum": "$items.qty"},
                    "total_revenue": {"$sum": "$items.total_line"}
                }
            },
            {"$sort": {"total_qty": -1}}, # Sắp xếp giảm dần theo số lượng
            {"$limit": limit}
        ]
        return list(self.collection.aggregate(pipeline))
    
    def get_stats_by_month(self, month, year):
        """Lấy thống kê doanh thu theo từng ngày trong tháng"""
        start_date = datetime(year, month, 1)
        # Tính ngày cuối tháng
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59)

        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {"$dayOfMonth": "$created_at"}, # Group theo ngày
                    "daily_revenue": {"$sum": "$total"},
                    "order_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        # Chuẩn hóa dữ liệu: Đảm bảo có đủ các ngày trong tháng (ngày không bán là 0)
        data = {}
        for day in range(1, last_day + 1):
            data[day] = 0
            
        for r in results:
            data[r["_id"]] = r["daily_revenue"]
            
        return data, sum(data.values()), len(list(self.collection.find({"created_at": {"$gte": start_date, "$lte": end_date}})))

    def get_category_stats(self, month, year):
        """Thống kê tỷ trọng doanh thu theo danh mục (cần lookup sang bảng products)"""
        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59)

        pipeline = [
            {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
            {"$unwind": "$items"},
            {
                "$lookup": {
                    "from": "products",
                    "localField": "items.product_id",
                    "foreignField": "_id",
                    "as": "product_info"
                }
            },
            {"$unwind": "$product_info"},
            {
                "$group": {
                    "_id": "$product_info.category", # Group theo Category
                    "total_revenue": {"$sum": "$items.total_line"}
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))