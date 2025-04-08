from PyQt6.QtWidgets import QStatusBar, QLabel

class StatusBarManager:
    def __init__(self, parent):
        self.parent = parent
        self.status_bar = QStatusBar()
        parent.setStatusBar(self.status_bar)
        self.setup_status_labels()

    def setup_status_labels(self):
        self.detected_objects_label = QLabel("Detected Objects: 0")
        self.status_bar.addWidget(self.detected_objects_label)

    def update_detections_count(self, count):
        self.detected_objects_label.setText(f"Detected Objects: {count}")

    def show_message(self, message, timeout=5000):
        self.status_bar.showMessage(message, timeout)

    def clear_message(self):
        self.status_bar.clearMessage()
