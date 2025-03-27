from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QMessageBox, QDockWidget
)
from PyQt6.QtCore import Qt, QTimer
import sys
from backend.controllers.camera_controller import CameraManager
from backend.controllers.detection_controller import DetectionManager
from config.settings_manager import SettingsManager
from .camera_display import CameraDisplayDock
from .detection_controls import DetectionControlsDock
from .report_manager import ReportManagerDock
from .status_bar import StatusBarManager
from .toolbar import ToolbarManager
from frontend.themes.theme_manager import ThemeManager
from backend.utils.gui_utils import GUIManager
from backend.services.application_state import ApplicationState

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProctorAI Release v1.3.8r")
        
        # Calculate 90% of screen size for window dimensions
        screen = self.screen().availableGeometry()
        width = int(screen.width() * 0.9)
        height = int(screen.height() * 0.9)
        self.resize(width, height)
        
        # Center window on screen
        self.move((screen.width() - width) // 2,
                 (screen.height() - height) // 2)
                 
        # Initialize ApplicationState first
        self.app_state = ApplicationState.get_instance()
        
        self.settings = SettingsManager()
        self.theme_manager = ThemeManager(self)
        self.setup_window()
        self.setup_components()
        self.setup_model()
        self.connect_signals()
        self.setup_connection_monitor()
        
    def setup_window(self):
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            self.camera_display = CameraDisplayDock("Camera and Display", self)
            self.camera_display.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
            
            self.report_manager = ReportManagerDock("Captured Images", self)
            self.report_manager.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
            
            self.detection_controls = DetectionControlsDock("Detection Controls", self)
            self.detection_controls.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.addWidget(self.camera_display)
            splitter.addWidget(self.report_manager)
            self.setCentralWidget(splitter)
            self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.detection_controls)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to setup window: {str(e)}")
            sys.exit(1)

    def setup_components(self):
        self.status_bar = StatusBarManager(self)
        self.toolbar = ToolbarManager(self)
        
    def setup_model(self):
        # Get initialized Roboflow instance
        rf = self.app_state.roboflow
        if rf is None or not rf.model:
            QMessageBox.critical(self, "Error", "Roboflow model not initialized.")
            sys.exit(1)

        self.camera_manager = CameraManager(self)
        self.detection_manager = DetectionManager(rf.model, self)
        self.detection_controls.populate_filter_selection(rf.classes)

    def connect_signals(self):
        self.camera_manager.frame_ready.connect(self.camera_display.update_display)
        self.detection_manager.detections_ready.connect(self.process_detections)
        self.detection_manager.detection_stopped.connect(self.on_detection_stopped)
        
        self.camera_display.camera_toggle_requested.connect(self.toggle_camera)
        self.detection_controls.detection_toggle_requested.connect(self.toggle_detection)
        self.report_manager.pdf_generation_requested.connect(self.generate_pdf)

    def on_detection_stopped(self):
        self.camera_display.reset_display()
        self.status_bar.update_detections_count(0)

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

    def setup_connection_monitor(self):
        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.check_connections)
        # Check connections every 30 seconds
        self.connection_timer.start(30000)
        
    def check_connections(self):
        if not self.app_state.database:
            return
            
        # Check connections and update status bar
        internet_status = GUIManager.check_internet_status()
        database_status = GUIManager.check_database_status()
        
        self.app_state.update_connection_status(
            internet=internet_status,
            database=database_status
        )
        
        self.status_bar.update_connection_status(
            internet=internet_status,
            database=database_status
        )

    def cleanup(self):
        if hasattr(self, 'camera_manager'):
            self.camera_manager.cleanup()
        self.report_manager.cleanup()
        if hasattr(self, 'connection_timer'):
            self.connection_timer.stop()
        
    def get_selected_capture_class(self):
        return self.detection_controls.get_selected_capture_class()
