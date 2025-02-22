import os
from backend.services.database_service import db_manager
from backend.utils.gui_utils import GUIManager
from fpdf import FPDF
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QComboBox, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import QDate

MIN_STUDENTS = 1
MAX_STUDENTS = 1000
EMPTY_FIELDS_MESSAGE = "All fields must be filled out."
INVALID_STUDENTS_MESSAGE = f"Number of students must be a positive number between {MIN_STUDENTS} and {MAX_STUDENTS}."

class PDFReport(FPDF):
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

    @staticmethod
    def get_time_options():
        times = []
        for h in range(24):
            for m in (0, 30):
                hour = h % 12
                hour = 12 if hour == 0 else hour
                period = 'AM' if h < 12 else 'PM'
                display_time = f"{hour:02d}:{m:02d} {period}"
                store_time = f"{h:02d}:{m:02d}"
                times.append((display_time, store_time))
        return times

    @staticmethod
    def prompt_report_details():
        PDFReport.dialog = QDialog()
        PDFReport.dialog.setWindowTitle("Report Details")
        layout = QVBoxLayout(PDFReport.dialog)

        def create_label_entry(text):
            label = QLabel(text)
            entry = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(entry)
            return entry

        entry_proctor = create_label_entry("Proctor's Name:")
        entry_num_students = create_label_entry("Number of Students:")
        entry_block = create_label_entry("Block:")
        entry_subject = create_label_entry("Subject:")
        entry_room = create_label_entry("Room:")

        time_options = PDFReport.get_time_options()
        
        entry_start = QComboBox()
        for display_time, _ in time_options:
            entry_start.addItem(display_time)
        layout.addWidget(QLabel("Start Time:"))
        layout.addWidget(entry_start)
        
        entry_end = QComboBox()
        for display_time, _ in time_options:
            entry_end.addItem(display_time)
        layout.addWidget(QLabel("End Time:"))
        layout.addWidget(entry_end)

        entry_date = QDateEdit(calendarPopup=True)
        entry_date.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Exam Date:"))
        layout.addWidget(entry_date)

        submit_button = QPushButton("Submit")
        layout.addWidget(submit_button)

        def on_submit():
            PDFReport.dialog.accept()

        submit_button.clicked.connect(on_submit)
        PDFReport.dialog.exec()

        start_time = time_options[entry_start.currentIndex()][1]
        end_time = time_options[entry_end.currentIndex()][1]

        return (entry_proctor.text(), entry_block.text(), entry_date.date().toString("yyyy-MM-dd"),
                entry_subject.text(), entry_room.text(), start_time, end_time,
                entry_num_students.text())

    @staticmethod
    def validate_num_students(num_students_str):
        is_numeric = num_students_str.isdigit()
        
        if not is_numeric:
            return False, INVALID_STUDENTS_MESSAGE
            
        num_students = int(num_students_str)
        is_valid_range = MIN_STUDENTS <= num_students <= MAX_STUDENTS
        
        if not is_valid_range:
            return False, INVALID_STUDENTS_MESSAGE
            
        return True, ""

    @staticmethod
    def save_pdf():
        proctor, block, date, subject, room, start, end, num_students = PDFReport.prompt_report_details()
        if not all([proctor, block, date, subject, room, start, end, num_students]):
            QMessageBox.critical(PDFReport.dialog, "Error", EMPTY_FIELDS_MESSAGE)
            return

        is_valid, error_message = PDFReport.validate_num_students(num_students)
        if not is_valid:
            QMessageBox.critical(PDFReport.dialog, "Error", error_message)
            return

        try:
            db_manager.insert_report_details(proctor, block, date, subject, room, start, end, num_students)
        except ValueError as e:
            QMessageBox.critical(PDFReport.dialog, "Error", str(e))
            return

        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Report')
        pdf_filename, _ = QFileDialog.getSaveFileName(None, "Save PDF", desktop_path, "PDF files (*.pdf)")
        if not pdf_filename:
            return

        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()
        pdf.body(proctor, block, date, subject, room, start, end, num_students)

        image_count = 0
        x_positions = [10, 110]
        y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]

        for filename in os.listdir("tempcaptures"):
            if filename.endswith(".jpg"):
                if image_count > 0 and image_count % 4 == 0:
                    pdf.add_page()
                    y_positions = [pdf.get_y() + 10, pdf.get_y() + 110]

                image_path = os.path.join("tempcaptures", filename)
                x = x_positions[image_count % 2]
                y = y_positions[(image_count // 2) % 2]
                pdf.image(image_path, x=x, y=y, w=90, h=90)
                pdf.set_font("Arial", size=8)
                pdf.set_xy(x, y - 5)
                filename_without_extension = os.path.splitext(filename)[0]
                pdf.cell(90, 5, filename_without_extension, 0, 0, 'C')
                image_count += 1

        pdf.output(pdf_filename)
        QMessageBox.information(PDFReport.dialog, "PDF Saved", f"PDF saved as {pdf_filename}")
        GUIManager.cleanup()
        PDFReport.dialog.close()
        PDFReport.dialog = None
