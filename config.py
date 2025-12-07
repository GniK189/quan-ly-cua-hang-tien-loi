import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "convenience_store_db") # Giá trị mặc định nếu không tìm thấy
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ CẢNH BÁO: Chưa tìm thấy GEMINI_API_KEY trong file .env")