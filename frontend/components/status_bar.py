from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import QTimer
from backend.utils.gui_utils import GUIManager

class StatusBarManager:
    def __init__(self, parent):
        self.parent = parent
        self.status_bar = QStatusBar()
        parent.setStatusBar(self.status_bar)
        
        self.setup_status_labels()
        self.setup_status_timers()
        self.update_initial_status()

    def setup_status_labels(self):
        self.detected_objects_label = QLabel("Detected Objects: 0")
        self.status_bar.addWidget(self.detected_objects_label)

        self.internet_status_label = QLabel("Internet: Checking")
        self.database_status_label = QLabel("Database: Checking")
        self.status_bar.addPermanentWidget(self.internet_status_label)
        self.status_bar.addPermanentWidget(self.database_status_label)

    def setup_status_timers(self):
        self.internet_status_timer = QTimer(self.parent)
        self.internet_status_timer.timeout.connect(
            lambda: GUIManager.update_internet_status(self.internet_status_label)
        )
        self.internet_status_timer.start(1000)

        self.database_status_timer = QTimer(self.parent)
        self.database_status_timer.timeout.connect(
            lambda: GUIManager.update_database_status(self.database_status_label)
        )
        self.database_status_timer.start(1000)

    def update_initial_status(self):
        GUIManager.update_status(self.internet_status_label, self.database_status_label)

    def update_detections_count(self, count):
        self.detected_objects_label.setText(f"Detected Objects: {count}")

    def show_message(self, message, timeout=5000):
        self.status_bar.showMessage(message, timeout)

    def clear_message(self):
        self.status_bar.clearMessage()

    def cleanup(self):
        self.internet_status_timer.stop()
        self.database_status_timer.stop()