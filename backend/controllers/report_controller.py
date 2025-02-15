from fpdf import FPDF
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QComboBox, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import QDate
from datetime import datetime
import os
from backend.services.database_service import db_manager
from backend.utils.gui_utils import GUIManager

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 20)
        self.cell(0, 5, "Proctor AI", ln=True, align='C')
        self.cell(0, 8, "Generated Report", ln=True, align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def body(self, proctor, block, date, subject, room, start, end):
        self.set_font("Arial", 'B', 12)
        self.cell(120, 7, f"Name: {proctor}", ln=False)
        self.cell(0, 7, f"Time Generated: {datetime.now().strftime('%H:%M:%S')}", ln=True)
        self.cell(120, 7, f"Exam Date: {date}", ln=False)
        self.cell(0, 7, f"Subject: {subject}", ln=True)
        self.cell(120, 7, f"Block: {block}", ln=False)
        self.cell(0, 7, f"Room: {room}", ln=True)
        self.cell(120, 7, f"Start Time: {start}", ln=False)
        self.cell(0, 7, f"End Time: {end}", ln=True)

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
        entry_block = create_label_entry("Block:")
        entry_date = QDateEdit(calendarPopup=True)
        entry_date.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Exam Date:"))
        layout.addWidget(entry_date)
        entry_subject = create_label_entry("Subject:")
        entry_room = create_label_entry("Room:")
        entry_start = QComboBox()
        entry_start.addItems([f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)])
        layout.addWidget(QLabel("Start Time:"))
        layout.addWidget(entry_start)
        entry_end = QComboBox()
        entry_end.addItems([f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)])
        layout.addWidget(QLabel("End Time:"))
        layout.addWidget(entry_end)

        submit_button = QPushButton("Submit")
        layout.addWidget(submit_button)

        def on_submit():
            PDFReport.dialog.accept()

        submit_button.clicked.connect(on_submit)
        PDFReport.dialog.exec()

        return (entry_proctor.text(), entry_block.text(), entry_date.date().toString("yyyy-MM-dd"),
                entry_subject.text(), entry_room.text(), entry_start.currentText(), entry_end.currentText())

    @staticmethod
    def save_pdf():
        proctor, block, date, subject, room, start, end = PDFReport.prompt_report_details()
        if not all([proctor, block, date, subject, room, start, end]):
            QMessageBox.critical(PDFReport.dialog, "Error", "All fields must be filled out.")
            return

        db_manager.insert_report_details(proctor, block, date, subject, room, start, end)

        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Report')
        pdf_filename, _ = QFileDialog.getSaveFileName(None, "Save PDF", desktop_path, "PDF files (*.pdf)")
        if not pdf_filename:
            return

        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()
        pdf.body(proctor, block, date, subject, room, start, end)

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
        GUIManager.cleanup(PDFReport.dialog)
        PDFReport.dialog = None
