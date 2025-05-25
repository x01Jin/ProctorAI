from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from backend.services.application_state import ApplicationState
from config import settings_manager

def check_database(log_display, on_complete, retry_count=3, attempt=0, parent=None):
    app_state = ApplicationState.get_instance()
    app_state.initialize_database(settings_manager)
    log_display.log("Checking database connection...")
    def try_db():
        if app_state.db_connected:
            log_display.log("Database connection established", "success")
            app_state.update_connection_status(database=True)
            QTimer.singleShot(100, lambda: on_complete(True))
        else:
            if attempt < retry_count - 1:
                log_display.log(f"Database connection failed: Connection failed, retrying... ({attempt + 1}/{retry_count})", "warning")
                QTimer.singleShot(1000, lambda: check_database(log_display, on_complete, retry_count, attempt + 1, parent))
            else:
                message_box = QMessageBox(parent)
                message_box.setIcon(QMessageBox.Icon.Warning)
                message_box.setWindowTitle("Database Connection Failed")
                message_box.setText("The connection to the database failed. Please contact the admin for information.\n\nWithout database access, the application will not work as intended.")
                message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                message_box.exec()
                
                log_display.log("Exiting the application...", "error")
                app_state.update_connection_status(database=False)
                QTimer.singleShot(1000, lambda: QApplication.instance().quit())
    QTimer.singleShot(1000, try_db)
