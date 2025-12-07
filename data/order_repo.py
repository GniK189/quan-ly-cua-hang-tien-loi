from data.db import db_instance
from datetime import datetime, timedelta
import pymongo

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