from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from config.config_bootstrap import ensure_config

def check_config(log_display, on_complete):
    log_display.log("Checking configuration and settings...")
    retry_attempted = False

    def show_error_and_exit():
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.setText("An error occurred when checking the configuration, please contact the admin to troubleshoot the problem")
        error_dialog.setWindowTitle("Configuration Error")
        error_dialog.exec()
        QApplication.instance().quit()

    def do_check():
        nonlocal retry_attempted
        config_result = ensure_config(None, log_display)
        
        if config_result:
            log_display.log("Configuration and settings valid", "success")
            QTimer.singleShot(100, lambda: on_complete(True))
            return

        if not retry_attempted:
            retry_attempted = True
            log_display.log("Retrying configuration check...", "warning")
            QTimer.singleShot(1000, do_check)
            return

        log_display.log("Configuration check failed after retry", "error")
        QTimer.singleShot(100, show_error_and_exit)

    QTimer.singleShot(1000, do_check)
