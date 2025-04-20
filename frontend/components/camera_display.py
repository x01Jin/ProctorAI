from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from .buttons import AnimatedStateButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import cv2
from backend.utils.gui.frame_display_manager import display_frame

class CameraDisplayDock(QDockWidget):
    camera_toggle_requested = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self._last_frame = None
        self._init_ui()

    def _init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        controls_layout = QHBoxLayout()
        self.camera_combo = QComboBox()
        controls_layout.addWidget(QLabel("Select Camera:"))
        controls_layout.addWidget(self.camera_combo)
        self.camera_button = AnimatedStateButton("Start Camera")
        self.camera_button.clicked.connect(lambda: self.camera_toggle_requested.emit())
        controls_layout.addWidget(self.camera_button)
        layout.addLayout(controls_layout)

        self.display_label = QLabel()
        self.display_label.setStyleSheet("background-color: black; border: 2px solid #444444;")
        self.display_label.setMinimumSize(320, 240)
        layout.addWidget(self.display_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setWidget(container)
        self._last_size = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        dock_width = self.width()
        dock_height = self.height() - self.camera_button.height() - 40
        target_width = int(dock_width * 0.9)
        target_height = int((target_width * 3) / 4)
        if target_height > dock_height * 0.9:
            target_height = int(dock_height * 0.9)
            target_width = int((target_height * 4) / 3)
        new_size = (target_width, target_height)
        if new_size != self._last_size:
            self._last_size = new_size
        self.display_label.setFixedSize(target_width, target_height)

    def update_display(self, frame=None, clear_markers=False):
        main_window = self.parent().window()
        if frame is not None:
            self._last_frame = frame
        frame_to_display = self._last_frame
        if frame_to_display is None:
            return
        if clear_markers:
            height, width = frame_to_display.shape[:2]
            bytes_per_line = 3 * width
            q_image = QImage(frame_to_display.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            self.display_label.setPixmap(QPixmap.fromImage(q_image))
        else:
            display_frame(frame_to_display, self.display_label, main_window)

    def reset_display(self):
        main_window = self.parent().window()
        if hasattr(main_window, 'camera_manager'):
            current_frame = main_window.camera_manager.current_image
            if current_frame is not None:
                frame_rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                self.update_display(frame_rgb, clear_markers=True)

    def update_camera_button_text(self, is_running):
        self.camera_button.setText("Stop Camera" if is_running else "Start Camera")
        self.camera_button.set_active(is_running)

    def get_selected_camera(self):
        return self.camera_combo.currentText()

    def populate_camera_list(self, cameras):
        self.camera_combo.clear()
        self.camera_combo.addItems(cameras)
