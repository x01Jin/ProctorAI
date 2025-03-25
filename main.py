import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from frontend.components.main_window import MainWindow
from frontend.components.splash_screen import SplashScreen

def ensure_directories():
    directories = [
        "tempcaptures",
        Path(os.path.expanduser("~")) / ".proctorai" / "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def handle_checks_complete(splash, app, config_ok, internet_ok, roboflow_ok, database_ok):
    if not config_ok or not roboflow_ok or not database_ok:
        app.quit()
        return
    
    QTimer.singleShot(1000, lambda: start_main_window(splash, app))

def start_main_window(splash, app):
    window = MainWindow()
    window.show()
    splash.close()

def main():
    ensure_directories()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    splash = SplashScreen()
    splash.show()
    
    # Start checks after a delay to show splash screen
    QTimer.singleShot(1000, lambda: splash.perform_checks(
        lambda c, i, r, d: handle_checks_complete(splash, app, c, i, r, d)
    ))
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
