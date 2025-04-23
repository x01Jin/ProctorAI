from PyQt6.QtCore import QObject, pyqtSignal
import logging
from backend.utils.thread_utils import start_qt_thread
from backend.utils.mp_utils import start_detection_process, clean_up_process
from backend.utils.deduplication_utils import DetectionDeduplicator
from multiprocessing import Queue, Event, Value
from ctypes import c_double
from queue import Empty

DETECTION_SLEEP_MS = 33
logger = logging.getLogger("detection")

def result_update_loop(manager):
    import time
    logger.info("Detection update thread starting")
    status_map = {0: "connected", 1: "disconnected", 2: "retrying"}
    last_status = None
    last_detection_time = time.time()
    detection_timeout = 2.5
    detections_cleared = False
    while manager.detection_active:
        if not hasattr(manager, "detections_ready") or not hasattr(manager, "main_window"):
            return
        status_val = manager.connection_state.value if hasattr(manager, "connection_state") else 1
        status_str = status_map.get(status_val, "disconnected")
        if status_str != last_status:
            if hasattr(manager, "detection_status_changed"):
                manager.detection_status_changed.emit(status_str)
            last_status = status_str
        new_detection = False
        if not manager.result_queue.empty():
            try:
                predictions = manager.result_queue.get_nowait()
                capture_class = manager.main_window.detection_controls.get_selected_capture_class()
                manager.detections = DetectionDeduplicator.deduplicate(predictions, capture_class)
                manager.detections_ready.emit(manager.detections)
                last_detection_time = time.time()
                detections_cleared = False
                new_detection = True
            except Empty:
                pass
        now = time.time()
        if not new_detection and status_str in ("retrying", "disconnected"):
            if now - last_detection_time > detection_timeout and not detections_cleared:
                manager.detections = []
                manager.detections_ready.emit([])
                detections_cleared = True
        manager.thread.msleep(DETECTION_SLEEP_MS)
    logger.info("Detection update thread stopped")

class DetectionManager(QObject):
    detections_ready = pyqtSignal(list)
    detection_stopped = pyqtSignal()
    connection_status_changed = pyqtSignal(bool)
    detection_status_changed = pyqtSignal(str)

    def __init__(self, model, main_window):
        super().__init__()
        self.model = model
        self.detections = []
        self.main_window = main_window
        self.detection_active = False
        self.thread = None
        self.detection_process = None
        self.frame_queue = None
        self.result_queue = None
        self.stop_event = None
        self.confidence_value = Value(c_double, self.main_window.detection_controls.get_confidence_threshold())
        from multiprocessing import Value as MPValue
        self.connection_state = MPValue('i', 0)

    def _get_model_config(self):
        return {
            'model': self.model
        }

    def toggle_detection(self, force_stop=False):
        if force_stop:
            self.detection_active = False
            self.main_window.detection_controls.update_detection_button_text(False)
            self.stop_detection()
            return

        self.detection_active = not self.detection_active
        if self.detection_active:
            self.main_window.detection_controls.update_detection_button_text(True)
            self.frame_queue = self.main_window.camera_manager.frame_queue
            self.result_queue = Queue()
            self.stop_event = Event()
            self.confidence_value.value = self.main_window.detection_controls.get_confidence_threshold()
            self.detection_process = start_detection_process(
                self.frame_queue,
                self.result_queue,
                self.stop_event,
                self._get_model_config(),
                self.confidence_value,
                self.connection_state
            )
            self.detection_process.start()
            self.thread = start_qt_thread(result_update_loop, self)
            logger.info("Detection process started successfully")
        else:
            self.main_window.detection_controls.update_detection_button_text(False)
            self.stop_detection()

    def stop_detection(self):
        self.detection_active = False
        if self.detection_process:
            clean_up_process(self.detection_process, self.stop_event)
            self.detection_process = None
            self.stop_event = None
        if self.thread:
            self.thread.stop()
            self.thread.wait()
            self.thread = None
        self.frame_queue = None
        if self.result_queue:
            self.result_queue = None
        self.detections = []
        if hasattr(self, "detection_stopped"):
            self.detection_stopped.emit()

    def update_confidence_threshold(self, new_value):
        self.confidence_value.value = new_value
