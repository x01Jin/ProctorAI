from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QFormLayout, QComboBox, QLabel, QLineEdit,
    QSpinBox, QPushButton, QMessageBox
)

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedWidth(320)
        layout = QVBoxLayout()
        
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
        layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme", "theme"))
        
        layout.addWidget(QLabel("Application Theme:"))
        layout.addWidget(self.theme_combo)
        group.setLayout(layout)
        
        return group
    
    def _create_roboflow_group(self):
        group = QGroupBox("Roboflow")
        layout = QFormLayout()
        
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
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
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
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
