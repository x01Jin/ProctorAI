from PyQt6.QtWidgets import QMessageBox
from backend.utils.log_config import setup_logging
from frontend.components.loading_dialog import LoadingDialog
import logging

setup_logging()
rlogger = logging.getLogger("report")
clogger = logging.getLogger("camera")
dlogger = logging.getLogger("detection")

def handle_settings_update(window):
    def do_update():
        if hasattr(window, "detection_manager") and window.detection_manager:
            window.detection_manager.toggle_detection(force_stop=True)
        roboflow_ok = window.app_state.reinitialize_roboflow()
        window._settings_update_result = {"roboflow_ok": roboflow_ok}
        if roboflow_ok:
            model_ok = setup_model(window)
            window._settings_update_result["model_ok"] = model_ok
        else:
            window._settings_update_result["model_ok"] = False

    def on_done():
        result = getattr(window, "_settings_update_result", None)
        if not result or not result.get("roboflow_ok"):
            error_msg = window.app_state.roboflow.last_error or "Failed to initialize Roboflow model"
            QMessageBox.critical(window, "Error", f"Model update failed: {error_msg}")
            return
        if not result.get("model_ok"):
            QMessageBox.critical(window, "Error", "Failed to set up model components.")
            return
        QMessageBox.information(
            window,
            "Success",
            "Roboflow model successfully changed and is ready to use"
        )

    LoadingDialog.show_loading(
        window,
        "Re-initializing settings...",
        do_update,
        on_done=on_done,
        logger_name="roboflow"
    )

def setup_model(window):
    from .component_setup import setup_model_components
    return setup_model_components(window)

def cleanup_resources(window):
    camera_active = hasattr(window, "camera_manager") and window.camera_manager and getattr(window.camera_manager, "camera_active", False)
    if camera_active and hasattr(window, "_toggle_camera"):
        clogger.info("Simulating camera button toggle for cleanup...")
        window._toggle_camera()
    else:
        if hasattr(window, "detection_manager") and window.detection_manager:
            dlogger.info("Cleaning up DetectionManager...")
            window.detection_manager.cleanup()
        if hasattr(window, "camera_manager") and window.camera_manager:
            clogger.info("Cleaning up CameraManager...")
            window.camera_manager.cleanup()

    if hasattr(window, "report_manager"):
        rlogger.info("Cleaning up ReportManager...")
        window.report_manager.cleanup()

    if hasattr(window, "thread_pool_manager"):
        window.thread_pool_manager.cleanup()
