# app/stats_ai_view.py
import tkinter as tk
from tkinter import ttk
import threading
import re
from tkinter.font import Font
from core.ai_service import AIService

class MarkdownText(tk.Text):
    """
    Widget Text tùy chỉnh để hiển thị Markdown đơn giản (Heading, Bold, List)
    mà không cần HTML.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cấu hình font chữ cơ bản (Đẹp hơn font mặc định)
        self.default_font = Font(family="Segoe UI", size=12)
        self.configure(font=self.default_font, wrap="word", padx=10, pady=10)
        
        # Định nghĩa các Style (Tags)
        # 1. Heading (Màu xanh, to, đậm)
        self.tag_configure("h1", font=("Segoe UI", 16, "bold"), foreground="#2980b9", spacing3=10)
        self.tag_configure("h2", font=("Segoe UI", 14, "bold"), foreground="#3498db", spacing3=5)
        
        # 2. Bold (Màu đỏ, đậm - để nhấn mạnh sản phẩm)
        self.tag_configure("bold", font=("Segoe UI", 12, "bold"), foreground="#c0392b")
        
        # 3. List (Thụt đầu dòng)
        self.tag_configure("li", lmargin1=20, lmargin2=20) 
        
        # 4. Normal text
        self.tag_configure("body", foreground="#333333")

    def load_markdown(self, text):
        """Parse text và áp dụng format"""
        self.config(state="normal")
        self.delete("1.0", tk.END)
        
        # Duyệt qua từng dòng để xử lý
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                self.insert(tk.END, "\n")
                continue

            # Xử lý Heading (#)
            if line.startswith("# "):
                self.insert(tk.END, line[2:] + "\n", "h1")
            elif line.startswith("## "):
                self.insert(tk.END, line[3:] + "\n", "h2")
            
            # Xử lý List (-)
            elif line.startswith("- "):
                # Insert dấu chấm tròn thay cho dấu gạch ngang cho đẹp
                self.insert(tk.END, "• " + line[2:] + "\n", "li")
            
            # Xử lý Text thường
            else:
                self.insert(tk.END, line + "\n", "body")

        # --- Xử lý Bold (**) sau khi đã insert text ---
        # Dùng Regex tìm tất cả các đoạn nằm giữa **...**
        content = self.get("1.0", tk.END)
        for match in re.finditer(r'\*\*(.*?)\*\*', content):
            start = match.start()
            end = match.end()
            
            # Chuyển đổi index từ python string sang index của tk.Text (dòng.cột)
            # Lưu ý: Cách này tính tương đối, để chính xác tuyệt đối cần duyệt kỹ hơn.
            # Nhưng với logic insert từng dòng ở trên, ta có thể highlight thủ công bằng regex search của Tkinter.
            pass 
        
        # Cách highlight Bold chuẩn xác hơn bằng công cụ search của Tkinter
        start_idx = "1.0"
        while True:
            # Tìm ký tự ** mở đầu
            match_start = self.search(r"\*\*", start_idx, stopindex=tk.END, regexp=True)
            if not match_start: break
            
            # Tìm ký tự ** kết thúc
            # +2 char để bỏ qua 2 dấu sao vừa tìm
            search_from = f"{match_start}+2c" 
            match_end = self.search(r"\*\*", search_from, stopindex=tk.END, regexp=True)
            if not match_end: break
            
            # Tính toán vị trí thực tế
            text_start = f"{match_start}+2c"
            text_end = match_end
            end_marker = f"{match_end}+2c"

            # Apply tag Bold cho phần text ở giữa
            self.tag_add("bold", text_start, text_end)
            
            # Ẩn các dấu ** đi cho đẹp (Hoặc comment dòng dưới nếu muốn giữ lại **)
            self.tag_add("hide", match_start, text_start) # Cần config tag hide nếu muốn ẩn
            self.tag_add("hide", match_end, end_marker)

            start_idx = end_marker
            
        # Config tag ẩn (cho màu chữ trùng màu nền hoặc size=0)
        self.tag_configure("hide", elide=True) # elide=True là tính năng ẩn text của Tkinter

        self.config(state="disabled")


class StatsAIView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.ai_service = AIService()
        self.create_widgets()

    def create_widgets(self):
        # Tiêu đề
        lbl_title = ttk.Label(self, text="✨ AI Smart Reorder Assistant", font=("Segoe UI", 16, "bold"), foreground="#2980b9")
        lbl_title.pack(pady=20)

        # Nút gọi AI
        self.btn_analyze = ttk.Button(self, text="Phân tích & Gợi ý nhập hàng ngay", command=self.run_analysis)
        self.btn_analyze.pack(pady=10)

        self.lbl_status = ttk.Label(self, text="Nhấn nút trên để AI phân tích dữ liệu...", foreground="gray", font=("Segoe UI", 10))
        self.lbl_status.pack()

        # --- Dùng Widget tự viết MarkdownText ---
        self.txt_result = MarkdownText(self, height=15, width=80, relief="flat", background="#f9f9f9")
        self.txt_result.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Text mặc định
        self.txt_result.load_markdown("# Xin chào!\nNhấn nút **Phân tích** để nhận báo cáo.")

    def run_analysis(self):
        self.btn_analyze.config(state="disabled")
        self.lbl_status.config(text="AI đang đọc dữ liệu bán hàng và suy nghĩ... (Vui lòng đợi)")
        self.txt_result.load_markdown("Đang tải dữ liệu...")
        
        thread = threading.Thread(target=self.process_ai)
        thread.start()

    def process_ai(self):
        try:
            # Lấy text markdown từ AI
            suggestion = self.ai_service.get_restock_suggestions()
            self.after(0, self.update_ui_result, suggestion)
        except Exception as e:
            self.after(0, self.update_ui_result, f"# Lỗi xảy ra\n{str(e)}")

    def update_ui_result(self, text):
        # Gọi hàm load_markdown của widget để hiển thị đẹp
        self.txt_result.load_markdown(text)
        
        self.lbl_status.config(text="Hoàn tất!")
        self.btn_analyze.config(state="normal")