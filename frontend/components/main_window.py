from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
from roboflow import Roboflow

from backend.controllers.camera_controller import CameraManager
from backend.controllers.detection_controller import DetectionManager
from config.settings import Settings
from .camera_display import CameraDisplayDock
from .detection_controls import DetectionControlsDock
from .report_manager import ReportManagerDock
from .status_bar import StatusBarManager
from .toolbar import ToolbarManager
from frontend.themes.theme_manager import ThemeManager
from backend.utils.gui_utils import GUIManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProctorAI")
        self.setGeometry(100, 100, 1280, 720)
        
        self.settings = Settings()
        self.theme_manager = ThemeManager(self)
        self.setup_window()
        self.setup_components()
        self.setup_model()
        self.connect_signals()
        
    def setup_window(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.camera_display = CameraDisplayDock("Camera and Display", self)
        self.report_manager = ReportManagerDock("Captured Images", self)
        self.detection_controls = DetectionControlsDock("Detection Controls", self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.camera_display)
        splitter.addWidget(self.report_manager)
        self.setCentralWidget(splitter)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.detection_controls)

    def setup_components(self):
        self.status_bar = StatusBarManager(self)
        self.toolbar = ToolbarManager(self)
        
    def setup_model(self):
        model, classes = self.initialize_roboflow()
        if model is None:
            QMessageBox.critical(self, "Error", "Failed to initialize Roboflow model.")
            sys.exit(1)

        self.camera_manager = CameraManager(self)
        self.detection_manager = DetectionManager(model, self)
        self.detection_controls.populate_filter_selection(classes)

    def connect_signals(self):
        self.camera_manager.frame_ready.connect(self.camera_display.update_display)
        self.detection_manager.detections_ready.connect(self.process_detections)
        
        self.camera_display.camera_toggle_requested.connect(self.toggle_camera)
        self.detection_controls.detection_toggle_requested.connect(self.toggle_detection)
        self.report_manager.pdf_generation_requested.connect(self.generate_pdf)

    def initialize_roboflow(self):
        try:
            rf = Roboflow(api_key=self.settings.get_setting("roboflow", "api_key"))
            project = rf.workspace().project(self.settings.get_setting("roboflow", "project"))
            model = project.version(self.settings.get_setting("roboflow", "model_version")).model
            return model, ["cheating", "not_cheating"]
        except Exception as e:
            print(f"Error initializing Roboflow: {e}")
            return None, []

    def toggle_camera(self):
        self.camera_manager.toggle_camera()

    def toggle_detection(self):
        self.detection_manager.toggle_detection()

    def generate_pdf(self):
        from backend.controllers.report_controller import PDFReport
        PDFReport.save_pdf()

    def process_detections(self, detections):
        self.status_bar.update_detections_count(len(detections))
        for detection in detections:
            if detection['class'] == self.get_selected_capture_class():
                GUIManager.capture_image(detection, self.camera_manager.current_image, self)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Exit Confirmation',
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup()
            event.accept()
        else:
            event.ignore()

    def cleanup(self):
        if hasattr(self, 'camera_manager'):
            self.camera_manager.cleanup()
        self.report_manager.cleanup()
        
    def get_selected_capture_class(self):
        return self.detection_controls.get_selected_capture_class()