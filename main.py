import sys
import multiprocessing
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import QTimer
from frontend.components.main_window import MainWindow
from frontend.components.splash_screen import SplashScreen
from backend.utils.log_config import setup_logging
from authentication.login_window import LoginWindow
from authentication.session_manager import SessionManager
import backend.services.database_service as db_service
import logging

def initialize_directories():
    directories = [
        "tempcaptures"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def start_login_window(splash, app):
    session_manager = SessionManager()
    login = LoginWindow(db_service, session_manager)
    result = login.exec()
    if result == QDialog.DialogCode.Accepted:
        user_id = login.get_user_id()
        proctor_name = login.get_proctor_name()
        start_main_window(splash, app, user_id, proctor_name)
    else:
        splash.close()
        app.quit()

def start_main_window(splash, app, user_id, proctor_name):
    window = MainWindow(user_id=user_id, proctor_name=proctor_name)
    window.show()
    splash.close()

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    logging.getLogger().error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def main():
    setup_logging()
    sys.excepthook = log_uncaught_exceptions
    initialize_directories()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    splash = SplashScreen()
    splash.show()

    QTimer.singleShot(1000, lambda: splash.perform_checks(
        lambda _: QTimer.singleShot(1000, lambda: start_login_window(splash, app))
    ))

    sys.exit(app.exec())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
