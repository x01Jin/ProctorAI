from PyQt6.QtWidgets import QStatusBar, QLabel
from backend.services.application_state import ApplicationState

class StatusBarManager:
    def __init__(self, parent):
        self.parent = parent
        self.status_bar = QStatusBar()
        parent.setStatusBar(self.status_bar)
        self.setup_status_labels()

    def setup_status_labels(self):
        self.detected_objects_label = QLabel("Detected Objects: 0")
        self.status_bar.addWidget(self.detected_objects_label)

        app_state = ApplicationState.get_instance()
        self.internet_status_label = QLabel(f"Internet: {'Connected' if app_state.internet_connected else 'Disconnected'}")
        self.database_status_label = QLabel(f"Database: {'Connected' if app_state.db_connected else 'Disconnected'}")
        self.status_bar.addPermanentWidget(self.internet_status_label)
        self.status_bar.addPermanentWidget(self.database_status_label)

    def update_connection_status(self, internet=None, database=None):
        if internet is not None:
            self.internet_status_label.setText(f"Internet: {'Connected' if internet else 'Disconnected'}")
        if database is not None:
            self.database_status_label.setText(f"Database: {'Connected' if database else 'Disconnected'}")

    def update_detections_count(self, count):
        self.detected_objects_label.setText(f"Detected Objects: {count}")

    def show_message(self, message, timeout=5000):
        self.status_bar.showMessage(message, timeout)

    def clear_message(self):
        self.status_bar.clearMessage()
