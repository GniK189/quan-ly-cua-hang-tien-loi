# app/stats_ai_view.py
import tkinter as tk
from tkinter import ttk
import threading
from core.ai_service import AIService

class StatsAIView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.ai_service = AIService()
        self.create_widgets()

    def create_widgets(self):
        # Tiêu đề
        lbl_title = ttk.Label(self, text="✨ AI Smart Reorder Assistant", font=("Arial", 16, "bold"), foreground="blue")
        lbl_title.pack(pady=20)

        # Nút gọi AI
        self.btn_analyze = ttk.Button(self, text="Phân tích & Gợi ý nhập hàng ngay", command=self.run_analysis)
        self.btn_analyze.pack(pady=10)

        self.lbl_status = ttk.Label(self, text="Nhấn nút trên để AI phân tích dữ liệu...", foreground="gray")
        self.lbl_status.pack()

        # Khu vực hiển thị kết quả
        self.txt_result = tk.Text(self, height=15, width=70, font=("Consolas", 10))
        self.txt_result.pack(padx=20, pady=10)

    def run_analysis(self):
        self.btn_analyze.config(state="disabled")
        self.lbl_status.config(text="AI đang đọc dữ liệu bán hàng và suy nghĩ... (Vui lòng đợi)")
        self.txt_result.delete("1.0", tk.END)
        
        # Chạy luồng riêng để không đơ UI
        thread = threading.Thread(target=self.process_ai)
        thread.start()

    def process_ai(self):
        try:
            suggestion = self.ai_service.get_restock_suggestions()
            # Cập nhật UI từ main thread (an toàn)
            self.after(0, self.update_ui_result, suggestion)
        except Exception as e:
            self.after(0, self.update_ui_result, f"Lỗi: {str(e)}")

    def update_ui_result(self, text):
        self.txt_result.insert(tk.END, text)
        self.lbl_status.config(text="Hoàn tất!")
        self.btn_analyze.config(state="normal")