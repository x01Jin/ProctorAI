from PyQt6.QtCore import QObject, pyqtSignal
import logging
from backend.utils.thread_utils import ThreadPoolManager
from backend.utils.mp_utils import start_detection_process, clean_up_process
from backend.utils.deduplication_utils import DetectionDeduplicator
from multiprocessing import Queue, Event, Value
from ctypes import c_double
from queue import Empty
import time

DETECTION_SLEEP_MS = 33
logger = logging.getLogger("detection")

class DetectionManager(QObject):
    detections_ready = pyqtSignal(list)
    detection_stopped = pyqtSignal()
    connection_status_changed = pyqtSignal(bool)
    detection_status_changed = pyqtSignal(str)
    detection_started = pyqtSignal()
    detection_start_failed = pyqtSignal(str)

    def __init__(self, model, main_window):
        super().__init__()
        self.model = model
        self.detections = []
        self.main_window = main_window
        self.detection_active = False
        self.detection_process = None
        self.frame_queue = None
        self.result_queue = None
        self.stop_event = None
        self.confidence_value = Value(c_double, self.main_window.detection_controls.get_confidence_threshold())
        from multiprocessing import Value as MPValue
        self.connection_state = MPValue('i', 0)
        self.thread_pool_manager = ThreadPoolManager()
        self.update_worker_signals = None

    def _get_model_config(self):
        return {'model': self.model}

    def _start_detection_process_worker(self):
        try:
            self.frame_queue = self.main_window.camera_manager.frame_queue
            if not self.frame_queue:
                raise ValueError("Camera frame queue is not available.")
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
            logger.info("Detection process started successfully via worker.")
            return True
        except Exception as e:
            logger.error(f"Failed to start detection process in worker: {str(e)}")
            self.detection_process = None
            self.frame_queue = None
            self.result_queue = None
            self.stop_event = None
            return False

    def _on_detection_process_started(self, success):
        if success:
            self.detection_active = True
            self.main_window.detection_controls.update_detection_button_text(True)
            self.update_worker_signals = self.thread_pool_manager.run(self._result_update_loop)
            self.detection_started.emit()
            logger.info("Detection update loop started.")
        else:
            self.detection_active = False
            self.main_window.detection_controls.update_detection_button_text(False)
            self.detection_start_failed.emit("Failed to initialize detection process.")
            logger.error("Detection start failed, update loop not started.")

    def _on_detection_start_error(self, error_info):
        etype, evalue, tb = error_info
        logger.error(f"Error during detection process start: {etype.__name__}: {evalue}\n{tb}")
        self.detection_active = False
        self.main_window.detection_controls.update_detection_button_text(False)
        self.detection_start_failed.emit(f"Error starting detection: {evalue}")

    def toggle_detection(self, force_stop=False):
        if force_stop:
            if self.detection_active:
                self.stop_detection()
            self.main_window.detection_controls.update_detection_button_text(False)
            return

        should_start = not self.detection_active
        if should_start:
            logger.info("Attempting to start detection...")
            worker_signals = self.thread_pool_manager.run(self._start_detection_process_worker)
            worker_signals.result.connect(self._on_detection_process_started)
            worker_signals.error.connect(self._on_detection_start_error)
        else:
            logger.info("Attempting to stop detection...")
            self.stop_detection()
            self.main_window.detection_controls.update_detection_button_text(False)

    def stop_detection(self):
        logger.info("Stopping detection process...")
        if not self.detection_active:
            return

        self.detection_active = False
        if self.detection_process:
            import time
            time.sleep(0.1)
            
            clean_up_process(self.detection_process, self.stop_event)
            self.detection_process = None
            self.stop_event = None
            
            if self.result_queue:
                while not self.result_queue.empty():
                    try:
                        self.result_queue.get_nowait()
                    except Empty:
                        break
                self.result_queue = None

        self.frame_queue = None
        self.detections = []
        
        if hasattr(self, "detection_stopped"):
            self.detection_stopped.emit()
            
        logger.info("Detection process stopped.")

    def update_confidence_threshold(self, new_value):
        if hasattr(self, 'confidence_value') and self.confidence_value:
            self.confidence_value.value = new_value
            logger.debug(f"Confidence threshold updated to: {new_value}")

    def _result_update_loop(self):
        logger.info("Detection update thread starting")
        status_map = {0: "connected", 1: "disconnected", 2: "retrying"}
        last_status = None
        last_detection_time = time.time()
        detection_timeout = 2.5
        detections_cleared = False

        while self.detection_active:
            if not hasattr(self, "detections_ready") or not hasattr(self, "main_window") or not self.result_queue:
                time.sleep(0.1)
                continue

            status_val = self.connection_state.value if hasattr(self, "connection_state") else 1
            status_str = status_map.get(status_val, "disconnected")

            if status_str != last_status:
                if hasattr(self, "detection_status_changed"):
                    self.detection_status_changed.emit(status_str)
                last_status = status_str

            new_detection = False
            try:
                if not self.result_queue.empty():
                    predictions = self.result_queue.get_nowait()
                    capture_class = self.main_window.detection_controls.get_selected_capture_class()
                    self.detections = DetectionDeduplicator.deduplicate(predictions, capture_class)
                    self.detections_ready.emit(self.detections)
                    last_detection_time = time.time()
                    detections_cleared = False
                    new_detection = True
            except Empty:
                pass
            except Exception as e:
                 logger.error(f"Error processing detection results: {str(e)}")


            now = time.time()
            if not new_detection and status_str in ("retrying", "disconnected"):
                if now - last_detection_time > detection_timeout and not detections_cleared:
                    self.detections = []
                    self.detections_ready.emit([])
                    detections_cleared = True

            time.sleep(DETECTION_SLEEP_MS / 1000.0)

        logger.info("Detection update thread stopped")

    def cleanup(self):
        self.stop_detection()
        self.thread_pool_manager.cleanup()
        logger.info("DetectionManager cleaned up.")
