import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from frontend.components.main_window import MainWindow
from frontend.components.splash_screen import SplashScreen
from config.settings_dialog import SettingsDialog
from config.settings_manager import SettingsManager

def ensure_directories():
    directories = [
        "tempcaptures",
        Path(os.path.expanduser("~")) / ".proctorai" / "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def handle_checks_complete(splash, app, config_ok, internet_ok, roboflow_ok, database_ok):
    if not config_ok:
        settings_dialog = SettingsDialog(SettingsManager())
        if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
            app.quit()
            return
    
    if not internet_ok:
        splash.log_message("Warning: Some features may be limited without internet connection", "warning")
    
    if not roboflow_ok:
        splash.log_message("Warning: Detection features will not work without Roboflow connection", "warning")
    
    if not database_ok:
        settings_dialog = SettingsDialog(SettingsManager())
        if settings_dialog.exec() != SettingsDialog.DialogCode.Accepted:
            app.quit()
            return
            
        # Retry database connection one last time
        if not splash.check_database():
            QMessageBox.critical(None, "Error", "Failed to set up database connection... exiting...")
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
