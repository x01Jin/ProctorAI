from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, QThreadPool

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.signals.error.emit((type(e), e, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class ThreadPoolManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadPoolManager, cls).__new__(cls)
            cls._instance.pool = QThreadPool()
            cls._instance.pool.setMaxThreadCount(QThreadPool.globalInstance().maxThreadCount())
        return cls._instance

    def run(self, fn, *args, **kwargs):
        worker = Worker(fn, *args, **kwargs)
        self.pool.start(worker)
        return worker.signals

    def cleanup(self):
        self.pool.waitForDone()
