from PyQt6.QtCore import QObject, pyqtSignal, QThread
from pygrabber.dshow_graph import FilterGraph
import cv2
import logging

logger = logging.getLogger('camera')

class CameraThread(QThread):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._is_running = True

    def run(self):
        logger.info("Starting camera capture thread")
        error_count = 0
        
        while self._is_running and self.manager.cap and self.manager.cap.isOpened():
            ret, frame = self.manager.cap.read()
            if ret:
                self.manager.current_image = frame
                self.manager.frame_ready.emit(frame)
                error_count = 0  # Reset error count on successful frame
            else:
                error_count += 1
                if error_count >= 5:  # Stop after 5 consecutive errors
                    logger.error("Too many consecutive frame read errors, stopping camera")
                    break
            self.msleep(16)
        
        logger.info("Camera capture thread stopped")

    def stop(self):
        logger.info("Stopping camera capture thread")
        self._is_running = False

class CameraManager(QObject):
    frame_ready = pyqtSignal(object)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.camera_active = False
        self.cap = None
        self.current_image = None
        self.camera_devices = self.list_cameras()
        self.selected_camera = self.camera_devices[0] if self.camera_devices else ''
        self.camera_thread = None

        self.main_window.camera_display.camera_combo.currentIndexChanged.connect(self.on_camera_selected)

    def _get_opencv_devices(self):
        # Fallback method using OpenCV
        devices = []
        for i in range(5):  # Check first 5 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                devices.append(f"Camera {i}")
                cap.release()
                logger.info(f"Found camera at index {i}")
        return devices

    def list_cameras(self):
        try:
            logger.debug("Attempting to list cameras using FilterGraph")
            graph = FilterGraph()
            devices = graph.get_input_devices()
            if not devices:
                logger.warning("No devices found using FilterGraph, falling back to OpenCV")
                devices = self._get_opencv_devices()
        except Exception as e:
            logger.error(f"Failed to initialize FilterGraph: {str(e)}")
            logger.info("Attempting fallback to OpenCV camera detection")
            devices = self._get_opencv_devices()
        
        if not devices:
            devices = ['No cameras found']
            logger.error("No cameras detected on the system")
        else:
            logger.info(f"Found {len(devices)} camera(s): {devices}")
        
        self.main_window.camera_display.populate_camera_list(devices)
        return devices

    def on_camera_selected(self, index):
        self.selected_camera = self.camera_devices[index]

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if self.camera_active:
            self.main_window.camera_display.update_camera_button_text(True)
            self.use_camera()
        else:
            self.main_window.camera_display.update_camera_button_text(False)
            self.stop_camera()

    def use_camera(self):
        try:
            if self.selected_camera == 'No cameras found':
                logger.error("Cannot start camera - no cameras available")
                return

            if self.selected_camera.startswith('Camera '):
                camera_index = int(self.selected_camera.split(' ')[1])
            else:
                camera_index = self.camera_devices.index(self.selected_camera)

            logger.info(f"Initializing camera: {self.selected_camera} (index: {camera_index})")
            self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                # Log camera properties
                width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                logger.info(f"Camera initialized - Resolution: {width}x{height}, FPS: {fps}")
                
                self.camera_thread = CameraThread(self)
                self.camera_thread.start()
                logger.info("Camera thread started successfully")
            else:
                logger.error(f"Failed to initialize camera {self.selected_camera} - Device not responding")
        except Exception as e:
            logger.error(f"Error initializing camera: {str(e)}")

    def _release_resources(self):
        logger.info("Releasing camera resources")
        self.camera_active = False
        
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread.wait()
            
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        try:
            if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'camera_display'):
                self.main_window.camera_display.display_label.clear()
                self.main_window.camera_display.display_label.setStyleSheet("background-color: black; border: 2px solid #444444;")
        except RuntimeError:
            pass

    def stop_camera(self):
        self._release_resources()

    def cleanup(self):
        logger.info("Cleaning up camera resources")
        self._release_resources()
