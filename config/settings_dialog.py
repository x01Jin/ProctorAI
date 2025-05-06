from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QFormLayout, QComboBox, QLabel, QLineEdit,
    QSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from frontend.themes.theme_manager import ThemeManager
from .settings_manager import get_setting, update_setting, save_settings

def validate_settings_dialog_inputs(api_key, project, model_classes, db_host, db_user, db_name, show_error):
    if not api_key.text().strip() or api_key.text().strip() == 'REQUIRED':
        show_error("Roboflow API key is required")
        return False
    if not project.text().strip() or project.text().strip() == 'REQUIRED':
        show_error("Roboflow project name is required")
        return False
    if not model_classes.text().strip() or model_classes.text().strip() == 'REQUIRED':
        show_error("Model classes are required (comma-separated)")
        return False
    if not all([db_host.text().strip(), db_user.text().strip(), db_name.text().strip()]):
        show_error("Database host, user, and name are required")
        return False
    return True

def save_settings_dialog(theme_combo, api_key, project, version, model_classes, db_host, db_user, db_pass, db_name, setup_mode, setup_type, settings_updated, parent, camera_backend_combo=None):
    try:
        update_setting("theme", "theme", theme_combo.currentText())
        if camera_backend_combo is not None:
            update_setting("camera", "backend", camera_backend_combo.currentText())
        update_setting("roboflow", "api_key", api_key.text().strip())
        update_setting("roboflow", "project", project.text().strip())
        update_setting("roboflow", "model_version", str(version.value()))
        update_setting("roboflow", "model_classes", model_classes.text().strip())
        update_setting("database", "host", db_host.text().strip())
        update_setting("database", "user", db_user.text().strip())
        update_setting("database", "password", db_pass.text())
        update_setting("database", "database", db_name.text().strip())
        save_settings()
        if setup_mode:
            QMessageBox.information(
                parent,
                "Success",
                f"{'Initial setup' if not setup_type else setup_type.capitalize() + ' setup'} completed successfully!"
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
        self.settings = __import__('config.settings_manager', fromlist=['settings_manager'])
        self.setup_mode = setup_mode
        self.setup_type = setup_type
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
        robo_group = self._create_roboflow_group()
        layout.addWidget(robo_group)
        db_group = self._create_database_group()
        layout.addWidget(db_group)
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
        backend_options = ["DirectShow - Microsoft", "Media Foundation - Microsoft"]
        self.camera_backend_combo.addItems(backend_options)
        backend = get_setting("camera", "backend")
        if backend not in backend_options:
            backend = "DirectShow - Microsoft"
        self.camera_backend_combo.setCurrentText(backend)
        backend_label = QLabel("Camera Backend:")
        layout.addWidget(backend_label)
        layout.addWidget(self.camera_backend_combo)
        return group
    
    def _create_roboflow_group(self):
        group = QGroupBox("Roboflow")
        layout = QFormLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        self.api_key = QLineEdit(get_setting("roboflow", "api_key"))
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.project = QLineEdit(get_setting("roboflow", "project"))
        self.version = QSpinBox()
        self.version.setMinimum(1)
        self.version.setValue(int(get_setting("roboflow", "model_version")))
        self.model_classes = QLineEdit(get_setting("roboflow", "model_classes"))
        layout.addRow("API Key:", self.api_key)
        layout.addRow("Project:", self.project)
        layout.addRow("Version:", self.version)
        layout.addRow("Model Classes:", self.model_classes)
        group.setLayout(layout)
        return group
    
    def _create_database_group(self):
        group = QGroupBox("Database")
        layout = QFormLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        self.db_host = QLineEdit(get_setting("database", "host"))
        self.db_user = QLineEdit(get_setting("database", "user"))
        self.db_pass = QLineEdit(get_setting("database", "password"))
        self.db_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_name = QLineEdit(get_setting("database", "database"))
        layout.addRow("Host:", self.db_host)
        layout.addRow("User:", self.db_user)
        layout.addRow("Password:", self.db_pass)
        layout.addRow("Database:", self.db_name)
        group.setLayout(layout)
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
    
    def _show_error(self, message):
        QMessageBox.critical(self, "Validation Error", message)
    
    def _handle_cancel(self):
        if self.setup_mode:
            msg = "Are you sure you want to cancel the setup?"
            if self.setup_type in ["roboflow", "database"]:
                msg = "Cancelling the setup will exit the application"
            reply = QMessageBox.question(
                self,
                "Confirm Cancel",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.reject()
        else:
            self.reject()

    def _save_settings(self):
        valid = validate_settings_dialog_inputs(
            self.api_key, self.project, self.model_classes,
            self.db_host, self.db_user, self.db_name, self._show_error
        )
        if not valid:
            return
        result = save_settings_dialog(
            self.theme_combo, self.api_key, self.project, self.version, self.model_classes,
            self.db_host, self.db_user, self.db_pass, self.db_name,
            self.setup_mode, self.setup_type, self.settings_updated, self, self.camera_backend_combo
        )
        if result:
            self.accept()
