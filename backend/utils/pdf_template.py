import logging
import os
from fpdf import FPDF
from PIL import Image
import tempfile

REPORT_DIR_NAME = "ProctorAI-Report"
WATERMARK_PATH = os.path.join("assets", "watermark.jpg")

class PDFReport(FPDF):
    def __del__(self):
        if hasattr(self, '_temp_watermark'):
            try:
                os.unlink(self._temp_watermark)
            except Exception as e:
                self.logger.error(f"Error deleting temporary watermark file: {e}")
                
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('report')

    def prepare_transparent_watermark(self):
        if not hasattr(self, '_temp_watermark'):
            with Image.open(WATERMARK_PATH) as img:
                img = img.convert('RGBA')
                transparent = Image.new('RGBA', img.size, (255, 255, 255, 0))
                blended = Image.blend(transparent, img, 0.50)
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                blended.save(temp_file.name, 'PNG')
                self._temp_watermark = temp_file.name
                self._watermark_original = img.size
    
    def add_watermark(self):
        self.prepare_transparent_watermark()
        
        page_width = self.w
        target_width = page_width * 0.8
        
        scale = target_width / self._watermark_original[0]
        target_height = self._watermark_original[1] * scale
        
        image_x = (page_width - target_width) / 2
        image_y = (self.h - target_height) / 2
        
        self.image(self._temp_watermark, x=image_x, y=image_y, w=target_width)

    def header(self):
        self.add_watermark()
        self.set_font("Arial", 'B', 20)
        self.cell(0, 5, "Proctor AI", ln=True, align='C')
        self.cell(0, 8, "Generated Report", ln=True, align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def body(self, proctor, block, date, subject, room, start, end, num_students):
        start_time = self.convert_to_12h(start)
        end_time = self.convert_to_12h(end)
        self.set_font("Arial", 'B', 12)
        self.cell(120, 7, f"Proctor: {proctor}", ln=False)
        self.cell(0, 7, f"Number of Students: {num_students}", ln=True)
        self.cell(120, 7, f"Subject: {subject}", ln=False)
        self.cell(0, 7, f"Block: {block}", ln=True)
        self.cell(120, 7, f"Exam Time: {start_time} - {end_time}", ln=False)
        self.cell(0, 7, f"Room: {room}", ln=True)
        self.cell(0, 7, f"Exam Date: {date}", ln=True)

    @staticmethod
    def convert_to_12h(time_str):
        hour, minute = map(int, time_str.split(':'))
        period = 'AM' if hour < 12 else 'PM'
        hour = hour % 12
        hour = 12 if hour == 0 else hour
        return f"{hour:02d}:{minute:02d} {period}"
