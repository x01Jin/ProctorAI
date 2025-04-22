from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from config.config_bootstrap import ensure_config

def check_config(log_display, on_complete):
    log_display.log("Checking configuration and settings...")
    def do_check():
        if ensure_config(None, log_display):
            log_display.log("Configuration and settings valid", "success")
            QTimer.singleShot(100, lambda: on_complete(True))
        else:
            log_display.log("Setup cancelled... exiting the application...", "error")
            QTimer.singleShot(1000, lambda: QApplication.instance().quit())
    QTimer.singleShot(1000, do_check)
