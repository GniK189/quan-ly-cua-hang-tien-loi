from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]

    def get_collection(self, name):
        return self.db[name]

db_instance = Database()