import logging
from fpdf import FPDF

REPORT_DIR_NAME = "ProctorAI-Report"

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('report')

    def header(self):
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
