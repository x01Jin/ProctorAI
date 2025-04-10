from PyQt6.QtCore import QObject, pyqtSignal, QThread
import cv2
import requests
import logging
from time import time

class DetectionThread(QThread):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._is_running = True
        self.logger = logging.getLogger('detection')

    def run(self):
        self.logger.info("Detection thread starting")
        try:
            while (self._is_running and 
                   self.manager.main_window.camera_manager.cap and 
                   self.manager.main_window.camera_manager.cap.isOpened()):
                if self.manager.main_window.camera_manager.current_image is not None:
                    self.manager.detections = self.manager.process_image(
                        self.manager.main_window.camera_manager.current_image
                    )
                    self.manager.detections_ready.emit(self.manager.detections)
                self.msleep(1000)
        except Exception as e:
            self.logger.error(f"Error in detection thread: {str(e)}")
        finally:
            self.logger.info("Detection thread ending")

    def stop(self):
        self.logger.debug("Stop requested for detection thread")
        self._is_running = False

class DetectionManager(QObject):
    detections_ready = pyqtSignal(list)
    detection_stopped = pyqtSignal()
    connection_status_changed = pyqtSignal(bool)

    def __init__(self, model, main_window):
        super().__init__()
        self.detection_active = False
        self.model = model
        self.detections = []
        self.main_window = main_window
        self.detection_thread = None
        self.logger = logging.getLogger('detection')
        self.logger.setLevel(logging.INFO)

    def toggle_detection(self, force_stop=False):
        try:
            if force_stop:
                self.logger.info("Force stopping detection")
                self.detection_active = False
                self.main_window.detection_controls.update_detection_button_text(False)
                self.stop_detection()
                return
                
            self.detection_active = not self.detection_active
            if self.detection_active:
                self.logger.info("Starting detection with current confidence threshold: " +
                               f"{int(self.main_window.detection_controls.get_confidence_threshold()*100)}%")
                self.main_window.detection_controls.update_detection_button_text(True)
                self.detection_thread = DetectionThread(self)
                self.detection_thread.start()
                self.logger.debug("Detection thread started successfully")
            else:
                self.logger.info("Stopping detection")
                self.main_window.detection_controls.update_detection_button_text(False)
                self.stop_detection()
        except Exception as e:
            self.logger.error(f"Error in toggle_detection: {str(e)}")
            self.main_window.detection_controls.update_detection_button_text(False)
            self.stop_detection()

    def stop_detection(self):
        try:
            self.detection_active = False
            if self.detection_thread and self.detection_thread.isRunning():
                self.logger.info("Stopping detection thread")
                self.detection_thread.stop()
                self.detection_thread.wait()
                self.logger.info("Detection thread stopped successfully")
            self.detections = []
            self.detection_stopped.emit()
        except Exception as e:
            self.logger.error(f"Error in stop_detection: {str(e)}")

    def process_image(self, image):
        start_time = time()
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            confidence_threshold = self.main_window.detection_controls.get_confidence_threshold()
            try:
                self.logger.debug("Sending prediction request to model")
                result = self.model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()
                predictions = result['predictions']
                
                if predictions:
                    pred_log = ", ".join([f"{p['class']}({int(p['confidence']*100)}%)" for p in predictions])
                    self.logger.info(f"Frame processed: {len(predictions)} detections - {pred_log}")
                else:
                    self.logger.debug("No detections in this frame")
                
                process_time = int((time() - start_time) * 1000)
                self.logger.debug(f"Processing time: {process_time}ms")
                
                self.connection_status_changed.emit(True)
                return predictions
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Network error during prediction: {str(e)}")
                if isinstance(e, requests.exceptions.HTTPError):
                    if "401" in str(e):
                        self.logger.error("Authentication error - please check API key")
                    elif "404" in str(e):
                        self.logger.error("Project or model version not found")
                    self.stop_detection()
                elif isinstance(e, requests.exceptions.ConnectionError):
                    self.logger.error("Connection error - check internet connection")
                    self.connection_status_changed.emit(False)
                return []
            except Exception as e:
                self.logger.error(f"Unexpected error during prediction: {str(e)}")
                self.stop_detection()
                return []
        except Exception as e:
            self.logger.error(f"Failed to process image: {str(e)}")
            return []
