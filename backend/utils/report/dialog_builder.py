from PyQt6.QtWidgets import QVBoxLayout, QLabel, QDateEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QDate
from .base_widgets import TextInputWidget, create_number_validator
from .block_widget import BlockWidget
from .room_widget import RoomWidget
from .time_widget import TimeWidget
from .field_validator import MIN_STUDENTS, MAX_STUDENTS

class DialogBuilder:
    def __init__(self, dialog):
        self.dialog = dialog
        self.dialog.setWindowTitle("Report Details")
        self.dialog.setFixedWidth(320)
        self.layout = QVBoxLayout(dialog)

    def build_widgets(self):
        widgets = {}
        widgets['proctor'] = TextInputWidget("Proctor's Name:")
        widgets['proctor'].entry.setReadOnly(True)
        widgets['num_students'] = TextInputWidget(
            "Number of Students:",
            create_number_validator(MIN_STUDENTS, MAX_STUDENTS),
        )
        widgets['num_students'].entry.setToolTip("You can only put numbers here")
        widgets['block'] = BlockWidget()
        widgets['subject'] = TextInputWidget("Subject:")
        widgets['room'] = RoomWidget()
        widgets['start_time'] = TimeWidget("Start Time:")
        widgets['end_time'] = TimeWidget("End Time:")
        widgets['date_label'], widgets['date'] = self._setup_date_widget()
        return widgets

    def _setup_date_widget(self):
        label = QLabel("Exam Date:")
        date_widget = QDateEdit(calendarPopup=True)
        date_widget.setDate(QDate.currentDate())
        return label, date_widget

    def add_widgets_to_layout(self, widgets):
        for key in ['proctor', 'num_students', 'block', 'subject', 'room', 'start_time', 'end_time', 'date_label', 'date']:
            self.layout.addWidget(widgets[key])

    def setup_submit_button(self):
        submit_button = QPushButton("Submit")
        submit_button.setEnabled(False)
        submit_button.setToolTip("All fields must be filled out")
        self.layout.addWidget(submit_button)
        return submit_button

    def show_error(self, message):
        QMessageBox.critical(self.dialog, "Error", message)
