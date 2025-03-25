from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QFormLayout, QComboBox, QLabel, QLineEdit,
    QSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from frontend.themes.theme_manager import ThemeManager

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None, setup_mode=False, setup_type=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_mode = setup_mode
        self.setup_type = setup_type
        self.setWindowTitle("Setup" if setup_mode else "Settings")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        self.theme_manager = ThemeManager(self)
        current_theme = settings.get_setting("theme", "theme")
        if current_theme:
            self.theme_manager.apply_theme(current_theme)
            
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme settings
        theme_group = self._create_theme_group()
        layout.addWidget(theme_group)
        
        # Roboflow settings
        robo_group = self._create_roboflow_group()
        layout.addWidget(robo_group)
        
        # Database settings
        db_group = self._create_database_group()
        layout.addWidget(db_group)
        
        # Buttons
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
        self.theme_combo.setCurrentText(self.settings.get_setting("theme", "theme"))
        
        theme_label = QLabel("Application Theme:")
        
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        
        return group
    
    def _create_roboflow_group(self):
        group = QGroupBox("Roboflow")
        layout = QFormLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.api_key = QLineEdit(self.settings.get_setting("roboflow", "api_key"))
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.project = QLineEdit(self.settings.get_setting("roboflow", "project"))
        
        self.version = QSpinBox()
        self.version.setMinimum(1)
        self.version.setValue(int(self.settings.get_setting("roboflow", "model_version")))
        
        self.model_classes = QLineEdit(self.settings.get_setting("roboflow", "model_classes"))
        
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
        
        self.db_host = QLineEdit(self.settings.get_setting("database", "host"))
        self.db_user = QLineEdit(self.settings.get_setting("database", "user"))
        self.db_pass = QLineEdit(self.settings.get_setting("database", "password"))
        self.db_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_name = QLineEdit(self.settings.get_setting("database", "database"))
        
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
    
    def _validate_inputs(self):
        if not self.api_key.text().strip() or self.api_key.text().strip() == 'REQUIRED':
            self._show_error("Roboflow API key is required")
            return False
            
        if not self.project.text().strip() or self.project.text().strip() == 'REQUIRED':
            self._show_error("Roboflow project name is required")
            return False
            
        if not self.model_classes.text().strip() or self.model_classes.text().strip() == 'REQUIRED':
            self._show_error("Model classes are required (comma-separated)")
            return False
            
        if not all([self.db_host.text().strip(),
                   self.db_user.text().strip(),
                   self.db_name.text().strip()]):
            self._show_error("Database host, user, and name are required")
            return False
            
        return True
    
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
        if not self._validate_inputs():
            return
            
        try:
            self.settings.update_setting("theme", "theme", self.theme_combo.currentText())
            
            self.settings.update_setting("roboflow", "api_key", self.api_key.text().strip())
            self.settings.update_setting("roboflow", "project", self.project.text().strip())
            self.settings.update_setting("roboflow", "model_version", str(self.version.value()))
            self.settings.update_setting("roboflow", "model_classes", self.model_classes.text().strip())
            
            self.settings.update_setting("database", "host", self.db_host.text().strip())
            self.settings.update_setting("database", "user", self.db_user.text().strip())
            self.settings.update_setting("database", "password", self.db_pass.text())
            self.settings.update_setting("database", "database", self.db_name.text().strip())
            
            self.settings.save_settings()
            
            # Show success message in setup mode
            if self.setup_mode:
                QMessageBox.information(
                    self,
                    "Success",
                    f"{'Initial setup' if not self.setup_type else self.setup_type.capitalize() + ' setup'} completed successfully!"
                )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
