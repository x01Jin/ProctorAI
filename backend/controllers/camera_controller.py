from PyQt6.QtCore import QObject, pyqtSignal, QThread
from pygrabber.dshow_graph import FilterGraph
import cv2

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

        self.main_window.cameraCombo.currentIndexChanged.connect(self.on_camera_selected)

    def list_cameras(self):
        graph = FilterGraph()
        devices = graph.get_input_devices()
        self.main_window.cameraCombo.addItems(devices)
        return devices

    def on_camera_selected(self, index):
        self.selected_camera = self.camera_devices[index]

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if self.camera_active:
            self.main_window.startCameraButton.setText("Stop Camera")
            self.use_camera()
        else:
            self.main_window.startCameraButton.setText("Start Camera")
            self.stop_camera()

    def use_camera(self):
        camera_index = self.camera_devices.index(self.selected_camera)
        self.cap = cv2.VideoCapture(camera_index)
        if self.cap.isOpened():
            self.camera_thread = QThread()
            self.camera_thread.run = self.update_camera
            self.camera_thread.start()
        else:
            print("Selected camera is not available.")

    def stop_camera(self):
        self.camera_active = False
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.quit()
            self.camera_thread.wait()
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.clear_display()

    def update_camera(self):
        while self.camera_active and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_image = frame
                self.frame_ready.emit(frame)
            QThread.msleep(16)

    def clear_display(self):
        self.main_window.displayLabel.clear()
        self.main_window.displayLabel.setStyleSheet("background-color: black; border: 2px solid #444444;")

    def __del__(self):
        self.stop_camera()
