from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
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
        
        message = "ProctorAI requires initial setup.\nPlease configure the API and database credentials to continue."
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
            if dialog.exec() == QDialog.DialogCode.Accepted:
                settings_dialog = SettingsDialog(settings, parent)
                if settings_dialog.exec() == QDialog.DialogCode.Accepted:
                    continue
            return False
        except Exception:
            return False