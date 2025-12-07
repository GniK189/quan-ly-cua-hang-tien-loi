from data.db import db_instance
from bson.objectid import ObjectId

class ProductRepo:
    def __init__(self):
        self.collection = db_instance.get_collection("products")

    def get_all(self):
        return list(self.collection.find())

    def add_product(self, product_data):
        return self.collection.insert_one(product_data)

    def update_stock(self, product_id, quantity_sold):
        self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"stock": -quantity_sold}}
        )

    def update_product_info(self, product_id, update_data):
        self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
    
    def delete_product(self, product_id):
        self.collection.delete_one({"_id": ObjectId(product_id)})