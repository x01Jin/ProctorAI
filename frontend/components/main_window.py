from PyQt6.QtWidgets import QMainWindow, QSplitter, QMessageBox, QDockWidget
from PyQt6.QtCore import Qt
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
from backend.controllers.report_controller import save_pdf

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProctorAI Release v1.3.9r")
        screen = self.screen().availableGeometry()
        width = int(screen.width() * 0.9)
        height = int(screen.height() * 0.9)
        self.resize(width, height)
        self.move((screen.width() - width) // 2, (screen.height() - height) // 2)
        self.app_state = ApplicationState.get_instance()
        self.settings = SettingsManager()
        self.theme_manager = ThemeManager(self)
        self._setup_window()
        self._setup_components()
        self._setup_model()
        self._connect_signals()

    def _setup_window(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.camera_display = CameraDisplayDock("Camera and Display", self)
        self.camera_display.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.report_manager = ReportManagerDock("Captured Images", self)
        self.report_manager.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.detection_controls = DetectionControlsDock("Detection Controls", self)
        self.detection_controls.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        splitter.addWidget(self.camera_display)
        splitter.addWidget(self.report_manager)
        self.setCentralWidget(splitter)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.detection_controls)

    def _setup_components(self):
        self.status_bar = StatusBarManager(self)
        self.toolbar = ToolbarManager(self)
        self.toolbar.settings_updated.connect(self._on_settings_updated)

    def _setup_model(self):
        rf = self.app_state.roboflow
        if rf is None or not rf.model or not rf.classes:
            self._handle_model_error("Roboflow not properly initialized or missing model/classes.")
            return False
        if not hasattr(self, 'camera_manager'):
            self.camera_manager = CameraManager(self)
        if not hasattr(self, 'detection_manager'):
            self.detection_manager = DetectionManager(rf.model, self)
        else:
            self.detection_manager.model = rf.model
        self.detection_controls.update_model_classes(rf.classes)
        return True

    def _handle_model_error(self, error_msg):
        QMessageBox.critical(self, "Setup Error", f"Failed to setup model and controls: {error_msg}")

    def _connect_signals(self):
        self.camera_manager.frame_ready.connect(self.camera_display.update_display)
        self.detection_manager.detections_ready.connect(self._process_detections)
        self.detection_manager.detection_stopped.connect(self._on_detection_stopped)
        self.camera_display.camera_toggle_requested.connect(self._toggle_camera)
        self.detection_controls.detection_toggle_requested.connect(self._toggle_detection)
        self.report_manager.pdf_generation_requested.connect(self._generate_pdf)

    def _on_detection_stopped(self):
        self.camera_display.reset_display()
        self.status_bar.update_detections_count(0)

    def _toggle_camera(self):
        self.camera_manager.toggle_camera()

    def _toggle_detection(self):
        self.detection_manager.toggle_detection()

    def _generate_pdf(self):
        save_pdf()

    def _process_detections(self, detections):
        selected_class = self.get_selected_capture_class()
        if not selected_class:
            return
        self.status_bar.update_detections_count(len(detections))
        for detection in detections:
            if detection['class'] == selected_class:
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

    def _on_settings_updated(self):
        if hasattr(self, 'detection_manager') and self.detection_manager:
            self.detection_manager.toggle_detection(force_stop=True)
        if not self.app_state.reinitialize_roboflow():
            error_msg = self.app_state.roboflow.last_error or "Failed to initialize Roboflow model"
            QMessageBox.critical(self, "Error", f"Model update failed: {error_msg}")
            return
        if not self._setup_model():
            return
        QMessageBox.information(
            self,
            "Success",
            "Roboflow model successfully changed and is ready to use"
        )

    def cleanup(self):
        if hasattr(self, 'camera_manager'):
            self.camera_manager.cleanup()
        self.report_manager.cleanup()

    def get_selected_capture_class(self):
        return self.detection_controls.get_selected_capture_class()
