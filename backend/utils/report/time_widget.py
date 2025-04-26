from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox

class TimeWidget(QWidget):
    def __init__(self, label_text):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(QLabel(label_text))
        self._setup_inputs()

    def _setup_inputs(self):
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(20)

        self.hours = QComboBox()
        self.hours.addItems([f"{i:02d}" for i in range(1, 13)])
        self.hours.setFixedWidth(60)

        self.minutes = QComboBox()
        self.minutes.addItems([f"{i:02d}" for i in range(0, 60, 5)])
        self.minutes.setFixedWidth(60)

        self.period = QComboBox()
        self.period.addItems(["AM", "PM"])
        self.period.setFixedWidth(60)

        input_layout.addWidget(self.hours)
        input_layout.addWidget(QLabel(":"))
        input_layout.addWidget(self.minutes)
        input_layout.addWidget(self.period)
        input_layout.addStretch()

        self.layout.addWidget(input_container)

    def connect_change_handler(self, handler):
        self.hours.currentTextChanged.connect(handler)
        self.minutes.currentTextChanged.connect(handler)
        self.period.currentTextChanged.connect(handler)

    def get_time_24h(self):
        hour = int(self.hours.currentText())
        minute = self.minutes.currentText()
        period = self.period.currentText()

        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute}"
