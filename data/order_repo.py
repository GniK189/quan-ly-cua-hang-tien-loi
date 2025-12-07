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