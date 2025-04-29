from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThread
import logging
from frontend.components.loading_dialog import LoadingDialog

dlogger = logging.getLogger("detection")
clogger = logging.getLogger("camera")

def connect_signals(window):
    window.camera_manager.frame_ready.connect(window.camera_display.update_display)
    window.detection_manager.detections_ready.connect(window._process_detections)
    window.detection_manager.detection_stopped.connect(window._on_detection_stopped)
    window.detection_manager.detection_status_changed.connect(window._on_detection_status_changed)
    window.detection_manager.detection_started.connect(window._on_detection_started)
    window.detection_manager.detection_start_failed.connect(window._on_detection_start_failed)
    window.camera_manager.camera_start_failed.connect(lambda msg: handle_camera_start_failure(window, msg))
    window.camera_manager.camera_started.connect(lambda: handle_camera_started(window))
    window.camera_manager.camera_stopped.connect(lambda: handle_camera_stopped(window))
    window.camera_display.camera_toggle_requested.connect(window._toggle_camera)
    window.detection_controls.detection_toggle_requested.connect(window._toggle_detection)
    window.report_manager.pdf_generation_requested.connect(window._generate_pdf)
    window.detection_controls.confidence_changed.connect(
        window.detection_manager.update_confidence_threshold
    )

def handle_detection_start(window):
    dlogger.info("Detection successfully started from MainWindow.")

def handle_detection_start_failure(window, error_message):
    QMessageBox.warning(window, "Detection Error", f"Could not start detection: {error_message}")
    dlogger.error(f"Detection start failed: {error_message}")

def handle_detection_stop(window):
    window.camera_display.reset_display()
    window.status_bar.update_detections_count(0)
    dlogger.info("Detection stopped signal received in MainWindow.")

def handle_camera_started(window):
    window.camera_display.update_camera_button_text(True)
    window.detection_controls.set_detection_enabled(True)
    clogger.info("Camera started successfully")

def handle_camera_stopped(window):
    window.camera_display.update_camera_button_text(False)
    window.detection_controls.set_detection_enabled(False)
    clogger.info("Camera stopped")

def handle_camera_start_failure(window, error_message):
    QMessageBox.critical(window, "Camera Error", error_message)
    clogger.error(f"Camera start failed: {error_message}")
    window.detection_controls.set_detection_enabled(False)

def handle_detection_status_change(window, status):
    window.status_bar.set_detection_status(status)

def handle_camera_toggle(window):
    def toggle_task():
        if getattr(window.camera_manager, "camera_active", True):
            if getattr(window.detection_manager, "detection_active", False):
                window.detection_manager.toggle_detection(force_stop=True)
                while getattr(window.detection_manager, "detection_active", True):
                    QApplication.processEvents()
                    QThread.msleep(50)
        window.camera_manager.toggle_camera()
        camera_active = getattr(window.camera_manager, "camera_active", False)
        window.detection_controls.set_detection_enabled(camera_active)
    LoadingDialog.show_loading(window, "Toggling camera...", toggle_task, logger_name="camera")
