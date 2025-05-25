from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import QTimer

class StatusBarManager:
    def __init__(self, parent, proctor_name=None, email=None):
        self.status_bar = QStatusBar()
        parent.setStatusBar(self.status_bar)
        self.connection_label = QLabel("●")
        self.connection_label.setStyleSheet("color: green; font-size: 18px;")
        self.status_bar.addWidget(self.connection_label)
        self.detected_objects_label = QLabel("Detected Objects: 0")
        self.status_bar.addWidget(self.detected_objects_label)
        self.proctor_info_label = QLabel("")
        if proctor_name and email:
            self.proctor_info_label.setText(
                f'Proctor: <b style="color:lime">{proctor_name}</b> | <b style="color:lime">{email}</b>'
            )
        self.status_bar.addPermanentWidget(self.proctor_info_label)
        self._blink_timer = QTimer()
        self._blink_timer.setInterval(500)
        self._blink_timer.timeout.connect(self._toggle_blink)
        self._blinking = False
        self._blink_state = True

    def update_detections_count(self, count):
        self.detected_objects_label.setText(f"Detected Students: {count}")

    def set_detection_status(self, status):
        if status == "connected":
            self._stop_blink()
            self.connection_label.setText("●")
            self.connection_label.setStyleSheet("color: green; font-size: 18px;")
        elif status == "disconnected":
            self._stop_blink()
            self.connection_label.setText("●")
            self.connection_label.setStyleSheet("color: red; font-size: 18px;")
        elif status == "retrying":
            self._start_blink()
        else:
            self._stop_blink()
            self.connection_label.setText("")
            self.connection_label.setStyleSheet("")

    def _start_blink(self):
        if not self._blinking:
            self._blinking = True
            self._blink_state = True
            self.connection_label.setText("●")
            self.connection_label.setStyleSheet("color: orange; font-size: 18px;")
            self._blink_timer.start()

    def _stop_blink(self):
        if self._blinking:
            self._blink_timer.stop()
            self._blinking = False
            self.connection_label.setText("●")
            self.connection_label.setStyleSheet("color: green; font-size: 18px;")

    def _toggle_blink(self):
        if self._blink_state:
            self.connection_label.setStyleSheet("color: orange; font-size: 18px;")
        else:
            self.connection_label.setStyleSheet("color: transparent; font-size: 18px;")
        self._blink_state = not self._blink_state

    def show_message(self, message, timeout=5000):
        self.status_bar.showMessage(message, timeout)

    def clear_message(self):
        self.status_bar.clearMessage()
