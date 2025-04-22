from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from backend.services.application_state import ApplicationState
from config import settings_manager
from config.settings_dialog import SettingsDialog

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
                log_display.log("Retry failed, check settings again.", "info")
                log_display.log("Opening setup to check the database settings...", "warning")
                dialog = SettingsDialog(parent=parent, setup_mode=True, setup_type="database")
                if dialog.exec() == dialog.DialogCode.Accepted:
                    QTimer.singleShot(100, lambda: check_database(log_display, on_complete, retry_count, attempt + 1, parent))
                else:
                    log_display.log("Database setup cancelled... exiting the application...", "error")
                    app_state.update_connection_status(database=False)
                    QTimer.singleShot(1000, lambda: QApplication.instance().quit())
    QTimer.singleShot(1000, try_db)
