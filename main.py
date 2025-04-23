import sys
import multiprocessing
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from frontend.components.main_window import MainWindow
from frontend.components.splash_screen import SplashScreen
from backend.utils.log_config import setup_logging

def initialize_directories():
    directories = [
        "tempcaptures"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def start_main_window(splash, app):
    window = MainWindow()
    window.show()
    splash.close()

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    import logging
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
        lambda _: QTimer.singleShot(1000, lambda: start_main_window(splash, app))
    ))
    
    sys.exit(app.exec())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
