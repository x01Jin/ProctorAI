from PyQt6.QtCore import QThread, QObject

class BaseThread(QThread):
    def __init__(self):
        super().__init__()
        self._is_running = True

    def stop(self):
        self._is_running = False

class BaseManager(QObject):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.active = False

    def stop_thread(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()

    def cleanup(self):
        self.stop_thread()
