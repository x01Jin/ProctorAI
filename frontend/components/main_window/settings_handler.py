from frontend.components.loading_dialog import LoadingDialog
import logging

rlogger = logging.getLogger("report")
clogger = logging.getLogger("camera")
dlogger = logging.getLogger("detection")

def handle_settings_update(window):
    def do_update():
        camera_active = hasattr(window, "camera_manager") and window.camera_manager and getattr(window.camera_manager, "camera_active", False)
        if camera_active:
            if hasattr(window, "detection_manager") and getattr(window.detection_manager, "detection_active", False):
                window.detection_manager.toggle_detection(force_stop=True)
            window.camera_manager.stop_camera()

    LoadingDialog.show_loading(
        window,
        "Re-initializing settings...",
        do_update,
    )

def setup_model(window):
    from .component_setup import setup_model_components
    return setup_model_components(window)

def cleanup_resources(window):
    camera_active = hasattr(window, "camera_manager") and window.camera_manager and getattr(window.camera_manager, "camera_active", False)
    if camera_active:
        clogger.info("Stopping camera for cleanup...")
        if hasattr(window, "detection_manager") and getattr(window.detection_manager, "detection_active", False):
            dlogger.info("Stopping detection first...")
            window.detection_manager.toggle_detection(force_stop=True)
        window.camera_manager.stop_camera()
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
