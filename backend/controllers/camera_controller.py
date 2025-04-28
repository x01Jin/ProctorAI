from PyQt6.QtCore import QObject, pyqtSignal
from pygrabber.dshow_graph import FilterGraph
import cv2
import logging
from backend.utils.thread_utils import ThreadPoolManager
from backend.utils.mp_utils import start_camera_process, clean_up_process
from multiprocessing import Queue, Event
from queue import Empty
from config.settings_manager import get_setting
 
CAMERA_SLEEP_MS = 16
logger = logging.getLogger("camera")

CAMERA_BACKEND_MAP = {
    "auto": None,
    "dshow": cv2.CAP_DSHOW,
    "msmf": cv2.CAP_MSMF
}
 
def frame_update_loop(manager):
    import time
    frame_interval = 1.0 / 60.0
    last_frame_time = 0
    logger.info("Frame update thread starting")
     
    while manager.camera_active:
        current_time = time.time()
        time_since_last = current_time - last_frame_time
         
        if time_since_last < frame_interval:
            time.sleep(max(0.001, frame_interval - time_since_last))
            continue
             
        try:
            frame = manager.frame_queue.get(timeout=0.1)
            manager.current_image = frame
            manager.frame_ready.emit(frame)
            last_frame_time = time.time()
        except Empty:
            time.sleep(0.01)
             
    logger.info("Frame update thread stopped")
 
class CameraManager(QObject):
    frame_ready = pyqtSignal(object)
    camera_start_failed = pyqtSignal(str)
 
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_image = None
        self.camera_devices = self.list_cameras()
        self.selected_camera = self.camera_devices[0] if self.camera_devices else ""
        self.main_window.camera_display.camera_combo.currentIndexChanged.connect(self.on_camera_selected)
        self.camera_active = False
        self.thread_pool_manager = ThreadPoolManager()
        self.camera_process = None
        self.frame_queue = None
        self.stop_event = None
        self.camera_backend = self._get_camera_backend()

    def _get_camera_backend(self):
        backend = get_setting("camera", "backend")
        if backend not in CAMERA_BACKEND_MAP:
            backend = "auto"
        return backend

    def _get_opencv_devices(self):
        devices = []
        backend = self._get_camera_backend()
        backend_flag = CAMERA_BACKEND_MAP[backend]
        for i in range(5):
            if backend_flag is not None:
                cap = cv2.VideoCapture(i, backend_flag)
            else:
                cap = cv2.VideoCapture(i)
            if cap.isOpened():
                devices.append(f"Camera {i}")
                cap.release()
                logger.info(f"Found camera at index {i} with backend {backend}")
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
            devices = ["No cameras found"]
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

    def _verify_camera_started(self):
        import time
        start_time = time.time()
        timeout = 5.0
        
        while time.time() - start_time < timeout:
            if not self.camera_process.is_alive():
                return False
            try:
                frame = self.frame_queue.get(timeout=0.1)
                if frame is not None:
                    self.frame_queue.put(frame)
                    return True
            except Empty:
                time.sleep(0.1)
        return False
        
    def use_camera(self):
        try:
            if self.selected_camera == "No cameras found":
                logger.error("Cannot start camera - no cameras available")
                return
            if self.selected_camera.startswith("Camera "):
                camera_index = int(self.selected_camera.split(" ")[1])
            else:
                camera_index = self.camera_devices.index(self.selected_camera)
            backend = self._get_camera_backend()
            logger.info(f"Initializing camera: {self.selected_camera} (index: {camera_index}) with backend {backend}")
            optimal_queue_size = 10
            self.frame_queue = Queue(maxsize=optimal_queue_size)
            self.stop_event = Event()
            self.camera_process = start_camera_process(self.frame_queue, self.stop_event, camera_index, backend)
            self.camera_process.start()
            if not self._verify_camera_started():
                self._release_resources()
                logger.error("Failed to start camera process")
                self.camera_start_failed.emit("Failed to start camera process. Please check your camera connection and try again.")
                return
            self.thread_pool_manager.run(frame_update_loop, self)
            logger.info("Camera process started successfully")
        except Exception as e:
            logger.error(f"Error initializing camera: {str(e)}")
            self._release_resources()

    def _release_resources(self):
        logger.info("Releasing camera resources")
        self.camera_active = False
        
        import time
        time.sleep(0.1)
        
        if self.camera_process:
            clean_up_process(self.camera_process, self.stop_event)
            if self.frame_queue:
                while not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except Exception:
                        break
            self.camera_process = None
            self.stop_event = None
            self.frame_queue = None
        
        if hasattr(self, 'thread_pool_manager'):
            self.thread_pool_manager.cleanup()
        
        try:
            if hasattr(self, "main_window") and self.main_window and hasattr(self.main_window, "camera_display"):
                self.main_window.camera_display.display_label.clear()
                self.main_window.camera_display.display_label.setStyleSheet("background-color: black; border: 2px solid #444444;")
        except RuntimeError:
            pass

    def stop_camera(self):
        self._release_resources()

    def cleanup(self):
        logger.info("Cleaning up camera resources")
        self._release_resources()
