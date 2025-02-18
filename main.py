import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from frontend.components.main_window import MainWindow

def ensure_directories():
    directories = [
        "tempcaptures",
        Path(os.path.expanduser("~")) / ".proctorai" / "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    load_dotenv()
    ensure_directories()
    
    app = QApplication(sys.argv)
    
    from config.init_settings import initialize_settings
    if not initialize_settings():
        sys.exit(1)
    
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
