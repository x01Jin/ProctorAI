from PyQt6.QtCore import QThread, QObject

class BaseThread(QThread):
    def __init__(self):
        super().__init__()
        self._is_running = True

    def run(self):
        while self._is_running:
            self.msleep(10)

    def stop(self):
        self._is_running = False

class BaseManager(QObject):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.active = False

    def start_thread(self, thread_cls, *args, **kwargs):
        if self.thread and self.thread.isRunning():
            self.stop_thread()
        self.thread = thread_cls(*args, **kwargs)
        self.thread.start()
        self.active = True

    def stop_thread(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.active = False

    def cleanup(self):
        self.stop_thread()
