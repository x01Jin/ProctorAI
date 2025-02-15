import sys
import os
from PyQt6.QtWidgets import QApplication
from frontend.components.main_window import MainWindow

def ensure_temp_directory():
    if not os.path.exists("tempcaptures"):
        os.makedirs("tempcaptures")

def main():
    ensure_temp_directory()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
