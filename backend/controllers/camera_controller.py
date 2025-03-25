from PyQt6.QtCore import QObject, pyqtSignal, QThread
from pygrabber.dshow_graph import FilterGraph
import cv2

class CameraThread(QThread):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._is_running = True

    def run(self):
        while self._is_running and self.manager.cap and self.manager.cap.isOpened():
            ret, frame = self.manager.cap.read()
            if ret:
                self.manager.current_image = frame
                self.manager.frame_ready.emit(frame)
            self.msleep(16)

    def stop(self):
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

    def list_cameras(self):
        graph = FilterGraph()
        devices = graph.get_input_devices()
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
        camera_index = self.camera_devices.index(self.selected_camera)
        self.cap = cv2.VideoCapture(camera_index)
        if self.cap.isOpened():
            self.camera_thread = CameraThread(self)
            self.camera_thread.start()
        else:
            print("Selected camera is not available.")

    def _release_resources(self):
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
        self._release_resources()
