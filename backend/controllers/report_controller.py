import os
from backend.services.database_service import db_manager
from backend.utils.gui_utils import GUIManager
from fpdf import FPDF
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDateEdit, 
    QComboBox, QPushButton, QMessageBox, QHBoxLayout, QWidget
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

MIN_STUDENTS = 1
MAX_STUDENTS = 1000
INVALID_STUDENTS_MESSAGE = f"Number of students must be a positive number between {MIN_STUDENTS} and {MAX_STUDENTS}."
REPORT_DIR_NAME = "ProctorAI-Report"
NUMBER_FIELD_MESSAGE = "You can only put numbers here"

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
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        report_dir = os.path.join(desktop_path, REPORT_DIR_NAME)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        PDFReport.dialog = QDialog()
        PDFReport.dialog.setWindowTitle("Report Details")
        layout = QVBoxLayout(PDFReport.dialog)
        PDFReport.is_completed = False

        def create_label_entry(text, parent_layout):
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(text)
            entry = QLineEdit()
            container_layout.addWidget(label)
            container_layout.addWidget(entry)
            parent_layout.addWidget(container)
            return entry

        def closeEvent(event):
            if not PDFReport.is_completed:
                reply = QMessageBox.question(PDFReport.dialog, "Confirm Cancel", 
                    "Are you sure you want to cancel report generation?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    event.ignore()
                    return
            event.accept()

        PDFReport.dialog.closeEvent = closeEvent

        PDFReport.dialog.setFixedWidth(320)

        # Proctor Name 
        entry_proctor = create_label_entry("Proctor's Name:", layout)

        # Number of Students
        entry_num_students = create_label_entry("Number of Students:", layout)
        validator = QIntValidator(MIN_STUDENTS, MAX_STUDENTS)
        entry_num_students.setValidator(validator)
        entry_num_students.setToolTip(NUMBER_FIELD_MESSAGE)

        # Block inputs
        block_widget = QWidget()
        block_layout = QVBoxLayout(block_widget)
        block_layout.setContentsMargins(0, 0, 0, 0)
        block_layout.addWidget(QLabel("Block:"))
        
        block_inputs = QWidget()
        block_inputs_layout = QHBoxLayout(block_inputs)
        block_inputs_layout.setContentsMargins(0, 0, 0, 0)
        
        entry_block_year = QLineEdit()
        entry_block_year.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9]{2}$")))
        entry_block_year.setPlaceholderText("42")
        entry_block_year.setToolTip("Year and semester (e.g. 42 for 4th year 2nd sem)")
        
        entry_block_course = QLineEdit()
        entry_block_course.setValidator(QRegularExpressionValidator(QRegularExpression("^[a-zA-Z]{2,5}$")))
        entry_block_course.setPlaceholderText("cse")
        entry_block_course.setToolTip("Course code (e.g. cse)")
        
        entry_block_number = QLineEdit()
        entry_block_number.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9]{2}$")))
        entry_block_number.setPlaceholderText("01")
        entry_block_number.setToolTip("Block number (e.g. 01)")
        
        for widget in [entry_block_year, QLabel("-"), entry_block_course, QLabel("-"), entry_block_number]:
            block_inputs_layout.addWidget(widget)
        
        block_layout.addWidget(block_inputs)
        layout.addWidget(block_widget)

        # Subject
        entry_subject = create_label_entry("Subject:", layout)

        # Room inputs
        room_widget = QWidget()
        room_layout = QVBoxLayout(room_widget)
        room_layout.setContentsMargins(0, 0, 0, 0)
        room_layout.addWidget(QLabel("Room:"))
        
        room_inputs = QWidget()
        room_inputs_layout = QHBoxLayout(room_inputs)
        room_inputs_layout.setContentsMargins(0, 0, 0, 0)
        
        entry_room_building = QComboBox()
        entry_room_building.addItems(["A", "V", "L", "F", "E"])
        
        entry_room_number = QLineEdit()
        entry_room_number.setValidator(QRegularExpressionValidator(QRegularExpression("^[1-9][0-9]{2}$")))
        entry_room_number.setPlaceholderText("304")
        entry_room_number.setToolTip("Room number: First digit (1-9) for floor, last 2 digits (01-99) for room")
        
        room_inputs_layout.addWidget(entry_room_building)
        room_inputs_layout.addWidget(entry_room_number)
        room_layout.addWidget(room_inputs)
        layout.addWidget(room_widget)

        # Time Selection
        def create_time_inputs(label):
            time_widget = QWidget()
            time_layout = QVBoxLayout(time_widget)
            time_layout.setContentsMargins(0, 0, 0, 0)
            time_layout.addWidget(QLabel(label))
            
            time_inputs = QWidget()
            time_inputs_layout = QHBoxLayout(time_inputs)
            time_inputs_layout.setContentsMargins(0, 0, 0, 0)
            time_inputs_layout.setSpacing(20)
            
            hours = QComboBox()
            hours.addItems([f"{i:02d}" for i in range(1, 13)])
            
            minutes = QComboBox()
            minutes.addItems([f"{i:02d}" for i in range(0, 60, 5)])
            
            period = QComboBox()
            period.addItems(["AM", "PM"])
            
            colon_label = QLabel(":")
            
            time_inputs_layout.addWidget(hours)
            time_inputs_layout.addWidget(colon_label)
            time_inputs_layout.addWidget(minutes)
            time_inputs_layout.addWidget(period)
            time_inputs_layout.addStretch()
            
            time_layout.addWidget(time_inputs)
            return time_widget, hours, minutes, period
        
        start_time_widget, entry_start_hour, entry_start_minute, entry_start_period = create_time_inputs("Start Time:")
        layout.addWidget(start_time_widget)
        
        end_time_widget, entry_end_hour, entry_end_minute, entry_end_period = create_time_inputs("End Time:")
        layout.addWidget(end_time_widget)

        entry_date = QDateEdit(calendarPopup=True)
        entry_date.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Exam Date:"))
        layout.addWidget(entry_date)

        def validate_fields():
            is_valid = all([
                entry_proctor.text(),
                entry_block_year.text() and entry_block_course.text() and entry_block_number.text(),
                entry_subject.text(),
                entry_room_number.text(),
                entry_num_students.text()
            ])
            submit_button.setEnabled(is_valid)
            submit_button.setToolTip("All fields must be filled out" if not is_valid else "")

        submit_button = QPushButton("Submit")
        submit_button.setEnabled(False)
        submit_button.setToolTip("All fields must be filled out")
        layout.addWidget(submit_button)

        entry_proctor.textChanged.connect(validate_fields)
        entry_block_year.textChanged.connect(validate_fields)
        entry_block_course.textChanged.connect(validate_fields)
        entry_block_number.textChanged.connect(validate_fields)
        entry_subject.textChanged.connect(validate_fields)
        entry_room_number.textChanged.connect(validate_fields)
        entry_num_students.textChanged.connect(validate_fields)

        def on_submit():
            is_valid_students, students_error = PDFReport.validate_num_students(entry_num_students.text())
            if not is_valid_students:
                QMessageBox.critical(PDFReport.dialog, "Error", students_error)
                return

            block_parts = [entry_block_year.text(), entry_block_course.text(), entry_block_number.text()]
            is_valid_block, block_error = PDFReport.validate_block(*block_parts)
            if not is_valid_block:
                QMessageBox.critical(PDFReport.dialog, "Error", block_error)
                return

            room_parts = [entry_room_building.currentText(), entry_room_number.text()]
            is_valid_room, room_error = PDFReport.validate_room(*room_parts)
            if not is_valid_room:
                QMessageBox.critical(PDFReport.dialog, "Error", room_error)
                return
                
            PDFReport.dialog.accept()

        submit_button.clicked.connect(on_submit)
        if not PDFReport.dialog.exec():
            return None

        def convert_12h_to_24h(hour, minute, period):
            hour = int(hour)
            if period == "PM" and hour != 12:
                hour += 12
            elif period == "AM" and hour == 12:
                hour = 0
            return f"{hour:02d}:{minute}"

        start_time = convert_12h_to_24h(
            entry_start_hour.currentText(),
            entry_start_minute.currentText(),
            entry_start_period.currentText()
        )
        
        end_time = convert_12h_to_24h(
            entry_end_hour.currentText(),
            entry_end_minute.currentText(),
            entry_end_period.currentText()
        )
        
        block = f"{entry_block_year.text()}-{entry_block_course.text().lower()}-{entry_block_number.text()}"
        room = f"{entry_room_building.currentText()}{entry_room_number.text()}"

        raw_date = entry_date.date().toString("yyyy-MM-dd")
        year, month, day = raw_date.split('-')
        formatted_date = f"{month}-{day}-{year}"
        
        return (entry_proctor.text(), block, formatted_date,
                entry_subject.text(), room, start_time, end_time,
                entry_num_students.text())

    @staticmethod
    def validate_block(year, course, number):
        if not year or not year.isdigit() or len(year) != 2:
            return False, "Block year must be 2 digits"
        if not course or not course.isalpha() or len(course) < 2 or len(course) > 5:
            return False, "Course code must be 2-5 letters"
        if not number or not number.isdigit() or len(number) != 2:
            return False, "Block number must be 2 digits"
        return True, ""
    
    @staticmethod
    def validate_room(building, number):
        if not building or building not in ["A", "V", "L", "F", "E"]:
            return False, "Invalid building code"
        if not number or not number.isdigit() or len(number) != 3:
            return False, "Room number must be 3 digits"
        floor = int(number[0])
        room = int(number[1:])
        if floor < 1 or floor > 9:
            return False, "Floor must be between 1-9"
        if room < 1 or room > 99:
            return False, "Room number must be between 01-99"
        return True, ""

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
        details = PDFReport.prompt_report_details()
        if details is None:
            return False
            
        proctor, block, date, subject, room, start, end, num_students = details

        try:
            db_manager.insert_report_details(proctor, block, date, subject, room, start, end, num_students)
        except ValueError as e:
            QMessageBox.critical(PDFReport.dialog, "Error", str(e))
            return False

        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        report_dir = os.path.join(desktop_path, REPORT_DIR_NAME)
        pdf_filename = os.path.join(report_dir, f"{block}_{subject}_{date}.pdf")

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

        try:
            pdf.output(pdf_filename)
            QMessageBox.information(PDFReport.dialog, "PDF Saved", f"PDF saved as {pdf_filename}")
            GUIManager.cleanup()
            PDFReport.is_completed = True
            PDFReport.dialog.close()
            PDFReport.dialog = None
            return True
        except Exception as e:
            QMessageBox.critical(PDFReport.dialog, "Error", f"Failed to save PDF: {str(e)}")
            return False
