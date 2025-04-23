from PyQt6.QtCore import QThread

class SimpleThread(QThread):
    def __init__(self, target, *args):
        super().__init__()
        self._target = target
        self._args = args
        self._running = True

    def run(self):
        self._target(*self._args)

    def stop(self):
        self._running = False

def start_qt_thread(target, *args):
    thread = SimpleThread(target, *args)
    thread.start()
    return thread
