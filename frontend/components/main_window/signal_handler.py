from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThread
import logging

logger = logging.getLogger("reports")

def connect_signals(window):
    window.camera_manager.frame_ready.connect(window.camera_display.update_display)
    window.detection_manager.detections_ready.connect(window._process_detections)
    window.detection_manager.detection_stopped.connect(window._on_detection_stopped)
    window.detection_manager.detection_status_changed.connect(window._on_detection_status_changed)
    window.detection_manager.detection_started.connect(window._on_detection_started)
    window.detection_manager.detection_start_failed.connect(window._on_detection_start_failed)
    window.camera_display.camera_toggle_requested.connect(window._toggle_camera)
    window.detection_controls.detection_toggle_requested.connect(window._toggle_detection)
    window.report_manager.pdf_generation_requested.connect(window._generate_pdf)
    window.detection_controls.confidence_changed.connect(
        window.detection_manager.update_confidence_threshold
    )

def handle_detection_start(window):
    logger.info("Detection successfully started from MainWindow.")

def handle_detection_start_failure(window, error_message):
    QMessageBox.warning(window, "Detection Error", f"Could not start detection: {error_message}")
    logger.error(f"Detection start failed: {error_message}")

def handle_detection_stop(window):
    window.camera_display.reset_display()
    window.status_bar.update_detections_count(0)
    logger.info("Detection stopped signal received in MainWindow.")

def handle_detection_status_change(window, status):
    window.status_bar.set_detection_status(status)

def handle_camera_toggle(window):
    if getattr(window.camera_manager, "camera_active", True):
        if getattr(window.detection_manager, "detection_active", False):
            window.detection_manager.toggle_detection(force_stop=True)
            while getattr(window.detection_manager, "detection_active", True):
                QApplication.processEvents()
                QThread.msleep(50)

    window.camera_manager.toggle_camera()
    camera_active = getattr(window.camera_manager, "camera_active", False)
    window.detection_controls.set_detection_enabled(camera_active)
