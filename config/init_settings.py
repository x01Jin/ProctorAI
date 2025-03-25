from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QMessageBox
)
from .settings_manager import SettingsManager
from .settings_dialog import SettingsDialog

class ValidationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings Required")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        message = """ProctorAI requires initial setup.
        Please configure:
        - Roboflow API key and project
        - Model classes (comma-separated)
        - Database credentials

        The application cannot start without these settings."""
        label = QLabel(message)
        layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        settings_btn = QPushButton("Open Settings")
        settings_btn.clicked.connect(self.open_settings)
        
        exit_btn = QPushButton("Exit Application")
        exit_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(settings_btn)
        button_layout.addWidget(exit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def open_settings(self):
        self.accept()

def initialize_settings(parent=None):
    settings = SettingsManager()
    while True:
        try:
            settings.validate_settings()
            return True
            
        except ValueError:
            dialog = ValidationDialog(parent)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return False
                
            settings_dialog = SettingsDialog(settings, parent)
            if settings_dialog.exec() != QDialog.DialogCode.Accepted:
                return False
                
            continue
            
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Error",
                f"Failed to initialize settings: {str(e)}"
            )
            return False
