from PyQt6.QtWidgets import QMessageBox
import logging

logger = logging.getLogger("reports")

def handle_settings_update(window):
    if hasattr(window, "detection_manager") and window.detection_manager:
        window.detection_manager.toggle_detection(force_stop=True)
    
    if not window.app_state.reinitialize_roboflow():
        error_msg = window.app_state.roboflow.last_error or "Failed to initialize Roboflow model"
        QMessageBox.critical(window, "Error", f"Model update failed: {error_msg}")
        return False

    if not setup_model(window):
        return False

    QMessageBox.information(
        window,
        "Success",
        "Roboflow model successfully changed and is ready to use"
    )
    return True

def setup_model(window):
    from .component_setup import setup_model_components
    return setup_model_components(window)

def cleanup_resources(window):
    logger.info("Starting MainWindow cleanup...")
    
    if hasattr(window, "detection_manager") and window.detection_manager:
        logger.info("Cleaning up DetectionManager...")
        window.detection_manager.cleanup()
    
    if hasattr(window, "camera_manager") and window.camera_manager:
        if getattr(window.camera_manager, "camera_active", False):
            logger.info("Stopping camera...")
            window.camera_manager.toggle_camera()
        logger.info("Cleaning up CameraManager...")
        window.camera_manager.cleanup()
    
    if hasattr(window, "report_manager"):
        logger.info("Cleaning up ReportManager...")
        window.report_manager.cleanup()
    
    if hasattr(window, "thread_pool_manager"):
        logger.info("Cleaning up ThreadPoolManager...")
        window.thread_pool_manager.cleanup()
    
    logger.info("MainWindow cleanup finished.")
