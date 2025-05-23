from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from frontend.themes.theme_manager import ThemeManager
from .settings_manager import get_setting, update_setting, save_settings

def save_settings_dialog(theme_combo, setup_mode, settings_updated, parent, camera_backend_combo=None):
    try:
        update_setting("theme", "theme", theme_combo.currentText())
        if camera_backend_combo:
            update_setting("camera", "backend", camera_backend_combo.currentText())
        save_settings()
        if setup_mode:
            QMessageBox.information(
                parent,
                "Success",
                "Initial setup completed successfully!"
            )
        if settings_updated:
            settings_updated.emit()
        return True
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to save settings: {str(e)}")
        return False

class SettingsDialog(QDialog):
    settings_updated = pyqtSignal()
    def __init__(self, parent=None, setup_mode=False, setup_type=None):
        super().__init__(parent)
        self.setup_mode = setup_mode
        self.setWindowTitle("Setup" if setup_mode else "Settings")
        self.setModal(True)
        self.theme_manager = ThemeManager(self)
        current_theme = get_setting("theme", "theme")
        if current_theme:
            self.theme_manager.apply_theme(current_theme)
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        theme_group = self._create_theme_group()
        layout.addWidget(theme_group)
        
        camera_group = self._create_camera_group()
        layout.addWidget(camera_group)
        
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_theme_group(self):
        group = QGroupBox("Theme")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(get_setting("theme", "theme"))
        theme_label = QLabel("Application Theme:")
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        return group
    
    def _create_camera_group(self):
        group = QGroupBox("Camera")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        self.camera_backend_combo = QComboBox()
        backend_options = [
            "DirectShow - Microsoft (Windows legacy video capture, for better compatibility)",
            "Media Foundation - Microsoft (Modern Windows media framework, for newer high end devices)"
        ]
        self.camera_backend_combo.addItems(backend_options)
        backend = get_setting("camera", "backend")
        if backend not in backend_options:
            backend = backend_options[0]
        self.camera_backend_combo.setCurrentText(backend)
        backend_label = QLabel("Camera Backend:")
        layout.addWidget(backend_label)
        layout.addWidget(self.camera_backend_combo)
        return group
    
    def _create_button_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        save_btn = QPushButton("Save")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self._save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self._handle_cancel)
        layout.addStretch()
        layout.addWidget(save_btn)
        layout.addWidget(cancel_btn)
        return layout
    
    def _handle_cancel(self):
        self.reject()
    
    def _save_settings(self):
        result = save_settings_dialog(
            self.theme_combo,
            self.setup_mode,
            self.settings_updated,
            self,
            self.camera_backend_combo
        )
        if result:
            self.accept()
