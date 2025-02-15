import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMessageBox
from frontend.components.main_window import MainWindow
from config.settings_manager import SettingsManager

def ensure_directories():
    directories = [
        "tempcaptures",
        Path(os.path.expanduser("~")) / ".proctorai" / "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def init_settings():
    try:
        settings = SettingsManager()
        settings.validate_settings()
        return True
    except ValueError as e:
        QMessageBox.critical(None, "Settings Error", str(e))
        return False
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to initialize settings: {str(e)}")
        return False

def main():
    load_dotenv()
    ensure_directories()
    
    if not init_settings():
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
