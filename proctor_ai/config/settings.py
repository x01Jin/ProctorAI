import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class Settings:
    def __init__(self):
        self.settings_file = "app_settings.json"
        self.default_settings = {
            "theme": "dark",
            "roboflow": {
                "api_key": "Ig1F9Y1p5qSulNYEAxwb",
                "project": "giam_sat_gian_lan",
                "model_version": 2
            },
            "database": {
                "host": "localhost",
                "user": "root",
                "password": "",
                "database": "proctorai"
            }
        }
        self._settings_data = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return self.default_settings

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self._settings_data, f, indent=4)

    def get_setting(self, category, key=None):
        if key:
            return self._settings_data.get(category, {}).get(key)
        return self._settings_data.get(category)

    def update_setting(self, category, key, value):
        if key is None:
            self._settings_data[category] = value
        else:
            if category not in self._settings_data:
                self._settings_data[category] = {}
            self._settings_data[category][key] = value
        self.save_settings()


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme"))
        theme_layout.addWidget(QLabel("Application Theme:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Roboflow settings
        robo_group = QGroupBox("Roboflow")
        robo_layout = QFormLayout()
        self.api_key = QLineEdit(self.settings.get_setting("roboflow", "api_key"))
        self.project = QLineEdit(self.settings.get_setting("roboflow", "project"))
        self.version = QSpinBox()
        self.version.setValue(self.settings.get_setting("roboflow", "model_version"))
        robo_layout.addRow("API Key:", self.api_key)
        robo_layout.addRow("Project:", self.project)
        robo_layout.addRow("Version:", self.version)
        robo_group.setLayout(robo_layout)
        layout.addWidget(robo_group)

        # Database settings
        db_group = QGroupBox("Database")
        db_layout = QFormLayout()
        self.db_host = QLineEdit(self.settings.get_setting("database", "host"))
        self.db_user = QLineEdit(self.settings.get_setting("database", "user"))
        self.db_pass = QLineEdit(self.settings.get_setting("database", "password"))
        self.db_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_name = QLineEdit(self.settings.get_setting("database", "database"))
        db_layout.addRow("Host:", self.db_host)
        db_layout.addRow("User:", self.db_user)
        db_layout.addRow("Password:", self.db_pass)
        db_layout.addRow("Database:", self.db_name)
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)

        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def save_settings(self):
        # Update theme (top-level setting)
        self.settings.update_setting("theme", None, self.theme_combo.currentText())
        
        # Update Roboflow settings (nested settings)
        self.settings.update_setting("roboflow", "api_key", self.api_key.text())
        self.settings.update_setting("roboflow", "project", self.project.text())
        self.settings.update_setting("roboflow", "model_version", self.version.value())
        
        # Update database settings (nested settings)
        self.settings.update_setting("database", "host", self.db_host.text())
        self.settings.update_setting("database", "user", self.db_user.text())
        self.settings.update_setting("database", "password", self.db_pass.text())
        self.settings.update_setting("database", "database", self.db_name.text())
        
        self.settings.save_settings()
        self.accept()
