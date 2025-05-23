from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from backend.services.application_state import ApplicationState

def check_roboflow(log_display, on_complete, retry_count=3, attempt=0, parent=None):
    app_state = ApplicationState.get_instance()
    app_state.initialize_roboflow()
    rf = app_state.roboflow
    log_display.log("Checking Roboflow connection...")
    def try_roboflow():
        if rf.initialize(splash_screen=log_display):
            log_display.log("Roboflow connection established", "success")
            app_state.update_connection_status(roboflow=True)
            QTimer.singleShot(100, lambda: on_complete(True))
        else:
            if attempt < retry_count - 1:
                log_display.log(f"Roboflow connection failed: {rf.last_error or 'Connection test failed'}, retrying... ({attempt + 1}/{retry_count})", "warning")
                QTimer.singleShot(1000, lambda: check_roboflow(log_display, on_complete, retry_count, attempt + 1, parent))
            else:
                message_box = QMessageBox(parent)
                message_box.setIcon(QMessageBox.Icon.Warning)
                message_box.setWindowTitle("Connection Failed")
                message_box.setText("The connection to the model API failed. Please contact the admin for information.\n\nWithout the AI model, the application will not work as intended.")
                message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                message_box.exec()
                
                log_display.log("Exiting the application...", "error")
                app_state.update_connection_status(roboflow=False)
                QTimer.singleShot(1000, lambda: QApplication.instance().quit())
    QTimer.singleShot(1000, try_roboflow)
