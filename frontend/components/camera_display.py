from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QSizePolicy, QFrame
)
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
        root_container = QWidget()
        root_layout = QVBoxLayout(root_container)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        self._setup_camera_controls(root_layout)
        self._setup_display_container(root_layout)
        
        self.setWidget(root_container)
        self._last_size = None

    def _setup_camera_controls(self, parent_layout):
        controls_layout = QHBoxLayout()
        self.camera_combo = QComboBox()
        controls_layout.addWidget(QLabel("Select Camera:"))
        controls_layout.addWidget(self.camera_combo)
        self.camera_button = AnimatedStateButton("Start Camera")
        self.camera_button.clicked.connect(lambda: self.camera_toggle_requested.emit())
        controls_layout.addWidget(self.camera_button)
        parent_layout.addLayout(controls_layout)

    def _setup_display_container(self, parent_layout):
        self.display_container = QFrame()
        self.display_container.setFrameStyle(QFrame.Shape.NoFrame)
        self.display_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        display_layout = QVBoxLayout(self.display_container)
        display_layout.setContentsMargins(0, 0, 0, 0)
        display_layout.setSpacing(0)
        display_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.display_label = QLabel()
        self.display_label.setStyleSheet("QLabel { background-color: black; border: 2px solid #444444; }")
        self.display_label.setMinimumSize(640, 360)
        self.display_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        display_layout.addWidget(self.display_label, 1)
        parent_layout.addWidget(self.display_container, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        available_width = int(self.width() * 0.95)
        available_height = int((self.height() - self.camera_button.height() - 40) * 0.95)
        
        max_width = available_width
        target_height = int(max_width * 9 / 16)
        
        if target_height > available_height:
            target_height = available_height
            max_width = int(target_height * 16 / 9)
            
        if (max_width, target_height) != self._last_size:
            self._last_size = (max_width, target_height)
            self.display_label.setFixedSize(max_width, target_height)

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
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.display_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.display_label.setPixmap(scaled_pixmap)
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
