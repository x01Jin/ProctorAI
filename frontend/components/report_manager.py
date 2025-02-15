from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QPushButton,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from backend.utils.gui_utils import GUIManager
import os

class ReportManagerDock(QDockWidget):
    pdf_generation_requested = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setup_ui()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.setup_scroll_area(layout)

        self.setup_pdf_button(layout)

        self.setWidget(container)
        self.setMinimumWidth(300)

    def setup_scroll_area(self, layout):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.scroll_area.setWidget(self.image_container)
        
        layout.addWidget(self.scroll_area)

    def setup_pdf_button(self, layout):
        self.pdf_button = QPushButton("Generate PDF Report")
        self.pdf_button.clicked.connect(self.pdf_generation_requested.emit)
        layout.addWidget(self.pdf_button)

    def display_captures(self, detections):
        main_window = self.parent().parent()
        GUIManager.display_captures(detections, self.image_layout, main_window)

    def cleanup(self):
        GUIManager.refresh_captures(self.image_layout)

        temp_dir = "tempcaptures"
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    def clear_captures(self):
        self.cleanup()
        while self.image_layout.count():
            item = self.image_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()