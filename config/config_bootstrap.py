from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from config.settings_manager import config_exists, load_settings, ensure_config_directory, CONFIG_FILE
from config.settings_dialog import SettingsDialog
from PyQt6.QtWidgets import QApplication
import configparser

DEFAULT_SETTINGS = {
    'theme': {'theme': 'dark'},
    'camera': {'backend': 'DirectShow - Microsoft (Windows legacy video capture, for better compatibility)'}
}

def create_default_config():
    ensure_config_directory()
    config = configparser.ConfigParser()
    settings = DEFAULT_SETTINGS.copy()
    for section, values in settings.items():
        if section not in config:
            config[section] = {}
        for key, value in values.items():
            config[section][key] = str(value)
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
    return settings

class ConfigConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings Required")
        self.setModal(True)
        layout = QVBoxLayout()
        message = (
            "ProctorAI requires initial configuration.\n"
            "Application cannot start without these settings."
        )
        label = QLabel(message)
        layout.addWidget(label)
        button_layout = QHBoxLayout()
        settings_btn = QPushButton("Open Settings")
        settings_btn.clicked.connect(self.accept)
        exit_btn = QPushButton("Exit Application")
        exit_btn.clicked.connect(self.reject)
        button_layout.addWidget(settings_btn)
        button_layout.addWidget(exit_btn)
        layout.addLayout(button_layout)
        self.setLayout(layout)

def ensure_config(parent, log_display):
    if config_exists():
        load_settings()
        return True
    log_display.log("No configuration file found, Attempting to create the configuration file with default values...", "warning")
    QApplication.processEvents()
    dialog = ConfigConfirmDialog(parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return False
    create_default_config()
    load_settings()
    log_display.log("Configuration file created, Launching setup...", "success")
    dialog = SettingsDialog(parent=parent, setup_mode=True)
    if dialog.exec() == dialog.DialogCode.Accepted:
        return True
    return False
