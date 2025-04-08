from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import cv2
import logging
from backend.utils.gui_utils import GUIManager

logger = logging.getLogger('camera')

class CameraDisplayDock(QDockWidget):
    camera_toggle_requested = pyqtSignal()
    last_size = None  # Track last logged size

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setup_ui()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        controls_layout = self.setup_camera_controls()
        layout.addLayout(controls_layout)

        display_layout = self.setup_display_area()
        layout.addLayout(display_layout)

        self.setWidget(container)

    def setup_camera_controls(self):
        controls_layout = QHBoxLayout()
        
        self.camera_combo = QComboBox()
        controls_layout.addWidget(QLabel("Select Camera:"))
        controls_layout.addWidget(self.camera_combo)

        self.camera_button = QPushButton("Start Camera")
        self.camera_button.clicked.connect(self.camera_toggle_requested.emit)
        controls_layout.addWidget(self.camera_button)

        return controls_layout

    def setup_display_area(self):
        display_layout = QVBoxLayout()
        
        self.display_label = QLabel()
        self.display_label.setStyleSheet("background-color: black; border: 2px solid #444444;")
        self.display_label.setMinimumSize(320, 240)  # Minimum size to prevent too small display
        display_layout.addWidget(self.display_label, alignment=Qt.AlignmentFlag.AlignCenter)

        return display_layout

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Calculate 90% of the dock's width
        dock_width = self.width()
        dock_height = self.height() - self.camera_button.height() - 40  # Account for controls and margins
        
        # Set display size based on available width while maintaining 4:3 aspect ratio
        target_width = int(dock_width * 0.9)
        target_height = int((target_width * 3) / 4)  # 4:3 aspect ratio
        
        # If target height is too tall, base dimensions on height instead
        if target_height > dock_height * 0.9:
            target_height = int(dock_height * 0.9)
            target_width = int((target_height * 4) / 3)
        
        # Only log if size has changed
        new_size = (target_width, target_height)
        if new_size != self.last_size:
            self.last_size = new_size
            logger.debug(f"Display resized to {target_width}x{target_height}")
            
        self.display_label.setFixedSize(target_width, target_height)

    def get_main_window(self):
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'filterCombo'):
                return parent
            parent = parent.parent()
        return None
        
    def update_display(self, frame, clear_markers=False):
        try:
            main_window = self.parent().window()
            if clear_markers:
                height, width = frame.shape[:2]
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                self.display_label.setPixmap(QPixmap.fromImage(q_image))
            else:
                GUIManager.display_frame(frame, self.display_label, main_window)
        except Exception as e:
            logger.error(f"Error updating display: {str(e)}")

    def reset_display(self):
        try:
            if hasattr(self.parent().window(), 'camera_manager'):
                current_frame = self.parent().window().camera_manager.current_image
                if current_frame is not None:
                    frame_rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                    self.update_display(frame_rgb, clear_markers=True)
                else:
                    logger.warning("No current frame available for display reset")
            else:
                logger.warning("Camera manager not available for display reset")
        except Exception as e:
            logger.error(f"Error resetting display: {str(e)}")

    def update_camera_button_text(self, is_running):
        self.camera_button.setText("Stop Camera" if is_running else "Start Camera")

    def get_selected_camera(self):
        return self.camera_combo.currentText()

    def populate_camera_list(self, cameras):
        try:
            self.camera_combo.clear()
            self.camera_combo.addItems(cameras)
            logger.info(f"Camera list updated with devices: {cameras}")
        except Exception as e:
            logger.error(f"Error populating camera list: {str(e)}")
