from PyQt6.QtCore import pyqtSignal
import cv2
import requests
import logging
from backend.utils.thread_utils import BaseThread, BaseManager

DETECTION_SLEEP_MS = 1000
logger = logging.getLogger('detection')

class DetectionThread(BaseThread):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def run(self):
        logger.info("Detection thread starting")
        while self._is_running and self.manager.main_window.camera_manager.cap and self.manager.main_window.camera_manager.cap.isOpened():
            if self.manager.main_window.camera_manager.current_image is not None:
                self.manager.detections = self.manager.process_image(
                    self.manager.main_window.camera_manager.current_image
                )
                self.manager.detections_ready.emit(self.manager.detections)
            self.msleep(DETECTION_SLEEP_MS)
        logger.info("Detection thread ending")

class DetectionManager(BaseManager):
    detections_ready = pyqtSignal(list)
    detection_stopped = pyqtSignal()
    connection_status_changed = pyqtSignal(bool)

    def __init__(self, model, main_window):
        super().__init__()
        self.model = model
        self.detections = []
        self.main_window = main_window

    def toggle_detection(self, force_stop=False):
        if force_stop:
            self.detection_active = False
            self.main_window.detection_controls.update_detection_button_text(False)
            self.stop_detection()
            return
        self.detection_active = not getattr(self, "detection_active", False)
        if self.detection_active:
            self.main_window.detection_controls.update_detection_button_text(True)
            self.start_thread(DetectionThread, self)
        else:
            self.main_window.detection_controls.update_detection_button_text(False)
            self.stop_detection()

    def stop_detection(self):
        self.detection_active = False
        self.stop_thread()
        self.detections = []
        self.detection_stopped.emit()

    def process_image(self, image):
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            confidence_threshold = self.main_window.detection_controls.get_confidence_threshold()
            try:
                result = self.model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()
                predictions = result['predictions']
                self.connection_status_changed.emit(True)
                return predictions
            except requests.exceptions.RequestException as e:
                if isinstance(e, requests.exceptions.HTTPError):
                    if "401" in str(e):
                        logger.error("Authentication error - please check API key")
                    elif "404" in str(e):
                        logger.error("Project or model version not found")
                    self.stop_detection()
                elif isinstance(e, requests.exceptions.ConnectionError):
                    logger.error("Connection error - check internet connection")
                    self.connection_status_changed.emit(False)
                return []
            except Exception as e:
                logger.error(f"Unexpected error during prediction: {str(e)}")
                self.stop_detection()
                return []
        except Exception as e:
            logger.error(f"Failed to process image: {str(e)}")
            return []
