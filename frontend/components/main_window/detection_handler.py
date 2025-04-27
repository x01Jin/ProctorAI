from backend.utils.log_config import setup_logging
import logging
from backend.utils.gui.image_capture_manager import ImageCaptureManager
from frontend.components.loading_dialog import LoadingDialog

setup_logging()
logger = logging.getLogger("detection")

def process_detections(window, detections):
    selected_class = window.get_selected_capture_class()
    if not selected_class:
        window.camera_display.update_display(clear_markers=True)
        return

    window.status_bar.update_detections_count(len(detections))
    if not detections:
        window.camera_display.update_display(clear_markers=True)
        return

    current_image = window.camera_manager.current_image
    if current_image is None:
        logger.warning("Cannot capture image, current_image is None.")
        return

    for detection in detections:
        if detection["class"] == selected_class:
            ImageCaptureManager.capture_image(detection, current_image, window)

def handle_detection_toggle(window):
    def toggle_task():
        window.detection_manager.toggle_detection()
    LoadingDialog.show_loading(window, "Toggling detection...", toggle_task)

def get_selected_capture_class(window):
    return window.detection_controls.get_selected_capture_class()
