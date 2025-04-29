from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QScrollArea, QWidget
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
    _instance = None

    def __init__(self, parent=None, logger_name="detection"):
        super().__init__(parent)
        self.logger = logging.getLogger(logger_name)
        self.root_logger = logging.getLogger()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setObjectName("LoadingDialog")
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self.apply_theme)
        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)
        self.tasks = {}
        self.apply_theme()
        self.logger.info("LoadingDialog initialized (multi-task)")
        self.root_logger.info("LoadingDialog initialized (multi-task)")

    @classmethod
    def instance(cls, parent=None, logger_name="detection"):
        if cls._instance is None or not cls._instance.isVisible():
            cls._instance = LoadingDialog(parent, logger_name)
        return cls._instance

    def apply_theme(self):
        palette = self.theme_manager.current_palette()
        self.setStyleSheet(
            f"background-color: {palette['background']};"
            f"color: {palette['text']};"
        )
        for task in self.tasks.values():
            task["label"].setStyleSheet(f"color: {palette['text']};")

    def add_task(self, message, task_fn, on_done=None, logger_name="detection", *args, **kwargs):
        logger = logging.getLogger(logger_name)
        root_logger = logging.getLogger()
        task_id = id(task_fn) + len(self.tasks)
        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        progress = QProgressBar(self)
        progress.setRange(0, 0)
        status_label = QLabel("Running...", self)
        status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        task_layout.addWidget(label)
        task_layout.addWidget(progress)
        task_layout.addWidget(status_label)
        self.scroll_layout.addWidget(task_widget)
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
            progress.setRange(0, 1)
            progress.setValue(1)
            status_label.setText("Done")
            logger.info("Task finished: %s", message)
            root_logger.info("Task finished: %s", message)
            if on_done:
                on_done()
            self._check_all_tasks_done()

        def on_thread_started():
            logger.debug("Worker thread started (id=%s)", int(thread.currentThreadId()))
            root_logger.debug("Worker thread started (id=%s)", int(thread.currentThreadId()))

        def on_worker_finished():
            logger.info("Worker finished successfully.")
            root_logger.info("Worker finished successfully.")

        def on_worker_error(e):
            logger.error("Worker error: %s", str(e))
            root_logger.error("Worker error: %s", str(e))
            status_label.setText("Error")
            progress.setRange(0, 1)
            progress.setValue(0)
            self._check_all_tasks_done()

        worker.finished.connect(cleanup)
        worker.error.connect(lambda e: (on_worker_error(e), cleanup()))
        thread.started.connect(on_thread_started)
        thread.started.connect(worker.run)
        thread.finished.connect(lambda: (logger.debug("Worker thread finished."), root_logger.debug("Worker thread finished.")))
        thread.start()
        logger.info("LoadingDialog task started: message='%s'", message)
        root_logger.info("LoadingDialog task started: message='%s'", message)
        self.tasks[task_id] = {
            "thread": thread,
            "worker": worker,
            "label": label,
            "progress": progress,
            "status_label": status_label,
            "widget": task_widget,
        }
        self.apply_theme()
        self.show()
        self.raise_()
        self.activateWindow()

    def _check_all_tasks_done(self):
        all_done = all(
            t["status_label"].text() in ("Done", "Error") for t in self.tasks.values()
        )
        if all_done:
            self.logger.info("All tasks finished. Dialog will close automatically.")
            self.root_logger.info("All tasks finished. Dialog will close automatically.")
            QTimer.singleShot(300, self.accept)

    @staticmethod
    def show_loading(parent, message, task_fn, on_done=None, logger_name="detection", *args, **kwargs):
        dialog = LoadingDialog.instance(parent, logger_name)
        dialog.add_task(message, task_fn, on_done, logger_name, *args, **kwargs)
        dialog.exec()