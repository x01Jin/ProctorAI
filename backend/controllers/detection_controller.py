from PyQt6.QtCore import QObject, pyqtSignal, QThread
import cv2
import requests
from backend.utils.gui_utils import GUIManager

class DetectionManager(QObject):
    detections_ready = pyqtSignal(list)
    connection_status_changed = pyqtSignal(bool)

    def __init__(self, model, main_window):
        super().__init__()
        self.detection_active = False
        self.model = model
        self.detections = []
        self.main_window = main_window
        self.detection_thread = None

    def toggle_detection(self):
        self.detection_active = not self.detection_active
        if self.detection_active:
            self.main_window.detection_controls.update_detection_button_text(True)
            self.detection_thread = QThread()
            self.detection_thread.run = self.process_camera_feed
            self.detection_thread.start()
        else:
            self.main_window.detection_controls.update_detection_button_text(False)
            self.stop_detection()

    def stop_detection(self):
        self.detection_active = False
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.terminate()
            self.detection_thread.wait()

    def process_camera_feed(self):
        while self.detection_active and self.main_window.camera_manager.cap and self.main_window.camera_manager.cap.isOpened():
            if self.main_window.camera_manager.current_image is not None:
                self.detections = self.process_image(self.main_window.camera_manager.current_image)
                self.detections_ready.emit(self.detections)
            QThread.msleep(1000)

    def process_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        confidence_threshold = self.main_window.detection_controls.get_confidence_threshold()
        
        if not GUIManager.connection():
            print("Connection Error. Retrying.")
            self.connection_status_changed.emit(False)
            QThread.sleep(3)
            return self.process_image(image)
        
        try:
            result = self.model.predict(image_rgb, confidence=confidence_threshold, overlap=30).json()
            self.connection_status_changed.emit(True)
            return result['predictions']
        except requests.exceptions.ConnectionError:
            print("Connection Error. Retrying.")
            self.connection_status_changed.emit(False)
            QThread.sleep(3)
            return self.process_image(image)
