from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

class InputWidget(QWidget):
    def __init__(self, label_text):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(label_text)
        self.layout.addWidget(self.label)

    def set_validator(self, validator):
        if hasattr(self, 'entry'):
            self.entry.setValidator(validator)

class TextInputWidget(InputWidget):
    def __init__(self, label_text, validator=None, placeholder=None):
        super().__init__(label_text)
        self.entry = QLineEdit()
        if validator:
            self.set_validator(validator)
        if placeholder:
            self.entry.setPlaceholderText(placeholder)
        self.layout.addWidget(self.entry)

    def text(self):
        return self.entry.text()

    def connect_change_handler(self, handler):
        self.entry.textChanged.connect(handler)

def create_number_validator(min_val, max_val):
    return QIntValidator(min_val, max_val)

def create_regex_validator(pattern):
    return QRegularExpressionValidator(QRegularExpression(pattern))
