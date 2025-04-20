from PyQt6.QtCore import QThread, pyqtSignal
import cv2
import requests
import logging
from backend.utils.thread_utils import start_qthread, stop_qthread
from backend.utils.deduplication_utils import deduplicate

DETECTION_SLEEP_MS = 1000
logger = logging.getLogger('detection')

class DetectionWorker(QThread):
    detections_ready = pyqtSignal(list)
    detection_stopped = pyqtSignal()
    connection_status_changed = pyqtSignal(bool)

    def __init__(self, model, main_window):
        super().__init__()
        self.model = model
        self.main_window = main_window
        self._is_running = True

    def run(self):
        logger.info("Detection thread starting")
        while self._is_running and self.main_window.camera_manager.cap and self.main_window.camera_manager.cap.isOpened():
            if self.main_window.camera_manager.current_image is not None:
                detections = process_image(
                    self.model,
                    self.main_window,
                    self.main_window.camera_manager.current_image,
                    self.connection_status_changed,
                    self.detection_stopped
                )
                self.detections_ready.emit(detections)
            self.msleep(DETECTION_SLEEP_MS)
        logger.info("Detection thread ending")

    def stop(self):
        self._is_running = False

def process_image(model, main_window, image, connection_status_changed=None, detection_stopped=None):
    try:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        confidence_threshold = main_window.detection_controls.get_confidence_threshold()
        try:
            result = model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()
            predictions = result['predictions']
            if connection_status_changed:
                connection_status_changed.emit(True)
            capture_class = main_window.detection_controls.get_selected_capture_class()
            return deduplicate(predictions, capture_class)
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                if "401" in str(e):
                    logger.error("Authentication error - please check API key")
                elif "404" in str(e):
                    logger.error("Project or model version not found")
                if detection_stopped:
                    detection_stopped.emit()
            elif isinstance(e, requests.exceptions.ConnectionError):
                logger.error("Connection error - check internet connection")
                if connection_status_changed:
                    connection_status_changed.emit(False)
            return []
        except Exception as e:
            logger.error(f"Unexpected error during prediction: {str(e)}")
            if detection_stopped:
                detection_stopped.emit()
            return []
    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}")
        return []

def toggle_detection(worker, main_window, force_stop=False):
    if force_stop:
        main_window.detection_controls.update_detection_button_text(False)
        stop_qthread(worker)
        return
    if not worker.isRunning():
        main_window.detection_controls.update_detection_button_text(True)
        start_qthread(worker)
    else:
        main_window.detection_controls.update_detection_button_text(False)
        stop_qthread(worker)
