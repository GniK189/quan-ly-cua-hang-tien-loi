import os
import sys
from dotenv import load_dotenv

# --- ĐOẠN CODE MỚI ĐỂ TÌM FILE .ENV TRONG EXE ---
if getattr(sys, 'frozen', False):
    # Nếu đang chạy từ file exe (đã đóng gói)
    base_path = sys._MEIPASS
else:
    # Nếu đang chạy code Python bình thường
    base_path = os.path.dirname(os.path.abspath(__file__))

# Load file .env từ đúng đường dẫn đã xác định
load_dotenv(os.path.join(base_path, '.env'))
# ------------------------------------------------

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "convenience_store_db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ CẢNH BÁO: Chưa tìm thấy GEMINI_API_KEY trong file .env")