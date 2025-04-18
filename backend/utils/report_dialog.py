from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDateEdit,
    QComboBox, QPushButton, QMessageBox, QHBoxLayout, QWidget
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from .report_validation import (
    validate_num_students, validate_block, validate_room,
    MIN_STUDENTS, MAX_STUDENTS, BUILDINGS
)

NUMBER_FIELD_MESSAGE = "You can only put numbers here"

class ReportDetailsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report Details")
        self.setFixedWidth(320)
        self.layout = QVBoxLayout(self)
        self.entries = {}
        self._build_ui()
        self.details = None

    def _label_entry(self, label, validator=None, placeholder=None):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        entry = QLineEdit()
        if validator:
            entry.setValidator(validator)
        if placeholder:
            entry.setPlaceholderText(placeholder)
        layout.addWidget(lbl)
        layout.addWidget(entry)
        self.layout.addWidget(container)
        return entry

    def _block_inputs(self):
        block_widget = QWidget()
        block_layout = QVBoxLayout(block_widget)
        block_layout.setContentsMargins(0, 0, 0, 0)
        block_layout.addWidget(QLabel("Block:"))
        block_inputs = QWidget()
        block_inputs_layout = QHBoxLayout(block_inputs)
        block_inputs_layout.setContentsMargins(0, 0, 0, 0)
        year = QLineEdit()
        year.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9]{2}$")))
        year.setPlaceholderText("42")
        course = QLineEdit()
        course.setValidator(QRegularExpressionValidator(QRegularExpression("^[a-zA-Z]{2,5}$")))
        course.setPlaceholderText("cse")
        number = QLineEdit()
        number.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9]{2}$")))
        number.setPlaceholderText("01")
        for w in [year, QLabel("-"), course, QLabel("-"), number]:
            block_inputs_layout.addWidget(w)
        block_layout.addWidget(block_inputs)
        self.layout.addWidget(block_widget)
        return year, course, number

    def _room_inputs(self):
        room_widget = QWidget()
        room_layout = QVBoxLayout(room_widget)
        room_layout.setContentsMargins(0, 0, 0, 0)
        room_layout.addWidget(QLabel("Room:"))
        room_inputs = QWidget()
        room_inputs_layout = QHBoxLayout(room_inputs)
        room_inputs_layout.setContentsMargins(0, 0, 0, 0)
        building = QComboBox()
        building.addItems(BUILDINGS)
        number = QLineEdit()
        number.setValidator(QRegularExpressionValidator(QRegularExpression("^[1-9][0-9]{2}$")))
        number.setPlaceholderText("304")
        room_inputs_layout.addWidget(building)
        room_inputs_layout.addWidget(number)
        room_layout.addWidget(room_inputs)
        self.layout.addWidget(room_widget)
        return building, number

    def _time_inputs(self, label):
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
        time_inputs_layout.addWidget(hours)
        time_inputs_layout.addWidget(QLabel(":"))
        time_inputs_layout.addWidget(minutes)
        time_inputs_layout.addWidget(period)
        time_inputs_layout.addStretch()
        time_layout.addWidget(time_inputs)
        self.layout.addWidget(time_widget)
        return hours, minutes, period

    def _build_ui(self):
        self.entries['proctor'] = self._label_entry("Proctor's Name:")
        self.entries['num_students'] = self._label_entry(
            "Number of Students:",
            QIntValidator(MIN_STUDENTS, MAX_STUDENTS),
        )
        self.entries['num_students'].setToolTip(NUMBER_FIELD_MESSAGE)
        self.entries['block_year'], self.entries['block_course'], self.entries['block_number'] = self._block_inputs()
        self.entries['subject'] = self._label_entry("Subject:")
        self.entries['room_building'], self.entries['room_number'] = self._room_inputs()
        self.entries['start_hour'], self.entries['start_minute'], self.entries['start_period'] = self._time_inputs("Start Time:")
        self.entries['end_hour'], self.entries['end_minute'], self.entries['end_period'] = self._time_inputs("End Time:")
        self.entries['date'] = QDateEdit(calendarPopup=True)
        self.entries['date'].setDate(QDate.currentDate())
        self.layout.addWidget(QLabel("Exam Date:"))
        self.layout.addWidget(self.entries['date'])
        self.submit_button = QPushButton("Submit")
        self.submit_button.setEnabled(False)
        self.submit_button.setToolTip("All fields must be filled out")
        self.layout.addWidget(self.submit_button)
        for key in ['proctor', 'block_year', 'block_course', 'block_number', 'subject', 'room_number', 'num_students']:
            self.entries[key].textChanged.connect(self._validate_fields)
        self.submit_button.clicked.connect(self._on_submit)

    def _validate_fields(self):
        e = self.entries
        valid = all([
            e['proctor'].text(),
            e['block_year'].text() and e['block_course'].text() and e['block_number'].text(),
            e['subject'].text(),
            e['room_number'].text(),
            e['num_students'].text()
        ])
        self.submit_button.setEnabled(valid)
        self.submit_button.setToolTip("" if valid else "All fields must be filled out")

    def _on_submit(self):
        e = self.entries
        valid_students, students_error = validate_num_students(e['num_students'].text())
        if not valid_students:
            QMessageBox.critical(self, "Error", students_error)
            return
        block_parts = [e['block_year'].text(), e['block_course'].text(), e['block_number'].text()]
        valid_block, block_error = validate_block(*block_parts)
        if not valid_block:
            QMessageBox.critical(self, "Error", block_error)
            return
        room_parts = [e['room_building'].currentText(), e['room_number'].text()]
        valid_room, room_error = validate_room(*room_parts)
        if not valid_room:
            QMessageBox.critical(self, "Error", room_error)
            return
        self.details = self._collect_details()
        self.accept()

    def _collect_details(self):
        e = self.entries
        def to_24h(hour, minute, period):
            h = int(hour)
            if period == "PM" and h != 12:
                h += 12
            elif period == "AM" and h == 12:
                h = 0
            return f"{h:02d}:{minute}"
        start_time = to_24h(e['start_hour'].currentText(), e['start_minute'].currentText(), e['start_period'].currentText())
        end_time = to_24h(e['end_hour'].currentText(), e['end_minute'].currentText(), e['end_period'].currentText())
        block = f"{e['block_year'].text()}-{e['block_course'].text().lower()}-{e['block_number'].text()}"
        room = f"{e['room_building'].currentText()}{e['room_number'].text()}"
        raw_date = e['date'].date().toString("yyyy-MM-dd")
        year, month, day = raw_date.split('-')
        formatted_date = f"{month}-{day}-{year}"
        return (
            e['proctor'].text(), block, formatted_date,
            e['subject'].text(), room, start_time, end_time,
            e['num_students'].text()
        )

def prompt_report_details():
    dialog = ReportDetailsDialog()
    if dialog.exec() and dialog.details:
        return dialog.details
    return None
