from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox
from ..report_validation import BUILDINGS
from .base_widgets import create_regex_validator

class RoomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(QLabel("Room:"))
        self._setup_inputs()

    def _setup_inputs(self):
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.building = QComboBox()
        self.building.addItems(BUILDINGS)
        self.building.setFixedWidth(60)

        self.number = QLineEdit()
        self.number.setValidator(create_regex_validator("^[1-9][0-9]{2}$"))
        self.number.setPlaceholderText("304")

        input_layout.addWidget(self.building)
        input_layout.addWidget(self.number)
        self.layout.addWidget(input_container)

    def connect_change_handler(self, handler):
        self.building.currentTextChanged.connect(handler)
        self.number.textChanged.connect(handler)

    def get_room_text(self):
        return f"{self.building.currentText()}{self.number.text()}"

    def has_complete_input(self):
        return bool(self.number.text())

    def get_building(self):
        return self.building.currentText()

    def get_number(self):
        return self.number.text()
