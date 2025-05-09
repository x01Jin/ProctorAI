from PyQt6.QtWidgets import QMessageBox
from backend.controllers.camera_controller import CameraManager
from backend.controllers.detection_controller import DetectionManager
from frontend.components.camera_display import CameraDisplayDock
from frontend.components.detection_controls import DetectionControlsDock
from frontend.components.report_manager import ReportManagerDock
from frontend.components.status_bar import StatusBarManager
from frontend.components.toolbar import ToolbarManager
from frontend.themes.theme_manager import ThemeManager

def setup_base_components(window, proctor_name=None, email=None):
    window.camera_display = CameraDisplayDock("Camera and Display", window)
    window.report_manager = ReportManagerDock("Captured Images", window)
    window.detection_controls = DetectionControlsDock("Detection Controls", window)
    window.status_bar = StatusBarManager(window, proctor_name, email)
    window.toolbar = ToolbarManager(window)
    window.theme_manager = ThemeManager(window)
    window.toolbar.settings_updated.connect(window._on_settings_updated)
    window.camera_manager = CameraManager(window)
    return check_camera_status(window)

def setup_model_components(window):
    rf = window.app_state.roboflow
    if rf is None or not rf.model or not rf.classes:
        handle_model_error(window, "Roboflow not properly initialized or missing model/classes.")
        return False
    
    if not hasattr(window, "detection_manager"):
        window.detection_manager = DetectionManager(rf.model, window)
    else:
        window.detection_manager.model = rf.model
    
    window.detection_controls.update_model_classes(rf.classes)
    return True

def handle_model_error(window, error_msg):
    QMessageBox.critical(window, "Setup Error", f"Failed to setup model and controls: {error_msg}")

def check_camera_status(window):
    if not hasattr(window, "camera_manager"):
        return False
    camera_active = getattr(window.camera_manager, "camera_active", False)
    if hasattr(window, "detection_controls"):
        window.detection_controls.set_detection_enabled(camera_active)
    return True
