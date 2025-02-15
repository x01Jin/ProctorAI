from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from backend.utils.gui_utils import GUIManager

class CameraDisplayDock(QDockWidget):
    camera_toggle_requested = pyqtSignal()

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
        self.display_label.setFixedSize(640, 480)
        self.display_label.setStyleSheet("background-color: black; border: 2px solid #444444;")
        display_layout.addWidget(self.display_label, alignment=Qt.AlignmentFlag.AlignCenter)

        return display_layout

    def get_main_window(self):
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'filterCombo'):
                return parent
            parent = parent.parent()
        return None
        
    def update_display(self, frame):
        main_window = self.parent().window()
        GUIManager.display_frame(frame, self.display_label, main_window)

    def update_camera_button_text(self, is_running):
        self.camera_button.setText("Stop Camera" if is_running else "Start Camera")

    def get_selected_camera(self):
        return self.camera_combo.currentText()

    def populate_camera_list(self, cameras):
        self.camera_combo.clear()
        self.camera_combo.addItems(cameras)