from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from .base_widgets import create_regex_validator

class BlockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(QLabel("Block:"))
        self._setup_inputs()

    def _setup_inputs(self):
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.year = QLineEdit()
        self.year.setValidator(create_regex_validator("^[0-9]{2}$"))
        self.year.setPlaceholderText("42")

        self.course = QLineEdit()
        self.course.setValidator(create_regex_validator("^[a-zA-Z]{2,5}$"))
        self.course.setPlaceholderText("CSE")

        self.number = QLineEdit()
        self.number.setValidator(create_regex_validator("^[0-9]{2}$"))
        self.number.setPlaceholderText("01")

        for widget in [self.year, QLabel("-"), self.course, QLabel("-"), self.number]:
            input_layout.addWidget(widget)

        self.layout.addWidget(input_container)

    def connect_change_handler(self, handler):
        self.year.textChanged.connect(handler)
        self.course.textChanged.connect(handler)
        self.number.textChanged.connect(handler)

    def get_block_text(self):
        course = self.course.text().upper()
        return f"{self.year.text()}-{course}-{self.number.text()}"

    def has_complete_input(self):
        return bool(self.year.text() and self.course.text() and self.number.text())
