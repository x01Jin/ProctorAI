from PyQt6.QtWidgets import QMainWindow, QMessageBox
import config.settings_manager as settings_manager
from backend.utils.thread_utils import ThreadPoolManager
from backend.services.application_state import ApplicationState
from .window_init import initialize_window
from .component_setup import setup_base_components, setup_model_components
from .signal_handler import (
    connect_signals,
    handle_detection_start,
    handle_detection_start_failure,
    handle_detection_stop,
    handle_detection_status_change,
    handle_camera_toggle,
)
from .detection_handler import (
    process_detections,
    handle_detection_toggle,
    get_selected_capture_class,
)
from .pdf_handler import generate_pdf
from .settings_handler import handle_settings_update, cleanup_resources

class MainWindow(QMainWindow):
    def __init__(self, user_id=None, proctor_name=None):
        super().__init__()
        self.user_id = user_id
        self.proctor_name = proctor_name
        self.app_state = ApplicationState.get_instance()
        settings_manager.load_settings()
        self.settings = settings_manager
        self.thread_pool_manager = ThreadPoolManager()

        if not setup_base_components(self):
            return
        if not setup_model_components(self):
            return
        initialize_window(self)
        connect_signals(self)

    def _on_detection_started(self):
        handle_detection_start(self)

    def _on_detection_start_failed(self, error_message):
        handle_detection_start_failure(self, error_message)

    def _on_detection_stopped(self):
        handle_detection_stop(self)

    def _on_detection_status_changed(self, status):
        handle_detection_status_change(self, status)

    def _toggle_camera(self):
        handle_camera_toggle(self)

    def _toggle_detection(self):
        handle_detection_toggle(self)

    def _process_detections(self, detections):
        process_detections(self, detections)

    def _generate_pdf(self):
        generate_pdf(self)

    def _on_settings_updated(self):
        handle_settings_update(self)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            cleanup_resources(self)
            event.accept()
        else:
            event.ignore()

    def get_selected_capture_class(self):
        return get_selected_capture_class(self)
