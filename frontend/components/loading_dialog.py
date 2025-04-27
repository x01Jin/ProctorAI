from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
from frontend.themes.theme_manager import ThemeManager
import logging

class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(Exception)

    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.task(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            self.error.emit(e)

class LoadingDialog(QDialog):
    def __init__(self, parent, message, logger_name="detection"):
        super().__init__(parent)
        self.logger = logging.getLogger(logger_name)
        self.root_logger = logging.getLogger()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setObjectName("LoadingDialog")
        self.layout = QVBoxLayout(self)
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress)
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self.apply_theme)
        self.apply_theme()
        self.logger.info("LoadingDialog initialized with message: '%s'", message)
        self.root_logger.info("LoadingDialog initialized with message: '%s'", message)

    def apply_theme(self):
        palette = self.theme_manager.current_palette()
        self.setStyleSheet(
            f"background-color: {palette['background']};"
            f"color: {palette['text']};"
        )
        self.label.setStyleSheet(
            f"color: {palette['text']};"
        )

    @staticmethod
    def show_loading(parent, message, task_fn, on_done=None, logger_name="detection", *args, **kwargs):
        logger = logging.getLogger(logger_name)
        root_logger = logging.getLogger()
        dialog = LoadingDialog(parent, message, logger_name)
        thread = QThread()
        worker = Worker(task_fn, *args, **kwargs)
        worker.moveToThread(thread)

        def cleanup():
            logger.debug("Cleanup started. Thread is running: %s", thread.isRunning())
            root_logger.debug("Cleanup started. Thread is running: %s", thread.isRunning())
            thread.quit()
            QTimer.singleShot(0, lambda: finalize())

        def finalize():
            if thread.isRunning():
                logger.debug("Waiting for thread to finish...")
                root_logger.debug("Waiting for thread to finish...")
                thread.wait()
            dialog.accept()
            logger.info("LoadingDialog closed.")
            root_logger.info("LoadingDialog closed.")
            if on_done:
                on_done()

        def on_thread_started():
            logger.debug("Worker thread started (id=%s)", int(thread.currentThreadId()))
            root_logger.debug("Worker thread started (id=%s)", int(thread.currentThreadId()))

        def on_worker_finished():
            logger.info("Worker finished successfully.")
            root_logger.info("Worker finished successfully.")

        def on_worker_error(e):
            logger.error("Worker error: %s", str(e))
            root_logger.error("Worker error: %s", str(e))

        worker.finished.connect(cleanup)
        worker.error.connect(lambda e: (on_worker_error(e), cleanup()))
        thread.started.connect(on_thread_started)
        thread.started.connect(worker.run)
        thread.finished.connect(lambda: (logger.debug("Worker thread finished."), root_logger.debug("Worker thread finished.")))
        thread.start()
        logger.info("LoadingDialog shown: message='%s'", message)
        root_logger.info("LoadingDialog shown: message='%s'", message)
        dialog.exec()